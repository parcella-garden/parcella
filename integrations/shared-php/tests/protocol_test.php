<?php

declare(strict_types=1);

// Run: docker run --rm -v "$PWD/integrations/shared-php:/app" -w /app php:8.3-cli php tests/protocol_test.php <signature-from-parcella>
// The signature argument is Parcella's own sign() result for the fixed
// request below (see the command in integrations/shared-php/README.md),
// so this proves PHP and Python agree.

require __DIR__ . '/../ParcellaProtocol.php';

use Parcella\Shared\ParcellaProtocol as P;

$failures = 0;
function check(string $label, bool $ok): void
{
    global $failures;
    echo ($ok ? 'ok   ' : 'FAIL ') . $label . PHP_EOL;
    if (!$ok) {
        $failures++;
    }
}

$secret = str_repeat('ab', 32);
$ts = '1792700000';
$body = '{"title":"Hallo"}';
$path = '/parcella/v1/drafts';
$fromPython = $argv[1] ?? '';

check('Python signature verifies in PHP', P::verify($secret, 'POST', $path, $body, $ts, $fromPython, 1792700000));
check('wrong secret fails', !P::verify(str_repeat('cd', 32), 'POST', $path, $body, $ts, $fromPython, 1792700000));
check('changed body fails', !P::verify($secret, 'POST', $path, $body . ' ', $ts, $fromPython, 1792700000));
check('other endpoint fails', !P::verify($secret, 'POST', '/parcella/v1/drafts/1', $body, $ts, $fromPython, 1792700000));
check('other method fails', !P::verify($secret, 'PUT', $path, $body, $ts, $fromPython, 1792700000));
check('stale timestamp fails', !P::verify($secret, 'POST', $path, $body, $ts, $fromPython, 1792700000 + 301));
check('timestamp within 5 min passes', P::verify($secret, 'POST', $path, $body, $ts, $fromPython, 1792700000 + 299));
check('short secret refused', !P::verify('short', 'POST', $path, $body, $ts, $fromPython, 1792700000));
check('non-numeric timestamp refused', !P::verify($secret, 'POST', $path, $body, '17927e5', $fromPython, 1792700000));
check('missing signature refused', !P::verify($secret, 'POST', $path, $body, $ts, null, 1792700000));

check('route ping', P::route('/parcella/v1/ping') === ['ping', null]);
check('route drafts', P::route('/site/parcella/v1/drafts') === ['drafts', null]);
check('route draft id decoded', P::route('/parcella/v1/drafts/a%20b') === ['drafts', 'a b']);
check('route rejects other paths', P::route('/parcella/v1/drafts/1/x') === null && P::route('/admin') === null);
check('requestPath drops the query', P::requestPath('/parcella/v1/ping?x=1') === '/parcella/v1/ping');

$png = base64_encode("\x89PNG\r\n\x1a\n" . str_repeat("\0", 20));
$draft = P::parseDraft(json_encode(['title' => "Zaun\nkaputt", 'source_id' => 'ann-1', 'image' => ['mime' => 'image/png', 'data_base64' => $png, 'filename' => '../../evil.php']]));
check('title newlines flattened', $draft['title'] === 'Zaun kaputt');
check('image accepted as replace', $draft['image']['state'] === 'replace' && $draft['image']['extension'] === 'png');
check('stored file name ignores the sender', (bool) preg_match('/^parcella-[0-9a-f]{16}\.png$/', P::storedFilename('png')));
check('image key absent = unchanged', P::parseDraft('{"title":"x"}')['image'] === ['state' => 'unchanged']);
check('image null = remove', P::parseDraft('{"title":"x","image":null}')['image'] === ['state' => 'remove']);

$rejects = [
    'not JSON' => 'nope',
    'no title' => '{"title":"  "}',
    'title not a string' => '{"title":5}',
    'bad source id' => '{"title":"x","source_id":"<script>"}',
    'svg not allowed' => json_encode(['title' => 'x', 'image' => ['mime' => 'image/svg+xml', 'data_base64' => base64_encode('<svg/>')]]),
    'php disguised as png' => json_encode(['title' => 'x', 'image' => ['mime' => 'image/png', 'data_base64' => base64_encode('<?php system($_GET[1]);')]]),
    'invalid base64' => json_encode(['title' => 'x', 'image' => ['mime' => 'image/png', 'data_base64' => '***']]),
];
foreach ($rejects as $label => $input) {
    try {
        P::parseDraft($input);
        check("rejects: $label", false);
    } catch (\InvalidArgumentException $e) {
        check("rejects: $label", true);
    }
}

check('secret is 64 hex characters', (bool) preg_match('/^[0-9a-f]{64}$/', P::generateSecret()));

echo $failures === 0 ? "ALL PASSED\n" : "$failures FAILED\n";
exit($failures === 0 ? 0 : 1);

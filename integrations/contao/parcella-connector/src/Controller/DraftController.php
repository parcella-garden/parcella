<?php

declare(strict_types=1);

namespace Parcella\ContaoParcellaConnector\Controller;

use Contao\Config;
use Contao\CoreBundle\Framework\ContaoFramework;
use Contao\CoreBundle\Routing\ContentUrlGenerator;
use Contao\CoreBundle\Slug\Slug;
use Contao\Dbafs;
use Contao\Input;
use Contao\NewsModel;
use Doctrine\DBAL\Connection;
use Parcella\ContaoParcellaConnector\ParcellaProtocol;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Routing\Generator\UrlGeneratorInterface;

/**
 * Parcella Connector for Contao: the Parcella Website Plugin Protocol v1.
 *
 * Drafts become unpublished news entries (the text as one text element).
 * Publishing stays a human decision in Contao: nothing here ever changes
 * an entry's "published" flag after creating it.
 *
 * Licensed GPL-2.0-or-later.
 */
final class DraftController
{
    public const VERSION = '1.0.0';
    private const IMAGE_FOLDER = 'files/parcella';

    public function __construct(
        private readonly ContaoFramework $framework,
        private readonly Connection $connection,
        private readonly Slug $slug,
        private readonly ContentUrlGenerator $urlGenerator,
        private readonly string $projectDir,
    ) {}

    // The request signature is the authentication; no Contao session or
    // request token is involved (_token_check), and the answers are never
    // cached.
    #[Route('/parcella/v1/{rest}', name: 'parcella_connector', requirements: ['rest' => '.+'], defaults: ['_token_check' => false], methods: ['GET', 'POST', 'PUT'], priority: 100)]
    public function __invoke(Request $request): JsonResponse
    {
        $path = ParcellaProtocol::requestPath($request->getRequestUri());
        $route = ParcellaProtocol::route($path);
        [$status, $data] = $route === null ? [404, ['error' => 'not found']] : $this->handle($route, $request, $path);

        $response = new JsonResponse($data, $status);
        $response->headers->set('Cache-Control', 'no-store, private');

        return $response;
    }

    /** @return array{0: int, 1: array} */
    private function handle(array $route, Request $request, string $path): array
    {
        $this->framework->initialize();
        $config = $this->framework->getAdapter(Config::class);
        $secret = (string) $config->get('parcellaConnectorSecret');
        if (\strlen($secret) < 32) {
            return [503, ['error' => 'The Parcella Connector has no shared secret yet (System > Settings).']];
        }
        $body = (string) $request->getContent();
        $verified = ParcellaProtocol::verify(
            $secret,
            $request->getMethod(),
            $path,
            $body,
            $request->headers->get('X-Parcella-Timestamp'),
            $request->headers->get('X-Parcella-Signature'),
        );
        if (!$verified) {
            return [401, ['error' => 'unauthorized']];
        }
        $archive = (int) $config->get('parcellaConnectorArchive');
        $author = (int) $config->get('parcellaConnectorAuthor');
        if ($archive <= 0 || $author <= 0) {
            return [503, ['error' => 'Choose a news archive and an author for drafts (System > Settings).']];
        }

        [$endpoint, $id] = $route;
        $method = strtoupper($request->getMethod());
        try {
            return match (true) {
                $endpoint === 'ping' && $method === 'GET' => [200, ParcellaProtocol::pingPayload('Parcella Connector for Contao', self::VERSION)],
                $endpoint === 'drafts' && $id === null && $method === 'POST' => $this->createDraft(ParcellaProtocol::parseDraft($body), $archive, $author),
                $endpoint === 'drafts' && $id !== null && $method === 'GET' => $this->draftStatus($id),
                $endpoint === 'drafts' && $id !== null && $method === 'PUT' => $this->updateDraft($id, ParcellaProtocol::parseDraft($body)),
                default => [405, ['error' => 'method not allowed']],
            };
        } catch (\InvalidArgumentException $e) {
            return [400, ['error' => $e->getMessage()]];
        }
    }

    private function createDraft(array $draft, int $archive, int $author): array
    {
        // Idempotent on source_id (kept in the entry's "description").
        if ($draft['source_id'] !== '' && ($existing = $this->findBySource($draft['source_id'])) !== null) {
            return [201, ['id' => (string) $existing, 'edit_url' => null]];
        }

        $now = time();
        $this->connection->insert('tl_news', [
            'pid' => $archive,
            'tstamp' => $now,
            'headline' => $draft['title'],
            'alias' => $this->uniqueAlias($draft['title']),
            'author' => $author,
            'date' => $now,
            'time' => $now,
            'teaser' => $draft['summary'] !== '' ? '<p>' . htmlspecialchars($draft['summary'], ENT_QUOTES) . '</p>' : '',
            'description' => $draft['source_id'] !== '' ? 'parcella:' . $draft['source_id'] : '',
            'source' => 'default',
            // Unpublished, always. (Contao 5 stores checkboxes as 0/1.)
            'published' => 0,
        ]);
        $newsId = (int) $this->connection->lastInsertId();
        $this->connection->insert('tl_content', [
            'pid' => $newsId,
            'ptable' => 'tl_news',
            'tstamp' => $now,
            'sorting' => 128,
            'type' => 'text',
            'text' => $this->cleanHtml($draft['html']),
        ]);
        $this->applyImage($newsId, $draft);

        return [201, ['id' => (string) $newsId, 'edit_url' => null]];
    }

    private function updateDraft(string $id, array $draft): array
    {
        $news = $this->loadNews($id);
        if ($news === null) {
            return [404, ['error' => 'not found']];
        }
        $now = time();
        $this->connection->update('tl_news', [
            'headline' => $draft['title'],
            'teaser' => $draft['summary'] !== '' ? '<p>' . htmlspecialchars($draft['summary'], ENT_QUOTES) . '</p>' : '',
            'tstamp' => $now,
            // "published" is deliberately left as a human set it.
        ], ['id' => (int) $news['id']]);
        $element = $this->connection->fetchOne(
            "SELECT id FROM tl_content WHERE pid = ? AND ptable = 'tl_news' AND type = 'text' ORDER BY sorting LIMIT 1",
            [(int) $news['id']],
        );
        if ($element !== false) {
            $this->connection->update('tl_content', ['text' => $this->cleanHtml($draft['html']), 'tstamp' => $now], ['id' => (int) $element]);
        }
        $this->applyImage((int) $news['id'], $draft);

        return [200, ['id' => (string) $news['id'], 'edit_url' => null]];
    }

    private function draftStatus(string $id): array
    {
        $news = $this->loadNews($id);
        if ($news === null) {
            return [404, ['error' => 'not found']];
        }
        $published = (int) $news['published'] === 1;
        $url = null;
        if ($published) {
            try {
                $model = $this->framework->getAdapter(NewsModel::class)->findByPk((int) $news['id']);
                $url = $model ? $this->urlGenerator->generate($model, [], UrlGeneratorInterface::ABSOLUTE_URL) : null;
            } catch (\Throwable) {
                // No reader page set on the archive: no public address yet.
                $url = null;
            }
        }

        return [200, ['status' => $published ? 'published' : 'draft', 'public_url' => $url]];
    }

    /**
     * The HTML arrives already sanitized from Parcella; Contao's own
     * allowed-tags filter (System > Settings > Allowed HTML tags) runs
     * over it again.
     */
    private function cleanHtml(string $html): string
    {
        $config = $this->framework->getAdapter(Config::class);

        return (string) $this->framework->getAdapter(Input::class)->stripTags(
            $html,
            (string) $config->get('allowedTags'),
            (string) $config->get('allowedAttributes'),
        );
    }

    private function applyImage(int $newsId, array $draft): void
    {
        $image = $draft['image'];
        if ($image['state'] === 'unchanged') {
            return;
        }
        if ($image['state'] === 'remove') {
            $this->connection->update('tl_news', ['addImage' => 0, 'singleSRC' => null], ['id' => $newsId]);

            return;
        }
        $folder = $this->projectDir . '/' . self::IMAGE_FOLDER;
        if (!is_dir($folder) && !mkdir($folder, 0775, true) && !is_dir($folder)) {
            throw new \InvalidArgumentException('The image folder could not be created.');
        }
        $name = ParcellaProtocol::storedFilename($image['extension']);
        if (file_put_contents($folder . '/' . $name, $image['bytes']) === false) {
            throw new \InvalidArgumentException('The image could not be stored.');
        }
        $file = $this->framework->getAdapter(Dbafs::class)->addResource(self::IMAGE_FOLDER . '/' . $name);
        $this->connection->update('tl_news', [
            'addImage' => 1,
            'singleSRC' => $file->uuid,
            'overwriteMeta' => 1,
            'alt' => $draft['title'],
        ], ['id' => $newsId]);
    }

    private function loadNews(string $id): ?array
    {
        if (!ctype_digit($id)) {
            return null;
        }
        $row = $this->connection->fetchAssociative('SELECT id, published FROM tl_news WHERE id = ?', [(int) $id]);

        return $row === false ? null : $row;
    }

    private function findBySource(string $sourceId): ?int
    {
        $id = $this->connection->fetchOne('SELECT id FROM tl_news WHERE description = ? LIMIT 1', ['parcella:' . $sourceId]);

        return $id === false ? null : (int) $id;
    }

    private function uniqueAlias(string $title): string
    {
        $base = $this->slug->generate($title) ?: 'parcella-draft';
        $alias = $base;
        for ($n = 2; $this->connection->fetchOne('SELECT COUNT(*) FROM tl_news WHERE alias = ?', [$alias]) > 0; $n++) {
            $alias = $base . '-' . $n;
        }

        return $alias;
    }
}

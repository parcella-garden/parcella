<?php

/**
 * Parcella Connector for Joomla: the Parcella Website Plugin Protocol v1.
 *
 * Drafts become unpublished articles. Publishing stays a human decision
 * in Joomla: nothing here ever changes an article's published state.
 *
 * @license GPL-2.0-or-later
 */

namespace Parcella\Plugin\System\ParcellaConnector\Extension;

defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Filter\InputFilter;
use Joomla\CMS\Filter\OutputFilter;
use Joomla\CMS\Plugin\CMSPlugin;
use Joomla\CMS\Table\Content;
use Joomla\CMS\Uri\Uri;
use Joomla\Database\DatabaseAwareTrait;
use Joomla\Database\ParameterType;
use Joomla\Event\SubscriberInterface;
use Joomla\Filesystem\File;
use Joomla\Filesystem\Folder;
use Parcella\Plugin\System\ParcellaConnector\ParcellaProtocol;

final class ParcellaConnector extends CMSPlugin implements SubscriberInterface
{
    use DatabaseAwareTrait;

    public const VERSION = '1.0.0';
    private const IMAGE_FOLDER = 'images/parcella';

    public static function getSubscribedEvents(): array
    {
        return ['onAfterInitialise' => 'onAfterInitialise'];
    }

    public function onAfterInitialise(): void
    {
        $app = $this->getApplication();
        if (!$app->isClient('site')) {
            return;
        }
        $path = ParcellaProtocol::requestPath((string) ($_SERVER['REQUEST_URI'] ?? '/'));
        $route = ParcellaProtocol::route($path);
        if ($route === null) {
            return;
        }

        [$status, $data] = $this->handle($route, strtoupper((string) ($_SERVER['REQUEST_METHOD'] ?? 'GET')), $path);

        $app->setHeader('Status', (string) $status, true);
        $app->setHeader('Content-Type', 'application/json; charset=utf-8', true);
        $app->setHeader('Cache-Control', 'no-store', true);
        $app->sendHeaders();
        echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $app->close();
    }

    /** @return array{0: int, 1: array} */
    private function handle(array $route, string $method, string $path): array
    {
        $secret = (string) $this->params->get('secret', '');
        if (strlen($secret) < 32) {
            return [503, ['error' => 'The Parcella Connector has no shared secret yet.']];
        }
        $body = (string) file_get_contents('php://input');
        $verified = ParcellaProtocol::verify(
            $secret,
            $method,
            $path,
            $body,
            $_SERVER['HTTP_X_PARCELLA_TIMESTAMP'] ?? null,
            $_SERVER['HTTP_X_PARCELLA_SIGNATURE'] ?? null
        );
        if (!$verified) {
            return [401, ['error' => 'unauthorized']];
        }
        if ((int) $this->params->get('catid', 0) <= 0 || (int) $this->params->get('created_by', 0) <= 0) {
            return [503, ['error' => 'Choose a category and an author in the Parcella Connector plugin settings.']];
        }

        [$endpoint, $id] = $route;
        try {
            if ($endpoint === 'ping' && $id === null && $method === 'GET') {
                return [200, ParcellaProtocol::pingPayload('Parcella Connector for Joomla', self::VERSION)];
            }
            if ($endpoint === 'drafts' && $id === null && $method === 'POST') {
                return $this->createDraft(ParcellaProtocol::parseDraft($body));
            }
            if ($endpoint === 'drafts' && $id !== null && $method === 'GET') {
                return $this->draftStatus($id);
            }
            if ($endpoint === 'drafts' && $id !== null && $method === 'PUT') {
                return $this->updateDraft($id, ParcellaProtocol::parseDraft($body));
            }
        } catch (\InvalidArgumentException $e) {
            return [400, ['error' => $e->getMessage()]];
        }

        return [405, ['error' => 'method not allowed']];
    }

    private function createDraft(array $draft): array
    {
        // Idempotent on source_id: a retried request returns the same article.
        if ($draft['source_id'] !== '' && ($existing = $this->findBySource($draft['source_id'])) !== null) {
            return [201, $this->draftAnswer($existing)];
        }

        $table = new Content($this->getDatabase());
        $data = [
            'title' => $draft['title'],
            'alias' => $this->uniqueAlias($draft['title']),
            'introtext' => $this->cleanHtml($draft['html']),
            'fulltext' => '',
            // Unpublished, always.
            'state' => 0,
            'catid' => (int) $this->params->get('catid'),
            'created' => Factory::getDate()->toSql(),
            'created_by' => (int) $this->params->get('created_by'),
            'language' => '*',
            'access' => 1,
            'metadesc' => mb_substr($draft['summary'], 0, 160),
            // Marks the article as created by Parcella (see loadArticle).
            'note' => 'parcella:' . ($draft['source_id'] !== '' ? $draft['source_id'] : 'draft-' . bin2hex(random_bytes(8))),
            'images' => json_encode($this->imageFields($draft, [])),
            'urls' => '{}',
            'attribs' => '{}',
            'metadata' => '{}',
            'metakey' => '',
        ];
        if (!$table->bind($data) || !$table->check() || !$table->store()) {
            return [500, ['error' => 'Joomla could not save the article.']];
        }
        $this->assignDefaultWorkflowStage((int) $table->id);

        return [201, $this->draftAnswer((int) $table->id)];
    }

    /**
     * Since Joomla 4 every article needs a workflow association: the
     * backend's article list joins on it (INNER JOIN), so an article
     * without one would be invisible there. Assigns the default stage of
     * the default com_content workflow, as Joomla's own model does.
     */
    private function assignDefaultWorkflowStage(int $articleId): void
    {
        $db = $this->getDatabase();
        $extension = 'com_content.article';
        $query = $db->getQuery(true)
            ->select($db->quoteName('s.id'))
            ->from($db->quoteName('#__workflow_stages', 's'))
            ->join('INNER', $db->quoteName('#__workflows', 'w'), $db->quoteName('w.id') . ' = ' . $db->quoteName('s.workflow_id'))
            ->where($db->quoteName('w.extension') . ' = :extension')
            ->where($db->quoteName('w.default') . ' = 1')
            ->where($db->quoteName('s.default') . ' = 1')
            ->bind(':extension', $extension, ParameterType::STRING);
        $stageId = (int) $db->setQuery($query, 0, 1)->loadResult();
        if ($stageId <= 0) {
            return;
        }
        $association = (object) ['item_id' => $articleId, 'stage_id' => $stageId, 'extension' => $extension];
        $db->insertObject('#__workflow_associations', $association);
    }

    private function updateDraft(string $id, array $draft): array
    {
        $table = $this->loadArticle($id);
        if ($table === null) {
            return [404, ['error' => 'not found']];
        }
        $images = json_decode((string) $table->images, true) ?: [];
        $table->title = $draft['title'];
        $table->introtext = $this->cleanHtml($draft['html']);
        $table->metadesc = mb_substr($draft['summary'], 0, 160);
        $table->images = json_encode($this->imageFields($draft, $images));
        // $table->state is deliberately left as a human set it.
        if (!$table->check() || !$table->store()) {
            return [500, ['error' => 'Joomla could not save the article.']];
        }

        return [200, $this->draftAnswer((int) $table->id)];
    }

    private function draftStatus(string $id): array
    {
        $table = $this->loadArticle($id);
        if ($table === null) {
            return [404, ['error' => 'not found']];
        }
        $published = (int) $table->state === 1;

        return [200, [
            'status' => $published ? 'published' : 'draft',
            'public_url' => $published
                ? Uri::root() . 'index.php?option=com_content&view=article&id=' . (int) $table->id . '&catid=' . (int) $table->catid
                : null,
        ]];
    }

    /**
     * The HTML arrives already sanitized from Parcella; Joomla's own input
     * filter (script, iframe, event handlers and the like removed) runs
     * over it again.
     */
    private function cleanHtml(string $html): string
    {
        return InputFilter::getInstance([], [], InputFilter::ONLY_BLOCK_DEFINED_TAGS, InputFilter::ONLY_BLOCK_DEFINED_ATTRIBUTES)
            ->clean($html, 'html');
    }

    private function imageFields(array $draft, array $current): array
    {
        $image = $draft['image'];
        if ($image['state'] === 'unchanged') {
            return $current;
        }
        $fields = array_merge($current, [
            'image_intro' => '', 'image_intro_alt' => '', 'image_fulltext' => '', 'image_fulltext_alt' => '',
        ]);
        if ($image['state'] === 'replace') {
            $folder = JPATH_ROOT . '/' . self::IMAGE_FOLDER;
            if (!is_dir($folder)) {
                Folder::create($folder);
            }
            $name = ParcellaProtocol::storedFilename($image['extension']);
            if (!File::write($folder . '/' . $name, $image['bytes'])) {
                throw new \InvalidArgumentException('The image could not be stored.');
            }
            $relative = self::IMAGE_FOLDER . '/' . $name;
            $fields['image_intro'] = $fields['image_fulltext'] = $relative;
            $fields['image_intro_alt'] = $fields['image_fulltext_alt'] = $draft['title'];
        }

        return $fields;
    }

    /**
     * Only articles this plugin created (note "parcella:..."): Parcella may
     * create and update its own drafts, never touch other content.
     */
    private function loadArticle(string $id): ?Content
    {
        if (!ctype_digit($id)) {
            return null;
        }
        $table = new Content($this->getDatabase());
        if (!$table->load((int) $id) || !str_starts_with((string) $table->note, 'parcella:')) {
            return null;
        }

        return $table;
    }

    private function findBySource(string $sourceId): ?int
    {
        $db = $this->getDatabase();
        $note = 'parcella:' . $sourceId;
        $query = $db->getQuery(true)
            ->select($db->quoteName('id'))
            ->from($db->quoteName('#__content'))
            ->where($db->quoteName('note') . ' = :note')
            ->bind(':note', $note, ParameterType::STRING);
        $id = $db->setQuery($query, 0, 1)->loadResult();

        return $id ? (int) $id : null;
    }

    private function uniqueAlias(string $title): string
    {
        $base = OutputFilter::stringURLSafe($title) ?: 'parcella-draft';
        $db = $this->getDatabase();
        $catid = (int) $this->params->get('catid');
        $alias = $base;
        for ($n = 2; $n < 100; $n++) {
            $query = $db->getQuery(true)
                ->select('COUNT(*)')
                ->from($db->quoteName('#__content'))
                ->where($db->quoteName('alias') . ' = :alias')
                ->where($db->quoteName('catid') . ' = :catid')
                ->bind(':alias', $alias, ParameterType::STRING)
                ->bind(':catid', $catid, ParameterType::INTEGER);
            if ((int) $db->setQuery($query)->loadResult() === 0) {
                return $alias;
            }
            $alias = $base . '-' . $n;
        }

        return $base . '-' . bin2hex(random_bytes(3));
    }

    private function draftAnswer(int $id): array
    {
        return [
            'id' => (string) $id,
            'edit_url' => Uri::root() . 'administrator/index.php?option=com_content&task=article.edit&id=' . $id,
        ];
    }
}

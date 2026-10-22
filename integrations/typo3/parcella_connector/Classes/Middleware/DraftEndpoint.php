<?php

declare(strict_types=1);

namespace Parcella\ParcellaConnector\Middleware;

use Parcella\ParcellaConnector\ParcellaProtocol;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface;
use TYPO3\CMS\Core\Configuration\ExtensionConfiguration;
use TYPO3\CMS\Core\Database\Connection;
use TYPO3\CMS\Core\Database\ConnectionPool;
use TYPO3\CMS\Core\DataHandling\SlugHelper;
use TYPO3\CMS\Core\Html\SanitizerBuilderFactory;
use TYPO3\CMS\Core\Http\JsonResponse;
use TYPO3\CMS\Core\Resource\ResourceFactory;
use TYPO3\CMS\Core\Site\SiteFinder;
use TYPO3\CMS\Core\Utility\GeneralUtility;

/**
 * Parcella Connector for TYPO3: the Parcella Website Plugin Protocol v1.
 *
 * Drafts become hidden records of EXT:news. Publishing stays a human
 * decision in TYPO3: nothing here ever changes a record's "hidden" flag
 * after creating it.
 *
 * Licensed GPL-2.0-or-later.
 */
final class DraftEndpoint implements MiddlewareInterface
{
    public const VERSION = '1.0.0';
    private const NEWS_TABLE = 'tx_news_domain_model_news';
    private const SOURCE_TABLE = 'tx_parcellaconnector_source';

    public function __construct(
        private readonly ConnectionPool $connectionPool,
        private readonly ExtensionConfiguration $extensionConfiguration,
    ) {}

    public function process(ServerRequestInterface $request, RequestHandlerInterface $handler): ResponseInterface
    {
        $path = $request->getUri()->getPath();
        $route = ParcellaProtocol::route($path);
        if ($route === null) {
            return $handler->handle($request);
        }
        [$status, $data] = $this->handle($route, $request, $path);

        return (new JsonResponse($data, $status))->withHeader('Cache-Control', 'no-store');
    }

    /** @return array{0: int, 1: array} */
    private function handle(array $route, ServerRequestInterface $request, string $path): array
    {
        $config = (array) $this->extensionConfiguration->get('parcella_connector');
        $secret = (string) ($config['secret'] ?? '');
        if (strlen($secret) < 32) {
            return [503, ['error' => 'The Parcella Connector has no shared secret yet (Settings > Extension Configuration).']];
        }
        $body = (string) $request->getBody();
        $verified = ParcellaProtocol::verify(
            $secret,
            $request->getMethod(),
            $path,
            $body,
            $request->getHeaderLine('X-Parcella-Timestamp') ?: null,
            $request->getHeaderLine('X-Parcella-Signature') ?: null,
        );
        if (!$verified) {
            return [401, ['error' => 'unauthorized']];
        }
        $storagePid = (int) ($config['storagePid'] ?? 0);
        if ($storagePid <= 0) {
            return [503, ['error' => 'Choose a storage folder for news drafts (Settings > Extension Configuration).']];
        }

        [$endpoint, $id] = $route;
        $method = strtoupper($request->getMethod());
        try {
            return match (true) {
                $endpoint === 'ping' && $method === 'GET' => [200, ParcellaProtocol::pingPayload('Parcella Connector for TYPO3', self::VERSION)],
                $endpoint === 'drafts' && $id === null && $method === 'POST' => $this->createDraft(ParcellaProtocol::parseDraft($body), $storagePid),
                $endpoint === 'drafts' && $id !== null && $method === 'GET' => $this->draftStatus($id, (int) ($config['detailPid'] ?? 0)),
                $endpoint === 'drafts' && $id !== null && $method === 'PUT' => $this->updateDraft($id, ParcellaProtocol::parseDraft($body)),
                default => [405, ['error' => 'method not allowed']],
            };
        } catch (\InvalidArgumentException $e) {
            return [400, ['error' => $e->getMessage()]];
        }
    }

    private function createDraft(array $draft, int $storagePid): array
    {
        // Idempotent on source_id: a retried request returns the same record.
        if ($draft['source_id'] !== '' && ($existing = $this->findBySource($draft['source_id'])) !== null) {
            return [201, ['id' => (string) $existing, 'edit_url' => null]];
        }

        $now = time();
        $news = $this->connectionPool->getConnectionForTable(self::NEWS_TABLE);
        $news->insert(self::NEWS_TABLE, [
            'pid' => $storagePid,
            'title' => $draft['title'],
            'teaser' => $draft['summary'],
            'bodytext' => $this->sanitize($draft['html']),
            'datetime' => $now,
            'crdate' => $now,
            'tstamp' => $now,
            // Hidden, always.
            'hidden' => 1,
            'sys_language_uid' => 0,
            'path_segment' => $this->slug($draft['title'], $storagePid),
        ]);
        $uid = (int) $news->lastInsertId();
        $this->applyImage($uid, $storagePid, $draft);

        // Every record Parcella creates gets a row here -- it's also what
        // marks the record as Parcella's own (see loadNews). A mapping can
        // outlive its record (deleted in TYPO3): replace it.
        $sourceId = $draft['source_id'] !== '' ? $draft['source_id'] : 'draft-' . bin2hex(random_bytes(8));
        $sources = $this->connectionPool->getConnectionForTable(self::SOURCE_TABLE);
        $sources->delete(self::SOURCE_TABLE, ['source_id' => $sourceId]);
        $sources->insert(self::SOURCE_TABLE, ['source_id' => $sourceId, 'news_uid' => $uid]);

        return [201, ['id' => (string) $uid, 'edit_url' => null]];
    }

    private function updateDraft(string $id, array $draft): array
    {
        $record = $this->loadNews($id);
        if ($record === null) {
            return [404, ['error' => 'not found']];
        }
        $this->connectionPool->getConnectionForTable(self::NEWS_TABLE)->update(
            self::NEWS_TABLE,
            [
                'title' => $draft['title'],
                'teaser' => $draft['summary'],
                'bodytext' => $this->sanitize($draft['html']),
                'tstamp' => time(),
                // "hidden" is deliberately left as a human set it.
            ],
            ['uid' => (int) $record['uid']],
        );
        $this->applyImage((int) $record['uid'], (int) $record['pid'], $draft);

        return [200, ['id' => (string) $record['uid'], 'edit_url' => null]];
    }

    private function draftStatus(string $id, int $detailPid): array
    {
        $record = $this->loadNews($id);
        if ($record === null) {
            return [404, ['error' => 'not found']];
        }
        $published = (int) $record['hidden'] === 0;

        return [200, [
            'status' => $published ? 'published' : 'draft',
            'public_url' => $published ? $this->publicUrl((int) $record['uid'], $detailPid) : null,
        ]];
    }

    /**
     * The HTML arrives already sanitized from Parcella; TYPO3's own HTML
     * sanitizer (the one the RTE uses) runs over it again.
     */
    private function sanitize(string $html): string
    {
        $builder = GeneralUtility::makeInstance(SanitizerBuilderFactory::class)->build('default');

        return $builder->build()->sanitize($html);
    }

    private function applyImage(int $newsUid, int $pid, array $draft): void
    {
        $image = $draft['image'];
        if ($image['state'] === 'unchanged') {
            return;
        }
        $references = $this->connectionPool->getConnectionForTable('sys_file_reference');
        $references->update(
            'sys_file_reference',
            ['deleted' => 1, 'tstamp' => time()],
            ['uid_foreign' => $newsUid, 'tablenames' => self::NEWS_TABLE, 'fieldname' => 'fal_media'],
        );
        $count = 0;
        if ($image['state'] === 'replace') {
            $storage = GeneralUtility::makeInstance(ResourceFactory::class)->getDefaultStorage();
            if ($storage === null) {
                throw new \InvalidArgumentException('TYPO3 has no default file storage for the image.');
            }
            $folder = $storage->hasFolder('parcella') ? $storage->getFolder('parcella') : $storage->createFolder('parcella');
            $temporary = GeneralUtility::tempnam('parcella_');
            GeneralUtility::writeFile($temporary, $image['bytes']);
            $file = $storage->addFile($temporary, $folder, ParcellaProtocol::storedFilename($image['extension']));
            $now = time();
            $references->insert('sys_file_reference', [
                'pid' => $pid,
                'uid_local' => $file->getUid(),
                'uid_foreign' => $newsUid,
                'tablenames' => self::NEWS_TABLE,
                'fieldname' => 'fal_media',
                'sorting_foreign' => 1,
                'showinpreview' => 1,
                'alternative' => $draft['title'],
                'crdate' => $now,
                'tstamp' => $now,
            ]);
            $count = 1;
        }
        $this->connectionPool->getConnectionForTable(self::NEWS_TABLE)
            ->update(self::NEWS_TABLE, ['fal_media' => $count], ['uid' => $newsUid]);
    }

    private function publicUrl(int $uid, int $detailPid): ?string
    {
        if ($detailPid <= 0) {
            return null;
        }
        try {
            $site = GeneralUtility::makeInstance(SiteFinder::class)->getSiteByPageId($detailPid);
            $uri = $site->getRouter()->generateUri($detailPid, [
                'tx_news_pi1' => ['action' => 'detail', 'controller' => 'News', 'news' => $uid],
            ]);

            return (string) $uri;
        } catch (\Throwable) {
            return null;
        }
    }

    private function slug(string $title, int $pid): string
    {
        $config = $GLOBALS['TCA'][self::NEWS_TABLE]['columns']['path_segment']['config'] ?? [];
        $helper = GeneralUtility::makeInstance(SlugHelper::class, self::NEWS_TABLE, 'path_segment', $config);

        return $helper->generate(['title' => $title], $pid);
    }

    /**
     * Only records this extension created (listed in its mapping table):
     * Parcella may create and update its own drafts, never touch other news.
     */
    private function loadNews(string $id): ?array
    {
        if (!ctype_digit($id)) {
            return null;
        }
        $owned = $this->connectionPool->getQueryBuilderForTable(self::SOURCE_TABLE);
        $isOwn = $owned->count('uid')
            ->from(self::SOURCE_TABLE)
            ->where($owned->expr()->eq('news_uid', $owned->createNamedParameter((int) $id, Connection::PARAM_INT)))
            ->executeQuery()
            ->fetchOne();
        if ((int) $isOwn === 0) {
            return null;
        }
        $queryBuilder = $this->connectionPool->getQueryBuilderForTable(self::NEWS_TABLE);
        $queryBuilder->getRestrictions()->removeAll();
        $record = $queryBuilder->select('uid', 'pid', 'hidden')
            ->from(self::NEWS_TABLE)
            ->where(
                $queryBuilder->expr()->eq('uid', $queryBuilder->createNamedParameter((int) $id, Connection::PARAM_INT)),
                $queryBuilder->expr()->eq('deleted', $queryBuilder->createNamedParameter(0, Connection::PARAM_INT)),
            )
            ->executeQuery()
            ->fetchAssociative();

        return $record === false ? null : $record;
    }

    private function findBySource(string $sourceId): ?int
    {
        $queryBuilder = $this->connectionPool->getQueryBuilderForTable(self::SOURCE_TABLE);
        $uid = $queryBuilder->select('news_uid')
            ->from(self::SOURCE_TABLE)
            ->where($queryBuilder->expr()->eq('source_id', $queryBuilder->createNamedParameter($sourceId)))
            ->executeQuery()
            ->fetchOne();
        if ($uid === false || $this->loadNews((string) $uid) === null) {
            return null;
        }

        return (int) $uid;
    }
}

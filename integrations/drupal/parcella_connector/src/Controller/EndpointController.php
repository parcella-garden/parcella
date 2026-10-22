<?php

declare(strict_types=1);

namespace Drupal\parcella_connector\Controller;

use Drupal\Component\Utility\Xss;
use Drupal\Core\Controller\ControllerBase;
use Drupal\Core\File\FileExists;
use Drupal\Core\File\FileSystemInterface;
use Drupal\Core\KeyValueStore\KeyValueStoreInterface;
use Drupal\Core\PageCache\ResponsePolicy\KillSwitch;
use Drupal\file\FileRepositoryInterface;
use Drupal\node\NodeInterface;
use Drupal\parcella_connector\ParcellaProtocol;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;

/**
 * The Parcella Website Plugin Protocol v1 endpoints.
 *
 * Drafts become unpublished nodes. Publishing stays a human decision in
 * Drupal: nothing here ever changes a node's published status.
 */
final class EndpointController extends ControllerBase {

  public const VERSION = '1.0.0';

  public function __construct(
    private readonly KeyValueStoreInterface $sources,
    private readonly KeyValueStoreInterface $ownNodes,
    private readonly FileRepositoryInterface $fileRepository,
    private readonly FileSystemInterface $fileSystem,
    private readonly KillSwitch $pageCacheKillSwitch,
  ) {}

  public static function create(ContainerInterface $container): static {
    return new static(
      $container->get('keyvalue')->get('parcella_connector.sources'),
      $container->get('keyvalue')->get('parcella_connector.nodes'),
      $container->get('file.repository'),
      $container->get('file_system'),
      $container->get('page_cache_kill_switch'),
    );
  }

  public function handle(Request $request, string $endpoint, string $id = ''): JsonResponse {
    $this->pageCacheKillSwitch->trigger();

    $config = $this->config('parcella_connector.settings');
    $secret = (string) $config->get('secret');
    if (strlen($secret) < 32) {
      return $this->answer(503, ['error' => 'The Parcella Connector has no shared secret yet.']);
    }
    $body = (string) $request->getContent();
    $verified = ParcellaProtocol::verify(
      $secret,
      $request->getMethod(),
      ParcellaProtocol::requestPath($request->getRequestUri()),
      $body,
      $request->headers->get('X-Parcella-Timestamp'),
      $request->headers->get('X-Parcella-Signature'),
    );
    if (!$verified) {
      return $this->answer(401, ['error' => 'unauthorized']);
    }

    if (($problem = $this->configurationProblem()) !== NULL) {
      return $this->answer(503, ['error' => $problem]);
    }

    try {
      return match ([$endpoint, $request->getMethod()]) {
        ['ping', 'GET'] => $this->answer(200, ParcellaProtocol::pingPayload('Parcella Connector for Drupal', self::VERSION)),
        ['drafts', 'POST'] => $this->createDraft(ParcellaProtocol::parseDraft($body)),
        ['draft', 'GET'] => $this->draftStatus($id),
        ['draft', 'PUT'] => $this->updateDraft($id, ParcellaProtocol::parseDraft($body)),
        default => $this->answer(405, ['error' => 'method not allowed']),
      };
    }
    catch (\InvalidArgumentException $e) {
      return $this->answer(400, ['error' => $e->getMessage()]);
    }
  }

  /**
   * Refuses to save anything half-configured: the content type and its
   * text field must exist (Drupal 11.4's standard profile, for one, no
   * longer creates any content type).
   */
  private function configurationProblem(): ?string {
    $config = $this->config('parcella_connector.settings');
    $type = (string) $config->get('node_type');
    if ($type === '' || $this->entityTypeManager()->getStorage('node_type')->load($type) === NULL) {
      return sprintf('The content type "%s" does not exist. Choose one under Configuration > Web services > Parcella Connector.', $type);
    }
    $fields = \Drupal::service('entity_field.manager')->getFieldDefinitions('node', $type);
    $bodyField = (string) ($config->get('body_field') ?: 'body');
    if (!isset($fields[$bodyField])) {
      return sprintf('The content type "%s" has no field "%s" for the text. Choose one under Configuration > Web services > Parcella Connector.', $type, $bodyField);
    }
    return NULL;
  }

  private function createDraft(array $draft): JsonResponse {
    // Idempotent on source_id: a retried request returns the same draft.
    if ($draft['source_id'] !== '' && ($existing = $this->loadNode((string) $this->sources->get($draft['source_id'])))) {
      return $this->answer(201, $this->draftAnswer($existing));
    }

    $config = $this->config('parcella_connector.settings');
    $node = $this->entityTypeManager()->getStorage('node')->create([
      'type' => $config->get('node_type') ?: 'article',
      'title' => $draft['title'],
      'uid' => (int) ($config->get('author_uid') ?: 1),
      // Unpublished, always.
      'status' => NodeInterface::NOT_PUBLISHED,
    ]);
    $this->applyContent($node, $draft);
    $node->save();
    $this->ownNodes->set((string) $node->id(), TRUE);

    if ($draft['source_id'] !== '') {
      $this->sources->set($draft['source_id'], $node->id());
    }
    return $this->answer(201, $this->draftAnswer($node));
  }

  private function updateDraft(string $id, array $draft): JsonResponse {
    $node = $this->loadNode($id);
    if ($node === NULL) {
      return $this->answer(404, ['error' => 'not found']);
    }
    $node->setTitle($draft['title']);
    $this->applyContent($node, $draft);
    // The published status is deliberately left as a human set it.
    $node->save();
    return $this->answer(200, $this->draftAnswer($node));
  }

  private function draftStatus(string $id): JsonResponse {
    $node = $this->loadNode($id);
    if ($node === NULL) {
      return $this->answer(404, ['error' => 'not found']);
    }
    $published = $node->isPublished();
    return $this->answer(200, [
      'status' => $published ? 'published' : 'draft',
      'public_url' => $published ? $node->toUrl('canonical', ['absolute' => TRUE])->toString() : NULL,
    ]);
  }

  /**
   * Body and image. The HTML comes from Parcella already sanitized; it
   * still goes through Drupal's admin XSS filter, and the text format
   * filters it again on output.
   */
  private function applyContent(NodeInterface $node, array $draft): void {
    $config = $this->config('parcella_connector.settings');
    $node->set((string) ($config->get('body_field') ?: 'body'), [
      'value' => Xss::filterAdmin($draft['html']),
      'summary' => $draft['summary'],
      'format' => $config->get('text_format') ?: 'basic_html',
    ]);
    $imageField = (string) ($config->get('image_field') ?: 'field_image');
    $image = $draft['image'];
    // The image is optional: a content type without an image field just
    // gets the text.
    if (!$node->hasField($imageField) || $image['state'] === 'unchanged') {
      return;
    }
    if ($image['state'] === 'remove') {
      $node->set($imageField, NULL);
      return;
    }
    $directory = 'public://parcella';
    $this->fileSystem->prepareDirectory($directory, FileSystemInterface::CREATE_DIRECTORY | FileSystemInterface::MODIFY_PERMISSIONS);
    $file = $this->fileRepository->writeData(
      $image['bytes'],
      $directory . '/' . ParcellaProtocol::storedFilename($image['extension']),
      FileExists::Rename,
    );
    $node->set($imageField, ['target_id' => $file->id(), 'alt' => $draft['title']]);
  }

  /**
   * Only nodes this module created: Parcella may create and update its own
   * drafts, never touch other content (anything else is "not found").
   */
  private function loadNode(string $id): ?NodeInterface {
    if ($id === '' || !ctype_digit($id) || !$this->ownNodes->has($id)) {
      return NULL;
    }
    $node = $this->entityTypeManager()->getStorage('node')->load((int) $id);
    return $node instanceof NodeInterface ? $node : NULL;
  }

  private function draftAnswer(NodeInterface $node): array {
    return [
      'id' => (string) $node->id(),
      'edit_url' => $node->toUrl('edit-form', ['absolute' => TRUE])->toString(),
    ];
  }

  private function answer(int $status, array $data): JsonResponse {
    $response = new JsonResponse($data, $status);
    $response->setPrivate();
    $response->headers->set('Cache-Control', 'no-store');
    return $response;
  }

}

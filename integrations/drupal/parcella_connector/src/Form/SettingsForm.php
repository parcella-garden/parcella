<?php

declare(strict_types=1);

namespace Drupal\parcella_connector\Form;

use Drupal\Core\Form\ConfigFormBase;
use Drupal\Core\Form\FormStateInterface;
use Drupal\Core\Url;
use Drupal\parcella_connector\ParcellaProtocol;
use Drupal\user\Entity\User;

/**
 * Shows the address and shared secret to enter in Parcella, and where
 * drafts go.
 */
final class SettingsForm extends ConfigFormBase {

  protected function getEditableConfigNames(): array {
    return ['parcella_connector.settings'];
  }

  public function getFormId(): string {
    return 'parcella_connector_settings';
  }

  public function buildForm(array $form, FormStateInterface $form_state): array {
    $config = $this->config('parcella_connector.settings');
    $endpoint = Url::fromRoute('parcella_connector.ping', [], ['absolute' => TRUE])->toString();
    $endpoint = preg_replace('#/ping$#', '', $endpoint);

    $form['intro'] = [
      '#markup' => '<p>' . $this->t('In Parcella, open <em>Admin → Integrations → Website</em>, choose <em>Parcella plugin</em> and enter these two values. Drafts arrive here as unpublished content; publishing stays your decision.') . '</p>',
    ];
    $form['endpoint'] = [
      '#type' => 'textfield',
      '#title' => $this->t('Plugin address'),
      '#value' => $endpoint,
      '#attributes' => ['readonly' => 'readonly'],
    ];
    $form['secret'] = [
      '#type' => 'textfield',
      '#title' => $this->t('Shared secret'),
      '#value' => (string) $config->get('secret'),
      '#attributes' => ['readonly' => 'readonly', 'autocomplete' => 'off'],
      '#description' => $this->t('Parcella signs every request with it. Treat it like a password.'),
    ];
    $form['regenerate'] = [
      '#type' => 'checkbox',
      '#title' => $this->t('Generate a new secret when saving'),
      '#description' => $this->t('The old one stops working at once; enter the new one in Parcella.'),
    ];

    $types = [];
    foreach ($this->entityTypeManager()->getStorage('node_type')->loadMultiple() as $type) {
      $types[$type->id()] = $type->label();
    }
    $form['node_type'] = [
      '#type' => 'select',
      '#title' => $this->t('Content type for drafts'),
      '#options' => $types,
      '#default_value' => $config->get('node_type'),
    ];
    $form['body_field'] = [
      '#type' => 'textfield',
      '#title' => $this->t('Field for the text'),
      '#default_value' => $config->get('body_field') ?: 'body',
      '#description' => $this->t('Machine name of a formatted text field on that content type, usually "body".'),
      '#required' => TRUE,
    ];
    $form['image_field'] = [
      '#type' => 'textfield',
      '#title' => $this->t('Field for the image'),
      '#default_value' => $config->get('image_field') ?: 'field_image',
      '#description' => $this->t('Machine name of an image field, usually "field_image". Optional: without it, drafts arrive without an image.'),
    ];
    $formats = [];
    foreach (filter_formats() as $format) {
      $formats[$format->id()] = $format->label();
    }
    $form['text_format'] = [
      '#type' => 'select',
      '#title' => $this->t('Text format'),
      '#options' => $formats,
      '#default_value' => $config->get('text_format'),
    ];
    $author = User::load((int) $config->get('author_uid'));
    $form['author_uid'] = [
      '#type' => 'entity_autocomplete',
      '#title' => $this->t('Author of new drafts'),
      '#target_type' => 'user',
      '#default_value' => $author,
      '#required' => TRUE,
    ];

    return parent::buildForm($form, $form_state);
  }

  public function validateForm(array &$form, FormStateInterface $form_state): void {
    $type = (string) $form_state->getValue('node_type');
    $fields = \Drupal::service('entity_field.manager')->getFieldDefinitions('node', $type);
    $body = (string) $form_state->getValue('body_field');
    if (!isset($fields[$body]) || !in_array($fields[$body]->getType(), ['text_with_summary', 'text_long', 'text'], TRUE)) {
      $form_state->setErrorByName('body_field', $this->t('"@field" is not a text field of this content type.', ['@field' => $body]));
    }
    $image = (string) $form_state->getValue('image_field');
    if ($image !== '' && (!isset($fields[$image]) || $fields[$image]->getType() !== 'image')) {
      $form_state->setErrorByName('image_field', $this->t('"@field" is not an image field of this content type.', ['@field' => $image]));
    }
    parent::validateForm($form, $form_state);
  }

  public function submitForm(array &$form, FormStateInterface $form_state): void {
    $config = $this->config('parcella_connector.settings')
      ->set('node_type', $form_state->getValue('node_type'))
      ->set('text_format', $form_state->getValue('text_format'))
      ->set('body_field', $form_state->getValue('body_field'))
      ->set('image_field', $form_state->getValue('image_field'))
      ->set('author_uid', (int) $form_state->getValue('author_uid'));
    if ($form_state->getValue('regenerate') || strlen((string) $config->get('secret')) < 32) {
      $config->set('secret', ParcellaProtocol::generateSecret());
    }
    $config->save();
    parent::submitForm($form, $form_state);
  }

}

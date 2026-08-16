<?php
/**
 * Contact module -- renders the [parcella_contact_form] shortcode,
 * backed by Parcella's public contact API. Unlike signup.php, this
 * form's submission creates a Parcella ticket directly instead of
 * sending a plain email -- see docs/ADR (contact-form-to-ticket
 * bridge) on the Parcella side.
 *
 * All calls to Parcella happen server-side in PHP, so the API token
 * never reaches the visitor's browser.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

/**
 * Submits a contact-form message. Server-side POST, so the API token
 * is attached here and never sent to (or seen by) the visitor's browser.
 */
function parcella_connector_contact_submit($payload) {
    $base_url = parcella_connector_base_url();
    $token = parcella_connector_api_token();
    if (empty($base_url) || empty($token)) {
        return ['error' => __('This form is not fully configured yet. Please contact the site administrator.', 'parcella-connector')];
    }

    $response = wp_remote_post($base_url . '/api/v1/public/contact', [
        'timeout' => 10,
        'headers' => [
            'Content-Type' => 'application/json',
            'X-Parcella-API-Token' => $token,
        ],
        'body' => wp_json_encode($payload),
    ]);

    if (is_wp_error($response)) {
        return ['error' => __('Could not reach Parcella. Please try again later.', 'parcella-connector')];
    }

    $status = wp_remote_retrieve_response_code($response);
    $body = json_decode(wp_remote_retrieve_body($response), true);

    if ($status === 401) {
        return ['error' => __('This form is not correctly configured (invalid API token). Please contact the site administrator.', 'parcella-connector')];
    }
    if ($status === 429) {
        return ['error' => __('Too many submissions right now. Please try again in a little while.', 'parcella-connector')];
    }
    if ($status !== 200 || !is_array($body)) {
        return ['error' => __('Something went wrong submitting your message. Please try again later.', 'parcella-connector')];
    }
    // A 200 response can still be a logical rejection (e.g. missing
    // consent) -- Parcella reports that via accepted=false rather than
    // an HTTP error status, same convention as the signup endpoint's
    // per-session accepted flags.
    if (empty($body['accepted'])) {
        return ['error' => !empty($body['reason'])
            ? $body['reason']
            : __('Your message could not be submitted. Please check the form and try again.', 'parcella-connector')];
    }

    return ['success' => true];
}

// ---------------------------------------------------------------------------
// Shortcode: [parcella_contact_form]
// ---------------------------------------------------------------------------

add_shortcode('parcella_contact_form', 'parcella_connector_contact_render_shortcode');

function parcella_connector_contact_render_shortcode($atts) {
    $feedback = null;

    if (
        isset($_POST['parcella_contact_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['parcella_contact_nonce'])), 'parcella_contact_submit')
    ) {
        $payload = [
            'name' => sanitize_text_field(wp_unslash($_POST['parcella_contact_name'] ?? '')),
            'email' => sanitize_email(wp_unslash($_POST['parcella_contact_email'] ?? '')),
            'message' => sanitize_textarea_field(wp_unslash($_POST['parcella_contact_message'] ?? '')),
            'consent' => isset($_POST['parcella_contact_consent']),
            // Honeypot: a hidden field real visitors never fill in (see
            // the CSS below). Forwarded as-is; Parcella itself decides
            // what to do with a filled-in value.
            'website' => sanitize_text_field(wp_unslash($_POST['website'] ?? '')),
        ];

        if (empty($payload['name']) || empty($payload['email']) || empty($payload['message'])) {
            $feedback = ['error' => __('Please fill in your name, email address, and message.', 'parcella-connector')];
        } elseif (!$payload['consent']) {
            $feedback = ['error' => __('Please confirm you have read the privacy policy to submit this form.', 'parcella-connector')];
        } else {
            $feedback = parcella_connector_contact_submit($payload);
        }
    }

    ob_start();
    ?>
    <div class="parcella-contact-form">
        <?php if ($feedback && isset($feedback['error'])): ?>
            <div class="parcella-contact-message parcella-contact-error"><?php echo esc_html($feedback['error']); ?></div>
        <?php elseif ($feedback && isset($feedback['success'])): ?>
            <div class="parcella-contact-message parcella-contact-success">
                <?php esc_html_e('Thank you, your message has been received. We will get back to you soon.', 'parcella-connector'); ?>
            </div>
        <?php endif; ?>

        <?php if (!$feedback || isset($feedback['error'])): ?>
        <form method="post" class="parcella-contact-form-form">
            <?php wp_nonce_field('parcella_contact_submit', 'parcella_contact_nonce'); ?>

            <p>
                <label for="parcella-contact-name"><?php esc_html_e('Name', 'parcella-connector'); ?> *</label><br>
                <input type="text" id="parcella-contact-name" name="parcella_contact_name" required
                       value="<?php echo isset($_POST['parcella_contact_name']) ? esc_attr(sanitize_text_field(wp_unslash($_POST['parcella_contact_name']))) : ''; ?>">
            </p>

            <p>
                <label for="parcella-contact-email"><?php esc_html_e('Email address', 'parcella-connector'); ?> *</label><br>
                <input type="email" id="parcella-contact-email" name="parcella_contact_email" required
                       value="<?php echo isset($_POST['parcella_contact_email']) ? esc_attr(sanitize_email(wp_unslash($_POST['parcella_contact_email']))) : ''; ?>">
            </p>

            <p>
                <label for="parcella-contact-message"><?php esc_html_e('Message', 'parcella-connector'); ?> *</label><br>
                <textarea id="parcella-contact-message" name="parcella_contact_message" rows="6" required><?php echo isset($_POST['parcella_contact_message']) ? esc_textarea(sanitize_textarea_field(wp_unslash($_POST['parcella_contact_message']))) : ''; ?></textarea>
            </p>

            <p>
                <label>
                    <input type="checkbox" name="parcella_contact_consent" value="1" required>
                    <?php esc_html_e("I have read the privacy policy and understand that my data will inevitably have to be processed electronically when I submit this contact form, as this is simply the nature of the process.", 'parcella-connector'); ?>
                </label>
            </p>

            <!--
                Honeypot field: hidden from real visitors via CSS and
                kept out of the tab order / accessibility tree, but
                still present in the markup for simple bots that fill
                in every field they find.
            -->
            <p class="parcella-contact-hp" aria-hidden="true">
                <label for="parcella-contact-website"><?php esc_html_e('Leave this field empty', 'parcella-connector'); ?></label>
                <input type="text" id="parcella-contact-website" name="website" tabindex="-1" autocomplete="off">
            </p>

            <p>
                <button type="submit" class="parcella-contact-submit"><?php esc_html_e('Send message', 'parcella-connector'); ?></button>
            </p>
        </form>
        <?php endif; ?>
    </div>
    <style>
        .parcella-contact-hp { position: absolute; left: -9999px; }
        .parcella-contact-message { padding: 0.75em 1em; margin-bottom: 1em; border-radius: 4px; }
        .parcella-contact-success { background: #e6f4ea; color: #1e4620; }
        .parcella-contact-error { background: #fdecea; color: #611a15; }
        .parcella-contact-submit {
            font-size: 1.15em;
            font-weight: 600;
            padding: 0.6em 1.6em;
            background: #2d6a4f;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .parcella-contact-submit:hover {
            background: #40916c;
        }
    </style>
    <?php
    return ob_get_clean();
}

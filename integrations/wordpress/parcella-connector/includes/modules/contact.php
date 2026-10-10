<?php
/**
 * Contact module -- renders the [parcella_contact_form] shortcode. A
 * submission becomes a conversation in the club's FreeScout inbox (via
 * Parcella's public contact API) instead of a plain email -- see
 * docs/module-freescout-bridge.md on the Parcella side.
 *
 * The form is posted by the visitor's browser straight to Parcella's
 * plain-HTML-form endpoint (POST /api/v1/public/forms/contact), which
 * redirects back here with the outcome in the URL fragment -- see the
 * shared form helpers in the main plugin file.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

// ---------------------------------------------------------------------------
// Shortcode: [parcella_contact_form]
// ---------------------------------------------------------------------------

add_shortcode('parcella_contact_form', 'parcella_connector_contact_render_shortcode');

function parcella_connector_contact_outcome_messages() {
    return [
        'ok' => __('Thank you, your message has been received. We will get back to you soon.', 'parcella-connector'),
        'consent_missing' => __('Please confirm you have read the privacy policy to submit this form.', 'parcella-connector'),
        'invalid' => __('Please fill in your name, email address, and message.', 'parcella-connector'),
        'rate_limited' => __('Too many submissions right now. Please try again in a little while.', 'parcella-connector'),
        'unavailable' => __('Your message could not be submitted right now. Please try again later.', 'parcella-connector'),
        'captcha' => __('The spam protection check failed. Please reload the page and try again.', 'parcella-connector'),
        'error' => __('Something went wrong submitting your message. Please try again later.', 'parcella-connector'),
    ];
}

function parcella_connector_contact_render_shortcode($atts) {
    // The page carries a per-visit outcome (?parcella_form=contact) and the
    // ALTCHA widget; a full-page cache has nothing useful to keep here.
    parcella_connector_disable_page_cache();

    ob_start();
    ?>
    <div class="parcella-contact-form">
        <?php parcella_connector_render_outcome('contact', parcella_connector_contact_outcome_messages()); ?>

        <form method="post" class="parcella-contact-form-form" action="<?php echo esc_url(parcella_connector_form_action('contact')); ?>">
            <p>
                <label for="parcella-contact-name"><?php esc_html_e('Name', 'parcella-connector'); ?> *</label><br>
                <input type="text" id="parcella-contact-name" name="name" required>
            </p>

            <p>
                <label for="parcella-contact-email"><?php esc_html_e('Email address', 'parcella-connector'); ?> *</label><br>
                <input type="email" id="parcella-contact-email" name="email" required>
            </p>

            <p>
                <label for="parcella-contact-message"><?php esc_html_e('Message', 'parcella-connector'); ?> *</label><br>
                <textarea id="parcella-contact-message" name="message" rows="6" required></textarea>
            </p>

            <p>
                <label>
                    <input type="checkbox" name="consent" value="1" required>
                    <?php esc_html_e("I have read the privacy policy and understand that my data will inevitably have to be processed electronically when I submit this contact form, as this is simply the nature of the process.", 'parcella-connector'); ?>
                </label>
            </p>

            <?php parcella_connector_render_common_fields('contact'); ?>
            <?php parcella_connector_render_altcha(); ?>

            <p>
                <button type="submit" class="parcella-submit parcella-contact-submit"><?php esc_html_e('Send message', 'parcella-connector'); ?></button>
            </p>
        </form>
    </div>
    <?php
    parcella_connector_render_form_styles();
    return ob_get_clean();
}

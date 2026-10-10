<?php
/**
 * Applicants module -- renders the [parcella_applicant_form] shortcode:
 * an application form for a free garden plot. A submission lands in
 * Parcella's applicants list (docs/module-applicants.md on the Parcella
 * side) for the board to follow up.
 *
 * Posted by the visitor's browser straight to Parcella's plain-HTML-form
 * endpoint (POST /api/v1/public/forms/applicant), which redirects back
 * here with the outcome in the URL fragment -- see the shared form
 * helpers in the main plugin file. Only the email address is required.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

add_shortcode('parcella_applicant_form', 'parcella_connector_applicants_render_shortcode');

function parcella_connector_applicants_outcome_messages() {
    return [
        'ok' => __('Thank you, your application has been received. We will get in touch with you.', 'parcella-connector'),
        'consent_missing' => __('Please confirm you have read the privacy policy to submit this form.', 'parcella-connector'),
        'invalid' => __('Please enter a valid email address.', 'parcella-connector'),
        'rate_limited' => __('Too many submissions right now. Please try again in a little while.', 'parcella-connector'),
        'captcha' => __('The spam protection check failed. Please reload the page and try again.', 'parcella-connector'),
        'error' => __('Something went wrong submitting your application. Please try again later.', 'parcella-connector'),
    ];
}

function parcella_connector_applicants_render_shortcode($atts) {
    // Per-visit outcome (?parcella_form=applicant) and the ALTCHA widget --
    // nothing a full-page cache should keep.
    parcella_connector_disable_page_cache();

    ob_start();
    ?>
    <div class="parcella-applicant-form">
        <?php parcella_connector_render_outcome('applicant', parcella_connector_applicants_outcome_messages()); ?>

        <form method="post" class="parcella-applicant-form-form" action="<?php echo esc_url(parcella_connector_form_action('applicant')); ?>">
            <p>
                <label for="parcella-applicant-email"><?php esc_html_e('Email address', 'parcella-connector'); ?> *</label><br>
                <input type="email" id="parcella-applicant-email" name="email" required autocomplete="email">
            </p>

            <p>
                <label for="parcella-applicant-first-name"><?php esc_html_e('First name', 'parcella-connector'); ?></label><br>
                <input type="text" id="parcella-applicant-first-name" name="first_name" autocomplete="given-name">
            </p>

            <p>
                <label for="parcella-applicant-last-name"><?php esc_html_e('Last name', 'parcella-connector'); ?></label><br>
                <input type="text" id="parcella-applicant-last-name" name="last_name" autocomplete="family-name">
            </p>

            <p>
                <label for="parcella-applicant-phone"><?php esc_html_e('Phone', 'parcella-connector'); ?></label><br>
                <input type="tel" id="parcella-applicant-phone" name="phone" autocomplete="tel">
            </p>

            <p>
                <label for="parcella-applicant-message"><?php esc_html_e('Anything you would like to tell us?', 'parcella-connector'); ?></label><br>
                <textarea id="parcella-applicant-message" name="message" rows="5"></textarea>
            </p>

            <p>
                <label>
                    <input type="checkbox" name="consent" value="1" required>
                    <?php esc_html_e('I have read the privacy policy and agree that my details are stored and processed electronically to handle my application for a garden plot.', 'parcella-connector'); ?>
                </label>
            </p>

            <?php parcella_connector_render_common_fields('applicant'); ?>
            <?php parcella_connector_render_altcha(); ?>

            <p>
                <button type="submit" class="parcella-submit parcella-applicant-submit"><?php esc_html_e('Send application', 'parcella-connector'); ?></button>
            </p>
        </form>
    </div>
    <?php
    parcella_connector_render_form_styles();
    return ob_get_clean();
}

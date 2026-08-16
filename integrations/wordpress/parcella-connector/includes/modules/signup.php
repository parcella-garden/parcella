<?php
/**
 * Signup module -- renders the [parcella_work_signup] shortcode, backed
 * by Parcella's public signup API. Uses parcella_connector_base_url()
 * and parcella_connector_api_token() from the main plugin file rather
 * than reading its own options, since the base URL/token are shared
 * across every module in this plugin.
 *
 * All calls to Parcella happen server-side in PHP, so the API token
 * never reaches the visitor's browser.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

// ---------------------------------------------------------------------------
// Helpers: talk to Parcella
// ---------------------------------------------------------------------------

/**
 * Fetches upcoming sessions / parcels, cached briefly in a transient so a
 * busy page doesn't hit Parcella on every single page view. Read-only,
 * unauthenticated calls -- matches Parcella's public GET endpoints.
 */
function parcella_connector_signup_fetch_json($path, $cache_key, $cache_seconds) {
    $cached = get_transient($cache_key);
    if ($cached !== false) {
        return $cached;
    }

    $base_url = parcella_connector_base_url();
    if (empty($base_url)) {
        return null;
    }

    $response = wp_remote_get($base_url . $path, ['timeout' => 8]);
    if (is_wp_error($response) || wp_remote_retrieve_response_code($response) !== 200) {
        return null;
    }

    $data = json_decode(wp_remote_retrieve_body($response), true);
    if (!is_array($data)) {
        return null;
    }

    set_transient($cache_key, $data, $cache_seconds);
    return $data;
}

function parcella_connector_signup_fetch_sessions() {
    return parcella_connector_signup_fetch_json('/api/v1/public/work-sessions/upcoming', 'parcella_connector_signup_sessions', 60);
}

function parcella_connector_signup_fetch_parcels() {
    return parcella_connector_signup_fetch_json('/api/v1/public/parcels', 'parcella_connector_signup_parcels', 3600);
}

/**
 * Submits a signup. Server-side POST, so the API token is attached here
 * and never sent to (or seen by) the visitor's browser.
 */
function parcella_connector_signup_submit($payload) {
    $base_url = parcella_connector_base_url();
    $token = parcella_connector_api_token();
    if (empty($base_url) || empty($token)) {
        return ['error' => __('This form is not fully configured yet. Please contact the site administrator.', 'parcella-connector')];
    }

    $response = wp_remote_post($base_url . '/api/v1/public/work-sessions/signup', [
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
    if ($status === 404 && is_array($body)) {
        return ['error' => __('That parcel number was not found. Please check it and try again.', 'parcella-connector')];
    }
    if ($status !== 200 || !is_array($body)) {
        return ['error' => __('Something went wrong submitting your signup. Please try again later.', 'parcella-connector')];
    }

    return ['result' => $body];
}

// ---------------------------------------------------------------------------
// Shortcode: [parcella_work_signup]
//
// The shortcode tag itself is unchanged from the original plugin --
// existing pages/posts using it keep working without any edits after
// upgrading to this consolidated plugin.
// ---------------------------------------------------------------------------

add_shortcode('parcella_work_signup', 'parcella_connector_signup_render_shortcode');

function parcella_connector_signup_render_shortcode($atts) {
    $feedback = null;

    if (
        isset($_POST['parcella_signup_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['parcella_signup_nonce'])), 'parcella_signup_submit')
    ) {
        $session_ids = isset($_POST['session_ids']) && is_array($_POST['session_ids'])
            ? array_map('sanitize_text_field', wp_unslash($_POST['session_ids']))
            : [];

        $payload = [
            'parcel_number' => sanitize_text_field(wp_unslash($_POST['parcel_number'] ?? '')),
            'name' => sanitize_text_field(wp_unslash($_POST['parcella_signup_name'] ?? '')),
            'remarks' => sanitize_textarea_field(wp_unslash($_POST['remarks'] ?? '')),
            'session_ids' => $session_ids,
            // Honeypot: a hidden field real visitors never fill in (see
            // the CSS below). Forwarded as-is; Parcella itself decides
            // what to do with a filled-in value.
            'website' => sanitize_text_field(wp_unslash($_POST['website'] ?? '')),
        ];

        if (empty($payload['parcel_number']) || empty($payload['session_ids'])) {
            $feedback = ['error' => __('Please provide a parcel number and select at least one session.', 'parcella-connector')];
        } else {
            $feedback = parcella_connector_signup_submit($payload);
            // Signup lists may have changed capacity -- drop the cached
            // session list so the form reflects it on next render.
            delete_transient('parcella_connector_signup_sessions');
        }
    }

    $sessions = parcella_connector_signup_fetch_sessions();
    $parcels = parcella_connector_signup_fetch_parcels();

    ob_start();
    ?>
    <div class="parcella-work-signup">
        <?php if ($sessions === null || $parcels === null): ?>
            <p><?php esc_html_e('The signup form is temporarily unavailable. Please try again later.', 'parcella-connector'); ?></p>
        <?php else: ?>

            <?php if ($feedback && isset($feedback['error'])): ?>
                <div class="parcella-signup-message parcella-signup-error"><?php echo esc_html($feedback['error']); ?></div>
            <?php elseif ($feedback && isset($feedback['result'])): ?>
                <?php
                $any_accepted = false;
                $any_rejected = false;
                foreach ($feedback['result']['results'] as $r) {
                    if ($r['accepted']) { $any_accepted = true; } else { $any_rejected = true; }
                }
                ?>
                <?php if ($any_accepted): ?>
                    <div class="parcella-signup-message parcella-signup-success">
                        <?php esc_html_e('Thank you, your signup has been received.', 'parcella-connector'); ?>
                    </div>
                <?php endif; ?>
                <?php if ($any_rejected): ?>
                    <div class="parcella-signup-message parcella-signup-error">
                        <?php esc_html_e('Some of the selected sessions could not be booked (likely full). Please choose another date for those.', 'parcella-connector'); ?>
                    </div>
                <?php endif; ?>
            <?php endif; ?>

            <?php if (empty($sessions)): ?>
                <p><?php esc_html_e('There are currently no upcoming work sessions open for signup.', 'parcella-connector'); ?></p>
            <?php else: ?>
            <form method="post" class="parcella-signup-form">
                <?php wp_nonce_field('parcella_signup_submit', 'parcella_signup_nonce'); ?>

                <p>
                    <label for="parcella-name"><?php esc_html_e('Name', 'parcella-connector'); ?></label><br>
                    <!--
                        Field is deliberately NOT called "name": WordPress
                        treats "name" as a reserved core query variable
                        (used to look up a post/page by slug). A POST
                        field literally called "name" gets picked up by
                        WP::parse_request() and WordPress tries to find a
                        page with that slug instead of just rendering
                        this page's own content -- which 404s the moment
                        this field is non-empty. Namespacing it avoids
                        the collision entirely.
                    -->
                    <input type="text" id="parcella-name" name="parcella_signup_name">
                </p>

                <p>
                    <label for="parcella-parcel"><?php esc_html_e('Parcel number', 'parcella-connector'); ?> *</label><br>
                    <select id="parcella-parcel" name="parcel_number" required>
                        <option value=""><?php esc_html_e('Please choose...', 'parcella-connector'); ?></option>
                        <?php foreach ($parcels as $parcel): ?>
                            <option value="<?php echo esc_attr($parcel['plot_number']); ?>">
                                <?php echo esc_html($parcel['plot_number']); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </p>

                <p>
                    <?php esc_html_e('I would like to sign up for the following work sessions:', 'parcella-connector'); ?><br>
                    <?php foreach ($sessions as $session): ?>
                        <label style="display:block;">
                            <input type="checkbox" name="session_ids[]" value="<?php echo esc_attr($session['id']); ?>">
                            <?php
                            echo esc_html(
                                sprintf(
                                    /* translators: 1: date, 2: start time, 3: end time, 4: session title */
                                    __('%1$s, %2$s - %3$s %4$s', 'parcella-connector'),
                                    date_i18n(get_option('date_format'), strtotime($session['date'])),
                                    $session['time_from'] ?? '',
                                    $session['time_until'] ?? '',
                                    $session['title']
                                )
                            );
                            if (isset($session['spots_left']) && $session['spots_left'] !== null) {
                                echo ' ' . esc_html(sprintf(
                                    /* translators: %d: number of remaining spots */
                                    _n('(%d spot left)', '(%d spots left)', $session['spots_left'], 'parcella-connector'),
                                    $session['spots_left']
                                ));
                            }
                            ?>
                        </label>
                    <?php endforeach; ?>
                </p>

                <p>
                    <label for="parcella-remarks"><?php esc_html_e('Remarks or individual session requests', 'parcella-connector'); ?></label><br>
                    <textarea id="parcella-remarks" name="remarks" rows="3"></textarea>
                </p>

                <!--
                    Honeypot field: hidden from real visitors via CSS and
                    kept out of the tab order / accessibility tree, but
                    still present in the markup for simple bots that fill
                    in every field they find.
                -->
                <p class="parcella-signup-hp" aria-hidden="true">
                    <label for="parcella-website"><?php esc_html_e('Leave this field empty', 'parcella-connector'); ?></label>
                    <input type="text" id="parcella-website" name="website" tabindex="-1" autocomplete="off">
                </p>

                <p>
                    <button type="submit" class="parcella-signup-submit"><?php esc_html_e('Sign up', 'parcella-connector'); ?></button>
                </p>
            </form>
            <?php endif; ?>
        <?php endif; ?>
    </div>
    <style>
        .parcella-signup-hp { position: absolute; left: -9999px; }
        .parcella-signup-message { padding: 0.75em 1em; margin-bottom: 1em; border-radius: 4px; }
        .parcella-signup-success { background: #e6f4ea; color: #1e4620; }
        .parcella-signup-submit {
            font-size: 1.15em;
            font-weight: 600;
            padding: 0.6em 1.6em;
            background: #2d6a4f;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .parcella-signup-submit:hover {
            background: #40916c;
        }
        .parcella-signup-error { background: #fdecea; color: #611a15; }
    </style>
    <?php
    return ob_get_clean();
}

<?php
/**
 * Signup module -- renders the [parcella_work_signup] shortcode, backed
 * by Parcella's public signup API. Uses parcella_connector_base_url()
 * and the shared form helpers from the main plugin file rather than
 * reading its own options.
 *
 * The session and parcel lists are fetched server-side (unauthenticated
 * read endpoints, cached briefly). The form itself is posted by the
 * visitor's browser straight to Parcella's plain-HTML-form endpoint
 * (POST /api/v1/public/forms/work-session-signup), which redirects back
 * here with the outcome in the URL fragment -- see the main plugin file.
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

// ---------------------------------------------------------------------------
// Shortcode: [parcella_work_signup]
//
// The shortcode tag itself is unchanged from the original plugin --
// existing pages/posts using it keep working without any edits after
// upgrading.
// ---------------------------------------------------------------------------

add_shortcode('parcella_work_signup', 'parcella_connector_signup_render_shortcode');

function parcella_connector_signup_outcome_messages() {
    $retry = __('Please choose another date, or contact us directly.', 'parcella-connector');
    return [
        'ok' => __('Thank you, your signup has been received.', 'parcella-connector'),
        'partial' => __('Thank you, your signup has been received. Some of the selected sessions could not be booked, though (they may be full or no longer accepting signups). Please choose another date for those, or contact us directly.', 'parcella-connector'),
        'session_full' => __('The selected session is already full.', 'parcella-connector') . ' ' . $retry,
        'registration_closed' => __('Registration for the selected session has closed.', 'parcella-connector') . ' ' . $retry,
        'session_not_found' => __('The selected session is no longer available.', 'parcella-connector') . ' ' . $retry,
        'no_members_for_parcel' => __('No members are currently assigned to this parcel. Please contact us directly.', 'parcella-connector'),
        'unknown_parcel' => __('That parcel number was not found. Please check it and try again.', 'parcella-connector'),
        'no_session_selected' => __('Please provide a parcel number and select at least one session.', 'parcella-connector'),
        'invalid' => __('Please check your entries and try again.', 'parcella-connector'),
        'rate_limited' => __('Too many submissions right now. Please try again in a little while.', 'parcella-connector'),
        'captcha' => __('The spam protection check failed. Please reload the page and try again.', 'parcella-connector'),
        'error' => __('Something went wrong submitting your signup. Please try again later.', 'parcella-connector'),
    ];
}

function parcella_connector_signup_render_shortcode($atts) {
    parcella_connector_disable_page_cache();

    // Coming back from a signup: capacities may have changed, so don't
    // show the cached session list from before it.
    if (parcella_connector_returned_from('signup')) {
        delete_transient('parcella_connector_signup_sessions');
    }

    $sessions = parcella_connector_signup_fetch_sessions();
    $parcels = parcella_connector_signup_fetch_parcels();

    ob_start();
    ?>
    <div class="parcella-work-signup">
        <?php if ($sessions === null || $parcels === null): ?>
            <p><?php esc_html_e('The signup form is temporarily unavailable. Please try again later.', 'parcella-connector'); ?></p>
        <?php else: ?>

            <?php parcella_connector_render_outcome('signup', parcella_connector_signup_outcome_messages()); ?>

            <?php if (empty($sessions)): ?>
                <p><?php esc_html_e('There are currently no upcoming work sessions open for signup.', 'parcella-connector'); ?></p>
            <?php else: ?>
            <form method="post" class="parcella-signup-form" action="<?php echo esc_url(parcella_connector_form_action('work-session-signup')); ?>">
                <p>
                    <label for="parcella-name"><?php esc_html_e('Name', 'parcella-connector'); ?></label><br>
                    <input type="text" id="parcella-name" name="name">
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
                            <input type="checkbox" name="session_ids" value="<?php echo esc_attr($session['id']); ?>">
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

                <?php parcella_connector_render_common_fields('signup'); ?>
                <?php parcella_connector_render_altcha(); ?>

                <p>
                    <button type="submit" class="parcella-submit parcella-signup-submit"><?php esc_html_e('Sign up', 'parcella-connector'); ?></button>
                </p>
            </form>
            <?php endif; ?>
        <?php endif; ?>
    </div>
    <?php
    parcella_connector_render_form_styles();
    return ob_get_clean();
}

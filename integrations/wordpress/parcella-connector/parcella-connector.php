<?php
/**
 * Plugin Name: Parcella Connector
 * Description: Consolidated connector for every integration between this WordPress site and a Parcella installation. Each capability lives in its own module under includes/modules/ (work-session signup, community calendar, a contact form that lands in the club's FreeScout inbox, and an application form for free garden plots), sharing one Parcella base URL configured here.
 * Version: 3.1.0
 * License: AGPL-3.0-or-later
 * Text Domain: parcella-connector
 *
 * This plugin is intentionally a thin client for every module it
 * contains: no business logic (capacity checks, matching, validation,
 * ticket routing, etc.) lives here -- all of that lives in Parcella
 * itself, behind the same kind of API contract any other CMS connector
 * would use. See the relevant docs/module-*.md file in the Parcella
 * repository for each module's contract.
 *
 * History: this plugin began life as "Parcella Work Session Signup", a
 * single-purpose connector. As more WordPress <-> Parcella
 * integrations were planned, it was consolidated into this one plugin
 * so every future integration shares one settings screen, rather than
 * each shipping its own plugin with its own separate credentials to
 * configure. The base URL's option name was deliberately kept
 * unchanged (parcella_signup_base_url) specifically so upgrading from
 * the old plugin doesn't require re-entering it -- see README.md for
 * the exact upgrade steps.
 *
 * Since 3.0.0 the forms no longer post to WordPress and on to Parcella
 * with a shared API token: the visitor's browser posts them straight to
 * Parcella's plain-HTML-form endpoints, exactly like a form on any
 * other website (see docs/ADR/0090 in the Parcella repository). That
 * gives every website one form contract -- same fields, same ALTCHA
 * spam protection, same rate limit per visitor -- and leaves this
 * plugin with no secret to keep.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

// Kept in sync with the "Version:" header above (was drifted at 2.0.0
// from a previous release that forgot to update this constant too --
// unused elsewhere today, but there's no reason to let it lie).
define('PARCELLA_CONNECTOR_VERSION', '3.1.0');
// Name unchanged from the original single-purpose plugin on purpose --
// see the History note above.
define('PARCELLA_CONNECTOR_OPTION_BASE_URL', 'parcella_signup_base_url');
// The API token 2.x stored. No longer used; deleted on upgrade so a
// secret doesn't linger in the WordPress database.
define('PARCELLA_CONNECTOR_OPTION_LEGACY_API_TOKEN', 'parcella_signup_api_token');
define('PARCELLA_CONNECTOR_PATH', plugin_dir_path(__FILE__));
define('PARCELLA_CONNECTOR_URL', plugin_dir_url(__FILE__));

// Loads translations from languages/parcella-connector-{locale}.mo.
// Falls back to the English strings in this file automatically if no
// matching .mo file exists.
add_action('plugins_loaded', function () {
    load_plugin_textdomain('parcella-connector', false, dirname(plugin_basename(__FILE__)) . '/languages');
});

// ---------------------------------------------------------------------------
// Shared settings page (Settings -> Parcella Connector)
// One base URL here, shared by every module below -- a module never
// renders its own copy of this field.
// ---------------------------------------------------------------------------

add_action('admin_menu', function () {
    add_options_page(
        __('Parcella Connector', 'parcella-connector'),
        __('Parcella Connector', 'parcella-connector'),
        'manage_options',
        'parcella-connector',
        'parcella_connector_render_settings_page'
    );
});

add_action('admin_init', function () {
    register_setting('parcella_connector_settings', PARCELLA_CONNECTOR_OPTION_BASE_URL, [
        'sanitize_callback' => function ($value) {
            return untrailingslashit(esc_url_raw(trim($value)));
        },
    ]);
    if (get_option(PARCELLA_CONNECTOR_OPTION_LEGACY_API_TOKEN) !== false) {
        delete_option(PARCELLA_CONNECTOR_OPTION_LEGACY_API_TOKEN);
    }
});

function parcella_connector_base_url() {
    return get_option(PARCELLA_CONNECTOR_OPTION_BASE_URL, '');
}

/**
 * This site's origin (scheme://host[:port]) -- what Parcella has to list
 * under Administration -> Integrations -> "Allowed website origins" before
 * it accepts this site's forms.
 */
function parcella_connector_site_origin() {
    $parts = wp_parse_url(home_url());
    if (empty($parts['scheme']) || empty($parts['host'])) {
        return '';
    }
    $origin = strtolower($parts['scheme'] . '://' . $parts['host']);
    return isset($parts['port']) ? $origin . ':' . $parts['port'] : $origin;
}

// ---------------------------------------------------------------------------
// Shared form helpers. The forms post straight from the visitor's browser
// to Parcella's /api/v1/public/forms/* endpoints; Parcella answers with a
// redirect back to this page, carrying the outcome as the URL fragment
// (#ok, #session_full, #captcha, ...). The page shows the matching
// message with CSS :target alone -- no JavaScript needed for that part.
// ---------------------------------------------------------------------------

function parcella_connector_form_action($endpoint) {
    return parcella_connector_base_url() . '/api/v1/public/forms/' . $endpoint;
}

/**
 * Where Parcella sends the visitor back to: this page, tagged with which
 * form was submitted, so only that form's messages are rendered -- the
 * outcome codes are used as element ids, and two shortcodes on one page
 * would otherwise both carry e.g. id="ok".
 */
function parcella_connector_return_url($form) {
    $base = is_singular() ? get_permalink() : home_url('/');
    return add_query_arg('parcella_form', $form, remove_query_arg('parcella_form', $base));
}

function parcella_connector_returned_from($form) {
    return isset($_GET['parcella_form']) && sanitize_key(wp_unslash($_GET['parcella_form'])) === $form;
}

/**
 * The outcome messages for one form, rendered only when the visitor has
 * just come back from submitting that form. Each one is hidden until its
 * id matches the URL fragment.
 *
 * @param string $form     'signup' or 'contact'
 * @param array  $messages outcome code => message; 'ok' and 'partial' are
 *                         successes, everything else an error
 */
function parcella_connector_render_outcome($form, $messages) {
    if (!parcella_connector_returned_from($form)) {
        return;
    }
    echo '<div class="parcella-outcome">';
    foreach ($messages as $code => $text) {
        $kind = in_array($code, ['ok', 'partial'], true) ? 'success' : 'error';
        printf(
            '<p id="%1$s" class="parcella-outcome-message parcella-outcome-%2$s" role="status">%3$s</p>',
            esc_attr($code), esc_attr($kind), esc_html($text)
        );
    }
    echo '</div>';
}

/**
 * The hidden fields every form carries: where to come back to, and the
 * honeypot -- hidden from real visitors via CSS and kept out of the tab
 * order / accessibility tree, but still present in the markup for simple
 * bots that fill in every field they find.
 */
function parcella_connector_render_common_fields($form) {
    $return_url = parcella_connector_return_url($form);
    ?>
    <input type="hidden" name="success_url" value="<?php echo esc_url($return_url); ?>">
    <input type="hidden" name="error_url" value="<?php echo esc_url($return_url); ?>">
    <p class="parcella-hp" aria-hidden="true">
        <label for="parcella-<?php echo esc_attr($form); ?>-website"><?php esc_html_e('Leave this field empty', 'parcella-connector'); ?></label>
        <input type="text" id="parcella-<?php echo esc_attr($form); ?>-website" name="website" tabindex="-1" autocomplete="off">
    </p>
    <?php
}

/**
 * The ALTCHA widget (MIT, bundled under assets/altcha/ -- no third party,
 * no cookies). Always embedded: while "Require ALTCHA" is off in Parcella
 * the solution is simply ignored, so the switch can be flipped there at
 * any time without touching this site.
 */
function parcella_connector_render_altcha() {
    wp_enqueue_script(
        'parcella-connector-altcha',
        PARCELLA_CONNECTOR_URL . 'assets/altcha/altcha.i18n.min.js',
        [], '3.2.3', true
    );
    ?>
    <altcha-widget challenge="<?php echo esc_url(parcella_connector_form_action('challenge')); ?>"
                   auto="onfocus" language="<?php echo esc_attr(substr(get_locale(), 0, 2)); ?>"
                   configuration='{"humanInteractionSignature": false}'></altcha-widget>
    <?php
}

// The bundle declares top-level consts; loading it as a module keeps them
// out of the page's global scope.
add_filter('script_loader_tag', function ($tag, $handle) {
    if ($handle === 'parcella-connector-altcha') {
        $tag = str_replace('<script ', '<script type="module" ', $tag);
    }
    return $tag;
}, 10, 2);

function parcella_connector_render_form_styles() {
    ?>
    <style>
        .parcella-hp { position: absolute; left: -9999px; }
        .parcella-outcome-message { display: none; padding: 0.75em 1em; margin-bottom: 1em; border-radius: 4px; }
        .parcella-outcome-message:target { display: block; }
        .parcella-outcome-success { background: #e6f4ea; color: #1e4620; }
        .parcella-outcome-error { background: #fdecea; color: #611a15; }
        .parcella-submit {
            font-size: 1.15em;
            font-weight: 600;
            padding: 0.6em 1.6em;
            background: #2d6a4f;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .parcella-submit:hover { background: #40916c; }
        .parcella-work-signup altcha-widget, .parcella-contact-form altcha-widget,
        .parcella-applicant-form altcha-widget { display: block; margin-bottom: 1em; }
    </style>
    <?php
}

/**
 * Best-effort opt-out from full-page caching plugins, for any page
 * rendering one of this connector's date-sensitive shortcodes (session
 * signup, community calendar). Those shortcodes fetch fresh data from
 * Parcella on every render (subject only to their own short-lived
 * transient cache -- 60s/5min, see each module) -- a full-page cache
 * plugin (WP Super Cache, WP Rocket, W3 Total Cache, WP Fastest Cache,
 * etc.) freezing the whole rendered HTML for hours/days shows stale or
 * already-passed dates until that cache happens to expire or be
 * purged, defeating the point of fetching live data at all.
 *
 * `DONOTCACHEPAGE` is the de facto standard constant respected by every
 * major caching plugin listed above -- there's no single official
 * WordPress core API for "don't cache this page", so this is the best
 * available cross-plugin signal. Call it from a shortcode's render
 * function: that runs during content generation, which is early enough
 * for every caching plugin above, since they all decide whether to
 * persist the page at output-buffer-flush time (page generation end),
 * not before the content filters run.
 */
function parcella_connector_disable_page_cache() {
    if (!defined('DONOTCACHEPAGE')) {
        define('DONOTCACHEPAGE', true);
    }
}

function parcella_connector_render_settings_page() {
    if (!current_user_can('manage_options')) {
        return;
    }
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('Parcella Connector', 'parcella-connector'); ?></h1>
        <p>
            <?php esc_html_e(
                'Shared connection settings for every Parcella integration on this site. Find the base URL on the "Integrations" page in Parcella\'s admin area (Administration -> Integrations).',
                'parcella-connector'
            ); ?>
        </p>
        <form method="post" action="options.php">
            <?php settings_fields('parcella_connector_settings'); ?>
            <table class="form-table">
                <tr>
                    <th scope="row">
                        <label for="parcella_base_url"><?php esc_html_e('Parcella base URL', 'parcella-connector'); ?></label>
                    </th>
                    <td>
                        <input type="url" id="parcella_base_url" name="<?php echo esc_attr(PARCELLA_CONNECTOR_OPTION_BASE_URL); ?>"
                               value="<?php echo esc_attr(get_option(PARCELLA_CONNECTOR_OPTION_BASE_URL, '')); ?>"
                               class="regular-text" placeholder="https://parcella.example-club.org">
                    </td>
                </tr>
                <tr>
                    <th scope="row"><?php esc_html_e('Allowed website origin', 'parcella-connector'); ?></th>
                    <td>
                        <code><?php echo esc_html(parcella_connector_site_origin()); ?></code>
                        <p class="description">
                            <?php esc_html_e('The forms on this site are sent straight from the visitor\'s browser to Parcella. Parcella only accepts them once this address is listed in its admin area under Administration -> Integrations -> "Allowed website origins".', 'parcella-connector'); ?>
                        </p>
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>

        <h2><?php esc_html_e('Modules', 'parcella-connector'); ?></h2>
        <table class="widefat" style="max-width: 700px;">
            <thead>
                <tr>
                    <th><?php esc_html_e('Module', 'parcella-connector'); ?></th>
                    <th><?php esc_html_e('Status', 'parcella-connector'); ?></th>
                    <th><?php esc_html_e('Usage', 'parcella-connector'); ?></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><?php esc_html_e('Work session signup', 'parcella-connector'); ?></td>
                    <td><span style="color: #1e4620;">&#9679; <?php esc_html_e('Active', 'parcella-connector'); ?></span></td>
                    <td><code>[parcella_work_signup]</code></td>
                </tr>
                <tr>
                    <td><?php esc_html_e('Community calendar', 'parcella-connector'); ?></td>
                    <td><span style="color: #1e4620;">&#9679; <?php esc_html_e('Active', 'parcella-connector'); ?></span></td>
                    <td><code>[parcella_calendar]</code></td>
                </tr>
                <tr>
                    <td><?php esc_html_e('Contact form', 'parcella-connector'); ?></td>
                    <td><span style="color: #1e4620;">&#9679; <?php esc_html_e('Active', 'parcella-connector'); ?></span></td>
                    <td><code>[parcella_contact_form]</code></td>
                </tr>
                <tr>
                    <td><?php esc_html_e('Garden plot applications', 'parcella-connector'); ?></td>
                    <td><span style="color: #1e4620;">&#9679; <?php esc_html_e('Active', 'parcella-connector'); ?></span></td>
                    <td><code>[parcella_applicant_form]</code></td>
                </tr>
            </tbody>
        </table>
        <p class="description">
            <?php esc_html_e('Further modules will appear in this table once added, sharing the connection settings above -- no separate settings to configure per module.', 'parcella-connector'); ?>
        </p>
    </div>
    <?php
}

// ---------------------------------------------------------------------------
// Modules
//
// Each module is a self-contained file registering whatever shortcodes,
// hooks, or admin UI it needs, using parcella_connector_base_url() and
// the shared form helpers above rather than reading its own options. To add a new module: drop a new file in includes/modules/,
// require it below, and add a row to the table above.
// ---------------------------------------------------------------------------

require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/signup.php';
require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/calendar.php';
require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/contact.php';
require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/applicants.php';

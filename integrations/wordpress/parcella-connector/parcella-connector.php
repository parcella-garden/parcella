<?php
/**
 * Plugin Name: Parcella Connector
 * Description: Consolidated connector for every integration between this WordPress site and a Parcella installation. Each capability lives in its own module under includes/modules/ (work-session signup and community calendar today; tickets, applicant management, and others are planned), sharing one Parcella base URL and API token configured here.
 * Version: 2.1.0
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
 * so every future integration shares one settings screen and one
 * base-URL/token pair, rather than each shipping its own plugin with
 * its own separate credentials to configure. The underlying WordPress
 * option names were deliberately kept unchanged
 * (parcella_signup_base_url / parcella_signup_api_token) specifically
 * so upgrading from the old plugin doesn't require re-entering them --
 * see README.md for the exact upgrade steps.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

define('PARCELLA_CONNECTOR_VERSION', '2.0.0');
// Names unchanged from the original single-purpose plugin on purpose --
// see the History note above.
define('PARCELLA_CONNECTOR_OPTION_BASE_URL', 'parcella_signup_base_url');
define('PARCELLA_CONNECTOR_OPTION_API_TOKEN', 'parcella_signup_api_token');
define('PARCELLA_CONNECTOR_PATH', plugin_dir_path(__FILE__));

// Loads translations from languages/parcella-connector-{locale}.mo.
// Falls back to the English strings in this file automatically if no
// matching .mo file exists.
add_action('plugins_loaded', function () {
    load_plugin_textdomain('parcella-connector', false, dirname(plugin_basename(__FILE__)) . '/languages');
});

// ---------------------------------------------------------------------------
// Shared settings page (Settings -> Parcella Connector)
// One base URL + one API token here, shared by every module below --
// a module never renders its own copy of these fields.
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
    register_setting('parcella_connector_settings', PARCELLA_CONNECTOR_OPTION_API_TOKEN, [
        'sanitize_callback' => 'sanitize_text_field',
    ]);
});

function parcella_connector_base_url() {
    return get_option(PARCELLA_CONNECTOR_OPTION_BASE_URL, '');
}

function parcella_connector_api_token() {
    return get_option(PARCELLA_CONNECTOR_OPTION_API_TOKEN, '');
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
                'Shared connection settings for every Parcella integration on this site. Find the base URL and API token on the "Integrations" page in Parcella\'s admin area (Administration -> Integrations).',
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
                    <th scope="row">
                        <label for="parcella_api_token"><?php esc_html_e('API token', 'parcella-connector'); ?></label>
                    </th>
                    <td>
                        <input type="password" id="parcella_api_token" name="<?php echo esc_attr(PARCELLA_CONNECTOR_OPTION_API_TOKEN); ?>"
                               value="<?php echo esc_attr(get_option(PARCELLA_CONNECTOR_OPTION_API_TOKEN, '')); ?>"
                               class="regular-text" autocomplete="off">
                        <p class="description">
                            <?php esc_html_e('Sent server-side only, for any module below that needs to write back to Parcella. Never exposed to visitors.', 'parcella-connector'); ?>
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
            </tbody>
        </table>
        <p class="description">
            <?php esc_html_e('More modules (tickets, applicant management) are planned. Each will appear in this table once added, sharing the connection settings above -- no separate credentials to configure per module.', 'parcella-connector'); ?>
        </p>
    </div>
    <?php
}

// ---------------------------------------------------------------------------
// Modules
//
// Each module is a self-contained file registering whatever shortcodes,
// hooks, or admin UI it needs, using parcella_connector_base_url() and
// parcella_connector_api_token() above rather than reading its own
// options. To add a new module: drop a new file in includes/modules/,
// require it below, and add a row to the table above.
// ---------------------------------------------------------------------------

require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/signup.php';
require_once PARCELLA_CONNECTOR_PATH . 'includes/modules/calendar.php';

<?php
/**
 * Calendar module -- renders the [parcella_calendar] shortcode, backed
 * by Parcella's public community-calendar JSON feed
 * (GET {base_url}/calendar/community.json). Read-only, so unlike
 * signup.php this module never needs the API token -- only the base
 * URL. See docs/ADR (calendar-display-via-shortcode) on the Parcella
 * side for why this replaced the earlier plan of just pointing an ICS
 * widget at community.ics: a shortcode renders as styled HTML matching
 * the surrounding page/widget, which a generic ICS-consuming widget
 * can't do.
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

/**
 * Fetches upcoming community-calendar items, cached briefly (5 min) so
 * a busy sidebar widget doesn't hit Parcella on every page view.
 * Reuses parcella_connector_signup_fetch_json() from signup.php -- that
 * helper is generic (path, cache key, cache duration), not actually
 * signup-specific, despite its name.
 */
function parcella_connector_calendar_fetch_items() {
    return parcella_connector_signup_fetch_json('/calendar/community.json', 'parcella_connector_calendar_items', 300);
}

// ---------------------------------------------------------------------------
// Shortcode: [parcella_calendar limit="5"]
// ---------------------------------------------------------------------------

add_shortcode('parcella_calendar', 'parcella_connector_calendar_render_shortcode');

function parcella_connector_calendar_render_shortcode($atts) {
    $atts = shortcode_atts(['limit' => 5], $atts, 'parcella_calendar');
    $limit = max(1, (int) $atts['limit']);

    $items = parcella_connector_calendar_fetch_items();

    ob_start();
    ?>
    <div class="parcella-calendar-widget">
        <?php if ($items === null): ?>
            <p><?php esc_html_e('The calendar is temporarily unavailable. Please try again later.', 'parcella-connector'); ?></p>
        <?php elseif (empty($items)): ?>
            <p><?php esc_html_e('No upcoming dates at the moment.', 'parcella-connector'); ?></p>
        <?php else: ?>
            <ul class="parcella-calendar-list">
                <?php foreach (array_slice($items, 0, $limit) as $item): ?>
                    <li class="parcella-calendar-item">
                        <span class="parcella-calendar-date">
                            <?php echo esc_html(date_i18n(get_option('date_format'), strtotime($item['date']))); ?>
                        </span>
                        <span class="parcella-calendar-title"><?php echo esc_html($item['title']); ?></span>
                        <?php if (!empty($item['time_from'])): ?>
                            <span class="parcella-calendar-time">
                                <?php
                                echo esc_html($item['time_from']);
                                if (!empty($item['time_until'])) {
                                    echo esc_html(' - ' . $item['time_until']);
                                }
                                ?>
                            </span>
                        <?php endif; ?>
                        <?php if (!empty($item['location'])): ?>
                            <span class="parcella-calendar-location"><?php echo esc_html($item['location']); ?></span>
                        <?php endif; ?>
                    </li>
                <?php endforeach; ?>
            </ul>
        <?php endif; ?>
    </div>
    <style>
        .parcella-calendar-list { list-style: none; margin: 0; padding: 0; }
        .parcella-calendar-item { padding: 0.5em 0; border-bottom: 1px solid #eee; }
        .parcella-calendar-item:last-child { border-bottom: none; }
        .parcella-calendar-date { display: block; font-weight: 600; }
        .parcella-calendar-title { display: block; }
        .parcella-calendar-time, .parcella-calendar-location { display: block; font-size: 0.85em; color: #666; }
    </style>
    <?php
    return ob_get_clean();
}

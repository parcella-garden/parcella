=== Parcella Connector ===
Contributors: kermie
Tags: allotment garden, club, forms, calendar, signup
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 8.0
Stable tag: 3.1.1
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Connects your club website to Parcella, the open-source management software for allotment garden associations: work-session signup, calendar, contact and plot application forms.

== Description ==

Parcella (https://github.com/parcella-garden/parcella) is open-source club management software for allotment garden associations. This plugin puts its public features on your WordPress site with shortcodes, all sharing one Parcella address:

* `[parcella_work_signup]` -- signup form for work sessions
* `[parcella_calendar limit="5"]` -- upcoming meetings, inspections and work sessions
* `[parcella_contact_form]` -- a contact form whose messages land in the club's helpdesk
* `[parcella_applicant_form]` -- an application form for free garden plots

The forms are plain HTML forms that the visitor's browser sends straight to your Parcella installation; WordPress never sees or stores the submissions, and the plugin holds no secret. Spam protection uses ALTCHA (proof of work), served from your own site -- no third party, no cookies.

Website drafts from Parcella's announcements don't need this plugin: Parcella creates them through WordPress's own REST API with an Application Password.

== External services ==

This plugin connects to **your own Parcella installation**, at the address you enter in its settings -- not to a service run by the plugin's authors:

* The calendar and the signup form read public data from it (`/calendar/community.json`, the list of open work sessions) when a page with the shortcode is shown.
* The forms send what visitors enter (name, email address, message, parcel number, chosen work sessions) to it when they submit.

What happens with that data is governed by your club's Parcella installation and its privacy policy.

== Installation ==

1. Upload the plugin and activate it.
2. Under *Settings → Parcella Connector*, enter your Parcella address (e.g. `https://verein.example.org`).
3. In Parcella, add your website's address to the allowed form origins (*Admin → Integrations → Website forms*).
4. Put the shortcodes on your pages.

== Changelog ==

= 3.1.1 =
* License changed from AGPL-3.0-or-later to GPL-2.0-or-later.

= 3.1.0 =
* Plot application form.

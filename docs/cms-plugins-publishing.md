# Publishing the CMS plugins

How to get each plugin in `integrations/` into its marketplace. The
uploads need the maintainer's own accounts; everything else is prepared.
All plugins are GPL-2.0-or-later (ADR 0108).

Build the upload files first:

    python3 integrations/package.py      # -> integrations/dist/ (not committed)

Before every release of a plugin: bump its version (see the table), add a
CHANGELOG entry, and, if `integrations/shared-php/ParcellaProtocol.php`
changed, run `sh integrations/shared-php/sync.sh` and the protocol test
(`integrations/shared-php/README.md`).

| Plugin | Version lives in | Marketplace | Upload |
|---|---|---|---|
| WordPress | `parcella-connector.php` (header + `PARCELLA_CONNECTOR_VERSION`), `readme.txt` (Stable tag) | wordpress.org plugin directory | SVN |
| Drupal | `CHANGELOG.md`, git tag | drupal.org | git |
| Joomla | `parcellaconnector.xml` | Joomla Extensions Directory (JED) | zip + listing |
| TYPO3 | `ext_emconf.php`, git tag | TYPO3 Extension Repository (TER) + Packagist | zip or `tailor` |
| Contao | git tag | Packagist (→ Contao Manager) | git |

Drupal, TYPO3 (Composer) and Contao install from a git repository whose
root is the plugin. This repository keeps all plugins in one place, so
each of those gets a small mirror repository, refreshed with a subtree
split:

    git subtree split --prefix=integrations/contao/parcella-connector -b split/contao
    git push git@github.com:parcella-garden/contao-parcella-connector.git split/contao:main
    # then tag the release in the mirror, e.g. v1.0.0

## WordPress (wordpress.org)

1. Log in at wordpress.org and submit the plugin at
   <https://wordpress.org/plugins/developers/add/> with
   `dist/wordpress/parcella-connector-<version>.zip`. The review takes a
   few days to weeks; reviewers read `readme.txt` (its "External
   services" section explains the calls to the club's own Parcella).
2. After approval you get an SVN repository. Put the plugin's files into
   `trunk/`, copy them to `tags/<version>/`, and commit. Later releases:
   update `trunk/`, add a new tag, raise *Stable tag* in `readme.txt`.
3. The `Contributors:` line in `readme.txt` must be the wordpress.org
   user name that owns the plugin.

## Drupal (drupal.org)

1. Create a project ("Module") named *Parcella Connector* with the
   machine name `parcella_connector` at <https://www.drupal.org/node/add/project-module>.
2. Push the module to the project's git repository on git.drupalcode.org
   (subtree split of `integrations/drupal/parcella_connector`, without
   `LICENSE.txt`: drupal.org adds the license itself and rejects copies).
3. Tag `1.0.0` and create a release on the project page. Packages and
   `composer require drupal/parcella_connector` work from then on.
4. Optional, recommended: apply for security advisory coverage, so the
   project shows the "covered" shield.

## Joomla (JED)

1. Log in at <https://extensions.joomla.org> and add a new extension in a
   fitting category (it creates articles from an external system).
2. Upload `dist/joomla/plg_system_parcellaconnector-<version>.zip`, add
   a description and a screenshot of the plugin settings. JED checks:
   GPL license, the `defined('_JEXEC') or die;` guard in every PHP file,
   no encoded code. A download link and a documentation link are
   required: the GitHub folder and its README work for both.
3. JED recommends an update server in the manifest
   (`<updateservers>`); add one pointing at a published `updates.xml`
   once there's a place to host it.

## TYPO3 (TER and Packagist)

1. Register the extension key `parcella_connector` at
   <https://extensions.typo3.org> (*My keys*).
2. Composer: create the mirror repository (subtree split of
   `integrations/typo3/parcella_connector`), submit it at
   <https://packagist.org/packages/submit> as
   `parcella/typo3-parcella-connector`, and tag `v1.0.0`.
3. TER: upload `dist/typo3/parcella_connector_<version>.zip` under *My
   extensions*, or use the `tailor` CLI (`tailor ter:publish 1.0.0`),
   which also works from CI.
4. EXT:news must be installed; the TER listing names it as a dependency
   through `ext_emconf.php`.

## Contao (Packagist → Contao Manager)

1. Create the mirror repository (subtree split of
   `integrations/contao/parcella-connector`) and tag `1.0.0`.
2. Submit it at <https://packagist.org/packages/submit> as
   `parcella/contao-parcella-connector`. Packages of type `contao-bundle`
   appear in the Contao Manager's search automatically.
3. Optional: register it at <https://extensions.contao.org> with a logo
   and description for a nicer listing.

## Testing a release

Each plugin was tested against a real installation in a temporary
container before 1.0.0 (Drupal 11.4, Joomla 5, TYPO3 13.4 with news
12.3, Contao 5.3): create a draft with an image, send it again (same
id), update it, publish it by hand, check that Parcella finds the public
address and that an update keeps it published, a wrong secret and a
disguised image are refused. Repeat that before a new major version of a
CMS is claimed as supported.

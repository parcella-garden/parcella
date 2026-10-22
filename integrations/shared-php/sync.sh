#!/bin/sh
# Copies ParcellaProtocol.php into every CMS plugin with that plugin's own
# namespace. Marketplaces don't allow plugins to depend on each other, so
# each one ships its own copy; this keeps them identical. Run it after
# editing ParcellaProtocol.php, then commit the copies.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
src="$here/ParcellaProtocol.php"

copy() {  # target file, namespace
    mkdir -p "$(dirname "$1")"
    sed -e "s|^namespace Parcella\\\\Shared;|namespace $2;|" \
        -e "s|^ \* Edit THIS file (| * Do not edit this copy: edit (|" \
        "$src" > "$1"
    echo "updated $1"
}

copy "$here/../drupal/parcella_connector/src/ParcellaProtocol.php" 'Drupal\\parcella_connector'
copy "$here/../joomla/plg_system_parcellaconnector/src/ParcellaProtocol.php" 'Parcella\\Plugin\\System\\ParcellaConnector'
copy "$here/../typo3/parcella_connector/Classes/ParcellaProtocol.php" 'Parcella\\ParcellaConnector'
copy "$here/../contao/parcella-connector/src/ParcellaProtocol.php" 'Parcella\\ContaoParcellaConnector'

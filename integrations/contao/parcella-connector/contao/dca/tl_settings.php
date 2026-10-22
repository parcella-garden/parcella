<?php

/*
 * Parcella Connector settings under System > Settings.
 * Licensed GPL-2.0-or-later.
 */

use Contao\CoreBundle\DataContainer\PaletteManipulator;
use Parcella\ContaoParcellaConnector\ParcellaProtocol;

PaletteManipulator::create()
    ->addLegend('parcella_connector_legend', null, PaletteManipulator::POSITION_AFTER, true)
    ->addField(['parcellaConnectorSecret', 'parcellaConnectorArchive', 'parcellaConnectorAuthor'], 'parcella_connector_legend', PaletteManipulator::POSITION_APPEND)
    ->applyToPalette('default', 'tl_settings');

$GLOBALS['TL_DCA']['tl_settings']['fields']['parcellaConnectorSecret'] = [
    'inputType' => 'text',
    'eval' => ['maxlength' => 64, 'minlength' => 64, 'rgxp' => 'alnum', 'tl_class' => 'w50', 'autocomplete' => 'off'],
    // An empty field gets a fresh secret on saving.
    'save_callback' => [
        static fn ($value) => \strlen((string) $value) === 64 && ctype_xdigit((string) $value)
            ? strtolower((string) $value)
            : ParcellaProtocol::generateSecret(),
    ],
];
$GLOBALS['TL_DCA']['tl_settings']['fields']['parcellaConnectorArchive'] = [
    'inputType' => 'select',
    'foreignKey' => 'tl_news_archive.title',
    'eval' => ['includeBlankOption' => true, 'chosen' => true, 'tl_class' => 'w50'],
];
$GLOBALS['TL_DCA']['tl_settings']['fields']['parcellaConnectorAuthor'] = [
    'inputType' => 'select',
    'foreignKey' => 'tl_user.name',
    'eval' => ['includeBlankOption' => true, 'chosen' => true, 'tl_class' => 'w50'],
];

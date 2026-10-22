<?php

$EM_CONF[$_EXTKEY] = [
    'title' => 'Parcella Connector',
    'description' => 'Receives website drafts from Parcella, the club management software for allotment garden associations, as hidden news records.',
    'category' => 'services',
    'state' => 'stable',
    'version' => '1.0.0',
    'author' => 'Parcella contributors',
    'constraints' => [
        'depends' => [
            'typo3' => '12.4.0-13.4.99',
            'news' => '11.0.0-12.99.99',
        ],
    ],
];

<?php

// Answers the Parcella Website Plugin Protocol below /parcella/v1/ on any
// site, after the site is resolved (needed for the detail page address)
// and before TYPO3 looks for a page.
return [
    'frontend' => [
        'parcella/parcella-connector' => [
            'target' => \Parcella\ParcellaConnector\Middleware\DraftEndpoint::class,
            'after' => ['typo3/cms-frontend/site'],
            'before' => ['typo3/cms-frontend/base-redirect-resolver'],
        ],
    ],
];

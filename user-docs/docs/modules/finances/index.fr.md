# Finances {#finances}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Le module Finances est l'espace de travail du trésorier. Il établit les
factures annuelles de l'association pour chaque parcelle et chaque
membre, suit qui a payé, envoie les relances de paiement et enregistre
les factures que l'association reçoit elle-même. Il tient aussi un
simple livre de caisse par compte bancaire. À partir de tout cela, il
produit un état comptable de trésorerie pour l'administration fiscale et
un budget prévisionnel pour l'année suivante.

!!! info "Qui peut l'utiliser"
    - Le module est **désactivé par défaut**. Un administrateur l'active
      dans les **Paramètres du club** (l'interrupteur s'appelle
      **Finances**), voir
      [Activer et désactiver les modules](../../administration/modules.md).
      Avant d'envoyer les premières factures, remplissez les
      **Paramètres financiers** (coordonnées bancaires, format des
      numéros de facture) dans les
      [Paramètres de l'association](../../administration/settings.md) --
      ils sont imprimés en pied de page de chaque facture.
    - Les membres du bureau et les administrateurs (et toute personne
      d'un groupe à accès complet) peuvent tout faire.
    - Tous les autres ont besoin d'un [groupe](../../administration/groups.md)
      qui accorde des droits sur **Finances** :
        - **lecture** -- voir chaque écran, ouvrir les PDF, exporter des
          fichiers CSV ;
        - **écriture** -- créer et modifier les séries, lignes, paiements,
          relances, comptes, écritures, factures reçues, catégories et le
          budget ;
        - **suppression** -- supprimer à nouveau ces éléments.
    - Quelques actions concernant les pièces jointes des factures reçues
      dans le stockage cloud sont réservées aux membres du bureau et aux
      administrateurs, voir [Factures reçues](incoming-invoices.md).

    Voir [Rôles, groupes et droits](../../getting-started/roles-and-permissions.md).

## Où le trouver {#where-to-find-it}

Quand le module est activé et que vous avez le droit de lecture, la
barre latérale affiche un groupe **Finances** avec quatre entrées :

| Entrée de menu | Ouvre |
|---|---|
| **Aperçu** | Le tableau de bord des finances décrit ci-dessous. |
| **Factures émises** | La liste des séries de factures, voir [Séries de factures](invoice-runs.md). |
| **Relances** | La liste des factures en retard, voir [Factures, paiements et relances](invoices.md#reminders). |
| **Factures reçues** | Les factures reçues par l'association, voir [Factures reçues](incoming-invoices.md). |

Tout le reste (comptes, catégories, catalogue d'articles, écritures,
état comptable, budget) est accessible depuis les cartes du tableau de
bord.

## Tableau de bord des finances {#finances-dashboard}

![Tableau de bord des finances](../../assets/screenshots/finances/dashboard.png)

La page d'accueil du module. Trois chiffres en haut vous donnent d'un
coup d'œil l'état de vos factures émises. En dessous, une carte par
domaine du module vous y mène.

| Chiffre | Ce qu'il affiche |
|---|---|
| **Factures ouvertes** | Le nombre de factures émises pas encore entièrement payées. Les factures partiellement payées comptent ici comme ouvertes. |
| **Montant en attente** | La somme encore impayée sur ces factures (montant de la facture moins les paiements enregistrés). Les frais de relance ne sont pas inclus dans ce chiffre. |
| **En retard** | Le nombre de factures ouvertes dont la date d'échéance de leur série de factures est dépassée. Affiché en rouge s'il est supérieur à zéro. |

| Carte | Indication sous le titre | Ouvre |
|---|---|---|
| **Factures émises** | *n* série(s) de factures | [Séries de factures](invoice-runs.md) |
| **Catégories** | *n* catégorie(s) définie(s) | [Catégories comptables](bookkeeping.md#bookkeeping-categories) |
| **Catalogue d'articles** | *n* modèle(s) d'article défini(s) | [Catalogue d'articles](invoice-runs.md#item-catalog) |
| **Comptes** | *n* compte(s) défini(s) | [Comptes](bank-accounts.md#accounts) |
| **Relances** | *n* facture(s) en retard | [Relances](invoices.md#reminders) |
| **Factures reçues** | *n* facture(s) entrante(s) | [Factures reçues](incoming-invoices.md) |
| **Toutes les écritures** | Tous les paiements des factures reçues et émises | [Toutes les écritures](bookkeeping.md#all-bookings) |
| **État comptable** | État de trésorerie pour l'administration fiscale | [État comptable](bookkeeping.md#accounting-statement) |
| **Budget prévisionnel** | Recettes et dépenses prévues par catégorie pour l'année à venir, à côté du réalisé des années passées | [Budget prévisionnel](bookkeeping.md#budget-plan) |

La plupart des sous-pages ont un bouton **Retour aux Finances** dans la
barre du haut qui vous ramène ici.

<!-- TODO(verify): finances/coming_soon.html ("This feature is coming soon.") exists, but no route renders it any more, so it is not documented as a screen. -->

## Le parcours de l'argent au fil de l'année {#how-the-money-flows-through-a-year}

Une année type d'association dans Parcella ressemble à ceci :

1. **Configurer une fois.** Créez vos [catégories comptables](bookkeeping.md#bookkeeping-categories)
   (ou importez votre plan comptable), vos [comptes bancaires et de caisse](bank-accounts.md#accounts),
   et les lignes de facture récurrentes dans le [catalogue d'articles](invoice-runs.md#item-catalog)
   (loyer au m², cotisation, eau, électricité, assurance ...).
2. **Préparer les factures annuelles.** Créez une [série de factures](invoice-runs.md)
   pour l'année, ajoutez les articles du catalogue, ajustez les prix et
   vérifiez l'[aperçu](invoice-runs.md#preview-invoices). Les relevés de
   compteurs, les assurances et les heures de travail de cette année
   doivent être complets à ce stade -- les articles basés sur la
   consommation les lisent en direct.
3. **Finaliser et envoyer.** La finalisation attribue les numéros de
   facture définitifs. Envoyez ensuite les factures par e-mail,
   téléversez-les dans les dossiers cloud des parcelles et téléchargez le
   lot d'impression pour tous ceux qui reçoivent du papier.
4. **Enregistrer les paiements.** Saisissez les paiements à la main dans
   la liste des factures de la série, ou importez votre relevé bancaire
   sur la [page des écritures du compte](bank-accounts.md#bookings-of-an-account)
   et associez chaque ligne à la facture qu'elle règle.
5. **Relancer les retardataires.** La page [Relances](invoices.md#reminders)
   liste toutes les factures en retard ; envoyez la première, deuxième,
   troisième relance depuis la facture, avec ou sans frais.
6. **Enregistrer les factures de l'association** comme
   [factures reçues](incoming-invoices.md) et marquez-les payées quand
   l'argent sort.
7. **Clôturer l'année.** L'[état comptable](bookkeeping.md#accounting-statement)
   affiche les recettes et dépenses par catégorie, comptées le jour où
   l'argent a réellement bougé. Utilisez-le pour l'administration fiscale
   et l'assemblée générale annuelle, et planifiez l'année suivante dans
   le [budget prévisionnel](bookkeeping.md#budget-plan).

Le guide pratique [Établir les factures annuelles](../../guides/annual-invoicing.md)
parcourt les étapes 2 à 5 dans l'ordre.

## Chapitres {#chapters}

- [Séries de factures](invoice-runs.md) -- le lot annuel de factures, ses
  lignes et le calcul de chaque montant, le catalogue d'articles,
  l'aperçu et la finalisation.
- [Factures, paiements et relances](invoices.md) -- toutes les factures
  de toutes les séries, l'envoi, les paiements et la procédure de
  relance.
- [Comptes bancaires et écritures](bank-accounts.md) -- vos comptes,
  leurs écritures, et l'import d'un relevé bancaire avec rapprochement
  des factures.
- [Factures reçues](incoming-invoices.md) -- les factures reçues par
  l'association et leurs paiements.
- [Catégories, budget et synthèse](bookkeeping.md) -- catégories
  comptables, liste des écritures de toute l'association, état comptable
  et budget prévisionnel.

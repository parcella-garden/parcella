# Comptes bancaires et écritures {#bank-accounts-and-bookings}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Vous enregistrez ici les comptes réels de l'association -- comptes
courants, compte d'épargne, caisse -- et voyez tout ce qui a été passé
sur chacun d'eux. Vous pouvez ajouter des écritures à la main ou
importer votre relevé bancaire sous forme de fichier CSV. Ce faisant,
Parcella propose d'associer chaque écriture à une facture ouverte, si
bien qu'un virement entrant est enregistré immédiatement comme paiement
du membre.

!!! info "Qui peut l'utiliser"
    Fait partie du module **Finances** (désactivé par défaut). Consulter
    les comptes et les écritures, et exporter en CSV, nécessite le droit
    de lecture sur **Finances**. Créer ou modifier des comptes, ajouter
    des écritures et importer nécessitent le droit d'écriture ; supprimer
    des comptes ou des écritures nécessite le droit de suppression. Les
    membres du bureau et les administrateurs peuvent tout faire. Voir
    [Finances](index.md).

!!! note "Pas une comptabilité complète"
    La liste des écritures d'un compte est un relevé des mouvements
    d'argent, pas une comptabilité en partie double. Il n'y a ni solde
    d'ouverture ni solde courant. Les écritures qui ne sont pas liées à
    une facture (frais bancaires, remboursement) n'ont pas de catégorie,
    elles n'apparaissent donc pas dans
    l'[état comptable](bookkeeping.md#accounting-statement).

## Comptes {#accounts}

![Comptes](../../assets/screenshots/finances/account-list.png)

Ouvrez-les avec la carte **Comptes** du tableau de bord des finances.
**Retour aux Finances** dans la barre du haut vous ramène.

### Nouveau compte {#new-account}

Affiché avec le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Nom** | Obligatoire, par ex. « Compte courant Crédit Mutuel » ou « Caisse ». Enregistrer sans nom affiche « Un nom est requis ». |
| **Type** | **Banque** ou **Espèces**. |
| **Numéro de compte/IBAN** | Facultatif, pour votre information. |
| **Note** | Facultatif. |
| **Actif** | Activé par défaut. Seuls les comptes actifs sont proposés lors de l'enregistrement d'un paiement. Désactivez-le pour un compte clôturé : son historique reste, mais il n'est plus proposé. |
| **Ajouter un compte** | Enregistre le compte. |

### Liste des comptes {#accounts-list}

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Nom**, **Type**, **Numéro de compte/IBAN**, **Note**, **Actif** | Les données du compte. Avec le droit d'écriture, elles sont modifiables dans la ligne ; cliquez sur l'icône de coche pour enregistrer. |
| **Paiements enregistrés** | La somme de tous les paiements de factures émises enregistrés sur ce compte. Les paiements de factures reçues et les autres écritures ne sont pas inclus. |
| Icône des écritures | Ouvre les [écritures](#bookings-of-an-account) du compte. |
| Icône de coche | Enregistre la ligne. Nécessite le droit d'écriture. |
| Icône corbeille | Supprime le compte après « Supprimer ce compte ? Il n'a aucune écriture. » Nécessite le droit de suppression. Grisée pour un compte qui a des écritures (voir ci-dessous). |

S'il n'y a encore aucun compte : « Aucun compte pour le moment --
ajoutez-en un ci-dessus. »

!!! note "Les comptes ayant des écritures ne peuvent pas être supprimés"
    Seul un compte sans aucune écriture -- aucune écriture saisie à la
    main ou importée, aucun paiement de facture enregistré dessus -- peut
    être supprimé. Pour tout autre compte, la corbeille est grisée (« A
    des écritures : décochez plutôt « Actif ». »). Désactiver **Actif**
    masque le compte des formulaires de paiement et conserve toutes ses
    écritures.

## Écritures d'un compte {#bookings-of-an-account}

![Écritures d'un compte](../../assets/screenshots/finances/account-bookings.png)

Ouvrez-la avec l'icône des écritures dans la liste des comptes. Le titre
est « Écritures — *nom du compte* ». Elle affiche tout ce qui a été passé
sur ce compte, le plus récent en premier :

- les paiements de factures émises enregistrés avec ce compte (montants
  positifs),
- les paiements de [factures reçues](incoming-invoices.md) enregistrés
  avec ce compte (montants négatifs),
- les autres écritures saisies à la main ou importées (positives ou
  négatives, telles que saisies).

Les 50 premières écritures sont affichées ; d'autres se chargent
automatiquement quand vous faites défiler vers le bas. Le bouton
**Retour aux Finances** dans la barre du haut vous ramène à la liste des
comptes (malgré son libellé). Sur les écrans d'import ci-dessous, le
même bouton vous ramène aux écritures du compte sans rien importer.

### Filtre et actions {#filter-and-actions}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Rechercher** | Trouve les écritures dont la référence, la description ou l'expéditeur/destinataire contient ce texte. |
| **Du** / **Au** | Seulement les écritures à ces dates ou entre elles. |
| **Montant min.** / **Montant max.** | Seulement les écritures dont le montant est dans cette plage. N'oubliez pas que l'argent sortant est négatif : pour trouver les dépenses de 100 ou plus, réglez **Montant max.** sur `-100`. |
| **Association** | **Toutes**, **Associée à une facture** (paiements de factures) ou **Non associée** (autres écritures). Pratique pour trouver les lignes bancaires à vérifier. |
| **Filtrer** / **Réinitialiser** | Applique le filtre / l'efface. |
| **Exporter CSV** | Télécharge les écritures correspondant au filtre actuel sous forme de fichier CSV (séparé par des points-virgules : date, montant, référence, description, contrepartie). Nécessite seulement le droit de lecture. |
| **Importer CSV** | Ouvre la boîte de dialogue d'import, voir [Importer un relevé bancaire](#importing-a-bank-statement). Nécessite le droit d'écriture. |
| **Ajouter une écriture** | Ouvre la boîte de dialogue pour une écriture à la main, voir [Ajouter une écriture à la main](#adding-a-booking-by-hand). Nécessite le droit d'écriture. |

### Tableau des écritures {#bookings-table}

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Date** | La date de l'écriture. |
| **Montant** | Le montant ; l'argent sortant s'affiche en rouge avec un signe moins. |
| **Référence** | Pour un paiement de facture, le numéro de facture sous forme de lien vers la facture (ou facture reçue). Vide pour les autres écritures. |
| **Description** | La note du paiement ou la description de l'écriture. |
| **Expéditeur / destinataire** | Qui a payé ou a été payé : le destinataire de la facture, l'expéditeur de la facture reçue, ou la contrepartie que vous avez saisie. |
| Icône corbeille | Supprime l'écriture après « Vraiment supprimer cette écriture ? ». Seulement pour les écritures saisies à la main ou importées, et seulement avec le droit de suppression. Les paiements de factures ne peuvent pas être supprimés ici -- supprimez-les sur la facture. |

Si le compte n'a aucune écriture : « Aucune écriture pour l'instant. »

Après un import ou une association, un message vert en haut vous indique
ce qui s'est passé, par ex. « 12 importées, 1 ignorées. »,
« 3 écriture(s) associée(s) à une facture existante. », « IBAN renseigné
pour 2 membre(s) à partir de l'import. » ou, après une écriture unique,
« Enregistré comme paiement pour la facture associée. »

## Ajouter une écriture à la main {#adding-a-booking-by-hand}

Cliquez sur **Ajouter une écriture**. La boîte de dialogue demande :

| Champ | Ce qu'il fait |
|---|---|
| **Date** | Obligatoire, préremplie avec la date du jour. |
| **Montant** | Obligatoire. Positif pour l'argent qui entre, négatif pour l'argent qui sort, par ex. `-12,50`. |
| **Description** | Facultatif. |
| **Expéditeur / destinataire** | Facultatif. Sert aussi à suggérer une facture correspondante. |
| **Ajouter une écriture** | Passe à l'étape d'association. |

### Factures correspondantes possibles {#possible-matching-invoices}

<!-- No screenshot: this page is only reached by submitting the form above. -->

Avant tout enregistrement, Parcella cherche des factures ouvertes du
même montant : pour un montant positif, les factures émises dont il
reste exactement ce montant à payer ; pour un montant négatif, les
factures reçues dont ce montant reste impayé. Il affiche la **Date**, le
**Montant** et l'**Expéditeur / destinataire** de l'écriture, puis les
choix :

| Choix | Ce qui se passe |
|---|---|
| **Enregistrer comme écriture générique** | Enregistre une écriture normale sur le compte, liée à aucune facture. |
| Une ligne par facture correspondante | Affiche la facture (numéro et destinataire, ou expéditeur et numéro) et « restant dû : *montant* ». Un badge vert « nom correspondant » apparaît quand l'expéditeur/destinataire saisi partage un nom avec le destinataire ou l'expéditeur de la facture. La choisir enregistre l'écriture comme **paiement de cette facture**, avec ce compte, cette date et la description comme note. |
| **Ajouter une écriture** | Enregistre votre choix. |

Au plus cinq factures sont proposées, celles avec un nom correspondant
en premier. Si exactement une suggestion a un nom correspondant, elle
est présélectionnée ; sinon, c'est **Enregistrer comme écriture
générique**. Si aucune facture ne correspond : « Aucune facture ouverte
ne correspond à ce montant. »

!!! tip
    L'association ne compare que le montant restant dû, au centime près.
    Une facture avec des frais de relance est due frais compris, et une
    facture partiellement payée seulement pour ce qui reste.

## Importer un relevé bancaire {#importing-a-bank-statement}

La plupart des banques permettent de télécharger le relevé de compte
sous forme de fichier CSV. N'importe quelle disposition de colonnes
fonctionne. L'import se fait en trois étapes.

**1. Téléverser.** Cliquez sur **Importer CSV**, choisissez le fichier
et cliquez sur **Importer CSV**. « N'importe quel CSV fonctionne --
téléchargez-le, puis associez ses colonnes aux champs Parcella à l'écran
suivant. » Les fichiers séparés par des points-virgules et par des
virgules sont tous deux reconnus, de même que l'UTF-8 et les anciens
encodages Windows. Un fichier vide est refusé avec « Ce fichier CSV
semble être vide. »

**2. Associer les colonnes CSV.** <!-- No screenshot: reached only by uploading a file. -->
« Pour chaque colonne ci-dessous, choisissez à quel champ Parcella elle
correspond (ou laissez-la ignorée). Date et Montant sont obligatoires. »
La page affiche les en-têtes de colonnes de votre fichier, chacun avec
une liste déroulante, et les cinq premières lignes comme échantillon.

| Champ | Signification |
|---|---|
| **— Ignorer —** | La colonne n'est pas utilisée. |
| **Date** | Obligatoire. La date de l'écriture. Formats acceptés : `2026-03-31`, `31.03.2026` et `31.03.26`. |
| **Montant** | Obligatoire. Montant signé, avec virgule ou point décimal (`-12,50` ou `-12.50`). Les séparateurs de milliers sont acceptés, tels que votre banque les exporte : `1.234,56`, `1,234.56` ou `1 234,56`. |
| **Description** | Facultatif, par ex. le motif du paiement. |
| **Expéditeur / destinataire** | Facultatif. Sert à l'association et s'affiche dans la liste. |
| **IBAN** | Facultatif. Voir l'astuce ci-dessous. |

Les en-têtes allemands et anglais courants (« Buchungsdatum »,
« Betrag », « Verwendungszweck », « Auftraggeber », « IBAN » ...) sont
présélectionnés pour vous ; vérifiez-les quand même. Cliquez sur
**Importer CSV** pour continuer. Si **Date** ou **Montant** n'est pas
associé, vous êtes renvoyé avec « Veuillez associer au moins une colonne
à Date et Montant. »

**3. Associer les lignes aux factures.** <!-- No screenshot: reached only through the import. -->
« Pour chaque ligne, choisissez une facture ouverte correspondante pour
l'enregistrer comme un vrai paiement, ou laissez-la comme écriture
générique. » Chaque ligne affiche **Date**, **Montant**, **Expéditeur /
destinataire** et une liste déroulante **Correspondance** avec **Ne pas
importer**, **Enregistrer comme écriture générique** et les factures
suggérées (montant dû entre parenthèses, un ✓ quand le nom correspond).
La présélection fonctionne comme pour une écriture unique. Les lignes
dont la date ou le montant n'ont pas pu être lus affichent « Ligne
invalide — sera ignorée ». Une ligne déjà présente sur ce compte reçoit
un badge **Déjà importé** et est préréglée sur **Ne pas importer**.
Cliquez sur **Importer CSV** pour tout enregistrer.

Ce qui est enregistré :

- chaque ligne avec une facture choisie devient un paiement de cette
  facture sur ce compte -- sauf si cette facture a été entièrement payée
  entre-temps : alors rien n'est enregistré, et le message de résultat
  l'indique ;
- chaque autre ligne valide devient une écriture normale ;
- les lignes réglées sur **Ne pas importer**, et les lignes invalides,
  sont ignorées et comptées dans le message de résultat.

!!! tip "Compléter les IBAN des membres"
    Si vous associez à la fois **Expéditeur / destinataire** et
    **IBAN**, Parcella cherche un membre dont le nom correspond
    exactement à celui de l'expéditeur (prénom nom, ou nom prénom, sans
    tenir compte des majuscules). Si ce membre n'a pas encore d'IBAN
    enregistré, l'IBAN du relevé est renseigné. Les IBAN existants ne
    sont jamais écrasés.

!!! tip "Importer deux fois le même relevé"
    Une ligne compte comme déjà importée quand ce compte a déjà une
    écriture avec la même date, le même montant et la même description
    (un paiement enregistré sur une facture compte aussi). Les exports
    qui se chevauchent sont donc sans risque : seules les nouvelles
    lignes sont ajoutées. Parcella compte plutôt que de simplement
    comparer -- si le fichier contient deux fois le même achat de café
    le même jour et que le compte ne l'a qu'une fois, l'un des deux est
    nouveau.

    Une ligne déjà existante n'est importée que si vous changez son
    **Ne pas importer** en autre chose. Cliquer deux fois sur
    **Importer CSV**, ou renvoyer la page avec le bouton retour,
    n'ajoute rien.

## Voir aussi {#related}

- [Factures, paiements et relances](invoices.md)
- [Factures reçues](incoming-invoices.md)
- [Toutes les écritures](bookkeeping.md#all-bookings) -- tous les
  paiements de factures sur tous les comptes.
- [Membres](../members.md) -- où l'IBAN est enregistré.

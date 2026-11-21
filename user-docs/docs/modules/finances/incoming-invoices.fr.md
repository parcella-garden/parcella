# Factures reçues {#incoming-invoices}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les factures reçues sont les factures que l'association reçoit : le
fournisseur d'eau, l'assureur, le magasin de bricolage. Les enregistrer
ici, réparties en postes avec chacun une catégorie comptable, et noter
quand elles ont été payées vous donne le côté dépenses de
l'[état comptable](bookkeeping.md#accounting-statement).

!!! info "Qui peut l'utiliser"
    Fait partie du module **Finances** (désactivé par défaut). La
    consultation nécessite le droit de lecture sur **Finances** ;
    enregistrer des factures, relier des contacts et ajouter des
    paiements nécessitent le droit d'écriture ; supprimer une facture ou
    un paiement nécessite le droit de suppression. Téléverser et
    télécharger la facture scannée (pièce jointe) n'est possible que pour
    les membres du bureau et les administrateurs, et seulement si le
    module **Stockage cloud** est activé et qu'un dossier des factures
    reçues est configuré. Voir [Finances](index.md).

## Liste des factures reçues {#incoming-invoices-list}

![Factures reçues](../../assets/screenshots/finances/incoming-invoice-list.png)

Ouvrez-la avec **Finances → Factures reçues** ou la carte **Factures
reçues** du tableau de bord. La liste est triée par date de facture, la
plus récente en premier.

**Barre du haut**

| Bouton | Ce qu'il fait |
|---|---|
| **Enregistrer une facture entrante** | Ouvre le formulaire pour une nouvelle facture reçue (voir ci-dessous). Nécessite le droit d'écriture. |
| **Retour aux Finances** | Retour au tableau de bord des finances. |

**Filtre**

| Filtre | Ce qu'il fait |
|---|---|
| **N° de facture** | Factures dont le numéro contient ce texte. |
| **Expéditeur** | Factures dont l'expéditeur contient ce texte. |
| **Montant min.** / **Montant max.** | Total de la facture au moins / au plus égal à ce montant. |
| **Statut de paiement** | **Tous**, **Ouverte**, **Partiellement payée** ou **Payée**. |
| **Filtrer** / **Réinitialiser** | Applique le filtre / l'efface. |

**Tableau**

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Date** | La date de la facture. |
| **Expéditeur** | Qui a envoyé la facture ; cliquez dessus pour ouvrir la [facture reçue](#incoming-invoice). |
| **N° de facture** | Le numéro de facture du fournisseur, s'il a été saisi. |
| **Catégories** | Une ligne par poste : sa catégorie (ou « Sans catégorie ») et sa description. |
| **Montant** | Le total de la facture (somme de tous les postes). |
| **Statut de paiement** | **Ouverte**, **Partiellement payée** ou **Payée**, d'après les paiements enregistrés. |
| Icône de téléchargement | Télécharge la facture jointe. Affichée seulement s'il y a une pièce jointe et que vous pouvez utiliser le stockage cloud. |
| Icône corbeille | Supprime la facture reçue, avec ses postes et ses paiements, après confirmation. Nécessite le droit de suppression. |

Si rien n'a encore été enregistré : « Aucune facture entrante
enregistrée pour l'instant. »

!!! note "La suppression conserve la pièce jointe"
    « Vraiment supprimer cette facture entrante ? La pièce jointe ne
    sera pas supprimée du dossier cloud. » La facture scannée reste dans
    le dossier commun ; supprimez-la là-bas à la main si nécessaire.

## Enregistrer une facture reçue {#record-incoming-invoice}

Cliquez sur **Enregistrer une facture entrante**. Une boîte de dialogue
s'ouvre :

| Champ | Ce qu'il fait |
|---|---|
| **Contact** | Facultatif. Affiché seulement si le module [Contacts externes](../external-contacts.md) est activé et que vous pouvez lire les contacts. Choisir un fournisseur parmi vos contacts remplit **Expéditeur** pour vous (« Choisir un contact remplit l'expéditeur. »), sauf si vous en avez déjà saisi un. **— aucun —** ne relie aucun contact. |
| **Expéditeur** | Obligatoire. Le nom du fournisseur, tel que vous voulez qu'il apparaisse dans les listes, le rapprochement bancaire et l'état comptable. |
| **N° de facture** | Facultatif. Le numéro de facture du fournisseur. |
| **Date de facture** | Obligatoire, prérempli avec la date du jour. |
| **Note** | Facultatif. |
| **Postes** | Une ligne par poste de coût (voir ci-dessous). |
| **Ajouter un poste** | Ajoute une autre ligne de poste. Chaque ligne sauf la première a un bouton de suppression. |
| **Pièce jointe** | Facultatif. La facture scannée ou photographiée. « Téléchargé vers le dossier cloud partagé ci-dessus. » Affiché seulement aux membres du bureau et aux administrateurs quand le stockage cloud et un dossier des factures reçues sont configurés. |
| **Enregistrer** | Enregistre la facture. Vous voyez « Enregistré. ». |
| **Annuler** | Ferme la boîte de dialogue sans enregistrer. |

Chaque poste a trois champs :

| Champ | Ce qu'il fait |
|---|---|
| Catégorie | [Catégorie comptable](bookkeeping.md#bookkeeping-categories) facultative. « — » signifie aucune ; le poste s'affiche alors comme « Sans catégorie ». |
| **Description (ce qui a été acheté)** | Texte libre facultatif, par ex. « Entretien de la tondeuse ». Plusieurs postes peuvent partager une catégorie tout en décrivant des achats différents. |
| Montant | Le montant du poste, par ex. `249,90`. Un poste sans montant valide est ignoré. |

!!! warning "Vérifiez avant d'enregistrer"
    L'expéditeur, la date, les postes et les montants ne peuvent plus
    être modifiés après l'enregistrement ; seuls le contact relié et les
    paiements peuvent l'être ensuite. En cas d'erreur, supprimez la
    facture reçue et enregistrez-la à nouveau.

Si la pièce jointe ne peut pas être téléversée, la facture est quand
même enregistrée et l'erreur du stockage cloud est affichée en haut de
la liste. Le nom de fichier de la pièce jointe dans le dossier cloud
commence par un numéro interne, si bien que deux factures portant le
même nom de fichier ne s'écrasent jamais. Le dossier lui-même se règle
sous **Intégrations** → **Dossier des factures reçues**, voir
[Intégrations](../../administration/integrations.md).

## Facture reçue {#incoming-invoice}

![Facture reçue](../../assets/screenshots/finances/incoming-invoice-detail.png)

S'ouvre quand vous cliquez sur un expéditeur dans la liste. Le titre est
« Facture entrante — *expéditeur* ».

**Barre du haut**

| Bouton | Ce qu'il fait |
|---|---|
| **Télécharger la pièce jointe** | Télécharge la facture jointe depuis le dossier cloud. Affiché seulement s'il y a une pièce jointe et que vous pouvez utiliser le stockage cloud. |
| **Retour aux factures entrantes** | Retour à la liste. |

Carte **Facture**

| Champ | Ce qu'il affiche |
|---|---|
| **Expéditeur** | L'expéditeur tel que saisi. |
| **Contact** | Le contact externe relié, sous forme de lien vers le contact si vous pouvez voir les contacts (« supprimé » si le contact a été supprimé depuis). Avec le droit d'écriture, une liste déroulante et **Enregistrer** permettent de relier un autre contact ou aucun. Changer le contact ne change **pas** le texte de l'**Expéditeur**. |
| **N° de facture** | Le numéro de facture du fournisseur. |
| **Date** | La date de la facture. |
| **Note** | La note. |
| **Montant** | Le total de la facture. |
| **Statut de paiement** | **Ouverte**, **Partiellement payée** ou **Payée**. |

Carte **Postes** : chaque poste avec sa catégorie (« code · titre », ou
« Sans catégorie »), sa description et son montant, ainsi que le
**Sous-total**.

Carte **Paiements** : chaque paiement enregistré pour cette facture avec
date, montant, compte et note. Une icône corbeille supprime un paiement
(nécessite le droit de suppression, demande « Supprimer ce
paiement ? »). S'il n'y en a aucun : « Aucun paiement enregistré pour le
moment. »

Pour enregistrer un paiement (droit d'écriture) :

| Champ | Ce qu'il fait |
|---|---|
| **Montant** | Obligatoire. Ce que l'association a payé, en nombre positif. Les paiements partiels sont possibles. |
| **Payé le** | Obligatoire, prérempli avec la date du jour. Cette date détermine l'année où la dépense compte dans l'état comptable. |
| **Note** | Facultatif. |
| **Compte** | Facultatif. Le [compte](bank-accounts.md#accounts) d'où l'argent est sorti ; seuls les comptes actifs sont proposés. Le paiement apparaît alors, en montant négatif, dans les écritures de ce compte. |
| **Ajouter un paiement** | Enregistre le paiement. |

Le statut devient **Payée** une fois que les paiements atteignent le
total de la facture. Les factures reçues n'ont ni relances ni frais.

!!! tip "Payer depuis le relevé bancaire"
    Au lieu de saisir le paiement ici, vous pouvez importer votre relevé
    bancaire sur la page des écritures du compte : une écriture négative
    du même montant qu'une facture reçue ouverte est proposée comme
    correspondance et enregistrée comme son paiement. Voir
    [Comptes bancaires et écritures](bank-accounts.md#possible-matching-invoices).

!!! note "Seules les factures payées comptent"
    L'état comptable et le budget prévisionnel comptent une dépense le
    jour où elle a été payée. Une facture reçue sans paiement n'y
    apparaît pas du tout.

## Voir aussi {#related}

- [Contacts externes](../external-contacts.md) -- la page de contact
  d'un fournisseur liste les factures reçues qui lui sont reliées.
- [Demandes d'achat](../purchase-requests.md) -- l'approbation d'un
  achat se fait là ; la facture qui en résulte est enregistrée ici à la
  main.
  <!-- TODO(verify): there is no link between a purchase request and an incoming invoice in the code; confirm this is the intended workflow. -->
- [Catégories, budget et synthèse](bookkeeping.md)
- [Intégrations](../../administration/integrations.md) -- le dossier
  cloud commun pour les pièces jointes.

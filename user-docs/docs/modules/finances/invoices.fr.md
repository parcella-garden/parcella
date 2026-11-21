# Factures, paiements et relances {#invoices-payments-and-reminders}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Une fois une série de factures finalisée, ses factures continuent leur
vie. Ce chapitre explique comment retrouver une facture, la renvoyer,
enregistrer ce qui a été payé, et relancer les membres qui n'ont pas
payé à l'échéance.

!!! info "Qui peut l'utiliser"
    Fait partie du module **Finances** (désactivé par défaut). Consulter
    les factures, les PDF et la liste des relances nécessite le droit de
    lecture sur **Finances**. Enregistrer des paiements, renvoyer des
    e-mails et envoyer des rappels nécessitent le droit d'écriture ;
    supprimer un paiement nécessite le droit de suppression. Les membres
    du bureau et les administrateurs peuvent tout faire. Voir
    [Finances](index.md).

Les factures ne sont jamais créées qu'en
[finalisant une série de factures](invoice-runs.md#what-finalizing-does).
Vous ne pouvez pas créer, modifier ou supprimer une facture isolée à la
main, et il n'y a pas de fonction d'annulation ni d'avoir.
<!-- TODO(verify): no cancel/credit-note feature exists in the code; if a finalized invoice is wrong, the club has to handle the correction outside Parcella (e.g. record a payment with a note). Confirm the recommended workaround with the maintainers. -->

## Factures (toutes les séries) {#invoices-all-runs}

![Factures](../../assets/screenshots/finances/invoice-list.png)

Ouvrez-la avec **Toutes les factures** sur la page
[Factures annuelles](invoice-runs.md#annual-invoices-list-of-runs). Elle
liste chaque facture de chaque série finalisée, le numéro de facture le
plus élevé en premier. **Retour aux séries de factures** dans la barre du
haut vous ramène.

**Filtre**

| Filtre | Ce qu'il fait |
|---|---|
| **Parcelle** | Factures dont le numéro de parcelle contient ce texte. |
| **N° de facture** | Factures dont le numéro contient ce texte, par ex. `2026/` pour toute l'année 2026. |
| **Destinataire** | Factures dont les noms des destinataires contiennent ce texte. |
| **Montant min.** / **Montant max.** | Montant de la facture (sous-total, sans frais de relance) au moins / au plus égal à cette valeur. |
| **Statut** | **Tous**, **Ouverte**, **Partiellement payée** ou **Payée**. |
| **Filtrer** / **Réinitialiser** | Applique le filtre / efface tous les filtres. |

**Tableau**

| Colonne | Ce qu'elle affiche |
|---|---|
| **N° de facture** | Le numéro de facture ; cliquez pour ouvrir la [facture](#invoice). |
| **Parcelle** | Le numéro de parcelle, ou **Sans parcelle (membre)** pour une facture adressée directement à un membre. |
| **Destinataire** | Les noms auxquels la facture était adressée lors de son émission. |
| **Sous-total** | Le montant de la facture. |
| **Payé** | La somme de tous les paiements enregistrés jusqu'ici. |
| **Statut** | **Ouverte** (rouge), **Partiellement payée** (jaune) ou **Payée** (vert), voir [Statut de paiement](#payment-status). |
| **Payé le** | Les dates de tous les paiements, séparées par des virgules. |

Si rien ne correspond : « Aucune facture ne correspond à ces filtres. »

La même liste, limitée à une série et avec des boutons pour les
paiements et les PDF, se trouve sur la
[page de la série finalisée](invoice-runs.md#invoice-run-finalized).

## Facture {#invoice}

![Facture](../../assets/screenshots/finances/invoice-detail.png)

S'ouvre quand vous cliquez sur un numéro de facture. Le titre est
« Facture *numéro* ».

**Barre du haut**

| Bouton | Ce qu'il fait |
|---|---|
| **PDF** | Ouvre le PDF de la facture dans un nouvel onglet. |
| **Renvoyer l'e-mail** | Renvoie le PDF de la facture par e-mail, même s'il a déjà été envoyé. Nécessite le droit d'écriture. Si personne ne peut être joint, vous voyez « Aucun membre à l'adresse de facturation joignable n'a été trouvé pour cette facture (notifications par e-mail + adresse e-mail enregistrée). » |
| **Retour aux factures** | Retour à la liste de toutes les factures. |

Carte **Facture**

| Champ | Ce qu'il affiche |
|---|---|
| **Parcelle** | Numéro de parcelle, ou **Sans parcelle (membre)**. |
| **Destinataire** | Noms et adresse tels qu'imprimés sur la facture. Ils ont été figés à la finalisation de la série ; les changements d'adresse ultérieurs ne les modifient pas. Si les locataires vivent à des adresses différentes, vous voyez « *n* exemplaires, un par adresse » et les noms et l'adresse de chaque exemplaire. |
| **Sous-total** | Le montant de la facture. |
| **Date d'échéance** | La date d'échéance de la série de factures. |
| **Statut** | Le statut de paiement, suivi de « payé jusqu'ici / total dû ». Le total dû inclut les éventuels frais de relance. |

Carte **Relances** : les rappels envoyés pour cette facture et le
formulaire pour envoyer le suivant, voir
[Envoyer un rappel](#sending-a-reminder).

!!! note "Où sont les paiements ?"
    Les paiements s'enregistrent dans la boîte de dialogue de paiement
    de la liste des factures de la série, voir [Paiements](#payments).
    La page de la facture en montre le résultat dans la ligne
    **Statut**.

### Le PDF de la facture {#the-invoice-pdf}

Le PDF est mis en page comme un courrier commercial allemand pour
enveloppes à fenêtre : logo et nom de l'association en haut, l'adresse
du destinataire là où la fenêtre de l'enveloppe la montre, puis le
numéro de facture, la date, l'échéance et la parcelle, un tableau des
lignes (**Description**, **Qté**, **Prix unitaire**, **Total**), le
**Sous-total**, le texte de pied de page de la série, et les
coordonnées de votre association (adresse, banque) en pied de page.
Ces coordonnées viennent des
[Paramètres de l'association](../../administration/settings.md).

La mise en page suit la norme **DIN 5008 Form B** : l'adresse se place
dans la fenêtre d'une enveloppe DL ou C6/5 à fenêtre, et de petits
repères sur le bord gauche indiquent où plier (au tiers et aux deux
tiers de la page) et où perforer. Les rappels de paiement et les
courriers d'annonce utilisent la même mise en page.

Le nom du fichier commence par la date d'émission et le numéro de
parcelle (ou le nom du membre), suivis du numéro de facture. Une facture
avec un exemplaire par adresse contient tous les exemplaires dans son
PDF, chacun sur ses propres pages.

## Paiements {#payments}

Un paiement est de l'argent reçu pour une facture. Vous pouvez
l'enregistrer de deux façons :

- **À la main :** sur la [page de la série finalisée](invoice-runs.md#payment-dialog),
  cliquez sur **Paiement** à côté de la facture, saisissez **Montant**,
  **Payé le**, une **Note** et un **Compte** facultatifs, et cliquez sur
  **Ajouter un paiement**.
- **À partir du relevé bancaire :** sur la
  [page des écritures d'un compte](bank-accounts.md#bookings-of-an-account),
  ajoutez une écriture ou importez un fichier CSV et choisissez la
  facture ouverte correspondante. Parcella enregistre alors le paiement
  pour vous, avec le compte déjà renseigné.

Une facture peut avoir un nombre quelconque de paiements : les paiements
partiels et échelonnés ne posent donc aucun problème. Pour corriger un
paiement erroné, supprimez-le (icône corbeille dans la boîte de dialogue
de paiement, nécessite le droit de suppression) et saisissez-le à
nouveau.

!!! tip "« Payé le » détermine l'année"
    L'[état comptable](bookkeeping.md#accounting-statement) compte les
    recettes à la date **Payé le**, pas à la date de facture. Une
    facture 2026 payée en janvier 2027 est une recette de 2027.

### Statut de paiement {#payment-status}

Le statut est recalculé à partir des paiements à chaque fois, il n'est
donc jamais périmé :

| Statut | Quand |
|---|---|
| **Ouverte** | Rien n'a encore été payé. |
| **Partiellement payée** | Quelque chose a été payé, mais moins que le montant de la facture plus tous les frais de relance. |
| **Payée** | Les paiements atteignent (ou dépassent) le montant de la facture plus tous les frais de relance. |

Les trop-perçus sont acceptés et s'affichent simplement comme
**Payée** ; Parcella ne gère pas de solde créditeur.

## Relances {#reminders}

![Relances](../../assets/screenshots/finances/reminders.png)

Ouvrez-la avec **Finances → Relances** ou la carte **Relances** du
tableau de bord. La liste **Factures en retard** affiche chaque facture
pas entièrement payée dont la date d'échéance de la série est dépassée,
la plus en retard en premier. C'est une liste de travail pour le
trésorier : ouvrez chaque facture et décidez s'il faut envoyer un
rappel.

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Parcelle** | Le numéro de parcelle. Vide pour une facture de membre. |
| **Destinataire** | Les noms des destinataires. |
| **N° de facture** | Le numéro de facture. |
| **Date d'échéance** | La date d'échéance de la série. |
| **Retard** | Le nombre de jours depuis l'échéance, par ex. « 14 jours ». |
| **Montant dû** | Ce qui reste dû : montant de la facture plus frais de relance moins paiements. |
| **Rappels envoyés** | Le nombre de rappels envoyés, avec la date du dernier, ou « Aucun envoyé pour l'instant ». |
| **Ouvrir** | Ouvre la facture, où vous envoyez le rappel. |

Si rien n'est en retard : « Aucune facture en retard — rien à
rappeler. »

Une facture disparaît de cette liste dès qu'elle est entièrement payée.

### Envoyer un rappel {#sending-a-reminder}

Sur la [facture](#invoice), la carte **Relances** liste chaque rappel
déjà envoyé :

| Colonne | Ce qu'elle affiche |
|---|---|
| « Rappel n° *n* » | Le niveau du rappel : le premier rappel est le n° 1, le suivant le n° 2, et ainsi de suite. |
| Date | Quand il a été créé. |
| Envoi | « Envoyé par e-mail », « À imprimer/envoyer par courrier » s'il n'a pas pu être envoyé par e-mail, ou « Envoyé par e-mail, plus des exemplaires à imprimer/envoyer par courrier » si certaines adresses l'ont reçu par e-mail et d'autres ont besoin d'un courrier. |
| Frais | Les frais facturés avec ce rappel, le cas échéant. |
| Icône PDF | Ouvre le PDF du rappel dans un nouvel onglet -- imprimez-le d'ici pour un envoi postal. Il contient les courriers à poster, un par adresse pour les personnes sans e-mail qui y vivent (tous les exemplaires si tout le monde a reçu l'e-mail). |

S'il n'y en a encore aucun : « Aucun rappel envoyé pour l'instant. »

Sous la liste, tant que la facture n'est pas entièrement payée et que
vous avez le droit d'écriture :

| Champ | Ce qu'il fait |
|---|---|
| **Frais (facultatif)** | Des frais de relance, par ex. `5,00`. Ils s'ajoutent à ce que doit la facture. Laissez vide pour aucun frais. |
| **Message (facultatif)** | Un court texte imprimé en bas du rappel. |
| **Envoyer le rappel** | Crée le rappel suivant et l'envoie. |

Ce que fait **Envoyer le rappel** : « Génère le rappel suivant au format
PDF -- les frais (le cas échéant) sont ajoutés au montant dû. L'envoie
par e-mail si le membre y a consenti et dispose d'une adresse
enregistrée, sinon le prépare pour l'impression/l'envoi postal. »

- Le rappel a toujours un niveau de plus que le précédent. Il n'y a pas
  d'étapes de relance fixes ; votre association décide combien de
  rappels envoyer et quand.
- L'e-mail part à la même personne que la facture (voir
  [qui reçoit un e-mail](invoice-runs.md#delivery)), avec l'objet
  « Rappel de paiement n° *n* pour la facture *numéro* — *nom de
  l'association* » et le PDF en pièce jointe.
- Si l'e-mail ne peut pas être envoyé, le rappel est conservé et marqué
  « À imprimer/envoyer par courrier ». Imprimez-le via l'icône PDF.

Le PDF du rappel est intitulé « Rappel de paiement n° *n* », fait
référence à la facture et à sa date, et liste le **Montant initial**,
**Déjà payé**, les **Frais des rappels précédents** et les **Frais de ce
rappel** (lignes de frais seulement s'il y en a), le montant maintenant
dû, votre message et une phrase finale demandant le paiement.

!!! warning "Les frais ne peuvent pas être retirés"
    Un rappel, et ses frais, ne peuvent être ni supprimés ni modifiés
    une fois envoyés. Vérifiez bien les frais avant de cliquer sur
    **Envoyer le rappel**. Si vous saisissez autre chose qu'un nombre
    dans **Frais (facultatif)**, le rappel est envoyé sans frais.

## Voir aussi {#related}

- [Séries de factures](invoice-runs.md) -- d'où viennent les factures.
- [Comptes bancaires et écritures](bank-accounts.md) -- enregistrer les
  paiements depuis votre relevé bancaire.
- [Établir les factures annuelles](../../guides/annual-invoicing.md)
- [Journal des e-mails](../../administration/email-log.md) -- vérifier si
  l'e-mail d'une facture ou d'un rappel a été accepté par le serveur de
  messagerie.

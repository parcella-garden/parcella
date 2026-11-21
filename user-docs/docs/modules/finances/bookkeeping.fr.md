# Catégories, budget et synthèse {#categories-budget-and-statement}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les catégories comptables sont des codes courts comme « 40000
Cotisations » que vous attachez aux lignes de facture et aux postes des
factures reçues. Grâce à elles, Parcella peut vous dire d'où vient
l'argent de l'association et où il est allé : dans la liste de toutes
les écritures, dans l'état comptable de trésorerie pour l'administration
fiscale, et dans le budget prévisionnel de l'année suivante.

!!! info "Qui peut l'utiliser"
    Fait partie du module **Finances** (désactivé par défaut). Les quatre
    écrans peuvent être consultés avec le droit de lecture sur
    **Finances**, y compris l'export PDF de l'état. Ajouter, modifier et
    importer des catégories et enregistrer le budget nécessitent le droit
    d'écriture ; supprimer une catégorie nécessite le droit de
    suppression. Les membres du bureau et les administrateurs peuvent
    tout faire. Voir [Finances](index.md).

## Catégories comptables {#bookkeeping-categories}

![Catégories comptables](../../assets/screenshots/finances/category-list.png)

Ouvrez-les avec la carte **Catégories** du tableau de bord des finances.
**Retour aux Finances** dans la barre du haut vous ramène.

Parcella ne fournit pas de plan comptable officiel. Les données
d'exemple contiennent trois catégories d'exemple ; remplacez-les par le
plan de votre association, saisi à la main ou importé depuis votre
logiciel de comptabilité.

### Nouvelle catégorie {#new-category}

Affiché avec le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Code** | Obligatoire. Exactement cinq chiffres, par ex. `40000`. Ne doit pas être utilisé par une autre catégorie. |
| **Intitulé** | Obligatoire, par ex. « Cotisations ». |
| **Groupe** | **Recettes**, **Dépenses**, **Immobilisations**, **Capitaux propres et dettes** ou **Autre**. Le budget prévisionnel place les catégories **Recettes** dans sa section des recettes et toutes les autres dans sa section des dépenses. |
| **Ajouter la catégorie** | Enregistre la catégorie. |

Erreurs : « Catégorie invalide -- le code doit comporter exactement
5 chiffres, un intitulé et un groupe sont requis. » ou « Une catégorie
avec ce code existe déjà. »

### Importer depuis un CSV {#import-from-csv}

Affiché avec le droit d'écriture. Choisissez un **Fichier CSV** et
cliquez sur **Importer**.

Le fichier nécessite une ligne d'en-tête `code,title,group`, séparée par
des virgules. **group** vaut `income`, `expense`, `fixed_assets`,
`equity_liabilities` ou `other` (majuscules ou minuscules). Par
exemple :

```
code,title,group
40000,Membership fees,income
40100,Lease income,income
60020,Volunteer allowance,expense
```

Les lignes avec un code invalide, un groupe inconnu, un intitulé
manquant ou un code déjà existant sont ignorées. Le résultat s'affiche
sous la forme « *n* importée(s), *m* ignorée(s). » Les catégories
existantes ne sont jamais modifiées par un import.

### Liste des catégories {#categories-list}

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Code**, **Intitulé**, **Groupe** | La catégorie. Avec le droit d'écriture, ils sont modifiables dans la ligne ; cliquez sur l'icône de coche pour enregistrer. Les mêmes règles que pour une nouvelle catégorie s'appliquent. |
| Icône corbeille | Supprime la catégorie après confirmation. Nécessite le droit de suppression. |

S'il n'y en a aucune : « Aucune catégorie pour le moment -- ajoutez-en
une ci-dessus ou importez un CSV. »

!!! warning "Supprimer une catégorie"
    « Supprimer cette catégorie ? Les lignes qui l'utilisent continuent
    de fonctionner, simplement sans catégorie. » Les lignes de facture,
    modèles d'articles et postes de factures reçues perdent la
    catégorie ; les paiements passés correspondants apparaissent alors
    comme « Sans catégorie » dans l'état. **Les montants prévus pour
    cette catégorie dans le budget prévisionnel sont supprimés.**
    Renommez une catégorie plutôt que de la supprimer et la recréer.

## Toutes les écritures {#all-bookings}

![Toutes les écritures](../../assets/screenshots/finances/bookings.png)

Ouvrez-la avec la carte **Toutes les écritures** du tableau de bord.
Elle liste chaque paiement reçu par l'association pour ses factures et
chaque paiement effectué pour des factures reçues, sur tous les comptes,
le plus récent en premier. Les écritures qui ne sont pas liées à une
facture (frais bancaires, remboursements) n'y figurent pas -- voir les
[écritures](bank-accounts.md#bookings-of-an-account) du compte pour
celles-ci.

**Filtre**

| Filtre | Ce qu'il fait |
|---|---|
| **Rechercher** | Trouve les paiements dont l'expéditeur/destinataire ou la description contient ce texte. |
| **Du** / **Au** | Date de paiement à ces dates ou entre elles. |
| **Catégorie** | **Toutes les catégories**, ou seulement les paiements dont la facture a une ligne dans cette catégorie. |
| **Type** | **Recettes et dépenses**, **Recette** ou **Dépense**. |
| **Montant min.** / **Montant max.** | Montant du paiement dans cette plage. Les dépenses comptent ici comme montants positifs. |
| **Filtrer** / **Réinitialiser** | Applique le filtre / l'efface. |

**Tableau** (l'en-tête indique le nombre, par ex. « 42 écriture(s) »)

| Colonne | Ce qu'elle affiche |
|---|---|
| **Date** | La date du paiement. |
| **Type** | **Recette** (vert) ou **Dépense** (rouge). |
| **Expéditeur / destinataire** | Le destinataire de la facture, ou l'expéditeur de la facture reçue. Cliquez dessus pour ouvrir cette facture. |
| **Catégories** | Toutes les catégories des lignes de la facture, ou « Sans catégorie ». |
| **Description** | Les noms et descriptions des lignes de la facture. |
| **Montant** | Le montant payé, en vert pour les recettes, en rouge pour les dépenses. |

Si rien ne correspond : « Aucune écriture ne correspond à ces filtres. »

!!! note
    Le montant affiché est le paiement entier, même si la facture a des
    lignes dans plusieurs catégories. L'[état comptable](#accounting-statement)
    le répartit entre les catégories ; cette liste, non.

## État comptable {#accounting-statement}

![État comptable](../../assets/screenshots/finances/accounting-statement.png)

Ouvrez-le avec la carte **État comptable** du tableau de bord. Le titre
est « État comptable *année* ». C'est un simple état des recettes et
dépenses par catégorie selon la trésorerie, du type qu'une association
à but non lucratif remet à l'administration fiscale ou présente à
l'assemblée générale annuelle.

**Barre du haut**

| Élément | Ce qu'il fait |
|---|---|
| Année | Liste déroulante avec chaque année où un paiement a été enregistré, plus l'année en cours. Affiche la plus récente en premier ; la changer recharge la page. |
| **Exporter en PDF** | Télécharge l'état de l'année choisie en PDF avec l'en-tête de votre association (« État de trésorerie *année* »). |
| **Retour aux Finances** | Retour au tableau de bord. |

La page a deux cartes, **Recettes** et **Dépenses**, listant chacune
**Catégorie** (« code · intitulé », ou « Sans catégorie ») et
**Montant**, avec une ligne **Total**. En dessous, le **Résultat net**
(recettes moins dépenses) s'affiche en vert, ou en rouge s'il est
négatif. Une carte sans entrées indique « Aucune entrée pour cette
année. »

Comment les chiffres sont comptés :

- **Seul l'argent qui a réellement bougé compte.** Les recettes sont les
  paiements enregistrés pour les factures émises, les dépenses les
  paiements enregistrés pour les factures reçues. Les factures impayées
  n'apparaissent pas.
- **La date de paiement détermine l'année**, pas la date de facture.
- **Chaque paiement est réparti par catégorie** au prorata des lignes de
  la facture. Si une facture de 100,00 comporte 80,00 de loyer et 20,00
  d'eau, un paiement partiel de 50,00 compte 40,00 pour le loyer et
  10,00 pour l'eau. Des frais de relance inclus dans un paiement sont
  répartis de la même façon.
- Les lignes sans catégorie, et les factures antérieures à l'utilisation
  des catégories, apparaissent comme « Sans catégorie ».
- Les écritures de compte non liées à une facture (frais bancaires,
  intérêts, achats en espèces saisis sur un compte) ne sont **pas**
  incluses. Enregistrez ces coûts comme [facture reçue](incoming-invoices.md)
  avec un paiement s'ils doivent apparaître ici.

!!! tip
    Pour un état propre, donnez une catégorie à chaque article du
    catalogue et à chaque poste de facture reçue *avant* de finaliser la
    série ou d'enregistrer la facture. Les catégories sont copiées sur
    les factures à la finalisation de la série et ne peuvent plus y être
    ajoutées ensuite.

## Budget prévisionnel {#budget-plan}

![Budget prévisionnel](../../assets/screenshots/finances/budget.png)

Ouvrez-le avec la carte **Budget prévisionnel** du tableau de bord. Le
titre est « Budget prévisionnel *année* ». Il s'ouvre sur **l'année
suivante**. Utilisez les flèches **Année précédente** / **Année
suivante** dans la barre du haut pour planifier une autre année ;
**Retour aux Finances** revient au tableau de bord.

Le tableau a une ligne par catégorie comptable et ces colonnes :

| Colonne | Ce qu'elle affiche |
|---|---|
| **Catégorie** | Code et intitulé. |
| « *année* réalisé » (trois colonnes) | Ce qui a réellement été encaissé ou payé chacune des trois années précédant l'année planifiée, exactement comme dans l'[état comptable](#accounting-statement). Pour l'année en cours, l'en-tête est « *année* à ce jour », car l'année n'est pas terminée. |
| « *année* prévu » | Le montant que vous prévoyez pour cette catégorie. Modifiable avec le droit d'écriture. |

Les lignes sont regroupées :

- **Recettes** -- toutes les catégories du groupe **Recettes**, avec une
  ligne **Total**.
- **Dépenses** -- toutes les autres catégories (dépenses,
  immobilisations, capitaux propres et dettes, autre), avec une ligne
  **Total**.
- **Autres (sans catégorie ou comptabilisé de l'autre côté)** --
  apparaît dans une section seulement si nécessaire. Elle contient ce
  que l'état a compté mais qu'aucune ligne de la section n'affiche :
  paiements sans catégorie, ou par exemple le paiement d'une facture
  reçue dont le poste porte une catégorie de recettes. Ainsi, les totaux
  de section correspondent toujours à l'état.
- **Résultat (recettes − dépenses)** en bas, en rouge s'il est négatif.

Saisissez les montants prévus sous forme de nombres, par ex. `1050.00`,
et cliquez sur **Enregistrer le budget**. Vous voyez « Budget
prévisionnel enregistré. ». « Les années passées montrent ce qui a
réellement été payé (comme dans l'état de trésorerie). Un champ vide
signifie « rien de prévu ». » Vider un champ supprime la prévision pour
cette catégorie. Ce qui n'est pas un nombre est refusé avec « Saisissez
les montants sous forme de nombres, p. ex. 1050.00. » et rien n'est
enregistré.

Seule la prévision est stockée. Les colonnes du réalisé sont recalculées
à chaque fois à partir des paiements enregistrés, elles concordent donc
toujours avec l'état comptable.

Si vous n'avez encore aucune catégorie : « Pas encore de catégories
comptables. Le budget a une ligne par catégorie. » avec un lien
**Gérer les catégories**.

## Voir aussi {#related}

- [Séries de factures](invoice-runs.md) -- où les lignes de facture
  reçoivent leur catégorie.
- [Factures reçues](incoming-invoices.md) -- où les postes de dépenses
  reçoivent leur catégorie.
- [Comptes bancaires et écritures](bank-accounts.md)

# Inventaire {#inventory}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

L'inventaire est le registre des biens de l'association : tout ce que
possède l'association, et les objets que des membres possèdent
personnellement mais gardent sur le terrain de l'association. Les objets
sont regroupés dans des catégories que vous définissez vous-même, portent
leur prix d'achat, leur valeur actuelle et leur coût de remplacement, et
peuvent être prêtés aux membres avec un système simple d'emprunt et de
retour.

!!! info "Qui peut l'utiliser"
    Les membres du bureau et les administrateurs ont toujours un accès
    complet. Les autres utilisateurs ont besoin d'un groupe qui accorde
    des droits sur **Inventaire** (voir
    [Groupes](../administration/groups.md)) :

    - **Lecture** -- voir la liste des objets, les pages des objets et
      les prêts en cours.
    - **Écriture** -- créer, modifier et retirer des objets, gérer les
      catégories, prêter des objets et les marquer comme retournés.
    - **Suppression** -- supprimer définitivement des objets et des
      catégories.

    Le module s'active avec **Inventaire** sous
    [Activer et désactiver les modules](../administration/modules.md).
    Il est activé par défaut.

## Liste de l'inventaire {#inventory-list}

![Liste de l'inventaire](../assets/screenshots/inventory/list.png)

**Inventaire** dans la navigation liste tous les objets, regroupés en
une carte par catégorie dans l'ordre alphabétique. Les objets sans
catégorie viennent en dernier sous **Sans catégorie**. Dans une carte,
les objets sont triés par nom.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Prêts en cours** | Ouvre la [liste de tout ce qui est actuellement prêté](#active-loans). |
| **Gérer les catégories** | Ouvre les [catégories](#inventory-categories). Affiché seulement avec le droit d'écriture. |
| **Nouvel objet** | Ouvre un [formulaire d'objet](#item-form) vide. Affiché seulement avec le droit d'écriture. |
| **Toutes les catégories** / une catégorie | N'affiche que les objets d'une catégorie. |
| **Inclure les objets retirés** | Liste aussi les objets [retirés](#retiring-and-deleting), affichés en gris avec un badge **Retiré**. Désactivé par défaut. |

| Colonne | Ce qu'elle affiche |
|---|---|
| **Nom** | L'objet, avec un lien vers sa page. Badges : **Retiré**, **Empruntable**. |
| **Propriétaire** | **Propriété du club** ou **Propriété d'un membre**. |
| **Emplacement** | L'emplacement de stockage. |
| **Quantité** | Pour les objets empruntables, disponible / possédé (par ex. **1 / 2** quand l'un des deux est prêté) ; sinon la quantité possédée. |
| **Valeur** | La valeur actuelle, si elle est saisie. |
| Bouton œil | Ouvre l'objet. |

## Page de l'objet {#item-page}

![Page de l'objet](../assets/screenshots/inventory/detail.png)

Cliquez sur le nom d'un objet pour ouvrir sa page.

### Boutons {#buttons}

| Bouton | Ce qu'il fait |
|---|---|
| **Modifier** | Ouvre le [formulaire de l'objet](#item-form). Nécessite le droit d'écriture. |
| **Retirer** | Marque l'objet comme n'étant plus possédé ou en service, après confirmation. Nécessite le droit d'écriture ; n'est plus affiché une fois l'objet retiré. Voir [Retirer et supprimer](#retiring-and-deleting). |
| **Supprimer** | Supprime définitivement l'objet et tout son historique de prêts, après confirmation. Nécessite le droit de suppression. |
| **Retour** | Revient à la liste de l'inventaire. |

Un objet retiré affiche l'avis « Cet objet est retiré -- plus
possédé/en service. » en haut.

### Vue d'ensemble {#overview}

| Champ | Ce qu'il affiche |
|---|---|
| **Catégorie** | La catégorie, ou **Sans catégorie**. |
| **Propriétaire** | **Propriété du club**, ou le nom du membre propriétaire. |
| **Emplacement de stockage** | Où l'objet est conservé, ou « - ». |
| **Quantité** | Pour les objets empruntables « disponible / possédé **disponible(s)** », sinon la quantité possédée. |
| **Description**, **Notes** | Affichées seulement si elles sont remplies. |

### Finances {#financials}

| Champ | Ce qu'il affiche |
|---|---|
| **Date d'achat** | Quand il a été acheté. |
| **Prix d'achat** | Ce qu'il a coûté. |
| **Valeur actuelle** | L'estimation actuelle du bureau, avec « au » et la date de la dernière vérification, si elle est saisie. |
| **Coût de remplacement** | Ce que coûterait son remplacement. |

Les champs vides affichent « - ».

### Emprunter {#check-out}

Affiché seulement pour les objets marqués comme empruntables. Si rien
n'est disponible, il indique **Rien de disponible à l'emprunt pour le
moment.** Le formulaire nécessite le droit d'écriture.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Membre** | Qui emprunte l'objet. Liste les membres actuels. Obligatoire. |
| **Quantité** | Combien d'unités. Au moins 1, au plus le nombre actuellement disponible. 1 par défaut. |
| **Date** | Le jour de l'emprunt. Par défaut aujourd'hui. |
| **Frais** | Facultatif. Un nombre seulement, par ex. `5` ou `2,50` -- sans symbole monétaire ni texte. Laissé vide, ce sont les **Frais de prêt suggérés** de l'objet qui s'appliquent (l'indication sous le champ les affiche). |
| **Note** | Texte libre facultatif, par ex. « retour d'ici dimanche ». |
| **Emprunter** | Enregistre le prêt. La quantité disponible diminue en conséquence. |

En cas de problème -- aucun membre choisi, plus d'unités que disponibles
(« Seulement 1 sur 2 disponible(s) actuellement. »), des frais contenant
du texte, une date invalide -- la page affiche le message au-dessus du
formulaire et conserve ce que vous avez saisi.

!!! note "Les frais sont enregistrés, pas facturés"
    Les frais sont stockés avec le prêt pour que le bureau sache ce qui a
    été convenu. Parcella ne crée ni facture ni écriture pour eux.

### Historique des prêts {#loan-history}

Chaque prêt de cet objet, le plus récent en premier.

| Colonne | Ce qu'elle affiche |
|---|---|
| **Membre** | Qui l'a emprunté. |
| **Qté** | Combien d'unités. |
| **Emprunté** | La date d'emprunt. |
| **Retourné** | La date de retour, ou un badge **En cours** tant qu'il est encore sorti. |
| **Frais** | Les frais facturés, ou « - ». |
| **Marquer comme retourné** | Enregistre le retour à la date du jour. Affiché pour les prêts en cours avec le droit d'écriture. |

## Formulaire de l'objet {#item-form}

![Nouvel objet](../assets/screenshots/inventory/form-new.png)

Le même formulaire sert pour **Nouvel objet** et **Modifier**, avec le
titre **Objet d'inventaire**.

### Général {#general}

| Champ | Ce qu'il fait |
|---|---|
| **Nom** | Ce qu'est l'objet. Obligatoire. |
| **Catégorie** | L'une de vos [catégories](#inventory-categories), ou **Aucune catégorie**. |
| **Description** | Description plus longue facultative. |
| **Emplacement de stockage** | Où il est conservé, par ex. « Cabane à outils ». |

### Propriété {#ownership}

| Champ | Ce qu'il fait |
|---|---|
| **Propriété du club** | Le choix par défaut. |
| **Propriété personnelle d'un membre** | Pour les objets que des membres gardent sur le terrain de l'association mais qui leur appartiennent -- utile à noter pour l'assurance et la responsabilité. Affiche **Membre propriétaire**. |
| **Membre propriétaire** | Le membre propriétaire. Obligatoire quand l'objet appartient à un membre ; liste les membres actuels. |

### Finances {#financials_1}

La valeur actuelle est saisie à la main chaque fois que quelqu'un la
vérifie. Parcella n'amortit rien automatiquement.

| Champ | Ce qu'il fait |
|---|---|
| **Date d'achat** | Facultatif. |
| **Prix d'achat** | Facultatif. |
| **Valeur actuelle** | Facultatif. Votre meilleure estimation actuelle. |
| **Coût de remplacement** | Facultatif. |
| **Valeur vérifiée pour la dernière fois le** | Date facultative, pour que chacun voie à quel point la valeur actuelle est à jour. |

Les montants sont uniquement des nombres : `5`, `2,50` ou `2.50`. Du
texte, un symbole monétaire ou un montant négatif est refusé avec un
message.

### Prêt {#lending}

| Champ | Ce qu'il fait |
|---|---|
| **Quantité possédée** | Combien d'unités identiques représente cette entrée -- trois brouettes peuvent être un seul objet de quantité 3. Un nombre entier de 1 ou plus ; 1 par défaut. |
| **Les membres peuvent emprunter cet objet** | Active l'emprunt et le retour pour cet objet. Affiche **Frais de prêt suggérés**. |
| **Frais de prêt suggérés** | Facultatif. Utilisés comme frais quand un prêt est enregistré sans frais ; modifiables pour chaque prêt. |

### Notes {#notes}

Texte libre pour tout le reste.

Cliquez sur **Enregistrer** pour enregistrer l'objet et ouvrir sa page,
ou sur **Annuler**.

!!! tip "Une entrée par type d'objet"
    Enregistrez les objets identiques comme un seul objet avec une
    quantité, pas comme des objets séparés. Le prêt affiche alors
    « 2 sur 3 disponibles », et un changement de prix se fait une seule
    fois.

## Retirer et supprimer {#retiring-and-deleting}

- **Retirez** un objet qui a réellement existé et qui est maintenant
  vendu, mis au rebut ou perdu. Il reste enregistré avec ses prix et son
  historique de prêts, mais est masqué de la liste sauf si vous cochez
  **Inclure les objets retirés**. Il n'y a pas de bouton pour annuler un
  retrait.
- **Supprimez** seulement une véritable erreur, par ex. un objet saisi
  deux fois. Cela supprime définitivement l'objet et tous ses prêts.
<!-- TODO(verify): a retired borrowable item still shows the Check out form and can still be lent; and there is no way in the web UI to un-retire an item. Confirm both are intended. -->

## Catégories de l'inventaire {#inventory-categories}

![Catégories de l'inventaire](../assets/screenshots/inventory/categories.png)

**Gérer les catégories** dans la liste de l'inventaire ouvre cette page.
Elle nécessite le droit d'écriture. **Retour** revient à la liste.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Nom (par ex. « Aire de jeux, Clôtures, Serrures et clés ») | Le nom de la nouvelle catégorie. Obligatoire ; ne doit pas déjà exister (« Une catégorie portant ce nom existe déjà. »). |
| **Description facultative** | Une courte description. |
| **Ajouter** | Crée la catégorie. |
| Colonnes **Nom**, **Description** | Les catégories existantes. |
| Bouton corbeille | Supprime la catégorie après confirmation. Ses objets ne sont **pas** supprimés -- ils deviennent **Sans catégorie**. Nécessite le droit de suppression. |

Les catégories ne peuvent pas être renommées sur cette page. Pour en
renommer une, créez la nouvelle catégorie, déplacez-y les objets en les
modifiant, et supprimez l'ancienne.

## Prêts en cours {#active-loans}

![Prêts en cours](../assets/screenshots/inventory/active-loans.png)

**Prêts en cours** dans la liste de l'inventaire affiche tout ce qui est
actuellement prêté, tous objets confondus, le plus ancien prêt en
premier. Utilisez-la pour voir qui a quoi avant une session de travail
ou à la fin de la saison.

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Objet** | L'objet, avec un lien vers sa page. |
| **Membre** | Qui l'a. |
| **Qté** | Combien d'unités. |
| **Depuis** | La date d'emprunt. |
| **Frais** | Les frais facturés, ou « - ». |
| **Marquer comme retourné** | Enregistre le retour à la date du jour et ouvre la page de l'objet. Nécessite le droit d'écriture. |

Si rien n'est sorti, la page indique **Rien n'est actuellement
emprunté.**

!!! tip "Voir la disponibilité dans le calendrier"
    Si le module calendrier est activé, **Calendrier → Mes calendriers →
    Ressources** liste les objets empruntables appartenant à
    l'association (sans les objets retirés) avec leur statut --
    **Disponible**, **Prêté** ou « 1 sur 2 disponibles » -- et qui les a
    depuis quand. Cela nécessite aussi le droit de lecture sur
    l'inventaire. Voir [Calendrier](calendar.md).

## Voir aussi {#related}

- [Membres](members.md) -- emprunteurs et propriétaires des objets
  appartenant à des membres
- [Demandes d'achat](purchase-requests.md) -- obtenir l'approbation
  avant d'acheter quelque chose de nouveau
- [Groupes](../administration/groups.md) -- donner à quelqu'un l'accès à
  l'inventaire sans les droits complets du bureau

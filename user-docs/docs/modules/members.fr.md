# Membres {#members}

!!! warning "Pas encore mis à jour"
    Cette page décrit une version antérieure. La version anglaise est à jour (changez de langue en haut).

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

La liste des membres est le cœur de Parcella : toutes les personnes qui
font partie de votre association, avec adresse, coordonnées bancaires,
coordonnées de contact et les parcelles qu'elles occupent. Les
factures, les heures de travail, les envois, la liste des anniversaires
et la feuille de présence aux assemblées lisent toutes leurs données
ici.

!!! info "Qui peut l'utiliser"
    Les membres font partie du cœur de l'application et sont toujours
    activés. Ils ne peuvent pas être désactivés.

    - **Toute personne pouvant se connecter** peut consulter la liste
      des membres, les pages des membres, la liste des étiquettes,
      l'export CSV et la feuille de présence.
    - **Ajouter et modifier** des membres, numéros de téléphone,
      adresses e-mail, étiquettes et attributions de parcelles nécessite
      le droit d'*écriture* sur **Membres et parcelles**.
    - **Supprimer** un membre, un numéro de téléphone, une adresse e-mail
      ou une étiquette nécessite le droit de *suppression* sur **Membres
      et parcelles**.

    Les membres du bureau et les administrateurs ont tous ces droits.
    Les autres obtiennent l'écriture ou la suppression via un groupe
    (voir [Rôles, groupes et droits](../getting-started/roles-and-permissions.md)).

## Liste des membres {#member-list}

![Liste des membres](../assets/screenshots/members/list.png)

Ouvrez **Membres** dans le menu principal. La liste affiche les membres
actifs, triés par nom puis par prénom. Le pied indique combien de
membres figurent actuellement dans la liste.

### Boutons en haut {#buttons-at-the-top}

| Bouton | Ce qu'il fait |
|---|---|
| **Import CSV** | Ouvre la boîte de dialogue d'import d'un fichier CSV (voir [Importer des membres depuis un fichier CSV](#importing-members-from-a-csv-file)). Nécessite le droit d'écriture. |
| **Export CSV** | Télécharge les membres *actuellement affichés* sous forme de fichier CSV. La recherche, les cases à cocher et le filtre d'étiquette s'appliquent tous (voir [Export CSV](#csv-export)). |
| **Écrire à ces *N* membres** | Démarre une nouvelle annonce adressée exactement aux membres de la liste filtrée. Affiché seulement une fois que vous avez cherché ou filtré, tant que le module **Annonces** est activé, et seulement aux membres du bureau et aux administrateurs. Pour écrire à tout le monde, démarrez plutôt l'annonce depuis [Annonces](announcements.md). |
| **Gérer les étiquettes** | Ouvre la page [Étiquettes des membres](#member-tags). |
| **Feuille de présence** | Ouvre la [Feuille de présence de l'assemblée](#meeting-sign-in-sheet). |
| **Nouveau membre** | Ouvre un [formulaire de membre](#new-member-and-edit-member) vide. Nécessite le droit d'écriture. |

### Recherche et filtres {#search-and-filters}

| Champ / bouton | Ce qu'il fait |
|---|---|
| Champ de recherche | Trouve les membres par prénom ou nom, rue, code postal, ville, IBAN, notes, adresse e-mail, numéro de téléphone et numéro de parcelle. Un numéro de parcelle ne trouve que les locataires *actuels* de la parcelle -- sauf si **Afficher uniquement les inactifs** est coché : il trouve alors aussi les anciens locataires. Comme les notes sont aussi cherchées, un numéro de ticket noté sur un membre retrouve ce membre. |
| **Afficher uniquement les inactifs** | N'affiche *que* les membres qui ne sont pas actifs : leur date **Membre jusqu'au** est passée, ou leur date **Membre depuis** est encore dans le futur. Utilisez-le pour retrouver des membres anciens ou décédés. |
| **Actifs confirmés uniquement** | N'affiche que les membres actifs qui ont une date **Membre depuis**. Les membres sans date de début (affichés comme *en attente*) sont laissés de côté. |
| **Infos e-mail = oui uniquement** | N'affiche que les membres qui ont coché **Peut recevoir des informations par e-mail**. |
| Liste déroulante des étiquettes (**Toutes les étiquettes**) | N'affiche que les membres ayant l'étiquette choisie. La liste apparaît dès qu'au moins une étiquette existe. Vous pouvez filtrer sur une seule étiquette à la fois. |
| **Rechercher** | Applique le texte de recherche. Les cases à cocher et la liste des étiquettes s'appliquent dès que vous les changez. |
| **Réinitialiser** | Efface tous les filtres. Affiché seulement tant qu'un filtre est actif. |

Quand **Afficher uniquement les inactifs** est coché, il l'emporte sur
**Actifs confirmés uniquement**. Un avis bleu au-dessus du tableau vous
rappelle lequel des deux filtres est actif.

Votre filtre vous suit : si vous ouvrez un membre depuis une liste
filtrée, les boutons **Précédent** et **Suivant** de la page du membre
parcourent la même liste filtrée, et **Retour** vous y ramène.

### Colonnes {#columns}

| Colonne | Ce qu'elle affiche |
|---|---|
| Case à cocher | Sélectionne le membre pour **Exporter la sélection** ou **Écrire à la sélection** (voir ci-dessous). |
| **Nom** | Nom, prénom -- cliquez dessus pour ouvrir le membre. Les étiquettes du membre apparaissent comme de petits libellés gris à côté du nom ; cliquez sur un libellé pour filtrer la liste sur cette étiquette. |
| **Membre depuis** | Le début de l'adhésion, ou « – » si aucun n'est enregistré. |
| **Parcelles** | Les numéros des parcelles attribuées au membre. <!-- TODO(verify): the list shows every parcel assignment of the member, including tenancies that have already ended -- confirm whether former parcels are meant to appear here. --> |
| **Statut** | **actif**, **inactif** ou **en attente** (voir ci-dessous). |
| Bouton œil | Ouvre la page du membre, comme un clic sur le nom. |

Le badge de statut signifie :

- **actif** -- l'adhésion a commencé et n'est pas terminée.
- **en attente** -- aucune date **Membre depuis** n'est encore
  enregistrée. Un membre en attente compte quand même comme actif
  partout ailleurs (factures, feuille de présence, chiffres du tableau
  de bord) ; le badge indique seulement que la date de début n'a pas été
  confirmée.
- **inactif** -- l'adhésion est terminée, ou n'a pas encore commencé.
  S'il y a une date **Membre jusqu'au**, le badge affiche « depuis »
  cette date.

### Choisir des membres à la main {#picking-members-by-hand}

Chaque ligne a une case à cocher : vous pouvez donc choisir quelques
membres dans la liste -- par exemple, filtrer toutes les personnes qui
acceptent les informations par e-mail, puis en cocher 12.

| Bouton | Ce qu'il fait |
|---|---|
| **Tout sélectionner** | Coche chaque membre de la liste actuelle. |
| **Tout désélectionner** | Efface toutes les coches. |
| ***N* sélectionné(s)** | Compte les membres cochés. |
| **Exporter la sélection** | Télécharge un fichier CSV avec seulement les membres cochés. Désactivé tant que vous n'avez coché personne. |
| **Écrire à la sélection** | Démarre une nouvelle annonce adressée seulement aux membres cochés. Affiché seulement tant que le module **Annonces** est activé, et seulement aux membres du bureau et aux administrateurs. |

!!! warning "Les coches sont perdues quand vous changez le filtre"
    Changer la recherche, une case à cocher ou la liste des étiquettes
    recharge la page, et vos coches disparaissent. Réglez d'abord le
    filtre, puis cochez.

Quand vous suivez le lien vers la liste des membres depuis une annonce
envoyée à des membres choisis, la liste n'affiche que ces membres avec
l'avis « Seuls les *N* membres sélectionnés sont affichés. » Cliquez sur
**Afficher toute la liste** pour revenir à la liste normale. Vous pouvez
choisir jusqu'à 2 000 membres à la fois.

### Export CSV {#csv-export}

**Export CSV** télécharge un fichier appelé `members.csv`, séparé par
des points-virgules, avec une ligne par membre de la liste actuelle. Les
en-têtes de colonnes sont en allemand, pour que le fichier puisse être
réimporté tel quel :

Vorname, Nachname, Strasse, PLZ, Ort, Geburtsdatum, IBAN, Member seit,
Member bis, E-Mail-Benachrichtigungen, E-Mail-Adressen, Telefonnummern,
Parzellen, Notizen, Tags.

- Les dates sont écrites sous la forme année-mois-jour (2024-03-01).
- L'information e-mail est écrite « Ja » ou « Nein ».
- Plusieurs adresses e-mail, numéros de téléphone, parcelles ou
  étiquettes partagent une cellule, séparés par des points-virgules.
- Les étiquettes sont exportées avec le nom que vous avez saisi, pas
  une traduction.
- Le fait qu'un membre refuse les cadeaux d'anniversaire n'est pas
  exporté.

!!! tip
    L'export correspond toujours à ce qui est à l'écran. Pour exporter
    tous les membres actifs, cliquez d'abord sur **Réinitialiser**. Pour
    exporter les anciens membres, cochez d'abord **Afficher uniquement
    les inactifs**.

## Importer des membres depuis un fichier CSV {#importing-members-from-a-csv-file}

Utilisez l'import pour amener dans Parcella une liste de membres
existante -- issue d'un tableur ou d'un ancien programme. Cela se fait
en deux étapes : vous téléversez le fichier, puis vous indiquez à
Parcella quelle colonne contient quoi. Rien n'est enregistré avant que
vous confirmiez la seconde étape.

Pour un pas-à-pas d'un premier import, voir
[Importer des membres et des parcelles](../guides/csv-import.md).

### Étape 1 : téléverser le fichier {#step-1-upload-the-file}

Cliquez sur **Import CSV** dans la liste des membres. La boîte de
dialogue **Import CSV** s'ouvre.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Champ de fichier | Choisissez un fichier `.csv`. |
| **Importer** | Téléverse le fichier et ouvre l'association des colonnes. Rien n'est encore enregistré. |

La boîte de dialogue liste les colonnes que Parcella comprend. Vous
n'êtes pas obligé d'utiliser ces en-têtes -- vous associez les colonnes
à l'étape suivante. Quelques points à savoir sur le fichier :

- Les colonnes peuvent être séparées par des points-virgules ou des
  virgules. Parcella détecte lequel ; s'il ne peut pas le déterminer, il
  suppose des points-virgules.
- La première ligne doit être la ligne d'en-tête.
- Les dates peuvent s'écrire 2024-03-01, 01.03.2024 ou 01.03.24.
- Plusieurs adresses e-mail ou numéros de téléphone dans une cellule
  sont séparés par des points-virgules.
- Le modèle le plus simple est un **Export CSV** de Parcella lui-même --
  le lien de la boîte de dialogue télécharge l'export complet, non
  filtré.

Si le fichier est vide, vous êtes renvoyé à la liste avec « Ce fichier
CSV semble vide. »

### Étape 2 : associer les colonnes {#step-2-map-the-columns}

<!-- TODO(verify): no screenshot -- this page is only reached by uploading a file, which the screenshot tool can't do. -->

La page **Associer les colonnes CSV** affiche chaque colonne de votre
fichier avec son en-tête et les cinq premières lignes de données en
dessous, pour que vous voyiez ce qu'elle contient. Au-dessus de chaque
colonne se trouve une liste déroulante.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Liste déroulante par colonne | Choisissez le champ Parcella auquel appartient cette colonne : **Prénom**, **Nom**, **Rue**, **Code postal**, **Ville**, **Date de naissance**, **IBAN**, **Membre depuis**, **Membre jusqu'au**, **Notifications par e-mail**, **Adresses e-mail**, **Numéros de téléphone**, **Notes** -- ou **— Ignorer —** pour sauter la colonne. Parcella présélectionne un champ quand il reconnaît l'en-tête (en anglais ou en allemand, par ex. « Nachname » ou « Last name »). |
| **Importer** | Importe les lignes et vous ramène à la liste des membres. **Prénom** et **Nom** doivent chacun être associés à une colonne, sinon vous obtenez « Veuillez associer les colonnes du prénom et du nom avant d'importer. » |
| **Retour** | Revient à la liste des membres sans rien importer. |

### Ce qui se passe à l'import {#what-happens-on-import}

Pour chaque ligne, Parcella cherche un membre existant avec le même
prénom et le même nom. Si vous avez associé une colonne **Date de
naissance** et que la ligne a une date de naissance, elle doit aussi
correspondre.

- **Aucune correspondance** : un nouveau membre est créé, y compris les
  adresses e-mail et numéros de téléphone de la ligne.
- **Une correspondance** : le membre existant est mis à jour, mais
  seulement avec ce que contient réellement la ligne (voir ci-dessous).
  Les adresses e-mail et numéros de téléphone ne sont **pas** touchés
  lors d'une mise à jour -- ajoutez-les ou retirez-les sur la page du
  membre.
- **Plusieurs membres portant ce nom** : Parcella utilise la date de
  naissance, les adresses e-mail et les numéros de téléphone de la ligne
  pour trouver le bon. Le membre qui a l'un d'eux est mis à jour ; la
  casse, les espaces et les tirets n'ont pas d'importance (« 0171
  234-5678 » est identique à « 01712345678 »). Si la ligne correspond
  encore à plusieurs membres, elle est ignorée avec « Ligne 4 : plusieurs
  membres s'appellent Hans Meier, ignorée. » et personne n'est modifié.
  Une adresse e-mail ou un numéro de téléphone seul ne fait jamais
  correspondre un membre portant un autre nom, car les couples en
  partagent souvent un.
- **Prénom ou nom vide** : la ligne est ignorée.

**Une mise à jour ne change que ce que dit le fichier.** Une colonne
réglée sur **— Ignorer —**, ou une cellule vide, laisse la valeur
enregistrée du membre telle quelle. Un fichier ne contenant que des noms
et de nouvelles adresses met donc à jour les adresses et rien d'autre.

La colonne **Notifications par e-mail** compte comme « non » quand elle
indique *nein*, *no*, *false* ou *0*, et comme « oui » pour toute autre
valeur renseignée. Pour un membre existant, une cellule vide ou
l'absence de cette colonne laisse son choix inchangé -- quelqu'un qui
s'est désinscrit le reste. Un nouveau membre sans valeur reçoit « oui ».

Ensuite, la liste des membres affiche un résumé comme « 12 nouvellement
importé(s), 3 mis à jour ». Si des lignes ont été ignorées, le résumé
ajoute le nombre d'erreurs et le détail des trois premières.

!!! tip "Membres portant le même nom"
    Si votre association a des membres aux noms identiques, associez la
    colonne **Date de naissance**, **Adresses e-mail** ou **Numéros de
    téléphone** : chaque ligne met alors à jour la bonne personne. Sans
    aucune d'elles, ces lignes sont ignorées plutôt que devinées.

## Page du membre {#member-page}

![Page du membre](../assets/screenshots/members/detail.png)

Cliquez sur un nom dans la liste des membres pour ouvrir la page du
membre. Elle affiche tout ce que Parcella sait du membre, et vous permet
d'ajouter directement des numéros de téléphone, des adresses e-mail, des
étiquettes et des parcelles.

### Boutons en haut {#buttons-at-the-top_1}

| Bouton | Ce qu'il fait |
|---|---|
| **Modifier** | Ouvre le [formulaire de modification](#new-member-and-edit-member). Nécessite le droit d'écriture. |
| **Précédent** / **Suivant** | Passe au membre précédent ou suivant *dans la liste d'où vous venez*, avec le même filtre. Vous pouvez aussi appuyer sur ++ctrl+left++ et ++ctrl+right++ (pas pendant la saisie dans un champ). Sur un Mac, ces touches peuvent être prises par le système pour changer de bureau. |
| **Retour** | Revient à la liste des membres, avec votre filtre. |

### Données principales {#master-data}

Affiche **Nom**, **Date de naissance**, **Adresse**, **IBAN**, **Membre
depuis**, **Membre jusqu'au**, **Info e-mail** (si le membre peut
recevoir des informations par e-mail) et **Ne souhaite pas de cadeau
d'anniversaire**. Pour modifier l'un d'eux, cliquez sur **Modifier**.

### Étiquettes {#tags}

Liste les étiquettes du membre. Cliquez sur une étiquette pour voir
tous les membres qui l'ont.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **×** à côté d'une étiquette | Retire l'étiquette de ce membre (**Retirer l'étiquette**). L'étiquette elle-même reste pour les autres membres. Nécessite le droit d'écriture. |
| **Ajouter une étiquette, p. ex. responsable de l'eau** | Tapez un nom d'étiquette et cliquez sur **+** (**Ajouter l'étiquette**). Si une étiquette de ce nom existe déjà -- majuscules et espaces superflus n'ont pas d'importance -- elle est réutilisée ; sinon une nouvelle étiquette est créée. Le champ propose les étiquettes existantes pendant la saisie. Nécessite le droit d'écriture. |
| **Gérer les étiquettes** | Ouvre la page [Étiquettes des membres](#member-tags). |

Retirer une étiquette d'un membre ne laisse pas d'entrée dans
l'historique : les étiquettes servent à retrouver des personnes, ce ne
sont pas des archives de l'association.

### Numéros de téléphone et adresses e-mail {#phone-numbers-and-email-addresses}

| Champ / bouton | Ce qu'il fait |
|---|---|
| Champ numéro de téléphone + **+** | Ajoute un autre numéro de téléphone. Nécessite le droit d'écriture. |
| Champ e-mail + **+** | Ajoute une autre adresse e-mail. Elle doit ressembler à une adresse e-mail. Nécessite le droit d'écriture. |
| Bouton corbeille | Supprime ce numéro de téléphone ou cette adresse e-mail (**Retirer**). Nécessite le droit de suppression. |

Cliquez sur une adresse e-mail pour écrire au membre depuis votre propre
logiciel de messagerie.

### Parcelles attribuées {#assigned-parcels}

Liste les parcelles attribuées au membre.

| Colonne | Ce qu'elle affiche |
|---|---|
| **Numéro de parcelle** | Cliquez dessus (ou sur le bouton flèche) pour ouvrir la parcelle. |
| **Superficie** | La superficie de la parcelle en mètres carrés. |
| **Statut** | Le statut de la parcelle : **actif**, **résilié** ou **supprimé**. |
| **Adresse de facturation** | Si l'adresse de ce membre est utilisée pour les factures de la parcelle. |
| **Depuis** | Le début du bail. |

<!-- TODO(verify): this table lists every assignment of the member, including ended tenancies, and has no "until" column -- confirm whether former parcels are meant to appear here. Also, a communal parcel would show as "deleted" here because the badge only knows active/terminated. -->

Pour attribuer une parcelle au membre (nécessite le droit d'écriture) :

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Choisir une parcelle…** | La parcelle à attribuer. Toutes les parcelles sont proposées, triées par numéro. |
| **Utiliser comme adresse de facturation** | Coché par défaut. Les factures de cette parcelle vont à l'adresse de ce membre. |
| **Attribuer** | Attribue la parcelle et ouvre la page de la parcelle. |

Le bail commence sans date. Pour définir une date de début, ou pour
terminer un bail, utilisez la page de la parcelle -- voir
[Locataires actuels](parcels.md#current-tenants).

### Procédures {#processes}

Si le module [Procédures](processes.md) est activé et que vous pouvez
voir les procédures, une carte **Procédures** liste les procédures
concernant ce membre. **Démarrer une procédure** en démarre une nouvelle
pour lui.

### Notes {#notes}

Les notes internes du membre, s'il y en a. Modifiez-les dans le
formulaire du membre.

### Zone de danger {#danger-zone}

Affichée seulement aux utilisateurs ayant le droit de suppression.

**Supprimer le membre** marque le membre comme supprimé après
confirmation. Le membre disparaît de toutes les listes et recherches.
Ses données restent dans la base de données, et les attributions de
parcelles, sessions de travail et autres enregistrements existants
restent tels quels.

!!! warning "Terminer une adhésion n'est pas supprimer"
    Pour un membre qui quitte l'association -- ou qui est décédé --
    renseignez plutôt **Membre jusqu'au** dans le formulaire de
    modification, et terminez ses baux sur la page de la parcelle. Il
    passe alors dans **Afficher uniquement les inactifs** et son
    historique reste visible. La suppression est destinée aux
    enregistrements qui n'auraient jamais dû exister, comme un doublon.
    <!-- TODO(verify): there's no way to restore a deleted member in the app; confirm. Also confirm how a deleted member who is still assigned to a parcel shows up on the parcel page. -->

## Nouveau membre et modifier un membre {#new-member-and-edit-member}

![Formulaire de nouveau membre](../assets/screenshots/members/form-new.png)

Cliquez sur **Nouveau membre** dans la liste des membres, ou sur
**Modifier** sur la page d'un membre. Les deux formulaires se
ressemblent ; le formulaire de nouveau membre demande en plus une
première adresse e-mail et un premier numéro de téléphone. Les champs
marqués d'une étoile rouge sont obligatoires.

### Données personnelles {#personal-data}

| Champ | Ce qu'il fait |
|---|---|
| **Prénom** \* | Obligatoire. |
| **Nom** \* | Obligatoire. |
| **Date de naissance** | Utilisée pour la liste des anniversaires et l'âge moyen sur le tableau de bord. Aide aussi l'import CSV à distinguer des membres portant le même nom. |
| **IBAN** | Le compte bancaire du membre, par ex. pour les prélèvements. |

### Adresse {#address}

| Champ | Ce qu'il fait |
|---|---|
| **Rue et numéro** | |
| **Code postal** | Jusqu'à 10 caractères. |
| **Ville** | |

L'adresse sert pour les courriers et les factures. Si le membre est
l'adresse de facturation d'une parcelle, les factures de cette parcelle
partent à cette adresse.

### Adhésion {#membership}

| Champ | Ce qu'il fait |
|---|---|
| **Membre depuis** | Le premier jour de l'adhésion. S'il est vide, le membre est listé comme *en attente* mais compte quand même comme actif. S'il est dans le futur, le membre compte comme inactif jusqu'à ce jour. |
| **Membre jusqu'au** | Le dernier jour de l'adhésion. « Laisser vide = membre actif ». À partir du lendemain, le membre compte comme inactif. |
| **Adresse e-mail** | Nouveaux membres seulement. Facultative -- d'autres adresses peuvent être ajoutées plus tard sur la page du membre. |
| **Numéro de téléphone** | Nouveaux membres seulement. Facultatif -- d'autres numéros peuvent être ajoutés plus tard sur la page du membre. |
| **Peut recevoir des informations par e-mail** | Coché par défaut pour les nouveaux membres. Décochez-le si le membre ne veut pas recevoir les informations de l'association par e-mail. La liste des membres peut filtrer dessus. |
| **Ne souhaite pas de cadeau d'anniversaire** | Cochez-le si le membre ne veut pas de cadeaux d'anniversaire. C'est affiché sur la liste des anniversaires, pour que la personne qui s'occupe des cadeaux le sache. |

### Notes {#notes_1}

| Champ | Ce qu'il fait |
|---|---|
| **Notes internes…** | Texte libre pour le bureau. Les notes sont incluses dans la recherche de la liste des membres. |

### Étiquettes {#tags_1}

| Champ | Ce qu'il fait |
|---|---|
| Cases d'étiquettes | Une case par étiquette existante. Cochez ou décochez pour l'ajouter ou la retirer. Affiché seulement une fois que des étiquettes existent. |
| **Nouvelles étiquettes, séparées par des virgules** | Tapez de nouvelles étiquettes, séparées par des virgules, par ex. « responsable de l'eau, équipe haies ». Un nom qui existe déjà est réutilisé. |

### Enregistrer {#saving}

| Bouton | Ce qu'il fait |
|---|---|
| **Créer un membre** / **Enregistrer les modifications** | Enregistre le membre et ouvre la page du membre. |
| **Annuler** | Quitte sans enregistrer. |

Si un nouveau nom d'étiquette n'est pas accepté (par exemple, il dépasse
100 caractères), le reste du membre est quand même enregistré et le
formulaire de modification se rouvre pour que vous puissiez corriger
l'étiquette.
<!-- TODO(verify): in that case the form reopens without an error message. -->

## Étiquettes des membres {#member-tags}

![Étiquettes des membres](../assets/screenshots/members/tags.png)

Les étiquettes sont des libellés libres pour retrouver des membres --
« responsable de l'eau », « bureau élargi », « équipe haies ».
Ajoutez-les sur la page d'un membre ou dans le formulaire du membre ;
renommez-les ou supprimez-les ici. Ouvrez la page avec **Gérer les
étiquettes** dans la liste des membres ou sur la page d'un membre.

Chaque étiquette a une ligne :

| Champ / bouton | Ce qu'il fait |
|---|---|
| Nom de l'étiquette + bouton de coche | Changez le nom et cliquez sur le bouton de coche (**Renommer**). Le nouveau nom s'affiche pour chaque membre qui a l'étiquette. Refusé si une autre étiquette porte déjà ce nom. Nécessite le droit d'écriture ; sans lui, vous ne voyez que le nom. |
| ***N* membre(s)** | Ouvre la liste des membres filtrée sur cette étiquette. |
| Bouton corbeille | **Supprimer l'étiquette** après confirmation. L'étiquette est retirée de chaque membre. Nécessite le droit de suppression. |
| Bouton de traduction | Ouvre les **Traductions** de l'étiquette : un nom par langue prise en charge par Parcella. Tant que l'association fonctionne dans une langue, les listes, formulaires et filtres affichent le nom de l'étiquette dans cette langue ; un champ vide affiche le nom que vous avez saisi. Cliquez sur **Enregistrer les traductions** pour les enregistrer. Nécessite le droit d'écriture ; sans lui, vous voyez les traductions sous forme de liste. Le petit chiffre sur le bouton indique combien de traductions existent. |
| **Retour aux membres** | Revient à la liste des membres. |

L'export CSV utilise toujours le nom que vous avez saisi, pas une
traduction.

## Feuille de présence de l'assemblée {#meeting-sign-in-sheet}

![Feuille de présence de l'assemblée](../assets/screenshots/members/signin-sheet.png)

Ouvrez-la avec **Feuille de présence** dans la liste des membres. Elle
produit une liste PDF à imprimer et à apporter à une assemblée
générale : chaque locataire actuel, regroupé par parcelle, avec une
ligne de signature pour chacun.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Titre** | Affiché en haut du PDF. Il commence par « Assemblée générale du » suivi de la date du jour ; modifiez-le comme vous voulez. Si vous le videz, le titre par défaut est utilisé. |
| **Générer le PDF** | Télécharge la feuille de présence sous forme de fichier PDF. |
| **Annuler** | Revient à la liste des membres. |

Ce que contient la feuille :

- Une ligne par personne, avec les colonnes **Parcelle**, **Nom** et
  **Signature**, triée par numéro de parcelle puis par nom.
- Si plusieurs personnes occupent une parcelle, le numéro de parcelle
  apparaît une fois et chacune a sa propre ligne de signature.
- Seuls les **membres actifs** qui sont **locataires actuels** d'une
  parcelle sont listés. Les membres sans parcelle, et les locataires
  déjà partis, ne figurent pas sur la feuille.
- Le PDF porte le logo de l'association et les mêmes en-tête et pied de
  page que les autres documents de l'association. Une longue liste
  s'étend simplement sur plusieurs pages.

!!! tip
    Les membres sans parcelle -- les membres d'honneur, par exemple --
    ne figurent pas sur la feuille. Ajoutez-les à la main s'ils peuvent
    assister à l'assemblée.

## Voir aussi {#related}

- [Parcelles](parcels.md) -- attribuer et terminer des baux
- [Candidats](applicants.md) -- faire d'un candidat un membre
- [Accueillir un nouveau membre](../guides/new-member.md)
- [Transmettre une parcelle](../guides/parcel-handover.md)
- [Importer des membres et des parcelles](../guides/csv-import.md)
- [Annonces](announcements.md) -- écrire aux membres filtrés ou choisis

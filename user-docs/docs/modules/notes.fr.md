# Notes {#notes}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Procès-verbaux d'assemblées générales, de réunions du bureau, de
rencontres avec des personnes extérieures, et tout ce qui mérite d'être
noté. Les notes s'écrivent en Markdown, sont classées sous une catégorie
et des étiquettes, et peuvent être recherchées, filtrées et triées. Si
votre association utilise un stockage cloud, chaque note peut y vivre
sous forme de fichier `.md` que vous pouvez aussi ouvrir et modifier
dans le cloud.

!!! info "Qui peut l'utiliser"
    - L'interrupteur du module est **Notes** sous **Administration →
      Activer et désactiver les modules**. Il est **activé** par défaut.
    - Les rôles **Conseil d'administration** et **Administrateur**, et
      les membres d'un groupe avec **Accès complet à chaque module**,
      peuvent tout faire.
    - Tous les autres ont besoin du droit **Notes** dans l'un de leurs
      [groupes](../administration/groups.md) :
        - *lecture* : voir la liste et les notes, les télécharger, lancer
          **Synchroniser** ;
        - *écriture* : créer et modifier des notes, importer des favoris,
          ajouter, renommer et traduire des catégories et des étiquettes ;
        - *suppression* : supprimer des notes, catégories et étiquettes.
    - Stocker les notes dans le cloud nécessite aussi le module
      **Stockage cloud** et un dossier des notes, voir
      [Les notes dans le cloud](#notes-in-the-cloud).

## Liste des notes {#note-list}

![Liste des notes](../assets/screenshots/notes/list.png)

Ouvrez **Notes** dans le menu.

### Boutons en haut {#buttons-at-the-top}

| Bouton | Ce qu'il fait |
|---|---|
| **Synchroniser** | Affiché seulement quand un dossier des notes est configuré. Lit immédiatement les changements du dossier cloud (voir [Les notes dans le cloud](#notes-in-the-cloud)). |
| **Catégories et étiquettes** | Ouvre [Catégories et étiquettes](#categories-tags). |
| **Importer des favoris** | Ouvre [Importer des favoris](#import-bookmarks). Nécessite l'*écriture*. |
| **Nouvelle note** | Ouvre un [formulaire de note](#writing-a-note) vide. Nécessite l'*écriture*. |

### Recherche et filtres {#search-and-filters}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Rechercher** | Cherche dans le titre, le texte et les noms d'étiquettes. Majuscules/minuscules indifférentes. |
| **Catégorie** | **Toutes**, **Sans catégorie**, ou une catégorie. |
| **Étiquettes** | **Toutes** ou une étiquette. |
| **Du** / **Au** | Seulement les notes dont la date tombe dans cette plage. |
| **Trier par** | **Date, plus récentes d'abord** (par défaut), **Date, plus anciennes d'abord**, **Titre**, **Dernière modification**. |
| **Appliquer** | Applique la recherche, les filtres et le tri. |
| **Réinitialiser** | Affiché dès que quelque chose est réglé. Revient à toutes les notes, les plus récentes d'abord. |

### Colonnes {#columns}

| Colonne | Ce qu'elle affiche |
|---|---|
| **Date** | Le jour dont parle la note (pour un procès-verbal : le jour de la réunion). |
| **Titre** | Avec un lien vers la note. Une icône de flèche ouvre le lien source de la note dans un nouvel onglet (favoris). Une icône de nuage orange signifie **Pas encore enregistrée dans le cloud**. |
| **Catégorie** | Cliquez pour filtrer la liste dessus. |
| **Étiquettes** | Cliquez sur l'une pour filtrer la liste dessus. |
| **Modifiée** | Quand la note a été enregistrée pour la dernière fois (masqué sur les petits écrans). |

Quand la liste est vide, elle indique **Aucune note pour l'instant.**, ou
**Aucune note ne correspond à ces filtres.** quand un filtre est actif.

## Lire une note {#reading-a-note}

![Une note](../assets/screenshots/notes/detail.png)

Cliquez sur le titre d'une note. Vous voyez le titre, la date, la
catégorie et les étiquettes (chacune cliquable pour filtrer la liste),
la **Source (lien)** s'il s'agit d'un favori, et le texte mis en forme.
Le pied indique qui a créé et qui a modifié en dernier la note, et, avec
un dossier cloud, le chemin du fichier de la note.

| Bouton | Ce qu'il fait |
|---|---|
| **Toutes les notes** | Retour à la liste. |
| **Télécharger .md** | Télécharge la note sous forme de fichier Markdown, avec titre, date, catégorie et étiquettes dans un en-tête. |
| **Télécharger le PDF** | Télécharge la note en PDF avec l'en-tête de votre association. Les images seulement liées depuis le web sont omises. |
| **Modifier** | Ouvre le formulaire. Nécessite l'*écriture*. |
| **Supprimer la note** | Nécessite la *suppression*. Demande **Supprimer cette note ? Son fichier dans le cloud sera également supprimé.** |

Ouvrir une note relit d'abord son fichier dans le cloud, vous voyez donc
toujours le texte actuel. En cas d'échec, la page affiche
**Impossible de lire le fichier du cloud, affichage de la dernière
version synchronisée : ...** avec la raison.

## Écrire une note {#writing-a-note}

![Formulaire de note](../assets/screenshots/notes/form.png)

**Nouvelle note** ou **Modifier** ouvre le formulaire (**Nouvelle note**
/ **Modifier la note**).

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Titre** | Obligatoire, jusqu'à 255 caractères. |
| **Date** | Obligatoire. Le jour dont parle la note, pas le jour où vous l'écrivez. |
| **Catégorie** | **Sans catégorie** ou l'une des catégories de l'association. |
| **Étiquettes** | Cochez des étiquettes existantes. |
| **Nouvelles étiquettes, séparées par des virgules** | Tapez de nouvelles étiquettes, séparées par des virgules. Elles sont créées à l'enregistrement et ajoutées à la liste d'étiquettes de l'association. |
| **Source (lien)** | Facultatif : la page web dont parle cette note. Une note avec une source est un favori. Doit commencer par `http://` ou `https://`. |
| **Note** | Le texte, en Markdown. Avec un dossier cloud, la zone indique où le fichier est enregistré. |
| **Enregistrer** | Enregistre la note. |
| **Annuler** | Retour sans enregistrer. |

L'éditeur a une barre d'outils pour gras, italique, barré, titre,
citation, listes, code, lien, tableau et ligne horizontale. L'icône œil
affiche un aperçu, l'icône de partage affiche texte et aperçu côte à
côte, les flèches passent en plein écran, et le point d'interrogation
ouvre un guide Markdown.

Messages possibles : **Veuillez saisir un titre.**, **Veuillez saisir
une date.**, **La source doit être une adresse web commençant par
http:// ou https://.**, **Cette catégorie n'existe pas (ou plus).**,
**Cette étiquette n'existe pas (ou plus).**

## Les notes dans le cloud {#notes-in-the-cloud}

Quand le module **Stockage cloud** est activé et qu'un administrateur a
défini un **Dossier des notes** sous **Administration → Intégrations →
Stockage cloud (documents des parcelles, factures, sauvegardes)**, le
texte de chaque note est un fichier Markdown dans ce dossier.

!!! note "Le fichier est la version de référence du texte"
    Le texte du fichier cloud l'emporte. Vous et d'autres pouvez ouvrir
    et modifier ces fichiers avec n'importe quel éditeur dans le cloud
    (Nextcloud Text, Obsidian, etc.) ; les changements apparaissent dans
    Parcella. Le titre, la date, la catégorie, les étiquettes et la
    source n'existent que dans Parcella et ne sont pas écrits dans le
    fichier.

Concrètement :

- **L'enregistrement** écrit d'abord le fichier. Si le fichier ne peut
  pas être écrit, la note n'est pas enregistrée et vous voyez **Non
  enregistrée, le fichier du cloud n'a pas pu être écrit : ...** avec
  votre texte toujours dans le formulaire. Ne changer que le titre, la
  date, les étiquettes ou la source ne touche pas du tout au fichier.
- **Les sous-dossiers sont des catégories.** Une note dans le dossier
  « Réunion du bureau/ » reçoit la catégorie « Réunion du bureau »
  (créée si nécessaire). Enregistrer une note avec une autre catégorie
  déplace son fichier dans le dossier de cette catégorie. Les notes sans
  catégorie sont directement dans le dossier des notes.
- **Les nouveaux fichiers** sont nommés d'après la date et le titre, par
  ex. `20261108-reunion-du-bureau.md`. Parcella ne renomme jamais un
  fichier ensuite.
- **Les fichiers créés dans le cloud** deviennent des notes. Leur date
  est tirée du début du nom de fichier (`2026-11-08`, `20261108`, ou
  `202506` pour le 1er de ce mois), sinon de la date de dernière
  modification du fichier.
- **Synchroniser** : la liste des notes lit d'elle-même les changements
  du cloud, au plus une fois par minute. **Synchroniser** le fait
  immédiatement et indique **Synchronisé : {n} nouvelles, {n} modifiées,
  {n} supprimées, {n} envoyées.** Un fichier supprimé dans le cloud
  retire sa note de la liste.
- **Supprimer** une note dans Parcella supprime aussi son fichier. En
  cas d'échec, la note n'est pas supprimée : **Non supprimée, le fichier
  du cloud n'a pas pu être supprimé : ...**
- **Pas encore de dossier ?** Les notes ne sont conservées que dans
  Parcella et marquées **Pas encore enregistrée dans le cloud**. Elles
  sont téléversées à la première synchronisation après la définition
  d'un dossier.

### Quand quelqu'un a modifié le fichier en même temps {#when-someone-changed-the-file-at-the-same-time}

Si le fichier a été modifié dans le cloud pendant que vous éditiez,
l'enregistrement s'arrête avec **Non enregistrée : la note a été
modifiée entre-temps dans le cloud.** Une carte jaune **Modifiée
entre-temps dans le cloud** affiche la version du cloud (avec
**Afficher en Markdown** pour le texte brut), et votre propre texte
reste dans le formulaire en dessous. Recopiez ce dont vous avez besoin
et cliquez à nouveau sur **Enregistrer** pour écraser la version du
cloud.

Si une note a été modifiée à la fois dans Parcella (alors qu'aucun
dossier n'était défini) et dans le cloud, la synchronisation conserve la
version du cloud et enregistre la vôtre comme une note séparée marquée
« conflict copy ». La liste indique alors combien de copies ont été
créées. Rien n'est perdu.

## Catégories et étiquettes {#categories-tags}

![Catégories et étiquettes](../assets/screenshots/notes/taxonomy.png)

**Catégories et étiquettes** affiche les catégories et étiquettes de
l'association. Chaque note a une catégorie et un nombre quelconque
d'étiquettes. Les mêmes catégories et étiquettes sont prévues pour être
utilisées aussi par la future base de connaissances. Les nouvelles
installations démarrent avec quatre catégories : « Assemblée générale »,
« Réunion du bureau », « Réunion avec des externes » et « Autre ».
**Notes** (en haut à droite) vous ramène.

La page a deux cartes, **Catégories** et **Étiquettes**, qui
fonctionnent de la même façon :

| Champ / bouton | Ce qu'il fait |
|---|---|
| Nom + bouton de coche | Renomme la catégorie ou l'étiquette. Nécessite l'*écriture* ; sinon le nom est simplement affiché. Renommer une catégorie déplace les fichiers de ses notes dans un dossier portant le nouveau nom à la prochaine synchronisation ; l'ancien dossier vide reste. |
| « {count} note(s) » | Ouvre la liste des notes filtrée dessus. |
| Bouton de traduction | Ouvre les noms par langue. Avec l'*écriture*, vous pouvez saisir un nom pour chaque langue prise en charge par Parcella et cliquer sur **Enregistrer les traductions** ; les champs vides affichent le nom principal. |
| Bouton corbeille | Supprime la catégorie ou l'étiquette après **Supprimer « {name} » ? Les notes sont conservées, sans cette entrée.** Nécessite la *suppression*. |
| **Nouvelle catégorie** / **Nouvelle étiquette** + **Ajouter** | En ajoute une. Nécessite l'*écriture*. |

## Importer des favoris {#import-bookmarks}

![Importer des favoris](../assets/screenshots/notes/import-bookmarks.png)

Si votre association rassemble des liens utiles (fournisseurs,
administrations, guides) dans Nextcloud Bookmarks ou un navigateur, vous
pouvez les transformer en notes d'un coup. Chaque favori devient une
note avec le lien comme source.

1. Exportez vos favoris sous forme de fichier HTML. Nextcloud Bookmarks
   et tous les navigateurs savent le créer.
2. Cliquez sur **Importer des favoris**, choisissez le fichier et
   cliquez sur **Afficher l'aperçu**. Rien n'est encore enregistré.
3. L'aperçu indique combien sont « nouveaux », « déjà une note » (une
   note avec le même lien existe -- ignoré) et « pas un lien web »
   (ignoré). Le tableau liste **Date**, **Titre** (avec lien et
   description), **Étiquettes** et **Statut** pour chaque favori.
4. Cliquez sur **Importer {count} favori(s)**, ou sur **Choisir un autre
   fichier**.

Les nouvelles notes n'ont pas de catégorie ; avec un dossier cloud, elles
sont enregistrées à la racine du dossier des notes. Les dossiers du
favori deviennent des étiquettes, la description devient le texte, et la
date d'ajout du favori devient la date de la note. Parcella n'ouvre
jamais les pages liées.

Si le fichier ne contient aucun favori : **Aucun favori trouvé dans ce
fichier.**

## Les notes et les assistants IA {#notes-and-ai-assistants}

Un administrateur peut activer le module **Connecteur MCP pour clients
IA**. Un assistant IA comme Claude peut alors rechercher, lire et écrire
des notes -- mais uniquement celles qui portent l'étiquette de libération
(par défaut `ki-freigegeben`). Toutes les autres notes lui restent
invisibles. Les notes écrites par l'IA reçoivent une étiquette (par
défaut `ki-erstellt`) pour que vous sachiez quoi relire. C'est désactivé
par défaut, car cela transmet des notes de l'association à un service
externe.

<!-- TODO(verify): where the release and created tag names are configured in the UI (stored as club settings); and link to the API tokens page section on "MCP connector only" tokens. -->

## Voir aussi {#related}

- [Intégrations](../administration/integrations.md) -- le stockage cloud
  et le dossier des notes.
- [Jetons API](../administration/api-tokens.md)
- [Groupes](../administration/groups.md) -- donner à quelqu'un des
  droits sur les notes.
- [Activer et désactiver les modules](../administration/modules.md)

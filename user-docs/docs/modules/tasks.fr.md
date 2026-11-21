# Tableau des tâches {#task-board}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Un tableau de tâches commun pour les affaires du bureau qui ne sont pas
liées à une session de travail : « renouveler le contrat d'assurance »,
« appeler l'électricien », « relancer le couvreur ». Les tâches sont des
cartes dans des colonnes que vous faites glisser de gauche à droite à
mesure que le travail avance.

!!! info "Qui peut l'utiliser"
    - L'interrupteur du module est **Tableau des tâches** sous
      **Administration → Activer et désactiver les modules**. Il est
      **activé** par défaut.
    - Seuls les rôles **Conseil d'administration** et **Administrateur**,
      et les membres d'un groupe avec **Accès complet à chaque module**,
      voient **Tableau des tâches** dans le menu. Il n'existe pas de
      droit de groupe pour l'ouvrir à d'autres utilisateurs, ni en
      lecture ni en écriture.
    - En option, des cartes peuvent être importées depuis un tableau
      Nextcloud Deck (interrupteur **Synchronisation Nextcloud Deck**,
      désactivé par défaut). Voir
      [Cartes de Nextcloud Deck](#cards-from-nextcloud-deck).

!!! note "À ne pas confondre avec les tâches des sessions de travail"
    Les travaux que les membres effectuent pendant une session de travail
    (« tailler la haie ») se trouvent dans le module
    [heures de travail](work-hours.md) sous **Tâches**. Le tableau des
    tâches sert à la liste de choses à faire du bureau lui-même.

## Le tableau {#the-board}

![Tableau des tâches](../assets/screenshots/tasks/board.png)

Le tableau affiche toutes les listes (colonnes) côte à côte ; faites
défiler latéralement s'il y en a plus que l'écran n'en contient. Les
nouvelles installations démarrent avec trois listes, « À faire »,
« En cours » et « Terminé ». Vous pouvez renommer, ajouter, réordonner
et supprimer des listes à votre guise.

L'entrée de menu **Tableau des tâches** affiche un chiffre rouge quand
des tâches sont en retard. Le tableau de bord a une carte **Tâches en
retard** avec le même chiffre ; son bouton **Afficher tout** ouvre le
tableau avec **En retard uniquement** déjà coché.

### Boutons en haut {#buttons-at-the-top}

| Bouton | Ce qu'il fait |
|---|---|
| **Ajouter une liste** | Ouvre une petite fenêtre pour ajouter une liste. Saisissez un **Nom** (jusqu'à 100 caractères) et cliquez sur **Ajouter**. La nouvelle liste se place à l'extrémité droite du tableau. |
| **Gérer les étiquettes** | Ouvre [Étiquettes des tâches](#task-tags). |
| **Exporter le rapport** | Ouvre [Exporter le rapport d'activité](#export-activity-report). |
| **Nouvelle tâche** | Ouvre la [fenêtre de tâche](#the-task-window) pour une nouvelle carte. |

### Une liste (colonne) {#a-list-column}

L'en-tête de chaque colonne affiche le nom de la liste, une icône de
coche verte s'il s'agit d'une [liste « terminé »](#done-lists), et le
nombre de cartes qu'elle contient.

| Action | Ce qu'elle fait |
|---|---|
| Faire glisser l'en-tête | Déplace toute la liste à une nouvelle position sur le tableau. |
| **⋮** → **Renommer** | Ouvre **Renommer la liste** ; changez le **Nom** et cliquez sur **Enregistrer les modifications**. |
| **⋮** → **Marquer comme liste « terminé »** / **Retirer le marquage « terminé »** | Active ou désactive la fonction de liste « terminé » pour cette liste. Voir [Listes « terminé »](#done-lists). |
| **⋮** → **Supprimer** | Ouvre **Supprimer la liste**. Impossible pour la dernière liste restante. |

Quand vous supprimez une liste qui contient encore des cartes, la
fenêtre indique **Cette liste contient encore des cartes. Choisissez une
autre liste vers laquelle les déplacer avant de la supprimer.** Choisissez
la cible dans **Déplacer ses cartes vers** et cliquez sur **Supprimer la
liste**. Les cartes sont ajoutées à la fin de cette liste, dans leur
ordre actuel -- aucune carte n'est jamais supprimée avec une liste. Une
liste vide demande **Supprimer la liste « {name} » ? Cette action est
irréversible.**

### Une carte {#a-card}

Chaque carte affiche :

- le badge de **priorité** (**Haute**, **Moyenne** ou **Basse**), s'il
  y en a une ;
- une icône de nuage si la carte vient de Nextcloud Deck ;
- le **titre** -- cliquez dessus pour ouvrir la
  [fenêtre de tâche](#the-task-window) ;
- à qui elle est attribuée, et l'**échéance**. Une échéance dépassée
  s'affiche en rouge ;
- **Terminé le {date}** en vert pour les cartes finies, qui sont aussi
  affichées estompées et barrées ;
- ses **étiquettes** sous forme de libellés colorés.

Une liste vide affiche **Aucune tâche**.

**Faites glisser une carte** vers une autre liste, ou vers le haut et le
bas dans une liste, pour changer sa place. L'ordre est enregistré
immédiatement. Si l'enregistrement échoue, la page se recharge pour
montrer l'état réel.

!!! note "Quand le glisser-déposer est désactivé"
    Tant qu'une recherche, un filtre ou un tri autre que **Manuel (ordre
    de glisser-déposer)** est actif, les cartes ne peuvent pas être
    déplacées, car le tableau n'affiche alors pas chaque carte dans son
    ordre réel. Cliquez sur **Réinitialiser les filtres** et remettez le
    tri sur **Manuel (ordre de glisser-déposer)**. Déplacer des listes
    entières fonctionne toujours.

### Recherche, filtres et tri {#search-filters-and-sort}

La barre au-dessus du tableau restreint ce que vous voyez. Tout se passe
instantanément dans votre navigateur et ne change rien au tableau
lui-même.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Champ de recherche | Cherche dans le titre, la description, les étiquettes et les commentaires. |
| **Toutes priorités** | N'affiche que les cartes de priorité **Haute**, **Moyenne** ou **Basse**. |
| **Tous les tags** | N'affiche que les cartes avec cette étiquette. Seules les étiquettes utilisées sur le tableau sont proposées. |
| **Tous les responsables** | N'affiche que les cartes attribuées à cette personne. Seules les personnes ayant des cartes sont proposées. |
| **Tous les mois d'échéance** | N'affiche que les cartes dont l'échéance tombe ce mois-là (par ex. « juillet 2026 »). Seuls les mois présents sont proposés. |
| **En retard uniquement** | N'affiche que les cartes en retard : une échéance passée et non terminée. |
| **Réinitialiser les filtres** | Réinitialise la recherche et les filtres. |
| Tri (**Manuel (ordre de glisser-déposer)**, **Échéance**, **Priorité**) | Réordonne les cartes dans chaque liste pour l'affichage : par mois d'échéance, ou Haute → Moyenne → Basse avec les cartes sans priorité en dernier. **Manuel (ordre de glisser-déposer)** réaffiche votre propre ordre. Le tri n'est jamais enregistré. |

Si rien ne correspond : **Aucune tâche ne correspond à votre
recherche/vos filtres.**

## La fenêtre de tâche {#the-task-window}

![Fenêtre de tâche](../assets/screenshots/tasks/task-modal.png)

Cliquer sur **Nouvelle tâche** ou sur le titre d'une carte ouvre une
fenêtre au-dessus du tableau, intitulée **Nouvelle tâche** ou **Modifier
la tâche**. Chaque carte a sa propre adresse web, vous pouvez donc la
mettre en favori ou envoyer le lien à un autre membre du bureau. Fermer
la fenêtre (X, **Annuler**, Échap ou un clic à côté) vous ramène au
tableau sans enregistrer.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Titre** | Obligatoire. |
| **Description** | Texte libre facultatif. |
| **Échéance** | Facultatif. Une carte dont l'échéance est dépassée compte comme en retard jusqu'à ce qu'elle soit terminée. |
| **Priorité** | **Aucune priorité** (par défaut), **Basse**, **Moyenne** ou **Haute**. La priorité ne change pas l'ordre des cartes ; elle affiche seulement un badge et permet de filtrer et trier. |
| **Étiquettes** | Cochez n'importe quelles [étiquettes de tâches](#task-tags) de l'association. S'il n'en existe encore aucune : **Aucune étiquette définie pour l'instant.** avec un lien vers **Gérer les étiquettes**. Vous ne pouvez pas taper de nouvelles étiquettes ici. |
| **Liste** | La liste dans laquelle se trouve la carte. Une nouvelle carte va dans la première liste sauf si vous en choisissez une autre ; elle est ajoutée à la fin. |
| **Terminé** | Marque la carte comme terminée (avec la date et l'heure). Les tâches terminées ne sont jamais affichées en retard. Déplacer une carte dans une liste « terminé » la marque automatiquement comme terminée. Décochez pour la rouvrir. |
| **Attribuée à** | Cochez un nombre quelconque de personnes. Seuls les comptes utilisateurs actifs sont listés. |
| **Créer** / **Enregistrer les modifications** | Enregistre la carte et revient au tableau. |
| **Supprimer la tâche** | Seulement sur les cartes existantes. Supprime la carte avec ses commentaires après **Supprimer cette tâche ? Cette action est irréversible.** |

### Commentaires {#comments}

Les cartes existantes ont une section **Commentaires** : un journal de
notes pour la personne qui reprendra la tâche. Chaque commentaire affiche
son auteur et l'heure.

- Tapez dans **Nouveau commentaire** et cliquez sur **Ajouter un
  commentaire**.
- Chaque commentaire a sous lui un petit lien rouge **Supprimer le
  commentaire**, qui retire ce commentaire après **Supprimer ce
  commentaire ? Cette action est irréversible.** Tout membre du bureau
  peut supprimer n'importe quel commentaire. Les commentaires ne peuvent
  pas être modifiés.


### Historique des modifications {#change-history}

Sous les commentaires, **Historique des modifications** liste chaque
modification enregistrée, la plus récente en premier : **Horodatage**,
**Champ**, **Ancienne valeur**, **Nouvelle valeur** et **Modifié par**.
Sont enregistrés les changements de titre, de description, d'échéance,
de priorité, d'étiquettes, de liste (affichée par son nom) et de la
marque « terminé ». Les changements d'attribution ne sont pas
enregistrés. S'il n'y en a encore aucun : **Aucune modification
enregistrée pour le moment.**

## Listes « terminé » {#done-lists}

Une carte n'est « terminée » que lorsqu'elle est marquée comme telle --
jamais simplement parce qu'elle se trouve dans une colonne appelée
« Terminé ». Pour que déplacer une carte dans une colonne la marque
comme terminée, marquez cette colonne comme liste « terminé » :

1. Ouvrez le menu **⋮** de la liste que vous utilisez pour les tâches
   finies.
2. Choisissez **Marquer comme liste « terminé »**. Une coche verte
   apparaît à côté de son nom.

À partir de là :

- déplacer une carte **dans** une liste « terminé » la marque comme
  terminée (glisser-déposer, changer la **Liste** dans la fenêtre de
  tâche, ou la créer là) ;
- la déplacer **hors** de celle-ci vers une liste normale la rouvre ;
- déplacer entre deux listes normales ne change rien ;
- la case **Terminé** marque ou rouvre une carte dans n'importe quelle
  liste.

Marquer une liste marque comme terminées les cartes qui s'y trouvent
déjà. Retirer le marquage d'une liste laisse ses cartes telles quelles.

Tant qu'aucune liste n'est marquée, le tableau affiche un avis bleu qui
l'explique.

## Étiquettes des tâches {#task-tags}

![Étiquettes des tâches](../assets/screenshots/tasks/tags.png)

**Gérer les étiquettes** sur le tableau ouvre **Étiquettes des tâches** :
la liste fixe des étiquettes que peuvent porter les cartes. Les cartes ne
peuvent porter que les étiquettes définies ici. **Retour au tableau**
revient au tableau.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nom** + couleur + **Ajouter une étiquette** | Crée une étiquette. Le nom est obligatoire, jusqu'à 100 caractères, et doit être unique (majuscules/minuscules indifférentes). Couleurs : **Gris** (par défaut), **Rouge**, **Orange**, **Jaune**, **Vert**, **Turquoise**, **Bleu**, **Violet**. |
| Nom et couleur d'une étiquette existante + bouton de coche | Renomme ou recolore l'étiquette. Le changement apparaît immédiatement sur chaque carte. |
| « {count} tâche(s) » | Combien de cartes portent l'étiquette. |
| Bouton corbeille | Supprime l'étiquette après **Supprimer l'étiquette « {name} » ? Elle sera retirée de toutes les tâches.** Les cartes restent. |

Erreurs possibles : **Une étiquette doit avoir un nom.**, **Une
étiquette portant ce nom existe déjà.**, **Couleur inconnue.** Sans
étiquette pour l'instant : **Aucune étiquette pour l'instant.**

## Exporter le rapport d'activité {#export-activity-report}

![Exporter le rapport d'activité](../assets/screenshots/tasks/export.png)

**Exporter le rapport** télécharge un fichier texte Markdown sur
l'activité du tableau, par exemple pour rédiger le procès-verbal du
bureau ou un résumé mensuel (éventuellement avec l'aide d'un assistant
IA).

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Du** | Début de la période. Par défaut il y a 30 jours. |
| **Au** | Fin de la période. Par défaut aujourd'hui. |
| **Télécharger** | Télécharge le rapport. |

Le rapport a trois parties : les cartes créées ou modifiées pendant la
période, les commentaires écrits pendant la période, et un instantané de
chaque carte du tableau à l'heure actuelle (les cartes terminées avec
leur date de fin).

!!! warning "Ce que signifie « modifiée pendant la période »"
    Une carte compte comme touchée si elle a été créée ou modifiée
    pendant la période. Le rapport ne peut pas dire exactement quand une
    carte a été déplacée dans sa liste actuelle. Le fichier l'indique
    lui-même, pour que la personne qui le lit n'invente pas de
    chronologie.

## Cartes de Nextcloud Deck {#cards-from-nextcloud-deck}

Si votre association planifiait auparavant dans Nextcloud Deck,
Parcella peut copier un tableau Deck sur le tableau des tâches et le
tenir à jour. C'est un miroir à sens unique, destiné à faciliter la
transition.

Configuré par un administrateur : activez **Synchronisation Nextcloud
Deck** sous **Activer et désactiver les modules**, puis saisissez le
serveur, l'utilisateur, le mot de passe d'application et l'**ID du
tableau Deck** sous **Administration → Intégrations → Nextcloud Deck**
(voir [Intégrations](../administration/integrations.md)). Parcella
interroge ensuite Deck toutes les 15 minutes ; **Synchroniser
maintenant** là-bas le fait immédiatement.

Ce que vous voyez sur le tableau :

- Chaque colonne Deck devient une liste du même nom (créée si
  nécessaire).
- Les cartes synchronisées ont une icône de nuage (**Synchronisé depuis
  Nextcloud Deck**).
- Dans la fenêtre de tâche, un avis gris indique : **Cette carte est
  synchronisée depuis Nextcloud Deck -- le titre, la description, la
  date d'échéance et la liste y sont gérés et mis à jour
  automatiquement. La priorité, les étiquettes, les assignés et les
  commentaires n'existent que dans Parcella et restent toujours
  modifiables.** Le titre, la description, l'échéance et la liste ne
  peuvent pas être modifiés dans Parcella.
- **Adopter dans Parcella** coupe le lien : à partir de là, la carte est
  une carte Parcella ordinaire, entièrement modifiable, et Deck ne la
  modifie plus.
- Une carte supprimée ou archivée dans Deck n'est jamais supprimée dans
  Parcella. Elle cesse simplement d'être synchronisée, comme si vous
  l'aviez adoptée.
- Les cartes Deck archivées ne sont pas copiées du tout.

## Voir aussi {#related}

- [Tableau de bord](../getting-started/dashboard.md) -- la carte
  **Tâches en retard**.
- [Heures de travail](work-hours.md) -- les tâches des sessions de
  travail.
- [Intégrations](../administration/integrations.md) -- la connexion à
  Nextcloud Deck.
- [Activer et désactiver les modules](../administration/modules.md)

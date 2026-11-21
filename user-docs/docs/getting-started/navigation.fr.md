# S'orienter dans l'application {#finding-your-way-around}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Chaque page de Parcella a le même cadre : une **barre latérale** verte à
gauche avec la navigation, et une **barre du haut** blanche au-dessus de
la page avec le titre de la page et les boutons de cette page.

!!! info "Qui peut l'utiliser"
    Toute personne connectée. Les entrées que *vous* voyez dépendent des
    modules activés par votre association et de vos droits -- voir
    [Pourquoi des entrées apparaissent et disparaissent](#why-entries-appear-and-disappear).

![Barre latérale et barre du haut](../assets/screenshots/getting-started/navigation.png)

## La barre latérale {#the-sidebar}

De haut en bas, la barre latérale contient :

1. **Le nom et le logo de votre association**, avec le mot **Gestion**
   en dessous.
2. **Les entrées de navigation** -- une par module.
3. **Administration** -- uniquement pour les administrateurs, toujours
   tout en bas de la liste.
4. **Le pied** avec votre propre compte.

### Entrées simples et groupes {#single-entries-and-groups}

Les petits modules sont un simple lien, par exemple **Membres**,
**Parcelles**, **Inventaire** ou **Notes**. Cliquez dessus et le module
s'ouvre.

Les modules plus importants sont un **groupe** : un titre en majuscules
avec une petite flèche. Cliquer sur le titre déplie ses pages :

| Groupe | Pages qu'il contient |
|---|---|
| **Sessions de travail** | **Sessions & Aperçu**, **Évaluation annuelle**, **Parrainages**, **Transferts d'heures**, **Tâches** |
| **Eau** | **Aperçu**, **Points de mesure**, **Relevés**, **Évaluation**, **Configuration** |
| **Électricité** | **Aperçu**, **Points de mesure**, **Relevés**, **Évaluation**, **Configuration** |
| **Assurance** | **Aperçu**, **Parcelles**, **Configuration**, **Évaluation** |
| **Calendrier** | **Calendrier communautaire**, **Anniversaires**, **Présence du conseil**, **Absence du conseil**, **Mes calendriers** |
| **Finances** | **Aperçu**, **Factures émises**, **Relances**, **Factures reçues** |
| **Administration** | **Système**, **Utilisateurs**, **Groupes**, **Jetons API**, **Paramètres**, **Intégrations**, **Journal des e-mails**, **Données d'exemple**, **Documentation API (Swagger)** |

Un **seul groupe est ouvert à la fois** : ouvrir un groupe referme celui
qui était ouvert, pour que la barre latérale reste courte. Le groupe qui
contient la page où vous êtes s'ouvre toujours de lui-même. Sinon, votre
navigateur se souvient du dernier groupe que vous avez ouvert.

La page où vous vous trouvez est mise en évidence par une barre claire
sur son bord gauche.

**Documentation API (Swagger)** ouvre la description technique de
l'interface de programmation de Parcella dans un nouvel onglet du
navigateur. Elle s'adresse aux personnes qui connectent d'autres
logiciels et peut être ignorée sinon.

### Badges : ce qui demande votre attention {#badges-things-that-need-attention}

Certaines entrées affichent un petit chiffre rouge. Il vous indique
combien d'éléments y attendent. Survolez-le pour voir ce qu'il compte.

| Entrée | Le badge compte |
|---|---|
| **Sessions de travail** et **Sessions & Aperçu** | Les nouvelles inscriptions des 14 derniers jours à des sessions de travail à venir que personne n'a encore marquées comme vérifiées. |
| **Demandes d'achat** | Les demandes qui attendent encore une décision. |
| **Candidats** | Les nouvelles candidatures que personne n'a encore regardées. |
| **Assistance** | Les conversations ouvertes (actives ou en attente) dans le helpdesk de l'association. |
| **Tableau des tâches** | Les tâches dont l'échéance est passée et qui ne sont pas terminées. |

Un badge disparaît de lui-même une fois l'affaire traitée -- par exemple
quand la demande d'achat est approuvée ou refusée, ou que la tâche est
terminée. Il n'y a pas de « marquer comme lu ». Les mêmes chiffres
apparaissent sous forme de tuiles sur le
[Tableau de bord](dashboard.md).

### Le pied : votre compte {#the-footer-your-account}

En bas de la barre latérale, vous voyez votre avatar et votre nom, et en
dessous les groupes dont vous faites partie (ou **Administrateur** /
**Conseil d'administration** pour les anciens comptes qui ont un rôle au
lieu de groupes -- voir
[Rôles, groupes et droits](roles-and-permissions.md)).

| Bouton | Ce qu'il fait |
|---|---|
| **Changer le mot de passe** | Ouvre votre profil : mot de passe, avatar et jetons API. Voir [Première connexion et votre compte](first-login.md#change-password). |
| **Déconnexion** | Vous déconnecte et revient à la page de connexion. |

## La barre du haut {#the-top-bar}

La barre du haut affiche à gauche le titre de la page actuelle. À droite
se trouvent les actions de cette page, comme **Nouveau membre**, un
export ou un bouton retour. La barre du haut reste visible quand vous
faites défiler une longue liste.

## Pourquoi des entrées apparaissent et disparaissent {#why-entries-appear-and-disappear}

Une entrée n'est affichée que si ces **deux** conditions sont remplies :

1. **Le module est activé** pour votre association. Les administrateurs
   activent et désactivent les modules sous
   [Activer et désactiver les modules](../administration/modules.md). Un
   module désactivé disparaît pour tout le monde -- ses données sont
   conservées et reviennent quand le module est réactivé.
2. **Vous avez le droit de le lire.** Les membres du bureau et les
   administrateurs voient chaque module activé. Tous les autres voient
   **Membres** et **Parcelles** ainsi que les modules pour lesquels l'un
   de leurs groupes accorde la **Lecture**. Voir
   [Rôles, groupes et droits](roles-and-permissions.md).

Quelques entrées suivent leur propre règle :

- **Tableau des tâches** et **Annonces** ne sont affichés qu'aux
  personnes ayant un accès complet (membres du bureau, administrateurs,
  ou un groupe avec **Accès complet à chaque module**). Les groupes ne
  peuvent pas les accorder séparément.
- **Assistance** : avec le droit de lecture sur **Assistance
  (helpdesk)**, vous obtenez la liste des conversations propre à
  Parcella. Sans lui, l'entrée apparaît quand même si le helpdesk de
  votre association a une adresse web, et ouvre alors le helpdesk
  lui-même dans un nouvel onglet.
- **Administration** n'est affiché qu'aux administrateurs.

Si vous ouvrez une page que vous n'avez pas le droit de voir -- depuis
un favori ou un lien envoyé par un collègue -- vous obtenez le message
**Vous n'avez pas la permission de faire cela**. Une page d'un module
désactivé répond par une page « introuvable » : « Cette fonction est
désactivée pour cette association. »

### L'ordre des entrées {#the-order-of-the-entries}

Votre association décide de l'ordre des entrées. Un administrateur le
règle dans les [Paramètres de l'association](../administration/settings.md#navigation-order).
L'ordre est le même pour tout le monde.

## Raccourci clavier pour les pages de détail {#keyboard-shortcut-for-detail-pages}

Sur les pages de détail qui ont des boutons **Précédent** et
**Suivant** -- membres, parcelles, points de mesure, la page assurance
d'une parcelle et les contacts externes -- **Ctrl + ←** et **Ctrl + →**
passent à l'enregistrement précédent et suivant, comme ces boutons. Le
raccourci ne fait rien pendant que vous tapez dans un champ.

!!! note "Utilisateurs de Mac"
    Sur un Mac, Ctrl + touches fléchées passe généralement d'un bureau à
    l'autre (« Spaces »), donc le système intercepte le raccourci avant
    que Parcella le voie. Utilisez plutôt les boutons de la page, ou
    désactivez ce raccourci système.

## Sur un téléphone ou une petite tablette {#on-a-phone-or-small-tablet}

Sur les écrans étroits, la barre latérale est masquée pour laisser de la
place à la page.

- Touchez le bouton **☰** en haut à gauche de la barre du haut pour
  faire apparaître la barre latérale.
- Touchez une entrée pour y aller ; la barre latérale se ferme
  d'elle-même.
- Pour la fermer sans aller nulle part, touchez la page assombrie à côté,
  ou appuyez sur **Échap** sur un clavier.

Les boutons et champs de saisie sont un peu plus grands sur les écrans
tactiles, et les rangées de boutons de filtre passent sur plusieurs
lignes au lieu de déborder de l'écran. Les tableaux larges peuvent
défiler latéralement avec le doigt.

## Voir aussi {#related}

- [Tableau de bord](dashboard.md)
- [Rôles, groupes et droits](roles-and-permissions.md)
- [Activer et désactiver les modules](../administration/modules.md)

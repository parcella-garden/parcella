# Rôles, groupes et droits {#roles-groups-and-permissions}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Toutes les personnes qui aident à faire tourner l'association n'ont pas
besoin de tout voir. La personne qui relève les compteurs d'eau n'a pas
besoin des coordonnées bancaires, et le trésorier n'a pas besoin de
planifier les sessions de travail. Parcella vous permet de donner à
chaque personne exactement l'accès dont sa fonction a besoin.

!!! info "Qui peut l'utiliser"
    Cette page explique les accès pour tout le monde. Seuls les
    **administrateurs** peuvent changer qui a quel accès, sous
    [Utilisateurs et invitations](../administration/users.md) et
    [Groupes](../administration/groups.md).

## Les trois niveaux d'accès {#the-three-levels-of-access}

Chaque compte relève de l'un des trois niveaux.

| Niveau | Voit et modifie | Ouvre l'espace **Administration** | Comment l'obtenir |
|---|---|---|---|
| **Administrateur** | Tout dans chaque module activé | Oui | Un groupe avec **Accès au panneau d'administration**, ou l'ancien rôle **Administrateur** |
| **Accès complet** (typiquement le bureau) | Tout dans chaque module activé | Non | Un groupe avec **Accès complet à chaque module**, ou l'ancien rôle **Conseil d'administration** |
| **Limité** | Ce que ses groupes autorisent, module par module ; au moins la lecture des membres et des parcelles | Non | Appartenance à un ou plusieurs groupes sans ces deux cases cochées |

L'espace **Administration** -- utilisateurs, groupes, paramètres de
l'association, intégrations, sauvegardes -- est volontairement séparé de
l'accès complet. Faire partie du bureau ne fait pas automatiquement de
quelqu'un la personne qui entretient l'installation, et inversement. Les
administrateurs ont toujours aussi un accès complet aux modules.

## Groupes {#groups}

Un **groupe** est un ensemble nommé de droits, par exemple « Équipe
eau », « Trésorier » ou « Bureau ». Les administrateurs créent les
groupes et y placent des comptes. Une personne peut faire partie de
plusieurs groupes.

Un groupe accorde soit :

- **Accès complet à chaque module**, soit
- **Accès au panneau d'administration** (qui inclut l'accès complet),
  soit
- **Lecture**, **Écriture** et **Suppression** par module, cochés
  individuellement.

### Ce que signifient Lecture, Écriture et Suppression {#what-read-write-and-delete-mean}

| Droit | Permet |
|---|---|
| **Lecture** | Ouvrir le module, voir ses listes et pages de détail, et télécharger ses exports et rapports. Sans lui, le module n'apparaît pas dans la barre latérale. |
| **Écriture** | Créer de nouveaux enregistrements et modifier ceux qui existent -- ajouter un relevé de compteur, modifier un membre, enregistrer le paiement d'une facture. |
| **Suppression** | Supprimer des enregistrements, là où le module permet la suppression. |

!!! tip "Cochez aussi Lecture"
    Écriture et Suppression s'entendent en plus de Lecture. Une personne
    qui ne peut pas lire un module ne le voit pas dans la barre latérale
    et ne peut pas ouvrir ses pages ; Écriture seule ne sert donc à rien.
    Chaque chapitre de module indique quelles actions nécessitent quel
    droit.

### Les modules qu'un groupe peut accorder {#the-modules-a-group-can-grant}

| Module dans le formulaire du groupe | Couvre |
|---|---|
| **Membres et parcelles** | [Membres](../modules/members.md) et [Parcelles](../modules/parcels.md) |
| **Sessions de travail** | [Heures de travail](../modules/work-hours.md) |
| **Eau** | Partie eau de [Eau et électricité](../modules/metering.md) |
| **Électricité** | Partie électricité de [Eau et électricité](../modules/metering.md) |
| **Assurance** | [Assurances](../modules/insurance.md) |
| **Demandes d'achat** | [Demandes d'achat](../modules/purchase-requests.md) |
| **Calendrier** | [Calendrier](../modules/calendar.md) |
| **Inventaire** | [Inventaire](../modules/inventory.md) |
| **Finances** | [Finances](../modules/finances/index.md) |
| **Assistance (helpdesk)** | [Assistance](../modules/support.md) |
| **Candidats** | [Candidats](../modules/applicants.md) |
| **Contacts externes** | [Contacts externes](../modules/external-contacts.md) |
| **Rapports** | [Rapports](../modules/reporting.md) |
| **Notes** | [Notes](../modules/notes.md) |
| **Procédures** | [Procédures](../modules/processes.md) |

### Plusieurs groupes : le plus généreux l'emporte {#several-groups-the-most-generous-wins}

Si une personne fait partie de plusieurs groupes, ses droits
s'additionnent. Pour chaque module et chaque niveau, il suffit qu'un
groupe l'accorde. Exemple : le groupe « Équipe eau » accorde la lecture
et l'écriture sur Eau, le groupe « Calendrier » la lecture sur
Calendrier. Quelqu'un qui fait partie des deux peut lire et modifier les
données d'eau et lire le calendrier.

### Tout le monde peut consulter les membres et les parcelles {#everybody-can-look-up-members-and-parcels}

Chaque compte, même sans aucun groupe, peut **lire** les membres et les
parcelles. Toute personne qui aide à gérer l'association doit savoir qui
est qui et quelle parcelle appartient à qui. Pour les modifier, il faut
l'**Écriture** sur **Membres et parcelles**.

## Ce que seul l'accès complet permet {#things-only-full-access-can-do}

Quelques domaines ne peuvent pas être accordés par module. Ils sont
toujours réservés aux personnes ayant un accès complet (bureau,
administrateurs, ou un groupe avec **Accès complet à chaque module**) :

- le [Tableau des tâches](../modules/tasks.md),
- les [Annonces](../modules/announcements.md),
- approuver ou refuser une [demande d'achat](../modules/purchase-requests.md)
  -- les deux approbations requises doivent venir de personnes ayant un
  accès complet,
- créer et modifier des calendriers sous **Mes calendriers** dans le
  [Calendrier](../modules/calendar.md),
- le dossier cloud d'une parcelle (parcourir, téléverser, télécharger)
  et le téléchargement de la pièce jointe d'une facture reçue,
- créer une tâche à partir d'une conversation d'assistance ou en lier
  une à une tâche.

## Les anciens rôles : Administrateur, Bureau, Trésorier, Lecture seule {#the-older-roles-administrator-board-treasurer-read-only}

Les versions précédentes de Parcella attribuaient à chaque compte un
**rôle** fixe. Les comptes créés à l'époque peuvent encore en avoir un :

| Rôle | Effet aujourd'hui |
|---|---|
| **Administrateur** | Accès complet plus l'espace d'administration, sans besoin de groupe. Le tout premier compte d'une nouvelle installation a ce rôle. |
| **Conseil d'administration** | Accès complet, sans besoin de groupe. |
| **Trésorier** | Rien de plus que la lecture de base des membres et des parcelles. Utilisez un groupe pour accorder davantage. |
| **Lecture seule (consultation uniquement)** | Comme Trésorier : accès de base uniquement, tout le reste vient des groupes. |

Les nouveaux comptes reçoivent le rôle inerte **Lecture seule** ; leur
accès réel ne vient que des groupes. Un administrateur peut faire passer
un compte Administrateur ou Conseil d'administration aux groupes avec
**Retirer le rôle existant** (voir
[Utilisateurs et invitations](../administration/users.md)). Placez
*d'abord* le compte dans le bon groupe, sinon il retombe à l'accès de
base.

Le pied de la barre latérale affiche les groupes dont vous faites
partie. Sans groupe, il affiche **Administrateur** ou **Conseil
d'administration** si vous avez ce rôle, sinon un tiret.

## Filet de sécurité : le dernier administrateur {#safety-net-the-last-administrator}

Parcella refuse toute modification qui ne laisserait **aucun compte
actif capable d'ouvrir l'espace d'administration**. Vous obtenez le
message **Impossible de retirer l'accès administrateur au dernier compte
Administrateur/Conseil restant** quand vous essayez de désactiver,
supprimer, rétrograder ou retirer de son groupe le dernier compte de ce
type, ou de supprimer ou décocher le dernier groupe qui l'accorde. Sans
au moins un administrateur, plus personne ne pourrait régler les
problèmes d'accès.

## L'API REST et les jetons API {#the-rest-api-and-api-tokens}

Les programmes qui communiquent avec Parcella via son interface de
programmation utilisent un [jeton API](../administration/api-tokens.md).
Un jeton personnel agit avec les droits du compte auquel il appartient.
<!-- TODO(verify): several REST API endpoints still check only the old role (Administrator/Board) rather than group permissions, so a group-based full-access account may be refused some API writes. Confirm before stating this to users. -->

## Voir aussi {#related}

- [Groupes](../administration/groups.md) -- créer des groupes et cocher des droits
- [Utilisateurs et invitations](../administration/users.md) -- ajouter des personnes aux groupes
- [S'orienter dans l'application](navigation.md#why-entries-appear-and-disappear)

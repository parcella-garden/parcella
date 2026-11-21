# Groupes {#groups}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les groupes décident de ce que chaque personne peut voir et modifier.
Vous créez un groupe pour une fonction dans votre association -- « Bureau »,
« Trésorier », « Équipe eau » --, vous cochez ce dont cette fonction a
besoin, et vous y placez les bonnes personnes.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Groupes**.

Les principes des groupes -- Lecture, Écriture et Suppression, accès
complet, espace d'administration -- sont expliqués dans
[Rôles, groupes et droits](../getting-started/roles-and-permissions.md).
Cette page décrit l'écran.

![Groupes](../assets/screenshots/administration/groups.png)

## Créer un groupe {#create-group}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nom** | Obligatoire, et doit être unique (**Un groupe portant ce nom existe déjà**). |
| **Description** | Note facultative sur la raison d'être du groupe. |
| **Accès complet à chaque module** | Les membres du groupe peuvent lire, modifier et supprimer tout dans chaque module activé, comme le bureau. |
| **Accès au panneau d'administration** | Les membres du groupe peuvent aussi ouvrir **Administration**. Cocher cette case inclut l'accès complet, donc la case d'accès complet disparaît. |
| **Créer un groupe** | Crée le groupe. Vous voyez **Groupe créé**. |

Un nouveau groupe sans aucune des deux cases cochées n'accorde encore
rien. Ouvrez-le ci-dessous pour cocher ses droits.

## Les cartes de groupe {#the-group-cards}

Chaque groupe apparaît sous forme de carte sous le formulaire, repliée.
L'en-tête affiche son nom et un badge **Administration** ou
**Accès complet** s'il accorde l'un des deux. Cliquez sur l'en-tête pour
déplier la carte.

Le bouton **corbeille** dans l'en-tête supprime le groupe après
confirmation. Ses membres perdent ce que le groupe leur donnait. Parcella
refuse de supprimer le dernier groupe qui donne accès à l'espace
d'administration, si aucun autre compte n'y a accès.

### Paramètres et droits {#settings-and-permissions}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nom**, **Description** | Comme à la création. |
| **Accès complet à chaque module**, **Accès au panneau d'administration** | Comme à la création. Quand l'une des deux est cochée, le tableau des droits est masqué car il n'est pas nécessaire. |
| Tableau des droits | Une ligne par **Module** avec les cases **Lecture**, **Écriture** et **Suppression**. Voir la liste des modules ci-dessous. |
| **Enregistrer** | Enregistre le nom, la description, les deux cases et tout le tableau. Vous voyez **Groupe mis à jour**. |

Les modules du tableau : **Membres et parcelles**, **Sessions de
travail**, **Eau**, **Électricité**, **Assurance**, **Demandes d'achat**,
**Calendrier**, **Inventaire**, **Finances**, **Assistance (helpdesk)**,
**Candidats**, **Contacts externes**, **Rapports**, **Notes**,
**Procédures**. Les modules que votre association a désactivés sont
quand même listés ; leurs coches prennent effet quand le module est
activé.

!!! tip "La lecture d'abord"
    Cochez **Lecture** partout où vous cochez **Écriture** ou
    **Suppression**. Sans Lecture, le module n'apparaît même pas dans la
    barre latérale de la personne.

Le tableau des tâches et les annonces ne figurent pas dans le tableau :
ils ne sont disponibles qu'avec l'accès complet.

### Utilisateurs assignés {#assigned-users}

Liste les comptes du groupe, avec avatar, nom et adresse e-mail.

| Élément | Ce qu'il fait |
|---|---|
| **×** à côté d'une personne | La retire immédiatement du groupe (**Utilisateur retiré**). |
| **Ajouter un utilisateur...** + **Ajouter** | Choisir un compte et l'ajouter (**Utilisateur ajouté**). |

La liste **Ajouter un utilisateur...** ne propose que les comptes qui
reçoivent leurs accès par des groupes. Les anciens comptes avec le rôle
**Administrateur** ou **Conseil d'administration** ont déjà un accès
complet et ne sont pas proposés ici ; si vous voulez les faire passer
aux groupes, ajoutez-les depuis leur page
[Modifier l'utilisateur](users.md#edit-user). Quand tous les comptes
possibles sont déjà dans le groupe, vous voyez une courte note au lieu
de la liste ; quand il n'y en a aucun, un lien **En inviter un**.

Les changements de droits prennent effet au prochain clic de la
personne -- elle n'a pas besoin de se reconnecter.

## Exemple de configuration {#example-set-up}

| Groupe | Coché |
|---|---|
| Administrateurs | **Accès au panneau d'administration** |
| Bureau | **Accès complet à chaque module** |
| Trésorier | Finances : Lecture, Écriture, Suppression. Membres et parcelles : Lecture, Écriture. Demandes d'achat : Lecture. Assurance : Lecture. |
| Releveurs de compteurs | Eau : Lecture, Écriture. Électricité : Lecture, Écriture. |
| Équipe des sessions de travail | Sessions de travail : Lecture, Écriture. Calendrier : Lecture. |

Une personne peut faire partie de plusieurs groupes ; ses droits
s'additionnent.

## Voir aussi {#related}

- [Utilisateurs et invitations](users.md)
- [Rôles, groupes et droits](../getting-started/roles-and-permissions.md)
- [Activer et désactiver les modules](modules.md)

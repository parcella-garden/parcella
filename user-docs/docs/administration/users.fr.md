# Utilisateurs et invitations {#users-and-invitations}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

C'est ici que vous décidez qui peut se connecter à Parcella. Les
nouvelles personnes sont invitées par e-mail et définissent elles-mêmes
leur mot de passe ; vous choisissez à quels groupes elles appartiennent.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Utilisateurs**.

Un *utilisateur* est un compte de connexion -- un membre du bureau, le
trésorier, la personne qui relève les compteurs. Ce n'est pas la même
chose qu'un *membre* de l'association : la plupart des jardiniers sont
membres mais n'ont jamais de compte utilisateur.

## Gestion des utilisateurs {#user-management}

![Gestion des utilisateurs](../assets/screenshots/administration/users.png)

La page présente le formulaire d'invitation à gauche et la liste des
comptes à droite. Les messages sur ce que vous venez de faire
apparaissent en haut.

### Inviter un utilisateur {#invite-user}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Adresse e-mail** | L'adresse e-mail de la nouvelle personne. Elle devient son identifiant de connexion. |
| **Groupes** | Cochez les groupes auxquels la personne doit appartenir. Ses accès viennent uniquement de ces groupes -- voir [Groupes](groups.md). S'il n'existe encore aucun groupe, vous voyez **Aucun groupe pour le moment.** avec un lien **En créer un**. |
| **Envoyer l'invitation** | Envoie un e-mail avec un lien personnel. Le lien est valable **7 jours**. |

Ce qui se passe :

- La personne reçoit l'e-mail **Invitation à Parcella** avec un bouton
  **Accepter l'invitation**. Elle choisit elle-même son nom et son mot
  de passe (voir [Première connexion](../getting-started/first-login.md#getting-an-account-the-invitation))
  et est placée dans les groupes cochés.
- Si l'adresse appartient déjà à un compte, vous voyez **E-mail déjà
  enregistré**.
- S'il existe déjà une invitation en attente pour l'adresse, l'ancienne
  cesse de fonctionner et seule la nouvelle compte.
- Si vous ne cochez aucun groupe, la personne pourra seulement consulter
  les membres et les parcelles après avoir accepté. Vous pouvez ajouter
  des groupes plus tard.

!!! warning "L'e-mail doit fonctionner"
    Les invitations nécessitent un serveur de messagerie fonctionnel
    (voir [Paramètres de l'association](settings.md#email-smtp)). Si le
    serveur de messagerie refuse l'e-mail, la page l'indique au lieu de
    **Invitation envoyée** : « L'invitation pour … est enregistrée, mais
    l'e-mail n'a pas pu être envoyé. Vérifiez les paramètres e-mail et le
    Journal des e-mails, puis renvoyez l'invitation. » L'invitation reste
    sous **Invitations en attente** ; une fois les paramètres e-mail
    corrigés, utilisez **Renvoyer l'invitation**. Le
    [Journal des e-mails](email-log.md) indique la raison donnée par le
    serveur de messagerie.

### Invitations en attente {#pending-invitations}

Affichées sous le formulaire tant que des invitations attendent d'être
acceptées. Chaque ligne affiche l'adresse, les groupes cochés (ou
**Aucun groupe sélectionné**), **Valable jusqu'au** avec la date, et le
badge **en attente**.

| Bouton | Ce qu'il fait |
|---|---|
| **Renvoyer l'invitation** (flèches circulaires) | Renvoie l'e-mail et prolonge le lien de 7 jours à partir d'aujourd'hui. Le lien du premier e-mail continue de fonctionner. Vous voyez **Invitation renvoyée**. |
| **Supprimer l'invitation** (corbeille) | Après confirmation, l'invitation est supprimée et son lien cesse de fonctionner. |

Les invitations acceptées disparaissent de la liste ; la personne
apparaît alors sous **Utilisateurs enregistrés**.

### Utilisateurs enregistrés {#registered-users}

| Colonne / bouton | Ce qu'elle affiche ou fait |
|---|---|
| **Nom** | Avatar et nom. |
| **E-mail** | L'adresse de connexion. |
| **Groupes** | Les groupes auxquels le compte appartient. Les anciens comptes sans groupe affichent leur rôle, **Administrateur** ou **Conseil d'administration** ; sinon **–**. |
| **Statut** | **actif** ou **inactif**. |
| **Modifier** (crayon) | Ouvre [Modifier l'utilisateur](#edit-user). |
| **Désactiver** / **Activer** (interrupteur) | Désactive ou réactive le compte en un clic. Pas affiché pour votre propre compte, marqué **Moi** à la place. |

**Désactiver** un compte bloque immédiatement la personne -- y compris
sur tout ordinateur où elle est connectée en ce moment. Tout ce qu'elle
a créé ou approuvé reste, avec son nom. Réactivez le compte et elle
pourra se connecter avec son ancien mot de passe.

Vous ne pouvez pas vous désactiver vous-même, ni désactiver le dernier
compte capable d'ouvrir l'espace d'administration.

## Modifier l'utilisateur {#edit-user}

![Modifier l'utilisateur](../assets/screenshots/administration/user-edit.png)

**Annuler** en haut revient à la liste sans enregistrer.

### Avatar {#avatar}

Comme sur le profil d'un utilisateur : choisissez un fichier PNG, JPEG
ou WebP de 2 Mo au maximum et cliquez sur **Téléverser**, ou
**Supprimer l'avatar** pour le supprimer. Utile pour les personnes qui
ne téléversent pas d'image elles-mêmes.

### Modifier l'utilisateur {#edit-user_1}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nom** | Obligatoire. |
| **Adresse e-mail** | Obligatoire ; c'est l'identifiant de connexion, prévenez donc la personne quand vous la changez. Ne doit pas appartenir à un autre compte (**E-mail déjà enregistré**). |
| **Rôle** | Affiché uniquement pour les anciens comptes qui ont encore le rôle **Administrateur** ou **Conseil d'administration**, avec la note *L'accès de ce compte provient de son rôle, pas de son appartenance à un groupe.* Il ne peut pas être modifié ici. |
| **Enregistrer les modifications** | Enregistre le nom et l'e-mail. Vous voyez **Utilisateur mis à jour** dans la liste. |

### Retirer le rôle existant {#remove-legacy-role}

Uniquement pour les comptes ayant le rôle **Administrateur** ou
**Conseil d'administration**. **Retirer le rôle existant** supprime le
rôle ; à partir de là, l'accès du compte ne vient plus que de ses
groupes, comme pour tous les comptes plus récents.

!!! warning "Ajoutez d'abord les groupes"
    Sans groupe, le compte retombe à l'accès de base (lecture des
    membres et des parcelles) dès que vous cliquez. Pour un ancien
    **Administrateur**, ajoutez d'abord le compte à un groupe avec
    **Accès au panneau d'administration** ; pour **Conseil
    d'administration**, à un groupe avec **Accès complet à chaque
    module**. Parcella refuse de retirer le rôle au dernier
    administrateur.

### Groupes {#groups}

Liste tous les groupes. **Ajouter** place le compte dans ce groupe,
**Retirer** l'en sort. Le changement s'applique immédiatement -- inutile
de cliquer sur **Enregistrer les modifications**.

### Zone de danger {#danger-zone}

Pas affichée quand vous modifiez votre propre compte.

| Bouton | Ce qu'il fait |
|---|---|
| **Désactiver** / **Activer** | Comme dans la liste : bloque immédiatement la personne, rien n'est supprimé. |
| <a id="reset-password"></a>**Réinitialiser le mot de passe** | Pour quelqu'un qui a oublié son mot de passe. Après confirmation, Parcella crée un **mot de passe temporaire** et l'affiche **une seule fois**, avec un bouton **Copier**. Transmettez-le à la personne (par téléphone, en personne). Son ancien mot de passe cesse de fonctionner, elle est déconnectée partout, et à sa prochaine connexion elle doit choisir un nouveau mot de passe. Si le compte est désactivé, il vous est rappelé de l'activer. |
| **Supprimer définitivement** | Supprime complètement le compte, après confirmation. Possible uniquement pour les comptes qui n'ont laissé aucune trace nulle part -- typiquement un compte créé par erreur et jamais utilisé. |

Pour votre propre mot de passe, utilisez plutôt **Changer le mot de
passe** dans la barre latérale.

Dès qu'une personne a fait quoi que ce soit dans Parcella -- créé un
enregistrement, approuvé une demande, saisi un relevé de compteur -- le
compte ne peut plus être supprimé, et vous voyez *Cet utilisateur a un
historique d'activité ... Désactivez-le plutôt.* Cela garde les
archives de l'association complètes : on peut toujours voir qui a fait
quoi, des années plus tard.

## Voir aussi {#related}

- [Groupes](groups.md)
- [Rôles, groupes et droits](../getting-started/roles-and-permissions.md)
- [Première connexion et votre compte](../getting-started/first-login.md)
- [Jetons API](api-tokens.md)

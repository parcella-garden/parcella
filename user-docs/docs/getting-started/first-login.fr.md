# Première connexion et votre compte {#first-login-and-your-account}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Cette page couvre tout ce qui concerne votre propre compte : comment
vous l'obtenez, comment vous vous connectez, et comment vous changez
votre mot de passe et votre photo.

!!! info "Qui peut l'utiliser"
    Toute personne ayant un compte Parcella. Il n'y a pas d'inscription
    publique : un compte n'existe qu'après qu'un administrateur vous a
    invité.

## Obtenir un compte : l'invitation {#getting-an-account-the-invitation}

Un administrateur de votre installation vous invite par e-mail (voir
[Utilisateurs et invitations](../administration/users.md)). Vous recevez
un e-mail avec l'objet **Invitation à Parcella** et un bouton
**Accepter l'invitation**. Le lien qu'il contient est valable
**7 jours**.

!!! tip "Aucun e-mail reçu ?"
    Regardez d'abord dans votre dossier de spam. S'il n'y est pas,
    demandez à l'administrateur de vérifier le
    [Journal des e-mails](../administration/email-log.md) et, si
    nécessaire, de renvoyer l'invitation. Le renvoi prolonge le lien de
    7 jours ; le lien du premier e-mail continue de fonctionner.

### Accepter l'invitation {#accept-invitation}

<!-- TODO(verify): no screenshot of "Set up your account" -- it needs a valid invitation link, which the screenshot tool can't produce from the sample data. -->

Cliquer sur le lien ouvre la page **Configurer votre compte**. Sous le
titre, vous voyez l'adresse à laquelle l'invitation a été envoyée
(**Invitation pour** ...). Cette adresse devient votre identifiant de
connexion ; vous ne pouvez pas la changer ici.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nom** | Votre prénom et votre nom. Les autres membres du bureau le voient dans les listes, sur les tâches, les approbations et l'historique des modifications. |
| **Mot de passe** | Au moins 8 caractères. |
| **Confirmer le mot de passe** | Retapez le même mot de passe. S'ils ne correspondent pas, vous voyez **Les mots de passe ne correspondent pas.** |
| **Créer un compte** | Crée votre compte et vous connecte immédiatement. Vous arrivez sur le [Tableau de bord](dashboard.md). |

Ce que vous pouvez voir ensuite dépend des groupes choisis par
l'administrateur lors de l'invitation. S'il n'en a choisi aucun, vous
pouvez seulement consulter les membres et les parcelles -- demandez-lui
de vous ajouter à un groupe. Voir
[Rôles, groupes et droits](roles-and-permissions.md).

### Invitation expirée {#invitation-expired}

![Invitation expirée](../assets/screenshots/getting-started/invitation-expired.png)

Vous voyez **Invitation expirée** -- *Ce lien d'invitation n'est plus
valide ou a déjà été utilisé.* -- quand :

- plus de 7 jours se sont écoulés depuis l'envoi (ou le dernier renvoi)
  de l'invitation,
- vous avez déjà créé votre compte avec ce lien, ou
- l'administrateur a supprimé l'invitation, ou a de nouveau invité la
  même adresse (seule la plus récente invitation fonctionne).

Demandez à un administrateur de vous inviter à nouveau.
**Retour à la connexion** vous mène à la page de connexion, ce qui
n'aide que si vous avez déjà un compte.

## Se connecter {#signing-in}

![Page de connexion](../assets/screenshots/getting-started/login.png)

Ouvrez l'adresse Parcella de votre association dans un navigateur web.
La page de connexion affiche le logo et le nom de votre association
(tous deux définis par un administrateur dans les
[Paramètres de l'association](../administration/settings.md)).

| Champ / bouton | Ce qu'il fait |
|---|---|
| **E-mail** | L'adresse à laquelle votre invitation a été envoyée. Majuscules et minuscules n'ont pas d'importance. |
| **Mot de passe** | Votre mot de passe. |
| **Se connecter** | Vous connecte et ouvre le [Tableau de bord](dashboard.md). |

Les messages que vous pouvez voir :

| Message | Signification |
|---|---|
| **L'e-mail ou le mot de passe est incorrect.** | L'un des deux est faux. Pour votre protection, Parcella ne dit pas lequel. |
| **Votre compte a été désactivé.** | Un administrateur a désactivé votre compte. Vos données sont toujours là ; demandez-lui de le réactiver. |
| **Trop de tentatives de connexion échouées. Veuillez patienter quelques minutes et réessayer.** | Après plusieurs mots de passe erronés, Parcella suspend les tentatives de connexion pour ce compte pendant environ 15 minutes. |

Vous restez connecté pendant **8 heures** (sauf si l'hébergeur de votre
installation a modifié cela). Ensuite, Parcella vous demande de vous
reconnecter, même si vous avez travaillé tout ce temps.

Pour vous déconnecter, cliquez sur **Déconnexion** en bas de la barre
latérale. Faites-le sur tout ordinateur partagé ou public.

!!! note "Mot de passe oublié ?"
    Il n'y a pas de lien « mot de passe oublié », c'est voulu. Demandez
    à un administrateur : il peut réinitialiser votre mot de passe et
    vous en donner un temporaire (voir
    [Utilisateurs et invitations](../administration/users.md#reset-password)).
    Vous devrez alors choisir un nouveau mot de passe à votre prochaine
    connexion.

## La toute première connexion après l'installation {#the-very-first-login-after-installation}

Quand Parcella démarre pour la première fois, il crée de lui-même un
compte administrateur :

- **E-mail :** `admin@parcella.local`
- **Mot de passe :** `admin1234`

Ces identifiants sont publiés dans les instructions d'installation de
Parcella et sont les mêmes sur chaque nouvelle installation : n'importe
qui pourrait donc les utiliser. C'est pourquoi ce compte est verrouillé
tant que son mot de passe n'a pas été changé : après la connexion, vous
arrivez directement sur **Changer le mot de passe**, avec l'avis

> Ce compte utilise encore le mot de passe par défaut de l'installation
> initiale. Veuillez en choisir un nouveau -- le reste de l'application
> reste verrouillé jusque-là.

Toute autre page vous ramène ici tant que vous n'avez pas enregistré de
nouveau mot de passe.

!!! warning "Faites-le avant toute autre chose"
    Changez le mot de passe immédiatement, même sur une installation de
    test accessible depuis internet. Ensuite, sous
    [Utilisateurs et invitations](../administration/users.md), remplacez
    le nom et l'adresse e-mail du compte par ceux d'une vraie personne,
    ou invitez les vrais administrateurs et travaillez avec leurs propres
    comptes.

Le même changement forcé a lieu après qu'un administrateur a
réinitialisé votre mot de passe : le mot de passe temporaire ne vous
mène qu'à la page **Changer le mot de passe**.

## Changer le mot de passe {#change-password}

![Changer le mot de passe](../assets/screenshots/getting-started/change-password.png)

Ouvrez-la avec **Changer le mot de passe** en bas de la barre latérale.
Cette page est votre profil personnel : elle contient aussi votre avatar
et un lien vers vos jetons API.

### Avatar {#avatar}

Votre avatar est la petite image ronde affichée à côté de votre nom dans
la barre latérale, dans les listes d'utilisateurs et sur les tâches.
Sans avatar, Parcella affiche une simple icône de personne.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Champ de fichier | Choisissez une image : PNG, JPEG ou WebP, 2 Mo au maximum. |
| **Téléverser** | Enregistre l'image. Vous voyez **Avatar téléversé avec succès.** Un mauvais type de fichier ou un fichier trop volumineux est refusé avec un message. |
| **Supprimer l'avatar** | Affiché seulement si vous en avez un. Le supprime. |

### Jetons API pour les intégrations {#api-tokens-for-integrations}

**Gérer** ouvre **Mes jetons API**. Vous n'en avez besoin que si vous
voulez connecter un autre programme (par exemple un assistant IA) à
Parcella. Voir [Jetons API](../administration/api-tokens.md).

### Changer le mot de passe {#changing-the-password}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Mot de passe actuel** | Votre mot de passe actuel, pour que personne ne puisse le changer sur un ordinateur où vous êtes resté connecté. |
| **Nouveau mot de passe** | Au moins 8 caractères, et différent de l'actuel. |
| **Confirmer le nouveau mot de passe** | Le nouveau mot de passe une seconde fois. |
| **Changer le mot de passe** | Enregistre le nouveau mot de passe. Vous voyez **Mot de passe changé avec succès.** |

Erreurs possibles : **Le mot de passe actuel est incorrect.**,
**Les mots de passe ne correspondent pas.**, **Le mot de passe doit
comporter au moins 8 caractères.** et **Le nouveau mot de passe doit
être différent de l'actuel.**

Ce qui se passe quand vous enregistrez :

- Vous restez connecté dans ce navigateur.
- **Vous êtes déconnecté de tous les autres endroits** -- un autre
  ordinateur, votre téléphone, ou un navigateur que quelqu'un d'autre
  utilise avec votre compte. Utilisez cela si vous soupçonnez que
  quelqu'un connaît votre mot de passe.
- Tous vos **jetons API cessent de fonctionner** (ils apparaissent comme
  **terminé**). Créez-en de nouveaux si vous en avez encore besoin.

## Langue {#language}

Parcella affiche la même langue à tout le monde dans votre association.
Il n'y a pas de choix de langue par utilisateur. Un administrateur
choisit la langue dans les
[Paramètres de l'association](../administration/settings.md#language)
-- English, Deutsch, Polski, Čeština, Slovenčina, Français ou
Nederlands. La page de connexion et les pages d'invitation utilisent
aussi cette langue.

Les formats de nombre, de date et de devise sont un réglage séparé
(**Région** et **Devise**), si bien qu'une association peut par exemple
utiliser des menus en anglais avec des formats de nombre allemands.

## Voir aussi {#related}

- [S'orienter dans l'application](navigation.md)
- [Rôles, groupes et droits](roles-and-permissions.md)
- [Utilisateurs et invitations](../administration/users.md) -- pour les administrateurs

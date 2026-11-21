# Sauvegarde et restauration {#backup-and-restore}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Une sauvegarde est une copie complète des données Parcella de votre
association dans un seul fichier. Avec elle, vous pouvez tout récupérer
après une panne de serveur, une erreur ou un déménagement vers un
nouvel hébergeur. Faites des sauvegardes régulièrement, et conservez-les
ailleurs que sur le serveur Parcella.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Tout commence depuis **Administration →
    Système**.

## Ce que contient une sauvegarde {#what-a-backup-contains}

Un fichier `.zip` avec :

- toute la base de données -- chaque membre, parcelle, relevé, facture,
  paramètre et compte utilisateur,
- les fichiers téléversés conservés dans Parcella : le logo, les images
  des annonces, les avatars et les fichiers des procédures,
- la clé que Parcella utilise pour chiffrer les mots de passe stockés
  (serveur de messagerie, site web, stockage cloud, helpdesk).

!!! warning "Traitez une sauvegarde comme un mot de passe"
    Comme elle contient cette clé et toutes les données personnelles de
    vos membres, quiconque possède le fichier peut tout lire.
    Conservez-la là où seul le bureau peut y accéder.

Les fichiers conservés dans votre stockage cloud (dossiers des
parcelles, pièces jointes des factures, fichiers de notes) ne font
**pas** partie de la sauvegarde -- ils se trouvent déjà dans le cloud,
qui a sa propre sauvegarde.

## Télécharger une sauvegarde {#download-a-backup}

Sur **Administration → Système**, la carte **Sauvegarde** a le bouton
**Télécharger la sauvegarde**. Votre navigateur télécharge immédiatement
le fichier zip. Rien n'est stocké sur le serveur : ce fichier est donc
la seule copie, enregistrez-le en lieu sûr.

En cas de problème, vous voyez **Échec de la sauvegarde :** suivi de la
raison.

## Restaurer depuis une sauvegarde {#restore-from-backup}

![Restaurer depuis une sauvegarde](../assets/screenshots/administration/backup-restore.png)

Ouvrez-la avec **Restaurer depuis une sauvegarde** sur la page Système.

!!! danger "Cela écrase toutes les données actuelles"
    La restauration remplace **toute** la base de données et tous les
    fichiers téléversés par le contenu de la sauvegarde. Tout ce qui a
    été saisi depuis cette sauvegarde est perdu, y compris les comptes
    utilisateurs et mots de passe créés depuis. C'est irréversible. Si
    vous risquez de vouloir revenir en arrière, **téléchargez d'abord
    une sauvegarde de l'état actuel**.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Fichier de sauvegarde (.zip)** | Choisissez un fichier de sauvegarde téléchargé depuis Parcella (200 Mo au maximum). |
| **Tapez RESTORE pour confirmer** | Tapez le mot `RESTORE` en majuscules. Cela évite une restauration par accident. |
| **Annuler** | Retour à la page Système. |
| **Restaurer** | Demande une dernière confirmation, puis restaure. Cela peut prendre un peu de temps. |

Ensuite, vous voyez **Restauration terminée avec succès.** Tout le
monde -- vous compris -- travaille désormais avec les données telles
qu'elles étaient au moment de la sauvegarde ; vous devrez peut-être vous
reconnecter avec le mot de passe valable à ce moment-là.

Messages possibles :

| Message | Signification |
|---|---|
| **La phrase de confirmation ne correspond pas -- rien n'a été modifié.** | Le mot n'était pas exactement `RESTORE`. |
| **Le fichier est trop volumineux.** | Plus de 200 Mo. |
| **Le fichier de sauvegarde a une structure inattendue : ...** | Pas une sauvegarde Parcella, ou un fichier endommagé. Rien n'a été modifié. |
| **Échec de la restauration, rien n'a été modifié : ...** | La restauration de la base de données a échoué et vos données sont comme avant. |
| **Base de données restaurée avec succès, mais la restauration des fichiers téléversés a échoué : ...** | Les données sont restaurées mais certains fichiers non. Relancer la restauration est sans risque. |

Les sauvegardes d'une version plus ancienne de Parcella peuvent être
restaurées dans une version plus récente ; la personne qui gère le
serveur devra peut-être lancer ensuite la mise à jour de la base de
données.
<!-- TODO(verify): whether the app applies pending database migrations by itself after a restore of an older backup, or whether the server admin must always run them (developer docs say a restore doesn't run them). -->

## Sauvegardes cloud {#cloud-backups}

![Sauvegardes cloud](../assets/screenshots/administration/backup-cloud.png)

Ouvrez-la avec **Sauvegardes cloud** sur la page Système. Parcella peut
faire automatiquement la même sauvegarde et la téléverser dans votre
stockage cloud.

Cela nécessite que le module **Stockage cloud** soit activé et qu'un
stockage soit configuré sous [Intégrations](integrations.md#cloud-storage).
Sinon, la page vous indique ce qui manque, avec un lien.

### Planification {#schedule}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Sauvegarder automatiquement vers le cloud** | Active ou désactive les sauvegardes automatiques. |
| **Dossier de destination** | Dossier dans le stockage cloud, par ex. `backups/parcella`. Créé s'il n'existe pas. Choisissez un dossier que seul le bureau peut ouvrir -- chaque sauvegarde contient la clé des mots de passe stockés. |
| **Fréquence** | **Toutes les heures**, **Quotidienne** (par défaut), **Hebdomadaire** ou **Mensuelle**. |
| **Nombre de sauvegardes à conserver** | Combien de sauvegardes garder, au moins 1 (10 par défaut). Quand une nouvelle est ajoutée, les plus anciennes au-delà de ce nombre sont supprimées. Seuls les fichiers de sauvegarde de Parcella sont concernés. |
| **Enregistrer** | Enregistre la planification (**Enregistré.**). |
| **Sauvegarder vers le cloud maintenant** | Crée et téléverse immédiatement une sauvegarde, que les sauvegardes automatiques soient activées ou non. |

Sous les champs, vous voyez le résultat de la dernière exécution :
**Dernière sauvegarde cloud : ... (réussie).**, **... -- échec :** avec
la raison, ou **Aucune sauvegarde cloud n'a encore été effectuée.**
Vérifiez-le de temps en temps -- une sauvegarde qui échoue en silence
pendant des semaines n'est pas une sauvegarde.

### Sauvegardes dans le cloud {#backups-in-the-cloud}

Une liste des sauvegardes du dossier de destination, les plus récentes
en premier, avec **Nom**, **Taille** et **Dernière modification**.
**Aucune sauvegarde dans ce dossier pour l'instant.** s'il n'y en a
aucune.

Pour en restaurer une, tapez `RESTORE` dans le champ de sa ligne et
cliquez sur **Restaurer**. Le même avertissement que ci-dessus
s'applique : cela écrase toutes les données actuelles.

## Bonnes pratiques {#good-practice}

- Téléchargez une sauvegarde avant de gros changements : une mise à
  jour, un import important, une série de factures.
- Gardez aussi au moins une copie en dehors du stockage cloud, par ex.
  sur une clé USB chiffrée dans le coffre de l'association.
- De temps en temps, testez une sauvegarde en la restaurant sur une
  installation de test séparée. Une sauvegarde que vous n'avez jamais
  restaurée n'est qu'un espoir.

## Voir aussi {#related}

- [Informations système et mises à jour](system.md)
- [Intégrations](integrations.md#cloud-storage)

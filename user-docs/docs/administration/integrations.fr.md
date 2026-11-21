# Intégrations {#integrations}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les intégrations relient Parcella aux autres systèmes qu'utilise votre
association : le site web de l'association, un stockage cloud, un
helpdesk, Nextcloud Deck et les applications de calendrier.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Intégrations**.

![Intégrations](../assets/screenshots/administration/integrations.png)

La page est une colonne de cartes, chacune repliée ; cliquez sur un
titre pour l'ouvrir. Chaque carte s'enregistre séparément avec son
propre bouton.

La plupart des intégrations nécessitent aussi qu'un module soit activé
sous [Activer et désactiver les modules](modules.md). Les cartes vous
indiquent quand il manque.

!!! note "Le serveur e-mail est ailleurs"
    Le serveur de messagerie sortant (SMTP) se règle dans les
    [Paramètres de l'association](settings.md#email-smtp), pas ici.

## Flux de calendrier privés {#private-calendar-feeds}

Le module calendrier propose des liens d'abonnement (flux de calendrier)
pour la liste des anniversaires et pour la présence et l'absence du
bureau, afin que les membres du bureau puissent les voir dans
l'application calendrier de leur téléphone. Ces liens contiennent un
secret commun et n'expirent jamais.

| Bouton | Ce qu'il fait |
|---|---|
| **Régénérer** | Après confirmation, crée un nouveau secret. **Tous les abonnements existants à ces flux cessent de fonctionner** ; les abonnés doivent copier le nouveau lien depuis les pages du calendrier. Vous voyez **Jeton des flux de calendrier régénéré.** |

Faites-le quand un lien a pu tomber entre de mauvaises mains, ou quand
quelqu'un qui l'avait quitte le bureau. Voir
[Calendrier](../modules/calendar.md).

## API publique d'inscription {#public-signup-api}

Cette carte permet au site web de votre association de communiquer avec
Parcella : les jardiniers s'inscrivent aux sessions de travail,
envoient un message de contact ou posent leur candidature à une
parcelle via des formulaires du site web, sans connexion à Parcella.

Si le module **API publique d'inscription** est désactivé, un avis en
haut de la page l'indique, avec un lien **Activer dans les Paramètres**.
Un avis similaire apparaît dans la carte tant que l'**API publique de
formulaire de contact** est désactivée. Le formulaire de candidature à
une parcelle nécessite en plus l'interrupteur **API publique du
formulaire de candidature**.

Un site web peut envoyer ses formulaires de deux façons, et vous pouvez
utiliser les deux.

### Avec le jeton API (extension du site web sur le serveur) {#with-the-api-token-website-plugin-on-the-server}

Pour un site web disposant d'une extension côté serveur -- un
« connecteur » -- qui envoie elle-même les données du formulaire à
Parcella.

| Élément | Ce qu'il fait |
|---|---|
| **Jeton API** | Le secret dont l'extension a besoin. Cliquez dans le champ pour le sélectionner, puis copiez-le dans les réglages de l'extension. |
| **Régénérer** | Après confirmation, crée un nouveau jeton. **Toute extension utilisant encore l'ancien cesse immédiatement de fonctionner** ; saisissez le nouveau partout. Vous voyez *Un nouveau jeton API a été généré ...* |
| **Points d'accès** | Un tableau des adresses web utilisées par les extensions, chacune avec **Méthode**, **URL** et **Authentification** (**Aucune (lecture publique)**, le jeton API, ou **Adresses de sites autorisées**). Le contact technique de votre site web en a besoin ; pas vous. |

La carte se termine par une note indiquant qu'une extension WordPress
prête à l'emploi fait partie du projet Parcella.

### Formulaires du site web (HTML simple, extension WordPress) {#website-forms-plain-html-wordpress-plugin}

Pour les sites web dont les formulaires envoient les données directement
depuis le navigateur du visiteur vers Parcella : pages HTML simples sur
n'importe quel système de site web, et l'extension WordPress à partir de
la version 3.0. Aucun jeton n'intervient : Parcella n'accepte donc que
les formulaires provenant des sites que vous listez ici. Tant que la
liste est vide, ces formulaires sont fermés.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Adresses de sites autorisées** | Une adresse web par ligne, seulement le schéma et l'hôte, par ex. `https://example.org`. Listez chaque adresse à laquelle le site de votre association est joignable, y compris l'adresse propre du site WordPress. Les entrées qui ne sont pas des adresses web sont écartées et listées dans un avertissement. |
| **Exiger ALTCHA (preuve de travail contre les robots de spam)** | Le navigateur du visiteur doit résoudre un petit calcul avant qu'un formulaire soit accepté -- pas de cookies, pas d'entreprise externe, rien à cliquer pour le visiteur. Cela s'applique à **tous** les modes d'envoi, y compris les extensions utilisant le jeton API. Ne cochez cette case qu'une fois que tous les formulaires de votre site intègrent le widget ALTCHA, sinon chaque envoi est refusé. |
| **Enregistrer les adresses** | Enregistre les deux. Vous voyez **Adresses de sites autorisées enregistrées.** |

Ce que les jardiniers voient et reçoivent est décrit dans
[Pour les jardiniers](../gardeners/index.md).

## Site web (brouillons depuis les annonces) {#website-drafts-from-announcements}

Permet au module [Annonces](../modules/announcements.md) de créer en un
clic un brouillon d'article sur le site web de votre association.
Parcella ne crée jamais que des **brouillons** ; la publication reste
une décision que vous prenez dans votre système de site web.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Type de site** | **Aucun (pas de brouillons sur le site)**, **WordPress**, **Dossier Markdown (stockage cloud)** ou **Plugin Parcella (TYPO3, Contao, Drupal, Joomla, ...)**. En choisir un affiche ses champs. Un seul type est actif à la fois ; changer de type conserve les réglages de l'autre pour plus tard. |
| **Enregistrer** | Enregistre le type et ses champs. Vous voyez **Paramètres du site enregistrés**, ou une erreur expliquant ce qui manque. |
| **Tester la connexion** | Essaie la connexion avec ce qui figure actuellement dans le formulaire, sans enregistrer. Affiche **Connexion réussie** ou l'erreur. |

Les champs marqués * sont obligatoires. Les champs de mot de passe
indiquent si quelque chose est enregistré ; laissez-les vides pour le
conserver.

**WordPress**

| Champ | Ce qu'il faut saisir |
|---|---|
| **Adresse du site WordPress** * | L'adresse de votre site web. |
| **Nom d'utilisateur WordPress** * | L'utilisateur WordPress au nom duquel les brouillons sont créés. |
| **Mot de passe d'application** * | Pas le mot de passe WordPress habituel : créez un mot de passe d'application dans WordPress sous *Utilisateurs → Profil → Mots de passe d'application*. |

**Dossier Markdown (stockage cloud)** -- pour les sites web construits à
partir de fichiers texte (Hugo, Jekyll, Eleventy, Astro et similaires).
Chaque brouillon devient un fichier marqué comme brouillon dans un
dossier de votre [stockage cloud](#cloud-storage) ; supprimer la ligne
de brouillon le publie.

| Champ | Ce qu'il faut saisir |
|---|---|
| **Dossier des articles** * | Dossier du stockage cloud pour les articles, par ex. `website/content/posts`. Il doit déjà exister. |
| **Dossier des images** | Où vont les images, dans des sous-dossiers par année et par mois. Vide : articles sans images. |
| **Chemin web du dossier des images** | Comment le site web désigne le dossier des images, par ex. `/media`. |
| **Adresse du site** | Utilisée pour le QR code de l'avis imprimé une fois l'article publié. |
| **Modèle de nom de fichier** | `{date}` devient AAAAMMJJ, `{slug}` le titre sans trémas ni espaces. |
| **Modèle d'adresse d'article** | L'adresse web de l'article, écrite dans le fichier. Laissez vide si votre site web la calcule lui-même. |
| **Auteur** | Écrit dans chaque article. |
| **Catégories** | Séparées par des virgules, telles que votre site web les nomme. |

**Plugin Parcella** -- pour TYPO3, Contao, Drupal, Joomla et d'autres
systèmes où le plugin Parcella est installé. Les réglages du plugin
affichent les deux valeurs.

| Champ | Ce qu'il faut saisir |
|---|---|
| **Adresse du plugin** * | Par ex. `https://example.org/parcella/v1`. |
| **Clé partagée** * | Générée par le plugin. |

## Stockage cloud {#cloud-storage}

Le titre est **Stockage cloud (documents des parcelles, factures,
sauvegardes)**. Il détermine où Parcella conserve les fichiers : un
dossier par parcelle (baux, documents), factures reçues, documents des
contacts, notes, fichiers des procédures, sauvegardes et le site web
Markdown. Qui d'autre peut voir un dossier se gère dans le stockage
lui-même, pas dans Parcella.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Type de stockage** | **Aucun (pas de stockage cloud)**, **Nextcloud**, **WebDAV (ownCloud, Seafile, HiDrive, Storage Box, ...)** ou **Compatible S3 (AWS, Hetzner, MinIO, Wasabi, ...)**. Un seul est actif à la fois. Les chemins de dossiers saisis ailleurs dans Parcella sont relatifs au stockage choisi. |
| **Enregistrer**, **Tester la connexion** | Comme sur la carte du site web. |

| Stockage | Champs |
|---|---|
| **Nextcloud** | **Adresse Nextcloud** *, **Nom d'utilisateur Nextcloud** *, **Mot de passe d'application** * -- créez un mot de passe d'application dans Nextcloud sous *Paramètres → Sécurité → Appareils & sessions* ; n'utilisez pas le mot de passe habituel. |
| **WebDAV** | **Adresse WebDAV** * (l'adresse complète du dossier dans lequel Parcella doit travailler, telle que votre fournisseur la documente), **Nom d'utilisateur** *, **Mot de passe** *. |
| **Compatible S3** | **Point de terminaison** *, **Région** * (laissez `us-east-1` si votre fournisseur n'a pas de régions), **Bucket** *, **ID de clé d'accès** *, **Clé d'accès secrète** *, **Chemin dans le bucket** (sous-dossier facultatif pour tous les fichiers de Parcella). |

Le stockage n'est utilisé qu'une fois le module **Stockage cloud**
activé. La carte affiche alors aussi les dossiers ci-dessous. Chacun a
un champ de chemin (relatif au stockage) et un bouton **Enregistrer** ;
laissez un chemin vide pour désactiver cet usage.

| Dossier | Utilisé pour |
|---|---|
| **Dossier des factures reçues** | Les pièces jointes des [factures reçues](../modules/finances/incoming-invoices.md) vont dans ce dossier commun unique. |
| **Dossier des documents des contacts externes** | Un dossier de base avec un sous-dossier par [contact externe](../modules/external-contacts.md), que vous créez dans le stockage. Chaque contact choisit ensuite son sous-dossier. Vide : la section des documents est masquée. |
| **Dossier des annonces imprimées** | Chaque PDF d'impression d'une [annonce](../modules/announcements.md) est aussi enregistré ici. **Parcourir** vous permet de naviguer dans le stockage et d'**utiliser** un dossier. Vide : téléchargement uniquement. |
| **Dossier des notes** | Les [notes](../modules/notes.md) y sont conservées sous forme de fichiers texte, et les modifications faites à ces fichiers dans le cloud apparaissent dans Parcella. Les sous-dossiers deviennent des catégories de notes. Vide : les notes ne vivent que dans Parcella. |
| **Dossier des fichiers de procédure** | Les fichiers téléversés dans une [procédure](../modules/processes.md), un sous-dossier par procédure. Vide : conservés dans Parcella. Les fichiers déjà téléversés restent où ils sont. |

Le dossier des sauvegardes automatiques se règle sur la page
[Sauvegardes cloud](backup.md#cloud-backups).

## Assistance / helpdesk {#support-helpdesk}

Connecte le helpdesk dans lequel votre association répond aux demandes.
Parcella relie alors ses conversations aux membres, aux parcelles et au
tableau des tâches (voir [Assistance](../modules/support.md)), et le
formulaire de contact du site web y crée de nouvelles demandes.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Helpdesk** | **Aucun (pas de helpdesk)**, **FreeScout**, **Zammad**, **Znuny / OTRS**, **osTicket**, **Zendesk** ou **Freshdesk**. Un seul est actif à la fois ; si vous revenez plus tard à un helpdesk, ses conversations reviennent aussi. Chaque choix affiche une courte note sur ce qui fonctionne avec lui. |
| **Enregistrer**, **Tester la connexion** | Comme sur la carte du site web. |

| Helpdesk | Champs | Remarques |
|---|---|---|
| **FreeScout** | **Adresse FreeScout** *, **Clé API** *, **ID de la boîte** (1 par défaut) | Tout fonctionne. Nécessite le module *API & Webhooks* de FreeScout. |
| **Zammad** | **Adresse Zammad** *, **Jeton d'accès** *, **Groupe pour les nouvelles demandes** * | Tout fonctionne. |
| **Znuny / OTRS** | **Adresse du service web** *, **Identifiant de l'agent** *, **Mot de passe** *, **File pour les nouvelles demandes** *, **Adresse de l'interface agent** | Pas de renommage des clients. Un service web Parcella doit être importé une fois dans Znuny. |
| **osTicket** | **Adresse osTicket** *, **Clé API** * | Seul le formulaire de contact du site web fonctionne ; la lecture et les réponses se font dans osTicket. |
| **Zendesk** | **Adresse Zendesk** *, **E-mail de l'agent** *, **Jeton API** * | Tout fonctionne. |
| **Freshdesk** | **Adresse Freshdesk** *, **Clé API** * | Tout fonctionne. |

L'indication sous chaque champ dit où trouver la clé ou le jeton dans
votre helpdesk. Activez aussi le module **Assistance (helpdesk)**.

## Nextcloud Deck {#nextcloud-deck}

Copie les cartes d'un tableau Nextcloud Deck sur le
[tableau des tâches](../modules/tasks.md) de Parcella -- dans un seul
sens, en lecture seule, tenues à jour automatiquement. C'est une
connexion distincte du stockage cloud ci-dessus, même quand les deux
utilisent le même Nextcloud.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **URL du serveur Nextcloud** | Par ex. `https://cloud.example.com`. |
| **Nom d'utilisateur Nextcloud** | |
| **Mot de passe d'application Nextcloud** | Créez-en un dans Nextcloud sous *Paramètres personnels → Sécurité*. Laissez vide pour conserver celui qui est enregistré. |
| **ID du tableau Deck** | Le nombre à la fin de l'adresse web du tableau (`.../apps/deck/board/3` → `3`). Coller l'adresse complète fonctionne aussi. |
| **Enregistrer** | Enregistre la connexion (**Paramètres Deck enregistrés**). |
| **Tester la connexion** | Vérifie la connexion avec ce qui figure dans le formulaire. |
| **Synchroniser maintenant** | Affiché une fois un ID de tableau enregistré. Copie les cartes immédiatement au lieu d'attendre. À côté : combien de tâches ont été synchronisées et quand, ou **Pas encore synchronisé**. |

Activez aussi le module **Synchronisation Nextcloud Deck**.

## Voir aussi {#related}

- [Activer et désactiver les modules](modules.md)
- [Sauvegarde et restauration](backup.md)
- [Pour les jardiniers](../gardeners/index.md) -- à quoi ressemblent les formulaires du site web de l'autre côté

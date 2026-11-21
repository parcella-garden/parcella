# Configurer une nouvelle association {#setting-up-a-new-club}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Parcella est installé et fonctionne. Ce guide vous mène de la toute
première connexion à une installation avec laquelle tout le bureau peut
travailler : un mot de passe administrateur sûr, les coordonnées et le
logo de votre association, la bonne langue, uniquement les modules dont
vous avez besoin, des comptes pour les autres membres du bureau, et --
si vous le souhaitez -- d'abord un tour d'essai avec des données
d'exemple.

Comptez environ une heure. Vous avez besoin du compte administrateur
fourni avec l'installation.

!!! info "Qui peut le faire"
    Tout se passe ici dans **Administration**, que seuls les
    administrateurs (et les groupes avec **Accès au panneau
    d'administration**) peuvent ouvrir. Voir
    [Rôles, groupes et droits](../getting-started/roles-and-permissions.md).

## 1. Se connecter et changer le mot de passe administrateur {#1-log-in-and-change-the-admin-password}

1. Ouvrez Parcella dans votre navigateur et connectez-vous avec le
   compte administrateur de l'installation.
   <!-- TODO(verify): the default login (admin@parcella.local / admin1234) is documented for developers; confirm whether self-hosters get the same default or set their own during installation before naming it here. -->
2. Si le compte utilise encore le mot de passe par défaut de
   l'installation, Parcella ouvre immédiatement **Changer le mot de
   passe** et affiche : *« Ce compte utilise encore le mot de passe par
   défaut de l'installation initiale. Veuillez en choisir un nouveau --
   le reste de l'application reste verrouillé jusque-là. »*
3. Saisissez le **Mot de passe actuel**, puis un **Nouveau mot de passe**
   et **Confirmer le nouveau mot de passe**, et cliquez sur **Changer le
   mot de passe**.

Vous pouvez changer à nouveau votre mot de passe à tout moment depuis le
menu utilisateur en bas de la barre latérale : **Changer le mot de
passe**.

!!! warning
    Ne sautez pas cette étape sur une installation accessible depuis
    internet. Sinon, toute personne connaissant le mot de passe par
    défaut pourrait se connecter en tant qu'administrateur.

Plus d'informations : [Première connexion et votre compte](../getting-started/first-login.md).

## 2. Saisir les coordonnées de votre association {#2-enter-your-clubs-details}

1. Dans la barre latérale, ouvrez **Administration → Paramètres**. La
   page s'appelle **Paramètres du club**.
2. Dans la carte **Données du club**, renseignez **Nom du club**,
   **Rue**, **Code postal**, **Ville**, **Numéro d'enregistrement du
   club** et **Registre du commerce**. Le nom apparaît dans les titres
   des pages ; le reste va dans le pied de page des courriers et des
   factures.
3. Dans **Membres du bureau**, recherchez et cochez les membres qui font
   actuellement partie du bureau. Vous ne pouvez choisir que des
   personnes qui existent déjà comme membres -- revenez-y après l'étape 9
   ou après votre [import](csv-import.md).
4. Sous **Superficies (m²)**, saisissez la **Superficie totale (m²)** du
   terrain et la **Superficie C (municipale, m²)** si vous en avez une.
   **Superficie A (parcelles, m²)** et **Superficie B (communale, m²)**
   sont calculées par Parcella à partir de vos parcelles.
5. Cliquez sur **Enregistrer les paramètres**. Vous voyez *« Paramètres
   enregistrés. »*

!!! tip
    La page des paramètres est longue. Utilisez le champ
    **Rechercher dans les paramètres...** en haut pour aller directement
    à un champ par son nom.

## 3. Ajouter votre logo {#3-add-your-logo}

1. Toujours sur **Administration → Paramètres**, trouvez la carte
   **Image de marque**.
2. Sous **Logo du club**, choisissez un fichier PNG, JPEG, WebP ou SVG
   de 2 Mo au maximum.
3. Cliquez sur **Enregistrer les paramètres**.

Le logo remplace celui de Parcella sur la page de connexion et dans la
barre latérale. Pour revenir au logo par défaut, cochez **Supprimer le
logo (revenir à l'icône par défaut)** et enregistrez.

## 4. Choisir la langue, la région et la devise {#4-choose-language-region-and-currency}

Ce sont volontairement trois réglages distincts : une association peut
par exemple utiliser l'interface en anglais avec les formats de nombre
et d'adresse allemands.

1. **Langue** -- la langue de toute l'installation. Chaque utilisateur
   voit la même.
2. **Région** -- format des nombres et des adresses (séparateur de
   milliers, ordre du code postal et de la ville).
3. **Devise** -- le symbole et sa position (« 19,99 € » ou « £19.99 »).
4. Cliquez sur **Enregistrer les paramètres**.

## 5. Configurer l'envoi des e-mails {#5-set-up-outgoing-email}

Parcella envoie les invitations, notifications, annonces et factures par
e-mail. Sans serveur de messagerie, les invitations de l'étape 9 ne
peuvent pas partir.

1. Sur **Administration → Paramètres**, trouvez la carte
   **E-mail (SMTP)**.
2. Renseignez **Serveur SMTP**, **Port SMTP**, **Utilisateur SMTP**,
   **Mot de passe SMTP** et **E-mail de l'expéditeur** -- votre
   fournisseur de messagerie vous donne ces valeurs.
3. Cliquez sur **Enregistrer les paramètres**.

Après l'enregistrement, le champ du mot de passe indique seulement
qu'un mot de passe est défini ; pour le changer, tapez-en un nouveau.

## 6. Activer et désactiver les modules {#6-turn-modules-on-and-off}

Toutes les associations n'utilisent pas tous les domaines fonctionnels.
En désactiver un le masque de la navigation ; ses données restent et
reviennent quand vous le réactivez.

1. Sur **Administration → Paramètres**, trouvez la carte **Domaines
   fonctionnels**.
2. Cochez les modules qu'utilise votre association et décochez les
   autres. Chacun a une courte description en dessous.
3. Cliquez sur **Enregistrer les paramètres**.

Quelques modules sont **désactivés** sur une nouvelle installation car
ils envoient des données à l'extérieur ou ouvrent quelque chose au
public : **Finances**, **Annonces**, **Stockage cloud**,
**Assistance (helpdesk)**, **Synchronisation Nextcloud Deck**,
**Connecteur MCP pour clients IA** et les trois API publiques du site
web. Ne les activez qu'une fois que vous en avez besoin.

Plus d'informations : [Activer et désactiver les modules](../administration/modules.md).

## 7. Faire des essais avec des données d'exemple (facultatif) {#7-try-things-out-with-sample-data-optional}

Avant de saisir des données réelles, vous pouvez remplir l'installation
vide avec des membres, parcelles, compteurs, sessions de travail et
autres fictifs, cliquer partout, puis tout supprimer.

1. Ouvrez **Administration → Données d'exemple**.
2. Lisez **Ce qui est ajouté**, puis cliquez sur **Ajouter des données
   d'exemple** et confirmez.
3. Explorez les modules. Essayez une série de factures, saisissez un
   relevé de compteur, transmettez une parcelle.
4. Quand vous avez terminé, revenez sur **Administration → Données
   d'exemple** et cliquez sur **Supprimer toutes les données
   d'exemple**, puis confirmez.

!!! warning "Supprimez les données d'exemple avant de commencer pour de vrai"
    - Les données d'exemple ne peuvent être **ajoutées** qu'à une
      nouvelle installation. Dès qu'un vrai membre ou une vraie parcelle
      existe, le bouton est bloqué.
    - **Supprimer toutes les données d'exemple** supprime exactement ce
      que le générateur a créé et rien de ce que vous avez saisi
      vous-même. Ce que vous rattachez *à* un enregistrement d'exemple
      pendant vos essais (un relevé sur un compteur d'exemple, un
      paiement sur une facture d'exemple) risque de ne pas disparaître
      proprement. Supprimez d'abord les données d'exemple, puis saisissez
      vos données réelles.
      <!-- TODO(verify): what happens on removal if a real record references a sample record (e.g. a finalized invoice run built from sample parcels)? -->
    - Les données d'exemple ne créent ni ne modifient aucun compte
      utilisateur.

Plus d'informations : [Données d'exemple](../administration/sample-data.md).

## 8. Créer des groupes {#8-create-groups}

Les nouveaux comptes utilisateurs reçoivent leurs accès par des
**groupes**, pas par un rôle fixe. Créez d'abord les groupes, puis
invitez les personnes dedans.

1. Ouvrez **Administration → Groupes**.
2. Sous **Créer un groupe**, saisissez un **Nom** (par exemple
   « Bureau ») et une **Description**.
3. Pour le bureau, cochez **Accès complet à chaque module**. Ne cochez
   **Accès au panneau d'administration** que pour les personnes qui
   doivent aussi gérer les utilisateurs et les paramètres.
4. Cliquez sur **Créer un groupe**.
5. Pour des fonctions plus restreintes, créez d'autres groupes et, dans
   le tableau des droits, cochez **Lecture**, **Écriture** et
   **Suppression** par **Module** -- par exemple « Équipe eau » avec
   lecture et écriture sur **Eau**, ou « Trésorier » avec tous les droits
   sur **Finances**. Cliquez sur **Enregistrer**.

!!! tip
    Toute personne pouvant se connecter peut toujours *consulter* les
    membres et les parcelles. Les groupes élargissent l'accès à partir
    de là ; ils ne le retirent jamais.

Plus d'informations : [Groupes](../administration/groups.md) et
[Rôles, groupes et droits](../getting-started/roles-and-permissions.md).

## 9. Inviter les autres membres du bureau {#9-invite-the-other-board-members}

1. Ouvrez **Administration → Utilisateurs** (la page s'appelle
   **Gestion des utilisateurs**).
2. Dans **Inviter un utilisateur**, saisissez l'**Adresse e-mail** de la
   personne et cochez ses **Groupes**.
3. Cliquez sur **Envoyer l'invitation**.
4. La personne reçoit un e-mail avec un lien. Sur **Configurer votre
   compte**, elle saisit son **Nom** et un **Mot de passe** (au moins
   8 caractères) et clique sur **Créer un compte**.

L'invitation est valable 7 jours et apparaît sous **Invitations en
attente** jusqu'à son acceptation. De là, vous pouvez **Renvoyer
l'invitation** (ce qui la prolonge aussi) ou **Supprimer
l'invitation**.

!!! warning
    L'invitation part par e-mail : configurez donc d'abord
    **E-mail (SMTP)** (étape 5). Si elle ne peut pas être envoyée, la
    page l'indique ; corrigez les paramètres e-mail et utilisez
    **Renvoyer l'invitation**.

Plus d'informations : [Utilisateurs et invitations](../administration/users.md).

## 10. Connecter un stockage cloud (facultatif) {#10-connect-cloud-storage-optional}

Si votre association conserve les contrats de bail et autres documents
dans Nextcloud (ou un autre stockage pris en charge), Parcella peut
afficher un dossier de documents sur la page de chaque parcelle.

1. Ouvrez **Administration → Intégrations** et trouvez **Stockage cloud
   (documents des parcelles, factures, sauvegardes)**.
2. Choisissez le **Type de stockage** et saisissez les informations de
   connexion demandées. Cliquez sur **Enregistrer**, puis sur **Tester
   la connexion**.
3. Réglez éventuellement les dossiers communs plus bas : **Dossier des
   factures reçues**, **Dossier des documents des contacts externes**,
   **Dossier des notes**, **Dossier des fichiers de procédure**,
   **Dossier des annonces imprimées**.
4. Allez dans **Administration → Paramètres → Domaines fonctionnels**,
   cochez **Stockage cloud** et cliquez sur **Enregistrer les
   paramètres**.
5. Sur la page de chaque parcelle, renseignez le **Chemin du dossier**
   dans **Documents (stockage cloud)** -- tapez-le ou utilisez
   **Parcourir…** -- et cliquez sur **Enregistrer**.

Les chemins sont toujours relatifs au stockage choisi. Parcella ne crée
ni ne partage les dossiers pour vous ; faites-le d'abord dans votre
cloud.

Plus d'informations : [Intégrations](../administration/integrations.md).

## 11. Saisir ou importer vos données réelles {#11-enter-or-import-your-real-data}

Ajoutez maintenant vos parcelles et vos membres -- à la main sous
**Parcelles → Nouvelle parcelle** et **Membres → Nouveau membre**, ou
en une fois depuis un tableur : voir
[Importer des membres et des parcelles](csv-import.md). Attribuez
ensuite chaque membre à sa parcelle (voir
[Accueillir un nouveau membre](new-member.md), étape 6).

## 12. Faire votre première sauvegarde {#12-make-your-first-backup}

1. Ouvrez **Administration → Utilisateurs** et trouvez la carte
   **Sauvegarde**.
2. Cliquez sur **Télécharger la sauvegarde** et conservez le fichier zip
   en lieu sûr.

La sauvegarde contient la base de données, les fichiers téléversés et la
clé de chiffrement. Traitez-la comme la liste des membres elle-même.

Plus d'informations : [Sauvegarde et restauration](../administration/backup.md).

## Voir aussi {#related}

- [Paramètres de l'association](../administration/settings.md)
- [Activer et désactiver les modules](../administration/modules.md)
- [Utilisateurs et invitations](../administration/users.md)
- [Groupes](../administration/groups.md)
- [Intégrations](../administration/integrations.md)
- [Données d'exemple](../administration/sample-data.md)
- [Sauvegarde et restauration](../administration/backup.md)
- [Importer des membres et des parcelles](csv-import.md)

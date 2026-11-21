# Accueillir un nouveau membre {#welcoming-a-new-member}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Quelqu'un demande un jardin, se voit proposer une parcelle, dit oui --
et devient membre et locataire. Ce guide suit ce parcours dans
Parcella, de la candidature à l'accueil.

Il y a deux façons de faire de quelqu'un un membre :

- **À partir d'une candidature** (étapes 1 à 6) : la personne est sur
  votre [liste d'attente](../glossary.md#applicant) dans **Candidats**.
  **Attribuer une parcelle** crée alors en une seule fois la fiche
  membre, le [bail](../glossary.md#tenancy) et l'adresse de facturation.
  C'est la voie habituelle.
- **À la main** (étape 7) : pour quelqu'un qui n'est jamais passé par la
  liste d'attente, ou une parcelle qui n'est pas résiliée.

!!! info "Qui peut le faire"
    Travailler sur les candidatures nécessite le droit d'**écriture** sur
    **Candidats** ; attribuer la parcelle nécessite aussi l'**écriture**
    sur **Membres et parcelles**. Les membres du bureau et les
    administrateurs ont les deux. Le module **Candidats** est activé par
    défaut.

## 1. La candidature arrive {#1-the-application-comes-in}

Les candidatures arrivent de deux façons :

- **Depuis votre site web**, si l'association y a le formulaire de
  candidature et que l'**API publique du formulaire de candidature** est
  activée (voir [Intégrations](../administration/integrations.md)). Elles
  apparaissent d'elles-mêmes.
- **À la main**, pour les candidatures par téléphone, par courrier ou en
  personne : ouvrez **Candidats**, cliquez sur **Nouveau candidat**,
  renseignez au moins l'**Adresse e-mail** (le seul champ obligatoire),
  plus **Prénom**, **Nom**, **Téléphone**, **Message du candidat** et une
  **Note du bureau** si vous le souhaitez, et cliquez sur
  **Enregistrer**.

Pour saisir une ancienne candidature venant d'une liste d'attente
papier, réglez **Candidature** sur la date d'origine. La date de
candidature détermine l'ordre de la liste d'attente.

Les nouvelles candidatures affichent un compteur à côté de **Candidats**
dans la barre latérale et sur le tableau de bord, jusqu'à ce que
quelqu'un les ait fait avancer.

!!! tip "Alerte"
    Si le nom, l'e-mail ou le téléphone d'un candidat correspond à un
    contact externe portant votre étiquette d'alerte, la liste et la page
    du candidat affichent un avertissement **Alerte**. Voir
    [Candidats](../modules/applicants.md).

## 2. Prendre contact {#2-get-in-touch}

1. Ouvrez **Candidats** et cliquez sur la nouvelle candidature.
2. Dans l'encadré **Contacter le candidat**, vérifiez et modifiez le
   texte de l'e-mail. L'objet est *« Merci de vous être inscrit(e) sur
   notre liste d'attente ! »*.
3. Cliquez sur **Envoyer** et confirmez.

Parcella envoie le texte par e-mail au candidat et passe le statut à
**Contacté**. L'encadré n'apparaît que tant que le statut est
**Nouveau**. Si vous avez pris contact autrement, changez simplement le
statut à la main (étape suivante).

Le texte par défaut de cet e-mail peut être modifié sous
**Administration → Paramètres → Candidats → Texte de l'e-mail aux
nouveaux candidats**.

## 3. Suivre le statut de la candidature {#3-track-the-applications-status}

Au fil de l'avancement, ouvrez la candidature, choisissez le nouveau
**Statut** et cliquez sur **Enregistrer** :

| Statut | Signification |
|---|---|
| **Nouveau** | Vient d'arriver. |
| **Contacté** | Vous avez pris contact ; le candidat est sur la liste d'attente. |
| **Parcelle proposée** | Vous avez proposé une parcelle précise. |
| **Acceptée** | Le candidat veut la parcelle ; la remise est en cours d'organisation. |
| **Refusée** | Plus d'offres. |
| **Clôturée (parcelle attribuée)** | Défini automatiquement par **Attribuer une parcelle** (étape 5). |

Si un candidat refuse une parcelle mais veut rester sur la liste,
repassez-le à **Contacté**. Chaque changement de statut est listé sous
**Historique du statut** sur la page de la candidature.

## 4. S'assurer que la parcelle est résiliée {#4-make-sure-the-parcel-is-terminated}

**Attribuer une parcelle** ne propose que des parcelles au statut
**résilié** -- la parcelle que quelqu'un a quittée ou va quitter.

1. Ouvrez la parcelle sous **Parcelles** et cliquez sur **Modifier**.
2. Réglez **Statut** sur **résilié**, ajoutez éventuellement une **Note
   de résiliation**, et cliquez sur **Enregistrer les modifications**.

Si le locataire sortant est encore en train de partir, voir
[Transmettre une parcelle](parcel-handover.md) -- ce guide couvre toute
la transmission, y compris côté ancien locataire.

## 5. Attribuer la parcelle {#5-assign-the-parcel}

1. Ouvrez la candidature et cliquez sur **Attribuer une parcelle**. (Le
   bouton est présent pour chaque candidature ouverte -- **Nouveau**,
   **Contacté**, **Parcelle proposée** ou **Acceptée**.)
2. Choisissez la **Parcelle résiliée**. La liste affiche chaque parcelle
   avec ses locataires actuels.
3. Fixez la **Date de remise** -- le jour où le nouveau locataire prend
   possession. Elle peut être dans le futur.
4. Cochez éventuellement **Autres candidats (co-locataires)** -- par
   exemple un conjoint qui a postulé séparément et reprend la parcelle
   avec ce candidat.
5. Saisissez éventuellement le **Dossier de documents pour les nouveaux
   locataires** (affiché seulement si vous pouvez gérer les dossiers
   cloud).
6. Cliquez sur **Aperçu**.
7. Vérifiez l'encadré **Remise de la parcelle … le …** :
    - **Anciens locataires** : leur bail se termine à la date de remise.
      S'ils n'ont pas d'autre parcelle, leur adhésion se termine la
      veille.
    - **Nouveaux locataires et destinataires des factures** : chaque
      candidat soit **devient un nouveau membre** (nom, e-mail et
      téléphone repris de la candidature), soit, si un membre actif
      utilise déjà la même adresse e-mail, est relié à ce membre
      existant.
8. Cliquez sur **Remettre la parcelle** et confirmez.

Ce qui se passe en une étape :

- Les candidats deviennent membres, avec **Membre depuis** fixé à la
  date de remise.
- Ils deviennent locataires de la parcelle à partir de la date de
  remise, avec **Utiliser comme adresse de facturation** coché.
- Les anciens locataires deviennent d'anciens locataires --
  l'historique reste sur la page de la parcelle.
- Le statut de la parcelle repasse à **actif**.
- Les candidatures passent à **Clôturée (parcelle attribuée)**.

Avec une date de remise dans le futur, les anciens locataires restent
locataires, membres et destinataires des factures jusqu'à ce jour ; les
nouveaux sont affichés comme à venir (« à partir du … ») sur la page de
la parcelle et prennent le relais à la date prévue.

## 6. Compléter la fiche du nouveau membre {#6-complete-the-new-members-record}

La remise ne copie que le nom, l'e-mail et le téléphone. Complétez le
reste :

1. Ouvrez **Membres** et cliquez sur le nouveau membre (ou suivez le
   lien depuis la page de la parcelle).
2. Cliquez sur **Modifier** et ajoutez **Date de naissance**, **IBAN**,
   l'adresse (**Rue et numéro**, **Code postal**, **Ville**).
3. Vérifiez **Peut recevoir des informations par e-mail**. C'est coché
   pour les membres créés par **Attribuer une parcelle**, puisque le
   candidat a donné une adresse e-mail ; décochez-le si le membre ne
   veut que du papier. Sans cela, les factures et les annonces vont dans
   la pile à imprimer au lieu de la boîte de réception.
4. Sous **Étiquettes**, cochez des étiquettes existantes ou tapez-en de
   nouvelles (par exemple « équipe haies »), séparées par des virgules.
5. Cliquez sur **Enregistrer les modifications**.

Vous pouvez aussi ajouter des étiquettes directement sur la page du
membre, dans la carte **Étiquettes**, avec **Ajouter une étiquette**.

## 7. Sans candidature : créer le membre à la main {#7-without-an-application-create-the-member-by-hand}

1. Ouvrez **Membres** et cliquez sur **Nouveau membre**.
2. Renseignez **Prénom** et **Nom** (obligatoires), l'adresse, **Date de
   naissance**, **IBAN**, **Membre depuis**, une **Adresse e-mail** et un
   **Numéro de téléphone**, **Peut recevoir des informations par
   e-mail** et d'éventuelles **Étiquettes**.
3. Cliquez sur **Créer un membre**.
4. Sur la page du membre, dans **Parcelles attribuées**, choisissez la
   parcelle sous **Choisir une parcelle…**, laissez **Utiliser comme
   adresse de facturation** coché si ce membre doit recevoir les
   factures de la parcelle, et cliquez sur **Attribuer**.

Vous pouvez aussi attribuer depuis la page de la parcelle :
**Locataires actuels → Choisir un membre… → Attribuer**, où vous pouvez
aussi saisir la date de début. Pour corriger la date de début plus tard,
utilisez l'icône crayon à côté du locataire sur la page de la parcelle
(**Modifier la location**, champ **Locataire depuis**).

Si un ancien locataire est encore sur la parcelle, terminez d'abord son
bail -- voir [Transmettre une parcelle](parcel-handover.md).

## 8. Accueillir le nouveau membre {#8-welcome-the-new-member}

Parcella n'a pas d'e-mail de bienvenue automatique. Deux choses aident :

**Une procédure pour l'accueil.** Le module **Procédures** comprend un
modèle d'exemple, **Accueil d'un nouveau membre**, en trois étapes :
**Accueil** (**Entretien d'accueil**, **Statuts et règlement remis**),
**Papiers** (**Bulletin d'adhésion signé**, **Mandat de prélèvement
reçu**) et **Finalisation** (**Ajouté à la liste de diffusion**,
**Notes**).

1. Une fois : ouvrez **Procédures → Modèles**, et sous **Partir d'un
   exemple** cliquez sur **Utiliser** à côté de **Accueil d'un nouveau
   membre**. Adaptez les étapes et les champs si vous le souhaitez.
   (Créer des modèles nécessite l'accès complet.)
2. Pour chaque nouveau membre : sur la page du membre, dans la carte
   **Procédures**, cliquez sur **Démarrer une procédure**, choisissez le
   **Modèle** et cliquez sur **Démarrer**.
3. Remplissez les champs au fur et à mesure et cliquez sur **Fait --
   étape suivante**. Les champs obligatoires doivent être remplis avant
   de pouvoir avancer.

**Un message personnel.** Avec le module **Annonces** activé, cochez le
nouveau membre dans la liste **Membres** et cliquez sur **Écrire à la
sélection**.

## Voir aussi {#related}

- [Candidats](../modules/applicants.md)
- [Membres](../modules/members.md)
- [Parcelles](../modules/parcels.md)
- [Procédures](../modules/processes.md)
- [Annonces](../modules/announcements.md)
- [Transmettre une parcelle](parcel-handover.md)
- Glossaire : [candidat](../glossary.md#applicant),
  [bail](../glossary.md#tenancy),
  [adresse de facturation](../glossary.md#invoice-address)

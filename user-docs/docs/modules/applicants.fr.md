# Candidats {#applicants}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

La liste des candidats est la liste d'attente de votre association pour
les parcelles libres. Les candidatures du formulaire de votre site web
arrivent ici d'elles-mêmes ; vous pouvez aussi saisir des candidatures
reçues par téléphone ou sur papier. Vous suivez qui vous avez contacté et
à qui vous avez proposé une parcelle, et quand une parcelle se libère
vous la remettez -- le candidat devient membre et nouveau locataire en
une seule étape.

Les candidats sont volontairement tenus à l'écart de la liste des
membres. La plupart des candidats n'obtiennent jamais de parcelle : leurs
données ne doivent donc pas se retrouver dans les effectifs, les
factures, les heures de travail ou les envois.

!!! info "Qui peut l'utiliser"
    Le module **Candidats** est activé par défaut. Il peut être désactivé
    sous [Activer et désactiver les modules](../administration/modules.md).

    - **Voir** la liste et les candidatures nécessite le droit de
      *lecture* sur **Candidats**.
    - **Ajouter** un candidat, **modifier** les coordonnées, le statut et
      la note du bureau, et **contacter** un nouveau candidat nécessitent
      le droit d'*écriture*.
    - **Supprimer** définitivement un candidat nécessite le droit de
      *suppression*.
    - **Attribuer une parcelle** nécessite le droit d'*écriture* à la fois
      sur **Candidats** et sur **Membres et parcelles**.

    Les membres du bureau et les administrateurs ont tous ces droits. Un
    groupe peut les accorder à d'autres, par ex. à la personne chargée de
    l'attribution des parcelles (voir [Groupes](../administration/groups.md)).

    Les candidatures de votre site web n'arrivent que tant que le module
    séparé **API publique du formulaire de candidature** est activé. Il
    est désactivé par défaut, car il permet à des personnes extérieures à
    l'association d'écrire dans Parcella. Voir
    [Candidatures depuis votre site web](#applications-from-your-website).

## Où remarquer les nouvelles candidatures {#where-you-notice-new-applications}

- L'entrée **Candidats** du menu principal affiche un chiffre rouge : les
  candidatures que personne n'a encore regardées (statut **Nouveau**). Il
  disparaît dès que chaque nouvelle candidature est passée à un autre
  statut.
- Le [tableau de bord](../getting-started/dashboard.md) a une carte
  **Nouvelles candidatures** avec le même chiffre, « pas encore
  traitées ». Elle ouvre la liste filtrée sur les nouvelles candidatures.

Parcella n'envoie pas d'e-mail au bureau pour une nouvelle candidature --
le chiffre dans le menu et sur le tableau de bord est le signal.

## Statuts {#statuses}

Chaque candidature passe par ces statuts. Vous les définissez sur la
[page de la candidature](#application-page) ; seul **Clôturée (parcelle
attribuée)** est défini par Parcella lui-même.

| Statut | Signification |
|---|---|
| **Nouveau** | Vient d'arriver ; personne ne l'a encore regardée. |
| **Contacté** | Le bureau a pris contact -- par ex. envoyé le premier e-mail. Le candidat est sur la liste d'attente. |
| **Parcelle proposée** | Une parcelle a été proposée. |
| **Acceptée** | Le candidat veut la parcelle proposée ; la remise est encore en cours d'organisation. |
| **Refusée** | L'association a refusé, ou le candidat ne veut plus d'offres. |
| **Clôturée (parcelle attribuée)** | Le candidat a obtenu une parcelle via **Attribuer une parcelle**. |

**Nouveau**, **Contacté**, **Parcelle proposée** et **Acceptée** comptent
comme *ouvertes*. Si un candidat refuse une offre mais veut rester sur
la liste d'attente, repassez-le à **Contacté**. S'il ne veut plus
d'offres, choisissez **Refusée**.

## Liste des candidats {#applicant-list}

![Liste des candidats](../assets/screenshots/applicants/list.png)

Ouvrez **Candidats** dans le menu principal. La liste affiche les
candidatures, la date de candidature la plus récente en premier.

### Filtre et recherche {#filter-and-search}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nouvelles** | Seulement les candidatures au statut **Nouveau**. Affiché seulement tant qu'il y a de nouvelles candidatures -- et la liste s'ouvre alors avec ce filtre. |
| **Ouvert** | Les candidatures **Nouveau**, **Contacté**, **Parcelle proposée** ou **Acceptée**. La liste s'ouvre avec ce filtre quand il n'y a pas de nouvelles candidatures. |
| **Clôturées** | Les candidatures **Clôturée (parcelle attribuée)** ou **Refusée**. |
| **Toutes** | Chaque candidature. |
| **Nom, e-mail, téléphone, message, notes…** | Cherche dans le prénom et le nom, l'adresse e-mail, le numéro de téléphone, le message du candidat et la note du bureau. Se combine avec les boutons de filtre. Comme la note du bureau est incluse, un numéro de ticket noté là retrouve le candidat. |
| **Rechercher** | Applique la recherche. |
| **Réinitialiser** | Efface la recherche, garde le bouton de filtre. |

### Colonnes {#columns}

| Colonne | Ce qu'elle affiche |
|---|---|
| Case à cocher | Sélectionne le candidat pour **Écrire aux candidats sélectionnés** (voir ci-dessous). |
| **Nom** | Prénom et nom, ou l'adresse e-mail si aucun nom n'a été donné. Cliquez dessus pour ouvrir la candidature. |
| **E-mail** | Cliquez pour écrire depuis votre propre logiciel de messagerie. |
| **Téléphone** | |
| **Candidature** | La date de candidature. Elle détermine l'ordre de la liste d'attente. |
| **Statut** | Voir [Statuts](#statuses). |
| Bouton œil | Ouvre la candidature. |

Deux types de badges peuvent apparaître à côté du nom :

- **2×**, **3×** … -- cette adresse e-mail a postulé plus d'une fois.
  Parcella ne fusionne pas les candidatures répétées ; chacune reste une
  entrée séparée, pour qu'aucun message ne se perde. C'est vous qui
  décidez quoi en faire. La page de la candidature liste les autres.
- **Alerte** -- le nom, l'adresse e-mail ou le numéro de téléphone du
  candidat correspond à un [contact externe](external-contacts.md) qui
  porte l'étiquette d'alerte de votre association. Survolez le badge
  pour voir quel contact et quelles données correspondent. Il n'y a pas
  d'alertes tant que le module Contacts externes est désactivé.

### Écrire aux candidats sélectionnés {#writing-to-selected-applicants}

Tant que le module **Annonces** est activé, les membres du bureau et les
administrateurs voient une case à cocher sur chaque ligne.

| Bouton | Ce qu'il fait |
|---|---|
| **Tout sélectionner** | Coche chaque candidat affiché par le filtre et la recherche actuels. |
| **Tout désélectionner** | Efface toutes les coches. |
| ***N* sélectionné(s)** | Compte les candidats cochés. |
| **Écrire aux candidats sélectionnés** | Démarre une nouvelle [annonce](announcements.md) aux candidats cochés. Elle part uniquement par e-mail, une fois par adresse -- quelqu'un qui a postulé deux fois reçoit un seul e-mail. Désactivé tant que vous n'avez coché personne. |

### Ajouter un candidat à la main {#adding-an-applicant-by-hand}

**Nouveau candidat** (en haut à droite, nécessite le droit d'écriture)
ouvre le formulaire [Nouveau candidat](#new-applicant).

## Nouveau candidat {#new-applicant}

![Formulaire de nouveau candidat](../assets/screenshots/applicants/form-new.png)

Pour les candidatures qui ne sont pas passées par le site web -- par
téléphone, par courrier, ou issues d'une ancienne liste d'attente
papier. Les candidatures du formulaire du site web apparaissent
d'elles-mêmes dans la liste.

| Champ | Ce qu'il fait |
|---|---|
| **Adresse e-mail** \* | Obligatoire -- le seul champ obligatoire. Doit être une adresse e-mail valide, sinon « Veuillez saisir une adresse e-mail valide. » |
| **Prénom** / **Nom** | Facultatifs ici, mais nécessaires avant de pouvoir attribuer une parcelle. |
| **Téléphone** | |
| **Candidature** | La date de candidature. « Laisser vide pour aujourd'hui. Modifiez-la pour saisir une candidature plus ancienne, p. ex. d'une liste d'attente papier -- elle détermine l'ordre. » Une date future est refusée. |
| **Message du candidat** | Ce que le candidat a écrit ou vous a dit. |
| **Note du bureau** | « Interne -- jamais montrée au candidat. » |

Cliquez sur **Enregistrer**. La candidature démarre au statut
**Nouveau**, son origine est **Saisie manuelle** (avec votre nom), et
elle n'a pas de date de consentement à la protection des données --
celle-ci n'est enregistrée que pour les candidatures du site web.
**Retour** revient à la liste sans enregistrer.

## Page de la candidature {#application-page}

![Page de la candidature](../assets/screenshots/applicants/detail.png)

Cliquez sur un candidat dans la liste pour ouvrir sa candidature.

Si le candidat correspond à un contact externe signalé, un encadré rouge
**Alerte** en haut nomme le contact et les données correspondantes (nom,
e-mail, téléphone). Les utilisateurs qui peuvent voir les contacts
externes peuvent cliquer pour aller au contact.

### Candidature {#application}

La carte de gauche contient tout ce que vous pouvez modifier.

| Champ | Ce qu'il fait |
|---|---|
| **Statut** | Voir [Statuts](#statuses). Chaque changement est enregistré dans l'**Historique du statut**. |
| **Adresse e-mail** \*, **Prénom**, **Nom**, **Téléphone** | Les coordonnées du candidat. |
| **Candidature** | La date de candidature. Modifiez-la pour placer une candidature au bon endroit dans la file, par ex. quand vous saisissez une ancienne candidature papier. Un changement est enregistré dans l'historique du statut, car il fait monter ou descendre le candidat. Les dates futures sont refusées. |
| **Message du candidat** | Le texte envoyé par le candidat. |
| **Note du bureau** | Notes internes, jamais montrées au candidat -- par ex. « appelé le 3 mai, préfère une petite parcelle ». |

Cliquez sur **Enregistrer** pour enregistrer vos modifications. Sans
droit d'écriture, vous voyez les données mais ne pouvez pas enregistrer.
Les changements de coordonnées et de la note du bureau ne sont pas
enregistrés dans l'historique.

### Boutons en haut {#buttons-at-the-top}

| Bouton | Ce qu'il fait |
|---|---|
| **Retour** | Revient à la liste des candidats. |
| **Supprimer** | Supprime définitivement la candidature après confirmation de « Supprimer définitivement ce candidat ? Action irréversible. » Son historique de statut part avec elle. Nécessite le droit de suppression. |

!!! info "Pourquoi les candidats peuvent être supprimés définitivement"
    Presque tout le reste dans Parcella conserve son historique. Les
    candidats sont l'exception : leurs données ne sont conservées que
    pour la candidature, vous devez donc pouvoir les supprimer
    complètement -- quand quelqu'un vous le demande, ou une fois la
    candidature terminée. Votre association peut aussi faire supprimer
    automatiquement les anciennes candidatures ; voir
    [Suppression automatique](#automatic-deletion).

### Contacter le candidat {#contact-applicant}

Affiché seulement sur une candidature **Nouveau**, aux utilisateurs
ayant le droit d'écriture. C'est la première étape du parcours : un
e-mail de remerciement qui confirme que le candidat est sur la liste
d'attente.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **À :** | L'adresse e-mail du candidat. |
| **Objet :** | « Merci de vous être inscrit(e) sur notre liste d'attente ! » (dans la langue dans laquelle vous utilisez Parcella). |
| Message | Le texte de l'e-mail, prêt à être modifié. Le nom du candidat et celui de l'association sont déjà remplis. |
| **Envoyer** | Après confirmation, envoie le texte au candidat par e-mail et passe le statut à **Contacté**. |

Après l'envoi, un avis vert indique « L'e-mail a été envoyé et le statut
passé à « Contacté ». » L'encadré disparaît ensuite, car la candidature
n'est plus nouvelle.

Si l'e-mail ne peut pas être envoyé, rien ne change : le statut reste
**Nouveau**, votre texte modifié reste dans l'encadré, et vous voyez
« L'e-mail n'a pas pu être envoyé -- veuillez vérifier les paramètres
SMTP. » Corrigez les paramètres e-mail et réessayez.

Le texte de départ vient de **Texte de l'e-mail aux nouveaux candidats**
dans les [Paramètres de l'association](../administration/settings.md) →
**Candidats**. S'il est vide, Parcella utilise son texte intégré dans la
langue dans laquelle vous utilisez Parcella. Les candidats n'ont pas de
réglage de langue propre : si votre association rédige son propre texte,
écrivez-le dans la langue de vos candidats.

!!! note
    Parcella ne conserve pas de copie de l'e-mail. Seul le passage au
    statut **Contacté** montre qu'il est parti.

### Attribuer une parcelle {#assign-a-parcel}

Affiché seulement sur une candidature ouverte, aux utilisateurs ayant le
droit d'écriture à la fois sur **Candidats** et sur **Membres et
parcelles**. **Attribuer une parcelle** remet une parcelle résiliée au
candidat -- voir [Attribuer une parcelle](#assign-a-parcel_1)
ci-dessous.

### Détails {#details}

| Ligne | Ce qu'elle affiche |
|---|---|
| **Candidature** | La date de candidature. |
| **Origine** | **Formulaire du site**, ou **Saisie manuelle** avec le nom de l'utilisateur qui l'a saisie. |
| **Consentement RGPD (candidat)** | Quand le candidat a coché la case de protection des données sur le formulaire du site web. Vide pour les candidatures saisies à la main. C'est le consentement du candidat -- pas une approbation du bureau. |
| **Statut modifié** | Quand le statut a changé pour la dernière fois. |

Toutes les dates sont affichées sans heure.

### Autres candidatures de cette adresse {#other-applications-from-this-address}

Affiché seulement si la même adresse e-mail a postulé plus d'une fois.
Liste les autres candidatures avec date et statut ; cliquez sur une date
pour en ouvrir une.

### Procédures {#processes}

Si le module [Procédures](processes.md) est activé et que vous pouvez
voir les procédures, une carte **Procédures** liste les procédures
concernant ce candidat. **Démarrer une procédure** en démarre une
nouvelle.

### Historique du statut {#status-history}

Chaque changement de statut et chaque changement de la date de
candidature, avec date, heure et l'utilisateur qui l'a fait -- le plus
récent en premier. Les changements faits par Parcella lui-même (une
remise) apparaissent aussi ici.

## Attribuer une parcelle {#assign-a-parcel_1}

![Attribuer une parcelle](../assets/screenshots/applicants/assign-parcel.png)

Quand une parcelle se libère, cette page la remet à un ou plusieurs
candidats en une seule étape. Ouvrez-la avec **Attribuer une parcelle**
sur une candidature.

!!! info "Avant de commencer"
    - La parcelle doit avoir le statut **résilié**. Définissez-le d'abord
      dans le [formulaire de la parcelle](parcels.md#new-parcel-and-edit-parcel).
      Si aucune parcelle n'est résiliée, la page vous l'indique.
    - Chaque candidat qui reprend la parcelle doit avoir un prénom et un
      nom sur sa candidature.

### Étape 1 : parcelle et date de remise {#step-1-parcel-and-handover-date}

| Champ | Ce qu'il fait |
|---|---|
| **Parcelle résiliée** | La parcelle à remettre. Seules les parcelles résiliées sont proposées, chacune avec les noms de ses locataires actuels. |
| **Date de remise** | Le jour où les nouveaux locataires prennent possession. Aujourd'hui par défaut. Elle peut être dans le futur : les anciens locataires restent alors locataires, membres et destinataires des factures jusqu'à ce jour, et les nouveaux locataires apparaissent comme à venir sur la page de la parcelle. |
| **Autres candidats (co-locataires)** | Facultatif : d'autres candidats ouverts qui reprennent la parcelle avec celui-ci, par ex. un couple qui a postulé séparément. |
| **Dossier de documents pour les nouveaux locataires** | Seulement pour les membres du bureau et les administrateurs tant que le module **Stockage cloud** est activé. Le dossier qui devient le dossier de documents de la parcelle à la date de remise. **Parcourir le stockage cloud** permet de naviguer dans votre stockage et de choisir **Utiliser ce dossier**. Créez et partagez vous-même le dossier dans votre stockage cloud. Facultatif -- vous pouvez aussi le définir plus tard sur la page de la parcelle. |
| **Aperçu** | Montre ce qui va se passer. Rien n'est encore modifié. |

### Étape 2 : vérifier l'aperçu {#step-2-check-the-preview}

La carte d'aperçu, **Remise de la parcelle *X* le *date***, liste
exactement ce qui va se passer :

- **Anciens locataires** -- le bail de chaque locataire actuel se
  termine à la date de remise. S'il n'a pas d'autre parcelle, son
  adhésion se termine la veille (« l'adhésion prend fin après le
  *date*. »). S'il a encore une autre parcelle, il garde son adhésion ;
  l'aperçu nomme cette parcelle.
- **Nouveaux locataires et destinataires des factures** -- chaque
  candidat soit « devient un nouveau membre » (nom, e-mail et téléphone
  repris de la candidature), soit, si un membre actif a déjà l'adresse
  e-mail du candidat, est relié à ce membre (« déjà membre : »).
- **Dossier de documents** -- quel dossier est retiré à la date de
  remise et lequel prend le relais. Si vous ne pouvez pas gérer les
  dossiers vous-même, une note indique qu'une personne ayant l'accès
  complet définira le nouveau dossier plus tard.

En cas de problème -- la parcelle n'est pas résiliée, la candidature
d'un candidat est déjà clôturée ou n'a pas de nom -- un message d'erreur
l'explique et rien ne se passe.

Cliquez sur **Remettre la parcelle** et confirmez. Parcella alors, en une
seule fois :

1. termine les anciens baux à la date de remise (ils restent dans
   l'historique de la parcelle comme anciens locataires),
2. termine l'adhésion des anciens locataires qui n'ont pas d'autre
   parcelle,
3. crée les nouveaux membres -- leur **Membre depuis** est la date de
   remise -- et en fait les locataires et destinataires des factures de
   la parcelle,
4. repasse la parcelle à **actif**,
5. passe les candidatures à **Clôturée (parcelle attribuée)**.

Vous arrivez ensuite sur la page de la parcelle.


!!! tip "Complétez ensuite la fiche du nouveau membre"
    Seuls le nom, l'adresse e-mail et le numéro de téléphone sont copiés
    depuis la candidature. Ouvrez le nouveau membre et ajoutez l'adresse
    et l'IBAN. **Peut recevoir des informations par e-mail** est coché,
    comme pour tout nouveau membre ; décochez-le s'il ne veut que du
    papier.

## Candidatures depuis votre site web {#applications-from-your-website}

La plupart des candidatures arrivent par un formulaire sur le site web
de votre association. Une fois configuré, chaque formulaire envoyé
apparaît dans la liste des candidats comme candidature **Nouveau** avec
l'origine **Formulaire du site** et la date à laquelle le candidat a
donné son consentement à la protection des données.

Ce que demande le formulaire : adresse e-mail (obligatoire), prénom et
nom, téléphone, un message, et une case de consentement à la protection
des données qui doit être cochée. Parcella protège le formulaire contre
le spam : des champs cachés que seuls les robots remplissent, un captcha
facultatif, et une limite de quelques envois par heure depuis le même
visiteur.

Pour le configurer :

1. Activez le module **API publique du formulaire de candidature** sous
   [Activer et désactiver les modules](../administration/modules.md).
2. Sous [Intégrations](../administration/integrations.md), saisissez
   l'adresse de votre site web pour que Parcella accepte les formulaires
   qui en viennent. La page liste aussi les adresses auxquelles le
   formulaire envoie.
3. Placez le formulaire sur votre site web :
    - **WordPress** : installez l'extension Parcella Connector et placez
      le shortcode `[parcella_applicant_form]` sur une page.
    - **Tout autre site web** : un simple formulaire HTML qui envoie les
      champs ci-dessus à Parcella. Votre webmestre trouvera les détails
      sous Intégrations.

Ce que voient les candidats est décrit dans
[Pour les jardiniers](../gardeners/index.md).

!!! note
    Parcella n'envoie pas de confirmation automatique au candidat.
    Utilisez [Contacter le candidat](#contact-applicant) pour la première
    réponse.

## Suppression automatique {#automatic-deletion}

Dans les [Paramètres de l'association](../administration/settings.md) →
**Candidats**, **Supprimer les candidatures après (mois)** permet à
Parcella de supprimer les anciennes candidatures pour vous. Toute
candidature dont le statut n'a pas changé depuis ce nombre de mois est
supprimée définitivement -- **quel que soit son statut**, et sans
prévenir personne. Les mois sont comptés à partir du dernier changement
de statut, ou de la date de candidature si le statut n'a jamais changé.

Laissez le champ vide ou à 0 (par défaut) pour conserver les
candidatures jusqu'à ce que vous les supprimiez à la main. La
vérification tourne en arrière-plan pendant que des personnes utilisent
Parcella, au plus une fois par heure.

!!! warning
    La suppression automatique supprime aussi les candidatures ouvertes
    qui attendent simplement depuis longtemps. Si votre liste d'attente
    est longue, choisissez une durée supérieure à l'attente habituelle,
    ou faites évoluer de temps en temps le statut des candidats qui
    attendent depuis longtemps.

## Voir aussi {#related}

- [Parcelles](parcels.md) -- résilier une parcelle avant une remise
- [Membres](members.md) -- compléter les données du nouveau membre
- [Transmettre une parcelle](../guides/parcel-handover.md)
- [Annonces](announcements.md) -- écrire aux candidats sélectionnés
- [Contacts externes](external-contacts.md) -- l'étiquette d'alerte
- [Intégrations](../administration/integrations.md) -- le formulaire du
  site web

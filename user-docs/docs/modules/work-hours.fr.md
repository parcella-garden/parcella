# Heures de travail {#work-hours}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

La plupart des associations de jardins familiaux attendent de chaque
membre ou de chaque parcelle un certain nombre
d'[heures de travail obligatoires](../glossary.md) par an, ou le paiement
des heures non effectuées. Ce module planifie les sessions de travail de
l'association, enregistre qui était présent, crédite les parrainages et
les exemptions, et calcule en fin d'année qui doit encore des heures et
quel montant cela représente.

!!! info "Qui peut l'utiliser"
    Le module est activé par défaut. Vous pouvez le désactiver sous
    **Administration → Paramètres** (**Gestion des heures de travail**)
    si votre association ne demande pas d'heures obligatoires -- voir
    [Activer et désactiver les modules](../administration/modules.md).
    Rien n'est supprimé quand vous le désactivez.

    Les utilisateurs Administrateur et Conseil d'administration peuvent
    tout faire. Les autres utilisateurs ont besoin d'un
    [groupe](../administration/groups.md) qui accorde des droits sur
    **Sessions de travail** : *lecture* pour voir les pages, *écriture*
    pour créer et modifier, *suppression* pour retirer des sessions,
    participants, parrainages, transferts, tâches, rôles du club et
    configurations annuelles. Sans au moins le droit de lecture, le menu
    **Sessions de travail** n'apparaît pas.

Vous trouvez le module dans le menu latéral sous **Sessions de
travail**, avec ces entrées : **Sessions & Aperçu**, **Évaluation
annuelle**, **Parrainages**, **Transferts d'heures** et **Tâches**. La
configuration des heures et les rôles du club sont accessibles par des
boutons de la page d'aperçu.

## Comment les heures sont comptées {#how-the-hours-are-counted}

Avant de regarder les écrans un par un, il est utile de savoir comment
Parcella fait le total d'une année. Pour chaque membre, il compte :

- **Les sessions de travail** -- chaque session de cette année civile où
  le statut du membre est **Présent**. Chaque présence compte avec les
  heures saisies pour cette personne ou, si aucune n'a été saisie, avec
  les **Heures par participant** de la session. **Inscrit** et
  **Absent** ne comptent rien.
- **Les parrainages** -- les **Heures créditées/an** de chaque parrainage
  attribué au membre dont la période chevauche l'année. Un parrainage ne
  compte qu'une fois qu'il a à la fois un membre et une date **Valable
  du**.
- **Les transferts d'heures** -- les heures que d'autres membres lui ont
  données (en plus), moins les heures qu'il a données (en moins).

La suite dépend du **Mode de facturation** défini pour l'année dans la
[configuration](#mandatory-hours-configuration) :

| Mode de facturation | Ce que cela signifie pour l'association |
|---|---|
| **Par location / parcelle** | Chaque parcelle doit une fois les heures annuelles. Les heures de tous ses locataires s'additionnent : si un locataire fait 2 heures et l'autre 3, une obligation de 5 heures est remplie. |
| **Par membre** | Chaque membre qui a eu un bail pendant l'année doit les heures individuellement. |

Les heures manquantes sont multipliées par le **Tarif horaire** pour
obtenir le montant dû.

### Exemptions {#exemptions}

Un membre est exempté pour une année quand il occupe un
[rôle du club](#club-roles) marqué **Exempté des heures obligatoires**
pour cette année -- typiquement le travail au bureau.

!!! warning "Un locataire exempté exempte toute la parcelle"
    En mode **Par location / parcelle**, une parcelle est exemptée dès
    qu'**au moins un** de ses locataires est exempté. Les co-locataires
    d'un membre du bureau ne doivent donc rien non plus cette année-là :
    la fonction au bureau « couvre » toute la parcelle. Peu importe que
    les autres locataires soient eux-mêmes exemptés ou non.

    En mode **Par membre**, seul le membre exempté est exempté.

Une exemption s'applique toujours à **toute l'année civile** pour
laquelle l'attribution du rôle est saisie. Un membre du bureau qui quitte
ses fonctions en octobre reste exempté le reste de l'année ; les dates
**Du** et **Au** servent à vos archives et ne raccourcissent pas
l'exemption. L'année suivante, vous attribuez à nouveau le rôle (ou
non).

### Qui compte comme locataire dans une année {#who-counts-as-a-tenant-in-a-year}

L'évaluation regarde qui occupait une parcelle *pendant l'année
évaluée*, pas qui l'occupe aujourd'hui :

- Terminer un bail n'annule pas les heures de cette année. Un locataire
  qui part en juin doit encore l'année complète. En mode **Par location
  / parcelle**, il reste sur la ligne de la parcelle, cumulé avec la
  personne qui a repris la parcelle ; dans tous les cas, il reçoit un
  badge **bail terminé le**.
- Un bail terminé avant le début de l'année, ou qui commence après, ne
  compte pas.
- Un membre qui est passé d'une parcelle à une autre au sein de
  l'association pendant l'année ne compte que sur la parcelle vers
  laquelle il a déménagé.
- Un membre qui occupe deux parcelles en même temps doit les heures pour
  chaque parcelle. Ses propres heures remplissent les parcelles dans
  l'ordre des numéros : chaque parcelle reçoit ce qui lui manque encore,
  la dernière reçoit le reste. Par exemple, 7,5 heures pour une
  obligation de 5 heures : la première parcelle est remplie avec
  5 heures, la seconde a 2,5 heures et 2,5 heures manquantes.
  L'évaluation affiche un tel locataire comme « 5.0 of 7.5 h ».
- Les membres supprimés disparaissent de toutes les évaluations, y
  compris des années passées. Si les heures d'un partant doivent encore
  être facturées, terminez son adhésion avec une date de fin au lieu de
  le supprimer -- voir [Membres](members.md).

## Sessions & Aperçu {#sessions-overview}

![Sessions & Aperçu](../assets/screenshots/work-hours/overview.png)

La page d'accueil du module, intitulée **Heures obligatoires** suivi de
l'année. Venez ici pour planifier les sessions et voir d'un coup d'œil
si de nouvelles inscriptions sont arrivées.

S'il n'y a pas encore de configuration pour l'année choisie, un bandeau
jaune indique **Pas encore de configuration des heures obligatoires pour
...** avec un lien **Créer maintenant →**. Sinon, trois tuiles affichent
les réglages de l'année.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Sélecteur d'année (en haut à droite) | Passe à une autre année. Seules les années ayant une [configuration](#mandatory-hours-configuration) sont listées. |
| **Nouvelle session** | Ouvre le [formulaire de session](#new-work-session-and-edit-session). Nécessite le droit d'écriture. |
| Tuile **Heures obligatoires** | Les heures requises cette année, et le tarif horaire (**à**). |
| Tuile **Mode** | **Par location** ou **Par membre** -- l'unité de facturation de cette année. |
| Tuile **Montant dû max.** | Heures × tarif : ce que doit une parcelle ou un membre **à zéro heure**. |
| **Évaluation annuelle** | Ouvre l'[Évaluation annuelle](#annual-evaluation) de cette année. |
| **Export CSV** | Télécharge l'évaluation sous forme de tableur (voir [Export CSV](#csv-export)). |

### Tableau des sessions de travail {#work-sessions-table}

Liste chaque session de l'année choisie, la plus récente en premier.

| Colonne | Ce qu'elle affiche |
|---|---|
| **Date** | La date de la session. |
| **Titre** | Renvoie vers la [page de la session](#session-page). Un chiffre rouge à côté compte les nouvelles inscriptions (voir ci-dessous). |
| **Type** | **Standard** (planifiée) ou **Spécial** (spontanée). |
| **Heure** | De -- à, ou « – » si aucune heure n'a été saisie. |
| **Participants** | Nombre de participants, « / maximum » si une limite est fixée, et entre parenthèses combien sont **présents** et combien sont **nouveaux**. |
| Bouton œil | Ouvre la page de la session. |

Si l'année n'a pas encore de sessions, le tableau indique **Pas encore
de sessions de travail pour ...** et propose **Créer une première
session** (avec le droit d'écriture).

### Accès rapide {#quick-access}

Les boutons sous le tableau mènent à **Configuration des heures**,
**Rôles du club**, **Parrainages** et **Tâches**.

### Nouvelles inscriptions : badges, tuile du tableau de bord et e-mails {#new-sign-ups-badges-dashboard-tile-and-e-mails}

Parcella marque une participation comme *nouvelle* pendant 14 jours après
sa création -- qu'un jardinier se soit inscrit via le site web de
l'association ou qu'un membre du bureau ait ajouté quelqu'un à la main.
Seules les sessions **Standard** qui n'ont pas encore eu lieu sont
comptées ; enregistrer la présence pour une session passée ou une
session **Spécial** n'apparaît jamais comme « nouveau ».

Vous voyez les nouvelles inscriptions à quatre endroits :

- un chiffre rouge à côté de **Sessions de travail** et **Sessions &
  Aperçu** dans le menu latéral,
- la tuile **Nouvelles inscriptions** du
  [tableau de bord](../getting-started/dashboard.md), avec un bouton
  **Afficher tout** qui mène ici,
- le chiffre rouge à côté du titre de la session dans le tableau
  ci-dessus,
- un badge rouge **Nouveau** à côté du participant sur la page de la
  session.

Une fois que vous les avez vues, cliquez sur **Marquer comme vu** sur la
[page de la session](#session-page). Cela efface la marque « nouveau »
pour toutes les personnes inscrites à la session à ce moment-là.
Quiconque s'inscrit ensuite est de nouveau marqué comme nouveau.

Parcella envoie aussi des e-mails à chaque utilisateur actif ayant le
rôle Administrateur ou Conseil d'administration :

- **Quand un membre du bureau ajoute un participant à la main**, les
  autres utilisateurs Administrateur et Conseil d'administration
  reçoivent un e-mail par participant (« Nouvelle inscription à une
  session de travail dans ... »). La personne qui l'a ajouté n'en reçoit
  pas.
- **Quand des jardiniers s'inscrivent via le site web de
  l'association**, tout le monde reçoit un e-mail récapitulatif par
  envoi (« ... nouvelle(s) inscription(s) à des sessions de travail dans
  ... »), quel que soit le nombre de sessions et de membres du foyer
  inscrits.

<!-- TODO(verify): users who only have full access through a group (not the Admin/Board role itself) don't receive these notification e-mails -- confirm this is intended. -->

## Inscriptions via le site web de l'association {#sign-ups-through-the-club-website}

Si le site web de votre association (par exemple WordPress) a un
formulaire d'inscription aux sessions de travail, les jardiniers peuvent
s'inscrire sans identifiant Parcella. Cela nécessite le module **API
publique d'inscription**, **désactivé par défaut** car il ouvre Parcella
aux envois depuis internet. Activez-le sous **Administration →
Paramètres**, puis configurez la connexion au site web dans
[Intégrations](../administration/integrations.md). Ce que voient les
jardiniers est décrit dans [Pour les jardiniers](../gardeners/index.md).

Côté bureau, voici ce qui se passe :

- **Quelles sessions sont proposées.** Seulement les sessions
  **Standard** dont la date n'est pas passée. Une session avec une
  **Date limite d'inscription (jours avant)** disparaît du site web ce
  nombre de jours plus tôt. Les sessions **Spécial** n'apparaissent
  jamais sur le site web.
- **Qui est inscrit.** Le jardinier saisit son numéro de parcelle et,
  éventuellement, son nom. Parcella compare le nom avec les locataires
  *actuels* de la parcelle. S'il correspond exactement à une personne,
  seule cette personne est inscrite. Si aucun nom n'a été donné, ou s'il
  ne correspond pas clairement à une personne, **tous les locataires
  actuels de la parcelle** sont inscrits, pour qu'aucune inscription ne
  se perde. Une parcelle sans locataire actuel ne peut pas s'inscrire.
- **Sessions complètes.** Si la session n'a pas assez de places libres
  pour toutes les personnes qui seraient inscrites, l'inscription à
  cette session est refusée dans son ensemble. Les participants marqués
  **Absent** n'occupent pas de place.
- **Pas de doublons.** S'inscrire deux fois à la même session ne crée
  pas de seconde entrée.
- **Ce que vous voyez.** Les inscriptions apparaissent comme des
  participants normaux au statut **Inscrit**, avec un badge **Nouveau**
  et une **Note** comme « Public signup, matched by name (parcel G012) |
  Phone: ... ». Quand tous les locataires ont été inscrits, la note
  l'indique et vous demande de retirer ceux qui ne se sont pas réellement
  inscrits.
- **Confirmation au jardinier.** Chaque membre nouvellement inscrit
  reçoit un e-mail de confirmation à l'adresse enregistrée dans sa fiche
  membre -- jamais à une adresse saisie dans le formulaire du site web.
  Vous pouvez modifier le texte ou le désactiver dans la
  [configuration](#sign-up-confirmation-email).

!!! tip "Après l'arrivée d'inscriptions par le site web"
    Ouvrez la session, vérifiez les notes des nouveaux participants,
    retirez ceux qui n'ont été inscrits que par précaution (nécessite le
    droit de suppression), et cliquez sur **Marquer comme vu**.

## Page de la session {#session-page}

![Page de la session](../assets/screenshots/work-hours/session-detail.png)

Cliquez sur le titre d'une session pour l'ouvrir. C'est ici que vous
gérez la liste des participants avant la session et enregistrez les
présences ensuite.

| Bouton (en haut) | Ce qu'il fait |
|---|---|
| **Modifier** | Ouvre le [formulaire de session](#new-work-session-and-edit-session). Nécessite le droit d'écriture. |
| **Liste des participants** | Télécharge un PDF à imprimer et à emporter à la session (voir ci-dessous). |
| **Supprimer** | Supprime la session après confirmation. **Toutes les participations sont perdues**, si bien que les heures ne comptent plus pour personne. Les tâches planifiées pour la session retournent dans les tâches en attente. Nécessite le droit de suppression. |
| **Retour** | Revient à l'aperçu. |

### Détails {#details}

Affiche le **Type** (**Standard** ou **Spécial**), la **Date**,
l'**Heure**, les **Places** (participants / maximum), les
**Heures/personne** et la description.

### Participants {#participants}

L'en-tête de la carte compte combien de participants sont **présents**
et combien sont **inscrits**. S'il y a de nouvelles inscriptions et que
vous avez le droit d'écriture, il affiche aussi **Marquer comme vu**
(voir [Nouvelles inscriptions](#new-sign-ups-badges-dashboard-tile-and-e-mails)).

Tapez dans **Rechercher par membre ou numéro de parcelle…** pour filtrer
le tableau.

| Colonne | Ce qu'elle affiche / fait |
|---|---|
| **Membre** | Nom, avec un lien vers la fiche du membre. Un badge rouge **Nouveau** marque une nouvelle inscription. |
| **Parcelle** | La ou les parcelles actuelles du membre. |
| **Statut** | **Inscrit**, **Présent** ou **Absent**. Avec le droit d'écriture, choisir une autre valeur l'enregistre immédiatement. Seul **Présent** compte pour les heures du membre. |
| **Heures** | Les heures créditées à cette personne. Le champ est prérempli avec ses propres heures ou, si aucune n'a été saisie, avec les **Heures par participant** de la session. Modifiez-le et cliquez sur **✓** pour enregistrer. Sans droit d'écriture, vous ne voyez que le nombre. |
| **Note** | Par exemple les informations saisies par un jardinier dans le formulaire du site web. |
| **×** | Retire le participant après confirmation. Nécessite le droit de suppression. |

!!! tip "Enregistrez les présences après la session"
    Passez toutes les personnes venues à **Présent** et corrigez les
    heures de celles qui sont restées moins ou plus longtemps. Laissez
    les personnes qui ne sont pas venues sur **Absent** plutôt que de les
    retirer, pour voir plus tard qui était attendu.

**Ajouter un participant** (droit d'écriture) : en bas de la carte,
commencez à taper un nom ou un numéro de parcelle dans **Sélectionner un
membre…** et choisissez le membre dans la liste -- vous devez choisir
quelqu'un dans la liste, taper un nom seul ne suffit pas. Les membres
déjà inscrits à la session ne sont pas proposés. Choisissez le statut
(**Présent** est présélectionné, car on s'en sert surtout pour
enregistrer les présences après coup), saisissez éventuellement des
heures (vide signifie la valeur par défaut de la session) et cliquez sur
**Ajouter**.

Ajouter quelqu'un à la main est toujours possible, même quand la session
est complète, que sa date limite d'inscription est passée ou que la
session est dans le passé -- les limites ne s'appliquent qu'aux
inscriptions via le site web.

### Tâches {#tasks}

Liste les [tâches](#tasks_1) planifiées pour cette session, avec
**Tâche**, **Charge de travail** et **Attribuée à**. Avec le droit
d'écriture, vous pouvez choisir l'un des participants de la session dans
**Attribuée à** (ou **Pas encore attribuée**), et marquer une tâche comme
faite ou non avec le bouton de coche. Les tâches faites sont barrées.
**Gérer les tâches** ouvre la liste des tâches.

### Liste des participants {#attendee-sheet}

Le PDF liste chaque participant de la session, trié par parcelle et par
nom, avec les colonnes **Parcelle**, **Membre**, **Heures**, **Tâches
assignées** et **Signature**. **Heures** affiche les heures individuelles
ou la valeur par défaut de la session, et reste vide si aucune n'existe.
**Tâches assignées** reste vide quand aucune tâche n'a encore été
attribuée, pour que vous puissiez en écrire une à la main. La liste
s'étend sur plusieurs pages si nécessaire.

L'impression ne change rien dans Parcella : après la session, saisissez
le statut et les heures corrigés sur la page de la session.

## Nouvelle session de travail et modifier la session {#new-work-session-and-edit-session}

![Nouvelle session de travail](../assets/screenshots/work-hours/session-form.png)

S'ouvre avec **Nouvelle session** sur l'aperçu, ou **Modifier** sur la
page d'une session. Nécessite le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Titre** | Obligatoire. Par exemple « Nettoyage de printemps ». |
| **Type** | **Standard (planifié)** pour les sessions prévues à l'avance, **Spécial (spontané)** pour celles qui ne le sont pas. Seules les sessions Standard apparaissent sur le site web de l'association et comptent comme nouvelles inscriptions. |
| **Date** | Obligatoire. Les heures de la session comptent pour l'année civile de cette date. |
| **De** / **Jusqu'au** | Heure de début et de fin facultatives. |
| **Max. participants** | Vide = illimité. Limite les inscriptions via le site web ; les membres du bureau peuvent quand même ajouter d'autres personnes à la main. |
| **Date limite d'inscription (jours avant)** | Ferme l'inscription sur le site web ce nombre de jours avant la session -- 1 la ferme la veille. Laissez vide pour la garder ouverte jusqu'à ce que la date de la session soit passée. N'affecte pas l'ajout de personnes dans Parcella. |
| **Heures par participant** | Les heures par défaut de chaque présent, par exemple 4.0. Vous pouvez encore changer les heures par personne lors de l'enregistrement des présences. |
| **Description** | Tâches, outils, remarques particulières. |
| **Annuler** / **Créer une session** ou **Enregistrer les modifications** | L'enregistrement vous amène sur la page de la session. |

## Évaluation annuelle {#annual-evaluation}

![Évaluation annuelle](../assets/screenshots/work-hours/evaluation.png)

Affiche, pour chaque parcelle ou membre, combien d'heures étaient
requises, combien ont été faites, et ce qui reste dû. Ouvrez-la depuis
le menu (**Évaluation annuelle**) ou l'aperçu. C'est la liste avec
laquelle vous travaillez en fin d'année, et c'est elle qu'utilise la
facturation pour l'article **Déficit d'heures de travail (depuis le
module)** (voir [Séries de factures](finances/invoice-runs.md)).

| Bouton | Ce qu'il fait |
|---|---|
| Sélecteur d'année | Change d'année. Seules les années configurées sont listées. |
| **Export CSV** | Télécharge l'évaluation (voir ci-dessous). |
| **Retour** | Revient à l'aperçu. |

Sans configuration pour l'année, la page n'affiche que le bandeau jaune
**Pas encore de configuration des heures obligatoires pour ...**

Les quatre tuiles en haut indiquent combien de lignes sont **Réalisé**
(par ex. « 18 / 25 »), le total des **Heures restantes**, le **Montant
total dû**, et le **Mode** avec les heures et le tarif.

### Le tableau {#the-table}

Les lignes sont vertes quand l'obligation est remplie et jaunes quand
des heures manquent.

| Colonne | Ce qu'elle affiche |
|---|---|
| **Parcelle** et **Locataire** (mode par location) | Une ligne par parcelle qui a eu au moins un locataire pendant l'année, y compris les parcelles dont le bail a été résilié. Chaque locataire est listé avec ses heures entre parenthèses, un badge **exempté** s'il est exempté, un badge **bail terminé le** avec la date si son bail s'est terminé pendant l'année, et « x of y h » s'il occupe plusieurs parcelles. |
| **Membre** (mode par membre) | Une ligne par membre qui a eu un bail pendant l'année, avec un badge **bail terminé le** le cas échéant. |
| **Requis** | L'obligation annuelle. |
| **Sessions** | Les heures des sessions de travail suivies. |
| **Parrainage** | Les heures créditées par les parrainages. |
| **Transferts** | Les heures reçues (+) ou données (−). « – » s'il n'y en a pas. |
| **Total** | Sessions + parrainage + transferts. |
| **Ouvert** | Les heures qui manquent encore. « – » pour les lignes exemptées. |
| **Dû** | Heures manquantes × tarif horaire. « – » pour les lignes exemptées. |
| **Statut** | **Exempté**, **Réalisé** ou **Ouvert**. |

Cliquez sur la flèche au début d'une ligne (**Afficher les sessions de
travail**) pour voir les **Sessions de travail suivies** de cette
année : date, session (avec lien) et heures -- en mode par location, une
liste par locataire. La liste totalise toujours la colonne **Sessions**.
Les parrainages et transferts n'en font pas partie.

### Export CSV {#csv-export}

Le fichier CSV utilise des points-virgules et les en-têtes de colonnes
de la page d'évaluation, dans la langue de l'association : Parcelle,
Locataire, Requis (h), Sessions (h), Parrainage (h), Transferts (h),
Total (h), Ouvert (h), Dû (EUR), Exempté et Réalisé, avec « Oui »/« Non »
dans cette langue pour les valeurs oui/non.

!!! warning "L'export CSV ne fonctionne qu'en mode par location"
    Pour une année configurée **Par membre**, le fichier CSV ne contient
    que la ligne d'en-tête. Utilisez plutôt la page d'évaluation.

!!! warning "Parcelles que plus personne n'occupe"
    Si tous les locataires d'une parcelle sont partis pendant l'année et
    que la parcelle n'a pas été relouée, la parcelle affiche quand même
    ses heures manquantes, mais la facture automatique ne peut pas les
    facturer car la parcelle n'a pas de locataire actuel à qui
    l'adresser. Facturez un tel partant à la main. Si la parcelle a été
    relouée, le nouveau locataire reçoit la facture de la parcelle pour
    l'année.

## Parrainages {#sponsorships}

![Parrainages](../assets/screenshots/work-hours/sponsorships.png)

Un parrainage est une partie du terrain qu'un membre entretient toute
l'année -- une haie, l'aire de jeux, l'entrée -- au lieu de participer
aux sessions de travail. Chaque parrain se voit créditer un nombre fixe
d'heures par an. Ouvrez-le depuis **Parrainages** dans le menu ou sur
l'aperçu.

La page a trois parties : le formulaire pour créer un parrainage (droit
d'écriture), **Parrainages actifs** et **Anciens parrainages**.

### Créer un parrainage / ajouter un membre {#create-sponsorship-add-member}

| Champ | Ce qu'il fait |
|---|---|
| **Zone** | Obligatoire. Propose les noms de zones déjà utilisés. Choisissez une zone existante pour y ajouter un autre membre -- plusieurs personnes peuvent partager une zone, et **chacune** reçoit la totalité des heures créditées. |
| **Membre** | Listés d'abord par numéro de parcelle (« G001 - Peter Ahnert ») ; les membres sans parcelle viennent en dernier. Laissez sur **– pas encore attribué –** pour proposer une zone que personne n'a encore prise. |
| **Description** | Ce qui est exactement entretenu. |
| **Heures créditées/an** | Obligatoire. Prérempli avec les heures obligatoires de la configuration de l'année, mais vous pouvez le changer si la zone demande plus ou moins d'effort. |
| **Valable du** | Vide = pas encore pris par quelqu'un. |
| **Valable jusqu'au** | Vide = toujours en cours. Ne peut pas être antérieur à **Valable du**. |
| **Enregistrer** | Crée l'entrée. |

!!! info "Quand un parrainage compte"
    Un parrainage crédite ses heures pour chaque année que sa période
    chevauche -- en totalité, même s'il s'est terminé en milieu d'année.
    Il ne compte qu'une fois qu'il a un **Membre** et une date **Valable
    du**. Une entrée sans date de début est une offre permanente et ne
    compte encore pour personne.

Si vous saisissez une date de fin antérieure à la date de début,
Parcella refuse d'enregistrer et affiche **La date de fin est antérieure
à la date de début.** Votre saisie est conservée pour que vous puissiez
la corriger. Les anciennes entrées enregistrées avec de telles dates
affichent un badge rouge **Fin avant le début** et ne comptent pour
aucune année jusqu'à ce que vous les corrigiez.

### Parrainages actifs {#active-sponsorships}

Liste les parrainages de l'année indiquée dans l'en-tête de la carte
(**en ...**) qui ne sont pas encore terminés, plus toutes les offres non
prises. Les entrées de même zone sont regroupées, avec un badge
« ... personne(s) ».

| Colonne | Ce qu'elle affiche / fait |
|---|---|
| **Zone** | Nom et description. |
| **Membre(s)** | Membre avec lien, ou *pas encore attribué*. |
| **Heures/an** | Heures créditées. |
| **Période** | Du – au (ou *en cours*), ou *pas encore pris*. |
| Crayon | Ouvre [Modifier le parrainage](#edit-sponsorship). Nécessite le droit d'écriture. |
| Corbeille | Supprime l'entrée après confirmation. Nécessite le droit de suppression. |

La page affiche l'année en cours quand elle est ouverte depuis le menu.
Le bouton **Parrainages** de l'aperçu l'ouvre pour l'année choisie
là-bas.

### Anciens parrainages {#former-sponsorships}

Chaque parrainage dont la date **Valable jusqu'au** est passée, la date
de fin la plus récente en premier, quelle que soit l'année affichée --
un registre permanent. Mêmes colonnes et actions que ci-dessus.

## Modifier le parrainage {#edit-sponsorship}

<!-- TODO(verify): no screenshot -- the sample data contains no sponsorships, so the edit page can't be reached by the screenshot tool. -->

S'ouvre avec le crayon sur la page des parrainages. Nécessite le droit
d'écriture. Il a les mêmes champs que le formulaire de création :
**Zone**, **Membre**, **Description**, **Heures créditées/an**,
**Valable du** et **Valable jusqu'au**, avec **Annuler** et
**Enregistrer les modifications**. Le même contrôle des dates
s'applique. Après l'enregistrement, vous revenez à la page des
parrainages pour l'année où commence le parrainage.

## Transferts d'heures {#hours-transfers}

![Transferts d'heures](../assets/screenshots/work-hours/transfers.png)

Un membre qui a fait plus que son dû peut donner des heures à un autre
membre, par exemple pour aider un voisin. Ouvrez **Transferts d'heures**
dans le menu.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Sélecteur d'année | Change d'année. Liste les années configurées. |
| **Évaluation** | Ouvre l'évaluation annuelle de cette année. |

### Donner des heures {#give-hours}

Nécessite le droit d'écriture et une configuration pour l'année ; sinon
la carte indique **Aucune configuration pour ...**.

| Champ | Ce qu'il fait |
|---|---|
| **De (donne)** | Obligatoire. Toutes les personnes qui ont été membres à un moment de l'année, par numéro de parcelle. |
| **À (reçoit)** | Obligatoire. Ne peut pas être le même membre. |
| **Heures** | Obligatoire, un nombre positif (arrondi à une décimale). Au plus l'excédent du donneur pour cette année. |
| **Note** | Facultatif, par ex. le motif. |
| **Transférer les heures** | Enregistre le transfert. |

**Combien peut être donné.** Parcella vérifie l'excédent du donneur à
l'enregistrement :

- **Par membre** : le total propre du donneur moins l'obligation.
- **Par location / parcelle** : l'excédent de la parcelle du donneur --
  la parcelle doit rester en règle -- et jamais plus que les propres
  heures du donneur. Les heures d'un co-locataire ne peuvent pas être
  données par quelqu'un d'autre.
- Les membres exemptés, et les bénévoles sans parcelle cette année-là,
  peuvent donner toutes leurs propres heures.

Si c'est trop, un bandeau rouge indique combien d'heures peuvent être
données, par exemple **Seulement 2.0 h peuvent être données -- c'est
l'excédent du donneur pour cette année.**

!!! note
    Le contrôle n'a lieu qu'une fois, à l'enregistrement du transfert. Si
    les présences sont corrigées plus tard (ou qu'un transfert sur
    lequel il s'appuyait est supprimé), le donneur peut se retrouver en
    déficit ; l'évaluation affiche alors simplement les heures
    manquantes.

### Transferts en ... {#transfers-in}

Liste les transferts de l'année avec **De**, **À**, **Heures** et
**Note**, plus la date et qui l'a saisi. La corbeille supprime un
transfert après la confirmation **Supprimer ce transfert ? Les heures
reviennent au donneur.** (droit de suppression). Les entrées erronées
sont supprimées plutôt que conservées comme historique -- ce sont des
corrections, pas l'histoire de l'association.

## Tâches {#tasks_1}

![Tâches](../assets/screenshots/work-hours/tasks.png)

Une liste de travaux à faire, que vous pouvez planifier pour une session
de travail et répartir entre les personnes inscrites. Ouvrez **Tâches**
dans le menu, sur l'aperçu, ou **Gérer les tâches** sur la page d'une
session.

Chaque tâche porte un libellé de **Charge de travail** -- **Légère**,
**Modérée** ou **Exigeante** -- pour que la personne qui coordonne une
session puisse confier un travail adapté à chacun. Ce libellé est tout
ce que Parcella enregistre : il n'y a pas de champ pour l'âge ou la santé
d'un membre, et rien n'est attribué automatiquement. Qui fait quoi reste
la décision du coordinateur.

### Nouvelle tâche {#new-task}

Nécessite le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Titre** | Obligatoire. Par exemple « Tailler la haie nord ». |
| **Description** | Tous les détails utiles avant de commencer. |
| **Charge de travail** | **Légère**, **Modérée** (présélectionnée) ou **Exigeante**. Une indication seulement, non imposée. |
| **Session de travail** | L'une des sessions à venir, ou **-- En attente (pas encore planifiée) --** pour la planifier plus tard. |
| **Ajouter la tâche** | Enregistre la tâche. |

### Tâches en attente {#backlog}

Les tâches sans session, la plus récente en premier, avec **Tâche**,
**Charge de travail** et **Planifier pour**. Choisir une session dans
**Planifier pour** y déplace immédiatement la tâche (droit d'écriture).
Seules les sessions à partir d'aujourd'hui sont proposées. La corbeille
supprime la tâche (droit de suppression).

### Tâches planifiées {#scheduled-tasks}

Sous les tâches en attente, une carte par session qui a des tâches (la
session la plus récente en premier), avec la date et le titre de la
session en lien. Colonnes : **Tâche**, **Charge de travail**,
**Attribuée à**, un bouton de coche pour la marquer faite ou non (droit
d'écriture), et une corbeille pour la supprimer (droit de suppression).
Les tâches faites sont barrées.

Vous attribuez une tâche à une personne sur la
[page de la session](#tasks), où la liste **Attribuée à** propose les
participants de cette session -- une attribution n'a de sens que pour
quelqu'un qui s'est inscrit à cette session.

<!-- TODO(verify): the web pages offer no way to move a task that is already scheduled to a different session or back to the backlog (only the backlog has a "Schedule to" list). Moving it via the API clears the assignment. Confirm this is intended or a gap. -->

## Rôles du club {#club-roles}

![Rôles du club](../assets/screenshots/work-hours/club-roles.png)

Les fonctions dans l'association -- président, trésorier, responsable de
l'eau -- et qui les occupe quelle année. Un rôle marqué comme exempté
libère son titulaire (et, en mode par location, toute sa parcelle) des
heures obligatoires pour cette année. Ouvrez-le avec **Rôles du club**
sur l'aperçu.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Sélecteur d'année | L'année dont les attributions de rôles sont affichées et créées. Propose l'année en cours et les quatre précédentes. |
| **Retour** | Revient à l'aperçu. |

### Nouveau rôle de club {#new-club-role}

Nécessite le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Nom** | Obligatoire, par ex. « Président ». |
| **Description** | Les missions de ce rôle. |
| **Exempté des heures obligatoires** | Cochez si les titulaires n'ont pas à faire d'heures de travail. |
| **Motif de l'exemption** | Apparaît quand la case est cochée : **Travail au conseil d'administration**, **Conseil d'administration élargi**, **Maladie / Raisons de santé**, **Exemption liée à l'âge** ou **Autre motif**. Pour vos archives ; cela ne change pas le fonctionnement de l'exemption. |
| **Créer un rôle** | Enregistre le rôle. |

### Rôles existants {#existing-roles}

Liste tous les rôles avec **Nom** (et description) et **Exempté**
(**Oui**/**Non**). Le crayon ouvre [Modifier le rôle de club](#edit-club-role)
(droit d'écriture). La corbeille supprime le rôle après l'avertissement
**Voulez-vous vraiment supprimer ce rôle ? Toutes les attributions seront
perdues.** (droit de suppression).

!!! warning "Supprimer un rôle modifie les années passées"
    Les attributions de *toutes* les années sont supprimées avec le
    rôle : les membres qui étaient exemptés les années précédentes ne le
    sont donc plus non plus dans les évaluations de ces années. Ne
    supprimez qu'un rôle saisi par erreur.

### Membres dans les rôles du club {#members-in-club-roles}

Attribue des membres à des rôles pour l'année choisie en haut. Nécessite
le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Membre** | Obligatoire. Les membres actuels, par ordre alphabétique. |
| **Rôle du club** | Obligatoire. |
| **Du** / **Au** | Dates facultatives du mandat. **Au** vide = toujours en cours. Pour vos archives seulement -- l'exemption couvre toujours toute l'année. |
| **Attribuer** | Enregistre l'attribution. Attribuer deux fois le même membre au même rôle la même année ne fait rien. |

Le tableau affiche les attributions de l'année avec **Membre**, **Rôle**,
**Exempté**, **Du**, **Au** (ou *en cours*) et **Note**. Le crayon
ouvre [Modifier l'attribution](#edit-assignment) (droit d'écriture) ;
**×** retire l'attribution après confirmation (droit de suppression).

!!! tip "Chaque année à nouveau"
    Les attributions de rôles appartiennent à une année. Au début d'une
    nouvelle année, choisissez-la en haut et attribuez à nouveau le
    bureau, sinon personne n'est exempté cette année-là. Pour saisir une
    année future que le sélecteur ne propose pas encore, créez
    l'attribution et changez son **Année** dans
    [Modifier l'attribution](#edit-assignment).

## Modifier le rôle de club {#edit-club-role}

<!-- TODO(verify): no screenshot -- the sample data contains no club roles. -->

S'ouvre avec le crayon à côté d'un rôle. Mêmes champs qu'à la création :
**Nom**, **Description**, **Exempté des heures obligatoires** et
**Motif de l'exemption**, avec **Annuler** et **Enregistrer les
modifications**. Changer si un rôle est exempté s'applique à chaque année
où il a été attribué, années passées comprises.

## Modifier l'attribution {#edit-assignment}

<!-- TODO(verify): no screenshot -- the sample data contains no club-role assignments. -->

S'ouvre avec le crayon à côté d'une attribution (**Modifier le membre
dans le rôle de club**).

| Champ | Ce qu'il fait |
|---|---|
| **Membre** | Obligatoire. |
| **Rôle du club** | Obligatoire. |
| **Année** | Obligatoire. L'exemption des heures obligatoires s'applique pour toute cette année civile. |
| **Du** / **Au** | Dates de mandat facultatives ; **Au** vide = toujours en cours. |
| **Note** | Par ex. motif de la démission, passation à… |
| **Annuler** / **Enregistrer les modifications** | L'enregistrement revient aux rôles du club de l'année de l'attribution. |

## Configuration des heures obligatoires {#mandatory-hours-configuration}

![Configuration des heures obligatoires](../assets/screenshots/work-hours/configuration.png)

Les règles annuelles : combien d'heures, ce que coûte une heure non
effectuée, et si vous comptez par parcelle ou par membre. Chaque année a
sa propre configuration : changer le tarif de l'année prochaine ne touche
donc pas les années passées. Ouvrez-la avec **Configuration des heures**
sur l'aperçu, ou **Créer maintenant →** dans un bandeau d'avertissement.

Sans configuration pour une année, cette année ne peut pas être évaluée,
les heures ne peuvent pas être transférées, et la facturation ne facture
pas de déficit d'heures de travail.

### Créer / mettre à jour l'année {#create-update-year}

Nécessite le droit d'écriture.

| Champ | Ce qu'il fait |
|---|---|
| **Année** | Obligatoire, préremplie avec l'année en cours. |
| **Total des heures obligatoires** | Obligatoire, par ex. 5.0. |
| **Tarif horaire** | Obligatoire. Valeur par heure non effectuée, dans la devise de l'association. |
| **Mode de facturation** | **Par location / parcelle** : tous les locataires d'une parcelle effectuent ensemble les heures obligatoires. **Par membre** : chaque membre effectue ses heures individuellement. |
| **Note** | Par ex. la décision de l'assemblée générale d'où viennent les chiffres. |
| **Enregistrer** | Enregistre l'année. Si l'année a déjà une configuration, elle est **écrasée** par ces valeurs. |

### E-mail de confirmation d'inscription {#sign-up-confirmation-email}

Nécessite le droit d'écriture. Gère l'e-mail que reçoit un membre après
s'être inscrit via le site web de l'association (voir
[Inscriptions via le site web de l'association](#sign-ups-through-the-club-website)).

| Champ | Ce qu'il fait |
|---|---|
| **Envoyer un e-mail de confirmation** | Activé par défaut. Décochez pour n'envoyer aucune confirmation. |
| **Votre texte** | Texte simple ; une ligne vide commence un nouveau paragraphe. Laissez vide pour utiliser le texte standard affiché en gris. Jusqu'à 5 000 caractères. |
| **Enregistrer** | Enregistre les deux réglages et affiche **Confirmation d'inscription enregistrée.** |

L'e-mail part à l'adresse e-mail enregistrée sur chaque membre inscrit,
jamais à une adresse saisie dans le formulaire du site web. Son objet est
« RE : votre inscription à la journée de travail du » suivi de la date.
Sous votre texte, Parcella ajoute le titre, la date et l'heure de la
session, et -- seulement si le nom correspondait exactement à un membre
-- les remarques saisies par le visiteur (jusqu'à 500 caractères). Si
l'envoi échoue, l'inscription est quand même conservée.

### Configurations historiques {#historical-configurations}

Toutes les années configurées, la plus récente en premier.

| Colonne | Ce qu'elle affiche / fait |
|---|---|
| **Année**, **Heures**, **Tarif** | Les réglages de l'année. |
| **Max. dû** | Heures × tarif. |
| **Mode** | **Location** ou **Membre**. |
| **Note** | Votre note. |
| Crayon | Ouvre [Modifier la configuration](#edit-configuration). Nécessite le droit d'écriture. |
| Corbeille | Supprime la configuration de l'année après confirmation. Nécessite le droit de suppression. Les sessions, parrainages et transferts restent, mais l'année ne peut plus être évaluée ni facturée. |

## Modifier la configuration {#edit-configuration}

![Modifier la configuration](../assets/screenshots/work-hours/configuration-form.png)

S'ouvre avec le crayon à côté d'une année. Les champs sont les mêmes
que ci-dessus -- **Année**, **Total des heures obligatoires**, **Tarif
horaire**, **Mode de facturation** et **Note** -- avec **Annuler** et
**Enregistrer les modifications**. Vous pouvez changer l'année
elle-même ; si une autre configuration existe déjà pour la nouvelle
année, Parcella refuse avec **Une configuration différente existe déjà
pour ...**.

!!! warning
    Changer les heures, le tarif ou le mode change immédiatement
    l'évaluation de cette année. Si des factures ont déjà été créées
    pour l'année, elles ne sont pas mises à jour.

<!-- TODO(verify): confirm that already-created invoices keep their amounts when the work-hours configuration changes afterwards. -->

## Voir aussi {#related}

- [Organiser une session de travail](../guides/work-session.md) -- pas à
  pas de la planification à la facturation
- [Établir les factures annuelles](../guides/annual-invoicing.md) et
  [Séries de factures](finances/invoice-runs.md) -- facturer les heures
  manquantes
- [Membres](members.md) et [Parcelles](parcels.md) -- les baux
  déterminent qui doit des heures
- [Calendrier](calendar.md) -- les sessions Standard apparaissent aussi
  dans le calendrier communautaire
- [Intégrations](../administration/integrations.md) -- connecter le
  formulaire d'inscription du site web de l'association
- [Journal des e-mails](../administration/email-log.md) -- vérifier si
  les e-mails de notification et de confirmation sont partis

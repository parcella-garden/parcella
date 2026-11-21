# Organiser une session de travail {#organising-a-work-session}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

La plupart des associations demandent à chaque parcelle (ou à chaque
membre) d'effectuer chaque année un certain nombre
d'[heures obligatoires](../glossary.md#mandatory-hours) de travaux
collectifs -- taille des haies, réparation des chemins, grand nettoyage
de printemps. Ce guide suit une
[session de travail](../glossary.md#work-session) de la planification à
l'évaluation de fin d'année : la créer, laisser les membres s'inscrire
sur le site web de l'association, enregistrer qui est réellement venu,
et voir qui doit encore des heures.

!!! info "Qui peut le faire"
    Créer des sessions et enregistrer les présences nécessite le droit
    d'**écriture** sur **Sessions de travail** ; retirer un participant
    ou un transfert nécessite la **suppression**. Le module (**Gestion
    des heures de travail**) est activé par défaut. La publication sur
    le site web nécessite un administrateur pour la configuration unique
    de l'étape 3.

## 1. Fixer les règles de l'année (une fois par an) {#1-set-the-years-rules-once-a-year}

1. Ouvrez **Sessions de travail → Sessions & Aperçu**. Si l'année n'a
   pas encore de règles, la page indique *« Pas encore de configuration
   des heures obligatoires pour … »* -- cliquez sur **Créer maintenant →**
   (ou sur **Configuration des heures** en bas).
2. Sous **Créer / Mettre à jour l'année**, saisissez :
    - **Année**
    - **Total des heures obligatoires** -- les heures dues par an ;
    - **Tarif horaire** -- ce que coûte une heure non effectuée ;
    - **Mode de facturation** -- **Par location / parcelle** (tous les
      locataires d'une parcelle effectuent les heures ensemble) ou
      **Par membre** (chaque membre pour lui-même) ;
    - éventuellement une **Note**, par ex. la décision de l'assemblée
      générale.
3. Cliquez sur **Enregistrer**.

Sur la même page, la carte **E-mail de confirmation d'inscription**
gère l'e-mail que reçoivent les membres après leur inscription sur le
site web (étape 3).

**Exemptions.** Les membres du bureau, les personnes ayant des raisons
de santé ou au-delà d'une limite d'âge sont souvent exemptés.
Configurez cela sous **Sessions & Aperçu → Rôles du club** : créez un
rôle avec **Exempté des heures obligatoires** et un **Motif de
l'exemption**, puis attribuez-y des membres pour l'année. Si un
locataire d'une parcelle est exempté, toute la parcelle est exemptée ;
une exemption vaut pour toute l'année civile.

## 2. Créer la session {#2-create-the-session}

1. Ouvrez **Sessions de travail → Sessions & Aperçu** et cliquez sur
   **Nouvelle session**.
2. Renseignez :
    - **Titre**, par ex. « Nettoyage de printemps » ;
    - **Type** : **Standard (planifié)** pour les sessions que vous
      annoncez, ou **Spécial (spontané)** pour celles qui ne sont pas
      prévues -- les sessions spéciales n'apparaissent jamais sur le
      site web ;
    - **Date**, **De** et **Jusqu'au** ;
    - **Max. participants** -- laissez vide pour illimité ;
    - **Date limite d'inscription (jours avant)** -- l'inscription sur le
      site web ferme ce nombre de jours avant la session (1 = la veille) ;
      vide signifie qu'elle ferme une fois la session passée ;
    - **Heures par participant** -- créditées à chaque personne
      présente, ajustables individuellement ensuite ;
    - **Description** -- tâches, outils, quoi apporter.
3. Cliquez sur **Créer une session**.

La session est listée sous **Sessions de travail …** pour son année.

## 3. Publier l'inscription sur le site web de l'association (configuration unique) {#3-publish-the-sign-up-on-the-club-website-one-time-setup}

Les membres s'inscrivent sur le site web de l'association avec leur
**numéro de parcelle** et, éventuellement, leur nom -- sans connexion à
Parcella. Le site web n'affiche jamais quels membres occupent quelle
parcelle.

Un administrateur configure cela une fois :

1. **Administration → Paramètres → Domaines fonctionnels** : cochez
   **API publique d'inscription** et cliquez sur **Enregistrer les
   paramètres**. Elle est désactivée par défaut car elle ouvre un
   formulaire public.
2. **Administration → Intégrations → API publique d'inscription** :
   notez le **Jeton API** (pour un connecteur côté serveur) et ajoutez
   votre site web sous **Adresses de sites autorisées** (par ex.
   `https://example.org`), puis **Enregistrer les adresses**. Cochez
   éventuellement **Exiger ALTCHA** contre le spam.
3. Sur le site web, ajoutez le formulaire d'inscription -- avec
   l'extension Parcella Connector pour WordPress, ou un simple
   formulaire HTML pour tout autre site. Votre webmestre trouvera les
   détails dans la documentation développeur.
   <!-- TODO(verify): link to the gardeners/website-form instructions once that page exists. -->

Ensuite, chaque nouvelle session **Standard** apparaît d'elle-même sur
le site web, tant que sa date n'est pas passée, que sa date limite
d'inscription n'est pas dépassée et qu'elle n'est pas complète.

**Ce qui se passe lors d'une inscription.** Parcella recherche les
locataires actuels de la parcelle. Si le nom saisi correspond
exactement à l'un d'eux, seul ce membre est inscrit. Si aucun nom n'a
été donné ou s'il ne correspond pas clairement, **tous** les locataires
actuels de la parcelle sont inscrits, avec une note demandant au bureau
de vérifier -- retirez ceux qui ne se sont pas réellement inscrits.
Chaque membre nouvellement inscrit reçoit l'e-mail de confirmation à
l'adresse enregistrée dans Parcella (pas celle saisie dans le
formulaire).

Plus d'informations : [Intégrations](../administration/integrations.md)
et [Pour les jardiniers](../gardeners/index.md).

## 4. Surveiller les inscriptions {#4-keep-an-eye-on-sign-ups}

- Les nouvelles inscriptions affichent un compteur à côté de **Sessions
  de travail** dans la barre latérale et sur le tableau de bord.
- Ouvrez la session (cliquez dessus dans la liste de **Sessions &
  Aperçu**). Les nouveaux participants portent un badge **Nouveau**. Une
  fois que vous les avez vus, cliquez sur **Marquer comme vu**.
- Vérifiez la colonne **Note** : les inscriptions par le site web y
  portent les remarques et coordonnées du visiteur, et un avertissement
  si toute la parcelle a été inscrite.
- Pour ajouter quelqu'un à la main (inscription par téléphone), utilisez
  **Sélectionner un membre…** en bas du tableau des participants,
  choisissez **Inscrit** et cliquez sur **Ajouter**.

**Tâches (facultatif).** Si vous tenez une liste de travaux sous
**Sessions de travail → Tâches**, planifiez-en quelques-uns pour cette
session. Sur la page de la session, vous pouvez ensuite attribuer
chacun à un participant (**Attribuée à**) et voir sa **Charge de
travail** (**Légère**, **Modérée**, **Exigeante**). **Gérer les tâches**
mène à la liste complète.

## 5. Le jour J : imprimer la feuille de présence {#5-on-the-day-print-the-attendee-sheet}

1. Ouvrez la session et cliquez sur **Liste des participants**.
2. Imprimez le PDF. Il liste chaque participant inscrit avec parcelle,
   nom, heures prévues, tâche attribuée et une ligne de signature.

Corrigez les heures sur papier si nécessaire ; vous les saisirez
ensuite. La feuille ne change rien dans Parcella.

## 6. Ensuite : enregistrer les présences {#6-afterwards-record-attendance}

1. Ouvrez la session.
2. Pour chaque participant, choisissez **Présent** ou **Absent** dans la
   liste déroulante **Statut**. C'est enregistré immédiatement.
3. Si quelqu'un a travaillé plus ou moins que les **Heures par
   participant**, tapez les heures réelles dans son champ **Heures** et
   cliquez sur le bouton ✓.
4. Les personnes venues sans s'inscrire : **Sélectionner un membre…**,
   statut **Présent**, leurs heures, **Ajouter**.
5. Utilisez le champ de recherche au-dessus du tableau pour trouver
   quelqu'un par nom ou numéro de parcelle.

Seules les participations **Présent** comptent pour les heures.

## 7. Parrainages et transferts d'heures {#7-sponsorships-and-hours-transfers}

Les **[parrainages](../glossary.md#sponsorship)** sont des zones dont un
membre s'occupe toute l'année (une haie, l'aire de jeux) au lieu de
venir aux sessions, ou en plus.

1. Ouvrez **Sessions de travail → Parrainages**.
2. Sous **Créer un parrainage / Ajouter un membre**, saisissez la
   **Zone**, le **Membre** (ou laissez **– pas encore attribué –** pour
   d'abord proposer la zone), une **Description**, les **Heures
   créditées/an** et **Valable du** / **Valable jusqu'au**.
3. Cliquez sur **Enregistrer**.

Un parrainage ne crédite des heures qu'une fois qu'il a une date
**Valable du** et un membre. Plusieurs membres peuvent partager une
zone -- ajoutez une ligne par membre avec le même nom de zone ; chacun
reçoit le crédit complet.

**[Transferts d'heures](../glossary.md#hours-transfer)** : un membre qui
a fait plus que le nécessaire peut donner des heures à quelqu'un
d'autre.

1. Ouvrez **Sessions de travail → Transferts d'heures**.
2. Sous **Donner des heures**, choisissez **De (donne)**,
   **À (reçoit)**, les **Heures** et éventuellement une **Note**.
3. Cliquez sur **Transférer les heures**.

Seul l'excédent du donneur pour l'année peut être donné. Les membres
sans parcelle et les membres exemptés peuvent donner toutes leurs
heures.

## 8. L'évaluation de fin d'année {#8-the-year-end-evaluation}

1. Ouvrez **Sessions de travail → Évaluation annuelle** et choisissez
   l'année.
2. Chaque ligne est une parcelle (ou un membre, selon le **Mode de
   facturation**) avec **Requis**, **Sessions**, **Parrainage**,
   **Transferts**, **Total**, **Ouvert** et **Dû**, et un **Statut**
   **Réalisé**, **Ouvert** ou **Exempté**.
3. Cliquez sur la flèche au début d'une ligne (**Afficher les sessions
   de travail**) pour voir de quelles sessions viennent les heures.
4. **Export CSV** télécharge l'évaluation.

Les locataires partis en cours d'année doivent encore les heures de
cette année ; leur ligne porte un badge « bail terminé le … ».

Pour facturer les heures manquantes, ajoutez un article **Déficit
d'heures de travail (depuis le module)** à la série de factures
annuelle -- voir [Établir les factures annuelles](annual-invoicing.md).

## Voir aussi {#related}

- [Heures de travail](../modules/work-hours.md)
- [Calendrier](../modules/calendar.md)
- [Intégrations](../administration/integrations.md)
- [Établir les factures annuelles](annual-invoicing.md)
- Glossaire : [heures obligatoires](../glossary.md#mandatory-hours),
  [exemption](../glossary.md#exemption),
  [parrainage](../glossary.md#sponsorship),
  [transfert d'heures](../glossary.md#hours-transfer)

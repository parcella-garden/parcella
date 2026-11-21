# Transmettre une parcelle {#handing-over-a-parcel}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Un locataire donne son congé, la parcelle est visitée et estimée,
proposée à la liste d'attente, et finalement un nouveau locataire signe
et reçoit les clés. Cela prend des semaines ou des mois et implique
plusieurs membres du bureau. Ce guide montre ce que Parcella enregistre
en chemin et comment une [procédure](../glossary.md#process) suit les
étapes qu'il n'enregistre pas de lui-même.

## Ce que Parcella suit -- et ne suit pas {#what-parcella-does-and-doesnt-track}

| Étape de la transmission | Dans Parcella |
|---|---|
| Le congé | Statut de la parcelle **résilié**, avec la date enregistrée automatiquement et une **Note de résiliation** facultative. |
| Anciens et nouveaux locataires | Terminer l'ancien [bail](../glossary.md#tenancy) le conserve dans l'historique ; le nouveau bail commence à la date de remise. **Attribuer une parcelle** sur une candidature fait les deux en une étape. |
| L'adhésion de l'ancien locataire | Se termine automatiquement avec **Attribuer une parcelle** s'il n'a pas d'autre parcelle. |
| Dossier de documents | Le dossier cloud des anciens locataires est retiré à la date de remise ; un nouveau prend le relais. |
| État des lieux, [estimation](../glossary.md#valuation), offre, visite, contrat, clés | Pas intégré. Suivez-les avec une **procédure** (étape 1). |
| [Caution](../glossary.md#deposit) | Pas de fonction de caution. Notez le montant et la date dans la procédure ; enregistrez l'argent dans **Finances** si vous l'utilisez (étape 7). |
| Relevés de compteurs finaux | Parcella conserve **un relevé par compteur et par an**. Notez les relevés de remise dans la procédure (étape 6). |
| Prix entre ancien et nouveau locataire | **Volontairement non suivi.** Ce que le nouveau locataire paie à l'ancien pour l'abri de jardin et les plantations est une affaire privée entre eux deux. Parcella n'a pas de champ pour cela -- n'en ajoutez pas non plus à votre modèle de procédure. |

!!! info "Qui peut le faire"
    Les modifications de parcelles et de baux nécessitent l'**écriture**
    sur **Membres et parcelles** ; **Attribuer une parcelle** nécessite
    aussi l'**écriture** sur **Candidats**. Les modèles de procédure
    nécessitent l'accès complet (bureau ou administrateur) ; travailler
    sur une procédure nécessite l'**écriture** sur **Procédures**.

## 1. Préparer un modèle de procédure de transmission (une fois) {#1-prepare-a-handover-process-template-once}

Le module **Procédures** comprend un modèle d'exemple **Passation de
parcelle**. Partez de celui-ci et adaptez-le au déroulement de votre
association.

1. Ouvrez **Procédures → Modèles** (la page s'appelle **Modèles de
   procédure**).
2. Sous **Partir d'un exemple**, cliquez sur **Utiliser** à côté de
   **Passation de parcelle**. Parcella crée un modèle ordinaire que vous
   pouvez modifier librement. Il porte sur une **Parcelle** : chaque
   procédure appartient donc à une parcelle et apparaît sur la page de
   celle-ci.
3. L'exemple a six étapes : **Visite**, **Estimation**, **Annonce**,
   **Nouveau locataire**, **Contrat et caution** et **Remise**. Pour
   correspondre au déroulement habituel ci-dessous, ajoutez et renommez
   des étapes dans l'éditeur (tapez un **Nom de l'étape** et cliquez sur
   **Ajouter** ; faites glisser les étapes pour les réordonner ; ajoutez
   des champs en tapant un libellé et en appuyant sur Entrée) :

| Étape | Exemples de champs | Type de champ |
|---|---|---|
| Congé *(nouvelle, en premier)* | Congé reçu le (obligatoire) · Lettre de congé | Date · Fichiers (PDF, photos) |
| **Visite** | **Date de la visite** · **Défauts constatés** · **Photos des défauts** · **Tous les défauts corrigés** | de l'exemple |
| **Estimation** | **Expert** · **Date de l'estimation** · **Rapport d'estimation** | de l'exemple |
| **Annonce** → renommer en « Offre à la liste d'attente » | **Texte de l'annonce** · **Publiée le** | de l'exemple |
| Visite des candidats *(nouvelle)* | Date de visite · Candidats intéressés (notes) | Date · Texte long |
| **Nouveau locataire** | **Nouveau locataire** (un candidat) · **Contact établi** · **Documents envoyés** | de l'exemple |
| **Contrat et caution** | **Contrat de vente confirmé** · **Caution** · **Caution reçue le** | de l'exemple |
| **Remise** → scinder en « Signature » et « Liste de contrôle finale » | Signature : **Signé par le nouveau locataire**, **Contresigné par le bureau**. Liste de contrôle finale : **Clés remises**, **Compteurs relevés**, **Procès-verbal de remise** | de l'exemple |

4. Dans l'étape « Liste de contrôle finale », ajoutez des champs
   **Nombre** pour les relevés de compteurs à la remise, par ex.
   « Relevé du compteur d'eau à la remise » et « Relevé du compteur
   d'électricité à la remise » (voir étape 6).

Marquez un champ **Obligatoire** si la procédure ne doit pas avancer
sans lui. Les modifications d'un modèle ne concernent que les
procédures démarrées ensuite.

!!! tip
    **Contrat de vente confirmé** n'est qu'une case à cocher : le bureau
    confirme que l'ancien et le nouveau locataire se sont mis d'accord.
    Le prix lui-même reste entre eux deux.

Plus d'informations : [Procédures](../modules/processes.md).

## 2. Enregistrer le congé {#2-record-the-notice}

Quand le congé du locataire arrive :

1. Ouvrez la parcelle sous **Parcelles** et cliquez sur **Modifier**.
2. Réglez **Statut** sur **résilié**. Parcella enregistre l'heure du
   changement de statut ; la page de la parcelle affiche ensuite
   **Résilié le**.
3. Ajoutez éventuellement une **Note de résiliation** (motif, date du
   congé, remarques).
4. Cliquez sur **Enregistrer les modifications**.

Le locataire reste un locataire actuel -- et continue de recevoir les
factures de la parcelle -- jusqu'à la fin effective du bail. Ne terminez
pas le bail maintenant ; **Attribuer une parcelle** le fait à la date de
remise (étape 5).

## 3. Démarrer la procédure {#3-start-the-process}

1. Sur la page de la parcelle, dans la carte **Procédures**, cliquez sur
   **Démarrer une procédure**.
2. Choisissez votre **Modèle** de transmission. Donnez éventuellement un
   **Titre** à la procédure.
3. Cliquez sur **Démarrer**.
4. Remplissez les champs de la première étape et cliquez sur
   **Enregistrer**. Quand l'étape est terminée, cliquez sur **Fait --
   étape suivante**.

La procédure apparaît sur la page de la parcelle avec son étape
actuelle, et dans **Procédures** pour tous ceux qui y travaillent. Les
fichiers que vous téléversez (courriers, photos, rapport d'estimation)
vont dans le dossier cloud de la parcelle s'il est défini, sinon dans le
stockage propre de Parcella.

Pour revenir à une étape précédente, cliquez sur **Revenir en arrière**,
choisissez l'étape et indiquez un **Motif**. Si la transmission échoue,
**Interrompre la procédure** avec un motif.

## 4. État des lieux, estimation, offre, visite {#4-inspection-valuation-offer-viewing}

Avancez dans ces étapes de la procédure au fur et à mesure. Le rapport
d'[estimation](../glossary.md#valuation) va dans **Rapport
d'estimation** ; le texte de l'offre dans **Texte de l'annonce**.

Pour trouver des personnes intéressées, ouvrez **Candidats** avec le
filtre **Ouvert** -- la liste est triée par date de candidature. Passez
ceux à qui vous proposez la parcelle à **Parcelle proposée**, et celui
qui la prend à **Acceptée**. Avec le module **Annonces** activé, cochez
plusieurs candidats et cliquez sur **Écrire aux candidats
sélectionnés** pour envoyer l'offre par e-mail.

Plus d'informations : [Candidats](../modules/applicants.md).

## 5. Remettre la parcelle au nouveau locataire {#5-hand-the-parcel-over-to-the-new-tenant}

Une fois le contrat signé -- ou, avec une date future, dès qu'elle est
fixée :

1. Ouvrez la candidature du nouveau locataire et cliquez sur
   **Attribuer une parcelle**.
2. Choisissez cette parcelle sous **Parcelle résiliée** et fixez la
   **Date de remise**.
3. Ajoutez un conjoint sous **Autres candidats (co-locataires)** s'ils
   reprennent la parcelle ensemble.
4. Si vous utilisez le stockage cloud, saisissez le **Dossier de
   documents pour les nouveaux locataires**. Le dossier des anciens
   locataires est retiré à la date de remise dans tous les cas.
5. Cliquez sur **Aperçu**, vérifiez les anciens et nouveaux locataires,
   puis cliquez sur **Remettre la parcelle** et confirmez.

À la date de remise :

- l'ancien bail se termine et passe sous **Anciens locataires** sur la
  page de la parcelle ;
- un ancien locataire sans autre parcelle quitte l'association
  (**Membre jusqu'au** est la veille de la date de remise) ;
- les candidats deviennent membres, locataires et destinataires des
  factures ;
- la parcelle est de nouveau **actif**.

Voir [Accueillir un nouveau membre](new-member.md), étapes 5 et 6, pour
les détails et pour compléter la fiche du nouveau membre.

### Si le nouveau locataire n'est pas un candidat {#if-the-new-tenant-isnt-an-applicant}

Par exemple un membre de la famille qui reprend la parcelle. Faites-le
à la main :

1. Sur la page de la parcelle, dans **Locataires actuels**, cliquez sur
   l'icône crayon à côté de l'ancien locataire (**Modifier la
   location**), réglez **Locataire jusqu'au** sur le dernier jour et
   cliquez sur **Enregistrer les modifications**. Ou, pour y mettre fin
   aujourd'hui, cliquez sur l'icône **Mettre fin à la location** et
   confirmez *« Mettre fin à cette location ? (l'historique est
   conservé) »*.
2. Si l'ancien locataire quitte l'association, ouvrez sa page de membre,
   cliquez sur **Modifier**, réglez **Membre jusqu'au** et cliquez sur
   **Enregistrer les modifications**. Ne le supprimez pas -- voir
   l'avertissement ci-dessous.
3. Attribuez le nouveau locataire : **Choisir un membre…**, la date de
   début, **Utiliser comme adresse de facturation**, **Attribuer**.
   Créez-le d'abord sous **Membres → Nouveau membre** si nécessaire.
4. Modifiez la parcelle et repassez **Statut** à **actif**.

!!! tip "Enregistrer un congé"
    Un locataire qui a donné son congé reste l'adresse de facturation
    jusqu'à son départ : réglez son **Locataire jusqu'au** dans
    **Modifier la location** et laissez **Utiliser comme adresse de
    facturation** coché. Une fois ce jour passé, la case se décoche
    d'elle-même -- assurez-vous que le nouveau locataire est l'adresse
    de facturation d'ici là.

!!! warning "Terminer, pas supprimer"
    Terminer un bail ou une adhésion conserve l'historique : qui avait
    quelle parcelle et quand, et quelles heures et factures
    appartenaient à qui. Supprimer un membre le retire de toutes les
    évaluations, y compris les heures de travail des années où il était
    locataire.

## 6. Relevés de compteurs finaux {#6-final-meter-readings}

Parcella enregistre un relevé par compteur et par an, et c'est sur ce
relevé que se base la facture annuelle. Il n'y a pas de « relevé de
remise » séparé.

- Notez les relevés du jour de la remise dans la procédure (l'étape
  « Liste de contrôle finale » de l'étape 1) et cochez **Compteurs
  relevés**.
- Ne les saisissez pas comme relevé de l'année sur le point de mesure,
  sauf si c'est vraiment ce que vous voulez : le relevé annuel effectué
  plus tard dans l'année le **remplace**.
- La facture annuelle d'eau et d'électricité de la parcelle va à la
  personne qui est destinataire des factures au moment de la
  finalisation de la [série de factures](../glossary.md#invoice-run) --
  après une transmission, le nouveau locataire -- pour la consommation
  de toute l'année. La façon dont l'ancien et le nouveau locataire se
  la partagent dépend d'eux et des règles de votre association ;
  réglez-la en dehors de Parcella, à l'aide des relevés de la procédure.

Si un compteur est changé lors de la remise, voir
[Relever les compteurs](meter-readings.md#a-meter-is-replaced).

## 7. Caution et argent {#7-deposit-and-money}

Parcella n'a pas de champ de caution sur la parcelle ou le membre.
Utilisez la procédure pour en garder trace : **Caution** (montant) et
**Caution reçue le** dans l'étape **Contrat et caution**.

Si vous utilisez le module **Finances**, enregistrez aussi l'argent
lui-même :

- **Caution reçue** : ouvrez **Finances → Aperçu → Comptes**, cliquez
  sur **Écritures** à côté du compte sur lequel l'argent est arrivé, et
  utilisez **Ajouter une écriture** (ou **Importer CSV** avec votre
  relevé bancaire).
- **Restitution de la caution de l'ancien locataire** : de la même
  façon, avec un montant négatif.

<!-- TODO(verify): confirm with the treasurer whether a deposit should rather be billed as a one-off invoice run (a "Fixed amount per parcel" item scoped to this parcel) so it gets an invoice number. -->

**Heures de travail.** Un locataire qui part en cours d'année doit
encore les [heures obligatoires](../glossary.md#mandatory-hours) de
cette année. Avec une facturation par parcelle, ses heures comptent avec
celles du nouveau locataire, et un déficit est facturé au destinataire
des factures de la parcelle au moment de la série de factures -- le
nouveau locataire. Si ce n'est pas ce que veut votre association,
réglez-le à la main. Voir [Établir les factures annuelles](annual-invoicing.md).

**Les factures ouvertes** de l'ancien locataire restent telles quelles ;
le numéro de facture, le destinataire et l'adresse sont conservés sur
chaque facture, vous pouvez donc toujours encaisser et relancer.

## 8. Clôturer la procédure {#8-close-the-process}

Quand la dernière étape est terminée, cliquez sur **Terminer la
procédure**. Une procédure terminée est en lecture seule et reste sur la
page de la parcelle, avec son **Historique** complet.

## Voir aussi {#related}

- [Parcelles](../modules/parcels.md)
- [Candidats](../modules/applicants.md)
- [Membres](../modules/members.md)
- [Procédures](../modules/processes.md)
- [Eau et électricité](../modules/metering.md)
- [Comptes bancaires et écritures](../modules/finances/bank-accounts.md)
- [Accueillir un nouveau membre](new-member.md)
- Glossaire : [caution](../glossary.md#deposit),
  [estimation](../glossary.md#valuation),
  [résiliation](../glossary.md#notice-of-termination),
  [bail](../glossary.md#tenancy)

# Glossaire {#glossary}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les termes de l'association et de Parcella, par ordre alphabétique.

Les chapitres renvoient directement à une entrée, par exemple
`glossary.md#deposit`.

## Actif, résilié, communale, supprimé { #parcel-status }

Les quatre statuts d'une [parcelle](#parcel) :

- **actif** -- une parcelle normale, généralement louée à quelqu'un.
- **résilié** -- le locataire a donné son [congé](#notice-of-termination)
  et la parcelle est en voie de passer à un nouveau locataire. Seules
  les parcelles résiliées peuvent être transmises à un
  [candidat](#applicant).
- **communale** -- terrain de l'association suivi comme une parcelle
  (chemins, aire de jeux), jamais loué. Il ne compte pas dans la
  superficie louée.
- **supprimé** -- plus utilisée, mais conservée avec son historique.

## Adresse de facturation { #invoice-address }

Le locataire d'une parcelle à l'adresse duquel partent les factures de
la parcelle -- **Utiliser comme adresse de facturation** sur le bail.
Plusieurs locataires d'une même parcelle peuvent l'avoir ; la parcelle
reçoit tout de même une seule facture. Une parcelle sans adresse de
facturation ne reçoit pas de facture.

## Ancien, actuel et futur locataire { #former-tenant }

Un [bail](#tenancy) est **actuel** tant qu'il court, **à venir** s'il
commence à une date future (après une transmission à date future), et
**ancien** une fois terminé. Les anciens locataires restent sur la page
de la parcelle sous **Anciens locataires** ; seuls les locataires
actuels (et à venir) peuvent être l'[adresse de facturation](#invoice-address).

## Bail { #tenancy }

La location d'une parcelle par un membre, d'une date de début à une
date de fin facultative. Terminer un bail le conserve dans l'historique ;
plusieurs membres peuvent partager une parcelle. Voir aussi
[ancien locataire](#former-tenant).

## Bureau { #board }

Le bureau élu de l'association. Dans Parcella, les membres du bureau ont
généralement un accès complet à chaque module. Vous indiquez le bureau
actuel sous **Administration → Paramètres → Membres du bureau** ; leur
accès vient d'un [groupe](#group) avec **Accès complet à chaque module**
(ou, pour les anciens comptes, du rôle **Conseil d'administration**).

## Candidat { #applicant }

Une personne qui a demandé un jardin et figure sur la
[liste d'attente](#waiting-list). Les candidats sont tenus à part des
[membres](#member) : ils ne deviennent membres que lorsqu'ils obtiennent
réellement une parcelle. Voir [Candidats](modules/applicants.md).

## Catalogue d'articles { #item-catalog }

Votre liste de lignes de facture réutilisables (loyer, eau, assurance,
...), reprises dans la [série de factures](#invoice-run) de chaque année.
Se trouve sous **Finances → Aperçu → Catalogue d'articles**.

## Caution { #deposit }

Une somme que le nouveau locataire verse en reprenant une parcelle, que
l'association conserve et rembourse -- ou dont elle garde une partie --
quand le locataire s'en va. Parcella n'a pas de fonction de caution à
part : notez le montant et la date dans la [procédure](#process) de
transmission et enregistrez l'argent dans **Finances**. Voir
[Transmettre une parcelle](guides/parcel-handover.md#7-deposit-and-money).

## Charges publiques { #public-burdens }

Les charges que le propriétaire du terrain répercute sur l'association
-- taxe foncière, nettoyage des rues et autres redevances communales
similaires -- généralement au mètre carré. L'association les répercute
sur les parcelles, y compris une part pour le terrain commun. Dans
l'application : **Charges publiques (surface propre + part de la
surface commune)** : la surface propre de la parcelle plus sa part égale
de la [superficie B](#areas), multipliées par le taux que vous saisissez.

## Compteur { #meter }

Le compteur d'eau ou d'électricité physique, avec son numéro, son année
d'étalonnage et son relevé initial. Un [point de mesure](#metering-point)
a un compteur à la fois ; quand il est remplacé, l'ancien est conservé
comme ancien compteur.

## Compteur principal { #main-meter }

Le compteur où l'association reçoit l'eau ou l'électricité du
fournisseur. Sa consommation devrait correspondre à peu près à la somme
de tous les compteurs des parcelles et de l'association ; Parcella
avertit si les parcelles ont consommé davantage au total.

## Contact externe { #external-contact }

Un fournisseur, un artisan, une administration ou un autre organisme
avec lequel l'association est en relation -- une entreprise et/ou une
personne de contact. Pas un membre. Voir
[Contacts externes](modules/external-contacts.md).

## Cotisation générale { #general-levy }

Un montant ponctuel que l'association doit réunir auprès de toutes les
parcelles ensemble -- une facture d'avocat, une réparation, une hausse
de prime d'assurance -- réparti à parts égales. Dans l'application :
**Cotisation générale (répartie également entre toutes les parcelles)**.
Vous saisissez le montant *total* comme prix unitaire ; Parcella le
divise par le nombre de parcelles facturées et place chaque part sur la
facture de la parcelle.

## Demande d'achat { #purchase-request }

Une demande de dépense de l'argent de l'association, qui nécessite une
[double approbation](#two-person-approval) avant l'achat. Voir
[Demandes d'achat](modules/purchase-requests.md).

## Données d'exemple { #sample-data }

Des membres, parcelles et autres enregistrements fictifs que vous
pouvez ajouter à une nouvelle installation pour essayer Parcella, et
supprimer en un clic. Voir [Données d'exemple](administration/sample-data.md).

## Double approbation { #two-person-approval }

Une [demande d'achat](#purchase-request) n'est approuvée qu'une fois que
deux membres du bureau différents l'ont approuvée -- et aucun des deux
ne peut être la personne qui l'a demandée. Un seul membre du bureau
peut la refuser.

## Droit { #permission }

Ce qu'un utilisateur peut faire dans un [module](#module) : **Lecture**
(consulter), **Écriture** (ajouter et modifier) ou **Suppression**.
Toute personne pouvant se connecter peut consulter les membres et les
parcelles. Voir
[Rôles, groupes et droits](getting-started/roles-and-permissions.md).

## Estimation { #valuation }

L'évaluation par un expert de la valeur de l'abri de jardin, des
plantations et des aménagements d'une parcelle quand le locataire s'en
va. Parcella ne la calcule pas ; vous conservez le rapport dans la
[procédure](#process) de transmission.

## Étalonnage { #calibration }

Les compteurs d'eau et d'électricité ne peuvent servir à la facturation
que jusqu'à l'expiration de leur étalonnage. Parcella enregistre l'année
dans **Étalonné jusqu'au** et signale les compteurs expirés par
**Étalonnage expiré**. La solution habituelle est de
[remplacer le compteur](guides/meter-readings.md#a-meter-is-replaced).

## État des lieux { #inspection }

La visite d'une parcelle par le bureau quand un locataire s'en va, pour
noter les défauts avant l'[estimation](#valuation). Suivi dans une
[procédure](#process) de transmission.

## Étiquette { #tag }

Un libellé libre sur un membre, comme « équipe haies » ou « responsable
eau », pour retrouver et filtrer des personnes. Les étiquettes existent
aussi pour les contacts externes.

## Exemption { #exemption }

Un membre qui n'a pas à effectuer d'[heures obligatoires](#mandatory-hours)
une année donnée -- généralement en raison d'un [rôle du club](#club-role),
de sa santé ou de son âge. Si un locataire d'une parcelle est exempté,
toute la parcelle est exemptée, et une exemption vaut toujours pour
l'année civile entière.

## Facteur { #factor }

Un multiplicateur sur un [point de mesure](#metering-point) pour les
compteurs qui n'affichent qu'une fraction de la valeur réelle (par
exemple 20 pour un compteur d'électricité avec transformateurs de
courant). Les relevés sont saisis tels qu'affichés ; l'évaluation les
multiplie par le facteur. Généralement 1.

## Groupe { #group }

Un ensemble de [droits](#permission) dans Parcella -- lecture, écriture
ou suppression par [module](#module), ou accès complet -- que vous
attribuez à des comptes utilisateurs. Les nouveaux utilisateurs
reçoivent leurs accès uniquement via des groupes. Voir
[Groupes](administration/groups.md).

## Heures obligatoires { #mandatory-hours }

Les heures de travail collectif qu'une parcelle ou un membre doit
chaque année à l'association, selon la décision de l'assemblée
générale. Les heures non effectuées sont payées selon un taux horaire.
Parcella y impute les [sessions de travail](#work-session) suivies, les
[parrainages](#sponsorship) et les [transferts d'heures](#hours-transfer),
et le manque peut être facturé dans la [série de factures](#invoice-run)
annuelle. Voir [Heures de travail](modules/work-hours.md).

## Liste d'attente { #waiting-list }

Les [candidats](#applicant) qui attendent une parcelle, dans l'ordre de
leur candidature. Dans Parcella : **Candidats** avec le filtre
**Ouvert**.

## Locataire { #tenant }

Un membre titulaire d'un [bail](#tenancy) sur une parcelle.

## Lot d'impression { #print-bundle }

Un seul PDF avec toutes les factures d'une série dont le destinataire
ne peut pas être joint par e-mail, prêt à imprimer et à poster.

## Membre { #member }

Une personne qui fait partie de l'association. Généralement aussi
[locataire](#tenant), mais pas forcément (membres bienfaiteurs ou
d'honneur). Un membre compte comme actif jusqu'à sa date
**Membre jusqu'au**.

## Module { #module }

Un domaine fonctionnel de Parcella -- Heures de travail, Eau, Finances,
Procédures, etc. -- qui peut être activé ou désactivé pour votre
association sous **Administration → Paramètres → Domaines
fonctionnels**. En désactiver un le masque ; ses données restent. Voir
[Activer et désactiver les modules](administration/modules.md).

## Parcelle { #parcel }

Un jardin, identifié par son **Numéro de parcelle**.

## Parrainage { #sponsorship }

Un membre entretient une partie du terrain de l'association -- une haie,
l'aire de jeux -- pendant l'année et se voit créditer pour cela un
nombre fixe d'[heures obligatoires](#mandatory-hours). Voir
**Sessions de travail → Parrainages**.

## Part de la surface commune { #communal-area-share }

Un article de facture qui facture le loyer du terrain commun de
l'association ([superficie B](#areas)), réparti à parts égales entre les
parcelles concernées. Dans l'application : **Part du bail de la surface
commune**.

## Point de mesure { #metering-point }

Un endroit où l'eau ou l'électricité est mesurée : le raccordement d'une
parcelle, le [compteur principal](#main-meter), ou un raccordement de
l'association (local, aire de lavage). Le point de mesure reste ; le
[compteur](#meter) qui y est installé peut changer.

## Procédure { #process }

Une liste de contrôle pas à pas que vous concevez vous-même -- par
exemple la transmission d'une parcelle ou l'accueil d'un membre --
menée pour une parcelle, un membre ou un candidat. Chaque étape a des
champs à remplir ; les champs obligatoires doivent être remplis avant de
passer à la suite. Voir [Procédures](modules/processes.md).

## Relance { #dunning }

Rappeler à un membre une facture impayée. Dans Parcella :
**Envoyer le rappel** sur une facture en retard crée **Rappel n° 1**,
**n° 2** et ainsi de suite, avec des frais facultatifs. Il n'y a pas de
niveaux de relance fixes ; le bureau décide quand envoyer le suivant.
Voir [Factures, paiements et relances](modules/finances/invoices.md).

## Relevé { #reading }

La valeur affichée par un compteur. Parcella conserve un relevé par
[compteur](#meter) et par année ; la consommation de l'année est ce
relevé moins le précédent.

## Résiliation { #notice-of-termination }

Le congé donné par le locataire (ou par l'association) qui met fin à un
bail. Dans Parcella, vous passez le statut de la parcelle à
**résilié** ; la date est enregistrée automatiquement.

## Rôle { #role }

Les anciens comptes ont un rôle fixe (**Administrateur**, **Conseil
d'administration**, **Trésorier**, **Lecture seule**). Les nouveaux
comptes reçoivent plutôt leurs accès via des [groupes](#group). Ce n'est
pas la même chose qu'un [rôle du club](#club-role).

## Rôle du club { #club-role }

Une fonction dans l'association -- président, trésorier, responsable de
l'eau -- qu'un membre occupe pendant une année. Un rôle du club peut
[exempter](#exemption) son titulaire des
[heures obligatoires](#mandatory-hours). Se configure sous
**Sessions de travail → Sessions & Aperçu → Rôles du club**. À ne pas
confondre avec un [rôle](#role) dans Parcella.

## Série de factures { #invoice-run }

Un lot de factures, généralement les factures annuelles d'une année.
Vous ajoutez des lignes, vérifiez un aperçu, puis la **finalisez** --
ce qui attribue les numéros de facture définitifs -- et l'envoyez. Voir
[Établir les factures annuelles](guides/annual-invoicing.md).

## Session de travail { #work-session }

Une date à laquelle les membres effectuent des travaux collectifs pour
l'association, comptés dans leurs [heures obligatoires](#mandatory-hours).
Les sessions **Standard** sont planifiées et peuvent être publiées sur
le site web de l'association ; les sessions **Spécial** sont spontanées
et internes. Voir [Organiser une session de travail](guides/work-session.md).

## Superficies A, B et C { #areas }

La superficie totale de l'association divisée en trois parties,
définies sous **Administration → Paramètres → Superficies (m²)** :

- **Superficie A (parcelles, m²)** -- la somme des superficies de toutes
  les parcelles, calculée par Parcella.
- **Superficie B (communale, m²)** -- chemins, espaces verts et autres
  terrains communs de l'association : le total moins A et C, calculé par
  Parcella.
- **Superficie C (municipale, m²)** -- terrain géré par l'association
  mais appartenant à la commune, saisi à la main.

La superficie B sert de base à la
[part de la surface commune](#communal-area-share) et aux
[charges publiques](#public-burdens).

## Transfert d'heures { #hours-transfer }

Un membre qui a effectué plus d'[heures obligatoires](#mandatory-hours)
que requis cède une partie du surplus à un autre membre pour la même
année. Voir **Sessions de travail → Transferts d'heures**.

## Transmission { #handover }

Le passage d'un ancien à un nouveau locataire sur une parcelle. Dans
Parcella, **Attribuer une parcelle** sur une candidature termine
l'ancien [bail](#tenancy), fait du candidat un membre et un locataire,
et remet la parcelle à l'état actif. Voir
[Transmettre une parcelle](guides/parcel-handover.md).

## Trésorier { #treasurer }

Le membre du bureau responsable de l'argent de l'association. Dans
Parcella, donnez au trésorier un [groupe](#group) avec tous les droits
sur **Finances**.

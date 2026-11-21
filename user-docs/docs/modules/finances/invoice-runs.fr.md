# Séries de factures {#invoice-runs}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Une série de factures est un lot de factures, généralement « les
factures annuelles 2026 ». Vous décrivez une fois quelles lignes figurent
sur les factures et comment chaque montant est calculé. Parcella calcule
ensuite la facture de chaque parcelle (et de chaque membre facturé
directement), vous permet de vérifier chacune en PDF, et n'attribue les
numéros de facture qu'au moment où vous finalisez.

!!! info "Qui peut l'utiliser"
    Fait partie du module **Finances** (désactivé par défaut). La
    lecture nécessite le droit de lecture sur **Finances** ; créer des
    séries, modifier les lignes, finaliser et envoyer nécessitent le
    droit d'écriture ; supprimer une série ou une ligne nécessite le
    droit de suppression. Les membres du bureau et les administrateurs
    peuvent tout faire. Voir [Finances](index.md).

Une série est toujours dans l'un de deux états :

| Statut | Signification |
|---|---|
| **Brouillon** | La série est en préparation. Les lignes peuvent être ajoutées, modifiées et supprimées librement, l'aperçu est recalculé à chaque ouverture, et toute la série peut encore être supprimée. Aucune facture n'existe encore. |
| **Finalisée** | Des factures avec des numéros définitifs ont été créées. Les lignes sont figées, la série ne peut plus être supprimée, et vous envoyez maintenant les factures et enregistrez les paiements. Il n'y a pas de retour au brouillon. |

## Factures annuelles (liste des séries) {#annual-invoices-list-of-runs}

![Factures annuelles](../../assets/screenshots/finances/run-list.png)

Ouvrez-la avec **Finances → Factures émises**, ou la carte **Factures
émises** du tableau de bord. Elle liste chaque série de factures, l'année
la plus récente en premier.

**Barre du haut**

| Bouton | Ce qu'il fait |
|---|---|
| **Nouvelle série de factures** | Ouvre le formulaire pour une nouvelle série (voir ci-dessous). Affiché seulement avec le droit d'écriture. |
| **Toutes les factures** | Ouvre la liste de toutes les factures de toutes les séries, voir [Factures](invoices.md#invoices-all-runs). |
| **Retour aux Finances** | Retour au tableau de bord des finances. |

**Filtre**

| Filtre | Ce qu'il fait |
|---|---|
| **Année** | N'affiche que les séries de cette année exacte. |
| **Objet** | Affiche les séries dont l'objet contient ce texte (majuscules/minuscules indifférentes). |
| **Statut** | **Tous**, **Brouillon** ou **Finalisée**. |
| **Filtrer** / **Réinitialiser** | Applique le filtre / efface tous les filtres. |

**Tableau des séries de factures**

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Année** | L'année que facture la série. |
| **Objet** | L'objet de la série, tel qu'imprimé sur les factures. |
| **Statut** | **Brouillon** (jaune) ou **Finalisée** (vert). |
| **Lignes** | Le nombre de lignes types (lignes de facture) de la série. |
| **Ouvrir** | Ouvre la série. |
| Icône corbeille | Supprime la série avec toutes ses lignes types, après confirmation. Affichée seulement pour les séries en brouillon et avec le droit de suppression. Une série finalisée ne peut jamais être supprimée. |

S'il n'y a encore aucune série, le tableau indique « Aucune série de
factures pour le moment. » ; si votre filtre ne trouve rien, « Aucune
série de factures ne correspond au filtre. »

### Nouvelle série de factures {#new-invoice-run}

Cliquez sur **Nouvelle série de factures** dans la barre du haut. Une
boîte de dialogue s'ouvre :

| Champ | Ce qu'il fait |
|---|---|
| **Année** | Obligatoire. Préremplie avec l'année en cours. Cette année détermine quels relevés de compteurs, données d'assurance et évaluation des heures de travail utilisent les articles basés sur la consommation, et dans quelle année comptent les numéros de facture. |
| **Objet** | Obligatoire. L'en-tête de chaque facture, par ex. « Facture annuelle 2026 ». |
| **Date d'émission** | Obligatoire. Préremplie avec la date du jour. Imprimée sur les factures comme date de facture. |
| **Date d'échéance** | Obligatoire. Imprimée sur les factures. Elle détermine aussi quand une facture impayée est considérée en retard et apparaît sous [Relances](invoices.md#reminders). |
| **Texte de pied de page** | Facultatif. Imprimé sous les lignes de chaque facture de la série, par ex. vos instructions de paiement. Vous pouvez utiliser ces paramètres, remplis pour chaque facture : `{invoice_number}`, `{parcel_number}`, `{invoice_address}` (noms et adresse du destinataire), `{due_date}`. |
| **Créer** | Crée la série en brouillon et l'ouvre. |
| **Annuler** | Ferme la boîte de dialogue sans enregistrer. |

!!! tip "Paramètres dans le texte de pied de page"
    Un pied de page typique est « Veuillez virer le montant avant le
    {due_date}, en indiquant {invoice_number} comme référence. » Si le
    texte de pied de page contient une accolade qui n'est pas l'un des
    quatre paramètres, le texte est imprimé exactement tel que saisi,
    sans rien remplir. Sur une facture de membre (sans parcelle), il n'y
    a pas de numéro de parcelle à remplir : évitez donc `{parcel_number}`
    si la série produit aussi des factures de membres.
    <!-- TODO(verify): by the code, a member invoice's footer prints the literal word "None" for {parcel_number}; confirm in a real PDF. -->

L'année, l'objet, les dates et le texte de pied de page ne peuvent plus
être modifiés après la création de la série. <!-- TODO(verify): no edit route for run header fields exists; if a mistake is made in a draft run, the only way is to delete and recreate it. -->

## Série de factures (brouillon) {#invoice-run-draft}

![Série de factures en brouillon](../../assets/screenshots/finances/run-detail.png)

Le titre de la page affiche l'année et l'objet, par ex. « 2026 —
Facture annuelle ». Tant que la série est un brouillon, c'est sur cette
page que vous composez ses lignes (« lignes types »).

**Barre du haut**

| Bouton | Ce qu'il fait |
|---|---|
| **Aperçu** | Ouvre l'[aperçu](#preview-invoices). Affiché seulement une fois que la série a au moins une ligne. |
| **Retour aux séries de factures** | Retour à la liste. |

### Lignes types {#item-definitions}

Chaque ligne du tableau est un type de ligne qui peut apparaître sur les
factures. Avec le droit d'écriture, chaque ligne est directement
modifiable ; modifiez les champs et cliquez sur l'icône de coche en fin
de ligne pour l'enregistrer. Sans droit d'écriture, vous voyez les mêmes
informations en texte simple.

| Colonne / champ | Ce qu'il fait |
|---|---|
| **Ordre** | Numéro de tri. Les lignes apparaissent sur la facture dans cet ordre. Une nouvelle ligne est préremplie avec dix de plus que le plus grand numéro d'ordre existant, ce qui laisse de la place pour en insérer une entre deux plus tard. |
| **Nom** | Obligatoire. Le texte de la ligne sur la facture, par ex. « Loyer ». |
| **Description** | Facultatif, le petit champ gris sous le nom. Imprimée en petits caractères sous le nom sur la facture. |
| **Calcul** | La façon de calculer le montant, voir [Bases de calcul](#calculation-bases) ci-dessous. Le changer modifie les autres champs affichés. |
| **Prix unitaire** | Le prix par unité (par parcelle, par personne, par m² ...). Pour la cotisation générale, c'est le total à répartir. Masqué pour les quatre modes de calcul automatiques, qui affichent « Calculé automatiquement » à la place. Saisissez-le avec une virgule ou un point décimal, par ex. `12,50`. |
| **S'applique à** | À qui la ligne est destinée. Selon le mode de calcul, c'est un interrupteur **Toutes les parcelles** / *n* parcelle(s), un interrupteur **Tous les membres** / *n* membre(s), ou une note fixe comme « Automatique (bilan des assurances) ». Voir [Qui reçoit une ligne](#who-gets-a-line). |
| **Catégorie** | [Catégorie comptable](bookkeeping.md#bookkeeping-categories) facultative. Elle est copiée sur chaque ligne de facture, pour que les paiements de cette facture soient répartis dans les bonnes catégories dans l'[état comptable](bookkeeping.md#accounting-statement). |
| Icône de coche | Enregistre la ligne. Nécessite le droit d'écriture. |
| Icône corbeille | Supprime la ligne après confirmation (« Supprimer cette ligne type ? »). Nécessite le droit de suppression. |

Quand vous désactivez l'interrupteur **S'applique à** d'une ligne, une
ligne supplémentaire s'ouvre en dessous avec le sélecteur de parcelles
ou de membres (voir [Le sélecteur](#the-picker)).

!!! note
    Les lignes ne peuvent être modifiées que tant que la série est un
    brouillon. Essayer d'enregistrer une ligne d'une série finalisée est
    refusé avec « Cette série de factures est déjà finalisée ; ses lignes
    types ne peuvent plus être modifiées. »

### Ajouter depuis le catalogue d'articles {#add-from-item-catalog}

Affiché avec le droit d'écriture quand votre
[catalogue d'articles](#item-catalog) contient des modèles que cette
série n'a pas encore. Chaque modèle restant est listé avec son mode de
calcul, son prix unitaire et sa portée, et **est coché par défaut**.
Décochez ce que vous ne voulez pas et cliquez sur **Ajouter les
articles sélectionnés**. Chaque modèle coché devient une nouvelle ligne
de cette série, avec tous ses réglages, y compris une sélection
particulière de parcelles ou de membres.

**Gérer le catalogue** vous mène au catalogue d'articles.

Un modèle compte comme « déjà ajouté » quand la série a une ligne
portant exactement le même nom. Si vous renommez ou supprimez la ligne
de la série, le modèle est donc de nouveau proposé ; si vous renommez le
modèle après l'avoir ajouté, il est aussi de nouveau proposé.

Quand il ne reste rien à proposer, vous voyez une courte note à la
place : « Tous les articles du catalogue ont déjà été ajoutés à cette
campagne de facturation. » ou, si le catalogue est vide, « Aucun article
dans le catalogue pour l'instant -- ajoutez les articles récurrents une
fois et sélectionnez-les ici chaque année. » Les deux ont un bouton
**Gérer le catalogue**.

### Ajouter une ligne {#add-item}

Sous le catalogue, un formulaire pour ajouter à la main une ligne
ponctuelle. Il a les mêmes champs que le tableau (**Ordre**, **Nom**,
**Description**, **Mode de calcul**, **Prix unitaire**, **Catégorie**),
puis l'interrupteur de portée (**S'applique à chaque parcelle** ou
**S'applique à chaque membre**, tous deux activés par défaut) et, quand
vous le désactivez, le sélecteur. Cliquez sur le bouton **+** pour
ajouter la ligne.

## Bases de calcul {#calculation-bases}

Le **Mode de calcul** détermine comment Parcella calcule la ligne pour
chaque parcelle ou membre. Chaque montant est arrondi au centime par
ligne ; le total de la facture est la somme de ses lignes.

| Mode de calcul | Facturé à | Quantité × prix | D'où viennent les chiffres |
|---|---|---|---|
| **Montant fixe par parcelle** | Chaque parcelle concernée | 1 × prix unitaire | Vous saisissez le montant, par ex. une contribution par parcelle. |
| **Montant fixe par personne** | Chaque membre concerné, sur sa propre facture | 1 × prix unitaire | Vous saisissez le montant, par ex. la cotisation. Facturé par membre, qu'il ait une parcelle ou non. |
| **Par m² loué** | Chaque parcelle concernée | superficie de la parcelle × prix unitaire | La superficie enregistrée sur la parcelle. Une parcelle sans superficie n'a pas de ligne. |
| **Part du bail de la surface commune** | Chaque parcelle concernée | (surface commune ÷ nombre de parcelles facturées) × prix unitaire | La surface commune (« Superficie B ») des [Paramètres de l'association](../../administration/settings.md). La part est arrondie à 0,1 m². |
| **Charges publiques (surface propre + part de la surface commune)** | Chaque parcelle concernée | (superficie de la parcelle + part de la surface commune) × prix unitaire | Comme ci-dessus, plus la superficie propre de la parcelle, à un seul taux par m². |
| **Cotisation générale (répartie également entre toutes les parcelles)** | Chaque parcelle concernée | 1 × (total ÷ nombre de parcelles facturées) | Vous saisissez comme prix unitaire le **total** que l'association doit encaisser ; chaque parcelle paie une part égale, arrondie au centime. |
| **Consommation d'eau (depuis le module)** | Chaque parcelle avec un compteur d'eau | consommation de l'année × prix par unité | La consommation et le prix viennent de [Eau et électricité](../metering.md). |
| **Consommation d'électricité (depuis le module)** | Chaque parcelle avec un compteur d'électricité | consommation de l'année × prix par unité | Comme pour l'eau. |
| **Coût d'assurance (depuis le module)** | Chaque parcelle assurée pour l'année | une ligne par composante d'assurance | Depuis [Assurances](../insurance.md). |
| **Déficit d'heures de travail (depuis le module)** | Chaque parcelle ou membre qui doit de l'argent pour des heures manquantes | 1 × montant dû | Depuis l'[évaluation des heures de travail](../work-hours.md) de l'année de la série. |

Détails pour chaque mode :

**Montant fixe par parcelle / par personne.** Si vous laissez le
**Prix unitaire** vide, la ligne ne facture rien.

**Par m² loué.** Utilise la superficie enregistrée pour chaque parcelle.
Vérifiez que chaque parcelle a sa superficie renseignée avant de
finaliser -- une parcelle sans superficie n'obtient silencieusement pas
de ligne de loyer.

**Part du bail de la surface commune.** La surface commune est répartie
à parts égales entre exactement les parcelles qui reçoivent cette ligne
(celles de sa portée qui ont aussi quelqu'un à facturer). Ainsi, les
parts totalisent toute la surface commune et l'association encaisse le
loyer complet. Si la surface commune est nulle ou non configurée, la
ligne ne facture rien du tout. La surface commune est calculée dans les
paramètres de l'association comme superficie totale moins la superficie
des parcelles moins la superficie municipale.

**Charges publiques** (voir le [glossaire](../../glossary.md)). Comme la
part commune, mais ajoutée à la superficie propre de la parcelle et
facturée à un taux combiné. Si la surface commune n'est pas configurée,
la superficie propre de la parcelle est quand même facturée -- la partie
commune compte simplement pour 0 m².

**Cotisation générale** (voir le [glossaire](../../glossary.md)).
Utilisez-la pour un coût ponctuel que l'association répercute, par ex.
des frais juridiques de 1 200,00 répartis sur 40 parcelles = 30,00
chacune. Seules les parcelles réellement facturées comptent, donc les
parcelles vacantes ne « mangent » jamais une part. Comme chaque part est
arrondie au centime, le total encaissé peut différer de quelques
centimes du montant saisi.

**Consommation d'eau / Consommation d'électricité.** Pour chaque
parcelle ayant un point de mesure de parcelle de ce type, Parcella prend
la consommation du compteur actuel dans l'année de la série (le relevé
de cette année moins le précédent) et la multiplie par le prix par unité
fixé pour cette année dans le module des compteurs. Vous ne saisissez
pas de prix unitaire ici.

- Une parcelle sans relevé pour l'année n'a pas de ligne.
- Si aucun prix n'est fixé pour ce fluide et cette année, personne n'est
  facturé.
- Après un échange de compteur en cours d'année, la consommation des
  **deux** compteurs est facturée : l'ancien jusqu'à son relevé final
  (saisi dans le formulaire d'échange) et le nouveau à partir de son
  relevé initial.

!!! warning "Points de mesure avec un facteur"
    Si un point de mesure a un facteur (multiplicateur) dans le module
    des compteurs, les écrans des compteurs affichent la consommation
    multipliée, mais la facture facture la différence **brute** des
    relevés. Vérifiez ces parcelles dans l'aperçu.


**Coût d'assurance.** Facturé pour chaque parcelle ayant une donnée
d'assurance pour l'année de la série. Au lieu d'une somme globale, la
facture affiche une ligne par composante que la parcelle a réellement :
« Assurance des biens (*formule*) », « Assurance accidents (ménage) » et,
le cas échéant, « Assurance accidents (+*n* personne(s)
supplémentaire(s)) ». Ces textes de ligne sont fixes, dans la langue de
l'association -- le nom de la ligne elle-même n'est pas utilisé. Les
montants viennent des prix d'assurance configurés pour cette année.

**Déficit d'heures de travail.** Facture ce que l'évaluation des heures
de travail de l'année de la série indique comme dû, exactement à ce
montant. Les parcelles ou membres exemptés et ceux qui ont rempli leurs
heures ne sont pas facturés. Que cela aille sur la facture de la
parcelle ou sur une facture séparée du membre dépend de la façon dont
les heures sont comptées cette année-là : par parcelle, sur la facture
de la parcelle ; par membre, sur la facture propre de chaque membre.

## Qui reçoit une ligne {#who-gets-a-line}

**Les modes par parcelle** (fixe par parcelle, par m², part commune,
charges publiques, cotisation générale) utilisent l'interrupteur
**S'applique à chaque parcelle** :

- Activé (par défaut) : chaque parcelle qui peut être facturée.
- Désactivé : seulement les parcelles que vous cochez dans le sélecteur.

**Montant fixe par personne** utilise à la place **S'applique à chaque
membre** :

- Activé (par défaut) : chaque membre actif.
- Désactivé : seulement les membres que vous cochez.

**Les quatre modes automatiques** (eau, électricité, assurance, déficit
d'heures de travail) n'ont pas de sélecteur. Qui est facturé découle de
l'autre module : avoir un compteur, une donnée d'assurance ou un
déficit. Une note comme « Automatique (parcelles avec un compteur d'eau
actif) » s'affiche à la place. (Malgré la formulation, un point de
mesure désactivé est quand même inclus dans la série.)

Quelles parcelles peuvent être facturées :

- Une parcelle ne reçoit une facture que si au moins un locataire
  **actuel** est marqué **Utiliser comme adresse de facturation**. Les
  locataires qui ont donné leur congé pour une date future comptent
  encore jusqu'à leur départ effectif.
- Une parcelle résiliée est quand même facturée si elle a un tel
  locataire (par exemple un nouveau locataire arrivé avant que le statut
  soit rechangé). Seules les parcelles supprimées sont toujours
  ignorées.
- Si les locataires à l'adresse de facturation vivent à des adresses
  différentes, la parcelle reçoit quand même **une** facture (un numéro,
  un montant), avec **un exemplaire par adresse**. Les locataires qui
  partagent une adresse sont nommés ensemble sur un exemplaire. Les
  exemplaires ne diffèrent que par la fenêtre d'adresse.
- Une parcelle dont toutes les lignes sont vides ne reçoit pas de
  facture.

Les factures de membres (issues de **Montant fixe par personne**, ou
d'un déficit d'heures compté par membre) sont des factures séparées
adressées au membre à sa propre adresse. Elles affichent **Sans parcelle
(membre)** au lieu d'un numéro de parcelle. Un locataire à qui l'on
facture aussi une contribution par personne reçoit donc deux factures :
une pour la parcelle, une pour lui-même. Toutes les lignes par personne
d'un même membre sont regroupées sur une seule facture.

### Le sélecteur {#the-picker}

Quand un interrupteur de portée est désactivé, un sélecteur apparaît
avec le libellé **Parcelles** ou **Membres**.

| Élément | Ce qu'il fait |
|---|---|
| **Afficher la liste** / **Masquer la liste** | Ouvre ou ferme la liste des cases à cocher. |
| **Rechercher…** | Restreint la liste aux numéros de parcelle ou noms correspondants. « Aucun résultat » apparaît quand rien ne correspond. |
| **Tout sélectionner** / **Tout désélectionner** | Coche ou décoche chaque entrée **actuellement visible** -- vous pouvez donc d'abord chercher puis ne sélectionner que celles-là. |

Le sélecteur de parcelles liste les parcelles actives ; le sélecteur de
membres liste les membres actifs.

!!! tip
    La portée reste modifiable jusqu'à la finalisation. Vous pouvez la
    changer aussi souvent que vous voulez pendant la préparation de la
    série.

## Aperçu des factures {#preview-invoices}

<!-- TODO(verify): no screenshot -- the preview page is two clicks away from a fixed URL (run list -> run -> Preview), which the screenshot tool can't follow, and the sample data has no invoice runs. -->

Cliquez sur **Aperçu** sur une série en brouillon. Parcella calcule
chaque facture que produirait la série, maintenant, sans rien enregistrer
ni envoyer. Le titre de la page est « Aperçu — *année* *objet* ».

L'encadré bleu en haut indique combien de factures seraient générées et
rappelle : « Rien n'est encore enregistré ni envoyé — vérifiez les PDF
ci-dessous, puis finalisez. »

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **Parcelle** | Le numéro de parcelle, ou **Sans parcelle (membre)** pour une facture de membre. |
| **Destinataire** | Les noms auxquels la facture sera adressée. |
| **Sous-total** | Le total de la facture. |
| **PDF** | Ouvre la facture en PDF dans un nouvel onglet, exactement comme elle sera, avec « Aperçu » comme numéro de facture et un bandeau « Aperçu — pas encore finalisé ni envoyé ». |
| **Finaliser et attribuer les numéros de facture** | Finalise la série, après confirmation. Affiché seulement avec le droit d'écriture tant que la série est un brouillon. |
| **Retour à la série de factures** | Retour à la série, pour corriger les lignes. |

Si la liste est vide, la page indique « Aucune facture ne serait générée
— vérifiez la portée des parcelles dans les lignes types et l'indicateur
d'adresse de facturation des membres concernés. »

!!! tip "L'aperçu est toujours en direct"
    Rien n'est stocké pour l'aperçu. À chaque ouverture, il lit les
    parcelles, locataires, relevés de compteurs, assurances et heures de
    travail actuels. Corrigez les données dans ces modules, puis
    rechargez simplement la page.

### Ce que fait la finalisation {#what-finalizing-does}

Quand vous cliquez sur **Finaliser et attribuer les numéros de facture**
et confirmez (« Finaliser cette série de factures ? Les numéros de
facture seront attribués définitivement et les lignes types ne pourront
plus être modifiées. Cette action est irréversible. ») :

1. Parcella calcule les factures une dernière fois, exactement comme
   l'aperçu.
2. Chaque facture reçoit un numéro définitif, dans l'ordre de la liste
   de l'aperçu. Le format vient du **Format du numéro de facture** des
   [Paramètres de l'association](../../administration/settings.md) (par
   défaut *année*/*numéro*, par ex. `2026/1`). La numérotation continue
   à partir du plus grand numéro déjà utilisé dans la même année, toutes
   séries confondues, et commence à 1 pour la première facture de
   l'année.
3. Les noms et adresses des destinataires sont copiés sur les factures.
   Les changements ultérieurs de l'adresse d'un membre ne réécrivent pas
   une facture déjà émise.
4. La série devient **Finalisée** et ses lignes sont figées.

Si **Prochain numéro de facture (remplacer)** est renseigné dans les
paramètres de l'association, cette série commence à ce numéro, et le
réglage est effacé ensuite. Si cela réutilisait un numéro déjà attribué
la même année, la finalisation s'arrête avec un message d'erreur et rien
n'est créé.

Une série sans aucune ligne ne peut pas être finalisée : « Cette série
de factures n'a pas encore de lignes types — ajoutez-en au moins une
avant de finaliser. »

## Série de factures (finalisée) {#invoice-run-finalized}

Une fois finalisée, la page de la série affiche une note verte « Cette
série de factures est finalisée. Les numéros de facture sont définitifs
et les lignes types ne peuvent plus être modifiées. » La liste des
lignes disparaît ; vous voyez à la place l'envoi et les factures de la
série.

### Envoi {#delivery}

Affiché avec le droit d'écriture.

| Bouton | Ce qu'il fait |
|---|---|
| **Envoyer les e-mails et téléverser vers le cloud** | Envoie par e-mail chaque facture de la série qui ne l'a pas encore été, avec le PDF joint, et téléverse chaque facture pas encore téléversée dans le dossier cloud de sa parcelle. Le relancer ne traite que ce qui manque encore. |
| **Télécharger le lot d'impression** | Télécharge un PDF avec un courrier pour chaque locataire qui ne reçoit pas les factures par e-mail -- un courrier par adresse, nommant les personnes sans e-mail qui y vivent -- prêt à imprimer et à mettre sous enveloppe à fenêtre. Ces factures sont marquées comme imprimées. |

**Qui reçoit un e-mail :** chaque locataire à l'adresse de facturation
nommé sur la facture (ou, pour une facture de membre, le membre) qui a
**Peut recevoir des informations par e-mail** activé et au moins une
adresse e-mail enregistrée. Chacun reçoit l'exemplaire de sa propre
adresse ; l'adresse e-mail principale est utilisée. Tous les autres
reçoivent un courrier imprimé du lot d'impression -- **même** quand
quelqu'un qui vit avec eux a reçu l'e-mail. Les locataires sans e-mail
qui partagent une adresse reçoivent un seul courrier ensemble : « Les
membres sans notifications par e-mail restent pour le lot d'impression
ci-dessous. »

**Le téléversement cloud** n'a lieu que si le stockage cloud est
configuré et que la parcelle a un dossier cloud. Les factures de membres
ne sont jamais téléversées, car il n'y a pas de dossier par membre. Les
téléversements échoués sont ignorés silencieusement et retentés la fois
suivante.

!!! note "Lot d'impression"
    Le lot est constitué selon qui peut être joint par e-mail, pas selon
    ce qui a été envoyé. Vous pouvez le télécharger avant ou après
    l'envoi des e-mails : il contient toujours les mêmes exemplaires --
    y compris ceux déjà imprimés la dernière fois. Si chaque facture peut
    partir par e-mail, vous obtenez le message « Pour toutes les factures
    de cette série, un membre est joignable par e-mail -- rien à
    imprimer. »

### Filtre {#filter}

Au-dessus du tableau des factures, vous pouvez restreindre la liste.
Cela fonctionne comme le filtre de
[Toutes les factures](invoices.md#invoices-all-runs) : **N° de facture**,
**Destinataire**, **Parcelle** (contient ce texte), **Montant min.**,
**Montant max.** (sous-total de la facture) et **Statut** (**Tous**,
**Ouverte**, **Partiellement payée**, **Payée**). **Filtrer** l'applique,
**Réinitialiser** l'efface.

### Factures {#invoices}

| Colonne / bouton | Ce qu'elle affiche |
|---|---|
| **N° de facture** | Le numéro de facture ; cliquez dessus pour ouvrir la [facture](invoices.md#invoice). |
| **Parcelle** | Numéro de parcelle, ou **Sans parcelle (membre)**. |
| **Destinataire** | Les noms des destinataires. |
| **Sous-total** | Le montant de la facture. |
| **Statut de paiement** | **Ouverte** (rouge, rien payé), **Partiellement payée** (jaune) ou **Payée** (vert). |
| **Envoi** | Des icônes pour ce qui a été fait : enveloppe = « Envoyé par e-mail », imprimante = « Inclus dans un lot d'impression », nuage = « Téléversé vers le stockage cloud ». Survolez une icône pour voir sa signification. |
| **Paiement** | Ouvre la boîte de dialogue de paiement de cette facture (voir ci-dessous). Nécessite le droit d'écriture. |
| **PDF** | Ouvre le PDF de la facture dans un nouvel onglet. |

### Boîte de dialogue de paiement {#payment-dialog}

Le moyen le plus rapide d'enregistrer les paiements de nombreuses
factures : cliquez sur **Paiement** sur une ligne, saisissez le
paiement, et vous revenez sur la page de la série, prêt pour la
suivante. Le titre de la boîte de dialogue est « Paiement — Facture
*numéro* ».

Elle liste les paiements enregistrés jusqu'ici (date, montant, compte,
note), chacun avec une icône corbeille pour le supprimer (nécessite le
droit de suppression, demande « Supprimer ce paiement ? »). S'il n'y en a
aucun : « Aucun paiement enregistré pour le moment. »

| Champ | Ce qu'il fait |
|---|---|
| **Montant** | Obligatoire. Le montant reçu, par ex. `45,00`. Les paiements partiels sont possibles ; enregistrez-les séparément. |
| **Payé le** | Obligatoire. Prérempli avec la date du jour. Cette date détermine l'année où la recette compte dans l'état comptable. |
| **Note** | Facultatif, par ex. « virement bancaire ». |
| **Compte** | Facultatif. Le [compte](bank-accounts.md#accounts) sur lequel l'argent est arrivé. Seuls les comptes actifs sont proposés. Le paiement apparaît alors dans les écritures de ce compte. |
| **Ajouter un paiement** | Enregistre le paiement. |

Le statut de paiement se met à jour tout seul : une fois que les
paiements atteignent le montant de la facture plus les éventuels frais
de relance, la facture est **Payée**. Voir
[Paiements](invoices.md#payments).

## Catalogue d'articles {#item-catalog}

![Catalogue d'articles](../../assets/screenshots/finances/item-templates.png)

Ouvrez-le depuis la carte **Catalogue d'articles** du tableau de bord ou
avec **Gérer le catalogue** sur une série en brouillon. Le catalogue
contient vos lignes de facture récurrentes (« modèles d'articles »)
pour ne pas avoir à les ressaisir chaque année. Les modèles sont
indépendants de toute série ; vous les reprenez dans une série avec
[Ajouter depuis le catalogue d'articles](#add-from-item-catalog).

L'écran a les mêmes champs que les lignes d'une série :

- **Nouveau modèle d'article** (avec le droit d'écriture) : **Ordre**,
  **Nom**, **Description**, **Mode de calcul**, **Prix unitaire**,
  **Catégorie**, l'interrupteur de portée (**S'applique à chaque
  parcelle** / **S'applique à chaque membre**) et le
  [sélecteur](#the-picker). Cliquez sur le bouton **+** pour enregistrer.
- **Modèles d'articles** : une ligne modifiable par modèle avec les
  colonnes **Ordre**, **Nom**, **Calcul**, **Prix unitaire**,
  **S'applique à** et **Catégorie**. Modifiez une ligne et cliquez sur
  son icône de coche pour l'enregistrer ; l'icône corbeille la supprime
  (nécessite le droit de suppression).

Après l'enregistrement, vous voyez « Enregistré. ». Si le catalogue est
vide : « Aucun modèle d'article pour l'instant -- ajoutez-en un
ci-dessus. »

Les modes de calcul et les règles de portée sont exactement ceux décrits
sous [Bases de calcul](#calculation-bases) et
[Qui reçoit une ligne](#who-gets-a-line).

!!! note "Modèles et séries sont indépendants"
    Ajouter un modèle à une série le copie. Modifier un modèle plus tard
    ne change pas les séries qui l'ont déjà utilisé, et supprimer un
    modèle laisse intactes les lignes de ces séries (« Supprimer ce
    modèle d'article ? Les séries qui l'ont déjà utilisé conservent
    leurs articles, simplement sans lien vers le modèle. »). Les prix
    qui changent chaque année se mettent de préférence à jour dans le
    catalogue avant d'ajouter les articles à la nouvelle série.

## Voir aussi {#related}

- [Établir les factures annuelles](../../guides/annual-invoicing.md) --
  toute la procédure pas à pas.
- [Factures, paiements et relances](invoices.md)
- [Eau et électricité](../metering.md), [Assurances](../insurance.md),
  [Heures de travail](../work-hours.md) -- d'où viennent les montants
  automatiques.
- [Paramètres de l'association](../../administration/settings.md) --
  format des numéros de facture, coordonnées bancaires, superficies.

# Établir les factures annuelles {#running-the-annual-invoices}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Une fois par an, l'association facture chaque parcelle : loyer, eau,
électricité, assurance, heures de travail non effectuées, éventuellement
une cotisation ou une [contribution exceptionnelle](../glossary.md#general-levy).
Dans Parcella, c'est une [série de factures](../glossary.md#invoice-run) :
vous définissez une fois les lignes, vérifiez un aperçu de chaque
facture, finalisez pour attribuer les numéros de facture, puis les
envoyez -- par e-mail, sur papier, ou dans le dossier cloud de chaque
parcelle. Ensuite, vous enregistrez les paiements et envoyez les
[relances](../glossary.md#dunning).

!!! info "Qui peut le faire"
    Tout ici nécessite le droit d'**écriture** sur **Finances**. Le
    module **Finances** est **désactivé** sur une nouvelle installation ;
    activez-le sous **Administration → Paramètres → Domaines
    fonctionnels** (voir
    [Activer et désactiver les modules](../administration/modules.md)).

!!! warning "La finalisation est irréversible"
    Tant que vous n'avez pas finalisé, rien n'est enregistré comme
    facture et rien n'est envoyé -- modifiez les lignes autant que vous
    voulez. La finalisation attribue des numéros de facture définitifs
    et verrouille la série. Téléchargez d'abord une sauvegarde
    (**Administration → Utilisateurs → Télécharger la sauvegarde**).

## 1. Vérifier les paramètres financiers (une fois) {#1-check-the-finance-settings-once}

1. Ouvrez **Administration → Paramètres** et trouvez **Paramètres
   financiers**.
2. Renseignez les coordonnées bancaires de l'association : **Nom de la
   banque**, **IBAN**, **BIC**, **Titulaire du compte**. Elles
   apparaissent en pied de page de chaque facture.
3. Vérifiez le **Format du numéro de facture**. Par défaut, c'est
   l'année et un numéro courant ; vous pouvez utiliser le vôtre, par
   exemple `R-{year}-{number}`. `{number}` est obligatoire.
4. Laissez **Prochain numéro de facture (remplacer)** vide, sauf si la
   première série de factures dans Parcella doit continuer une
   numérotation que vous utilisiez avant. Il est utilisé une fois puis
   effacé.
5. Assurez-vous que **E-mail (SMTP)** est configuré si vous voulez
   envoyer les factures par e-mail.
6. Cliquez sur **Enregistrer les paramètres**.

## 2. Préparer le catalogue d'articles (une fois, puis réutiliser) {#2-prepare-the-item-catalog-once-then-reuse}

Le catalogue d'articles contient les lignes que vous facturez chaque
année, pour ne pas avoir à les redéfinir à chaque série.

1. Ouvrez **Finances → Aperçu** et cliquez sur **Catalogue
   d'articles**.
2. Sous **Nouveau modèle d'article**, renseignez **Ordre** (position sur
   la facture), **Nom**, **Description**, le **Mode de calcul**, le
   **Prix unitaire** et éventuellement une **Catégorie**.
3. Choisissez à qui il s'applique (voir ci-dessous) et cliquez sur le
   bouton **+**.

| Mode de calcul | Ce qu'il facture |
|---|---|
| **Montant fixe par parcelle** | Le prix unitaire une fois par parcelle -- par ex. le loyer. |
| **Montant fixe par personne** | Le prix unitaire une fois par *membre* -- par ex. une cotisation, y compris pour les membres sans parcelle. |
| **Par m² loué** | Prix unitaire × la superficie de la parcelle. |
| **Part du bail de la surface commune** | La surface commune (superficie B), répartie à parts égales entre les parcelles facturées, × prix unitaire. |
| **Charges publiques (surface propre + part de la surface commune)** | La surface propre de la parcelle plus sa part de la surface commune, × prix unitaire. |
| **Cotisation générale (répartie également entre toutes les parcelles)** | Le prix unitaire est un montant *total* réparti à parts égales entre toutes les parcelles facturées. |
| **Consommation d'eau (depuis le module)** | La consommation d'eau de la parcelle × le prix de l'eau pour l'année. |
| **Consommation d'électricité (depuis le module)** | La consommation d'électricité de la parcelle × le prix de l'électricité pour l'année. |
| **Coût d'assurance (depuis le module)** | L'assurance de la parcelle, une ligne par type d'assurance. |
| **Déficit d'heures de travail (depuis le module)** | Les [heures obligatoires](../glossary.md#mandatory-hours) manquantes × le tarif horaire. |

**À qui s'applique un article.** Les articles par parcelle ont
**S'applique à chaque parcelle** ; décochez-le pour choisir des
**Parcelles** précises. **Montant fixe par personne** a à la place
**S'applique à chaque membre** et un sélecteur **Membres**. Les quatre
articles « depuis le module » choisissent leurs parcelles eux-mêmes --
**Automatique (...)** s'affiche au lieu d'un sélecteur -- et leur prix
unitaire est **Calculé automatiquement**.

Plus d'informations : [Séries de factures](../modules/finances/invoice-runs.md).

## 3. Vérifier les chiffres utilisés par les articles automatiques {#3-check-the-numbers-the-automatic-items-use}

Les articles « depuis le module » prennent leurs chiffres dans d'autres
modules. Vérifiez-les pour l'année facturée **avant** de finaliser.

**Eau et électricité**

1. Ouvrez **Eau → Configuration** et vérifiez qu'un prix (**Prix par
   m³**) existe pour l'année (dans **Historique des prix**). Sinon,
   saisissez l'**Année** et le prix sous **Nouveau/mise à jour du prix**
   et cliquez sur **Enregistrer**. Faites de même sous **Électricité →
   Configuration**.
2. Ouvrez **Eau → Aperçu**. S'il indique que certains points de mesure
   n'ont pas encore de relevé pour l'année, relevez-les d'abord -- voir
   [Relever les compteurs](meter-readings.md). Une parcelle sans relevé
   pour l'année n'a aucune ligne d'eau.
3. Ouvrez **Eau → Évaluation** pour l'année et recherchez les parcelles
   avec **pas de relevé** ou une consommation invraisemblable.

**Heures de travail**

1. Ouvrez **Sessions de travail → Sessions & Aperçu** et vérifiez la
   **Configuration des heures** de l'année : heures requises et
   **Tarif horaire**.
2. Ouvrez **Sessions de travail → Évaluation annuelle** pour l'année.
   Vérifiez les colonnes **Ouvert** et **Dû** -- c'est ce qui sera
   facturé. Il manque des présences, des parrainages ou des
   exemptions ? Corrigez-les maintenant (voir
   [Organiser une session de travail](work-session.md)).

**Assurance**

1. Ouvrez **Assurance → Configuration** et **Assurance → Parcelles** et
   vérifiez les prix de l'année et l'assurance de chaque parcelle.

!!! tip "Qui reçoit la facture"
    Une facture de parcelle va aux locataires actuels de la parcelle
    marqués **Utiliser comme adresse de facturation**. Les parcelles
    sans un tel locataire ne reçoivent pas de facture. Vérifiez-le sur
    les pages des parcelles avant de finaliser -- surtout après une
    transmission.

## 4. Créer la série de factures {#4-create-the-invoice-run}

1. Ouvrez **Finances → Factures émises** (la page s'appelle
   **Factures annuelles**).
2. Cliquez sur **Nouvelle série de factures**.
3. Saisissez l'**Année** facturée, un **Objet** (par ex. « Facture
   annuelle 2026 »), la **Date d'émission** et la **Date d'échéance**.
4. Rédigez éventuellement un **Texte de pied de page**. Il peut contenir
   `{invoice_number}`, `{parcel_number}`, `{invoice_address}` et
   `{due_date}`, qui sont remplis pour chaque facture.
5. Cliquez sur **Créer**.

La série est un **Brouillon**. Ouvrez-la avec **Ouvrir**.

## 5. Ajouter les lignes {#5-add-the-line-items}

1. Sur la page de la série, sous **Ajouter depuis le catalogue
   d'articles**, cochez les articles du catalogue pour cette année et
   cliquez sur **Ajouter les articles sélectionnés**.
2. Pour ce qui n'est facturé que cette année, remplissez **Ajouter une
   ligne** en bas, de la même façon que dans le catalogue.
3. Vérifiez le tableau **Lignes types** : ordre, prix, à qui s'applique
   chaque ligne. Vous pouvez encore modifier ou supprimer des lignes
   tant que la série est un brouillon.

## 6. Aperçu {#6-preview}

1. Cliquez sur **Aperçu** en haut de la page de la série.
2. La page indique combien de factures seraient générées et les liste
   sous **Factures calculées**, avec destinataire et sous-total.
3. Ouvrez-en quelques-unes avec **PDF** et vérifiez-les : adresse,
   lignes, montants, pied de page.
4. Pour corriger quelque chose, utilisez **Retour à la série de
   factures**, modifiez les lignes, et refaites l'aperçu. Rien n'a
   encore été enregistré ni envoyé.

S'il indique *« Aucune facture ne serait générée »*, vérifiez la portée
des parcelles des lignes et l'indicateur **Utiliser comme adresse de
facturation** des locataires.

## 7. Finaliser {#7-finalize}

1. Sur la page d'aperçu, cliquez sur **Finaliser et attribuer les
   numéros de facture** et confirmez.
2. Parcella crée les factures avec des numéros définitifs. La page de la
   série indique désormais qu'elle est finalisée et liste les
   **Factures**.

Les noms et adresses des destinataires sont enregistrés sur chaque
facture tels qu'ils sont à ce moment. Les changements d'adresse
ultérieurs ne réécrivent pas les factures finalisées.

## 8. Envoyer les factures {#8-send-the-invoices}

1. Sur la page de la série finalisée, trouvez la carte **Envoi**.
2. Cliquez sur **Envoyer les e-mails et téléverser vers le cloud**.
    - Les factures sont envoyées par e-mail (PDF joint) aux destinataires
      qui ont **Peut recevoir des informations par e-mail** et une
      adresse e-mail.
    - Si la parcelle a un dossier de documents dans le stockage cloud,
      la facture y est aussi téléversée.
    - Cliquer à nouveau n'envoie que ce qui n'a pas encore été envoyé.
3. Cliquez sur **Télécharger le lot d'impression**. Il contient un
   courrier pour chaque locataire qui ne reçoit pas les factures par
   e-mail, en un seul PDF à imprimer et poster : un courrier par
   adresse, nommant les personnes sans e-mail qui y vivent. Cela inclut
   quelqu'un dont le colocataire a reçu l'e-mail. Ils sont ensuite
   marqués comme inclus dans un lot d'impression.

La colonne **Envoi** indique pour chaque facture si elle a été
**Envoyé par e-mail**, **Inclus dans un lot d'impression** ou
**Téléversé vers le stockage cloud**. Pour renvoyer une seule facture,
ouvrez-la et cliquez sur **Renvoyer l'e-mail**.

Plus d'informations : [Factures, paiements et relances](../modules/finances/invoices.md).

## 9. Enregistrer les paiements {#9-record-payments}

**À la main**

1. Ouvrez la série (ou **Toutes les factures** sur **Factures
   annuelles** pour chercher dans toutes les séries par numéro de
   facture, destinataire ou montant).
2. Cliquez sur **Paiement** sur la ligne de la facture.
3. Saisissez le **Montant**, **Payé le**, éventuellement une **Note** et
   le **Compte** sur lequel il est arrivé, et cliquez sur **Ajouter un
   paiement**.

Les paiements partiels sont possibles ; le statut passe de lui-même de
**Ouverte** à **Partiellement payée** puis à **Payée**.

**À partir du relevé bancaire**

1. Une fois : ouvrez **Finances → Aperçu → Comptes** et ajoutez votre
   compte bancaire sous **Nouveau compte**.
2. Cliquez sur **Écritures** à côté du compte, puis sur **Importer CSV**.
3. Téléversez le relevé exporté depuis votre banque en ligne. Sur
   **Associer les colonnes CSV**, associez au moins **Date** et
   **Montant** ; **Description**, **Expéditeur / destinataire** et
   **IBAN** aident au rapprochement.
4. Sur **Associer les lignes aux factures**, Parcella propose pour chaque
   paiement entrant les factures ouvertes du même montant. Choisissez la
   bonne pour l'enregistrer comme paiement sur cette facture, ou
   choisissez **Enregistrer comme écriture générique**.
5. Cliquez sur **Importer CSV** en bas de la page pour créer les
   écritures et les paiements.

Plus d'informations : [Comptes bancaires et écritures](../modules/finances/bank-accounts.md).

## 10. Envoyer les relances {#10-send-reminders}

1. Après la date d'échéance, ouvrez **Finances → Relances**.
   **Factures en retard** liste chaque facture impayée dont l'échéance
   est dépassée, avec la durée du retard et le nombre de rappels
   envoyés.
2. Cliquez sur **Ouvrir** à côté d'une facture.
3. Saisissez éventuellement des **Frais (facultatif)** et un **Message
   (facultatif)**.
4. Cliquez sur **Envoyer le rappel**.

Parcella crée le rappel suivant en PDF (**Rappel n° 1**, **n° 2**, …),
ajoute les frais au montant dû, et l'envoie par e-mail si le membre a
accepté l'e-mail ; sinon il est marqué **À imprimer/envoyer par
courrier** pour que vous l'imprimiez et le postiez. Il n'y a pas de
niveaux de relance fixes -- vous décidez quand envoyer le suivant.

## Voir aussi {#related}

- [Finances](../modules/finances/index.md)
- [Séries de factures](../modules/finances/invoice-runs.md)
- [Factures, paiements et relances](../modules/finances/invoices.md)
- [Comptes bancaires et écritures](../modules/finances/bank-accounts.md)
- [Catégories, budget et synthèse](../modules/finances/bookkeeping.md)
- [Eau et électricité](../modules/metering.md)
- [Heures de travail](../modules/work-hours.md)
- [Assurances](../modules/insurance.md)
- [Relever les compteurs](meter-readings.md)

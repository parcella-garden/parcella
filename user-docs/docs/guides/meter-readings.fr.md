# Relever les compteurs {#collecting-meter-readings}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Une fois par an, quelqu'un fait le tour du terrain et relève chaque
compteur d'eau et d'électricité : le compteur principal de l'association,
un compteur par parcelle, et les raccordements propres à l'association
(local, aire de lavage). Ce guide couvre la saisie de ces relevés -- sur
un téléphone pendant la tournée, ou ensuite à partir d'une liste -- ainsi
que le remplacement d'un compteur et la vérification des résultats.

L'eau et l'électricité fonctionnent exactement de la même façon ;
chacune a son propre menu. Les étapes ci-dessous parlent d'**Eau** ;
pour l'électricité, utilisez plutôt le menu **Électricité**.

!!! info "Qui peut le faire"
    La saisie des relevés nécessite le droit d'**écriture** sur **Eau**
    (ou **Électricité**) ; supprimer un relevé nécessite la
    **suppression**. Les deux modules sont activés par défaut. Une
    association peut donner à l'équipe des compteurs un groupe avec
    exactement ces droits -- voir [Groupes](../administration/groups.md).

## Comment Parcella calcule la consommation {#how-parcella-counts-consumption}

- Chaque **[point de mesure](../glossary.md#metering-point)** (le
  raccordement d'une parcelle, le compteur principal, un raccordement de
  l'association) a un **compteur** installé à la fois.
- Un compteur a **un relevé par an**. La consommation de l'année est ce
  relevé moins celui de l'année précédente -- ou moins le **Relevé
  initial** du compteur s'il s'agit du premier.
- Saisir un relevé pour une année qui en a déjà un le **remplace**.
- Les relevés sont saisis exactement tels que l'afficheur les montre.
  Certains compteurs d'électricité n'affichent qu'une fraction de la
  valeur réelle ; leur point de mesure a alors un **Facteur** (par ex. 20)
  que l'évaluation applique.

## 1. Avant la tournée : vérifier la liste des points de mesure {#1-before-the-round-check-the-list-of-metering-points}

1. Ouvrez **Eau → Aperçu**. Les tuiles indiquent combien de compteurs
   principaux, de raccordements de parcelles et de l'association
   existent, ainsi que les **Points de comptage manquants** : les
   parcelles sans raccordement d'eau dans Parcella.
2. Cliquez sur **Afficher** sous **Points de comptage manquants** pour
   voir ces parcelles ; chacune renvoie vers **Nouveau point de mesure**
   avec la parcelle déjà sélectionnée. Ajoutez celles qui ont vraiment
   un compteur.
3. Un raccordement sans alimentation pendant un certain temps (eau coupée
   sur une parcelle vacante) ? Ouvrez son point de mesure, renseignez
   **Désactiver à partir du** et cliquez sur **Désactiver**. Il sort de
   la liste des relevés jusqu'à ce que vous le **Réactiver**.

Si votre liste de compteurs est encore dans un tableur, importez-la --
voir [Importer des membres et des parcelles](csv-import.md#4-metering-points).

## 2. Option A : saisir les relevés sur votre téléphone pendant la tournée {#2-option-a-enter-readings-on-your-phone-while-you-walk}

1. Ouvrez **Eau → Relevés** sur votre téléphone. La page affiche
   l'année en cours ; choisissez-en une autre dans la liste déroulante
   des années en haut si nécessaire.
2. La page liste **Compteur principal**, **Parcelles** (triées par
   numéro de parcelle) et **Raccordements du club**. Chaque ligne
   affiche le numéro du compteur et le relevé de l'**Année précédente**
   pour contrôle.
3. Tapez le relevé dans le champ de la ligne et touchez le bouton
   d'enregistrement à côté. La ligne affiche alors la valeur comme
   **enregistré**.
4. Continuez avec le compteur suivant. Les lignes sans valeur indiquent
   **Pas encore renseigné**.

Les relevés saisis ici reçoivent la date du jour. Pour utiliser une
autre date ou ajouter une note, saisissez plutôt le relevé sur la page
du point de mesure (option C).

## 3. Option B : relever sur papier ou dans un tableur, puis importer {#3-option-b-collect-on-paper-or-in-a-spreadsheet-then-import}

1. Ouvrez **Eau → Relevés**, choisissez l'année et cliquez sur
   **Export CSV**. Vous obtenez un fichier avec une ligne par compteur :
   **Type**, **Numéro de parcelle**, **Libellé**, **Numéro de compteur**,
   **Année**, et des colonnes **Date**, **Relevé** et **Note** vides.
2. Imprimez-le ou remplissez-le sur une tablette. Renseignez **Date** et
   **Relevé** pour chaque compteur relevé.
3. De retour sur **Eau → Relevés**, cliquez sur **Import CSV**,
   choisissez le fichier et cliquez sur **Importer**.
4. Sur **Associer les colonnes CSV**, vérifiez l'association. Si votre
   fichier n'a pas de colonne d'année, saisissez-la dans **Année par
   défaut (facultatif)**. Cliquez sur **Importer**.
5. Lisez le résumé sur la page des relevés : combien de relevés ont été
   enregistrés, et combien de lignes ont été ignorées et pourquoi.

Les lignes sans relevé sont ignorées comme « ligne invalide » -- c'est
normal pour les compteurs que vous n'avez pas encore relevés. Détails
sur les colonnes et les messages d'erreur :
[Importer des membres et des parcelles](csv-import.md#5-meter-readings).

## 4. Option C : saisir un relevé unique avec date et note {#4-option-c-enter-a-single-reading-with-date-and-note}

1. Ouvrez **Eau → Points de mesure** et cliquez sur le point de mesure.
2. En bas, sous **Relevés**, renseignez **Année**, **Date**,
   **Relevé du compteur** et éventuellement une **Note**.
3. Cliquez sur **Enregistrer un relevé**.

Le tableau **Relevés** de la même page liste chaque année avec son
relevé et sa consommation. Un relevé erroné peut y être supprimé.

## 5. Quand un relevé semble faux {#5-when-a-reading-looks-wrong}

Un relevé inférieur à celui de l'année précédente (ou supérieur à un
relevé ultérieur déjà enregistré) est **quand même enregistré**, avec un
avertissement comme *« Relevé enregistré, mais veuillez le vérifier : Le
relevé de compteur (…) est inférieur au relevé précédent (…) du même
compteur. Un relevé antérieur a-t-il été estimé ? Veuillez vérifier. »*
Le relevé garde un marqueur d'avertissement sur la page des relevés et
sur le point de mesure.

Causes fréquentes : une faute de frappe, un chiffre mal lu, un relevé
antérieur estimé trop haut, ou un compteur qui a en fait été remplacé
(étape 6). Corrigez la valeur en saisissant à nouveau le relevé pour la
même année.

## 6. Un compteur est remplacé { #a-meter-is-replaced }

Quand un compteur est physiquement changé -- par exemple parce que son
étalonnage expire :

1. Relevez l'ancien compteur une dernière fois, si vous le pouvez
   encore, et saisissez-le sur la page du point de mesure comme relevé
   de l'année (option C).
2. Dans la carte **Compteur Eau actuel** (**Compteur Électricité
   actuel** pour l'électricité), ouvrez **Échanger le compteur**.
3. Saisissez **Ancien compteur retiré le**, **Nouveau compteur installé
   le**, le **Nouveau numéro**, **Étalonné jusqu'au** (une année) et le
   **Relevé initial** du nouveau compteur (généralement ce que son
   afficheur indique à l'installation).
4. Cliquez sur **Échanger** et confirmez.

L'ancien compteur n'est pas supprimé : il passe dans **Anciens
compteurs** avec ses dates d'installation et de retrait et son
**Dernier relevé**. Désormais, les relevés vont au nouveau compteur,
dont la consommation part de son **Relevé initial**.

!!! tip "Consommation l'année du changement"
    Renseignez **Relevé final de l'ancien compteur** dans le formulaire
    d'échange -- ce qu'affiche l'ancien compteur le jour du retrait. La
    consommation de l'année additionne alors les deux compteurs (l'ancien
    jusqu'au changement, le nouveau à partir de son relevé initial), et
    c'est ce total que facture la facture annuelle. Sans le relevé final,
    la part de l'ancien compteur depuis son dernier relevé n'est pas
    facturée.

!!! tip "Une faute de frappe, pas un nouveau compteur ?"
    Si vous avez seulement mal tapé le numéro du compteur ou le relevé
    initial, utilisez plutôt **Modifier le compteur**.
    **Échanger le compteur** est réservé à un vrai remplacement.

## 7. Vérifier l'année {#7-check-the-year}

1. Ouvrez **Eau → Évaluation** et choisissez l'année.
2. Les tuiles comparent **Compteur principal** avec **Total parcelles**
   et **Total club** ; les tableaux en dessous listent chaque point de
   mesure avec sa **Consommation**. Les points auxquels il manque encore
   un relevé affichent **pas de relevé**.
3. Si les parcelles et les raccordements de l'association ont consommé
   ensemble plus que le compteur principal, Parcella affiche un
   avertissement. C'est normal tant que les relevés sont en cours de
   saisie ; une fois tous saisis, cela signale un compteur mal lu.
4. **Export CSV** télécharge l'évaluation pour vos propres archives ou
   pour le fournisseur.

**Eau → Aperçu** vous indique aussi combien de points de mesure n'ont
pas encore de relevé pour l'année, avec un lien
**Enregistrer maintenant →**.

## 8. Fixer le prix pour la facturation {#8-set-the-price-for-billing}

Si vous facturez l'eau et l'électricité avec les factures annuelles de
Parcella :

1. Ouvrez **Eau → Configuration**.
2. Sous **Nouveau/mise à jour du prix**, saisissez l'**Année** et le
   **Prix par m³** et éventuellement une **Note** (par ex.
   « changement de tarif du fournisseur »).
3. Cliquez sur **Enregistrer**.

Sans prix pour l'année, la série de factures ne facture pas d'eau pour
cette année. Poursuivez ensuite avec
[Établir les factures annuelles](annual-invoicing.md).

## Voir aussi {#related}

- [Eau et électricité](../modules/metering.md)
- [Importer des membres et des parcelles](csv-import.md)
- [Établir les factures annuelles](annual-invoicing.md)
- [Transmettre une parcelle](parcel-handover.md)
- Glossaire : [point de mesure](../glossary.md#metering-point),
  [compteur](../glossary.md#meter)

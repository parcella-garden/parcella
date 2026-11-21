# Importer des membres et des parcelles {#importing-members-and-parcels}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Si votre association tient déjà sa liste de membres, de parcelles ou de
compteurs dans un tableur, vous n'avez pas à tout ressaisir. Enregistrez
le tableur en fichier CSV, téléversez-le, indiquez à Parcella quelle
colonne correspond à quoi, et importez.

Cela fonctionne de la même façon pour les **parcelles**, les
**membres**, les **points de mesure**, les **relevés de compteurs** et
les **contacts externes**. Ce guide les parcourt dans l'ordre qui a du
sens pour une nouvelle installation.

!!! info "Qui peut le faire"
    Importer des membres et des parcelles nécessite le droit
    d'**écriture** sur **Membres et parcelles** ; les points de mesure et
    les relevés nécessitent l'écriture sur **Eau** ou **Électricité** ;
    les contacts externes nécessitent l'écriture sur **Contacts
    externes**. Les membres du bureau et les administrateurs ont tous ces
    droits.

!!! warning "Téléchargez d'abord une sauvegarde"
    Un import écrit de nombreux enregistrements d'un coup et il n'y a
    pas d'« annuler ». Ouvrez **Administration → Utilisateurs** et
    cliquez sur **Télécharger la sauvegarde** avant de commencer. Voir
    [Sauvegarde et restauration](../administration/backup.md).

## Comment fonctionne chaque import {#how-every-import-works}

Les cinq imports ont les deux mêmes étapes.

1. **Téléverser.** Sur la page de la liste, cliquez sur **Import CSV**,
   choisissez le fichier et cliquez sur **Importer**. Rien n'est encore
   enregistré.
2. **Associer les colonnes CSV.** Parcella affiche un tableau : une
   colonne par colonne de votre fichier, avec votre en-tête en haut et
   les cinq premières lignes de données en dessous. Au-dessus de chaque
   colonne se trouve une liste déroulante. Parcella a déjà deviné le
   champ correspondant à partir de l'en-tête (les en-têtes anglais et
   allemands fonctionnent, par exemple « Nachname » ou « Last name »).
   Vérifiez chaque liste déroulante, corrigez les mauvaises, et réglez
   les colonnes dont vous ne voulez pas sur **— Ignorer —**. Cliquez
   ensuite sur **Importer**.

Vous revenez ensuite sur la page de la liste avec un court résumé :
combien de lignes ont été créées, mises à jour ou ignorées, et les
raisons pour les premières lignes ignorées.

### À quoi doit ressembler votre fichier {#what-your-file-should-look-like}

- **La première ligne contient les en-têtes de colonnes.** Chaque ligne
  en dessous est un enregistrement. Les en-têtes n'ont pas besoin de
  correspondre exactement -- vous les associez à l'étape 2.
- **Point-virgule ou virgule** entre les colonnes : Parcella détecte
  celui qu'utilise votre fichier.
- **L'UTF-8 est préférable.** La plupart des tableurs proposent « CSV
  UTF-8 » à l'enregistrement. Le « CSV » simple d'Excel (Windows/ANSI)
  fonctionne aussi : les trémas et accents passent dans les deux cas.
- **Dates** au format `2026-03-15` ou `15.03.2026` (aussi `15.03.26`).
- **Nombres décimaux** avec une virgule ou un point : `312,5` et `312.5`
  fonctionnent tous deux. Les montants bancaires et les relevés de
  compteurs peuvent aussi avoir des séparateurs de milliers, à
  l'allemande ou à l'anglaise : `12.345,6` et `12,345.6`.
- **Plusieurs valeurs dans une cellule** (adresses e-mail, numéros de
  téléphone, étiquettes) sont séparées par un point-virgule. Votre
  tableur met des guillemets autour d'une telle cellule à
  l'enregistrement -- c'est normal.

!!! tip "Partir d'un export"
    Le modèle le plus simple est l'export de Parcella lui-même. Chaque
    liste avec un import a aussi un **Export CSV**. Exportez la liste
    (encore vide ou remplie de données d'exemple), remplissez le fichier
    dans votre tableur, et réimportez-le : les en-têtes correspondent
    alors sans aucun travail d'association.

## 1. Parcelles {#1-parcels}

Importez d'abord les parcelles. Les membres, points de mesure et relevés
font référence aux parcelles par leur numéro.

1. Ouvrez **Parcelles** et cliquez sur **Import CSV**.
2. Choisissez votre fichier et cliquez sur **Importer**.
3. Sur **Associer les colonnes CSV**, associez au moins **Numéro de
   parcelle**. Les autres champs sont facultatifs.
4. Cliquez sur **Importer**. Le résumé ressemble à *« 24 importé(s),
   0 ignoré(s) »*.

| Champ | Ce qu'attend Parcella |
|---|---|
| **Numéro de parcelle** | Obligatoire. Enregistré en majuscules (« g12 » devient « G12 »). |
| **Superficie (m²)** | Un nombre, avec virgule ou point comme séparateur décimal. Toute autre valeur est laissée vide. |
| **Latitude** / **Longitude** | Position GPS facultative, en degrés décimaux (par ex. `51,339695`). |
| **Statut** | `ACTIVE`, `TERMINATED`, `COMMUNAL` ou `DELETED` (majuscules ou minuscules). Vide ou toute autre valeur signifie actif. |
| **Notes** | Texte libre. |

!!! warning "Les parcelles existantes sont ignorées, pas mises à jour"
    Si un numéro de parcelle existe déjà dans Parcella, cette ligne est
    **ignorée** et la parcelle existante reste exactement telle quelle.
    Pour modifier des parcelles existantes, faites-le à la main. Les
    lignes sans numéro de parcelle sont ignorées et comptées à part dans
    le résumé.

L'import des parcelles n'attribue **pas** de locataires. L'export des
parcelles a une colonne avec les noms des locataires, mais l'import
l'ignore -- voir l'étape 3 ci-dessous.

## 2. Membres {#2-members}

1. Ouvrez **Membres** et cliquez sur **Import CSV**.
2. Choisissez votre fichier et cliquez sur **Importer**.
3. Sur **Associer les colonnes CSV**, associez au moins **Prénom** et
   **Nom**. Sans les deux, l'import s'arrête avec *« Veuillez associer
   les colonnes du prénom et du nom avant d'importer. »*
4. Cliquez sur **Importer**. Le résumé ressemble à *« 80 nouvellement
   importé(s), 0 mis à jour »*.

| Champ | Ce qu'attend Parcella |
|---|---|
| **Prénom**, **Nom** | Obligatoires. Une ligne où l'un des deux est vide est ignorée. |
| **Rue**, **Code postal**, **Ville** | Texte libre. |
| **Date de naissance** | Une date (voir ci-dessus). Sert aussi à distinguer deux membres portant le même nom. |
| **IBAN** | Texte libre, non vérifié. |
| **Membre depuis**, **Membre jusqu'au** | Dates. Un **Membre jusqu'au** vide signifie un membre actif. |
| **Notifications par e-mail** | « No », « Nein », « false » ou « 0 » signifie que le membre ne veut **pas** recevoir les informations de l'association par e-mail ; toute autre valeur renseignée signifie oui. Une cellule vide ou une colonne non associée signifie oui pour un nouveau membre et « inchangé » pour un membre existant. |
| **Adresses e-mail** | Une ou plusieurs, séparées par des points-virgules. La première devient l'adresse principale. |
| **Numéros de téléphone** | Un ou plusieurs, séparés par des points-virgules. Le premier devient le numéro principal. |
| **Notes** | Texte libre. |

**Correspondance avec les membres existants.** Pour chaque ligne,
Parcella cherche un membre existant avec le même prénom et le même nom
-- et, si la ligne a une date de naissance, la même date de naissance.
S'il en trouve exactement un, il **met à jour** ce membre au lieu d'en
créer un second. Si plusieurs membres portent ce nom, les adresses
e-mail et numéros de téléphone de la ligne désignent le bon ; si la
ligne correspond encore à plusieurs, elle est ignorée et nommée dans le
résumé. Un e-mail ou un téléphone seul ne fait jamais correspondre un
membre portant un autre nom.

Une mise à jour ne modifie que ce que contient la ligne : une colonne
réglée sur **— Ignorer —**, ou une cellule vide, laisse la valeur
enregistrée telle quelle. Vous pouvez donc mettre à jour seulement les
adresses avec un fichier qui ne contient que les noms et les adresses.
Les adresses e-mail et numéros de téléphone ne sont jamais modifiés lors
d'une mise à jour ; ils ne sont ajoutés que pour les nouveaux membres.

Les étiquettes, les attributions de parcelles et le réglage **Ne
souhaite pas de cadeau d'anniversaire** ne font pas partie de l'import.
L'export contient bien des colonnes **Parcelles** et **Étiquettes**,
mais l'import les ignore.

## 3. Attribuer les membres à leurs parcelles {#3-assign-members-to-their-parcels}

Il n'y a pas d'import pour les baux. Attribuez-les à la main une fois
que les membres et les parcelles existent :

1. Ouvrez une parcelle sous **Parcelles**.
2. Dans **Locataires actuels**, commencez à taper le nom du membre dans
   **Choisir un membre…** et choisissez-le dans la liste.
3. Saisissez éventuellement la date de début du bail.
4. Laissez **Utiliser comme adresse de facturation** coché pour le
   locataire qui doit recevoir les factures de la parcelle.
5. Cliquez sur **Attribuer**.

Avec de nombreuses parcelles, le bouton **Suivant** en haut de la page
de la parcelle vous mène directement à la suivante.

Plus d'informations : [Parcelles](../modules/parcels.md).

## 4. Points de mesure {#4-metering-points}

Les points de mesure sont les raccordements d'eau et d'électricité
(compteur principal, un par parcelle, raccordements de l'association).
L'eau et l'électricité s'importent séparément, chacune dans son propre
menu.

1. Ouvrez **Eau → Points de mesure** (ou **Électricité → Points de
   mesure**) et cliquez sur **Import CSV**.
2. Choisissez votre fichier et cliquez sur **Importer**.
3. Associez les colonnes et cliquez sur **Importer**. Au moins une
   colonne doit être associée.

| Champ | Ce qu'attend Parcella |
|---|---|
| **Type** | `PARCEL`, `MAIN_METER` ou `CLUB`. Si vous n'associez pas du tout cette colonne, chaque ligne compte comme un raccordement de parcelle. Si vous l'associez, une ligne au type vide ou inconnu est ignorée (« type invalide »). |
| **Numéro de parcelle** | Obligatoire pour les raccordements de parcelle ; doit correspondre à un numéro de parcelle existant, sinon la ligne est ignorée (« parcelle introuvable »). |
| **Libellé** | Le nom d'un compteur principal ou d'un raccordement de l'association, par ex. « Local ». |
| **Numéro de compteur** | Le numéro imprimé sur le compteur. |
| **Installé le** | Une date. |
| **Étalonné jusqu'au** | Une **année** seulement, par ex. `2031`. |
| **Relevé initial** | Le relevé à l'installation du compteur. Vide signifie 0. |
| **Facteur** | Généralement vide (= 1). Pour les compteurs qui n'affichent qu'une fraction de la valeur réelle, par ex. `20`. Doit être supérieur à 0. |

L'import ne fait que **créer** des points de mesure. Une parcelle qui a
déjà un point de mesure pour ce fluide, ou un compteur principal ou un
raccordement de l'association portant le même libellé, est ignoré comme
« existe déjà » -- importer deux fois le même export ne fait donc pas de
dégâts. Les nouveaux points de mesure sont toujours activés au départ.

!!! note
    **Étalonné jusqu'au** est une année. Une date dans cette colonne
    (`30.06.2027`, `2027-06`, `06/2027`) convient aussi : Parcella en
    extrait l'année. Une ligne dont la valeur n'a pas d'année à quatre
    chiffres (`06/27`, `bientôt`) est ignorée avec « « Étalonné jusqu'au »
    n'est pas une année » ; les autres lignes sont importées.

Plus d'informations : [Eau et électricité](../modules/metering.md).

## 5. Relevés de compteurs {#5-meter-readings}

Les relevés sont rattachés à des points de mesure qui existent déjà ;
l'import ne crée jamais de point de mesure.

1. Ouvrez **Eau → Relevés** (ou **Électricité → Relevés**) et cliquez
   sur **Import CSV**.
2. Choisissez votre fichier et cliquez sur **Importer**.
3. Associez les colonnes. Si votre fichier n'a pas de colonne d'année,
   ou si certaines lignes la laissent vide, saisissez l'année dans
   **Année par défaut (facultatif)**.
4. Cliquez sur **Importer**.

| Champ | Ce qu'attend Parcella |
|---|---|
| **Type** | Comme pour les points de mesure. Non associé = chaque ligne est un raccordement de parcelle. |
| **Numéro de parcelle** / **Libellé** | Trouvent le point de mesure, comme ci-dessus. |
| **Numéro de compteur** | Contrôle facultatif. S'il ne correspond pas au compteur actuellement installé, la ligne est ignorée (« numéro de compteur différent ») -- elle appartient probablement à un compteur remplacé depuis. |
| **Année** | L'année à laquelle appartient le relevé. Prime sur **Année par défaut (facultatif)**. |
| **Date** | Le jour du relevé. Obligatoire. |
| **Relevé** | La valeur affichée. Obligatoire. |
| **Note** | Texte libre. |

Parcella ne devine jamais l'année à partir de la date. Un relevé fait en
janvier peut encore appartenir à la facturation de l'année précédente :
c'est donc vous qui indiquez l'année.

Un fichier peut contenir plusieurs années. Si un point de mesure a déjà
un relevé pour cette année, l'import le **remplace**.

Un relevé qui semble invraisemblable -- inférieur au précédent, par
exemple -- est quand même enregistré. Le résumé affiche alors un
avertissement séparé avec les lignes concernées, pour que vous puissiez
les vérifier.

Plus d'informations : [Relever les compteurs](meter-readings.md).

## 6. Contacts externes {#6-external-contacts}

Fournisseurs, artisans et administrations, si vous utilisez le module
**Contacts externes**.

1. Ouvrez **Contacts externes** et cliquez sur **Import CSV**.
2. Choisissez votre fichier et cliquez sur **Importer**.
3. Sur **Associer les colonnes**, associez les colonnes. Aucun champ
   n'est obligatoire ; les lignes complètement vides sont ignorées.
4. Cliquez sur **Importer**.

| Champ | Ce qu'attend Parcella |
|---|---|
| **Type (entreprise/personne)** | « Firma », « Company » ou « Unternehmen » pour une entreprise ; « Person » pour une personne. Sans lui, une ligne avec un prénom ou un nom est une personne, sinon une entreprise. |
| **Nom de l'entreprise** | Pour une entreprise : son nom. Pour une personne : l'entreprise à laquelle elle appartient -- créée si elle n'existe pas encore. |
| **Prénom**, **Nom**, **Fonction** | Pour les personnes. |
| **Rue**, **Code postal**, **Ville**, **IBAN** | Adresse et coordonnées bancaires. Pour une personne rattachée à une entreprise, elles remplissent les champs vides de l'entreprise. |
| **Adresses e-mail**, **Numéros de téléphone**, **Étiquettes** | Plusieurs valeurs séparées par des points-virgules. |
| **Notes** | Texte libre. |

Une entreprise qui existe déjà (même nom, sans tenir compte des
majuscules et minuscules) ou une personne portant le même nom est
**mise à jour** à partir des cellules non vides de la ligne. Les numéros
de téléphone, e-mails et étiquettes manquants sont ajoutés. Contrairement
à l'import des membres, rien n'est jamais effacé ni supprimé.

Plus d'informations : [Contacts externes](../modules/external-contacts.md).

## Problèmes fréquents {#common-problems}

| Ce que vous voyez | Pourquoi, et que faire |
|---|---|
| *« Ce fichier CSV semble vide. »* | Le fichier n'a aucune ligne. Vérifiez que vous avez enregistré la bonne feuille. |
| Toutes les données se retrouvent dans une seule colonne sur l'écran d'association | Parcella n'a pas pu déterminer le séparateur. Réenregistrez le fichier en « CSV (séparateur : point-virgule) » ou « CSV (séparateur : virgule) ». |
| Caractères bizarres à la place des accents | Le fichier utilise un encodage inhabituel (ni UTF-8 ni Windows/ANSI, par ex. venant d'un vieux Mac). Réenregistrez-le en « CSV UTF-8 ». |
| Membres ignorés avec « prénom ou nom manquant » | Ces lignes ont une cellule de nom vide, ou la colonne du nom n'a pas été associée. |
| Un membre apparaît deux fois | Les deux lignes diffèrent par l'orthographe ou la date de naissance, donc Parcella les traite comme deux personnes différentes. Supprimez le doublon à la main. |
| L'adresse d'un membre existant est soudain vide | Le membre a été mis à jour à partir d'une ligne ou d'un fichier sans cette colonne. Voir l'avertissement de l'étape 2 ; restaurez depuis votre sauvegarde si nécessaire. |
| Parcelles « ignorées » | Le numéro de parcelle existe déjà. Modifiez les parcelles existantes à la main. |
| Points de mesure « parcelle introuvable » | Le numéro de parcelle du fichier n'existe pas dans Parcella -- importez d'abord les parcelles, et vérifiez l'orthographe (« G12 » ou « G 12 »). |
| Relevés « point de mesure introuvable » | Importez ou créez d'abord les points de mesure. Si vous avez associé **Type**, vérifiez sa valeur. |
| Relevés « ligne invalide » | **Date** ou **Relevé** est vide ou incompréhensible, ou il n'y a pas d'année (ni colonne **Année** ni **Année par défaut (facultatif)**). |
| Relevés « aucun compteur actif » | Le point de mesure n'a pas de compteur installé. Ajoutez-en un sur la page du point de mesure. |
| `'` en tête des numéros de téléphone exportés | Parcella l'ajoute aux cellules commençant par `+`, `-`, `=` ou `@` pour que les tableurs ne les traitent pas comme des formules. Supprimez-le avant d'importer des membres, ou laissez-le -- l'import des contacts externes le retire pour vous. |

## Voir aussi {#related}

- [Membres](../modules/members.md)
- [Parcelles](../modules/parcels.md)
- [Eau et électricité](../modules/metering.md)
- [Contacts externes](../modules/external-contacts.md)
- [Configurer une nouvelle association](new-club-setup.md)
- [Relever les compteurs](meter-readings.md)

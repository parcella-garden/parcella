# Contacts externes {#external-contacts}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les contacts externes sont le carnet d'adresses de l'association pour
toutes les personnes qui ne sont pas membres : fournisseurs, artisans,
le service des eaux, la mairie. Un contact est soit une **entreprise**,
soit une **personne**, et une personne peut travailler dans une
entreprise. Vous pouvez relier des contacts aux factures reçues et aux
demandes d'achat, leur attribuer des étiquettes, et conserver leurs
documents dans le cloud de l'association.

!!! info "Qui peut l'utiliser"
    Les membres du bureau et les administrateurs ont toujours un accès
    complet. Tous les autres ne voient rien de ce module tant qu'un
    groupe ne leur accorde pas des droits sur **Contacts externes** (voir
    [Groupes](../administration/groups.md)) :

    - **Lecture** -- voir la liste et les pages de contact, exporter en
      CSV, voir la page des étiquettes, télécharger des documents.
    - **Écriture** -- créer et modifier des contacts, ajouter des
      numéros de téléphone, adresses e-mail et étiquettes, renommer des
      étiquettes, importer un CSV, choisir le dossier de documents d'un
      contact et téléverser des documents.
    - **Suppression** -- supprimer des contacts, numéros de téléphone,
      adresses e-mail et étiquettes, et fusionner des entreprises.

    Le module s'active avec **Contacts externes** sous
    [Activer et désactiver les modules](../administration/modules.md).
    Il est activé par défaut.

## Entreprises et personnes {#companies-and-people}

- Une **entreprise** a un nom d'entreprise, une adresse, un IBAN et ses
  propres numéros de téléphone et adresses e-mail.
- Une **personne** a un prénom et un nom, une fonction (par ex.
  « Employé », « Gérant ») et éventuellement une entreprise. Si la
  personne n'a pas d'adresse ou d'IBAN propre, sa page affiche ceux de
  l'entreprise.
- Qu'un contact soit une entreprise ou une personne se décide à sa
  création et ne peut plus être changé ensuite.
- Un nom d'entreprise ne peut exister qu'une fois, de même que le nom
  d'une personne (les majuscules n'ont pas d'importance). Les membres ne
  comptent pas -- un contact peut porter le même nom qu'un membre.
- Chaque champ est facultatif. Un contact sans aucun nom s'affiche comme
  **Contact sans nom**.

## Liste des contacts {#contact-list}

![Contacts externes](../assets/screenshots/external-contacts/list.png)

**Contacts externes** dans la navigation liste chaque entreprise, avec
ses personnes en retrait en dessous, et chaque personne qui n'appartient
à aucune entreprise. La liste est triée par ordre alphabétique du nom de
l'entreprise, ou du nom de famille pour les personnes sans entreprise.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Import CSV** | Ouvre la [boîte de dialogue d'import](#csv-import). Nécessite le droit d'écriture. |
| **Export CSV** | Télécharge la liste sous forme de fichier CSV (voir [Export CSV](#csv-export)). Utilise la recherche et le filtre d'étiquette actuels. |
| **Gérer les étiquettes** | Ouvre la [page des étiquettes](#contact-tags). |
| **Nouveau contact** | Ouvre le [formulaire de contact](#contact-form). Nécessite le droit d'écriture. |
| Champ de recherche | Cherche dans le nom de l'entreprise, le prénom et le nom, la fonction, la rue, le code postal, la ville, l'IBAN, les notes, les numéros de téléphone et les adresses e-mail. Cliquez sur **Rechercher** pour appliquer. |
| **Toutes les étiquettes** / une étiquette | N'affiche que les contacts avec cette étiquette. Affiché seulement une fois que des étiquettes existent. |
| **Réinitialiser** | Efface la recherche et le filtre d'étiquette. Affiché seulement tant qu'un filtre est actif. |

| Colonne | Ce qu'elle affiche |
|---|---|
| **Nom** | Une icône de bâtiment pour les entreprises, une icône de personne pour les personnes ; le nom renvoie vers la page du contact. Les personnes affichent leur fonction après le nom. |
| **Étiquettes** | Les étiquettes du contact. Cliquez sur une étiquette pour filtrer la liste dessus. |
| **Téléphone** | Le premier numéro de téléphone. |
| **E-mail** | La première adresse e-mail, sous forme de lien mail. |
| Bouton œil | Ouvre le contact. |

Quand une recherche ou une étiquette correspond à une personne, son
entreprise est aussi listée, et la personne correspondante est mise en
évidence en dessous. Le pied indique combien d'entrées (entreprises et
personnes sans entreprise) sont listées.

## Formulaire de contact {#contact-form}

![Nouveau contact externe](../assets/screenshots/external-contacts/form-new.png)

**Nouveau contact** ouvre un formulaire vide, **Modifier** sur la page
d'un contact le formulaire rempli. **Ajouter une personne** sur la page
d'une entreprise l'ouvre comme nouvelle personne avec l'entreprise déjà
renseignée.

Pour un nouveau contact, choisissez d'abord **Entreprise** ou
**Personne** en haut. Le formulaire n'affiche alors que les champs de ce
type.

### Entreprise / Personne {#company-person}

| Champ | Affiché pour | Ce qu'il fait |
|---|---|---|
| **Prénom**, **Nom** | Personne | Le nom de la personne. L'un des deux suffit. |
| **Nom de l'entreprise** | Entreprise | Le nom de l'entreprise. |
| **Entreprise (facultatif)** | Personne | L'entreprise où travaille la personne. Propose les entreprises existantes pendant la saisie. Une entreprise existante est reliée ; un nouveau nom crée cette entreprise. Laissez vide pour une personne seule. Lors d'une **Modification**, le vider retire la personne de l'entreprise. |
| **Fonction** | Personne | Par ex. « Employé, Gérant ». |
| **E-mail**, **Téléphone** | Nouveaux contacts | La première adresse e-mail et le premier numéro de téléphone. Ajoutez-en d'autres plus tard sur la page du contact. |

La note « Tous les champs sont facultatifs. Un nom d'entreprise et le
nom d'une personne ne peuvent exister qu'une seule fois. » vous rappelle
les [règles ci-dessus](#companies-and-people).

### Adresse et coordonnées bancaires {#address-bank-details}

| Champ | Ce qu'il fait |
|---|---|
| **Rue**, **Code postal**, **Ville** | L'adresse postale. |
| **IBAN** | Compte bancaire, par ex. pour payer les factures du fournisseur. Jusqu'à 34 caractères. |

Pour une personne dans une entreprise : « Laisser vide pour utiliser
celles de l'entreprise. Saisie avec une nouvelle entreprise, elle devient
l'adresse de l'entreprise. » Si l'entreprise n'a pas encore d'adresse ou
d'IBAN, ce que vous saisissez est enregistré sur l'entreprise ; si c'est
identique à celui de l'entreprise, ce n'est pas enregistré deux fois.
Seuls une adresse ou un IBAN réellement différents restent sur la
personne.

### Notes et étiquettes {#notes-and-tags}

| Champ | Ce qu'il fait |
|---|---|
| **Notes** | Texte libre -- horaires d'ouverture, numéro client, numéro de ticket. La recherche de la liste le trouve. |
| Cases d'étiquettes | Cochez des étiquettes existantes. |
| **Nouvelles étiquettes, séparées par des virgules** | Tapez de nouvelles étiquettes ; elles sont créées et ajoutées. |

Cliquez sur **Créer le contact** (nouveau) ou **Enregistrer les
modifications** (modification), ou sur **Annuler**. Si une entreprise ou
une personne du même nom existe déjà, le formulaire revient avec un
message comme « Une entreprise … existe déjà. » et conserve ce que vous
avez saisi.

## Page du contact {#contact-page}

<!-- TODO(verify): no screenshot -- the sample data contains no external contacts, so the screenshot tool has no contact page to open. Add one once sample data seeds contacts. -->

### Boutons {#buttons}

| Bouton | Ce qu'il fait |
|---|---|
| **Modifier** | Ouvre le formulaire de contact. Nécessite le droit d'écriture. |
| **Précédent** / **Suivant** | L'entrée précédente ou suivante de la liste, en conservant votre recherche et votre filtre d'étiquette. Clavier : ++ctrl+left++ et ++ctrl+right++. |
| **Retour à la liste** | Revient à la liste avec le même filtre. |

### Entreprise / Personne {#company-person_1}

| Champ | Ce qu'il affiche |
|---|---|
| **Entreprise** (entreprise) | Le nom de l'entreprise. |
| **Nom**, **Fonction**, **Entreprise** (personne) | Le nom de la personne, sa fonction et un lien vers son entreprise. Une entreprise supprimée est marquée « (supprimé) ». |
| **Adresse** | L'adresse du contact. Pour une personne qui n'en a pas, celle de l'entreprise, marquée **Adresse de l'entreprise**. |
| **IBAN** | L'IBAN du contact. Pour une personne qui n'en a pas, celui de l'entreprise, marqué **IBAN de l'entreprise**. |

### Personnes {#people}

Seulement sur la page d'une entreprise : chaque personne de
l'entreprise, avec fonction, numéros de téléphone et adresses e-mail.
**Ajouter une personne** crée une nouvelle personne dans cette
entreprise (droit d'écriture). « Aucune personne dans cette entreprise
pour l'instant. » s'il n'y en a aucune.

### Étiquettes {#tags}

Les étiquettes du contact ; cliquez sur l'une pour voir tous les
contacts qui l'ont. Avec le droit d'écriture, le **x** sur une étiquette
la retire de ce contact, et le champ **Ajouter une étiquette…** ajoute
une étiquette existante ou nouvelle (jusqu'à 100 caractères).
**Gérer les étiquettes** ouvre la [page des étiquettes](#contact-tags).

### Numéros de téléphone et adresses e-mail {#phone-numbers-and-email-addresses}

| Champ / bouton | Ce qu'il fait |
|---|---|
| Numéro / adresse | Cliquez pour appeler ou écrire un e-mail. Un libellé s'affiche entre parenthèses. |
| Champ numéro / adresse, **Libellé (facultatif)**, **+** | Ajoute un autre numéro ou une autre adresse, par ex. avec le libellé « Bureau » ou « Factures ». Nécessite le droit d'écriture. |
| Bouton corbeille | Supprime le numéro ou l'adresse. Nécessite le droit de suppression. |

### Factures reçues et demandes d'achat {#incoming-invoices-and-purchase-requests}

Liste les [factures reçues](finances/incoming-invoices.md) et les
[demandes d'achat](purchase-requests.md) reliées à ce contact -- sur la
page d'une entreprise, aussi celles reliées à ses personnes, avec le nom
de la personne après l'entrée. Chaque carte n'est affichée que si ce
module est activé et que vous pouvez le lire.

| Carte | Colonnes |
|---|---|
| **Factures reçues** | Date de facture, numéro de facture (ou expéditeur), montant total. |
| **Demandes d'achat** | Date de création, titre, coût estimé. |

### Documents {#documents}

Affiché quand le module de stockage cloud est activé. Les courriers,
offres et contrats ne sont pas stockés dans Parcella mais dans un dossier
du cloud de l'association ; cette carte affiche ce dossier.

- Un administrateur définit d'abord le dossier de base sous
  [Intégrations](../administration/integrations.md) (**Dossier des
  documents des contacts externes**). D'ici là, la carte l'indique.
- Le dossier de chaque contact est créé à la main dans le cloud, à
  l'intérieur du dossier de base. Sur la page du contact, une personne
  ayant le droit d'écriture le choisit ensuite dans la liste **Dossier**
  et clique sur **Enregistrer le dossier**. **Changer de dossier** en
  choisit un autre ; **— aucun dossier —** supprime le lien (les fichiers
  restent dans le cloud).
- Une fois un dossier choisi, la carte liste ses fichiers et
  sous-dossiers. Cliquez sur un sous-dossier pour l'ouvrir, sur un
  fichier pour le télécharger. Le chemin au-dessus de la liste permet de
  remonter.
- Avec le droit d'écriture, **Téléverser** place un fichier dans le
  dossier actuellement affiché.
- La suppression, le renommage et le déplacement de fichiers se font
  dans le cloud lui-même.

Les documents appartiennent à l'entreprise : la page d'une personne
renvoie plutôt aux documents de l'entreprise (« Les documents sont rangés
avec l'entreprise : »).

!!! warning
    Si vous renommez le dossier d'un contact dans le cloud, Parcella en
    perd la trace. Choisissez-le à nouveau sur la page du contact.

### Notes {#notes}

Les notes, s'il y en a.

### Zone de danger {#danger-zone}

Affichée avec le droit de suppression.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Fusionner avec** + **Fusionner** | Seulement sur la page d'une entreprise. Pour deux entrées de la même société (par ex. « Müller GmbH » et « Mueller GmbH ») : choisissez l'entreprise à conserver et cliquez sur **Fusionner**, puis confirmez. Les personnes, numéros de téléphone, adresses e-mail, étiquettes et factures et demandes d'achat reliées passent à l'entreprise choisie. Son adresse, son IBAN et son dossier de documents sont complétés à partir de celle-ci là où ils manquent ; les notes sont ajoutées à ses notes. Cette entreprise est ensuite supprimée, et celle conservée s'ouvre. |
| **Supprimer le contact** | Supprime le contact après confirmation. Il disparaît de la liste et des sélecteurs, mais les factures et demandes d'achat reliées l'affichent toujours (marqué « supprimé » là où elles l'affichent). Son nom redevient libre. Une entreprise qui a encore des personnes ne peut pas être supprimée : « Cette entreprise a encore des personnes. Déplacez-les ou supprimez-les d'abord. » |

## Étiquettes des contacts {#contact-tags}

![Étiquettes des contacts](../assets/screenshots/external-contacts/tags.png)

**Gérer les étiquettes** ouvre **Étiquettes des contacts**. Les
étiquettes des contacts sont distinctes des étiquettes des membres.
**Retour aux contacts** revient à la liste.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Signale les candidats :** | Choisissez une étiquette (ou **— aucune —**) et cliquez sur **Enregistrer**. Les candidats dont le nom, l'adresse e-mail ou le numéro de téléphone correspond à un contact portant cette étiquette reçoivent une alerte rouge dans la liste des candidats et un avertissement sur leur page -- utile pour une étiquette « ne pas louer ». Une entreprise étiquetée signale aussi ses personnes. Affiché seulement quand le module des candidats est activé et que des étiquettes existent ; le changer nécessite le droit d'écriture. Voir [Candidats](applicants.md). |
| Nom de l'étiquette + bouton de coche | Renomme l'étiquette sur chaque contact. Nécessite le droit d'écriture. Un nom qui existe déjà est refusé. |
| **{count} contact(s)** | Ouvre la liste filtrée sur cette étiquette. |
| Bouton corbeille | Supprime l'étiquette de chaque contact, après confirmation. Nécessite le droit de suppression. |
| **Traductions** | Ouvre un champ par langue. Le nom d'une étiquette peut s'afficher différemment selon la langue ; les champs vides affichent le nom propre de l'étiquette. **Enregistrer les traductions** les enregistre (droit d'écriture). |

Les nouvelles étiquettes se créent sur un contact ou dans le formulaire
de contact, pas sur cette page.

## Export CSV {#csv-export}

**Export CSV** télécharge `external-contacts.csv` : séparé par des
points-virgules, une ligne par entreprise ou personne, avec les colonnes
Typ, Firma, Vorname, Nachname, Position, Strasse, PLZ, Ort, IBAN,
E-Mail-Adressen, Telefonnummern, Tags, Notizen (type, entreprise,
prénom, nom, fonction, rue, code postal, ville, IBAN, adresses e-mail,
numéros de téléphone, étiquettes, notes). « Typ » vaut « Firma » ou
« Person ». Chaque entreprise vient en premier, suivie de ses personnes.
Plusieurs adresses e-mail, numéros ou étiquettes partagent une cellule,
séparés par des points-virgules.

Le fichier peut être réimporté tel quel.

## Import CSV {#csv-import}

L'import se fait en deux étapes et nécessite le droit d'écriture.

### Étape 1 : choisir le fichier {#step-1-choose-the-file}

**Import CSV** dans la liste ouvre **Importer des contacts depuis un
CSV**. Choisissez un fichier `.csv` (séparé par des points-virgules ou
des virgules, avec une ligne d'en-tête) et cliquez sur **Importer**.
Rien n'est encore enregistré.

### Étape 2 : importer les contacts {#step-2-import-contacts}

<!-- TODO(verify): no screenshot -- this screen is only reachable by uploading a file, which the screenshot tool can't do from a URL. -->

La carte **Associer les colonnes** affiche chaque colonne de votre
fichier avec son en-tête et les cinq premières lignes. Pour chaque
colonne, choisissez le champ dans lequel elle va, ou **— ignorer —** :

**Type (entreprise/personne)**, **Nom de l'entreprise**, **Prénom**,
**Nom**, **Fonction**, **Rue**, **Code postal**, **Ville**, **IBAN**,
**Adresses e-mail**, **Numéros de téléphone**, **Étiquettes**, **Notes**.

Parcella présélectionne le champ pour les en-têtes allemands et anglais
courants, et associe complètement son propre export. Aucun champ n'est
obligatoire. Cliquez sur **Importer** pour lancer l'import ; **Retour**
annule.

Comment chaque ligne est traitée :

- **Entreprise ou personne :** la colonne de type indique
  « Firma »/« Company » ou « Person ». Sans elle, une ligne avec un
  prénom ou un nom est une personne, sinon une entreprise.
- **Les contacts existants sont mis à jour :** une entreprise est
  reconnue par son nom, une personne par son prénom et son nom (les
  majuscules n'ont pas d'importance). Le contact correspondant reçoit
  chaque champ rempli dans le fichier ; les numéros de téléphone,
  adresses e-mail et étiquettes qu'il n'a pas encore sont ajoutés. Rien
  n'est jamais supprimé ni vidé.
- **De nouveaux contacts** sont créés pour les lignes sans
  correspondance.
- **L'entreprise d'une personne :** la colonne entreprise relie la
  personne à l'entreprise de ce nom, créée si nécessaire. L'adresse et
  l'IBAN de la ligne complètent ce qui manque à cette entreprise et ne
  restent sur la personne que là où ils diffèrent.
- Les lignes complètement vides sont ignorées.

Ensuite, la liste affiche un résumé, par ex. « 3 contact(s) créé(s),
1 mis à jour. », plus les premiers problèmes si des lignes ont été
ignorées (par ex. un nom en double).

## Où les contacts sont choisis ailleurs {#where-contacts-are-picked-elsewhere}

Quand ce module est activé et que vous pouvez lire les contacts,
d'autres modules proposent un sélecteur de contact. Les entreprises
apparaissent comme un groupe avec leurs personnes en dessous ; les
contacts supprimés ne sont pas proposés.

| Où | Libellé | Ce qu'il fait |
|---|---|---|
| [Factures reçues](finances/incoming-invoices.md) -- nouvelle facture | **Contact** | Choisir un contact remplit l'expéditeur. L'expéditeur reste un champ de texte libre. |
| Page d'une facture reçue | **Contact** | Définir ou changer le contact relié plus tard. |
| [Demandes d'achat](purchase-requests.md) -- nouvelle demande et page de la demande | **Fournisseur (contact)** | Le fournisseur de l'achat. Modifiable quel que soit le statut. |

## Voir aussi {#related}

- [Candidats](applicants.md) -- alertes issues des contacts étiquetés
- [Intégrations](../administration/integrations.md) -- le stockage cloud
  et le dossier de base des documents
- [Groupes](../administration/groups.md) -- donner au trésorier l'accès
  aux contacts

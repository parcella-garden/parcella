# Percelen {#parcels}

!!! warning "Nog niet bijgewerkt"
    Deze pagina beschrijft een oudere versie. De Engelse versie is actueel (taal wisselt u bovenaan).

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De perceellijst bevat elk tuinperceel van uw vereniging: het nummer, de
oppervlakte, de status en wie het huurt. Elk perceel houdt een volledige
huurgeschiedenis bij, zodat u jaren later nog ziet wie welk perceel had,
en wanneer.

!!! info "Wie kan dit gebruiken"
    Percelen hoort bij de kern en staat altijd aan. De module kan niet
    worden uitgeschakeld.

    - **Iedereen die kan inloggen** kan de perceellijst, de
      perceelpagina's en de CSV-export bekijken.
    - **Percelen toevoegen en bewerken**, en huren toewijzen, bewerken en
      beëindigen, vraagt *schrijf*recht op **Leden en percelen**.
    - **Een eerdere huur verwijderen** of een perceel definitief
      verwijderen vraagt *verwijder*recht op **Leden en percelen**.
    - De kaart **Documenten (cloudopslag)** op een perceelpagina is
      alleen voor bestuursleden en beheerders, en alleen zolang de module
      **Cloudopslag** aan staat (standaard uit).

    Zie [Rollen, groepen en rechten](../getting-started/roles-and-permissions.md).

## Perceelstatussen {#parcel-statuses}

Elk perceel heeft een van vier statussen:

| Status | Betekenis |
|---|---|
| **actief** | Een normaal, verhuurd perceel. |
| **beëindigd** | De huur is opgezegd -- het perceel is beschikbaar voor een nieuwe huurder. Alleen beëindigde percelen kunnen [aan aanmelders worden overgedragen](applicants.md#assign-a-parcel). |
| **gemeenschappelijk** | Een gemeenschappelijk deel dat de vereniging zelf beheert -- paden, de speeltuin, het gazon bij het verenigingsgebouw. U legt het vast als een perceel, met oppervlakte, maar het wordt niet aan leden verhuurd. U kunt het terugzetten op **actief** als de vereniging besluit het toch te verhuren. |
| **verwijderd** | Het perceel bestaat niet meer, bijv. nadat twee percelen zijn samengevoegd. De geschiedenis blijft bewaard. |

U wijzigt de status in het [perceelformulier](#new-parcel-and-edit-parcel).
Elke wijziging wordt met datum en gebruiker vastgelegd in de
wijzigingsgeschiedenis van het perceel, dus u hebt geen aparte
opzegdatum nodig.

## Perceellijst {#parcel-list}

![Perceellijst](../assets/screenshots/parcels/list.png)

Open **Percelen** in het hoofdmenu. De lijst toont elk perceel,
gesorteerd op perceelnummer -- ook verwijderde, tenzij u op status
filtert.

### Knoppen bovenaan {#buttons-at-the-top}

| Knop | Wat het doet |
|---|---|
| **CSV-import** | Opent het importvenster (zie [Percelen importeren uit een CSV-bestand](#importing-parcels-from-a-csv-file)). Vraagt schrijfrecht. |
| **CSV-export** | Downloadt alle percelen als CSV-bestand (zie [CSV-export](#csv-export)). |
| **Nieuw perceel** | Opent een leeg [perceelformulier](#new-parcel-and-edit-parcel). Vraagt schrijfrecht. |

### Zoeken en filteren {#search-and-filter}

| Veld / knop | Wat het doet |
|---|---|
| **Zoek perceelnummer…** | Vindt percelen waarvan het perceelnummer de tekst bevat. Om een perceel op de naam van de huurder te vinden, zoekt u in de [ledenlijst](members.md#search-and-filters). |
| **Alle statussen** | Toont alleen percelen met de gekozen status. Werkt zodra u het wijzigt. |
| **Zoeken** | Past de zoektekst toe. |
| **Resetten** | Wist zoektekst en statusfilter. Alleen zichtbaar zolang er een actief is. |

Net als in de ledenlijst houden **Vorige**, **Volgende** en **Terug** op
een perceelpagina het filter vast waar u vandaan kwam.

### Kolommen {#columns}

| Kolom | Wat ze toont |
|---|---|
| Vinkje | Selecteert het perceel voor **Selectie exporteren** of **Schrijf naar de pachters** (zie hieronder). |
| **Perceelnummer** | Klik erop om het perceel te openen. |
| **Oppervlakte** | Oppervlakte in vierkante meter, of „–“. |
| **Status** | **actief**, **beëindigd**, **gemeenschappelijk** of **verwijderd**. |
| **Huurder** | De huidige huurders. Klik op een naam om het lid te openen. Eerdere en toekomstige huurders staan hier niet. |
| Oogknop | Opent de perceelpagina. |

Onderaan staat het aantal percelen in de lijst en, als oppervlakten zijn
vastgelegd, hun totale oppervlakte -- handig om een gefilterde selectie
te controleren, bijv. de totale oppervlakte van alle actieve percelen.

### Percelen kiezen en hun pachters schrijven {#picking-parcels}

Elke rij heeft een vinkje, zodat u percelen met de hand kunt kiezen --
bijvoorbeeld alle percelen langs één waterleiding -- en een bericht kunt
sturen aan de mensen die ze huren.

| Knop | Wat het doet |
|---|---|
| **Alles selecteren** | Vinkt elk perceel in de huidige lijst aan. |
| **Niets selecteren** | Wist alle vinkjes. |
| ***N* geselecteerd** | Telt de aangevinkte percelen. |
| **Selectie exporteren** | Downloadt het CSV-bestand (zie hieronder) met alleen de aangevinkte percelen. Uitgeschakeld tot u er een aanvinkt. |
| **Schrijf naar de pachters** | Start een nieuwe [mededeling](announcements.md) aan de **huidige** huurders van de aangevinkte percelen. Alleen zichtbaar als de module **Mededelingen** aan staat, en alleen voor bestuursleden en beheerders. |

Een bericht aan percelen gaat over de **huur**, niet over het
lidmaatschap: het is gericht aan de huurders van elk perceel samen, net
als de jaarfactuur. Dus:

- **Eén bericht per perceel.** Wie twee van de aangevinkte percelen
  huurt, krijgt twee berichten, één per huur. Elke e-mail en brief noemt
  zijn perceel („Perceel 12“).
- **E-mail** aan elke huurder die informatie per e-mail toestaat
  (**Mag informatie per e-mail ontvangen**) en een adres heeft.
- **Brief** aan de overige huurders: één per postadres, met de naam van
  iedereen daar zonder e-mail -- ook als een huisgenoot de e-mail kreeg.
  Met **Ook een brief sturen aan leden die de e-mail krijgen** krijgt
  iedereen met een postadres een brief.
- Eerdere en toekomstige huurders vallen weg.

Voor berichten aan leden (verenigingsnieuws, uitnodigingen voor een
algemene ledenvergadering) gebruikt u de [ledenlijst](members.md).

### CSV-export {#csv-export}

**CSV-export** downloadt een bestand `parcels.csv`, gescheiden door
puntkomma's, met *elk* perceel -- zoektekst en statusfilter tellen niet
mee. **Selectie exporteren** (hierboven) schrijft hetzelfde bestand met
alleen de aangevinkte percelen. De kolomkoppen zijn Duits, zodat het
bestand opnieuw kan worden geïmporteerd:

Gartennummer (perceelnummer), Fläche (qm) (oppervlakte), Breitengrad
(breedtegraad), Längengrad (lengtegraad), Status, Kündigungsnotiz
(beëindigingsnotitie), Mitglieder (leden), Notizen (notities).

- Getallen gebruiken een decimale komma (312,5).
- De status wordt geschreven als ACTIVE, TERMINATED, COMMUNAL of DELETED.
- De kolom met leden noemt de huurders van het perceel, gescheiden door
  puntkomma's; wie als factuuradres is gemarkeerd, staat eerst en heeft
  een `*` achter de naam.
  <!-- TODO(verify): the members column includes former tenants as well, not only current ones. -->

## Percelen importeren uit een CSV-bestand {#importing-parcels-from-a-csv-file}

Met de import maakt u al uw percelen in één keer aan, bijvoorbeeld uit
een spreadsheet. Het werkt als de ledenimport: u uploadt het bestand,
koppelt de kolommen en bevestigt. Een stapsgewijze uitleg staat in
[Leden en percelen importeren](../guides/csv-import.md).

!!! tip "Eerst percelen importeren, dan leden"
    De import maakt alleen percelen aan -- hij wijst geen huurders toe.
    Wijs huurders daarna toe op elke perceelpagina of ledenpagina.

### Stap 1: het bestand uploaden {#step-1-upload-the-file}

Klik op **CSV-import** in de perceellijst. Kies in het venster
**CSV-import** een `.csv`-bestand en klik op **Importeren**. Er wordt nog
niets opgeslagen.

- Kolommen mogen gescheiden zijn door puntkomma's of komma's; Parcella
  herkent welke.
- De eerste rij moet de koprij zijn. De koppen hoeven niet exact te
  kloppen -- u koppelt ze in de volgende stap.

Is het bestand leeg, dan komt u terug met „Dit CSV-bestand lijkt leeg te
zijn.“

### Stap 2: de kolommen koppelen {#step-2-map-the-columns}

<!-- TODO(verify): no screenshot -- this page is only reached by uploading a file, which the screenshot tool can't do. -->

De pagina **CSV-kolommen koppelen** toont elke kolom van uw bestand met
de kop en de eerste vijf gegevensrijen.

| Veld / knop | Wat het doet |
|---|---|
| Keuzelijst per kolom | Kies **Perceelnummer**, **Oppervlakte (m²)**, **Breedtegraad**, **Lengtegraad**, **Status**, **Notities** -- of **— Negeren —**. Parcella kiest alvast een veld als het de kop herkent (in het Engels of Duits, bijv. „Gartennummer“ of „Plot number“). |
| **Importeren** | Importeert de rijen en brengt u terug naar de perceellijst. **Perceelnummer** moet aan een kolom gekoppeld zijn, anders krijgt u „Koppel eerst de kolom met het perceelnummer voordat u importeert.“ |
| **Terug** | Terug naar de perceellijst zonder te importeren. |

### Wat er bij het importeren gebeurt {#what-happens-on-import}

- Perceelnummers worden in hoofdletters gezet, net als in het formulier.
- Een rij waarvan het perceelnummer **al bestaat, wordt overgeslagen**
  -- bestaande percelen worden door een import nooit gewijzigd.
- Een rij zonder perceelnummer wordt genegeerd.
- Oppervlakte, breedtegraad en lengtegraad mogen een decimale punt of
  komma gebruiken. Een waarde die geen getal is, blijft leeg.
- **Status** moet ACTIVE, TERMINATED, COMMUNAL of DELETED zijn
  (hoofdletters maken niet uit). Iets anders, of een lege cel, wordt
  **actief**.

De perceellijst toont daarna een samenvatting zoals „40 geïmporteerd, 2
overgeslagen.“, plus hoeveel rijen zijn genegeerd omdat ze geen
perceelnummer hadden.

## Perceelpagina {#parcel-page}

![Perceelpagina](../assets/screenshots/parcels/detail.png)

Klik op een perceelnummer om de perceelpagina te openen. Die toont de
gegevens van het perceel, wie het nu huurt, wie het eerder huurde en wat
er is gewijzigd.

### Knoppen bovenaan {#buttons-at-the-top_1}

| Knop | Wat het doet |
|---|---|
| **Bewerken** | Opent het [bewerkformulier](#new-parcel-and-edit-parcel). Vraagt schrijfrecht. |
| **Vorige** / **Volgende** | Springt naar het vorige of volgende perceel in de lijst waar u vandaan kwam. U kunt ook ++ctrl+left++ en ++ctrl+right++ gebruiken (niet terwijl u in een veld typt). |
| **Terug** | Terug naar de perceellijst, met uw filter. |

### Perceeldetails {#parcel-details}

| Regel | Wat ze toont |
|---|---|
| **Perceelnummer** | |
| **Oppervlakte** | In vierkante meter. |
| **Coördinaten** | Alleen als breedtegraad en lengtegraad allebei zijn vastgelegd. **Op kaart bekijken** opent de plek op OpenStreetMap in een nieuw tabblad. |
| **Status** | De huidige status. |
| **Beëindigd op** | Wanneer de status voor het laatst op **beëindigd** is gezet, uit de wijzigingsgeschiedenis. |
| **Beëindigingsnotitie** | De reden of opmerkingen, als die zijn vastgelegd. |
| **Aangemaakt** | Wanneer het perceel in Parcella is ingevoerd. |
| **Notities** | De interne notities van het perceel, als die er zijn. |

Onder de details toont een kaart **Processen** de
[processen](processes.md) over dit perceel, als die module aan staat en
u processen mag zien. **Proces starten** start er een nieuw.

### Huidige huurders {#current-tenants}

De leden die het perceel nu huren, plus iedereen die het op een latere
datum overneemt.

| Kolom | Wat ze toont |
|---|---|
| **Lid** | De naam van de huurder -- klik erop om het lid te openen. Een blauwe badge **vanaf *datum*** markeert een toekomstige huurder die op die datum overneemt. Een badge **tot *datum*** markeert een huurder die heeft opgezegd en op die datum vertrekt. |
| **Factuuradres** | Of facturen voor dit perceel naar het adres van dit lid gaan. |
| **Sinds** | Het begin van de huur, of „–“ als er geen is ingevuld. |
| Potloodknop | Opent [Huur bewerken](#edit-tenancy) om datums of het factuuradres te wijzigen. Vraagt schrijfrecht. |
| Kalenderknop | **Huur beëindigen** (zie hieronder). Vraagt schrijfrecht. |

Huurt niemand het perceel, dan staat op de kaart „Geen huidige
huurders“.

#### Een huurder toewijzen {#assigning-a-tenant}

Onderaan de kaart (vraagt schrijfrecht):

| Veld / knop | Wat het doet |
|---|---|
| **Kies lid…** | Begin een naam te typen; kies het lid uit de lijst die verschijnt. Alleen actieve leden worden aangeboden. Kiest u niet uit de lijst, dan krijgt u „Selecteer een lid uit de lijst“. |
| Datumveld | De eerste dag van de huur. Optioneel. |
| **Gebruiken als factuuradres** | Standaard aangevinkt. Facturen voor dit perceel gaan naar het adres van dit lid. |
| **Toewijzen** | Voegt het lid toe als huurder. |

U kunt meerdere leden aan één perceel toewijzen -- een stel of een
gezin, bijvoorbeeld. Ze tellen allemaal als huurders met gelijke rechten;
er is geen „hoofdhuurder“. U kunt **Gebruiken als factuuradres** ook bij
meer dan één van hen aanvinken.

!!! note "Een eerdere huurder opnieuw toewijzen"
    Heeft het lid dit perceel eerder gehuurd, dan heropent Parcella de
    oude huur in plaats van een tweede aan te maken. De nieuwe
    begindatum vervangt de oude (vandaag, als u de datum leeg laat), en
    de eerdere periode staat niet meer onder **Voormalige huurders**.

!!! tip "Een perceel aan een nieuwe huurder overdragen"
    Komt de nieuwe huurder van de wachtlijst, gebruik dan **Perceel
    toewijzen** op de [pagina van de aanmelder](applicants.md#assign-a-parcel).
    Dat beëindigt de oude huren, maakt het nieuwe lid aan en zet het
    perceel in één stap weer op actief. Zie ook
    [Een perceel overdragen](../guides/parcel-handover.md).

#### Een huur beëindigen {#ending-a-tenancy}

Klik op de kalenderknop naast een huurder en bevestig „Beëindig deze
huur? (geschiedenis blijft behouden)“.

- De huur eindigt **vandaag**. Het lid verschuift meteen naar
  **Voormalige huurders**, met vandaag als einddatum.
- Het lid is niet langer het factuuradres voor dit perceel.
- Er wordt niets verwijderd: de huur blijft zichtbaar in de geschiedenis
  van het perceel en kan later worden gecorrigeerd.
- Het **lidmaatschap** wordt niet beëindigd. Verlaat het lid de
  vereniging, vul dan **Lid tot** in op de
  [ledenpagina](members.md#membership).
- De **status** van het perceel verandert niet. Is het perceel nu
  beschikbaar voor een nieuwe huurder, zet het dan in het
  perceelformulier op **beëindigd**.
- Heeft het perceel nu geen huidige of toekomstige huurder meer, dan
  wordt de documentenmap in de cloudopslag (als die is ingesteld)
  afgesloten.

De knop werkt alleen voor een huur zonder einddatum. Voor een huurder
die al voor een latere datum heeft opgezegd, wijzigt u de datum in
[Huur bewerken](#edit-tenancy).

!!! tip "Op een andere dag dan vandaag beëindigen"
    Om een huur vast te leggen die op een andere dag is geëindigd (of
    zal eindigen), opent u de potloodknop en vult u **Huurder tot** in.

### Voormalige huurders {#former-tenants}

Alleen zichtbaar als het perceel eerder huurders had. Toont elke
geëindigde huur, de meest recente eerst.

| Kolom / knop | Wat ze toont |
|---|---|
| **Lid** | Klik op de naam om het lid te openen. |
| **Van** / **Tot** | De huurperiode. |
| Potloodknop | **Periode corrigeren** -- opent [Huur bewerken](#edit-tenancy), bijv. om een verkeerde datum te herstellen. Vraagt schrijfrecht. |
| Prullenbakknop | **Item verwijderen** na bevestiging van „Dit item echt permanent verwijderen? Dit kan niet ongedaan worden gemaakt.“ Vraagt verwijderrecht. |

!!! warning "Een eerdere huur verwijderen is alleen voor vergissingen"
    Verwijderen haalt het item voorgoed weg -- het is bedoeld voor een
    toewijzing die per vergissing of dubbel is ingevoerd. Bij een gewone
    huurderswissel beëindigt u de huur; verwijder haar nooit. Alleen
    geëindigde huren kunnen worden verwijderd; een huidige moet eerst
    worden beëindigd.

### Documenten (cloudopslag) {#documents-cloud-storage}

Alleen zichtbaar voor bestuursleden en beheerders zolang de module
**Cloudopslag** aan staat. De kaart koppelt het perceel aan een map in
de cloudopslag van uw vereniging (bijvoorbeeld Nextcloud), waar u
huurcontracten en andere papieren van de huidige huurders bewaart.
Richt de opslag eerst in onder [Integraties](../administration/integrations.md).

| Veld / knop | Wat het doet |
|---|---|
| **Mappad** | Het pad van de map die bij de huidige huur hoort, bijv. „kgv_dokumente/parzellen/G016/2024-03_016_Mueller“. De map moet al bestaan en in uw cloudopslag met de huurders gedeeld zijn. |
| **Bladeren…** | Opent **Map kiezen**: klik door de mappen (of typ in **Mappen filteren…**) en klik dan op **Deze map gebruiken**. Dubbelklikken op een map kiest haar meteen. De hoofdmap van de opslag zelf kunt u niet kiezen -- „Open eerst een map voordat u deze selecteert.“ |
| **Opslaan** | Slaat het mappad op. |
| Bestandenlijst | Toont de bestanden en submappen van de map met **Naam** en **Laatst gewijzigd**. Klik op een submap om die te openen; het pad boven de lijst leidt terug. De downloadknop downloadt een bestand. |
| Bestandsveld + **Uploaden** | Uploadt een bestand naar de map die u nu bekijkt. |

Eindigt een huur en huurt niemand het perceel meer, dan wordt de map
automatisch afgesloten, zodat de volgende huurders de oude papieren niet
zien. Na een overdracht met een latere datum vertelt een melding wanneer
de huidige map wordt afgesloten en welke map op die dag overneemt.

### Wijzigingsgeschiedenis {#change-history}

Alleen zichtbaar zodra er iets is gewijzigd. Elke wijziging van het
perceelnummer, de oppervlakte, de coördinaten, de status, de
beëindigingsnotitie of de notities wordt vastgelegd:

| Kolom | Wat ze toont |
|---|---|
| **Tijdstempel** | Datum en tijd van de wijziging. |
| **Veld** | De technische naam van het gewijzigde veld, bijv. *status* of *area_sqm*. |
| **Oude waarde** / **Nieuwe waarde** | De waarde ervoor en erna. |
| **Gewijzigd door** | De gebruiker die de wijziging maakte, of **Onbekend**. |

Wijzigingen aan huren staan hier niet -- die ziet u in de
huurderstabellen hierboven.

## Nieuw perceel en perceel bewerken {#new-parcel-and-edit-parcel}

![Formulier nieuw perceel](../assets/screenshots/parcels/form-new.png)

Klik op **Nieuw perceel** in de perceellijst, of op **Bewerken** op een
perceelpagina. Het bewerkformulier heeft een paar velden meer dan het
formulier voor een nieuw perceel.

![Formulier perceel bewerken](../assets/screenshots/parcels/form-edit.png)

| Veld | Wat het doet |
|---|---|
| **Perceelnummer** \* | Verplicht, bijv. „G093“ of „G26/27“. Wordt automatisch in hoofdletters gezet. Moet uniek zijn: heeft een ander perceel het al, dan krijgt u „Perceelnummer '…' bestaat al.“ |
| **Oppervlakte (m²)** | De oppervlakte in vierkante meter. Een decimale punt of komma werkt allebei. Gebruikt voor oppervlaktegebonden tarieven en statistieken. |
| **Breedtegraad** / **Lengtegraad** | Optionele GPS-positie van het perceel, bijv. 51.339695 en 12.373075. Zijn beide ingevuld, dan linkt de perceelpagina naar een kaart. De breedtegraad moet tussen -90 en 90 liggen, de lengtegraad tussen -180 en 180. De positie wordt nooit op openbare pagina's getoond. |
| **Status** | Alleen in het bewerkformulier. **actief**, **beëindigd**, **gemeenschappelijk** of **verwijderd** -- zie [Perceelstatussen](#parcel-statuses). Het tijdstip van de wijziging wordt automatisch vastgelegd. Nieuwe percelen beginnen altijd als **actief**. |
| **Beëindigingsnotitie** | Alleen in het bewerkformulier. Reden of opmerkingen bij een beëindiging. |
| **Notities** | Interne notities over het perceel. |

| Knop | Wat het doet |
|---|---|
| **Perceel aanmaken** / **Wijzigingen opslaan** | Slaat op en opent de perceelpagina. |
| **Annuleren** | Verlaat het formulier zonder op te slaan. |

<!-- TODO(verify): an area or coordinate that isn't a number is silently left empty instead of showing an error. -->

### Gevarenzone {#danger-zone}

Het bewerkformulier eindigt met een **Gevarenzone**. **Perceel permanent
verwijderen** haalt het perceel na bevestiging uit de database. Alle
huren van het perceel -- huidige en eerdere -- worden mee verwijderd.
Wateraansluitingen blijven bestaan, maar zijn niet meer aan een perceel
gekoppeld. Dit kan niet ongedaan worden gemaakt en vraagt verwijderrecht.

!!! warning "Gebruik liever de status verwijderd"
    Definitief verwijderen is bedoeld voor percelen die per vergissing
    zijn aangemaakt, zoals testitems. Voor een perceel dat niet meer
    bestaat, zet u de status op **verwijderd** -- het perceel en de
    volledige geschiedenis blijven beschikbaar.

## Huur bewerken {#edit-tenancy}

![Huur bewerken](../assets/screenshots/parcels/assignment-form.png)

Geopend met de potloodknop naast een huidige of eerdere huurder. De kop
noemt het lid en het perceel. Vraagt schrijfrecht.

| Veld | Wat het doet |
|---|---|
| **Gebruiken als factuuradres** | Facturen voor dit perceel gaan naar het adres van dit lid. „Geldt alleen zolang deze huur actueel is -- wordt automatisch uitgeschakeld zodra de huur is beëindigd (einddatum vandaag of eerder). Een huurder die heeft opgezegd, behoudt het tot dan.“ Het vinkje wordt grijs zodra **Huurder tot** vandaag of eerder is; een datum in de toekomst laat het zoals het is. |
| **Huurder sinds** | De eerste dag van de huur. |
| **Huurder tot** | De dag waarop de huur eindigt. „Leeg = nog huidige huurder“. Een datum in de toekomst betekent dat de huurder heeft opgezegd: hij blijft huidige huurder tot die dag en krijgt een badge **tot *datum***. Vanaf die dag staat hij onder **Voormalige huurders**. |

| Knop | Wat het doet |
|---|---|
| **Wijzigingen opslaan** | Slaat op en brengt u terug naar de perceelpagina. Heeft het perceel nu geen huidige of toekomstige huurder, dan wordt de documentenmap in de cloud afgesloten. |
| **Annuleren** / **Terug** | Terug naar de perceelpagina zonder op te slaan. |

**Huurder tot** leegmaken bij een eerdere huur maakt die weer actueel.

## Gerelateerd {#related}

- [Leden](members.md) -- ledengegevens en percelen toewijzen vanaf de ledenkant
- [Aanmelders](applicants.md) -- een beëindigd perceel overdragen aan mensen op de wachtlijst
- [Een perceel overdragen](../guides/parcel-handover.md)
- [Leden en percelen importeren](../guides/csv-import.md)
- [Water en elektriciteit](metering.md) -- meters horen bij percelen
- [Integraties](../administration/integrations.md) -- cloudopslag inrichten

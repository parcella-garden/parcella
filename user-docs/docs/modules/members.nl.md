# Leden {#members}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De ledenlijst is het hart van Parcella: iedereen die bij uw vereniging
hoort, met adres, bankgegevens, contactgegevens en de percelen die hij
huurt. Facturen, werkuren, mailings, de verjaardagslijst en de
presentielijst voor vergaderingen lezen allemaal hieruit.

!!! info "Wie kan dit gebruiken"
    Leden hoort bij de kern en staat altijd aan. De module kan niet
    worden uitgeschakeld.

    - **Iedereen die kan inloggen** kan de ledenlijst, de ledenpagina's,
      de lijst met tags, de CSV-export en de presentielijst bekijken.
    - **Leden toevoegen en bewerken**, telefoonnummers, e-mailadressen,
      tags en perceeltoewijzingen vraagt *schrijf*recht op **Leden en
      percelen**.
    - **Een lid, telefoonnummer, e-mailadres of tag verwijderen** vraagt
      *verwijder*recht op **Leden en percelen**.

    Bestuursleden en beheerders hebben dat allemaal. Anderen krijgen
    schrijf- of verwijderrecht via een groep (zie
    [Rollen, groepen en rechten](../getting-started/roles-and-permissions.md)).

## Ledenlijst {#member-list}

![Ledenlijst](../assets/screenshots/members/list.png)

Open **Leden** in het hoofdmenu. De lijst toont de actieve leden,
gesorteerd op achternaam en daarna voornaam. Onderaan staat hoeveel
leden de lijst nu bevat.

### Knoppen bovenaan {#buttons-at-the-top}

| Knop | Wat het doet |
|---|---|
| **CSV-import** | Opent het importvenster voor een CSV-bestand (zie [Leden importeren uit een CSV-bestand](#importing-members-from-a-csv-file)). Vraagt schrijfrecht. |
| **CSV-export** | Downloadt de leden die *nu getoond worden* als CSV-bestand. Zoekopdracht, vinkjes en tagfilter tellen allemaal mee (zie [CSV-export](#csv-export)). |
| **Deze *N* leden schrijven** | Start een nieuwe mededeling aan precies de leden in de gefilterde lijst. Alleen zichtbaar nadat u hebt gezocht of gefilterd, als de module **Mededelingen** aan staat, en alleen voor bestuursleden en beheerders. Om iedereen te schrijven, start u de mededeling vanuit [Mededelingen](announcements.md). |
| **Tags beheren** | Opent de pagina [Ledentags](#member-tags). |
| **Presentielijst** | Opent de [Presentielijst vergadering](#meeting-sign-in-sheet). |
| **Nieuw lid** | Opent een leeg [ledenformulier](#new-member-and-edit-member). Vraagt schrijfrecht. |

### Zoeken en filters {#search-and-filters}

| Veld / knop | Wat het doet |
|---|---|
| Zoekveld | Vindt leden op voor- of achternaam, straat, postcode, plaats, IBAN, notities, e-mailadres, telefoonnummer en perceelnummer. Een perceelnummer vindt alleen de *huidige* huurders van het perceel -- tenzij **Toon alleen inactieven** is aangevinkt, dan ook eerdere huurders. Omdat ook notities worden doorzocht, vindt een ticketnummer dat u bij een lid hebt genoteerd dat lid. |
| **Toon alleen inactieven** | Toont *alleen* leden die niet actief zijn: hun datum **Lid tot** is verstreken, of hun datum **Lid sinds** ligt nog in de toekomst. Gebruik dit om oud-leden of overleden leden op te zoeken. |
| **Alleen bevestigd actief** | Toont alleen actieve leden die een datum **Lid sinds** hebben. Leden zonder begindatum (getoond als *in afwachting*) vallen weg. |
| **Alleen e-mailinfo = ja** | Toont alleen leden die **Mag informatie per e-mail ontvangen** hebben aangevinkt. |
| Tagkeuzelijst (**Alle tags**) | Toont alleen leden met de gekozen tag. De keuzelijst verschijnt zodra er minstens één tag bestaat. U kunt op één tag tegelijk filteren. |
| **Zoeken** | Past de zoektekst toe. De vinkjes en de tagkeuzelijst werken zodra u ze wijzigt. |
| **Resetten** | Wist alle filters. Alleen zichtbaar zolang er een filter actief is. |

Is **Toon alleen inactieven** aangevinkt, dan gaat dat voor **Alleen
bevestigd actief**. Een blauwe melding boven de tabel herinnert u eraan
welk van de twee filters aan staat.

Uw filter gaat met u mee: opent u een lid vanuit een gefilterde lijst,
dan lopen de knoppen **Vorige** en **Volgende** op de ledenpagina door
dezelfde gefilterde lijst, en **Terug** brengt u ernaar terug.

### Kolommen {#columns}

| Kolom | Wat ze toont |
|---|---|
| Vinkje | Selecteert het lid voor **Selectie exporteren** of **Selectie aanschrijven** (zie hieronder). |
| **Naam** | Achternaam, voornaam -- klik erop om het lid te openen. De tags van het lid staan als kleine grijze labels naast de naam; klik op een label om de lijst op die tag te filteren. |
| **Lid sinds** | Het begin van het lidmaatschap, of „–“ als er geen is vastgelegd. |
| **Percelen** | De perceelnummers die aan het lid zijn toegewezen. <!-- TODO(verify): the list shows every parcel assignment of the member, including tenancies that have already ended -- confirm whether former parcels are meant to appear here. --> |
| **Status** | **actief**, **inactief** of **in afwachting** (zie hieronder). |
| Oogknop | Opent de ledenpagina, net als klikken op de naam. |

De statusbadge betekent:

- **actief** -- het lidmaatschap is begonnen en niet geëindigd.
- **in afwachting** -- er is nog geen datum **Lid sinds** vastgelegd. Een
  lid in afwachting telt overal elders gewoon als actief (facturen,
  presentielijst, tellingen op het dashboard); de badge zegt alleen dat
  de begindatum nog niet is bevestigd.
- **inactief** -- het lidmaatschap is geëindigd of nog niet begonnen. Is
  er een datum **Lid tot**, dan toont de badge „sinds“ die datum.

### Leden met de hand kiezen {#picking-members-by-hand}

Elke rij heeft een vinkje, zodat u een paar leden uit de lijst kunt
kiezen -- bijvoorbeeld filteren op iedereen die e-mailinformatie
toestaat en daarvan 12 aanvinken.

| Knop | Wat het doet |
|---|---|
| **Alles selecteren** | Vinkt elk lid in de huidige lijst aan. |
| **Niets selecteren** | Wist alle vinkjes. |
| ***N* geselecteerd** | Telt de aangevinkte leden. |
| **Selectie exporteren** | Downloadt een CSV-bestand met alleen de aangevinkte leden. Uitgeschakeld tot u iemand aanvinkt. |
| **Selectie aanschrijven** | Start een nieuwe mededeling aan alleen de aangevinkte leden. Alleen zichtbaar als de module **Mededelingen** aan staat, en alleen voor bestuursleden en beheerders. |

!!! warning "Vinkjes verdwijnen als u het filter wijzigt"
    Een wijziging van de zoekopdracht, een vinkje of de tagkeuzelijst
    laadt de pagina opnieuw, en uw vinkjes zijn weg. Stel eerst het
    filter in, vink daarna aan.

Volgt u de link naar de ledenlijst vanuit een mededeling die aan
gekozen leden is verstuurd, dan toont de lijst alleen die leden, met de
melding „Alleen de *N* geselecteerde leden worden getoond.“ Klik op
**Hele lijst tonen** om terug te gaan naar de gewone lijst. U kunt tot
2.000 leden tegelijk kiezen.

### CSV-export {#csv-export}

**CSV-export** downloadt een bestand `members.csv`, gescheiden door
puntkomma's, met één rij per lid in de huidige lijst. De kolomkoppen
zijn Duits, zodat het bestand ongewijzigd weer kan worden geïmporteerd:

Vorname, Nachname, Strasse, PLZ, Ort, Geburtsdatum, IBAN, Member seit,
Member bis, E-Mail-Benachrichtigungen, E-Mail-Adressen, Telefonnummern,
Parzellen, Notizen, Tags.

- Datums worden geschreven als jaar-maand-dag (2024-03-01).
- E-mailinformatie wordt geschreven als „Ja“ of „Nein“.
- Meerdere e-mailadressen, telefoonnummers, percelen of tags delen één
  cel, gescheiden door puntkomma's.
- Tags worden geëxporteerd met de naam die u hebt getypt, niet met een
  vertaling.
- Of een lid geen verjaardagscadeaus wil, wordt niet geëxporteerd.

!!! tip
    De export komt altijd overeen met wat op het scherm staat. Om elk
    actief lid te exporteren, klikt u eerst op **Resetten**. Om oud-leden
    te exporteren, vinkt u eerst **Toon alleen inactieven** aan.

## Leden importeren uit een CSV-bestand {#importing-members-from-a-csv-file}

Met de import brengt u een bestaande ledenlijst -- uit een spreadsheet
of een ouder programma -- in Parcella. Het gaat in twee stappen: u
uploadt het bestand en vertelt Parcella dan welke kolom wat bevat. Er
wordt niets opgeslagen voordat u de tweede stap bevestigt.

Een stapsgewijze uitleg voor een eerste import vindt u in
[Leden en percelen importeren](../guides/csv-import.md).

### Stap 1: het bestand uploaden {#step-1-upload-the-file}

Klik op **CSV-import** in de ledenlijst. Het venster **CSV-import**
opent.

| Veld / knop | Wat het doet |
|---|---|
| Bestandsveld | Kies een `.csv`-bestand. |
| **Importeren** | Uploadt het bestand en opent de kolomkoppeling. Er wordt nog niets opgeslagen. |

Het venster noemt de kolommen die Parcella begrijpt. U hoeft die koppen
niet te gebruiken -- u koppelt de kolommen in de volgende stap. Goed om
te weten over het bestand:

- Kolommen mogen gescheiden zijn door puntkomma's of komma's. Parcella
  herkent welke; lukt dat niet, dan gaat het uit van puntkomma's.
- De eerste rij moet de koprij zijn.
- Datums mogen geschreven zijn als 2024-03-01, 01.03.2024 of 01.03.24.
- Meerdere e-mailadressen of telefoonnummers in één cel worden
  gescheiden door puntkomma's.
- Het eenvoudigste sjabloon is een **CSV-export** uit Parcella zelf --
  de link in het venster downloadt de volledige, ongefilterde export.

Is het bestand leeg, dan komt u terug in de lijst met „Dit CSV-bestand
lijkt leeg te zijn.“

### Stap 2: de kolommen koppelen {#step-2-map-the-columns}

<!-- TODO(verify): no screenshot -- this page is only reached by uploading a file, which the screenshot tool can't do. -->

De pagina **CSV-kolommen koppelen** toont elke kolom van uw bestand met
de kop en daaronder de eerste vijf gegevensrijen, zodat u ziet wat erin
staat. Boven elke kolom staat een keuzelijst.

| Veld / knop | Wat het doet |
|---|---|
| Keuzelijst per kolom | Kies het Parcella-veld waar deze kolom bij hoort: **Voornaam**, **Achternaam**, **Straat**, **Postcode**, **Plaats**, **Geboortedatum**, **IBAN**, **Lid sinds**, **Lid tot**, **E-mailmeldingen**, **E-mailadressen**, **Telefoonnummers**, **Notities** -- of **— Negeren —** om de kolom over te slaan. Parcella kiest alvast een veld als het de kop herkent (in het Engels of Duits, bijv. „Nachname“ of „Last name“). |
| **Importeren** | Importeert de rijen en brengt u terug naar de ledenlijst. **Voornaam** en **Achternaam** moeten elk aan een kolom gekoppeld zijn, anders krijgt u „Koppel eerst zowel voornaam als achternaam voordat u importeert.“ |
| **Terug** | Terug naar de ledenlijst zonder iets te importeren. |

### Wat er bij het importeren gebeurt {#what-happens-on-import}

Voor elke rij zoekt Parcella een bestaand lid met dezelfde voor- en
achternaam. Hebt u een kolom **Geboortedatum** gekoppeld en heeft de rij
een geboortedatum, dan moet die ook overeenkomen.

- **Geen overeenkomst**: er wordt een nieuw lid aangemaakt, inclusief de
  e-mailadressen en telefoonnummers uit de rij.
- **Een overeenkomst**: het bestaande lid wordt bijgewerkt, maar alleen
  met wat de rij echt bevat (zie hieronder). E-mailadressen en
  telefoonnummers worden bij een update **niet** aangeraakt -- die voegt
  u toe of verwijdert u op de ledenpagina.
- **Meerdere leden met die naam**: Parcella gebruikt de geboortedatum,
  e-mailadressen en telefoonnummers van de rij om de juiste te vinden.
  Het lid dat er een van heeft, wordt bijgewerkt; hoofdletters, spaties
  en streepjes maken niet uit („0171 234-5678“ is hetzelfde als
  „01712345678“). Past de rij nog steeds op meer dan één lid, dan wordt
  ze overgeslagen met „Rij 4: meerdere leden heten Hans Meier,
  overgeslagen.“ en wordt niemand gewijzigd. Een e-mailadres of
  telefoonnummer alleen koppelt nooit aan een lid met een andere naam,
  omdat stellen er vaak een delen.
- **Voor- of achternaam leeg**: de rij wordt overgeslagen.

**Een update wijzigt alleen wat het bestand zegt.** Een kolom die u op
**— Negeren —** hebt gezet, of een lege cel, laat de opgeslagen waarde
van het lid zoals ze is. Een bestand met alleen namen en nieuwe adressen
werkt dus de adressen bij en verder niets.

De kolom **E-mailmeldingen** telt als „nee“ bij *nein*, *no*, *false* of
*0*, en als „ja“ bij alles wat verder is ingevuld. Bij een bestaand lid
laat een lege cel of het ontbreken van de kolom de keuze ongewijzigd --
wie zich heeft afgemeld, blijft afgemeld. Een nieuw lid zonder waarde
krijgt „ja“.

Daarna toont de ledenlijst een samenvatting zoals „12 nieuw
geïmporteerd, 3 bijgewerkt“. Zijn er rijen overgeslagen, dan vermeldt
de samenvatting ook het aantal fouten en de details van de eerste drie.

!!! tip "Leden met dezelfde naam"
    Heeft uw vereniging leden met identieke namen, koppel dan de kolom
    **Geboortedatum**, **E-mailadressen** of **Telefoonnummers**: dan
    werkt elke rij de juiste persoon bij. Zonder een van die kolommen
    worden zulke rijen overgeslagen in plaats van geraden.

## Ledenpagina {#member-page}

![Ledenpagina](../assets/screenshots/members/detail.png)

Klik op een naam in de ledenlijst om de ledenpagina te openen. Die toont
alles wat Parcella over het lid weet, en laat u direct telefoonnummers,
e-mailadressen, tags en percelen toevoegen.

### Knoppen bovenaan {#buttons-at-the-top_1}

| Knop | Wat het doet |
|---|---|
| **Bewerken** | Opent het [bewerkformulier](#new-member-and-edit-member). Vraagt schrijfrecht. |
| **Vorige** / **Volgende** | Springt naar het vorige of volgende lid *in de lijst waar u vandaan kwam*, met hetzelfde filter. U kunt ook ++ctrl+left++ en ++ctrl+right++ gebruiken (niet terwijl u in een veld typt). Op een Mac kan het systeem deze toetsen gebruiken om tussen bureaubladen te wisselen. |
| **Terug** | Terug naar de ledenlijst, met uw filter. |

### Hoofdgegevens {#master-data}

Toont **Naam**, **Geboortedatum**, **Adres**, **IBAN**, **Lid sinds**,
**Lid tot**, **E-mail info** (of het lid informatie per e-mail mag
ontvangen) en **Wil geen verjaardagscadeaus**. Om iets daarvan te
wijzigen, klikt u op **Bewerken**.

### Tags {#tags}

Toont de tags van het lid. Klik op een tag om alle leden met die tag te
zien.

| Veld / knop | Wat het doet |
|---|---|
| **×** naast een tag | Haalt de tag weg bij dit lid (**Tag verwijderen**). De tag zelf blijft bestaan voor andere leden. Vraagt schrijfrecht. |
| **Tag toevoegen, bijv. waterverantwoordelijke** | Typ een tagnaam en klik op **+** (**Tag toevoegen**). Bestaat er al een tag met die naam -- hoofdletters en extra spaties maken niet uit --, dan wordt die hergebruikt; anders wordt een nieuwe tag gemaakt. Het veld stelt bestaande tags voor terwijl u typt. Vraagt schrijfrecht. |
| **Tags beheren** | Opent de pagina [Ledentags](#member-tags). |

Een tag bij een lid weghalen laat geen historie achter: tags zijn labels
om mensen terug te vinden, geen verenigingsadministratie.

### Telefoonnummers en e-mailadressen {#phone-numbers-and-email-addresses}

| Veld / knop | Wat het doet |
|---|---|
| Telefoonveld + **+** | Voegt nog een telefoonnummer toe. Vraagt schrijfrecht. |
| E-mailveld + **+** | Voegt nog een e-mailadres toe. Het moet op een e-mailadres lijken. Vraagt schrijfrecht. |
| Prullenbakknop | Verwijdert dat telefoonnummer of e-mailadres (**Verwijderen**). Vraagt verwijderrecht. |

Klik op een e-mailadres om het lid vanuit uw eigen mailprogramma te
schrijven.

### Toegewezen percelen {#assigned-parcels}

Toont de percelen die aan het lid zijn toegewezen.

| Kolom | Wat ze toont |
|---|---|
| **Perceelnummer** | Klik erop (of op de pijlknop) om het perceel te openen. |
| **Oppervlakte** | De oppervlakte van het perceel in vierkante meter. |
| **Status** | De status van het perceel: **actief**, **beëindigd** of **verwijderd**. |
| **Factuuradres** | Of het adres van dit lid wordt gebruikt voor de facturen van het perceel. |
| **Sinds** | Het begin van de huur. |

<!-- TODO(verify): this table lists every assignment of the member, including ended tenancies, and has no "until" column -- confirm whether former parcels are meant to appear here. Also, a communal parcel would show as "deleted" here because the badge only knows active/terminated. -->

Om het lid een perceel te geven (vraagt schrijfrecht):

| Veld / knop | Wat het doet |
|---|---|
| **Kies perceel…** | Het toe te wijzen perceel. Elk perceel wordt aangeboden, gesorteerd op perceelnummer. |
| **Gebruiken als factuuradres** | Standaard aangevinkt. Facturen voor dit perceel gaan naar het adres van dit lid. |
| **Toewijzen** | Wijst het perceel toe en opent de perceelpagina. |

De huur begint zonder datum. Om een begindatum in te stellen of een huur
te beëindigen, gebruikt u de perceelpagina -- zie
[Huidige huurders](parcels.md#current-tenants).

### Processen {#processes}

Staat de module [Processen](processes.md) aan en mag u processen zien,
dan toont een kaart **Processen** de processen over dit lid. **Proces
starten** start er een nieuw voor dit lid.

### Notities {#notes}

De interne notities van het lid, als die er zijn. U bewerkt ze in het
ledenformulier.

### Gevarenzone {#danger-zone}

Alleen zichtbaar voor gebruikers met verwijderrecht.

**Lid verwijderen** markeert het lid na bevestiging als verwijderd. Het
lid verdwijnt uit alle lijsten en zoekresultaten. De gegevens blijven in
de database, en bestaande perceeltoewijzingen, werksessies en andere
records blijven zoals ze zijn.

!!! warning "Een lidmaatschap beëindigen is niet verwijderen"
    Voor een lid dat de vereniging verlaat -- of is overleden -- vult u
    in het bewerkformulier **Lid tot** in, en beëindigt u de huur op de
    perceelpagina. Het lid verschuift dan naar **Toon alleen
    inactieven** en de geschiedenis blijft zichtbaar. Verwijderen is
    bedoeld voor records die nooit hadden mogen bestaan, zoals een
    dubbele.
    <!-- TODO(verify): there's no way to restore a deleted member in the app; confirm. Also confirm how a deleted member who is still assigned to a parcel shows up on the parcel page. -->

## Nieuw lid en lid bewerken {#new-member-and-edit-member}

![Formulier nieuw lid](../assets/screenshots/members/form-new.png)

Klik op **Nieuw lid** in de ledenlijst, of op **Bewerken** op een
ledenpagina. Beide formulieren zien er hetzelfde uit; het formulier
voor een nieuw lid vraagt daarnaast een eerste e-mailadres en
telefoonnummer. Velden met een rood sterretje zijn verplicht.

### Persoonlijke gegevens {#personal-data}

| Veld | Wat het doet |
|---|---|
| **Voornaam** \* | Verplicht. |
| **Achternaam** \* | Verplicht. |
| **Geboortedatum** | Gebruikt voor de verjaardagslijst en de gemiddelde leeftijd op het dashboard. Helpt de CSV-import ook leden met dezelfde naam uit elkaar te houden. |
| **IBAN** | De bankrekening van het lid, bijv. voor automatische incasso's. |

### Adres {#address}

| Veld | Wat het doet |
|---|---|
| **Straat en huisnummer** | |
| **Postcode** | Maximaal 10 tekens. |
| **Plaats** | |

Het adres wordt gebruikt voor brieven en facturen. Is het lid het
factuuradres van een perceel, dan gaan de facturen voor dat perceel
hierheen.

### Lidmaatschap {#membership}

| Veld | Wat het doet |
|---|---|
| **Lid sinds** | De eerste dag van het lidmaatschap. Is het leeg, dan staat het lid als *in afwachting* in de lijst maar telt het nog als actief. Ligt het in de toekomst, dan telt het lid tot die dag als inactief. |
| **Lid tot** | De laatste dag van het lidmaatschap. „Leeg laten = actief lid“. Vanaf de dag erna telt het lid als inactief. |
| **E-mailadres** | Alleen bij nieuwe leden. Optioneel -- meer adressen kunnen later op de ledenpagina worden toegevoegd. |
| **Telefoonnummer** | Alleen bij nieuwe leden. Optioneel -- meer nummers kunnen later op de ledenpagina worden toegevoegd. |
| **Mag informatie per e-mail ontvangen** | Bij nieuwe leden standaard aangevinkt. Vink het uit als het lid geen verenigingsinformatie per e-mail wil. De ledenlijst kan hierop filteren. |
| **Wil geen verjaardagscadeaus** | Vink aan als het lid geen verjaardagscadeaus wil. Het staat op de verjaardagslijst, zodat wie voor de cadeaus zorgt het weet. |

### Notities {#notes_1}

| Veld | Wat het doet |
|---|---|
| **Interne notities…** | Vrije tekst voor het bestuur. De zoekfunctie van de ledenlijst doorzoekt ook de notities. |

### Tags {#tags_1}

| Veld | Wat het doet |
|---|---|
| Tagvinkjes | Eén vinkje per bestaande tag. Vink aan of uit om de tag toe te voegen of weg te halen. Alleen zichtbaar als er tags bestaan. |
| **Nieuwe tags, gescheiden door komma's** | Typ nieuwe tags, gescheiden door komma's, bijv. „waterverantwoordelijke, hagenteam“. Een bestaande naam wordt hergebruikt. |

### Opslaan {#saving}

| Knop | Wat het doet |
|---|---|
| **Lid aanmaken** / **Wijzigingen opslaan** | Slaat het lid op en opent de ledenpagina. |
| **Annuleren** | Verlaat het formulier zonder op te slaan. |

Wordt een nieuwe tagnaam niet geaccepteerd (bijvoorbeeld omdat hij
langer is dan 100 tekens), dan wordt de rest van het lid toch opgeslagen
en opent het bewerkformulier opnieuw, zodat u de tag kunt corrigeren.
<!-- TODO(verify): in that case the form reopens without an error message. -->

## Ledentags {#member-tags}

![Ledentags](../assets/screenshots/members/tags.png)

Tags zijn vrije labels om leden terug te vinden -- „waterverantwoordelijke“,
„uitgebreid bestuur“, „hagenteam“. U voegt ze toe op een ledenpagina of
in het ledenformulier; hier hernoemt of verwijdert u ze. Open de pagina
met **Tags beheren** in de ledenlijst of op een ledenpagina.

Elke tag heeft één rij:

| Veld / knop | Wat het doet |
|---|---|
| Tagnaam + vinkknop | Wijzig de naam en klik op de vinkknop (**Hernoemen**). De nieuwe naam verschijnt bij elk lid met de tag. Geweigerd als een andere tag al die naam heeft. Vraagt schrijfrecht; zonder dat ziet u alleen de naam. |
| ***N* lid/leden** | Opent de ledenlijst gefilterd op deze tag. |
| Prullenbakknop | **Tag verwijderen** na bevestiging. De tag wordt bij elk lid weggehaald. Vraagt verwijderrecht. |
| Vertaalknop | Opent de **Vertalingen** van de tag: één naam per taal die Parcella ondersteunt. Zolang de vereniging in een taal draait, tonen lijsten, formulieren en filters de naam van de tag in die taal; een leeg veld toont de naam die u hebt getypt. Klik op **Vertalingen opslaan** om ze op te slaan. Vraagt schrijfrecht; zonder dat ziet u de vertalingen als lijst. Het kleine getal op de knop zegt hoeveel vertalingen er zijn. |
| **Terug naar leden** | Terug naar de ledenlijst. |

De CSV-export gebruikt altijd de naam die u hebt getypt, niet een
vertaling.

## Presentielijst vergadering {#meeting-sign-in-sheet}

![Presentielijst vergadering](../assets/screenshots/members/signin-sheet.png)

Open haar met **Presentielijst** in de ledenlijst. Ze maakt een
PDF-lijst om af te drukken en mee te nemen naar een algemene
ledenvergadering: elke huidige huurder, gegroepeerd per perceel, met een
handtekeningregel voor ieder.

| Veld / knop | Wat het doet |
|---|---|
| **Kop** | Bovenaan de PDF. Begint als „General meeting on“ plus de datum van vandaag (deze standaardtekst is altijd Engels); wijzig hem naar wat u wilt. Maakt u het veld leeg, dan wordt de standaard gebruikt. |
| **PDF genereren** | Downloadt de presentielijst als PDF-bestand. |
| **Annuleren** | Terug naar de ledenlijst. |

Wat er op de lijst staat:

- Eén rij per persoon, met de kolommen **Perceel**, **Naam** en
  **Handtekening**, gesorteerd op perceelnummer en dan op achternaam.
- Huren meerdere mensen één perceel, dan staat het perceelnummer één
  keer en krijgt ieder een eigen handtekeningregel.
- Alleen **actieve leden** die **huidige huurder** van een perceel zijn,
  staan erop. Leden zonder perceel en huurders die al zijn vertrokken,
  staan niet op de lijst.
- De PDF draagt het verenigingslogo en dezelfde kop- en voettekst als de
  andere documenten van de vereniging. Een lange lijst loopt gewoon over
  meerdere pagina's door.

!!! tip
    Leden zonder perceel -- erelid, bijvoorbeeld -- staan niet op de
    lijst. Voeg ze met de hand toe als ze de vergadering mogen bijwonen.

## Gerelateerd {#related}

- [Percelen](parcels.md) -- huren toewijzen en beëindigen
- [Aanmelders](applicants.md) -- een aanmelder lid maken
- [Een nieuw lid verwelkomen](../guides/new-member.md)
- [Een perceel overdragen](../guides/parcel-handover.md)
- [Leden en percelen importeren](../guides/csv-import.md)
- [Mededelingen](announcements.md) -- gefilterde of gekozen leden schrijven

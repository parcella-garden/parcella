# Kalender {#calendar}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De kalendermodule bewaart de datums die voor uw vereniging belangrijk
zijn op één plek: vergaderingen en inspecties, verjaardagen van leden,
wanneer bestuursleden aanwezig zijn en wanneer iemand weg is. Op elke
kalender kunt u zich abonneren vanuit een agenda-app op telefoon of
computer.

!!! info "Wie kan dit gebruiken"
    - De moduleschakelaar is **Kalender** onder **Administratie → Modules
      in- en uitschakelen**. Ze staat standaard **aan**.
    - De rollen **Bestuur** en **Beheerder**, en leden van een groep met
      **Volledige toegang tot elke module**, kunnen alles.
    - Alle anderen hebben het recht **Kalender** in een van hun
      [groepen](../administration/groups.md) nodig: *lezen* om de
      kalenders te zien, *schrijven* om items toe te voegen, *verwijderen*
      om ze weg te halen.
    - **Afwezigheid bestuur** is de uitzondering: iedereen die is
      ingelogd en de kalender kan openen, kan een afwezigheid registreren.
    - Eigen agenda's aanmaken en bewerken onder **Eigen agenda's** vraagt
      volledige toegang (Bestuur, Beheerder of een groep met volledige
      toegang).

Er is bewust geen maandraster. Elke kalender is een eenvoudige lijst van
wat eraan komt, vanaf vandaag. Voorbije items verdwijnen vanzelf uit de
lijst (en uit de abonnementsfeeds).

U vindt alle kalenders in de zijbalk onder **Kalender**:
**Verenigingskalender**, **Verjaardagen**, **Aanwezigheid bestuur**,
**Afwezigheid bestuur** en **Eigen agenda's**. Het gewone kalenderadres
brengt u naar de **Verenigingskalender**.

## Verenigingskalender {#community-calendar}

![Verenigingskalender](../assets/screenshots/calendar/community.png)

De kalender voor de hele vereniging: ledenvergaderingen,
perceelinspecties en andere verenigingsactiviteiten, samen met de
geplande werksessies uit de module [werkuren](work-hours.md). Dit is de
kalender die u op uw openbare website kunt tonen.

### Nieuw item {#new-entry}

De kaart **Nieuw item** links wordt alleen getoond als u *schrijf*recht
op de kalender hebt.

| Veld / knop | Wat het doet |
|---|---|
| **Type** | **Ledenvergadering**, **Perceelinspectie** of **Overig** (de standaard). Verandert alleen de gekleurde badge in de lijst. |
| **Titel** | Verplicht. De naam van de activiteit, bijv. „Algemene ledenvergadering“. |
| **Datum** | Verplicht. De (eerste) dag van de activiteit. |
| **Tijd** | Optionele begintijd. Laat leeg voor een item van een hele dag. |
| **Einddatum** | Optioneel. Alleen voor meerdaagse items -- leeg laten voor één dag. |
| **Eindtijd** | Optionele eindtijd. |
| **Locatie** | Optioneel. Getoond met een speld onder de titel. |
| **Beschrijving** | Optionele vrije tekst. Wordt niet in de lijst getoond, maar gaat wel in de abonnementsfeed en de websitewidget. |
| **Item toevoegen** | Slaat het item op en toont het in de lijst. |

### Aankomend {#upcoming}

| Kolom | Wat ze toont |
|---|---|
| **Datum** | De datum, plus de tijdspanne als die is ingevuld. |
| **Titel** | De titel en locatie. Bij een werksessie linkt de titel naar die sessie in de module werkuren. |
| **Type** | Een badge: **Ledenvergadering**, **Perceelinspectie**, **Overig** of **Werksessie**. |
| Prullenbakpictogram | Verwijdert het item na bevestiging (**Dit item echt verwijderen?**). Alleen zichtbaar met *verwijder*recht, en alleen bij items die hier zijn gemaakt -- werksessies wijzigt u in de module werkuren. |

Is er niets gepland, dan zegt de lijst **Geen aankomende items.**

!!! note "Welke werksessies verschijnen"
    Alleen gewone, geplande werksessies verschijnen hier. Spontane
    „speciale“ sessies (bijvoorbeeld „vandaag het bankje verven“)
    blijven weg, omdat leden er niet op kunnen plannen. Werksessies
    worden rechtstreeks uit de module werkuren gelezen, dus een sessie
    daar verzetten verandert haar hier ook -- er hoeft niets
    gesynchroniseerd te worden.

### Abonneren (ICS) {#subscribe-ics}

De knop **Abonneren (ICS)** rechtsboven toont de **Openbare ICS-link
(kan worden ingesloten op je openbare website):**. Klik in het vak om het
adres te selecteren en kopieer het.

Deze feed vraagt geen login en geen wachtwoord. Ze bevat alleen wat al
openbaar is: de items hierboven en de geplande werksessies. U kunt haar
aan een agenda-app toevoegen, of op de website van de vereniging tonen
(zie [Abonneren in een agenda-app](#subscribing-in-a-calendar-app)
hieronder).

<!-- TODO(verify): the WordPress connector plugin renders this calendar with a [parcella_calendar] shortcode. Link to the integrations page once it documents the plugin side. -->

## Verjaardagen {#birthdays}

![Verjaardagen](../assets/screenshots/calendar/birthdays.png)

De komende verjaardagen van uw actieve leden. Voor deze lijst wordt
niets opgeslagen: ze wordt telkens uit de geboortedatum van elk lid
berekend. Corrigeer een geboortedatum bij het [lid](members.md) en de
lijst klopt meteen. Leden zonder geboortedatum verschijnen niet.

### Periode en volgorde kiezen {#choosing-the-time-range-and-order}

De kop van de kaart **Aankomende verjaardagen** toont de getoonde datums
(bijvoorbeeld „01.12.2026 – 28.02.2027“) en twee keuzelijsten. De lijst
laadt opnieuw zodra u er een wijzigt.

| Veld | Wat het doet |
|---|---|
| **Periode** | **Komende maand**, **Komende 3 maanden** (de standaard) of **Komende 12 maanden**, altijd vanaf vandaag geteld. **Komende 12 maanden** toont elk lid met een geboortedatum. |
| **Sorteren op** | **Sorteren op verjaardag** (de standaard), **Sorteren op achternaam** of **Sorteren op tuinnummer**. Sorteren op tuin gebruikt het laagste huidige perceelnummer van het lid en zet leden zonder perceel achteraan. |

### Aankomende verjaardagen {#upcoming-birthdays}

| Kolom | Wat ze toont |
|---|---|
| **Datum** | De datum van de volgende verjaardag. |
| **Naam** | Het lid, gelinkt aan de ledengegevens. Ronde verjaardagen (30, 40, 50 ...) krijgen een badge **Rond**, en de hele rij is gemarkeerd. |
| **Wordt** | De leeftijd die het lid wordt. |
| **Tags** | De tags van het lid. Klik op een tag om de ledenlijst gefilterd op die tag te openen. |
| **Cadeau** | **Geen cadeau** als het lid heeft laten weten geen verjaardagscadeau te willen (ingesteld bij het lid). |

Is er in de gekozen periode niemand jarig, dan zegt de lijst **Geen
aankomende verjaardagen bekend.**

### PDF afdrukken {#print-pdf}

**PDF afdrukken** maakt een afdrukbare lijst voor wie de cadeaus
uitdeelt. Ze gebruikt precies de periode en volgorde die u op de pagina
hebt gekozen.

De PDF is A4 liggend, met het briefhoofd van uw vereniging, en heeft
meer kolommen dan de webpagina: perceel, naam, verjaardag, leeftijd die
het lid wordt (ronde verjaardagen gemarkeerd), tags, „Geen cadeau“,
postadres, hoofd-e-mailadres en hoofdtelefoonnummer. Bij sorteren op
perceel worden de leden gegroepeerd onder hun perceelnummer; een lid met
meerdere percelen verschijnt onder elk ervan, en leden zonder perceel
komen als laatste onder „Geen perceel“.

!!! warning "Persoonsgegevens"
    De afdruk bevat adressen en telefoonnummers. Ga zorgvuldig om met
    papieren exemplaren.

### Abonneren (ICS) {#subscribe-ics_1}

De knop **Abonneren (ICS)** toont een **Privé ICS-link (niet delen --
iedereen met deze link kan hem bekijken):**. De feed bevat de verjaardag
van elk actief lid als jaarlijks terugkerend item van een hele dag.

## Aanwezigheid bestuur {#council-presence}

![Aanwezigheid bestuur](../assets/screenshots/calendar/council-presence.png)

Plan wanneer bestuursleden aanwezig zijn, bijvoorbeeld een spreekuur in
het clubhuis. Leden kunnen dan zien wanneer er iemand van het bestuur is.

### Nieuw aanwezigheidsmoment {#new-presence-slot}

Alleen zichtbaar met *schrijf*recht op de kalender.

| Veld / knop | Wat het doet |
|---|---|
| **Bestuurslid(en)** | Verplicht. Vink een of meer gebruikersaccounts aan. Kies er meer dan één als meerdere leden dit moment samen invullen -- ieder van hen krijgt een eigen item voor hetzelfde moment. Vinkt u niemand aan, dan toont het formulier **Selecteer minstens één bestuurslid** en slaat het niet op. |
| **Datum** | Verplicht. |
| **Van** / **Tot** | Optionele tijden. Zonder tijd telt het moment als hele dag. |
| **Notitie** | Optioneel, bijv. „Inloopspreekuur voor leden“. |
| **Toevoegen** | Slaat het moment op. |

De lijst met personen toont alleen actieve gebruikersaccounts, niet elk
lid: een bestuurslid heeft een Parcella-account nodig om erin te staan.

### Aankomend {#upcoming_1}

De items zijn gegroepeerd onder één kop per dag.

| Kolom | Wat ze toont |
|---|---|
| **Lid** | De afbeelding en naam van de gebruiker. |
| **Tijd** | Van -- tot, of een streepje als er geen tijd is opgegeven. |
| **Notitie** | De notitie, als die er is. |
| Prullenbakpictogram | Verwijdert dit ene item (één persoon, één moment) na bevestiging. Vraagt *verwijder*recht. |

Is er niets gepland: **Geen aankomende aanwezigheidsmomenten gepland.**

De knop **Abonneren (ICS)** toont een privélink, net als bij de
verjaardagen. Momenten met een tijd verschijnen in agenda-apps als
afspraken met een tijd.

## Afwezigheid bestuur {#council-absence}

![Afwezigheid bestuur](../assets/screenshots/calendar/council-absence.png)

Vakanties en andere afwezigheden, zodat het bestuur weet wie er niet
is. Iedereen die is ingelogd, kan deze pagina gebruiken -- u hebt geen
extra recht nodig.

### Afwezigheid registreren {#log-absence}

| Veld / knop | Wat het doet |
|---|---|
| **Lid/leden** | Standaard bent u het; kies ook anderen als u dit namens hen registreert. U kunt uzelf uitvinken om een afwezigheid alleen voor iemand anders te registreren. Vinkt u iedereen uit, dan wordt de afwezigheid voor u geregistreerd. |
| **Van** | Verplicht. Eerste dag van de afwezigheid. |
| **Tot** | Verplicht. Laatste dag van de afwezigheid. |
| **Notitie** | Optioneel, bijv. „Vakantie“. U bepaalt zelf wat u eventueel uitlegt. |
| **Toevoegen** | Slaat één afwezigheid per aangevinkte persoon op. |

### Aankomende afwezigheden {#upcoming-absences}

Afwezigheden blijven in de lijst tot hun laatste dag voorbij is.

| Kolom | Wat ze toont |
|---|---|
| **Wie** | De afbeelding en naam van de gebruiker. |
| **Periode** | Van -- tot. |
| **Notitie** | De notitie, als die er is. |
| Prullenbakpictogram | Verwijdert het item na bevestiging. U ziet het bij uw eigen items; het bestuur en gebruikers met volledige toegang zien het bij elk item, om vergissingen op te ruimen. |

Is niemand weg: **Geen aankomende afwezigheden geregistreerd.**

De knop **Abonneren (ICS)** toont een privélink, net als bij de
verjaardagen. Afwezigheden zijn items van een hele dag.

## Eigen agenda's {#my-calendars}

![Eigen agenda's](../assets/screenshots/calendar/custom-index.png)

De eigen extra agenda's van uw vereniging, voor alles wat niet op de
openbare verenigingskalender hoort: reserveringen van het clubhuis,
bestuursdata, het maairooster. Geen van deze agenda's is ooit openbaar.

De lijst **Agenda's** toont:

- **Middelen** bovenaan, als de module [inventaris](inventory.md) aan
  staat en u die mag lezen -- zie [Middelen](#resources) hieronder.
- Elke agenda met haar kleurstip, naam en beschrijving. Klik op de naam
  om haar te openen.
- **Alleen bestuur** bij agenda's die alleen het bestuur en gebruikers
  met volledige toegang kunnen zien. Andere gebruikers zien deze
  agenda's helemaal niet.
- **Gearchiveerd** bij agenda's die zijn gearchiveerd. Alleen het bestuur
  en gebruikers met volledige toegang zien gearchiveerde agenda's.

Zijn er nog geen agenda's, dan zegt de lijst **Nog geen agenda's.**

### Nieuwe agenda {#new-calendar}

Alleen zichtbaar voor het bestuur en gebruikers met volledige toegang.

| Veld / knop | Wat het doet |
|---|---|
| **Naam** | Verplicht, maximaal 100 tekens, bijv. „Reserveringen clubhuis“. |
| **Kleur** | De kleur van de stip naast de naam. Standaard groen. |
| **Beschrijving** | Optioneel. Getoond onder de naam en op de pagina van de agenda. |
| **Alleen zichtbaar voor het bestuur en gebruikers met volledige toegang** | Maakt hiervan een agenda **Alleen bestuur**. |
| **Agenda aanmaken** | Maakt de agenda aan. |

### Een agenda bewerken {#editing-a-calendar}

Open **Bewerken** onder de naam van een agenda (alleen bestuur en
gebruikers met volledige toegang).

| Veld / knop | Wat het doet |
|---|---|
| **Naam**, **Kleur**, **Beschrijving** | Zoals hierboven. |
| **Alleen zichtbaar voor het bestuur en gebruikers met volledige toegang** | Wisselt de agenda tussen iedereen en alleen bestuur. Een wijziging maakt ook een nieuwe abonnementslink aan, zodat wie eerder geabonneerd was de toegang verliest. |
| **Actief (vinkje weghalen om te archiveren)** | Vink uit om de agenda te archiveren. De items blijven bewaard, maar er kunnen geen nieuwe worden toegevoegd en de abonnementslink werkt niet meer. Vink weer aan om de agenda terug te halen. |
| **Nieuw abonnementsadres (oude werken niet meer)** | Vink dit aan als iemand die de link had de agenda niet meer mag zien, bijvoorbeeld na vertrek uit het bestuur. |
| **Opslaan** | Slaat de wijzigingen op. |

Een agenda verwijderen kan niet. Archiveer haar in plaats daarvan, zodat
de geschiedenis blijft.

## De pagina van een agenda {#a-calendars-page}

![De pagina van een agenda](../assets/screenshots/calendar/custom-detail.png)

Een agenda openen vanuit **Eigen agenda's** toont haar kleur en naam als
paginatitel, de beschrijving en de komende items. **Terug** brengt u
naar **Eigen agenda's**.

De kaart **Nieuw item** werkt als die op de
[Verenigingskalender](#new-entry), zonder het veld **Type**. Ze is
alleen zichtbaar met *schrijf*recht en alleen zolang de agenda actief
is. Titel en locatie mogen maximaal 255 tekens zijn; tijden moeten
geldige tijden zijn (uu:mm), anders worden ze genegeerd.

De lijst **Aankomend** toont **Datum** (met einddatum en tijden),
**Titel** (met locatie en beschrijving) en een prullenbakpictogram om
een item te verwijderen (vraagt *verwijder*recht).

Een gearchiveerde agenda toont **Deze agenda is gearchiveerd: de items
blijven, maar er kunnen geen nieuwe worden toegevoegd.**

De knop **Abonneren (ICS)** (alleen bij actieve agenda's) toont een
**Privé-abonnementsadres (niet delen)**. Elk van uw eigen agenda's heeft
een eigen geheime link, los van de gedeelde link die de agenda's voor
verjaardagen en het bestuur gebruiken.

## Middelen {#resources}

![Middelen](../assets/screenshots/calendar/resources.png)

Een alleen-lezen overzicht van de voorwerpen van de vereniging die leden
kunnen lenen, en wie ze nu heeft. U bereikt het vanuit **Eigen agenda's**
en het werkt alleen als de inventarismodule aan staat en u daarvoor
leesrecht hebt, omdat het toont wie wat heeft geleend. **Terug** brengt
u naar **Eigen agenda's**.

De lijst bevat elk voorwerp van de vereniging dat als uitleenbaar is
gemarkeerd en niet buiten gebruik is gesteld. Voorwerpen worden beheerd
en uitgeleend in de module [inventaris](inventory.md), niet hier.

| Kolom | Wat ze toont |
|---|---|
| **Voorwerp** | De naam van het voorwerp (gelinkt aan de inventaris) en de categorie. |
| **Status** | De beschikbaarheid: **Beschikbaar**, **Uitgeleend** (niets meer over), of bij voorwerpen waarvan u er meerdere hebt bijv. „2 van 5 beschikbaar“. |
| **Momenteel uitgeleend** | Eén regel per lopende uitlening: „sinds 03.11.2026: Jan Jansen (1×)“, of een streepje als niemand het heeft. |


Uitleningen in Parcella hebben geen geplande terugbrengdatum, dus deze
pagina toont alleen de huidige situatie, geen planning voor de toekomst.

Zijn er geen uitleenbare voorwerpen: **Geen uitleenbare voorwerpen van de
vereniging.**

## Abonneren in een agenda-app {#subscribing-in-a-calendar-app}

Elke kalender heeft een knop **Abonneren (ICS)** met een adres (een
„ICS-link“). In de meeste agenda-apps voegt u het toe met een optie als
„Abonneren op agenda“, „Agenda toevoegen via URL“ of „Van internet“. De
app controleert het adres dan regelmatig, zodat nieuwe items vanzelf
verschijnen. Hoe vaak hangt af van de app.

| Kalender | Link | Wie mag haar hebben |
|---|---|---|
| Verenigingskalender | Openbaar | Iedereen. Veilig voor de website van de vereniging. |
| Verjaardagen | Privé, gedeeld geheim | Alleen mensen die verjaardagen van leden mogen zien. |
| Aanwezigheid bestuur | Privé, gedeeld geheim | Bestuur en helpers. |
| Afwezigheid bestuur | Privé, gedeeld geheim | Bestuur en helpers. |
| Elk van de **Eigen agenda's** | Privé, één geheim per agenda | Wie die agenda mag zien. |

De links voor verjaardagen, aanwezigheid en afwezigheid van het bestuur
gebruiken allemaal **hetzelfde** geheim voor uw hele installatie. Wie
een van deze links heeft, kan alle drie de feeds lezen, zonder in te
loggen. Geef ze alleen aan mensen die u vertrouwt.

!!! warning "Als een privélink uitlekt"
    Vink voor **Eigen agenda's** bij de agenda **Nieuw abonnementsadres
    (oude werken niet meer)** aan en sla op. Voor de links voor
    verjaardagen en het bestuur is er geen knop om het gedeelde geheim
    te wijzigen.
    <!-- TODO(verify): there is no UI to rotate the shared ICS token (stored as a club setting); confirm whether an administrator can reset it somewhere, e.g. via the API club settings. -->

## Gerelateerd {#related}

- [Werkuren](work-hours.md) -- waar de werksessies op de
  verenigingskalender vandaan komen.
- [Leden](members.md) -- geboortedatums, tags en de instelling „geen
  cadeau“.
- [Inventaris](inventory.md) -- uitleenbare voorwerpen en uitleningen.
- [Groepen](../administration/groups.md) -- iemand rechten op de
  kalender geven.
- [Modules in- en uitschakelen](../administration/modules.md)

# Leden en percelen importeren {#importing-members-and-parcels}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Houdt uw vereniging haar ledenlijst, perceellijst of meterlijst al bij in
een spreadsheet, dan hoeft u niet alles opnieuw te typen. Sla de
spreadsheet op als CSV-bestand, upload het, vertel Parcella welke kolom
wat is, en importeer.

Dat werkt op dezelfde manier voor **percelen**, **leden**,
**meetpunten**, **meterstanden** en **externe contacten**. Dit stappenplan
loopt ze door in de volgorde die voor een nieuwe installatie zinvol is.

!!! info "Wie kan dit doen"
    Leden en percelen importeren vraagt **schrijf**recht op **Leden en
    percelen**; meetpunten en meterstanden vragen schrijven op **Water**
    of **Elektriciteit**; externe contacten vragen schrijven op **Externe
    contacten**. Bestuursleden en beheerders hebben ze allemaal.

!!! warning "Download eerst een back-up"
    Een import schrijft veel records tegelijk en er is geen „ongedaan
    maken“. Open **Administratie → Systeem** en klik op **Back-up
    downloaden** voordat u begint. Zie
    [Back-up en herstel](../administration/backup.md).

## Hoe elke import werkt {#how-every-import-works}

Alle vijf de imports hebben dezelfde twee stappen.

1. **Uploaden.** Klik op de lijstpagina op **CSV-import**, kies het
   bestand en klik op **Importeren**. Er wordt nog niets opgeslagen.
2. **CSV-kolommen koppelen.** Parcella toont een tabel: één kolom per
   kolom van uw bestand, met uw kop bovenaan en de eerste vijf
   gegevensrijen eronder. Boven elke kolom staat een keuzelijst.
   Parcella heeft het passende veld al uit de kop geraden (Engelse en
   Duitse koppen werken allebei, bijvoorbeeld „Nachname“ of „Last
   name“). Controleer elke keuzelijst, verbeter de verkeerde, en zet
   kolommen die u niet wilt op **— Negeren —**. Klik dan op
   **Importeren**.

Daarna bent u terug op de lijstpagina met een korte samenvatting: hoeveel
rijen zijn aangemaakt, bijgewerkt of overgeslagen, en de redenen voor de
eerste paar overgeslagen rijen.

### Hoe uw bestand eruit moet zien {#what-your-file-should-look-like}

- **De eerste rij bevat de kolomkoppen.** Elke rij eronder is één record.
  De koppen hoeven niet precies te kloppen -- u koppelt ze in stap 2.
- **Puntkomma of komma** tussen de kolommen: Parcella herkent welke uw
  bestand gebruikt.
- **Bij voorkeur UTF-8.** De meeste spreadsheetprogramma's bieden bij
  het opslaan „CSV UTF-8“ aan. Gewone „CSV“ uit Excel (Windows/ANSI)
  werkt ook: accenten en umlauts komen in beide gevallen goed door.
- **Datums** als `2026-03-15` of `15.03.2026` (ook `15.03.26`).
- **Decimale getallen** met komma of punt: `312,5` en `312.5` werken
  allebei. Bankbedragen en meterstanden mogen ook
  duizendtalscheidingstekens hebben, op z'n Duits of op z'n Engels:
  `12.345,6` en `12,345.6`.
- **Meerdere waarden in één cel** (e-mailadressen, telefoonnummers,
  tags) worden gescheiden door puntkomma's. Het spreadsheetprogramma zet
  zo'n cel bij het opslaan tussen aanhalingstekens -- dat is in orde.

!!! tip "Begin met een export"
    Het eenvoudigste sjabloon is de eigen export van Parcella. Elke lijst
    met een import heeft ook een **CSV-export**. Exporteer de (nog lege of
    met voorbeeldgegevens gevulde) lijst, vul het bestand in uw
    spreadsheetprogramma in en importeer het opnieuw: de koppen passen dan
    zonder enige koppeling.

## 1. Percelen {#1-parcels}

Importeer eerst de percelen. Leden, meetpunten en meterstanden verwijzen
naar percelen via hun nummer.

1. Open **Percelen** en klik op **CSV-import**.
2. Kies het bestand en klik op **Importeren**.
3. Koppel op **CSV-kolommen koppelen** minstens **Perceelnummer**. De
   andere velden zijn optioneel.
4. Klik op **Importeren**. De samenvatting luidt bijvoorbeeld *„24
   geïmporteerd, 0 overgeslagen.“*

| Veld | Wat Parcella verwacht |
|---|---|
| **Perceelnummer** | Verplicht. Wordt in hoofdletters opgeslagen („g12“ wordt „G12“). |
| **Oppervlakte (m²)** | Een getal, met komma of punt als decimaalteken. Al het andere blijft leeg. |
| **Breedtegraad** / **Lengtegraad** | Optionele GPS-positie, in decimale graden (bijv. `51,339695`). |
| **Status** | `ACTIVE`, `TERMINATED`, `COMMUNAL` of `DELETED` (hoofd- of kleine letters). Leeg of iets anders betekent actief. |
| **Notities** | Vrije tekst. |

!!! warning "Bestaande percelen worden overgeslagen, niet bijgewerkt"
    Bestaat een perceelnummer al in Parcella, dan wordt die rij
    **overgeslagen** en blijft het bestaande perceel precies zoals het
    is. Wilt u bestaande percelen wijzigen, bewerk ze dan met de hand.
    Rijen zonder perceelnummer worden genegeerd en in de samenvatting
    apart geteld.

De perceelimport wijst **geen** huurders toe. De perceelexport heeft een
kolom met de namen van de huurders, maar de import negeert die -- zie
stap 3 hieronder.

## 2. Leden {#2-members}

1. Open **Leden** en klik op **CSV-import**.
2. Kies het bestand en klik op **Importeren**.
3. Koppel op **CSV-kolommen koppelen** minstens **Voornaam** en
   **Achternaam**. Zonder beide stopt de import met *„Koppel eerst zowel
   voornaam als achternaam voordat u importeert.“*
4. Klik op **Importeren**. De samenvatting luidt bijvoorbeeld *„80 nieuw
   geïmporteerd, 0 bijgewerkt“*.

| Veld | Wat Parcella verwacht |
|---|---|
| **Voornaam**, **Achternaam** | Verplicht. Een rij waarin een van beide leeg is, wordt overgeslagen. |
| **Straat**, **Postcode**, **Plaats** | Vrije tekst. |
| **Geboortedatum** | Een datum (zie hierboven). Wordt ook gebruikt om twee leden met dezelfde naam uit elkaar te houden. |
| **IBAN** | Vrije tekst, wordt niet gecontroleerd. |
| **Lid sinds**, **Lid tot** | Datums. Een leeg **Lid tot** betekent een actief lid. |
| **E-mailmeldingen** | „No“, „Nein“, „false“ of „0“ betekent dat het lid verenigingsinformatie **niet** per e-mail wil; alles wat verder is ingevuld betekent ja. Een lege cel of een niet-gekoppelde kolom betekent ja voor een nieuw lid en „geen wijziging“ voor een bestaand lid. |
| **E-mailadressen** | Een of meer, gescheiden door puntkomma's. Het eerste wordt het hoofdadres. |
| **Telefoonnummers** | Een of meer, gescheiden door puntkomma's. Het eerste wordt het hoofdnummer. |
| **Notities** | Vrije tekst. |

**Bestaande leden herkennen.** Voor elke rij zoekt Parcella een bestaand
lid met dezelfde voor- en achternaam -- en, als de rij een geboortedatum
heeft, ook met dezelfde geboortedatum. Vindt het er precies één, dan
**werkt** het dat lid **bij** in plaats van een tweede aan te maken.
Hebben meerdere leden die naam, dan kiezen de e-mailadressen en
telefoonnummers uit de rij het juiste; past de rij nog steeds op meer dan
één, dan wordt ze overgeslagen en in de samenvatting vermeld. Een e-mail
of telefoonnummer alleen koppelt nooit aan een lid met een andere naam.

Een update wijzigt alleen wat de rij bevat: een kolom op **— Negeren —**
of een lege cel laat de opgeslagen waarde zoals ze is. U kunt dus alleen
de adressen bijwerken met een bestand dat alleen namen en adressen
bevat. E-mailadressen en telefoonnummers worden bij een update nooit
gewijzigd; ze worden alleen voor nieuwe leden toegevoegd.

Tags, perceeltoewijzingen en de instelling **Wil geen
verjaardagscadeaus** horen niet bij de import. De export bevat kolommen
**Parzellen** en **Tags**, maar de import negeert ze.

## 3. Leden aan hun percelen toewijzen {#3-assign-members-to-their-parcels}

Er is geen import van huren. Bestaan leden en percelen eenmaal, wijs ze
dan met de hand toe:

1. Open het perceel in **Percelen**.
2. Begin in **Huidige huurders** de naam van het lid te typen in **Kies
   lid…** en kies het uit de lijst.
3. Vul eventueel de begindatum van de huur in.
4. Laat **Gebruiken als factuuradres** aangevinkt bij de huurder die de
   facturen van het perceel moet krijgen.
5. Klik op **Toewijzen**.

Bij veel percelen brengt de knop **Volgende** bovenaan de perceelpagina u
direct naar het volgende.

Meer: [Percelen](../modules/parcels.md).

## 4. Meetpunten {#4-metering-points}

Meetpunten zijn de water- en elektriciteitsaansluitingen (hoofdmeter, één
per perceel, verenigingsaansluitingen). Water en elektriciteit worden
apart geïmporteerd, elk in een eigen menu.

1. Open **Water → Meetpunten** (of **Elektriciteit → Meetpunten**) en
   klik op **CSV-import**.
2. Kies het bestand en klik op **Importeren**.
3. Koppel de kolommen en klik op **Importeren**. Er moet minstens één
   kolom gekoppeld zijn.

| Veld | Wat Parcella verwacht |
|---|---|
| **Type** | `PARCEL`, `MAIN_METER` of `CLUB`. Koppelt u deze kolom helemaal niet, dan telt elke rij als perceelaansluiting. Koppelt u haar wel, dan wordt een rij met een leeg of onbekend type overgeslagen („ongeldig type“). |
| **Perceelnummer** | Verplicht bij perceelaansluitingen; moet overeenkomen met een bestaand perceelnummer, anders wordt de rij overgeslagen („perceel niet gevonden“). |
| **Omschrijving** | Naam van een hoofdmeter of verenigingsaansluiting, bijv. „Clubhuis“. |
| **Meternummer** | Het nummer dat op de meter staat. |
| **Geïnstalleerd op** | Datum. |
| **Gekalibreerd tot** | Alleen het **jaartal**, bijv. `2031`. |
| **Beginstand** | De stand bij de installatie van de meter. Leeg betekent 0. |
| **Factor** | Meestal leeg (= 1). Bij meters die maar een deel van de echte waarde tonen, bijv. `20`. Moet groter zijn dan 0. |

De import **maakt** meetpunten alleen **aan**. Een perceel dat voor dit
medium al een meetpunt heeft, of een hoofdmeter of verenigingsaansluiting
met dezelfde omschrijving, wordt overgeslagen als „bestaat al“ -- twee keer
dezelfde export importeren kan dus geen kwaad. Nieuwe meetpunten beginnen
altijd als ingeschakeld.

!!! note
    **Gekalibreerd tot** is een jaartal. Een datum in deze kolom
    (`30.06.2027`, `2027-06`, `06/2027`) is ook in orde: Parcella haalt
    er het jaar uit. Een rij waarvan de waarde geen viercijferig jaartal
    heeft (`06/27`, `binnenkort`), wordt overgeslagen met „‘Gekalibreerd
    tot’ is geen jaartal“; de andere rijen worden geïmporteerd.

Meer: [Water en elektriciteit](../modules/metering.md).

## 5. Meterstanden {#5-meter-readings}

Meterstanden worden gekoppeld aan meetpunten die al bestaan; de import
maakt nooit een meetpunt aan.

1. Open **Water → Meterstanden** (of **Elektriciteit → Meterstanden**) en
   klik op **CSV-import**.
2. Kies het bestand en klik op **Importeren**.
3. Koppel de kolommen. Heeft uw bestand geen kolom met het jaar, of laten
   sommige rijen die leeg, vul het jaar dan in bij **Standaardjaar
   (optioneel)**.
4. Klik op **Importeren**.

| Veld | Wat Parcella verwacht |
|---|---|
| **Type** | Als bij meetpunten. Niet gekoppeld = elke rij is een perceelaansluiting. |
| **Perceelnummer** / **Omschrijving** | Vinden het meetpunt, net als hierboven. |
| **Meternummer** | Optionele controle. Komt het niet overeen met de meter die nu is geïnstalleerd, dan wordt de rij overgeslagen („meternummer komt niet overeen“) -- waarschijnlijk hoort ze bij een meter die intussen is vervangen. |
| **Jaar** | Het jaar waar de stand bij hoort. Heeft voorrang boven **Standaardjaar (optioneel)**. |
| **Datum** | De dag van de aflezing. Verplicht. |
| **Meterstand** | De waarde op de display. Verplicht. |
| **Notitie** | Vrije tekst. |

Parcella raadt het jaar nooit uit de datum. Een stand uit januari kan nog
bij de afrekening van vorig jaar horen, dus u zegt welk jaar het is.

Eén bestand kan meerdere jaren bevatten. Heeft een meetpunt al een stand
voor een jaar, dan **vervangt** de import die.

Een stand die onwaarschijnlijk lijkt -- bijvoorbeeld lager dan de
vorige -- wordt toch opgeslagen. De samenvatting toont dan een aparte
waarschuwing met de betrokken rijen, zodat u ze kunt controleren.

Meer: [Meterstanden opnemen](meter-readings.md).

## 6. Externe contacten {#6-external-contacts}

Leveranciers, vaklui en instanties, als u de module **Externe contacten**
gebruikt.

1. Open **Externe contacten** en klik op **CSV-import**.
2. Kies het bestand en klik op **Importeren**.
3. Koppel de kolommen op **Kolommen koppelen**. Geen enkel veld is
   verplicht; volledig lege rijen worden overgeslagen.
4. Klik op **Importeren**.

| Veld | Wat Parcella verwacht |
|---|---|
| **Type (bedrijf/persoon)** | „Firma“, „Company“ of „Unternehmen“ voor een bedrijf; „Person“ voor een persoon. Zonder deze kolom is een rij met voor- of achternaam een persoon, anders een bedrijf. |
| **Bedrijfsnaam** | Bij een bedrijf: de naam ervan. Bij een persoon: het bedrijf waar hij bij hoort -- dat wordt aangemaakt als het nog niet bestaat. |
| **Voornaam**, **Achternaam**, **Functie** | Bij personen. |
| **Straat**, **Postcode**, **Plaats**, **IBAN** | Adres en bankgegevens. Bij een persoon bij een bedrijf vullen ze lege velden van het bedrijf aan. |
| **E-mailadressen**, **Telefoonnummers**, **Labels** | Meerdere waarden gescheiden door puntkomma's. |
| **Notities** | Vrije tekst. |

Een bedrijf dat al bestaat (dezelfde naam, hoofdletters maken niet uit),
of een persoon met dezelfde naam, wordt **bijgewerkt** met de niet-lege
cellen van de rij. Ontbrekende telefoonnummers, e-mails en labels worden
toegevoegd. Anders dan bij de ledenimport wordt er nooit iets verwijderd
of leeggemaakt.

Meer: [Externe contacten](../modules/external-contacts.md).

## Veelvoorkomende problemen {#common-problems}

| Wat u ziet | Waarom en wat te doen |
|---|---|
| *„Dit CSV-bestand lijkt leeg te zijn.“* | Het bestand heeft helemaal geen rijen. Controleer of u het juiste werkblad hebt opgeslagen. |
| Alle gegevens komen op het koppelscherm in één kolom terecht | Parcella kon het scheidingsteken niet bepalen. Sla het bestand opnieuw op als „CSV (gescheiden door puntkomma's)“ of „CSV (gescheiden door komma's)“. |
| Vreemde tekens in plaats van accenten | Het bestand gebruikt een ongebruikelijke codering (geen UTF-8 en geen Windows/ANSI, bijv. van een oude Mac). Sla het opnieuw op als „CSV UTF-8“. |
| Leden overgeslagen omdat voor- of achternaam ontbreekt | Die rijen hebben een lege naamcel, of de naamkolom is niet gekoppeld. |
| Een lid verschijnt twee keer | Twee rijen verschillen in spelling of geboortedatum, dus Parcella beschouwt ze als verschillende mensen. Verwijder het dubbele lid met de hand. |
| Het adres van een bestaand lid is ineens leeg | Het lid is bijgewerkt vanuit een rij of bestand zonder deze kolom. Zie de uitleg in stap 2; herstel de gegevens zo nodig uit de back-up. |
| Percelen „overgeslagen“ | Het perceelnummer bestaat al. Bewerk bestaande percelen met de hand. |
| Meetpunten „perceel niet gevonden“ | Het perceelnummer uit het bestand bestaat niet in Parcella -- importeer eerst de percelen en controleer de spelling („G12“ tegenover „G 12“). |
| Meterstanden „meetpunt niet gevonden“ | Importeer of maak eerst de meetpunten aan. Hebt u **Type** gekoppeld, controleer dan de waarde. |
| Meterstanden „ongeldige rij“ | **Datum** of **Meterstand** is leeg of onleesbaar, of het jaar ontbreekt (geen kolom **Jaar** en geen **Standaardjaar (optioneel)**). |
| Meterstanden „geen actieve meter“ | Het meetpunt heeft geen geïnstalleerde meter. Voeg er een toe op de pagina van het meetpunt. |
| `'` aan het begin van geëxporteerde telefoonnummers | Parcella voegt het toe aan cellen die beginnen met `+`, `-`, `=` of `@`, zodat spreadsheetprogramma's ze niet als formule zien. Haal het weg vóór de ledenimport, of laat het staan -- de import van externe contacten haalt het voor u weg. |

## Gerelateerd {#related}

- [Leden](../modules/members.md)
- [Percelen](../modules/parcels.md)
- [Water en elektriciteit](../modules/metering.md)
- [Externe contacten](../modules/external-contacts.md)
- [Een nieuwe vereniging inrichten](new-club-setup.md)
- [Meterstanden opnemen](meter-readings.md)

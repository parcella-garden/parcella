# Een werksessie organiseren {#organising-a-work-session}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De meeste verenigingen vragen van elk perceel (of elk lid) per jaar een
aantal [verplichte uren](../glossary.md#mandatory-hours)
gemeenschapswerk -- haag snoeien, paden herstellen, de voorjaarsschoonmaak.
Dit stappenplan volgt één [werksessie](../glossary.md#work-session) van
planning tot jaarevaluatie: aanmaken, leden zich via de website laten
aanmelden, vastleggen wie er echt kwam, en zien wie nog uren schuldig is.

!!! info "Wie kan dit doen"
    Sessies aanmaken en aanwezigheid vastleggen vraagt **schrijf**recht
    op **Werksessies**; een deelnemer of overdracht verwijderen vraagt
    **verwijderen**. De module (**Werktijdenbeheer**) staat standaard aan.
    Publiceren op de website vraagt een beheerder voor de eenmalige
    inrichting in stap 3.

## 1. De regels van het jaar instellen (eens per jaar) {#1-set-the-years-rules-once-a-year}

1. Open **Werksessies → Sessies & Overzicht**. Heeft het jaar nog geen
   regels, dan zegt de pagina *„Nog geen configuratie voor verplichte
   uren voor ….“* -- klik op **Nu aanmaken →** (of **Urenconfiguratie**
   onderaan).
2. Vul onder **Jaar aanmaken / bijwerken** in:
    - **Jaar**
    - **Totaal verplichte uren** -- de uren die per jaar verschuldigd
      zijn;
    - **Uurtarief** -- wat een niet-gewerkt uur kost;
    - **Facturatiemodus** -- **Per huur / perceel** (alle huurders van
      een perceel werken de uren samen af) of **Per lid** (elk lid
      afzonderlijk);
    - eventueel een **Notitie**, bijv. het besluit van de algemene
      ledenvergadering.
3. Klik op **Opslaan**.

Op dezelfde pagina regelt de kaart **Bevestigingsmail bij aanmelding** de
e-mail die leden krijgen nadat ze zich via de website hebben aangemeld
(stap 3).

**Vrijstellingen.** Bestuursleden, mensen met gezondheidsredenen of boven
een leeftijdsgrens zijn vaak vrijgesteld. Richt dat in onder **Sessies &
Overzicht → Verenigingsrollen**: maak een rol aan met **Vrijgesteld van
verplichte uren** en een **Reden vrijstelling**, en wijs er dan voor het
jaar leden aan toe. Is één huurder van een perceel vrijgesteld, dan is het
hele perceel vrijgesteld; een vrijstelling geldt voor het hele
kalenderjaar.

## 2. De sessie aanmaken {#2-create-the-session}

1. Open **Werksessies → Sessies & Overzicht** en klik op **Nieuwe
   sessie**.
2. Vul in:
    - **Titel**, bijv. „Voorjaarsschoonmaak“;
    - **Type**: **Standaard (gepland)** voor sessies die u aankondigt, of
      **Speciaal (spontaan)** voor ongeplande -- speciale sessies
      verschijnen nooit op de website;
    - **Datum**, **Van** en **Tot**;
    - **Max. deelnemers** -- leeg laten voor onbeperkt;
    - **Aanmeldingstermijn (dagen vooraf)** -- de aanmelding via de
      website sluit zoveel dagen vóór de sessie (1 = de dag ervoor); leeg
      betekent dat ze sluit als de sessie voorbij is;
    - **Uren per deelnemer** -- toegekend aan iedereen die aanwezig is,
      later per persoon aan te passen;
    - **Beschrijving** -- taken, gereedschap, wat mee te nemen.
3. Klik op **Sessie aanmaken**.

De sessie staat in de lijst **Werksessies …** van haar jaar.

## 3. De aanmelding op de website publiceren (eenmalige inrichting) {#3-publish-the-sign-up-on-the-club-website-one-time-setup}

Leden melden zich op de website van de vereniging aan met hun
**perceelnummer** en, optioneel, hun naam -- zonder Parcella-account. De
website toont nooit welke leden op welk perceel wonen.

Een beheerder richt dit één keer in:

1. **Administratie → Instellingen → Functiegebieden**: vink **Publieke
   aanmeld-API** aan en klik op **Instellingen opslaan**. Het staat
   standaard uit omdat het een openbaar formulier opent.
2. **Administratie → Integraties → Publieke aanmeld-API**: noteer het
   **API-token** (voor een connector aan de serverkant) en voeg uw
   website toe onder **Toegestane websiteadressen** (bijv.
   `https://example.org`), dan **Adressen opslaan**. Vink eventueel
   **ALTCHA vereisen** aan tegen spam.
3. Voeg op de website het aanmeldformulier toe -- met de plug-in Parcella
   Connector voor WordPress, of een gewoon HTML-formulier voor elke
   andere site. Uw webbouwer vindt de details in de
   ontwikkelaarsdocumentatie.
   <!-- TODO(verify): link to the gardeners/website-form instructions once that page exists. -->

Daarna verschijnt elke nieuwe **Standaard**-sessie vanzelf op de website,
zolang haar datum niet voorbij is, haar aanmeldingstermijn niet voorbij
is en ze niet vol is.

**Wat er bij een aanmelding gebeurt.** Parcella zoekt de huidige
huurders van het perceel op. Komt de ingetypte naam met precies één van
hen overeen, dan wordt alleen dat lid aangemeld. Is er geen naam
opgegeven of komt die niet duidelijk overeen, dan worden **alle** huidige
huurders van het perceel aangemeld, met een notitie die het bestuur vraagt
het te controleren -- verwijder wie zich niet echt heeft aangemeld. Elk
nieuw aangemeld lid krijgt de bevestigingsmail op het adres dat in
Parcella is opgeslagen (niet het adres dat in het formulier is getypt).

Meer: [Integraties](../administration/integrations.md) en
[Voor tuinders](../gardeners/index.md).

## 4. De aanmeldingen in de gaten houden {#4-keep-an-eye-on-sign-ups}

- Nieuwe aanmeldingen tonen een teller naast **Werksessies** in de
  zijbalk en op het dashboard.
- Open de sessie (klik erop in de lijst op **Sessies & Overzicht**).
  Nieuwe deelnemers dragen een badge **Nieuw**. Hebt u ernaar gekeken,
  klik dan op **Markeren als bekeken**.
- Controleer de kolom **Notitie**: aanmeldingen via de website bevatten
  daar de opmerkingen en contactgegevens van de bezoeker, en een
  waarschuwing als het hele perceel is aangemeld.
- Om iemand met de hand toe te voegen (aanmelding per telefoon),
  gebruikt u **Kies lid…** onderaan de deelnemerstabel, kiest u
  **Geregistreerd**, en klikt u op **Toevoegen**.

**Taken (optioneel).** Houdt u een lijst met klussen bij onder
**Werksessies → Taken**, plan er dan daar een paar in voor deze sessie.
Op de sessiepagina kunt u ze dan aan een deelnemer toewijzen
(**Toegewezen aan**) en ziet u hun **Belasting** (**Licht**,
**Gemiddeld**, **Zwaar**). **Taken beheren** leidt naar de volledige
lijst.

## 5. Op de dag zelf: de deelnemerslijst afdrukken {#5-on-the-day-print-the-attendee-sheet}

1. Open de sessie en klik op **Deelnemerslijst**.
2. Druk de PDF af. Die toont elke aangemelde deelnemer met perceel, naam,
   verwachte uren, toegewezen taak en een handtekeningregel.

Corrigeer de uren zo nodig op papier; u typt ze daarna in. De lijst
verandert niets in Parcella.

## 6. Daarna: de aanwezigheid vastleggen {#6-afterwards-record-attendance}

1. Open de sessie.
2. Kies voor elke deelnemer **Aanwezig** of **Niet verschenen** in de
   keuzelijst **Status**. Dat wordt meteen opgeslagen.
3. Werkte iemand meer of minder dan **Uren per deelnemer**, typ dan de
   werkelijke uren in zijn veld **Uren** en klik op de knop ✓.
4. Mensen die zonder aanmelding kwamen: **Kies lid…**, status
   **Aanwezig**, hun uren, **Toevoegen**.
5. Gebruik het zoekveld boven de tabel om iemand op naam of
   perceelnummer te vinden.

Alleen deelnames met **Aanwezig** tellen mee voor de uren.

## 7. Sponsorschappen en urenoverdrachten {#7-sponsorships-and-hours-transfers}

**[Sponsorschappen](../glossary.md#sponsorship)** zijn delen van het
terrein die een lid het hele jaar verzorgt (een haag, de speeltuin) in
plaats van, of naast, het bijwonen van sessies.

1. Open **Werksessies → Sponsorschappen**.
2. Vul onder **Sponsorschap aanmaken / lid toevoegen** het **Gebied**,
   het **Lid** (of laat het op **– nog niet toegewezen –** om het gebied
   eerst aan te bieden), een **Beschrijving**, de **Te crediteren
   uren/jaar** en **Geldig vanaf** / **Geldig tot** in.
3. Klik op **Opslaan**.

Een sponsorschap kent pas uren toe als het een datum **Geldig vanaf** en
een lid heeft. Meerdere leden kunnen een gebied delen -- voeg per lid een
rij toe met dezelfde gebiedsnaam; ieder krijgt het volledige aantal uren.

**[Urenoverdrachten](../glossary.md#hours-transfer)**: een lid dat meer
deed dan nodig, kan uren aan iemand anders geven.

1. Open **Werksessies → Uren overdragen**.
2. Kies onder **Uren overdragen** **Van (geeft)**, **Aan (ontvangt)**, de
   **Uren** en eventueel een **Notitie**.
3. Klik op **Uren overdragen**.

Alleen het overschot van de gever voor het jaar kan worden gegeven.
Leden zonder perceel en vrijgestelde leden kunnen al hun uren geven.

## 8. De jaarevaluatie {#8-the-year-end-evaluation}

1. Open **Werksessies → Jaarlijkse evaluatie** en kies het jaar.
2. Elke rij is een perceel (of lid, afhankelijk van de
   **Facturatiemodus**) met **Vereist**, **Sessies**, **Sponsorschap**,
   **Overgedragen**, **Totaal**, **Openstaand** en **Schuld**, en een
   **Status** **Voldaan**, **Open** of **Vrijgesteld**.
3. Klik op de pijl aan het begin van een rij (**Werksessies tonen**) om
   te zien uit welke sessies de uren kwamen.
4. **CSV-export** downloadt de evaluatie.

Huurders die in de loop van het jaar vertrokken, zijn de uren van dat
jaar nog steeds verschuldigd; hun rij draagt een badge „pacht beëindigd
…“.

Om de openstaande uren te factureren, voegt u een post **Tekort werkuren
(uit module)** toe aan de jaarlijkse factuurronde -- zie
[De jaarfacturen opmaken](annual-invoicing.md).

## Gerelateerd {#related}

- [Werkuren](../modules/work-hours.md)
- [Kalender](../modules/calendar.md)
- [Integraties](../administration/integrations.md)
- [De jaarfacturen opmaken](annual-invoicing.md)
- Woordenlijst: [verplichte uren](../glossary.md#mandatory-hours),
  [vrijstelling](../glossary.md#exemption),
  [sponsorschap](../glossary.md#sponsorship),
  [urenoverdracht](../glossary.md#hours-transfer)

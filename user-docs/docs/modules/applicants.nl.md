# Aanmelders {#applicants}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De lijst met aanmelders is de wachtlijst van uw vereniging voor vrije
tuinpercelen. Aanmeldingen via het formulier op uw website komen hier
vanzelf binnen; u kunt ook aanmeldingen invoeren die telefonisch of op
papier binnenkwamen. U houdt bij wie u hebt gecontacteerd en wie een
tuin is aangeboden, en wanneer een perceel vrijkomt, draagt u het over
-- de aanmelder wordt in één stap lid en nieuwe huurder.

Aanmelders staan bewust los van de ledenlijst. De meeste aanmelders
krijgen nooit een perceel, dus hun gegevens mogen niet terechtkomen in
ledentellingen, facturen, werkuren of mailings.

!!! info "Wie kan dit gebruiken"
    De module **Aanmelders** staat standaard aan. U kunt haar uitschakelen
    onder [Modules in- en uitschakelen](../administration/modules.md).

    - De lijst en de aanmeldingen **zien** vraagt *lees*recht op
      **Aanmelders**.
    - Een aanmelder **toevoegen**, contactgegevens, status en notitie van
      het bestuur **bewerken**, en een nieuwe aanmelder **contacteren**
      vraagt *schrijf*recht.
    - Een aanmelder definitief **verwijderen** vraagt *verwijder*recht.
    - **Perceel toewijzen** vraagt *schrijf*recht op zowel
      **Aanmelders** als **Leden en percelen**.

    Bestuursleden en beheerders hebben dat allemaal. Een groep kan het
    aan anderen geven, bijv. aan wie de perceeltoewijzing regelt (zie
    [Groepen](../administration/groups.md)).

    Aanmeldingen via uw website komen alleen binnen zolang de aparte
    module **Openbare aanmeldformulier-API** aan staat. Die staat
    standaard uit, omdat ze mensen buiten de vereniging in Parcella laat
    schrijven. Zie [Aanmeldingen via uw website](#applications-from-your-website).

## Waar u nieuwe aanmeldingen opmerkt {#where-you-notice-new-applications}

- Het item **Aanmelders** in het hoofdmenu toont een rood getal: de
  aanmeldingen waar nog niemand naar heeft gekeken (status **Nieuw**).
  Het verdwijnt zodra elke nieuwe aanmelding een andere status heeft
  gekregen.
- Het [dashboard](../getting-started/dashboard.md) heeft een kaart
  **Nieuwe aanmeldingen** met hetzelfde getal, „nog niet bekeken“. Die
  opent de lijst gefilterd op nieuwe aanmeldingen.

Parcella mailt het bestuur niet over een nieuwe aanmelding -- het getal
in het menu en op het dashboard is het signaal.

## Statussen {#statuses}

Elke aanmelding doorloopt deze statussen. U stelt ze in op de
[aanmeldingspagina](#application-page); alleen **Afgesloten (tuin
toegewezen)** zet Parcella zelf.

| Status | Betekenis |
|---|---|
| **Nieuw** | Net binnengekomen; nog niemand heeft ernaar gekeken. |
| **Gecontacteerd** | Het bestuur heeft contact gehad -- bijv. de eerste e-mail gestuurd. De aanmelder staat op de wachtlijst. |
| **Tuin aangeboden** | Er is een tuin aangeboden. |
| **Geaccepteerd** | De aanmelder wil de aangeboden tuin; de overdracht wordt nog geregeld. |
| **Afgewezen** | De vereniging heeft afgewezen, of de aanmelder wil geen verdere aanbiedingen. |
| **Afgesloten (tuin toegewezen)** | De aanmelder heeft via **Perceel toewijzen** een perceel gekregen. |

**Nieuw**, **Gecontacteerd**, **Tuin aangeboden** en **Geaccepteerd**
tellen als *open*. Slaat een aanmelder een aanbod af maar wil hij op de
wachtlijst blijven, zet hem dan terug op **Gecontacteerd**. Wil hij geen
verdere aanbiedingen, zet dan **Afgewezen**.

## Lijst met aanmelders {#applicant-list}

![Lijst met aanmelders](../assets/screenshots/applicants/list.png)

Open **Aanmelders** in het hoofdmenu. De lijst toont de aanmeldingen,
de meest recente aanmeldingsdatum eerst.

### Filteren en zoeken {#filter-and-search}

| Veld / knop | Wat het doet |
|---|---|
| **Nieuw** | Alleen aanmeldingen met status **Nieuw**. Alleen zichtbaar zolang er nieuwe aanmeldingen zijn -- en dan opent de lijst met dit filter. |
| **Open** | Aanmeldingen die **Nieuw**, **Gecontacteerd**, **Tuin aangeboden** of **Geaccepteerd** zijn. De lijst opent met dit filter als er geen nieuwe aanmeldingen zijn. |
| **Afgerond** | Aanmeldingen die **Afgesloten (tuin toegewezen)** of **Afgewezen** zijn. |
| **Alle** | Elke aanmelding. |
| **Naam, e-mail, telefoon, bericht, notities…** | Doorzoekt voor- en achternaam, e-mailadres, telefoonnummer, het bericht van de aanmelder en de notitie van het bestuur. Werkt samen met de filterknoppen. Omdat de notitie van het bestuur wordt doorzocht, vindt een ticketnummer dat u daar hebt genoteerd de aanmelder. |
| **Zoeken** | Past de zoekopdracht toe. |
| **Wissen** | Wist de zoekopdracht, houdt de filterknop. |

### Kolommen {#columns}

| Kolom | Wat ze toont |
|---|---|
| Vinkje | Selecteert de aanmelder voor **Schrijf naar de geselecteerde aanvragers** (zie hieronder). |
| **Naam** | Voor- en achternaam, of het e-mailadres als er geen naam is opgegeven. Klik erop om de aanmelding te openen. |
| **E-mail** | Klik om vanuit uw eigen mailprogramma te schrijven. |
| **Telefoon** | |
| **Aangemeld op** | De aanmeldingsdatum. Die bepaalt de volgorde van de wachtlijst. |
| **Status** | Zie [Statussen](#statuses). |
| Oogknop | Opent de aanmelding. |

Naast de naam kunnen twee soorten badges verschijnen:

- **2×**, **3×** … -- dit e-mailadres heeft zich meer dan eens
  aangemeld. Parcella voegt herhaalde aanmeldingen niet samen; elke
  blijft een apart item, zodat er geen bericht verloren gaat. U beslist
  wat u ermee doet. De aanmeldingspagina noemt de andere.
- **Rode vlag** -- de naam, het e-mailadres of het telefoonnummer van de
  aanmelder komt overeen met een [extern contact](external-contacts.md)
  dat de rodevlag-tag van uw vereniging draagt. Beweeg de muis over de
  badge om te zien welk contact en welke gegevens overeenkomen. Zolang
  de module Externe contacten uit staat, zijn er geen rode vlaggen.

### Geselecteerde aanmelders schrijven {#writing-to-selected-applicants}

Zolang de module **Mededelingen** aan staat, zien bestuursleden en
beheerders een vinkje op elke rij.

| Knop | Wat het doet |
|---|---|
| **Alles selecteren** | Vinkt elke aanmelder aan die het huidige filter en de zoekopdracht tonen. |
| **Niets selecteren** | Wist alle vinkjes. |
| ***N* geselecteerd** | Telt de aangevinkte aanmelders. |
| **Schrijf naar de geselecteerde aanvragers** | Start een nieuwe [mededeling](announcements.md) aan de aangevinkte aanmelders. Ze gaat alleen per e-mail uit, één keer per adres -- wie zich twee keer heeft aangemeld, krijgt één e-mail. Uitgeschakeld tot u iemand aanvinkt. |

### Een aanmelder met de hand toevoegen {#adding-an-applicant-by-hand}

**Aanmelder toevoegen** (rechtsboven, vraagt schrijfrecht) opent het
formulier [Nieuwe aanmelder](#new-applicant).

## Nieuwe aanmelder {#new-applicant}

![Formulier nieuwe aanmelder](../assets/screenshots/applicants/form-new.png)

Voor aanmeldingen die niet via de website binnenkwamen -- telefonisch,
per brief, of van een oude papieren wachtlijst. Aanmeldingen via het
websiteformulier verschijnen vanzelf in de lijst.

| Veld | Wat het doet |
|---|---|
| **E-mailadres** \* | Verplicht -- het enige verplichte veld. Moet een geldig e-mailadres zijn, anders „Vul een geldig e-mailadres in.“ |
| **Voornaam** / **Achternaam** | Hier optioneel, maar nodig voordat u een perceel kunt toewijzen. |
| **Telefoon** | |
| **Aangemeld op** | De aanmeldingsdatum. „Leeg laten voor vandaag. Pas aan om een oudere aanmelding in te voeren, bijv. van een papieren wachtlijst -- die bepaalt de volgorde.“ Een datum in de toekomst wordt geweigerd. |
| **Bericht van de aanmelder** | Wat de aanmelder schreef of vertelde. |
| **Notitie van het bestuur** | „Intern -- wordt nooit aan de aanmelder getoond.“ |

Klik op **Opslaan**. De aanmelding begint met status **Nieuw**, de bron
is **Handmatig ingevoerd** (met uw naam), en er is geen datum van
privacytoestemming -- die wordt alleen vastgelegd voor aanmeldingen via
de website. **Terug** brengt u zonder opslaan terug naar de lijst.

## Aanmeldingspagina {#application-page}

![Aanmeldingspagina](../assets/screenshots/applicants/detail.png)

Klik op een aanmelder in de lijst om de aanmelding te openen.

Komt de aanmelder overeen met een extern contact met een rode vlag, dan
noemt een rood vak **Rode vlag** bovenaan het contact en de
overeenkomende gegevens (naam, e-mail, telefoon). Gebruikers die externe
contacten mogen zien, kunnen doorklikken naar het contact.

### Aanmelding {#application}

De linkerkaart bevat alles wat u kunt bewerken.

| Veld | Wat het doet |
|---|---|
| **Status** | Zie [Statussen](#statuses). Elke wijziging wordt vastgelegd in de **Statusgeschiedenis**. |
| **E-mailadres** \*, **Voornaam**, **Achternaam**, **Telefoon** | De contactgegevens van de aanmelder. |
| **Aangemeld op** | De aanmeldingsdatum. Wijzig haar om een aanmelding op de juiste plaats in de wachtrij te zetten, bijv. bij het invoeren van een oude papieren aanmelding. Een wijziging wordt in de statusgeschiedenis vastgelegd, omdat ze de aanmelder omhoog of omlaag schuift. Datums in de toekomst worden geweigerd. |
| **Bericht van de aanmelder** | De tekst die de aanmelder stuurde. |
| **Notitie van het bestuur** | Interne notities, nooit aan de aanmelder getoond -- bijv. „gebeld op 3 mei, wil liever een kleine tuin“. |

Klik op **Opslaan** om uw wijzigingen te bewaren. Zonder schrijfrecht
ziet u de gegevens, maar kunt u niet opslaan. Wijzigingen aan
contactgegevens en de notitie van het bestuur worden niet in de
geschiedenis vastgelegd.

### Knoppen bovenaan {#buttons-at-the-top}

| Knop | Wat het doet |
|---|---|
| **Terug** | Terug naar de lijst met aanmelders. |
| **Verwijderen** | Verwijdert de aanmelding definitief na bevestiging van „Deze aanmelder definitief verwijderen? Dit kan niet ongedaan worden gemaakt.“ De statusgeschiedenis gaat mee. Vraagt verwijderrecht. |

!!! info "Waarom aanmelders definitief verwijderd kunnen worden"
    Bijna al het andere in Parcella houdt zijn geschiedenis bij.
    Aanmelders zijn de uitzondering: hun gegevens worden alleen voor de
    aanmelding bewaard, dus u moet ze volledig kunnen verwijderen --
    als iemand daarom vraagt, of zodra de aanmelding voorbij is. Uw
    vereniging kan oude aanmeldingen ook automatisch laten verwijderen;
    zie [Automatisch verwijderen](#automatic-deletion).

### Aanvrager contacteren {#contact-applicant}

Alleen zichtbaar bij een aanmelding met status **Nieuw**, voor gebruikers
met schrijfrecht. Het is de eerste stap van de werkwijze: een
bedankmail die bevestigt dat de aanmelder op de wachtlijst staat.

| Veld / knop | Wat het doet |
|---|---|
| **Aan:** | Het e-mailadres van de aanmelder. |
| **Onderwerp:** | „Bedankt voor je aanmelding op onze wachtlijst!“ (in de taal waarin u Parcella gebruikt). |
| Bericht | De tekst van de e-mail, klaar om te bewerken. De naam van de aanmelder en van de vereniging zijn al ingevuld. |
| **Verzenden** | Stuurt na bevestiging de tekst per e-mail naar de aanmelder en zet de status op **Gecontacteerd**. |

Na het verzenden zegt een groene melding „De e-mail is verzonden en de
status op "Gecontacteerd" gezet.“ Het vak verdwijnt dan, omdat de
aanmelding niet meer nieuw is.

Kan de e-mail niet worden verzonden, dan verandert er niets: de status
blijft **Nieuw**, uw bewerkte tekst blijft in het vak staan, en u ziet
„De e-mail kon niet worden verzonden -- controleer de SMTP-instellingen.
De status is niet gewijzigd.“ Herstel de mailinstellingen en probeer het
opnieuw.

De begintekst komt uit **Tekst van de e-mail aan nieuwe aanvragers**
onder [Verenigingsinstellingen](../administration/settings.md) →
**Aanmelders**. Is die leeg, dan gebruikt Parcella zijn ingebouwde tekst
in de taal waarin u Parcella gebruikt. Aanmelders hebben geen eigen
taalinstelling; schrijft uw vereniging een eigen tekst, schrijf hem dan
in de taal die uw aanmelders spreken.

!!! note
    Parcella bewaart geen kopie van de e-mail. Alleen de
    statuswijziging naar **Gecontacteerd** laat zien dat hij is
    verstuurd.

### Perceel toewijzen {#assign-a-parcel}

Alleen zichtbaar bij een open aanmelding, voor gebruikers met
schrijfrecht op zowel **Aanmelders** als **Leden en percelen**.
**Perceel toewijzen** draagt een beëindigd perceel over aan de
aanmelder -- zie [Perceel toewijzen](#assign-a-parcel_1) hieronder.

### Details {#details}

| Regel | Wat ze toont |
|---|---|
| **Aangemeld op** | De aanmeldingsdatum. |
| **Bron** | **Websiteformulier**, of **Handmatig ingevoerd** met de naam van de gebruiker die haar invoerde. |
| **Privacytoestemming (aanmelder)** | Wanneer de aanmelder het privacyvakje op het websiteformulier aanvinkte. Leeg bij handmatig ingevoerde aanmeldingen. Dit is de toestemming van de aanmelder -- geen goedkeuring door het bestuur. |
| **Status gewijzigd** | Wanneer de status voor het laatst veranderde. |

Alle datums worden zonder tijdstip getoond.

### Andere aanmeldingen van dit adres {#other-applications-from-this-address}

Alleen zichtbaar als hetzelfde e-mailadres zich meer dan eens heeft
aangemeld. Toont de andere aanmeldingen met datum en status; klik op een
datum om er een te openen.

### Processen {#processes}

Staat de module [Processen](processes.md) aan en mag u processen zien,
dan toont een kaart **Processen** de processen over deze aanmelder.
**Proces starten** start er een nieuw.

### Statusgeschiedenis {#status-history}

Elke statuswijziging en elke wijziging van de aanmeldingsdatum, met
datum, tijd en de gebruiker die haar maakte -- de nieuwste eerst.
Wijzigingen door Parcella zelf (een overdracht) staan hier ook.

## Perceel toewijzen {#assign-a-parcel_1}

![Perceel toewijzen](../assets/screenshots/applicants/assign-parcel.png)

Komt er een perceel vrij, dan draagt deze pagina het in één stap over
aan een of meer aanmelders. Open haar met **Perceel toewijzen** op een
aanmelding.

!!! info "Voordat u begint"
    - Het perceel moet de status **beëindigd** hebben. Stel die eerst in
      in het [perceelformulier](parcels.md#new-parcel-and-edit-parcel).
      Is er geen beëindigd perceel, dan zegt de pagina dat.
    - Elke aanmelder die het perceel overneemt, heeft een voor- en
      achternaam in de aanmelding nodig.

### Stap 1: perceel en overdrachtsdatum {#step-1-parcel-and-handover-date}

| Veld | Wat het doet |
|---|---|
| **Beëindigd perceel** | Het over te dragen perceel. Alleen beëindigde percelen worden aangeboden, elk met de namen van de huidige huurders. |
| **Overdrachtsdatum** | De dag waarop de nieuwe huurders overnemen. Standaard vandaag. Mag in de toekomst liggen: de oude huurders blijven dan tot die dag huurder, lid en factuurontvanger, en de nieuwe huurders staan op de perceelpagina als toekomstig. |
| **Verdere kandidaten (medepachters)** | Optioneel: andere open aanmelders die het perceel samen met deze overnemen, bijv. een stel dat zich apart heeft aangemeld. |
| **Documentenmap voor de nieuwe pachters** | Alleen voor bestuursleden en beheerders zolang de module **Cloudopslag** aan staat. De map die op de overdrachtsdatum de documentenmap van het perceel wordt. Met **Cloudopslag doorbladeren** klikt u door uw opslag en kiest u **Deze map gebruiken**. Maak en deel de map zelf in uw cloudopslag. Optioneel -- u kunt haar ook later op de perceelpagina instellen. |
| **Voorbeeld** | Toont wat er gaat gebeuren. Er wordt nog niets gewijzigd. |

### Stap 2: het voorbeeld controleren {#step-2-check-the-preview}

De voorbeeldkaart, **Overdracht van perceel *X* op *datum***, toont
precies wat er gaat gebeuren:

- **Huidige pachters** -- de huur van elke huidige huurder eindigt op de
  overdrachtsdatum. Huurt hij geen ander perceel, dan eindigt zijn
  lidmaatschap de dag ervoor („lidmaatschap eindigt na *datum*“). Huurt
  hij nog een ander perceel, dan blijft hij lid; het voorbeeld noemt dat
  perceel.
- **Nieuwe pachters en factuurontvangers** -- elke aanmelder „wordt
  nieuw lid“ (naam, e-mail en telefoon uit de aanmelding) of wordt,
  als een actief lid al het e-mailadres van de aanmelder heeft, aan dat
  lid gekoppeld („al lid“).
- **Documentenmap** -- welke map op de overdrachtsdatum buiten gebruik
  gaat en welke overneemt. Kunt u zelf geen mappen beheren, dan zegt
  een notitie dat iemand met volledige toegang de nieuwe map later
  instelt.

Klopt er iets niet -- het perceel is niet beëindigd, de aanmelding van
een aanmelder is al afgesloten of heeft geen naam --, dan legt een
foutmelding het uit en gebeurt er niets.

Klik op **Perceel overdragen** en bevestig. Parcella doet dan in één
keer:

1. beëindigt de oude huren op de overdrachtsdatum (ze blijven als
   voormalige huurders in de geschiedenis van het perceel),
2. beëindigt het lidmaatschap van oude huurders die geen ander perceel
   huren,
3. maakt de nieuwe leden aan -- hun **Lid sinds** is de
   overdrachtsdatum -- en maakt hen huurder en factuurontvanger van het
   perceel,
4. zet het perceel terug op **actief**,
5. zet de aanmeldingen op **Afgesloten (tuin toegewezen)**.

Daarna komt u op de perceelpagina.


!!! tip "Het nieuwe lid daarna aanvullen"
    Alleen naam, e-mailadres en telefoonnummer worden uit de aanmelding
    overgenomen. Open het nieuwe lid en vul adres en IBAN aan. **Mag
    informatie per e-mail ontvangen** is aangevinkt, zoals bij elk nieuw
    lid; vink het uit als het lid alleen papier wil.

## Aanmeldingen via uw website {#applications-from-your-website}

De meeste aanmeldingen komen via een formulier op de website van uw
vereniging. Is het ingericht, dan verschijnt elk ingestuurd formulier in
de lijst als aanmelding met status **Nieuw**, bron **Websiteformulier**
en de datum waarop de aanmelder privacytoestemming gaf.

Wat het formulier vraagt: e-mailadres (verplicht), voor- en achternaam,
telefoon, een bericht en een vakje voor privacytoestemming dat
aangevinkt moet zijn. Parcella beschermt het formulier tegen spam:
verborgen velden die alleen bots invullen, een optionele captcha, en een
limiet van een paar inzendingen per uur van dezelfde bezoeker.

Zo richt u het in:

1. Schakel de module **Openbare aanmeldformulier-API** in onder
   [Modules in- en uitschakelen](../administration/modules.md).
2. Vul onder [Integraties](../administration/integrations.md) het adres
   van uw website in, zodat Parcella formulieren ervan accepteert. De
   pagina toont ook de adressen waarnaar het formulier verstuurt.
3. Zet het formulier op uw website:
    - **WordPress**: installeer de plug-in Parcella Connector en plaats
      de shortcode `[parcella_applicant_form]` op een pagina.
    - **Elke andere website**: een gewoon HTML-formulier dat de velden
      hierboven naar Parcella stuurt. Uw webbouwer vindt de details
      onder Integraties.

Wat aanmelders zien, staat in [Voor tuinders](../gardeners/index.md).

!!! note
    Parcella stuurt de aanmelder geen automatische bevestiging. Gebruik
    [Aanvrager contacteren](#contact-applicant) voor het eerste
    antwoord.

## Automatisch verwijderen {#automatic-deletion}

Onder [Verenigingsinstellingen](../administration/settings.md) →
**Aanmelders** laat **Aanmeldingen verwijderen na (maanden)** Parcella
oude aanmeldingen voor u verwijderen. Elke aanmelding waarvan de status
zoveel maanden niet is veranderd, wordt definitief verwijderd -- **wat
de status ook is**, en zonder iemand te waarschuwen. De maanden tellen
vanaf de laatste statuswijziging, of vanaf de aanmeldingsdatum als de
status nooit is veranderd.

Laat het veld leeg of op 0 (de standaard) om aanmeldingen te bewaren tot
u ze met de hand verwijdert. De controle draait op de achtergrond terwijl
mensen Parcella gebruiken, hooguit eens per uur.

!!! warning
    Automatisch verwijderen haalt ook open aanmeldingen weg die gewoon
    lang hebben gewacht. Is uw wachtlijst lang, kies dan een periode die
    langer is dan de gebruikelijke wachttijd, of zet de status van lang
    wachtende aanmelders af en toe verder.

## Gerelateerd {#related}

- [Percelen](parcels.md) -- een perceel beëindigen vóór een overdracht
- [Leden](members.md) -- de gegevens van het nieuwe lid aanvullen
- [Een perceel overdragen](../guides/parcel-handover.md)
- [Mededelingen](announcements.md) -- geselecteerde aanmelders schrijven
- [Externe contacten](external-contacts.md) -- de rodevlag-tag
- [Integraties](../administration/integrations.md) -- het websiteformulier

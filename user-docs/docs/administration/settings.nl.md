# Verenigingsinstellingen {#club-settings}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De instellingenpagina bevat de stamgegevens van uw vereniging en de
schakelaars die voor de hele installatie gelden: taal, logo, mailserver,
financiële gegevens en meer.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Open **Administratie → Instellingen**.

![Verenigingsinstellingen](../assets/screenshots/administration/settings.png)

## Hoe de pagina werkt {#how-the-page-works}

De pagina is een kolom met kaarten. Elke kaart is dichtgeklapt; klik op
de kop om haar te openen. Een kaart openen klapt de andere in.

| Element | Wat het doet |
|---|---|
| **Instellingen zoeken...** | Typ een woord, bijvoorbeeld „logo“ of „IBAN“. Kaarten die het bevatten, gaan open en het woord wordt gemarkeerd; alle andere kaarten worden verborgen. Past er niets, dan ziet u **Geen instellingen komen overeen met uw zoekopdracht.** |
| **Instellingen opslaan** | Bovenaan en onderaan de pagina. Slaat **alle kaarten tegelijk** op, welke u ook hebt gewijzigd. U ziet **Instellingen opgeslagen.** |

!!! warning "Eén opslagknop voor alles"
    Wijzigingen worden pas bewaard als u op **Instellingen opslaan**
    klikt. Verlaat u eerst de pagina, dan gaan ze verloren.

De kaarten, van boven naar beneden:

## Taal {#language}

De taal van de hele installatie: menu's, knoppen, meldingen, de
inlogpagina, en de e-mails en PDF's die Parcella maakt. Iedereen ziet
dezelfde taal; er is geen persoonlijke taalinstelling.

Kies tussen **Deutsch**, **English**, **Polski**, **Čeština**,
**Slovenčina**, **Français** en **Nederlands**. Een nieuwe installatie
begint in het Engels.

Waar een tekst nog niet in de gekozen taal is vertaald, toont Parcella in
plaats daarvan de Engelse tekst.

De taal verandert niets aan hoe getallen, datums en geld eruitzien --
dat is de kaart **Regio & valuta**.

## Huisstijl {#branding}

| Veld | Wat het doet |
|---|---|
| **Verenigingslogo** | Toont uw huidige logo (of het Parcella-pictogram). Kies een nieuw bestand -- PNG, JPEG, WebP of SVG, maximaal 2 MB -- om het te vervangen. Het logo verschijnt op de inlogpagina, bovenaan de zijbalk en in de kop van gegenereerde PDF's. |
| **Logo verwijderen (terug naar het standaardicoon)** | Alleen getoond als er een logo is geüpload. Vink aan en sla op om terug te gaan naar het Parcella-pictogram. |

Een verkeerd bestandstype of een te groot bestand wordt met een melding
geweigerd; de rest van de pagina wordt toch opgeslagen.

## Regio & valuta {#region-currency}

| Veld | Wat het doet |
|---|---|
| **Regio** | Hoe getallen en adressen worden geschreven -- duizendtalscheidingsteken, decimale komma of punt, of de postcode vóór of na de plaats komt. Bepaalt ook de tijdzone voor agendafeeds. Keuzes (altijd in het Engels getoond): Germany, United Kingdom, France, Netherlands, Poland, Czech Republic, Slovakia. Standaard: Germany. |
| **Valuta** | Het valutasymbool en waar het staat („19,99 €“ of „£19.99“). Keuzes: Euro (€), British Pound (£), Polish Złoty (zł), Czech Koruna (Kč). Standaard: Euro. |

Beide staan los van de taal: een Nederlandstalige vereniging kan
Nederlandse menu's met eurobedragen gebruiken, een Engelstalige
installatie kan Duitse getalnotatie gebruiken.

## Functiegebieden {#feature-areas}

De schakelaars die modules in- en uitschakelen. Uitgebreid beschreven in
[Modules in- en uitschakelen](modules.md).

## Navigatievolgorde {#navigation-order}

Bepaalt de volgorde van de items in ieders zijbalk. Elk item heeft een
getalveld: **Dashboard**, **Leden**, **Perceel**, **Ondersteuning**,
**Aankoopaanvragen**, **Werksessies**, **Water**, **Elektriciteit**,
**Verzekering**, **Kalender**, **Mededelingen**, **Inventaris**,
**Takenbord**, **Financiën**, **Aanmelders**, **Externe contacten**,
**Rapportages**, **Notities**, **Processen**.

Lagere getallen komen eerst. Standaard zijn de getallen 100, 200, 300
... in de volgorde hierboven, zodat u een item tussen twee andere kunt
zetten door het bijvoorbeeld 150 te geven. Lege velden vallen terug op
het standaardgetal; alles wat geen geheel getal is, wordt genegeerd.

**Administratie** staat niet in de lijst: die staat altijd als laatste.

## Updates {#updates}

| Veld | Wat het doet |
|---|---|
| **Automatisch op updates controleren** | Standaard aan. Parcella vraagt GitHub dan om de paar uur of er een nieuwere versie is uitgebracht, en toont een melding op de pagina [Systeem](system.md). Er wordt niets over uw vereniging verstuurd. Zet het uit als uw server geen contact met internet mag maken; de pagina Systeem toont dan helemaal geen update-informatie. |

## Aanmelders {#applicants}

Alleen van belang als u de module [Aanmelders](../modules/applicants.md)
gebruikt.

| Veld | Wat het doet |
|---|---|
| **Aanmeldingen verwijderen na (maanden)** | Elke aanmelding waarvan de status zoveel maanden niet is veranderd, wordt **definitief verwijderd**, wat de status ook is, zonder iemand te waarschuwen. Geteld vanaf de laatste statuswijziging, of vanaf de aanmeldingsdatum als de status nooit is veranderd. Laat leeg of vul 0 in om aanmeldingen te bewaren tot u ze met de hand verwijdert. Nuttig voor gegevensbescherming. |
| **Tekst van de e-mail aan nieuwe aanvragers** | De tekst die **Aanvrager contacteren** bij een nieuwe aanmelding gebruikt; vóór elke verzending kan hij nog worden gewijzigd. `{name}` wordt de naam van de aanmelder, `{club}` de naam van de vereniging. Laat leeg om de ingebouwde tekst te gebruiken, die grijs wordt getoond. |

## E-maillogboek {#email-log}

| Veld | Wat het doet |
|---|---|
| **E-maillogboek bewaren (dagen)** | Hoe lang het [E-maillogboek](email-log.md) zijn regels bewaart. Oudere worden automatisch verwijderd, omdat adressen van ontvangers persoonsgegevens zijn. Standaard 90 dagen, mogelijk 1 tot 3650. |

## Verenigingsgegevens {#club-data}

| Veld | Gebruikt voor |
|---|---|
| **Verenigingsnaam** | Getoond bovenaan de zijbalk, op de inlogpagina en op afgedrukte documenten. Leeg: „Parcella“. |
| **Straat**, **Postcode**, **Plaats** | Het adres van de vereniging in de voettekst van gegenereerde PDF's (facturen, mededelingen, lijsten). |
| **Verenigingsregistratienummer**, **Kamer van Koophandel** | Ook in de voettekst van PDF's afgedrukt, zoals in Duitsland geregistreerde verenigingen die moeten vermelden. |

## Bestuursleden {#board-members}

Welke leden nu in het bestuur zitten. Hun namen worden in de voettekst
van gegenereerde documenten afgedrukt.

| Element | Wat het doet |
|---|---|
| **Bestuursleden** / **Lijst tonen** | Klapt de lijst met alle huidige leden uit, elk met een vinkje. **Lijst verbergen** klapt haar weer in. |
| **Zoeken…** | Beperkt de lijst tot passende namen. **Geen resultaten** als niets past. |
| **Alles selecteren** / **Niets selecteren** | Vinkt elk zichtbaar lid aan of uit. |

Een lid dat de vereniging verlaat, valt vanzelf van de afgedrukte lijst.

## Oppervlakten (m²) {#areas-sqm}

Het terrein van de vereniging, verdeeld zoals Duitse volkstuinverenigingen
het meestal rapporteren.

| Veld | Wat het doet |
|---|---|
| **Totale oppervlakte (m²)** | Het hele terrein van de vereniging. Vul het zelf in. |
| **Oppervlakte A (percelen, m²)** | Berekend, niet te bewerken: de som van de oppervlakten van alle percelen, verhuurd of beëindigd. Verwijderde percelen en gemeenschappelijke delen tellen niet mee. Hetzelfde getal als **Totale oppervlakte (m²)** op het [Dashboard](../getting-started/dashboard.md). |
| **Oppervlakte B (gemeenschappelijk, m²)** | Berekend: totale oppervlakte min oppervlakte A min oppervlakte C. |
| **Oppervlakte C (gemeentelijk, m²)** | Vul het zelf in. |

Deze cijfers worden gebruikt wanneer een
[factuurronde](../modules/finances/invoice-runs.md) kosten verdeelt naar
het aandeel van elk perceel in de gemeenschappelijke oppervlakte.

## Financiële instellingen {#finance-settings}

Gebruikt door de module [Financiën](../modules/finances/index.md).

| Veld | Wat het doet |
|---|---|
| **Naam van de bank**, **IBAN**, **BIC**, **Rekeninghouder** | Afgedrukt in de voettekst van elke factuur, zodat leden weten waar ze moeten betalen. |
| **Volgend factuurnummer (overschrijven)** | Meestal leeg: de nummers lopen gewoon door. Vul een nummer in om de allereerstvolgende factuurronde -- in welk jaar ook -- daar te laten beginnen. Parcella controleert pas bij het afronden van die ronde of het nummer al bezet is. Het veld maakt zichzelf leeg na gebruik. |
| **Factuurnummerformaat** | Hoe factuurnummers eruitzien. `{number}` is verplicht, `{year}` optioneel; alle andere tekst wordt gebruikt zoals geschreven, bijv. `R-{year}-{number}`. Onder het veld ziet u **Momenteel gebruikt:** met een voorbeeld; **(standaard, niets aangepasts opgeslagen)** betekent dat de standaard `{year}/{number}` geldt. Het veld stelt een paar voorbeelden voor. |

Het formaat geldt alleen voor facturen die vanaf nu worden aangemaakt.
Al uitgegeven nummers veranderen nooit. Een ongeldig formaat wordt niet
opgeslagen; u ziet **Ongeldig factuurnummerformaat -- het moet {number}
precies één keer bevatten (optioneel ook {year}), geen andere
plaatshouders.**

## E-mail (SMTP) {#email-smtp}

Elke e-mail die Parcella verstuurt -- uitnodigingen, meldingen,
mededelingen, facturen -- gaat via deze mailserver de deur uit. Parcella
leest geen enkele mailbox.

| Veld | Wat het doet |
|---|---|
| **SMTP-server** | Het adres van de mailserver, van uw e-mailprovider. |
| **SMTP-poort** | Meestal 587 (of wat uw provider zegt). |
| **SMTP-gebruiker** | De login voor de mailserver, vaak het e-mailadres. |
| **SMTP-wachtwoord** | Getoond als **Nog niet ingesteld** of **•••••••• (ingesteld -- opnieuw invoeren om te wijzigen)**. Laat leeg om het opgeslagen wachtwoord te houden; typ een nieuw om het te vervangen. Versleuteld opgeslagen. |
| **Afzender e-mail** | Het adres waarvan e-mails afkomstig zijn. |

!!! tip "Controleer of het werkt"
    Nodig na het opslaan uzelf uit met een tweede adres of verstuur een
    willekeurige e-mail, en kijk dan in het
    [E-maillogboek](email-log.md). **Mislukt** met een fout vertelt u
    waar de mailserver niet blij mee was.

Zijn deze velden leeg, dan gebruikt Parcella de mailinstellingen die de
persoon die het installeerde eventueel in de serverconfiguratie heeft
gezet.

Parcella versleutelt de verbinding met de mailserver met STARTTLS, de
methode die normaal op poort 587 wordt gebruikt. Daar is op de
instellingenpagina geen schakelaar voor; het kan alleen in de
serverconfiguratie worden gewijzigd.
<!-- TODO(verify): whether mail servers that only offer implicit TLS on port 465 work at all. -->

## Gerelateerd {#related}

- [Modules in- en uitschakelen](modules.md)
- [Integraties](integrations.md)
- [Een nieuwe vereniging inrichten](../guides/new-club-setup.md)

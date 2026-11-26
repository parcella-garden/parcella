# Dashboard {#dashboard}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Het dashboard is de startpagina die u na het inloggen ziet. Het toont de
belangrijkste cijfers van de vereniging in één oogopslag en wijst u op
zaken die aandacht vragen. Klik op **Dashboard** bovenaan de zijbalk om
ernaar terug te gaan.

!!! info "Wie kan dit gebruiken"
    Iedereen die is ingelogd. Sommige tegels verschijnen alleen als hun
    module is ingeschakeld, en een paar vragen ook leesrecht voor die
    module (zie hieronder).

![Dashboard](../assets/screenshots/getting-started/dashboard.png)

Alle cijfers worden telkens opnieuw berekend wanneer u de pagina opent.

## De tegels {#the-tiles}

De tegels bovenaan staan in een vaste volgorde. De eerste vier worden
altijd getoond; de andere verschijnen afhankelijk van de modules van uw
vereniging.

| Tegel | Wat hij telt | Wanneer hij verschijnt | Knop |
|---|---|---|---|
| **Leden** | Groot getal: huidige leden -- niet verwijderd, lidmaatschap niet beëindigd, en al begonnen of zonder datum **lid sinds**. Daaronder: **... actief** -- de leden daarvan die een datum **lid sinds** hebben. Als van minstens één huidig lid een geboortedatum bekend is: **Gemiddelde leeftijd ... jaar**, alleen berekend over die leden. | Altijd | **Toon** opent de ledenlijst, gefilterd op actieve leden. |
| **Actieve percelen** | Percelen met de status *actief*. Daaronder, in oranje: **... onbewoond** -- actieve percelen zonder huidige of komende huurder (een perceel waarvan de laatste huur is geëindigd, telt als onbewoond; een perceel waarvan de huurder heeft opgezegd of waarvan de nieuwe huurder later begint, niet); of **allemaal bewoond** als er geen zijn. | Altijd | **Toon alles** opent de perceellijst. |
| **Beëindigd** | Percelen met de status *beëindigd*. | Altijd | **Toon** opent de perceellijst, gefilterd op beëindigde percelen. |
| **Totale oppervlakte (m²)** | De som van de oppervlakte van alle percelen, actief en beëindigd. Verwijderde percelen en gemeenschappelijke delen tellen niet mee. Dit is hetzelfde getal als **Oppervlakte A** in de [verenigingsinstellingen](../administration/settings.md#areas-sqm). | Altijd | -- |
| **Openstaande aankoopverzoeken** | Aanvragen die nog **wacht op goedkeuring** zijn. | Module **Aankoopaanvragen** aan en u mag aankoopaanvragen lezen | **Toon alles** |
| **Nieuwe aanmeldingen** | Aanmeldingen met de status *nieuw*, dus **nog niet bekeken**. | Module **Aanmelders** aan en u mag aanmelders lezen | **Toon alles** opent de lijst met aanmelders, gefilterd op nieuwe. |
| **Open processen** | Processen die **lopend** zijn. | Module **Processen** aan en u mag processen lezen | **Toon alles** opent de open processen. |
| **Open supportgesprekken** | **Actieve of wachtende gesprekken in de helpdesk** van de vereniging. | Module **Support (helpdesk)** aan en u mag haar lezen | **Toon alles** |
| **Achterstallige taken** | Taken op het takenbord waarvan de vervaldatum is verstreken en die niet klaar zijn. | Module **Takenbord** aan en u hebt volledige toegang (het takenbord is alleen voor gebruikers met volledige toegang) | **Toon alles** opent het takenbord met alleen de achterstallige taken. |
| **Nieuwe aanmeldingen** | Aanmeldingen **voor werksessies** van de laatste 14 dagen, voor gewone sessies die nog niet hebben plaatsgevonden. Aanmeldingen voor een sessie die iemand als bekeken heeft gemarkeerd, tellen niet meer. | Module **Werktijdenbeheer** aan en u mag werkuren lezen | **Toon alles** opent **Sessies & Overzicht**. |

De getallen op **Openstaande aankoopverzoeken**, **Nieuwe aanmeldingen**,
**Open supportgesprekken**, **Achterstallige taken** en **Nieuwe
aanmeldingen** (werksessies) zijn dezelfde als de rode badges in de
zijbalk (zie [Uw weg vinden](navigation.md#badges-things-that-need-attention)).
Net als de badges dalen ze vanzelf zodra iets is afgehandeld.

## Verjaardagen deze week {#birthdays-this-week}

Deze kaart verschijnt alleen als minstens één huidig lid in de komende
zeven dagen jarig is, vandaag inbegrepen. Ze toont die leden, de
eerstvolgende bovenaan:

- de naam van het lid, met een link naar de pagina van het lid,
- **vandaag wordt ...** bij een verjaardag vandaag, anders de datum en
  **wordt ...**,
- een gemarkeerde badge **Rond** bij ronde verjaardagen (30, 40, 50, ...).

Leden zonder bekende geboortedatum worden niet getoond. De kaart wordt
ook getoond als de module **Kalender** uit staat; de knop **Toon alles**
leidt naar de volledige verjaardagenlijst in de kalender, waarvoor de
kalendermodule en het bijbehorende recht nodig zijn.

## Recente leden {#recent-members}

De vijf huidige leden die het laatst **in Parcella zijn ingevoerd**, met
rechts hun datum **lid sinds** (– als die niet is ingesteld). Klik op een
naam om het lid te openen. Op een nieuwe installatie verschijnt **Nog
geen leden aangemaakt.**

**Nieuw lid** opent het formulier voor een nieuw lid.

## Snelkoppelingen {#quick-access}

Snelkoppelingen voor veelvoorkomende taken:

| Knop | Wat het doet |
|---|---|
| **Nieuw lid aanmaken** | Opent het formulier voor een nieuw lid. |
| **Nieuw perceel aanmaken** | Opent het formulier voor een nieuw perceel. |
| **Leden exporteren als CSV** | Downloadt de ledenlijst als CSV-bestand, bijvoorbeeld voor een spreadsheet. |
| **Percelen exporteren als CSV** | Downloadt de perceellijst als CSV-bestand. |

Leden en percelen aanmaken vraagt **Schrijven** op **Leden en
percelen**. Zonder dat recht antwoordt het formulier met **U heeft hier
geen toestemming voor**.

## Gerelateerd {#related}

- [Leden](../modules/members.md) en [Percelen](../modules/parcels.md)
- [Uw weg vinden](navigation.md)
- [Modules in- en uitschakelen](../administration/modules.md)

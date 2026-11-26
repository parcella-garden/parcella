# Takenbord {#task-board}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Een gedeeld takenbord voor de eigen zaken van het bestuur die niet aan
een werksessie vastzitten: „verzekeringspolis verlengen“, „elektricien
bellen“, „dakdekker nabellen“. Taken zijn kaarten in kolommen die u van
links naar rechts sleept naarmate het werk vordert.

!!! info "Wie kan dit gebruiken"
    - De moduleschakelaar is **Takenbord** onder **Administratie →
      Modules in- en uitschakelen**. Ze staat standaard **aan**.
    - Alleen de rollen **Bestuur** en **Beheerder**, en leden van een
      groep met **Volledige toegang tot elke module**, zien **Takenbord**
      in het menu. Er is geen groepsrecht om het voor andere gebruikers
      open te stellen, om te lezen of te schrijven.
    - Optioneel kunnen kaarten uit een bord in Nextcloud Deck worden
      overgenomen (moduleschakelaar **Nextcloud Deck-synchronisatie**,
      standaard uit). Zie [Kaarten uit Nextcloud Deck](#cards-from-nextcloud-deck).

!!! note "Niet hetzelfde als taken bij werksessies"
    De klussen die leden tijdens een werksessie doen („haag snoeien“)
    staan in de module [werkuren](work-hours.md) onder **Taken**. Het
    takenbord is voor de eigen takenlijst van het bestuur.

## Het bord {#the-board}

![Takenbord](../assets/screenshots/tasks/board.png)

Het bord toont alle lijsten (kolommen) naast elkaar; scrol opzij als er
meer zijn dan op het scherm passen. Nieuwe installaties beginnen met drie
lijsten: „To Do“, „In Progress“ en „Done“. U kunt lijsten naar wens
hernoemen, toevoegen, verplaatsen en verwijderen.

Het menu-item **Takenbord** toont een rood getal als er taken te laat
zijn. Het dashboard heeft een kaart **Achterstallige taken** met
hetzelfde getal; de knop **Toon alles** opent het bord met **Alleen
achterstallige** al aangevinkt.

### Knoppen bovenaan {#buttons-at-the-top}

| Knop | Wat het doet |
|---|---|
| **Lijst toevoegen** | Opent een klein venster om een lijst toe te voegen. Vul een **Naam** in (maximaal 100 tekens) en klik op **Toevoegen**. De nieuwe lijst komt helemaal rechts op het bord. |
| **Labels beheren** | Opent [Taaklabels](#task-tags). |
| **Rapport exporteren** | Opent [Activiteitenrapport exporteren](#export-activity-report). |
| **Nieuwe taak** | Opent het [taakvenster](#the-task-window) voor een nieuwe kaart. |

### Een lijst (kolom) {#a-list-column}

Elke kolomkop toont de naam van de lijst, een groen vinkpictogram als het
een [klaar-lijst](#done-lists) is, en het aantal kaarten erin.

| Actie | Wat het doet |
|---|---|
| De kop slepen | Verplaatst de hele lijst naar een nieuwe plek op het bord. |
| **⋮** → **Naam wijzigen** | Opent **Lijst hernoemen**; wijzig de **Naam** en klik op **Wijzigingen opslaan**. |
| **⋮** → **Markeren als klaar-lijst** / **Niet meer als klaar-lijst markeren** | Zet de klaar-lijstfunctie voor deze lijst aan of uit. Zie [Klaar-lijsten](#done-lists). |
| **⋮** → **Verwijderen** | Opent **Lijst verwijderen**. Niet mogelijk voor de laatste overgebleven lijst. |

Verwijdert u een lijst die nog kaarten heeft, dan zegt het venster **Deze
lijst bevat nog kaarten. Kies een andere lijst om ze naartoe te
verplaatsen voordat u verwijdert.** Kies het doel in **Verplaats de
kaarten naar** en klik op **Lijst verwijderen**. De kaarten worden
achteraan die lijst toegevoegd, in hun huidige volgorde -- er wordt nooit
een kaart samen met een lijst verwijderd. Een lege lijst vraagt **Lijst
"{naam}" verwijderen? Dit kan niet ongedaan worden gemaakt.**

### Een kaart {#a-card}

Elke kaart toont:

- de badge **prioriteit** (**Hoog**, **Gemiddeld** of **Laag**), als die
  is ingesteld;
- een wolkpictogram als de kaart uit Nextcloud Deck komt;
- de **titel** -- klik erop om het [taakvenster](#the-task-window) te
  openen;
- aan wie ze is toegewezen, en de **vervaldatum**. Een verstreken
  vervaldatum wordt rood getoond;
- **Klaar {datum}** in groen bij afgeronde kaarten, die ook vervaagd en
  doorgestreept worden getoond;
- haar **tags** als gekleurde labels.

Een lege lijst toont **Geen taken**.

**Sleep een kaart** naar een andere lijst, of omhoog en omlaag binnen een
lijst, om haar plaats te wijzigen. De volgorde wordt meteen opgeslagen.
Mislukt het opslaan, dan laadt de pagina opnieuw om de echte stand te
tonen.

!!! note "Wanneer slepen is uitgeschakeld"
    Zolang een zoekopdracht, een filter of een andere sortering dan
    **Handmatig (sleepvolgorde)** actief is, kunnen kaarten niet worden
    gesleept, omdat het bord dan niet elke kaart in haar echte volgorde
    toont. Klik op **Filters wissen** en zet de sortering terug op
    **Handmatig (sleepvolgorde)**. Hele lijsten verplaatsen werkt nog
    steeds.

### Zoeken, filters en sorteren {#search-filters-and-sort}

De balk boven het bord beperkt wat u ziet. Dat gebeurt meteen in uw
browser en verandert niets aan het bord zelf.

| Veld / knop | Wat het doet |
|---|---|
| Zoekveld | Doorzoekt titel, beschrijving, tags en reacties. |
| **Elke prioriteit** | Toont alleen kaarten met prioriteit **Hoog**, **Gemiddeld** of **Laag**. |
| **Elke tag** | Toont alleen kaarten met deze tag. Alleen tags die op het bord worden gebruikt, worden aangeboden. |
| **Elke eigenaar** | Toont alleen kaarten die aan deze persoon zijn toegewezen. Alleen mensen met kaarten worden aangeboden. |
| **Elke vervalmaand** | Toont alleen kaarten die in deze maand vervallen (bijv. „juli 2026“). Alleen maanden die voorkomen, worden aangeboden. |
| **Alleen achterstallige** | Toont alleen achterstallige kaarten: een vervaldatum in het verleden en niet klaar. |
| **Filters wissen** | Zet zoekopdracht en filters terug. |
| Sorteren (**Handmatig (sleepvolgorde)**, **Vervaldatum**, **Prioriteit**) | Ordent de kaarten binnen elke lijst om te bekijken: op vervalmaand, of Hoog → Gemiddeld → Laag met kaarten zonder prioriteit achteraan. **Handmatig (sleepvolgorde)** toont weer uw eigen volgorde. De sortering wordt nooit opgeslagen. |

Komt er niets overeen: **Geen taken komen overeen met je
zoekopdracht/filters.**

## Het taakvenster {#the-task-window}

![Taakvenster](../assets/screenshots/tasks/task-modal.png)

Klikken op **Nieuwe taak** of op de titel van een kaart opent een venster
boven het bord, met de kop **Nieuwe taak** of **Taak bewerken**. Elke
kaart heeft een eigen webadres, zodat u haar als bladwijzer kunt
bewaren of de link naar een ander bestuurslid kunt sturen. Het venster
sluiten (X, **Annuleren**, Esc of ernaast klikken) brengt u zonder
opslaan terug naar het bord.

| Veld / knop | Wat het doet |
|---|---|
| **Titel** | Verplicht. |
| **Omschrijving** | Optionele vrije tekst. |
| **Deadline** | Optioneel. Een kaart waarvan de vervaldatum voorbij is, telt als achterstallig tot ze klaar is. |
| **Prioriteit** | **Geen prioriteit** (standaard), **Laag**, **Gemiddeld** of **Hoog**. Prioriteit verandert de volgorde van de kaarten niet; ze toont alleen een badge en u kunt erop filteren en sorteren. |
| **Tags** | Vink een van de [taaklabels](#task-tags) van de vereniging aan. Bestaan er nog geen: **Nog geen labels aangemaakt.** met een link naar **Labels beheren**. U kunt hier geen nieuwe tags typen. |
| **Lijst** | In welke lijst de kaart staat. Een nieuwe kaart gaat naar de eerste lijst tenzij u een andere kiest; ze wordt achteraan toegevoegd. |
| **Klaar** | Markeert de kaart als klaar (met datum en tijd). Afgeronde taken worden nooit als achterstallig getoond. Een kaart naar een klaar-lijst verplaatsen markeert hem automatisch als klaar. Vink uit om haar te heropenen. |
| **Toegewezen aan** | Vink zoveel mensen aan als u wilt. Alleen actieve gebruikersaccounts worden getoond. |
| **Aanmaken** / **Wijzigingen opslaan** | Slaat de kaart op en brengt u terug naar het bord. |
| **Taak verwijderen** | Alleen bij bestaande kaarten. Verwijdert de kaart met haar reacties na **Deze taak verwijderen? Dit kan niet ongedaan worden gemaakt.** |

### Reacties {#comments}

Bestaande kaarten hebben een gedeelte **Reacties**: een doorlopend logboek
van notities voor wie de taak daarna oppakt. Elke reactie toont auteur
en tijd.

- Typ in **Nieuwe reactie** en klik op **Reactie toevoegen**.
- Onder elke reactie staat een kleine rode link **Reactie verwijderen**,
  die de reactie verwijdert na **Deze reactie verwijderen? Dit kan niet
  ongedaan worden gemaakt.** Elk bestuurslid kan elke reactie
  verwijderen. Reacties kunnen niet worden bewerkt.


### Wijzigingsgeschiedenis {#change-history}

Onder de reacties toont **Wijzigingsgeschiedenis** elke vastgelegde
wijziging, de nieuwste eerst: **Tijdstempel**, **Veld**, **Oude
waarde**, **Nieuwe waarde** en **Gewijzigd door**. Vastgelegd worden
wijzigingen van titel, beschrijving, vervaldatum, prioriteit, tags, lijst
(getoond met de naam van de lijst) en de markering klaar. Wijzigingen in
aan wie de kaart is toegewezen, worden niet vastgelegd. Zijn er nog
geen: **Nog geen wijzigingen geregistreerd.**

## Klaar-lijsten {#done-lists}

Een kaart is alleen „klaar“ als ze als klaar is gemarkeerd -- nooit
alleen omdat ze in een kolom met de naam „Done“ staat. Om een kaart bij
het verplaatsen naar een kolom als klaar te markeren, markeert u die
kolom als klaar-lijst:

1. Open het menu **⋮** van de lijst die u voor afgeronde taken gebruikt.
2. Kies **Markeren als klaar-lijst**. Naast de naam verschijnt een groen
   vinkje.

Vanaf dan:

- een kaart **naar** een klaar-lijst verplaatsen markeert haar als klaar
  (slepen, **Lijst** in het taakvenster wijzigen, of haar daar
  aanmaken);
- haar **eruit** naar een gewone lijst verplaatsen heropent haar;
- verplaatsen tussen twee gewone lijsten verandert niets;
- het vakje **Klaar** markeert of heropent een kaart in elke lijst.

Een lijst markeren markeert de kaarten die er al in staan als klaar. Een
markering weghalen laat de kaarten zoals ze zijn.

Zolang er geen lijst gemarkeerd is, toont het bord een blauwe melding
die dit uitlegt.

## Taaklabels {#task-tags}

![Taaklabels](../assets/screenshots/tasks/tags.png)

**Labels beheren** op het bord opent **Taaklabels**: de vaste lijst met
labels die kaarten kunnen dragen. Kaarten kunnen alleen de hier
aangemaakte labels dragen. **Terug naar het bord** brengt u terug naar
het bord.

| Veld / knop | Wat het doet |
|---|---|
| **Naam** + kleur + **Label toevoegen** | Maakt een label aan. De naam is verplicht, maximaal 100 tekens, en moet uniek zijn (hoofd-/kleine letters tellen niet). Kleuren: **Grijs** (standaard), **Rood**, **Oranje**, **Geel**, **Groen**, **Turkoois**, **Blauw**, **Paars**. |
| Naam en kleur van een bestaand label + vinkknop | Hernoemt het label of geeft het een andere kleur. De wijziging is meteen op elke kaart zichtbaar. |
| „{aantal} ta(a)k(en)“ | Hoeveel kaarten het label dragen. |
| Prullenbakknop | Verwijdert het label na **Label ‘{naam}’ verwijderen? Het wordt van alle taken verwijderd.** De kaarten blijven. |

Mogelijke fouten: **Een label heeft een naam nodig.**, **Er bestaat al
een label met deze naam.**, **Onbekende kleur.** Zonder labels: **Nog
geen labels.**

## Activiteitenrapport exporteren {#export-activity-report}

![Activiteitenrapport exporteren](../assets/screenshots/tasks/export.png)

**Rapport exporteren** downloadt een Markdown-tekstbestand over de
activiteit op het bord, bijvoorbeeld om de notulen van het bestuur of een
maandelijkse samenvatting op te stellen (ook met hulp van een
AI-assistent).

| Veld / knop | Wat het doet |
|---|---|
| **Van** | Begin van de periode. Standaard 30 dagen geleden. |
| **Tot** | Einde van de periode. Standaard vandaag. |
| **Downloaden** | Downloadt het rapport. |

Het rapport heeft drie delen: de kaarten die in de periode zijn
aangemaakt of gewijzigd, de reacties die in de periode zijn geschreven,
en een momentopname van elke kaart die nu op het bord staat (afgeronde
kaarten met hun klaardatum).

!!! warning "Wat „gewijzigd in de periode“ betekent"
    Een kaart telt als aangeraakt als ze in de periode is aangemaakt of
    bewerkt. Het rapport kan niet precies zeggen wanneer een kaart naar
    haar huidige lijst is verplaatst. Het bestand zegt dat zelf, zodat
    wie het leest geen tijdlijn verzint.

## Kaarten uit Nextcloud Deck {#cards-from-nextcloud-deck}

Plande uw vereniging vroeger in Nextcloud Deck, dan kan Parcella één
Deck-bord naar het takenbord kopiëren en bijhouden. Dit is een
eenrichtingsspiegel, bedoeld om u te helpen overstappen.

Ingericht door een beheerder: schakel **Nextcloud Deck-synchronisatie**
in onder **Modules in- en uitschakelen** en vul dan server, gebruiker,
app-wachtwoord en **Deck-bord-ID** in onder **Administratie →
Integraties → Nextcloud Deck** (zie
[Integraties](../administration/integrations.md)). Parcella controleert
Deck dan elke 15 minuten; **Nu synchroniseren** daar doet het meteen.

Wat u op het bord ziet:

- Elke Deck-kolom wordt een lijst met dezelfde naam (zo nodig
  aangemaakt).
- Gesynchroniseerde kaarten hebben een wolkpictogram (**Gesynchroniseerd
  vanuit Nextcloud Deck**).
- In het taakvenster zegt een grijze melding: **Deze kaart is
  gesynchroniseerd vanuit Nextcloud Deck -- titel, beschrijving,
  vervaldatum en lijst worden daar beheerd en automatisch bijgewerkt.
  Prioriteit, tags, toegewezenen en reacties bestaan alleen in Parcella
  en zijn altijd bewerkbaar.** Titel, beschrijving, vervaldatum en lijst
  kunnen in Parcella niet worden gewijzigd.
- **Overnemen in Parcella** verbreekt de koppeling: vanaf dan is de kaart
  een gewone Parcella-kaart, volledig bewerkbaar, en verandert Deck haar
  niet meer.
- Een kaart die in Deck wordt verwijderd of gearchiveerd, wordt in
  Parcella nooit verwijderd. Ze wordt gewoon niet meer gesynchroniseerd,
  alsof u haar had overgenomen.
- Gearchiveerde Deck-kaarten worden helemaal niet gekopieerd.

## Gerelateerd {#related}

- [Dashboard](../getting-started/dashboard.md) -- de kaart
  **Achterstallige taken**.
- [Werkuren](work-hours.md) -- taken voor werksessies.
- [Integraties](../administration/integrations.md) -- de koppeling met
  Nextcloud Deck.
- [Modules in- en uitschakelen](../administration/modules.md)

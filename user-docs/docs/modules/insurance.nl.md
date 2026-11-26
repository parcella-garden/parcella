# Verzekering {#insurance}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De verzekeringsmodule houdt bij welke percelen in een bepaald jaar de
collectieve verzekering van de vereniging hebben afgesloten -- een
pakket **opstalverzekering** en/of een **ongevallenverzekering** -- en
berekent wat elk perceel daarvoor verschuldigd is. Alles wordt per jaar
bewaard, zodat de cijfers van vorig jaar blijven zoals ze waren wanneer u
het nieuwe jaar inricht.

!!! info "Wie kan dit gebruiken"
    Bestuursleden en beheerders hebben altijd volledige toegang. Andere
    gebruikers hebben een groep nodig die rechten op **Verzekering**
    geeft (zie [Groepen](../administration/groups.md)):

    - **Lezen** -- het overzicht, de perceellijst, de verzekeringspagina
      van elk perceel, de configuratie en het jaarverslag zien, en de
      CSV-export downloaden.
    - **Schrijven** -- de verzekering van een perceel, de bedragen van de
      ongevallenverzekering en de pakketten wijzigen.
    - **Verwijderen** -- een pakket opstalverzekering verwijderen.

    De module wordt ingeschakeld met **Verzekeringsbeheer** onder
    [Modules in- en uitschakelen](../administration/modules.md). Ze staat
    standaard aan.

U vindt de module in de navigatie onder **Verzekering**, met de items
**Overzicht**, **Perceel**, **Configuratie** en **Evaluatie**.

## Hoe de kosten worden berekend {#how-the-cost-is-calculated}

De kosten van een perceel voor een jaar zijn de som van twee delen.

**Opstalverzekering:** heeft het perceel een opstalverzekering en is er
een pakket gekozen, dan betaalt het het bedrag van dat pakket.
Opstalverzekering aan maar geen pakket gekozen kost niets.

**Ongevallenverzekering:** heeft het perceel een ongevallenverzekering en
bestaat er voor dat jaar een configuratie, dan betaalt het:

- het **Basisbedrag per perceel** één keer, als minstens één persoon uit
  het huishouden van het perceel als gedekt is aangevinkt, plus
- het **Extra bedrag per extra persoon** voor elke aangevinkte persoon
  die *niet* tot het huishouden hoort.

Is niemand uit het huishouden aangevinkt, dan wordt het basisbedrag niet
in rekening gebracht, ook als er extra personen verzekerd zijn. Zonder
configuratie voor het jaar kost de ongevallenverzekering niets.

**Voorbeeld:** basisbedrag 3,00, extra bedrag 3,00. Een perceel met
pakket „Pakket 2“ (60,00), ongevallenverzekering voor het stel dat op
hetzelfde adres woont en één medehuurder die elders woont, betaalt
60,00 + 3,00 + 1 × 3,00 = **66,00**.

### Wie als huishouden telt {#who-counts-as-the-household}

Parcella kijkt naar de huidige huurders van het perceel -- mensen van wie
de huur actueel is en van wie het lidmaatschap niet is beëindigd of
verwijderd -- en vergelijkt hun adressen (straat, postcode en plaats;
hoofdletters en extra spaties maken niet uit).

- De grootste groep huurders die hetzelfde adres delen, is het
  **huishouden**. Zijn twee groepen even groot, dan wint de eerst
  gevonden.
- Alle anderen staan als **ander perceellid** dat tegen het extra bedrag
  kan worden meeverzekerd.
- Een huurder zonder adres vormt nooit een huishouden met iemand, ook
  niet met een andere huurder zonder adres.
- Een perceel met maar één huurder: die persoon is het huishouden, met
  of zonder adres.

!!! tip "Houd adressen consistent"
    „Hoofdstraat 5“ en „Hoofdstr. 5“ zijn voor Parcella verschillende
    adressen. Verschijnt een stel als huishouden plus „ander perceellid“,
    controleer dan de spelling in beide ledengegevens.

Wordt de verzekering van een perceel voor het eerst voor een jaar
geopend, dan wordt elk lid van het huishouden als gedekt aangevinkt.
Vanaf dan tellen de vinkjes: een lid dat later verhuist, verandert de
rekening niet voor een jaar dat al is ingericht, en een nieuw lid van het
huishouden verschijnt niet aangevinkt tot u het aanvinkt.

De factuurmodule gebruikt dezelfde berekening wanneer ze de verzekering
aan de jaarfactuur van een perceel toevoegt, met één regel per deel
(opstalpakket, basisbedrag huishouden, extra personen). Zie
[Factuurrondes](finances/invoice-runs.md).

## Overzicht {#overview}

![Overzicht](../assets/screenshots/insurance/overview.png)

De startpagina van de module (**Verzekering → Overzicht**). Ze toont de
cijfers van één jaar in één oogopslag.

| Veld / knop | Wat het doet |
|---|---|
| Jaarkeuze (rechtsboven) | Zet alle cijfers op een ander jaar. Toont elk jaar met een configuratie voor de ongevallenverzekering, plus het huidige jaar. |
| **Percelen beheren** | Opent de [perceellijst](#parcels) voor het gekozen jaar. |
| Waarschuwing „Er bestaat geen verzekeringsconfiguratie voor …“ | Getoond als het jaar nog geen bedragen voor de ongevallenverzekering heeft. **Nu aanmaken →** opent de [configuratie](#configuration) voor dat jaar. |
| **Opstalverzekering** | Aantal percelen met opstalverzekering in dit jaar. |
| **Ongevallenverzekering** | Aantal percelen met ongevallenverzekering waarbij minstens één lid van het huishouden gedekt is. Een perceel waar alleen een extra persoon verzekerd is, telt niet. |
| **Opstalopbrengst** | Som van de opstalkosten van alle percelen voor het jaar. |
| **Ongevalopbrengst** | Som van de ongevallenkosten van alle percelen voor het jaar. |
| **Opstalverzekeringspakketten {jaar}** | De pakketten van het jaar met hun bedragen. Alleen getoond als er pakketten zijn. |
| **Configuratie** | Opent de [configuratie](#configuration). |
| **Percelen beheren** | Opent de [perceellijst](#parcels). |
| **Jaarverslag** | Opent het [jaarverslag](#annual-report). |

## Percelen {#parcels}

![Percelen](../assets/screenshots/insurance/parcels-list.png)

**Verzekering → Perceel** toont de percelen met hun verzekeringsstatus en
kosten voor één jaar. Open de lijst vanuit het overzicht om het daar
gekozen jaar te houden; vanuit de navigatie toont ze het huidige jaar.

De lijst bevat elk actief perceel. Beëindigde percelen staan er ook in,
gemarkeerd als **beëindigd**, omdat het einde van een huur het
verzekeringscontract niet vanzelf opzegt. Een beëindigd perceel blijft
in de lijst tot u de verzekeringspagina opent, beide
verzekeringssoorten uitschakelt en op **Opslaan** klikt -- dat legt vast
„gecontroleerd, niets meer te verzekeren“, en het perceel verdwijnt uit
de lijst van dit jaar.

**Filters** (boven de tabel; ze werken zodra u een waarde kiest):

| Filter | Wat het doet |
|---|---|
| **Opstalverzekering** | **Alle**, **Geen** (percelen zonder opstalverzekering), of één pakket van het jaar (percelen die met precies dat pakket verzekerd zijn). |
| **Ongevallenverzekering** | **Alle**, **Ja** (ongevallenverzekering aan) of **Geen** (uit of nooit ingericht). |
| **Reset** | Wist beide filters. Alleen zichtbaar zolang er een filter actief is. |

**Kolommen:**

| Kolom | Wat ze toont |
|---|---|
| **Perceel** | Perceelnummer, gelinkt aan de verzekeringspagina van het perceel. Klik op de kolomkop om op perceelnummer te sorteren; klik nog eens om om te keren. |
| **Opstalverzekering** | De naam van het pakket, **Ja** als de opstalverzekering aan staat maar geen pakket is gekozen, of „–“. |
| **Ongevallenverzekering** | **Ja** als de ongevallenverzekering aan staat, met het aantal extra personen tussen haakjes, bijv. **Ja (+1)**; anders „–“. |
| **Totale kosten** | De totale verzekeringskosten van het perceel voor het jaar. Klik op de kop om op kosten te sorteren. |
| Potloodknop | Opent de verzekeringspagina van het perceel. |

De rij **Som** onderaan telt de percelen met opstal- en met
ongevallenverzekering (weer alleen die met minstens één gedekt lid van
het huishouden) en telt de totale kosten van de getoonde percelen op.
Onder de tabel staat hoeveel percelen er getoond worden.

## Verzekeringspagina van een perceel {#parcel-insurance-page}

![Verzekeringspagina van een perceel](../assets/screenshots/insurance/detail.png)

Geopend vanuit de perceellijst of het jaarverslag, met de titel
**Verzekering voor perceel {perceelnummer}**. Hier legt u vast wat een
perceel heeft afgesloten voor het jaar uit de link waar u vandaan kwam.

| Veld / knop | Wat het doet |
|---|---|
| **Vorige** / **Volgende** | Naar het vorige of volgende perceel in de volgorde van de perceellijst (op perceelnummer). Toetsenbord: ++ctrl+left++ en ++ctrl+right++. |
| **Terug** | Terug naar de perceellijst voor dit jaar. |
| Waarschuwing „Er bestaat geen verzekeringsconfiguratie voor …“ | Het jaar heeft nog geen bedragen voor de ongevallenverzekering, dus die kost niets. **Nu aanmaken →** opent de configuratie. |
| **Opstalverzekering afgesloten** | Schakelaar. Staat hij aan, dan verschijnt het veld **Pakket**. |
| **Pakket** | Het pakket opstalverzekering voor dit jaar. Heeft het jaar geen pakketten, dan verschijnt in plaats daarvan een waarschuwing met **Nu aanmaken →**. |
| **Ongevallenverzekering afgesloten** | Schakelaar. Staat hij aan, dan verschijnen de lijsten met personen. |
| **Huishouden (delen een adres met andere bewoners):** | Het herkende huishouden (zie [Wie als huishouden telt](#who-counts-as-the-household)). Elke aangevinkte persoon is gedekt; vink uit wie niet wil. Het basisbedrag wordt één keer in rekening gebracht als minstens één persoon hier is aangevinkt. |
| **Andere perceelleden (ander adres) …** | Huurders buiten het huishouden. Vink een persoon aan om hem tegen het extra bedrag mee te verzekeren. Alleen getoond als er zulke huurders zijn. |
| **Kosten {jaar}** | **Opstalverzekering**, **Ongevallenverzekering** en **Totaal** voor dit perceel, zoals nu opgeslagen. De cijfers worden na het opslaan bijgewerkt. |
| **Opslaan** | Slaat de verzekering van het perceel voor dit jaar op en laadt de pagina opnieuw. Alleen zichtbaar met schrijfrecht; zonder dat zijn alle velden alleen-lezen. |

!!! warning "Ongevallenverzekering uitschakelen wist de vinkjes"
    Slaat u op met **Ongevallenverzekering afgesloten** uit, dan worden
    de aangevinkte leden van het huishouden en extra personen verwijderd.
    Zet u haar later weer aan, vink de personen dan opnieuw aan voordat u
    opslaat.

!!! note
    Opstalverzekering uitschakelen wist ook het gekozen pakket.

## Configuratie {#configuration}

![Configuratie](../assets/screenshots/insurance/configuration.png)

**Verzekering → Configuratie** bevat de prijzen van het jaar. Kies het
jaar met de keuzelijst rechtsboven; **Terug** brengt u naar het
overzicht. Zonder schrijfrecht ziet u alleen de bedragen en pakketten.

### Ongevallenverzekering {jaar} {#accident-insurance}

| Veld / knop | Wat het doet |
|---|---|
| **Basisbedrag per perceel** | Eén keer per perceel met ongevallenverzekering in rekening gebracht, voor het huishouden. Vooraf ingevuld met 3,00 als het jaar nog geen configuratie heeft. |
| **Extra bedrag per extra persoon** | In rekening gebracht voor elk verzekerd perceellid buiten het huishouden. Vooraf ingevuld met 3,00 als het jaar nog geen configuratie heeft. |
| **Opslaan** | Slaat beide bedragen op voor het gekozen jaar. Opslaan maakt de configuratie van het jaar aan als die nog niet bestaat; vanaf dan verschijnt het jaar in de jaarkeuzes. |

Bedragen accepteren een komma of een punt als decimaalteken (`3,50` of
`3.50`). Een bedrag dat Parcella niet als getal kan lezen, wordt als 0
opgeslagen -- controleer het cijfer na het opslaan.

### Nieuw opstalverzekeringspakket {#new-property-insurance-package}

| Veld / knop | Wat het doet |
|---|---|
| **Naam** | De naam van het pakket, bijv. „Pakket 1“. Verplicht. |
| **Bedrag** | Wat een perceel met dit pakket per jaar betaalt. Verplicht. |
| **Sorteervolgorde** | Pakketten worden op dit getal gesorteerd, laagste eerst, daarna op bedrag. Standaard 0. |
| **+** | Voegt het pakket toe aan het gekozen jaar. |

### Pakketten {jaar} {#packages}

De pakketten van het jaar. Met schrijfrecht kunt u **Naam** en **Bedrag**
direct in de rij wijzigen en met de vinkknop bevestigen. De
prullenbakknop verwijdert het pakket na bevestiging (vraagt
verwijderrecht).

!!! warning "Een pakket verwijderen dat in gebruik is"
    Percelen die het verwijderde pakket hadden, houden „opstalverzekering
    afgesloten“, maar zonder pakket -- ze kosten dan niets voor de
    opstalverzekering en tonen **Ja** in plaats van een pakketnaam. Kies
    bij elk van die percelen een nieuw pakket.

!!! tip "Een nieuw jaar inrichten"
    Pakketten en bedragen horen bij één jaar en worden niet automatisch
    gekopieerd. Open aan het begin van een nieuw jaar de configuratie
    voor dat jaar, vul de bedragen voor de ongevallenverzekering in, maak
    de pakketten opnieuw aan en loop dan de perceellijst door. Elk
    perceel begint het nieuwe jaar zonder vastgelegde verzekering.

## Jaarverslag {#annual-report}

![Jaarverslag](../assets/screenshots/insurance/evaluation.png)

**Verzekering → Evaluatie** (of **Jaarverslag** op het overzicht), met
de titel **Verzekeringsrapport {jaar}**, toont elk perceel dat in een
jaar een opstal- of ongevallenverzekering heeft, met de kosten. Gebruik
het om de totalen te vergelijken met de rekening van de verzekeraar.

**Filters** (werken zodra u een waarde kiest):

| Filter | Wat het doet |
|---|---|
| Jaar | Het jaar van het verslag. |
| **Alle types** / **Opstalverzekering** / **Ongevallenverzekering** | Alle verzekerde percelen, of alleen die met dat soort verzekering. |
| **Alle pakketten** / een pakket | Alleen percelen die met dat opstalpakket verzekerd zijn. |
| **Alle** / **Met extra personen** / **Zonder extra personen** | Percelen met minstens één verzekerde extra persoon, of percelen met ongevallenverzekering zonder. |

| Veld / kolom | Wat het toont |
|---|---|
| **Verzekerde percelen** | Aantal percelen dat onder de huidige filters wordt getoond. |
| **Totale inkomsten** | Som van de kolom **Totaal**. |
| **Perceel** | Perceelnummer, gelinkt aan de verzekeringspagina van het perceel. |
| **Opstalverzekering** | De naam van het pakket, of „–“. |
| **Opstalkosten** | De opstalkosten van het perceel. |
| **Ongevallenverzekering** | **Ja** of „–“. |
| **Extra personen** | Aantal verzekerde extra personen buiten het huishouden. |
| **Ongevalkosten** | De ongevallenkosten van het perceel. |
| **Totaal** | De totale verzekeringskosten van het perceel. |
| **CSV-export** | Downloadt de lijst zoals ze nu gefilterd is, als bestand gescheiden door puntkomma's met decimale komma's. |
| **Terug** | Terug naar het overzicht. |

!!! note "Kolomkoppen van het CSV-bestand"
    Het CSV-bestand gebruikt dezelfde kolomkoppen als deze pagina, in de
    taal van de vereniging: Perceel, Opstalverzekering, Pakket,
    Opstalkosten (EUR), Ongevallenverzekering, Extra personen,
    Ongevalkosten (EUR), Totaal (EUR). Ja/nee-waarden worden ook in die
    taal geschreven.

!!! note "Twee manieren van tellen"
    **Verzekerde percelen** telt hier elk getoond perceel. De tegel
    **Ongevallenverzekering** op het overzicht telt alleen percelen met
    minstens één gedekt lid van het huishouden, dus de twee getallen
    kunnen verschillen.

## Gerelateerd {#related}

- [Percelen](parcels.md) -- huren en beëindiging, die bepalen wie op de
  verzekeringspagina van een perceel verschijnt
- [Leden](members.md) -- de adressen waarmee het huishouden wordt herkend
- [Factuurrondes](finances/invoice-runs.md) -- de verzekering met de
  jaarfactuur factureren
- [Groepen](../administration/groups.md) -- een penningmeester toegang
  tot deze module geven

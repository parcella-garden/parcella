# Financiën {#finances}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

In de module Financiën werkt de penningmeester. Ze maakt de jaarfacturen
van de vereniging voor elk perceel en lid, houdt bij wie heeft betaald,
verstuurt betalingsherinneringen en legt de rekeningen vast die de
vereniging zelf ontvangt. Ze houdt ook per bankrekening een eenvoudig
kasboek bij. Uit dat alles maakt ze een boekhoudkundig overzicht op
kasbasis voor de belastingdienst en een begroting voor het volgende
jaar.

!!! info "Wie kan dit gebruiken"
    - De module staat **standaard uit**. Een beheerder schakelt haar in
      onder **Verenigingsinstellingen** (de schakelaar heet
      **Financiën**), zie
      [Modules in- en uitschakelen](../../administration/modules.md).
      Vul vóór de eerste facturen de **Financiële instellingen** in
      (bankgegevens, formaat van het factuurnummer) in
      [Verenigingsinstellingen](../../administration/settings.md) -- ze
      worden in de voettekst van elke factuur afgedrukt.
    - Bestuursleden en beheerders (en iedereen in een groep met volledige
      toegang) kunnen alles.
    - Alle anderen hebben een [groep](../../administration/groups.md)
      nodig die rechten op **Financiën** geeft:
        - **lezen** -- elk scherm zien, PDF's openen, CSV-bestanden
          exporteren;
        - **schrijven** -- rondes, posten, betalingen, herinneringen,
          rekeningen, boekingen, inkomende facturen, categorieën en de
          begroting aanmaken en wijzigen;
        - **verwijderen** -- die dingen weer verwijderen.
    - Een paar handelingen rond bijlagen van inkomende facturen in de
      cloudopslag zijn alleen voor bestuursleden en beheerders, zie
      [Inkomende facturen](incoming-invoices.md).

    Zie [Rollen, groepen en rechten](../../getting-started/roles-and-permissions.md).

## Waar u het vindt {#where-to-find-it}

Staat de module aan en mag u haar lezen, dan toont de zijbalk een groep
**Financiën** met vier items:

| Menu-item | Opent |
|---|---|
| **Overzicht** | Het financiële dashboard dat hieronder wordt beschreven. |
| **Uitgaande facturen** | De lijst met factuurrondes, zie [Factuurrondes](invoice-runs.md). |
| **Herinneringen** | De lijst met achterstallige facturen, zie [Facturen, betalingen en herinneringen](invoices.md#reminders). |
| **Inkomende facturen** | Rekeningen die de vereniging heeft ontvangen, zie [Inkomende facturen](incoming-invoices.md). |

Al het andere (rekeningen, categorieën, artikelcatalogus, boekingen,
overzicht, begroting) bereikt u via de kaarten van het dashboard.

## Financieel dashboard {#finances-dashboard}

![Financieel dashboard](../../assets/screenshots/finances/dashboard.png)

De startpagina van de module. Drie cijfers bovenaan geven in één
oogopslag de stand van uw uitgaande facturen. Daaronder brengt één kaart
per onderdeel van de module u erheen.

| Cijfer | Wat het toont |
|---|---|
| **Openstaande facturen** | Hoeveel uitgaande facturen nog niet volledig zijn betaald. Gedeeltelijk betaalde facturen tellen hier als open. |
| **Openstaand bedrag** | De som die over die facturen nog niet is betaald (factuurbedrag min geregistreerde betalingen). Aanmaningskosten zitten niet in dit cijfer. |
| **Achterstallig** | Hoeveel van de open facturen voorbij de vervaldatum van hun factuurronde zijn. Rood getoond als het meer dan nul is. |

| Kaart | Hint onder de titel | Opent |
|---|---|---|
| **Uitgaande facturen** | *n* factuurronde(s) | [Factuurrondes](invoice-runs.md) |
| **Categorieën** | *n* categorie(ën) gedefinieerd | [Boekhoudcategorieën](bookkeeping.md#bookkeeping-categories) |
| **Artikelcatalogus** | *n* artikelsjabloon/sjablonen gedefinieerd | [Artikelcatalogus](invoice-runs.md#item-catalog) |
| **Rekeningen** | *n* rekening(en) gedefinieerd | [Rekeningen](bank-accounts.md#accounts) |
| **Herinneringen** | *n* factu(u)r(en) achterstallig | [Herinneringen](invoices.md#reminders) |
| **Inkomende facturen** | *n* inkomende factu(u)r(en) | [Inkomende facturen](incoming-invoices.md) |
| **Alle boekingen** | Alle betalingen van inkomende en uitgaande facturen | [Alle boekingen](bookkeeping.md#all-bookings) |
| **Boekhoudkundig overzicht** | Overzicht op kasbasis voor de belastingdienst | [Boekhoudkundig overzicht](bookkeeping.md#accounting-statement) |
| **Begroting** | Begrote inkomsten en uitgaven per categorie voor het komende jaar, naast de werkelijke cijfers van eerdere jaren | [Begroting](bookkeeping.md#budget-plan) |

De meeste subpagina's hebben een knop **Terug naar Financiën** in de
bovenbalk die u hierheen terugbrengt.

<!-- TODO(verify): finances/coming_soon.html ("This feature is coming soon.") exists, but no route renders it any more, so it is not documented as a screen. -->

## Hoe het geld door een jaar loopt {#how-the-money-flows-through-a-year}

Een typisch verenigingsjaar in Parcella ziet er zo uit:

1. **Eén keer inrichten.** Maak uw
   [boekhoudcategorieën](bookkeeping.md#bookkeeping-categories) aan (of
   importeer uw rekeningschema), uw
   [bank- en kasrekeningen](bank-accounts.md#accounts), en de
   terugkerende factuurregels in de
   [artikelcatalogus](invoice-runs.md#item-catalog) (pacht per m²,
   contributie, water, elektriciteit, verzekering ...).
2. **De jaarfacturen voorbereiden.** Maak een
   [factuurronde](invoice-runs.md) voor het jaar aan, voeg de posten uit
   de catalogus toe, pas prijzen aan en controleer het
   [voorbeeld](invoice-runs.md#preview-invoices). Meterstanden,
   verzekering en werkuren voor dat jaar moeten op dit punt compleet
   zijn -- de verbruiksposten lezen ze live.
3. **Definitief maken en versturen.** Definitief maken kent de blijvende
   factuurnummers toe. Verstuur de facturen dan per e-mail, upload ze
   naar de cloudmappen van de percelen, en download de afdrukbundel voor
   iedereen die papier krijgt.
4. **Betalingen vastleggen.** Voer betalingen met de hand in op de
   factuurlijst van de ronde, of importeer uw bankafschrift op de
   [boekingenpagina van de rekening](bank-accounts.md#bookings-of-an-account)
   en koppel elke regel aan de factuur die ze betaalt.
5. **Late betalers aanmanen.** De pagina
   [Herinneringen](invoices.md#reminders) toont elke achterstallige
   factuur; verstuur vanuit de factuur de eerste, tweede, derde
   herinnering, met of zonder kosten.
6. **De eigen rekeningen van de vereniging** vastleggen als
   [inkomende facturen](incoming-invoices.md) en als betaald markeren
   wanneer het geld de deur uit gaat.
7. **Het jaar afsluiten.** Het
   [boekhoudkundig overzicht](bookkeeping.md#accounting-statement) toont
   inkomsten en uitgaven per categorie, geteld op de dag waarop het geld
   echt bewoog. Gebruik het voor de belastingdienst en de algemene
   ledenvergadering, en plan het volgende jaar in de
   [begroting](bookkeeping.md#budget-plan).

Het stappenplan [De jaarfacturen opmaken](../../guides/annual-invoicing.md)
loopt stap 2 tot 5 op volgorde door.

## Hoofdstukken {#chapters}

- [Factuurrondes](invoice-runs.md) -- de jaarlijkse factuurbatch, de
  posten en hoe elk bedrag wordt berekend, de artikelcatalogus, het
  voorbeeld en definitief maken.
- [Facturen, betalingen en herinneringen](invoices.md) -- elke factuur
  over alle rondes heen, verzending, betalingen en het aanmaningsproces.
- [Bankrekeningen en boekingen](bank-accounts.md) -- uw rekeningen, hun
  boekingen, en een bankafschrift importeren met koppeling aan facturen.
- [Inkomende facturen](incoming-invoices.md) -- rekeningen die de
  vereniging heeft ontvangen en hun betalingen.
- [Categorieën, begroting en overzicht](bookkeeping.md) --
  boekhoudcategorieën, de lijst met alle boekingen van de vereniging,
  het boekhoudkundig overzicht en de begroting.

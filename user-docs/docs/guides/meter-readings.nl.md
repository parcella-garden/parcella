# Meterstanden opnemen {#collecting-meter-readings}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Eens per jaar loopt iemand over het terrein en leest elke water- en
elektriciteitsmeter af: de hoofdmeter van de vereniging, één meter per
perceel, en de eigen aansluitingen van de vereniging (clubhuis,
wasplaats). Dit stappenplan behandelt het invoeren van die standen -- op
een telefoon terwijl u loopt, of achteraf vanuit een lijst -- plus het
vervangen van een meter en het controleren van de resultaten.

Water en elektriciteit werken precies hetzelfde; elk heeft een eigen
menu. De stappen hieronder zeggen **Water**; gebruik voor elektriciteit
in plaats daarvan het menu **Elektriciteit**.

!!! info "Wie kan dit doen"
    Standen invoeren vraagt **schrijf**recht op **Water** (of
    **Elektriciteit**); een stand verwijderen vraagt **verwijderen**.
    Beide modules staan standaard aan. Een vereniging kan het meterteam
    een groep met precies deze rechten geven -- zie
    [Groepen](../administration/groups.md).

## Hoe Parcella het verbruik telt {#how-parcella-counts-consumption}

- Elk **[meetpunt](../glossary.md#metering-point)** (de aansluiting van
  een perceel, de hoofdmeter, een verenigingsaansluiting) heeft telkens
  één **meter** geïnstalleerd.
- Een meter heeft **één stand per jaar**. Het verbruik van het jaar is
  die stand min de stand van het vorige jaar -- of min de **Beginstand**
  van de meter als het de eerste is.
- Een stand invoeren voor een jaar dat er al een heeft, **vervangt**
  die.
- Standen worden precies ingevoerd zoals de display ze toont. Sommige
  elektriciteitsmeters tonen maar een deel van de echte waarde; hun
  meetpunt heeft dan een **Factor** (bijv. 20) die de evaluatie
  meerekent.

## 1. Vóór de ronde: de lijst met meetpunten controleren {#1-before-the-round-check-the-list-of-metering-points}

1. Open **Water → Overzicht**. De tegels tonen hoeveel hoofdmeters,
   perceel- en verenigingsaansluitingen er zijn, en **Ontbrekende
   meetpunten**: percelen zonder wateraansluiting in Parcella.
2. Klik op **Toon** onder **Ontbrekende meetpunten** om die percelen te
   zien; elk linkt naar **Nieuw meetpunt** met het perceel al gekozen.
   Voeg toe wat echt een meter heeft.
3. Een aansluiting die een tijd geen levering heeft (water afgesloten op
   een onverhuurd perceel)? Open haar meetpunt, stel **Uitschakelen per**
   in en klik op **Uitschakelen**. Het valt uit de lijst met standen tot
   u **Weer inschakelen**.

Staat uw meterlijst nog in een spreadsheet, importeer die dan -- zie
[Leden en percelen importeren](csv-import.md#4-metering-points).

## 2. Optie A: standen op uw telefoon invoeren terwijl u loopt {#2-option-a-enter-readings-on-your-phone-while-you-walk}

1. Open **Water → Meterstanden** op uw telefoon. De pagina toont het
   huidige jaar; kies zo nodig een ander in de jaarkeuze bovenaan.
2. De pagina toont **Hoofdmeter**, **Percelen** (gesorteerd op
   perceelnummer) en **Verenigingsaansluitingen**. Elke rij toont het
   meternummer en de stand van **Vorig jaar** ter controle.
3. Typ de stand in het veld van de rij en tik op de opslagknop ernaast.
   De rij toont de waarde dan als **geregistreerd**.
4. Ga verder met de volgende meter. Rijen zonder waarde zeggen **Nog
   niet ingevoerd**.

Standen die hier worden ingevoerd, krijgen de datum van vandaag. Om een
andere datum te gebruiken of een notitie toe te voegen, voert u de stand
in plaats daarvan in op de pagina van het meetpunt (optie C).

## 3. Optie B: op papier of in een spreadsheet verzamelen, dan importeren {#3-option-b-collect-on-paper-or-in-a-spreadsheet-then-import}

1. Open **Water → Meterstanden**, kies het jaar en klik op
   **CSV-export**. U krijgt een bestand met één rij per meter: **Type**,
   **Parcel number**, **Label**, **Meter number**, **Year**, en lege
   kolommen **Date**, **Reading** en **Note**.
2. Druk het af of vul het in op een tablet. Vul **Date** en **Reading**
   in voor elke meter die u afleest.
3. Klik terug op **Water → Meterstanden** op **CSV-import**, kies het
   bestand en klik op **Importeren**.
4. Controleer op **CSV-kolommen koppelen** de koppeling. Heeft uw bestand
   geen kolom voor het jaar, vul het dan in bij **Standaardjaar
   (optioneel)**. Klik op **Importeren**.
5. Lees de samenvatting op de pagina met meterstanden: hoeveel standen
   zijn vastgelegd, en hoeveel rijen zijn overgeslagen en waarom.

Rijen zonder stand worden als „ongeldige rij“ overgeslagen -- dat is te
verwachten voor meters die u nog niet hebt afgelezen. Details over
kolommen en foutmeldingen:
[Leden en percelen importeren](csv-import.md#5-meter-readings).

## 4. Optie C: één stand met datum en notitie invoeren {#4-option-c-enter-a-single-reading-with-date-and-note}

1. Open **Water → Meetpunten** en klik op het meetpunt.
2. Vul onderaan, onder **Meterstanden**, **Jaar**, **Datum**,
   **Meterstand** en eventueel een **Notitie** in.
3. Klik op **Meterstand opnemen**.

De tabel **Meterstanden** op dezelfde pagina toont elk jaar met stand en
verbruik. Een foute stand kunt u daar verwijderen.

## 5. Als een stand er verkeerd uitziet {#5-when-a-reading-looks-wrong}

Een stand die lager is dan die van vorig jaar (of hoger dan een al
vastgelegde latere) wordt **toch opgeslagen**, met een waarschuwing zoals
*„Meterstand opgeslagen, maar controleer hem a.u.b.: De meterstand (…) is
lager dan de vorige stand (…) van dezelfde meter. Is een eerdere stand
geschat? Controleer dit a.u.b.“* De stand houdt een waarschuwingsteken op
de pagina met meterstanden en bij het meetpunt.

Gebruikelijke oorzaken: een typefout, een verkeerd gelezen cijfer, een
eerdere stand die te hoog was geschat, of een meter die in werkelijkheid
is vervangen (stap 6). Corrigeer de waarde door de stand voor hetzelfde
jaar opnieuw vast te leggen.

## 6. Een meter wordt vervangen {#a-meter-is-replaced}

Wordt een meter fysiek gewisseld -- bijvoorbeeld omdat de kalibratie
afloopt:

1. Lees de oude meter een laatste keer af, als dat nog kan, en voer de
   stand op de pagina van het meetpunt in als stand van het jaar (optie
   C).
2. Open in de kaart **Huidige Water meter** (**Huidige Elektriciteit
   meter** bij elektriciteit) **Meter wisselen**.
3. Vul **Oude meter verwijderd op**, **Nieuwe meter geïnstalleerd op**,
   het **Nieuw nummer**, **Gekalibreerd tot** (een jaartal) en de
   **Beginstand** van de nieuwe meter in (meestal wat de display bij de
   installatie toont).
4. Klik op **Wisselen** en bevestig.

De oude meter wordt niet verwijderd: hij verschuift naar **Eerdere
meters** met de datums van installatie en verwijdering en zijn **Laatste
stand**. Vanaf nu gaan standen naar de nieuwe meter, waarvan het verbruik
begint bij zijn **Beginstand**.

!!! tip "Verbruik in het jaar van de wissel"
    Vul in het wisselformulier **Eindstand van de oude meter** in -- wat
    de oude meter op de dag van verwijderen aangeeft. Het verbruik van het
    jaar telt dan beide meters op (de oude tot de wissel, de nieuwe vanaf
    zijn beginstand), en dat totaal factureert de jaarfactuur. Zonder
    eindstand wordt het deel van de oude meter sinds zijn laatste stand
    niet gefactureerd.

!!! tip "Typefout, geen nieuwe meter?"
    Hebt u alleen het meternummer of de beginstand verkeerd getypt,
    gebruik dan **Meter bewerken**. **Meter wisselen** is voor een echte
    vervanging.

## 7. Het jaar controleren {#7-check-the-year}

1. Open **Water → Evaluatie** en kies het jaar.
2. De tegels vergelijken **Hoofdmeter** met **Percelen totaal** en
   **Vereniging totaal**; de tabellen eronder tonen elk meetpunt met zijn
   **Verbruik**. Punten waarvoor nog een stand ontbreekt, tonen **geen
   stand**.
3. Verbruikten de percelen en verenigingsaansluitingen samen meer dan de
   hoofdmeter, dan toont Parcella een waarschuwing. Dat is normaal zolang
   de standen nog worden ingevoerd; zijn ze allemaal binnen, dan wijst
   het op een verkeerd afgelezen meter.
4. **CSV-export** downloadt de evaluatie voor uw eigen administratie of
   het nutsbedrijf.

**Water → Overzicht** zegt ook hoeveel meetpunten voor het jaar nog een
stand missen, met een link **Nu opnemen →**.

## 8. De prijs voor de facturatie instellen {#8-set-the-price-for-billing}

Factureert u water en elektriciteit met de jaarfacturen van Parcella:

1. Open **Water → Configuratie**.
2. Vul onder **Nieuwe/bijgewerkte prijs** het **Jaar** en de **Prijs per
   m³** in, en eventueel een **Notitie** (bijv. „tariefwijziging
   leverancier“).
3. Klik op **Opslaan**.

Zonder prijs voor het jaar factureert de factuurronde voor dat jaar geen
water. Ga dan verder met [De jaarfacturen opmaken](annual-invoicing.md).

## Gerelateerd {#related}

- [Water en elektriciteit](../modules/metering.md)
- [Leden en percelen importeren](csv-import.md)
- [De jaarfacturen opmaken](annual-invoicing.md)
- [Een perceel overdragen](parcel-handover.md)
- Woordenlijst: [meetpunt](../glossary.md#metering-point),
  [meter](../glossary.md#meter)

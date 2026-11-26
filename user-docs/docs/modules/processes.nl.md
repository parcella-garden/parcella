# Processen {#processes}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Veel verenigingstaken volgen elke keer dezelfde stappen: een tuin
overdragen, een nieuw lid verwelkomen, een klacht afhandelen. Met
processen beschrijft u zo'n taak één keer als **sjabloon** -- een reeks
**fasen**, elk met de **velden** die moeten worden ingevuld -- en voert u
haar zo vaak uit als nodig, voor een tuin, een lid of een aanmelder.
Parcella houdt bij waar elke uitvoering staat, wat er is ingevuld en wie
wat heeft gedaan.

!!! info "Wie kan dit gebruiken"
    - De moduleschakelaar is **Processen** onder **Administratie →
      Modules in- en uitschakelen**. Ze staat standaard **aan**.
    - De rollen **Bestuur** en **Beheerder**, en leden van een groep met
      **Volledige toegang tot elke module**, kunnen alles, ook sjablonen
      bouwen.
    - Alle anderen hebben het recht **Processen** in een van hun
      [groepen](../administration/groups.md) nodig:
        - *lezen*: processen, hun waarden, bestanden en geschiedenis
          zien;
        - *schrijven*: processen starten, velden invullen, bestanden
          uploaden, naar de volgende fase gaan of teruggaan;
        - *verwijderen*: een proces afbreken of verwijderen.
    - **Sjablonen** kunnen alleen met volledige toegang worden aangemaakt
      en gewijzigd.
    - Processen over aanmelders, en velden voor aanmelders, vragen ook
      leesrecht op de module [Aanmelders](applicants.md). Zonder dat ziet
      u „Alleen zichtbaar met toegang tot de module kandidaten.“

## Hoe het in elkaar zit {#how-it-fits-together}

- Een **sjabloon** zegt waar het proces over gaat (een tuin, een lid,
  een aanmelder, of niets in het bijzonder) en somt de fasen op
  volgorde op.
- Elke **fase** heeft willekeurig veel **velden**. Een veld kan
  **Verplicht** zijn.
- Een proces starten maakt een kopie van het sjabloon. Latere wijzigingen
  aan het sjabloon raken processen die al lopen niet.
- Een proces staat altijd in één **huidige fase**. U gaat verder met
  **Klaar -- volgende fase** zodra elk verplicht veld van die fase is
  ingevuld. Na de laatste fase is het proces **Afgerond**.
- U kunt teruggaan naar een eerdere fase (met een reden), of het proces
  afbreken (met een reden). Een afgerond of afgebroken proces kan niet
  meer worden gewijzigd.

## Lijst met processen {#process-list}

![Lijst met processen](../assets/screenshots/processes/list.png)

Open **Processen** in het menu.

| Veld / knop | Wat het doet |
|---|---|
| **Sjablonen** | Opent [Processjablonen](#process-templates). Alleen met volledige toegang. |
| **Proces starten** | Opent [Proces starten](#start-a-process). Vraagt *schrijven*. |
| **Status** | **Lopend** (standaard), **Gesloten** (afgerond of afgebroken) of **Alle**. |
| **Sjabloon** | **Alle sjablonen** of één sjabloon; gearchiveerde sjablonen zijn gemarkeerd met „(gearchiveerd)“. |
| **Filteren** | Past de twee filters toe. |

| Kolom | Wat ze toont |
|---|---|
| **Proces** | De titel (gelinkt) en daaronder de naam van het sjabloon. |
| **Voor** | De tuin, het lid of de aanmelder, gelinkt aan hun pagina. „(verwijderd)“ als dat record is verwijderd. |
| **Huidige fase** | De fase waarin het proces staat, bijv. „Taxatie (2/6)“. Een streepje bij gesloten processen. |
| **Gestart** | De startdatum. |
| **Status** | **Lopend**, **Afgerond** of **Afgebroken**. |

Is de lijst leeg, dan staat er **Geen processen.**, en zonder sjablonen
wordt **Maak eerst een sjabloon.** aangeboden.

!!! tip "Processen op de pagina's van tuinen, leden en aanmelders"
    De pagina van een [tuin](parcels.md), een [lid](members.md) en een
    [aanmelder](applicants.md) heeft een kaart **Processen** met hun
    processen, huidige fase en status. De knop **Proces starten** daarin
    opent de startpagina met die tuin, dat lid of die aanmelder al
    gekozen, en biedt alleen de passende sjablonen aan.

## Proces starten {#start-a-process}

![Proces starten](../assets/screenshots/processes/new.png)

1. Kies het **Sjabloon**. De pagina laadt opnieuw en toont de
   beschrijving van het sjabloon en de **Fasen**. Gearchiveerde sjablonen
   worden niet aangeboden.
2. Gaat het sjabloon over een tuin, lid of aanmelder, kies die dan in het
   veld **Tuin**, **Lid** of **Kandidaat**. Dit is verplicht.
3. Geef eventueel een **Titel** -- zonder titel wordt de naam van het
   sjabloon gebruikt. Tip: neem het perceelnummer of de naam op, bijv.
   „Overdracht tuin 17“, zodat u processen in de lijst uit elkaar kunt
   houden.
4. Klik op **Starten**. Het proces opent in de eerste fase.

**Annuleren** brengt u terug naar de lijst. Bestaat er nog geen
sjabloon, dan zegt de pagina **Er is nog geen actief sjabloon.**

## Een lopend proces {#a-running-process}

![Een proces](../assets/screenshots/processes/detail.png)

Bovenaan ziet u de status, het sjabloon, waar het proces over gaat
(gelinkt) en „Gestart op {datum} door {naam}“. Daaronder toont een rij
badges de voortgang: groen met een vinkje voor afgeronde fasen, blauw
voor de huidige fase, grijs voor fasen die nog komen. Klik op een badge
om naar die fase te springen.

Een afgerond proces toont **Afgerond op {datum}.**; een afgebroken
proces toont **Afgebroken**, de datum en de reden.

### De fasen {#the-stages}

Elke fase is een kaart met haar nummer en naam.

- **Afgeronde fasen** tonen de datum en wie ze afrondde. Hun velden
  kunnen nog worden gecorrigeerd zolang het proces open is.
- De **huidige fase** is gemarkeerd als **Huidige fase** en blauw
  omlijnd.
- **Nog niet bereikte fasen** zijn gemarkeerd als **Nog niet bereikt**
  en tonen alleen de namen van hun velden.

In een fase die u kunt bewerken, vult u de velden in en klikt u op
**Opslaan**. Dat slaat de velden van die ene fase op. Bestanden worden
apart geüpload (zie hieronder). Is een waarde ongeldig, dan ziet u een
melding zoals **Vul een geldig getal in.** of **Vul een geldige datum
in.**

### Verder gaan {#moving-on}

Onderaan de huidige fase:

- **Nog nodig om verder te gaan:** toont de verplichte velden die nog
  leeg zijn, elk gelinkt aan zijn veld. Zolang er iets staat, is de knop
  uitgeschakeld.
- **Klaar -- volgende fase** rondt de fase af en zet het proces verder.
  In de laatste fase heet de knop **Proces afronden**.

Een verplicht vinkje telt als ingevuld zodra het is aangevinkt; een
verplicht bestandsveld zodra het minstens één bestand heeft.

### Teruggaan {#go-back}

De kaart **Teruggaan** (met *schrijven*, zodra het proces voorbij de
eerste fase is) zet het proces terug naar een eerdere fase, bijvoorbeeld
als een inspectie moet worden herhaald.

| Veld / knop | Wat het doet |
|---|---|
| **Terug naar fase** | Naar welke eerdere fase. De vorige fase is voorgeselecteerd. |
| **Reden** | Verplicht. Gaat in de geschiedenis. |
| **Teruggaan** | Zet het proces terug. Alle tot nu toe ingevulde waarden blijven bewaard. |

### Geschiedenis {#history}

De kaart **Geschiedenis** toont alles wat er gebeurde, het nieuwste
bovenaan, met tijd, fase, notitie en gebruiker: **Gestart**, **Verder
naar**, **Terug naar**, **Afgerond**, **Afgebroken**, **Veld gewijzigd**
(met oude en nieuwe waarde), **Bestand toegevoegd** en **Bestand
verwijderd**.

### Afbreken of verwijderen {#abort-or-delete}

Alleen met *verwijder*recht:

| Veld / knop | Wat het doet |
|---|---|
| **Proces afbreken** + **Reden** + **Afbreken** | Stopt een open proces definitief, na **Dit proces echt afbreken? Het kan niet opnieuw worden geopend.** De reden is verplicht en wordt bij het proces getoond. Het proces blijft in de lijst als **Afgebroken**. |
| **Proces verwijderen** | Haalt het proces volledig weg, met alle waarden en bestanden, na **Dit proces met alle waarden en bestanden echt verwijderen?** Alleen voor een proces dat per ongeluk is gestart. Bestanden in de cloud worden niet verwijderd. |

## Veldsoorten {#field-types}

| Soort | Wat u in een proces invult |
|---|---|
| **Tekst** | Eén regel, maximaal 1.000 tekens. |
| **Lange tekst** | Meerdere regels. |
| **Getal** | Een getal. Komma of punt werkt allebei als decimaalteken („1.234,50“ en „1,234.50“). |
| **Bedrag** | Als een getal, getoond met de valuta van uw vereniging. |
| **Datum** | Een datum. |
| **Vinkje** | Aangevinkt of niet, bijv. „Sleutels overhandigd“. |
| **Keuze uit lijst** | Een van de opties die in het sjabloon zijn vastgelegd. |
| **Bestanden (PDF, foto's)** | Een of meer geüploade bestanden. |
| **Lid** | Een lid van de vereniging. |
| **Kandidaat** | Een aanmelder (vraagt toegang tot de module Aanmelders). |
| **Tuin** | Een tuin. |

Een veld kan een hulptekst hebben, die eronder wordt getoond.

### Bestanden {#files}

Een bestandsveld toont zijn bestanden met naam, grootte, datum en wie ze
uploadde; een wolkpictogram betekent **Opgeslagen in de cloud**. Klik op
een naam om het bestand te openen of te downloaden. Om er een toe te
voegen, gebruikt u **Kies een bestand** en **Uploaden**; het kleine
kruisje verwijdert een bestand na **Dit bestand verwijderen?** (zolang de
fase bewerkbaar is).

Alleen PDF, JPEG, PNG of WebP, maximaal 20 MB. Onder de uploadknop zegt
Parcella waar het bestand heen gaat, in deze volgorde:

1. **De cloudmap van de tuin**, in een submap voor dit proces -- als de
   module Cloudopslag aan staat en het proces gaat over een tuin met een
   cloudmap, of over een lid met precies één huidige tuin die er een
   heeft.
2. **De map voor procesbestanden**, als een beheerder **Map voor
   procesbestanden** heeft ingesteld onder **Administratie →
   Integraties**.
3. Anders **de privéopslag van Parcella**: „Bewaard in de privéopslag van
   Parcella (geen cloudmap ingesteld voor dit perceel of voor
   processen).“

!!! warning "Tuinmappen worden vaak met de huurders gedeeld"
    Zijn uw tuinmappen in de cloud gedeeld met de huurders van de tuin,
    dan zien zij ook de bestanden van processen over hun tuin. Dat is zo
    bedoeld -- officiële documenten over een tuin zijn open voor de
    huurders. Wilt u bestanden alleen voor het bestuur, stel dan geen
    cloudmap in bij de tuin en gebruik de map voor procesbestanden.

Een bestand uit een proces verwijderen verwijdert een bestand in de
eigen opslag van Parcella, maar ontkoppelt een bestand in de cloud
alleen; het bestand zelf blijft daar staan.

## Processjablonen {#process-templates}

![Processjablonen](../assets/screenshots/processes/templates.png)

**Sjablonen** in de lijst met processen (alleen met volledige toegang)
opent **Processjablonen**. **Processen** rechtsboven brengt u terug.

De kaart **Sjablonen** toont elk sjabloon met waar het over gaat, het
aantal fasen, hoe vaak het is gebruikt, en **gearchiveerd** als het
gearchiveerd is. **Bewerken** opent de [sjablooneditor](#the-template-editor).

### Nieuw sjabloon {#new-template}

| Veld / knop | Wat het doet |
|---|---|
| **Naam** | Verplicht, maximaal 200 tekens. |
| **Een proces gaat over** | **Tuin**, **Lid**, **Kandidaat** of **Niet gekoppeld**. Bij het starten van een proces kiest u de tuin, het lid of de aanmelder waar het over gaat, en het proces verschijnt dan op hun pagina. |
| **Beschrijving** | Optioneel. Getoond wanneer iemand het sjabloon kiest om een proces te starten. |
| **Aanmaken** | Maakt het sjabloon aan en opent de editor. |

### Beginnen met een voorbeeld {#start-from-an-example}

Maakt een gewoon sjabloon dat u daarna vrij kunt aanpassen, in uw taal.
Klik op **Gebruiken** naast:

- **Overdracht van een tuin** -- een opgezegde tuin op weg naar de
  volgende huurder: inspectie, taxatie, advertentie, nieuwe huurder,
  contract en overdracht.
- **Nieuw lid verwelkomen** -- een nieuw lid verwelkomen: eerste
  gesprek, papierwerk en laatste details.

## De sjablooneditor {#the-template-editor}

![Sjablooneditor](../assets/screenshots/processes/template-edit.png)

De editor heeft de kop „Sjabloon: {naam}“. Wijzigingen worden opgeslagen
terwijl u ze maakt; rechtsboven verschijnt kort een bevestiging.

De kop toont de naam, waar het sjabloon over gaat, en een notitie:
„Wijzigingen gelden voor processen die vanaf nu worden gestart. Al
gestarte processen ({aantal}) houden hun fasen en velden.“

| Knop | Wat het doet |
|---|---|
| **Details** | Opent naam, **Een proces gaat over** en beschrijving om te bewerken; **Opslaan** bewaart ze. |
| **Archiveren** / **Herstellen** | Met een gearchiveerd sjabloon kunnen geen nieuwe processen worden gestart; lopende gaan door. |
| **Verwijderen** | Alleen zolang er nog geen proces vanuit het sjabloon is gestart, na **Dit sjabloon echt verwijderen?** Archiveer het anders. |

### Fasen {#stages}

De linkerkaart toont de **Fasen** op volgorde, met hun aantal velden.
Klik op een fase om haar te bewerken. Sleep een fase aan haar greep om de
volgorde te wijzigen. Voeg een fase toe door een naam te typen in
**Nieuwe fase, bijv. ‘Inspectie’** en op **Toevoegen** te klikken.

De gekozen fase wordt rechts getoond:

- Haar **naam** en **Beschrijving (optioneel)** kunnen ter plekke worden
  bewerkt. De beschrijving staat in een lopend proces bovenaan de fase.
- Het menu **⋮** (**Faseacties**) heeft **Omhoog**, **Omlaag** en **Fase
  verwijderen** (na **Deze fase met alle velden verwijderen?**).

### Velden {#fields}

Het tabblad **Velden** toont de velden van de fase met hun soort, opties,
hulptekst en een badge **Verplicht**. Een fase zonder velden is een
eenvoudige stap om af te vinken.

Om een veld toe te voegen, typt u de naam in **Nieuw veld: typ een naam,
druk op Enter**, kiest u de **Soort**, vinkt u zo nodig **Verplicht**
aan en drukt u op Enter of klikt u op **Veld toevoegen**. Bij **Keuze uit
lijst** opent eerst een zijpaneel, omdat een keuze haar opties nodig
heeft.

Sleep velden aan hun greep om de volgorde te wijzigen. Klik op een veld
om het paneel **Veld bewerken** te openen:

| Veld / knop | Wat het doet |
|---|---|
| **Label** | Verplicht, maximaal 200 tekens. |
| **Soort** | Een van de [veldsoorten](#field-types). |
| **Opties (alleen bij keuze, één per regel)** | Verplicht bij **Keuze uit lijst**: minstens één optie. |
| **Verplicht** | Het proces kan pas verder als dit veld is ingevuld. |
| **Hulptekst (optioneel)** | Getoond onder het veld in een lopend proces. |
| **Opslaan** / **Sluiten** | Slaat het veld op / sluit het paneel. |
| **Naar fase verplaatsen** + pijlknop | Verplaatst het veld naar het einde van een andere fase. |
| **Omhoog** / **Omlaag** | Wijzigt de volgorde, zonder slepen. |
| **Dupliceren** | Voegt er direct onder een kopie toe. |
| **Veld verwijderen** | Haalt het veld uit het sjabloon. |

Het tabblad **Voorbeeld** toont hoe de fase eruitziet in een lopend
proces, met de invoervelden uitgeschakeld.

## Uitgewerkt voorbeeld: een tuinoverdracht {#worked-example-a-plot-handover}

Een huurder heeft tuin 17 opgezegd. Zo voert het bestuur de overdracht
uit met het voorbeeld **Overdracht van een tuin**.

**Eén keer: het sjabloon inrichten.** Open **Processen → Sjablonen** en
klik op **Gebruiken** naast **Overdracht van een tuin**. U krijgt een
sjabloon over een **Tuin** met zes fasen:

| # | Fase | Velden (* = verplicht) |
|---|---|---|
| 1 | Inspectie | Datum van de inspectie*, Gevonden gebreken, Foto's van de gebreken, Alle gebreken verholpen* |
| 2 | Taxatie | Taxateur*, Datum van de taxatie*, Taxatierapport* (bestand) |
| 3 | Advertentie | Advertentietekst*, Foto's voor de advertentie, Gepubliceerd op* |
| 4 | Nieuwe huurder | Nieuwe huurder* (aanmelder), Contact gelegd*, Documenten verstuurd* |
| 5 | Contract en borg | Koopovereenkomst bevestigd*, Borg (bedrag), Borg ontvangen op |
| 6 | Overdracht | Ondertekend door de nieuwe huurder*, Medeondertekend door het bestuur*, Sleutels overhandigd*, Meters afgelezen*, Overdrachtsprotocol (bestand) |

Pas het aan uw vereniging aan: maak bijvoorbeeld **Borg** verplicht, of
voeg een veld **Keuze uit lijst** „Uitkomst taxatie“ toe met de opties
„Overname tegen taxatiewaarde“ en „Tuin moet worden ontruimd“.

**Elke keer: het uitvoeren.**

1. Open tuin 17 en klik op **Proces starten** in de kaart **Processen**.
   **Overdracht van een tuin** en de tuin zijn al gekozen. Vul de titel
   „Overdracht tuin 17“ in en klik op **Starten**.
2. **Inspectie**: vul na de rondgang de datum in, noteer de gebreken,
   upload foto's en klik op **Opslaan**. De fase kan nog niet worden
   afgerond: **Alle gebreken verholpen** is nog nodig. Zodra de huurder
   alles heeft hersteld, vinkt u het aan, **Opslaan**, dan **Klaar --
   volgende fase**.
3. **Taxatie**: vul taxateur en datum in, upload het rapport als PDF.
   Heeft de tuin een cloudmap, dan komt het rapport daar in een submap
   voor deze overdracht. **Klaar -- volgende fase**.
4. **Advertentie** en **Nieuwe huurder**: leg de advertentie vast, kies
   dan de gekozen persoon uit de lijst met aanmelders en vink de twee
   vakjes aan.
5. **Contract en borg**: bevestig de overeenkomst, vul de borg in en de
   dag waarop ze binnenkwam.
6. **Overdracht**: vink handtekeningen, sleutels en meterstanden aan,
   upload het overdrachtsprotocol, en klik op **Proces afronden**.

Haakt de nieuwe huurder in fase 5 af, gebruik dan **Teruggaan** om terug
te keren naar **Advertentie**, met de reden „Aanmelder trok zich terug“.
De tot nu toe ingevulde waarden blijven, en de geschiedenis toont wat er
gebeurde.

Het proces zelf legt alleen de overdracht vast. De oude huur beëindigen,
de nieuwe beginnen en de meters in Parcella aflezen doet u in de modules
[percelen](parcels.md) en [meters](metering.md) -- zie het
[stappenplan voor een perceeloverdracht](../guides/parcel-handover.md).

## Gerelateerd {#related}

- [Een perceel overdragen](../guides/parcel-handover.md)
- [Percelen](parcels.md), [Leden](members.md),
  [Aanmelders](applicants.md) -- de kaart **Processen** op hun pagina's.
- [Integraties](../administration/integrations.md) -- de map voor
  procesbestanden.
- [Groepen](../administration/groups.md) -- iemand rechten op processen
  geven.

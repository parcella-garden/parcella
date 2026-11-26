# De jaarfacturen opmaken {#running-the-annual-invoices}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Eens per jaar factureert de vereniging elk perceel: pacht, water,
elektriciteit, verzekering, gemiste werkuren, misschien contributie of
een eenmalige [omslag](../glossary.md#general-levy). In Parcella is dat
een [factuurronde](../glossary.md#invoice-run): u legt de factuurregels
één keer vast, controleert een voorbeeld van elke afzonderlijke factuur,
rondt af om factuurnummers toe te kennen, en verstuurt ze dan -- per
e-mail, op papier, of naar de cloudmap van elk perceel. Daarna legt u
betalingen vast en verstuurt u [herinneringen](../glossary.md#dunning).

!!! info "Wie kan dit doen"
    Alles hier vraagt **schrijf**recht op **Financiën**. De module
    **Financiën** staat op een nieuwe installatie **uit**; schakel haar
    in onder **Administratie → Instellingen → Functiegebieden** (zie
    [Modules in- en uitschakelen](../administration/modules.md)).

!!! warning "Afronden kan niet ongedaan worden gemaakt"
    Tot u afrondt, wordt niets als factuur opgeslagen en wordt niets
    verstuurd -- wijzig de regels zo vaak als u wilt. Afronden kent
    blijvende factuurnummers toe en vergrendelt de ronde. Download eerst
    een back-up (**Administratie → Systeem → Back-up downloaden**).

## 1. De financiële instellingen controleren (één keer) {#1-check-the-finance-settings-once}

1. Open **Administratie → Instellingen** en zoek **Financiële
   instellingen**.
2. Vul de bankgegevens van de vereniging in: **Naam van de bank**,
   **IBAN**, **BIC**, **Rekeninghouder**. Ze verschijnen in de voettekst
   van elke factuur.
3. Controleer het **Factuurnummerformaat**. De standaard is het jaar en
   een doorlopend nummer; u kunt een eigen formaat gebruiken,
   bijvoorbeeld `R-{year}-{number}`. `{number}` is verplicht.
4. Laat **Volgend factuurnummer (overschrijven)** leeg, tenzij de eerste
   factuurronde in Parcella een eerder gebruikte nummering moet
   voortzetten. Het wordt één keer gebruikt en daarna gewist.
5. Zorg dat **E-mail (SMTP)** is ingericht als u facturen wilt mailen.
6. Klik op **Instellingen opslaan**.

## 2. De artikelcatalogus voorbereiden (één keer, daarna hergebruiken) {#2-prepare-the-item-catalog-once-then-reuse}

De artikelcatalogus bevat de factuurregels die u elk jaar factureert,
zodat u ze niet voor elke ronde opnieuw hoeft vast te leggen.

1. Open **Financiën → Overzicht** en klik op **Artikelcatalogus**.
2. Vul onder **Nieuw artikelsjabloon** **Volgorde** (positie op de
   factuur), **Naam**, **Omschrijving**, de **Berekeningswijze**, de
   **Stukprijs** en eventueel een **Categorie** in.
3. Kies voor wie het geldt (zie hieronder) en klik op de knop **+**.

| Berekeningswijze | Wat ze factureert |
|---|---|
| **Vast bedrag per perceel** | De stukprijs één keer per perceel -- bijv. de pacht. |
| **Vast bedrag per persoon** | De stukprijs één keer per *lid* -- bijv. contributie, ook voor leden zonder perceel. |
| **Per gehuurde m²** | Stukprijs × de oppervlakte van het perceel. |
| **Aandeel in de pacht van het gemeenschappelijk terrein** | De gemeenschappelijke oppervlakte (Oppervlakte B), gelijk verdeeld over de gefactureerde percelen, × stukprijs. |
| **Publieke lasten (eigen oppervlakte + aandeel gemeenschappelijk terrein)** | De eigen oppervlakte van het perceel plus zijn aandeel in de gemeenschappelijke oppervlakte, × stukprijs. |
| **Algemene omslag (gelijk verdeeld over alle percelen)** | De stukprijs is een *totaal* bedrag dat gelijk over alle gefactureerde percelen wordt verdeeld. |
| **Waterverbruik (uit module)** | Het waterverbruik van het perceel × de waterprijs voor het jaar. |
| **Stroomverbruik (uit module)** | Het elektriciteitsverbruik van het perceel × de elektriciteitsprijs voor het jaar. |
| **Verzekeringskosten (uit module)** | De verzekering van het perceel, één regel per soort verzekering. |
| **Tekort werkuren (uit module)** | Ontbrekende [verplichte uren](../glossary.md#mandatory-hours) × het uurtarief. |

**Voor wie een regel geldt.** Perceelgebonden regels hebben **Geldt voor
elk perceel**; vink het uit om afzonderlijke **Percelen** te kiezen.
**Vast bedrag per persoon** heeft in plaats daarvan **Geldt voor elk lid**
en een keuzelijst **Leden**. De vier regels „uit module“ kiezen hun
percelen zelf -- in plaats van een keuzelijst staat er **Automatisch
(...)** -- en hun stukprijs **Wordt automatisch berekend**.

Meer: [Factuurrondes](../modules/finances/invoice-runs.md).

## 3. De getallen controleren die de automatische regels gebruiken {#3-check-the-numbers-the-automatic-items-use}

De regels „uit module“ halen hun getallen uit andere modules. Controleer
ze voor het jaar dat u factureert **vóór** u afrondt.

**Water en elektriciteit**

1. Open **Water → Configuratie** en controleer of er voor het jaar een
   prijs (**Prijs per m³**) bestaat (in **Prijsgeschiedenis**). Zo niet,
   vul dan onder **Nieuwe/bijgewerkte prijs** **Jaar** en prijs in en
   klik op **Opslaan**. Doe hetzelfde onder **Elektriciteit →
   Configuratie**.
2. Open **Water → Overzicht**. Zegt het dat sommige meetpunten nog geen
   stand voor het jaar hebben, verzamel die dan eerst -- zie
   [Meterstanden opnemen](meter-readings.md). Een perceel zonder stand
   voor het jaar krijgt helemaal geen waterregel.
3. Open **Water → Evaluatie** voor het jaar en zoek naar percelen met
   **geen stand** of onwaarschijnlijk verbruik.

**Werkuren**

1. Open **Werksessies → Sessies & Overzicht** en controleer de
   **Urenconfiguratie** van het jaar: vereiste uren en **Uurtarief**.
2. Open **Werksessies → Jaarlijkse evaluatie** voor het jaar. Controleer
   de kolommen **Openstaand** en **Schuld** -- dat wordt gefactureerd.
   Ontbreken aanwezigheden, sponsorschappen of vrijstellingen? Herstel ze
   nu (zie [Een werksessie organiseren](work-session.md)).

**Verzekering**

1. Open **Verzekering → Configuratie** en **Verzekering → Perceel** en
   controleer de prijzen van het jaar en de verzekering van elk perceel.

!!! tip "Wie de factuur krijgt"
    Een perceelfactuur gaat naar de huidige huurders van het perceel die
    zijn gemarkeerd met **Gebruiken als factuuradres**. Percelen zonder
    zo'n huurder krijgen geen factuur. Controleer dit op de
    perceelpagina's vóór u afrondt -- vooral na een overdracht.

## 4. De factuurronde aanmaken {#4-create-the-invoice-run}

1. Open **Financiën → Uitgaande facturen** (de pagina heet **Jaarlijkse
   facturen**).
2. Klik op **Nieuwe factuurronde**.
3. Vul het gefactureerde **Jaar** in, een **Onderwerp** (bijv.
   „Jaarfactuur 2026“), de **Factuurdatum** en de **Vervaldatum**.
4. Schrijf eventueel een **Voettekst**. Die mag `{invoice_number}`,
   `{parcel_number}`, `{invoice_address}` en `{due_date}` bevatten, die
   per factuur worden ingevuld.
5. Klik op **Aanmaken**.

De ronde is een **Concept**. Open haar met **Openen**.

## 5. De factuurregels toevoegen {#5-add-the-line-items}

1. Vink op de pagina van de ronde, onder **Toevoegen uit
   artikelcatalogus**, de catalogusitems voor dit jaar aan en klik op
   **Geselecteerde items toevoegen**.
2. Vul voor alles wat alleen dit jaar wordt gefactureerd onderaan **Regel
   toevoegen** in, op dezelfde manier als in de catalogus.
3. Controleer de tabel **Regeldefinities**: volgorde, prijzen, voor wie
   elke regel geldt. Zolang de ronde een concept is, kunt u regels nog
   bewerken of verwijderen.

## 6. Voorbeeld {#6-preview}

1. Klik bovenaan de pagina van de ronde op **Voorbeeld**.
2. De pagina zegt hoeveel facturen er zouden worden gegenereerd en toont
   ze onder **Berekende facturen**, met ontvanger en subtotaal.
3. Open er een paar met **PDF** en controleer ze: adres, regels,
   bedragen, voettekst.
4. Om iets te herstellen, gaat u **Terug naar factuurronde**, wijzigt u
   de regels, en bekijkt u het voorbeeld opnieuw. Er is nog niets
   opgeslagen of verzonden.

Zegt het *„Er zouden geen facturen worden gegenereerd“*, controleer dan
het perceelbereik van de regels en de vlag **Gebruiken als factuuradres**
van de huurders.

## 7. Afronden {#7-finalize}

1. Klik op de voorbeeldpagina op **Afronden en factuurnummers toekennen**
   en bevestig.
2. Parcella maakt de facturen aan met blijvende nummers. De pagina van de
   ronde zegt nu dat ze is afgerond en toont de **Facturen**.

Namen en adressen van de ontvangers worden op elke factuur opgeslagen
zoals ze op dit moment zijn. Latere adreswijzigingen herschrijven
afgeronde facturen niet.

## 8. De facturen versturen {#8-send-the-invoices}

1. Zoek op de pagina van de afgeronde ronde de kaart **Verzending**.
2. Klik op **E-mails versturen & naar cloud uploaden**.
    - Facturen worden gemaild (PDF als bijlage) naar factuurontvangers
      die **Mag informatie per e-mail ontvangen** en een e-mailadres
      hebben.
    - Heeft het perceel een documentenmap in de cloudopslag, dan wordt de
      factuur daar ook geüpload.
    - Nogmaals klikken verstuurt alleen wat nog niet is verstuurd.
3. Klik op **Afdrukbundel downloaden**. Die bevat een brief voor elke
   huurder die geen facturen per e-mail krijgt, als één PDF om af te
   drukken en te posten: één brief per adres, met de namen van wie daar
   geen e-mail heeft. Dat geldt ook voor iemand van wie een huisgenoot de
   e-mail kreeg. Ze worden daarna gemarkeerd als opgenomen in een
   afdrukbundel.

De kolom **Verzending** toont per factuur of ze **Verstuurd per e-mail**,
**Opgenomen in een afdrukbundel** of **Geüpload naar cloudopslag** is. Om
één factuur opnieuw te versturen, opent u haar en klikt u op **E-mail
opnieuw versturen**.

Meer: [Facturen, betalingen en herinneringen](../modules/finances/invoices.md).

## 9. Betalingen vastleggen {#9-record-payments}

**Met de hand**

1. Open de ronde (of **Alle facturen** op **Jaarlijkse facturen** om over
   alle rondes heen te zoeken op factuurnummer, ontvanger of bedrag).
2. Klik op **Betaling** in de rij van de factuur.
3. Vul **Bedrag**, **Betaald op**, eventueel een **Notitie** en de
   **Rekening** waarop het binnenkwam in, en klik op **Betaling
   toevoegen**.

Deelbetalingen zijn prima; de status verandert vanzelf van **Open** naar
**Gedeeltelijk betaald** naar **Betaald**.

**Uit het bankafschrift**

1. Eén keer: open **Financiën → Overzicht → Rekeningen** en voeg uw
   bankrekening toe onder **Nieuwe rekening**.
2. Klik op het boekingenpictogram naast de rekening, dan op **CSV
   importeren**.
3. Upload het afschrift dat u uit internetbankieren hebt geëxporteerd.
   Koppel op **CSV-kolommen koppelen** minstens **Datum** en **Bedrag**;
   **Omschrijving**, **Afzender / ontvanger** en **IBAN** helpen bij het
   koppelen.
4. Op **Rijen koppelen aan facturen** stelt Parcella voor elke
   binnenkomende betaling open facturen met hetzelfde bedrag voor. Kies
   de juiste om haar als betaling van die factuur vast te leggen, of kies
   **Registreren als gewone boeking**.
5. Klik onderaan de pagina op **CSV importeren** om de boekingen en
   betalingen aan te maken.

Meer: [Bankrekeningen en boekingen](../modules/finances/bank-accounts.md).

## 10. Herinneringen versturen {#10-send-reminders}

1. Open na de vervaldatum **Financiën → Herinneringen**. **Achterstallige
   facturen** toont elke onbetaalde factuur voorbij haar vervaldatum, met
   hoe lang ze achterstallig is en hoeveel herinneringen er zijn
   verstuurd.
2. Klik op **Openen** naast een factuur.
3. Vul eventueel **Kosten (optioneel)** en een **Bericht (optioneel)**
   in.
4. Klik op **Herinnering versturen**.

Parcella maakt de volgende herinnering als PDF (**Herinnering nr. 1**,
**nr. 2**, …), telt de kosten op bij het verschuldigde bedrag, en mailt
haar als het lid voor e-mail heeft gekozen; anders wordt ze gemarkeerd als
**Om te printen/per post te versturen**, zodat u haar afdrukt en post. Er
zijn geen vaste aanmaningsniveaus -- u beslist wanneer de volgende gaat.

## Gerelateerd {#related}

- [Financiën](../modules/finances/index.md)
- [Factuurrondes](../modules/finances/invoice-runs.md)
- [Facturen, betalingen en herinneringen](../modules/finances/invoices.md)
- [Bankrekeningen en boekingen](../modules/finances/bank-accounts.md)
- [Categorieën, begroting en overzicht](../modules/finances/bookkeeping.md)
- [Water en elektriciteit](../modules/metering.md)
- [Werkuren](../modules/work-hours.md)
- [Verzekering](../modules/insurance.md)
- [Meterstanden opnemen](meter-readings.md)

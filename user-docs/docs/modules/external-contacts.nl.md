# Externe contacten {#external-contacts}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Externe contacten is het adresboek van de vereniging voor iedereen die
geen lid is: leveranciers, vaklui, het waterbedrijf, de gemeente. Een
contact is een **bedrijf** of een **persoon**, en een persoon kan bij een
bedrijf werken. U kunt contacten koppelen aan inkomende facturen en
aankoopaanvragen, ze labelen, en hun documenten in de cloud van de
vereniging bewaren.

!!! info "Wie kan dit gebruiken"
    Bestuursleden en beheerders hebben altijd volledige toegang. Alle
    anderen zien niets van deze module tot een groep rechten op
    **Externe contacten** geeft (zie [Groepen](../administration/groups.md)):

    - **Lezen** -- de lijst en de contactpagina's zien, CSV exporteren,
      de labelpagina zien, documenten downloaden.
    - **Schrijven** -- contacten aanmaken en bewerken, telefoonnummers,
      e-mailadressen en labels toevoegen, labels hernoemen, CSV
      importeren, de documentenmap van een contact kiezen en documenten
      uploaden.
    - **Verwijderen** -- contacten, telefoonnummers, e-mailadressen en
      labels verwijderen, en bedrijven samenvoegen.

    De module wordt ingeschakeld met **Externe contacten** onder
    [Modules in- en uitschakelen](../administration/modules.md). Ze staat
    standaard aan.

## Bedrijven en personen {#companies-and-people}

- Een **bedrijf** heeft een bedrijfsnaam, een adres, een IBAN en eigen
  telefoonnummers en e-mailadressen.
- Een **persoon** heeft een voor- en achternaam, een functie (bijv.
  „Medewerker“, „Eigenaar“) en optioneel een bedrijf. Heeft de persoon
  geen eigen adres of IBAN, dan toont zijn pagina die van het bedrijf.
- Of een contact een bedrijf of een persoon is, wordt bij het aanmaken
  bepaald en kan later niet worden gewijzigd.
- Een bedrijfsnaam mag maar één keer bestaan, en een persoonsnaam ook
  (hoofdletters maken niet uit). Leden tellen niet mee -- een contact
  mag dezelfde naam hebben als een lid.
- Elk veld is optioneel. Een contact zonder naam wordt getoond als
  **Naamloos contact**.

## Lijst met contacten {#contact-list}

![Externe contacten](../assets/screenshots/external-contacts/list.png)

**Externe contacten** in de navigatie toont elk bedrijf, met zijn
personen ingesprongen eronder, en elke persoon die niet bij een bedrijf
hoort. De lijst is alfabetisch gesorteerd op bedrijfsnaam, of op
achternaam bij personen zonder bedrijf.

| Veld / knop | Wat het doet |
|---|---|
| **CSV-import** | Opent het [importvenster](#csv-import). Vraagt schrijfrecht. |
| **CSV-export** | Downloadt de lijst als CSV-bestand (zie [CSV-export](#csv-export)). Gebruikt de huidige zoekopdracht en het labelfilter. |
| **Labels beheren** | Opent de [labelpagina](#contact-tags). |
| **Nieuw contact** | Opent het [contactformulier](#contact-form). Vraagt schrijfrecht. |
| Zoekveld | Doorzoekt bedrijfsnaam, voor- en achternaam, functie, straat, postcode, plaats, IBAN, notities, telefoonnummers en e-mailadressen. Klik op **Zoeken** om toe te passen. |
| **Alle labels** / een label | Toont alleen contacten met dat label. Alleen zichtbaar als er labels bestaan. |
| **Wissen** | Wist zoekopdracht en labelfilter. Alleen zichtbaar zolang er een filter actief is. |

| Kolom | Wat ze toont |
|---|---|
| **Naam** | Een gebouwpictogram bij bedrijven, een persoonspictogram bij personen; de naam linkt naar de contactpagina. Personen tonen hun functie na de naam. |
| **Tags** | De labels van het contact. Klik op een label om de lijst erop te filteren. |
| **Telefoon** | Het eerste telefoonnummer. |
| **E-mail** | Het eerste e-mailadres, als maillink. |
| Oogknop | Opent het contact. |

Komt een zoekopdracht of label overeen met een persoon, dan wordt ook
zijn bedrijf getoond, met de overeenkomende persoon eronder gemarkeerd.
Onderaan staat hoeveel items (bedrijven en personen zonder bedrijf) er
getoond worden.

## Contactformulier {#contact-form}

![Nieuw extern contact](../assets/screenshots/external-contacts/form-new.png)

**Nieuw contact** opent een leeg formulier, **Bewerken** op een
contactpagina het ingevulde. **Persoon toevoegen** op de pagina van een
bedrijf opent het als nieuwe persoon met het bedrijf al ingevuld.

Kies bij een nieuw contact eerst bovenaan **Bedrijf** of **Persoon**
(**Soort contact**). Het formulier toont dan alleen de velden voor die
soort.

### Bedrijf / Persoon {#company-person}

| Veld | Getoond bij | Wat het doet |
|---|---|---|
| **Voornaam**, **Achternaam** | Persoon | De naam van de persoon. Een van beide is genoeg. |
| **Bedrijfsnaam** | Bedrijf | De naam van het bedrijf. |
| **Bedrijf (optioneel)** | Persoon | Het bedrijf waar de persoon werkt. Stelt bestaande bedrijven voor terwijl u typt. Een bestaand bedrijf wordt gekoppeld; een nieuwe naam maakt dat bedrijf aan. Laat leeg voor een persoon op zichzelf. Bij **Bewerken** haalt leegmaken de persoon uit het bedrijf. |
| **Functie** | Persoon | Bijv. „medewerker, eigenaar“. |
| **E-mail**, **Telefoon** | Nieuwe contacten | Het eerste e-mailadres en telefoonnummer. Meer voegt u later toe op de contactpagina. |

De notitie „Alle velden zijn optioneel. Een bedrijfsnaam en een
persoonsnaam mogen elk maar één keer voorkomen.“ herinnert u aan de
[regels hierboven](#companies-and-people).

### Adres en bankgegevens {#address-bank-details}

| Veld | Wat het doet |
|---|---|
| **Straat**, **Postcode**, **Plaats** | Het postadres. |
| **IBAN** | Bankrekening, bijv. om de facturen van de leverancier te betalen. Maximaal 34 tekens. |

Bij een persoon bij een bedrijf: „Leeg laten om die van het bedrijf te
gebruiken. Samen met een nieuw bedrijf ingevuld, wordt het het adres van
het bedrijf.“ Heeft het bedrijf nog geen adres of IBAN, dan wordt wat u
invult bij het bedrijf opgeslagen; is het hetzelfde als dat van het
bedrijf, dan wordt het niet dubbel opgeslagen. Alleen een adres of IBAN
dat echt afwijkt, blijft bij de persoon.

### Notities en labels {#notes-and-tags}

| Veld | Wat het doet |
|---|---|
| **Notities** | Vrije tekst -- openingstijden, klantnummer, een ticketnummer. De zoekfunctie van de lijst vindt het. |
| Labelvinkjes | Vink bestaande labels aan. |
| **Nieuwe labels, gescheiden door komma's** | Typ nieuwe labels; ze worden aangemaakt en toegevoegd. |

Klik op **Contact aanmaken** (nieuw) of **Wijzigingen opslaan**
(bewerken), of op **Annuleren**. Bestaat er al een bedrijf of persoon met
dezelfde naam, dan komt het formulier terug met een melding zoals „Er
bestaat al een bedrijf …“ en houdt het vast wat u hebt getypt.

## Contactpagina {#contact-page}

<!-- TODO(verify): no screenshot -- the sample data contains no external contacts, so the screenshot tool has no contact page to open. Add one once sample data seeds contacts. -->

### Knoppen {#buttons}

| Knop | Wat het doet |
|---|---|
| **Bewerken** | Opent het contactformulier. Vraagt schrijfrecht. |
| **Vorige** / **Volgende** | Het vorige of volgende item van de lijst, met behoud van zoekopdracht en labelfilter. Toetsenbord: ++ctrl+left++ en ++ctrl+right++. |
| **Naar de lijst** | Terug naar de lijst met hetzelfde filter. |

### Bedrijf / Persoon {#company-person_1}

| Veld | Wat het toont |
|---|---|
| **Bedrijf** (bedrijf) | De bedrijfsnaam. |
| **Naam**, **Functie**, **Bedrijf** (persoon) | Naam en functie van de persoon en een link naar zijn bedrijf. Een verwijderd bedrijf is gemarkeerd met „(verwijderd)“. |
| **Adres** | Het adres van het contact. Bij een persoon zonder eigen adres dat van het bedrijf, gemarkeerd als **Adres van het bedrijf**. |
| **IBAN** | De IBAN van het contact. Bij een persoon zonder eigen IBAN die van het bedrijf, gemarkeerd als **IBAN van het bedrijf**. |

### Personen {#people}

Alleen op de pagina van een bedrijf: elke persoon bij het bedrijf, met
functie, telefoonnummers en e-mailadressen. **Persoon toevoegen** maakt
een nieuwe persoon bij dit bedrijf aan (schrijfrecht). „Nog geen personen
bij dit bedrijf.“ als er geen zijn.

### Labels {#tags}

De labels van het contact; klik op een label om alle contacten ermee te
zien. Met schrijfrecht haalt de **x** op een label het bij dit contact
weg, en het veld **Label toevoegen…** voegt een bestaand of nieuw label
toe (maximaal 100 tekens). **Labels beheren** opent de
[labelpagina](#contact-tags).

### Telefoonnummers en e-mailadressen {#phone-numbers-and-email-addresses}

| Veld / knop | Wat het doet |
|---|---|
| Nummer / adres | Klik om te bellen of een e-mail te schrijven. Een omschrijving staat tussen haakjes. |
| Nummer- / adresveld, **Omschrijving (optioneel)**, **+** | Voegt nog een nummer of adres toe, bijv. met de omschrijving „Kantoor“ of „Facturen“. Vraagt schrijfrecht. |
| Prullenbakknop | Verwijdert het nummer of adres. Vraagt verwijderrecht. |

### Inkomende facturen en aankoopaanvragen {#incoming-invoices-and-purchase-requests}

Toont de [inkomende facturen](finances/incoming-invoices.md) en
[aankoopaanvragen](purchase-requests.md) die aan dit contact zijn
gekoppeld -- op de pagina van een bedrijf ook die van zijn personen, met
de naam van de persoon achter het item. Elke kaart wordt alleen getoond
als die module aan staat en u haar mag lezen.

| Kaart | Kolommen |
|---|---|
| **Inkomende facturen** | Factuurdatum, factuurnummer (of afzender), totaalbedrag. |
| **Inkoopaanvragen** | Aanmaakdatum, titel, geschatte kosten. |

### Documenten {#documents}

Getoond als de module Cloudopslag aan staat. Brieven, offertes en
contracten worden niet in Parcella bewaard maar in een map in de cloud
van de vereniging; deze kaart toont die map.

- Een beheerder stelt eerst de basismap in onder
  [Integraties](../administration/integrations.md) (**Map voor
  documenten van externe contacten**). Tot dan zegt de kaart dat.
- De map voor elk contact wordt met de hand in de cloud aangemaakt,
  binnen de basismap. Op de contactpagina kiest iemand met schrijfrecht
  haar dan uit de lijst **Map** en klikt op **Map opslaan**. **Map
  wijzigen** kiest een andere; **— geen map —** ontkoppelt haar (de
  bestanden blijven in de cloud).
- Is er een map gekozen, dan toont de kaart haar bestanden en submappen.
  Klik op een submap om die te openen, op een bestand om het te
  downloaden. Het pad boven de lijst leidt terug omhoog.
- Met schrijfrecht zet **Uploaden** een bestand in de map die nu wordt
  getoond.
- Bestanden verwijderen, hernoemen en verplaatsen doet u in de cloud
  zelf.

Documenten horen bij het bedrijf: de pagina van een persoon linkt in
plaats daarvan naar de documenten van het bedrijf („Documenten worden
bij het bedrijf bewaard:“).

!!! warning
    Hernoemt u de map van een contact in de cloud, dan verliest Parcella
    haar uit het oog. Kies haar opnieuw op de contactpagina.

### Notities {#notes}

De notities, als die er zijn.

### Gevarenzone {#danger-zone}

Getoond met verwijderrecht.

| Veld / knop | Wat het doet |
|---|---|
| **Samenvoegen met** + **Samenvoegen** | Alleen op de pagina van een bedrijf. Voor twee vermeldingen van hetzelfde bedrijf (bijv. „Müller GmbH“ en „Mueller GmbH“): kies het bedrijf dat blijft en klik op **Samenvoegen**, bevestig dan. Personen, telefoonnummers, e-mailadressen, labels en gekoppelde facturen en aankoopaanvragen gaan naar het gekozen bedrijf. Adres, IBAN en documentenmap worden aangevuld vanuit dit bedrijf waar het gekozen bedrijf er geen heeft; notities worden aan de notities toegevoegd. Dit bedrijf wordt daarna verwijderd, en het bewaarde bedrijf opent. |
| **Contact verwijderen** | Verwijdert het contact na bevestiging. Het verdwijnt uit de lijst en de keuzevelden, maar gekoppelde facturen en aankoopaanvragen tonen het nog steeds (gemarkeerd als „verwijderd“ waar ze het tonen). De naam komt weer vrij. Een bedrijf dat nog personen heeft, kan niet worden verwijderd: „Dit bedrijf heeft nog personen. Verplaats of verwijder die eerst.“ |

## Contactlabels {#contact-tags}

![Contactlabels](../assets/screenshots/external-contacts/tags.png)

**Labels beheren** opent **Contactlabels**. Contactlabels staan los van
de ledentags. **Terug naar contacten** brengt u naar de lijst.

| Veld / knop | Wat het doet |
|---|---|
| **Markeert aanvragers:** | Kies één label (of **— geen —**) en klik op **Opslaan**. Aanmelders van wie naam, e-mailadres of telefoonnummer overeenkomt met een contact met dit label, krijgen een rode vlag in de lijst met aanmelders en een waarschuwing op hun pagina -- handig voor een label „niet verhuren“. Een gelabeld bedrijf markeert ook zijn personen. Alleen zichtbaar als de module Aanmelders aan staat en er labels bestaan; wijzigen vraagt schrijfrecht. Zie [Aanmelders](applicants.md). |
| Labelnaam + vinkknop | Hernoemt het label bij elk contact. Vraagt schrijfrecht. Een naam die al bestaat, wordt geweigerd. |
| **{aantal} contact(en)** | Opent de lijst gefilterd op dit label. |
| Prullenbakknop | Verwijdert het label bij elk contact, na bevestiging. Vraagt verwijderrecht. |
| **Vertalingen** | Opent één veld per taal. De naam van een label kan per taal anders worden getoond; lege velden tonen de eigen naam van het label. **Vertalingen opslaan** slaat ze op (schrijfrecht). |

Nieuwe labels worden bij een contact of in het contactformulier
aangemaakt, niet op deze pagina.

## CSV-export {#csv-export}

**CSV-export** downloadt `external-contacts.csv`: gescheiden door
puntkomma's, één rij per bedrijf of persoon, met de kolommen Typ, Firma,
Vorname, Nachname, Position, Strasse, PLZ, Ort, IBAN, E-Mail-Adressen,
Telefonnummern, Tags, Notizen (type, bedrijf, voornaam, achternaam,
functie, straat, postcode, plaats, IBAN, e-mailadressen,
telefoonnummers, labels, notities). „Typ“ is „Firma“ of „Person“. Elk
bedrijf komt eerst, gevolgd door zijn personen. Meerdere e-mailadressen,
nummers of labels delen één cel, gescheiden door puntkomma's.

Het bestand kan ongewijzigd opnieuw worden geïmporteerd.

## CSV-import {#csv-import}

De import heeft twee stappen en vraagt schrijfrecht.

### Stap 1: het bestand kiezen {#step-1-choose-the-file}

**CSV-import** in de lijst opent **Contacten importeren uit CSV**. Kies
een `.csv`-bestand (gescheiden door puntkomma of komma, met een
kopregel) en klik op **Importeren**. Er wordt nog niets opgeslagen.

### Stap 2: Contacten importeren {#step-2-import-contacts}

<!-- TODO(verify): no screenshot -- this screen is only reachable by uploading a file, which the screenshot tool can't do from a URL. -->

De kaart **Kolommen koppelen** toont elke kolom van uw bestand met de
kop en de eerste vijf rijen. Kies voor elke kolom het veld waar ze in
hoort, of **— negeren —**:

**Type (bedrijf/persoon)**, **Bedrijfsnaam**, **Voornaam**,
**Achternaam**, **Functie**, **Straat**, **Postcode**, **Plaats**,
**IBAN**, **E-mailadressen**, **Telefoonnummers**, **Labels**,
**Notities**.

Parcella kiest alvast het veld bij gangbare Duitse en Engelse koppen, en
koppelt zijn eigen export volledig. Geen enkel veld is verplicht. Klik op
**Importeren** om het uit te voeren; **Terug** annuleert.

Zo wordt elke rij behandeld:

- **Bedrijf of persoon:** de kolom type zegt „Firma“/„Company“ of
  „Person“. Zonder die kolom is een rij met een voor- of achternaam een
  persoon, anders een bedrijf.
- **Bestaande contacten worden bijgewerkt:** een bedrijf wordt
  gevonden op zijn naam, een persoon op voor- en achternaam
  (hoofdletters maken niet uit). De gevonden vermelding krijgt elk veld
  dat in het bestand is ingevuld; telefoonnummers, e-mailadressen en
  labels die ze nog niet heeft, worden toegevoegd. Er wordt nooit iets
  verwijderd of leeggemaakt.
- **Nieuwe contacten** worden aangemaakt voor rijen zonder
  overeenkomst.
- **Het bedrijf van een persoon:** de bedrijfskolom koppelt de persoon
  aan het bedrijf met die naam, dat zo nodig wordt aangemaakt. Adres en
  IBAN van de rij vullen aan wat dat bedrijf mist, en blijven alleen bij
  de persoon waar ze afwijken.
- Volledig lege rijen worden overgeslagen.

Daarna toont de lijst een samenvatting, bijv. „3 contact(en) aangemaakt,
1 bijgewerkt.“, plus de eerste problemen als er rijen zijn overgeslagen
(bijv. een dubbele naam).

## Waar contacten elders worden gekozen {#where-contacts-are-picked-elsewhere}

Staat deze module aan en mag u contacten lezen, dan bieden andere modules
een keuzeveld voor contacten. Bedrijven verschijnen als groep met hun
personen eronder; verwijderde contacten worden niet aangeboden.

| Waar | Label | Wat het doet |
|---|---|---|
| [Inkomende facturen](finances/incoming-invoices.md) -- nieuwe factuur | **Contact** | Een contact kiezen vult de afzender in. De afzender blijft een vrij tekstveld. |
| Pagina van een inkomende factuur | **Contact** | Het gekoppelde contact later instellen of wijzigen. |
| [Aankoopaanvragen](purchase-requests.md) -- nieuwe aanvraag en pagina van een aanvraag | **Leverancier (contact)** | De leverancier voor de aankoop. Kan in elke status worden gewijzigd. |

## Gerelateerd {#related}

- [Aanmelders](applicants.md) -- rode vlaggen door gelabelde contacten
- [Integraties](../administration/integrations.md) -- cloudopslag en de
  basismap voor documenten
- [Groepen](../administration/groups.md) -- de penningmeester toegang
  tot contacten geven

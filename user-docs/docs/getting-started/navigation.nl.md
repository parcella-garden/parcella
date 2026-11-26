# Uw weg vinden {#finding-your-way-around}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Elke pagina in Parcella heeft hetzelfde kader: een groene **zijbalk**
links met de navigatie, en een witte **bovenbalk** boven de pagina met de
paginatitel en de knoppen voor die pagina.

!!! info "Wie kan dit gebruiken"
    Iedereen die is ingelogd. Welke items *u* ziet, hangt af van de
    modules die uw vereniging heeft ingeschakeld en van uw rechten --
    zie [Waarom items verschijnen en verdwijnen](#why-entries-appear-and-disappear).

![Zijbalk en bovenbalk](../assets/screenshots/getting-started/navigation.png)

## De zijbalk {#the-sidebar}

Van boven naar beneden bevat de zijbalk:

1. **De naam en het logo van uw vereniging**, met daaronder het woord
   **Beheer**.
2. **De navigatie-items** -- één per module.
3. **Administratie** -- alleen voor beheerders, altijd helemaal
   onderaan de lijst.
4. **De voettekst** met uw eigen account.

### Losse items en groepen {#single-entries-and-groups}

Kleinere modules zijn één link, bijvoorbeeld **Leden**, **Perceel**,
**Inventaris** of **Notities**. Klik erop en de module opent.

Grotere modules zijn een **groep**: een kop in hoofdletters met een
klein pijltje. Klikken op de kop klapt de pagina's uit:

| Groep | Pagina's erin |
|---|---|
| **Werksessies** | **Sessies & Overzicht**, **Jaarlijkse evaluatie**, **Sponsorschappen**, **Uren overdragen**, **Taken** |
| **Water** | **Overzicht**, **Meetpunten**, **Meterstanden**, **Evaluatie**, **Configuratie** |
| **Elektriciteit** | **Overzicht**, **Meetpunten**, **Meterstanden**, **Evaluatie**, **Configuratie** |
| **Verzekering** | **Overzicht**, **Perceel**, **Configuratie**, **Evaluatie** |
| **Kalender** | **Verenigingskalender**, **Verjaardagen**, **Aanwezigheid bestuur**, **Afwezigheid bestuur**, **Eigen agenda's** |
| **Financiën** | **Overzicht**, **Uitgaande facturen**, **Herinneringen**, **Inkomende facturen** |
| **Administratie** | **Systeem**, **Gebruikers**, **Groepen**, **API-tokens**, **Instellingen**, **Integraties**, **E-maillogboek**, **Voorbeeldgegevens**, **API-documentatie (Swagger)** |

Er is **telkens maar één groep open**: een groep openen klapt de eerder
geopende in, zodat de zijbalk kort blijft. De groep met de pagina
waarop u bent, opent altijd vanzelf. Verder onthoudt uw browser welke
groep u het laatst opende.

De pagina waarop u bent, is gemarkeerd met een lichte balk aan de
linkerkant.

**API-documentatie (Swagger)** opent de technische beschrijving van de
programmeerinterface van Parcella in een nieuw browsertabblad. Die is
bedoeld voor mensen die andere software koppelen; verder kunt u haar
negeren.

### Badges: zaken die aandacht vragen {#badges-things-that-need-attention}

Sommige items tonen een klein rood getal. Dat zegt hoeveel zaken daar
wachten. Beweeg de muis erover om te zien wat het telt.

| Item | De badge telt |
|---|---|
| **Werksessies** en **Sessies & Overzicht** | Nieuwe aanmeldingen voor komende werksessies van de laatste 14 dagen die nog niemand als bekeken heeft gemarkeerd. |
| **Aankoopaanvragen** | Aanvragen die nog op een beslissing wachten. |
| **Aanmelders** | Nieuwe aanmeldingen waar nog niemand naar heeft gekeken. |
| **Ondersteuning** | Open gesprekken (actief of in afwachting) in de helpdesk van de vereniging. |
| **Takenbord** | Taken waarvan de vervaldatum is verstreken en die niet klaar zijn. |

Een badge verdwijnt vanzelf zodra de zaak is afgehandeld -- bijvoorbeeld
wanneer de aankoopaanvraag is goedgekeurd of afgewezen, of de taak klaar
is. Er is geen „markeren als gelezen“. Dezelfde getallen verschijnen als
tegels op het [Dashboard](dashboard.md).

### De voettekst: uw account {#the-footer-your-account}

Onderaan de zijbalk ziet u uw avatar en naam, en daaronder de groepen
waartoe u behoort (of **Beheerder** / **Bestuur** bij oudere accounts die
een rol hebben in plaats van groepen -- zie
[Rollen, groepen en rechten](roles-and-permissions.md)).

| Knop | Wat het doet |
|---|---|
| **Wachtwoord wijzigen** | Opent uw profiel: wachtwoord, avatar en API-tokens. Zie [Eerste aanmelding en uw account](first-login.md#change-password). |
| **Uitloggen** | Logt u uit en brengt u terug naar de inlogpagina. |

## De bovenbalk {#the-top-bar}

De bovenbalk toont links de titel van de huidige pagina. Rechts staan de
acties voor deze pagina, zoals **Nieuw lid**, een export of een
terugknop. De bovenbalk blijft zichtbaar wanneer u in een lange lijst
naar beneden scrolt.

## Waarom items verschijnen en verdwijnen {#why-entries-appear-and-disappear}

Een item wordt alleen getoond als **allebei** waar is:

1. **De module is ingeschakeld** voor uw vereniging. Beheerders
   schakelen modules in en uit onder
   [Modules in- en uitschakelen](../administration/modules.md). Een
   uitgeschakelde module verdwijnt voor iedereen -- de gegevens blijven
   bewaard en komen terug als de module weer wordt ingeschakeld.
2. **U mag het lezen.** Bestuursleden en beheerders zien elke
   ingeschakelde module. Alle anderen zien **Leden** en **Perceel** plus
   de modules waarvoor een van hun groepen **Lezen** geeft. Zie
   [Rollen, groepen en rechten](roles-and-permissions.md).

Een paar items volgen een eigen regel:

- **Takenbord** en **Mededelingen** worden alleen getoond aan mensen met
  volledige toegang (bestuursleden, beheerders, of een groep met
  **Volledige toegang tot elke module**). Groepen kunnen ze niet apart
  toekennen.
- **Ondersteuning**: met leesrecht voor **Support (helpdesk)** krijgt u
  de eigen lijst met gesprekken in Parcella. Zonder dat recht verschijnt
  het item nog steeds als de helpdesk van uw vereniging een webadres
  heeft, en opent het dan de helpdesk zelf in een nieuw tabblad.
- **Administratie** wordt alleen aan beheerders getoond.

Opent u een pagina die u niet mag zien -- via een bladwijzer of een link
van een collega --, dan krijgt u de melding **U heeft hier geen
toestemming voor**. Een pagina van een uitgeschakelde module antwoordt
met een pagina „niet gevonden“: „Deze functie is voor deze vereniging
uitgeschakeld.“

### De volgorde van de items {#the-order-of-the-entries}

Uw vereniging bepaalt de volgorde van de items. Een beheerder stelt die in
onder [Verenigingsinstellingen](../administration/settings.md#navigation-order).
De volgorde is voor iedereen gelijk.

## Sneltoets voor detailpagina's {#keyboard-shortcut-for-detail-pages}

Op detailpagina's met de knoppen **Vorige** en **Volgende** -- leden,
percelen, meetpunten, de verzekeringspagina van een perceel en externe
contacten -- springen **Ctrl + ←** en **Ctrl + →** naar het vorige en
volgende record, net als die knoppen. De sneltoets doet niets terwijl u
in een veld typt.

!!! note "Mac-gebruikers"
    Op een Mac wisselen Ctrl + pijltjestoetsen meestal tussen
    bureaubladen („Spaces“), zodat het systeem de sneltoets onderschept
    voordat Parcella hem ziet. Gebruik dan de knoppen op de pagina, of
    schakel die systeemsneltoets uit.

## Op een telefoon of kleine tablet {#on-a-phone-or-small-tablet}

Op smalle schermen is de zijbalk verborgen om ruimte te maken voor de
pagina.

- Tik op de knop **☰** linksboven in de bovenbalk om de zijbalk in te
  schuiven.
- Tik op een item om erheen te gaan; de zijbalk sluit vanzelf.
- Om hem te sluiten zonder ergens heen te gaan, tikt u op de verduisterde
  pagina ernaast of drukt u op een toetsenbord op **Esc**.

Knoppen en invoervelden zijn op aanraakschermen iets groter, en rijen
filterknoppen lopen door op meerdere regels in plaats van buiten het
scherm te vallen. Brede tabellen kunt u met uw vinger opzij schuiven.

## Gerelateerd {#related}

- [Dashboard](dashboard.md)
- [Rollen, groepen en rechten](roles-and-permissions.md)
- [Modules in- en uitschakelen](../administration/modules.md)

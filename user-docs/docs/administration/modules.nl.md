# Modules in- en uitschakelen {#turning-modules-on-and-off}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Niet elke vereniging gebruikt elk onderdeel van Parcella. Een vereniging
zonder eigen watervoorziening heeft geen meterstanden nodig; een
vereniging zonder verplichte werkuren heeft geen werksessies nodig. U
bepaalt welke modules uw vereniging gebruikt.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Open **Administratie → Instellingen** en klap de
    kaart **Functiegebieden** uit.

Elke module heeft een schakelaar, haar naam en een korte beschrijving.
Zet de schakelaars om die u wilt wijzigen en klik op **Instellingen
opslaan**.

## Wat er gebeurt als u een module uitschakelt {#what-happens-when-you-switch-a-module-off}

- Ze **verdwijnt uit de zijbalk en het dashboard** voor iedereen, ook
  voor beheerders. (Uitzondering: de tegel *Verjaardagen deze week*
  blijft op het dashboard, ook als Kalender is uitgeschakeld.)
- Haar pagina's kunnen niet meer worden geopend, ook niet via een
  bladwijzer.
- **Er wordt niets verwijderd.** Al haar gegevens blijven in de database
  en zijn ongewijzigd terug zodra u de module weer inschakelt.
- Groepsrechten voor de module blijven zoals ze zijn, zodat dezelfde
  mensen weer toegang hebben na het opnieuw inschakelen.

Een module inschakelen maakt haar meteen zichtbaar voor iedereen met
volledige toegang. Anderen zien haar pas in de zijbalk als een groep hun
**Lezen** ervoor geeft -- zie [Groepen](groups.md).

## De schakelaars {#the-switches}

Ze staan in deze volgorde op de kaart.

| Schakelaar | Wat het doet | Standaard aan |
|---|---|---|
| **Werktijdenbeheer** | Werksessies, sponsorschappen, verenigingsrollen en het jaarverslag over werkuren. Zie [Werkuren](../modules/work-hours.md). | Ja |
| **Waterbeheer** | Watermeters, meterstanden en verbruiksrapporten. Zie [Water en elektriciteit](../modules/metering.md). | Ja |
| **Elektriciteitsbeheer** | Elektriciteitsmeters, meterstanden en verbruiksrapporten. | Ja |
| **Verzekeringsbeheer** | Opstal- en ongevallenverzekering per perceel, met jaarverslag. Zie [Verzekering](../modules/insurance.md). | Ja |
| **Support (helpdesk)** | Koppelt de gesprekken van uw helpdesk aan leden en het takenbord. Kies de helpdesk eerst onder [Integraties](integrations.md#support-helpdesk). Zie [Ondersteuning](../modules/support.md). | Nee |
| **Aankoopaanvragen** | Verenigingsuitgaven met vier-ogenprincipe. Zie [Aankoopaanvragen](../modules/purchase-requests.md). | Ja |
| **Kalender** | Verenigingskalender, verjaardagen, aan- en afwezigheid van het bestuur, elk met een agendafeed. Zie [Kalender](../modules/calendar.md). | Ja |
| **Inventaris** | Alles wat de vereniging bezit, met categorieën en uitlenen. Zie [Inventaris](../modules/inventory.md). | Ja |
| **Takenbord** | Een bord Te doen / Bezig / Klaar voor verenigingszaken. Alleen voor gebruikers met volledige toegang (bestuur, beheerders en groepen met volledige toegang). Zie [Takenbord](../modules/tasks.md). | Ja |
| **Aanmelders** | Mensen die zich voor een vrij perceel hebben aangemeld. Zie [Aanmelders](../modules/applicants.md). | Ja |
| **Externe contacten** | Leveranciers, vaklui, instanties. Zie [Externe contacten](../modules/external-contacts.md). | Ja |
| **Rapportages** | Cijfers van de vereniging door de tijd als grafieken, alleen lezen. Zie [Rapportages](../modules/reporting.md). | Ja |
| **Notities** | Notities met categorieën en labels, optioneel als bestanden in de cloud opgeslagen. Zie [Notities](../modules/notes.md). | Ja |
| **Processen** | Uw eigen stapsgewijze processen. Zie [Processen](../modules/processes.md). | Ja |
| **MCP-connector voor AI-clients** | Laat een AI-assistent (Claude, ChatGPT, ...) **alleen de notities die u voor AI hebt vrijgegeven** doorzoeken, lezen en schrijven, verder niets. Vraagt een [API-token](api-tokens.md) van het soort **Alleen MCP-connector**. | Nee |
| **Publieke aanmeld-API** | Laat het formulier op de website van de vereniging tuinders zonder login aanmelden voor werksessies. Zie [Integraties](integrations.md#public-signup-api) en [Voor tuinders](../gardeners/index.md). | Nee |
| **Publieke contactformulier-API** | Laat het contactformulier op de website van de vereniging een nieuwe vraag in uw helpdesk aanmaken in plaats van een e-mail te sturen. | Nee |
| **Openbare aanmeldformulier-API** | Laat het aanmeldformulier voor percelen op de website van de vereniging direct aanmelders aanmaken. De module **Aanmelders** kan zonder dit worden gebruikt, voor aanmeldingen die u met de hand invoert. | Nee |
| **Mededelingen** | Schrijf verenigingsnieuws één keer en bereid het voor op de website, de e-mail aan leden en een afdrukbare mededeling. Zie [Mededelingen](../modules/announcements.md). | Nee |
| **Cloudopslag** | Een cloudmap per perceel voor huurcontracten en papierwerk; ook nodig voor bijlagen van inkomende facturen, documenten van contacten, notitiebestanden en back-ups in de cloud. Kies de opslag eerst onder [Integraties](integrations.md#cloud-storage). | Nee |
| **Financiën** | Jaarfacturen per perceel, betalingen en boekhouding. Vul eerst de [financiële instellingen](settings.md#finance-settings) in. Zie [Financiën](../modules/finances/index.md). | Nee |
| **Nextcloud Deck-synchronisatie** | Kopieert de kaarten van één Nextcloud Deck-bord naar het takenbord, automatisch actueel gehouden. Richt de verbinding eerst in onder [Integraties](integrations.md#nextcloud-deck). | Nee |

**Leden** en **Percelen** hebben geen schakelaar: ze zijn de kern van
Parcella en staan altijd aan.

## Waarom sommige schakelaars uit staan {#why-some-switches-start-off}

De schakelaars die op een nieuwe installatie uit staan, doen een van
deze dingen:

- **Ze openen een deur naar het openbare internet.** De drie
  *Publieke/Openbare ... API*-schakelaars laten iedereen die uw website
  bezoekt gegevens naar Parcella sturen. Zet er een aan als uw website
  echt het passende formulier heeft, en alleen die u nodig hebt.
- **Ze slaan wachtwoorden voor andere diensten op**, of laten Parcella
  daarin handelen: cloudopslag, helpdesk, Nextcloud Deck, de
  websiteverbinding van mededelingen.
- **Ze gaan om met geld of bereiken elk lid tegelijk:** financiën en
  mededelingen.
- **Ze geven gegevens aan een extern bedrijf:** de MCP-connector geeft
  een AI-dienst toegang tot de notities die u vrijgeeft.

Er gaat niets kapot als u ze uit laat. Zet ze bewust aan, zodra u weet
dat u ze nodig hebt.

## Gerelateerd {#related}

- [Modules](../modules/index.md) -- wat elke module doet
- [Groepen](groups.md) -- wie een ingeschakelde module mag gebruiken
- [Integraties](integrations.md) -- verbindingen die meerdere modules
  nodig hebben

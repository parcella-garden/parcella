# API-tokens {#api-tokens}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Een API-token is een sleutel waarmee een ander programma Parcella namens
iemand kan gebruiken, zonder diens wachtwoord -- bijvoorbeeld een script
dat gegevens exporteert, of een AI-assistent die de notities van de
vereniging leest. De meeste verenigingen hebben er nooit een nodig.

!!! info "Wie kan dit gebruiken"
    Elke gebruiker kan **zijn eigen** tokens beheren: **Wachtwoord
    wijzigen** in de zijbalk → **API-tokens voor koppelingen** →
    **Beheren** (pagina **Mijn API-tokens**). Beheerders zien daarnaast
    de tokens van **iedereen** onder **Administratie → API-tokens**.

![API-tokens](../assets/screenshots/administration/api-tokens.png)

## Hoe een token zich gedraagt {#how-a-token-behaves}

- Het handelt **met precies de rechten van het account waartoe het
  behoort**. Een token van een meteropnemer kan alleen doen wat de
  meteropnemer kan.
- Het wordt **maar één keer** getoond, direct na het aanmaken. Kopieer
  het dan; later kan het niet meer worden opgezocht.
- Het werkt niet meer als het verloopt, als het wordt ingetrokken, of als
  het wachtwoord van het account wordt gewijzigd of gereset. Het account
  deactiveren stopt het ook.

Behandel een token als een wachtwoord. Kan het zijn uitgelekt, trek het
dan in.

## Nieuwe token {#new-token}

| Veld / knop | Wat het doet |
|---|---|
| **Gebruiker** | *Alleen op de pagina voor beheerders.* Als welk account het token handelt. U kunt tokens aanmaken voor uzelf en voor accounts **zonder** volledige toegang -- meestal een apart account voor een koppeling dat zelf nooit inlogt. Tokens voor andere accounts met volledige toegang zijn niet mogelijk, omdat een token ongemerkt namens die persoon zou handelen. |
| **Naam** | Verplicht, maximaal 100 tekens. Zeg waar het voor is, bijv. „Claude kennisbank“. |
| **Verloopt** | **na 30 dagen**, **na 90 dagen**, **na 365 dagen** (standaard) of **nooit**. Kies liefst een vervaldatum. |
| **Alleen MCP-connector (voor een AI-client)** | Alleen getoond als de module **MCP-connector voor AI-clients** aan staat. Zo'n token werkt alleen voor de AI-koppeling en alleen met notities die voor AI zijn vrijgegeven; elk ander gebruik wordt geweigerd. Gebruik voor een AI-assistent altijd dit soort. |
| **Token aanmaken** | Maakt het token aan en toont het in een groen vak: *Kopieer hem nu: hij wordt maar één keer getoond ...* |

## De lijst met tokens {#the-token-list}

| Kolom / knop | Wat ze toont of doet |
|---|---|
| **Naam** | De naam, de eerste tekens van het token (om het te herkennen), en waar van toepassing een badge **Alleen MCP**. |
| **Gebruiker** | *Alleen op de pagina voor beheerders.* Van wie het token is. |
| **Aangemaakt** | Datum van aanmaken. |
| **Laatst gebruikt** | Wanneer een programma het voor het laatst gebruikte, of **nooit**. |
| **Verloopt** | Vervaldatum of **nooit**. |
| **Status** | **actief**, **verlopen**, **ingetrokken**, of **beëindigd** (het wachtwoord is gewijzigd nadat het token werd aangemaakt). |
| **Intrekken** | Alleen bij actieve tokens. Na bevestiging werkt het token meteen niet meer. |

**Nog geen API-tokens.** verschijnt als er geen zijn.

## Een AI-assistent aan de notities koppelen {#connecting-an-ai-assistant-to-the-notes}

Met de module **MCP-connector voor AI-clients** kan een AI-assistent
zoals Claude de [notities](../modules/notes.md) die u ervoor hebt
vrijgegeven doorzoeken en lezen -- en als u dat toestaat schrijven --,
en verder niets. In het kort:

1. Schakel **MCP-connector voor AI-clients** (en **Notities**) in onder
   [Modules in- en uitschakelen](modules.md).
2. [Nodig](users.md) een apart account voor de assistent uit en plaats
   het in een [groep](groups.md) die alleen **Notities** lezen (en zo
   nodig schrijven) geeft.
3. Maak hier een token voor dat account aan met **Alleen MCP-connector**
   aangevinkt.
4. Geef notities vrij voor de AI door ze het vrijgavelabel te geven dat
   in het hoofdstuk over notities wordt beschreven.

Geef alleen notities vrij zonder persoonsgegevens: ze gaan naar een
externe AI-dienst. De stapsgewijze inrichting voor elke AI-client staat
in de [MCP-installatiehandleiding](https://github.com/parcella-garden/parcella/blob/main/docs/mcp-setup.md).

## Voor ontwikkelaars {#for-developers}

De REST API zelf -- eindpunten, authenticatie, voorbeelden -- wordt
beschreven in de
[ontwikkelaarsdocumentatie](https://github.com/parcella-garden/parcella#rest-api),
en interactief onder **Administratie → API-documentatie (Swagger)**.

## Gerelateerd {#related}

- [Eerste aanmelding en uw account](../getting-started/first-login.md#change-password)
- [Gebruikers en uitnodigingen](users.md)

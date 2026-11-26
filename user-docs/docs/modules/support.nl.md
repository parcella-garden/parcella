# Ondersteuning {#support}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Parcella heeft geen eigen ticketsysteem. Uw vereniging beantwoordt
e-mails en vragen uit het contactformulier in een helpdesk -- FreeScout,
Zammad, Znuny / OTRS, osTicket, Zendesk of Freshdesk -- en de module
Ondersteuning koppelt die helpdesk aan Parcella: u ziet welk gesprek bij
welk lid en perceel hoort, leest het gesprek, en maakt er een kaart op
het takenbord van. Antwoorden schrijft u altijd in de helpdesk zelf.

!!! info "Wie kan dit gebruiken"
    - De module wordt ingeschakeld met **Support (helpdesk)** onder
      [Modules in- en uitschakelen](../administration/modules.md). Ze
      staat **standaard uit**, omdat ze de toegangsgegevens van de
      helpdesk opslaat. De helpdesk zelf kiest en koppelt een beheerder
      onder [Integraties](../administration/integrations.md).
    - **Supportgesprekken in Parcella:** bestuursleden en beheerders, en
      gebruikers wier groep **Lezen** voor **Support (helpdesk)** geeft
      (zie [Groepen](../administration/groups.md)). **Schrijven** is nodig
      om een gesprek aan een lid of perceel te koppelen.
    - **Taak aanmaken:** alleen bestuursleden en beheerders (of gebruikers
      in een groep met volledige toegang), net als bij het takenbord zelf.
    - **Alle anderen** krijgen toch een link **Ondersteuning** in de
      navigatie zodra de module aan staat en de helpdesk een webadres
      heeft: die opent de helpdesk direct in een nieuw tabblad.

## Waar gesprekken vandaan komen {#where-conversations-come-from}

Parcella controleert de helpdesk ongeveer elke vijf minuten op nieuwe en
gewijzigde gesprekken. Het slaat alleen een verwijzing op -- onderwerp,
klant, status, aantal berichten, en de koppelingen naar lid, perceel en
taak. De berichten zelf blijven in de helpdesk en worden telkens opnieuw
opgehaald als u een gesprek opent.

**Leden koppelen:** komt er een gesprek binnen, dan zoekt Parcella het
lid waar het bij hoort:

1. Was deze helpdeskklant al eerder aan een lid gekoppeld, dan wordt dat
   lid gebruikt.
2. Anders: heeft **precies één** lid het e-mailadres van de klant, dan
   wordt dat lid automatisch gekoppeld.
3. Delen meerdere leden het adres (bijv. een stel met één mailbox), of
   heeft niemand het (een buurman, een leverancier), dan blijft het
   gesprek zonder lid. U kunt er met de hand een koppelen.

Heeft het gekoppelde lid precies één huidig perceel, dan wordt dat
perceel ook gekoppeld. Een gesprek dat een lid heeft -- automatisch of
door u ingesteld -- wordt later nooit opnieuw gekoppeld.

Verandert de naam van een lid in Parcella, dan wordt ook zijn klantrecord
in de helpdesk hernoemd, als de helpdesk dat ondersteunt.

**Statussen:** elke helpdesk noemt zijn toestanden anders; Parcella toont
ze als `active`, `pending`, `closed`, `spam` of `deleted`. Gesloten,
spam- en verwijderde gesprekken worden verborgen in de lijst, de badge
en het dashboard. Wordt een gesprek in de helpdesk heropend, dan
verschijnt het weer, met de koppeling naar het lid intact.

### Wat elke helpdesk ondersteunt {#what-each-helpdesk-supports}

| Helpdesk | Lijst met gesprekken en badge | Gesprekken lezen | Contactformulier maakt gesprek aan | Klantnamen gesynchroniseerd |
|---|---|---|---|---|
| FreeScout | ja | ja | ja | ja |
| Zammad | ja | ja | ja | ja |
| Znuny / OTRS | ja | ja | ja | nee |
| osTicket | nee | nee | ja | nee |
| Zendesk | ja | ja | ja | ja |
| Freshdesk | ja | ja | ja | ja |

Met osTicket kan Parcella alleen vragen uit het contactformulier van de
website doorgeven; u werkt ermee in osTicket alleen.

Alleen berichten die de klant kan zien, worden getoond -- interne
notities blijven in de helpdesk. Bijlagen worden niet getoond; open het
gesprek daarvoor in de helpdesk.

## Supportgesprekken {#support-conversations}

![Supportgesprekken](../assets/screenshots/support/list.png)

**Ondersteuning** in de navigatie opent de lijst met open gesprekken van
de actieve helpdesk, het laatst bijgewerkte eerst. De rode badge naast
**Ondersteuning** -- en de tegel **Open supportgesprekken** op het
[dashboard](../getting-started/dashboard.md) -- telt dezelfde gesprekken,
met of zonder lid.

| Veld / knop | Wat het doet |
|---|---|
| **Openen in {helpdesk}** | Opent de helpdesk in een nieuw tabblad. Alleen zichtbaar als het webadres van de helpdesk is ingesteld. |
| **Onderwerp** | Het onderwerp van het gesprek. Klik ergens in de rij om het gesprek te openen. |
| **Klant** | De naam van de afzender, of zijn e-mailadres. |
| **Lid** | Het gekoppelde lid, of „—“. |
| **Status** | `active` of `pending` (gesloten gesprekken staan er niet in). |
| **Berichten** | Aantal berichten, zoals de helpdesk het laatst meldde. |
| **Bijgewerkt** | Wanneer het gesprek in de helpdesk voor het laatst veranderde. |
| **Taak** | Een bordpictogram als het gesprek aan een taak is gekoppeld. |

In plaats van de lijst kunt u zien:

- „Er is nog geen helpdesk ingesteld. …“ -- een beheerder moet er nog een
  kiezen onder [Integraties](../administration/integrations.md).
- „{helpdesk} kan via zijn interface geen gesprekken opsommen. …“ -- de
  helpdesk is osTicket.
- „Nog geen supportgesprekken.“ -- er staat nu niets open.

## Pagina van een gesprek {#conversation-page}

<!-- TODO(verify): no screenshot -- the list's rows open conversations by click, not by a link, so the screenshot tool can't follow one; without a connected helpdesk the transcript would only show an error anyway. -->

Toont één gesprek, met het onderwerp als titel.

| Knop | Wat het doet |
|---|---|
| **Terug** | Terug naar de lijst. |
| **Openen in {helpdesk}** | Opent dit gesprek in de helpdesk -- daar beantwoordt u het. |

### Gesprek {#conversation}

De berichten, het oudste eerst, elk met auteur en tijd. Kunnen ze niet
worden geladen, dan legt een melding uit waarom -- de helpdesk is niet
bereikbaar, hij kan geen gesprekken tonen (osTicket), of „De helpdesk van
dit gesprek is niet (meer) ingesteld.“ als de vereniging intussen naar
een andere helpdesk is overgestapt. „Er konden geen berichten worden
geladen.“ betekent dat de helpdesk er geen teruggaf.

### Lid {#member}

Toont het gekoppelde lid (met een link naar zijn pagina), of „Geen lid
gekoppeld.“.

Kies met schrijfrecht een lid en klik op **Opslaan**:

- Leden met het e-mailadres van de klant staan bovenaan, gemarkeerd als
  **voorgesteld**. Delen meerdere leden het adres, dan vraagt een
  notitie u het juiste te kiezen.
- Daaronder alle huidige leden.
- **-- geen --** verwijdert de koppeling.

Een lid opslaan zet ook het perceel opnieuw: heeft het lid precies één
huidig perceel, dan wordt dat gekoppeld; anders geen.

### Perceel {#parcel}

Getoond zodra er een lid is gekoppeld. Kies met schrijfrecht een van de
huidige percelen van het lid, of **-- geen --**, en klik op **Opslaan**.
<!-- TODO(verify): without write permission the Parcel card is empty -- the linked parcel isn't displayed at all for read-only users. -->

### Takenbord {#task-board}

| Veld / knop | Wat het doet |
|---|---|
| **Taak openen** | Getoond als het gesprek aan een taak is gekoppeld; opent de taak. |
| Lijst + **Taak aanmaken** | Maakt een nieuwe kaart aan in de gekozen lijst van het [takenbord](tasks.md) en koppelt die aan het gesprek. De titel van de kaart is het onderwerp; de beschrijving noemt de helpdesk, het gespreksnummer en, als het is gekoppeld, het lid. Alleen bestuursleden en beheerders. |

Heeft het takenbord nog geen lijsten, dan mislukt het aanmaken van een
taak met „Er bestaan nog geen lijsten op het takenbord“.
<!-- TODO(verify): there is a route to link an existing task to a conversation, but no form on the page uses it. -->

!!! note "Antwoorden gebeurt in de helpdesk"
    Parcella heeft bewust geen antwoordveld. Klik op **Openen in
    {helpdesk}** en antwoord daar; het nieuwe bericht verschijnt in
    Parcella de volgende keer dat u het gesprek opent.

## Het contactformulier van de website {#the-website-contact-form}

Heeft de website van uw vereniging een contactformulier, dan kan dat via
Parcella direct een gesprek in de helpdesk aanmaken. Dit is een aparte
schakelaar, **Publieke contactformulier-API**, ook standaard uit. Het
inrichten staat beschreven onder
[Integraties](../administration/integrations.md).

## Gerelateerd {#related}

- [Integraties](../administration/integrations.md) -- de helpdesk kiezen
  en koppelen
- [Takenbord](tasks.md) -- een gesprek opvolgen
- [Leden](members.md) -- e-mailadressen die voor het koppelen worden
  gebruikt
- [Dashboard](../getting-started/dashboard.md)

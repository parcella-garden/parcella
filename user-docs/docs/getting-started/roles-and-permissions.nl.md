# Rollen, groepen en rechten {#roles-groups-and-permissions}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Niet iedereen die helpt de vereniging te leiden, hoeft alles te zien.
Wie de watermeters opneemt, heeft de bankgegevens niet nodig, en de
penningmeester hoeft geen werksessies te plannen. Met Parcella geeft u
iedereen precies de toegang die zijn taak vraagt.

!!! info "Wie kan dit gebruiken"
    Deze pagina legt de toegang voor iedereen uit. Alleen
    **beheerders** kunnen wijzigen wie welke toegang heeft, onder
    [Gebruikers en uitnodigingen](../administration/users.md) en
    [Groepen](../administration/groups.md).

## De drie toegangsniveaus {#the-three-levels-of-access}

Elk account valt in een van drie niveaus.

| Niveau | Ziet en wijzigt | Opent de **Administratie** | Hoe u het krijgt |
|---|---|---|---|
| **Beheerder** | Alles in elke ingeschakelde module | Ja | Een groep met **Toegang tot het administratiepaneel**, of de oudere rol **Beheerder** |
| **Volledige toegang** (meestal het bestuur) | Alles in elke ingeschakelde module | Nee | Een groep met **Volledige toegang tot elke module**, of de oudere rol **Bestuur** |
| **Beperkt** | Wat de groepen toestaan, per module; minstens leesrecht op leden en percelen | Nee | Lidmaatschap van een of meer groepen zonder die twee vinkjes |

De **Administratie** -- gebruikers, groepen, verenigingsinstellingen,
integraties, back-ups -- staat bewust los van volledige toegang. In het
bestuur zitten maakt iemand niet vanzelf degene die voor de installatie
zorgt, en omgekeerd. Beheerders hebben altijd ook volledige toegang tot
de modules.

## Groepen {#groups}

Een **groep** is een benoemde set rechten, bijvoorbeeld „Waterteam“,
„Penningmeester“ of „Bestuur“. Beheerders maken groepen aan en plaatsen
accounts erin. Iemand kan in meerdere groepen zitten.

Een groep geeft ofwel:

- **Volledige toegang tot elke module**, of
- **Toegang tot het administratiepaneel** (inclusief volledige toegang),
  of
- **Lezen**, **Schrijven** en **Verwijderen** per module, elk apart
  aangevinkt.

### Wat Lezen, Schrijven en Verwijderen betekenen {#what-read-write-and-delete-mean}

| Recht | Staat toe |
|---|---|
| **Lezen** | De module openen, de lijsten en detailpagina's zien, en exports en rapporten downloaden. Zonder dit recht verschijnt de module niet in de zijbalk. |
| **Schrijven** | Nieuwe records aanmaken en bestaande wijzigen -- een meterstand toevoegen, een lid bewerken, een betaling van een factuur vastleggen. |
| **Verwijderen** | Records verwijderen, voor zover de module verwijderen toestaat. |

!!! tip "Vink ook Lezen aan"
    Schrijven en Verwijderen zijn bedoeld bovenop Lezen. Wie een module
    niet mag lezen, ziet haar niet in de zijbalk en kan haar pagina's
    niet openen, dus Schrijven alleen heeft geen zin. Elk
    modulehoofdstuk zegt welke handelingen welk recht nodig hebben.

### De modules die een groep kan toekennen {#the-modules-a-group-can-grant}

| Module in het groepsformulier | Omvat |
|---|---|
| **Leden en percelen** | [Leden](../modules/members.md) en [Percelen](../modules/parcels.md) |
| **Werksessies** | [Werkuren](../modules/work-hours.md) |
| **Water** | Het waterdeel van [Water en elektriciteit](../modules/metering.md) |
| **Elektriciteit** | Het elektriciteitsdeel van [Water en elektriciteit](../modules/metering.md) |
| **Verzekering** | [Verzekering](../modules/insurance.md) |
| **Aankoopaanvragen** | [Aankoopaanvragen](../modules/purchase-requests.md) |
| **Kalender** | [Kalender](../modules/calendar.md) |
| **Inventaris** | [Inventaris](../modules/inventory.md) |
| **Financiën** | [Financiën](../modules/finances/index.md) |
| **Support (helpdesk)** | [Ondersteuning](../modules/support.md) |
| **Aanmelders** | [Aanmelders](../modules/applicants.md) |
| **Externe contacten** | [Externe contacten](../modules/external-contacts.md) |
| **Rapportages** | [Rapportages](../modules/reporting.md) |
| **Notities** | [Notities](../modules/notes.md) |
| **Processen** | [Processen](../modules/processes.md) |

### Meerdere groepen: de ruimste wint {#several-groups-the-most-generous-wins}

Zit iemand in meerdere groepen, dan tellen de rechten op. Per module en
per niveau is één groep die het toekent genoeg. Voorbeeld: groep
„Waterteam“ geeft Water lezen + schrijven, groep „Kalender“ geeft
Kalender lezen. Wie in beide zit, mag watergegevens lezen en wijzigen en
de kalender lezen.

### Iedereen kan leden en percelen opzoeken {#everybody-can-look-up-members-and-parcels}

Elk account, ook een zonder enige groep, kan leden en percelen
**lezen**. Wie helpt de vereniging te leiden, moet weten wie wie is en
welk perceel van wie is. Wijzigen vraagt **Schrijven** op **Leden en
percelen**.

## Wat alleen volledige toegang kan {#things-only-full-access-can-do}

Een paar onderdelen kunnen niet per module worden toegekend. Ze zijn
altijd voorbehouden aan mensen met volledige toegang (bestuur,
beheerders, of een groep met **Volledige toegang tot elke module**):

- het [Takenbord](../modules/tasks.md),
- [Mededelingen](../modules/announcements.md),
- een [aankoopaanvraag](../modules/purchase-requests.md) goedkeuren of
  afwijzen -- de twee vereiste goedkeuringen moeten van mensen met
  volledige toegang komen,
- agenda's maken en bewerken onder **Eigen agenda's** in de
  [Kalender](../modules/calendar.md),
- de cloudmap van een perceel (bladeren, uploaden, downloaden) en het
  downloaden van de bijlage van een inkomende factuur,
- een taak maken vanuit een ondersteuningsgesprek of er een aan een taak
  koppelen.

## De oudere rollen: Beheerder, Bestuur, Penningmeester, Alleen-lezen {#the-older-roles-administrator-board-treasurer-read-only}

Eerdere versies van Parcella gaven elk account een vaste **rol**.
Accounts uit die tijd kunnen er nog een hebben:

| Rol | Effect nu |
|---|---|
| **Beheerder** | Volledige toegang plus de administratie, zonder groep. Het allereerste account van een nieuwe installatie heeft deze rol. |
| **Bestuur** | Volledige toegang, zonder groep. |
| **Penningmeester** | Niets meer dan het basisleesrecht op leden en percelen. Gebruik een groep om meer toe te kennen. |
| **Alleen-lezen (alleen weergave)** | Hetzelfde als Penningmeester: alleen basistoegang, al het andere komt uit groepen. |

Nieuwe accounts krijgen de inerte rol **Alleen-lezen**; hun echte
toegang komt alleen uit groepen. Een beheerder kan een account met
Beheerder of Bestuur overzetten op groepen met **Oude rol verwijderen**
(zie [Gebruikers en uitnodigingen](../administration/users.md)). Plaats
het account *eerst* in de juiste groep, anders zakt het terug naar
basistoegang.

De voettekst van de zijbalk toont de groepen waarin u zit. Zonder groep
toont hij **Beheerder** of **Bestuur** als u die rol hebt, anders een
streepje.

## Vangnet: de laatste beheerder {#safety-net-the-last-administrator}

Parcella weigert elke wijziging waardoor **geen actief account de
administratie meer kan openen**. U krijgt de melding **Kan de laatst
overgebleven Beheerder-/Bestuursaccount de beheerderstoegang niet
ontnemen** wanneer u het laatste zulke account probeert te deactiveren,
te verwijderen, te degraderen of uit zijn groep te halen, of de laatste
groep die dit recht geeft probeert te verwijderen of uit te vinken.
Zonder minstens één beheerder kan niemand toegangsproblemen nog
oplossen.

## De REST API en API-tokens {#the-rest-api-and-api-tokens}

Programma's die via de programmeerinterface met Parcella praten,
gebruiken een [API-token](../administration/api-tokens.md). Een
persoonlijk token werkt met de rechten van het account waartoe het
behoort.
<!-- TODO(verify): several REST API endpoints still check only the old role (Administrator/Board) rather than group permissions, so a group-based full-access account may be refused some API writes. Confirm before stating this to users. -->

## Gerelateerd {#related}

- [Groepen](../administration/groups.md) -- groepen maken en rechten aanvinken
- [Gebruikers en uitnodigingen](../administration/users.md) -- mensen aan groepen toevoegen
- [Uw weg vinden](navigation.md#why-entries-appear-and-disappear)

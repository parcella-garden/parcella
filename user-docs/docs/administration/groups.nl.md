# Groepen {#groups}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Groepen bepalen wat iedereen mag zien en wijzigen. U maakt een groep aan
voor een taak in uw vereniging -- „Bestuur“, „Penningmeester“,
„Waterteam“ --, vinkt aan wat die taak nodig heeft, en plaatst de juiste
mensen erin.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Open **Administratie → Groepen**.

De ideeën achter groepen -- Lezen, Schrijven en Verwijderen, volledige
toegang, de administratie -- worden uitgelegd in
[Rollen, groepen en rechten](../getting-started/roles-and-permissions.md).
Deze pagina beschrijft het scherm.

![Groepen](../assets/screenshots/administration/groups.png)

## Groep aanmaken {#create-group}

| Veld / knop | Wat het doet |
|---|---|
| **Naam** | Verplicht, en moet uniek zijn (**Er bestaat al een groep met deze naam**). |
| **Omschrijving** | Optionele notitie over waar de groep voor is. |
| **Volledige toegang tot elke module** | Leden van de groep mogen alles in elke ingeschakelde module lezen, wijzigen en verwijderen, zoals het bestuur. |
| **Toegang tot het administratiepaneel** | Leden van de groep mogen ook **Administratie** openen. Dit aanvinken omvat volledige toegang, dus het vakje voor volledige toegang verdwijnt. |
| **Groep aanmaken** | Maakt de groep aan. U ziet **Groep aangemaakt**. |

Een nieuwe groep zonder een van beide vakjes aangevinkt geeft nog niets.
Open haar hieronder om de rechten aan te vinken.

## De groepskaarten {#the-group-cards}

Elke groep verschijnt als dichtgeklapte kaart onder het formulier. De
kop toont de naam en een badge **Administratie** of **Volledige toegang**
als ze een daarvan geeft. Klik op de kop om de kaart open te klappen.

De **prullenbak**knop in de kop verwijdert de groep na bevestiging. Haar
leden verliezen wat de groep hun gaf. Parcella weigert de laatste groep
te verwijderen die iemand toegang tot de administratie geeft, als geen
ander account die heeft.

### Instellingen en rechten {#settings-and-permissions}

| Veld / knop | Wat het doet |
|---|---|
| **Naam**, **Omschrijving** | Als bij het aanmaken. |
| **Volledige toegang tot elke module**, **Toegang tot het administratiepaneel** | Als bij het aanmaken. Is een van beide aangevinkt, dan wordt de rechtentabel verborgen omdat die niet nodig is. |
| Rechtentabel | Eén rij per **Module** met de vakjes **Lezen**, **Schrijven** en **Verwijderen**. Zie de tabel met modules hieronder. |
| **Opslaan** | Slaat naam, omschrijving, de twee vakjes en de hele tabel op. U ziet **Groep bijgewerkt**. |

De modules in de tabel: **Leden en percelen**, **Werksessies**,
**Water**, **Elektriciteit**, **Verzekering**, **Aankoopaanvragen**,
**Kalender**, **Inventaris**, **Financiën**, **Support (helpdesk)**,
**Aanmelders**, **Externe contacten**, **Rapportages**, **Notities**,
**Processen**. Modules die uw vereniging heeft uitgeschakeld, staan er
nog steeds in; hun vinkjes gelden zodra de module wordt ingeschakeld.

!!! tip "Lezen komt eerst"
    Vink **Lezen** aan overal waar u **Schrijven** of **Verwijderen**
    aanvinkt. Zonder Lezen verschijnt de module niet eens in de zijbalk
    van de persoon.

Het takenbord en de mededelingen staan niet in de tabel: die zijn alleen
ooit beschikbaar met volledige toegang.

### Toegewezen gebruikers {#assigned-users}

Toont de accounts in de groep, met avatar, naam en e-mailadres.

| Element | Wat het doet |
|---|---|
| **×** naast een persoon | Haalt hem meteen uit de groep (**Gebruiker verwijderd**). |
| **Gebruiker toevoegen...** + **Toevoegen** | Kies een account en voeg het toe (**Gebruiker toegevoegd**). |

De lijst **Gebruiker toevoegen...** biedt alleen accounts aan die hun
toegang uit groepen krijgen. Oudere accounts met de rol **Beheerder** of
**Bestuur** hebben al volledige toegang en worden hier niet aangeboden;
wilt u ze naar groepen overzetten, voeg ze dan toe vanaf hun pagina
[Gebruiker bewerken](users.md#edit-user). Zitten alle geschikte accounts
al in de groep, dan ziet u in plaats van de lijst een korte notitie; zijn
er helemaal geen, een link **Nu uitnodigen**.

Wijzigingen in rechten gelden bij de volgende klik van de persoon -- hij
hoeft niet opnieuw in te loggen.

## Voorbeeldindeling {#example-set-up}

| Groep | Aangevinkt |
|---|---|
| Beheerders | **Toegang tot het administratiepaneel** |
| Bestuur | **Volledige toegang tot elke module** |
| Penningmeester | Financiën: Lezen, Schrijven, Verwijderen. Leden en percelen: Lezen, Schrijven. Aankoopaanvragen: Lezen. Verzekering: Lezen. |
| Meteropnemers | Water: Lezen, Schrijven. Elektriciteit: Lezen, Schrijven. |
| Werksessieteam | Werksessies: Lezen, Schrijven. Kalender: Lezen. |

Iemand kan in meerdere groepen zitten; de rechten tellen op.

## Gerelateerd {#related}

- [Gebruikers en uitnodigingen](users.md)
- [Rollen, groepen en rechten](../getting-started/roles-and-permissions.md)
- [Modules in- en uitschakelen](modules.md)

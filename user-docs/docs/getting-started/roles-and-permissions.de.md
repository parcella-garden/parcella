# Rollen, Gruppen und Rechte {#roles-groups-and-permissions}

Nicht jeder, der beim Führen des Vereins hilft, muss alles sehen. Wer die
Wasserzähler abliest, braucht keine Bankdaten, und der Kassierer muss keine
Arbeitseinsätze planen. Mit Parcella gibst du jeder Person genau den
Zugriff, den ihre Aufgabe braucht.

!!! info "Wer das nutzen kann"
    Diese Seite erklärt den Zugriff für alle. Nur **Administratoren**
    können ändern, wer welchen Zugriff hat, unter
    [Benutzer und Einladungen](../administration/users.md) und
    [Gruppen](../administration/groups.md).

## Die drei Zugriffsstufen {#the-three-levels-of-access}

Jedes Konto gehört zu einer von drei Stufen.

| Stufe | Sieht und ändert | Öffnet den Bereich **Administration** | So bekommt man sie |
|---|---|---|---|
| **Administrator** | Alles in jedem eingeschalteten Modul | Ja | Eine Gruppe mit **Zugriff auf den Administrationsbereich** oder die ältere Rolle **Administrator** |
| **Voller Zugriff** (typischerweise der Vorstand) | Alles in jedem eingeschalteten Modul | Nein | Eine Gruppe mit **Voller Zugriff auf jedes Modul** oder die ältere Rolle **Vorstand** |
| **Eingeschränkt** | Was ihre Gruppen erlauben, Modul für Modul; mindestens Leserecht für Mitglieder und Parzellen | Nein | Mitgliedschaft in einer oder mehreren Gruppen ohne diese beiden Häkchen |

Der Bereich **Administration** -- Benutzer, Gruppen, Vereinseinstellungen,
Integrationen, Backups -- ist bewusst vom vollen Zugriff getrennt. Wer im
Vorstand ist, betreut nicht automatisch auch die Installation, und
umgekehrt. Administratoren haben aber immer auch vollen Zugriff auf die
Module.

## Gruppen {#groups}

Eine **Gruppe** ist ein benanntes Bündel von Rechten, zum Beispiel
„Wasserteam“, „Kassierer“ oder „Vorstand“. Administratoren legen Gruppen an
und fügen Konten hinzu. Eine Person kann in mehreren Gruppen sein.

Eine Gruppe gewährt entweder:

- **Voller Zugriff auf jedes Modul** oder
- **Zugriff auf den Administrationsbereich** (schließt vollen Zugriff ein)
  oder
- **Lesen**, **Schreiben** und **Löschen** je Modul, einzeln angehakt.

### Was Lesen, Schreiben und Löschen bedeuten {#what-read-write-and-delete-mean}

| Recht | Erlaubt |
|---|---|
| **Lesen** | Das Modul öffnen, seine Listen und Detailseiten sehen und seine Exporte und Berichte herunterladen. Ohne dieses Recht erscheint das Modul nicht in der Seitenleiste. |
| **Schreiben** | Neue Einträge anlegen und bestehende ändern -- einen Zählerstand eintragen, ein Mitglied bearbeiten, eine Rechnungszahlung erfassen. |
| **Löschen** | Einträge entfernen, sofern das Modul Löschen überhaupt zulässt. |

!!! tip "Lesen mit anhaken"
    Schreiben und Löschen sind als Ergänzung zu Lesen gedacht. Wer ein
    Modul nicht lesen darf, sieht es nicht in der Seitenleiste und kann
    seine Seiten nicht öffnen; Schreiben allein nützt also nichts. Jedes
    Modulkapitel sagt, welche Aktion welches Recht braucht.

### Die Module, die eine Gruppe freigeben kann {#the-modules-a-group-can-grant}

| Modul im Gruppenformular | Umfasst |
|---|---|
| **Mitglieder & Parzellen** | [Mitglieder](../modules/members.md) und [Parzellen](../modules/parcels.md) |
| **Arbeitseinsätze** | [Arbeitsstunden](../modules/work-hours.md) |
| **Wasser** | Den Wasser-Teil von [Wasser und Strom](../modules/metering.md) |
| **Strom** | Den Strom-Teil von [Wasser und Strom](../modules/metering.md) |
| **Versicherung** | [Versicherungen](../modules/insurance.md) |
| **Einkaufswünsche** | [Einkaufswünsche](../modules/purchase-requests.md) |
| **Kalender** | [Kalender](../modules/calendar.md) |
| **Inventar** | [Inventar](../modules/inventory.md) |
| **Finanzen** | [Finanzen](../modules/finances/index.md) |
| **Support (Helpdesk)** | [Support](../modules/support.md) |
| **Bewerber** | [Bewerber](../modules/applicants.md) |
| **Externe Kontakte** | [Externe Kontakte](../modules/external-contacts.md) |
| **Auswertungen** | [Auswertungen](../modules/reporting.md) |
| **Notizen** | [Notizen](../modules/notes.md) |
| **Vorgänge** | [Vorgänge](../modules/processes.md) |

### Mehrere Gruppen: das großzügigste Recht gilt {#several-groups-the-most-generous-wins}

Ist eine Person in mehreren Gruppen, addieren sich ihre Rechte. Für jedes
Modul und jede Stufe genügt eine Gruppe, die sie gewährt. Beispiel: Die
Gruppe „Wasserteam“ gewährt Wasser Lesen + Schreiben, die Gruppe „Kalender“
gewährt Kalender Lesen. Wer in beiden ist, darf Wasserdaten lesen und
ändern und den Kalender lesen.

### Mitglieder und Parzellen nachschlagen kann jeder {#everybody-can-look-up-members-and-parcels}

Jedes Konto, auch eines ohne jede Gruppe, darf Mitglieder und Parzellen
**lesen**. Wer beim Führen des Vereins hilft, muss wissen, wer wer ist und
welche Parzelle wem gehört. Ändern braucht **Schreiben** bei **Mitglieder &
Parzellen**.

## Was nur voller Zugriff kann {#things-only-full-access-can-do}

Einige Bereiche lassen sich nicht je Modul freigeben. Sie sind immer
Personen mit vollem Zugriff vorbehalten (Vorstand, Administratoren oder eine
Gruppe mit **Voller Zugriff auf jedes Modul**):

- das [Aufgabenboard](../modules/tasks.md),
- [Mitteilungen](../modules/announcements.md),
- einen [Einkaufswunsch](../modules/purchase-requests.md) freigeben oder
  ablehnen -- die beiden nötigen Freigaben müssen von Personen mit vollem
  Zugriff kommen,
- Kalender unter **Eigene Kalender** im [Kalender](../modules/calendar.md)
  anlegen und bearbeiten,
- der Cloud-Ordner einer Parzelle (durchsuchen, hochladen, herunterladen)
  und das Herunterladen des Anhangs einer Eingangsrechnung,
- aus einer Support-Konversation eine Aufgabe anlegen oder sie mit einer
  Aufgabe verknüpfen.

## Die älteren Rollen: Administrator, Vorstand, Kassierer, Lesend {#the-older-roles-administrator-board-treasurer-read-only}

Frühere Versionen von Parcella gaben jedem Konto eine feste **Rolle**.
Damals angelegte Konten können noch eine haben:

| Rolle | Wirkung heute |
|---|---|
| **Administrator** | Voller Zugriff plus Administrationsbereich, ohne Gruppe. Das allererste Konto einer neuen Installation hat diese Rolle. |
| **Vorstand** | Voller Zugriff, ohne Gruppe. |
| **Kassierer** | Nichts über das Grund-Leserecht für Mitglieder und Parzellen hinaus. Mehr gibt es über eine Gruppe. |
| **Lesend (nur anschauen)** | Wie Kassierer: nur Grundzugriff, alles andere kommt aus Gruppen. |

Neue Konten bekommen die wirkungslose Rolle **Lesend**; ihren eigentlichen
Zugriff erhalten sie nur über Gruppen. Ein Administrator kann ein
Administrator- oder Vorstandskonto mit **Alte Rolle entfernen** auf Gruppen
umstellen (siehe [Benutzer und Einladungen](../administration/users.md)).
Füg das Konto *vorher* der richtigen Gruppe hinzu, sonst fällt es auf den
Grundzugriff zurück.

Der Fußbereich der Seitenleiste zeigt deine Gruppen. Ohne Gruppe steht dort
**Administrator** oder **Vorstand**, wenn du diese Rolle hast, sonst ein
Strich.

## Sicherheitsnetz: der letzte Administrator {#safety-net-the-last-administrator}

Parcella verweigert jede Änderung, nach der **kein aktives Konto mehr den
Administrationsbereich öffnen kann**. Du erhältst die Meldung **Der letzten
verbleibenden Administrator-/Vorstandsperson kann der Admin-Zugriff nicht
entzogen werden**, wenn du das letzte solche Konto deaktivieren, löschen,
herabstufen oder aus seiner Gruppe nehmen willst, oder die letzte Gruppe
löschen oder abhaken willst, die diesen Zugriff gewährt. Ohne mindestens
einen Administrator könnte niemand mehr Zugriffsprobleme beheben.

## Die REST-API und API-Tokens {#the-rest-api-and-api-tokens}

Programme, die über die Programmierschnittstelle mit Parcella sprechen,
benutzen ein [API-Token](../administration/api-tokens.md). Ein persönliches
Token handelt mit den Rechten des Kontos, dem es gehört.

## Siehe auch {#related}

- [Gruppen](../administration/groups.md) -- Gruppen anlegen und Rechte anhaken
- [Benutzer und Einladungen](../administration/users.md) -- Personen Gruppen zuordnen
- [Sich zurechtfinden](navigation.md#why-entries-appear-and-disappear)

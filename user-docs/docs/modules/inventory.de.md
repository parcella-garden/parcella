# Inventar {#inventory}

Das Inventar ist das Bestandsverzeichnis des Vereins: alles, was dem Verein
gehört, und Dinge, die Mitgliedern persönlich gehören, aber auf
Vereinsgelände lagern. Gegenstände sind in selbst festgelegte Kategorien
gruppiert, haben Kaufpreis, aktuellen Wert und Wiederbeschaffungswert und
lassen sich mit einem einfachen Ausleih- und Rückgabesystem an Mitglieder
verleihen.

!!! info "Wer das nutzen kann"
    Vorstandsmitglieder und Administratoren haben immer vollen Zugriff.
    Andere Benutzer brauchen eine Gruppe, die Rechte für **Inventar**
    gewährt (siehe [Gruppen](../administration/groups.md)):

    - **Lesen** -- die Liste der Gegenstände, ihre Seiten und die aktiven
      Ausleihen sehen.
    - **Schreiben** -- Gegenstände anlegen, bearbeiten und ausmustern,
      Kategorien verwalten, Gegenstände ausleihen und als zurückgegeben
      markieren.
    - **Löschen** -- Gegenstände und Kategorien endgültig löschen.

    Eingeschaltet wird das Modul mit **Inventar** unter
    [Module ein- und ausschalten](../administration/modules.md). Es ist
    standardmäßig an.

## Inventarliste {#inventory-list}

![Inventarliste](../assets/screenshots/inventory/list.png)

**Inventar** in der Navigation listet alle Gegenstände, gruppiert in je eine
Karte pro Kategorie in alphabetischer Reihenfolge. Gegenstände ohne
Kategorie stehen zuletzt unter **Ohne Kategorie**. Innerhalb einer Karte
sind die Gegenstände nach Namen sortiert.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Aktive Ausleihen** | Öffnet die [Liste von allem, was gerade verliehen ist](#active-loans). |
| **Kategorien verwalten** | Öffnet die [Kategorien](#inventory-categories). Erscheint nur mit Schreibrecht. |
| **Neuer Gegenstand** | Öffnet ein leeres [Gegenstandsformular](#item-form). Erscheint nur mit Schreibrecht. |
| **Alle Kategorien** / eine Kategorie | Zeigt nur die Gegenstände einer Kategorie. |
| **Ausgemusterte Gegenstände einbeziehen** | Listet auch [ausgemusterte](#retiring-and-deleting) Gegenstände, grau mit einem Badge **Ausgemustert**. Standardmäßig aus. |

| Spalte | Was sie zeigt |
|---|---|
| **Name** | Der Gegenstand, verlinkt auf seine Seite. Badges: **Ausgemustert**, **Ausleihbar**. |
| **Eigentümer** | **Vereinseigentum** oder **Mitgliedseigentum**. |
| **Lagerort** | Der Lagerort. |
| **Menge** | Bei ausleihbaren Gegenständen verfügbar / vorhanden (z. B. **1 / 2**, wenn einer von zweien verliehen ist); sonst die vorhandene Menge. |
| **Wert** | Der aktuelle Wert, falls eingetragen. |
| Augen-Schaltfläche | Öffnet den Gegenstand. |

## Gegenstandsseite {#item-page}

![Gegenstandsseite](../assets/screenshots/inventory/detail.png)

Ein Klick auf den Namen eines Gegenstands öffnet seine Seite.

### Schaltflächen {#buttons}

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Bearbeiten** | Öffnet das [Gegenstandsformular](#item-form). Braucht Schreibrecht. |
| **Ausmustern** | Markiert den Gegenstand nach einer Bestätigung als nicht mehr im Besitz oder Einsatz. Braucht Schreibrecht; erscheint nicht mehr, sobald der Gegenstand ausgemustert ist. Siehe [Ausmustern und löschen](#retiring-and-deleting). |
| **Löschen** | Löscht den Gegenstand und seine ganze Ausleihhistorie nach einer Bestätigung endgültig. Braucht Löschrecht. |
| **Zurück** | Führt zur Inventarliste zurück. |

Ein ausgemusterter Gegenstand zeigt oben den Hinweis „Dieser Gegenstand ist
ausgemustert -- nicht mehr im Besitz/Einsatz.“

### Übersicht {#overview}

| Feld | Was es zeigt |
|---|---|
| **Kategorie** | Die Kategorie oder **Ohne Kategorie**. |
| **Eigentümer** | **Vereinseigentum** oder der Name des Mitglieds, dem er gehört. |
| **Lagerort** | Wo der Gegenstand aufbewahrt wird, oder „-“. |
| **Menge** | Bei ausleihbaren Gegenständen „verfügbar / vorhanden **verfügbar**“, sonst die vorhandene Menge. |
| **Beschreibung**, **Notizen** | Erscheinen nur, wenn ausgefüllt. |

### Finanzen {#financials}

| Feld | Was es zeigt |
|---|---|
| **Kaufdatum** | Wann er gekauft wurde. |
| **Kaufpreis** | Was er gekostet hat. |
| **Aktueller Wert** | Die aktuelle Schätzung des Vorstands, mit „Stand“ und dem Datum der letzten Prüfung, falls eingetragen. |
| **Wiederbeschaffungswert** | Was ein Ersatz kosten würde. |

Leere Felder zeigen „-“.

### Ausleihen {#check-out}

Erscheint nur bei Gegenständen, die als ausleihbar markiert sind. Ist nichts
verfügbar, steht dort **Aktuell nichts zum Ausleihen verfügbar.** Das
Formular braucht Schreibrecht.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Mitglied** | Wer den Gegenstand ausleiht. Listet die aktuellen Mitglieder. Pflicht. |
| **Menge** | Wie viele Stück. Mindestens 1, höchstens die gerade verfügbare Zahl. Vorgabe 1. |
| **Datum** | Der Tag der Ausleihe. Vorgabe heute. |
| **Gebühr** | Freiwillig. Nur eine Zahl, z. B. `5` oder `2,50` -- kein Währungszeichen und kein Text. Leer gelassen gilt die **Vorgeschlagene Leihgebühr** des Gegenstands (der Hinweis unter dem Feld zeigt sie). |
| **Notiz** | Freiwilliger Freitext, z. B. „bis Sonntag zurück“. |
| **Ausleihen** | Hält die Ausleihe fest. Die verfügbare Menge sinkt entsprechend. |

Stimmt etwas nicht -- kein Mitglied gewählt, mehr Stück als verfügbar („Nur 1
von 2 sind gerade verfügbar.“), eine Gebühr mit Text, ein ungültiges Datum --,
zeigt die Seite die Meldung über dem Formular und behält deine Eingaben.

!!! note "Gebühren werden festgehalten, nicht berechnet"
    Die Gebühr wird mit der Ausleihe gespeichert, damit der Vorstand weiß,
    was vereinbart wurde. Eine Rechnung oder Buchung legt Parcella dafür
    nicht an.

### Ausleihhistorie {#loan-history}

Jede Ausleihe dieses Gegenstands, die neueste zuerst.

| Spalte | Was sie zeigt |
|---|---|
| **Mitglied** | Wer ihn ausgeliehen hat. |
| **Menge** | Wie viele Stück. |
| **Ausgeliehen** | Das Ausleihdatum. |
| **Zurückgegeben** | Das Rückgabedatum oder ein Badge **Ausstehend**, solange er noch weg ist. |
| **Gebühr** | Die berechnete Gebühr oder „-“. |
| **Als zurückgegeben markieren** | Hält die Rückgabe mit dem heutigen Datum fest. Erscheint bei ausstehenden Ausleihen mit Schreibrecht. |

## Gegenstandsformular {#item-form}

![Neuer Gegenstand](../assets/screenshots/inventory/form-new.png)

Dasselbe Formular dient für **Neuer Gegenstand** und **Bearbeiten**, mit
dem Titel **Inventargegenstand**.

### Allgemein {#general}

| Feld | Was es bewirkt |
|---|---|
| **Name** | Was der Gegenstand ist. Pflicht. |
| **Kategorie** | Eine deiner [Kategorien](#inventory-categories) oder **Keine Kategorie**. |
| **Beschreibung** | Freiwillige längere Beschreibung. |
| **Lagerort** | Wo er aufbewahrt wird, z. B. „Geräteschuppen“. |

### Eigentum {#ownership}

| Feld | Was es bewirkt |
|---|---|
| **Eigentum des Vereins** | Die Vorgabe. |
| **Persönliches Eigentum eines Mitglieds** | Für Dinge, die Mitglieder auf Vereinsgelände aufbewahren, aber selbst besitzen -- wichtig für Versicherung und Haftung. Zeigt **Eigentümer (Mitglied)**. |
| **Eigentümer (Mitglied)** | Das Mitglied, dem er gehört. Pflicht, wenn der Gegenstand Mitgliedseigentum ist; listet die aktuellen Mitglieder. |

### Finanzen {#financials_1}

Den aktuellen Wert trägst du von Hand ein, wann immer jemand ihn prüft.
Parcella schreibt nichts automatisch ab.

| Feld | Was es bewirkt |
|---|---|
| **Kaufdatum** | Freiwillig. |
| **Kaufpreis** | Freiwillig. |
| **Aktueller Wert** | Freiwillig. Deine aktuell beste Schätzung. |
| **Wiederbeschaffungswert** | Freiwillig. |
| **Wert zuletzt geprüft am** | Freiwilliges Datum, damit alle sehen, wie aktuell der Wert ist. |

Beträge sind nur Zahlen: `5`, `2,50` oder `2.50`. Text, ein Währungszeichen
oder ein negativer Betrag wird mit einer Meldung abgelehnt.

### Verleih {#lending}

| Feld | Was es bewirkt |
|---|---|
| **Vorhandene Menge** | Wie viele gleiche Stück dieser Eintrag darstellt -- drei Schubkarren können ein Gegenstand mit Menge 3 sein. Eine ganze Zahl ab 1; Vorgabe 1. |
| **Mitglieder können dies ausleihen** | Schaltet Ausleihe und Rückgabe für diesen Gegenstand ein. Zeigt **Vorgeschlagene Leihgebühr**. |
| **Vorgeschlagene Leihgebühr** | Freiwillig. Gilt als Gebühr, wenn eine Ausleihe ohne Gebühr erfasst wird; lässt sich je Ausleihe ändern. |

### Notizen {#notes}

Freitext für alles andere.

Mit **Speichern** sicherst du den Gegenstand und öffnest seine Seite, mit
**Abbrechen** verwirfst du.

!!! tip "Ein Eintrag je Art von Ding"
    Erfass gleiche Dinge als einen Gegenstand mit einer Menge, nicht als
    getrennte Gegenstände. Der Verleih zeigt dann „2 von 3 verfügbar“, und
    eine Preisänderung machst du nur einmal.

## Ausmustern und löschen {#retiring-and-deleting}

- **Ausmustern** für einen Gegenstand, den es wirklich gab und der jetzt
  verkauft, verschrottet oder verloren ist. Er bleibt mit seinen Preisen
  und seiner Ausleihhistorie verzeichnet, ist aber in der Liste
  ausgeblendet, solange du **Ausgemusterte Gegenstände einbeziehen** nicht
  anhakst. Eine Schaltfläche, um das Ausmustern rückgängig zu machen, gibt
  es nicht.
- **Löschen** nur bei einem echten Fehler, z. B. einem doppelt
  eingetragenen Gegenstand. Es entfernt den Gegenstand und alle seine
  Ausleihen endgültig.

## Inventarkategorien {#inventory-categories}

![Inventarkategorien](../assets/screenshots/inventory/categories.png)

**Kategorien verwalten** in der Inventarliste öffnet diese Seite. Sie
braucht Schreibrecht. **Zurück** führt zur Liste zurück.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| Name (z. B. „Spielplatz, Zäune, Schlösser & Schlüssel“) | Der Name der neuen Kategorie. Pflicht; darf noch nicht existieren („Eine Kategorie mit diesem Namen existiert bereits.“). |
| **Optionale Beschreibung** | Eine kurze Beschreibung. |
| **Hinzufügen** | Legt die Kategorie an. |
| Spalten **Name**, **Beschreibung** | Die bestehenden Kategorien. |
| Papierkorb-Schaltfläche | Löscht die Kategorie nach einer Bestätigung. Ihre Gegenstände werden **nicht** gelöscht -- sie werden **Ohne Kategorie**. Braucht Löschrecht. |

Umbenennen lassen sich Kategorien auf dieser Seite nicht. Leg dazu die neue
Kategorie an, verschieb die Gegenstände durch Bearbeiten dorthin und lösch
die alte.

## Aktive Ausleihen {#active-loans}

![Aktive Ausleihen](../assets/screenshots/inventory/active-loans.png)

**Aktive Ausleihen** in der Inventarliste zeigt alles, was gerade verliehen
ist, über alle Gegenstände hinweg, die älteste Ausleihe zuerst. Damit
siehst du vor einem Arbeitseinsatz oder am Saisonende, wer was hat.

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Gegenstand** | Der Gegenstand, verlinkt auf seine Seite. |
| **Mitglied** | Wer ihn hat. |
| **Menge** | Wie viele Stück. |
| **Seit** | Das Ausleihdatum. |
| **Gebühr** | Die berechnete Gebühr oder „-“. |
| **Als zurückgegeben markieren** | Hält die Rückgabe mit dem heutigen Datum fest und öffnet die Seite des Gegenstands. Braucht Schreibrecht. |

Ist nichts ausgeliehen, steht dort **Aktuell nichts ausgeliehen.**

!!! tip "Verfügbarkeit im Kalender sehen"
    Ist das Kalendermodul eingeschaltet, listet **Kalender → Eigene
    Kalender → Ressourcen** die ausleihbaren Gegenstände des Vereins
    (ausgemusterte nicht) mit ihrem Status -- **Verfügbar**, **Verliehen**
    oder „1 von 2 verfügbar“ -- und wer sie seit wann hat. Dafür braucht es
    auch das Leserecht fürs Inventar. Siehe [Kalender](calendar.md).

## Siehe auch {#related}

- [Mitglieder](members.md) -- Ausleiher und Eigentümer von Mitgliedseigentum
- [Einkaufswünsche](purchase-requests.md) -- Freigabe einholen, bevor etwas
  Neues gekauft wird
- [Gruppen](../administration/groups.md) -- jemandem Zugriff aufs Inventar
  geben, ohne volle Vorstandsrechte

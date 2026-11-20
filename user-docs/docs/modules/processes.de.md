# Vorgänge {#processes}

Viele Vereinsaufgaben laufen jedes Mal in denselben Schritten ab: eine
Parzelle übergeben, ein neues Mitglied begrüßen, eine Beschwerde bearbeiten.
Mit Vorgängen beschreibst du so eine Aufgabe einmal als **Vorlage** -- eine
Folge von **Stufen**, jede mit den auszufüllenden **Feldern** -- und führst
sie dann so oft aus, wie du sie brauchst, für eine Parzelle, ein Mitglied
oder einen Bewerber. Parcella hält fest, wo jeder Vorgang steht, was
eingetragen wurde und wer was getan hat.

!!! info "Wer das nutzen kann"
    - Der Modulschalter ist **Vorgänge** unter **Administration → Module
      ein- und ausschalten**. Er ist standardmäßig **an**.
    - Die Rollen **Vorstand** und **Administrator** sowie Mitglieder einer
      Gruppe mit **Voller Zugriff auf jedes Modul** können alles,
      einschließlich Vorlagen bauen.
    - Alle anderen brauchen das Recht **Vorgänge** in einer ihrer
      [Gruppen](../administration/groups.md):
        - *Lesen*: Vorgänge, ihre Werte, Dateien und ihren Verlauf sehen;
        - *Schreiben*: Vorgänge starten, Felder ausfüllen, Dateien
          hochladen, zur nächsten Stufe weitergehen oder zurückgehen;
        - *Löschen*: einen Vorgang abbrechen oder löschen.
    - **Vorlagen** lassen sich nur mit vollem Zugriff anlegen und ändern.
    - Vorgänge zu Bewerbern und Bewerberfelder brauchen außerdem
      Leserecht für das Modul [Bewerber](applicants.md). Ohne es siehst du
      „Nur sichtbar mit Zugriff auf das Bewerbermodul.“

## Wie es zusammenhängt {#how-it-fits-together}

- Eine **Vorlage** sagt, worum es im Vorgang geht (eine Parzelle, ein
  Mitglied, ein Bewerber oder nichts Bestimmtes), und listet ihre Stufen in
  Reihenfolge.
- Jede **Stufe** hat beliebig viele **Felder**. Ein Feld kann ein
  **Pflichtfeld** sein.
- Beim Starten eines Vorgangs entsteht eine Kopie der Vorlage. Spätere
  Änderungen an der Vorlage wirken nicht auf schon laufende Vorgänge.
- Ein Vorgang steht immer in genau einer **aktuellen Stufe**. Mit
  **Erledigt -- nächste Stufe** geht es weiter, sobald jedes Pflichtfeld
  dieser Stufe ausgefüllt ist. Nach der letzten Stufe ist der Vorgang
  **Abgeschlossen**.
- Du kannst zu einer früheren Stufe zurückgehen (mit Grund) oder den
  Vorgang abbrechen (mit Grund). Ein abgeschlossener oder abgebrochener
  Vorgang lässt sich nicht mehr ändern.

## Vorgangsliste {#process-list}

![Vorgangsliste](../assets/screenshots/processes/list.png)

Öffne **Vorgänge** im Menü.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Vorlagen** | Öffnet die [Vorgangsvorlagen](#process-templates). Nur mit vollem Zugriff. |
| **Vorgang starten** | Öffnet [Vorgang starten](#start-a-process). Braucht *Schreiben*. |
| **Status** | **In Bearbeitung** (Vorgabe), **Abgeschlossen/abgebrochen** oder **Alle**. |
| **Vorlage** | **Alle Vorlagen** oder eine Vorlage; archivierte Vorlagen sind mit „(archiviert)“ markiert. |
| **Filtern** | Wendet die beiden Filter an. |

| Spalte | Was sie zeigt |
|---|---|
| **Vorgang** | Der Titel (verlinkt) und darunter der Name der Vorlage. |
| **Für** | Die Parzelle, das Mitglied oder der Bewerber, verlinkt auf die jeweilige Seite. „(gelöscht)“, wenn dieser Eintrag gelöscht wurde. |
| **Aktuelle Stufe** | Die Stufe, in der der Vorgang steht, z. B. „Wertermittlung (2/6)“. Ein Strich bei geschlossenen Vorgängen. |
| **Gestartet** | Das Startdatum. |
| **Status** | **In Bearbeitung**, **Abgeschlossen** oder **Abgebrochen**. |

Ist die Liste leer, sagt sie **Keine Vorgänge.** und bietet, wenn es noch
keine Vorlagen gibt, **Zuerst eine Vorlage anlegen.** an.

!!! tip "Vorgänge auf den Seiten von Parzellen, Mitgliedern und Bewerbern"
    Die Seite einer [Parzelle](parcels.md), eines [Mitglieds](members.md) und
    eines [Bewerbers](applicants.md) hat eine Karte **Vorgänge**, die deren
    Vorgänge mit aktueller Stufe und Status listet. Ihre Schaltfläche
    **Vorgang starten** öffnet die Startseite mit dieser Parzelle, diesem
    Mitglied oder Bewerber schon ausgewählt und bietet nur die passenden
    Vorlagen an.

## Vorgang starten {#start-a-process}

![Vorgang starten](../assets/screenshots/processes/new.png)

1. Wähl die **Vorlage**. Die Seite lädt neu und zeigt die Beschreibung der
   Vorlage und ihre **Stufen**. Archivierte Vorlagen werden nicht
   angeboten.
2. Geht es in der Vorlage um eine Parzelle, ein Mitglied oder einen
   Bewerber, wähl sie oder ihn im Feld **Parzelle**, **Mitglied** oder
   **Bewerber**. Das ist Pflicht.
3. Gib bei Bedarf einen **Titel** an -- ohne Angabe wird der Name der
   Vorlage verwendet. Tipp: Nimm die Parzellennummer oder den Namen auf,
   z. B. „Übergabe Parzelle 17“, damit du Vorgänge in der Liste
   auseinanderhalten kannst.
4. Klick auf **Starten**. Der Vorgang öffnet sich in seiner ersten Stufe.

**Abbrechen** führt zur Liste zurück. Gibt es noch keine Vorlage, sagt die
Seite **Es gibt noch keine aktive Vorlage.**

## Ein laufender Vorgang {#a-running-process}

![Ein Vorgang](../assets/screenshots/processes/detail.png)

Oben siehst du den Status, die Vorlage, worum es im Vorgang geht (verlinkt)
und „Gestartet am … von …“. Darunter zeigt eine Reihe von Badges den
Fortschritt: grün mit Häkchen für erledigte Stufen, blau für die aktuelle
Stufe, grau für Stufen, die noch kommen. Ein Klick auf ein Badge springt zu
dieser Stufe.

Ein abgeschlossener Vorgang zeigt **Abgeschlossen am ….**, ein
abgebrochener **Abgebrochen**, das Datum und den Grund.

### Die Stufen {#the-stages}

Jede Stufe ist eine Karte mit ihrer Nummer und ihrem Namen.

- **Erledigte Stufen** zeigen das Datum und wer sie erledigt hat. Ihre
  Felder lassen sich korrigieren, solange der Vorgang offen ist.
- Die **aktuelle Stufe** ist als **Aktuelle Stufe** markiert und blau
  umrahmt.
- **Noch nicht erreichte Stufen** sind als **Noch nicht erreicht** markiert
  und listen nur die Namen ihrer Felder.

In einer bearbeitbaren Stufe füllst du die Felder aus und klickst auf
**Speichern**. Das speichert die Felder dieser einen Stufe. Dateien werden
getrennt hochgeladen (siehe unten). Ist ein Wert ungültig, siehst du eine
Meldung wie **Bitte eine gültige Zahl eingeben.** oder **Bitte ein gültiges
Datum eingeben.**

### Weitergehen {#moving-on}

Unten in der aktuellen Stufe:

- **Fehlt noch, bevor es weitergeht:** listet die Pflichtfelder, die noch
  leer sind, jedes verlinkt auf sein Feld. Solange etwas gelistet ist, ist
  die Schaltfläche gesperrt.
- **Erledigt -- nächste Stufe** schließt die Stufe ab und bringt den Vorgang
  weiter. In der letzten Stufe heißt die Schaltfläche **Vorgang
  abschließen**.

Ein Pflicht-Häkchen gilt als ausgefüllt, sobald es gesetzt ist; ein
Pflicht-Dateifeld, sobald es mindestens eine Datei hat.

### Zurückgehen {#go-back}

Die Karte **Zurückgehen** (mit *Schreiben*, sobald der Vorgang über seine
erste Stufe hinaus ist) bringt den Vorgang zu einer früheren Stufe zurück,
zum Beispiel wenn eine Begehung wiederholt werden muss.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Zurück zu Stufe** | Zu welcher früheren Stufe es zurückgeht. Die vorherige Stufe ist vorausgewählt. |
| **Grund** | Pflicht. Kommt in den Verlauf. |
| **Zurückgehen** | Setzt den Vorgang zurück. Alle bisher eingetragenen Werte bleiben erhalten. |

### Verlauf {#history}

Die Karte **Verlauf** listet alles, was passiert ist, das Neueste oben, mit
Zeit, Stufe, Notiz und Benutzer: **Gestartet**, **Weiter zu**, **Zurück
zu**, **Abgeschlossen**, **Abgebrochen**, **Feld geändert** (mit altem und
neuem Wert), **Datei hinzugefügt** und **Datei entfernt**.

### Abbrechen oder löschen {#abort-or-delete}

Nur mit Recht *Löschen*:

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Vorgang abbrechen** + **Grund** + **Abbrechen** | Beendet einen offenen Vorgang endgültig, nach **Diesen Vorgang wirklich abbrechen? Er kann nicht wieder geöffnet werden.** Der Grund ist Pflicht und wird beim Vorgang angezeigt. Der Vorgang bleibt als **Abgebrochen** in der Liste. |
| **Vorgang löschen** | Entfernt den Vorgang vollständig, mit allen Werten und Dateien, nach **Diesen Vorgang mit allen Werten und Dateien wirklich löschen?** Nur für einen versehentlich gestarteten Vorgang. Dateien in der Cloud werden nicht gelöscht. |

## Feldarten {#field-types}

| Art | Was du in einem Vorgang einträgst |
|---|---|
| **Text** | Eine Zeile, bis zu 1.000 Zeichen. |
| **Langer Text** | Mehrere Zeilen. |
| **Zahl** | Eine Zahl. Komma und Punkt gehen beide als Dezimaltrenner („1.234,50“ und „1,234.50“). |
| **Geldbetrag** | Wie eine Zahl, angezeigt mit der Währung deines Vereins. |
| **Datum** | Ein Datum. |
| **Häkchen** | Gesetzt oder nicht, z. B. „Schlüssel übergeben“. |
| **Auswahl aus Liste** | Eine der in der Vorlage festgelegten Optionen. |
| **Dateien (PDF, Fotos)** | Eine oder mehrere hochgeladene Dateien. |
| **Mitglied** | Ein Mitglied des Vereins. |
| **Bewerber** | Ein Bewerber (braucht Zugriff aufs Bewerbermodul). |
| **Parzelle** | Eine Parzelle. |

Ein Feld kann einen Hilfetext haben, der darunter steht.

### Dateien {#files}

Ein Dateifeld listet seine Dateien mit Name, Größe, Datum und wer sie
hochgeladen hat; ein Wolken-Symbol heißt **In der Cloud gespeichert**. Ein
Klick auf einen Namen öffnet die Datei oder lädt sie herunter. Zum
Hinzufügen nimm **Datei auswählen** und **Hochladen**; das kleine x entfernt
eine Datei nach **Diese Datei entfernen?** (solange die Stufe bearbeitbar
ist).

Nur PDF, JPEG, PNG oder WebP, bis 20 MB. Unter der Hochladen-Schaltfläche
sagt Parcella, wohin die Datei kommt, in dieser Reihenfolge:

1. **Der Cloud-Ordner der Parzelle**, in einem Unterordner für diesen
   Vorgang -- wenn das Cloud-Speicher-Modul an ist und es im Vorgang um eine
   Parzelle mit Cloud-Ordner geht oder um ein Mitglied mit genau einer
   aktuellen Parzelle, die einen hat.
2. **Der Ordner für Vorgangsdateien**, wenn ein Administrator unter
   **Administration → Integrationen** einen **Ordner für Vorgangsdateien**
   festgelegt hat.
3. Sonst **Parcellas privater Speicher**: „Wird in Parcellas privatem
   Speicher abgelegt (kein Cloud-Ordner für diese Parzelle oder für Prozesse
   eingerichtet).“

!!! warning "Parzellenordner sind oft mit den Pächtern geteilt"
    Sind deine Parzellenordner in der Cloud mit den Pächtern der Parzelle
    geteilt, sehen sie auch die Dateien von Vorgängen zu ihrer Parzelle.
    Das ist so gewollt -- offizielle Unterlagen zu einer Parzelle sind für
    ihre Pächter offen. Willst du Dateien nur für den Vorstand, leg an der
    Parzelle keinen Cloud-Ordner fest und nimm stattdessen den Ordner für
    Vorgangsdateien.

Entfernst du eine Datei aus einem Vorgang, wird eine Datei in Parcellas
eigenem Speicher gelöscht, eine Datei in der Cloud dagegen nur abgehängt;
die Datei selbst bleibt dort.

## Vorgangsvorlagen {#process-templates}

![Vorgangsvorlagen](../assets/screenshots/processes/templates.png)

**Vorlagen** in der Vorgangsliste (nur mit vollem Zugriff) öffnet die
**Vorgangsvorlagen**. **Vorgänge** oben rechts führt zurück.

Die Karte **Vorlagen** listet jede Vorlage mit dem, worum es geht, ihrer
Zahl an Stufen, wie oft sie verwendet wurde, und **archiviert**, wenn sie
archiviert ist. **Bearbeiten** öffnet den
[Vorlagen-Editor](#the-template-editor).

### Neue Vorlage {#new-template}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name** | Pflicht, bis zu 200 Zeichen. |
| **Ein Vorgang betrifft** | **Parzelle**, **Mitglied**, **Bewerber** oder **Nicht zugeordnet**. Beim Start eines Vorgangs wird die Parzelle, das Mitglied oder der Bewerber ausgewählt, und der Vorgang erscheint auf deren Seite. |
| **Beschreibung** | Freiwillig. Erscheint, wenn jemand die Vorlage zum Starten eines Vorgangs wählt. |
| **Anlegen** | Legt die Vorlage an und öffnet den Editor. |

### Mit einem Beispiel beginnen {#start-from-an-example}

Legt eine normale Vorlage in deiner Sprache an, die du danach frei ändern
kannst. Klick auf **Übernehmen** neben:

- **Parzellenübergabe** -- eine gekündigte Parzelle auf dem Weg zum
  nächsten Pächter: Begehung, Wertermittlung, Ausschreibung, neuer Pächter,
  Vertrag und Übergabe.
- **Aufnahme neuer Mitglieder** -- ein neues Mitglied willkommen heißen:
  erstes Gespräch, Unterlagen und letzte Details.

## Der Vorlagen-Editor {#the-template-editor}

![Vorlagen-Editor](../assets/screenshots/processes/template-edit.png)

Der Editor ist mit „Vorlage: …“ überschrieben. Änderungen werden gespeichert,
während du sie machst; oben rechts erscheint kurz eine Bestätigung.

Der Kopf zeigt den Namen, worum es in der Vorlage geht, und einen Hinweis:
„Änderungen gelten für Vorgänge, die ab jetzt gestartet werden. Bereits
gestartete Vorgänge (…) behalten ihre Stufen und Felder.“

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Details** | Öffnet Name, **Ein Vorgang betrifft** und Beschreibung zum Bearbeiten; **Speichern** sichert sie. |
| **Archivieren** / **Wiederherstellen** | Mit einer archivierten Vorlage lassen sich keine neuen Vorgänge starten; laufende gehen weiter. |
| **Löschen** | Nur solange aus der Vorlage noch kein Vorgang gestartet wurde, nach **Diese Vorlage wirklich löschen?** Sonst archivier sie. |

### Stufen {#stages}

Die linke Karte listet die **Stufen** in Reihenfolge, mit ihrer Zahl an
Feldern. Ein Klick auf eine öffnet sie zum Bearbeiten. Zieh eine Stufe an
ihrem Griff, um die Reihenfolge zu ändern. Eine Stufe fügst du hinzu, indem
du einen Namen in **Neue Stufe, z. B. „Begehung“** eintippst und auf
**Hinzufügen** klickst.

Die gewählte Stufe steht rechts:

- Ihr **Name** und ihre **Beschreibung (optional)** lassen sich direkt
  bearbeiten. Die Beschreibung erscheint in einem laufenden Vorgang oben in
  der Stufe.
- Das Menü **⋮** (**Aktionen für die Stufe**) hat **Nach oben**, **Nach
  unten** und **Stufe löschen** (nach **Diese Stufe mit allen Feldern
  löschen?**).

### Felder {#fields}

Der Reiter **Felder** listet die Felder der Stufe mit ihrer Art, ihren
Optionen, ihrem Hilfetext und einem Badge **Pflichtfeld**. Eine Stufe ohne
Felder ist ein einfacher Schritt zum Abhaken.

Für ein neues Feld tippst du seine Bezeichnung in **Neues Feld: Bezeichnung
eingeben, Enter drücken**, wählst den **Typ**, hakst bei Bedarf
**Pflichtfeld** an und drückst Enter oder klickst auf **Feld hinzufügen**.
Bei **Auswahl aus Liste** öffnet sich zuerst ein Seitenfeld, weil eine
Auswahl ihre Optionen braucht.

Zieh Felder an ihrem Griff, um die Reihenfolge zu ändern. Ein Klick auf ein
Feld öffnet das Seitenfeld **Feld bearbeiten**:

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Bezeichnung** | Pflicht, bis zu 200 Zeichen. |
| **Art** | Eine der [Feldarten](#field-types). |
| **Optionen (nur bei Auswahl, eine pro Zeile)** | Pflicht bei **Auswahl aus Liste**: mindestens eine Option. |
| **Pflichtfeld** | Der Vorgang kann erst weiter, wenn dieses Feld ausgefüllt ist. |
| **Hilfetext (optional)** | Erscheint in einem laufenden Vorgang unter dem Feld. |
| **Speichern** / **Schließen** | Speichert das Feld / schließt das Seitenfeld. |
| **In Stufe verschieben** + Pfeil-Schaltfläche | Verschiebt das Feld ans Ende einer anderen Stufe. |
| **Nach oben** / **Nach unten** | Ändert die Reihenfolge, ohne zu ziehen. |
| **Duplizieren** | Fügt direkt darunter eine Kopie ein. |
| **Feld löschen** | Entfernt das Feld aus der Vorlage. |

Der Reiter **Vorschau** zeigt, wie die Stufe in einem laufenden Vorgang
aussieht, mit gesperrten Eingaben.

## Durchgespieltes Beispiel: eine Parzellenübergabe {#worked-example-a-plot-handover}

Ein Pächter hat Parzelle 17 gekündigt. So wickelt der Vorstand die Übergabe
mit dem Beispiel **Parzellenübergabe** ab.

**Einmal: die Vorlage einrichten.** Öffne **Vorgänge → Vorlagen** und klick
auf **Übernehmen** neben **Parzellenübergabe**. Du bekommst eine Vorlage zu
einer **Parzelle** mit sechs Stufen:

| # | Stufe | Felder (* = Pflicht) |
|---|---|---|
| 1 | Begehung | Datum der Begehung*, Festgestellte Mängel, Fotos der Mängel, Alle Mängel behoben* |
| 2 | Wertermittlung | Wertermittler*, Datum der Wertermittlung*, Wertermittlungsprotokoll* (Datei) |
| 3 | Ausschreibung | Ausschreibungstext*, Fotos für die Ausschreibung, Veröffentlicht am* |
| 4 | Neuer Pächter | Neuer Pächter* (Bewerber), Kontakt hergestellt*, Unterlagen verschickt* |
| 5 | Vertrag und Kaution | Kaufvertrag bestätigt*, Kaution (Betrag), Kaution eingegangen am |
| 6 | Übergabe | Vom neuen Pächter unterschrieben*, Vom Vorstand gegengezeichnet*, Schlüssel übergeben*, Zähler abgelesen*, Übergabeprotokoll (Datei) |

Pass sie an deinen Verein an: Mach zum Beispiel **Kaution** zur Pflicht oder
füg ein Feld **Auswahl aus Liste** „Ergebnis der Wertermittlung“ mit den
Optionen „Übernahme zum Schätzwert“ und „Parzelle ist zu räumen“ hinzu.

**Jedes Mal: ausführen.**

1. Öffne Parzelle 17 und klick in ihrer Karte **Vorgänge** auf **Vorgang
   starten**. **Parzellenübergabe** und die Parzelle sind schon gewählt.
   Gib den Titel „Übergabe Parzelle 17“ ein und klick auf **Starten**.
2. **Begehung**: Trag nach dem Rundgang das Datum ein, liste die Mängel auf,
   lade Fotos hoch und klick auf **Speichern**. Abschließen lässt sich die
   Stufe noch nicht: **Alle Mängel behoben** fehlt noch. Sobald der Pächter
   alles behoben hat, hak es an, **Speichern**, dann **Erledigt -- nächste
   Stufe**.
3. **Wertermittlung**: Trag Wertermittler und Datum ein und lade das
   Protokoll als PDF hoch. Hat die Parzelle einen Cloud-Ordner, landet das
   Protokoll dort in einem Unterordner für diese Übergabe. **Erledigt --
   nächste Stufe**.
4. **Ausschreibung** und **Neuer Pächter**: Halte die Ausschreibung fest,
   wähl dann die ausgewählte Person aus der Bewerberliste und hak die beiden
   Kästchen an.
5. **Vertrag und Kaution**: Bestätige den Vertrag, trag die Kaution und den
   Tag ihres Eingangs ein.
6. **Übergabe**: Hak Unterschriften, Schlüssel und Zählerstände an, lade das
   Übergabeprotokoll hoch und klick auf **Vorgang abschließen**.

Springt der neue Pächter in Stufe 5 ab, geh mit **Zurückgehen** zu
**Ausschreibung** zurück, mit dem Grund „Bewerber hat zurückgezogen“. Die
bisher eingetragenen Werte bleiben, und der Verlauf zeigt, was passiert ist.

Der Vorgang selbst hält nur die Übergabe fest. Das alte Pachtverhältnis
beenden, das neue beginnen und die Zähler in Parcella ablesen machst du in
den Modulen [Parzellen](parcels.md) und [Wasser und Strom](metering.md) -- siehe
die [Anleitung zur Parzellenübergabe](../guides/parcel-handover.md).

## Siehe auch {#related}

- [Eine Parzelle übergeben](../guides/parcel-handover.md)
- [Parzellen](parcels.md), [Mitglieder](members.md),
  [Bewerber](applicants.md) -- die Karte **Vorgänge** auf ihren Seiten.
- [Integrationen](../administration/integrations.md) -- der Ordner für
  Vorgangsdateien.
- [Gruppen](../administration/groups.md) -- jemandem Rechte für Vorgänge
  geben.

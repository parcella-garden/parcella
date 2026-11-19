# Parzellen {#parcels}

Die Parzellenliste enthält jeden Garten deines Vereins: seine Nummer, seine
Fläche, seinen Status und wer ihn hat. Jede Parzelle behält ihren
vollständigen Pachtverlauf, sodass du noch Jahre später siehst, wer welchen
Garten wann hatte.

!!! info "Wer das nutzen kann"
    Parzellen gehört zum Kern und ist immer eingeschaltet. Es lässt sich
    nicht abschalten.

    - **Alle, die sich anmelden können**, dürfen die Parzellenliste, die
      Parzellenseiten und den CSV-Export ansehen.
    - **Anlegen und Bearbeiten** von Parzellen sowie Pacht zuordnen,
      bearbeiten und beenden braucht das Recht *Schreiben* bei
      **Mitglieder & Parzellen**.
    - **Löschen** eines früheren Pachteintrags oder das endgültige Löschen
      einer Parzelle braucht das Recht *Löschen* bei **Mitglieder &
      Parzellen**.
    - Die Karte **Dokumente (Cloud-Speicher)** auf einer Parzellenseite ist
      nur für Vorstandsmitglieder und Administratoren da, und nur solange
      das Modul **Cloud-Speicher** eingeschaltet ist (standardmäßig aus).

    Siehe [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md).

## Parzellenstatus {#parcel-statuses}

Jede Parzelle hat einen von vier Status:

| Status | Bedeutung |
|---|---|
| **aktiv** | Eine normale, verpachtete Parzelle. |
| **gekündigt** | Die Pacht ist gekündigt -- die Parzelle wartet auf einen neuen Pächter. Nur gekündigte Parzellen lassen sich [an Bewerber übergeben](applicants.md#assign-a-parcel). |
| **Gemeinschaftsfläche** | Eine Fläche, die der Verein selbst bewirtschaftet -- Wege, der Spielplatz, die Wiese am Vereinsheim. Du erfasst sie wie eine Parzelle mit ihrer Fläche, sie wird aber nicht an Mitglieder verpachtet. Entscheidet der Verein doch, sie zu verpachten, kannst du sie auf **aktiv** zurückstellen. |
| **gelöscht** | Die Parzelle gibt es nicht mehr, z. B. nachdem zwei Gärten zusammengelegt wurden. Ihr Verlauf bleibt erhalten. |

Den Status änderst du im [Parzellenformular](#new-parcel-and-edit-parcel).
Jede Änderung wird mit Datum und Benutzer in der Änderungshistorie der
Parzelle festgehalten; ein eigenes Kündigungsdatum brauchst du also nicht.

## Parzellenliste {#parcel-list}

![Parzellenliste](../assets/screenshots/parcels/list.png)

Öffne **Parzellen** im Hauptmenü. Die Liste zeigt jede Parzelle, sortiert
nach Gartennummer -- auch gelöschte, solange du nicht nach Status filterst.

### Schaltflächen oben {#buttons-at-the-top}

| Schaltfläche | Was sie bewirkt |
|---|---|
| **CSV Import** | Öffnet den Import-Dialog (siehe [Parzellen aus einer CSV-Datei importieren](#importing-parcels-from-a-csv-file)). Braucht Schreibrecht. |
| **CSV Export** | Lädt alle Parzellen als CSV-Datei herunter (siehe [CSV-Export](#csv-export)). |
| **Neue Parzelle** | Öffnet ein leeres [Parzellenformular](#new-parcel-and-edit-parcel). Braucht Schreibrecht. |

### Suche und Filter {#search-and-filter}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Gartennummer suchen…** | Findet Parzellen, deren Gartennummer den Text enthält. Um eine Parzelle über den Namen ihres Pächters zu finden, durchsuch stattdessen die [Mitgliederliste](members.md#search-and-filters). |
| **Alle Status** | Zeigt nur Parzellen mit dem gewählten Status. Wirkt, sobald du ihn änderst. |
| **Suchen** | Wendet den Suchtext an. |
| **Zurücksetzen** | Hebt Suche und Statusfilter auf. Erscheint nur, solange einer aktiv ist. |

Wie in der Mitgliederliste behalten **Vorherige**, **Nächste** und
**Zurück** auf einer Parzellenseite den Filter, aus dem du kamst.

### Spalten {#columns}

| Spalte | Was sie zeigt |
|---|---|
| **Gartennummer** | Ein Klick öffnet die Parzelle. |
| **Fläche** | Fläche in Quadratmetern oder „–“. |
| **Status** | **aktiv**, **gekündigt**, **Gemeinschaftsfläche** oder **gelöscht**. |
| **Pächter** | Die aktuellen Pächter. Ein Klick auf einen Namen öffnet das Mitglied. Frühere und künftige Pächter stehen hier nicht. |
| Augen-Schaltfläche | Öffnet die Parzellenseite. |

Die Fußzeile zeigt die Zahl der Parzellen in der Liste und, wenn Flächen
erfasst sind, ihre Gesamtfläche -- praktisch, um eine gefilterte Auswahl zu
prüfen, z. B. die Gesamtfläche aller aktiven Parzellen.

### CSV-Export {#csv-export}

**CSV Export** lädt eine Datei namens `parcels.csv` herunter, getrennt
durch Semikolons, mit *jeder* Parzelle -- Suche und Statusfilter gelten
nicht. Die Spaltenüberschriften sind deutsch, damit sich die Datei wieder
importieren lässt:

Gartennummer, Fläche (qm), Breitengrad, Längengrad, Status,
Kündigungsnotiz, Mitglieder, Notizen.

- Zahlen stehen mit Dezimalkomma (312,5).
- Der Status steht als ACTIVE, TERMINATED, COMMUNAL oder DELETED.
- Die Spalte Mitglieder listet die Pächter der Parzelle, getrennt durch
  Semikolons, die als Rechnungsadresse markierten zuerst und mit einem `*`
  hinter dem Namen.

## Parzellen aus einer CSV-Datei importieren {#importing-parcels-from-a-csv-file}

Mit dem Import legst du alle Parzellen auf einmal an, zum Beispiel aus einer
Tabellenkalkulation. Er funktioniert wie der Mitgliederimport: Datei
hochladen, Spalten zuordnen, bestätigen. Eine Schritt-für-Schritt-Anleitung
findest du unter [Mitglieder und Parzellen importieren](../guides/csv-import.md).

!!! tip "Erst Parzellen importieren, dann Mitglieder"
    Der Import legt nur Parzellen an -- er ordnet keine Pächter zu. Pächter
    ordnest du danach auf jeder Parzellen- oder Mitgliederseite zu.

### Schritt 1: die Datei hochladen {#step-1-upload-the-file}

Klick in der Parzellenliste auf **CSV Import**. Wähl im Dialog
**CSV-Import** eine `.csv`-Datei und klick auf **Importieren**. Noch wird
nichts gespeichert.

- Spalten dürfen durch Semikolons oder Kommas getrennt sein; Parcella
  erkennt es.
- Die erste Zeile muss die Überschriftenzeile sein. Die Überschriften
  müssen nicht genau passen -- du ordnest sie im nächsten Schritt zu.

Ist die Datei leer, kommst du mit „Diese CSV-Datei scheint leer zu sein.“
zurück.

### Schritt 2: die Spalten zuordnen {#step-2-map-the-columns}

Die Seite **CSV-Spalten zuordnen** zeigt jede Spalte deiner Datei mit
Überschrift und den ersten fünf Datenzeilen.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| Auswahl je Spalte | Wähl **Gartennummer**, **Fläche (qm)**, **Breitengrad**, **Längengrad**, **Status**, **Notizen** -- oder **— Ignorieren —**. Parcella wählt ein Feld vor, wenn es die Überschrift erkennt (auf Deutsch oder Englisch, z. B. „Gartennummer“ oder „Plot number“). |
| **Importieren** | Importiert die Zeilen und führt zur Parzellenliste zurück. **Gartennummer** muss einer Spalte zugeordnet sein, sonst erscheint „Bitte ordnen Sie vor dem Import die Spalte für die Gartennummer zu.“ |
| **Zurück** | Führt ohne Import zur Parzellenliste zurück. |

### Was beim Import passiert {#what-happens-on-import}

- Gartennummern werden großgeschrieben, genau wie im Formular.
- Eine Zeile, deren Gartennummer **schon existiert, wird übersprungen** --
  bestehende Parzellen ändert ein Import nie.
- Eine Zeile ohne Gartennummer wird ignoriert.
- Fläche, Breiten- und Längengrad dürfen Dezimalpunkt oder -komma haben.
  Ein Wert, der keine Zahl ist, bleibt leer.
- **Status** muss ACTIVE, TERMINATED, COMMUNAL oder DELETED sein
  (Großbuchstaben egal). Alles andere oder eine leere Zelle wird zu
  **aktiv**.

Die Parzellenliste zeigt danach eine Zusammenfassung wie „40 importiert,
2 übersprungen“ und dazu, wie viele Zeilen ohne Gartennummer ignoriert
wurden.

## Parzellenseite {#parcel-page}

![Parzellenseite](../assets/screenshots/parcels/detail.png)

Ein Klick auf eine Gartennummer öffnet die Parzellenseite. Sie zeigt die
Angaben zur Parzelle, wer sie jetzt hat, wer sie vorher hatte und was sich
geändert hat.

### Schaltflächen oben {#buttons-at-the-top_1}

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Bearbeiten** | Öffnet das [Bearbeitungsformular](#new-parcel-and-edit-parcel). Braucht Schreibrecht. |
| **Vorherige** / **Nächste** | Springt zur vorherigen oder nächsten Parzelle der Liste, aus der du kamst. Auch ++ctrl+left++ und ++ctrl+right++ funktionieren (nicht beim Tippen in einem Feld). |
| **Zurück** | Führt zur Parzellenliste zurück, mit deinem Filter. |

### Parzellendetails {#parcel-details}

| Zeile | Was sie zeigt |
|---|---|
| **Gartennummer** | |
| **Fläche** | In Quadratmetern. |
| **Koordinaten** | Nur wenn Breiten- und Längengrad beide erfasst sind. **Auf Karte anzeigen** öffnet die Stelle auf OpenStreetMap in einem neuen Tab. |
| **Status** | Der aktuelle Status. |
| **Gekündigt am** | Wann der Status zuletzt auf **gekündigt** gesetzt wurde, aus der Änderungshistorie. |
| **Kündigungsnotiz** | Grund oder Anmerkungen, falls erfasst. |
| **Angelegt** | Wann die Parzelle in Parcella erfasst wurde. |
| **Notizen** | Die internen Notizen zur Parzelle, falls vorhanden. |

Unter den Details listet eine Karte **Vorgänge** die
[Vorgänge](processes.md) zu dieser Parzelle, wenn das Modul eingeschaltet
ist und du Vorgänge sehen darfst. **Vorgang starten** beginnt einen neuen.

### Aktuelle Pächter {#current-tenants}

Die Mitglieder, die die Parzelle jetzt haben, dazu alle, die sie zu einem
künftigen Datum übernehmen.

| Spalte | Was sie zeigt |
|---|---|
| **Mitglied** | Der Name des Pächters -- ein Klick öffnet das Mitglied. Ein blaues Badge **ab *Datum*** markiert einen künftigen Pächter, der an diesem Tag übernimmt. Ein Badge **bis *Datum*** markiert einen Pächter, der gekündigt hat und an diesem Tag geht. |
| **Rechnungsadresse** | Ob Rechnungen für diese Parzelle an die Adresse dieses Mitglieds gehen. |
| **Seit** | Der Beginn der Pacht oder „–“, wenn keiner eingetragen ist. |
| Stift-Schaltfläche | Öffnet [Pachtverhältnis bearbeiten](#edit-tenancy), um Daten oder die Rechnungsadresse zu ändern. Braucht Schreibrecht. |
| Kalender-Schaltfläche | **Pachtverhältnis beenden** (siehe unten). Braucht Schreibrecht. |

Hat niemand die Parzelle, steht auf der Karte „Keine aktuellen Pächter“.

#### Einen Pächter zuordnen {#assigning-a-tenant}

Unten auf der Karte (braucht Schreibrecht):

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Mitglied wählen…** | Einen Namen eintippen und das Mitglied aus der erscheinenden Liste wählen. Nur aktive Mitglieder stehen zur Wahl. Wählst du nicht aus der Liste, erscheint „Bitte ein Mitglied aus der Liste auswählen“. |
| Datumsfeld | Der erste Tag der Pacht. Freiwillig. |
| **Als Rechnungsadresse verwenden** | Standardmäßig angehakt. Rechnungen für diese Parzelle gehen an die Adresse dieses Mitglieds. |
| **Zuordnen** | Fügt das Mitglied als Pächter hinzu. |

Du kannst einer Parzelle mehrere Mitglieder zuordnen -- etwa ein Paar oder
eine Familie. Alle gelten als gleichberechtigte Pächter; einen
„Hauptpächter“ gibt es nicht. **Als Rechnungsadresse verwenden** kannst du
auch bei mehreren anhaken.

!!! note "Einen früheren Pächter erneut zuordnen"
    Hatte das Mitglied diese Parzelle schon einmal, öffnet Parcella seine
    alte Pacht wieder, statt eine zweite anzulegen. Das neue Beginndatum
    ersetzt das alte (heute, wenn du das Datum leer lässt), und der frühere
    Zeitraum erscheint nicht mehr unter **Frühere Pächter**.

!!! tip "Eine Parzelle an einen neuen Pächter übergeben"
    Kommt der neue Pächter von der Warteliste, nutz stattdessen **Parzelle
    zuweisen** auf der [Bewerberseite](applicants.md#assign-a-parcel). Das
    beendet die alte Pacht, legt das neue Mitglied an und aktiviert die
    Parzelle in einem Schritt. Siehe auch
    [Eine Parzelle übergeben](../guides/parcel-handover.md).

#### Eine Pacht beenden {#ending-a-tenancy}

Klick auf die Kalender-Schaltfläche neben einem Pächter und bestätige
„Pachtverhältnis beenden? (Historie bleibt erhalten)“.

- Die Pacht endet **heute**. Das Mitglied wandert sofort zu **Frühere
  Pächter**, mit heute als Enddatum.
- Das Mitglied ist nicht mehr die Rechnungsadresse für diese Parzelle.
- Nichts wird gelöscht: Die Pacht bleibt im Verlauf der Parzelle sichtbar
  und lässt sich später korrigieren.
- Die **Mitgliedschaft** wird nicht beendet. Verlässt das Mitglied den
  Verein, setz **Mitglied bis** auf seiner
  [Mitgliederseite](members.md#membership).
- Der **Status** der Parzelle ändert sich nicht. Wartet die Parzelle jetzt
  auf einen neuen Pächter, setz sie im Parzellenformular auf **gekündigt**.
- Hat die Parzelle jetzt keinen aktuellen oder künftigen Pächter mehr, wird
  ihr Dokumentenordner im Cloud-Speicher (falls gesetzt) stillgelegt.

Die Schaltfläche funktioniert nur bei einer Pacht ohne Enddatum. Für einen
Pächter, der schon zu einem künftigen Datum gekündigt hat, änderst du das
Datum stattdessen in [Pachtverhältnis bearbeiten](#edit-tenancy).

!!! tip "Zu einem anderen Tag als heute beenden"
    Um eine Pacht festzuhalten, die an einem anderen Tag endete (oder enden
    wird), öffne die Stift-Schaltfläche und trag **Pächter bis** ein.

### Frühere Pächter {#former-tenants}

Erscheint nur, wenn die Parzelle früher Pächter hatte. Listet jede beendete
Pacht, die jüngste zuerst.

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Mitglied** | Ein Klick auf den Namen öffnet das Mitglied. |
| **Von** / **Bis** | Der Zeitraum der Pacht. |
| Stift-Schaltfläche | **Zeitraum korrigieren** -- öffnet [Pachtverhältnis bearbeiten](#edit-tenancy), z. B. um ein falsches Datum zu berichtigen. Braucht Schreibrecht. |
| Papierkorb-Schaltfläche | **Eintrag löschen** nach der Bestätigung „Diesen Eintrag wirklich endgültig löschen? Das kann nicht rückgängig gemacht werden.“ Braucht Löschrecht. |

!!! warning "Eine frühere Pacht löschen ist nur für Fehler"
    Löschen entfernt den Eintrag endgültig -- gedacht für eine Zuordnung,
    die versehentlich oder doppelt eingetragen wurde. Bei einem normalen
    Pächterwechsel beendest du die Pacht, löschst sie aber nie. Nur
    beendete Pachten lassen sich löschen; eine aktuelle muss erst beendet
    werden.

### Dokumente (Cloud-Speicher) {#documents-cloud-storage}

Nur für Vorstandsmitglieder und Administratoren sichtbar, solange das Modul
**Cloud-Speicher** eingeschaltet ist. Es verbindet die Parzelle mit einem
Ordner im Cloud-Speicher deines Vereins (zum Beispiel Nextcloud), in dem du
Pachtverträge und andere Unterlagen der aktuellen Pächter ablegst. Richte
den Speicher zuerst unter [Integrationen](../administration/integrations.md)
ein.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Ordnerpfad** | Der Pfad des Ordners zur aktuellen Pacht, z. B. „kgv_dokumente/parzellen/G016/2024-03_016_Mueller“. Der Ordner muss schon existieren und in deinem Cloud-Speicher mit den Pächtern geteilt sein. |
| **Durchsuchen…** | Öffnet **Ordner auswählen**: Klick dich durch die Ordner (oder tipp in **Ordner filtern…**) und klick dann auf **Diesen Ordner verwenden**. Ein Doppelklick auf einen Ordner wählt ihn sofort. Das Stammverzeichnis des Speichers selbst kannst du nicht wählen -- „Öffnen Sie zuerst einen Ordner, bevor Sie ihn auswählen.“ |
| **Speichern** | Speichert den Ordnerpfad. |
| Dateiliste | Zeigt Dateien und Unterordner des Ordners mit **Name** und **Zuletzt geändert**. Ein Klick auf einen Unterordner öffnet ihn; der Pfad darüber führt zurück. Die Download-Schaltfläche lädt eine Datei herunter. |
| Dateifeld + **Hochladen** | Lädt eine Datei in den Ordner, den du gerade ansiehst. |

Endet eine Pacht und hat niemand mehr die Parzelle, wird der Ordner
automatisch stillgelegt, damit die nächsten Pächter die alten Unterlagen
nicht sehen. Nach einer Übergabe mit künftigem Datum sagt dir ein Hinweis,
wann der aktuelle Ordner stillgelegt wird und welcher Ordner an diesem Tag
übernimmt.

### Änderungshistorie {#change-history}

Erscheint erst, wenn etwas geändert wurde. Jede Änderung an Gartennummer,
Fläche, Koordinaten, Status, Kündigungsnotiz oder Notizen wird festgehalten:

| Spalte | Was sie zeigt |
|---|---|
| **Zeitpunkt** | Datum und Uhrzeit der Änderung. |
| **Feld** | Der technische Name des geänderten Felds, z. B. *status* oder *area_sqm*. |
| **Alter Wert** / **Neuer Wert** | Der Wert vorher und nachher. |
| **Geändert von** | Der Benutzer, der die Änderung gemacht hat, oder **Unbekannt**. |

Änderungen an Pachten erscheinen hier nicht -- die stehen in den
Pächtertabellen darüber.

## Neue Parzelle und Parzelle bearbeiten {#new-parcel-and-edit-parcel}

![Formular Neue Parzelle](../assets/screenshots/parcels/form-new.png)

Klick auf **Neue Parzelle** in der Parzellenliste oder auf **Bearbeiten**
auf einer Parzellenseite. Das Bearbeitungsformular hat ein paar Felder mehr
als das Formular für eine neue Parzelle.

![Formular Parzelle bearbeiten](../assets/screenshots/parcels/form-edit.png)

| Feld | Was es bewirkt |
|---|---|
| **Gartennummer** \* | Pflicht, z. B. „G093“ oder „G26/27“. Wird automatisch großgeschrieben. Muss eindeutig sein: Hat schon eine andere Parzelle diese Nummer, erscheint „Gartennummer '…' existiert bereits.“ |
| **Fläche (qm)** | Die Fläche in Quadratmetern. Dezimalpunkt und -komma funktionieren beide. Für flächenabhängige Gebühren und Statistiken. |
| **Breitengrad** / **Längengrad** | Freiwillige GPS-Position der Parzelle, z. B. 51.339695 und 12.373075. Sind beide ausgefüllt, verlinkt die Parzellenseite auf eine Karte. Der Breitengrad muss zwischen -90 und 90 liegen, der Längengrad zwischen -180 und 180. Die Position erscheint nie auf öffentlichen Seiten. |
| **Status** | Nur im Bearbeitungsformular. **aktiv**, **gekündigt**, **Gemeinschaftsfläche** oder **gelöscht** -- siehe [Parzellenstatus](#parcel-statuses). Der Zeitpunkt der Änderung wird automatisch festgehalten. Neue Parzellen beginnen immer als **aktiv**. |
| **Kündigungsnotiz** | Nur im Bearbeitungsformular. Grund oder Anmerkungen zu einer Kündigung. |
| **Notizen** | Interne Notizen zur Parzelle. |

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Parzelle anlegen** / **Änderungen speichern** | Speichert und öffnet die Parzellenseite. |
| **Abbrechen** | Verlässt das Formular ohne Speichern. |

### Gefahrenzone {#danger-zone}

Das Bearbeitungsformular endet mit einer **Gefahrenzone**. **Parzelle
endgültig löschen** entfernt die Parzelle nach deiner Bestätigung aus der
Datenbank. Alle Pachten der Parzelle -- aktuelle und frühere -- werden mit
entfernt. Wasseranschlüsse bleiben erhalten, sind aber keiner Parzelle mehr
zugeordnet. Das lässt sich nicht rückgängig machen und braucht Löschrecht.

!!! warning "Stattdessen den Status gelöscht verwenden"
    Endgültiges Löschen ist für versehentlich angelegte Parzellen gedacht,
    etwa Testeinträge. Für eine Parzelle, die es nicht mehr gibt, setz den
    Status auf **gelöscht** -- die Parzelle und ihr ganzer Verlauf bleiben
    verfügbar.

## Pachtverhältnis bearbeiten {#edit-tenancy}

![Pachtverhältnis bearbeiten](../assets/screenshots/parcels/assignment-form.png)

Geöffnet mit der Stift-Schaltfläche neben einem aktuellen oder früheren
Pächter. Die Überschrift nennt Mitglied und Parzelle. Braucht Schreibrecht.

| Feld | Was es bewirkt |
|---|---|
| **Als Rechnungsadresse verwenden** | Rechnungen für diese Parzelle gehen an die Adresse dieses Mitglieds. „Gilt nur, solange dieses Pachtverhältnis aktuell ist -- wird automatisch geleert, sobald es beendet ist (Enddatum heute oder früher). Wer gekündigt hat, behält sie bis dahin.“ Das Kästchen ist ausgegraut, sobald **Pächter bis** heute oder früher ist; ein Datum in der Zukunft lässt es, wie es ist. |
| **Pächter seit** | Der erste Tag der Pacht. |
| **Pächter bis** | Der Tag, an dem die Pacht endet. „Leer = aktuell noch Pächter“. Ein Datum in der Zukunft heißt, der Pächter hat gekündigt: Er bleibt bis zu diesem Tag aktueller Pächter und bekommt ein Badge **bis *Datum***. Ab diesem Tag steht er unter **Frühere Pächter**. |

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Änderungen speichern** | Speichert und führt zur Parzellenseite zurück. Hat die Parzelle jetzt keinen aktuellen oder künftigen Pächter mehr, wird ihr Cloud-Dokumentenordner stillgelegt. |
| **Abbrechen** / **Zurück** | Führt ohne Speichern zur Parzellenseite zurück. |

Leerst du **Pächter bis** bei einer früheren Pacht, wird sie wieder
aktuell.

## Siehe auch {#related}

- [Mitglieder](members.md) -- Mitgliederdaten und Parzellen von der Mitgliederseite aus zuordnen
- [Bewerber](applicants.md) -- eine gekündigte Parzelle an Personen von der Warteliste übergeben
- [Eine Parzelle übergeben](../guides/parcel-handover.md)
- [Mitglieder und Parzellen importieren](../guides/csv-import.md)
- [Wasser und Strom](metering.md) -- Zähler gehören zu Parzellen
- [Integrationen](../administration/integrations.md) -- Cloud-Speicher einrichten

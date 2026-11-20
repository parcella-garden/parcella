# Zählerstände erfassen {#collecting-meter-readings}

Einmal im Jahr geht jemand über die Anlage und liest jeden Wasser- und
Stromzähler ab: den Hauptzähler des Vereins, einen Zähler je Parzelle und
die eigenen Anschlüsse des Vereins (Vereinsheim, Waschplatz). Diese
Anleitung zeigt, wie du diese Stände einträgst -- auf dem Handy beim
Rundgang oder hinterher aus einer Liste --, dazu den Tausch eines Zählers und
die Kontrolle der Ergebnisse.

Wasser und Strom funktionieren genau gleich; jedes hat sein eigenes Menü. Die
Schritte unten sagen **Wasser**; für Strom nimmst du stattdessen das Menü
**Strom**.

!!! info "Wer das tun kann"
    Zählerstände eintragen braucht das Recht **Schreiben** für **Wasser**
    (oder **Strom**); einen Stand löschen braucht **Löschen**. Beide Module
    sind standardmäßig an. Ein Verein kann dem Ableseteam eine Gruppe mit
    genau diesen Rechten geben -- siehe [Gruppen](../administration/groups.md).

## Wie Parcella den Verbrauch zählt {#how-parcella-counts-consumption}

- Jeder **[Zählpunkt](../glossary.md#metering-point)** (der Anschluss einer
  Parzelle, der Hauptzähler, ein Vereinsanschluss) hat immer genau einen
  eingebauten **Zähler**.
- Ein Zähler hat **einen Stand je Jahr**. Der Verbrauch des Jahres ist
  dieser Stand minus der Stand des Vorjahres -- oder minus der
  **Anfangsstand** des Zählers, wenn es der erste ist.
- Ein Stand für ein Jahr, das schon einen hat, **ersetzt** ihn.
- Stände werden genau so eingetragen, wie die Anzeige sie zeigt. Manche
  Stromzähler zeigen nur einen Bruchteil des echten Werts; ihr Zählpunkt hat
  dann einen **Faktor** (z. B. 20), den die Auswertung einrechnet.

## 1. Vor dem Rundgang: die Liste der Zählpunkte prüfen {#1-before-the-round-check-the-list-of-metering-points}

1. Öffne **Wasser → Übersicht**. Die Kacheln zeigen, wie viele
   Hauptzähler, Parzellen- und Vereinsanschlüsse es gibt, und **Fehlende
   Zählpunkte**: Parzellen ohne Wasseranschluss in Parcella.
2. Klick unter **Fehlende Zählpunkte** auf **Anzeigen**, um diese Parzellen
   zu sehen; jede verlinkt auf **Neuer Zählpunkt** mit schon gewählter
   Parzelle. Leg die an, die wirklich einen Zähler haben.
3. Ein Anschluss eine Zeit lang ohne Versorgung (Wasser auf einer freien
   Parzelle abgestellt)? Öffne seinen Zählpunkt, setz **Abschalten ab** und
   klick auf **Abschalten**. Er fällt aus der Ableseliste, bis du ihn mit
   **Wieder einschalten** zurückholst.

Steht deine Zählerliste noch in einer Tabelle, importier sie -- siehe
[Mitglieder und Parzellen importieren](csv-import.md#4-metering-points).

## 2. Weg A: Stände beim Rundgang auf dem Handy eintragen {#2-option-a-enter-readings-on-your-phone-while-you-walk}

1. Öffne **Wasser → Ablesung** auf deinem Handy. Die Seite zeigt das
   aktuelle Jahr; wähl bei Bedarf oben im Auswahlfeld ein anderes.
2. Die Seite listet **Hauptzähler**, **Parzellen** (nach Parzellennummer
   sortiert) und **Vereinsanschlüsse**. Jede Zeile zeigt die Zählernummer
   und zur Kontrolle den Stand aus dem **Vorjahr**.
3. Tipp den Stand in das Feld der Zeile und tipp auf die
   Speichern-Schaltfläche daneben. Die Zeile zeigt den Wert dann als
   **erfasst**.
4. Weiter mit dem nächsten Zähler. Zeilen ohne Wert sagen **Noch nicht
   erfasst**.

Hier eingetragene Stände bekommen das heutige Datum. Für ein anderes Datum
oder eine Notiz trägst du den Stand stattdessen auf der Seite des Zählpunkts
ein (Weg C).

## 3. Weg B: auf Papier oder in einer Tabelle sammeln und importieren {#3-option-b-collect-on-paper-or-in-a-spreadsheet-then-import}

1. Öffne **Wasser → Ablesung**, wähl das Jahr und klick auf **CSV
   Export**. Du bekommst eine Datei mit einer Zeile je Zähler: **Type**,
   **Parcel number**, **Label**, **Meter number**, **Year** und leere
   Spalten **Date**, **Reading** und **Note**.
2. Druck sie aus oder füll sie auf einem Tablet aus. Trag **Date** und
   **Reading** für jeden abgelesenen Zähler ein.
3. Klick zurück unter **Wasser → Ablesung** auf **CSV-Import**, wähl die
   Datei und klick auf **Importieren**.
4. Prüf auf **CSV-Spalten zuordnen** die Zuordnung. Hat deine Datei keine
   Jahresspalte, trag das Jahr in **Standardjahr (optional)** ein. Klick auf
   **Importieren**.
5. Lies die Zusammenfassung auf der Ablesungsseite: wie viele Stände erfasst
   wurden und wie viele Zeilen warum übersprungen wurden.

Zeilen ohne Stand werden als „ungültige Zeile“ übersprungen -- das ist bei
Zählern, die du noch nicht abgelesen hast, so gewollt. Einzelheiten zu
Spalten und Fehlermeldungen:
[Mitglieder und Parzellen importieren](csv-import.md#5-meter-readings).

## 4. Weg C: einen einzelnen Stand mit Datum und Notiz eintragen {#4-option-c-enter-a-single-reading-with-date-and-note}

1. Öffne **Wasser → Zählpunkte** und klick auf den Zählpunkt.
2. Füll unten unter **Zählerstände** **Jahr**, **Datum**, **Zählerstand**
   und bei Bedarf eine **Notiz** aus.
3. Klick auf **Ablesung erfassen**.

Die Tabelle **Zählerstände** auf derselben Seite listet jedes Jahr mit
seinem Stand und Verbrauch. Ein falscher Stand lässt sich dort löschen.

## 5. Wenn ein Stand falsch aussieht {#5-when-a-reading-looks-wrong}

Ein Stand, der kleiner als der des Vorjahres (oder größer als ein schon
erfasster späterer) ist, wird **trotzdem gespeichert**, mit einer Warnung
wie *„Zählerstand gespeichert, bitte aber prüfen: Der Zählerstand (…) ist
kleiner als der vorherige Stand (…) …“*. Der Stand behält auf der
Ablesungsseite und am Zählpunkt eine Warnmarkierung.

Häufige Ursachen: ein Tippfehler, eine falsch gelesene Ziffer, ein früherer
Stand, der zu hoch geschätzt war, oder ein Zähler, der tatsächlich getauscht
wurde (Schritt 6). Korrigier den Wert, indem du den Stand für dasselbe Jahr
noch einmal erfasst.

## 6. Ein Zähler wird getauscht {#a-meter-is-replaced}

Wird ein Zähler tatsächlich ausgewechselt -- zum Beispiel weil seine Eichung
abläuft:

1. Lies den alten Zähler ein letztes Mal ab, wenn das noch geht, und trag
   den Stand auf der Seite des Zählpunkts als Stand des Jahres ein (Weg C).
2. Öffne in der Karte **Aktueller Wasserzähler** (**Aktueller Stromzähler**
   bei Strom) **Zähler tauschen**.
3. Trag **Alter Zähler ausgebaut am**, **Neuer Zähler eingebaut am**, die
   **Neue Nummer**, **Geeicht bis** (ein Jahr) und den **Anfangsstand** des
   neuen Zählers ein (meist das, was seine Anzeige beim Einbau zeigt).
4. Klick auf **Tauschen** und bestätige.

Der alte Zähler wird nicht gelöscht: Er wandert mit Ein- und Ausbaudatum und
seinem **Letzten Stand** zu **Frühere Zähler**. Ab jetzt gehen die Stände an
den neuen Zähler, dessen Verbrauch bei seinem **Anfangsstand** beginnt.

!!! warning "Verbrauch im Jahr des Tauschs"
    Stände lassen sich nur für den gerade eingebauten Zähler eintragen, und
    die Jahresrechnung nutzt den Verbrauch des aktuellen Zählers. Was der
    alte Zähler im Jahr des Tauschs gezählt hat, steht unter **Frühere
    Zähler**, kommt aber **nicht** auf die Rechnung dieses Jahres. Prüf
    solche Parzellen von Hand und berechne den Anteil des alten Zählers
    getrennt, wenn dein Verein ihn abrechnet.

!!! tip "Tippfehler, kein neuer Zähler?"
    Hast du dich nur bei Zählernummer oder Anfangsstand vertippt, nimm
    stattdessen **Zähler bearbeiten**. **Zähler tauschen** ist für einen
    echten Wechsel.

## 7. Das Jahr prüfen {#7-check-the-year}

1. Öffne **Wasser → Auswertung** und wähl das Jahr.
2. Die Kacheln vergleichen den **Hauptzähler** mit **Parzellen gesamt** und
   **Verein gesamt**; die Tabellen darunter listen jeden Zählpunkt mit seinem
   **Verbrauch**. Zählpunkte, denen noch ein Stand fehlt, zeigen **keine
   Ablesung**.
3. Haben Parzellen und Vereinsanschlüsse zusammen mehr verbraucht als der
   Hauptzähler, zeigt Parcella eine Warnung. Solange noch Stände eingetragen
   werden, ist das normal; sind alle drin, deutet es auf einen falsch
   abgelesenen Zähler hin.
4. **CSV Export** lädt die Auswertung für deine Unterlagen oder den
   Versorger herunter.

Auch **Wasser → Übersicht** sagt dir, wie vielen Zählpunkten für das Jahr
noch ein Stand fehlt, mit einem Link **Jetzt erfassen →**.

## 8. Den Preis für die Abrechnung festlegen {#8-set-the-price-for-billing}

Rechnest du Wasser und Strom mit den Jahresrechnungen von Parcella ab:

1. Öffne **Wasser → Konfiguration**.
2. Trag unter **Preis neu/aktualisieren** das **Jahr** und den **Preis pro
   m³** ein, bei Bedarf eine **Notiz** (z. B. „Tarifänderung des
   Versorgers“).
3. Klick auf **Speichern**.

Ohne Preis für das Jahr berechnet der Rechnungslauf für dieses Jahr kein
Wasser. Weiter geht es mit
[Die Jahresrechnung erstellen](annual-invoicing.md).

## Siehe auch {#related}

- [Wasser und Strom](../modules/metering.md)
- [Mitglieder und Parzellen importieren](csv-import.md)
- [Die Jahresrechnung erstellen](annual-invoicing.md)
- [Eine Parzelle übergeben](parcel-handover.md)
- Glossar: [Zählpunkt](../glossary.md#metering-point),
  [Zähler](../glossary.md#meter)

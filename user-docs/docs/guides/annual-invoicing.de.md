# Die Jahresrechnung erstellen {#running-the-annual-invoices}

Einmal im Jahr rechnet der Verein jede Parzelle ab: Pacht, Wasser, Strom,
Versicherung, fehlende Arbeitsstunden, vielleicht einen Mitgliedsbeitrag
oder eine einmalige [Umlage](../glossary.md#general-levy). In Parcella ist
das ein [Rechnungslauf](../glossary.md#invoice-run): Du legst die Posten
einmal fest, prüfst eine Vorschau jeder einzelnen Rechnung, schließt ab, um
Rechnungsnummern zu vergeben, und verschickst sie dann -- per E-Mail, auf
Papier oder in den Cloud-Ordner jeder Parzelle. Danach erfasst du Zahlungen
und verschickst [Mahnungen](../glossary.md#dunning).

!!! info "Wer das tun kann"
    Alles hier braucht das Recht **Schreiben** für **Finanzen**. Das Modul
    **Finanzen** ist in einer neuen Installation **aus**; schalte es unter
    **Administration → Einstellungen → Funktionsbereiche** ein (siehe
    [Module ein- und ausschalten](../administration/modules.md)).

!!! warning "Abschließen lässt sich nicht rückgängig machen"
    Bis du abschließt, wird nichts als Rechnung gespeichert und nichts
    verschickt -- ändere die Posten, so oft du willst. Das Abschließen
    vergibt endgültige Rechnungsnummern und sperrt den Lauf. Lade vorher eine
    Sicherung herunter (**Administration → Benutzer → Sicherung
    herunterladen**).

## 1. Die Finanzeinstellungen prüfen (einmal) {#1-check-the-finance-settings-once}

1. Öffne **Administration → Einstellungen** und such
   **Finanzeinstellungen**.
2. Trag die Bankverbindung des Vereins ein: **Bankname**, **IBAN**, **BIC**,
   **Kontoinhaber**. Sie stehen in der Fußzeile jeder Rechnung.
3. Prüf das **Format der Rechnungsnummer**. Die Vorgabe ist das Jahr und
   eine laufende Nummer; du kannst ein eigenes nutzen, zum Beispiel
   `R-{year}-{number}`. `{number}` ist Pflicht.
4. Lass **Nächste Rechnungsnummer (überschreiben)** leer, außer der erste
   Rechnungslauf in Parcella muss eine bisher genutzte Nummerierung
   fortsetzen. Sie wird einmal genutzt und dann geleert.
5. Stell sicher, dass **E-Mail (SMTP)** eingerichtet ist, wenn du Rechnungen
   per E-Mail verschicken willst.
6. Klick auf **Einstellungen speichern**.

## 2. Den Artikelkatalog vorbereiten (einmal, dann wiederverwenden) {#2-prepare-the-item-catalog-once-then-reuse}

Der Artikelkatalog enthält die Posten, die du jedes Jahr berechnest, damit
du sie nicht für jeden Lauf neu festlegen musst.

1. Öffne **Finanzen → Übersicht** und klick auf **Artikelkatalog**.
2. Füll unter **Neue Artikelvorlage** **Reihenfolge** (Position auf der
   Rechnung), **Name**, **Beschreibung**, die **Berechnungsart**, den
   **Einzelpreis** und bei Bedarf eine **Kategorie** aus.
3. Wähl, für wen er gilt (siehe unten), und klick auf die Schaltfläche **+**.

| Berechnungsart | Was berechnet wird |
|---|---|
| **Festbetrag je Parzelle** | Der Einzelpreis einmal je Parzelle -- z. B. die Pacht. |
| **Festbetrag je Person** | Der Einzelpreis einmal je *Mitglied* -- z. B. ein Mitgliedsbeitrag, auch für Mitglieder ohne Parzelle. |
| **Je gepachtetem m²** | Einzelpreis × Fläche der Parzelle. |
| **Anteil an der Gemeinschaftsflächenpacht** | Die Gemeinschaftsfläche (B-Fläche), gleichmäßig auf die berechneten Parzellen verteilt, × Einzelpreis. |
| **Öffentliche Lasten (eigene Fläche + Gemeinschaftsflächenanteil)** | Die eigene Fläche der Parzelle plus ihr Anteil an der Gemeinschaftsfläche, × Einzelpreis. |
| **Allgemeine Umlage (gleichmäßig auf alle Parzellen aufgeteilt)** | Der Einzelpreis ist ein *Gesamtbetrag*, der gleichmäßig auf alle berechneten Parzellen aufgeteilt wird. |
| **Wasserverbrauch (aus Modul)** | Wasserverbrauch der Parzelle × Wasserpreis des Jahres. |
| **Stromverbrauch (aus Modul)** | Stromverbrauch der Parzelle × Strompreis des Jahres. |
| **Versicherungskosten (aus Modul)** | Die Versicherung der Parzelle, eine Zeile je Versicherungsart. |
| **Pflichtstunden-Fehlbetrag (aus Modul)** | Fehlende [Pflichtstunden](../glossary.md#mandatory-hours) × Stundensatz. |

**Für wen ein Posten gilt.** Parzellenbezogene Posten haben **Gilt für jede
Parzelle**; nimm den Haken weg, um einzelne **Parzellen** auszuwählen.
**Festbetrag je Person** hat stattdessen **Gilt für jedes Mitglied** und
eine Auswahl **Mitglieder**. Die vier Posten „aus Modul“ wählen ihre
Parzellen selbst -- statt einer Auswahl steht **Automatisch (...)** da --,
und ihr Einzelpreis **wird automatisch berechnet**.

Mehr: [Rechnungsläufe](../modules/finances/invoice-runs.md).

## 3. Die Zahlen prüfen, die die automatischen Posten nutzen {#3-check-the-numbers-the-automatic-items-use}

Die Posten „aus Modul“ nehmen ihre Zahlen aus anderen Modulen. Prüf sie für
das abzurechnende Jahr, **bevor** du abschließt.

**Wasser und Strom**

1. Öffne **Wasser → Konfiguration** und prüf, dass es für das Jahr einen
   Preis (**Preis pro m³**) gibt (im **Preisverlauf**). Wenn nicht, trag
   unter **Preis neu/aktualisieren** **Jahr** und Preis ein und klick auf
   **Speichern**. Dasselbe unter **Strom → Konfiguration**.
2. Öffne **Wasser → Übersicht**. Sagt sie, dass einigen Zählpunkten für das
   Jahr noch ein Stand fehlt, sammle die erst ein -- siehe
   [Zählerstände erfassen](meter-readings.md). Eine Parzelle ohne Stand für
   das Jahr bekommt gar keine Wasserzeile.
3. Öffne **Wasser → Auswertung** für das Jahr und such nach Parzellen mit
   **keine Ablesung** oder unplausiblem Verbrauch.

**Arbeitsstunden**

1. Öffne **Arbeitseinsätze → Einsätze & Übersicht** und prüf die
   **Stunden-Konfiguration** des Jahres: geforderte Stunden und
   **Stundensatz**.
2. Öffne **Arbeitseinsätze → Jahresauswertung** für das Jahr. Prüf die
   Spalten **Offen** und **Schuldbetrag** -- das wird berechnet. Fehlen
   Anwesenheiten, Patenschaften oder Befreiungen? Korrigier sie jetzt
   (siehe [Einen Arbeitseinsatz organisieren](work-session.md)).

**Versicherungen**

1. Öffne **Versicherungen → Konfiguration** und **Versicherungen →
   Parzellen** und prüf die Preise des Jahres und die Versicherung jeder
   Parzelle.

!!! tip "Wer die Rechnung bekommt"
    Eine Parzellenrechnung geht an die aktuellen Pächter der Parzelle mit
    **Als Rechnungsadresse verwenden**. Parzellen ohne so einen Pächter
    bekommen keine Rechnung. Prüf das vor dem Abschließen auf den
    Parzellenseiten -- besonders nach einer Übergabe.

## 4. Den Rechnungslauf anlegen {#4-create-the-invoice-run}

1. Öffne **Finanzen → Ausgangsrechnungen** (die Seite heißt
   **Jahresrechnungen**).
2. Klick auf **Neuer Rechnungslauf**.
3. Gib das abzurechnende **Jahr**, einen **Betreff** (z. B.
   „Jahresrechnung 2026“), das **Rechnungsdatum** und das **Zahlungsziel**
   ein.
4. Schreib bei Bedarf einen **Fußtext**. Er darf `{invoice_number}`,
   `{parcel_number}`, `{invoice_address}` und `{due_date}` enthalten, die je
   Rechnung ausgefüllt werden.
5. Klick auf **Anlegen**.

Der Lauf ist ein **Entwurf**. Öffne ihn mit **Öffnen**.

## 5. Die Posten hinzufügen {#5-add-the-line-items}

1. Hak auf der Seite des Laufs unter **Aus dem Artikelkatalog hinzufügen**
   die Katalogposten für dieses Jahr an und klick auf **Ausgewählte Posten
   hinzufügen**.
2. Für alles, was nur dieses Jahr berechnet wird, füll unten **Position
   hinzufügen** aus, genauso wie im Katalog.
3. Prüf die Tabelle **Positionsdefinitionen**: Reihenfolge, Preise, für wen
   jeder Posten gilt. Solange der Lauf ein Entwurf ist, kannst du Posten
   noch bearbeiten oder löschen.

## 6. Vorschau {#6-preview}

1. Klick oben auf der Seite des Laufs auf **Vorschau**.
2. Die Seite sagt, wie viele Rechnungen erstellt würden, und listet sie unter
   **Berechnete Rechnungen** mit Empfänger und Summe.
3. Öffne ein paar mit **PDF** und prüf sie: Adresse, Posten, Beträge,
   Fußtext.
4. Um etwas zu korrigieren, geh **Zurück zum Rechnungslauf**, ändere die
   Posten und schau dir die Vorschau erneut an. Noch ist nichts gespeichert
   oder verschickt.

Sagt sie *„Es würden keine Rechnungen erstellt“*, prüf die
Parzellenzuordnung der Posten und das Häkchen **Als Rechnungsadresse
verwenden** der Pächter.

## 7. Abschließen {#7-finalize}

1. Klick auf der Vorschauseite auf **Abschließen & Rechnungsnummern
   vergeben** und bestätige.
2. Parcella legt die Rechnungen mit endgültigen Nummern an. Die Seite des
   Laufs sagt jetzt, dass er abgeschlossen ist, und listet die
   **Rechnungen**.

Namen und Adressen der Empfänger werden so auf jeder Rechnung gespeichert,
wie sie in diesem Moment sind. Spätere Adressänderungen schreiben
abgeschlossene Rechnungen nicht um.

## 8. Die Rechnungen verschicken {#8-send-the-invoices}

1. Such auf der Seite des abgeschlossenen Laufs die Karte **Versand**.
2. Klick auf **E-Mails senden & in Cloud hochladen**.
    - Rechnungen gehen per E-Mail (mit PDF im Anhang) an Rechnungsempfänger
      mit **Darf per E-Mail Informationen erhalten** und einer
      E-Mail-Adresse.
    - Hat die Parzelle einen Dokumentenordner im Cloud-Speicher, wird die
      Rechnung auch dorthin hochgeladen.
    - Ein erneuter Klick verschickt nur, was noch nicht verschickt wurde.
3. Klick auf **Sammel-PDF herunterladen**. Es enthält jede Rechnung, deren
   Empfänger nicht per E-Mail erreichbar ist, als ein PDF zum Drucken und
   Versenden. Sie werden dann als im Sammel-PDF enthalten markiert.

Die Spalte **Versand** zeigt je Rechnung, ob sie **Per E-Mail versendet**,
**In Sammel-PDF enthalten** oder **In Cloud-Speicher hochgeladen** wurde. Um
eine einzelne Rechnung noch einmal zu schicken, öffne sie und klick auf
**E-Mail erneut senden**.

Mehr: [Rechnungen, Zahlungen und Mahnungen](../modules/finances/invoices.md).

## 9. Zahlungen erfassen {#9-record-payments}

**Von Hand**

1. Öffne den Lauf (oder **Alle Rechnungen** auf **Jahresrechnungen**, um
   über alle Läufe nach Rechnungsnummer, Empfänger oder Betrag zu suchen).
2. Klick in der Zeile der Rechnung auf **Zahlung**.
3. Gib **Betrag**, **Bezahlt am**, bei Bedarf eine **Notiz** und das
   **Konto**, auf dem das Geld eingegangen ist, ein und klick auf **Zahlung
   hinzufügen**.

Teilzahlungen sind in Ordnung; der Status wechselt von selbst von **Offen**
über **Teilweise bezahlt** zu **Bezahlt**.

**Aus dem Kontoauszug**

1. Einmal: Öffne **Finanzen → Übersicht → Konten** und leg dein Bankkonto
   unter **Neues Konto** an.
2. Klick neben dem Konto auf **Buchungen**, dann auf **CSV importieren**.
3. Lade den Auszug hoch, den du aus deinem Online-Banking exportiert hast.
   Ordne auf **CSV-Spalten zuordnen** mindestens **Datum** und **Betrag**
   zu; **Beschreibung**, **Absender / Empfänger** und **IBAN** helfen bei
   der Zuordnung.
4. Auf **Zeilen Rechnungen zuordnen** schlägt Parcella für jede eingehende
   Zahlung offene Rechnungen mit demselben Betrag vor. Wähl die richtige,
   um sie als Zahlung dieser Rechnung zu erfassen, oder nimm **Als
   allgemeine Buchung erfassen**.
5. Klick unten auf der Seite auf **CSV importieren**, um Buchungen und
   Zahlungen anzulegen.

Mehr: [Konten und Buchungen](../modules/finances/bank-accounts.md).

## 10. Mahnungen verschicken {#10-send-reminders}

1. Öffne nach dem Zahlungsziel **Finanzen → Mahnungen**. **Überfällige
   Rechnungen** listet jede unbezahlte Rechnung nach ihrem Zahlungsziel, mit
   der Dauer der Überfälligkeit und der Zahl der verschickten Mahnungen.
2. Klick neben einer Rechnung auf **Öffnen**.
3. Gib bei Bedarf eine **Gebühr (optional)** und eine **Nachricht
   (optional)** ein.
4. Klick auf **Mahnung senden**.

Parcella erstellt die nächste Mahnung als PDF (**Mahnung Nr. 1**, **Nr. 2**,
…), addiert die Gebühr zum geschuldeten Betrag und verschickt sie per
E-Mail, wenn das Mitglied E-Mail zugestimmt hat; sonst wird sie als **Zum
Drucken/Postversand** markiert, damit du sie druckst und verschickst. Feste
Mahnstufen gibt es nicht -- du entscheidest, wann die nächste rausgeht.

## Siehe auch {#related}

- [Finanzen](../modules/finances/index.md)
- [Rechnungsläufe](../modules/finances/invoice-runs.md)
- [Rechnungen, Zahlungen und Mahnungen](../modules/finances/invoices.md)
- [Konten und Buchungen](../modules/finances/bank-accounts.md)
- [Kategorien, Haushaltsplan und Übersicht](../modules/finances/bookkeeping.md)
- [Wasser und Strom](../modules/metering.md)
- [Arbeitsstunden](../modules/work-hours.md)
- [Versicherungen](../modules/insurance.md)
- [Zählerstände erfassen](meter-readings.md)

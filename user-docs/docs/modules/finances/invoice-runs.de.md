# Rechnungsläufe {#invoice-runs}

Ein Rechnungslauf ist ein Stapel Rechnungen, meist „die Jahresrechnungen
2026“. Du beschreibst einmal, welche Zeilen auf die Rechnungen kommen und wie
jeder Betrag berechnet wird. Parcella ermittelt dann die Rechnung für jede
Parzelle (und für jedes direkt abgerechnete Mitglied), lässt dich jede
einzelne als PDF prüfen und vergibt Rechnungsnummern erst beim Abschließen.

!!! info "Wer das nutzen kann"
    Teil des Moduls **Finanzen** (standardmäßig aus). Lesen braucht das
    Leserecht für **Finanzen**; Läufe anlegen, Positionen bearbeiten,
    abschließen und versenden braucht Schreibrecht; einen Lauf oder eine
    Position löschen braucht Löschrecht. Vorstandsmitglieder und
    Administratoren können alles. Siehe [Finanzen](index.md).

Ein Lauf ist immer in einem von zwei Zuständen:

| Status | Bedeutung |
|---|---|
| **Entwurf** | Der Lauf wird vorbereitet. Positionen lassen sich frei hinzufügen, ändern und entfernen, die Vorschau wird bei jedem Öffnen neu berechnet, und der ganze Lauf lässt sich noch löschen. Es gibt noch keine Rechnung. |
| **Abgeschlossen** | Rechnungen mit endgültigen Nummern sind angelegt. Die Positionen sind eingefroren, der Lauf lässt sich nicht mehr löschen, und jetzt verschickst du die Rechnungen und erfasst Zahlungen. Zurück zum Entwurf geht es nicht. |

## Jahresrechnungen (Liste der Läufe) {#annual-invoices-list-of-runs}

![Jahresrechnungen](../../assets/screenshots/finances/run-list.png)

Du öffnest sie mit **Finanzen → Ausgangsrechnungen** oder der Karte
**Ausgangsrechnungen** auf dem Dashboard. Sie listet jeden Rechnungslauf, das
neueste Jahr zuerst.

**Obere Leiste**

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Neuer Rechnungslauf** | Öffnet das Formular für einen neuen Lauf (siehe unten). Erscheint nur mit Schreibrecht. |
| **Alle Rechnungen** | Öffnet die Liste aller Rechnungen über alle Läufe, siehe [Rechnungen](invoices.md#invoices-all-runs). |
| **Zurück zu Finanzen** | Zurück zum Finanz-Dashboard. |

**Filter**

| Filter | Was er bewirkt |
|---|---|
| **Jahr** | Zeigt nur Läufe genau dieses Jahres. |
| **Betreff** | Zeigt Läufe, deren Betreff diesen Text enthält (Groß- und Kleinschreibung egal). |
| **Status** | **Alle**, **Entwurf** oder **Abgeschlossen**. |
| **Filtern** / **Zurücksetzen** | Wendet den Filter an / setzt alle Filter zurück. |

**Tabelle der Rechnungsläufe**

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Jahr** | Das Jahr, das der Lauf abrechnet. |
| **Betreff** | Der Betreff des Laufs, wie er auf den Rechnungen steht. |
| **Status** | **Entwurf** (gelb) oder **Abgeschlossen** (grün). |
| **Positionen** | Wie viele Positionsdefinitionen (Rechnungszeilen) der Lauf hat. |
| **Öffnen** | Öffnet den Lauf. |
| Papierkorb-Symbol | Löscht den Lauf mit allen seinen Positionsdefinitionen nach einer Bestätigung. Erscheint nur bei Entwürfen und mit Löschrecht. Ein abgeschlossener Lauf lässt sich nie löschen. |

Gibt es noch keine Läufe, sagt die Tabelle „Noch keine Rechnungsläufe
vorhanden.“; passt nichts zu deinem Filter, „Keine Rechnungsläufe passen zum
Filter.“

### Neuer Rechnungslauf {#new-invoice-run}

Klick in der oberen Leiste auf **Neuer Rechnungslauf**. Ein Dialog öffnet
sich:

| Feld | Was es bewirkt |
|---|---|
| **Jahr** | Pflicht. Vorbelegt mit dem aktuellen Jahr. Dieses Jahr entscheidet, welche Zählerstände, Versicherungsdaten und welche Pflichtstunden-Auswertung die verbrauchsabhängigen Posten nutzen und in welchem Jahr die Rechnungsnummern zählen. |
| **Betreff** | Pflicht. Die Überschrift jeder Rechnung, z. B. „Jahresrechnung 2026“. |
| **Rechnungsdatum** | Pflicht. Vorbelegt mit heute. Steht als Rechnungsdatum auf den Rechnungen. |
| **Zahlungsziel** | Pflicht. Steht auf den Rechnungen. Es entscheidet auch, ab wann eine unbezahlte Rechnung als überfällig gilt und unter [Mahnungen](invoices.md#reminders) erscheint. |
| **Fußtext** | Freiwillig. Steht auf jeder Rechnung des Laufs unter den Positionen, z. B. deine Zahlungshinweise. Du kannst diese Platzhalter nutzen, die je Rechnung ausgefüllt werden: `{invoice_number}`, `{parcel_number}`, `{invoice_address}` (Namen und Adresse der Empfänger), `{due_date}`. |
| **Anlegen** | Legt den Lauf als Entwurf an und öffnet ihn. |
| **Abbrechen** | Schließt den Dialog ohne Speichern. |

!!! tip "Platzhalter im Fußtext"
    Ein typischer Fußtext ist „Bitte überweise den Betrag bis {due_date}
    unter Angabe von {invoice_number}.“ Enthält der Fußtext eine
    geschweifte Klammer, die keiner der vier Platzhalter ist, wird der Text
    genau so gedruckt, wie du ihn getippt hast, ohne etwas auszufüllen.
    Auf einer Mitgliedsrechnung (einer ohne Parzelle) gibt es keine
    Parzellennummer zum Ausfüllen; vermeide `{parcel_number}` also, wenn
    der Lauf auch Mitgliedsrechnungen erzeugt.

Jahr, Betreff, Daten und Fußtext lassen sich nach dem Anlegen des Laufs
nicht mehr ändern.

## Rechnungslauf (Entwurf) {#invoice-run-draft}

![Rechnungslauf im Entwurf](../../assets/screenshots/finances/run-detail.png)

Der Seitentitel zeigt Jahr und Betreff, z. B. „2026 — Jahresrechnung“.
Solange der Lauf ein Entwurf ist, stellst du hier seine Zeilen
(„Positionsdefinitionen“) zusammen.

**Obere Leiste**

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Vorschau** | Öffnet die [Vorschau](#preview-invoices). Erscheint erst, wenn der Lauf mindestens eine Position hat. |
| **Zurück zu den Rechnungsläufen** | Zurück zur Liste. |

### Positionsdefinitionen {#item-definitions}

Jede Zeile ist eine Art von Zeile, die auf den Rechnungen erscheinen kann.
Mit Schreibrecht ist jede Zeile direkt bearbeitbar; ändere die Felder und
klick auf das Häkchen-Symbol am Ende der Zeile, um sie zu speichern. Ohne
Schreibrecht siehst du dieselben Angaben als reinen Text.

| Spalte / Feld | Was es bewirkt |
|---|---|
| **Reihenfolge** | Sortiernummer. Die Zeilen erscheinen in dieser Reihenfolge auf der Rechnung. Eine neue Position ist mit zehn mehr als der bisher höchsten Nummer vorbelegt; so bleibt Platz, später eine dazwischenzuschieben. |
| **Name** | Pflicht. Der Text der Zeile auf der Rechnung, z. B. „Pacht“. |
| **Beschreibung** | Freiwillig, das kleine graue Feld unter dem Namen. Steht auf der Rechnung klein unter dem Namen. |
| **Berechnung** | Wie der Betrag berechnet wird, siehe [Berechnungsgrundlagen](#calculation-bases) unten. Eine Änderung bestimmt, welche der anderen Felder angezeigt werden. |
| **Einzelpreis** | Der Preis je Einheit (je Parzelle, je Person, je m² ...). Bei der allgemeinen Umlage ist es die aufzuteilende Gesamtsumme. Bei den vier automatischen Berechnungsarten ausgeblendet; dort steht „Wird automatisch berechnet“. Mit Dezimalkomma oder -punkt eingeben, z. B. `12,50`. |
| **Gilt für** | Für wen die Zeile ist. Je nach Berechnungsart ist das ein Schalter **Alle Parzellen** / *n* Parzelle(n), ein Schalter **Alle Mitglieder** / *n* Mitglied(er) oder ein fester Hinweis wie „Automatisch (Versicherungsauswertung)“. Siehe [Wer eine Zeile bekommt](#who-gets-a-line). |
| **Kategorie** | Freiwillige [Buchhaltungskategorie](bookkeeping.md#bookkeeping-categories). Sie wird auf jede Rechnungszeile übernommen, sodass Zahlungen dieser Rechnung in der [Buchhaltungsübersicht](bookkeeping.md#accounting-statement) auf die richtigen Kategorien verteilt werden. |
| Häkchen-Symbol | Speichert die Zeile. Braucht Schreibrecht. |
| Papierkorb-Symbol | Löscht die Position nach einer Bestätigung („Diese Positionsdefinition löschen?“). Braucht Löschrecht. |

Schaltest du den Schalter **Gilt für** einer Zeile aus, öffnet sich darunter
eine zusätzliche Zeile mit der Auswahl für Parzellen oder Mitglieder (siehe
[Die Auswahl](#the-picker)).

!!! note
    Positionen lassen sich nur ändern, solange der Lauf ein Entwurf ist. Der
    Versuch, eine Position in einem abgeschlossenen Lauf zu speichern, wird
    mit dem Hinweis abgelehnt, dass der Rechnungslauf schon abgeschlossen ist
    und seine Positionsdefinitionen nicht mehr geändert werden können.

### Aus dem Artikelkatalog hinzufügen {#add-from-item-catalog}

Erscheint mit Schreibrecht, wenn dein [Artikelkatalog](#item-catalog)
Vorlagen enthält, die dieser Lauf noch nicht hat. Jede übrige Vorlage steht
mit Berechnungsart, Einzelpreis und Geltungsbereich da und **ist
standardmäßig angehakt**. Nimm den Haken bei dem weg, was du nicht willst,
und klick auf **Ausgewählte Posten hinzufügen**. Jede angehakte Vorlage wird
eine neue Position dieses Laufs, mit allen ihren Einstellungen, auch einer
bestimmten Auswahl von Parzellen oder Mitgliedern.

**Katalog verwalten** führt zum Artikelkatalog.

Eine Vorlage gilt als „schon hinzugefügt“, wenn der Lauf eine Position mit
genau demselben Namen hat. Benennst du die Position im Lauf um oder löschst
sie, wird die Vorlage also wieder angeboten; benennst du die Vorlage nach dem
Hinzufügen um, ebenfalls.

Gibt es nichts mehr anzubieten, siehst du stattdessen einen kurzen Hinweis:
„Alle Katalogposten wurden diesem Rechnungslauf bereits hinzugefügt.“ oder,
wenn der Katalog leer ist, dass es noch keine Katalogeinträge gibt. Beide
haben eine Schaltfläche **Katalog verwalten**.

### Position hinzufügen {#add-item}

Unter dem Katalog ein Formular, um eine einmalige Position von Hand
hinzuzufügen. Es hat dieselben Felder wie die Tabelle (**Reihenfolge**,
**Name**, **Beschreibung**, **Berechnungsart**, **Einzelpreis**,
**Kategorie**), dann den Schalter für den Geltungsbereich (**Gilt für jede
Parzelle** oder **Gilt für jedes Mitglied**, beide standardmäßig an) und,
wenn du ihn ausschaltest, die Auswahl. Klick auf die Schaltfläche **+**, um
die Position hinzuzufügen.

## Berechnungsgrundlagen {#calculation-bases}

Die **Berechnungsart** entscheidet, wie Parcella die Zeile für jede Parzelle
oder jedes Mitglied berechnet. Jeder Betrag wird je Zeile auf den Cent
gerundet; die Rechnungssumme ist die Summe ihrer Zeilen.

| Berechnungsart | Berechnet an | Menge × Preis | Woher die Zahlen kommen |
|---|---|---|---|
| **Festbetrag je Parzelle** | Jede Parzelle im Geltungsbereich | 1 × Einzelpreis | Du gibst den Betrag ein, z. B. einen Vereinsbeitrag je Parzelle. |
| **Festbetrag je Person** | Jedes Mitglied im Geltungsbereich, auf einer eigenen Rechnung | 1 × Einzelpreis | Du gibst den Betrag ein, z. B. den Mitgliedsbeitrag. Je Mitglied berechnet, ob es eine Parzelle hat oder nicht. |
| **Je gepachtetem m²** | Jede Parzelle im Geltungsbereich | Parzellenfläche × Einzelpreis | Die bei der Parzelle hinterlegte Fläche. Eine Parzelle ohne Fläche bekommt keine Zeile. |
| **Anteil an der Gemeinschaftsflächenpacht** | Jede Parzelle im Geltungsbereich | (Gemeinschaftsfläche ÷ Zahl der berechneten Parzellen) × Einzelpreis | Die Gemeinschaftsfläche („Fläche B“) aus den [Vereinseinstellungen](../../administration/settings.md). Der Anteil wird auf 0,1 m² gerundet. |
| **Öffentliche Lasten (eigene Fläche + Gemeinschaftsflächenanteil)** | Jede Parzelle im Geltungsbereich | (Parzellenfläche + Anteil an der Gemeinschaftsfläche) × Einzelpreis | Wie oben, plus die eigene Fläche der Parzelle, zu einem Satz je m². |
| **Allgemeine Umlage (gleichmäßig auf alle Parzellen aufgeteilt)** | Jede Parzelle im Geltungsbereich | 1 × (Gesamtsumme ÷ Zahl der berechneten Parzellen) | Du gibst als Einzelpreis die **Gesamtsumme** ein, die der Verein einnehmen muss; jede Parzelle zahlt einen gleichen Anteil, auf den Cent gerundet. |
| **Wasserverbrauch (aus Modul)** | Jede Parzelle mit Wasserzähler | Verbrauch des Jahres × Preis je Einheit | Verbrauch und Preis kommen aus [Wasser und Strom](../metering.md). |
| **Stromverbrauch (aus Modul)** | Jede Parzelle mit Stromzähler | Verbrauch des Jahres × Preis je Einheit | Wie beim Wasser. |
| **Versicherungskosten (aus Modul)** | Jede Parzelle mit Versicherung im Jahr | eine Zeile je Versicherungsbestandteil | Aus [Versicherungen](../insurance.md). |
| **Pflichtstunden-Fehlbetrag (aus Modul)** | Jede Parzelle oder jedes Mitglied, das Geld für fehlende Arbeitsstunden schuldet | 1 × geschuldeter Betrag | Aus der [Pflichtstunden-Auswertung](../work-hours.md) des Jahres des Laufs. |

Einzelheiten zu jeder Art:

**Festbetrag je Parzelle / je Person.** Lässt du den **Einzelpreis** leer,
berechnet die Position nichts.

**Je gepachtetem m².** Nutzt die bei jeder Parzelle erfasste Fläche. Prüf vor
dem Abschließen, dass jede Parzelle ihre Fläche eingetragen hat -- eine
Parzelle ohne Fläche bekommt stillschweigend keine Pachtzeile.

**Anteil an der Gemeinschaftsflächenpacht.** Die Gemeinschaftsfläche wird
gleichmäßig auf genau die Parzellen aufgeteilt, die diese Position bekommen
(die in ihrem Geltungsbereich, die auch jemanden zum Abrechnen haben). So
ergeben die Anteile zusammen die ganze Gemeinschaftsfläche, und der Verein
nimmt die volle Pacht ein. Ist die Gemeinschaftsfläche null oder nicht
eingerichtet, berechnet die Position gar nichts. Die Gemeinschaftsfläche
ergibt sich in den Vereinseinstellungen aus Gesamtfläche minus
Parzellenfläche minus kommunale Fläche.

**Öffentliche Lasten** (siehe [Glossar](../../glossary.md)). Wie der
Gemeinschaftsanteil, aber zur eigenen Fläche der Parzelle addiert und zu
einem gemeinsamen Satz berechnet. Ist die Gemeinschaftsfläche nicht
eingerichtet, wird die eigene Fläche der Parzelle trotzdem berechnet -- der
Gemeinschaftsteil zählt einfach als 0 m².

**Allgemeine Umlage** (siehe [Glossar](../../glossary.md)). Für einmalige
Kosten, die der Verein weitergibt, z. B. Anwaltskosten von 1.200,00 auf 40
Parzellen = je 30,00. Es zählen nur Parzellen, die tatsächlich eine Rechnung
bekommen; freie Parzellen „schlucken“ also nie einen Anteil. Weil jeder
Anteil auf den Cent gerundet wird, kann die eingenommene Summe um ein paar
Cent vom eingegebenen Betrag abweichen.

**Wasserverbrauch / Stromverbrauch.** Für jede Parzelle mit einem
Parzellen-Zählpunkt dieser Art nimmt Parcella den Verbrauch des aktuellen
Zählers im Jahr des Laufs (Stand dieses Jahres minus Stand davor) und
multipliziert ihn mit dem Preis je Einheit, der im Zählermodul für dieses
Jahr festgelegt ist. Einen Einzelpreis gibst du hier nicht ein.

- Eine Parzelle ohne Zählerstand für das Jahr bekommt keine Zeile.
- Ist für dieses Medium und Jahr kein Preis gesetzt, wird niemandem etwas
  berechnet.
- Nach einem Zählertausch im Lauf des Jahres wird der Verbrauch **beider**
  Zähler berechnet: der alte bis zu seinem Endstand (im Tauschformular
  eingetragen) und der neue ab seinem Anfangsstand.

!!! warning "Zählpunkte mit Faktor"
    Hat ein Zählpunkt im Zählermodul einen Faktor (Multiplikator), zeigen
    die Zählerseiten den multiplizierten Verbrauch, aber die Rechnung
    berechnet die **reine** Differenz der Zählerstände. Prüf solche
    Parzellen in der Vorschau.

**Versicherungskosten.** Berechnet für jede Parzelle mit Versicherungsdaten
im Jahr des Laufs. Statt einer Pauschale zeigt die Rechnung eine Zeile je
Bestandteil, den die Parzelle tatsächlich hat: „Sachversicherung
(*Paket*)“, „Unfallversicherung (Haushalt)“ und gegebenenfalls
„Unfallversicherung (+*n* weitere Person(en))“. Diese Zeilentexte sind fest,
in der Sprache des Vereins -- der eigene Name der Position wird dafür nicht
genutzt. Die Beträge kommen aus den Versicherungspreisen des Jahres.

**Pflichtstunden-Fehlbetrag.** Berechnet, was die Pflichtstunden-Auswertung
für das Jahr des Laufs als geschuldet ausweist, genau in dieser Höhe.
Befreite und erfüllte Parzellen oder Mitglieder bekommen nichts. Ob das auf
der Parzellenrechnung oder auf einer eigenen Mitgliedsrechnung landet, hängt
davon ab, wie die Arbeitsstunden in dem Jahr gezählt werden: je Parzelle
kommt es auf die Rechnung der Parzelle, je Mitglied auf die eigene Rechnung
jedes Mitglieds.

## Wer eine Zeile bekommt {#who-gets-a-line}

**Parzellenbezogene Arten** (Festbetrag je Parzelle, je m²,
Gemeinschaftsanteil, öffentliche Lasten, allgemeine Umlage) nutzen den
Schalter **Gilt für jede Parzelle**:

- An (Vorgabe): jede Parzelle, die abgerechnet werden kann.
- Aus: nur die Parzellen, die du in der Auswahl anhakst.

**Festbetrag je Person** nutzt stattdessen **Gilt für jedes Mitglied**:

- An (Vorgabe): jedes aktive Mitglied.
- Aus: nur die Mitglieder, die du anhakst.

**Die vier automatischen Arten** (Wasser, Strom, Versicherung,
Pflichtstunden-Fehlbetrag) haben keine Auswahl. Wer berechnet wird, ergibt
sich aus dem anderen Modul: einen Zähler haben, Versicherungsdaten oder einen
Fehlbetrag. Stattdessen steht ein Hinweis wie „Automatisch (Parzellen mit
aktivem Wasserzähler)“ da. (Trotz des Wortlauts ist ein abgeschalteter
Zählpunkt im Lauf weiter enthalten.)

Welche Parzellen überhaupt abgerechnet werden können:

- Eine Parzelle bekommt nur dann eine Rechnung, wenn mindestens ein
  **aktueller** Pächter mit **Als Rechnungsadresse verwenden** markiert ist.
  Pächter, die zu einem künftigen Datum gekündigt haben, zählen weiter, bis
  sie wirklich gegangen sind.
- Eine gekündigte Parzelle wird trotzdem abgerechnet, wenn sie so einen
  Pächter hat (zum Beispiel einen neuen Pächter, der übernommen hat, bevor
  der Status zurückgesetzt wurde). Nur gelöschte Parzellen werden immer
  übersprungen.
- Wohnen mehrere Pächter mit Rechnungsadresse an verschiedenen Adressen,
  geht die Rechnung an die größte Gruppe mit gemeinsamer Adresse.
- Eine Parzelle, deren Zeilen alle leer bleiben, bekommt keine Rechnung.

Mitgliedsrechnungen (aus **Festbetrag je Person** oder einem je Mitglied
gezählten Pflichtstunden-Fehlbetrag) sind eigene Rechnungen an das Mitglied
unter seiner eigenen Adresse. Sie zeigen **Keine Parzelle (Mitglied)** statt
einer Parzellennummer. Ein Pächter, dem auch ein Beitrag je Person berechnet
wird, bekommt also zwei Rechnungen: eine für die Parzelle, eine für sich
selbst. Alle Zeilen je Person für dasselbe Mitglied kommen auf eine Rechnung.

### Die Auswahl {#the-picker}

Ist ein Schalter für den Geltungsbereich aus, erscheint eine Auswahl mit der
Beschriftung **Parzellen** oder **Mitglieder**.

| Element | Was es bewirkt |
|---|---|
| **Liste anzeigen** / **Liste ausblenden** | Öffnet oder schließt die Liste der Kästchen. |
| **Suchen…** | Grenzt die Liste auf passende Parzellennummern oder Namen ein. Passt nichts, erscheint „Keine Treffer“. |
| **Alle auswählen** / **Keine auswählen** | Hakt jeden **gerade sichtbaren** Eintrag an oder ab -- du kannst also erst suchen und dann genau diese auswählen. |

Die Parzellenauswahl listet aktive Parzellen, die Mitgliederauswahl aktive
Mitglieder.

!!! tip
    Der Geltungsbereich bleibt bis zum Abschließen änderbar. Ändere ihn
    beim Vorbereiten des Laufs so oft du willst.

## Rechnungsvorschau {#preview-invoices}

Klick in einem Entwurf auf **Vorschau**. Parcella berechnet jede Rechnung,
die der Lauf erzeugen würde, genau jetzt, ohne etwas zu speichern oder zu
verschicken. Der Seitentitel ist „Vorschau — *Jahr* *Betreff*“.

Der blaue Kasten oben sagt, wie viele Rechnungen erstellt würden, und
erinnert dich: „Es wird noch nichts gespeichert oder versendet — PDFs unten
prüfen und dann abschließen.“

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Parzelle** | Die Parzellennummer oder **Keine Parzelle (Mitglied)** bei einer Mitgliedsrechnung. |
| **Empfänger** | Die Namen, an die die Rechnung geht. |
| **Summe** | Die Rechnungssumme. |
| **PDF** | Öffnet die Rechnung als PDF in einem neuen Tab, genau so, wie sie aussehen wird, mit „Vorschau“ als Rechnungsnummer und einem Banner, dass sie noch nicht abgeschlossen oder versendet ist. |
| **Abschließen & Rechnungsnummern vergeben** | Schließt den Lauf nach einer Bestätigung ab. Erscheint nur mit Schreibrecht, solange der Lauf ein Entwurf ist. |
| **Zurück zum Rechnungslauf** | Zurück zum Lauf, um Positionen zu korrigieren. |

Ist die Liste leer, sagt die Seite, dass keine Rechnungen erstellt würden,
und bittet dich, die Parzellenzuordnung der Positionen und die
Rechnungsadresse der betroffenen Mitglieder zu prüfen.

!!! tip "Die Vorschau ist immer aktuell"
    Für die Vorschau wird nichts gespeichert. Bei jedem Öffnen liest sie die
    aktuellen Parzellen, Pächter, Zählerstände, Versicherungen und
    Arbeitsstunden. Korrigier die Daten in diesen Modulen und lade die Seite
    einfach neu.

### Was das Abschließen bewirkt {#what-finalizing-does}

Klickst du auf **Abschließen & Rechnungsnummern vergeben** und bestätigst
(„Diesen Rechnungslauf abschließen? Rechnungsnummern werden endgültig
vergeben, …“):

1. Parcella berechnet die Rechnungen ein letztes Mal, genau wie die
   Vorschau.
2. Jede Rechnung bekommt eine endgültige Nummer, in der Reihenfolge der
   Vorschauliste. Das Format kommt aus **Format der Rechnungsnummer** in den
   [Vereinseinstellungen](../../administration/settings.md) (Vorgabe
   *Jahr*/*Nummer*, z. B. `2026/1`). Die Nummerierung setzt bei der
   höchsten im selben Jahr schon vergebenen Nummer fort, über alle Läufe,
   und beginnt bei 1 für die erste Rechnung des Jahres.
3. Namen und Adressen der Empfänger werden auf die Rechnungen kopiert.
   Spätere Adressänderungen eines Mitglieds schreiben eine schon gestellte
   Rechnung nicht um.
4. Der Lauf wird **Abgeschlossen**, und seine Positionen sind eingefroren.

Ist in den Vereinseinstellungen **Nächste Rechnungsnummer (überschreiben)**
ausgefüllt, beginnt dieser Lauf stattdessen bei dieser Nummer, und die
Einstellung wird danach geleert. Würde dabei eine im selben Jahr schon
vergebene Nummer erneut verwendet, bricht das Abschließen mit einer
Fehlermeldung ab, und es wird nichts angelegt.

Ein Lauf ohne Position lässt sich nicht abschließen; Parcella bittet dann,
vorher mindestens eine Position hinzuzufügen.

## Rechnungslauf (abgeschlossen) {#invoice-run-finalized}

Nach dem Abschließen zeigt die Seite des Laufs einen grünen Hinweis „Dieser
Rechnungslauf ist abgeschlossen. Rechnungsnummern sind endgültig, …“. Die
Positionsliste ist weg; stattdessen siehst du den Versand und die Rechnungen
des Laufs.

### Versand {#delivery}

Erscheint mit Schreibrecht.

| Schaltfläche | Was sie bewirkt |
|---|---|
| **E-Mails senden & in Cloud hochladen** | Verschickt jede Rechnung des Laufs, die noch nicht per E-Mail rausging, mit dem PDF im Anhang, und lädt jede Rechnung, die noch nicht hochgeladen ist, in den Cloud-Ordner ihrer Parzelle. Ein erneuter Klick erledigt nur, was noch fehlt. |
| **Sammel-PDF herunterladen** | Lädt ein PDF mit jeder Rechnung herunter, deren Empfänger nicht per E-Mail erreichbar ist, fertig zum Drucken für Fensterumschläge. Diese Rechnungen werden als gedruckt markiert. |

**Wer eine E-Mail bekommt:** ein aktueller Pächter der Parzelle mit
Rechnungsadresse (oder, bei einer Mitgliedsrechnung, das Mitglied), der
**Darf per E-Mail Informationen erhalten** eingeschaltet und mindestens eine
E-Mail-Adresse hinterlegt hat. Genommen wird die Hauptadresse. Alle anderen
bleiben für das Sammel-PDF: „Mitglieder ohne E-Mail-Benachrichtigung bleiben
für den Sammel-Druck unten übrig.“

**Hochladen in die Cloud** passiert nur, wenn der Cloud-Speicher
eingerichtet ist und die Parzelle einen Cloud-Ordner hat.
Mitgliedsrechnungen werden nie hochgeladen, weil es keinen Mitgliederordner
gibt. Gescheiterte Uploads werden stillschweigend übersprungen und beim
nächsten Mal erneut versucht.

!!! note "Sammel-PDF"
    Das Sammel-PDF richtet sich danach, wer per E-Mail erreichbar ist, nicht
    danach, was verschickt wurde. Du kannst es vor oder nach dem
    E-Mail-Versand herunterladen, und es enthält immer dieselben
    Rechnungen -- auch die, die du letztes Mal schon gedruckt hast. Kann jede
    Rechnung per E-Mail gehen, bekommst du die Meldung, dass nichts mehr zu
    drucken ist.

### Filter {#filter}

Über der Rechnungstabelle kannst du die Liste eingrenzen. Das funktioniert
wie der Filter unter [Alle Rechnungen](invoices.md#invoices-all-runs):
**Rechnungs-Nr.**, **Empfänger**, **Parzelle** (enthält diesen Text),
**Betrag von**, **Betrag bis** (Rechnungssumme) und **Status** (**Alle**,
**Offen**, **Teilweise bezahlt**, **Bezahlt**). **Filtern** wendet ihn an,
**Zurücksetzen** setzt ihn zurück.

### Rechnungen {#invoices}

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Rechnungs-Nr.** | Die Rechnungsnummer; ein Klick öffnet die [Rechnung](invoices.md#invoice). |
| **Parzelle** | Parzellennummer oder **Keine Parzelle (Mitglied)**. |
| **Empfänger** | Die Namen der Empfänger. |
| **Summe** | Der Rechnungsbetrag. |
| **Zahlungsstatus** | **Offen** (rot, nichts bezahlt), **Teilweise bezahlt** (gelb) oder **Bezahlt** (grün). |
| **Versand** | Symbole für das, was passiert ist: Umschlag = „Per E-Mail versendet“, Drucker = „In Sammel-PDF enthalten“, Wolke = „In Cloud-Speicher hochgeladen“. Fahr mit der Maus über ein Symbol, um seine Bedeutung zu sehen. |
| **Zahlung** | Öffnet den Zahlungsdialog für diese Rechnung (siehe unten). Braucht Schreibrecht. |
| **PDF** | Öffnet das Rechnungs-PDF in einem neuen Tab. |

### Zahlungsdialog {#payment-dialog}

Der schnellste Weg, Zahlungen für viele Rechnungen zu erfassen: Klick in
einer Zeile auf **Zahlung**, trag die Zahlung ein, und du bist zurück auf der
Seite des Laufs, bereit für die nächste. Der Dialog heißt „Zahlung —
Rechnung *Nummer*“.

Er listet die bisher erfassten Zahlungen (Datum, Betrag, Konto, Notiz), jede
mit einem Papierkorb-Symbol zum Löschen (braucht Löschrecht, fragt nach).
Gibt es keine, steht dort, dass noch keine Zahlungen erfasst sind.

| Feld | Was es bewirkt |
|---|---|
| **Betrag** | Pflicht. Der erhaltene Betrag, z. B. `45,00`. Teilzahlungen sind in Ordnung; erfass jede einzeln. |
| **Bezahlt am** | Pflicht. Vorbelegt mit heute. Dieses Datum entscheidet, in welchem Jahr die Einnahme in der Buchhaltungsübersicht zählt. |
| **Notiz** | Freiwillig, z. B. „Überweisung“. |
| **Konto** | Freiwillig. Das [Konto](bank-accounts.md#accounts), auf dem das Geld eingegangen ist. Angeboten werden nur aktive Konten. Die Zahlung erscheint dann in den Buchungen dieses Kontos. |
| **Zahlung hinzufügen** | Speichert die Zahlung. |

Der Zahlungsstatus aktualisiert sich von selbst: Erreichen die Zahlungen den
Rechnungsbetrag plus etwaige Mahngebühren, ist die Rechnung **Bezahlt**.
Siehe [Zahlungen](invoices.md#payments).

## Artikelkatalog {#item-catalog}

![Artikelkatalog](../../assets/screenshots/finances/item-templates.png)

Du öffnest ihn über die Karte **Artikelkatalog** auf dem Dashboard oder mit
**Katalog verwalten** in einem Entwurf. Der Katalog enthält deine
wiederkehrenden Rechnungszeilen („Artikelvorlagen“), damit du sie nicht jedes
Jahr neu tippen musst. Vorlagen sind von jedem Lauf unabhängig; in einen Lauf
holst du sie mit [Aus dem Artikelkatalog hinzufügen](#add-from-item-catalog).

Die Seite hat dieselben Felder wie die Positionen eines Laufs:

- **Neue Artikelvorlage** (mit Schreibrecht): **Reihenfolge**, **Name**,
  **Beschreibung**, **Berechnungsart**, **Einzelpreis**, **Kategorie**, der
  Schalter für den Geltungsbereich (**Gilt für jede Parzelle** / **Gilt für
  jedes Mitglied**) und die [Auswahl](#the-picker). Klick auf die
  Schaltfläche **+**, um zu speichern.
- **Artikelvorlagen**: eine bearbeitbare Zeile je Vorlage mit den Spalten
  **Reihenfolge**, **Name**, **Berechnung**, **Einzelpreis**, **Gilt für**
  und **Kategorie**. Ändere eine Zeile und klick auf ihr Häkchen-Symbol, um
  sie zu speichern; das Papierkorb-Symbol löscht sie (braucht Löschrecht).

Nach dem Speichern siehst du „Gespeichert.“. Ist der Katalog leer: „Noch
keine Artikelvorlagen -- oben eine hinzufügen.“

Die Berechnungsarten und Regeln für den Geltungsbereich sind genau die unter
[Berechnungsgrundlagen](#calculation-bases) und
[Wer eine Zeile bekommt](#who-gets-a-line) beschriebenen.

!!! note "Vorlagen und Läufe sind unabhängig"
    Eine Vorlage in einen Lauf zu übernehmen, kopiert sie. Eine spätere
    Änderung der Vorlage ändert Läufe nicht, die sie schon verwendet haben,
    und das Löschen einer Vorlage lässt die Positionen dieser Läufe
    unberührt („Diese Artikelvorlage löschen? Läufe, die sie bereits
    verwendet haben, behalten ihre Posten, nur ohne Verknüpfung zur
    Vorlage.“). Preise, die sich jedes Jahr ändern, aktualisierst du am
    besten im Katalog, bevor du die Posten in den neuen Lauf übernimmst.

## Siehe auch {#related}

- [Die Jahresrechnung erstellen](../../guides/annual-invoicing.md) -- der
  ganze Ablauf Schritt für Schritt.
- [Rechnungen, Zahlungen und Mahnungen](invoices.md)
- [Wasser und Strom](../metering.md), [Versicherungen](../insurance.md),
  [Arbeitsstunden](../work-hours.md) -- woher die automatischen Beträge
  kommen.
- [Vereinseinstellungen](../../administration/settings.md) -- Format der
  Rechnungsnummer, Bankverbindung, Flächen.

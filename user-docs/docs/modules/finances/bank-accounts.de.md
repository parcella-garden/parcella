# Konten und Buchungen {#bank-accounts-and-bookings}

Hier erfasst du die echten Konten des Vereins -- Girokonten, ein Sparkonto,
die Barkasse -- und siehst alles, was auf jedem davon gebucht wurde.
Buchungen kannst du von Hand anlegen oder deinen Kontoauszug als CSV-Datei
importieren. Dabei bietet Parcella an, jede Buchung einer offenen Rechnung
zuzuordnen; eine eingehende Überweisung wird so gleich als Zahlung des
Mitglieds erfasst.

!!! info "Wer das nutzen kann"
    Teil des Moduls **Finanzen** (standardmäßig aus). Konten und Buchungen
    ansehen und als CSV exportieren braucht das Leserecht für **Finanzen**.
    Konten anlegen oder ändern, Buchungen hinzufügen und importieren braucht
    Schreibrecht; Konten oder Buchungen löschen braucht Löschrecht.
    Vorstandsmitglieder und Administratoren können alles. Siehe
    [Finanzen](index.md).

!!! note "Keine vollständige Buchhaltung"
    Die Buchungsliste eines Kontos ist ein Verzeichnis von Geldbewegungen,
    keine doppelte Buchführung. Es gibt keinen Anfangs- und keinen
    laufenden Saldo. Buchungen, die an keine Rechnung gebunden sind (eine
    Bankgebühr, eine Erstattung), haben keine Kategorie und erscheinen
    deshalb nicht in der
    [Buchhaltungsübersicht](bookkeeping.md#accounting-statement).

## Konten {#accounts}

![Konten](../../assets/screenshots/finances/account-list.png)

Du öffnest sie mit der Karte **Konten** auf dem Finanz-Dashboard. **Zurück
zu Finanzen** in der oberen Leiste führt zurück.

### Neues Konto {#new-account}

Erscheint mit Schreibrecht.

| Feld | Was es bewirkt |
|---|---|
| **Name** | Pflicht, z. B. „Giro Sparkasse“ oder „Barkasse“. Ohne Namen wird nicht gespeichert. |
| **Typ** | **Bank** oder **Bar**. |
| **Kontonummer/IBAN** | Freiwillig, für deine Unterlagen. |
| **Notiz** | Freiwillig. |
| **Aktiv** | Standardmäßig an. Beim Erfassen einer Zahlung werden nur aktive Konten angeboten. Schalte es bei einem aufgelösten Konto aus: Sein Verlauf bleibt, aber es wird nicht mehr angeboten. |
| **Konto hinzufügen** | Speichert das Konto. Du siehst „Erledigt.“. |

### Kontenliste {#accounts-list}

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Name**, **Typ**, **Kontonummer/IBAN**, **Notiz**, **Aktiv** | Die Angaben des Kontos. Mit Schreibrecht sind sie in der Zeile bearbeitbar; das Häkchen-Symbol speichert. |
| **Erfasste Zahlungen** | Die Summe aller Zahlungen für Ausgangsrechnungen, die mit diesem Konto erfasst wurden. Zahlungen von Eingangsrechnungen und andere Buchungen sind nicht enthalten. |
| Buchungen-Symbol | Öffnet die [Buchungen](#bookings-of-an-account) des Kontos. |
| Häkchen-Symbol | Speichert die Zeile. Braucht Schreibrecht. |
| Papierkorb-Symbol | Löscht das Konto nach „Dieses Konto löschen? Es hat keine Buchungen.“ Braucht Löschrecht. Ausgegraut bei einem Konto mit Buchungen (siehe unten). |

Gibt es noch keine Konten: „Noch keine Konten -- oben eines hinzufügen.“

!!! note "Konten mit Buchungen lassen sich nicht löschen"
    Löschen lässt sich nur ein Konto ganz ohne Buchungen -- keine von Hand
    eingetragene oder importierte Buchung, keine darauf erfasste
    Rechnungszahlung. Bei jedem anderen Konto ist der Papierkorb ausgegraut
    („Hat Buchungen: stattdessen den Haken bei „Aktiv“ entfernen.“). **Aktiv**
    auszuschalten blendet das Konto in den Zahlungsformularen aus und behält
    alle seine Buchungen.

## Buchungen eines Kontos {#bookings-of-an-account}

![Buchungen eines Kontos](../../assets/screenshots/finances/account-bookings.png)

Du öffnest sie mit dem Buchungen-Symbol in der Kontenliste. Der Titel ist
„Buchungen — *Kontoname*“. Die Seite zeigt alles, was auf diesem Konto
gebucht ist, das Neueste zuerst:

- Zahlungen von Ausgangsrechnungen, die mit diesem Konto erfasst wurden
  (positive Beträge),
- Zahlungen von [Eingangsrechnungen](incoming-invoices.md), die mit diesem
  Konto erfasst wurden (negative Beträge),
- andere Buchungen, die du von Hand eingetragen oder importiert hast
  (positiv oder negativ, wie eingegeben).

Die ersten 50 Buchungen werden angezeigt; weitere laden automatisch beim
Herunterscrollen. Die Schaltfläche **Zurück zu Finanzen** in der oberen
Leiste führt (trotz ihrer Beschriftung) zur Kontenliste zurück. Auf den
Importseiten unten führt dieselbe Schaltfläche zurück zu den Buchungen des
Kontos, ohne etwas zu importieren.

### Filter und Aktionen {#filter-and-actions}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Suche** | Findet Buchungen, deren Referenz, Beschreibung oder Absender/Empfänger diesen Text enthält. |
| **Von** / **Bis** | Nur Buchungen an oder zwischen diesen Daten. |
| **Betrag von** / **Betrag bis** | Nur Buchungen mit einem Betrag in diesem Bereich. Denk daran, dass ausgehendes Geld negativ ist: Um Ausgaben ab 100 zu finden, setz **Betrag bis** auf `-100`. |
| **Zuordnung** | **Alle**, **Einer Rechnung zugeordnet** (Rechnungszahlungen) oder **Nicht zugeordnet** (andere Buchungen). Praktisch, um Bankzeilen zu finden, die noch geprüft werden müssen. |
| **Filtern** / **Zurücksetzen** | Wendet den Filter an / setzt ihn zurück. |
| **CSV exportieren** | Lädt die Buchungen, die zum aktuellen Filter passen, als CSV-Datei herunter (mit Semikolons: Datum, Betrag, Referenz, Beschreibung, Gegenseite). Braucht nur Leserecht. |
| **CSV importieren** | Öffnet den Importdialog, siehe [Einen Kontoauszug importieren](#importing-a-bank-statement). Braucht Schreibrecht. |
| **Buchung hinzufügen** | Öffnet den Dialog für eine Buchung von Hand, siehe [Eine Buchung von Hand hinzufügen](#adding-a-booking-by-hand). Braucht Schreibrecht. |

### Buchungstabelle {#bookings-table}

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Datum** | Das Buchungsdatum. |
| **Betrag** | Der Betrag; ausgehendes Geld steht rot mit Minuszeichen da. |
| **Referenz** | Bei einer Rechnungszahlung die Rechnungsnummer als Link zur Rechnung (oder Eingangsrechnung). Leer bei anderen Buchungen. |
| **Beschreibung** | Die Zahlungsnotiz oder Buchungsbeschreibung. |
| **Absender / Empfänger** | Wer gezahlt hat oder bezahlt wurde: der Rechnungsempfänger, der Absender der Eingangsrechnung oder die von dir eingetragene Gegenseite. |
| Papierkorb-Symbol | Löscht die Buchung nach „Diese Buchung wirklich löschen?“. Nur bei von Hand eingetragenen oder importierten Buchungen und nur mit Löschrecht. Rechnungszahlungen lassen sich hier nicht löschen -- lösch sie stattdessen bei der Rechnung. |

Hat das Konto keine Buchungen: „Noch keine Buchungen.“

Nach einem Import oder einer Zuordnung sagt dir eine grüne Meldung oben, was
passiert ist, z. B. „12 importiert, 1 übersprungen.“, „3 Buchung(en) einer
bestehenden Rechnung zugeordnet.“, „2 Mitglieds-IBAN(s) aus dem Import
übernommen.“ oder, nach einer einzelnen Buchung, „Als Zahlung gegen die
zugeordnete Rechnung erfasst.“

## Eine Buchung von Hand hinzufügen {#adding-a-booking-by-hand}

Klick auf **Buchung hinzufügen**. Der Dialog fragt nach:

| Feld | Was es bewirkt |
|---|---|
| **Datum** | Pflicht, vorbelegt mit heute. |
| **Betrag** | Pflicht. Positiv für eingehendes Geld, negativ für ausgehendes, z. B. `-12,50`. |
| **Beschreibung** | Freiwillig. |
| **Absender / Empfänger** | Freiwillig. Dient auch dazu, eine passende Rechnung vorzuschlagen. |
| **Buchung hinzufügen** | Geht weiter zum Zuordnungsschritt. |

### Mögliche passende Rechnungen {#possible-matching-invoices}

Bevor etwas gespeichert wird, sucht Parcella offene Rechnungen mit demselben
Betrag: bei einem positiven Betrag Ausgangsrechnungen, bei denen noch genau
so viel offen ist; bei einem negativen Betrag Eingangsrechnungen, bei denen
noch so viel unbezahlt ist. Die Seite zeigt **Datum**, **Betrag** und
**Absender / Empfänger** der Buchung und dann die Möglichkeiten:

| Möglichkeit | Was passiert |
|---|---|
| **Als allgemeine Buchung erfassen** | Speichert eine normale Buchung auf dem Konto, an keine Rechnung gebunden. |
| Eine Zeile je passender Rechnung | Zeigt die Rechnung (Nummer und Empfänger oder Absender und Nummer) und „offen: *Betrag*“. Ein grünes Badge „Name passt“ erscheint, wenn der eingetragene Absender/Empfänger einen Namen mit dem Empfänger oder Absender der Rechnung teilt. Wählst du sie, wird die Buchung als **Zahlung dieser Rechnung** erfasst, mit diesem Konto, diesem Datum und der Beschreibung als Notiz. |
| **Buchung hinzufügen** | Speichert deine Wahl. |

Höchstens fünf Rechnungen werden vorgeschlagen, die mit passendem Namen
zuerst. Hat genau ein Vorschlag einen passenden Namen, ist er vorausgewählt;
sonst **Als allgemeine Buchung erfassen**. Passt keine Rechnung: „Keine
offenen Rechnungen passen zu diesem Betrag.“

!!! tip
    Die Zuordnung vergleicht nur den noch offenen Betrag, auf den Cent. Eine
    Rechnung mit Mahngebühr ist samt Gebühr offen, eine teilweise bezahlte
    nur mit dem Rest.

## Einen Kontoauszug importieren {#importing-a-bank-statement}

Die meisten Banken lassen dich den Kontoauszug als CSV-Datei herunterladen.
Jeder Spaltenaufbau funktioniert. Der Import hat drei Schritte.

**1. Hochladen.** Klick auf **CSV importieren**, wähl die Datei und klick auf
**CSV importieren**. Jede CSV-Datei funktioniert -- erst hochladen, im
nächsten Schritt ordnest du die Spalten den Parcella-Feldern zu. Dateien mit
Semikolon oder Komma werden beide erkannt, ebenso UTF-8 und ältere
Windows-Kodierungen. Eine leere Datei wird mit „Diese CSV-Datei scheint leer
zu sein.“ abgelehnt.

**2. CSV-Spalten zuordnen.** Wähl für jede Spalte, zu welchem Parcella-Feld
sie gehört (oder lass sie ignoriert); Datum und Betrag sind Pflicht. Die
Seite zeigt die Spaltenüberschriften deiner Datei, jede mit einem
Auswahlfeld, und die ersten fünf Zeilen als Beispiel.

| Feld | Bedeutung |
|---|---|
| **— Ignorieren —** | Die Spalte wird nicht genutzt. |
| **Datum** | Pflicht. Das Buchungsdatum. Angenommene Formate: `2026-03-31`, `31.03.2026` und `31.03.26`. |
| **Betrag** | Pflicht. Betrag mit Vorzeichen, mit Dezimalkomma oder -punkt (`-12,50` oder `-12.50`). Tausendertrennzeichen sind in Ordnung, so wie deine Bank sie exportiert: `1.234,56`, `1,234.56` oder `1 234,56`. |
| **Beschreibung** | Freiwillig, z. B. der Verwendungszweck. |
| **Absender / Empfänger** | Freiwillig. Dient der Zuordnung und erscheint in der Liste. |
| **IBAN** | Freiwillig. Siehe den Tipp unten. |

Gängige deutsche und englische Überschriften („Buchungsdatum“, „Betrag“,
„Verwendungszweck“, „Auftraggeber“, „IBAN“ ...) sind schon vorausgewählt;
prüf sie trotzdem. Klick auf **CSV importieren**, um weiterzugehen. Sind
**Datum** oder **Betrag** nicht zugeordnet, kommst du mit der Bitte zurück,
beiden mindestens eine Spalte zuzuordnen.

**3. Zeilen Rechnungen zuordnen.** Wähl für jede Zeile eine passende offene
Rechnung, um sie als echte Zahlung zu erfassen, oder lass sie eine
allgemeine Buchung bleiben. Jede Zeile zeigt **Datum**, **Betrag**,
**Absender / Empfänger** und ein Auswahlfeld **Zuordnung** mit **Nicht
importieren**, **Als allgemeine Buchung erfassen** und den vorgeschlagenen
Rechnungen (offener Betrag in Klammern, ein ✓, wenn der Name passt). Die
Vorauswahl funktioniert wie bei einer einzelnen Buchung. Zeilen, deren Datum
oder Betrag sich nicht lesen ließ, zeigen „Ungültige Zeile — wird
übersprungen“. Eine Zeile, die schon auf diesem Konto ist, bekommt ein Badge
**Bereits importiert** und ist auf **Nicht importieren** voreingestellt.
Klick auf **CSV importieren**, um alles zu speichern.

Was gespeichert wird:

- jede Zeile mit gewählter Rechnung wird eine Zahlung dieser Rechnung auf
  diesem Konto -- außer die Rechnung wurde inzwischen vollständig bezahlt:
  Dann wird nichts erfasst, und die Ergebnismeldung sagt das;
- jede andere gültige Zeile wird eine normale Buchung;
- Zeilen auf **Nicht importieren** und ungültige Zeilen werden übersprungen
  und in der Ergebnismeldung gezählt.

!!! tip "IBANs der Mitglieder ergänzen"
    Ordnest du sowohl **Absender / Empfänger** als auch **IBAN** zu, sucht
    Parcella ein Mitglied, dessen Name genau der Name des Absenders ist
    (Vorname Nachname oder Nachname Vorname, Groß- und Kleinschreibung
    egal). Hat dieses Mitglied noch keine IBAN hinterlegt, wird die IBAN aus
    dem Auszug eingetragen. Vorhandene IBANs werden nie überschrieben.

!!! tip "Denselben Auszug zweimal importieren"
    Eine Zeile gilt als schon importiert, wenn dieses Konto bereits eine
    Buchung mit demselben Datum, Betrag und derselben Beschreibung hat (eine
    gegen eine Rechnung erfasste Zahlung zählt auch). Überlappende Exporte
    sind also sicher: Nur die neuen Zeilen kommen dazu. Parcella zählt,
    statt nur zu vergleichen -- hat die Datei denselben Kaffeekauf zweimal an
    einem Tag und das Konto ihn einmal, ist einer davon neu.

    Eine schon vorhandene Zeile wird nur importiert, wenn du ihr **Nicht
    importieren** auf etwas anderes änderst. Zweimal auf **CSV importieren**
    klicken oder die Seite mit dem Zurück-Knopf erneut absenden, fügt nichts
    hinzu.

## Siehe auch {#related}

- [Rechnungen, Zahlungen und Mahnungen](invoices.md)
- [Eingangsrechnungen](incoming-invoices.md)
- [Alle Buchungen](bookkeeping.md#all-bookings) -- jede Rechnungszahlung
  über alle Konten.
- [Mitglieder](../members.md) -- wo die IBAN hinterlegt ist.

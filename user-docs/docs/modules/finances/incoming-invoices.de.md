# Eingangsrechnungen {#incoming-invoices}

Eingangsrechnungen sind die Rechnungen, die der Verein bekommt: vom
Wasserversorger, vom Versicherer, vom Baumarkt. Erfasst du sie hier, in
Positionen mit je einer Buchhaltungskategorie aufgeteilt, und hältst fest,
wann sie bezahlt wurden, ergibt das die Ausgabenseite der
[Buchhaltungsübersicht](bookkeeping.md#accounting-statement).

!!! info "Wer das nutzen kann"
    Teil des Moduls **Finanzen** (standardmäßig aus). Ansehen braucht das
    Leserecht für **Finanzen**; Rechnungen erfassen, Kontakte verknüpfen und
    Zahlungen hinzufügen braucht Schreibrecht; eine Rechnung oder Zahlung
    löschen braucht Löschrecht. Die eingescannte Rechnung (Anhang)
    hochladen und herunterladen können nur Vorstandsmitglieder und
    Administratoren, und nur wenn das Modul **Cloud-Speicher** an und ein
    Ordner für Eingangsrechnungen eingerichtet ist. Siehe
    [Finanzen](index.md).

## Liste der Eingangsrechnungen {#incoming-invoices-list}

![Eingangsrechnungen](../../assets/screenshots/finances/incoming-invoice-list.png)

Du öffnest sie mit **Finanzen → Eingangsrechnungen** oder der Karte
**Eingangsrechnungen** auf dem Dashboard. Die Liste ist nach
Rechnungsdatum sortiert, die neuesten zuerst.

**Obere Leiste**

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Eingangsrechnung erfassen** | Öffnet das Formular für eine neue Eingangsrechnung (siehe unten). Braucht Schreibrecht. |
| **Zurück zu Finanzen** | Zurück zum Finanz-Dashboard. |

**Filter**

| Filter | Was er bewirkt |
|---|---|
| **Rechnungsnr.** | Rechnungen, deren Nummer diesen Text enthält. |
| **Absender** | Rechnungen, deren Absender diesen Text enthält. |
| **Betrag von** / **Betrag bis** | Rechnungssumme mindestens / höchstens so viel. |
| **Zahlungsstatus** | **Alle**, **Offen**, **Teilweise bezahlt** oder **Bezahlt**. |
| **Filtern** / **Zurücksetzen** | Wendet den Filter an / setzt ihn zurück. |

**Tabelle**

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Datum** | Das Rechnungsdatum. |
| **Absender** | Wer die Rechnung geschickt hat; ein Klick öffnet die [Eingangsrechnung](#incoming-invoice). |
| **Rechnungsnr.** | Die Rechnungsnummer des Lieferanten, falls eingetragen. |
| **Kategorien** | Eine Zeile je Position: ihre Kategorie (oder „Ohne Kategorie“) und ihre Beschreibung. |
| **Betrag** | Die Rechnungssumme (Summe aller Positionen). |
| **Zahlungsstatus** | **Offen**, **Teilweise bezahlt** oder **Bezahlt**, nach den erfassten Zahlungen. |
| Download-Symbol | Lädt die angehängte Rechnung herunter. Erscheint nur, wenn es einen Anhang gibt und du den Cloud-Speicher nutzen darfst. |
| Papierkorb-Symbol | Löscht die Eingangsrechnung mit ihren Positionen und Zahlungen nach einer Bestätigung. Braucht Löschrecht. |

Ist noch nichts erfasst: „Noch keine Eingangsrechnungen erfasst.“

!!! note "Beim Löschen bleibt der Anhang"
    „Diese Eingangsrechnung wirklich löschen? Der Anhang wird dabei nicht
    aus dem Cloud-Ordner gelöscht.“ Die eingescannte Rechnung bleibt im
    gemeinsamen Ordner; entfern sie dort bei Bedarf von Hand.

## Eingangsrechnung erfassen {#record-incoming-invoice}

Klick auf **Eingangsrechnung erfassen**. Ein Dialog öffnet sich:

| Feld | Was es bewirkt |
|---|---|
| **Kontakt** | Freiwillig. Erscheint nur, wenn das Modul [Externe Kontakte](../external-contacts.md) an ist und du Kontakte lesen darfst. Wählst du einen Lieferanten aus deinen Kontakten, wird **Absender** für dich ausgefüllt („Die Auswahl eines Kontakts füllt den Absender aus.“), außer du hast schon einen eingetippt. **— keiner —** verknüpft keinen Kontakt. |
| **Absender** | Pflicht. Der Name des Lieferanten, wie er in Listen, beim Bankabgleich und in der Buchhaltungsübersicht erscheinen soll. |
| **Rechnungsnr.** | Freiwillig. Die Rechnungsnummer des Lieferanten. |
| **Rechnungsdatum** | Pflicht, vorbelegt mit heute. |
| **Notiz** | Freiwillig. |
| **Positionen** | Eine Zeile je Kostenposition (siehe unten). |
| **Position hinzufügen** | Fügt eine weitere Positionszeile hinzu. Jede Zeile außer der ersten hat eine Entfernen-Schaltfläche. |
| **Anhang** | Freiwillig. Die eingescannte oder fotografierte Rechnung. „Wird in den oben angegebenen gemeinsamen Cloud-Ordner hochgeladen.“ Erscheint nur für Vorstandsmitglieder und Administratoren, wenn Cloud-Speicher und ein Ordner für Eingangsrechnungen eingerichtet sind. |
| **Speichern** | Speichert die Rechnung. Du siehst „Gespeichert.“. |
| **Abbrechen** | Schließt den Dialog ohne Speichern. |

Jede Position hat drei Felder:

| Feld | Was es bewirkt |
|---|---|
| Kategorie | Freiwillige [Buchhaltungskategorie](bookkeeping.md#bookkeeping-categories). „—“ heißt keine; die Position erscheint dann als „Ohne Kategorie“. |
| **Beschreibung (was wurde gekauft)** | Freiwilliger Freitext, z. B. „Wartung Rasenmäher“. Mehrere Positionen können sich eine Kategorie teilen, aber verschiedene Käufe beschreiben. |
| Betrag | Der Betrag der Position, z. B. `249,90`. Eine Position ohne gültigen Betrag wird weggelassen. |

!!! warning "Vor dem Speichern prüfen"
    Absender, Datum, Positionen und Beträge lassen sich nach dem Speichern
    nicht mehr bearbeiten; später ändern lassen sich nur der verknüpfte
    Kontakt und die Zahlungen. Stimmt etwas nicht, lösch die
    Eingangsrechnung und erfass sie neu.

Lässt sich der Anhang nicht hochladen, wird die Rechnung trotzdem
gespeichert, und der Fehler des Cloud-Speichers erscheint oben in der Liste.
Der Dateiname des Anhangs im Cloud-Ordner beginnt mit einer internen Nummer,
damit sich zwei Rechnungen mit gleichem Dateinamen nie überschreiben. Den
Ordner selbst legst du unter **Integrationen** → **Ordner für
Eingangsrechnungen** fest, siehe
[Integrationen](../../administration/integrations.md).

## Eingangsrechnung {#incoming-invoice}

![Eingangsrechnung](../../assets/screenshots/finances/incoming-invoice-detail.png)

Öffnet sich, wenn du in der Liste auf einen Absender klickst. Der Titel ist
„Eingangsrechnung — *Absender*“.

**Obere Leiste**

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Anhang herunterladen** | Lädt die angehängte Rechnung aus dem Cloud-Ordner herunter. Erscheint nur, wenn es einen Anhang gibt und du den Cloud-Speicher nutzen darfst. |
| **Zurück zu den Eingangsrechnungen** | Zurück zur Liste. |

Karte **Rechnung**

| Feld | Was es zeigt |
|---|---|
| **Absender** | Der Absender wie eingetragen. |
| **Kontakt** | Der verknüpfte externe Kontakt, als Link zum Kontakt, wenn du Kontakte sehen darfst (als gelöscht markiert, wenn der Kontakt inzwischen gelöscht wurde). Mit Schreibrecht kannst du über ein Auswahlfeld und **Speichern** einen anderen oder keinen Kontakt verknüpfen. Den Text **Absender** ändert das **nicht**. |
| **Rechnungsnr.** | Die Rechnungsnummer des Lieferanten. |
| **Datum** | Das Rechnungsdatum. |
| **Notiz** | Die Notiz. |
| **Betrag** | Die Rechnungssumme. |
| **Zahlungsstatus** | **Offen**, **Teilweise bezahlt** oder **Bezahlt**. |

Karte **Positionen**: jede Position mit ihrer Kategorie („Kürzel · Titel“
oder „Ohne Kategorie“), Beschreibung und Betrag, und die **Summe**.

Karte **Zahlungen**: jede für diese Rechnung erfasste Zahlung mit Datum,
Betrag, Konto und Notiz. Ein Papierkorb-Symbol löscht eine Zahlung (braucht
Löschrecht, fragt „Diese Zahlung löschen?“). Gibt es keine: „Noch keine
Zahlungen erfasst.“

Eine Zahlung erfassen (Schreibrecht):

| Feld | Was es bewirkt |
|---|---|
| **Betrag** | Pflicht. Was der Verein gezahlt hat, als positive Zahl. Teilzahlungen sind in Ordnung. |
| **Bezahlt am** | Pflicht, vorbelegt mit heute. Dieses Datum entscheidet, in welchem Jahr die Ausgabe in der Buchhaltungsübersicht zählt. |
| **Notiz** | Freiwillig. |
| **Konto** | Freiwillig. Das [Konto](bank-accounts.md#accounts), von dem das Geld abgegangen ist; angeboten werden nur aktive Konten. Die Zahlung erscheint dann als negativer Betrag in den Buchungen dieses Kontos. |
| **Zahlung hinzufügen** | Speichert die Zahlung. |

Der Status wird **Bezahlt**, sobald die Zahlungen die Rechnungssumme
erreichen. Eingangsrechnungen haben keine Mahnungen und Gebühren.

!!! tip "Aus dem Kontoauszug bezahlen"
    Statt die Zahlung hier einzutragen, kannst du deinen Kontoauszug auf der
    Buchungsseite des Kontos importieren: Eine negative Buchung mit demselben
    Betrag wie eine offene Eingangsrechnung wird als Zuordnung angeboten und
    als deren Zahlung erfasst. Siehe
    [Konten und Buchungen](bank-accounts.md#possible-matching-invoices).

!!! note "Nur bezahlte Rechnungen zählen"
    Buchhaltungsübersicht und Haushaltsplan zählen eine Ausgabe an dem Tag,
    an dem sie bezahlt wurde. Eine Eingangsrechnung ohne Zahlung erscheint
    dort gar nicht.

## Siehe auch {#related}

- [Externe Kontakte](../external-contacts.md) -- die Kontaktseite eines
  Lieferanten listet die mit ihm verknüpften Eingangsrechnungen.
- [Einkaufswünsche](../purchase-requests.md) -- dort wird ein Kauf
  freigegeben; die Rechnung dazu erfasst du hier von Hand.
- [Kategorien, Haushaltsplan und Übersicht](bookkeeping.md)
- [Integrationen](../../administration/integrations.md) -- der gemeinsame
  Cloud-Ordner für Anhänge.

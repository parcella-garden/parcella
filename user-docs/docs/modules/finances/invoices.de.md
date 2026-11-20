# Rechnungen, Zahlungen und Mahnungen {#invoices-payments-and-reminders}

Ist ein Rechnungslauf abgeschlossen, leben seine Rechnungen weiter. Dieses
Kapitel behandelt, wie du eine Rechnung findest, sie erneut verschickst,
festhältst, was bezahlt wurde, und Mitglieder mahnst, die bis zum
Zahlungsziel nicht bezahlt haben.

!!! info "Wer das nutzen kann"
    Teil des Moduls **Finanzen** (standardmäßig aus). Rechnungen, PDFs und
    die Mahnliste ansehen braucht das Leserecht für **Finanzen**. Zahlungen
    erfassen, E-Mails erneut senden und Mahnungen verschicken braucht
    Schreibrecht; eine Zahlung löschen braucht Löschrecht.
    Vorstandsmitglieder und Administratoren können alles. Siehe
    [Finanzen](index.md).

Rechnungen entstehen nur durch das
[Abschließen eines Rechnungslaufs](invoice-runs.md#what-finalizing-does).
Eine einzelne Rechnung kannst du nicht von Hand anlegen, bearbeiten oder
löschen, und es gibt keine Storno- oder Gutschriftfunktion.

## Rechnungen (alle Läufe) {#invoices-all-runs}

![Rechnungen](../../assets/screenshots/finances/invoice-list.png)

Du öffnest sie mit **Alle Rechnungen** auf der Seite
[Jahresrechnungen](invoice-runs.md#annual-invoices-list-of-runs). Sie listet
jede Rechnung aus jedem abgeschlossenen Lauf, die höchste Rechnungsnummer
zuerst. **Zurück zu den Rechnungsläufen** in der oberen Leiste führt
zurück.

**Filter**

| Filter | Was er bewirkt |
|---|---|
| **Parzelle** | Rechnungen, deren Parzellennummer diesen Text enthält. |
| **Rechnungs-Nr.** | Rechnungen, deren Nummer diesen Text enthält, z. B. `2026/` für alle aus 2026. |
| **Empfänger** | Rechnungen, deren Empfängernamen diesen Text enthalten. |
| **Betrag von** / **Betrag bis** | Rechnungsbetrag (Summe, ohne Mahngebühren) mindestens / höchstens so viel. |
| **Status** | **Alle**, **Offen**, **Teilweise bezahlt** oder **Bezahlt**. |
| **Filtern** / **Zurücksetzen** | Wendet den Filter an / setzt alle Filter zurück. |

**Tabelle**

| Spalte | Was sie zeigt |
|---|---|
| **Rechnungs-Nr.** | Die Rechnungsnummer; ein Klick öffnet die [Rechnung](#invoice). |
| **Parzelle** | Die Parzellennummer oder **Keine Parzelle (Mitglied)** bei einer Rechnung direkt an ein Mitglied. |
| **Empfänger** | Die Namen, an die die Rechnung beim Ausstellen ging. |
| **Summe** | Der Rechnungsbetrag. |
| **Bezahlt** | Die Summe aller bisher erfassten Zahlungen. |
| **Status** | **Offen** (rot), **Teilweise bezahlt** (gelb) oder **Bezahlt** (grün), siehe [Zahlungsstatus](#payment-status). |
| **Bezahlt am** | Die Daten aller Zahlungen, durch Kommas getrennt. |

Passt nichts: „Keine Rechnungen entsprechen diesen Filtern.“

Dieselbe Liste, auf einen Lauf beschränkt und mit Schaltflächen für Zahlungen
und PDFs, steht auf der
[Seite des abgeschlossenen Laufs](invoice-runs.md#invoice-run-finalized).

## Rechnung {#invoice}

![Rechnung](../../assets/screenshots/finances/invoice-detail.png)

Öffnet sich, wenn du auf eine Rechnungsnummer klickst. Der Titel ist
„Rechnung *Nummer*“.

**Obere Leiste**

| Schaltfläche | Was sie bewirkt |
|---|---|
| **PDF** | Öffnet das Rechnungs-PDF in einem neuen Tab. |
| **E-Mail erneut senden** | Schickt das Rechnungs-PDF noch einmal per E-Mail, auch wenn es schon verschickt wurde. Braucht Schreibrecht. Ist niemand erreichbar, siehst du einen Hinweis, dass für diese Rechnung kein erreichbares Mitglied mit Rechnungsadresse (E-Mail-Benachrichtigung plus hinterlegte E-Mail-Adresse) gefunden wurde. |
| **Zurück zu den Rechnungen** | Zurück zur Liste aller Rechnungen. |

Karte **Rechnung**

| Feld | Was es zeigt |
|---|---|
| **Parzelle** | Parzellennummer oder **Keine Parzelle (Mitglied)**. |
| **Empfänger** | Namen und Adresse, wie sie auf der Rechnung stehen. Sie wurden beim Abschließen des Laufs festgeschrieben; spätere Adressänderungen ändern sie nicht. |
| **Summe** | Der Rechnungsbetrag. |
| **Zahlungsziel** | Das Zahlungsziel des Rechnungslaufs. |
| **Status** | Der Zahlungsstatus, gefolgt von „bisher bezahlt / insgesamt geschuldet“. Das insgesamt Geschuldete enthält etwaige Mahngebühren. |

Karte **Mahnungen**: die zu dieser Rechnung verschickten Mahnungen und das
Formular für die nächste, siehe [Eine Mahnung senden](#sending-a-reminder).

!!! note "Wo sind die Zahlungen?"
    Zahlungen erfasst du im Zahlungsdialog in der Rechnungsliste des Laufs,
    siehe [Zahlungen](#payments). Die Rechnungsseite zeigt das Ergebnis in
    der Zeile **Status**.

### Das Rechnungs-PDF {#the-invoice-pdf}

Das PDF ist als deutscher Geschäftsbrief für Fensterumschläge gesetzt: oben
Logo und Name des Vereins, die Empfängeradresse dort, wo ein
Fensterumschlag sie zeigt, dann Rechnungsnummer, Datum, Zahlungsziel und
Parzelle, eine Tabelle der Zeilen (**Beschreibung**, **Menge**,
**Einzelpreis**, **Gesamt**), die **Summe**, der Fußtext des Laufs und die
Angaben deines Vereins (Adresse, Bank) in der Fußzeile. Diese Vereinsangaben
kommen aus den [Vereinseinstellungen](../../administration/settings.md).

Das Layout folgt **DIN 5008 Form B**: Die Adresse sitzt im Fenster eines
DL- oder C6/5-Fensterumschlags, und kurze Striche am linken Rand zeigen, wo
gefalzt (bei einem und zwei Dritteln der Seite) und wo gelocht wird.
Zahlungserinnerungen und Briefe aus Mitteilungen haben dasselbe Layout.

Der Dateiname beginnt mit dem Rechnungsdatum und der Parzellennummer (oder
dem Nachnamen des Mitglieds), gefolgt von der Rechnungsnummer.

## Zahlungen {#payments}

Eine Zahlung ist Geld, das für eine Rechnung eingegangen ist. Du kannst sie
auf zwei Wegen erfassen:

- **Von Hand:** Klick auf der
  [Seite des abgeschlossenen Laufs](invoice-runs.md#payment-dialog) neben
  der Rechnung auf **Zahlung**, gib **Betrag**, **Bezahlt am**, eine
  freiwillige **Notiz** und das **Konto** ein und klick auf **Zahlung
  hinzufügen**.
- **Aus dem Kontoauszug:** Füg auf der
  [Buchungsseite eines Kontos](bank-accounts.md#bookings-of-an-account) eine
  Buchung hinzu oder importier eine CSV-Datei und wähl die passende offene
  Rechnung. Parcella erfasst die Zahlung dann für dich, mit dem Konto schon
  gesetzt.

Eine Rechnung kann beliebig viele Zahlungen haben; Teil- und Ratenzahlungen
sind also kein Problem. Um eine falsche Zahlung zu korrigieren, lösch sie
(Papierkorb-Symbol im Zahlungsdialog, braucht Löschrecht) und trag sie neu
ein.

!!! tip "„Bezahlt am“ entscheidet das Jahr"
    Die [Buchhaltungsübersicht](bookkeeping.md#accounting-statement) zählt
    Einnahmen am Datum **Bezahlt am**, nicht am Rechnungsdatum. Eine
    Rechnung von 2026, bezahlt im Januar 2027, ist eine Einnahme von 2027.

### Zahlungsstatus {#payment-status}

Der Status wird jedes Mal aus den Zahlungen ermittelt; er ist also nie
veraltet:

| Status | Wann |
|---|---|
| **Offen** | Noch nichts bezahlt. |
| **Teilweise bezahlt** | Etwas bezahlt, aber weniger als Rechnungsbetrag plus alle Mahngebühren. |
| **Bezahlt** | Die Zahlungen erreichen Rechnungsbetrag plus alle Mahngebühren (oder mehr). |

Überzahlungen werden angenommen und erscheinen einfach als **Bezahlt**;
Parcella führt kein Guthaben.

## Mahnungen {#reminders}

![Mahnungen](../../assets/screenshots/finances/reminders.png)

Du öffnest sie mit **Finanzen → Mahnungen** oder der Karte **Mahnungen** auf
dem Dashboard. Die Liste **Überfällige Rechnungen** zeigt jede Rechnung, die
nicht vollständig bezahlt ist und deren Zahlungsziel vorbei ist, die am
längsten überfällige zuerst. Sie ist eine Arbeitsliste für die Kasse: Öffne
jede Rechnung und entscheide, ob du mahnst.

| Spalte / Schaltfläche | Was sie zeigt |
|---|---|
| **Parzelle** | Die Parzellennummer. Leer bei einer Mitgliedsrechnung. |
| **Empfänger** | Die Namen der Empfänger. |
| **Rechnungsnr.** | Die Rechnungsnummer. |
| **Fällig am** | Das Zahlungsziel des Laufs. |
| **Überfällig seit** | Wie viele Tage seit dem Zahlungsziel, z. B. „14 Tagen“. |
| **Offener Betrag** | Was noch geschuldet wird: Rechnungsbetrag plus Mahngebühren minus Zahlungen. |
| **Mahnungen versendet** | Wie viele Mahnungen verschickt wurden, mit dem Datum der letzten, oder „Noch keine versendet“. |
| **Öffnen** | Öffnet die Rechnung, wo du die Mahnung verschickst. |

Ist nichts überfällig: „Keine überfälligen Rechnungen — nichts zu mahnen.“

Eine Rechnung verschwindet aus dieser Liste, sobald sie vollständig bezahlt
ist.

### Eine Mahnung senden {#sending-a-reminder}

Auf der [Rechnung](#invoice) listet die Karte **Mahnungen** jede schon
verschickte Mahnung:

| Spalte | Was sie zeigt |
|---|---|
| „Mahnung Nr. *n*“ | Die Stufe der Mahnung: Die erste ist Nr. 1, die nächste Nr. 2 und so weiter. |
| Datum | Wann sie angelegt wurde. |
| Versand | „Per E-Mail versendet“ oder „Zum Drucken/Postversand“, wenn sie nicht per E-Mail gehen konnte. |
| Gebühr | Die mit dieser Mahnung berechnete Gebühr, falls vorhanden. |
| PDF-Symbol | Öffnet das Mahnungs-PDF in einem neuen Tab -- druck es von hier für den Postversand. |

Wurde noch keine verschickt: „Noch keine Mahnungen versendet.“

Unter der Liste, solange die Rechnung nicht vollständig bezahlt ist und du
Schreibrecht hast:

| Feld | Was es bewirkt |
|---|---|
| **Gebühr (optional)** | Eine Mahngebühr, z. B. `5,00`. Sie kommt zu dem dazu, was die Rechnung schuldet. Leer lassen für keine Gebühr. |
| **Nachricht (optional)** | Ein kurzer Text, der unten auf der Mahnung steht. |
| **Mahnung senden** | Legt die nächste Mahnung an und stellt sie zu. |

Was **Mahnung senden** tut: Es erstellt die nächste Mahnung als PDF, addiert
die Gebühr (falls angegeben) zum offenen Betrag und verschickt sie per
E-Mail, wenn das Mitglied zugestimmt und eine Adresse hinterlegt hat, sonst
bereitet es sie zum Drucken bzw. für den Postversand vor.

- Die Mahnung ist immer eine Stufe höher als die letzte. Feste Mahnstufen
  gibt es nicht; dein Verein entscheidet, wie viele Mahnungen er wann
  schickt.
- Die E-Mail geht an dieselbe Person, an die auch die Rechnung ginge (siehe
  [wer eine E-Mail bekommt](invoice-runs.md#delivery)), mit einem Betreff,
  der die Mahnungsnummer, die Rechnungsnummer und den Vereinsnamen nennt,
  und dem PDF im Anhang.
- Lässt sich die E-Mail nicht verschicken, bleibt die Mahnung erhalten und
  wird als „Zum Drucken/Postversand“ markiert. Druck sie über das
  PDF-Symbol.

Das Mahnungs-PDF ist mit „Zahlungserinnerung Nr. *n*“ überschrieben, nimmt
Bezug auf die Rechnung und ihr Datum und listet **Ursprünglicher Betrag**,
**Bereits gezahlt**, **Vorherige Mahngebühren** und **Gebühr dieser
Mahnung** (Gebührenzeilen nur, wenn es eine Gebühr gibt), den jetzt
fälligen Betrag, deine Nachricht und einen Schlusssatz mit der Bitte um
Zahlung.

!!! warning "Gebühren lassen sich nicht entfernen"
    Eine Mahnung und ihre Gebühr lassen sich nach dem Versand weder löschen
    noch ändern. Prüf die Gebühr, bevor du auf **Mahnung senden** klickst.
    Trägst du in **Gebühr (optional)** etwas ein, das keine Zahl ist, wird
    die Mahnung ohne Gebühr verschickt.

## Siehe auch {#related}

- [Rechnungsläufe](invoice-runs.md) -- woher die Rechnungen kommen.
- [Konten und Buchungen](bank-accounts.md) -- Zahlungen aus dem
  Kontoauszug erfassen.
- [Die Jahresrechnung erstellen](../../guides/annual-invoicing.md)
- [E-Mail-Protokoll](../../administration/email-log.md) -- prüfen, ob der
  Mailserver eine Rechnungs- oder Mahnungs-E-Mail angenommen hat.

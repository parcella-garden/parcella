# Finanzen {#finances}

Im Finanzmodul arbeitet die Kasse. Es erstellt die Jahresrechnungen des
Vereins für jede Parzelle und jedes Mitglied, verfolgt, wer bezahlt hat,
verschickt Mahnungen und erfasst die Rechnungen, die der Verein selbst
bekommt. Außerdem führt es ein einfaches Kassenbuch je Bankkonto. Aus all
dem entstehen eine kassenbasierte Einnahmen-Überschuss-Rechnung fürs
Finanzamt und ein Haushaltsplan fürs nächste Jahr.

!!! info "Wer das nutzen kann"
    - Das Modul ist **standardmäßig aus**. Ein Administrator schaltet es
      unter **Vereinseinstellungen** ein (der Schalter heißt **Finanzen**),
      siehe [Module ein- und ausschalten](../../administration/modules.md).
      Bevor du die ersten Rechnungen verschickst, füll die
      **Finanzeinstellungen** (Bankverbindung, Format der Rechnungsnummer)
      in den [Vereinseinstellungen](../../administration/settings.md) aus --
      sie stehen in der Fußzeile jeder Rechnung.
    - Vorstandsmitglieder und Administratoren (und alle in einer Gruppe mit
      vollem Zugriff) können alles.
    - Alle anderen brauchen eine [Gruppe](../../administration/groups.md),
      die Rechte für **Finanzen** gewährt:
        - **Lesen** -- jede Seite sehen, PDFs öffnen, CSV-Dateien
          exportieren;
        - **Schreiben** -- Läufe, Posten, Zahlungen, Mahnungen, Konten,
          Buchungen, Eingangsrechnungen, Kategorien und den Haushaltsplan
          anlegen und ändern;
        - **Löschen** -- diese Dinge wieder löschen.
    - Ein paar Aktionen rund um Cloud-Anhänge von Eingangsrechnungen sind
      nur für Vorstandsmitglieder und Administratoren, siehe
      [Eingangsrechnungen](incoming-invoices.md).

    Siehe [Rollen, Gruppen und Rechte](../../getting-started/roles-and-permissions.md).

## Wo du es findest {#where-to-find-it}

Ist das Modul an und darfst du es lesen, zeigt die Seitenleiste eine Gruppe
**Finanzen** mit vier Einträgen:

| Menüeintrag | Öffnet |
|---|---|
| **Übersicht** | Das unten beschriebene Finanz-Dashboard. |
| **Ausgangsrechnungen** | Die Liste der Rechnungsläufe, siehe [Rechnungsläufe](invoice-runs.md). |
| **Mahnungen** | Die Liste der überfälligen Rechnungen, siehe [Rechnungen, Zahlungen und Mahnungen](invoices.md#reminders). |
| **Eingangsrechnungen** | Rechnungen, die der Verein bekommen hat, siehe [Eingangsrechnungen](incoming-invoices.md). |

Alles andere (Konten, Kategorien, Artikelkatalog, Buchungen, Übersicht,
Haushaltsplan) erreichst du über die Karten des Dashboards.

## Finanz-Dashboard {#finances-dashboard}

![Finanz-Dashboard](../../assets/screenshots/finances/dashboard.png)

Die Startseite des Moduls. Drei Zahlen oben zeigen auf einen Blick, wie es um
deine Ausgangsrechnungen steht. Darunter führt je eine Karte zu einem
Bereich des Moduls.

| Zahl | Was sie zeigt |
|---|---|
| **Offene Rechnungen** | Wie viele Ausgangsrechnungen noch nicht vollständig bezahlt sind. Teilweise bezahlte Rechnungen zählen hier als offen. |
| **Offener Betrag** | Die Summe, die bei diesen Rechnungen noch offen ist (Rechnungsbetrag minus erfasste Zahlungen). Mahngebühren sind nicht enthalten. |
| **Überfällig** | Wie viele der offenen Rechnungen über das Fälligkeitsdatum ihres Rechnungslaufs hinaus sind. Rot, wenn es mehr als null sind. |

| Karte | Hinweis unter dem Titel | Öffnet |
|---|---|---|
| **Ausgangsrechnungen** | *n* Rechnungslauf(e/äufe) | [Rechnungsläufe](invoice-runs.md) |
| **Kategorien** | *n* Kategorie(n) angelegt | [Buchhaltungskategorien](bookkeeping.md#bookkeeping-categories) |
| **Artikelkatalog** | *n* Artikelvorlage(n) angelegt | [Artikelkatalog](invoice-runs.md#item-catalog) |
| **Konten** | *n* Konto/Konten angelegt | [Konten](bank-accounts.md#accounts) |
| **Mahnungen** | *n* Rechnung(en) überfällig | [Mahnungen](invoices.md#reminders) |
| **Eingangsrechnungen** | *n* Eingangsrechnung(en) | [Eingangsrechnungen](incoming-invoices.md) |
| **Alle Buchungen** | Alle Zahlungen aus Eingangs- und Ausgangsrechnungen | [Alle Buchungen](bookkeeping.md#all-bookings) |
| **Buchhaltungsübersicht** | Kassenbasierte Übersicht für das Finanzamt | [Buchhaltungsübersicht](bookkeeping.md#accounting-statement) |
| **Haushaltsplan** | Geplante Einnahmen und Ausgaben je Kategorie für das kommende Jahr, neben den Ist-Werten der Vorjahre | [Haushaltsplan](bookkeeping.md#budget-plan) |

Die meisten Unterseiten haben oben eine Schaltfläche **Zurück zu Finanzen**,
die dich hierher zurückbringt.

## Wie das Geld durchs Jahr fließt {#how-the-money-flows-through-a-year}

Ein typisches Vereinsjahr in Parcella sieht so aus:

1. **Einmal einrichten.** Leg deine
   [Buchhaltungskategorien](bookkeeping.md#bookkeeping-categories) an (oder
   importier deinen Kontenrahmen), deine
   [Bank- und Kassenkonten](bank-accounts.md#accounts) und die
   wiederkehrenden Rechnungsposten im
   [Artikelkatalog](invoice-runs.md#item-catalog) (Pacht pro m²,
   Mitgliedsbeitrag, Wasser, Strom, Versicherung ...).
2. **Die Jahresrechnungen vorbereiten.** Leg einen
   [Rechnungslauf](invoice-runs.md) für das Jahr an, füg die Posten aus dem
   Katalog hinzu, pass die Preise an und prüf die
   [Vorschau](invoice-runs.md#preview-invoices). Zählerstände,
   Versicherungen und Arbeitsstunden des Jahres sollten jetzt vollständig
   sein -- die verbrauchsabhängigen Posten lesen sie live.
3. **Abschließen und verschicken.** Beim Abschließen bekommen die
   Rechnungen ihre endgültigen Nummern. Dann verschickst du sie per E-Mail,
   lädst sie in die Cloud-Ordner der Parzellen und lädst das Druckpaket für
   alle herunter, die Papier bekommen.
4. **Zahlungen erfassen.** Trag Zahlungen von Hand in der Rechnungsliste des
   Laufs ein oder importier deinen Kontoauszug auf der
   [Buchungsseite des Kontos](bank-accounts.md#bookings-of-an-account) und
   ordne jede Zeile der Rechnung zu, die sie bezahlt.
5. **Säumigen hinterhergehen.** Die Seite [Mahnungen](invoices.md#reminders)
   listet jede überfällige Rechnung; die erste, zweite, dritte Mahnung
   schickst du aus der Rechnung, mit oder ohne Gebühr.
6. **Die eigenen Rechnungen des Vereins erfassen** als
   [Eingangsrechnungen](incoming-invoices.md) und als bezahlt markieren,
   wenn das Geld rausgeht.
7. **Das Jahr abschließen.** Die
   [Buchhaltungsübersicht](bookkeeping.md#accounting-statement) zeigt
   Einnahmen und Ausgaben je Kategorie, gezählt an dem Tag, an dem das Geld
   wirklich geflossen ist. Nutz sie fürs Finanzamt und die
   Jahreshauptversammlung, und plan das nächste Jahr im
   [Haushaltsplan](bookkeeping.md#budget-plan).

Die Anleitung [Die Jahresrechnung erstellen](../../guides/annual-invoicing.md)
geht die Schritte 2 bis 5 der Reihe nach durch.

## Kapitel {#chapters}

- [Rechnungsläufe](invoice-runs.md) -- der jährliche Rechnungsstapel, seine
  Posten und wie jeder Betrag berechnet wird, der Artikelkatalog, die
  Vorschau und das Abschließen.
- [Rechnungen, Zahlungen und Mahnungen](invoices.md) -- jede Rechnung über
  alle Läufe, der Versand, Zahlungen und das Mahnwesen.
- [Konten und Buchungen](bank-accounts.md) -- deine Konten, ihre Buchungen
  und der Import eines Kontoauszugs mit Rechnungszuordnung.
- [Eingangsrechnungen](incoming-invoices.md) -- Rechnungen, die der Verein
  bekommen hat, und ihre Zahlungen.
- [Kategorien, Haushaltsplan und Übersicht](bookkeeping.md) --
  Buchhaltungskategorien, die vereinsweite Buchungsliste, die
  Buchhaltungsübersicht und der Haushaltsplan.

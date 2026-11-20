# Glossar {#glossary}

Begriffe aus dem Verein und aus Parcella, alphabetisch. Die Kapitel
verlinken direkt auf einen Eintrag, zum Beispiel `glossary.md#deposit`.

## Arbeitseinsatz {#work-session}

Ein Termin, an dem Mitglieder Gemeinschaftsarbeit für den Verein leisten,
angerechnet auf ihre [Pflichtstunden](#mandatory-hours).
**Standard**-Einsätze sind geplant und lassen sich auf der Vereinswebsite
veröffentlichen; **besondere** Einsätze sind spontan und intern. Siehe
[Einen Arbeitseinsatz organisieren](guides/work-session.md).

## Artikelkatalog {#item-catalog}

Deine Liste wiederverwendbarer Rechnungsposten (Pacht, Wasser, Versicherung,
...), die du in den [Rechnungslauf](#invoice-run) jedes Jahres übernimmst. Zu
finden unter **Finanzen → Übersicht → Artikelkatalog**.

## Befreiung {#exemption}

Ein Mitglied, das in einem bestimmten Jahr keine
[Pflichtstunden](#mandatory-hours) leisten muss -- meist wegen eines
[Vereinsamts](#club-role), aus gesundheitlichen Gründen oder wegen des
Alters. Ist ein Pächter einer Parzelle befreit, ist die ganze Parzelle
befreit, und eine Befreiung gilt immer für das ganze Kalenderjahr.

## Begehung {#inspection}

Der Rundgang des Vorstands über eine Parzelle, wenn ein Pächter geht, um vor
der [Wertermittlung](#valuation) Mängel festzuhalten. Wird in einem
Übergabe-[Vorgang](#process) verfolgt.

## Beispieldaten {#sample-data}

Erfundene Mitglieder, Parzellen und andere Einträge, die du einer frischen
Installation hinzufügen kannst, um Parcella auszuprobieren, und mit einem
Klick wieder entfernst. Siehe [Beispieldaten](administration/sample-data.md).

## Bewerber {#applicant}

Jemand, der sich um einen Garten beworben hat und auf der
[Warteliste](#waiting-list) steht. Bewerber werden getrennt von
[Mitgliedern](#member) geführt: Mitglied werden sie erst, wenn sie wirklich
eine Parzelle bekommen. Siehe [Bewerber](modules/applicants.md).

## Eichung {#calibration}

Wasser- und Stromzähler dürfen nur bis zum Ablauf ihrer Eichung zur
Abrechnung genutzt werden. Parcella speichert das Jahr als **Geeicht bis**
und markiert abgelaufene Zähler mit **Eichung abgelaufen**. Die übliche
Lösung ist, [den Zähler zu tauschen](guides/meter-readings.md#a-meter-is-replaced).

## Einkaufswunsch {#purchase-request}

Ein Antrag, Vereinsgeld auszugeben, der vor dem Kauf eine
[Vier-Augen-Freigabe](#two-person-approval) braucht. Siehe
[Einkaufswünsche](modules/purchase-requests.md).

## Externer Kontakt {#external-contact}

Ein Lieferant, Handwerker, eine Behörde oder eine andere Stelle, mit der der
Verein zu tun hat -- eine Firma und/oder eine Ansprechperson. Kein Mitglied.
Siehe [Externe Kontakte](modules/external-contacts.md).

## Faktor {#factor}

Ein Multiplikator an einem [Zählpunkt](#metering-point) für Zähler, die nur
einen Bruchteil des echten Werts zeigen (zum Beispiel 20 bei einem
Stromzähler mit Stromwandlern). Zählerstände werden eingetragen, wie sie
angezeigt werden; die Auswertung multipliziert mit dem Faktor. Meist 1.

## Flächen A, B und C {#areas}

Die Gesamtfläche des Vereins, aufgeteilt in drei Teile, festgelegt unter
**Administration → Einstellungen → Flächen (qm)**:

- **A-Fläche (Parzellen, qm)** -- die Summe aller Parzellenflächen,
  berechnet von Parcella.
- **B-Fläche (Gemeinschaft, qm)** -- Wege, Grünflächen und anderes
  gemeinsames Vereinsland: die Gesamtfläche minus A und C, berechnet von
  Parcella.
- **C-Fläche (Stadt, qm)** -- Land, das der Verein verwaltet, das aber der
  Kommune gehört, von Hand eingetragen.

Auf der B-Fläche beruhen der
[Gemeinschaftsflächenanteil](#communal-area-share) und die
[öffentlichen Lasten](#public-burdens).

## Früherer, aktueller und künftiger Pächter {#former-tenant}

Ein [Pachtverhältnis](#tenancy) ist **aktuell**, solange es läuft,
**künftig**, wenn es an einem späteren Datum beginnt (nach einer Übergabe mit
künftigem Datum), und **früher**, sobald es geendet hat. Frühere Pächter
bleiben auf der Seite der Parzelle unter **Frühere Pächter**; nur aktuelle
(und künftige) Pächter können [Rechnungsadresse](#invoice-address) sein.

## Gemeinschaftsflächenanteil {#communal-area-share}

Ein Rechnungsposten, der die Pacht für das gemeinsame Vereinsland
([B-Fläche](#areas)) gleichmäßig auf die Parzellen verteilt, für die er gilt.
In der App: **Anteil an der Gemeinschaftsflächenpacht**.

## Gruppe {#group}

Eine Sammlung von [Rechten](#permission) in Parcella -- Lesen, Schreiben oder
Löschen je [Modul](#module) oder voller Zugriff --, die du Benutzerkonten
gibst. Neue Benutzer bekommen ihre Rechte nur über Gruppen. Siehe
[Gruppen](administration/groups.md).

## Hauptzähler {#main-meter}

Der Zähler, an dem der Verein Wasser oder Strom vom Versorger übernimmt. Sein
Verbrauch sollte etwa der Summe aller Parzellen- und Vereinszähler
entsprechen; Parcella warnt, wenn die Parzellen zusammen mehr verbraucht
haben.

## Kasse (Kassierer) {#treasurer}

Das Vorstandsmitglied, das für das Geld des Vereins zuständig ist. Gib der
Kasse in Parcella eine [Gruppe](#group) mit allen Rechten für **Finanzen**.

## Kaution {#deposit}

Ein Betrag, den der neue Pächter bei der Übernahme einer Parzelle zahlt und
den der Verein verwahrt und beim Auszug zurückzahlt -- oder einen Teil davon
behält. Parcella hat keine eigene Kautionsfunktion: Halte Betrag und Datum
im Übergabe-[Vorgang](#process) fest und erfass das Geld in **Finanzen**.
Siehe [Eine Parzelle übergeben](guides/parcel-handover.md#7-deposit-and-money).

## Kündigung {#notice-of-termination}

Die Erklärung des Pächters (oder des Vereins), dass eine Pacht endet. In
Parcella setzt du den Status der Parzelle auf **gekündigt**; das Datum wird
automatisch protokolliert.

## Mahnung {#dunning}

Die Erinnerung an eine unbezahlte Rechnung. In Parcella: **Mahnung senden**
bei einer überfälligen Rechnung erzeugt **Mahnung Nr. 1**, **Nr. 2** und so
weiter, mit freiwilliger Gebühr. Feste Mahnstufen gibt es nicht; der Vorstand
entscheidet, wann die nächste rausgeht. Siehe
[Rechnungen, Zahlungen und Mahnungen](modules/finances/invoices.md).

## Mitglied {#member}

Eine Person, die dem Verein angehört. Meist auch [Pächter](#tenant), aber
nicht unbedingt (fördernde oder Ehrenmitglieder). Ein Mitglied gilt bis zu
seinem Datum **Mitglied bis** als aktiv.

## Modul {#module}

Ein Bereich von Parcella -- Arbeitsstunden, Wasser, Finanzen, Vorgänge und so
weiter --, der sich für deinen Verein unter **Administration → Einstellungen
→ Funktionsbereiche** ein- oder ausschalten lässt. Ein ausgeschaltetes Modul
ist ausgeblendet; seine Daten bleiben. Siehe
[Module ein- und ausschalten](administration/modules.md).

## Öffentliche Lasten {#public-burdens}

Abgaben, die der Grundeigentümer an den Verein weitergibt -- Grundsteuer,
Straßenreinigung und ähnliche kommunale Gebühren --, meist je Quadratmeter.
Der Verein gibt sie an die Parzellen weiter, einschließlich eines Anteils für
das Gemeinschaftsland. In der App: **Öffentliche Lasten (eigene Fläche +
Gemeinschaftsflächenanteil)**: die eigene Fläche der Parzelle plus ihr
gleicher Anteil an der [B-Fläche](#areas), mal dem Satz, den du eingibst.

## Pachtverhältnis {#tenancy}

Die Pacht einer Parzelle durch ein Mitglied, von einem Startdatum bis zu
einem freiwilligen Enddatum. Ein beendetes Pachtverhältnis bleibt als
Verlauf erhalten; mehrere Mitglieder können sich eine Parzelle teilen. Siehe
auch [früherer Pächter](#former-tenant).

## Pächter {#tenant}

Ein Mitglied mit einem [Pachtverhältnis](#tenancy) an einer Parzelle.

## Parzelle (Garten) {#parcel}

Ein Gartengrundstück, erkennbar an seiner **Gartennummer**. An manchen
Stellen in der App heißt es „Garten“.

## Parzellenstatus: aktiv, gekündigt, Gemeinschaftsfläche, gelöscht {#parcel-status}

Die vier Status einer [Parzelle](#parcel):

- **aktiv** -- eine normale Parzelle, meist an jemanden verpachtet.
- **gekündigt** -- der Pächter hat [gekündigt](#notice-of-termination), und
  die Parzelle ist auf dem Weg zu einem neuen Pächter. Nur gekündigte
  Parzellen lassen sich an einen [Bewerber](#applicant) übergeben.
- **Gemeinschaftsfläche** -- Vereinsland, das als Parzelle geführt wird
  (Wege, Spielplatz), nie verpachtet. Zählt nicht zur verpachteten Fläche.
- **gelöscht** -- nicht mehr in Gebrauch, aber mit seinem Verlauf erhalten.

## Patenschaft {#sponsorship}

Ein Mitglied kümmert sich das Jahr über um einen Bereich der Anlage -- eine
Hecke, den Spielplatz -- und bekommt dafür eine feste Zahl
[Pflichtstunden](#mandatory-hours) angerechnet. Siehe **Arbeitseinsätze →
Patenschaften**.

## Pflichtstunden {#mandatory-hours}

Die Stunden Gemeinschaftsarbeit, die eine Parzelle oder ein Mitglied dem
Verein jedes Jahr schuldet, wie von der Mitgliederversammlung beschlossen.
Nicht geleistete Stunden werden zu einem Stundensatz bezahlt. Parcella
rechnet besuchte [Arbeitseinsätze](#work-session),
[Patenschaften](#sponsorship) und
[Stundenübertragungen](#hours-transfer) darauf an, und der Fehlbetrag lässt
sich im jährlichen [Rechnungslauf](#invoice-run) abrechnen. Siehe
[Arbeitsstunden](modules/work-hours.md).

## Rechnungsadresse {#invoice-address}

Der Pächter einer Parzelle, an dessen Adresse die Rechnungen der Parzelle
gehen -- **Als Rechnungsadresse verwenden** am Pachtverhältnis. Mehrere
Pächter einer Parzelle können sie haben; die Parzelle bekommt trotzdem eine
Rechnung. Eine Parzelle ohne Rechnungsadresse bekommt keine Rechnung.

## Rechnungslauf {#invoice-run}

Ein Stapel Rechnungen, meist die Jahresrechnungen eines Jahres. Du fügst
Posten hinzu, prüfst eine Vorschau, **schließt** ihn dann **ab** -- das
vergibt die endgültigen Rechnungsnummern -- und verschickst ihn. Siehe
[Die Jahresrechnung erstellen](guides/annual-invoicing.md).

## Recht {#permission}

Was ein Benutzer in einem [Modul](#module) tun darf: **Lesen** (ansehen),
**Schreiben** (hinzufügen und ändern) oder **Löschen**. Jeder, der sich
anmelden kann, darf Mitglieder und Parzellen nachschlagen. Siehe
[Rollen, Gruppen und Rechte](getting-started/roles-and-permissions.md).

## Rolle {#role}

Ältere Konten haben eine feste Rolle (**Administrator**, **Vorstand**,
**Kassierer**, **Lesend (nur anschauen)**). Neue Konten bekommen ihre Rechte
stattdessen über [Gruppen](#group). Nicht dasselbe wie ein
[Vereinsamt](#club-role).

## Sammel-PDF {#print-bundle}

Ein PDF mit jeder Rechnung eines Laufs, deren Empfänger nicht per E-Mail
erreichbar ist, fertig zum Drucken und Verschicken.

## Stundenübertragung {#hours-transfer}

Ein Mitglied, das mehr [Pflichtstunden](#mandatory-hours) als nötig geleistet
hat, gibt einen Teil des Überschusses für dasselbe Jahr an ein anderes
Mitglied ab. Siehe **Arbeitseinsätze → Stundenübertragung**.

## Tag {#tag}

Ein freies Etikett an einem Mitglied, wie „Heckenteam“ oder
„Wasserverantwortlich“, um Leute zu finden und zu filtern. Tags gibt es auch
für externe Kontakte.

## Übergabe {#handover}

Der Wechsel vom bisherigen zum neuen Pächter einer Parzelle. In Parcella
beendet **Parzelle zuweisen** bei einer Bewerbung das alte
[Pachtverhältnis](#tenancy), macht den Bewerber zu Mitglied und Pächter und
setzt die Parzelle wieder auf aktiv. Siehe
[Eine Parzelle übergeben](guides/parcel-handover.md).

## Umlage {#general-levy}

Ein einmaliger Betrag, den der Verein von allen Parzellen gemeinsam
aufbringen muss -- eine Anwaltsrechnung, eine Reparatur, eine gestiegene
Versicherungsprämie --, zu gleichen Teilen. In der App: **Allgemeine Umlage
(gleichmäßig auf alle Parzellen aufgeteilt)**. Du gibst den *Gesamtbetrag*
als Einzelpreis ein; Parcella teilt ihn durch die Zahl der abgerechneten
Parzellen und setzt jeden Anteil auf die Rechnung der Parzelle.

## Vereinsamt {#club-role}

Ein Amt im Verein -- Vorsitz, Kasse, Wasserwart --, das ein Mitglied ein Jahr
lang innehat. Ein Vereinsamt kann seinen Inhaber von den
[Pflichtstunden](#mandatory-hours) [befreien](#exemption). Eingerichtet
unter **Arbeitseinsätze → Einsätze & Übersicht → Vereinsrollen**. Nicht zu
verwechseln mit einer [Rolle](#role) in Parcella.

## Vier-Augen-Prinzip {#two-person-approval}

Ein [Einkaufswunsch](#purchase-request) ist erst freigegeben, wenn zwei
verschiedene Vorstandsmitglieder zugestimmt haben -- und keins davon darf die
Person sein, die ihn gestellt hat. Ein einzelnes Vorstandsmitglied kann ihn
ablehnen.

## Vorgang {#process}

Eine Schritt-für-Schritt-Checkliste, die du selbst entwirfst -- zum Beispiel
eine Parzellenübergabe oder die Aufnahme eines Mitglieds --, ausgeführt für
eine Parzelle, ein Mitglied oder einen Bewerber. Jede Stufe hat Felder zum
Ausfüllen; Pflichtfelder müssen ausgefüllt sein, bevor es weitergeht. Siehe
[Vorgänge](modules/processes.md).

## Vorstand {#board}

Der gewählte Vorstand des Vereins. In Parcella haben Vorstandsmitglieder
meist vollen Zugriff auf jedes Modul. Den aktuellen Vorstand trägst du unter
**Administration → Einstellungen → Vorstandsmitglieder** ein; seine Rechte
kommen aus einer [Gruppe](#group) mit **Voller Zugriff auf jedes Modul**
(oder, bei älteren Konten, aus der Rolle **Vorstand**).

## Warteliste {#waiting-list}

Die [Bewerber](#applicant), die auf eine Parzelle warten, in der Reihenfolge
ihrer Bewerbung. In Parcella: **Bewerber** mit dem Filter **Offen**.

## Wertermittlung (Wertgutachten) {#valuation}

Die Einschätzung durch einen Fachmann, was Laube, Pflanzen und Einbauten auf
einer Parzelle wert sind, wenn der Pächter geht. Parcella berechnet sie
nicht; du legst das Gutachten im Übergabe-[Vorgang](#process) ab.

## Zähler {#meter}

Der Wasser- oder Stromzähler selbst, mit seiner Nummer, seinem Eichjahr und
seinem Anfangsstand. Ein [Zählpunkt](#metering-point) hat immer genau einen
Zähler; wird er ersetzt, bleibt der alte als früherer Zähler erhalten.

## Zählerstand {#reading}

Der Wert auf der Anzeige eines Zählers. Parcella speichert einen Zählerstand
je [Zähler](#meter) und Jahr; der Verbrauch des Jahres ist dieser Stand
minus der vorherige.

## Zählpunkt {#metering-point}

Eine Stelle, an der Wasser oder Strom gemessen wird: der Anschluss einer
Parzelle, der [Hauptzähler](#main-meter) oder ein Vereinsanschluss
(Vereinsheim, Waschplatz). Der Zählpunkt bleibt; der dort eingebaute
[Zähler](#meter) kann wechseln.

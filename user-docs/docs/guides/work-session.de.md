# Einen Arbeitseinsatz organisieren {#organising-a-work-session}

Die meisten Vereine erwarten von jeder Parzelle (oder jedem Mitglied) eine
bestimmte Zahl an [Pflichtstunden](../glossary.md#mandatory-hours)
Gemeinschaftsarbeit im Jahr -- Hecke schneiden, Wege ausbessern, der
Frühjahrsputz. Diese Anleitung begleitet einen
[Arbeitseinsatz](../glossary.md#work-session) von der Planung bis zur
Jahresauswertung: ihn anlegen, Mitglieder sich über die Vereinswebsite
anmelden lassen, festhalten, wer wirklich gekommen ist, und sehen, wer noch
Stunden schuldet.

!!! info "Wer das tun kann"
    Einsätze anlegen und Anwesenheit erfassen braucht das Recht
    **Schreiben** für **Arbeitseinsätze**; einen Teilnehmer oder eine
    Übertragung entfernen braucht **Löschen**. Das Modul
    (**Pflichtstunden-Verwaltung**) ist standardmäßig an. Die
    Veröffentlichung auf der Website braucht für die einmalige Einrichtung
    in Schritt 3 einen Administrator.

## 1. Die Regeln des Jahres festlegen (einmal im Jahr) {#1-set-the-years-rules-once-a-year}

1. Öffne **Arbeitseinsätze → Einsätze & Übersicht**. Hat das Jahr noch keine
   Regeln, sagt die Seite *„Keine Pflichtstunden-Konfiguration für …
   vorhanden.“* -- klick auf **Jetzt anlegen →** (oder unten auf
   **Stunden-Konfiguration**).
2. Trag unter **Jahr anlegen / aktualisieren** ein:
    - **Jahr**
    - **Pflichtstunden gesamt** -- die je Jahr geschuldeten Stunden;
    - **Stundensatz** -- was eine nicht geleistete Stunde kostet;
    - **Abrechnungsmodus** -- **Pro Pachtvertrag / Parzelle** (alle Pächter
      einer Parzelle arbeiten die Stunden gemeinsam ab) oder **Pro
      Mitglied** (jedes Mitglied für sich);
    - bei Bedarf eine **Notiz**, z. B. den Beschluss der
      Mitgliederversammlung.
3. Klick auf **Speichern**.

Auf derselben Seite steuert die Karte **Bestätigungs-E-Mail zur Anmeldung**
die E-Mail, die Mitglieder nach einer Anmeldung über die Website bekommen
(Schritt 3).

**Befreiungen.** Vorstandsmitglieder, Menschen mit gesundheitlichen Gründen
oder über einer Altersgrenze sind oft befreit. Das richtest du unter
**Einsätze & Übersicht → Vereinsrollen** ein: Leg eine Rolle mit **Von
Pflichtstunden befreit** und einem **Befreiungsgrund** an und ordne ihr dann
Mitglieder für das Jahr zu. Ist ein Pächter einer Parzelle befreit, ist die
ganze Parzelle befreit; eine Befreiung gilt für das ganze Kalenderjahr.

## 2. Den Einsatz anlegen {#2-create-the-session}

1. Öffne **Arbeitseinsätze → Einsätze & Übersicht** und klick auf **Neuer
   Einsatz**.
2. Füll aus:
    - **Titel**, z. B. „Frühjahrsputz“;
    - **Typ**: **Standard (geplant)** für Einsätze, die du ankündigst, oder
      **Besonders (spontan)** für ungeplante -- besondere Einsätze
      erscheinen nie auf der Website;
    - **Datum**, **Von** und **Bis**;
    - **Max. Teilnehmer** -- leer lassen für unbegrenzt;
    - **Anmeldeschluss (Tage vorher)** -- die Anmeldung auf der Website
      schließt so viele Tage vor dem Einsatz (1 = am Vortag); leer heißt, sie
      schließt, wenn der Einsatz vorbei ist;
    - **Stunden pro Teilnehmer** -- wird jedem angerechnet, der kommt,
      später je Person anpassbar;
    - **Beschreibung** -- Aufgaben, Werkzeug, was man mitbringen soll.
3. Klick auf **Einsatz anlegen**.

Der Einsatz steht unter **Arbeitseinsätze …** für sein Jahr.

## 3. Die Anmeldung auf der Vereinswebsite veröffentlichen (einmalige Einrichtung) {#3-publish-the-sign-up-on-the-club-website-one-time-setup}

Mitglieder melden sich auf der Vereinswebsite mit ihrer
**Parzellennummer** und, freiwillig, ihrem Namen an -- ohne Parcella-Zugang.
Die Website zeigt nie, welche Mitglieder auf welcher Parzelle sind.

Ein Administrator richtet das einmal ein:

1. **Administration → Einstellungen → Funktionsbereiche**: **Öffentliche
   Anmelde-API** anhaken und auf **Einstellungen speichern** klicken. Sie ist
   standardmäßig aus, weil sie ein öffentliches Formular öffnet.
2. **Administration → Integrationen → Öffentliche Anmelde-API**: Notier dir
   das **API-Token** (für einen serverseitigen Connector), trag deine Website
   unter **Erlaubte Website-Adressen** ein (z. B. `https://example.org`) und
   klick auf **Adressen speichern**. Hak bei Bedarf **ALTCHA verlangen** gegen
   Spam an.
3. Bau auf der Website das Anmeldeformular ein -- mit dem Plugin Parcella
   Connector für WordPress oder einem einfachen HTML-Formular für jede andere
   Website. Die Einzelheiten findet die Person, die eure Website betreut, in
   der Entwicklerdokumentation.

Danach erscheint jeder neue **Standard**-Einsatz von selbst auf der Website,
solange sein Datum und sein Anmeldeschluss nicht vorbei sind und er nicht
voll ist.

**Was bei einer Anmeldung passiert.** Parcella schaut nach den aktuellen
Pächtern der Parzelle. Passt der eingetippte Name auf genau einen von ihnen,
wird nur dieses Mitglied angemeldet. Fehlt der Name oder passt er nicht
eindeutig, werden **alle** aktuellen Pächter der Parzelle angemeldet, mit
einer Notiz, die den Vorstand um Prüfung bittet -- entfern alle, die sich
nicht wirklich angemeldet haben. Jedes neu angemeldete Mitglied bekommt die
Bestätigungs-E-Mail an die in Parcella hinterlegte Adresse (nicht die ins
Formular getippte).

Mehr: [Integrationen](../administration/integrations.md) und
[Für Gärtner](../gardeners/index.md).

## 4. Die Anmeldungen im Blick behalten {#4-keep-an-eye-on-sign-ups}

- Neue Anmeldungen zeigen einen Zähler neben **Arbeitseinsätze** in der
  Seitenleiste und auf dem Dashboard.
- Öffne den Einsatz (Klick in der Liste auf **Einsätze & Übersicht**). Neue
  Teilnehmer tragen ein Badge **Neu**. Hast du sie dir angesehen, klick auf
  **Als gesehen markieren**.
- Prüf die Spalte **Notiz**: Anmeldungen über die Website tragen dort die
  Bemerkungen und Kontaktdaten und eine Warnung, wenn die ganze Parzelle
  angemeldet wurde.
- Um jemanden von Hand hinzuzufügen (Anmeldung per Telefon), nimm unten in
  der Teilnehmertabelle **Mitglied wählen…**, wähl **Angemeldet** und klick
  auf **Hinzufügen**.

**Aufgaben (freiwillig).** Führst du unter **Arbeitseinsätze → Aufgaben**
eine Liste von Arbeiten, plan dort einige für diesen Einsatz ein. Auf der
Seite des Einsatzes kannst du dann jede einem Teilnehmer zuweisen
(**Zugewiesen an**) und ihren **Aufwand** sehen (**Leicht**, **Mittel**,
**Anspruchsvoll**). **Aufgaben verwalten** führt zur ganzen Liste.

## 5. Am Tag selbst: die Teilnehmerliste drucken {#5-on-the-day-print-the-attendee-sheet}

1. Öffne den Einsatz und klick auf **Teilnehmerliste**.
2. Druck das PDF. Es listet jeden angemeldeten Teilnehmer mit Parzelle,
   Name, erwarteten Stunden, zugewiesener Aufgabe und einer
   Unterschriftszeile.

Korrigier die Stunden bei Bedarf auf dem Papier; eintippen tust du sie
hinterher. Die Liste ändert nichts in Parcella.

## 6. Danach: die Anwesenheit erfassen {#6-afterwards-record-attendance}

1. Öffne den Einsatz.
2. Wähl für jeden Teilnehmer im Auswahlfeld **Status** **Erschienen** oder
   **Nicht erschienen**. Das speichert sofort.
3. Hat jemand mehr oder weniger als die **Stunden pro Teilnehmer**
   gearbeitet, tipp die tatsächlichen Stunden in sein Feld **Stunden** und
   klick auf die Schaltfläche ✓.
4. Leute, die ohne Anmeldung gekommen sind: **Mitglied wählen…**, Status
   **Erschienen**, ihre Stunden, **Hinzufügen**.
5. Mit dem Suchfeld über der Tabelle findest du jemanden nach Name oder
   Parzellennummer.

Nur Teilnahmen mit **Erschienen** zählen für die Stunden.

## 7. Patenschaften und Stundenübertragungen {#7-sponsorships-and-hours-transfers}

**[Patenschaften](../glossary.md#sponsorship)** sind Bereiche, um die sich
ein Mitglied das ganze Jahr kümmert (eine Hecke, der Spielplatz), statt oder
zusätzlich zu den Einsätzen.

1. Öffne **Arbeitseinsätze → Patenschaften**.
2. Trag unter **Patenschaft anlegen / Mitglied hinzufügen** den **Bereich**,
   das **Mitglied** (oder lass es auf **– noch nicht vergeben –**, um den
   Bereich erst auszuschreiben), eine **Beschreibung**, die **Anrechenbaren
   Stunden/Jahr** sowie **Gültig ab** / **Gültig bis** ein.
3. Klick auf **Speichern**.

Eine Patenschaft rechnet erst Stunden an, wenn sie ein Datum **Gültig ab**
und ein Mitglied hat. Mehrere Mitglieder können sich einen Bereich teilen --
leg je Mitglied eine Zeile mit demselben Bereichsnamen an; jedes bekommt die
volle Anrechnung.

**[Stundenübertragungen](../glossary.md#hours-transfer)**: Ein Mitglied, das
mehr als nötig geleistet hat, kann Stunden an jemand anderen abgeben.

1. Öffne **Arbeitseinsätze → Stundenübertragung**.
2. Wähl unter **Stunden übertragen** **Von (gibt ab)**, **An (erhält)**, die
   **Stunden** und bei Bedarf eine **Notiz**.
3. Klick auf **Stunden übertragen**.

Abgeben lässt sich nur der Überschuss des Gebenden im Jahr. Mitglieder ohne
Parzelle und befreite Mitglieder können alle ihre Stunden abgeben.

## 8. Die Jahresauswertung {#8-the-year-end-evaluation}

1. Öffne **Arbeitseinsätze → Jahresauswertung** und wähl das Jahr.
2. Jede Zeile ist eine Parzelle (oder, je nach **Abrechnungsmodus**, ein
   Mitglied) mit **Pflicht**, **Einsätze**, **Patenschaft**,
   **Übertragen**, **Gesamt**, **Offen** und **Schuldbetrag** und einem
   **Status** **Erfüllt**, **Offen** oder **Befreit**.
3. Klick auf den Pfeil am Anfang einer Zeile (**Arbeitseinsätze
   anzeigen**), um zu sehen, aus welchen Einsätzen die Stunden kamen.
4. **CSV-Export** lädt die Auswertung herunter.

Pächter, die im Lauf des Jahres gegangen sind, schulden trotzdem die
Stunden dieses Jahres; ihre Zeile trägt ein Badge „Pacht beendet …“.

Um die offenen Stunden abzurechnen, füg dem jährlichen Rechnungslauf eine
Position **Pflichtstunden-Fehlbetrag (aus Modul)** hinzu -- siehe
[Die Jahresrechnung erstellen](annual-invoicing.md).

## Siehe auch {#related}

- [Arbeitsstunden](../modules/work-hours.md)
- [Kalender](../modules/calendar.md)
- [Integrationen](../administration/integrations.md)
- [Die Jahresrechnung erstellen](annual-invoicing.md)
- Glossar: [Pflichtstunden](../glossary.md#mandatory-hours),
  [Befreiung](../glossary.md#exemption),
  [Patenschaft](../glossary.md#sponsorship),
  [Stundenübertragung](../glossary.md#hours-transfer)

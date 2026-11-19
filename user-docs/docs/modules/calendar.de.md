# Kalender {#calendar}

Das Kalendermodul hält die Termine, die deinem Verein wichtig sind, an einem
Ort zusammen: Versammlungen und Begehungen, Geburtstage der Mitglieder,
wann Vorstandsmitglieder vor Ort sind und wann jemand nicht da ist. Jeder
Kalender lässt sich in einer Kalender-App auf Handy oder Computer
abonnieren.

!!! info "Wer das nutzen kann"
    - Der Modulschalter ist **Kalender** unter **Administration → Module ein-
      und ausschalten**. Er ist standardmäßig **an**.
    - Die Rollen **Vorstand** und **Administrator** sowie Mitglieder einer
      Gruppe mit **Voller Zugriff auf jedes Modul** können alles.
    - Alle anderen brauchen das Recht **Kalender** in einer ihrer
      [Gruppen](../administration/groups.md): *Lesen*, um die Kalender zu
      sehen, *Schreiben*, um Einträge hinzuzufügen, *Löschen*, um sie zu
      entfernen.
    - **Vorstandsabwesenheit** ist die Ausnahme: Wer angemeldet ist und den
      Kalender öffnen kann, kann eine Abwesenheit eintragen.
    - Eigene Kalender unter **Eigene Kalender** anlegen und bearbeiten
      braucht vollen Zugriff (Vorstand, Administrator oder eine Gruppe mit
      vollem Zugriff).

Eine Monatsansicht gibt es absichtlich nicht. Jeder Kalender ist eine
einfache Liste dessen, was ansteht, ab heute. Vergangene Einträge fallen
automatisch aus der Liste (und aus den Abo-Feeds).

Alle Kalender findest du in der Seitenleiste unter **Kalender**:
**Vereinskalender**, **Geburtstage**, **Vorstandspräsenz**,
**Vorstandsabwesenheit** und **Eigene Kalender**. Die einfache
Kalenderadresse führt zum **Vereinskalender**.

## Vereinskalender {#community-calendar}

![Vereinskalender](../assets/screenshots/calendar/community.png)

Der vereinsweite Kalender: Mitgliederversammlungen, Parzellenbegehungen und
andere Vereinstermine, zusammen mit den geplanten Arbeitseinsätzen aus dem
Modul [Arbeitsstunden](work-hours.md). Diesen Kalender kannst du auf deiner
öffentlichen Website zeigen.

### Neuer Eintrag {#new-entry}

Die Karte **Neuer Eintrag** links erscheint nur mit Recht *Schreiben* für
den Kalender.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Art** | **Mitgliederversammlung**, **Parzellenbegehung** oder **Sonstiges** (Vorgabe). Ändert nur das farbige Badge in der Liste. |
| **Titel** | Pflicht. Der Name des Termins, z. B. „Jahreshauptversammlung“. |
| **Datum** | Pflicht. Der (erste) Tag des Termins. |
| **Uhrzeit** | Freiwillige Anfangszeit. Für einen ganztägigen Eintrag leer lassen. |
| **Enddatum** | Freiwillig. Nur für mehrtägige Einträge -- bei einem Tag leer lassen. |
| **Endzeit** | Freiwillige Endzeit. |
| **Ort** | Freiwillig. Erscheint mit einer Stecknadel unter dem Titel. |
| **Beschreibung** | Freiwilliger Freitext. Erscheint nicht in der Liste, geht aber in den Abo-Feed und das Website-Widget. |
| **Eintrag hinzufügen** | Speichert den Eintrag und zeigt ihn in der Liste. |

### Anstehend {#upcoming}

| Spalte | Was sie zeigt |
|---|---|
| **Datum** | Das Datum, dazu der Zeitraum, falls eingetragen. |
| **Titel** | Titel und Ort. Bei einem Arbeitseinsatz verlinkt der Titel auf diesen Einsatz im Arbeitsstunden-Modul. |
| **Art** | Ein Badge: **Mitgliederversammlung**, **Parzellenbegehung**, **Sonstiges** oder **Arbeitseinsatz**. |
| Papierkorb-Symbol | Löscht den Eintrag nach einer Bestätigung (**Diesen Eintrag wirklich löschen?**). Erscheint nur mit Recht *Löschen* und nur bei hier angelegten Einträgen -- Arbeitseinsätze änderst du im Arbeitsstunden-Modul. |

Ist nichts geplant, sagt die Liste **Keine anstehenden Einträge.**

!!! note "Welche Arbeitseinsätze erscheinen"
    Hier erscheinen nur reguläre, geplante Arbeitseinsätze. Spontane
    „Sondereinsätze“ (zum Beispiel „heute die Bank streichen“) fehlen, weil
    Mitglieder sie nicht einplanen können. Arbeitseinsätze werden direkt aus
    dem Arbeitsstunden-Modul gelesen; verschiebst du dort einen Einsatz,
    ändert er sich auch hier -- es gibt nichts abzugleichen.

### Abonnieren (ICS) {#subscribe-ics}

Die Schaltfläche **Abonnieren (ICS)** oben rechts zeigt den **Öffentlichen
ICS-Link (kann auf der öffentlichen Website eingebunden werden)**. Klick in
das Feld, um die Adresse zu markieren und zu kopieren.

Dieser Feed braucht keine Anmeldung und kein Passwort. Er enthält nur, was
ohnehin öffentlich ist: die Einträge oben und die geplanten
Arbeitseinsätze. Du kannst ihn in einer Kalender-App hinzufügen oder auf der
Vereinswebsite zeigen (siehe
[In einer Kalender-App abonnieren](#subscribing-in-a-calendar-app) unten).

## Geburtstage {#birthdays}

![Geburtstage](../assets/screenshots/calendar/birthdays.png)

Die anstehenden Geburtstage deiner aktiven Mitglieder. Für diese Liste wird
nichts gespeichert: Sie wird jedes Mal aus dem Geburtsdatum jedes Mitglieds
berechnet. Korrigierst du ein Geburtsdatum beim [Mitglied](members.md),
stimmt die Liste sofort. Mitglieder ohne Geburtsdatum erscheinen nicht.

### Zeitraum und Reihenfolge wählen {#choosing-the-time-range-and-order}

Der Kopf der Karte **Anstehende Geburtstage** zeigt die abgedeckten Daten
(zum Beispiel „01.12.2026 – 28.02.2027“) und zwei Auswahlfelder. Die Liste
lädt neu, sobald du eines änderst.

| Feld | Was es bewirkt |
|---|---|
| Zeitraum | **Nächster Monat**, **Nächste 3 Monate** (Vorgabe) oder **Nächste 12 Monate**, immer ab heute gezählt. **Nächste 12 Monate** listet jedes Mitglied mit Geburtsdatum. |
| Sortierung | **Nach Geburtstag sortieren** (Vorgabe), **Nach Nachname sortieren** oder **Nach Parzellennummer sortieren**. Die Sortierung nach Parzelle nutzt die niedrigste aktuelle Parzellennummer des Mitglieds und stellt Mitglieder ohne Parzelle ans Ende. |

### Anstehende Geburtstage {#upcoming-birthdays}

| Spalte | Was sie zeigt |
|---|---|
| **Datum** | Das Datum des nächsten Geburtstags. |
| **Name** | Das Mitglied, verlinkt auf seinen Eintrag. Runde Geburtstage (30, 40, 50 ...) bekommen ein Badge **Rund**, und die ganze Zeile ist hervorgehoben. |
| **Wird** | Das Alter, das das Mitglied wird. |
| **Tags** | Die Tags des Mitglieds. Ein Klick auf einen öffnet die Mitgliederliste, gefiltert nach diesem Tag. |
| **Geschenk** | **Kein Geschenk**, wenn das Mitglied kein Geburtstagsgeschenk möchte (beim Mitglied eingestellt). |

Hat im gewählten Zeitraum niemand Geburtstag, sagt die Liste **Keine
anstehenden Geburtstage hinterlegt.**

### PDF drucken {#print-pdf}

**PDF drucken** erzeugt eine Liste zum Ausdrucken für die Person, die die
Geschenke verteilt. Sie nutzt genau den Zeitraum und die Reihenfolge, die du
auf der Seite gewählt hast.

Das PDF ist A4 quer, mit dem Briefkopf deines Vereins, und hat mehr Spalten
als die Webseite: Parzelle, Name, Geburtstag, das neue Alter (runde
Geburtstage hervorgehoben), Tags, „Kein Geschenk“, Postadresse, Haupt-E-Mail
und Haupttelefonnummer. Bei Sortierung nach Parzelle stehen die Mitglieder
unter ihrer Parzellennummer; ein Mitglied mit mehreren Parzellen erscheint
unter jeder, und Mitglieder ohne Parzelle kommen zuletzt unter „Ohne Garten“.

!!! warning "Persönliche Daten"
    Der Ausdruck enthält Adressen und Telefonnummern. Behandle Papierkopien
    entsprechend.

### Abonnieren (ICS) {#subscribe-ics_1}

Die Schaltfläche **Abonnieren (ICS)** zeigt einen **Privaten ICS-Link (nicht
weitergeben -- jeder mit diesem Link kann ihn abrufen)**. Der Feed enthält den
Geburtstag jedes aktiven Mitglieds als jährlich wiederkehrenden
ganztägigen Eintrag.

## Vorstandspräsenz {#council-presence}

![Vorstandspräsenz](../assets/screenshots/calendar/council-presence.png)

Plane, wann Vorstandsmitglieder vor Ort sind, zum Beispiel Sprechzeiten im
Vereinsheim. Mitglieder sehen dann, wann jemand vom Vorstand da ist.

### Neue Präsenzzeit {#new-presence-slot}

Erscheint nur mit Recht *Schreiben* für den Kalender.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Vorstandsmitglied(er)** | Pflicht. Hak ein oder mehrere Benutzerkonten an. Wähl mehrere, wenn sich mehrere diesen Termin teilen -- jedes bekommt einen eigenen Eintrag für denselben Termin. Hakst du niemanden an, zeigt das Formular **Bitte mindestens ein Vorstandsmitglied auswählen** und speichert nicht. |
| **Datum** | Pflicht. |
| **Von** / **Bis** | Freiwillige Uhrzeiten. Ohne Uhrzeit gilt der Termin als ganztägig. |
| **Notiz** | Freiwillig, z. B. „Offene Sprechstunde für Mitglieder“. |
| **Hinzufügen** | Speichert den Termin. |

Die Personenliste zeigt nur aktive Benutzerkonten, nicht jedes Mitglied: Ein
Vorstandsmitglied braucht einen Parcella-Zugang, um gelistet zu werden.

### Anstehend {#upcoming_1}

Die Einträge stehen unter je einer Überschrift pro Tag.

| Spalte | Was sie zeigt |
|---|---|
| **Mitglied** | Bild und Name des Benutzers. |
| **Uhrzeit** | Von -- bis oder ein Strich, wenn keine Uhrzeit angegeben ist. |
| **Notiz** | Die Notiz, falls vorhanden. |
| Papierkorb-Symbol | Löscht diesen einen Eintrag (eine Person, ein Termin) nach einer Bestätigung. Braucht Recht *Löschen*. |

Ist nichts geplant: **Keine anstehenden Präsenzzeiten geplant.**

Die Schaltfläche **Abonnieren (ICS)** zeigt einen privaten Link, wie bei den
Geburtstagen. Termine mit Uhrzeit erscheinen in Kalender-Apps als Termine
mit Zeit.

## Vorstandsabwesenheit {#council-absence}

![Vorstandsabwesenheit](../assets/screenshots/calendar/council-absence.png)

Urlaub und andere Abwesenheiten, damit der Vorstand weiß, wer nicht
erreichbar ist. Diese Seite kann jeder nutzen, der angemeldet ist -- ein
zusätzliches Recht brauchst du nicht.

### Abwesenheit eintragen {#log-absence}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Mitglied(er)** | Standardmäßig du selbst; wähl weitere Personen aus, wenn du für sie einträgst. Du kannst dich selbst abwählen, um nur für jemand anderen einzutragen. Wählst du alle ab, wird die Abwesenheit für dich eingetragen. |
| **Von** | Pflicht. Erster Tag der Abwesenheit. |
| **Bis** | Pflicht. Letzter Tag der Abwesenheit. |
| **Notiz** | Freiwillig, z. B. „Urlaub“. Was du erklärst, entscheidest du. |
| **Hinzufügen** | Speichert eine Abwesenheit je angehakter Person. |

### Anstehende Abwesenheiten {#upcoming-absences}

Abwesenheiten bleiben in der Liste, bis ihr letzter Tag vorbei ist.

| Spalte | Was sie zeigt |
|---|---|
| **Wer** | Bild und Name des Benutzers. |
| **Zeitraum** | Von -- bis. |
| **Notiz** | Die Notiz, falls vorhanden. |
| Papierkorb-Symbol | Löscht den Eintrag nach einer Bestätigung. Du siehst es bei deinen eigenen Einträgen; Vorstand und Benutzer mit vollem Zugriff sehen es bei jedem Eintrag, um Fehler zu bereinigen. |

Ist niemand weg: **Keine anstehenden Abwesenheiten eingetragen.**

Die Schaltfläche **Abonnieren (ICS)** zeigt einen privaten Link, wie bei den
Geburtstagen. Abwesenheiten sind ganztägige Einträge.

## Eigene Kalender {#my-calendars}

![Eigene Kalender](../assets/screenshots/calendar/custom-index.png)

Die zusätzlichen Kalender deines Vereins, für alles, was nicht in den
öffentlichen Vereinskalender gehört: Belegung des Vereinsheims,
Vorstandstermine, der Mähplan. Keiner dieser Kalender ist je öffentlich.

Die Liste **Kalender** zeigt:

- **Ressourcen** ganz oben, wenn das Modul [Inventar](inventory.md)
  eingeschaltet ist und du es lesen darfst -- siehe
  [Ressourcen](#resources) unten.
- Jeden Kalender mit Farbpunkt, Name und Beschreibung. Ein Klick auf den
  Namen öffnet ihn.
- **Nur Vorstand** bei Kalendern, die nur Vorstand und Benutzer mit vollem
  Zugriff sehen. Andere Benutzer sehen diese Kalender gar nicht.
- **Archiviert** bei archivierten Kalendern. Archivierte Kalender sehen nur
  Vorstand und Benutzer mit vollem Zugriff.

Gibt es noch keine Kalender, sagt die Liste **Noch keine Kalender.**

### Neuer Kalender {#new-calendar}

Erscheint nur für Vorstand und Benutzer mit vollem Zugriff.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name** | Pflicht, bis zu 100 Zeichen, z. B. „Vereinsheim-Belegung“. |
| **Farbe** | Die Farbe des Punkts neben dem Namen. Vorgabe ist Grün. |
| **Beschreibung** | Freiwillig. Erscheint unter dem Namen und auf der Seite des Kalenders. |
| **Nur für Vorstand und Benutzer mit Vollzugriff sichtbar** | Macht daraus einen Kalender **Nur Vorstand**. |
| **Kalender anlegen** | Legt den Kalender an. |

### Einen Kalender bearbeiten {#editing-a-calendar}

Öffne **Bearbeiten** unter dem Namen eines Kalenders (nur Vorstand und
Benutzer mit vollem Zugriff).

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name**, **Farbe**, **Beschreibung** | Wie oben. |
| **Nur für Vorstand und Benutzer mit Vollzugriff sichtbar** | Schaltet den Kalender zwischen „alle“ und „nur Vorstand“ um. Die Änderung erzeugt auch eine neue Abo-Adresse; wer vorher abonniert hat, verliert den Zugriff. |
| **Aktiv (Haken entfernen zum Archivieren)** | Haken entfernen, um den Kalender zu archivieren. Seine Einträge bleiben, neue können nicht hinzugefügt werden, und seine Abo-Adresse funktioniert nicht mehr. Wieder anhaken holt den Kalender zurück. |
| **Neue Abo-Adresse (alte funktionieren nicht mehr)** | Anhaken, wenn jemand, der den Link hatte, den Kalender nicht mehr sehen soll, zum Beispiel nach dem Ausscheiden aus dem Vorstand. |
| **Speichern** | Speichert die Änderungen. |

Einen Kalender löschen geht nicht. Archivier ihn stattdessen, damit sein
Verlauf erhalten bleibt.

## Die Seite eines Kalenders {#a-calendars-page}

![Die Seite eines Kalenders](../assets/screenshots/calendar/custom-detail.png)

Öffnest du einen Kalender aus **Eigene Kalender**, zeigt die Seite Farbe und
Name als Seitentitel, die Beschreibung und die anstehenden Einträge.
**Zurück** führt zu **Eigene Kalender**.

Die Karte **Neuer Eintrag** funktioniert wie die im
[Vereinskalender](#new-entry), ohne das Feld **Art**. Sie erscheint nur mit
Recht *Schreiben* und nur, solange der Kalender aktiv ist. Titel und Ort
dürfen bis zu 255 Zeichen haben; Uhrzeiten müssen gültig sein (hh:mm), sonst
werden sie ignoriert.

Die Liste **Anstehend** zeigt **Datum** (mit Enddatum und Uhrzeiten),
**Titel** (mit Ort und Beschreibung) und ein Papierkorb-Symbol zum Löschen
eines Eintrags (braucht Recht *Löschen*).

Ein archivierter Kalender zeigt **Dieser Kalender ist archiviert: Seine
Einträge bleiben, neue können nicht hinzugefügt werden.**

Die Schaltfläche **Abonnieren (ICS)** (nur bei aktiven Kalendern) zeigt eine
**Private Abo-Adresse (nicht weitergeben)**. Jeder deiner eigenen Kalender
hat seinen eigenen geheimen Link, getrennt vom gemeinsamen Link der
Geburtstags- und Vorstandskalender.

## Ressourcen {#resources}

![Ressourcen](../assets/screenshots/calendar/resources.png)

Eine nur lesende Übersicht der eigenen Gegenstände des Vereins, die
Mitglieder ausleihen können, und wer sie gerade hat. Du erreichst sie über
**Eigene Kalender**; sie funktioniert nur, wenn das Inventarmodul
eingeschaltet ist und du es lesen darfst, weil sie zeigt, wer was
ausgeliehen hat. **Zurück** führt zu **Eigene Kalender**.

Die Liste enthält jeden ausleihbaren Gegenstand im Vereinsbesitz, der nicht
ausgemustert ist. Verwaltet und verliehen werden Gegenstände im Modul
[Inventar](inventory.md), nicht hier.

| Spalte | Was sie zeigt |
|---|---|
| **Gegenstand** | Der Name des Gegenstands (verlinkt ins Inventar) und seine Kategorie. |
| **Status** | Die Verfügbarkeit: **Verfügbar**, **Verliehen** (nichts mehr da) oder bei mehrfach vorhandenen Gegenständen z. B. „2 von 5 verfügbar“. |
| **Derzeit verliehen** | Eine Zeile je offener Ausleihe: „seit 03.11.2026: Erika Muster (1×)“ oder ein Strich, wenn ihn niemand hat. |

Ausleihen in Parcella haben kein geplantes Rückgabedatum; diese Seite zeigt
also nur die aktuelle Lage, keinen Zeitplan für die Zukunft.

Gibt es keine ausleihbaren Gegenstände: **Keine ausleihbaren Gegenstände im
Vereinsbesitz.**

## In einer Kalender-App abonnieren {#subscribing-in-a-calendar-app}

Jeder Kalender hat eine Schaltfläche **Abonnieren (ICS)** mit einer Adresse
(einem „ICS-Link“). In den meisten Kalender-Apps fügst du sie mit einer
Option wie „Kalender abonnieren“, „Kalender per URL hinzufügen“ oder „Aus dem
Internet“ hinzu. Die App prüft die Adresse dann regelmäßig, sodass neue
Einträge von selbst erscheinen. Wie oft sie prüft, hängt von der App ab.

| Kalender | Link | Wer ihn haben darf |
|---|---|---|
| Vereinskalender | Öffentlich | Alle. Sicher für die Vereinswebsite. |
| Geburtstage | Privat, gemeinsames Geheimnis | Nur Personen, die Geburtstage der Mitglieder sehen sollen. |
| Vorstandspräsenz | Privat, gemeinsames Geheimnis | Vorstand und Helfer. |
| Vorstandsabwesenheit | Privat, gemeinsames Geheimnis | Vorstand und Helfer. |
| Jeder der **Eigenen Kalender** | Privat, ein Geheimnis je Kalender | Wer diesen Kalender sehen soll. |

Die Links für Geburtstage, Vorstandspräsenz und Vorstandsabwesenheit nutzen
alle **dasselbe** Geheimnis für deine ganze Installation. Wer einen dieser
Links hat, kann alle drei Feeds lesen, ohne sich anzumelden. Gib sie nur
Personen, denen du vertraust.

!!! warning "Wenn ein privater Link nach außen gelangt"
    Bei **Eigenen Kalendern** hak im Kalender **Neue Abo-Adresse (alte
    funktionieren nicht mehr)** an und speichere. Für die Geburtstags- und
    Vorstandslinks gibt es keine Schaltfläche, um das gemeinsame Geheimnis
    zu ändern.

## Siehe auch {#related}

- [Arbeitsstunden](work-hours.md) -- woher die Arbeitseinsätze im
  Vereinskalender kommen.
- [Mitglieder](members.md) -- Geburtsdaten, Tags und die Einstellung „Kein
  Geschenk“.
- [Inventar](inventory.md) -- ausleihbare Gegenstände und Ausleihen.
- [Gruppen](../administration/groups.md) -- jemandem Kalenderrechte geben.
- [Module ein- und ausschalten](../administration/modules.md)

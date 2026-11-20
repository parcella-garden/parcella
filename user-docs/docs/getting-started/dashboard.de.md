# Dashboard {#dashboard}

Das Dashboard ist die Startseite nach der Anmeldung. Es zeigt die
wichtigsten Zahlen des Vereins auf einen Blick und weist auf Dinge hin, die
Aufmerksamkeit brauchen. Mit **Dashboard** ganz oben in der Seitenleiste
kommst du jederzeit zurück.

!!! info "Wer das nutzen kann"
    Alle, die angemeldet sind. Manche Kacheln erscheinen nur, wenn ihr
    Modul eingeschaltet ist, und einige brauchen zusätzlich Leserecht für
    dieses Modul (siehe unten).

![Dashboard](../assets/screenshots/getting-started/dashboard.png)

Alle Zahlen werden bei jedem Öffnen der Seite neu berechnet.

## Die Kacheln {#the-tiles}

Die Kacheln oben haben eine feste Reihenfolge. Die ersten vier erscheinen
immer, die anderen je nach den Modulen deines Vereins.

| Kachel | Was sie zählt | Wann sie erscheint | Schaltfläche |
|---|---|---|---|
| **Mitglieder** | Große Zahl: aktuelle Mitglieder -- nicht gelöscht, Mitgliedschaft nicht beendet und entweder schon begonnen oder ohne Datum **Mitglied seit**. Darunter: **... aktiv** -- die Mitglieder davon mit einem Datum **Mitglied seit**. Ist bei mindestens einem aktuellen Mitglied ein Geburtsdatum hinterlegt: **Durchschnittsalter ... Jahre**, nur aus diesen Mitgliedern berechnet. | Immer | **Anzeigen** öffnet die Mitgliederliste, gefiltert auf aktive Mitglieder. |
| **Parzellen aktiv** | Parzellen mit dem Status *aktiv*. Darunter in Orange: **... unbesetzt** -- aktive Parzellen ohne aktuellen oder künftigen Pächter (eine Parzelle, deren letztes Pachtverhältnis beendet ist, zählt als unbesetzt; eine mit gekündigtem Pächter oder einem später beginnenden neuen Pächter nicht); oder **alle besetzt**, wenn es keine gibt. | Immer | **Alle anzeigen** öffnet die Parzellenliste. |
| **Gekündigt** | Parzellen mit dem Status *gekündigt*. | Immer | **Anzeigen** öffnet die Parzellenliste, gefiltert auf gekündigte Parzellen. |
| **Gesamtfläche (qm)** | Die Summe der Flächen aller Parzellen, aktiv und gekündigt. Gelöschte Parzellen und Gemeinschaftsflächen zählen nicht. Das ist dieselbe Zahl wie **A-Fläche (Parzellen, qm)** in den [Vereinseinstellungen](../administration/settings.md#areas-sqm). | Immer | -- |
| **Offene Einkaufswünsche** | Anträge, die noch **warten auf Freigabe**. | Modul **Einkaufswünsche** eingeschaltet und du darfst Einkaufswünsche lesen | **Alle anzeigen** |
| **Neue Bewerbungen** | Bewerbungen mit dem Status *neu*, also **noch nicht bearbeitet**. | Modul **Bewerber** eingeschaltet und du darfst Bewerber lesen | **Alle anzeigen** öffnet die Bewerberliste, gefiltert auf neue. |
| **Offene Vorgänge** | Vorgänge **in Bearbeitung**. | Modul **Vorgänge** eingeschaltet und du darfst Vorgänge lesen | **Alle anzeigen** öffnet die offenen Vorgänge. |
| **Offene Support-Anfragen** | **Aktive oder wartende Unterhaltungen im Helpdesk** des Vereins. | Modul **Support (Helpdesk)** eingeschaltet und du darfst es lesen | **Alle anzeigen** |
| **Überfällige Aufgaben** | Aufgaben auf dem Aufgabenboard, deren Fälligkeit überschritten und die nicht erledigt sind. | Modul **Aufgabenboard** eingeschaltet und du hast vollen Zugriff (das Aufgabenboard ist nur für Personen mit vollem Zugriff) | **Alle anzeigen** öffnet das Aufgabenboard mit nur den überfälligen Aufgaben. |
| **Neue Anmeldungen** | Anmeldungen **zu Arbeitseinsätzen** aus den letzten 14 Tagen, für reguläre Einsätze, die noch bevorstehen. Anmeldungen zu einem Einsatz, den jemand als gesehen markiert hat, zählen nicht mehr. | Modul **Pflichtstunden-Verwaltung** eingeschaltet und du darfst Arbeitsstunden lesen | **Alle anzeigen** öffnet **Einsätze & Übersicht**. |

Die Zahlen bei **Offene Einkaufswünsche**, **Neue Bewerbungen**, **Offene
Support-Anfragen**, **Überfällige Aufgaben** und **Neue Anmeldungen** sind
dieselben wie die roten Badges in der Seitenleiste (siehe
[Sich zurechtfinden](navigation.md#badges-things-that-need-attention)). Wie
die Badges sinken sie von selbst, sobald etwas erledigt ist.

## Geburtstage diese Woche {#birthdays-this-week}

Diese Karte erscheint nur, wenn mindestens ein aktuelles Mitglied in den
nächsten sieben Tagen Geburtstag hat, heute eingeschlossen. Sie listet diese
Mitglieder, die nächsten zuerst:

- den Namen des Mitglieds, verlinkt auf seine Mitgliederseite,
- **heute wird ...** bei einem Geburtstag heute, sonst das Datum und
  **wird ...**,
- ein hervorgehobenes Badge **Rund** bei runden Geburtstagen (30, 40,
  50, ...).

Mitglieder ohne hinterlegtes Geburtsdatum erscheinen nicht. Die Karte
erscheint auch bei ausgeschaltetem Modul **Kalender**; ihre Schaltfläche
**Alle anzeigen** führt zur vollständigen Geburtstagsliste im Kalender, die
das Kalendermodul und das Recht dafür braucht.

## Neueste Mitglieder {#recent-members}

Die fünf aktuellen Mitglieder, die zuletzt **in Parcella angelegt** wurden,
rechts mit ihrem Datum **Mitglied seit** (– wenn keines gesetzt ist). Ein
Klick auf einen Namen öffnet das Mitglied. Bei einer frischen Installation
erscheint **Noch keine Mitglieder angelegt.**

**Neues Mitglied** öffnet das Formular für ein neues Mitglied.

## Schnellzugriff {#quick-access}

Abkürzungen für häufige Aufgaben:

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Neues Mitglied anlegen** | Öffnet das Formular für ein neues Mitglied. |
| **Neue Parzelle anlegen** | Öffnet das Formular für eine neue Parzelle. |
| **Mitglieder als CSV exportieren** | Lädt die Mitgliederliste als CSV-Datei herunter, etwa für eine Tabellenkalkulation. |
| **Parzellen als CSV exportieren** | Lädt die Parzellenliste als CSV-Datei herunter. |

Mitglieder und Parzellen anlegen braucht **Schreiben** bei **Mitglieder &
Parzellen**. Ohne dieses Recht antwortet das Formular mit **Du hast keine
Berechtigung dafür**.

## Siehe auch {#related}

- [Mitglieder](../modules/members.md) und [Parzellen](../modules/parcels.md)
- [Sich zurechtfinden](navigation.md)
- [Module ein- und ausschalten](../administration/modules.md)

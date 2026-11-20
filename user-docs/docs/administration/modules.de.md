# Module ein- und ausschalten {#turning-modules-on-and-off}

Nicht jeder Verein nutzt jeden Teil von Parcella. Ein Verein ohne eigene
Wasserversorgung braucht keine Zählerstände; ein Verein ohne Pflichtstunden
braucht keine Arbeitseinsätze. Du entscheidest, welche Module dein Verein
nutzt.

!!! info "Wer das nutzen kann"
    Nur Administratoren. Öffne **Administration → Einstellungen** und klapp
    die Karte **Funktionsbereiche** auf.

Jedes Modul hat einen Schalter, seinen Namen und eine kurze Beschreibung.
Leg die Schalter um, die du ändern willst, und klick auf **Einstellungen
speichern**.

## Was passiert, wenn du ein Modul ausschaltest {#what-happens-when-you-switch-a-module-off}

- Es **verschwindet für alle aus Seitenleiste und Dashboard**, auch für
  Administratoren. (Ausnahme: Die Kachel mit den Geburtstagen dieser Woche
  bleibt auf dem Dashboard, auch wenn der Kalender aus ist.)
- Seine Seiten lassen sich nicht mehr öffnen, auch nicht über ein
  Lesezeichen.
- **Nichts wird gelöscht.** Alle seine Daten bleiben in der Datenbank und
  sind unverändert wieder da, sobald du das Modul wieder einschaltest.
- Gruppenrechte für das Modul bleiben, wie sie sind; nach dem Wiedereinschalten
  haben also dieselben Leute wieder Zugriff.

Ein eingeschaltetes Modul ist für alle mit vollem Zugriff sofort sichtbar.
Andere sehen es erst in der Seitenleiste, wenn eine Gruppe ihnen **Lesen**
dafür gewährt -- siehe [Gruppen](groups.md).

## Die Schalter {#the-switches}

Sie stehen in dieser Reihenfolge auf der Karte.

| Schalter | Was er bewirkt | Standardmäßig an |
|---|---|---|
| **Pflichtstunden-Verwaltung** | Arbeitseinsätze, Patenschaften, Vereinsrollen und die jährliche Pflichtstunden-Auswertung. Siehe [Arbeitsstunden](../modules/work-hours.md). | Ja |
| **Wasserverwaltung** | Wasserzähler, Zählerstände und Verbrauchsauswertungen. Siehe [Wasser und Strom](../modules/metering.md). | Ja |
| **Stromverwaltung** | Stromzähler, Zählerstände und Verbrauchsauswertungen. | Ja |
| **Versicherungsverwaltung** | Sach- und Unfallversicherung je Parzelle, mit Jahresauswertung. Siehe [Versicherungen](../modules/insurance.md). | Ja |
| **Support (Helpdesk)** | Verknüpft die Konversationen deines Helpdesks mit Mitgliedern und dem Aufgabenboard. Wähl das Helpdesk vorher unter [Integrationen](integrations.md#support-helpdesk). Siehe [Support](../modules/support.md). | Nein |
| **Einkaufswünsche** | Vereinsausgaben mit Vier-Augen-Freigabe. Siehe [Einkaufswünsche](../modules/purchase-requests.md). | Ja |
| **Kalender** | Vereinskalender, Geburtstage, Vorstandspräsenz und -abwesenheit, jeweils mit Kalender-Feed. Siehe [Kalender](../modules/calendar.md). | Ja |
| **Inventar** | Alles, was der Verein besitzt, mit Kategorien und Verleih. Siehe [Inventar](../modules/inventory.md). | Ja |
| **Aufgabenboard** | Ein Board „Zu erledigen / In Arbeit / Erledigt“ für die Vereinsarbeit. Nur für Benutzer mit vollem Zugriff (Vorstand, Administratoren und Gruppen mit vollem Zugriff). Siehe [Aufgabenboard](../modules/tasks.md). | Ja |
| **Bewerber** | Personen, die sich um einen freien Garten beworben haben. Siehe [Bewerber](../modules/applicants.md). | Ja |
| **Externe Kontakte** | Lieferanten, Handwerker, Behörden. Siehe [Externe Kontakte](../modules/external-contacts.md). | Ja |
| **Auswertungen** | Vereinszahlen im Zeitverlauf als Diagramme, nur lesend. Siehe [Auswertungen](../modules/reporting.md). | Ja |
| **Notizen** | Notizen mit Kategorien und Schlagworten, auf Wunsch als Dateien in der Cloud. Siehe [Notizen](../modules/notes.md). | Ja |
| **Vorgänge** | Eigene Abläufe Schritt für Schritt. Siehe [Vorgänge](../modules/processes.md). | Ja |
| **MCP-Connector für KI-Clients** | Lässt einen KI-Assistenten (Claude, ChatGPT, ...) **nur die Notizen, die du für die KI freigegeben hast,** durchsuchen, lesen und schreiben, sonst nichts. Braucht ein [API-Token](api-tokens.md) der Art **Nur MCP-Connector**. | Nein |
| **Öffentliche Anmelde-API** | Lässt das Formular der Vereinswebsite Gärtner ohne Anmeldung für Arbeitseinsätze anmelden. Siehe [Integrationen](integrations.md#public-signup-api) und [Für Gärtner](../gardeners/index.md). | Nein |
| **Öffentliche Kontaktformular-API** | Lässt das Kontaktformular der Vereinswebsite eine neue Anfrage in deinem Helpdesk anlegen, statt eine E-Mail zu schicken. | Nein |
| **Öffentliche Bewerbungsformular-API** | Lässt das Bewerbungsformular der Vereinswebsite für Gärten direkt Bewerber anlegen. Das Modul **Bewerber** lässt sich auch ohne nutzen, für Bewerbungen, die du von Hand eingibst. | Nein |
| **Mitteilungen** | Vereinsnachrichten einmal schreiben und für Website, Mitglieder-E-Mail und einen druckbaren Aushang vorbereiten. Siehe [Mitteilungen](../modules/announcements.md). | Nein |
| **Cloud-Speicher** | Ein Cloud-Ordner je Parzelle für Pachtverträge und Unterlagen; außerdem nötig für Anhänge von Eingangsrechnungen, Dokumente von Kontakten, Notizdateien und Cloud-Sicherungen. Wähl den Speicher vorher unter [Integrationen](integrations.md#cloud-storage). | Nein |
| **Finanzen** | Jahresrechnungen je Parzelle, Zahlungen und Buchhaltung. Füll vorher die [Finanzeinstellungen](settings.md#finance-settings) aus. Siehe [Finanzen](../modules/finances/index.md). | Nein |
| **Nextcloud-Deck-Synchronisierung** | Kopiert die Karten eines Nextcloud-Deck-Boards auf das Aufgabenboard und hält sie automatisch aktuell. Richte die Verbindung vorher unter [Integrationen](integrations.md#nextcloud-deck) ein. | Nein |

**Mitglieder** und **Parzellen** haben keinen Schalter: Sie sind der Kern von
Parcella und immer an.

## Warum manche Schalter aus beginnen {#why-some-switches-start-off}

Die Schalter, die in einer neuen Installation aus sind, tun eins davon:

- **Sie öffnen eine Tür zum öffentlichen Internet.** Die drei Schalter
  *Öffentliche … API* lassen jeden, der eure Website besucht, Daten an
  Parcella schicken. Schalte einen nur ein, wenn eure Website das passende
  Formular wirklich hat, und nur den, den du brauchst.
- **Sie speichern Passwörter für andere Dienste** oder lassen Parcella dort
  handeln: Cloud-Speicher, Helpdesk, Nextcloud Deck, die Website-Verbindung
  der Mitteilungen.
- **Sie gehen mit Geld um oder erreichen alle Mitglieder auf einmal:**
  Finanzen und Mitteilungen.
- **Sie geben Daten an ein externes Unternehmen:** Der MCP-Connector gibt
  einem KI-Dienst Zugriff auf die Notizen, die du freigibst.

Es geht nichts kaputt, wenn du sie auslässt. Schalte sie bewusst ein, sobald
du weißt, dass du sie brauchst.

## Siehe auch {#related}

- [Module](../modules/index.md) -- was jedes Modul tut
- [Gruppen](groups.md) -- wer ein eingeschaltetes Modul nutzen darf
- [Integrationen](integrations.md) -- Verbindungen, die mehrere Module
  brauchen

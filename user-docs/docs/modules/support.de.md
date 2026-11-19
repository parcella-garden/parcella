# Support {#support}

Parcella hat kein eigenes Ticketsystem. Dein Verein beantwortet E-Mails und
Kontaktformular-Anfragen in einem Helpdesk -- FreeScout, Zammad, Znuny /
OTRS, osTicket, Zendesk oder Freshdesk --, und das Support-Modul verbindet
dieses Helpdesk mit Parcella: Du siehst, welche Konversation zu welchem
Mitglied und welcher Parzelle gehört, liest die Konversation und machst
daraus eine Karte auf dem Aufgabenboard. Geantwortet wird immer im Helpdesk
selbst.

!!! info "Wer das nutzen kann"
    - Eingeschaltet wird das Modul mit **Support (Helpdesk)** unter
      [Module ein- und ausschalten](../administration/modules.md). Es ist
      **standardmäßig aus**, weil es die Zugangsdaten des Helpdesks
      speichert. Das Helpdesk selbst wählt und verbindet ein Administrator
      unter [Integrationen](../administration/integrations.md).
    - **Support-Konversationen in Parcella:** Vorstandsmitglieder und
      Administratoren sowie Benutzer, deren Gruppe **Lesen** für **Support
      (Helpdesk)** gewährt (siehe [Gruppen](../administration/groups.md)).
      **Schreiben** braucht es, um eine Konversation mit einem Mitglied oder
      einer Parzelle zu verknüpfen.
    - **Aufgabe erstellen:** nur Vorstandsmitglieder und Administratoren
      (oder Benutzer in einer Gruppe mit vollem Zugriff), genau wie beim
      Aufgabenboard selbst.
    - **Alle anderen** bekommen trotzdem einen Link **Support** in der
      Navigation, sobald das Modul an ist und das Helpdesk eine Webadresse
      hat: Er öffnet das Helpdesk direkt in einem neuen Tab.

## Woher die Konversationen kommen {#where-conversations-come-from}

Parcella schaut etwa alle fünf Minuten im Helpdesk nach neuen und
geänderten Konversationen. Es speichert nur einen Querverweis -- Betreff,
Kunde, Status, Zahl der Nachrichten und die Verknüpfungen zu Mitglied,
Parzelle und Aufgabe. Die Nachrichten selbst bleiben im Helpdesk und werden
jedes Mal frisch geholt, wenn du eine Konversation öffnest.

**Mitglieder zuordnen:** Kommt eine Konversation herein, sucht Parcella das
Mitglied, zu dem sie gehört:

1. Wurde dieser Helpdesk-Kunde schon früher einem Mitglied zugeordnet, wird
   dieses Mitglied genommen.
2. Sonst: Hat **genau ein** Mitglied die E-Mail-Adresse des Kunden, wird
   dieses Mitglied automatisch verknüpft.
3. Teilen sich mehrere Mitglieder die Adresse (z. B. ein Paar mit einem
   Postfach) oder hat sie niemand (ein Nachbar, ein Lieferant), bleibt die
   Konversation ohne Mitglied. Du kannst eines von Hand verknüpfen.

Hat das verknüpfte Mitglied genau eine aktuelle Parzelle, wird diese
Parzelle mit verknüpft. Eine Konversation, die ein Mitglied hat -- ob
automatisch oder von dir gesetzt --, wird später nie neu zugeordnet.

Ändert sich der Name eines Mitglieds in Parcella, wird sein Kundeneintrag im
Helpdesk mit umbenannt, wenn das Helpdesk das unterstützt.

**Status:** Jedes Helpdesk benennt seine Zustände anders; Parcella zeigt sie
als `active`, `pending`, `closed`, `spam` oder `deleted`. Geschlossene,
Spam- und gelöschte Konversationen sind in der Liste, im Badge und auf dem
Dashboard ausgeblendet. Wird eine Konversation im Helpdesk wieder geöffnet,
taucht sie mit ihrer Mitgliedsverknüpfung wieder auf.

### Was jedes Helpdesk unterstützt {#what-each-helpdesk-supports}

| Helpdesk | Konversationsliste und Badge | Konversationen lesen | Kontaktformular legt Konversation an | Kundennamen abgeglichen |
|---|---|---|---|---|
| FreeScout | ja | ja | ja | ja |
| Zammad | ja | ja | ja | ja |
| Znuny / OTRS | ja | ja | ja | nein |
| osTicket | nein | nein | ja | nein |
| Zendesk | ja | ja | ja | ja |
| Freshdesk | ja | ja | ja | ja |

Mit osTicket kann Parcella nur Anfragen aus dem Kontaktformular der Website
weitergeben; bearbeitet werden sie allein in osTicket.

Es erscheinen nur Nachrichten, die der Kunde sehen kann -- interne Notizen
bleiben im Helpdesk. Anhänge werden nicht gezeigt; dafür öffnest du die
Konversation im Helpdesk.

## Support-Konversationen {#support-conversations}

![Support-Konversationen](../assets/screenshots/support/list.png)

**Support** in der Navigation öffnet die Liste der offenen Konversationen
des aktiven Helpdesks, die zuletzt aktualisierten zuerst. Das rote Badge
neben **Support** -- und die Kachel **Offene Support-Anfragen** auf dem
[Dashboard](../getting-started/dashboard.md) -- zählt dieselben
Konversationen, ob sie ein Mitglied haben oder nicht.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **In … öffnen** | Öffnet das Helpdesk in einem neuen Tab. Erscheint nur, wenn die Webadresse des Helpdesks eingetragen ist. |
| **Betreff** | Der Betreff der Konversation. Ein Klick irgendwo in die Zeile öffnet die Konversation. |
| **Kunde** | Der Name des Absenders oder seine E-Mail-Adresse. |
| **Mitglied** | Das verknüpfte Mitglied oder „—“. |
| **Status** | `active` oder `pending` (geschlossene werden nicht gelistet). |
| **Nachrichten** | Zahl der Nachrichten, wie zuletzt vom Helpdesk gemeldet. |
| **Aktualisiert** | Wann sich die Konversation im Helpdesk zuletzt geändert hat. |
| **Aufgabe** | Ein Board-Symbol, wenn die Konversation mit einer Aufgabe verknüpft ist. |

Statt der Liste siehst du vielleicht:

- „Es ist noch kein Helpdesk eingerichtet. …“ -- ein Administrator muss
  noch eines unter [Integrationen](../administration/integrations.md)
  wählen.
- „… kann über seine Schnittstelle keine Unterhaltungen auflisten. …“ -- das
  Helpdesk ist osTicket.
- „Noch keine Support-Konversationen.“ -- gerade ist nichts offen.

## Konversationsseite {#conversation-page}

Zeigt eine Konversation, mit ihrem Betreff als Titel.

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Zurück** | Führt zur Liste zurück. |
| **In … öffnen** | Öffnet diese Konversation im Helpdesk -- dort beantwortest du sie. |

### Konversation {#conversation}

Die Nachrichten, die älteste zuerst, jede mit Verfasser und Uhrzeit. Lassen
sie sich nicht laden, erklärt ein Hinweis warum -- das Helpdesk ist nicht
erreichbar, es kann keine Konversationen anzeigen (osTicket) oder „Das
Helpdesk dieser Unterhaltung ist nicht (mehr) eingerichtet.“, wenn der
Verein inzwischen zu einem anderen Helpdesk gewechselt ist. „Es konnten keine
Nachrichten geladen werden.“ heißt, dass das Helpdesk keine geliefert hat.

### Mitglied {#member}

Zeigt das verknüpfte Mitglied (mit Link auf seine Seite) oder „Kein Mitglied
zugeordnet.“.

Mit Schreibrecht wählst du ein Mitglied und klickst auf **Speichern**:

- Mitglieder mit der E-Mail-Adresse des Kunden stehen oben, markiert als
  **vorgeschlagen**. Teilen sich mehrere Mitglieder die Adresse, bittet ein
  Hinweis, das richtige auszuwählen.
- Darunter alle aktuellen Mitglieder.
- **-- keine --** entfernt die Verknüpfung.

Speicherst du ein Mitglied, wird auch die Parzelle neu gesetzt: Hat das
Mitglied genau eine aktuelle Parzelle, wird sie verknüpft, sonst keine.

### Parzelle {#parcel}

Erscheint, sobald ein Mitglied verknüpft ist. Mit Schreibrecht wählst du
eine der aktuellen Parzellen des Mitglieds oder **-- keine --** und klickst
auf **Speichern**.

### Aufgabenboard {#task-board}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Aufgabe öffnen** | Erscheint, wenn die Konversation mit einer Aufgabe verknüpft ist; öffnet die Aufgabe. |
| Liste + **Aufgabe erstellen** | Legt eine neue Karte in der gewählten Liste des [Aufgabenboards](tasks.md) an und verknüpft sie mit der Konversation. Der Titel der Karte ist der Betreff; ihre Beschreibung nennt das Helpdesk, die Nummer der Konversation und, falls verknüpft, das Mitglied. Nur Vorstandsmitglieder und Administratoren. |

Hat das Aufgabenboard noch keine Listen, scheitert das Erstellen mit „Es gibt
noch keine Listen auf dem Aufgabenboard“.

!!! note "Geantwortet wird im Helpdesk"
    Parcella hat absichtlich kein Antwortfeld. Klick auf **In … öffnen** und
    antworte dort; die neue Nachricht erscheint in Parcella, wenn du die
    Konversation das nächste Mal öffnest.

## Das Kontaktformular der Website {#the-website-contact-form}

Hat die Website deines Vereins ein Kontaktformular, kann es über Parcella
direkt eine Konversation im Helpdesk anlegen. Das ist ein eigener Schalter,
**Öffentliche Kontaktformular-API**, ebenfalls standardmäßig aus. Die
Einrichtung steht unter [Integrationen](../administration/integrations.md).

## Siehe auch {#related}

- [Integrationen](../administration/integrations.md) -- das Helpdesk wählen
  und verbinden
- [Aufgabenboard](tasks.md) -- eine Konversation weiterverfolgen
- [Mitglieder](members.md) -- die E-Mail-Adressen für die Zuordnung
- [Dashboard](../getting-started/dashboard.md)

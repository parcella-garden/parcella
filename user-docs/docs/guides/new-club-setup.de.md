# Einen neuen Verein einrichten {#setting-up-a-new-club}

Parcella ist installiert und läuft. Diese Anleitung führt dich von der
allerersten Anmeldung zu einer Installation, mit der der ganze Vorstand
arbeiten kann: ein sicheres Admin-Passwort, die Angaben und das Logo deines
Vereins, die richtige Sprache, nur die Module, die du brauchst, Zugänge für
die anderen Vorstandsmitglieder und -- wenn du magst -- vorher eine
Übungsrunde mit Beispieldaten.

Plane etwa eine Stunde ein. Du brauchst das Administratorkonto, das mit der
Installation kam.

!!! info "Wer das tun kann"
    Alles hier passiert in der **Administration**, die nur Administratoren
    (und Gruppen mit **Zugriff auf den Administrationsbereich**) öffnen
    können. Siehe
    [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md).

## 1. Anmelden und das Admin-Passwort ändern {#1-log-in-and-change-the-admin-password}

1. Öffne Parcella im Browser und melde dich mit dem Administratorkonto aus
   der Installation an.
2. Nutzt das Konto noch das Standardpasswort aus der Einrichtung, öffnet
   Parcella sofort **Passwort ändern** und zeigt: *„Dieses Konto verwendet
   noch das Standardpasswort aus der Ersteinrichtung. Bitte ein neues
   vergeben -- bis dahin bleibt der Rest der Anwendung gesperrt.“*
3. Gib das **Aktuelle Passwort** ein, dann ein **Neues Passwort** und
   **Neues Passwort bestätigen**, und klick auf **Passwort ändern**.

Dein Passwort kannst du jederzeit über das Benutzermenü unten in der
Seitenleiste wieder ändern: **Passwort ändern**.

!!! warning
    Überspring das nicht bei einer Installation, die aus dem Internet
    erreichbar ist. Sonst könnte sich jeder, der das Standardpasswort kennt,
    als Administrator anmelden.

Mehr: [Erste Anmeldung und dein Konto](../getting-started/first-login.md).

## 2. Die Angaben deines Vereins eintragen {#2-enter-your-clubs-details}

1. Öffne in der Seitenleiste **Administration → Einstellungen**. Die Seite
   heißt **Vereinseinstellungen**.
2. Füll in der Karte **Vereinsdaten** **Name des Vereins**, **Straße**,
   **PLZ**, **Ort**, **Vereinsnummer** und **Registergericht** aus. Der Name
   erscheint in den Seitentiteln; der Rest kommt in die Fußzeile von Briefen
   und Rechnungen.
3. Such und hak unter **Vorstandsmitglieder** die Mitglieder an, die gerade
   im Vorstand sind. Wählen kannst du nur Personen, die es schon als
   Mitglieder gibt -- komm darauf nach Schritt 9 oder nach deinem
   [Import](csv-import.md) zurück.
4. Trag unter **Flächen (qm)** die **Gesamtfläche (qm)** der Anlage und,
   falls vorhanden, die **C-Fläche (Stadt, qm)** ein. **A-Fläche (Parzellen,
   qm)** und **B-Fläche (Gemeinschaft, qm)** berechnet Parcella aus deinen
   Parzellen.
5. Klick auf **Einstellungen speichern**. Du siehst *„Einstellungen
   gespeichert.“*

!!! tip
    Die Einstellungsseite ist lang. Mit dem Feld **Einstellungen
    durchsuchen...** oben springst du per Namen zu einem Feld.

## 3. Dein Logo hinzufügen {#3-add-your-logo}

1. Such, immer noch unter **Administration → Einstellungen**, die Karte
   **Branding**.
2. Wähl unter **Vereinslogo** eine PNG-, JPEG-, WebP- oder SVG-Datei mit
   höchstens 2 MB.
3. Klick auf **Einstellungen speichern**.

Das Logo ersetzt das Parcella-Logo auf der Anmeldeseite und in der
Seitenleiste. Um zum Standard zurückzukehren, hak **Logo entfernen (zurück
zum Standard-Symbol)** an und speichere.

## 4. Sprache, Region und Währung wählen {#4-choose-language-region-and-currency}

Das sind absichtlich drei getrennte Einstellungen: Ein Verein kann zum
Beispiel die englische Oberfläche, aber deutsche Zahlen- und Adressformate
nutzen.

1. **Sprache** -- die Sprache der ganzen Installation. Alle Benutzer sehen
   dieselbe.
2. **Region** -- Zahlen- und Adressformat (Tausendertrennzeichen,
   Reihenfolge von PLZ und Ort).
3. **Währung** -- das Symbol und wo es steht („19,99 €“ oder „£19.99“).
4. Klick auf **Einstellungen speichern**.

## 5. Den E-Mail-Versand einrichten {#5-set-up-outgoing-email}

Parcella verschickt Einladungen, Benachrichtigungen, Mitteilungen und
Rechnungen per E-Mail. Ohne Mailserver lassen sich die Einladungen in
Schritt 9 nicht verschicken.

1. Such unter **Administration → Einstellungen** die Karte **E-Mail
   (SMTP)**.
2. Füll **SMTP-Server**, **SMTP-Port**, **SMTP-Benutzer**, **SMTP-Passwort**
   und **Absender-E-Mail** aus -- diese Werte nennt dir dein Mail-Anbieter.
3. Klick auf **Einstellungen speichern**.

Nach dem Speichern zeigt das Passwortfeld nur noch, dass ein Passwort
gesetzt ist; zum Ändern tippst du ein neues ein.

## 6. Module ein- und ausschalten {#6-turn-modules-on-and-off}

Nicht jeder Verein nutzt jeden Bereich. Ein ausgeschaltetes Modul
verschwindet aus der Navigation; seine Daten bleiben und sind wieder da,
wenn du es wieder einschaltest.

1. Such unter **Administration → Einstellungen** die Karte
   **Funktionsbereiche**.
2. Hak die Module an, die dein Verein nutzt, und nimm bei den anderen den
   Haken weg. Unter jedem steht eine kurze Beschreibung.
3. Klick auf **Einstellungen speichern**.

Ein paar Module sind in einer neuen Installation **aus**, weil sie Daten
nach außen schicken oder etwas öffentlich machen: **Finanzen**,
**Mitteilungen**, **Cloud-Speicher**, **Support (Helpdesk)**,
**Nextcloud-Deck-Synchronisierung**, **MCP-Connector für KI-Clients** und
die drei öffentlichen Website-APIs. Schalte sie erst ein, wenn du sie
brauchst.

Mehr: [Module ein- und ausschalten](../administration/modules.md).

## 7. Mit Beispieldaten ausprobieren (freiwillig) {#7-try-things-out-with-sample-data-optional}

Bevor du echte Daten eingibst, kannst du die leere Installation mit
erfundenen Mitgliedern, Parzellen, Zählern, Arbeitseinsätzen und mehr füllen,
dich durchklicken und alles wieder entfernen.

1. Öffne **Administration → Beispieldaten**.
2. Lies **Was hinzugefügt wird**, klick dann auf **Beispieldaten
   hinzufügen** und bestätige.
3. Erkunde die Module. Probier einen Rechnungslauf aus, erfass einen
   Zählerstand, übergib eine Parzelle.
4. Bist du fertig, geh zurück zu **Administration → Beispieldaten**, klick
   auf **Alle Beispieldaten entfernen** und bestätige.

!!! warning "Entferne die Beispieldaten, bevor es richtig losgeht"
    - Beispieldaten lassen sich nur einer frischen Installation
      **hinzufügen**. Sobald es ein echtes Mitglied oder eine echte
      Parzelle gibt, ist die Schaltfläche gesperrt.
    - **Alle Beispieldaten entfernen** löscht genau das, was der Generator
      angelegt hat, und nichts, was du selbst eingetippt hast. Was du beim
      Üben *an* einen Beispieleintrag hängst (einen Zählerstand an einem
      Beispielzähler, eine Zahlung zu einer Beispielrechnung), geht
      vielleicht nicht sauber mit raus. Entferne erst die Beispieldaten und
      gib dann deine echten Daten ein.
    - Beispieldaten legen keine Benutzerkonten an und ändern keine.

Mehr: [Beispieldaten](../administration/sample-data.md).

## 8. Gruppen anlegen {#8-create-groups}

Neue Benutzerkonten bekommen ihre Rechte über **Gruppen**, nicht über eine
feste Rolle. Leg erst die Gruppen an und lade dann Leute in sie ein.

1. Öffne **Administration → Gruppen**.
2. Gib unter **Gruppe anlegen** einen **Namen** (zum Beispiel „Vorstand“)
   und eine **Beschreibung** ein.
3. Hak für den Vorstand **Voller Zugriff auf jedes Modul** an. **Zugriff auf
   den Administrationsbereich** hakst du nur für die an, die auch Benutzer
   und Einstellungen verwalten sollen.
4. Klick auf **Gruppe anlegen**.
5. Für engere Aufgaben legst du weitere Gruppen an und hakst in der
   Rechtetabelle je **Modul** **Lesen**, **Schreiben** und **Löschen** an --
   zum Beispiel „Wasserteam“ mit Lesen und Schreiben für **Wasser** oder
   „Kasse“ mit allen Rechten für **Finanzen**. Klick auf **Speichern**.

!!! tip
    Jeder, der sich anmelden kann, kann Mitglieder und Parzellen immer
    *nachschlagen*. Gruppen erweitern den Zugriff von dort aus; sie nehmen
    ihn nie weg.

Mehr: [Gruppen](../administration/groups.md) und
[Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md).

## 9. Die anderen Vorstandsmitglieder einladen {#9-invite-the-other-board-members}

1. Öffne **Administration → Benutzer** (die Seite heißt
   **Benutzerverwaltung**).
2. Gib unter **Benutzer einladen** die **E-Mail-Adresse** der Person ein und
   hak ihre **Gruppen** an.
3. Klick auf **Einladung senden**.
4. Die Person bekommt eine E-Mail mit einem Link. Auf **Konto einrichten**
   gibt sie ihren **Namen** und ein **Passwort** (mindestens 8 Zeichen) ein
   und klickt auf **Konto anlegen**.

Die Einladung gilt 7 Tage und steht unter **Ausstehende Einladungen**, bis
sie angenommen wird. Von dort kannst du sie mit **Einladung erneut senden**
noch einmal schicken (das verlängert sie auch) oder mit **Einladung
löschen** zurückziehen.

!!! warning
    Die Einladung geht per E-Mail raus; richte also erst **E-Mail (SMTP)**
    ein (Schritt 5). Lässt sie sich nicht verschicken, sagt die Seite das;
    korrigier die Mail-Einstellungen und nimm **Einladung erneut senden**.

Mehr: [Benutzer und Einladungen](../administration/users.md).

## 10. Cloud-Speicher verbinden (freiwillig) {#10-connect-cloud-storage-optional}

Bewahrt dein Verein Pachtverträge und andere Unterlagen in Nextcloud (oder
einem anderen unterstützten Speicher) auf, kann Parcella auf jeder
Parzellenseite einen Dokumentenordner zeigen.

1. Öffne **Administration → Integrationen** und such **Cloud-Speicher
   (Parzellendokumente, Rechnungen, Sicherungen)**.
2. Wähl den **Speicher-Typ** und gib die Verbindungsdaten ein, nach denen er
   fragt. Klick auf **Speichern**, dann auf **Verbindung testen**.
3. Leg weiter unten bei Bedarf die gemeinsamen Ordner fest: **Ordner für
   Eingangsrechnungen**, **Ordner für Dokumente externer Kontakte**,
   **Notizen-Ordner**, **Ordner für Vorgangsdateien**, **Ordner für
   gedruckte Mitteilungen**.
4. Geh zu **Administration → Einstellungen → Funktionsbereiche**, hak
   **Cloud-Speicher** an und klick auf **Einstellungen speichern**.
5. Leg auf der Seite jeder Parzelle in **Dokumente (Cloud-Speicher)** den
   **Ordnerpfad** fest -- eintippen oder **Durchsuchen…** nutzen -- und klick
   auf **Speichern**.

Pfade sind immer relativ zum gewählten Speicher. Parcella legt die Ordner
nicht für dich an und gibt sie nicht frei; das machst du vorher in deiner
Cloud.

Mehr: [Integrationen](../administration/integrations.md).

## 11. Deine echten Daten eingeben oder importieren {#11-enter-or-import-your-real-data}

Leg jetzt deine Parzellen und Mitglieder an -- von Hand unter **Parzellen →
Neue Parzelle** und **Mitglieder → Neues Mitglied** oder auf einen Schlag
aus einer Tabelle: siehe
[Mitglieder und Parzellen importieren](csv-import.md). Ordne dann jedes
Mitglied seiner Parzelle zu (siehe
[Ein neues Mitglied aufnehmen](new-member.md), Schritt 6).

## 12. Deine erste Sicherung machen {#12-make-your-first-backup}

1. Öffne **Administration → Benutzer** und such die Karte
   **Datensicherung**.
2. Klick auf **Sicherung herunterladen** und bewahr die ZIP-Datei an einem
   sicheren Ort auf.

Die Sicherung enthält die Datenbank, hochgeladene Dateien und den
Verschlüsselungsschlüssel. Behandle sie wie die Mitgliederliste selbst.

Mehr: [Backup und Wiederherstellung](../administration/backup.md).

## Siehe auch {#related}

- [Vereinseinstellungen](../administration/settings.md)
- [Module ein- und ausschalten](../administration/modules.md)
- [Benutzer und Einladungen](../administration/users.md)
- [Gruppen](../administration/groups.md)
- [Integrationen](../administration/integrations.md)
- [Beispieldaten](../administration/sample-data.md)
- [Backup und Wiederherstellung](../administration/backup.md)
- [Mitglieder und Parzellen importieren](csv-import.md)

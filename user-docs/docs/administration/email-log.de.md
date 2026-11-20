# E-Mail-Protokoll {#e-mail-log}

Das E-Mail-Protokoll listet jede E-Mail, die Parcella zu verschicken
versucht hat -- Einladungen, Benachrichtigungen, Mitteilungen, Rechnungen,
Anmeldebestätigungen -- und was der Mailserver geantwortet hat. Schau hier
nach, wenn jemand sagt: „Die E-Mail habe ich nie bekommen.“

!!! info "Wer das nutzen kann"
    Nur Administratoren. Öffne **Administration → E-Mail-Protokoll**.

![E-Mail-Protokoll](../assets/screenshots/administration/email-log.png)

## Das Protokoll lesen {#reading-the-log}

Oben erklärt ein kurzer Hinweis die Seite und wie viele Tage Einträge
aufbewahrt werden, mit einem Link **Ändern** zur
[Einstellung](settings.md#email-log).

Die Karte **Ausgehende E-Mails** zeigt die Zahl der gefundenen Einträge und
eine Tabelle, die neuesten zuerst, 50 je Seite:

| Spalte | Was sie zeigt |
|---|---|
| **Datum/Uhrzeit** | Wann Parcella die E-Mail an den Mailserver übergeben hat, in der Zeitzone deines Vereins. |
| **Empfänger** | Die Adresse, an die sie ging. |
| **Betreff** | Die Betreffzeile. Eine Büroklammer heißt, sie hatte Anhänge; fahr mit der Maus darüber, um zu sehen, wie viele. |
| **Status** | **Gesendet** oder **Fehlgeschlagen**. Unter **Fehlgeschlagen** siehst du die Fehlermeldung des Mailservers. |

**Neuere** und **Ältere** unten blättern durch das Protokoll (**Seite … von
…**).

### Was „Gesendet“ und „Fehlgeschlagen“ bedeuten {#what-sent-and-failed-mean}

- **Gesendet** heißt, dein Mailserver hat die E-Mail **angenommen**. Das
  beweist nicht, dass sie angekommen ist: Ist das Postfach voll oder gibt es
  die Adresse nicht mehr, geht die Fehlermeldung an das Absenderpostfach
  deines Vereins, nicht in dieses Protokoll.
- **Fehlgeschlagen** heißt, der Mailserver hat sie sofort abgelehnt oder war
  nicht erreichbar -- zum Beispiel ein falsches Passwort, ein unbekannter
  Empfänger oder gar kein eingerichteter Mailserver.

Scheitern viele E-Mails mit demselben Fehler, prüf die
Mailserver-Einstellungen in den
[Vereinseinstellungen](settings.md#email-smtp).

## Suchen und filtern {#searching-and-filtering}

| Element | Was es bewirkt |
|---|---|
| **Empfänger suchen…** | Zeigt nur E-Mails, deren Empfängeradresse enthält, was du tippst. |
| Statusliste | **Alle Status**, **Gesendet** oder **Fehlgeschlagen**. Eine Änderung filtert sofort. |
| **Filtern** | Wendet die Suche an. |
| **Zurücksetzen** | Erscheint, solange ein Filter aktiv ist; zeigt wieder alles. |

**Noch keine E-Mails protokolliert.** erscheint, wenn nichts passt.

## Wie lange Einträge aufbewahrt werden {#how-long-entries-are-kept}

Empfängeradressen sind personenbezogene Daten; Einträge werden deshalb nach
der Zahl von Tagen automatisch gelöscht, die unter
[Vereinseinstellungen → E-Mail-Protokoll](settings.md#email-log) eingestellt
ist -- 90 Tage, wenn du nichts änderst. Das Protokoll speichert nur
Empfänger, Betreff, Status und Fehler und die Zahl der Anhänge -- nicht den
Text der E-Mail.

## Siehe auch {#related}

- [Vereinseinstellungen](settings.md#email-smtp)
- [Benutzer und Einladungen](users.md)

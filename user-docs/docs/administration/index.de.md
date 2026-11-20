# Administration {#administration}

In der Administration wird deine Parcella-Installation eingerichtet und
gepflegt: wer sich anmelden darf, was jemand tun darf, die Stammdaten des
Vereins, Verbindungen zu anderen Diensten und Sicherungen.

!!! info "Wer das nutzen kann"
    Nur **Administratoren**: Konten mit der älteren Rolle **Administrator**
    oder in einer Gruppe mit **Zugriff auf den Administrationsbereich**.
    Vorstandsmitglieder mit vollem Zugriff auf die Module sehen sie nicht,
    außer sie sind auch Administratoren. Siehe
    [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md).

Du findest sie unten in der Seitenleiste unter **Administration**.

## Die Seiten {#the-pages}

| Eintrag in der Seitenleiste | Seite | Was du dort tust |
|---|---|---|
| **System** | [Systeminfo und Updates](system.md) | Deine Version sehen und ob es ein Update gibt; eine Sicherung herunterladen. |
| | [Backup und Wiederherstellung](backup.md) | Aus einer Sicherung wiederherstellen; automatische Sicherungen in die Cloud planen. |
| **Benutzer** | [Benutzer und Einladungen](users.md) | Leute einladen, Konten bearbeiten, deaktivieren und löschen, Passwörter zurücksetzen. |
| **Gruppen** | [Gruppen](groups.md) | Festlegen, wer was lesen, schreiben und löschen darf. |
| **API-Tokens** | [API-Tokens](api-tokens.md) | Die Tokens aller sehen und widerrufen; Tokens für Integrationskonten anlegen. |
| **Einstellungen** | [Vereinseinstellungen](settings.md) | Name und Adresse des Vereins, Logo, Sprache, Region und Währung, Mailserver, Finanzangaben, Reihenfolge der Navigation und mehr. |
| | [Module ein- und ausschalten](modules.md) | Die Karte **Funktionsbereiche** auf der Einstellungsseite. |
| **Integrationen** | [Integrationen](integrations.md) | Website-Formulare, Website-Entwürfe, Cloud-Speicher, Helpdesk, Nextcloud Deck, Links für Kalender-Feeds. |
| **E-Mail-Protokoll** | [E-Mail-Protokoll](email-log.md) | Prüfen, ob eine E-Mail rausgegangen ist. |
| **Beispieldaten** | [Beispieldaten](sample-data.md) | Eine frische Installation zum Ausprobieren mit Beispieldaten füllen und sie wieder entfernen. |
| **API-Dokumentation (Swagger)** | -- | Die technische Beschreibung der Programmierschnittstelle, für Entwickler. |

## Eine neue Installation einrichten {#setting-up-a-new-installation}

Eine sinnvolle Reihenfolge für eine ganz neue Installation:

1. Melde dich mit dem eingebauten Administratorkonto an und ändere sein
   Passwort -- siehe
   [Erste Anmeldung](../getting-started/first-login.md#the-very-first-login-after-installation).
2. Unter [Vereinseinstellungen](settings.md): Sprache, Region und Währung,
   Vereinsdaten, Logo und den Mailserver (ohne ihn kann Parcella keine
   Einladungen verschicken).
3. Unter [Module ein- und ausschalten](modules.md): Schalte aus, was du
   nicht brauchst, und ein, was du brauchst.
4. Leg [Gruppen](groups.md) für die Aufgaben in deinem Verein an.
5. [Lade](users.md) die anderen Vorstandsmitglieder in diese Gruppen ein.
6. Richte [Sicherungen](backup.md) ein.

Die Anleitung [Einen neuen Verein einrichten](../guides/new-club-setup.md)
geht das zusammen mit dem Eingeben von Mitgliedern und Parzellen durch.

Wie Parcella selbst installiert wird (Server, Docker, Webadresse), steht in
der
[Entwicklerdokumentation](https://github.com/parcella-garden/parcella#install-self-hosting).

# Erste Anmeldung und dein Konto {#first-login-and-your-account}

Diese Seite behandelt alles rund um dein eigenes Konto: wie du eines
bekommst, wie du dich anmeldest und wie du Passwort und Bild änderst.

!!! info "Wer das nutzen kann"
    Alle mit einem Parcella-Konto. Eine öffentliche Registrierung gibt es
    nicht: Ein Konto entsteht erst, wenn ein Administrator dich eingeladen
    hat.

## Ein Konto bekommen: die Einladung {#getting-an-account-the-invitation}

Ein Administrator deiner Installation lädt dich per E-Mail ein (siehe
[Benutzer und Einladungen](../administration/users.md)). Du bekommst eine
E-Mail mit dem Betreff **Einladung zur Parcella** und der Schaltfläche
**Einladung annehmen**. Der Link darin ist **7 Tage** gültig.

!!! tip "Keine E-Mail angekommen?"
    Schau zuerst in den Spam-Ordner. Ist sie dort nicht, bitte den
    Administrator, das [E-Mail-Protokoll](../administration/email-log.md)
    zu prüfen und die Einladung bei Bedarf erneut zu senden. Das erneute
    Senden gibt dem Link weitere 7 Tage; der Link aus der ersten E-Mail
    funktioniert weiter.

### Einladung annehmen {#accept-invitation}

Der Link öffnet die Seite **Konto einrichten**. Unter der Überschrift steht
die Adresse, an die die Einladung ging (**Einladung für** ...). Diese
Adresse wird deine Anmeldung; hier lässt sie sich nicht ändern.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name** | Dein Vor- und Nachname. Andere Vorstandsmitglieder sehen ihn in Listen, bei Aufgaben, Freigaben und im Änderungsverlauf. |
| **Passwort** | Mindestens 8 Zeichen. |
| **Passwort wiederholen** | Dasselbe Passwort noch einmal. Stimmen beide nicht überein, erscheint **Passwörter stimmen nicht überein.** |
| **Konto anlegen** | Legt dein Konto an und meldet dich sofort an. Du landest auf dem [Dashboard](dashboard.md). |

Was du danach siehst, hängt von den Gruppen ab, die der Administrator bei
der Einladung gewählt hat. Hat er keine gewählt, kannst du nur Mitglieder
und Parzellen nachschlagen -- bitte ihn dann, dich einer Gruppe
hinzuzufügen. Siehe [Rollen, Gruppen und Rechte](roles-and-permissions.md).

### Einladung abgelaufen {#invitation-expired}

![Einladung abgelaufen](../assets/screenshots/getting-started/invitation-expired.png)

Du siehst **Einladung abgelaufen** -- *Dieser Einladungslink ist nicht mehr
gültig oder wurde bereits verwendet.* --, wenn:

- seit dem Versand (oder dem letzten erneuten Senden) mehr als 7 Tage
  vergangen sind,
- du mit diesem Link schon ein Konto angelegt hast oder
- der Administrator die Einladung gelöscht oder dieselbe Adresse erneut
  eingeladen hat (nur die neueste Einladung gilt).

Bitte einen Administrator, dich erneut einzuladen. **Zur Anmeldung** führt
zur Anmeldeseite; das hilft nur, wenn du schon ein Konto hast.

## Anmelden {#signing-in}

![Anmeldeseite](../assets/screenshots/getting-started/login.png)

Öffne die Parcella-Adresse deines Vereins im Webbrowser. Die Anmeldeseite
zeigt Logo und Namen deines Vereins (beides legt ein Administrator in den
[Vereinseinstellungen](../administration/settings.md) fest).

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **E-Mail** | Die Adresse, an die deine Einladung ging. Groß- und Kleinschreibung spielen keine Rolle. |
| **Passwort** | Dein Passwort. |
| **Anmelden** | Meldet dich an und öffnet das [Dashboard](dashboard.md). |

Mögliche Meldungen:

| Meldung | Bedeutung |
|---|---|
| **E-Mail oder Passwort falsch.** | Eines von beiden stimmt nicht. Zu deinem Schutz sagt Parcella nicht, welches. |
| **Ihr Konto ist deaktiviert.** | Ein Administrator hat dein Konto abgeschaltet. Deine Daten sind noch da; bitte ihn, es wieder zu aktivieren. |
| **Zu viele fehlgeschlagene Anmeldeversuche. Bitte einige Minuten warten und erneut versuchen.** | Nach wiederholt falschen Passwörtern sperrt Parcella Anmeldeversuche für dieses Konto für etwa 15 Minuten. |

Du bleibst **8 Stunden** angemeldet (sofern der Betreiber deiner
Installation das nicht geändert hat). Danach fragt Parcella erneut nach der
Anmeldung, auch wenn du die ganze Zeit gearbeitet hast.

Zum Abmelden klickst du unten in der Seitenleiste auf **Abmelden**. Tu das
an jedem gemeinsam genutzten oder öffentlichen Computer.

!!! note "Passwort vergessen?"
    Einen Link „Passwort vergessen“ gibt es absichtlich nicht. Frag einen
    Administrator: Er kann dein Passwort zurücksetzen und dir ein
    vorläufiges geben (siehe
    [Benutzer und Einladungen](../administration/users.md#reset-password)).
    Bei der nächsten Anmeldung musst du dann ein neues wählen.

## Die allererste Anmeldung nach der Installation {#the-very-first-login-after-installation}

Beim ersten Start legt Parcella selbst ein Administratorkonto an:

- **E-Mail:** `admin@parcella.local`
- **Passwort:** `admin1234`

Diese Daten stehen in Parcellas Installationsanleitung und sind bei jeder
neuen Installation gleich; jeder könnte sie also benutzen. Deshalb bleibt
dieses Konto gesperrt, bis sein Passwort geändert ist: Nach der Anmeldung
landest du direkt auf **Passwort ändern**, mit dem Hinweis

> Dieses Konto verwendet noch das Standardpasswort aus der
> Ersteinrichtung. Bitte ein neues vergeben -- bis dahin bleibt der Rest
> der Anwendung gesperrt.

Jede andere Seite schickt dich hierher zurück, bis du ein neues Passwort
gespeichert hast.

!!! warning "Das zuerst erledigen"
    Ändere das Passwort sofort, auch auf einer Testinstallation, die aus
    dem Internet erreichbar ist. Ändere dann unter
    [Benutzer und Einladungen](../administration/users.md) Namen und
    E-Mail-Adresse des Kontos auf die einer echten Person, oder lade die
    echten Administratoren ein und arbeite mit deren Konten.

Dieselbe Pflicht zur Änderung gilt, nachdem ein Administrator dein Passwort
zurückgesetzt hat: Das vorläufige Passwort bringt dich nur bis zur Seite
**Passwort ändern**.

## Passwort ändern {#change-password}

![Passwort ändern](../assets/screenshots/getting-started/change-password.png)

Du öffnest sie mit **Passwort ändern** unten in der Seitenleiste. Die Seite
ist dein persönliches Profil: Dort findest du auch deinen Avatar und einen
Link zu deinen API-Tokens.

### Avatar {#avatar}

Dein Avatar ist das kleine runde Bild neben deinem Namen in der
Seitenleiste, in Benutzerlisten und bei Aufgaben. Ohne Bild zeigt Parcella
ein einfaches Personensymbol.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| Dateifeld | Ein Bild wählen: PNG, JPEG oder WebP, höchstens 2 MB. |
| **Hochladen** | Speichert das Bild. Du siehst **Avatar erfolgreich hochgeladen.** Ein falscher Dateityp oder eine zu große Datei wird mit einer Meldung abgelehnt. |
| **Avatar entfernen** | Nur sichtbar, wenn du einen hast. Entfernt ihn wieder. |

### API-Tokens für Integrationen {#api-tokens-for-integrations}

**Verwalten** öffnet **Meine API-Tokens**. Das brauchst du nur, wenn du ein
anderes Programm (zum Beispiel einen KI-Assistenten) mit Parcella verbinden
willst. Siehe [API-Tokens](../administration/api-tokens.md).

### Das Passwort ändern {#changing-the-password}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Aktuelles Passwort** | Dein jetziges Passwort, damit niemand es an einem Computer ändern kann, an dem du angemeldet geblieben bist. |
| **Neues Passwort** | Mindestens 8 Zeichen und anders als das aktuelle. |
| **Neues Passwort bestätigen** | Das neue Passwort noch einmal. |
| **Passwort ändern** | Speichert das neue Passwort. Du siehst **Passwort erfolgreich geändert.** |

Mögliche Fehler: **Aktuelles Passwort ist falsch.**, **Passwörter stimmen
nicht überein.**, **Passwort muss mindestens 8 Zeichen haben.** und **Das
neue Passwort muss sich vom aktuellen unterscheiden.**

Was beim Speichern passiert:

- In diesem Browser bleibst du angemeldet.
- **Überall sonst, wo du angemeldet warst, wirst du abgemeldet** -- auf
  einem anderen Computer, deinem Handy oder in einem Browser, in dem jemand
  anderes dein Konto nutzt. Nutze das, wenn du vermutest, dass jemand dein
  Passwort kennt.
- Alle deine **API-Tokens funktionieren nicht mehr** (sie erscheinen als
  **beendet**). Leg neue an, wenn du sie noch brauchst.

## Sprache {#language}

Parcella zeigt allen in deinem Verein dieselbe Sprache. Eine Sprachwahl je
Benutzer gibt es nicht. Ein Administrator wählt die Sprache in den
[Vereinseinstellungen](../administration/settings.md#language) -- English,
Deutsch, Polski, Čeština, Slovenčina, Français oder Nederlands. Auch die
Anmeldeseite und die Einladungsseiten verwenden diese Sprache.

Zahlen-, Datums- und Währungsformate sind eine eigene Einstellung
(**Region** und **Währung**); ein Verein kann also zum Beispiel englische
Menüs mit deutschen Zahlenformaten nutzen.

## Siehe auch {#related}

- [Sich zurechtfinden](navigation.md)
- [Rollen, Gruppen und Rechte](roles-and-permissions.md)
- [Benutzer und Einladungen](../administration/users.md) -- für Administratoren

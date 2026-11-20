# Benutzer und Einladungen {#users-and-invitations}

Hier entscheidest du, wer sich bei Parcella anmelden kann. Neue Leute werden
per E-Mail eingeladen und legen ihr Passwort selbst fest; du wählst, zu
welchen Gruppen sie gehören.

!!! info "Wer das nutzen kann"
    Nur Administratoren. Öffne **Administration → Benutzer**.

Ein *Benutzer* ist ein Anmeldekonto -- ein Vorstandsmitglied, die Kasse, die
Person, die die Zähler abliest. Das ist nicht dasselbe wie ein
Vereins*mitglied*: Die meisten Gärtner sind Mitglieder, bekommen aber nie ein
Benutzerkonto.

## Benutzerverwaltung {#user-management}

![Benutzerverwaltung](../assets/screenshots/administration/users.png)

Die Seite hat links das Einladungsformular und rechts die Liste der Konten.
Meldungen zu dem, was du gerade getan hast, erscheinen oben.

### Benutzer einladen {#invite-user}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **E-Mail-Adresse** | Die E-Mail-Adresse der neuen Person. Sie wird ihr Anmeldename. |
| **Gruppen** | Hak die Gruppen an, zu denen die Person gehören soll. Ihre Rechte kommen nur aus diesen Gruppen -- siehe [Gruppen](groups.md). Gibt es noch keine Gruppen, siehst du **Noch keine Gruppen vorhanden.** mit einem Link **Eine anlegen**. |
| **Einladung senden** | Schickt eine E-Mail mit einem persönlichen Link. Der Link gilt **7 Tage**. |

Was passiert:

- Die Person bekommt die Einladungs-E-Mail mit einer Schaltfläche
  **Einladung annehmen**. Namen und Passwort wählt sie selbst (siehe
  [Erste Anmeldung](../getting-started/first-login.md#getting-an-account-the-invitation))
  und kommt in die angehakten Gruppen.
- Gehört die Adresse schon zu einem Konto, siehst du **E-Mail bereits
  registriert**.
- Gibt es für die Adresse schon eine ausstehende Einladung, hört die alte
  auf zu funktionieren, und nur die neue zählt.
- Hakst du keine Gruppe an, kann die Person nach dem Annehmen nur Mitglieder
  und Parzellen nachschlagen. Gruppen kannst du später hinzufügen.

!!! warning "E-Mail muss funktionieren"
    Einladungen brauchen einen funktionierenden Mailserver (siehe
    [Vereinseinstellungen](settings.md#email-smtp)). Lehnt der Mailserver
    die E-Mail ab, sagt die Seite das statt **Einladung gesendet**: „Die
    Einladung für … ist gespeichert, aber die E-Mail konnte nicht gesendet
    werden. Prüfe die E-Mail-Einstellungen und das E-Mail-Protokoll und sende
    die Einladung dann erneut.“ Die Einladung bleibt unter **Ausstehende
    Einladungen**; funktionieren die Mail-Einstellungen, nimm **Einladung
    erneut senden**. Das [E-Mail-Protokoll](email-log.md) zeigt den Grund
    des Mailservers.

### Ausstehende Einladungen {#pending-invitations}

Erscheint unter dem Formular, solange Einladungen auf Annahme warten. Jede
Zeile zeigt die Adresse, die angehakten Gruppen (oder **Keine Gruppen
ausgewählt**), **Gültig bis** mit dem Datum und das Badge **ausstehend**.

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Einladung erneut senden** (Kreispfeile) | Schickt die E-Mail noch einmal und gibt dem Link ab heute weitere 7 Tage. Der Link aus der ersten E-Mail funktioniert weiter. Du siehst **Einladung erneut gesendet**. |
| **Einladung löschen** (Papierkorb) | Nach der Bestätigung wird die Einladung entfernt, und ihr Link funktioniert nicht mehr. |

Angenommene Einladungen verschwinden aus der Liste; die Person steht dann
unter **Registrierte Benutzer**.

### Registrierte Benutzer {#registered-users}

| Spalte / Schaltfläche | Was sie zeigt oder bewirkt |
|---|---|
| **Name** | Bild und Name. |
| **E-Mail** | Die Anmeldeadresse. |
| **Gruppen** | Die Gruppen, zu denen das Konto gehört. Ältere Konten ohne Gruppen zeigen ihre Rolle, **Administrator** oder **Vorstand**; sonst **–**. |
| **Status** | **aktiv** oder **inaktiv**. |
| **Bearbeiten** (Stift) | Öffnet [Benutzer bearbeiten](#edit-user). |
| **Deaktivieren** / **Aktivieren** (Schalter) | Schaltet das Konto mit einem Klick aus oder wieder ein. Erscheint nicht bei deinem eigenen Konto, das stattdessen mit **Ich** markiert ist. |

**Deaktivieren** sperrt die Person sofort aus -- auch an jedem Computer, an
dem sie gerade angemeldet ist. Alles, was sie angelegt oder genehmigt hat,
bleibt, mit ihrem Namen daran. Aktivier das Konto wieder, und sie kann sich
mit ihrem alten Passwort anmelden.

Dich selbst kannst du nicht deaktivieren, und auch nicht das letzte Konto,
das den Administrationsbereich öffnen kann.

## Benutzer bearbeiten {#edit-user}

![Benutzer bearbeiten](../assets/screenshots/administration/user-edit.png)

**Abbrechen** oben führt ohne Speichern zur Liste zurück.

### Avatar {#avatar}

Wie im eigenen Profil eines Benutzers: Wähl eine PNG-, JPEG- oder WebP-Datei
mit höchstens 2 MB und klick auf **Hochladen**, oder **Avatar entfernen**, um
ihn zu löschen. Praktisch für Leute, die selbst kein Bild hochladen.

### Benutzer bearbeiten {#edit-user_1}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name** | Pflicht. |
| **E-Mail-Adresse** | Pflicht; sie ist der Anmeldename, sag der Person also Bescheid, wenn du sie änderst. Darf nicht zu einem anderen Konto gehören (**E-Mail bereits registriert**). |
| **Rolle** | Erscheint nur bei älteren Konten, die noch die Rolle **Administrator** oder **Vorstand** haben, mit dem Hinweis *Der Zugriff dieses Kontos basiert auf seiner Rolle, nicht auf einer Gruppenmitgliedschaft.* Hier nicht bearbeitbar. |
| **Änderungen speichern** | Speichert Name und E-Mail. Du siehst in der Liste **Benutzer aktualisiert**. |

### Alte Rolle entfernen {#remove-legacy-role}

Nur bei Konten mit der Rolle **Administrator** oder **Vorstand**. **Alte
Rolle entfernen** nimmt die Rolle weg; ab dann kommen die Rechte des Kontos
nur aus seinen Gruppen, wie bei jedem neueren Konto.

!!! warning "Erst die Gruppen hinzufügen"
    Ohne Gruppe fällt das Konto im Moment des Klicks auf Grundrechte zurück
    (Mitglieder und Parzellen lesen). Steck ein früheres **Administrator**-
    Konto vorher in eine Gruppe mit **Zugriff auf den
    Administrationsbereich**, ein **Vorstand**-Konto in eine Gruppe mit
    **Voller Zugriff auf jedes Modul**. Beim letzten Administrator weigert
    sich Parcella, die Rolle zu entfernen.

### Gruppen {#groups}

Listet jede Gruppe. **Hinzufügen** steckt das Konto in diese Gruppe,
**Entfernen** nimmt es heraus. Die Änderung gilt sofort -- **Änderungen
speichern** ist nicht nötig.

### Gefahrenzone {#danger-zone}

Erscheint nicht, wenn du dein eigenes Konto bearbeitest.

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Deaktivieren** / **Aktivieren** | Wie in der Liste: sperrt die Person sofort aus, nichts wird gelöscht. |
| <a id="reset-password"></a>**Passwort zurücksetzen** | Für jemanden, der sein Passwort vergessen hat. Nach der Bestätigung erzeugt Parcella ein **vorläufiges Passwort** und zeigt es **einmal**, mit einer Schaltfläche **Kopieren**. Gib es der Person (telefonisch, persönlich). Ihr altes Passwort funktioniert nicht mehr, sie wird überall abgemeldet und muss bei der nächsten Anmeldung ein neues Passwort wählen. Ist das Konto deaktiviert, wirst du daran erinnert, es zu aktivieren. |
| **Endgültig löschen** | Entfernt das Konto nach der Bestätigung vollständig. Geht nur bei Konten, die nirgends Spuren hinterlassen haben -- typischerweise ein versehentlich angelegtes, nie benutztes Konto. |

Für dein eigenes Passwort nimm stattdessen **Passwort ändern** in der
Seitenleiste.

Hat eine Person irgendetwas in Parcella getan -- einen Eintrag angelegt,
einen Antrag genehmigt, einen Zählerstand eingetragen --, lässt sich das
Konto nicht mehr löschen, und du siehst einen Hinweis, dass der Benutzer
schon Aktivitäten hat und du ihn stattdessen deaktivieren sollst. So
bleiben die Unterlagen des Vereins vollständig: Auch Jahre später siehst
du, wer was getan hat.

## Siehe auch {#related}

- [Gruppen](groups.md)
- [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md)
- [Erste Anmeldung und dein Konto](../getting-started/first-login.md)
- [API-Tokens](api-tokens.md)

# Gruppen {#groups}

Gruppen entscheiden, was jede Person sehen und ändern darf. Du legst eine
Gruppe für eine Aufgabe in deinem Verein an -- „Vorstand“, „Kasse“,
„Wasserteam“ --, hakst an, was diese Aufgabe braucht, und steckst die
richtigen Leute hinein.

!!! info "Wer das nutzen kann"
    Nur Administratoren. Öffne **Administration → Gruppen**.

Die Gedanken hinter Gruppen -- Lesen, Schreiben und Löschen, voller Zugriff,
der Administrationsbereich -- erklärt
[Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md).
Diese Seite beschreibt den Bildschirm.

![Gruppen](../assets/screenshots/administration/groups.png)

## Gruppe anlegen {#create-group}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name** | Pflicht und muss eindeutig sein (**Eine Gruppe mit diesem Namen existiert bereits**). |
| **Beschreibung** | Freiwillige Notiz, wofür die Gruppe da ist. |
| **Voller Zugriff auf jedes Modul** | Mitglieder der Gruppe dürfen in jedem eingeschalteten Modul alles lesen, ändern und löschen, wie der Vorstand. |
| **Zugriff auf den Administrationsbereich** | Mitglieder der Gruppe dürfen auch die **Administration** öffnen. Das Anhaken schließt vollen Zugriff ein; das Kästchen für vollen Zugriff verschwindet deshalb. |
| **Gruppe anlegen** | Legt die Gruppe an. Du siehst **Gruppe erstellt**. |

Eine neue Gruppe ohne eines der beiden Kästchen gewährt noch nichts. Öffne
sie unten, um ihre Rechte anzuhaken.

## Die Gruppenkarten {#the-group-cards}

Jede Gruppe erscheint als zugeklappte Karte unter dem Formular. Der Kopf
zeigt ihren Namen und ein Badge **Administration** oder **Voller Zugriff**,
wenn sie eins davon gewährt. Ein Klick auf den Kopf klappt die Karte auf.

Die **Papierkorb**-Schaltfläche im Kopf löscht die Gruppe nach deiner
Bestätigung. Ihre Mitglieder verlieren, was die Gruppe ihnen gegeben hat.
Parcella weigert sich, die letzte Gruppe zu löschen, die überhaupt jemandem
Zugriff auf den Administrationsbereich gibt, wenn kein anderes Konto ihn
hat.

### Einstellungen und Rechte {#settings-and-permissions}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Name**, **Beschreibung** | Wie beim Anlegen. |
| **Voller Zugriff auf jedes Modul**, **Zugriff auf den Administrationsbereich** | Wie beim Anlegen. Ist eins davon angehakt, ist die Rechtetabelle ausgeblendet, weil sie nicht gebraucht wird. |
| Rechtetabelle | Eine Zeile je **Modul** mit den Kästchen **Lesen**, **Schreiben** und **Löschen**. Siehe die Liste der Module unten. |
| **Speichern** | Speichert Name, Beschreibung, die beiden Kästchen und die ganze Tabelle. Du siehst **Gruppe aktualisiert**. |

Die Module in der Tabelle: **Mitglieder & Parzellen**, **Arbeitseinsätze**,
**Wasser**, **Strom**, **Versicherung**, **Einkaufswünsche**, **Kalender**,
**Inventar**, **Finanzen**, **Support (Helpdesk)**, **Bewerber**, **Externe
Kontakte**, **Auswertungen**, **Notizen**, **Vorgänge**. Module, die dein
Verein ausgeschaltet hat, stehen trotzdem da; ihre Häkchen wirken, sobald
das Modul eingeschaltet wird.

!!! tip "Lesen kommt zuerst"
    Hak überall **Lesen** an, wo du **Schreiben** oder **Löschen** anhakst.
    Ohne Lesen erscheint das Modul nicht einmal in der Seitenleiste der
    Person.

Aufgabenboard und Mitteilungen stehen nicht in der Tabelle: Sie gibt es
immer nur mit vollem Zugriff.

### Zugewiesene Benutzer {#assigned-users}

Listet die Konten in der Gruppe mit Bild, Name und E-Mail-Adresse.

| Element | Was es bewirkt |
|---|---|
| **×** neben einer Person | Nimmt sie sofort aus der Gruppe (**Benutzer entfernt**). |
| **Benutzer hinzufügen...** + **Hinzufügen** | Ein Konto auswählen und hinzufügen (**Benutzer hinzugefügt**). |

Die Liste **Benutzer hinzufügen...** bietet nur Konten an, die ihre Rechte
über Gruppen bekommen. Ältere Konten mit der Rolle **Administrator** oder
**Vorstand** haben schon vollen Zugriff und werden hier nicht angeboten;
willst du sie auf Gruppen umstellen, füg sie über ihre Seite
[Benutzer bearbeiten](users.md#edit-user) hinzu. Sind alle infrage kommenden
Konten schon in der Gruppe, siehst du statt der Liste einen kurzen Hinweis;
gibt es gar keine, einen Link **Jetzt einladen**.

Änderungen an Rechten wirken beim nächsten Klick der Person -- sie muss sich
nicht neu anmelden.

## Beispiel-Einrichtung {#example-set-up}

| Gruppe | Angehakt |
|---|---|
| Administratoren | **Zugriff auf den Administrationsbereich** |
| Vorstand | **Voller Zugriff auf jedes Modul** |
| Kasse | Finanzen: Lesen, Schreiben, Löschen. Mitglieder & Parzellen: Lesen, Schreiben. Einkaufswünsche: Lesen. Versicherung: Lesen. |
| Ableseteam | Wasser: Lesen, Schreiben. Strom: Lesen, Schreiben. |
| Team Arbeitseinsätze | Arbeitseinsätze: Lesen, Schreiben. Kalender: Lesen. |

Eine Person kann in mehreren Gruppen sein; ihre Rechte addieren sich.

## Siehe auch {#related}

- [Benutzer und Einladungen](users.md)
- [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md)
- [Module ein- und ausschalten](modules.md)

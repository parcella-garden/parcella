# Sich zurechtfinden {#finding-your-way-around}

Jede Seite in Parcella hat denselben Rahmen: links eine grüne
**Seitenleiste** mit der Navigation und über der Seite eine weiße
**Kopfleiste** mit dem Seitentitel und den Schaltflächen für diese Seite.

!!! info "Wer das nutzen kann"
    Alle, die angemeldet sind. Welche Einträge *Sie* sehen, hängt von den
    Modulen ab, die Ihr Verein eingeschaltet hat, und von Ihren Rechten --
    siehe [Warum Einträge erscheinen und verschwinden](#why-entries-appear-and-disappear).

![Seitenleiste und Kopfleiste](../assets/screenshots/getting-started/navigation.png)

## Die Seitenleiste {#the-sidebar}

Von oben nach unten enthält die Seitenleiste:

1. **Name und Logo Ihres Vereins**, darunter das Wort **Verwaltung**.
2. **Die Navigationseinträge** -- einer je Modul.
3. **Administration** -- nur für Administratoren, immer ganz unten in der
   Liste.
4. **Den Fußbereich** mit Ihrem eigenen Konto.

### Einzelne Einträge und Gruppen {#single-entries-and-groups}

Kleinere Module sind ein einzelner Link, zum Beispiel **Mitglieder**,
**Parzellen**, **Inventar** oder **Notizen**. Ein Klick öffnet das Modul.

Größere Module sind eine **Gruppe**: eine Überschrift in Großbuchstaben mit
einem kleinen Pfeil. Ein Klick auf die Überschrift klappt ihre Seiten auf:

| Gruppe | Seiten darin |
|---|---|
| **Arbeitseinsätze** | **Einsätze & Übersicht**, **Jahresauswertung**, **Patenschaften**, **Stundenübertragung**, **Aufgaben** |
| **Wasser** | **Übersicht**, **Zählpunkte**, **Ablesung**, **Auswertung**, **Konfiguration** |
| **Strom** | **Übersicht**, **Zählpunkte**, **Ablesung**, **Auswertung**, **Konfiguration** |
| **Versicherungen** | **Übersicht**, **Parzellen**, **Konfiguration**, **Auswertung** |
| **Kalender** | **Vereinskalender**, **Geburtstage**, **Vorstandspräsenz**, **Vorstandsabwesenheit**, **Eigene Kalender** |
| **Finanzen** | **Übersicht**, **Ausgangsrechnungen**, **Mahnungen**, **Eingangsrechnungen** |
| **Administration** | **System**, **Benutzer**, **Gruppen**, **API-Tokens**, **Einstellungen**, **Integrationen**, **E-Mail-Protokoll**, **Beispieldaten**, **API-Dokumentation (Swagger)** |

Es ist **immer nur eine Gruppe offen**: Wenn Sie eine Gruppe öffnen, klappt
die vorher offene zu, damit die Seitenleiste kurz bleibt. Die Gruppe mit
der Seite, auf der Sie gerade sind, öffnet sich immer von selbst. Sonst
merkt sich Ihr Browser, welche Gruppe Sie zuletzt geöffnet haben.

Die aktuelle Seite ist mit einem hellen Balken am linken Rand markiert.

**API-Dokumentation (Swagger)** öffnet die technische Beschreibung von
Parcellas Programmierschnittstelle in einem neuen Browser-Tab. Sie ist für
Leute gedacht, die andere Software anbinden; alle anderen können sie
ignorieren.

### Badges: was Aufmerksamkeit braucht {#badges-things-that-need-attention}

Einige Einträge zeigen eine kleine rote Zahl. Sie sagt, wie viele Dinge
dort warten. Fahren Sie mit der Maus darüber, um zu sehen, was gezählt
wird.

| Eintrag | Das Badge zählt |
|---|---|
| **Arbeitseinsätze** und **Einsätze & Übersicht** | Neue Anmeldungen zu kommenden Arbeitseinsätzen aus den letzten 14 Tagen, die noch niemand als gesehen markiert hat. |
| **Einkaufswünsche** | Anträge, die noch auf eine Entscheidung warten. |
| **Bewerber** | Neue Bewerbungen, die sich noch niemand angesehen hat. |
| **Support** | Offene Konversationen (aktiv oder wartend) im Helpdesk des Vereins. |
| **Aufgabenboard** | Aufgaben, deren Fälligkeit überschritten und die nicht erledigt sind. |

Ein Badge verschwindet von selbst, sobald die Sache erledigt ist -- zum
Beispiel wenn der Einkaufswunsch freigegeben oder abgelehnt oder die
Aufgabe erledigt ist. Ein „als gelesen markieren“ gibt es nicht. Dieselben
Zahlen erscheinen als Kacheln auf dem [Dashboard](dashboard.md).

### Der Fußbereich: Ihr Konto {#the-footer-your-account}

Unten in der Seitenleiste sehen Sie Ihren Avatar und Namen und darunter die
Gruppen, denen Sie angehören (oder **Administrator** / **Vorstand** bei
älteren Konten, die statt Gruppen eine Rolle haben -- siehe
[Rollen, Gruppen und Rechte](roles-and-permissions.md)).

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Passwort ändern** | Öffnet Ihr Profil: Passwort, Avatar und API-Tokens. Siehe [Erste Anmeldung und Ihr Konto](first-login.md#change-password). |
| **Abmelden** | Meldet Sie ab und führt zur Anmeldeseite zurück. |

## Die Kopfleiste {#the-top-bar}

Die Kopfleiste zeigt links den Titel der aktuellen Seite. Rechts stehen die
Aktionen dieser Seite, etwa **Neues Mitglied**, ein Export oder eine
Zurück-Schaltfläche. Die Kopfleiste bleibt sichtbar, wenn Sie in einer
langen Liste nach unten scrollen.

## Warum Einträge erscheinen und verschwinden {#why-entries-appear-and-disappear}

Ein Eintrag wird nur angezeigt, wenn **beides** zutrifft:

1. **Das Modul ist eingeschaltet** für Ihren Verein. Administratoren
   schalten Module unter
   [Module ein- und ausschalten](../administration/modules.md) ein und
   aus. Ein ausgeschaltetes Modul verschwindet für alle -- seine Daten
   bleiben erhalten und sind wieder da, wenn das Modul wieder
   eingeschaltet wird.
2. **Sie dürfen es lesen.** Vorstandsmitglieder und Administratoren sehen
   jedes eingeschaltete Modul. Alle anderen sehen **Mitglieder** und
   **Parzellen** sowie die Module, für die eine ihrer Gruppen **Lesen**
   erlaubt. Siehe [Rollen, Gruppen und Rechte](roles-and-permissions.md).

Einige Einträge folgen einer eigenen Regel:

- **Aufgabenboard** und **Mitteilungen** sehen nur Personen mit vollem
  Zugriff (Vorstandsmitglieder, Administratoren oder eine Gruppe mit
  **Voller Zugriff auf jedes Modul**). Gruppen können sie nicht einzeln
  freigeben.
- **Support**: Mit Leserecht für **Support (Helpdesk)** bekommen Sie
  Parcellas eigene Liste der Konversationen. Ohne dieses Recht erscheint
  der Eintrag trotzdem, wenn der Helpdesk Ihres Vereins eine Webadresse
  hat; er öffnet dann den Helpdesk selbst in einem neuen Tab.
- **Administration** sehen nur Administratoren.

Öffnen Sie eine Seite, die Sie nicht sehen dürfen -- über ein Lesezeichen
oder einen Link von Kollegen --, erscheint die Meldung **Sie haben keine
Berechtigung dafür**. Die Seite eines ausgeschalteten Moduls antwortet mit
einer „nicht gefunden“-Seite: „Dieser Funktionsbereich ist in diesem Verein
deaktiviert.“

### Die Reihenfolge der Einträge {#the-order-of-the-entries}

Ihr Verein legt die Reihenfolge der Einträge fest. Ein Administrator stellt
sie in den [Vereinseinstellungen](../administration/settings.md#navigation-order)
ein. Die Reihenfolge ist für alle gleich.

## Tastenkürzel für Detailseiten {#keyboard-shortcut-for-detail-pages}

Auf Detailseiten mit den Schaltflächen **Vorherige** und **Nächste** --
Mitglieder, Parzellen, Zählpunkte, die Versicherungsseite einer Parzelle
und externe Kontakte (dort **Zurück** und **Weiter**) -- springen
**Strg + ←** und **Strg + →** zum vorherigen und nächsten Datensatz, genau
wie diese Schaltflächen. Während Sie in einem Feld tippen, tut das Kürzel
nichts.

!!! note "Mac-Nutzer"
    Auf dem Mac wechseln Ctrl + Pfeiltasten meist zwischen Schreibtischen
    („Spaces“); das System fängt das Kürzel ab, bevor Parcella es sieht.
    Nutzen Sie dann die Schaltflächen auf der Seite oder schalten Sie das
    Systemkürzel ab.

## Auf dem Handy oder kleinen Tablet {#on-a-phone-or-small-tablet}

Auf schmalen Bildschirmen ist die Seitenleiste ausgeblendet, um Platz für
die Seite zu schaffen.

- Tippen Sie auf die Schaltfläche **☰** oben links in der Kopfleiste, um
  die Seitenleiste einzublenden.
- Tippen Sie auf einen Eintrag, um dorthin zu gehen; die Seitenleiste
  schließt sich von selbst.
- Um sie zu schließen, ohne irgendwohin zu gehen, tippen Sie auf die
  abgedunkelte Seite daneben oder drücken auf einer Tastatur **Esc**.

Schaltflächen und Eingabefelder sind auf Touchscreens etwas größer, und
Reihen von Filter-Schaltflächen brechen auf mehrere Zeilen um, statt über
den Rand zu laufen. Breite Tabellen lassen sich mit dem Finger seitlich
scrollen.

## Siehe auch {#related}

- [Dashboard](dashboard.md)
- [Rollen, Gruppen und Rechte](roles-and-permissions.md)
- [Module ein- und ausschalten](../administration/modules.md)

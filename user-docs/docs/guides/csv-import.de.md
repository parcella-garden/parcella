# Mitglieder und Parzellen importieren {#importing-members-and-parcels}

Führt dein Verein seine Mitglieder-, Parzellen- oder Zählerliste schon in
einer Tabelle, musst du nicht alles neu eintippen. Speichere die Tabelle als
CSV-Datei, lade sie hoch, sag Parcella, welche Spalte was ist, und
importiere.

Das funktioniert genauso für **Parzellen**, **Mitglieder**, **Zählpunkte**,
**Zählerstände** und **externe Kontakte**. Diese Anleitung geht sie in der
Reihenfolge durch, die für eine neue Installation sinnvoll ist.

!!! info "Wer das tun kann"
    Mitglieder und Parzellen importieren braucht das Recht **Schreiben** für
    **Mitglieder & Parzellen**; Zählpunkte und Zählerstände brauchen
    Schreiben für **Wasser** oder **Strom**; externe Kontakte brauchen
    Schreiben für **Externe Kontakte**. Vorstandsmitglieder und
    Administratoren haben alle diese Rechte.

!!! warning "Lade vorher eine Sicherung herunter"
    Ein Import schreibt viele Einträge auf einmal, und es gibt kein
    „Rückgängig“. Öffne **Administration → Benutzer** und klick auf
    **Sicherung herunterladen**, bevor du anfängst. Siehe
    [Backup und Wiederherstellung](../administration/backup.md).

## Wie jeder Import funktioniert {#how-every-import-works}

Alle fünf Importe haben dieselben zwei Schritte.

1. **Hochladen.** Klick auf der Listenseite auf **CSV Import** (bei externen
   Kontakten: **CSV-Import**), wähl die Datei und klick auf **Importieren**.
   Noch wird nichts gespeichert.
2. **CSV-Spalten zuordnen.** Parcella zeigt eine Tabelle: eine Spalte je
   Spalte deiner Datei, mit deiner Überschrift oben und den ersten fünf
   Datenzeilen darunter. Über jeder Spalte ist ein Auswahlfeld. Parcella hat
   das passende Feld schon aus der Überschrift erraten (deutsche und
   englische Überschriften gehen beide, zum Beispiel „Nachname“ oder „Last
   name“). Prüf jedes Auswahlfeld, korrigier die falschen und setz Spalten,
   die du nicht willst, auf **— Ignorieren —**. Klick dann auf
   **Importieren**.

Danach bist du zurück auf der Listenseite mit einer kurzen
Zusammenfassung: wie viele Zeilen angelegt, aktualisiert oder übersprungen
wurden, und die Gründe für die ersten übersprungenen Zeilen.

### Wie deine Datei aussehen sollte {#what-your-file-should-look-like}

- **Die erste Zeile enthält die Spaltenüberschriften.** Jede Zeile darunter
  ist ein Eintrag. Die Überschriften müssen nicht genau passen -- du ordnest
  sie in Schritt 2 zu.
- **Semikolon oder Komma** zwischen den Spalten: Parcella erkennt, welches
  deine Datei nutzt.
- **UTF-8 ist am besten.** Die meisten Tabellenprogramme bieten beim
  Speichern „CSV UTF-8“ an. Excels einfaches „CSV“ (Windows/ANSI) geht auch:
  Umlaute und Akzente kommen so oder so durch.
- **Daten** als `2026-03-15` oder `15.03.2026` (auch `15.03.26`).
- **Dezimalzahlen** mit Komma oder Punkt: `312,5` und `312.5` gehen beide.
  Bankbeträge und Zählerstände dürfen auch Tausendertrennzeichen haben, auf
  deutsche oder englische Art: `12.345,6` und `12,345.6`.
- **Mehrere Werte in einer Zelle** (E-Mail-Adressen, Telefonnummern, Tags)
  werden durch Semikolon getrennt. Dein Tabellenprogramm setzt beim
  Speichern Anführungszeichen um so eine Zelle -- das ist in Ordnung.

!!! tip "Mit einem Export beginnen"
    Die einfachste Vorlage ist der eigene Export von Parcella. Jede Liste mit
    Import hat auch **CSV Export**. Exportier die (noch leere oder mit
    Beispieldaten gefüllte) Liste, füll die Datei in deinem Tabellenprogramm
    aus und importier sie wieder: Die Überschriften passen dann ohne
    Zuordnungsarbeit.

## 1. Parzellen {#1-parcels}

Importier zuerst die Parzellen. Mitglieder, Zählpunkte und Zählerstände
verweisen über ihre Gartennummer auf Parzellen.

1. Öffne **Parzellen** und klick auf **CSV Import**.
2. Wähl deine Datei und klick auf **Importieren**.
3. Ordne auf **CSV-Spalten zuordnen** mindestens die **Gartennummer** zu.
   Die anderen Felder sind freiwillig.
4. Klick auf **Importieren**. Die Zusammenfassung lautet etwa *„24
   importiert, 0 übersprungen“*.

| Feld | Was Parcella erwartet |
|---|---|
| **Gartennummer** | Pflicht. Wird in Großbuchstaben gespeichert („g12“ wird „G12“). |
| **Fläche (qm)** | Eine Zahl, Komma oder Punkt als Dezimaltrenner. Alles andere bleibt leer. |
| **Breitengrad** / **Längengrad** | Freiwillige GPS-Position in Dezimalgrad (z. B. `51,339695`). |
| **Status** | `ACTIVE`, `TERMINATED`, `COMMUNAL` oder `DELETED` (Groß- oder Kleinschreibung). Leer oder alles andere heißt aktiv. |
| **Notizen** | Freitext. |

!!! warning "Bestehende Parzellen werden übersprungen, nicht aktualisiert"
    Gibt es eine Gartennummer schon in Parcella, wird diese Zeile
    **übersprungen**, und die bestehende Parzelle bleibt genau, wie sie ist.
    Bestehende Parzellen änderst du von Hand. Zeilen ohne Gartennummer
    werden ignoriert und in der Zusammenfassung getrennt gezählt.

Der Parzellenimport ordnet **keine** Pächter zu. Der Parzellenexport hat
eine Spalte mit den Namen der Pächter, aber der Import ignoriert sie --
siehe Schritt 3 unten.

## 2. Mitglieder {#2-members}

1. Öffne **Mitglieder** und klick auf **CSV Import**.
2. Wähl deine Datei und klick auf **Importieren**.
3. Ordne auf **CSV-Spalten zuordnen** mindestens **Vorname** und
   **Nachname** zu. Ohne beide bricht der Import mit der Bitte ab, beide
   Spalten zuzuordnen.
4. Klick auf **Importieren**. Die Zusammenfassung lautet etwa *„80 neu
   importiert, 0 aktualisiert“*.

| Feld | Was Parcella erwartet |
|---|---|
| **Vorname**, **Nachname** | Pflicht. Eine Zeile, in der eins davon leer ist, wird übersprungen. |
| **Strasse**, **PLZ**, **Ort** | Freitext. |
| **Geburtsdatum** | Ein Datum (siehe oben). Hilft auch, zwei Mitglieder mit gleichem Namen zu unterscheiden. |
| **IBAN** | Freitext, nicht geprüft. |
| **Member seit**, **Member bis** | Daten. Ein leeres **Member bis** heißt aktives Mitglied. |
| **E-Mail-Benachrichtigungen** | „No“, „Nein“, „false“ oder „0“ heißt, das Mitglied möchte **keine** Vereinsinformationen per E-Mail; alles andere Ausgefüllte heißt ja. Eine leere Zelle oder eine nicht zugeordnete Spalte heißt bei einem neuen Mitglied ja und bei einem bestehenden „unverändert“. |
| **E-Mail-Adressen** | Eine oder mehrere, durch Semikolon getrennt. Die erste wird die Hauptadresse. |
| **Telefonnummern** | Eine oder mehrere, durch Semikolon getrennt. Die erste wird die Hauptnummer. |
| **Notizen** | Freitext. |

**Bestehende Mitglieder zuordnen.** Für jede Zeile sucht Parcella ein
bestehendes Mitglied mit gleichem Vor- und Nachnamen -- und, wenn die Zeile
ein Geburtsdatum hat, mit gleichem Geburtsdatum. Findet es genau eins,
**aktualisiert** es dieses Mitglied, statt ein zweites anzulegen. Haben
mehrere Mitglieder diesen Namen, wählen die E-Mail-Adressen und
Telefonnummern der Zeile das richtige; passt die Zeile dann immer noch auf
mehr als eins, wird sie übersprungen und in der Zusammenfassung genannt.
E-Mail oder Telefon allein ordnen nie ein Mitglied mit anderem Namen zu.

Eine Aktualisierung ändert nur, was die Zeile enthält: Eine Spalte auf **—
Ignorieren —** oder eine leere Zelle lässt den gespeicherten Wert in Ruhe. Du
kannst also nur die Adressen mit einer Datei aktualisieren, die nur Namen und
Adressen enthält. E-Mail-Adressen und Telefonnummern werden bei einer
Aktualisierung nie geändert; sie kommen nur bei neuen Mitgliedern dazu.

Tags, Parzellenzuordnungen und die Einstellung **Möchte keine
Geburtstagsgeschenke** gehören nicht zum Import. Der Export enthält zwar
Spalten **Parzellen** und **Tags**, aber der Import ignoriert sie.

## 3. Mitglieder ihren Parzellen zuordnen {#3-assign-members-to-their-parcels}

Für Pachtverhältnisse gibt es keinen Import. Ordne sie von Hand zu, sobald
Mitglieder und Parzellen existieren:

1. Öffne eine Parzelle unter **Parzellen**.
2. Tipp unter **Aktuelle Pächter** den Namen des Mitglieds in **Mitglied
   wählen…** und wähl es aus der Liste.
3. Gib bei Bedarf das Datum ein, an dem das Pachtverhältnis begann.
4. Lass **Als Rechnungsadresse verwenden** bei dem Pächter angehakt, der die
   Rechnungen der Parzelle bekommen soll.
5. Klick auf **Zuordnen**.

Bei vielen Parzellen bringt dich die Schaltfläche **Nächste** oben auf der
Parzellenseite direkt zur nächsten.

Mehr: [Parzellen](../modules/parcels.md).

## 4. Zählpunkte {#4-metering-points}

Zählpunkte sind die Wasser- und Stromanschlüsse (Hauptzähler, einer je
Parzelle, Vereinsanschlüsse). Wasser und Strom werden getrennt importiert,
jedes in seinem eigenen Menü.

1. Öffne **Wasser → Zählpunkte** (oder **Strom → Zählpunkte**) und klick auf
   **CSV-Import**.
2. Wähl deine Datei und klick auf **Importieren**.
3. Ordne die Spalten zu und klick auf **Importieren**. Mindestens eine
   Spalte muss zugeordnet sein.

| Feld | Was Parcella erwartet |
|---|---|
| **Typ** | `PARCEL`, `MAIN_METER` oder `CLUB`. Ordnest du diese Spalte gar nicht zu, gilt jede Zeile als Parzellenanschluss. Ordnest du sie zu, wird eine Zeile mit leerem oder unbekanntem Typ übersprungen („ungültiger Typ“). |
| **Parzellennummer** | Pflicht bei Parzellenanschlüssen; muss zu einer bestehenden Gartennummer passen, sonst wird die Zeile übersprungen („Parzelle nicht gefunden“). |
| **Bezeichnung** | Der Name eines Hauptzählers oder Vereinsanschlusses, z. B. „Vereinsheim“. |
| **Zählernummer** | Die auf dem Zähler aufgedruckte Nummer. |
| **Eingebaut am** | Ein Datum. |
| **Geeicht bis** | Nur ein **Jahr**, z. B. `2031`. |
| **Anfangsstand** | Der Stand beim Einbau des Zählers. Leer heißt 0. |
| **Faktor** | Meist leer (= 1). Für Zähler, die nur einen Bruchteil des echten Werts zeigen, z. B. `20`. Muss größer als 0 sein. |

Der Import **legt** Zählpunkte nur **an**. Eine Parzelle, die für dieses
Medium schon einen Zählpunkt hat, oder ein Hauptzähler bzw.
Vereinsanschluss mit derselben Bezeichnung wird als „bereits vorhanden“
übersprungen -- denselben Export zweimal zu importieren, schadet also nicht.
Neue Zählpunkte beginnen immer eingeschaltet.

!!! note
    **Geeicht bis** ist ein Jahr. Ein Datum in dieser Spalte (`30.06.2027`,
    `2027-06`, `06/2027`) geht auch: Parcella nimmt das Jahr daraus. Eine
    Zeile, deren Wert keine vierstellige Jahreszahl hat (`06/27`, `bald`),
    wird mit „„Geeicht bis“ ist keine Jahreszahl“ übersprungen; die anderen
    Zeilen werden importiert.

Mehr: [Wasser und Strom](../modules/metering.md).

## 5. Zählerstände {#5-meter-readings}

Zählerstände kommen zu schon bestehenden Zählpunkten; der Import legt nie
einen Zählpunkt an.

1. Öffne **Wasser → Ablesung** (oder **Strom → Ablesung**) und klick auf
   **CSV-Import**.
2. Wähl deine Datei und klick auf **Importieren**.
3. Ordne die Spalten zu. Hat deine Datei keine Jahresspalte oder lassen
   einige Zeilen sie leer, gib das Jahr in **Standardjahr (optional)** ein.
4. Klick auf **Importieren**.

| Feld | Was Parcella erwartet |
|---|---|
| **Typ** | Wie bei den Zählpunkten. Nicht zugeordnet = jede Zeile ist ein Parzellenanschluss. |
| **Parzellennummer** / **Bezeichnung** | Finden den Zählpunkt, genauso wie oben. |
| **Zählernummer** | Freiwillige Gegenprobe. Passt sie nicht zum gerade eingebauten Zähler, wird die Zeile übersprungen („Zählernummer stimmt nicht überein“) -- sie gehört wahrscheinlich zu einem inzwischen getauschten Zähler. |
| **Jahr** | Das Jahr, zu dem der Stand gehört. Hat Vorrang vor **Standardjahr (optional)**. |
| **Datum** | Der Tag, an dem abgelesen wurde. Pflicht. |
| **Zählerstand** | Der Wert auf der Anzeige. Pflicht. |
| **Notiz** | Freitext. |

Parcella errät das Jahr nie aus dem Datum. Ein im Januar abgelesener Stand
kann noch zur Abrechnung des Vorjahres gehören; du sagst also, welches Jahr
es ist.

Eine Datei darf mehrere Jahre enthalten. Hat ein Zählpunkt für dieses Jahr
schon einen Stand, **ersetzt** der Import ihn.

Ein Stand, der unplausibel aussieht -- zum Beispiel kleiner als der
vorherige --, wird trotzdem gespeichert. Die Zusammenfassung zeigt dann eine
eigene Warnung mit den betroffenen Zeilen, damit du sie prüfen kannst.

Mehr: [Zählerstände erfassen](meter-readings.md).

## 6. Externe Kontakte {#6-external-contacts}

Lieferanten, Handwerker und Behörden, wenn du das Modul **Externe Kontakte**
nutzt.

1. Öffne **Externe Kontakte** und klick auf **CSV-Import**.
2. Wähl deine Datei und klick auf **Importieren**.
3. Ordne auf **Spalten zuordnen** die Spalten zu. Kein Feld ist Pflicht;
   komplett leere Zeilen werden übersprungen.
4. Klick auf **Importieren**.

| Feld | Was Parcella erwartet |
|---|---|
| **Typ (Firma/Person)** | „Firma“, „Company“ oder „Unternehmen“ für eine Firma; „Person“ für eine Person. Ohne die Spalte ist eine Zeile mit Vor- oder Nachname eine Person, sonst eine Firma. |
| **Firmenname** | Bei einer Firma: ihr Name. Bei einer Person: die Firma, zu der sie gehört -- wird angelegt, wenn es sie noch nicht gibt. |
| **Vorname**, **Nachname**, **Position** | Bei Personen. |
| **Straße**, **PLZ**, **Ort**, **IBAN** | Adresse und Bankverbindung. Bei einer Person in einer Firma füllen sie die leeren Felder der Firma. |
| **E-Mail-Adressen**, **Telefonnummern**, **Tags** | Mehrere Werte, durch Semikolon getrennt. |
| **Notizen** | Freitext. |

Eine schon bestehende Firma (gleicher Name, ohne Rücksicht auf Groß- und
Kleinschreibung) oder eine Person mit gleichem Namen wird aus den
nicht-leeren Zellen der Zeile **aktualisiert**. Fehlende Telefonnummern,
E-Mails und Tags kommen dazu. Anders als beim Mitgliederimport wird nie etwas
geleert oder entfernt.

Mehr: [Externe Kontakte](../modules/external-contacts.md).

## Häufige Probleme {#common-problems}

| Was du siehst | Warum, und was zu tun ist |
|---|---|
| Die Datei sei leer | Die Datei hat gar keine Zeilen. Prüf, ob du das richtige Blatt gespeichert hast. |
| Alle Daten landen auf der Zuordnungsseite in einer Spalte | Parcella konnte das Trennzeichen nicht erkennen. Speichere die Datei erneut als „CSV (Trennzeichen-getrennt)“ mit Semikolon oder Komma. |
| Seltsame Zeichen statt Umlauten | Die Datei nutzt eine ungewöhnliche Kodierung (weder UTF-8 noch Windows/ANSI, z. B. von einem alten Mac). Speichere sie erneut als „CSV UTF-8“. |
| Mitglieder übersprungen, weil Vor- oder Nachname fehlt | Diese Zeilen haben eine leere Namenszelle, oder die Namensspalte wurde nicht zugeordnet. |
| Ein Mitglied erscheint doppelt | Die beiden Zeilen unterscheiden sich in Schreibweise oder Geburtsdatum; Parcella hält sie deshalb für verschiedene Personen. Lösch das Doppel von Hand. |
| Die Adresse eines bestehenden Mitglieds ist plötzlich leer | Das Mitglied wurde aus einer Zeile oder Datei ohne diese Spalte aktualisiert. Siehe den Hinweis in Schritt 2; stell bei Bedarf aus deiner Sicherung wieder her. |
| Parzellen „übersprungen“ | Die Gartennummer gibt es schon. Bestehende Parzellen bearbeitest du von Hand. |
| Zählpunkte „Parzelle nicht gefunden“ | Die Gartennummer in der Datei gibt es in Parcella nicht -- importier erst die Parzellen und prüf die Schreibweise („G12“ oder „G 12“). |
| Zählerstände „Zählpunkt nicht gefunden“ | Importier oder lege erst die Zählpunkte an. Hast du **Typ** zugeordnet, prüf seinen Wert. |
| Zählerstände „ungültige Zeile“ | **Datum** oder **Zählerstand** ist leer oder unverständlich, oder es gibt kein Jahr (weder eine Spalte **Jahr** noch ein **Standardjahr (optional)**). |
| Zählerstände „kein aktiver Zähler“ | Am Zählpunkt ist kein Zähler eingebaut. Füg auf der Seite des Zählpunkts einen hinzu. |
| Führendes `'` in exportierten Telefonnummern | Parcella setzt es vor Zellen, die mit `+`, `-`, `=` oder `@` beginnen, damit Tabellenprogramme sie nicht als Formeln behandeln. Entfern es vor dem Mitgliederimport, oder lass es -- der Import externer Kontakte entfernt es für dich. |

## Siehe auch {#related}

- [Mitglieder](../modules/members.md)
- [Parzellen](../modules/parcels.md)
- [Wasser und Strom](../modules/metering.md)
- [Externe Kontakte](../modules/external-contacts.md)
- [Einen neuen Verein einrichten](new-club-setup.md)
- [Zählerstände erfassen](meter-readings.md)

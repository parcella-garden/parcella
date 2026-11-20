# Ein neues Mitglied aufnehmen {#welcoming-a-new-member}

Jemand bewirbt sich um einen Garten, bekommt eine Parzelle angeboten, sagt
ja -- und wird Mitglied und Pächter. Diese Anleitung folgt diesem Weg durch
Parcella, von der Bewerbung bis zur Begrüßung.

Es gibt zwei Wege, jemanden zum Mitglied zu machen:

- **Aus einer Bewerbung** (Schritte 1-6): Die Person steht auf deiner
  [Warteliste](../glossary.md#applicant) unter **Bewerber**. **Parzelle
  zuweisen** erledigt dann Mitgliedseintrag,
  [Pachtverhältnis](../glossary.md#tenancy) und Rechnungsadresse in einem
  Schritt. Das ist der übliche Weg.
- **Von Hand** (Schritt 7): für jemanden, der nie über die Warteliste kam,
  oder eine Parzelle, die nicht gekündigt ist.

!!! info "Wer das tun kann"
    Für die Arbeit mit Bewerbungen brauchst du das Recht **Schreiben** für
    **Bewerber**; die Parzelle zuweisen braucht außerdem **Schreiben** für
    **Mitglieder & Parzellen**. Vorstandsmitglieder und Administratoren
    haben beides. Das Modul **Bewerber** ist standardmäßig an.

## 1. Die Bewerbung kommt herein {#1-the-application-comes-in}

Bewerbungen kommen auf zwei Wegen:

- **Von deiner Website**, wenn der Verein dort das Bewerbungsformular hat
  und die **Öffentliche Bewerbungsformular-API** eingeschaltet ist (siehe
  [Integrationen](../administration/integrations.md)). Sie erscheinen von
  selbst.
- **Von Hand**, für Bewerbungen per Telefon, Brief oder persönlich: Öffne
  **Bewerber**, klick auf **Bewerber erfassen**, füll mindestens die
  **E-Mail-Adresse** aus (das einzige Pflichtfeld), dazu nach Belieben
  **Vorname**, **Nachname**, **Telefon**, **Nachricht des Bewerbers** und
  eine **Notiz des Vorstands**, und klick auf **Speichern**.

Um eine alte Bewerbung von einer Papier-Warteliste einzutragen, setz
**Beworben am** auf das ursprüngliche Datum. Das Bewerbungsdatum bestimmt
die Reihenfolge der Warteliste.

Neue Bewerbungen zeigen einen Zähler neben **Bewerber** in der Seitenleiste
und auf dem Dashboard, bis jemand sie weiterbearbeitet hat.

!!! tip "Rote Liste"
    Passen Name, E-Mail oder Telefon eines Bewerbers zu einem externen
    Kontakt mit deinem „Rote Liste“-Tag, zeigen die Liste und die Seite des
    Bewerbers eine Warnung **Rote Liste**. Siehe
    [Bewerber](../modules/applicants.md).

## 2. Kontakt aufnehmen {#2-get-in-touch}

1. Öffne **Bewerber** und klick auf die neue Bewerbung.
2. Prüf und bearbeite im Kasten **Bewerber kontaktieren** den Text der
   E-Mail. Der Betreff ist *„Vielen Dank für Ihre Anmeldung auf unserer
   Warteliste!“*.
3. Klick auf **Senden** und bestätige.

Parcella schickt den Text per E-Mail an den Bewerber und setzt den Status
auf **Kontaktiert**. Den Kasten gibt es nur, solange der Status **Neu** ist.
Hast du anders Kontakt aufgenommen, änderst du einfach den Status von Hand
(nächster Schritt).

Den Standardtext dieser E-Mail änderst du unter **Administration →
Einstellungen → Bewerber → Text der E-Mail an neue Bewerber**.

## 3. Den Stand der Bewerbung verfolgen {#3-track-the-applications-status}

Geht es weiter, öffne die Bewerbung, wähl den neuen **Status** und klick auf
**Speichern**:

| Status | Bedeutung |
|---|---|
| **Neu** | Gerade eingegangen. |
| **Kontaktiert** | Ihr hattet Kontakt; der Bewerber steht auf der Warteliste. |
| **Garten angeboten** | Du hast eine bestimmte Parzelle angeboten. |
| **Angenommen** | Der Bewerber will die Parzelle; die Übergabe wird vorbereitet. |
| **Abgelehnt** | Keine weiteren Angebote. |
| **Abgeschlossen (Garten vergeben)** | Wird automatisch von **Parzelle zuweisen** gesetzt (Schritt 5). |

Lehnt ein Bewerber eine Parzelle ab, will aber auf der Liste bleiben, setz
ihn zurück auf **Kontaktiert**. Jede Statusänderung steht im
**Statusverlauf** auf der Seite der Bewerbung.

## 4. Sicherstellen, dass die Parzelle gekündigt ist {#4-make-sure-the-parcel-is-terminated}

**Parzelle zuweisen** bietet nur Parzellen mit dem Status **gekündigt** an
-- die Parzelle, die jemand verlassen hat oder gleich verlässt.

1. Öffne die Parzelle unter **Parzellen** und klick auf **Bearbeiten**.
2. Setz den **Status** auf **gekündigt**, füg bei Bedarf eine
   **Kündigungsnotiz** hinzu und klick auf **Änderungen speichern**.

Ist der bisherige Pächter noch mitten im Auszug, siehe
[Eine Parzelle übergeben](parcel-handover.md) -- dort steht die ganze
Übergabe einschließlich der Seite des alten Pächters.

## 5. Die Parzelle zuweisen {#5-assign-the-parcel}

1. Öffne die Bewerbung und klick auf **Parzelle zuweisen**. (Die
   Schaltfläche gibt es bei jeder offenen Bewerbung -- **Neu**,
   **Kontaktiert**, **Garten angeboten** oder **Angenommen**.)
2. Wähl die **Gekündigte Parzelle**. Die Liste zeigt jede Parzelle mit
   ihren aktuellen Pächtern.
3. Setz das **Übergabedatum** -- den Tag, an dem der neue Pächter
   übernimmt. Es darf in der Zukunft liegen.
4. Hak bei Bedarf **Weitere Bewerber (Mitpächter)** an -- zum Beispiel
   einen Partner, der sich getrennt beworben hat und die Parzelle zusammen
   mit diesem Bewerber übernimmt.
5. Gib bei Bedarf den **Dokumentenordner für die neuen Pächter** ein
   (erscheint nur, wenn du Cloud-Ordner verwalten darfst).
6. Klick auf **Vorschau**.
7. Prüf den Kasten **Übergabe der Parzelle … am …**:
    - **Bisherige Pächter**: Ihr Pachtverhältnis endet am Übergabedatum.
      Haben sie keine andere Parzelle, endet ihre Mitgliedschaft am Tag
      davor.
    - **Neue Pächter und Rechnungsempfänger**: Jeder Bewerber **wird neues
      Mitglied** (Name, E-Mail und Telefon kommen aus der Bewerbung) oder
      wird, wenn ein aktives Mitglied schon dieselbe E-Mail-Adresse nutzt,
      mit diesem bestehenden Mitglied verknüpft.
8. Klick auf **Parzelle übergeben** und bestätige.

Was in einem Schritt passiert:

- Die Bewerber werden Mitglieder, mit **Mitglied seit** auf dem
  Übergabedatum.
- Sie werden ab dem Übergabedatum Pächter der Parzelle, mit **Als
  Rechnungsadresse verwenden** gesetzt.
- Die bisherigen Pächter werden frühere Pächter -- der Verlauf bleibt auf
  der Parzellenseite.
- Der Status der Parzelle geht zurück auf **aktiv**.
- Die Bewerbungen werden auf **Abgeschlossen (Garten vergeben)** gesetzt.

Liegt das Übergabedatum in der Zukunft, bleiben die bisherigen Pächter bis
zu diesem Tag Pächter, Mitglieder und Rechnungsempfänger; die neuen stehen
als künftige („ab …“) auf der Parzellenseite und übernehmen am Stichtag.

## 6. Den Eintrag des neuen Mitglieds vervollständigen {#6-complete-the-new-members-record}

Die Übergabe kopiert nur Name, E-Mail und Telefon. Füll den Rest aus:

1. Öffne **Mitglieder** und klick auf das neue Mitglied (oder folg dem Link
   auf der Parzellenseite).
2. Klick auf **Bearbeiten** und ergänze **Geburtsdatum**, **IBAN** und die
   Adresse (**Straße und Hausnummer**, **PLZ**, **Ort**).
3. Prüf **Darf per E-Mail Informationen erhalten**. Bei Mitgliedern, die
   über **Parzelle zuweisen** angelegt wurden, ist es angehakt, weil der
   Bewerber eine E-Mail-Adresse angegeben hat; nimm den Haken weg, wenn das
   Mitglied nur Papier möchte. Ohne den Haken landen Rechnungen und
   Mitteilungen auf dem Druckstapel statt im Postfach.
4. Hak unter **Tags** bestehende Tags an oder tipp neue ein (zum Beispiel
   „Heckenteam“), durch Kommas getrennt.
5. Klick auf **Änderungen speichern**.

Tags kannst du auch direkt auf der Seite des Mitglieds hinzufügen, in der
Karte **Tags** mit **Tag hinzufügen**.

## 7. Ohne Bewerbung: das Mitglied von Hand anlegen {#7-without-an-application-create-the-member-by-hand}

1. Öffne **Mitglieder** und klick auf **Neues Mitglied**.
2. Füll **Vorname** und **Nachname** (Pflicht), die Adresse,
   **Geburtsdatum**, **IBAN**, **Mitglied seit**, eine **E-Mail-Adresse**
   und **Telefonnummer**, **Darf per E-Mail Informationen erhalten** und
   gegebenenfalls **Tags** aus.
3. Klick auf **Mitglied anlegen**.
4. Wähl auf der Seite des Mitglieds unter **Zugeordnete Parzellen** die
   Parzelle in **Parzelle wählen…**, lass **Als Rechnungsadresse verwenden**
   angehakt, wenn dieses Mitglied die Rechnungen der Parzelle bekommen soll,
   und klick auf **Zuordnen**.

Alternativ ordnest du von der Parzellenseite aus zu: **Aktuelle Pächter →
Mitglied wählen… → Zuordnen**, wo du auch das Startdatum eingeben kannst.
Um das Startdatum später zu korrigieren, nimm das Stift-Symbol neben dem
Pächter auf der Parzellenseite (**Pachtverhältnis bearbeiten**, Feld
**Pächter seit**).

Ist noch ein bisheriger Pächter auf der Parzelle, beende erst sein
Pachtverhältnis -- siehe [Eine Parzelle übergeben](parcel-handover.md).

## 8. Das neue Mitglied begrüßen {#8-welcome-the-new-member}

Eine automatische Begrüßungs-E-Mail hat Parcella nicht. Zwei Dinge helfen:

**Ein Vorgang für die Aufnahme.** Das Modul **Vorgänge** bringt eine
Beispielvorlage mit, **Aufnahme neuer Mitglieder**, mit drei Stufen:
**Begrüßung** (**Begrüßungsgespräch**, **Satzung und Gartenordnung
übergeben**), **Unterlagen** (**Unterschriebener Mitgliedsantrag**,
**SEPA-Lastschriftmandat liegt vor**) und **Abschluss** (**In den Verteiler
aufgenommen**, **Notizen**).

1. Einmal: Öffne **Vorgänge → Vorlagen** und klick unter **Mit einem
   Beispiel beginnen** auf **Übernehmen** neben **Aufnahme neuer
   Mitglieder**. Pass Stufen und Felder nach Belieben an. (Vorlagen anlegen
   braucht vollen Zugriff.)
2. Für jedes neue Mitglied: Klick auf der Seite des Mitglieds in der Karte
   **Vorgänge** auf **Vorgang starten**, wähl die **Vorlage** und klick auf
   **Starten**.
3. Füll die Felder aus, sobald etwas erledigt ist, und klick auf **Erledigt
   -- nächste Stufe**. Pflichtfelder müssen ausgefüllt sein, bevor es
   weitergeht.

**Eine persönliche Nachricht.** Ist das Modul **Mitteilungen** an, hak das
neue Mitglied in der Liste **Mitglieder** an und klick auf **An Auswahl
schreiben**.

## Siehe auch {#related}

- [Bewerber](../modules/applicants.md)
- [Mitglieder](../modules/members.md)
- [Parzellen](../modules/parcels.md)
- [Vorgänge](../modules/processes.md)
- [Mitteilungen](../modules/announcements.md)
- [Eine Parzelle übergeben](parcel-handover.md)
- Glossar: [Bewerber](../glossary.md#applicant),
  [Pachtverhältnis](../glossary.md#tenancy),
  [Rechnungsadresse](../glossary.md#invoice-address)

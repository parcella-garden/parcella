# Eine Parzelle übergeben {#handing-over-a-parcel}

Ein Pächter kündigt, die Parzelle wird begangen und bewertet, der Warteliste
angeboten, und schließlich unterschreibt ein neuer Pächter und bekommt die
Schlüssel. Das dauert Wochen oder Monate und betrifft mehrere
Vorstandsmitglieder. Diese Anleitung zeigt, was Parcella unterwegs
festhält und wie ein [Vorgang](../glossary.md#process) die Schritte
verfolgt, die es nicht von selbst festhält.

## Was Parcella festhält -- und was nicht {#what-parcella-does-and-doesnt-track}

| Teil der Übergabe | In Parcella |
|---|---|
| Die Kündigung | Parzellenstatus **gekündigt**, mit automatisch protokolliertem Datum und einer freiwilligen **Kündigungsnotiz**. |
| Bisherige und neue Pächter | Das Beenden des alten [Pachtverhältnisses](../glossary.md#tenancy) bewahrt es als Verlauf; das neue beginnt am Übergabedatum. **Parzelle zuweisen** bei einer Bewerbung erledigt beides in einem Schritt. |
| Die Mitgliedschaft des bisherigen Pächters | Endet mit **Parzelle zuweisen** automatisch, wenn er keine andere Parzelle hat. |
| Dokumentenordner | Der Cloud-Ordner der bisherigen Pächter wird am Übergabedatum abgelöst; ein neuer übernimmt. |
| Begehung, [Wertermittlung](../glossary.md#valuation), Angebot, Besichtigung, Vertrag, Schlüssel | Nicht eingebaut. Verfolg sie mit einem **Vorgang** (Schritt 1). |
| [Kaution](../glossary.md#deposit) | Keine Kautionsfunktion. Betrag und Datum hältst du im Vorgang fest; das Geld erfasst du in **Finanzen**, wenn du es nutzt (Schritt 7). |
| Endstände der Zähler | Parcella speichert **einen Zählerstand je Zähler und Jahr**. Übergabestände hältst du im Vorgang fest (Schritt 6). |
| Preis zwischen bisherigem und neuem Pächter | **Bewusst nicht erfasst.** Was der neue Pächter dem bisherigen für Laube und Pflanzen zahlt, ist Privatsache der beiden. Parcella hat dafür kein Feld -- füg auch deiner Vorgangsvorlage keins hinzu. |

!!! info "Wer das tun kann"
    Änderungen an Parzellen und Pachtverhältnissen brauchen **Schreiben**
    für **Mitglieder & Parzellen**; **Parzelle zuweisen** braucht außerdem
    **Schreiben** für **Bewerber**. Vorgangsvorlagen brauchen vollen Zugriff
    (Vorstand oder Administrator); die Arbeit an einem Vorgang braucht
    **Schreiben** für **Vorgänge**.

## 1. Eine Vorgangsvorlage für die Übergabe vorbereiten (einmal) {#1-prepare-a-handover-process-template-once}

Das Modul **Vorgänge** bringt eine Beispielvorlage **Parzellenübergabe**
mit. Beginn damit und pass sie an den Ablauf deines Vereins an.

1. Öffne **Vorgänge → Vorlagen** (die Seite heißt **Vorgangsvorlagen**).
2. Klick unter **Mit einem Beispiel beginnen** auf **Übernehmen** neben
   **Parzellenübergabe**. Parcella legt eine normale Vorlage an, die du frei
   ändern kannst. Sie betrifft eine **Parzelle**; jeder Vorgang gehört also
   zu einer Parzelle und erscheint auf deren Seite.
3. Das Beispiel hat sechs Stufen: **Begehung**, **Wertermittlung**,
   **Ausschreibung**, **Neuer Pächter**, **Vertrag und Kaution** und
   **Übergabe**. Um zum üblichen Ablauf unten zu passen, füg im Editor Stufen
   hinzu und benenn sie um (einen **Namen der Stufe** eintippen und auf
   **Hinzufügen** klicken; Stufen zum Umsortieren ziehen; Felder hinzufügen,
   indem du eine Bezeichnung tippst und Enter drückst):

| Stufe | Beispielfelder | Feldart |
|---|---|---|
| Kündigung *(neu, zuerst)* | Kündigung eingegangen am (Pflicht) · Kündigungsschreiben | Datum · Dateien (PDF, Fotos) |
| **Begehung** | **Datum der Begehung** · **Festgestellte Mängel** · **Fotos der Mängel** · **Alle Mängel behoben** | aus dem Beispiel |
| **Wertermittlung** | **Wertermittler** · **Datum der Wertermittlung** · **Wertermittlungsprotokoll** | aus dem Beispiel |
| **Ausschreibung** → umbenennen in „Angebot an die Warteliste“ | **Ausschreibungstext** · **Veröffentlicht am** | aus dem Beispiel |
| Besichtigung *(neu)* | Besichtigungstermin · Interessierte Bewerber (Notizen) | Datum · Langer Text |
| **Neuer Pächter** | **Neuer Pächter** (ein Bewerber) · **Kontakt hergestellt** · **Unterlagen verschickt** | aus dem Beispiel |
| **Vertrag und Kaution** | **Kaufvertrag bestätigt** · **Kaution** · **Kaution eingegangen am** | aus dem Beispiel |
| **Übergabe** → aufteilen in „Unterschrift“ und „Abschluss-Checkliste“ | Unterschrift: **Vom neuen Pächter unterschrieben**, **Vom Vorstand gegengezeichnet**. Abschluss-Checkliste: **Schlüssel übergeben**, **Zähler abgelesen**, **Übergabeprotokoll** | aus dem Beispiel |

4. Füg in der Stufe „Abschluss-Checkliste“ Felder vom Typ **Zahl** für die
   Zählerstände bei der Übergabe hinzu, z. B. „Wasserzählerstand bei
   Übergabe“ und „Stromzählerstand bei Übergabe“ (siehe Schritt 6).

Markier ein Feld als **Pflichtfeld**, wenn der Vorgang ohne es nicht
weitergehen darf. Änderungen an einer Vorlage wirken nur auf Vorgänge, die
danach gestartet werden.

!!! tip
    **Kaufvertrag bestätigt** ist nur ein Häkchen: Der Vorstand bestätigt,
    dass sich bisheriger und neuer Pächter geeinigt haben. Der Preis selbst
    bleibt zwischen den beiden.

Mehr: [Vorgänge](../modules/processes.md).

## 2. Die Kündigung erfassen {#2-record-the-notice}

Wenn die Kündigung des Pächters eingeht:

1. Öffne die Parzelle unter **Parzellen** und klick auf **Bearbeiten**.
2. Setz den **Status** auf **gekündigt**. Parcella protokolliert den
   Zeitpunkt der Statusänderung; die Parzellenseite zeigt dann **Gekündigt
   am**.
3. Füg bei Bedarf eine **Kündigungsnotiz** hinzu (Grund, Datum der
   Kündigung, Bemerkungen).
4. Klick auf **Änderungen speichern**.

Der Pächter bleibt aktueller Pächter -- und bekommt weiter die Rechnungen der
Parzelle --, bis das Pachtverhältnis wirklich endet. Beende das
Pachtverhältnis jetzt nicht; das erledigt **Parzelle zuweisen** am
Übergabedatum (Schritt 5).

## 3. Den Vorgang starten {#3-start-the-process}

1. Klick auf der Seite der Parzelle in der Karte **Vorgänge** auf **Vorgang
   starten**.
2. Wähl deine Übergabe-**Vorlage**. Gib dem Vorgang bei Bedarf einen
   **Titel**.
3. Klick auf **Starten**.
4. Füll die Felder der ersten Stufe aus und klick auf **Speichern**. Ist die
   Stufe vollständig, klick auf **Erledigt -- nächste Stufe**.

Der Vorgang erscheint mit seiner aktuellen Stufe auf der Parzellenseite und
unter **Vorgänge** für alle, die daran arbeiten. Hochgeladene Dateien
(Briefe, Fotos, das Wertermittlungsprotokoll) kommen in den Cloud-Ordner der
Parzelle, wenn einer gesetzt ist, sonst in Parcellas eigenen Speicher.

Um zu einer früheren Stufe zurückzugehen, klick auf **Zurückgehen**, wähl
die Stufe und gib einen **Grund** an. Platzt die Übergabe, nimm **Vorgang
abbrechen** mit einem Grund.

## 4. Begehung, Wertermittlung, Angebot, Besichtigung {#4-inspection-valuation-offer-viewing}

Arbeite diese Stufen im Vorgang ab, wie sie passieren. Das
[Wertermittlungs](../glossary.md#valuation)protokoll kommt in
**Wertermittlungsprotokoll**, der Text des Angebots in
**Ausschreibungstext**.

Um Interessierte zu finden, öffne **Bewerber** mit dem Filter **Offen** --
die Liste ist nach Bewerbungsdatum sortiert. Setz die, denen du die Parzelle
anbietest, auf **Garten angeboten**, und den, der sie nimmt, auf
**Angenommen**. Ist das Modul **Mitteilungen** an, hak mehrere Bewerber an
und klick auf **An ausgewählte Bewerber schreiben**, um das Angebot per
E-Mail zu verschicken.

Mehr: [Bewerber](../modules/applicants.md).

## 5. Die Parzelle an den neuen Pächter übergeben {#5-hand-the-parcel-over-to-the-new-tenant}

Sobald der Vertrag unterschrieben ist -- oder, mit einem künftigen Datum,
sobald er feststeht:

1. Öffne die Bewerbung des neuen Pächters und klick auf **Parzelle
   zuweisen**.
2. Wähl diese Parzelle unter **Gekündigte Parzelle** und setz das
   **Übergabedatum**.
3. Füg unter **Weitere Bewerber (Mitpächter)** einen Partner hinzu, wenn
   sie die Parzelle gemeinsam übernehmen.
4. Nutzt du Cloud-Speicher, gib den **Dokumentenordner für die neuen
   Pächter** ein. Der Ordner der bisherigen Pächter wird am Übergabedatum so
   oder so abgelöst.
5. Klick auf **Vorschau**, prüf bisherige und neue Pächter, klick dann auf
   **Parzelle übergeben** und bestätige.

Am Übergabedatum:

- endet das bisherige Pachtverhältnis und wandert auf der Parzellenseite zu
  **Frühere Pächter**;
- verlässt ein bisheriger Pächter ohne andere Parzelle den Verein
  (**Mitglied bis** ist der Tag vor dem Übergabedatum);
- werden die Bewerber Mitglieder, Pächter und Rechnungsempfänger;
- ist die Parzelle wieder **aktiv**.

Einzelheiten und das Vervollständigen des neuen Mitgliedseintrags stehen in
[Ein neues Mitglied aufnehmen](new-member.md), Schritte 5 und 6.

### Wenn der neue Pächter kein Bewerber ist {#if-the-new-tenant-isnt-an-applicant}

Zum Beispiel ein Familienmitglied, das übernimmt. Mach es von Hand:

1. Klick auf der Parzellenseite unter **Aktuelle Pächter** auf das
   Stift-Symbol neben dem bisherigen Pächter (**Pachtverhältnis
   bearbeiten**), setz **Pächter bis** auf den letzten Tag und klick auf
   **Änderungen speichern**. Oder, um es heute zu beenden, klick auf das
   Symbol **Pachtverhältnis beenden** und bestätige *„Pachtverhältnis
   beenden? (Historie bleibt erhalten)“*.
2. Verlässt der bisherige Pächter den Verein, öffne seine Mitgliedsseite,
   klick auf **Bearbeiten**, setz **Mitglied bis** und klick auf
   **Änderungen speichern**. Lösch ihn nicht -- siehe die Warnung unten.
3. Ordne den neuen Pächter zu: **Mitglied wählen…**, das Startdatum, **Als
   Rechnungsadresse verwenden**, **Zuordnen**. Leg ihn bei Bedarf vorher
   unter **Mitglieder → Neues Mitglied** an.
4. Bearbeite die Parzelle und setz den **Status** zurück auf **aktiv**.

!!! tip "Eine Kündigung festhalten"
    Ein Pächter, der gekündigt hat, bleibt Rechnungsadresse, bis er geht:
    Setz sein **Pächter bis** in **Pachtverhältnis bearbeiten** und lass
    **Als Rechnungsadresse verwenden** angehakt. Ist der Tag vorbei, wird
    das Häkchen von selbst entfernt -- sorg dafür, dass bis dahin der neue
    Pächter die Rechnungsadresse ist.

!!! warning "Beenden, nicht löschen"
    Ein Pachtverhältnis oder eine Mitgliedschaft zu beenden, bewahrt den
    Verlauf: wer wann welche Parzelle hatte und welche Stunden und
    Rechnungen zu wem gehörten. Ein Mitglied zu löschen, entfernt es aus
    jeder Auswertung, auch aus den Arbeitsstunden der Jahre, in denen es
    Pächter war.

## 6. Endstände der Zähler {#6-final-meter-readings}

Parcella speichert einen Zählerstand je Zähler und Jahr, und auf diesem
Stand beruht die Jahresrechnung. Einen eigenen „Übergabestand“ gibt es
nicht.

- Schreib die Stände am Tag der Übergabe in den Vorgang (die Stufe
  „Abschluss-Checkliste“ aus Schritt 1) und hak **Zähler abgelesen** an.
- Trag sie nicht als Jahresstand am Zählpunkt ein, außer du willst genau
  das: Der Jahresstand später im Jahr **ersetzt** ihn.
- Die jährliche Wasser- und Stromrechnung der Parzelle geht an den, der beim
  Abschließen des [Rechnungslaufs](../glossary.md#invoice-run)
  Rechnungsempfänger ist -- nach einer Übergabe also der neue Pächter --,
  für den Verbrauch des ganzen Jahres. Wie bisheriger und neuer Pächter das
  aufteilen, ist ihre Sache und die Sache der Regeln deines Vereins; regelt
  das außerhalb von Parcella, mit den Ständen aus dem Vorgang.

Wird bei der Übergabe ein Zähler getauscht, siehe
[Zählerstände erfassen](meter-readings.md#a-meter-is-replaced).

## 7. Kaution und Geld {#7-deposit-and-money}

Parcella hat kein Kautionsfeld an der Parzelle oder am Mitglied. Nimm den
Vorgang für die Unterlagen: **Kaution** (Betrag) und **Kaution eingegangen
am** in der Stufe **Vertrag und Kaution**.

Nutzt du das Modul **Finanzen**, erfass auch das Geld selbst:

- **Eingegangene Kaution**: Öffne **Finanzen → Übersicht → Konten**, klick
  neben dem Konto, auf dem das Geld eingegangen ist, auf **Buchungen** und
  nimm **Buchung hinzufügen** (oder **CSV importieren** mit deinem
  Kontoauszug).
- **Die Kaution des bisherigen Pächters zurückzahlen**: genauso, als
  negativer Betrag.

**Arbeitsstunden.** Ein Pächter, der im Lauf des Jahres geht, schuldet
trotzdem die [Pflichtstunden](../glossary.md#mandatory-hours) dieses Jahres.
Bei Abrechnung je Parzelle zählen seine Stunden zusammen mit denen des neuen
Pächters, und ein Fehlbetrag wird dem Rechnungsempfänger der Parzelle zum
Zeitpunkt des Rechnungslaufs berechnet -- dem neuen Pächter. Will dein Verein
das nicht, regel es von Hand. Siehe
[Die Jahresrechnung erstellen](annual-invoicing.md).

**Offene Rechnungen** des bisherigen Pächters bleiben, wie sie sind;
Rechnungsnummer, Empfänger und Adresse bleiben auf jeder Rechnung erhalten,
du kannst also weiter kassieren und mahnen.

## 8. Den Vorgang abschließen {#8-close-the-process}

Ist die letzte Stufe erledigt, klick auf **Vorgang abschließen**. Ein
abgeschlossener Vorgang ist schreibgeschützt und bleibt mit seinem ganzen
**Verlauf** auf der Parzellenseite.

## Siehe auch {#related}

- [Parzellen](../modules/parcels.md)
- [Bewerber](../modules/applicants.md)
- [Mitglieder](../modules/members.md)
- [Vorgänge](../modules/processes.md)
- [Wasser und Strom](../modules/metering.md)
- [Konten und Buchungen](../modules/finances/bank-accounts.md)
- [Ein neues Mitglied aufnehmen](new-member.md)
- Glossar: [Kaution](../glossary.md#deposit),
  [Wertermittlung](../glossary.md#valuation),
  [Kündigung](../glossary.md#notice-of-termination),
  [Pachtverhältnis](../glossary.md#tenancy)

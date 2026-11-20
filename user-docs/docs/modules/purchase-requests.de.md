# Einkaufswünsche {#purchase-requests}

Einkaufswünsche sorgen dafür, dass kein Vereinsgeld ohne Einigung
ausgegeben wird: Bevor jemand etwas für den Verein kauft, stellt er einen
Antrag, und **zwei verschiedene Vorstandsmitglieder** müssen ihn freigeben.
Ein einzelnes Vorstandsmitglied kann ihn allein stoppen. Alle Beteiligten
können den Antrag direkt auf seiner Seite besprechen.

!!! info "Wer das nutzen kann"
    - **Anträge sehen und kommentieren:** alle, deren Gruppe **Lesen** bei
      **Einkaufswünsche** gewährt (siehe [Gruppen](../administration/groups.md)).
    - **Anträge anlegen und den Lieferanten ändern:** **Schreiben** bei
      **Einkaufswünsche**.
    - **Freigeben oder ablehnen:** nur Vorstandsmitglieder und
      Administratoren oder Benutzer in einer Gruppe mit vollem Zugriff. Ein
      normales Recht **Schreiben** genügt nicht.

    Eingeschaltet wird das Modul mit **Einkaufswünsche** unter
    [Module ein- und ausschalten](../administration/modules.md). Es ist
    standardmäßig an.

Der Navigationseintrag **Einkaufswünsche** zeigt ein rotes Badge mit der Zahl
der offenen Anträge -- dieselbe Zahl wie die Dashboard-Kachel. Es zählt jeden
offenen Antrag, auch solche, die du schon freigegeben hast und die auf eine
zweite Freigabe warten.

## Das Vier-Augen-Prinzip {#the-two-person-approval-principle}

Diese Regeln gelten immer, egal wer die Anwendung nutzt:

1. Ein Antrag ist beim Anlegen **Offen**.
2. Er wird **Genehmigt**, sobald **zwei verschiedene** Vorstandsmitglieder
   auf **Freigeben** geklickt haben. Jedes Vorstandsmitglied kann einen
   Antrag nur einmal freigeben.
3. **Weder der Antragsteller noch die Person, die den Antrag erfasst hat**,
   darf ihn freigeben. Das zählt, wenn ein Vorstandsmitglied einen Antrag
   für jemand anderen erfasst: Es zählt dann zur Seite des Antragstellers
   und kann keine der beiden Freigaben selbst geben.
4. **Eine Ablehnung genügt.** Jedes Vorstandsmitglied kann einen offenen
   Antrag mit Begründung ablehnen. Auch der Antragsteller kann seinen
   eigenen Antrag ablehnen -- etwa um ihn zurückzuziehen.
5. Ist ein Antrag **Genehmigt** oder **Abgelehnt**, ist das endgültig.
   Weitere Freigaben oder Ablehnungen sind nicht möglich, und es gibt
   keinen Weg, ihn wieder zu öffnen.

!!! note
    Freigaben und Ablehnungen verschicken keine E-Mails. Das tun nur neue
    Kommentare (siehe [Diskussion](#discussion)).

## Übersicht {#overview}

![Übersicht der Einkaufswünsche](../assets/screenshots/purchase-requests/list.png)

**Einkaufswünsche** listet die Anträge, die neuesten zuerst.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Neuer Einkaufswunsch** | Öffnet das [Formular](#new-purchase-request). Erscheint nur mit Schreibrecht. |
| **Offen** / **Genehmigt** / **Abgelehnt** / **Alle** | Zeigt nur Anträge in diesem Status oder alle. **Offen** ist gewählt, wenn du auf die Seite kommst. |
| **Titel** | Was gekauft werden soll; verlinkt auf den Antrag. |
| **Antragsteller** | Der Name des Antragstellers. Bei einem Antrag für jemand anderen der eingetippte Name (oder seine E-Mail-Adresse, wenn kein Name angegeben ist). |
| **Geschätzte Kosten** | Die geschätzten Kosten oder „–“, wenn keine eingetragen sind. |
| **Freigaben** | Bei offenen Anträgen, wie viele der zwei nötigen Freigaben es gibt, z. B. **1 / 2**. „–“ bei abgeschlossenen Anträgen. |
| **Status** | **Offen**, **Genehmigt** oder **Abgelehnt**. |
| Augen-Schaltfläche | Öffnet den Antrag. |

## Neuer Einkaufswunsch {#new-purchase-request}

![Neuer Einkaufswunsch](../assets/screenshots/purchase-requests/form.png)

Klick in der Übersicht auf **Neuer Einkaufswunsch**.

### Einkaufswunsch {#purchase-request}

| Feld | Was es bewirkt |
|---|---|
| **Was soll gekauft werden?** | Der Titel des Antrags. Pflicht. |
| **Begründung** | Warum der Verein es braucht. Pflicht. |
| **Link zur Einkaufsmöglichkeit** | Freiwillige Webadresse eines Shops oder Angebots. Muss eine vollständige Adresse sein, die mit `http://` oder `https://` beginnt. |
| **Lieferant (Kontakt)** | Freiwilliger Lieferant aus den [Externen Kontakten](external-contacts.md). Firmen stehen mit ihren Personen darunter. Erscheint nur, wenn das Modul Externe Kontakte eingeschaltet ist und du Kontakte lesen darfst. |
| **Geschätzte Kosten** | Freiwillig. Komma oder Punkt als Dezimaltrennzeichen. Lass es leer, wenn der Preis noch nicht bekannt ist. Kann Parcella den Wert nicht als Zahl lesen, wird der Antrag ohne Kosten gespeichert. |

### Antragsteller {#requester}

| Feld | Was es bewirkt |
|---|---|
| **Für eine andere Person anlegen (die keinen eigenen Zugang hat)** | Anhaken, wenn du einen Antrag für jemand anderen erfasst, z. B. für ein Mitglied, das dich angerufen hat. Zeigt die beiden Felder darunter. Lässt du es leer, bist du der Antragsteller. |
| **Name der Person** | Der Name des Antragstellers. |
| **E-Mail-Adresse** | Die E-Mail-Adresse des Antragstellers. Er bekommt einen Link, um die Angaben zu bestätigen (siehe [Bestätigung durch den Antragsteller](#confirmation-by-the-requester)). |

Mit **Einkaufswunsch anlegen** speicherst du, mit **Abbrechen** gehst du
zurück. Nach dem Speichern öffnet sich die Seite des Antrags.

!!! note "Ohne E-Mail-Adresse"
    Du kannst die **E-Mail-Adresse** leer lassen: Der Antrag wird mit dem
    eingetippten Namen als Antragsteller gespeichert, nur ohne
    Bestätigungs-E-Mail. Hakst du das Kästchen an, lässt aber Name und
    Adresse leer, zählt der Antrag als *dein eigener*. So oder so kannst du
    einen Antrag, den du selbst erfasst hast, nicht freigeben.

## Antragsseite {#request-page}

![Einkaufswunsch](../assets/screenshots/purchase-requests/detail.png)

Beim Öffnen eines Antrags siehst du seine Details, die Diskussion und die
Freigaben. **Zurück** führt zur Übersicht.

### Details {#details}

| Feld | Was es zeigt |
|---|---|
| **Antragsteller** | Wer den Kauf wünscht. Bei einem Antrag für jemand anderen auch seine E-Mail-Adresse und ein Badge: **Bestätigung ausstehend** oder **Vom Antragsteller bestätigt**. |
| **Erstellt von** | Wer den Antrag erfasst hat, und wann. |
| **Begründung** | Die angegebene Begründung. |
| **Link** | Der Shop-Link, falls eingetragen. Öffnet sich in einem neuen Tab. |
| **Lieferant (Kontakt)** | Der verknüpfte externe Kontakt oder „–“. Mit Schreibrecht kannst du einen anderen Kontakt wählen (oder **— keiner —**) und auf **Speichern** klicken -- in jedem Status, weil der Lieferant nicht Teil der Freigabe ist. Ein inzwischen gelöschter Kontakt erscheint mit „(gelöscht)“. |
| **Geschätzte Kosten** | Erscheint nur, wenn Kosten eingetragen sind. |

Unter den Details zeigt ein abgeschlossener Antrag ein Banner:

- **Genehmigt** -- mit Datum und Uhrzeit der zweiten Freigabe.
- **Abgelehnt** -- mit wer ihn abgelehnt hat, wann, und der Begründung.

### Diskussion {#discussion}

Die Karte **Diskussion (…)** listet alle Kommentare, die ältesten zuerst,
mit Verfasser und Zeit. Wer den Antrag sehen kann, kann kommentieren, in
jedem Status -- gerade bei einem abgelehnten Antrag möchte oft jemand etwas
erklären.

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| Kommentarfeld | Deine Frage oder dein Hinweis, bis zu 5.000 Zeichen. Ein leerer Kommentar wird abgelehnt. |
| **Kommentieren** | Fügt den Kommentar hinzu und verschickt ihn per E-Mail. |

Kommentare lassen sich danach nicht bearbeiten oder löschen.

Jeder neue Kommentar geht per E-Mail an:

- den Antragsteller -- die Adresse seines Kontos oder, bei einem Antrag
  für jemand anderen, die dort angegebene E-Mail-Adresse;
- jeden aktiven Benutzer, der den Antrag vorher kommentiert oder
  freigegeben hat.

Der Verfasser des Kommentars bekommt keine E-Mail, und niemand bekommt
denselben Kommentar zweimal. Benutzer bekommen eine Schaltfläche, die den
Antrag öffnet, damit sie in Parcella antworten können. Ein Antragsteller
ohne Konto kann nicht in Parcella antworten; seine E-Mail bittet ihn, sich an
den Vorstand zu wenden.

### Freigaben (…/2) {#approvals-count2}

Listet jede Freigabe mit dem Namen des Vorstandsmitglieds und Datum und
Uhrzeit. **Noch keine Freigaben.**, wenn es keine gibt.

Solange der Antrag **Offen** ist, sehen Vorstandsmitglieder außerdem:

| Schaltfläche / Meldung | Was sie bewirkt |
|---|---|
| **Freigeben** | Hält deine Freigabe fest. Die zweite Freigabe von einem anderen Vorstandsmitglied setzt den Antrag auf **Genehmigt**. |
| „Als Antragsteller können Sie diesen Einkaufswunsch nicht selbst freigeben …“ | Erscheint statt **Freigeben**, wenn du der Antragsteller bist oder den Antrag erfasst hast. |
| „Sie haben bereits freigegeben.“ | Erscheint statt **Freigeben**, nachdem du freigegeben hast. |
| **Ablehnen** | Öffnet ein Feld für die Begründung der Ablehnung. |
| **Endgültig ablehnen** | Lehnt den Antrag mit der eingetragenen Begründung ab (Pflicht). Der Antrag ist sofort abgeschlossen. |

## Bestätigung durch den Antragsteller {#confirmation-by-the-requester}

Legst du einen Antrag für jemand anderen mit E-Mail-Adresse an, schickt
Parcella dieser Person eine E-Mail „Bitte bestätigen: Einkaufswunsch
„…““. Sie nennt dich als die Person, die ihn erfasst hat, wiederholt Titel
und Begründung und enthält eine Schaltfläche **Angaben bestätigen**.

Die Bestätigung ist **nur zur Information**. Sie zeigt dem Vorstand, dass
die Person den Antrag wirklich so gemeint hat. Für die Freigabe ist sie
*nicht* nötig: Vorstandsmitglieder können freigeben oder ablehnen, ob der
Antragsteller bestätigt hat oder nicht. Hat der Antragsteller ein eigenes
Konto und legt den Antrag selbst an, gibt es gar keinen
Bestätigungsschritt.

### Einkaufswunsch bestätigen {#confirm-purchase-request}

Der Link in der E-Mail öffnet eine Seite, die **ohne Anmeldung**
funktioniert. Sie zeigt **Titel**, **Begründung**, **Link** (falls
vorhanden) und **Geschätzte Kosten** (falls vorhanden) des Antrags, mit der
Erklärung, dass der Antrag im Namen der Person erfasst wurde.

| Schaltfläche / Meldung | Was sie bewirkt |
|---|---|
| **Angaben bestätigen** | Hält die Bestätigung fest. Auf der Antragsseite wechselt das Badge von **Bestätigung ausstehend** zu **Vom Antragsteller bestätigt**. |
| „Sie haben diese Angaben bereits bestätigt.“ | Erscheint statt der Schaltfläche, wenn der Link schon benutzt wurde. Den Link erneut zu öffnen schadet nicht. |

Nach dem Bestätigen sieht die Person eine Seite **Vielen Dank!**, die sagt,
dass ihre Bestätigung für den Antrag gespeichert ist.

### Link nicht gefunden {#link-not-found}

![Link nicht gefunden](../assets/screenshots/purchase-requests/confirmation-invalid.png)

Die Seite **Link nicht gefunden** erscheint, wenn der Link falsch oder
unvollständig ist oder der Antrag **vor mehr als 30 Tagen** angelegt wurde
-- Bestätigungslinks funktionieren nach 30 Tagen nicht mehr. Der
Antragsteller sollte sich dann direkt an den Vorstand wenden; der Vorstand
kann trotzdem über den Antrag entscheiden.

!!! note
    Der Seitentext sagt, der Link „ist ungültig oder wurde bereits
    verwendet“. Ein schon benutzter Link funktioniert innerhalb der 30
    Tage weiter -- er zeigt „Sie haben diese Angaben bereits bestätigt.“

## Siehe auch {#related}

- [Externe Kontakte](external-contacts.md) -- Lieferanten, die du mit einem
  Antrag verknüpfen kannst; die Seite eines Kontakts listet seine
  Einkaufswünsche
- [Eingangsrechnungen](finances/incoming-invoices.md) -- die Rechnung
  erfassen, sobald der genehmigte Kauf erledigt ist
- [Dashboard](../getting-started/dashboard.md) -- die Kachel der offenen
  Einkaufswünsche
- [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md)

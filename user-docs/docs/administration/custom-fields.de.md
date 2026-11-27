# Eigene Felder {#custom-fields}

Mit eigenen Feldern hältst du fest, wofür Parcella kein Feld hat: den
Beruf eines Mitglieds, oder bei einer Parzelle, ob es eine Gartenlaube
gibt -- und wenn ja, ihre Fläche und ihr Baujahr. Du richtest die Felder
einmal ein; danach erscheinen sie in den Formularen für Mitglieder und
Parzellen wie jedes andere Feld.

!!! info "Wer das nutzen kann"
    Einrichten: nur Administratoren. Öffne
    **Administration → Eigene Felder**. Ausfüllen: jeder, der
    Mitglieder und Parzellen bearbeiten darf.

## Die Seite {#the-page}

Oben wählst du den Bereich: **Mitglieder** oder **Parzellen**. Jeder hat
seine eigenen Felder.

Die Karte **Felder** zeigt sie in der Reihenfolge, in der sie in den
Formularen erscheinen. Felder in einer Gruppe stehen eingerückt darunter (↳).

| Spalte / Schaltfläche | Was sie zeigt oder tut |
|---|---|
| **Bezeichnung** | Der Name des Felds, wie er im Formular steht. Ein rotes * heißt **Pflichtfeld**; **Archiviert** markiert ein archiviertes Feld. Darunter steht der Hilfetext. |
| **Typ** | Die Art des Felds, mit Einheit oder Auswahlwerten. |
| **Schlüssel** | Der feste Name des Felds in Exporten und der API. Er entsteht aus der ersten Bezeichnung und bleibt, wenn du das Feld umbenennst. |
| Pfeile | Schieben das Feld nach oben oder unten. Ein Feld in einer Gruppe bewegt sich innerhalb der Gruppe. |
| Stift | Feld bearbeiten. |
| **Archivieren** / **Wiederherstellen** | Siehe [Ein Feld archivieren](#archiving-a-field). |
| Papierkorb | Löscht das Feld endgültig -- siehe [Ein Feld löschen](#deleting-a-field). |

## Feldtypen {#field-types}

| Typ | Im Formular | Beispiel |
|---|---|---|
| **Text** | Eine Zeile Text | Beruf |
| **Langer Text** | Mehrere Zeilen | Hinweise zur Hecke |
| **Zahl** | Eine Zahl, auf Wunsch mit Einheit wie m² oder cm | Fläche der Gartenlaube |
| **Datum** | Ein Datum | Baujahr der Laube |
| **Ja/Nein** | Ein Kästchen | Hat eine Regentonne |
| **Auswahl** | Eine Liste mit den Werten, die du vorgibst | Poolart: Stahlwand, aufblasbar |
| **Gruppe (Ja/Nein mit Unterfeldern)** | Ein Kästchen; die Felder darin erscheinen, sobald es angehakt ist | Pool → Durchmesser, Höhe, im Winter abgebaut |

Zahlen werden mit zwei Nachkommastellen gespeichert.

## Ein Feld oder eine Gruppe anlegen {#adding-a-field-or-group}

Nimm die Karte **Neues Feld oder neue Gruppe**:

| Feld | Was es bewirkt |
|---|---|
| **Bezeichnung** | Pflicht. |
| **Typ** | Siehe [Feldtypen](#field-types). |
| **In Gruppe** | Erscheint erst, wenn es eine Gruppe gibt. Legt das Feld in diese Gruppe. Eine Gruppe kann nicht in einer anderen Gruppe liegen. |
| **Einheit** | Nur bei Zahlen, z. B. m². Steht neben dem Feld und dem Wert. |
| **Auswahlwerte** | Nur bei Auswahlfeldern: ein Wert pro Zeile. |
| **Hilfetext** | Ein kurzer Hinweis unter dem Feld im Formular. |
| **Pflichtfeld** | Das Formular lässt sich ohne Wert nicht speichern. In einer Gruppe nur Pflicht, solange die Gruppe angehakt ist. Ja/Nein-Felder und Gruppen können keine Pflichtfelder sein. |
| **Hinzufügen** | Legt das Feld an. Es kommt ans Ende seines Bereichs oder seiner Gruppe. |

### Beispiel: ein Pool {#example-a-pool}

1. Wähle **Parzellen**, gib als Bezeichnung „Pool“ ein, Typ **Gruppe**, und **Hinzufügen**.
2. Lege „Durchmesser“ an, Typ **Zahl**, Einheit „cm“, **In Gruppe** „Pool“.
3. Lege „Höhe“ genauso an.
4. Lege „Im Winter abgebaut“ an, Typ **Ja/Nein**, in der Gruppe „Pool“.

Im Bearbeitungsformular einer Parzelle gibt es jetzt ein Kästchen
**Pool**; sobald du es anhakst, erscheinen die drei Felder darunter.

## Ein Feld bearbeiten {#editing-a-field}

Der Stift öffnet **Feld bearbeiten**. Bezeichnung, Einheit,
Auswahlwerte, Hilfetext und **Pflichtfeld** kannst du jederzeit ändern.
Den **Typ** nur, solange noch niemand einen Wert eingetragen hat; eine
Gruppe bleibt immer eine Gruppe.

!!! warning "Einen Auswahlwert entfernen"
    Entfernst du einen Wert, den Mitglieder oder Parzellen haben, bleibt
    ihr Wert stehen, lässt sich im Formular aber nicht wieder wählen.

## Ein Feld archivieren {#archiving-a-field}

**Archivieren** blendet ein Feld in
Formularen, Detailseiten, im Listenfilter und in Exporten aus. Die
bisher eingetragenen Werte bleiben erhalten. **Wiederherstellen** holt
das Feld mit seinen Werten zurück. Eine archivierte Gruppe blendet auch
ihre Felder aus; ein Feld in einer archivierten Gruppe lässt sich erst
wiederherstellen, wenn die Gruppe wieder da ist.

## Ein Feld löschen {#deleting-a-field}

Der Papierkorb löscht ein Feld endgültig, zusammen mit allen
eingetragenen Werten; eine gelöschte Gruppe nimmt auch ihre Felder mit.
Vorher fragt eine Bestätigung nach und nennt, wie viele Werte verloren
gehen, z. B. „Die Gruppe „Pool“ mit allen ihren Feldern endgültig
löschen? 12 eingetragene Werte werden mitgelöscht.“ Das lässt sich
nicht rückgängig machen -- brauchst du das Feld vielleicht noch,
archiviere es lieber.

## Wo eigene Felder erscheinen {#where-custom-fields-show-up}

- **Bearbeitungsformular** eines Mitglieds oder einer Parzelle: die Karte
  **Weitere Angaben**. Siehe [Mitglieder](../modules/members.md#further-details_1)
  und [Parzellen](../modules/parcels.md#further-details_1).
- **Detailseite**: die Karte **Weitere Angaben** mit den Feldern, die
  einen Wert haben. Eine Gruppe erscheint nur, wenn sie angehakt ist.
- **Listenfilter**: die Auswahl **– eigenes Feld –** in der Mitglieder-
  und der Parzellenliste.
- **CSV-Export und -Import**: eine Spalte pro Feld.
- **REST-API**: für Entwickler, siehe die API-Dokumentation.

Nimmst du im Formular den Haken einer Gruppe weg, werden die Felder
darin geleert: kein Pool, keine Poolmaße.

## Siehe auch {#related}

- [Mitglieder](../modules/members.md)
- [Parzellen](../modules/parcels.md)
- [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md)

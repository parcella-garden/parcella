# Auswertungen {#reporting}

Die wichtigsten Zahlen deines Vereins im Zeitverlauf, als Diagramme: wie alt
deine Mitglieder sind, wie sich die Mitgliedschaft entwickelt hat, wie viele
Gärten gekündigt wurden, wie viele Leute sich bewerben und wie die
Arbeitsstunden liefen. Praktisch für den Jahresbericht oder die
Mitgliederversammlung.

!!! info "Wer das nutzen kann"
    - Der Modulschalter ist **Auswertungen** unter **Administration →
      Module ein- und ausschalten**. Er ist standardmäßig **an**.
    - Die Rollen **Vorstand** und **Administrator** sowie Mitglieder einer
      Gruppe mit **Voller Zugriff auf jedes Modul** sehen es immer.
    - Alle anderen brauchen *Lesen* bei **Auswertungen** in einer ihrer
      [Gruppen](../administration/groups.md). Die Seite zeigt nur Summen
      und Zahlen, nie Namen; Zugriff auf Mitglieder, Arbeitsstunden oder
      Bewerber braucht es dafür also nicht.

## Die Auswertungsseite {#reporting-page}

![Auswertungen](../assets/screenshots/reporting/index.png)

Öffne **Auswertungen** im Menü. Die Seite ist nur lesend. Jede Zahl wird bei
jedem Öffnen aus deinen aktuellen Daten berechnet; nichts wird gespeichert
oder muss aktualisiert werden. Zeitreihen zeigen bis zu den letzten 10
Jahren, vom ersten Jahr mit Daten bis zum aktuellen Jahr. Ein vergangenes
Jahr zählt mit dem Stand vom 31. Dezember, das aktuelle Jahr mit dem Stand
von heute.

Jedes Diagramm ist eine Karte mit:

- dem Diagramm selbst (fahr mit der Maus darüber, um die genauen Zahlen
  zu sehen);
- einem grauen Hinweis mit Info-Symbol, wo etwas erklärt werden muss, zum
  Beispiel wie viele Mitglieder nicht mitgezählt wurden;
- **Zahlen als Tabelle anzeigen**, das dieselben Zahlen als Tabelle
  aufklappt, fertig zum Kopieren. Kreisdiagramme ergänzen eine Spalte
  **Anteil / Summe** mit den Prozenten, gestapelte Diagramme eine Spalte
  mit der Summe je Jahr.

Ein Diagramm ohne Daten zeigt **Noch keine Daten.**

Manche Diagramme erscheinen nur, wenn ihr Modul eingeschaltet ist: Die
Bewerber-Diagramme brauchen **Bewerber**, die Arbeitsstunden-Diagramme
**Pflichtstunden-Verwaltung** und das Strom-Diagramm **Stromverwaltung**.

## Die Diagramme {#the-charts}

| Diagramm | Was es zählt |
|---|---|
| **Mitglieder nach Generation** | Kreisdiagramm der heute aktiven Mitglieder nach Geburtsjahr: **Stille Generation (bis 1945)**, **Babyboomer (1946–1964)**, **Generation X (1965–1980)**, **Millennials (1981–1996)**, **Generation Z (1997–2012)**, **Generation Alpha (ab 2013)**. Mitglieder ohne Geburtsdatum fehlen; der Hinweis sagt, wie viele. |
| **Mitglieder pro Jahr** | Liniendiagramm der Zahl der **Mitglieder** in jedem Jahr: alle, deren Datum „Mitglied seit“ am oder vor Jahresende liegt und die bis dahin nicht ausgeschieden waren. Mitglieder ohne Eintrittsdatum zählen in jedem Jahr; der Hinweis sagt, wie viele. |
| **Gekündigte Parzellen pro Jahr** | Balkendiagramm der **Beendeten Pachtverhältnisse** je Jahr: jede Pacht, deren Enddatum in dieses Jahr fällt, auch schon gesetzte Enddaten später in diesem Jahr. Ein Garten, der von einem Pächter an den nächsten geht, zählt als eine beendete Pacht. |
| **Bewerbungen pro Quartal** | Balkendiagramm der neuen **Bewerbungen** nach Bewerbungsdatum, für jedes Quartal des letzten und dieses Jahres. |
| **Bewerbungen pro Jahr** | Dasselbe je Jahr. |
| **Arbeitsstunden pro Jahr** | Gestapelte Balken für jedes Jahr mit einer Arbeitsstunden-Konfiguration. Jede Parzelle (oder jedes Mitglied, siehe unten) zählt in genau einer Gruppe, in dieser Reihenfolge geprüft: **Befreit**, **Zahlt Ersatzbeitrag (Stunden fehlen)**, **Erfüllt mit Patenschaft**, **Erfüllt durch Arbeitseinsätze**. In Jahren, in denen Arbeitsstunden je Mitglied statt je Parzelle geschuldet waren, sagt der Hinweis „In … pro Mitglied statt pro Parzelle gezählt.“ |
| **Stundenübertragungen pro Jahr** | Zwei Balken je Jahr: die Zahl der **Übertragungen** von Stunden und die insgesamt **Übertragenen Stunden**. |
| **Parzellen mit Strom** | Kreisdiagramm der heute aktiven Parzellen **Mit Stromanschluss** (mindestens ein Stromzähler auf der Parzelle) und **Ohne Stromanschluss**. |

!!! note "Was du beachten solltest"
    - **Mitglieder nach Generation** und **Parzellen mit Strom** zeigen nur
      den heutigen Stand. Parcella hebt keine Momentaufnahmen auf und kann
      deshalb nicht sagen, wie das in einem früheren Jahr aussah.
    - Ein gelöschtes Mitglied (statt eines mit Enddatum) verschwindet auch
      aus jedem vergangenen Jahr. Beende Mitgliedschaften, statt Mitglieder
      zu löschen, dann bleibt der Verlauf richtig.
    - Die Zahlen kommen aus den Daten, wie sie eingetragen sind. Ein
      fehlendes Eintrittsdatum oder Geburtsdatum taucht in den Hinweisen
      auf; korrigiere es beim [Mitglied](members.md) und lade die Seite neu.

Eine Export-Schaltfläche für die Diagramme gibt es nicht. Nutz **Zahlen als
Tabelle anzeigen**, um die Zahlen zu kopieren, zum Beispiel in eine
Tabellenkalkulation oder den Jahresbericht.

## Siehe auch {#related}

- [Mitglieder](members.md) -- Eintrittsdaten und Geburtsdaten.
- [Parzellen](parcels.md) -- Pachten und ihre Enddaten.
- [Bewerber](applicants.md)
- [Arbeitsstunden](work-hours.md) -- Befreiungen, Patenschaften und
  Stundenübertragungen.
- [Wasser und Strom](metering.md) -- Stromzähler je Parzelle.

# Systeminfo und Updates {#system-information-and-updates}

Die Seite System zeigt, welche Version von Parcella läuft, ob eine neuere
verfügbar ist, und ist der Ausgangspunkt für Sicherungen.

!!! info "Wer das nutzen kann"
    Nur Administratoren. Öffne **Administration → System**.

![System](../assets/screenshots/administration/system.png)

## Update-Hinweis {#update-notice}

Parcella fragt regelmäßig bei GitHub, wo es veröffentlicht wird, ob eine
neuere Version erschienen ist. Über deinen Verein wird dabei nichts
übertragen. Abschalten kannst du das unter
[Vereinseinstellungen → Updates](settings.md#updates); der Update-Hinweis
verschwindet dann von dieser Seite.

**Bist du auf dem neuesten Stand**, siehst du die laufende Version mit dem
Hinweis, dass sie aktuell ist, und wann zuletzt geprüft wurde -- direkt nach
der Installation den Hinweis, dass noch nicht geprüft wurde.

**Gibt es eine neuere Version**, zeigt ein hervorgehobener Kasten die neue
Versionsnummer, die laufende Version und die vier Befehle, die das Update
auf dem Server installieren.

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Jetzt prüfen** | Fragt sofort bei GitHub nach, statt auf die nächste automatische Prüfung (alle sechs Stunden) zu warten. |

!!! note "Aktualisiert wird auf dem Server"
    Das Update selbst ist keine Schaltfläche in Parcella. Wer den Server
    betreibt, tippt die im Kasten gezeigten Befehle ein. Gib sie weiter,
    wenn du das nicht bist. Lade vorher eine [Sicherung](backup.md)
    herunter.

    Der Kasten warnt auch, dass der erste Befehl die Konfigurationsdatei des
    Servers durch die aktuelle ersetzt. Änderungen, die die Serververwaltung
    an dieser Datei gemacht hat, gehen verloren, außer sie stehen in einer
    eigenen Override-Datei, wie es die Installationsanleitung erklärt.

Lies vor dem Aktualisieren die Release Notes auf GitHub, um zu sehen, was
sich geändert hat.

## Datensicherung {#backup}

Die Karte **Datensicherung** hat drei Schaltflächen:

| Schaltfläche | Was sie bewirkt |
|---|---|
| **Cloud-Sicherungen** | Öffnet den Zeitplan für automatische Sicherungen in deinen Cloud-Speicher. |
| **Aus Sicherung wiederherstellen** | Öffnet die Wiederherstellungsseite. |
| **Sicherung herunterladen** | Lädt sofort eine vollständige Sicherung herunter. |

Alle drei sind unter [Backup und Wiederherstellung](backup.md) beschrieben.

## Siehe auch {#related}

- [Backup und Wiederherstellung](backup.md)
- [Vereinseinstellungen](settings.md#updates)

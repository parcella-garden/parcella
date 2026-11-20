# Module {#modules}

Parcella besteht aus Modulen: eines je Bereich der Vereinsarbeit. Dein Verein
schaltet nur die ein, die er braucht; die anderen verschwinden für alle aus
der Navigation. Ein Modul auszuschalten löscht nie seine Daten -- schaltest
du es wieder ein, ist alles wieder da.

Ein Administrator schaltet Module unter
[Module ein- und ausschalten](../administration/modules.md) ein und aus.
Wer ein eingeschaltetes Modul nutzen darf, legen
[Gruppen](../administration/groups.md) fest.

## Übersicht {#overview}

| Modul | Wofür | Nach der Installation an? |
|---|---|---|
| [Mitglieder](members.md) | Alle, die zum Verein gehören: Kontaktdaten, Mitgliedschaftsdaten, Ämter, Verlauf. | Immer an |
| [Parzellen](parcels.md) | Die Gärten, ihre Pacht und Pächter, früher und heute. | Immer an |
| [Bewerber](applicants.md) | Personen, die sich um eine freie Parzelle beworben haben, ihr Status und die Notizen des Vorstands. | Ja |
| [Arbeitsstunden](work-hours.md) | Arbeitseinsätze, Anmeldungen und Anwesenheit, Patenschaften, Stundenübertragungen und die Jahresauswertung der Pflichtstunden. | Ja |
| [Wasser und Strom](metering.md) | Zähler, Ablesungen und Verbrauchsberichte. Wasser und Strom werden getrennt eingeschaltet. | Ja |
| [Versicherungen](insurance.md) | Sach- und Unfallversicherung je Parzelle und Jahr, mit Jahresbericht. | Ja |
| [Finanzen](finances/index.md) | Jahresrechnungen je Parzelle, Zahlungen, Mahnungen, Bankkonten, Eingangsrechnungen und Buchhaltung. | Nein |
| [Einkaufswünsche](purchase-requests.md) | Ausgaben des Vereins, die zwei Vorstandsmitglieder freigeben, bevor Geld ausgegeben wird. | Ja |
| [Kalender](calendar.md) | Vereinskalender, Geburtstage, Vorstandspräsenz und -abwesenheit, eigene Kalender -- jeweils auch als abonnierbarer Kalender-Feed. | Ja |
| [Mitteilungen](announcements.md) | Vereinsnachrichten einmal schreiben und an die Website, per E-Mail und als druckbaren Aushang senden. | Nein |
| [Aufgabenboard](tasks.md) | Ein Board mit „Zu erledigen“ / „In Arbeit“ / „Erledigt“ für die Vereinsarbeit. Nur Vorstand und Administratoren. | Ja |
| [Inventar](inventory.md) | Alles, was dem Verein gehört (und Gegenstände von Mitgliedern auf Vereinsgelände), mit Verleih. | Ja |
| [Notizen](notes.md) | Protokolle und andere Notizen, mit Kategorien und Schlagwörtern, auf Wunsch als Dateien in der Cloud. | Ja |
| [Vorgänge](processes.md) | Eigene Abläufe Schritt für Schritt, etwa eine Parzellenübergabe, für eine Parzelle, ein Mitglied oder einen Bewerber. | Ja |
| [Externe Kontakte](external-contacts.md) | Lieferanten, Handwerker und Behörden, verknüpft mit Rechnungen und Einkaufswünschen. | Ja |
| [Support](support.md) | Die Helpdesk-Konversationen deines Vereins, verknüpft mit Mitgliedern, Parzellen und Aufgaben. | Nein |
| [Auswertungen](reporting.md) | Vereinszahlen über die Jahre als Diagramme. Nur lesend. | Ja |

## Warum manche Module ausgeschaltet starten {#why-some-modules-start-switched-off}

Die Module, die nach der Installation aus sind, tun jeweils etwas, das ein
Verein bewusst entscheiden sollte:

- **Finanzen** verwaltet Geld der Mitglieder und verschickt Rechnungen in
  großer Zahl.
- **Mitteilungen** kann alle Mitglieder anschreiben und auf deiner Website
  veröffentlichen.
- **Support** verbindet sich mit einem externen Helpdesk und braucht dessen
  Zugangsdaten.

Dasselbe gilt für die Zusätze in der Modulliste ohne eigenes Kapitel:
**Cloud-Speicher**, **Nextcloud-Deck-Synchronisierung**, **MCP-Connector
für KI-Clients** und die drei öffentlichen Website-Formulare (**Öffentliche
Anmelde-API**, **Öffentliche Kontaktformular-API**, **Öffentliche
Bewerbungsformular-API**). Sie speichern entweder Passwörter für externe
Dienste oder öffnen ein Formular ins öffentliche Internet. Siehe
[Module ein- und ausschalten](../administration/modules.md) und
[Integrationen](../administration/integrations.md).

## Siehe auch {#related}

- [Rollen, Gruppen und Rechte](../getting-started/roles-and-permissions.md)
- [Sich zurechtfinden](../getting-started/navigation.md)

# API-Tokens {#api-tokens}

Ein API-Token ist ein Schlüssel, mit dem ein anderes Programm Parcella im
Namen von jemandem nutzen kann, ohne dessen Passwort -- zum Beispiel ein
Skript, das Daten exportiert, oder ein KI-Assistent, der die Notizen des
Vereins liest. Die meisten Vereine brauchen nie einen.

!!! info "Wer das nutzen kann"
    Jeder Benutzer kann **seine eigenen** Tokens verwalten: **Passwort
    ändern** in der Seitenleiste → **API-Tokens für Anbindungen** →
    **Verwalten** (Seite **Meine API-Tokens**). Administratoren sehen unter
    **Administration → API-Tokens** außerdem die Tokens **aller**.

![API-Tokens](../assets/screenshots/administration/api-tokens.png)

## Wie sich ein Token verhält {#how-a-token-behaves}

- Er handelt **mit genau den Rechten des Kontos, zu dem er gehört**. Der
  Token eines Ablesers kann nur, was der Ableser kann.
- Er wird **nur einmal** angezeigt, direkt nach dem Erstellen. Kopier ihn
  dann; nachschlagen lässt er sich später nicht.
- Er hört auf zu funktionieren, wenn er abläuft, widerrufen wird oder das
  Passwort des Kontos geändert oder zurückgesetzt wird. Auch das
  Deaktivieren des Kontos stoppt ihn.

Behandle einen Token wie ein Passwort. Könnte er nach außen gelangt sein,
widerruf ihn.

## Neuer Token {#new-token}

| Feld / Schaltfläche | Was es bewirkt |
|---|---|
| **Benutzer** | *Nur auf der Administratorseite.* Als welches Konto der Token handelt. Du kannst Tokens für dich selbst anlegen und für Konten **ohne** vollen Zugriff -- typischerweise ein eigenes Konto für eine Anbindung, das sich selbst nie anmeldet. Tokens für andere Konten mit vollem Zugriff gehen nicht, weil ein Token still im Namen dieser Person handeln würde. |
| **Name** | Pflicht, bis zu 100 Zeichen. Sag, wofür er ist, z. B. „Claude Wissensdatenbank“. |
| **Läuft ab** | **nach 30 Tagen**, **nach 90 Tagen**, **nach 365 Tagen** (Vorgabe) oder **nie**. Nimm lieber ein Ablaufdatum. |
| **Nur MCP-Connector (für einen KI-Client)** | Erscheint nur, wenn das Modul **MCP-Connector für KI-Clients** an ist. So ein Token funktioniert nur für die KI-Anbindung und nur mit Notizen, die für die KI freigegeben sind; jede andere Nutzung wird abgelehnt. Für einen KI-Assistenten nimm immer diese Art. |
| **Token erstellen** | Erstellt den Token und zeigt ihn in einem grünen Kasten: *Jetzt kopieren: Er wird nur dieses eine Mal angezeigt …* |

## Die Tokenliste {#the-token-list}

| Spalte / Schaltfläche | Was sie zeigt oder bewirkt |
|---|---|
| **Name** | Der Name, die ersten Zeichen des Tokens (zum Wiedererkennen) und gegebenenfalls ein Badge **Nur MCP**. |
| **Benutzer** | *Nur auf der Administratorseite.* Wessen Token es ist. |
| **Erstellt** | Erstellungsdatum. |
| **Zuletzt benutzt** | Wann ein Programm ihn zuletzt genutzt hat, oder **nie**. |
| **Läuft ab** | Ablaufdatum oder **nie**. |
| **Status** | **aktiv**, **abgelaufen**, **widerrufen** oder **beendet** (das Passwort wurde nach dem Erstellen des Tokens geändert). |
| **Widerrufen** | Nur bei aktiven Tokens. Nach der Bestätigung funktioniert der Token sofort nicht mehr. |

**Noch keine API-Tokens.** erscheint, wenn es keine gibt.

## Einen KI-Assistenten mit den Notizen verbinden {#connecting-an-ai-assistant-to-the-notes}

Mit dem Modul **MCP-Connector für KI-Clients** kann ein KI-Assistent wie
Claude die [Notizen](../modules/notes.md), die du für ihn freigegeben hast,
durchsuchen und lesen -- und, wenn du es erlaubst, schreiben --, sonst
nichts. Kurz gesagt:

1. Schalte **MCP-Connector für KI-Clients** (und **Notizen**) unter
   [Module ein- und ausschalten](modules.md) ein.
2. [Lade](users.md) ein eigenes Konto für den Assistenten ein und steck es
   in eine [Gruppe](groups.md), die nur Lesen (und auf Wunsch Schreiben)
   für **Notizen** gewährt.
3. Erstell hier einen Token für dieses Konto mit angehaktem **Nur
   MCP-Connector**.
4. Gib Notizen für die KI frei, indem du ihnen das Freigabe-Schlagwort aus
   dem Notizen-Kapitel gibst.

Gib nur Notizen frei, die keine personenbezogenen Daten enthalten: Sie gehen
an einen externen KI-Dienst. Die Schritt-für-Schritt-Einrichtung für jeden
KI-Client steht in der
[MCP-Einrichtungsanleitung](https://github.com/parcella-garden/parcella/blob/main/docs/mcp-setup.md).

## Für Entwickler {#for-developers}

Die REST-API selbst -- Endpunkte, Authentifizierung, Beispiele -- ist in der
[Entwicklerdokumentation](https://github.com/parcella-garden/parcella#rest-api)
beschrieben und interaktiv unter **Administration → API-Dokumentation
(Swagger)**.

## Siehe auch {#related}

- [Erste Anmeldung und dein Konto](../getting-started/first-login.md#change-password)
- [Benutzer und Einladungen](users.md)

# Systeeminformatie en updates {#system-information-and-updates}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

De pagina Systeem toont welke versie van Parcella u gebruikt, of er een
nieuwere beschikbaar is, en is het beginpunt voor back-ups.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Open **Administratie → Systeem**.

![Systeem](../assets/screenshots/administration/system.png)

## Updatemelding {#update-notice}

Parcella vraagt regelmatig aan GitHub, waar het wordt gepubliceerd, of
er een nieuwere versie is uitgebracht. Er wordt niets over uw vereniging
verstuurd. U kunt dit uitzetten onder
[Verenigingsinstellingen → Updates](settings.md#updates); de
updatemelding verdwijnt dan van deze pagina.

**Bent u up-to-date**, dan ziet u

> Versie v1.2.3 -- up-to-date (laatst gecontroleerd: 18.11.2026 14:05)

of **... nog niet op updates gecontroleerd** direct na de installatie.

**Bestaat er een nieuwere versie**, dan toont een gemarkeerd vak
**Update beschikbaar:** met het nieuwe versienummer, de versie die u
gebruikt, en de vier commando's die de update op de server installeren.

| Knop | Wat het doet |
|---|---|
| **Nu controleren** | Vraagt het GitHub meteen in plaats van op de volgende automatische controle te wachten (elke zes uur). |

!!! note "Bijwerken gebeurt op de server"
    De update zelf is geen knop in Parcella. Wie de server beheert, typt
    de commando's uit het vak. Geef ze door als u dat niet bent.
    Download eerst een [back-up](backup.md).

    Het vak waarschuwt ook dat het eerste commando het
    configuratiebestand van de server door het actuele vervangt.
    Wijzigingen die de serverbeheerder in dat bestand heeft gemaakt,
    gaan verloren, tenzij hij ze in een apart overschrijvingsbestand
    bewaart, zoals de installatie-instructies uitleggen.

Lees vóór het bijwerken de releasenotes op GitHub, om te zien wat er is
veranderd.

## Back-up {#backup}

De kaart **Back-up** heeft drie knoppen:

| Knop | Wat het doet |
|---|---|
| **Cloudback-ups** | Opent het schema voor automatische back-ups naar uw cloudopslag. |
| **Herstellen vanaf back-up** | Opent de herstelpagina. |
| **Back-up downloaden** | Downloadt meteen een volledige back-up. |

Alle drie staan beschreven in [Back-up en herstel](backup.md).

## Gerelateerd {#related}

- [Back-up en herstel](backup.md)
- [Verenigingsinstellingen](settings.md#updates)

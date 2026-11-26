# Back-up en herstel {#backup-and-restore}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Een back-up is een volledige kopie van de Parcella-gegevens van uw
vereniging in één bestand. Daarmee krijgt u alles terug na een kapotte
server, een vergissing, of een verhuizing naar een andere host. Maak
regelmatig back-ups, en bewaar ze ergens anders dan op de
Parcella-server.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Alles begint bij **Administratie → Systeem**.

## Wat een back-up bevat {#what-a-backup-contains}

Eén `.zip`-bestand met:

- de hele database -- elk lid, perceel, elke meterstand, factuur,
  instelling en elk gebruikersaccount,
- geüploade bestanden die in Parcella worden bewaard: het logo,
  afbeeldingen van mededelingen, avatars en procesbestanden,
- de sleutel waarmee Parcella opgeslagen wachtwoorden versleutelt
  (mailserver, website, cloudopslag, helpdesk).

!!! warning "Behandel een back-up als een wachtwoord"
    Omdat ze die sleutel en alle persoonsgegevens van uw leden bevat,
    kan iedereen met het bestand alles lezen. Bewaar het waar alleen het
    bestuur erbij kan.

Bestanden in uw cloudopslag (perceelmappen, bijlagen van facturen,
notitiebestanden) zitten **niet** in de back-up -- die staan al in de
cloud, die een eigen back-up heeft.

## Een back-up downloaden {#download-a-backup}

Op **Administratie → Systeem** heeft de kaart **Back-up** de knop
**Back-up downloaden**. Uw browser downloadt het zip-bestand meteen. Er
wordt niets op de server opgeslagen, dus dit bestand is de enige kopie:
bewaar het op een veilige plek.

Gaat er iets mis, dan ziet u **Back-up mislukt:** gevolgd door de reden.

## Herstellen vanaf back-up {#restore-from-backup}

![Herstellen vanaf back-up](../assets/screenshots/administration/backup-restore.png)

Open de pagina met **Herstellen vanaf back-up** op de pagina Systeem.

!!! danger "Dit overschrijft alle huidige gegevens"
    Herstellen vervangt de **volledige** database en alle geüploade
    bestanden door de inhoud van de back-up. Alles wat sinds die back-up
    is ingevoerd, is weg, ook gebruikersaccounts en wachtwoorden die
    sindsdien zijn aangemaakt. Dit kan niet ongedaan worden gemaakt.
    Wilt u misschien terug, **download dan eerst een back-up van de
    huidige stand**.

| Veld / knop | Wat het doet |
|---|---|
| **Back-upbestand (.zip)** | Kies een back-upbestand dat uit Parcella is gedownload (maximaal 200 MB). |
| **Typ RESTORE om te bevestigen** | Typ het woord `RESTORE` in hoofdletters. Dat beschermt tegen per ongeluk herstellen. |
| **Annuleren** | Terug naar de pagina Systeem. |
| **Herstellen** | Vraagt nog één keer, en herstelt dan. Dat kan even duren. |

Daarna ziet u **Herstel succesvol voltooid.** Iedereen -- ook u -- werkt
nu met de gegevens zoals ze waren toen de back-up werd gemaakt; u moet
misschien opnieuw inloggen met het wachtwoord dat toen gold.

Mogelijke meldingen:

| Melding | Betekenis |
|---|---|
| **Bevestigingszin kwam niet overeen -- er is niets gewijzigd.** | Het woord was niet precies `RESTORE`. |
| **Het bestand is te groot.** | Meer dan 200 MB. |
| **Het back-upbestand heeft een onverwachte structuur: ...** | Geen Parcella-back-up, of een beschadigd bestand. Er is niets gewijzigd. |
| **Herstellen mislukt, er is niets gewijzigd: ...** | Het herstellen van de database is mislukt en uw gegevens zijn als voorheen. |
| **Database succesvol hersteld, maar het herstellen van geüploade bestanden is mislukt: ...** | De gegevens zijn hersteld maar sommige bestanden niet. Het herstel opnieuw uitvoeren is veilig. |

Back-ups uit een oudere Parcella-versie kunnen in een nieuwere worden
hersteld; wie voor de server zorgt, moet daarna misschien de database-update
uitvoeren.
<!-- TODO(verify): whether the app applies pending database migrations by itself after a restore of an older backup, or whether the server admin must always run them (developer docs say a restore doesn't run them). -->

## Cloudback-ups {#cloud-backups}

![Cloudback-ups](../assets/screenshots/administration/backup-cloud.png)

Open de pagina met **Cloudback-ups** op de pagina Systeem. Parcella kan
dezelfde back-up automatisch maken en naar uw cloudopslag uploaden.

Daarvoor moet de module **Cloudopslag** aan staan en een opslag zijn
ingericht onder [Integraties](integrations.md#cloud-storage). Anders zegt
de pagina wat er ontbreekt, met een link.

### Schema {#schedule}

| Veld / knop | Wat het doet |
|---|---|
| **Automatisch back-uppen naar de cloud** | Zet automatische back-ups aan of uit. |
| **Bestemmingsmap** | Map in de cloudopslag, bijv. `backups/parcella`. Wordt aangemaakt als ze niet bestaat. Kies een map die alleen het bestuur kan openen -- elke back-up bevat de sleutel van de opgeslagen wachtwoorden. |
| **Frequentie** | **Elk uur**, **Dagelijks** (standaard), **Wekelijks** of **Maandelijks**. |
| **Zoveel back-ups bewaren** | Hoeveel back-ups worden bewaard, minstens 1 (standaard 10). Komt er een nieuwe bij, dan worden de oudste boven dit aantal verwijderd. Alleen de eigen back-upbestanden van Parcella worden aangeraakt. |
| **Opslaan** | Slaat het schema op (**Opgeslagen.**). |
| **Nu back-uppen naar de cloud** | Maakt en uploadt meteen een back-up, of automatische back-ups nu aan staan of niet. |

Onder de velden ziet u het resultaat van de laatste uitvoering:
**Laatste cloudback-up: ... (gelukt).**, **... -- mislukt:** met de
reden, of **Er is nog geen cloudback-up uitgevoerd.** Kijk er af en toe
naar -- een back-up die wekenlang zonder melding mislukt, is geen
back-up.

### Back-ups in de cloud {#backups-in-the-cloud}

Een lijst van de back-ups in de bestemmingsmap, de nieuwste eerst, met
**Naam**, **Grootte** en **Laatst gewijzigd**. **Nog geen back-ups in
deze map.** als er geen zijn.

Om er een te herstellen, typt u `RESTORE` in het veld in haar rij en
klikt u op **Herstellen**. Dezelfde waarschuwing als hierboven geldt: het
overschrijft alle huidige gegevens.

## Goede gewoonten {#good-practice}

- Download een back-up vóór grote wijzigingen: een update, een grote
  import, een factuurronde.
- Bewaar ook minstens één kopie buiten de cloudopslag, bijv. op een
  versleutelde USB-stick in de kluis van de vereniging.
- Test af en toe een back-up door haar op een losse testinstallatie te
  herstellen. Een back-up die u nooit hebt hersteld, is alleen een
  hoop.

## Gerelateerd {#related}

- [Systeeminformatie en updates](system.md)
- [Integraties](integrations.md#cloud-storage)

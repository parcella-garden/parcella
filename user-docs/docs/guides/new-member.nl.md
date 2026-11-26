# Een nieuw lid verwelkomen {#welcoming-a-new-member}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Iemand meldt zich aan voor een tuin, krijgt een perceel aangeboden, zegt
ja -- en wordt lid en huurder. Dit stappenplan volgt dat pad door
Parcella, van de aanmelding tot het welkom.

Er zijn twee manieren om iemand lid te maken:

- **Vanuit een aanmelding** (stap 1-6): de persoon staat op uw
  [wachtlijst](../glossary.md#applicant) in **Aanmelders**. **Perceel
  toewijzen** regelt dan in één keer de ledengegevens, de
  [huur](../glossary.md#tenancy) en het factuuradres. Dit is de gewone
  weg.
- **Met de hand** (stap 7): voor iemand die nooit via de wachtlijst is
  gegaan, of een perceel dat niet beëindigd is.

!!! info "Wie kan dit doen"
    Werken met aanmeldingen vraagt **schrijf**recht op **Aanmelders**;
    het perceel toewijzen vraagt ook **schrijven** op **Leden en
    percelen**. Bestuursleden en beheerders hebben beide. De module
    **Aanmelders** staat standaard aan.

## 1. De aanmelding komt binnen {#1-the-application-comes-in}

Aanmeldingen komen op twee manieren binnen:

- **Via uw website**, als de vereniging daar het aanmeldformulier heeft
  en de **Openbare aanmeldformulier-API** aan staat (zie
  [Integraties](../administration/integrations.md)). Ze verschijnen
  vanzelf.
- **Met de hand**, voor aanmeldingen per telefoon, brief of persoonlijk:
  open **Aanmelders**, klik op **Aanmelder toevoegen**, vul minstens het
  **E-mailadres** in (het enige verplichte veld), plus naar wens
  **Voornaam**, **Achternaam**, **Telefoon**, **Bericht van de
  aanmelder** en een **Notitie van het bestuur**, en klik op
  **Opslaan**.

Om een oude aanmelding van een papieren wachtlijst in te voeren, zet u
**Aangemeld op** op de oorspronkelijke datum. De aanmeldingsdatum
bepaalt de volgorde van de wachtlijst.

Nieuwe aanmeldingen tonen een teller naast **Aanmelders** in de zijbalk
en op het dashboard, tot iemand ze verder heeft gezet.

!!! tip "Rode vlag"
    Komt de naam, het e-mailadres of het telefoonnummer van een aanmelder
    overeen met een extern contact met uw label „rode vlag“, dan tonen de
    lijst en de pagina van de aanmelder een waarschuwing **Rode vlag**.
    Zie [Aanmelders](../modules/applicants.md).

## 2. Contact opnemen {#2-get-in-touch}

1. Open **Aanmelders** en klik op de nieuwe aanmelding.
2. Controleer en bewerk in het vak **Aanvrager contacteren** de tekst
   van de e-mail. Het onderwerp is *„Bedankt voor je aanmelding op onze
   wachtlijst!“*.
3. Klik op **Verzenden** en bevestig.

Parcella mailt de tekst naar de aanmelder en zet de status op
**Gecontacteerd**. Het vak staat er alleen zolang de status **Nieuw**
is. Hebt u op een andere manier contact gehad, wijzig de status dan
gewoon met de hand (volgende stap).

De standaardtekst van deze e-mail kunt u wijzigen in **Administratie →
Instellingen → Aanmelders → Tekst van de e-mail aan nieuwe aanvragers**.

## 3. De status van de aanmelding bijhouden {#3-track-the-applications-status}

Naarmate het vordert, opent u de aanmelding, kiest u de nieuwe
**Status** en klikt u op **Opslaan**:

| Status | Betekenis |
|---|---|
| **Nieuw** | Net binnengekomen. |
| **Gecontacteerd** | U hebt contact gehad; de aanmelder staat op de wachtlijst. |
| **Tuin aangeboden** | U hebt een bepaald perceel aangeboden. |
| **Geaccepteerd** | De aanmelder wil het perceel; de overdracht wordt geregeld. |
| **Afgewezen** | Geen verdere aanbiedingen. |
| **Afgesloten (tuin toegewezen)** | Automatisch gezet door **Perceel toewijzen** (stap 5). |

Slaat een aanmelder een perceel af maar wil hij op de lijst blijven, zet
hem dan terug op **Gecontacteerd**. Elke statuswijziging staat onder
**Statusgeschiedenis** op de pagina van de aanmelding.

## 4. Zorg dat het perceel beëindigd is {#4-make-sure-the-parcel-is-terminated}

**Perceel toewijzen** biedt alleen percelen met de status **beëindigd**
aan -- het perceel dat iemand heeft verlaten of binnenkort verlaat.

1. Open het perceel onder **Percelen** en klik op **Bewerken**.
2. Zet **Status** op **beëindigd**, voeg eventueel een
   **Beëindigingsnotitie** toe, en klik op **Wijzigingen opslaan**.

Is de vertrekkende huurder nog midden in het vertrek, zie dan
[Een perceel overdragen](parcel-handover.md) -- dat behandelt de hele
overdracht, ook de kant van de oude huurder.

## 5. Het perceel toewijzen {#5-assign-the-parcel}

1. Open de aanmelding en klik op **Perceel toewijzen**. (De knop staat
   er bij elke open aanmelding -- **Nieuw**, **Gecontacteerd**, **Tuin
   aangeboden** of **Geaccepteerd**.)
2. Kies het **Beëindigd perceel**. De lijst toont elk perceel met zijn
   huidige huurders.
3. Stel de **Overdrachtsdatum** in -- de dag waarop de nieuwe huurder
   overneemt. Die mag in de toekomst liggen.
4. Vink eventueel **Verdere kandidaten (medepachters)** aan --
   bijvoorbeeld een partner die zich apart aanmeldde en het perceel samen
   met deze aanmelder overneemt.
5. Vul eventueel de **Documentenmap voor de nieuwe pachters** in (alleen
   getoond als u cloudmappen mag beheren).
6. Klik op **Voorbeeld**.
7. Controleer het vak **Overdracht van perceel … op …**:
    - **Huidige pachters**: hun huur eindigt op de overdrachtsdatum.
      Huren ze geen ander perceel, dan eindigt hun lidmaatschap de dag
      ervoor.
    - **Nieuwe pachters en factuurontvangers**: elke aanmelder **wordt
      nieuw lid** (naam, e-mail en telefoon uit de aanmelding) of wordt,
      als een actief lid al hetzelfde e-mailadres gebruikt, aan dat
      bestaande lid gekoppeld.
8. Klik op **Perceel overdragen** en bevestig.

Wat er in één stap gebeurt:

- De aanmelders worden lid, met **Lid sinds** op de overdrachtsdatum.
- Ze worden vanaf de overdrachtsdatum huurder van het perceel, met
  **Gebruiken als factuuradres** ingesteld.
- De oude huurders worden voormalige huurders -- de geschiedenis blijft
  op de perceelpagina.
- De status van het perceel gaat terug naar **actief**.
- De aanmeldingen worden op **Afgesloten (tuin toegewezen)** gezet.

Met een overdrachtsdatum in de toekomst blijven de oude huurders tot die
dag huurder, lid en factuurontvanger; de nieuwe worden op de
perceelpagina als toekomstig („vanaf …“) getoond en nemen op die datum
over.

## 6. De gegevens van het nieuwe lid aanvullen {#6-complete-the-new-members-record}

De overdracht neemt alleen naam, e-mail en telefoon over. Vul de rest
aan:

1. Open **Leden** en klik op het nieuwe lid (of volg de link vanaf de
   perceelpagina).
2. Klik op **Bewerken** en vul **Geboortedatum**, **IBAN** en het adres
   (**Straat en huisnummer**, **Postcode**, **Plaats**) aan.
3. Controleer **Mag informatie per e-mail ontvangen**. Het is aangevinkt
   bij leden die door **Perceel toewijzen** zijn aangemaakt, omdat de
   aanmelder een e-mailadres opgaf; vink het uit als het lid alleen
   papier wil. Zonder dat gaan facturen en mededelingen naar de
   afdrukstapel in plaats van de inbox.
4. Vink onder **Tags** bestaande tags aan of typ nieuwe (bijvoorbeeld
   „hagenteam“), gescheiden door komma's.
5. Klik op **Wijzigingen opslaan**.

U kunt tags ook direct op de pagina van het lid toevoegen, in de kaart
**Tags**, met **Tag toevoegen**.

## 7. Zonder aanmelding: het lid met de hand aanmaken {#7-without-an-application-create-the-member-by-hand}

1. Open **Leden** en klik op **Nieuw lid**.
2. Vul **Voornaam** en **Achternaam** in (verplicht), het adres,
   **Geboortedatum**, **IBAN**, **Lid sinds**, een **E-mailadres** en
   **Telefoonnummer**, **Mag informatie per e-mail ontvangen** en
   eventuele **Tags**.
3. Klik op **Lid aanmaken**.
4. Kies op de pagina van het lid, in **Toegewezen percelen**, het perceel
   onder **Kies perceel…**, laat **Gebruiken als factuuradres**
   aangevinkt als dit lid de facturen van het perceel moet krijgen, en
   klik op **Toewijzen**.

U kunt ook toewijzen vanaf de pagina van het perceel: **Huidige
huurders → Kies lid… → Toewijzen**, waar u ook de begindatum kunt
invullen. Om de begindatum later te corrigeren, gebruikt u het
potloodpictogram naast de huurder op de perceelpagina (**Huur
bewerken**, veld **Huurder sinds**).

Staat er nog een oude huurder op het perceel, beëindig dan eerst zijn
huur -- zie [Een perceel overdragen](parcel-handover.md).

## 8. Het nieuwe lid welkom heten {#8-welcome-the-new-member}

Parcella heeft geen automatische welkomstmail. Twee dingen helpen:

**Een proces voor het verwelkomen.** De module **Processen** heeft een
voorbeeldsjabloon, **Nieuw lid verwelkomen**, met drie fasen: **Welkom**
(**Welkomstgesprek**, **Statuten en tuinreglement overhandigd**),
**Papierwerk** (**Ondertekend aanmeldformulier**, **Machtiging
automatische incasso ontvangen**) en **Afronding** (**Toegevoegd aan de
mailinglijst**, **Notities**).

1. Eén keer: open **Processen → Sjablonen** en klik onder **Beginnen met
   een voorbeeld** op **Gebruiken** naast **Nieuw lid verwelkomen**. Pas
   fasen en velden naar wens aan. (Sjablonen aanmaken vraagt volledige
   toegang.)
2. Voor elk nieuw lid: klik op de pagina van het lid, in de kaart
   **Processen**, op **Proces starten**, kies het **Sjabloon** en klik
   op **Starten**.
3. Vul de velden in naarmate dingen gebeuren en klik op **Klaar --
   volgende fase**. Verplichte velden moeten zijn ingevuld voordat u
   verder kunt.

**Een persoonlijk bericht.** Staat de module **Mededelingen** aan, vink
dan het nieuwe lid aan in de lijst **Leden** en klik op **Selectie
aanschrijven**.

## Gerelateerd {#related}

- [Aanmelders](../modules/applicants.md)
- [Leden](../modules/members.md)
- [Percelen](../modules/parcels.md)
- [Processen](../modules/processes.md)
- [Mededelingen](../modules/announcements.md)
- [Een perceel overdragen](parcel-handover.md)
- Woordenlijst: [aanmelder](../glossary.md#applicant),
  [huur](../glossary.md#tenancy),
  [factuuradres](../glossary.md#invoice-address)

# Een nieuwe vereniging inrichten {#setting-up-a-new-club}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Parcella is geïnstalleerd en draait. Dit stappenplan brengt u van de
allereerste aanmelding naar een installatie waarmee het hele bestuur kan
werken: een veilig beheerderswachtwoord, de gegevens en het logo van uw
vereniging, de juiste taal, alleen de modules die u nodig hebt,
accounts voor de andere bestuursleden en -- als u wilt -- eerst een
proefronde met voorbeeldgegevens.

Reken op ongeveer een uur. U hebt het beheerdersaccount nodig dat bij de
installatie is ontstaan.

!!! info "Wie kan dit doen"
    Alles hier gebeurt in **Administratie**, die alleen beheerders (en
    groepen met **Toegang tot het administratiepaneel**) kunnen openen.
    Zie [Rollen, groepen en rechten](../getting-started/roles-and-permissions.md).

## 1. Inloggen en het beheerderswachtwoord wijzigen {#1-log-in-and-change-the-admin-password}

1. Open Parcella in uw browser en log in met het beheerdersaccount van de
   installatie.
   <!-- TODO(verify): the default login (admin@parcella.local / admin1234) is documented for developers; confirm whether self-hosters get the same default or set their own during installation before naming it here. -->
2. Gebruikt het account nog het standaardwachtwoord van de installatie,
   dan opent Parcella meteen **Wachtwoord wijzigen** en toont: *„Dit
   account gebruikt nog het standaardwachtwoord van de eerste
   installatie. Kies een nieuw wachtwoord -- tot die tijd blijft de rest
   van de applicatie vergrendeld.“*
3. Vul **Huidig wachtwoord** in, dan **Nieuw wachtwoord** en **Bevestig
   nieuw wachtwoord**, en klik op **Wachtwoord wijzigen**.

U kunt het wachtwoord altijd opnieuw wijzigen via het gebruikersmenu
onderaan de zijbalk: **Wachtwoord wijzigen**.

!!! warning
    Sla dit niet over bij een installatie die vanaf internet bereikbaar
    is. Iedereen die het standaardwachtwoord kent, zou anders als
    beheerder kunnen inloggen.

Meer: [Eerste aanmelding en uw account](../getting-started/first-login.md).

## 2. De gegevens van uw vereniging invullen {#2-enter-your-clubs-details}

1. Open in de zijbalk **Administratie → Instellingen**. De pagina heet
   **Verenigingsinstellingen**.
2. Vul op de kaart **Verenigingsgegevens** **Verenigingsnaam**,
   **Straat**, **Postcode**, **Plaats**,
   **Verenigingsregistratienummer** en **Kamer van Koophandel** in. De
   naam verschijnt in paginakoppen; de rest gaat in de voettekst van
   brieven en facturen.
3. Zoek en vink in **Bestuursleden** de leden aan die nu in het bestuur
   zitten. U kunt alleen mensen kiezen die al als lid bestaan -- kom hier
   terug na stap 9 of na de [import](csv-import.md).
4. Vul in **Oppervlakten (m²)** de **Totale oppervlakte (m²)** van het
   terrein in en **Oppervlakte C (gemeentelijk, m²)** als u die hebt.
   **Oppervlakte A (percelen, m²)** en **Oppervlakte B (gemeenschappelijk,
   m²)** berekent Parcella uit uw percelen.
5. Klik op **Instellingen opslaan**. U ziet *„Instellingen opgeslagen.“*

!!! tip
    De instellingenpagina is lang. Gebruik het veld **Instellingen
    zoeken...** bovenaan om op naam naar een veld te springen.

## 3. Uw logo toevoegen {#3-add-your-logo}

1. Zoek, nog steeds in **Administratie → Instellingen**, de kaart
   **Huisstijl**.
2. Kies in **Verenigingslogo** een PNG-, JPEG-, WebP- of SVG-bestand van
   maximaal 2 MB.
3. Klik op **Instellingen opslaan**.

Het logo vervangt het Parcella-logo op de inlogpagina en in de zijbalk.
Om terug te gaan naar de standaard, vinkt u **Logo verwijderen (terug
naar het standaardicoon)** aan en slaat u op.

## 4. Taal, regio en valuta kiezen {#4-choose-language-region-and-currency}

Dit zijn bewust drie aparte instellingen: een vereniging kan
bijvoorbeeld een Engelse interface gebruiken, maar Duitse getal- en
adresnotatie.

1. **Taal** -- de taal van de hele installatie. Iedereen ziet dezelfde.
2. **Regio** -- de notatie van getallen en adressen
   (duizendtalscheidingsteken, volgorde van postcode en plaats).
3. **Valuta** -- het symbool en de plaats ervan („19,99 €“ of „£19.99“).
4. Klik op **Instellingen opslaan**.

## 5. Uitgaande e-mail instellen {#5-set-up-outgoing-email}

Parcella verstuurt per e-mail uitnodigingen, meldingen, mededelingen en
facturen. Zonder mailserver kunnen de uitnodigingen in stap 9 niet worden
verstuurd.

1. Zoek in **Administratie → Instellingen** de kaart **E-mail (SMTP)**.
2. Vul **SMTP-server**, **SMTP-poort**, **SMTP-gebruiker**,
   **SMTP-wachtwoord** en **Afzender e-mail** in -- deze waarden krijgt u
   van uw e-mailprovider.
3. Klik op **Instellingen opslaan**.

Na het opslaan toont het wachtwoordveld alleen dat er een wachtwoord is
ingesteld; om het te wijzigen, typt u een nieuw.

## 6. Modules in- en uitschakelen {#6-turn-modules-on-and-off}

Niet elke vereniging gebruikt elk functiegebied. Een module uitschakelen
verbergt haar in de navigatie; de gegevens blijven en komen terug als u
haar weer inschakelt.

1. Zoek in **Administratie → Instellingen** de kaart **Functiegebieden**.
2. Vink de modules aan die uw vereniging gebruikt en vink de rest uit.
   Elke module heeft een korte beschrijving.
3. Klik op **Instellingen opslaan**.

Een paar modules staan op een nieuwe installatie **uit**, omdat ze
gegevens naar buiten sturen of iets voor het publiek openen:
**Financiën**, **Mededelingen**, **Cloudopslag**, **Support
(helpdesk)**, **Nextcloud Deck-synchronisatie**, **MCP-connector voor
AI-clients** en de drie openbare API's voor de website. Schakel ze pas in
als u ze nodig hebt.

Meer: [Modules in- en uitschakelen](../administration/modules.md).

## 7. Het uitproberen met voorbeeldgegevens (optioneel) {#7-try-things-out-with-sample-data-optional}

Voordat u echte gegevens invoert, kunt u de lege installatie vullen met
verzonnen leden, percelen, meters, werksessies en meer, rondklikken, en
alles weer weghalen.

1. Open **Administratie → Voorbeeldgegevens**.
2. Lees **Wat dit toevoegt**, klik dan op **Voorbeeldgegevens
   toevoegen** en bevestig.
3. Verken de modules. Probeer een factuurronde, leg een meterstand vast,
   draag een perceel over.
4. Bent u klaar, ga dan terug naar **Administratie → Voorbeeldgegevens**
   en klik op **Alle voorbeeldgegevens verwijderen**, en bevestig.

!!! warning "Verwijder de voorbeeldgegevens voordat u live gaat"
    - Voorbeeldgegevens kunnen alleen aan een nieuwe installatie worden
      **toegevoegd**. Zodra er één echt lid of perceel bestaat, is de
      knop geblokkeerd.
    - **Alle voorbeeldgegevens verwijderen** verwijdert precies wat de
      generator heeft gemaakt, en niets wat u zelf hebt ingevoerd. Wat u
      tijdens het proberen *aan* een voorbeeldrecord koppelt (een stand
      op een voorbeeldmeter, een betaling op een voorbeeldfactuur), wordt
      misschien niet netjes verwijderd. Verwijder eerst de
      voorbeeldgegevens, voer daarna de echte in.
      <!-- TODO(verify): what happens on removal if a real record references a sample record (e.g. a finalized invoice run built from sample parcels)? -->
    - Voorbeeldgegevens maken of wijzigen geen gebruikersaccounts.

Meer: [Voorbeeldgegevens](../administration/sample-data.md).

## 8. Groepen aanmaken {#8-create-groups}

Nieuwe gebruikersaccounts krijgen hun toegang uit **groepen**, niet uit
een vaste rol. Maak eerst de groepen aan en nodig daarna mensen erin uit.

1. Open **Administratie → Groepen**.
2. Vul in **Groep aanmaken** een **Naam** (bijvoorbeeld „Bestuur“) en een
   **Omschrijving** in.
3. Vink voor het bestuur **Volledige toegang tot elke module** aan.
   **Toegang tot het administratiepaneel** vinkt u alleen aan voor mensen
   die ook gebruikers en instellingen moeten beheren.
4. Klik op **Groep aanmaken**.
5. Maak voor smallere taken meer groepen aan en vink in de rechtentabel
   **Lezen**, **Schrijven** en **Verwijderen** per **Module** aan --
   bijvoorbeeld „Waterteam“ met lezen en schrijven voor **Water**, of
   „Penningmeester“ met volledige rechten voor **Financiën**. Klik op
   **Opslaan**.

!!! tip
    Iedereen die kan inloggen, kan altijd leden en percelen *bekijken*.
    Groepen breiden de toegang daarvandaan uit; ze nemen nooit iets weg.

Meer: [Groepen](../administration/groups.md) en
[Rollen, groepen en rechten](../getting-started/roles-and-permissions.md).

## 9. De andere bestuursleden uitnodigen {#9-invite-the-other-board-members}

1. Open **Administratie → Gebruikers** (de pagina heet
   **Gebruikersbeheer**).
2. Vul in **Gebruiker uitnodigen** het **E-mailadres** van de persoon in
   en vink zijn **Groepen** aan.
3. Klik op **Uitnodiging verzenden**.
4. De persoon krijgt een e-mail met een link. Op **Stel uw account in**
   vult hij zijn **Naam** en **Wachtwoord** (minstens 8 tekens) in en
   klikt hij op **Account aanmaken**.

De uitnodiging is 7 dagen geldig en staat in **Openstaande
uitnodigingen** tot ze is geaccepteerd. Van daaruit kunt u **Uitnodiging
opnieuw verzenden** (wat haar ook verlengt) of **Uitnodiging
verwijderen**.

!!! warning
    De uitnodiging gaat per e-mail, dus stel eerst **E-mail (SMTP)** in
    (stap 5). Kan ze niet worden verzonden, dan zegt de pagina dat;
    herstel de mailinstellingen en gebruik **Uitnodiging opnieuw
    verzenden**.

Meer: [Gebruikers en uitnodigingen](../administration/users.md).

## 10. Cloudopslag koppelen (optioneel) {#10-connect-cloud-storage-optional}

Bewaart uw vereniging huurcontracten en andere documenten in Nextcloud
(of een andere ondersteunde opslag), dan kan Parcella op de pagina van
elk perceel een documentenmap tonen.

1. Open **Administratie → Integraties** en zoek **Cloudopslag
   (perceeldocumenten, facturen, back-ups)**.
2. Kies het **Type opslag** en vul de verbindingsgegevens in die het
   vraagt. Klik op **Opslaan**, dan op **Verbinding testen**.
3. Stel eventueel de gedeelde mappen eronder in: **Map voor inkomende
   facturen**, **Map voor documenten van externe contacten**,
   **Notitiemap**, **Map voor procesbestanden**, **Map voor geprinte
   mededelingen**.
4. Ga naar **Administratie → Instellingen → Functiegebieden**, vink
   **Cloudopslag** aan en klik op **Instellingen opslaan**.
5. Stel op de pagina van elk perceel het **Mappad** in onder
   **Documenten (cloudopslag)** -- typ het of gebruik **Bladeren…** -- en
   klik op **Opslaan**.

Paden zijn altijd relatief ten opzichte van de gekozen opslag. Parcella
maakt of deelt geen mappen voor u; doe dat eerst in uw cloud.

Meer: [Integraties](../administration/integrations.md).

## 11. Uw echte gegevens invoeren of importeren {#11-enter-or-import-your-real-data}

Voeg nu uw percelen en leden toe -- met de hand via **Percelen → Nieuw
perceel** en **Leden → Nieuw lid**, of in één keer vanuit een
spreadsheet: zie [Leden en percelen importeren](csv-import.md). Wijs
daarna elk lid toe aan zijn perceel (zie
[Een nieuw lid verwelkomen](new-member.md), stap 7).

## 12. Uw eerste back-up maken {#12-make-your-first-backup}

1. Open **Administratie → Systeem** en zoek de kaart **Back-up**.
2. Klik op **Back-up downloaden** en bewaar het zip-bestand op een veilige
   plek.

De back-up bevat de database, de geüploade bestanden en de
versleutelingssleutel. Behandel haar als de ledenlijst zelf.

Meer: [Back-up en herstel](../administration/backup.md).

## Gerelateerd {#related}

- [Verenigingsinstellingen](../administration/settings.md)
- [Modules in- en uitschakelen](../administration/modules.md)
- [Gebruikers en uitnodigingen](../administration/users.md)
- [Groepen](../administration/groups.md)
- [Integraties](../administration/integrations.md)
- [Voorbeeldgegevens](../administration/sample-data.md)
- [Back-up en herstel](../administration/backup.md)
- [Leden en percelen importeren](csv-import.md)

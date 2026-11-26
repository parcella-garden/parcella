# Integraties {#integrations}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Integraties verbinden Parcella met de andere systemen die uw vereniging
gebruikt: de website van de vereniging, een cloudopslag, een helpdesk,
Nextcloud Deck en agenda-apps.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Open **Administratie → Integraties**.

![Integraties](../assets/screenshots/administration/integrations.png)

De pagina is een kolom met kaarten, elk dichtgeklapt; klik op een kop om
die te openen. Elke kaart slaat zelfstandig op met een eigen knop.

De meeste integraties vragen ook een module die is ingeschakeld onder
[Modules in- en uitschakelen](modules.md). De kaarten zeggen het als die
ontbreekt.

!!! note "De mailserver staat elders"
    De uitgaande mailserver (SMTP) stelt u in onder
    [Verenigingsinstellingen](settings.md#email-smtp), niet hier.

## Privé-agendafeeds {#private-calendar-feeds}

De kalendermodule biedt abonnementslinks (agendafeeds) voor de
verjaardagslijst en voor de aan- en afwezigheid van het bestuur, zodat
bestuursleden ze in de agenda-app op hun telefoon kunnen zien. Deze
links bevatten één gedeeld geheim en verlopen nooit.

| Knop | Wat het doet |
|---|---|
| **Opnieuw genereren** | Maakt na bevestiging een nieuw geheim aan. **Elk bestaand abonnement op deze feeds werkt niet meer**; abonnees moeten de nieuwe link van de kalenderpagina's kopiëren. U ziet **Token voor agendafeeds opnieuw gegenereerd. Bestaande abonnementen werken pas weer met de nieuwe URL.** |

Doe dit als een link in verkeerde handen kan zijn gekomen, of als iemand
die haar had het bestuur verlaat. Zie [Kalender](../modules/calendar.md).

## Publieke aanmeld-API {#public-signup-api}

Met deze kaart praat de website van uw vereniging met Parcella: tuinders
melden zich aan voor werksessies, sturen een contactbericht of melden
zich aan voor een tuin via formulieren op de website, zonder
Parcella-account.

Staat de module **Publieke aanmeld-API** uit, dan zegt een melding
bovenaan de pagina dat, met een link **Inschakelen bij Instellingen**.
Een vergelijkbare melding verschijnt in de kaart zolang de **Publieke
contactformulier-API** uit staat. Het aanmeldformulier voor een tuin
vraagt daarnaast de schakelaar **Openbare aanmeldformulier-API**.

Een website kan haar formulieren op twee manieren versturen, en u kunt
beide gebruiken.

### Met het API-token (websiteplug-in op de server) {#with-the-api-token-website-plugin-on-the-server}

Voor een website met een plug-in aan de serverkant -- een „connector“ --
die de formuliergegevens zelf naar Parcella stuurt.

| Element | Wat het doet |
|---|---|
| **API-token** | Het geheim dat de plug-in nodig heeft. Klik in het veld om het te selecteren en kopieer het naar de instellingen van de plug-in. |
| **Opnieuw genereren** | Maakt na bevestiging een nieuw token aan. **Elke plug-in die nog het oude gebruikt, werkt meteen niet meer**; vul het nieuwe overal in. U ziet *Er is een nieuw API-token gegenereerd ...* |
| **Eindpunten** | Een tabel met de webadressen die de plug-ins gebruiken, elk met **Methode**, **URL** en **Authenticatie** (**Geen (publiek leesbaar)**, het API-token, of **Toegestane websiteadressen**). Uw technische contactpersoon voor de website heeft dit nodig; u niet. |

De kaart eindigt met een notitie dat er een kant-en-klare WordPress-plug-in
bij het Parcella-project hoort.

### Websiteformulieren (eenvoudige HTML, WordPress-plug-in) {#website-forms-plain-html-wordpress-plugin}

Voor websites waarvan de formulieren rechtstreeks vanuit de browser van
de bezoeker naar Parcella gaan: eenvoudige HTML-pagina's op elk
websitesysteem, en de WordPress-plug-in vanaf versie 3.0. Er komt geen
token aan te pas, dus Parcella accepteert alleen formulieren van de
websites die u hier opgeeft. Zolang de lijst leeg is, zijn deze
formulieren gesloten.

| Veld / knop | Wat het doet |
|---|---|
| **Toegestane websiteadressen** | Eén webadres per regel, alleen schema en host, bijv. `https://example.org`. Noem elk adres waarop uw verenigingswebsite bereikbaar is, ook het eigen adres van de WordPress-site. Regels die geen webadres zijn, worden weggelaten en in een waarschuwing genoemd. |
| **ALTCHA vereisen (rekenpuzzel tegen spambots)** | De browser van de bezoeker moet een kleine puzzel oplossen voordat een formulier wordt geaccepteerd -- geen cookies, geen extern bedrijf, niets om op te klikken voor de bezoeker. Dit geldt voor **elke** manier van versturen, ook plug-ins met het API-token. Vink dit pas aan als alle formulieren van uw website de ALTCHA-widget bevatten, anders wordt elke inzending geweigerd. |
| **Adressen opslaan** | Slaat beide op. U ziet **Toegestane websiteadressen opgeslagen.** |

Wat tuinders zien en ontvangen, staat in
[Voor tuinders](../gardeners/index.md).

## Website (concepten vanuit mededelingen) {#website-drafts-from-announcements}

Laat de module [Mededelingen](../modules/announcements.md) met één klik
een conceptbericht op de website van uw vereniging aanmaken. Parcella
maakt alleen ooit **concepten** aan; publiceren blijft een beslissing die
u in uw websitesysteem neemt.

| Veld / knop | Wat het doet |
|---|---|
| **Websitetype** | **Geen (geen websiteconcepten)**, **WordPress**, **Markdown-map (cloudopslag)** of **Parcella-plugin (TYPO3, Contao, Drupal, Joomla, ...)**. Een keuze toont haar velden. Er is maar één type tegelijk actief; wisselen houdt de instellingen van het andere type voor later. |
| **Opslaan** | Slaat het type en de velden op. U ziet **Website-instellingen opgeslagen**, of een fout die uitlegt wat ontbreekt. |
| **Verbinding testen** | Probeert de verbinding met wat nu in het formulier staat, zonder op te slaan. Toont **Verbinding geslaagd** of de fout. |

Velden met * zijn verplicht. Wachtwoordvelden tonen of er iets is
opgeslagen; laat ze leeg om het te houden.

**WordPress**

| Veld | Wat u invult |
|---|---|
| **Adres van de WordPress-site** * | Het adres van uw website. |
| **WordPress-gebruikersnaam** * | De WordPress-gebruiker als wie de concepten worden aangemaakt. |
| **Applicatiewachtwoord** * | Niet het gewone WordPress-wachtwoord: maak in WordPress een applicatiewachtwoord aan onder *Gebruikers → Profiel → Applicatiewachtwoorden*. |

**Markdown-map (cloudopslag)** -- voor websites die uit tekstbestanden
worden gebouwd (Hugo, Jekyll, Eleventy, Astro en dergelijke). Elk concept
wordt een bestand, gemarkeerd als concept, in een map op uw
[cloudopslag](#cloud-storage); de conceptregel verwijderen publiceert
het.

| Veld | Wat u invult |
|---|---|
| **Map voor berichten** * | Map op de cloudopslag voor de berichten, bijv. `website/content/posts`. Die moet al bestaan. |
| **Map voor afbeeldingen** | Waar afbeeldingen heen gaan, in submappen per jaar en maand. Leeg: berichten zonder afbeeldingen. |
| **Webpad van de afbeeldingenmap** | Hoe de website de afbeeldingenmap aanspreekt, bijv. `/media`. |
| **Adres van de website** | Gebruikt voor de QR-code op de afgedrukte mededeling zodra een bericht is gepubliceerd. |
| **Patroon voor bestandsnamen** | `{date}` wordt JJJJMMDD, `{slug}` de titel zonder accenten of spaties. |
| **Patroon voor berichtadressen** | Het webadres van het bericht, in het bestand geschreven. Laat leeg als uw website het zelf bepaalt. |
| **Auteur** | In elk bericht geschreven. |
| **Categorieën** | Gescheiden door komma's, zoals uw website ze noemt. |

**Parcella-plugin** -- voor TYPO3, Contao, Drupal, Joomla en andere
systemen waarop de Parcella-plug-in is geïnstalleerd. De eigen
instellingen van de plug-in tonen beide waarden.

| Veld | Wat u invult |
|---|---|
| **Adres van de plugin** * | Bijv. `https://example.org/parcella/v1`. |
| **Gedeelde sleutel** * | Door de plug-in aangemaakt. |

## Cloudopslag {#cloud-storage}

De kop luidt **Cloudopslag (perceeldocumenten, facturen, back-ups)**. Hier
bepaalt u waar Parcella bestanden bewaart: een map per perceel
(huurcontracten, papierwerk), inkomende facturen, documenten van
contacten, notities, procesbestanden, back-ups en de Markdown-website.
Wie verder een map kan zien, regelt u in de opslag zelf, niet in
Parcella.

| Veld / knop | Wat het doet |
|---|---|
| **Type opslag** | **Geen (geen cloudopslag)**, **Nextcloud**, **WebDAV (ownCloud, Seafile, HiDrive, Storage Box, ...)** of **S3-compatibel (AWS, Hetzner, MinIO, Wasabi, ...)**. Er is maar één tegelijk actief. Mappaden die elders in Parcella worden ingevuld, zijn relatief ten opzichte van de gekozen opslag. |
| **Opslaan**, **Verbinding testen** | Als op de websitekaart. |

| Opslag | Velden |
|---|---|
| **Nextcloud** | **Nextcloud-adres** *, **Nextcloud-gebruikersnaam** *, **App-wachtwoord** * -- maak in Nextcloud een app-wachtwoord aan onder *Instellingen → Beveiliging → Apparaten & sessies*; gebruik niet het gewone wachtwoord. |
| **WebDAV** | **WebDAV-adres** * (het volledige adres van de map waarin Parcella moet werken, zoals uw aanbieder het opgeeft), **Gebruikersnaam** *, **Wachtwoord** *. |
| **S3-compatibel** | **Endpoint** *, **Regio** * (laat `us-east-1` staan als uw aanbieder geen regio's kent), **Bucket** *, **Toegangssleutel-ID** *, **Geheime toegangssleutel** *, **Pad in de bucket** (optionele submap voor alle bestanden van Parcella). |

De opslag wordt pas gebruikt als de module **Cloudopslag** is
ingeschakeld. Dan toont de kaart ook de mappen hieronder. Elke map heeft
een padveld (relatief ten opzichte van de opslag) en een knop
**Opslaan**; laat een pad leeg om dat gebruik uit te zetten.

| Map | Gebruikt voor |
|---|---|
| **Map voor inkomende facturen** | Bijlagen van [inkomende facturen](../modules/finances/incoming-invoices.md) komen in deze ene gedeelde map. |
| **Map voor documenten van externe contacten** | Een basismap met één submap per [extern contact](../modules/external-contacts.md), die u zelf in de opslag aanmaakt. Elk contact kiest dan zijn submap. Leeg: het documentengedeelte is verborgen. |
| **Map voor geprinte mededelingen** | Elke afdruk-PDF van een [mededeling](../modules/announcements.md) wordt ook hier opgeslagen. Met **Bladeren…** klikt u door de opslag en kiest u **Deze map gebruiken**. Leeg: alleen downloaden. |
| **Notitiemap** | [Notities](../modules/notes.md) worden hier als tekstbestanden bewaard, en wijzigingen aan die bestanden in de cloud verschijnen in Parcella. Submappen worden notitiecategorieën. Leeg: notities bestaan alleen in Parcella. |
| **Map voor procesbestanden** | Bestanden die bij een [proces](../modules/processes.md) zijn geüpload, één submap per proces. Leeg: in Parcella bewaard. Al geüploade bestanden blijven waar ze zijn. |

De map voor automatische back-ups stelt u in op de pagina
[Cloudback-ups](backup.md#cloud-backups).

## Support / helpdesk {#support-helpdesk}

Verbindt de helpdesk waarin uw vereniging vragen beantwoordt. Parcella
koppelt dan de gesprekken ervan aan leden, percelen en het takenbord (zie
[Ondersteuning](../modules/support.md)), en het contactformulier van de
website maakt daar nieuwe vragen aan.

| Veld / knop | Wat het doet |
|---|---|
| **Helpdesk** | **Geen (geen helpdesk)**, **FreeScout**, **Zammad**, **Znuny / OTRS**, **osTicket**, **Zendesk** of **Freshdesk**. Er is maar één tegelijk actief; schakelt u later terug, dan komen ook de gesprekken terug. Elke keuze toont een korte notitie over wat ermee werkt. |
| **Opslaan**, **Verbinding testen** | Als op de websitekaart. |

| Helpdesk | Velden | Opmerkingen |
|---|---|---|
| **FreeScout** | **FreeScout-adres** *, **API-sleutel** *, **Mailbox-ID** (standaard 1) | Alles werkt. Vraagt de FreeScout-module *API & Webhooks*. |
| **Zammad** | **Zammad-adres** *, **Toegangstoken** *, **Groep voor nieuwe vragen** * | Alles werkt. |
| **Znuny / OTRS** | **Adres van de webservice** *, **Agent-login** *, **Wachtwoord** *, **Wachtrij voor nieuwe vragen** *, **Adres van de agentinterface** | Geen hernoemen van klanten. Een Parcella-webservice moet één keer in Znuny worden geïmporteerd. |
| **osTicket** | **osTicket-adres** *, **API-sleutel** * | Alleen het contactformulier van de website werkt; lezen en antwoorden gebeuren in osTicket. |
| **Zendesk** | **Zendesk-adres** *, **E-mailadres van de agent** *, **API-token** * | Alles werkt. |
| **Freshdesk** | **Freshdesk-adres** *, **API-sleutel** * | Alles werkt. |

De hint onder elk veld zegt waar u de sleutel of het token in uw
helpdesk vindt. Schakel ook de module **Support (helpdesk)** in.

## Nextcloud Deck {#nextcloud-deck}

Kopieert de kaarten van één Nextcloud Deck-bord naar het
[takenbord](../modules/tasks.md) van Parcella -- in één richting,
alleen-lezen, automatisch actueel gehouden. Dit is een aparte
verbinding, los van de cloudopslag hierboven, ook als beide dezelfde
Nextcloud gebruiken.

| Veld / knop | Wat het doet |
|---|---|
| **Nextcloud-server-URL** | Bijv. `https://cloud.example.com`. |
| **Nextcloud-gebruikersnaam** | |
| **Nextcloud-app-wachtwoord** | Maak er een aan in Nextcloud onder *Persoonlijke instellingen → Beveiliging*. Laat leeg om het opgeslagen wachtwoord te houden. |
| **Deck-bord-ID** | Het nummer aan het einde van het webadres van het bord (`.../apps/deck/board/3` → `3`). Het hele adres plakken werkt ook. |
| **Opslaan** | Slaat de verbinding op (**Deck-instellingen opgeslagen**). |
| **Verbinding testen** | Controleert de verbinding met wat in het formulier staat. |
| **Nu synchroniseren** | Getoond zodra er een bord-ID is opgeslagen. Kopieert de kaarten meteen in plaats van te wachten. Ernaast: hoeveel taken wanneer zijn gesynchroniseerd, of **Nog niet gesynchroniseerd**. |

Schakel ook de module **Nextcloud Deck-synchronisatie** in.

## Gerelateerd {#related}

- [Modules in- en uitschakelen](modules.md)
- [Back-up en herstel](backup.md)
- [Voor tuinders](../gardeners/index.md) -- hoe de websiteformulieren er
  van de andere kant uitzien

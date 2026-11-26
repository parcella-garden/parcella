# Integrácie {#integrations}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Integrácie prepájajú Parcellu s ďalšími systémami, ktoré váš spolok
používa: s webom spolku, cloudovým úložiskom, helpdeskom, Nextcloud
Deck a kalendárovými aplikáciami.

!!! info "Kto to môže používať"
    Len administrátori. Otvorte **Administrácia → Integrácie**.

![Integrácie](../assets/screenshots/administration/integrations.png)

Stránka je stĺpec kariet, každá je zbalená; kliknutím na nadpis ju
otvoríte. Každá karta sa ukladá samostatne vlastným tlačidlom.

Väčšina integrácií potrebuje aj zapnutý modul v časti
[Zapínanie a vypínanie modulov](modules.md). Karty vám povedia, keď
chýba.

!!! note "E-mailový server je inde"
    Odchádzajúci poštový server (SMTP) sa nastavuje v
    [Nastaveniach spolku](settings.md#email-smtp), nie tu.

## Súkromné kalendárové kanály {#private-calendar-feeds}

Modul kalendára ponúka odkazy na odber (kalendárové kanály) pre zoznam
narodenín a pre prítomnosť a neprítomnosť výboru, aby ich členovia
výboru videli v kalendárovej aplikácii v telefóne. Tieto odkazy
obsahujú jeden spoločný tajný kľúč a nikdy nevypršia.

| Tlačidlo | Čo robí |
|---|---|
| **Vygenerovať znova** | Po potvrdení vytvorí nový tajný kľúč. **Každý existujúci odber týchto kanálov prestane fungovať**; odberatelia si musia skopírovať nový odkaz zo stránok kalendára. Uvidíte **Token kalendárových kanálov bol znova vygenerovaný.** |

Urobte to, keď sa odkaz mohol dostať do nesprávnych rúk alebo keď z
výboru odchádza niekto, kto ho mal. Pozri [Kalendár](../modules/calendar.md).

## Verejné API pre prihlášky {#public-signup-api}

Táto karta umožňuje webu vášho spolku komunikovať s Parcellou:
záhradkári sa cez formuláre na webe prihlasujú na pracovné zmeny,
posielajú kontaktnú správu alebo žiadajú o parcelu, bez prihlásenia do
Parcelly.

Ak je modul **Verejné API pre prihlášky** vypnutý, upozornenie hore na
stránke to povie, s odkazom **Zapnúť v Nastaveniach**. Podobné
upozornenie sa zobrazí v karte, kým je vypnuté **Verejné API
kontaktného formulára**. Formulár žiadosti o parcelu navyše potrebuje
prepínač **Verejné API formulára prihlášok**.

Web môže posielať svoje formuláre dvoma spôsobmi a môžete používať oba.

### S API tokenom (plugin webu na serveri) {#with-the-api-token-website-plugin-on-the-server}

Pre web s pluginom na strane servera -- „konektorom“ --, ktorý dáta z
formulára posiela do Parcelly sám.

| Prvok | Čo robí |
|---|---|
| **API token** | Tajný kľúč, ktorý plugin potrebuje. Kliknite do poľa, aby ste ho označili, a potom ho skopírujte do nastavení pluginu. |
| **Vygenerovať znova** | Po potvrdení vytvorí nový token. **Každý plugin, ktorý ešte používa starý, okamžite prestane fungovať**; zadajte nový všade. Uvidíte *Bol vygenerovaný nový API token ...* |
| **Endpointy** | Tabuľka webových adries, ktoré pluginy používajú, každá s **Metóda**, **URL** a **Autentifikácia** (**Žiadna (verejné čítanie)**, API token alebo **Povolené adresy webov**). Potrebuje ju technický kontakt vášho webu, nie vy. |

Karta končí poznámkou, že hotový plugin pre WordPress je súčasťou
projektu Parcella.

### Formuláre na webe (jednoduché HTML, plugin pre WordPress) {#website-forms-plain-html-wordpress-plugin}

Pre weby, ktorých formuláre posielajú dáta priamo z prehliadača
návštevníka do Parcelly: jednoduché stránky HTML v akomkoľvek
webovom systéme a plugin pre WordPress od verzie 3.0. Nepoužíva sa
žiadny token, preto Parcella prijíma formuláre len z webov, ktoré tu
uvediete. Kým je zoznam prázdny, sú tieto formuláre zatvorené.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Povolené adresy webov** | Jedna webová adresa na riadok, len schéma a host, napr. `https://example.org`. Uveďte každú adresu, na ktorej je web vášho spolku dostupný, vrátane vlastnej adresy webu WordPress. Záznamy, ktoré nie sú webovými adresami, sa vynechajú a uvedú vo varovaní. |
| **Vyžadovať ALTCHA (výpočtová úloha proti spamovým botom)** | Prehliadač návštevníka musí vyriešiť malú úlohu, kým sa formulár prijme -- žiadne cookies, žiadna externá firma, návštevník nemusí na nič klikať. Platí to pre **každý** spôsob odosielania, vrátane pluginov s API tokenom. Zaškrtnite to, až keď všetky formuláre vášho webu obsahujú widget ALTCHA, inak bude každé odoslanie odmietnuté. |
| **Uložiť adresy** | Uloží oboje. Uvidíte **Povolené adresy webov boli uložené.** |

Čo záhradkári vidia a dostávajú, je opísané v časti
[Pre záhradkárov](../gardeners/index.md).

## Webová stránka (koncepty z oznámení) {#website-drafts-from-announcements}

Umožní modulu [Oznamy](../modules/announcements.md) jedným kliknutím
vytvoriť koncept príspevku na webe vášho spolku. Parcella vytvára vždy
len **koncepty**; o zverejnení rozhodujete vy vo svojom webovom
systéme.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Typ webu** | **Žiadny (bez konceptov na webe)**, **WordPress**, **Priečinok Markdown (cloudové úložisko)** alebo **Plugin Parcella (TYPO3, Contao, Drupal, Joomla, ...)**. Výber zobrazí jeho polia. Aktívny je vždy len jeden typ; prepnutím sa nastavenia druhého typu zachovajú na neskôr. |
| **Uložiť** | Uloží typ a jeho polia. Uvidíte **Nastavenia webu uložené** alebo chybu, ktorá vysvetlí, čo chýba. |
| **Otestovať pripojenie** | Vyskúša pripojenie s tým, čo je práve vo formulári, bez uloženia. Ukáže **Pripojenie úspešné** alebo chybu. |

Polia označené * sú povinné. Polia hesiel ukazujú, či je niečo uložené;
nechajte ich prázdne, ak to chcete ponechať.

**WordPress**

| Pole | Čo zadať |
|---|---|
| **Adresa webu WordPress** * | Adresa vášho webu. |
| **Používateľské meno WordPress** * | Používateľ WordPress, v mene ktorého sa koncepty vytvárajú. |
| **Heslo aplikácie** * | Nie bežné heslo WordPress: vytvorte heslo aplikácie vo WordPresse v časti *Users → Profile → Application Passwords*. |

**Priečinok Markdown (cloudové úložisko)** -- pre weby zostavené z
textových súborov (Hugo, Jekyll, Eleventy, Astro a podobné). Každý
koncept sa stane súborom označeným ako koncept v priečinku na vašom
[cloudovom úložisku](#cloud-storage); odstránením riadku s konceptom sa
zverejní.

| Pole | Čo zadať |
|---|---|
| **Priečinok príspevkov** * | Priečinok na cloudovom úložisku pre príspevky, napr. `website/content/posts`. Musí už existovať. |
| **Priečinok obrázkov** | Kam idú obrázky, v podpriečinkoch podľa roka a mesiaca. Prázdne: príspevky bez obrázkov. |
| **Webová cesta k priečinku obrázkov** | Ako web adresuje priečinok obrázkov, napr. `/media`. |
| **Adresa webu** | Použije sa pre QR kód na vytlačenom ozname, keď je príspevok zverejnený. |
| **Vzor názvu súboru** | `{date}` sa zmení na RRRRMMDD, `{slug}` na názov bez diakritiky a medzier. |
| **Vzor adresy príspevku** | Webová adresa príspevku, zapísaná do súboru. Nechajte prázdne, ak si ju web zistí sám. |
| **Autor** | Zapíše sa do každého príspevku. |
| **Kategórie** | Oddelené čiarkou, ako ich pomenúva váš web. |

**Plugin Parcella** -- pre TYPO3, Contao, Drupal, Joomla a iné systémy
s nainštalovaným pluginom Parcella. Vlastné nastavenia pluginu ukazujú
obe hodnoty.

| Pole | Čo zadať |
|---|---|
| **Adresa pluginu** * | Napr. `https://example.org/parcella/v1`. |
| **Zdieľaný kľúč** * | Vygeneruje ho plugin. |

## Cloudové úložisko {#cloud-storage}

Nadpis znie **Cloudové úložisko (dokumenty parciel, faktúry, zálohy)**.
Rozhoduje, kde Parcella uchováva súbory: priečinok pre každú parcelu
(nájmy, dokumenty), prijaté faktúry, dokumenty kontaktov, poznámky,
súbory procesov, zálohy a web v Markdowne. Kto ďalší vidí priečinok,
sa spravuje v samotnom úložisku, nie v Parcelle.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Typ úložiska** | **Žiadne (bez cloudového úložiska)**, **Nextcloud**, **WebDAV (ownCloud, Seafile, HiDrive, Storage Box, ...)** alebo **Kompatibilné s S3 (AWS, Hetzner, MinIO, Wasabi, ...)**. Aktívne je vždy len jedno. Cesty k priečinkom zadané inde v Parcelle sú relatívne k zvolenému úložisku. |
| **Uložiť**, **Otestovať pripojenie** | Ako pri karte webu. |

| Úložisko | Polia |
|---|---|
| **Nextcloud** | **Adresa Nextcloud** *, **Používateľské meno Nextcloud** *, **Heslo aplikácie** * -- heslo aplikácie vytvorte v Nextcloude v časti *Nastavenia → Zabezpečenie → Zariadenia a relácie*; nepoužívajte bežné heslo. |
| **WebDAV** | **Adresa WebDAV** * (úplná adresa priečinka, v ktorom má Parcella pracovať, ako ju uvádza váš poskytovateľ), **Používateľské meno** *, **Heslo** *. |
| **Kompatibilné s S3** | **Endpoint** *, **Región** * (ak váš poskytovateľ nemá regióny, ponechajte `us-east-1`), **Bucket** *, **ID prístupového kľúča** *, **Tajný prístupový kľúč** *, **Cesta v buckete** (voliteľný podpriečinok pre všetky súbory Parcelly). |

Úložisko sa používa, až keď je zapnutý modul **Cloudové úložisko**.
Potom karta ukazuje aj priečinky nižšie. Každý má pole s cestou
(relatívnou k úložisku) a tlačidlo **Uložiť**; ak cestu necháte prázdnu,
toto použitie sa vypne.

| Priečinok | Na čo sa používa |
|---|---|
| **Priečinok pre prijaté faktúry** | Prílohy [prijatých faktúr](../modules/finances/incoming-invoices.md) idú do tohto jedného zdieľaného priečinka. |
| **Priečinok pre dokumenty externých kontaktov** | Základný priečinok s jedným podpriečinkom pre každý [externý kontakt](../modules/external-contacts.md), ktorý v úložisku vytvoríte vy. Každý kontakt si potom vyberie svoj podpriečinok. Prázdne: sekcia dokumentov je skrytá. |
| **Priečinok pre tlačené oznamy** | Každé PDF na tlač [oznamu](../modules/announcements.md) sa uloží aj sem. **Prehľadávať…** vám umožní preklikať sa úložiskom a priečinok **použiť**. Prázdne: len stiahnutie. |
| **Priečinok poznámok** | [Poznámky](../modules/notes.md) sa tu uchovávajú ako textové súbory a zmeny týchto súborov v cloude sa objavia v Parcelle. Podpriečinky sa stanú kategóriami poznámok. Prázdne: poznámky sú len v Parcelle. |
| **Priečinok pre súbory procesov** | Súbory nahrané do [procesu](../modules/processes.md), jeden podpriečinok na proces. Prázdne: uchovávajú sa v Parcelle. Už nahrané súbory zostávajú tam, kde sú. |

Priečinok pre automatické zálohy sa nastavuje na stránke
[Zálohy v cloude](backup.md#cloud-backups).

## Podpora / helpdesk {#support-helpdesk}

Pripojí helpdesk, v ktorom váš spolok odpovedá na žiadosti. Parcella
potom prepája jeho konverzácie s členmi, parcelami a nástenkou úloh
(pozri [Podpora](../modules/support.md)) a kontaktný formulár na webe v
ňom vytvára nové žiadosti.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Helpdesk** | **Žiadny (bez helpdesku)**, **FreeScout**, **Zammad**, **Znuny / OTRS**, **osTicket**, **Zendesk** alebo **Freshdesk**. Aktívny je vždy len jeden; ak sa neskôr prepnete späť, vrátia sa aj jeho konverzácie. Každá voľba ukazuje krátku poznámku o tom, čo s ňou funguje. |
| **Uložiť**, **Otestovať pripojenie** | Ako pri karte webu. |

| Helpdesk | Polia | Poznámky |
|---|---|---|
| **FreeScout** | **Adresa FreeScout** *, **Kľúč API** *, **ID schránky** (predvolene 1) | Všetko funguje. Potrebuje modul *API & Webhooks* vo FreeScoute. |
| **Zammad** | **Adresa Zammad** *, **Prístupový token** *, **Skupina pre nové žiadosti** * | Všetko funguje. |
| **Znuny / OTRS** | **Adresa webovej služby** *, **Prihlasovacie meno agenta** *, **Heslo** *, **Front pre nové žiadosti** *, **Adresa rozhrania agenta** | Bez premenovania zákazníkov. Do Znuny treba raz importovať webovú službu Parcella. |
| **osTicket** | **Adresa osTicket** *, **Kľúč API** * | Funguje len kontaktný formulár na webe; čítanie a odpovedanie prebieha v osTickete. |
| **Zendesk** | **Adresa Zendesk** *, **E-mail agenta** *, **API token** * | Všetko funguje. |
| **Freshdesk** | **Adresa Freshdesk** *, **Kľúč API** * | Všetko funguje. |

Nápoveda pod každým poľom hovorí, kde v helpdesku nájdete kľúč alebo
token. Zapnite aj modul **Podpora (helpdesk)**.

## Nextcloud Deck {#nextcloud-deck}

Kopíruje karty jednej nástenky Nextcloud Deck na
[nástenku úloh](../modules/tasks.md) Parcelly -- len jedným smerom, len
na čítanie, automaticky udržiavané aktuálne. Je to samostatné pripojenie
oddelené od cloudového úložiska vyššie, aj keď obe používajú ten istý
Nextcloud.

| Pole / tlačidlo | Čo robí |
|---|---|
| **URL servera Nextcloud** | Napr. `https://cloud.example.com`. |
| **Používateľské meno Nextcloud** | |
| **Aplikačné heslo Nextcloud** | Vytvorte ho v Nextcloude v časti *Osobné nastavenia → Zabezpečenie*. Nechajte prázdne, ak chcete ponechať uložené. |
| **ID nástenky Deck** | Číslo na konci webovej adresy nástenky (`.../apps/deck/board/3` → `3`). Funguje aj vloženie celej adresy. |
| **Uložiť** | Uloží pripojenie (**Nastavenia Deck uložené**). |
| **Otestovať pripojenie** | Overí pripojenie s tým, čo je vo formulári. |
| **Synchronizovať teraz** | Zobrazí sa, keď je ID nástenky uložené. Skopíruje karty hneď, namiesto čakania. Vedľa neho: koľko úloh sa synchronizovalo a kedy, alebo **Zatiaľ nesynchronizované**. |

Zapnite aj modul **Synchronizácia Nextcloud Deck**.

## Súvisiace {#related}

- [Zapínanie a vypínanie modulov](modules.md)
- [Zálohovanie a obnova](backup.md)
- [Pre záhradkárov](../gardeners/index.md) -- ako vyzerajú formuláre na webe z druhej strany

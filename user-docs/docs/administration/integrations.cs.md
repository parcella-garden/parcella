# Integrace {#integrations}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Integrace propojují Parcellu s dalšími systémy, které váš spolek
používá: web spolku, cloudové úložiště, helpdesk, Nextcloud Deck a
kalendářové aplikace.

!!! info "Kdo to může používat"
    Jen administrátoři. Otevřete **Administrace → Integrace**.

![Integrace](../assets/screenshots/administration/integrations.png)

Stránka je sloupec karet, každá je sbalená; kliknutím na záhlaví ji
otevřete. Každá karta se ukládá samostatně vlastním tlačítkem.

Většina integrací také potřebuje modul zapnutý v části
[Zapínání a vypínání modulů](modules.md). Karty vám řeknou, když chybí.

!!! note "E-mailový server je jinde"
    Odchozí poštovní server (SMTP) se nastavuje v
    [Nastavení spolku](settings.md#email-smtp), ne zde.

## Soukromé kalendářové kanály {#private-calendar-feeds}

Modul kalendáře nabízí odkazy pro odběr (kalendářové kanály) pro seznam
narozenin a pro přítomnost a nepřítomnost výboru, aby je členové výboru
viděli v kalendáři v telefonu. Tyto odkazy obsahují jeden sdílený tajný
klíč a nikdy nevyprší.

| Tlačítko | Co dělá |
|---|---|
| **Vygenerovat znovu** | Po potvrzení vytvoří nový tajný klíč. **Všechny stávající odběry těchto kanálů přestanou fungovat**; odběratelé musí zkopírovat nový odkaz ze stránek kalendáře. Uvidíte **Token kalendářových kanálů byl znovu vygenerován.** |

Udělejte to, když se odkaz mohl dostat do nesprávných rukou nebo když z
výboru odchází někdo, kdo ho měl. Viz [Kalendář](../modules/calendar.md).

## Veřejné API pro přihlášky {#public-signup-api}

Tato karta umožňuje webu vašeho spolku komunikovat s Parcellou:
zahrádkáři se přes formuláře na webu přihlašují na pracovní směny,
posílají kontaktní zprávu nebo žádají o parcelu, bez přihlášení do
Parcelly.

Pokud je modul **Veřejné API pro přihlášky** vypnutý, upozorní na to
poznámka nahoře na stránce s odkazem **Zapnout v Nastavení**. Podobná
poznámka se objeví uvnitř karty, dokud je vypnuté **Veřejné API
kontaktního formuláře**. Formulář žádosti o parcelu navíc potřebuje
přepínač **Veřejné API formuláře přihlášek**.

Web může posílat své formuláře dvěma způsoby a můžete používat oba.

### S API tokenem (plugin webu na serveru) {#with-the-api-token-website-plugin-on-the-server}

Pro web s pluginem na straně serveru -- „konektorem“ --, který sám
posílá data formulářů do Parcelly.

| Prvek | Co dělá |
|---|---|
| **API token** | Tajný klíč, který plugin potřebuje. Kliknutím do pole ho označte a pak ho zkopírujte do nastavení pluginu. |
| **Vygenerovat znovu** | Po potvrzení vytvoří nový token. **Každý plugin, který stále používá starý, okamžitě přestane fungovat**; nový zadejte všude. Uvidíte *Byl vygenerován nový API token ...* |
| **Endpointy** | Tabulka webových adres, které pluginy používají, každá s údaji **Metoda**, **URL** a **Autentizace** (**Žádná (veřejné čtení)**, API token nebo **Povolené adresy webů**). Potřebuje ji technický správce vašeho webu, vy ne. |

Karta končí poznámkou, že hotový plugin pro WordPress je součástí
projektu Parcella.

### Formuláře na webu (jednoduché HTML, plugin pro WordPress) {#website-forms-plain-html-wordpress-plugin}

Pro weby, jejichž formuláře odesílají data přímo z prohlížeče
návštěvníka do Parcelly: jednoduché HTML stránky na libovolném
redakčním systému a plugin pro WordPress od verze 3.0. Žádný token se
nepoužívá, proto Parcella přijímá jen formuláře z webů, které zde
uvedete. Dokud je seznam prázdný, jsou tyto formuláře zavřené.

| Pole / tlačítko | Co dělá |
|---|---|
| **Povolené adresy webů** | Jedna webová adresa na řádek, jen schéma a hostitel, např. `https://example.org`. Uveďte každou adresu, na které je web vašeho spolku dostupný, včetně vlastní adresy webu WordPress. Položky, které nejsou webovými adresami, se vyřadí a uvedou ve varování. |
| **Vyžadovat ALTCHA (výpočetní úloha proti spamovým botům)** | Prohlížeč návštěvníka musí vyřešit malou úlohu, než se formulář přijme -- žádné cookies, žádná externí firma, návštěvník nemusí nic klikat. Platí to pro **každý** způsob odesílání, včetně pluginů s API tokenem. Zaškrtněte to, až budou všechny formuláře vašeho webu obsahovat widget ALTCHA, jinak bude každé odeslání odmítnuto. |
| **Uložit adresy** | Uloží obojí. Uvidíte **Povolené adresy webů byly uloženy.** |

Co zahrádkáři vidí a dostávají, popisuje stránka
[Pro zahrádkáře](../gardeners/index.md).

## Webové stránky (koncepty z oznámení) {#website-drafts-from-announcements}

Umožňuje modulu [Oznámení](../modules/announcements.md) vytvořit jedním
kliknutím koncept příspěvku na webu vašeho spolku. Parcella vždy
vytváří jen **koncepty**; o zveřejnění rozhodujete vy ve svém
redakčním systému.

| Pole / tlačítko | Co dělá |
|---|---|
| **Typ webu** | **Žádný (bez konceptů na webu)**, **WordPress**, **Složka Markdown (cloudové úložiště)** nebo **Plugin Parcella (TYPO3, Contao, Drupal, Joomla, ...)**. Po výběru se zobrazí příslušná pole. Aktivní je vždy jen jeden typ; při přepnutí zůstávají nastavení druhého typu zachována na později. |
| **Uložit** | Uloží typ a jeho pole. Uvidíte **Nastavení webu uloženo**, nebo chybu, která vysvětlí, co chybí. |
| **Otestovat připojení** | Vyzkouší připojení s tím, co je právě ve formuláři, bez uložení. Ukáže **Připojení úspěšné** nebo chybu. |

Pole označená * jsou povinná. Pole hesel ukazují, zda je něco uloženo;
chcete-li to zachovat, nechte je prázdná.

**WordPress**

| Pole | Co zadat |
|---|---|
| **Adresa webu WordPress** * | Adresa vašeho webu. |
| **Uživatelské jméno WordPress** * | Uživatel WordPressu, pod kterým se koncepty vytvářejí. |
| **Heslo aplikace** * | Ne běžné heslo do WordPressu: vytvořte heslo aplikace ve WordPressu v *Uživatelé → Profil → Hesla aplikací*. |

**Složka Markdown (cloudové úložiště)** -- pro weby sestavené z
textových souborů (Hugo, Jekyll, Eleventy, Astro a podobné). Každý
koncept se stane souborem označeným jako koncept ve složce ve vašem
[cloudovém úložišti](#cloud-storage); odstraněním řádku s konceptem se
příspěvek zveřejní.

| Pole | Co zadat |
|---|---|
| **Složka příspěvků** * | Složka v cloudovém úložišti pro příspěvky, např. `website/content/posts`. Musí už existovat. |
| **Složka obrázků** | Kam se ukládají obrázky, v podsložkách podle roku a měsíce. Prázdné: příspěvky bez obrázků. |
| **Webová cesta ke složce obrázků** | Jak web adresuje složku obrázků, např. `/media`. |
| **Adresa webu** | Používá se pro QR kód na tištěném oznámení, jakmile je příspěvek zveřejněn. |
| **Vzor názvu souboru** | `{date}` se nahradí YYYYMMDD, `{slug}` názvem bez diakritiky a mezer. |
| **Vzor adresy příspěvku** | Webová adresa příspěvku, zapsaná do souboru. Nechte prázdné, pokud si ji váš web zjistí sám. |
| **Autor** | Zapisuje se do každého příspěvku. |
| **Kategorie** | Oddělené čárkou, tak jak je pojmenovává váš web. |

**Plugin Parcella** -- pro TYPO3, Contao, Drupal, Joomla a další systémy
s nainstalovaným pluginem Parcella. Obě hodnoty ukazuje nastavení
pluginu.

| Pole | Co zadat |
|---|---|
| **Adresa pluginu** * | Např. `https://example.org/parcella/v1`. |
| **Sdílený klíč** * | Vygeneruje ho plugin. |

## Cloudové úložiště {#cloud-storage}

Záhlaví zní **Cloudové úložiště (dokumenty parcel, faktury, zálohy)**.
Určuje, kde Parcella uchovává soubory: složku pro každou parcelu
(nájemní smlouvy, dokumenty), přijaté faktury, dokumenty kontaktů,
poznámky, soubory procesů, zálohy a web v Markdownu. Kdo další může
složku vidět, se spravuje v samotném úložišti, ne v Parcelle.

| Pole / tlačítko | Co dělá |
|---|---|
| **Typ úložiště** | **Žádné (bez cloudového úložiště)**, **Nextcloud**, **WebDAV (ownCloud, Seafile, HiDrive, Storage Box, ...)** nebo **Kompatibilní s S3 (AWS, Hetzner, MinIO, Wasabi, ...)**. Aktivní je vždy jen jedno. Cesty ke složkám zadané jinde v Parcelle jsou relativní k vybranému úložišti. |
| **Uložit**, **Otestovat připojení** | Jako na kartě webu. |

| Úložiště | Pole |
|---|---|
| **Nextcloud** | **Adresa Nextcloud** *, **Uživatelské jméno Nextcloud** *, **Heslo aplikace** * -- heslo aplikace vytvořte v Nextcloudu v *Nastavení → Zabezpečení → Zařízení a relace*; nepoužívejte běžné heslo. |
| **WebDAV** | **Adresa WebDAV** * (úplná adresa složky, ve které má Parcella pracovat, podle dokumentace vašeho poskytovatele), **Uživatelské jméno** *, **Heslo** *. |
| **Kompatibilní s S3** | **Endpoint** *, **Region** * (ponechte `us-east-1`, pokud poskytovatel regiony nemá), **Bucket** *, **ID přístupového klíče** *, **Tajný přístupový klíč** *, **Cesta v bucketu** (volitelná podsložka pro všechny soubory Parcelly). |

Úložiště se používá, až když je zapnutý modul **Cloudové úložiště**.
Pak karta ukazuje i níže uvedené složky. Každá má pole s cestou
(relativní k úložišti) a tlačítko **Uložit**; ponecháte-li cestu
prázdnou, toto použití se vypne.

| Složka | Použití |
|---|---|
| **Složka pro přijaté faktury** | Přílohy [přijatých faktur](../modules/finances/incoming-invoices.md) se ukládají do této jedné společné složky. |
| **Složka pro dokumenty externích kontaktů** | Základní složka s jednou podsložkou pro každý [externí kontakt](../modules/external-contacts.md), kterou v úložišti vytvoříte vy. Každý kontakt si pak vybere svou podsložku. Prázdné: sekce dokumentů je skrytá. |
| **Složka pro tištěná oznámení** | Každé PDF k tisku z [oznámení](../modules/announcements.md) se uloží také sem. **Procházet…** vám umožní proklikat se úložištěm a složku **použít**. Prázdné: jen stažení. |
| **Složka poznámek** | [Poznámky](../modules/notes.md) se zde uchovávají jako textové soubory a změny těchto souborů v cloudu se projeví v Parcelle. Podsložky se stanou kategoriemi poznámek. Prázdné: poznámky existují jen v Parcelle. |
| **Složka pro soubory procesů** | Soubory nahrané k [procesu](../modules/processes.md), jedna podsložka pro každý proces. Prázdné: uchovávají se v Parcelle. Již nahrané soubory zůstávají, kde jsou. |

Složka pro automatické zálohy se nastavuje na stránce
[Zálohy v cloudu](backup.md#cloud-backups).

## Podpora / helpdesk {#support-helpdesk}

Připojuje helpdesk, ve kterém váš spolek vyřizuje dotazy. Parcella pak
propojuje jeho konverzace se členy, parcelami a nástěnkou úkolů (viz
[Podpora](../modules/support.md)) a kontaktní formulář na webu v něm
vytváří nové požadavky.

| Pole / tlačítko | Co dělá |
|---|---|
| **Helpdesk** | **Žádný (bez helpdesku)**, **FreeScout**, **Zammad**, **Znuny / OTRS**, **osTicket**, **Zendesk** nebo **Freshdesk**. Aktivní je vždy jen jeden; pokud se k němu později vrátíte, vrátí se i jeho konverzace. U každé volby je krátká poznámka, co s ní funguje. |
| **Uložit**, **Otestovat připojení** | Jako na kartě webu. |

| Helpdesk | Pole | Poznámky |
|---|---|---|
| **FreeScout** | **Adresa FreeScout** *, **Klíč API** *, **ID schránky** (výchozí 1) | Funguje vše. Potřebuje modul FreeScoutu *API & Webhooks*. |
| **Zammad** | **Adresa Zammad** *, **Přístupový token** *, **Skupina pro nové žádosti** * | Funguje vše. |
| **Znuny / OTRS** | **Adresa webové služby** *, **Přihlašovací jméno agenta** *, **Heslo** *, **Fronta pro nové žádosti** *, **Adresa rozhraní agenta** | Nelze přejmenovávat zákazníky. Do Znuny je třeba jednou importovat webovou službu Parcella. |
| **osTicket** | **Adresa osTicket** *, **Klíč API** * | Funguje jen kontaktní formulář na webu; čtení a odpovídání probíhá v osTicketu. |
| **Zendesk** | **Adresa Zendesk** *, **E-mail agenta** *, **API token** * | Funguje vše. |
| **Freshdesk** | **Adresa Freshdesk** *, **Klíč API** * | Funguje vše. |

Nápověda pod každým polem říká, kde v helpdesku klíč nebo token
najdete. Zapněte také modul **Podpora (helpdesk)**.

## Nextcloud Deck {#nextcloud-deck}

Kopíruje karty jedné tabule Nextcloud Deck na
[nástěnku úkolů](../modules/tasks.md) Parcelly -- jen jedním směrem, jen
pro čtení, automaticky aktualizované. Jde o samostatné spojení, odlišné
od cloudového úložiště výše, i když oba používají stejný Nextcloud.

| Pole / tlačítko | Co dělá |
|---|---|
| **URL serveru Nextcloud** | Např. `https://cloud.example.com`. |
| **Uživatelské jméno Nextcloud** | |
| **Aplikační heslo Nextcloud** | Vytvořte ho v Nextcloudu v *Osobní nastavení → Zabezpečení*. Nechte prázdné, chcete-li zachovat uložené. |
| **ID nástěnky Deck** | Číslo na konci webové adresy tabule (`.../apps/deck/board/3` → `3`). Funguje i vložení celé adresy. |
| **Uložit** | Uloží spojení (**Nastavení Deck uloženo**). |
| **Otestovat připojení** | Ověří spojení s tím, co je ve formuláři. |
| **Synchronizovat nyní** | Zobrazí se, jakmile je ID tabule uloženo. Zkopíruje karty hned, místo čekání. Vedle: kolik úkolů bylo synchronizováno a kdy, nebo **Zatím nesynchronizováno**. |

Zapněte také modul **Synchronizace Nextcloud Deck**.

## Související {#related}

- [Zapínání a vypínání modulů](modules.md)
- [Zálohování a obnova](backup.md)
- [Pro zahrádkáře](../gardeners/index.md) -- jak formuláře na webu vypadají z druhé strany

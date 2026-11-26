# Zapínanie a vypínanie modulov {#turning-modules-on-and-off}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Nie každý spolok používa každú časť Parcelly. Spolok bez vlastného
vodovodu nepotrebuje odpočty meradiel; spolok, ktorý nevyžaduje
pracovné hodiny, nepotrebuje pracovné zmeny. Vy rozhodujete, ktoré
moduly váš spolok používa.

!!! info "Kto to môže používať"
    Len administrátori. Otvorte **Administrácia → Nastavenia** a
    rozbaľte kartu **Funkčné oblasti**.

Každý modul má prepínač, svoj názov a krátky popis. Prepnite prepínače,
ktoré chcete zmeniť, a kliknite na **Uložiť nastavenia**.

## Čo sa stane, keď modul vypnete {#what-happens-when-you-switch-a-module-off}

- **Zmizne z bočného panela a z dashboardu** pre všetkých, vrátane
  administrátorov. (Výnimka: dlaždica *Narodeniny tento týždeň* zostáva
  na dashboarde aj pri vypnutom Kalendári.)
- Jeho stránky sa už nedajú otvoriť, ani zo záložky.
- **Nič sa nezmaže.** Všetky jeho dáta zostávajú v databáze a sú späť,
  nezmenené, hneď ako modul znova zapnete.
- Oprávnenia skupín pre modul zostávajú, ako sú, takže po opätovnom
  zapnutí majú prístup znova tí istí ľudia.

Zapnutý modul je hneď viditeľný pre všetkých s plným prístupom. Ostatní
ho uvidia v bočnom paneli až vtedy, keď im skupina udelí **Čítanie** --
pozri [Skupiny](groups.md).

## Prepínače {#the-switches}

Na karte sú v tomto poradí.

| Prepínač | Čo robí | Predvolene zapnutý |
|---|---|---|
| **Správa pracovných hodín** | Pracovné zmeny, sponzorstvá, roly v spolku a ročný prehľad pracovných hodín. Pozri [Pracovné hodiny](../modules/work-hours.md). | Áno |
| **Správa vody** | Vodomery, odpočty a prehľady spotreby. Pozri [Voda a elektrina](../modules/metering.md). | Áno |
| **Správa elektriny** | Elektromery, odpočty a prehľady spotreby. | Áno |
| **Správa poistení** | Poistenie majetku a úrazové poistenie pre parcely, s ročným prehľadom. Pozri [Poistenie](../modules/insurance.md). | Áno |
| **Podpora (helpdesk)** | Prepája konverzácie vášho helpdesku s členmi a nástenkou úloh. Najprv vyberte helpdesk v časti [Integrácie](integrations.md#support-helpdesk). Pozri [Podpora](../modules/support.md). | Nie |
| **Žiadosti o nákup** | Výdavky spolku so schválením dvoma osobami. Pozri [Žiadosti o nákup](../modules/purchase-requests.md). | Áno |
| **Kalendár** | Kalendár spolku, narodeniny, prítomnosť a neprítomnosť výboru, každý s kalendárovým kanálom. Pozri [Kalendár](../modules/calendar.md). | Áno |
| **Inventár** | Všetko, čo spolok vlastní, s kategóriami a požičiavaním. Pozri [Inventár](../modules/inventory.md). | Áno |
| **Nástenka úloh** | Nástenka Na spracovanie / Rozpracované / Hotovo pre záležitosti spolku. Len pre používateľov s plným prístupom (výbor, administrátori a skupiny s plným prístupom). Pozri [Nástenka úloh](../modules/tasks.md). | Áno |
| **Uchádzači** | Ľudia, ktorí požiadali o voľnú záhradku. Pozri [Uchádzači](../modules/applicants.md). | Áno |
| **Externé kontakty** | Dodávatelia, remeselníci, úrady. Pozri [Externé kontakty](../modules/external-contacts.md). | Áno |
| **Prehľady** | Čísla spolku v čase ako grafy, len na čítanie. Pozri [Prehľady](../modules/reporting.md). | Áno |
| **Poznámky** | Poznámky s kategóriami a štítkami, voliteľne uložené ako súbory v cloude. Pozri [Poznámky](../modules/notes.md). | Áno |
| **Procesy** | Vaše vlastné procesy krok za krokom. Pozri [Procesy](../modules/processes.md). | Áno |
| **Konektor MCP pre klientov AI** | Umožní AI asistentovi (Claude, ChatGPT, ...) vyhľadávať, čítať a zapisovať **len tie poznámky, ktoré ste uvoľnili pre AI**, nič iné. Potrebuje [API token](api-tokens.md) druhu **Len konektor MCP (pre klienta AI)**. | Nie |
| **Verejné API pre prihlášky** | Umožní formuláru na webe spolku prihlasovať záhradkárov na pracovné zmeny bez prihlásenia. Pozri [Integrácie](integrations.md#public-signup-api) a [Pre záhradkárov](../gardeners/index.md). | Nie |
| **Verejné API kontaktného formulára** | Umožní kontaktnému formuláru na webe spolku vytvoriť novú požiadavku vo vašom helpdesku namiesto odoslania e-mailu. | Nie |
| **Verejné API formulára prihlášok** | Umožní formuláru žiadosti o parcelu na webe spolku priamo vytvárať uchádzačov. Modul **Uchádzači** sa dá používať aj bez neho, pre prihlášky, ktoré zadávate ručne. | Nie |
| **Oznamy** | Novinky spolku napíšete raz a pripravíte ich pre web, e-mail členom a oznam na vytlačenie. Pozri [Oznamy](../modules/announcements.md). | Nie |
| **Cloudové úložisko** | Cloudový priečinok pre každú parcelu na nájomné zmluvy a dokumenty; potrebný aj pre prílohy prijatých faktúr, dokumenty kontaktov, súbory poznámok a zálohy v cloude. Najprv vyberte úložisko v časti [Integrácie](integrations.md#cloud-storage). | Nie |
| **Financie** | Ročné faktúry za parcely, platby a účtovníctvo. Najprv vyplňte [finančné nastavenia](settings.md#finance-settings). Pozri [Financie](../modules/finances/index.md). | Nie |
| **Synchronizácia Nextcloud Deck** | Kopíruje karty jednej nástenky Nextcloud Deck na nástenku úloh, automaticky udržiavané aktuálne. Najprv nastavte pripojenie v časti [Integrácie](integrations.md#nextcloud-deck). | Nie |

**Členovia** a **Parcely** nemajú prepínač: sú jadrom Parcelly a sú
vždy zapnuté.

## Prečo sú niektoré prepínače na začiatku vypnuté {#why-some-switches-start-off}

Prepínače, ktoré sú v novej inštalácii vypnuté, robia jedno z tohto:

- **Otvárajú dvere do verejného internetu.** Tri prepínače *Verejné
  API ...* umožňujú komukoľvek, kto navštívi váš web, posielať dáta do
  Parcelly. Zapnite niektorý, len keď váš web naozaj má príslušný
  formulár, a len ten, ktorý potrebujete.
- **Ukladajú heslá k iným službám** alebo umožňujú Parcelle v nich
  konať: cloudové úložisko, helpdesk, Nextcloud Deck, prepojenie oznamov
  s webom.
- **Pracujú s peniazmi alebo oslovia naraz každého člena:** financie a
  oznamy.
- **Odovzdávajú dáta externej firme:** konektor MCP dáva službe AI
  prístup k poznámkam, ktoré uvoľníte.

Ak ich necháte vypnuté, nič sa nepokazí. Zapnite ich zámerne, keď
viete, že ich potrebujete.

## Súvisiace {#related}

- [Moduly](../modules/index.md) -- čo robí každý modul
- [Skupiny](groups.md) -- kto smie používať zapnutý modul
- [Integrácie](integrations.md) -- prepojenia, ktoré potrebuje viacero modulov

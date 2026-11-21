# Zapínání a vypínání modulů {#turning-modules-on-and-off}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Ne každý spolek používá všechny části Parcelly. Spolek bez vlastního
rozvodu vody nepotřebuje odečty vodoměrů; spolek, který nevyžaduje
pracovní hodiny, nepotřebuje pracovní směny. Které moduly váš spolek
používá, rozhodujete vy.

!!! info "Kdo to může používat"
    Jen administrátoři. Otevřete **Administrace → Nastavení** a
    rozbalte kartu **Funkční oblasti**.

Každý modul má přepínač, název a krátký popis. Přepněte, co chcete
změnit, a klikněte na **Uložit nastavení**.

## Co se stane, když modul vypnete {#what-happens-when-you-switch-a-module-off}

- **Zmizí z postranního panelu a z dashboardu** pro všechny, včetně
  administrátorů. (Výjimka: dlaždice *Narozeniny tento týden* zůstává na
  dashboardu i při vypnutém Kalendáři.)
- Jeho stránky už nelze otevřít, ani ze záložky.
- **Nic se nesmaže.** Všechna jeho data zůstávají v databázi a jsou zpět,
  beze změny, jakmile modul znovu zapnete.
- Oprávnění skupin pro modul zůstávají, jak jsou, takže po opětovném
  zapnutí mají přístup opět titíž lidé.

Zapnutý modul je okamžitě viditelný pro všechny s plným přístupem.
Ostatní ho v postranním panelu uvidí, až jim některá skupina dá pro
modul **Čtení** -- viz [Skupiny](groups.md).

## Přepínače {#the-switches}

Na kartě jsou v tomto pořadí.

| Přepínač | Co dělá | Výchozí stav zapnuto |
|---|---|---|
| **Správa pracovních hodin** | Pracovní směny, sponzoringy, role ve spolku a roční přehled pracovních hodin. Viz [Pracovní hodiny](../modules/work-hours.md). | Ano |
| **Správa vody** | Vodoměry, odečty a přehledy spotřeby. Viz [Voda a elektřina](../modules/metering.md). | Ano |
| **Správa elektřiny** | Elektroměry, odečty a přehledy spotřeby. | Ano |
| **Správa pojištění** | Pojištění majetku a úrazové pojištění pro každou parcelu, s ročním přehledem. Viz [Pojištění](../modules/insurance.md). | Ano |
| **Podpora (helpdesk)** | Propojuje konverzace vašeho helpdesku se členy a nástěnkou úkolů. Helpdesk nejprve vyberte v [Integrace](integrations.md#support-helpdesk). Viz [Podpora](../modules/support.md). | Ne |
| **Žádosti o nákup** | Výdaje spolku se schválením dvěma osobami. Viz [Žádosti o nákup](../modules/purchase-requests.md). | Ano |
| **Kalendář** | Kalendář spolku, narozeniny, přítomnost a nepřítomnost výboru, každý s kalendářovým kanálem. Viz [Kalendář](../modules/calendar.md). | Ano |
| **Inventář** | Vše, co spolek vlastní, s kategoriemi a půjčováním. Viz [Inventář](../modules/inventory.md). | Ano |
| **Nástěnka úkolů** | Tabule K vyřízení / Rozpracováno / Hotovo pro záležitosti spolku. Jen pro uživatele s plným přístupem (výbor, administrátoři a skupiny s plným přístupem). Viz [Nástěnka úkolů](../modules/tasks.md). | Ano |
| **Uchazeči** | Lidé, kteří se přihlásili o volnou parcelu. Viz [Uchazeči](../modules/applicants.md). | Ano |
| **Externí kontakty** | Dodavatelé, řemeslníci, úřady. Viz [Externí kontakty](../modules/external-contacts.md). | Ano |
| **Přehledy** | Údaje spolku v čase jako grafy, jen pro čtení. Viz [Přehledy](../modules/reporting.md). | Ano |
| **Poznámky** | Poznámky s kategoriemi a štítky, volitelně uložené jako soubory v cloudu. Viz [Poznámky](../modules/notes.md). | Ano |
| **Procesy** | Vaše vlastní procesy krok za krokem. Viz [Procesy](../modules/processes.md). | Ano |
| **Konektor MCP pro klienty AI** | Umožní asistentovi AI (Claude, ChatGPT, ...) vyhledávat, číst a zapisovat **jen ty poznámky, které jste pro AI uvolnili**, nic jiného. Potřebuje [API token](api-tokens.md) druhu **Jen konektor MCP (pro klienta AI)**. | Ne |
| **Veřejné API pro přihlášky** | Umožní formuláři na webu spolku přihlašovat zahrádkáře na pracovní směny bez přihlášení do aplikace. Viz [Integrace](integrations.md#public-signup-api) a [Pro zahrádkáře](../gardeners/index.md). | Ne |
| **Veřejné API kontaktního formuláře** | Umožní kontaktnímu formuláři na webu spolku vytvořit nový požadavek ve vašem helpdesku místo odeslání e-mailu. | Ne |
| **Veřejné API formuláře přihlášek** | Umožní formuláři žádosti o parcelu na webu spolku přímo vytvářet uchazeče. Modul **Uchazeči** lze používat i bez něj, pro žádosti zadávané ručně. | Ne |
| **Oznámení** | Napište novinky spolku jednou a připravte je pro web, e-mail členům a vytisknutelné oznámení. Viz [Oznámení](../modules/announcements.md). | Ne |
| **Cloudové úložiště** | Cloudová složka pro každou parcelu na nájemní smlouvy a dokumenty; potřebná také pro přílohy přijatých faktur, dokumenty kontaktů, soubory poznámek a zálohy v cloudu. Úložiště nejprve vyberte v [Integrace](integrations.md#cloud-storage). | Ne |
| **Finance** | Roční faktury pro každou parcelu, platby a účetnictví. Nejprve vyplňte [finanční nastavení](settings.md#finance-settings). Viz [Finance](../modules/finances/index.md). | Ne |
| **Synchronizace Nextcloud Deck** | Kopíruje karty jedné tabule Nextcloud Deck na nástěnku úkolů a automaticky je udržuje aktuální. Spojení nejprve nastavte v [Integrace](integrations.md#nextcloud-deck). | Ne |

**Členové** a **Parcely** nemají žádný přepínač: jsou jádrem Parcelly a
jsou vždy zapnuté.

## Proč jsou některé přepínače na začátku vypnuté {#why-some-switches-start-off}

Přepínače, které jsou v nové instalaci vypnuté, dělají jedno z
následujícího:

- **Otevírají dveře veřejnému internetu.** Tři přepínače *Veřejné API
  ...* umožňují komukoli, kdo navštíví váš web, posílat data do
  Parcelly. Zapněte některý jen tehdy, když váš web opravdu má
  odpovídající formulář, a jen ten, který potřebujete.
- **Ukládají hesla k jiným službám** nebo v nich nechávají Parcellu
  jednat: cloudové úložiště, helpdesk, Nextcloud Deck, propojení
  oznámení s webem.
- **Pracují s penězi nebo osloví všechny členy najednou:** finance a
  oznámení.
- **Předávají data externí firmě:** konektor MCP dává službě AI přístup
  k poznámkám, které uvolníte.

Když je necháte vypnuté, nic se nerozbije. Zapínejte je uváženě, až
budete vědět, že je potřebujete.

## Související {#related}

- [Moduly](../modules/index.md) -- co který modul dělá
- [Skupiny](groups.md) -- kdo smí zapnutý modul používat
- [Integrace](integrations.md) -- propojení, která potřebuje více modulů

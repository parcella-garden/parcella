# Moduly {#modules}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Parcella se skládá z modulů: jeden pro každou oblast práce spolku. Váš
spolek zapíná jen ty, které potřebuje; ostatní zmizí z navigace pro
všechny. Vypnutím modulu se nikdy nesmažou jeho data -- zapněte ho znovu
a vše je zpět.

Moduly zapíná a vypíná administrátor, viz
[Zapínání a vypínání modulů](../administration/modules.md). Kdo smí
zapnutý modul používat, se nastavuje pomocí
[skupin](../administration/groups.md).

## Přehled {#overview}

| Modul | K čemu slouží | Zapnutý po instalaci? |
|---|---|---|
| [Členové](members.md) | Všichni, kdo patří do spolku: kontaktní údaje, data členství, role, historie. | Vždy zapnutý |
| [Parcely](parcels.md) | Zahrádky, jejich nájmy a nájemci, dřívější i současní. | Vždy zapnutý |
| [Uchazeči](applicants.md) | Lidé, kteří se přihlásili o volnou parcelu, jejich stav a poznámky výboru. | Ano |
| [Pracovní hodiny](work-hours.md) | Pracovní směny, přihlášky a docházka, sponzoringy, převody hodin a roční hodnocení povinných hodin. | Ano |
| [Voda a elektřina](metering.md) | Měřidla, odečty a přehledy spotřeby. Voda a elektřina se zapínají zvlášť. | Ano |
| [Pojištění](insurance.md) | Pojištění majetku a úrazové pojištění pro každou parcelu a rok, s ročním přehledem. | Ano |
| [Finance](finances/index.md) | Roční faktury pro každou parcelu, platby, upomínky, bankovní účty, přijaté faktury a účetnictví. | Ne |
| [Žádosti o nákup](purchase-requests.md) | Výdaje spolku schválené dvěma členy výboru dřív, než se utratí peníze. | Ano |
| [Kalendář](calendar.md) | Kalendář spolku, narozeniny, přítomnost a nepřítomnost výboru, vaše vlastní kalendáře -- každý také jako odebíratelný kalendářový kanál. | Ano |
| [Oznámení](announcements.md) | Napište novinky spolku jednou a pošlete je na web, e-mailem a jako vytisknutelné oznámení. | Ne |
| [Nástěnka úkolů](tasks.md) | Tabule K vyřízení / Rozpracováno / Hotovo pro záležitosti spolku. Jen pro výbor a administrátory. | Ano |
| [Inventář](inventory.md) | Vše, co spolek vlastní (a věci členů uložené na pozemku spolku), včetně půjčování. | Ano |
| [Poznámky](notes.md) | Zápisy ze schůzí a další poznámky, s kategoriemi a štítky, volitelně uložené jako soubory v cloudu. | Ano |
| [Procesy](processes.md) | Vaše vlastní postupy krok za krokem, například předání parcely, spuštěné pro parcelu, člena nebo uchazeče. | Ano |
| [Externí kontakty](external-contacts.md) | Dodavatelé, řemeslníci a úřady, propojení s fakturami a žádostmi o nákup. | Ano |
| [Podpora](support.md) | Konverzace helpdesku vašeho spolku, propojené se členy, parcelami a úkoly. | Ne |
| [Přehledy](reporting.md) | Údaje spolku v průběhu let jako grafy. Jen pro čtení. | Ano |

## Proč jsou některé moduly na začátku vypnuté {#why-some-modules-start-switched-off}

Moduly, které jsou po instalaci vypnuté, dělají každý něco, o čem by se
spolek měl rozhodnout vědomě:

- **Finance** pracují s penězi členů a rozesílají faktury hromadně.
- **Oznámení** mohou poslat e-mail všem členům a publikovat na vašem webu.
- **Podpora** se připojuje k externímu helpdesku a potřebuje jeho
  přístupové údaje.

Totéž platí pro doplňky v seznamu modulů, které nemají vlastní kapitolu:
**Cloudové úložiště**, **Synchronizace Nextcloud Deck**, **Konektor MCP
pro klienty AI** a tři veřejné formuláře pro web (**Veřejné API pro
přihlášky**, **Veřejné API kontaktního formuláře**, **Veřejné API
formuláře přihlášek**). Buď ukládají hesla k externím službám, nebo
otevírají formulář veřejnému internetu. Viz
[Zapínání a vypínání modulů](../administration/modules.md) a
[Integrace](../administration/integrations.md).

## Související {#related}

- [Role, skupiny a oprávnění](../getting-started/roles-and-permissions.md)
- [Orientace v aplikaci](../getting-started/navigation.md)

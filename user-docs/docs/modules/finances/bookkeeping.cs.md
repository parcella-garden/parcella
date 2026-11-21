# Kategorie, rozpočet a přehled {#categories-budget-and-statement}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Účetní kategorie jsou krátké kódy jako „40000 Členské příspěvky“, které
připojujete k řádkům faktur a k položkám přijatých faktur. Díky nim vám
Parcella řekne, odkud peníze spolku přišly a kam odešly: v seznamu všech
plateb, v účetním přehledu na peněžní bázi pro finanční úřad a v
rozpočtu na příští rok.

!!! info "Kdo to může používat"
    Součást modulu **Finance** (ve výchozím stavu vypnutý). Všechny
    čtyři obrazovky lze prohlížet s oprávněním ke čtení u **Finance**,
    včetně exportu přehledu do PDF. Přidávání, změny a import kategorií
    a ukládání rozpočtu vyžadují oprávnění k zápisu; smazání kategorie
    vyžaduje oprávnění k mazání. Členové výboru a administrátoři mohou
    vše. Viz [Finance](index.md).

## Účetní kategorie {#bookkeeping-categories}

![Účetní kategorie](../../assets/screenshots/finances/category-list.png)

Otevřete je kartou **Kategorie** na finančním přehledu. **Zpět na
Finance** v horní liště vás vrátí zpět.

Parcella nedodává žádný oficiální účtový rozvrh. Ukázková data obsahují
tři příkladové kategorie; nahraďte je vlastním rozvrhem spolku, zadaným
ručně nebo importovaným z účetního softwaru.

### Nová kategorie {#new-category}

Zobrazí se s oprávněním k zápisu.

| Pole | Co dělá |
|---|---|
| **Číslo** | Povinné. Přesně pět číslic, např. `40000`. Nesmí ho používat jiná kategorie. |
| **Název** | Povinné, např. „Členské příspěvky“. |
| **Skupina** | **Příjmy**, **Výdaje**, **Dlouhodobý majetek**, **Vlastní kapitál a závazky** nebo **Ostatní**. Rozpočet řadí kategorie **Příjmy** do části příjmů a všechny ostatní do části výdajů. |
| **Přidat kategorii** | Uloží kategorii. |

Chyby: „Neplatná kategorie -- číslo musí mít přesně 5 číslic, název a
skupina jsou povinné.“ nebo „Kategorie s tímto číslem již existuje.“

### Import z CSV {#import-from-csv}

Zobrazí se s oprávněním k zápisu. Vyberte **Soubor CSV** a klikněte na
**Importovat**.

Soubor potřebuje řádek záhlaví `code,title,group`, oddělený čárkami.
**group** je jedno z `income`, `expense`, `fixed_assets`,
`equity_liabilities`, `other` (velkými nebo malými písmeny). Například:

```
code,title,group
40000,Členské příspěvky,income
40100,Příjmy z nájmu,income
60020,Odměny dobrovolníkům,expense
```

Řádky s neplatným číslem, neznámou skupinou, chybějícím názvem nebo s
číslem, které už existuje, se přeskočí. Výsledek se ukáže jako
„Importováno *n*, přeskočeno *m*.“ Existující kategorie import nikdy
nemění.

### Seznam kategorií {#categories-list}

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Číslo**, **Název**, **Skupina** | Kategorie. S oprávněním k zápisu jsou v řádku upravitelné; uložíte je ikonou zaškrtnutí. Platí stejná pravidla jako u nové kategorie. |
| Ikona koše | Po potvrzení smaže kategorii. Vyžaduje oprávnění k mazání. |

Pokud žádné nejsou: „Zatím žádné kategorie -- přidejte výše nebo
importujte CSV.“

!!! warning "Smazání kategorie"
    „Smazat tuto kategorii? Položky, které ji používají, zůstanou
    zachovány, jen bez kategorie.“ Řádky faktur, šablony položek a
    položky přijatých faktur kategorii ztratí; minulé platby za ně se
    pak v přehledu zobrazí jako „Bez kategorie“. **Plánované částky této
    kategorie v rozpočtu se smažou.** Kategorii raději přejmenujte, než
    abyste ji mazali a vytvářeli znovu.

## Všechny platby {#all-bookings}

![Všechny platby](../../assets/screenshots/finances/bookings.png)

Otevřete je kartou **Všechny platby** na přehledu. Uvádí každou platbu,
kterou spolek přijal za své faktury, a každou platbu, kterou provedl za
přijaté faktury, napříč všemi účty, nejnovější první. Zápisy, které
nejsou vázány na fakturu (bankovní poplatky, vratky), zahrnuty nejsou
-- ty najdete v [zápisech](bank-accounts.md#bookings-of-an-account)
účtu.

**Filtr**

| Filtr | Co dělá |
|---|---|
| **Hledat** | Najde platby, jejichž odesílatel/příjemce nebo popis obsahuje tento text. |
| **Od** / **Do** | Datum platby v těchto dnech nebo mezi nimi. |
| **Kategorie** | **Všechny kategorie**, nebo jen platby, jejichž faktura má řádek v této kategorii. |
| **Typ** | **Příjmy a výdaje**, **Příjem** nebo **Výdaj**. |
| **Částka od** / **Částka do** | Částka platby v tomto rozmezí. Výdaje se zde počítají jako kladné částky. |
| **Filtrovat** / **Zrušit filtr** | Použije filtr / zruší ho. |

**Tabulka** (záhlaví ukazuje počet, např. „42 plateb“)

| Sloupec | Co ukazuje |
|---|---|
| **Datum** | Datum platby. |
| **Typ** | **Příjem** (zeleně) nebo **Výdaj** (červeně). |
| **Odesílatel / příjemce** | Příjemce faktury nebo odesílatel přijaté faktury. Kliknutím otevřete danou fakturu. |
| **Kategorie** | Všechny kategorie na řádcích faktury, nebo „Bez kategorie“. |
| **Popis** | Názvy a popisy řádků faktury. |
| **Částka** | Zaplacená částka, zeleně u příjmů, červeně u výdajů. |

Pokud nic neodpovídá: „Žádné platby neodpovídají těmto filtrům.“

!!! note "Poznámka"
    Zobrazená částka je celá platba, i když má faktura řádky ve více
    kategoriích. [Účetní přehled](#accounting-statement) ji mezi
    kategorie rozdělí; tento seznam ne.

## Účetní přehled {#accounting-statement}

![Účetní přehled](../../assets/screenshots/finances/accounting-statement.png)

Otevřete ho kartou **Účetní přehled** na přehledu. Titulek je „Účetní
přehled *rok*“. Je to jednoduchý přehled příjmů a výdajů na peněžní
bázi po kategoriích, jaký nezisková organizace předává finančnímu úřadu
nebo předkládá výroční členské schůzi.

**Horní lišta**

| Prvek | Co dělá |
|---|---|
| Rok | Rozbalovací seznam s každým rokem, ve kterém byla zaznamenána platba, plus aktuální rok. Nejnovější je první; změnou se stránka znovu načte. |
| **Exportovat jako PDF** | Stáhne přehled za vybraný rok jako PDF s hlavičkovým papírem vašeho spolku („Přehled příjmů a výdajů *rok*“). |
| **Zpět na Finance** | Zpět na přehled. |

Stránka má dvě karty, **Příjmy** a **Výdaje**, každá uvádí **Kategorie**
(„číslo · název“ nebo „Bez kategorie“) a **Částka**, s řádkem
**Celkem**. Pod nimi je zobrazen **Výsledek** (příjmy minus výdaje)
zeleně, nebo červeně, je-li záporný. Karta bez záznamů uvádí „Pro tento
rok nejsou žádné záznamy.“

Jak se údaje počítají:

- **Počítají se jen peníze, které se skutečně pohnuly.** Příjmy jsou
  platby zaznamenané u vydaných faktur, výdaje platby zaznamenané u
  přijatých faktur. Nezaplacené faktury se neobjeví.
- **Rok určuje datum platby**, ne datum faktury.
- **Každá platba se rozdělí podle kategorií** v poměru řádků faktury.
  Pokud má faktura na 100,00 řádky 80,00 nájem a 20,00 voda, částečná
  platba 50,00 se započítá 40,00 na nájem a 10,00 na vodu. Poplatek za
  upomínku obsažený v platbě se rozdělí stejně.
- Řádky bez kategorie a faktury z doby před používáním kategorií se
  zobrazí jako „Bez kategorie“.
- Zápisy na účtech, které nejsou vázány na fakturu (bankovní poplatky,
  úroky, hotovostní nákupy zadané na účet), zahrnuty **nejsou**. Pokud
  se zde mají objevit, zaznamenejte takové náklady jako
  [přijatou fakturu](incoming-invoices.md) s platbou.

!!! tip "Tip"
    Pro čistý přehled dejte každé položce katalogu a každé položce
    přijaté faktury kategorii *dřív*, než vyúčtování dokončíte nebo účet
    zaznamenáte. Kategorie se na faktury kopírují při dokončení
    vyúčtování a dodatečně je k nim přidat nelze.

## Rozpočet {#budget-plan}

![Rozpočet](../../assets/screenshots/finances/budget.png)

Otevřete ho kartou **Rozpočet** na přehledu. Titulek je „Rozpočet
*rok*“. Otevře se na **příštím roce**. Šipkami **Předchozí rok** /
**Následující rok** v horní liště naplánujete jiný rok; **Zpět na
Finance** vede zpět na přehled.

Tabulka má jeden řádek na účetní kategorii a tyto sloupce:

| Sloupec | Co ukazuje |
|---|---|
| **Kategorie** | Číslo a název. |
| „*rok* skutečnost“ (tři sloupce) | Co bylo skutečně přijato nebo zaplaceno v každém ze tří let před plánovaným rokem, přesně jako v [účetním přehledu](#accounting-statement). U aktuálního roku zní záhlaví „*rok* zatím“, protože rok ještě neskončil. |
| „*rok* plán“ | Částka, kterou pro tuto kategorii plánujete. S oprávněním k zápisu upravitelná. |

Řádky jsou seskupené:

- **Příjmy** -- všechny kategorie skupiny **Příjmy**, s řádkem
  **Celkem**.
- **Výdaje** -- všechny ostatní kategorie (výdaje, dlouhodobý majetek,
  vlastní kapitál a závazky, ostatní), s řádkem **Celkem**.
- **Ostatní (bez kategorie nebo zaúčtováno na druhé straně)** --
  objeví se v části jen v případě potřeby. Obsahuje to, co přehled
  započítal, ale žádný řádek části neukazuje: platby bez kategorie nebo
  například platbu přijaté faktury, jejíž položka nese kategorii
  příjmů. Díky tomu součty částí vždy odpovídají přehledu.
- **Výsledek (příjmy − výdaje)** dole, červeně, je-li záporný.

Plánované částky zadávejte jako čísla, např. `1050.00`, a klikněte na
**Uložit plán**. Uvidíte „Rozpočet uložen.“. „Minulé roky ukazují, co
bylo skutečně zaplaceno (jako v pokladním výkazu). Prázdné pole znamená
„nic neplánováno“.“ Vyprázdněním pole se plán pro danou kategorii
odstraní. Něco, co není číslo, se odmítne zprávou „Zadejte částky jako
čísla, např. 1050.00.“ a nic se neuloží.

Ukládá se jen plán. Sloupce skutečnosti se pokaždé přepočítají ze
zaznamenaných plateb, takže vždy souhlasí s účetním přehledem.

Pokud zatím nemáte žádné kategorie: „Zatím žádné účetní kategorie.
Rozpočet má jeden řádek na kategorii.“ s odkazem **Spravovat
kategorie**.

## Související {#related}

- [Vyúčtování](invoice-runs.md) -- kde řádky faktur dostávají kategorii.
- [Přijaté faktury](incoming-invoices.md) -- kde výdajové položky
  dostávají kategorii.
- [Bankovní účty a zaúčtování](bank-accounts.md)

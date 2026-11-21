# Bankovní účty a zaúčtování {#bank-accounts-and-bookings}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Zde evidujete skutečné účty spolku -- běžné účty, spořicí účet,
pokladnu -- a vidíte vše, co bylo na každém z nich zaúčtováno. Zápisy
můžete přidávat ručně nebo importovat bankovní výpis jako soubor CSV.
Parcella přitom nabízí přiřazení každého zápisu k otevřené faktuře, takže
příchozí převod se rovnou zaznamená jako platba člena.

!!! info "Kdo to může používat"
    Součást modulu **Finance** (ve výchozím stavu vypnutý). Prohlížení
    účtů a zápisů a export CSV vyžaduje oprávnění ke čtení u
    **Finance**. Vytváření nebo změny účtů, přidávání zápisů a import
    vyžadují oprávnění k zápisu; mazání účtů nebo zápisů vyžaduje
    oprávnění k mazání. Členové výboru a administrátoři mohou vše. Viz
    [Finance](index.md).

!!! note "Nejde o úplnou účetní knihu"
    Seznam zápisů účtu je evidence pohybů peněz, ne podvojné
    účetnictví. Neexistuje počáteční ani průběžný zůstatek. Zápisy,
    které nejsou vázány na fakturu (bankovní poplatek, vratka), nemají
    kategorii, takže se v [účetním přehledu](bookkeeping.md#accounting-statement)
    neobjeví.

## Účty {#accounts}

![Účty](../../assets/screenshots/finances/account-list.png)

Otevřete je kartou **Účty** na finančním přehledu. **Zpět na Finance** v
horní liště vás vrátí zpět.

### Nový účet {#new-account}

Zobrazí se s oprávněním k zápisu.

| Pole | Co dělá |
|---|---|
| **Název** | Povinné, např. „Běžný účet Fio“ nebo „Pokladna“. Uložení bez názvu ukáže „Jméno je povinné“. |
| **Typ** | **Banka** nebo **Hotovost**. |
| **Číslo účtu/IBAN** | Volitelné, pro vaši informaci. |
| **Poznámka** | Volitelné. |
| **Aktivní** | Ve výchozím stavu zapnuto. Při zaznamenávání platby se nabízejí jen aktivní účty. Vypněte to u zrušeného účtu: jeho historie zůstane, ale už se nenabízí. |
| **Přidat účet** | Uloží účet. Uvidíte „Hotovo.“. |

### Seznam účtů {#accounts-list}

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Název**, **Typ**, **Číslo účtu/IBAN**, **Poznámka**, **Aktivní** | Údaje účtu. S oprávněním k zápisu jsou v řádku upravitelné; uložíte je ikonou zaškrtnutí. |
| **Zaznamenané platby** | Součet všech plateb vydaných faktur zaznamenaných na tento účet. Platby přijatých faktur a jiné zápisy nejsou zahrnuty. |
| Ikona zápisů | Otevře [zápisy](#bookings-of-an-account) účtu. |
| Ikona zaškrtnutí | Uloží řádek. Vyžaduje oprávnění k zápisu. |
| Ikona koše | Smaže účet po dotazu „Smazat tento účet? Nemá žádné zaúčtování.“ Vyžaduje oprávnění k mazání. U účtu se zápisy je zašedlá (viz níže). |

Pokud zatím žádné účty nejsou: „Zatím žádné účty -- přidejte jeden
výše.“

!!! note "Účty se zápisy nelze smazat"
    Smazat lze jen účet bez jakýchkoli zápisů -- žádný ručně zadaný ani
    importovaný zápis, žádná na něm zaznamenaná platba faktury. U
    každého jiného účtu je koš zašedlý („Má zaúčtování: místo toho
    zrušte zaškrtnutí „Aktivní“.“). Vypnutím **Aktivní** se účet skryje
    z formulářů plateb a všechny jeho zápisy zůstanou.

## Zápisy účtu {#bookings-of-an-account}

![Zápisy účtu](../../assets/screenshots/finances/account-bookings.png)

Otevřete je ikonou zápisů v seznamu účtů. Titulek je „Zápisy — *název
účtu*“. Ukazuje vše, co bylo na tomto účtu zaúčtováno, nejnovější
první:

- platby vydaných faktur zaznamenané s tímto účtem (kladné částky),
- platby [přijatých faktur](incoming-invoices.md) zaznamenané s tímto
  účtem (záporné částky),
- jiné zápisy, které jste zadali ručně nebo importovali (kladné nebo
  záporné, jak byly zadány).

Zobrazí se prvních 50 zápisů; další se načítají automaticky při
posouvání dolů. Tlačítko **Zpět na Finance** v horní liště vás vrátí na
seznam účtů (navzdory svému popisku). Na obrazovkách importu níže vás
stejné tlačítko vrátí na zápisy účtu, aniž by se cokoli importovalo.

### Filtr a akce {#filter-and-actions}

| Pole / tlačítko | Co dělá |
|---|---|
| **Hledat** | Najde zápisy, jejichž reference, popis nebo odesílatel/příjemce obsahuje tento text. |
| **Od** / **Do** | Jen zápisy v těchto dnech nebo mezi nimi. |
| **Částka od** / **Částka do** | Jen zápisy s částkou v tomto rozmezí. Pamatujte, že odchozí peníze jsou záporné: chcete-li najít výdaje 100 a více, nastavte **Částka do** na `-100`. |
| **Přiřazení** | **Vše**, **Přiřazeno k faktuře** (platby faktur) nebo **Nepřiřazeno** (jiné zápisy). Hodí se k nalezení bankovních řádků, které je ještě třeba zkontrolovat. |
| **Filtrovat** / **Zrušit filtr** | Použije filtr / zruší ho. |
| **Export CSV** | Stáhne zápisy odpovídající aktuálnímu filtru jako soubor CSV (oddělený středníky: datum, částka, reference, popis, protistrana). Stačí oprávnění ke čtení. |
| **Import CSV** | Otevře dialog importu, viz [Import bankovního výpisu](#importing-a-bank-statement). Vyžaduje oprávnění k zápisu. |
| **Přidat zápis** | Otevře dialog pro ruční zápis, viz [Ruční přidání zápisu](#adding-a-booking-by-hand). Vyžaduje oprávnění k zápisu. |

### Tabulka zápisů {#bookings-table}

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Datum** | Datum zápisu. |
| **Částka** | Částka; odchozí peníze jsou zobrazeny červeně se znaménkem minus. |
| **Reference** | U platby faktury číslo faktury jako odkaz na fakturu (nebo přijatou fakturu). U jiných zápisů prázdné. |
| **Popis** | Poznámka k platbě nebo popis zápisu. |
| **Odesílatel / příjemce** | Kdo platil nebo komu se platilo: příjemce faktury, odesílatel přijaté faktury nebo protistrana, kterou jste zadali. |
| Ikona koše | Smaže zápis po dotazu „Opravdu smazat tento zápis?“. Jen u ručně zadaných nebo importovaných zápisů a jen s oprávněním k mazání. Platby faktur zde smazat nelze -- smažte je místo toho u faktury. |

Pokud účet nemá žádné zápisy: „Zatím žádné zápisy.“

Po importu nebo přiřazení vám zelená zpráva nahoře řekne, co se stalo,
např. „Importováno 12, přeskočeno 1.“, „3 plateb přiřazeno k existující
faktuře.“, „2 IBAN členů doplněny z importu.“ nebo po jednotlivém zápisu
„Zaznamenáno jako platba k přiřazené faktuře.“

## Ruční přidání zápisu {#adding-a-booking-by-hand}

Klikněte na **Přidat zápis**. Dialog se ptá na:

| Pole | Co dělá |
|---|---|
| **Datum** | Povinné, předvyplněno dneškem. |
| **Částka** | Povinné. Kladná pro příchozí peníze, záporná pro odchozí, např. `-12,50`. |
| **Popis** | Volitelné. |
| **Odesílatel / příjemce** | Volitelné. Používá se také k navržení odpovídající faktury. |
| **Přidat zápis** | Pokračuje ke kroku přiřazení. |

### Možné odpovídající faktury {#possible-matching-invoices}

<!-- No screenshot: this page is only reached by submitting the form above. -->

Než se cokoli uloží, Parcella hledá otevřené faktury se stejnou částkou:
u kladné částky vydané faktury, u kterých zbývá zaplatit přesně tolik;
u záporné částky přijaté faktury, u kterých zbývá zaplatit tolik. Ukáže
**Datum**, **Částka** a **Odesílatel / příjemce** zápisu a pak možnosti:

| Možnost | Co se stane |
|---|---|
| **Zaznamenat jako obecnou platbu** | Uloží běžný zápis na účtu, nevázaný na žádnou fakturu. |
| Jeden řádek na odpovídající fakturu | Ukazuje fakturu (číslo a příjemce, nebo odesílatele a číslo) a „zbývá: *částka*“. Zelený odznak „jméno odpovídá“ se objeví, když zadaný odesílatel/příjemce sdílí jméno s příjemcem nebo odesílatelem faktury. Jeho výběrem se zápis zaznamená jako **platba této faktury**, s tímto účtem, datem a popisem jako poznámkou. |
| **Přidat zápis** | Uloží vaši volbu. |

Navrhuje se nejvýše pět faktur, ty s odpovídajícím jménem první. Pokud
má odpovídající jméno právě jeden návrh, je předvybraný; jinak je
předvybrané **Zaznamenat jako obecnou platbu**. Pokud žádná faktura
neodpovídá: „Žádná otevřená faktura neodpovídá této částce.“

!!! tip "Tip"
    Přiřazení porovnává jen zbývající dlužnou částku, na haléř/cent
    přesně. Faktura s poplatkem za upomínku je dlužná včetně poplatku a
    částečně zaplacená faktura jen ve výši zbytku.

## Import bankovního výpisu {#importing-a-bank-statement}

Většina bank umožňuje stáhnout výpis z účtu jako soubor CSV. Funguje
jakékoli rozložení sloupců. Import má tři kroky.

**1. Nahrání.** Klikněte na **Import CSV**, vyberte soubor a klikněte na
**Import CSV**. „Funguje jakékoli CSV -- nahrajte jej a na další
obrazovce přiřaďte sloupce k polím Parcella.“ Rozpoznají se soubory
oddělené středníkem i čárkou a také UTF-8 i starší kódování Windows.
Prázdný soubor se odmítne zprávou „Tento soubor CSV se zdá být
prázdný.“

**2. Mapování sloupců CSV.** <!-- No screenshot: reached only by uploading a file. -->
„U každého sloupce vyberte, kterému poli Parcella odpovídá (nebo jej
ponechte ignorovaný). Datum a Částka jsou povinné.“ Stránka ukazuje
záhlaví sloupců vašeho souboru, každé s rozbalovacím seznamem, a prvních
pět řádků jako ukázku.

| Pole | Význam |
|---|---|
| **— Ignorovat —** | Sloupec se nepoužije. |
| **Datum** | Povinné. Datum zápisu. Přijímané formáty: `2026-03-31`, `31.03.2026` a `31.03.26`. |
| **Částka** | Povinné. Částka se znaménkem, s desetinnou čárkou nebo tečkou (`-12,50` nebo `-12.50`). Oddělovače tisíců nevadí, jak je banka exportuje: `1.234,56`, `1,234.56` nebo `1 234,56`. |
| **Popis** | Volitelné, např. účel platby. |
| **Odesílatel / příjemce** | Volitelné. Používá se k párování a zobrazuje se v seznamu. |
| **IBAN** | Volitelné. Viz tip níže. |

Běžná německá a anglická záhlaví („Buchungsdatum“, „Betrag“,
„Verwendungszweck“, „Auftraggeber“, „IBAN“ ...) jsou předvybrána;
přesto je zkontrolujte. Pokračujte kliknutím na **Import CSV**. Pokud
**Datum** nebo **Částka** nejsou přiřazeny, budete vráceni se zprávou
„Přiřaďte prosím alespoň jeden sloupec k Datu a Částce.“

**3. Přiřazení řádků k fakturám.** <!-- No screenshot: reached only through the import. -->
„Pro každý řádek vyberte odpovídající otevřenou fakturu, chcete-li ji
zaznamenat jako skutečnou platbu, nebo ji ponechte jako obecnou
platbu.“ Každý řádek ukazuje **Datum**, **Částka**, **Odesílatel /
příjemce** a rozbalovací seznam **Shoda** s možnostmi **Neimportovat**,
**Zaznamenat jako obecnou platbu** a navrženými fakturami (dlužná částka
v závorce, ✓ při shodě jména). Předvýběr funguje jako u jednotlivého
zápisu. Řádky, jejichž datum nebo částku nešlo přečíst, ukazují
„Neplatný řádek — bude přeskočen“. Řádek, který už na tomto účtu je,
dostane odznak **Již importováno** a je přednastaven na
**Neimportovat**. Vše uložíte kliknutím na **Import CSV**.

Co se uloží:

- každý řádek s vybranou fakturou se stane platbou této faktury na
  tomto účtu -- pokud tato faktura mezitím nebyla plně zaplacena: pak se
  nic nezaznamená a výsledná zpráva to uvede;
- každý jiný platný řádek se stane běžným zápisem;
- řádky nastavené na **Neimportovat** a neplatné řádky se přeskočí a
  započítají do výsledné zprávy.

!!! tip "Doplnění IBAN členů"
    Pokud přiřadíte jak **Odesílatel / příjemce**, tak **IBAN**,
    Parcella hledá člena, jehož jméno se přesně shoduje se jménem
    odesílatele (jméno příjmení, nebo příjmení jméno, bez ohledu na
    velikost písmen). Pokud tento člen ještě nemá uložený IBAN, doplní
    se IBAN z výpisu. Existující IBAN se nikdy nepřepisují.

!!! tip "Dvojí import stejného výpisu"
    Řádek se počítá jako již importovaný, když tento účet už má zápis se
    stejným datem, částkou a popisem (počítá se i platba zaznamenaná k
    faktuře). Překrývající se exporty jsou proto bezpečné: přidají se
    jen nové řádky. Parcella počítá, ne jen porovnává -- pokud soubor
    obsahuje tentýž nákup kávy dvakrát v jeden den a účet ho má jednou,
    jeden z nich je nový.

    Řádek, který už existuje, se importuje, jen pokud jeho
    **Neimportovat** změníte na něco jiného. Dvojí kliknutí na **Import
    CSV** nebo opětovné odeslání stránky tlačítkem zpět nic nepřidá.

## Související {#related}

- [Faktury, platby a upomínky](invoices.md)
- [Přijaté faktury](incoming-invoices.md)
- [Všechny platby](bookkeeping.md#all-bookings) -- každá platba faktury
  napříč všemi účty.
- [Členové](../members.md) -- kde je uložen IBAN.

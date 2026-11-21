# Vyúčtování {#invoice-runs}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Vyúčtování je jedna dávka faktur, obvykle „roční faktury 2026“. Jednou
popíšete, které řádky na faktury patří a jak se počítá každá částka.
Parcella pak vypočítá fakturu pro každou parcelu (a pro každého přímo
fakturovaného člena), nechá vás každou zkontrolovat jako PDF a čísla
faktur přidělí až při dokončení.

!!! info "Kdo to může používat"
    Součást modulu **Finance** (ve výchozím stavu vypnutý). Čtení
    vyžaduje oprávnění ke čtení u **Finance**; vytváření vyúčtování,
    úprava položek, dokončení a odesílání vyžadují oprávnění k zápisu;
    smazání vyúčtování nebo položky vyžaduje oprávnění k mazání. Členové
    výboru a administrátoři mohou vše. Viz [Finance](index.md).

Vyúčtování je vždy v jednom ze dvou stavů:

| Stav | Význam |
|---|---|
| **Koncept** | Vyúčtování se připravuje. Položky lze volně přidávat, měnit a odebírat, náhled se přepočítá při každém otevření a celé vyúčtování lze ještě smazat. Zatím neexistuje žádná faktura. |
| **Dokončeno** | Byly vytvořeny faktury s trvalými čísly. Položky jsou zmrazené, vyúčtování už nelze smazat a nyní faktury rozesíláte a zaznamenáváte platby. Cesta zpět ke konceptu neexistuje. |

## Roční vyúčtování (seznam vyúčtování) {#annual-invoices-list-of-runs}

![Roční vyúčtování](../../assets/screenshots/finances/run-list.png)

Otevřete ho přes **Finance → Vydané faktury** nebo kartou **Vydané
faktury** na přehledu. Uvádí všechna vyúčtování, nejnovější rok první.

**Horní lišta**

| Tlačítko | Co dělá |
|---|---|
| **Nové vyúčtování** | Otevře formulář nového vyúčtování (viz níže). Zobrazí se jen s oprávněním k zápisu. |
| **Všechny faktury** | Otevře seznam všech faktur napříč vyúčtováními, viz [Faktury](invoices.md#invoices-all-runs). |
| **Zpět na Finance** | Zpět na finanční přehled. |

**Filtr**

| Filtr | Co dělá |
|---|---|
| **Rok** | Ukáže jen vyúčtování přesně tohoto roku. |
| **Předmět** | Ukáže vyúčtování, jejichž předmět obsahuje tento text (na velikosti písmen nezáleží). |
| **Stav** | **Vše**, **Koncept** nebo **Dokončeno**. |
| **Filtrovat** / **Zrušit filtr** | Použije filtr / zruší všechny filtry. |

**Tabulka vyúčtování**

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Rok** | Rok, který vyúčtování účtuje. |
| **Předmět** | Předmět vyúčtování, jak se tiskne na faktury. |
| **Stav** | **Koncept** (žlutě) nebo **Dokončeno** (zeleně). |
| **Položky** | Kolik definic položek (řádků faktury) vyúčtování má. |
| **Otevřít** | Otevře vyúčtování. |
| Ikona koše | Po potvrzení smaže vyúčtování se všemi definicemi položek. Zobrazí se jen u konceptů a s oprávněním k mazání. Dokončené vyúčtování nelze nikdy smazat. |

Pokud zatím žádná vyúčtování nejsou, tabulka uvádí „Zatím žádná
vyúčtování.“; pokud filtru nic neodpovídá, „Filtru neodpovídá žádné
vyúčtování.“

### Nové vyúčtování {#new-invoice-run}

Klikněte na **Nové vyúčtování** v horní liště. Otevře se dialog:

| Pole | Co dělá |
|---|---|
| **Rok** | Povinné. Předvyplněno aktuálním rokem. Tento rok určuje, které odečty měřidel, záznamy pojištění a vyhodnocení pracovních hodin použijí položky podle spotřeby a ve kterém roce se počítají čísla faktur. |
| **Předmět** | Povinné. Nadpis každé faktury, např. „Roční faktura 2026“. |
| **Datum vystavení** | Povinné. Předvyplněno dneškem. Tiskne se na faktury jako datum faktury. |
| **Datum splatnosti** | Povinné. Tiskne se na faktury. Určuje také, kdy se nezaplacená faktura počítá jako po splatnosti a objeví se v [Upomínky](invoices.md#reminders). |
| **Text patičky** | Volitelné. Tiskne se pod položkami na každé faktuře vyúčtování, např. vaše platební pokyny. Můžete použít tyto zástupné symboly, které se vyplní pro každou fakturu: `{invoice_number}`, `{parcel_number}`, `{invoice_address}` (jména a adresa příjemců), `{due_date}`. |
| **Vytvořit** | Vytvoří vyúčtování jako koncept a otevře ho. |
| **Zrušit** | Zavře dialog bez uložení. |

!!! tip "Zástupné symboly v textu patičky"
    Typická patička je „Částku prosím uhraďte do {due_date} s
    variabilním symbolem {invoice_number}.“ Pokud text patičky obsahuje
    složenou závorku, která není jedním ze čtyř zástupných symbolů,
    vytiskne se text přesně tak, jak jste ho napsali, bez vyplnění.
    Na faktuře člena (bez parcely) není co doplnit za číslo parcely,
    takže se `{parcel_number}` vyhněte, pokud vyúčtování vytvoří i
    faktury členům.
    <!-- TODO(verify): by the code, a member invoice's footer prints the literal word "None" for {parcel_number}; confirm in a real PDF. -->

Rok, předmět, data a text patičky po vytvoření vyúčtování nelze změnit. <!-- TODO(verify): no edit route for run header fields exists; if a mistake is made in a draft run, the only way is to delete and recreate it. -->

## Vyúčtování (koncept) {#invoice-run-draft}

![Koncept vyúčtování](../../assets/screenshots/finances/run-detail.png)

Titulek stránky ukazuje rok a předmět, např. „2026 — Roční faktura“.
Dokud je vyúčtování konceptem, skládáte na této stránce jeho řádky
(„definice položek“).

**Horní lišta**

| Tlačítko | Co dělá |
|---|---|
| **Náhled** | Otevře [náhled](#preview-invoices). Zobrazí se, až má vyúčtování alespoň jednu položku. |
| **Zpět na vyúčtování** | Zpět na seznam. |

### Definice položek {#item-definitions}

Každý řádek je jeden druh řádku, který se může objevit na fakturách. S
oprávněním k zápisu je každý řádek přímo upravitelný; změňte pole a
kliknutím na ikonu zaškrtnutí na konci řádku ho uložte. Bez oprávnění k
zápisu vidíte stejné údaje jako prostý text.

| Sloupec / pole | Co dělá |
|---|---|
| **Pořadí** | Řadicí číslo. Řádky se na faktuře objeví v tomto pořadí. Nová položka je předvyplněna číslem o deset vyšším než dosud nejvyšší, aby zbylo místo pro pozdější vložení položky mezi. |
| **Název** | Povinné. Text řádku na faktuře, např. „Nájem“. |
| **Popis** | Volitelné, malé šedé pole pod názvem. Tiskne se drobným písmem pod názvem na faktuře. |
| **Výpočet** | Jak se částka počítá, viz [Základy výpočtu](#calculation-bases) níže. Jeho změnou se mění, která další pole se zobrazí. |
| **Jednotková cena** | Cena za jednotku (za parcelu, za osobu, za m² ...). U obecné dávky je to celková částka k rozdělení. Skryto u čtyř automatických způsobů výpočtu, které místo toho ukazují „Počítá se automaticky“. Zadejte s desetinnou čárkou nebo tečkou, např. `12,50`. |
| **Platí pro** | Pro koho je řádek. Podle způsobu výpočtu je to přepínač **Všechny parcely** / *n* parcel, přepínač **Všichni členové** / *n* členů, nebo pevná poznámka jako „Automaticky (na základě vyhodnocení pojištění)“. Viz [Kdo dostane řádek](#who-gets-a-line). |
| **Kategorie** | Volitelná [účetní kategorie](bookkeeping.md#bookkeeping-categories). Zkopíruje se na každý řádek faktury, takže platby této faktury se v [účetním přehledu](bookkeeping.md#accounting-statement) rozdělí do správných kategorií. |
| Ikona zaškrtnutí | Uloží řádek. Vyžaduje oprávnění k zápisu. |
| Ikona koše | Po potvrzení („Smazat tuto definici položky?“) smaže položku. Vyžaduje oprávnění k mazání. |

Když u řádku vypnete přepínač **Platí pro**, otevře se pod ním další
řádek s výběrem parcel nebo členů (viz [Výběr](#the-picker)).

!!! note "Poznámka"
    Položky lze měnit, jen dokud je vyúčtování konceptem. Pokus uložit
    položku u dokončeného vyúčtování je odmítnut zprávou „Toto
    vyúčtování je již dokončeno; jeho definice položek již nelze
    měnit.“

### Přidat z katalogu položek {#add-from-item-catalog}

Zobrazí se s oprávněním k zápisu, když váš [katalog položek](#item-catalog)
obsahuje šablony, které toto vyúčtování ještě nemá. Každá zbývající
šablona je uvedena se způsobem výpočtu, jednotkovou cenou a rozsahem a
**je ve výchozím stavu zaškrtnutá**. Odškrtněte, co nechcete, a
klikněte na **Přidat vybrané položky**. Každá zaškrtnutá šablona se
stane novou položkou vyúčtování se všemi svými nastaveními, včetně
konkrétního výběru parcel nebo členů.

**Spravovat katalog** vás vezme do katalogu položek.

Šablona se počítá jako „už přidaná“, když vyúčtování má položku s přesně
stejným názvem. Pokud tedy položku ve vyúčtování přejmenujete nebo
smažete, šablona se nabídne znovu; pokud po přidání přejmenujete
šablonu, nabídne se také znovu.

Když už není co nabídnout, uvidíte místo toho krátkou poznámku:
„Všechny položky z katalogu už byly do tohoto běhu přidány.“ nebo,
pokud je katalog prázdný, „Zatím žádné položky v katalogu -- přidejte
opakující se položky jednou a vybírejte je zde každý rok.“ Obě mají
tlačítko **Spravovat katalog**.

### Přidat položku {#add-item}

Pod katalogem je formulář pro ruční přidání jednorázové položky. Má
stejná pole jako tabulka (**Pořadí**, **Název**, **Popis**, **Způsob
výpočtu**, **Jednotková cena**, **Kategorie**), dále přepínač rozsahu
(**Platí pro každou parcelu** nebo **Platí pro každého člena**, oba ve
výchozím stavu zapnuté) a po jeho vypnutí výběr. Položku přidáte
tlačítkem **+**.

## Základy výpočtu {#calculation-bases}

**Způsob výpočtu** určuje, jak Parcella spočítá řádek pro každou parcelu
nebo člena. Každá částka se zaokrouhluje na haléře/centy po řádcích;
součet faktury je součet jejích řádků.

| Způsob výpočtu | Komu se účtuje | Množství × cena | Odkud čísla pocházejí |
|---|---|---|---|
| **Pevná částka za parcelu** | Každé parcele v rozsahu | 1 × jednotková cena | Částku zadáte vy, např. poplatek spolku za parcelu. |
| **Pevná částka za osobu** | Každému členovi v rozsahu, na vlastní faktuře | 1 × jednotková cena | Částku zadáte vy, např. členský příspěvek. Účtuje se po členech, ať parcelu mají, nebo ne. |
| **Za pronajatý m²** | Každé parcele v rozsahu | rozloha parcely × jednotková cena | Rozloha uložená u parcely. Parcela bez rozlohy řádek nedostane. |
| **Podíl na nájmu společné plochy** | Každé parcele v rozsahu | (společná plocha ÷ počet fakturovaných parcel) × jednotková cena | Společná plocha („rozloha B“) z [Nastavení spolku](../../administration/settings.md). Podíl se zaokrouhluje na 0,1 m². |
| **Veřejné dávky (vlastní plocha + podíl na společné ploše)** | Každé parcele v rozsahu | (rozloha parcely + podíl na společné ploše) × jednotková cena | Jako výše, plus vlastní rozloha parcely, jednou sazbou za m². |
| **Obecná dávka (rozdělena rovnoměrně mezi všechny parcely)** | Každé parcele v rozsahu | 1 × (celkem ÷ počet fakturovaných parcel) | Jako jednotkovou cenu zadáte **celkovou** částku, kterou spolek potřebuje vybrat; každá parcela platí stejný podíl, zaokrouhlený na haléře/centy. |
| **Spotřeba vody (z modulu)** | Každé parcele s vodoměrem | roční spotřeba × cena za jednotku | Spotřeba a cena pocházejí z modulu [Voda a elektřina](../metering.md). |
| **Spotřeba elektřiny (z modulu)** | Každé parcele s elektroměrem | roční spotřeba × cena za jednotku | Jako u vody. |
| **Náklady na pojištění (z modulu)** | Každé parcele s pojištěním na daný rok | jeden řádek za každou složku pojištění | Z modulu [Pojištění](../insurance.md). |
| **Nedoplatek pracovních hodin (z modulu)** | Každé parcele nebo členovi, který dluží peníze za chybějící pracovní hodiny | 1 × dlužná částka | Z [vyhodnocení pracovních hodin](../work-hours.md) za rok vyúčtování. |

Podrobnosti k jednotlivým způsobům:

**Pevná částka za parcelu / za osobu.** Pokud **Jednotková cena**
necháte prázdnou, položka nic neúčtuje.

**Za pronajatý m².** Používá rozlohu zaznamenanou u každé parcely. Před
dokončením zkontrolujte, že každá parcela má rozlohu vyplněnou --
parcela bez ní tiše nedostane žádný řádek za nájem.

**Podíl na nájmu společné plochy.** Společná plocha se rovnoměrně
rozdělí mezi přesně ty parcely, které tuto položku dostanou (ty v jejím
rozsahu, které mají také komu fakturovat). Podíly tak dají dohromady
celou společnou plochu a spolek vybere celý nájem. Pokud je společná
plocha nulová nebo není nastavená, položka neúčtuje vůbec nic. Společná
plocha se v Nastavení spolku počítá jako celková rozloha minus rozloha
parcel minus obecní plocha.

**Veřejné dávky** (viz [slovníček](../../glossary.md)). Jako podíl na
společné ploše, ale přičtený k vlastní rozloze parcely a účtovaný jednou
společnou sazbou. Pokud společná plocha není nastavená, vlastní rozloha
parcely se přesto vyúčtuje -- společná část se prostě počítá jako 0 m².

**Obecná dávka** (viz [slovníček](../../glossary.md)). Použijte ji pro
jednorázový náklad, který spolek přenáší, např. právní poplatek
1 200,00 rozdělený mezi 40 parcel = 30,00 každá. Počítají se jen
skutečně fakturované parcely, takže volné parcely si podíl nikdy
„neukousnou“. Protože se každý podíl zaokrouhluje na haléře/centy, může
se vybraná částka od zadané lišit o několik haléřů.

**Spotřeba vody / Spotřeba elektřiny.** U každé parcely s měrným místem
parcely daného druhu vezme Parcella spotřebu aktuálního měřidla v roce
vyúčtování (odečet za ten rok minus předchozí odečet) a vynásobí ji
cenou za jednotku nastavenou pro ten rok v modulu měření. Jednotkovou
cenu zde nezadáváte.

- Parcela bez odečtu za rok řádek nedostane.
- Pokud pro dané médium a rok není nastavena cena, nikomu se neúčtuje.
- Po výměně měřidla během roku se účtuje spotřeba **obou** měřidel:
  starého do jeho konečného stavu (zadaného ve formuláři výměny) a
  nového od jeho počátečního stavu.

!!! warning "Měrná místa s násobitelem"
    Pokud má měrné místo v modulu měření násobitel, obrazovky měření
    ukazují vynásobenou spotřebu, ale faktura účtuje **surový** rozdíl
    odečtů. Takové parcely zkontrolujte v náhledu.


**Náklady na pojištění.** Účtují se každé parcele, která má záznam
pojištění pro rok vyúčtování. Místo jedné paušální částky ukazuje
faktura jeden řádek za každou složku, kterou parcela skutečně má:
„Pojištění majetku (*balíček*)“, „Úrazové pojištění (domácnost)“ a
případně „Úrazové pojištění (+*n* další osoby)“. Tyto texty řádků jsou
pevné, v jazyce spolku -- vlastní název položky se pro ně nepoužívá.
Částky pocházejí z cen pojištění nastavených pro daný rok.

**Nedoplatek pracovních hodin.** Účtuje přesně tu částku, kterou
vyhodnocení pracovních hodin za rok vyúčtování uvádí jako dlužnou.
Osvobozeným a splněným parcelám nebo členům se neúčtuje. Zda skončí na
faktuře parcely, nebo na samostatné faktuře člena, závisí na tom, jak se
v daném roce počítají pracovní hodiny: po parcelách na faktuře parcely,
po členech na vlastní faktuře každého člena.

## Kdo dostane řádek {#who-gets-a-line}

**Způsoby podle parcel** (pevná částka za parcelu, za m², podíl na
společné ploše, veřejné dávky, obecná dávka) používají přepínač
**Platí pro každou parcelu**:

- Zapnuto (výchozí): každá parcela, kterou lze fakturovat.
- Vypnuto: jen parcely, které zaškrtnete ve výběru.

**Pevná částka za osobu** používá místo toho **Platí pro každého
člena**:

- Zapnuto (výchozí): každý aktivní člen.
- Vypnuto: jen členové, které zaškrtnete.

**Čtyři automatické způsoby** (voda, elektřina, pojištění, nedoplatek
pracovních hodin) výběr nemají. Komu se účtuje, vyplývá z jiného modulu:
z existence měřidla, záznamu pojištění nebo nedoplatku. Místo toho se
zobrazí poznámka jako „Automaticky (parcely s aktivním vodoměrem)“.
(Navzdory formulaci je i vypnuté měrné místo do vyúčtování zahrnuto.)

Které parcely lze vůbec fakturovat:

- Parcela dostane fakturu, jen pokud je alespoň jeden **současný**
  nájemce označen **Použít jako fakturační adresu**. Nájemci, kteří
  dali výpověď k budoucímu datu, se počítají, dokud skutečně neodejdou.
- Ukončená parcela se fakturuje i nadále, pokud takového nájemce má
  (například nového nájemce, který ji převzal dřív, než byl stav
  vrácen). Vždy se přeskakují jen smazané parcely.
- Pokud nájemci s fakturační adresou bydlí na různých adresách,
  parcela přesto dostane **jednu** fakturu (jedno číslo, jedna částka),
  s **kopií pro každou adresu**. Nájemci se společnou adresou jsou
  uvedeni společně na jedné kopii. Kopie se liší jen adresním okénkem.
- Parcela, jejíž řádky vyjdou všechny prázdné, fakturu nedostane.

Faktury členům (z **Pevná částka za osobu** nebo nedoplatku pracovních
hodin počítaného po členech) jsou samostatné faktury adresované členovi
na jeho vlastní adresu. Místo čísla parcely ukazují **Bez parcely
(člen)**. Nájemce, kterému se zároveň účtuje poplatek za osobu, tedy
dostane dvě faktury: jednu za parcelu, jednu za sebe. Všechny řádky za
osobu pro stejného člena se spojí na jedné faktuře.

### Výběr {#the-picker}

Když je přepínač rozsahu vypnutý, objeví se výběr s popiskem
**Parcely** nebo **Členové**.

| Prvek | Co dělá |
|---|---|
| **Zobrazit seznam** / **Skrýt seznam** | Otevře nebo zavře seznam zaškrtávacích políček. |
| **Hledat…** | Zúží seznam na odpovídající čísla parcel nebo jména. Když nic neodpovídá, zobrazí se „Žádné výsledky“. |
| **Vybrat vše** / **Zrušit výběr** | Zaškrtne nebo odškrtne všechny **právě viditelné** položky -- takže můžete nejprve hledat a pak vybrat jen ty. |

Výběr parcel uvádí aktivní parcely; výběr členů uvádí aktivní členy.

!!! tip "Tip"
    Rozsah zůstává upravitelný až do dokončení. Během přípravy
    vyúčtování ho můžete měnit, jak často chcete.

## Náhled faktur {#preview-invoices}

<!-- TODO(verify): no screenshot -- the preview page is two clicks away from a fixed URL (run list -> run -> Preview), which the screenshot tool can't follow, and the sample data has no invoice runs. -->

Klikněte na **Náhled** u konceptu vyúčtování. Parcella spočítá každou
fakturu, kterou by vyúčtování vytvořilo, právě teď, aniž by cokoli
ukládala nebo odesílala. Titulek stránky je „Náhled — *rok* *předmět*“.

Modrý rámeček nahoře uvádí, kolik faktur by se vytvořilo, a
připomíná: „Zatím nic není uloženo ani odesláno — zkontrolujte PDF níže
a poté dokončete.“

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Parcela** | Číslo parcely, nebo **Bez parcely (člen)** u faktury člena. |
| **Příjemce** | Jména, na která bude faktura adresována. |
| **Součet** | Celková částka faktury. |
| **PDF** | Otevře fakturu jako PDF v nové záložce, přesně tak, jak bude vypadat, s „Náhled“ místo čísla faktury a s pruhem „Náhled — dosud nedokončeno ani neodesláno“. |
| **Dokončit a přidělit čísla faktur** | Po potvrzení vyúčtování dokončí. Zobrazí se jen s oprávněním k zápisu, dokud je vyúčtování konceptem. |
| **Zpět na vyúčtování** | Zpět na vyúčtování k opravě položek. |

Pokud je seznam prázdný, stránka uvádí „Nebyly by vytvořeny žádné
faktury — zkontrolujte rozsah parcel v definicích položek a příznak
fakturační adresy u dotčených členů.“

!!! tip "Náhled je vždy aktuální"
    Pro náhled se nic neukládá. Při každém otevření načte aktuální
    parcely, nájemce, odečty měřidel, pojištění a pracovní hodiny.
    Opravte data v těchto modulech a pak stránku prostě znovu načtěte.

### Co dokončení udělá {#what-finalizing-does}

Když kliknete na **Dokončit a přidělit čísla faktur** a potvrdíte
(„Dokončit toto vyúčtování? Čísla faktur budou trvale přidělena a
definice položek už nepůjde měnit. Nelze to vrátit zpět.“):

1. Parcella naposledy spočítá faktury, přesně jako náhled.
2. Každá faktura dostane trvalé číslo, v pořadí seznamu náhledu. Formát
   pochází z **Formát čísla faktury** v
   [Nastavení spolku](../../administration/settings.md) (výchozí
   *rok*/*číslo*, např. `2026/1`). Číslování pokračuje od nejvyššího
   čísla již použitého ve stejném roce, napříč všemi vyúčtováními, a u
   první faktury roku začíná od 1.
3. Jména a adresy příjemců se zkopírují na faktury. Pozdější změny
   adresy člena již vystavenou fakturu nepřepíšou.
4. Vyúčtování se stane **Dokončeno** a jeho položky se zmrazí.

Pokud je v Nastavení spolku vyplněno **Další číslo faktury (přepsat)**,
začne toto vyúčtování místo toho tímto číslem a nastavení se poté
vymaže. Pokud by se tím znovu použilo číslo již přidělené ve stejném
roce, dokončení se zastaví s chybovou zprávou a nic se nevytvoří.

Vyúčtování bez jakékoli položky nelze dokončit: „Toto vyúčtování zatím
nemá žádné definice položek — před dokončením přidejte alespoň jednu.“

## Vyúčtování (dokončené) {#invoice-run-finalized}

Po dokončení stránka vyúčtování ukazuje zelenou poznámku „Toto
vyúčtování je dokončeno. Čísla faktur jsou trvalá, definice položek již
nelze měnit.“ Seznam položek zmizí; místo něj vidíte doručení a faktury
vyúčtování.

### Doručení {#delivery}

Zobrazí se s oprávněním k zápisu.

| Tlačítko | Co dělá |
|---|---|
| **Odeslat e-maily a nahrát do cloudu** | Pošle e-mailem každou fakturu vyúčtování, která ještě nebyla odeslána, s PDF v příloze, a každou dosud nenahranou fakturu nahraje do cloudové složky její parcely. Opětovné spuštění vezme jen to, co ještě chybí. |
| **Stáhnout tiskový balíček** | Stáhne jedno PDF s dopisem pro každého nájemce, který faktury e-mailem nedostává -- jeden dopis na adresu s uvedením lidí na ní bez e-mailu --, připravené k tisku a vložení do obálek s okénkem. Tyto faktury se označí jako vytištěné. |

**Kdo dostane e-mail:** každý nájemce s fakturační adresou uvedený na
faktuře (nebo u faktury člena samotný člen), který má zapnuté **Může
dostávat informace e-mailem** a uloženou alespoň jednu e-mailovou
adresu. Každý dostane kopii pro svou adresu; použije se hlavní
e-mailová adresa. Všichni ostatní dostanou tištěný dopis z tiskového
balíčku -- **i** když někdo, s kým bydlí, dostal e-mail. Nájemci bez
e-mailu se společnou adresou dostanou jeden společný dopis: členové bez
e-mailových upozornění zůstávají pro tiskový balíček níže.

**Nahrání do cloudu** proběhne, jen pokud je nastavené cloudové úložiště
a parcela má cloudovou složku. Faktury členů se nikdy nenahrávají,
protože neexistuje složka člena. Neúspěšná nahrání se tiše přeskočí a
příště se zkusí znovu.

!!! note "Tiskový balíček"
    Balíček se sestavuje podle toho, kdo je dostupný e-mailem, ne podle
    toho, co bylo odesláno. Můžete ho stáhnout před odesláním e-mailů
    i po něm a vždy obsahuje stejné kopie -- včetně těch, které jste
    vytiskli minule. Pokud lze všechny faktury poslat e-mailem, dostanete
    zprávu „U všech faktur v tomto vyúčtování je člen dostupný e-mailem
    -- není co tisknout.“

### Filtr {#filter}

Nad tabulkou faktur můžete seznam zúžit. Funguje jako filtr v
[Všechny faktury](invoices.md#invoices-all-runs): **Č. faktury**,
**Příjemce**, **Parcela** (obsahuje tento text), **Částka od**,
**Částka do** (součet faktury) a **Stav** (**Vše**, **Otevřená**,
**Částečně uhrazená**, **Uhrazená**). **Filtrovat** ho použije,
**Zrušit filtr** ho zruší.

### Faktury {#invoices}

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Č. faktury** | Číslo faktury; kliknutím otevřete [fakturu](invoices.md#invoice). |
| **Parcela** | Číslo parcely, nebo **Bez parcely (člen)**. |
| **Příjemce** | Jména příjemců. |
| **Součet** | Částka faktury. |
| **Stav platby** | **Otevřená** (červeně, nic nezaplaceno), **Částečně uhrazená** (žlutě) nebo **Uhrazená** (zeleně). |
| **Doručení** | Ikony toho, co se stalo: obálka = „Odesláno e-mailem“, tiskárna = „Zahrnuto v tiskovém balíčku“, mrak = „Nahráno do cloudového úložiště“. Najeďte na ikonu myší a uvidíte její význam. |
| **Platba** | Otevře dialog platby pro tuto fakturu (viz níže). Vyžaduje oprávnění k zápisu. |
| **PDF** | Otevře PDF faktury v nové záložce. |

### Dialog platby {#payment-dialog}

Nejrychlejší způsob, jak zaznamenat platby u mnoha faktur: klikněte na
**Platba** v řádku, zadejte platbu a jste zpět na stránce vyúčtování,
připraveni na další. Titulek dialogu je „Platba — Faktura *číslo*“.

Uvádí dosud zaznamenané platby (datum, částka, účet, poznámka), každou s
ikonou koše pro smazání (vyžaduje oprávnění k mazání, ptá se „Smazat
tuto platbu?“). Pokud žádné nejsou: „Zatím nebyly zaznamenány žádné
platby.“

| Pole | Co dělá |
|---|---|
| **Částka** | Povinné. Přijatá částka, např. `45,00`. Částečné platby jsou v pořádku; zaznamenejte každou zvlášť. |
| **Uhrazeno dne** | Povinné. Předvyplněno dneškem. Toto datum určuje, ve kterém roce se příjem počítá v účetním přehledu. |
| **Poznámka** | Volitelné, např. „bankovní převod“. |
| **Účet** | Volitelné. [Účet](bank-accounts.md#accounts), na který peníze přišly. Nabízejí se jen aktivní účty. Platba se pak objeví v zápisech tohoto účtu. |
| **Přidat platbu** | Uloží platbu. |

Stav platby se aktualizuje sám: jakmile platby dosáhnou částky faktury
plus případných poplatků za upomínky, faktura je **Uhrazená**. Viz
[Platby](invoices.md#payments).

## Katalog položek {#item-catalog}

![Katalog položek](../../assets/screenshots/finances/item-templates.png)

Otevřete ho z karty **Katalog položek** na přehledu nebo tlačítkem
**Spravovat katalog** u konceptu vyúčtování. Katalog obsahuje vaše
opakující se řádky faktur („šablony položek“), abyste je nemuseli každý
rok psát znovu. Šablony jsou nezávislé na vyúčtováních; do vyúčtování
je natáhnete pomocí [Přidat z katalogu položek](#add-from-item-catalog).

Obrazovka má stejná pole jako položky vyúčtování:

- **Nová šablona položky** (s oprávněním k zápisu): **Pořadí**,
  **Název**, **Popis**, **Způsob výpočtu**, **Jednotková cena**,
  **Kategorie**, přepínač rozsahu (**Platí pro každou parcelu** /
  **Platí pro každého člena**) a [výběr](#the-picker). Uložíte
  tlačítkem **+**.
- **Šablony položek**: jeden upravitelný řádek na šablonu se sloupci
  **Pořadí**, **Název**, **Výpočet**, **Jednotková cena**, **Platí
  pro** a **Kategorie**. Změňte řádek a uložte ho ikonou zaškrtnutí;
  ikona koše ho smaže (vyžaduje oprávnění k mazání).

Po uložení uvidíte „Uloženo.“. Pokud je katalog prázdný: „Zatím žádné
šablony položek -- přidejte jednu výše.“

Způsoby výpočtu a pravidla rozsahu jsou přesně ta, která jsou popsána v
[Základy výpočtu](#calculation-bases) a [Kdo dostane řádek](#who-gets-a-line).

!!! note "Šablony a vyúčtování jsou nezávislé"
    Přidáním šablony do vyúčtování se šablona zkopíruje. Pozdější změna
    šablony nemění vyúčtování, která ji už použila, a smazání šablony
    ponechá položky těchto vyúčtování beze změny („Smazat tuto šablonu
    položky? Vyúčtování, která ji už použila, si své položky ponechají,
    jen bez odkazu na šablonu.“). Ceny, které se každý rok mění, je
    nejlepší aktualizovat v katalogu dřív, než položky přidáte do
    nového vyúčtování.

## Související {#related}

- [Roční vyúčtování](../../guides/annual-invoicing.md) -- celý postup
  krok za krokem.
- [Faktury, platby a upomínky](invoices.md)
- [Voda a elektřina](../metering.md), [Pojištění](../insurance.md),
  [Pracovní hodiny](../work-hours.md) -- odkud pocházejí automatické
  částky.
- [Nastavení spolku](../../administration/settings.md) -- formát čísla
  faktury, bankovní údaje, rozlohy.

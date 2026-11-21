# Voda a elektřina {#water-and-electricity}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Mnoho spolků nakupuje vodu a elektřinu přes jednu hlavní přípojku a
předává je parcelám přes podružná měřidla. Tato kapitola pokrývá modul
**Voda** i **Elektřina**. Evidují vaše měřidla, shromažďují roční
odečty, počítají spotřebu každé parcely a ukazují, zda měřidla parcel
dávají dohromady to, co ukazuje hlavní měřidlo. Roční cena za jednotku,
kterou zde zadáte, se použije, když faktury účtují spotřebu.

Oba moduly fungují úplně stejně. Liší se jen v tomto:

| | Voda | Elektřina |
|---|---|---|
| Menu | **Voda** | **Elektřina** |
| Jednotka | m³ | kWh |
| Odečty se zadávají s | jedním desetinným místem (např. 145,0) | celými čísly (např. 950) |
| Přepínač modulu | **Správa vody** | **Správa elektřiny** |
| Oprávnění skupiny | **Voda** | **Elektřina** |

Údaje o vodě a elektřině jsou úplně oddělené: parcela může mít měrné
místo vody i měrné místo elektřiny a každé má vlastní měřidla, odečty,
ceny a oprávnění. Snímky obrazovky níže ukazují modul vody. V modulu
elektřiny je vše na stejném místě, s kWh místo m³.

!!! info "Kdo to může používat"
    Oba moduly jsou ve výchozím stavu zapnuté. Ten, který váš spolek
    nespravuje, vypněte v **Administrace → Nastavení** (**Správa vody**,
    **Správa elektřiny**) -- viz
    [Zapínání a vypínání modulů](../administration/modules.md). Data
    zůstanou a po opětovném zapnutí modulu se znovu objeví.

    Správci a členové výboru mohou vše. Ostatní uživatelé potřebují
    [skupinu](../administration/groups.md) s oprávněními **Voda** nebo
    **Elektřina**: *čtení* pro zobrazení stránek a stahování souborů CSV,
    *zápis* pro vytváření měrných míst, zaznamenávání odečtů, výměnu
    měřidel, import a nastavení cen, *mazání* pro mazání měrných míst,
    odečtů a cen.

V bočním menu má každý modul položky **Přehled**, **Měrná místa**,
**Odečty**, **Vyhodnocení** a **Konfigurace**.

## Měrná místa a měřidla {#metering-points-and-meters}

Všude se používají dva pojmy:

- **Měrné místo** je místo, kde se měří spotřeba. Je jedním ze tří
  typů:
    - **Hlavní měřidlo** -- místo předání od dodavatele, kde spolek
      přebírá vodu nebo elektřinu,
    - **Parcela** -- přípojka jedné parcely,
    - **Spolek** -- přípojka ve vlastnictví spolku, například klubovna
      nebo mycí místo.
- **Měřidlo** je fyzické zařízení na měrném místě s vlastním číslem.
  Když se měřidlo vymění, měrné místo zůstane a dostane nové měřidlo;
  staré se uchová v historii.

## Jak fungují odečty a spotřeba {#how-readings-and-consumption-work}

Tato pravidla platí všude, kde se zadávají odečty -- na stránce odečtů,
na stránce měrného místa i v importu CSV.

- **Jeden odečet na měřidlo a rok.** Každý odečet patří k roku (roku
  vyúčtování) a má datum. Pokud zaznamenáte odečet za rok, který už
  odečet má, stará hodnota, datum a poznámka se **nahradí**. Tak také
  opravíte chybu.
- **Spotřeba** roku = odečet tohoto roku minus poslední odečet z
  dřívějšího roku. Pokud dřívější odečet neexistuje, použije se
  **Počáteční stav** měřidla. Bez odečtu za rok není žádná spotřeba
  („žádný odečet“ nebo „–“).
- **Rok se neodvozuje z data.** Odečet provedený v lednu může ještě
  patřit k cyklu minulého roku. Rok vždy volíte sami.

### Upozornění na nevěrohodnost {#plausibility-warnings}

Měřidlo běžně počítá jen nahoru. Parcella vás varuje -- ale **odečet
přesto uloží** --, když:

- odečet je **nižší než předchozí odečet** stejného měřidla (poslední
  dřívější rok nebo počáteční stav), nebo
- odečet je **vyšší než již zaznamenaný pozdější odečet** stejného
  měřidla.

Hned po uložení uvidíte žlutý pruh, například **Odečet uložen, ale
zkontrolujte ho prosím: Odečet měřidla (110.0) je menší než předchozí
odečet (120.5) stejného měřidla. Byl dřívější odečet odhadnut?
Zkontrolujte to prosím.** Varování zůstává viditelné vedle odečtu na
stránce měrného místa a na stránce odečtů, dokud hodnoty nesedí.

!!! tip "Proč jen varuje"
    Pokud byl loňský odečet odhadnut příliš vysoko, je letošní skutečný
    odečet nižší. Jeho zablokování by znemožnilo zadat skutečnou
    hodnotu. Zaznamenejte skutečný odečet a pak opravte odhadnutý.

Druhá kontrola porovnává součty: pokud parcely a přípojky spolku
dohromady za rok spotřebovaly **více** než hlavní měřidlo, uvádí to
červený pruh v přehledu a ve vyhodnocení. Je to nápověda, ne chyba:
dokud se odečty ještě sbírají, bývají čísla často neúplná.

### Výměna měřidla {#meter-exchange}

Když se měřidlo vymění -- například proto, že mu vypršela kalibrace --,
použijte **Vyměnit měřidlo** na [stránce měrného místa](#metering-point-page).
Staré měřidlo se nesmaže: označí se jako odstraněné a uvede se v
**Předchozí měřidla** se svým posledním odečtem. Nové měřidlo začíná
vlastním **Počáteční stav**, takže staré a nové odečty se nikdy
nesmíchají.

**Konečný stav starého měřiče.** Zadejte, co staré měřidlo ukazuje v den
odstranění. Uloží se jako odečet starého měřidla za tento rok a roční
spotřeba měrného místa pak sečte obě měřidla: staré do jeho konečného
stavu, nové od jeho počátečního stavu. Faktura i **Vyhodnocení** tento
součet používají; vyhodnocení takové místo označí „vč. vyměněného
měřidla“. Bez konečného stavu se za tento rok počítá jen nové měřidlo.


**Vyměnit** je pro skutečnou výměnu. Pokud jste jen špatně napsali číslo
měřidla nebo datum, použijte místo toho **Upravit měřidlo** -- opraví
aktuální měřidlo bez vytvoření nového.

### Násobitel {#factor}

Některá měřidla ukazují jen část toho, co jimi skutečně proteče. Velký
elektroměr za měřicími transformátory proudu může počítat 1/20 energie,
takže jeho displej je třeba násobit 20. U takového měrného místa
nastavte **Násobitel** (obvykle 1):

- Odečty se stále zadávají přesně tak, jak je ukazuje displej; kontrola
  věrohodnosti pracuje s těmito hodnotami.
- Spotřeba se v tomto modulu násobí násobitelem (zaokrouhleno na dvě
  desetinná místa, pokud násobitel není 1). Násobitel patří k měrnému
  místu, takže přežije výměnu měřidla, a jeho změna platí pro všechny
  roky.
- Místa s násobitelem jiným než 1 ukazují odznak jako **×20**.

!!! warning "Násobitel se na fakturách nepoužívá"
    Faktury účtují prostý rozdíl mezi odečty, bez násobitele.

### Vypnutí měrného místa {#switching-a-metering-point-off}

Pokud přípojka nějakou dobu nemá dodávku -- voda zavřená, elektřina
parcely odpojená --, **vypněte ji** místo smazání. Vypnuté místo:

- se už neobjevuje na stránce odečtů, v exportu CSV odečtů ani v počtu
  „ještě nemá odečet“ -- **pokud už nemá odečet za tento rok**, takže
  konečný odečet zůstává viditelný a upravitelný,
- je v seznamu zašedlé s odznakem **Vypnuto**,
- ponechává si všechna měřidla a odečty.

Pro vyúčtování není potřeba nic zvláštního: bez odečtu za rok není
spotřeba, takže se nic neúčtuje. Opětovným zapnutím se místo vrátí.

## Přehled {#overview}

![Přehled vody](../assets/screenshots/water/overview.png)

Úvodní stránka modulu s titulkem **Voda** (nebo **Elektřina**) a rokem.
Sem přijdete, chcete-li vidět, zda jsou všechny odečty za rok zadané a
zda čísla sedí.

![Přehled elektřiny](../assets/screenshots/electricity/overview.png)

| Pole / tlačítko | Co dělá |
|---|---|
| Výběr roku | Přepne rok. Uvádí každý rok s odečty plus aktuální rok. |
| **Zaznamenat odečet** | Otevře [stránku odečtů](#readings_1) pro tento rok. |
| Červený pruh | Parcely a přípojky spolku dohromady spotřebovaly v tomto roce více než hlavní měřidlo. |
| Modrý pruh | **... měrné(ých) místo(a) ještě nemá(í) odečet pro ...**, s **Zaznamenat nyní →**. Počítá aktivní místa s měřidlem a bez odečtu za rok. |
| Dlaždice **Hlavní měřidlo** | Spotřeba hlavního měřidla (měřidel) a kolik jich je. **Zobrazit** je vypíše. |
| Dlaždice **Parcely** | Celková spotřeba všech měrných míst parcel a kolik jich je. **Zobrazit** je vypíše. |
| Dlaždice **Přípojky spolku** | Totéž pro přípojky spolku. |
| Dlaždice **Rozdíl** | Hlavní měřidlo minus parcely a spolek (**Hlavní - rozdělený**): voda nebo elektřina, kterou nelze doložit, např. kvůli únikům nebo pomalu běžícím měřidlům. Červeně, je-li záporný. |
| Dlaždice **Chybějící měřicí body** | Kolik parcel nemá pro toto médium měrné místo. **Zobrazit** je vypíše. Počítají se i ukončené parcely -- do nástupu dalšího nájemce je stále třeba je sledovat. |
| **Všechna měrná místa** | Otevře [seznam](#metering-points). |
| **Nové měrné místo** | Otevře [formulář](#new-metering-point). Vyžaduje oprávnění k zápisu. |
| **Výroční zpráva** | Otevře [Vyhodnocení](#evaluation) za tento rok. |

## Měrná místa {#metering-points}

![Měrná místa](../assets/screenshots/water/metering-points.png)

Všechna měrná místa tohoto média: nejprve hlavní měřidla, pak parcely
podle čísla parcely, pak přípojky spolku podle označení.

| Pole / tlačítko | Co dělá |
|---|---|
| **Zpět** | Vrátí se na přehled. |
| **CSV import** | Otevře dialog pro nahrání souboru CSV (viz [Import měrných míst](#importing-metering-points)). Vyžaduje oprávnění k zápisu. |
| **CSV export** | Stáhne všechna měrná místa (viz níže). |
| **Nové měrné místo** | Otevře [formulář](#new-metering-point). Vyžaduje oprávnění k zápisu. |
| **Vše** / **Aktivní** / **Vypnuto** | Ukáže všechna místa, jen aktivní, nebo jen vypnutá. |
| Pruh filtru | Když jste přišli z dlaždice přehledu, šedý pruh uvádí filtr (např. **Parcela**). **Zrušit filtr** opět ukáže vše. |

| Sloupec | Co ukazuje / dělá |
|---|---|
| **Typ** | **Hlavní měřidlo**, **Parcela** nebo **Spolek**. |
| **Měrné místo** | „Parcela“ plus číslo parcely, nebo označení. Odkazuje na [stránku měrného místa](#metering-point-page). |
| **Číslo měřidla** | Číslo aktuálního měřidla, s odznakem **×**, pokud je nastaven násobitel; **žádné aktivní měřidlo**, pokud žádné není. |
| **Stav** | **aktivní**, **Vypnuto** (najetím myší uvidíte od kdy), nebo **bez měřidla**. |
| **Kalibrováno do** | Rok, kdy kalibrace aktuálního měřidla vyprší. Výstražný trojúhelník znamená **Kalibrace vypršela** -- rok byl dosažen. |
| Tlačítko s okem | Otevře stránku měrného místa. |
| Koš | Po varování **Opravdu smazat toto měrné místo? Všechny přidružené měřiče a odečty budou také smazány.** smaže měrné místo. Vyžaduje oprávnění k mazání. |

Počet měrných míst se zobrazuje pod tabulkou.

!!! warning "Smazání odstraní celou historii"
    Smazání měrného místa smaže i všechna jeho měřidla a odečty, takže
    zmizí i minulá spotřeba. Pokud je přípojka jen mimo provoz,
    [vypněte ji](#switching-a-metering-point-off).

### Chybějící měřicí body {#missing-metering-points}

![Parcely bez měrného místa](../assets/screenshots/water/metering-points-missing.png)

Otevírá se tlačítkem **Zobrazit** na dlaždici **Chybějící měřicí body**.
Místo tabulky stránka vypisuje každou parcelu bez měrného místa pro toto
médium -- ukončené parcely jsou označeny **(ukončená)**. **Přidat měřicí
bod** otevře [formulář](#new-metering-point) s již vybranou parcelou
(oprávnění k zápisu). Pokud nic nechybí, uvádí **Každá parcela má
měřicí bod.**

### Export CSV (měrná místa) {#csv-export-metering-points}

Soubor oddělený středníky s jedním řádkem na měrné místo a jeho
aktuální měřidlo: typ, číslo parcely, označení, číslo měřidla,
instalováno, kalibrováno do, počáteční stav, aktivní, neaktivní od,
násobitel. Má stejný formát, jaký očekává import, takže můžete
exportovat, upravit v tabulce a nová místa znovu importovat.

## Import měrných míst {#importing-metering-points}

Užitečné při prvním nastavení modulu. Klikněte na **CSV import** v
seznamu měrných míst, vyberte soubor `.csv` a klikněte na
**Importovat**. Sloupce nemusí mít zvláštní názvy -- přiřadíte je na
další stránce. Rozpoznají se středníky i čárky a fungují i soubory ze
starších verzí Excelu (ne UTF-8).

### Mapování sloupců CSV {#map-csv-columns}

Snímek této stránky není, protože se objeví až po nahrání souboru.

Stránka ukazuje každý sloupec vašeho souboru s prvními pěti řádky. Nad
každým sloupcem vyberte, ke kterému poli patří, nebo **— Ignorovat —**.
Parcella odhadne přiřazení podle záhlaví sloupců, anglických nebo
německých (například „Zählernummer“ se stane **Číslo měřiče**).

| Pole | Co znamená |
|---|---|
| **Typ** | `MAIN_METER`, `PARCEL` nebo `CLUB`. Pokud sloupec Typ vůbec nepřiřadíte, každý řádek se považuje za parcelu -- typické pro prostý seznam měřidel parcel. |
| **Číslo parcely** | U řádků parcel: číslo existující parcely. |
| **Označení** | Název hlavního měřidla nebo přípojky spolku. |
| **Číslo měřiče** | Číslo měřidla. |
| **Instalováno** | Datum jako 2026-09-18 nebo 18.09.2026. |
| **Kalibrováno do** | Rok, například 2032. Funguje i datum; použije se jeho rok. Hodnota bez čtyřmístného roku řádek přeskočí. |
| **Počáteční stav** | Stav měřidla při instalaci; prázdné = 0. |
| **Násobitel** | Prázdné = 1. |
| **Importovat** | Vytvoří měrná místa. Přiřazen musí být alespoň jeden sloupec. |

Co se stane:

- Vytvářejí se jen **nová** měrná místa; existující se nikdy nemění.
  Řádek parcely se přeskočí, pokud parcela už měrné místo má, a řádek
  hlavního měřidla nebo spolku, pokud existuje jedno se stejným
  označením -- dvojí import stejného souboru tedy nic nepokazí. Řádky
  hlavních měřidel nebo přípojek spolku bez označení nelze ověřit a
  vytvoří se vždy.
- Řádky se přeskočí, pokud je typ neplatný, číslo parcely neexistuje
  nebo je násobitel neplatný.
- Nová místa začínají jako aktivní.

Poté seznam ukáže souhrn jako **12 importováno, 2 přeskočeno** s důvody
u prvních tří přeskočených řádků.


## Nové měrné místo {#new-metering-point}

![Nové měrné místo](../assets/screenshots/water/metering-point-form.png)

Otevírá se z přehledu, ze seznamu nebo tlačítkem **Přidat měřicí bod**
u parcely bez něj. Vyžaduje oprávnění k zápisu. První karta popisuje
měrné místo, druhá jeho měřidlo.

| Pole | Co dělá |
|---|---|
| **Typ** | **Parcela**, **Přípojné místo ve vlastnictví spolku** nebo **Hlavní měřidlo (bod předání energií)**. |
| **Parcela** | Zobrazí se u míst parcel. Nabízí aktivní a ukončené parcely. |
| **Označení** | Zobrazí se u míst spolku a hlavních měřidel, například „klubovna“. |
| **Poznámky** | Cokoli užitečného, např. kde měřidlo je. |
| **Číslo** | Povinné. Číslo měřidla. Stejné číslo se může objevit vícekrát -- Parcella duplicity nekontroluje. |
| **Kalibrováno do (rok)** | Rok, kdy kalibrace vyprší, např. 2032. |
| **Instalováno** | Předvyplněno dneškem. |
| **Počáteční stav** | Stav měřidla při instalaci; z něj se počítá spotřeba prvního roku. Výchozí 0. |
| **Násobitel** | Násobitel z displeje na skutečnou spotřebu, obvykle 1 (viz [Násobitel](#factor)). Musí být větší než 0, nejvýše 100 000, s nejvýše čtyřmi desetinnými místy. |
| **Zrušit** / **Vytvořit měrné místo** | Uložením se otevře stránka nového měrného místa. |

!!! tip "Tip"
    **Parcela** a **Označení** jsou označeny jako povinné, ale formulář
    vás nezastaví, když je necháte prázdné. Vždy je vyplňte, jinak
    odečty tohoto místa nelze přiřadit v importu CSV a místo se v
    seznamech špatně hledá.

## Stránka měrného místa {#metering-point-page}

![Stránka měrného místa](../assets/screenshots/water/metering-point-detail.png)

Vše o jednom měrném místě: jeho údaje, aktuální měřidlo, odečty a
předchozí měřidla.

| Tlačítko (nahoře) | Co dělá |
|---|---|
| **Předchozí** / **Další** | Přejde na předchozí nebo další měrné místo v pořadí seznamu. Také pomocí Ctrl+← a Ctrl+→. |
| **Zpět** | Vrátí se na seznam. |

### Měrné místo {#metering-point}

Ukazuje **Typ**, **Stav** (**aktivní** nebo **Vypnuto** s datem **od**),
**Parcela** (s odkazem), **Násobitel**, pokud není 1, a **Poznámky**.

S oprávněním k zápisu můžete měnit:

| Pole / tlačítko | Co dělá |
|---|---|
| **Označení** | U míst parcel volitelné (např. „Východní vchod“); u míst spolku a hlavních měřidel jejich název. |
| **Poznámky** | Volný text. |
| **Násobitel** | Viz [Násobitel](#factor). Mění spotřebu všech let, včetně minulých. Neplatné hodnoty se odmítnou s vysvětlením. |
| **Uložit** | Uloží tato tři pole. |
| **Vypnout od** + **Vypnout** | Vypne místo od zvoleného data (výchozí dnes). Viz [Vypnutí měrného místa](#switching-a-metering-point-off). |
| **Znovu zapnout** | Zobrazí se u vypnutých míst. |

### Aktuální měřidlo {#current-meter}

Ukazuje **Číslo**, **Instalováno**, **Kalibrováno do** (s odznakem
**Kalibrace vypršela**, jakmile je rok dosažen) a **Počáteční stav**.
Pokud žádné není: **Pro toto měrné místo neexistuje aktivní měřidlo.**

S oprávněním k zápisu jsou zde dvě tlačítka:

**Upravit měřidlo** -- opraví aktuální měřidlo na místě, při překlepech:

| Pole | Co dělá |
|---|---|
| **Číslo** | Povinné. |
| **Instalováno**, **Kalibrováno do**, **Počáteční stav** | Změní uložené hodnoty. Změna počátečního stavu změní spotřebu prvního roku měřidla. |
| **Uložit** | Uloží bez vytvoření nového měřidla. |

**Vyměnit měřidlo** -- zaznamená fyzickou výměnu měřidla (viz
[Výměna měřidla](#meter-exchange)):

| Pole | Co dělá |
|---|---|
| **Staré měřidlo odstraněno dne** | Povinné, výchozí dnes. |
| **Konečný stav starého měřiče** | Co staré měřidlo ukazuje v den odstranění. Uloží se jako jeho odečet za tento rok, takže se vyúčtuje jeho spotřeba až do výměny. Nápověda: v den odstranění; bez něj se spotřeba starého měřidla od jeho posledního odečtu nevyúčtuje. |
| **Nové měřidlo nainstalováno dne** | Povinné, výchozí dnes. |
| **Nové číslo** | Povinné. |
| **Kalibrováno do** | Rok kalibrace nového měřidla. |
| **Počáteční stav** | Stav nového měřidla při instalaci, výchozí 0. |
| **Vyměnit** | Po potvrzení **Opravdu chcete vyměnit měřidlo? Staré měřidlo bude deaktivováno.** se staré měřidlo přesune do **Předchozí měřidla**. |

### Odečty {#readings}

Odečty aktuálního měřidla, nejnovější rok první.

| Sloupec | Co ukazuje / dělá |
|---|---|
| **Rok** | Rok vyúčtování. |
| **Datum** | Datum odečtu. |
| **Stav měřiče (m³)** | Hodnota, jak ji ukazuje měřidlo, se žlutým varováním na nevěrohodnost, pokud nesedí. |
| **Spotřeba (m³)** | Spotřeba v daném roce, vynásobená násobitelem (zobrazeným jako odznak v záhlaví). |
| **Poznámka** | Vaše poznámka. |
| Koš | Po potvrzení smaže odečet. Vyžaduje oprávnění k mazání. |

**Zaznamenání odečtu** (oprávnění k zápisu), pod tabulkou:

| Pole | Co dělá |
|---|---|
| **Rok** | Povinné, výchozí aktuální rok. |
| **Datum** | Povinné, výchozí dnes. |
| **Odečet měřidla (m³)** | Povinné. Jako desetinný oddělovač funguje čárka i tečka. |
| **Poznámka** | Volitelné, např. „odhad“. |
| **Zaznamenat odečet** | Uloží odečet. Pokud rok už odečet má, nahradí se. Text, který není číslo, se odmítne zprávou **Neplatný odečet měřidla**. |

### Předchozí měřidla {#former-meters}

Vyměněná měřidla, naposledy odstraněná první, s údaji **Číslo**,
**Instalováno**, **Odstraněno** a **Poslední odečet**.

## Odečty {#readings_1}

![Odečty](../assets/screenshots/water/readings.png)

Stránka pro sběr ročních odečtů, navržená tak, aby fungovala v telefonu
během obchůzky areálu. Otevřete ji položkou **Odečty** v menu nebo
tlačítkem **Zaznamenat odečet** v přehledu. Titulek ukazuje médium a
rok, např. „Odečet vody 2026“.

| Pole / tlačítko | Co dělá |
|---|---|
| Výběr roku | Rok, za který zaznamenáváte: příští rok, tento rok nebo jeden ze tří předchozích. |
| **CSV import** | Nahrání odečtů ze souboru (viz [Import odečtů](#importing-readings)). Vyžaduje oprávnění k zápisu. |
| **CSV export** | Stáhne seznam tohoto roku (viz níže). |
| **Zpět** | Vrátí se na přehled. |

Stránka vypisuje každé měrné místo, které letos potřebuje odečet, ve
třech skupinách: **Hlavní měřidlo**, **Parcely** (podle čísla parcely) a
**Přípojky spolku**. Vypnutá místa se objeví, jen pokud už mají odečet
za rok. Každý řádek ukazuje:

- název měrného místa a číslo měřidla,
- **Předchozí rok**: poslední odečet před tímto rokem, nebo počáteční
  stav -- nová hodnota by neměla být nižší,
- pokud je odečet už zadán: hodnotu s **zaznamenáno** a případné
  varování na nevěrohodnost,
- jinak, s oprávněním k zápisu, vstupní pole a tlačítko zaškrtnutí.
  Napište hodnotu a stiskněte tlačítko; datum se nastaví na dnešek. Bez
  oprávnění k zápisu: **Zatím nezadáno**.

!!! tip "Oprava zaznamenané hodnoty"
    Jakmile je hodnota zaznamenaná, na této stránce ji změnit nelze.
    Otevřete stránku měrného místa a zaznamenejte odečet za stejný rok
    znovu -- nahradí ten starý.

### Export CSV (odečty) {#csv-export-readings}

Soubor oddělený středníky pro vybraný rok s jedním řádkem na měrné
místo, které potřebuje odečet: typ, číslo parcely, označení, číslo
měřidla, rok, datum, stav, poznámka. Datum a stav jsou prázdné tam, kde
ještě nic není zaznamenáno -- hodí se jako formulář pro toho, kdo
odečítá měřidla, který můžete vyplnit a znovu importovat.

## Import odečtů {#importing-readings}

Klikněte na **CSV import** na stránce odečtů, vyberte soubor a klikněte
na **Importovat**. Jeden soubor může obsahovat odečty za více let.

### Mapování sloupců CSV {#map-csv-columns_1}

Snímek této stránky není, protože se objeví až po nahrání souboru.

Stejně jako u měrných míst vyberte u každého sloupce, ke kterému poli
patří, nebo **— Ignorovat —**.

| Pole | Co znamená |
|---|---|
| **Typ** | `MAIN_METER`, `PARCEL` nebo `CLUB`. Pokud není přiřazen, každý řádek se počítá jako parcela. |
| **Číslo parcely** / **Označení** | Najde měrné místo: číslo parcely u parcel, označení u hlavních měřidel a přípojek spolku. |
| **Číslo měřiče** | Volitelná kontrola: pokud neodpovídá **aktuálnímu** měřidlu místa, řádek se přeskočí, protože odečet může patřit měřidlu, které bylo mezitím vyměněno. |
| **Rok** | Rok vyúčtování řádku. |
| **Datum** | Povinné. 2026-09-18 nebo 18.09.2026. |
| **Stav měřiče** | Povinné. |
| **Poznámka** | Volitelné. |
| **Výchozí rok (volitelné)** | Použije se u každého řádku, kde Rok není přiřazen nebo je prázdný. Vlastní Rok řádku má vždy přednost. Parcella nikdy neodhaduje rok z data. |
| **Importovat** | Zaznamená odečty. Přiřazen musí být alespoň jeden sloupec. |

Co se stane:

- Odečty se přidávají jen k **existujícím** měrným místům; import nikdy
  nevytvoří nové.
- Odečet za rok, který už odečet má, ho nahradí.
- Řádky se přeskočí, pokud měrné místo nebylo nalezeno, nemá aktivní
  měřidlo, číslo měřidla neodpovídá nebo rok, datum či stav chybí nebo
  jsou neplatné.
- Nevěrohodné odečty se přesto zaznamenají, stejně jako při ručním
  zadání.

Poté stránka odečtů ukáže souhrn jako **40 odečtů zaznamenáno, 2
přeskočeno (měřicí bod nenalezen)** s prvními několika důvody a --
pokud je třeba -- žlutý pruh **... odečet/odečtů zaznamenáno s
upozorněním na nevěrohodnost** s uvedením dotčených řádků.

## Vyhodnocení {#evaluation}

![Vyhodnocení](../assets/screenshots/water/evaluation.png)

Roční přehled spotřeby s titulkem např. „Zpráva o vodě 2026“. Otevřete
ho položkou **Vyhodnocení** v menu nebo tlačítkem **Výroční zpráva** v
přehledu.

| Pole / tlačítko | Co dělá |
|---|---|
| Výběr roku | Uvádí každý rok s odečty plus aktuální rok. |
| **CSV export** | Stáhne zprávu (viz níže). |
| **Zpět** | Vrátí se na přehled. |
| Červený pruh | **Rozdělená spotřeba (...) přesahuje spotřebu hlavního měřidla (...).** -- viz [Upozornění na nevěrohodnost](#plausibility-warnings). |

Tři dlaždice ukazují **Hlavní měřidlo**, **Parcely celkem** a **Spolek
celkem**. Pod nimi jsou tři tabulky -- **Hlavní měřidlo**, **Parcely** a
**Přípojky spolku** --, každá s **Měrné místo** (s odkazem), **Číslo
měřidla** a **Spotřeba (m³)**, nebo *žádný odečet*, kde odečet za rok
chybí. Spotřeba zahrnuje násobitel.

Export CSV (středníky) používá záhlaví sloupců stránky v jazyce spolku:
typ, měrné místo, číslo měřidla, stav a spotřeba (s jednotkou).

## Konfigurace cen {#price-configuration}

![Konfigurace cen](../assets/screenshots/water/configuration.png)

Cena za m³ nebo kWh pro každý rok. Vyúčtování ji používá pro položky
**Spotřeba vody (z modulu)** a **Spotřeba elektřiny (z modulu)**:
spotřeba × cena roku vyúčtování. Pokud pro tento rok není nastavena
cena, tyto položky nic neúčtují. Každý rok si ponechává vlastní cenu,
takže minulá vyúčtování zůstávají správná, i když se cena změní.
Otevřete **Konfigurace** v menu.

### Nová/aktualizovaná cena {#newupdate-price}

Vyžaduje oprávnění k zápisu.

| Pole | Co dělá |
|---|---|
| **Rok** | Povinné, předvyplněno aktuálním rokem. |
| **Cena za m³** (nebo **za kWh**) | Povinné, např. 2.50. Ukládá se na dvě desetinná místa. |
| **Poznámka** | Např. „změna sazby dodavatele“. |
| **Uložit** | Uloží cenu. Pokud rok už cenu má, **přepíše** se. |

### Historie cen {#price-history}

Všechny roky, nejnovější první, s údaji **Rok**, **Cena** (za jednotku)
a **Poznámka**. Tužka otevře [Upravit cenu](#edit-price) (oprávnění k
zápisu); koš po potvrzení smaže cenu roku (oprávnění k mazání).

## Upravit cenu {#edit-price}

Snímek této stránky není, protože ukázková data neobsahují žádné ceny.

Otevírá se tužkou v historii cen. Pole: **Rok**, **Cena za m³** (nebo
**za kWh**) a **Poznámka**, s tlačítky **Zrušit** a **Uložit**. Pokud
změníte rok na takový, který už cenu má, Parcella odmítne se zprávou
**Pro rok ... již existuje jiná konfigurace ceny.**

<!-- TODO(verify): confirm that already-created invoices keep their amounts when a year's price is changed afterwards. -->

## Související {#related}

- [Odečty měřidel](../guides/meter-readings.md) -- roční postup krok za
  krokem
- [Vyúčtování](finances/invoice-runs.md) a
  [Roční vyúčtování](../guides/annual-invoicing.md) -- vyúčtování
  spotřeby
- [Parcely](parcels.md) -- parcely, ke kterým měrná místa patří
- [Import členů a parcel](../guides/csv-import.md) -- stejný způsob
  přiřazení sloupců u dalších importů
- [Přehledy](reporting.md)

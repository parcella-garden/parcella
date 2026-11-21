# Procesy {#processes}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Mnoho prací ve spolku probíhá pokaždé stejnými kroky: předání zahrádky,
přivítání nového člena, vyřízení stížnosti. S procesy takovou práci
popíšete jednou jako **šablonu** -- řadu **fází**, každou s **poli** k
vyplnění -- a pak ji spouštíte, jak často potřebujete, pro zahrádku,
člena nebo uchazeče. Parcella sleduje, kde každé spuštění je, co bylo
zadáno a kdo co udělal.

!!! info "Kdo to může používat"
    - Přepínač modulu je **Procesy** v **Administrace → Zapínání a
      vypínání modulů**. Ve výchozím stavu je **zapnutý**.
    - Role **Výbor** a **Správce** a členové skupiny s **Plný přístup ke
      každému modulu** mohou vše, včetně tvorby šablon.
    - Všichni ostatní potřebují oprávnění **Procesy** v některé ze svých
      [skupin](../administration/groups.md):
        - *čtení*: vidět procesy, jejich hodnoty, soubory a historii;
        - *zápis*: zahajovat procesy, vyplňovat pole, nahrávat soubory,
          posouvat se do další fáze nebo se vracet;
        - *mazání*: přerušit nebo smazat proces.
    - **Šablony** lze vytvářet a měnit jen s plným přístupem.
    - Procesy týkající se uchazečů a pole uchazečů vyžadují také přístup
      ke čtení modulu [uchazečů](applicants.md). Bez něj uvidíte
      „Viditelné jen s přístupem k modulu uchazečů.“

## Jak to do sebe zapadá {#how-it-fits-together}

- **Šablona** říká, čeho se proces týká (zahrádky, člena, uchazeče nebo
  ničeho konkrétního), a vypisuje jeho fáze v pořadí.
- Každá **fáze** má libovolný počet **polí**. Pole může být
  **Povinné**.
- Zahájení procesu vytvoří kopii šablony. Pozdější změny šablony
  neovlivní procesy, které už běží.
- Proces je vždy v jedné **aktuální fázi**. Dál se posunete tlačítkem
  **Hotovo -- další fáze**, jakmile je vyplněno každé povinné pole této
  fáze. Po poslední fázi je proces **Dokončeno**.
- Můžete se vrátit k dřívější fázi (s důvodem) nebo proces přerušit (s
  důvodem). Dokončený nebo přerušený proces už nelze měnit.

## Seznam procesů {#process-list}

![Seznam procesů](../assets/screenshots/processes/list.png)

Otevřete **Procesy** v menu.

| Pole / tlačítko | Co dělá |
|---|---|
| **Šablony** | Otevře [Šablony procesů](#process-templates). Jen s plným přístupem. |
| **Zahájit proces** | Otevře [Zahájit proces](#start-a-process). Vyžaduje *zápis*. |
| **Stav** | **Probíhající** (výchozí), **Uzavřené** (dokončené nebo přerušené) nebo **Vše**. |
| **Šablona** | **Všechny šablony** nebo jedna šablona; archivované šablony jsou označeny „(archivováno)“. |
| **Filtrovat** | Použije oba filtry. |

| Sloupec | Co ukazuje |
|---|---|
| **Proces** | Název (s odkazem) a pod ním název šablony. |
| **Pro** | Zahrádka, člen nebo uchazeč, s odkazem na jejich stránku. „(odstraněno)“, pokud byl tento záznam smazán. |
| **Aktuální fáze** | Fáze, ve které proces je, např. „Ocenění (2/6)“. U uzavřených procesů pomlčka. |
| **Zahájeno** | Datum zahájení. |
| **Stav** | **Probíhá**, **Dokončeno** nebo **Přerušeno**. |

Pokud je seznam prázdný, uvádí **Žádné procesy.** a bez šablon nabízí
**Nejprve vytvořte šablonu.**

!!! tip "Procesy na stránkách zahrádek, členů a uchazečů"
    Stránka [zahrádky](parcels.md), [člena](members.md) a
    [uchazeče](applicants.md) má kartu **Procesy** s jejich procesy,
    aktuální fází a stavem. Její tlačítko **Zahájit proces** otevře
    stránku zahájení s již vybranou zahrádkou, členem nebo uchazečem a
    nabídne jen odpovídající šablony.

## Zahájit proces {#start-a-process}

![Zahájit proces](../assets/screenshots/processes/new.png)

1. Vyberte **Šablona**. Stránka se znovu načte a ukáže popis šablony a
   její **Fáze**. Archivované šablony se nenabízejí.
2. Pokud se šablona týká zahrádky, člena nebo uchazeče, vyberte ho v poli
   s popiskem **Zahrádka**, **Člen** nebo **Uchazeč**. Je to povinné.
3. Volitelně zadejte **Název** -- pokud zůstane prázdný, použije se
   název šablony. Tip: uveďte číslo zahrádky nebo jméno, např. „Předání
   zahrádky 17“, abyste procesy v seznamu rozlišili.
4. Klikněte na **Zahájit**. Proces se otevře na své první fázi.

**Zrušit** vás vrátí na seznam. Pokud zatím neexistuje žádná šablona,
stránka uvádí **Zatím neexistuje žádná aktivní šablona.**

## Běžící proces {#a-running-process}

![Proces](../assets/screenshots/processes/detail.png)

Nahoře vidíte stav, šablonu, čeho se proces týká (s odkazem) a
„Zahájeno {date}, {name}“. Pod tím řada odznaků ukazuje postup: zeleně
se zaškrtnutím u dokončených fází, modře u aktuální fáze, šedě u fází,
které teprve přijdou. Kliknutím na odznak na tuto fázi skočíte.

Dokončený proces ukazuje **Dokončeno {date}.**; přerušený ukazuje
**Přerušeno**, datum a důvod.

### Fáze {#the-stages}

Každá fáze je karta s číslem a názvem.

- **Dokončené fáze** ukazují datum a kdo je dokončil. Jejich pole lze
  ještě opravit, dokud je proces otevřený.
- **Aktuální fáze** je označena **Aktuální fáze** a orámována modře.
- **Fáze, kterých ještě nebylo dosaženo,** jsou označeny **Zatím
  nedosaženo** a uvádějí jen názvy svých polí.

Ve fázi, kterou můžete upravovat, vyplňte pole a klikněte na **Uložit**.
Tím se uloží pole této jedné fáze. Soubory se nahrávají zvlášť (viz
níže). Pokud hodnota není platná, uvidíte zprávu jako **Zadejte platné
číslo.** nebo **Zadejte platné datum.**

### Posun dál {#moving-on}

Dole v aktuální fázi:

- **Před posunem ještě chybí:** vypisuje povinná pole, která jsou ještě
  prázdná, každé s odkazem na své pole. Dokud je něco uvedeno, je
  tlačítko neaktivní.
- **Hotovo -- další fáze** dokončí fázi a posune proces dál. V poslední
  fázi je tlačítko **Dokončit proces**.

Povinné zaškrtávací pole se počítá jako vyplněné, jakmile je zaškrtnuté;
povinné pole souborů, jakmile má alespoň jeden soubor.

### Vrátit se {#go-back}

Karta **Vrátit se** (se *zápisem*, jakmile je proces za svou první
fází) vrátí proces na dřívější fázi, například když se musí opakovat
prohlídka.

| Pole / tlačítko | Co dělá |
|---|---|
| **Zpět na fázi** | Na kterou dřívější fázi se vrátit. Předvybraná je předchozí fáze. |
| **Důvod** | Povinné. Zapíše se do historie. |
| **Vrátit se** | Vrátí proces zpět. Všechny dosud zadané hodnoty se zachovají. |

### Historie {#history}

Karta **Historie** vypisuje vše, co se stalo, nejnovější nahoře, s
časem, fází, poznámkou a uživatelem: **Zahájeno**, **Posun na**,
**Návrat na**, **Dokončeno**, **Přerušeno**, **Pole změněno** (se starou
a novou hodnotou), **Soubor přidán** a **Soubor odebrán**.

### Přerušení nebo smazání {#abort-or-delete}

Jen s oprávněním k *mazání*:

| Pole / tlačítko | Co dělá |
|---|---|
| **Přerušit proces** + **Důvod** + **Přerušit** | Po dotazu **Opravdu přerušit tento proces? Nelze jej znovu otevřít.** definitivně zastaví otevřený proces. Důvod je povinný a zobrazuje se u procesu. Proces zůstane v seznamu jako **Přerušeno**. |
| **Smazat proces** | Po dotazu **Opravdu smazat tento proces se všemi hodnotami a soubory?** proces úplně odstraní i se všemi hodnotami a soubory. Jen pro proces zahájený omylem. Soubory v cloudu se nesmažou. |

## Typy polí {#field-types}

| Typ | Co v procesu zadáte |
|---|---|
| **Text** | Jeden řádek, nejvýše 1 000 znaků. |
| **Dlouhý text** | Více řádků. |
| **Číslo** | Číslo. Jako desetinný oddělovač funguje čárka i tečka („1.234,50“ i „1,234.50“). |
| **Částka** | Jako číslo, zobrazené s měnou vašeho spolku. |
| **Datum** | Datum. |
| **Zaškrtávací pole** | Zaškrtnuto, nebo ne, např. „Klíče předány“. |
| **Výběr ze seznamu** | Jedna z možností definovaných v šabloně. |
| **Soubory (PDF, fotky)** | Jeden nebo více nahraných souborů. |
| **Člen** | Člen spolku. |
| **Uchazeč** | Uchazeč (vyžaduje přístup k modulu uchazečů). |
| **Zahrádka** | Zahrádka. |

Pole může mít text nápovědy, zobrazený pod ním.

### Soubory {#files}

Pole souborů vypisuje své soubory s názvem, velikostí, datem a tím, kdo
je nahrál; ikona mraku znamená **Uloženo v cloudu**. Kliknutím na název
soubor otevřete nebo stáhnete. Nový přidáte pomocí **Vyberte soubor** a
**Nahrát**; malé x soubor po dotazu **Odebrat tento soubor?** odebere
(dokud je fáze upravitelná).

Jen PDF, JPEG, PNG nebo WebP, nejvýše 20 MB. Pod tlačítkem nahrání
Parcella uvádí, kam soubor půjde, v tomto pořadí:

1. **Cloudová složka zahrádky**, v podsložce pro tento proces -- pokud
   je zapnutý modul cloudového úložiště a proces se týká zahrádky s
   cloudovou složkou nebo člena s právě jednou současnou zahrádkou,
   která ji má.
2. **Složka pro soubory procesů**, pokud administrátor nastavil
   **Složka pro soubory procesů** v **Administrace → Integrace**.
3. Jinak **soukromé úložiště Parcelly**: „Ukládá se do soukromého
   úložiště Parcelly (pro tuto parcelu ani pro procesy není nastavena
   cloudová složka).“

!!! warning "Složky zahrádek bývají sdílené s nájemci"
    Pokud jsou vaše složky zahrádek v cloudu sdílené s nájemci zahrádky,
    vidí i soubory procesů týkajících se jejich zahrádky. To je záměr --
    úřední dokumenty o zahrádce jsou otevřené jejím nájemcům. Pokud
    chcete soubory jen pro výbor, nenastavujte u zahrádky cloudovou
    složku a použijte místo toho složku pro soubory procesů.

Odebrání souboru z procesu smaže soubor ve vlastním úložišti Parcelly,
ale soubor v cloudu jen odpojí; samotný soubor tam zůstane.

## Šablony procesů {#process-templates}

![Šablony procesů](../assets/screenshots/processes/templates.png)

**Šablony** v seznamu procesů (jen s plným přístupem) otevře **Šablony
procesů**. **Procesy** vpravo nahoře vás vrátí zpět.

Karta **Šablony** vypisuje každou šablonu s tím, čeho se týká, počtem
fází, jak často byla použita, a **archivováno**, pokud je archivovaná.
**Upravit** otevře [editor šablon](#the-template-editor).

### Nová šablona {#new-template}

| Pole / tlačítko | Co dělá |
|---|---|
| **Název** | Povinné, nejvýše 200 znaků. |
| **Proces se týká** | **Zahrádka**, **Člen**, **Uchazeč** nebo **Nepřiřazeno**. Při zahájení procesu se vybere zahrádka, člen nebo uchazeč, kterého se týká, a proces se uvádí na jeho stránce. |
| **Popis** | Volitelné. Zobrazí se, když někdo vybírá šablonu pro zahájení procesu. |
| **Vytvořit** | Vytvoří šablonu a otevře editor. |

### Začít příkladem {#start-from-an-example}

Vytvoří běžnou šablonu ve vašem jazyce, kterou pak můžete libovolně
měnit. Klikněte na **Použít** vedle:

- **Předání zahrádky** -- vypovězená zahrádka na cestě k dalšímu
  nájemci: prohlídka, ocenění, inzerát, nový nájemce, smlouva a předání.
- **Přijetí nového člena** -- přivítání nového člena: první schůzka,
  dokumenty a poslední podrobnosti.

## Editor šablon {#the-template-editor}

![Editor šablon](../assets/screenshots/processes/template-edit.png)

Editor má nadpis „Šablona: {name}“. Změny se ukládají průběžně; vpravo
nahoře se objeví krátké potvrzení.

Záhlaví ukazuje název, čeho se šablona týká, a poznámku: „Změny platí
pro procesy zahájené od teď. Již zahájené procesy ({count}) si ponechají
své fáze a pole.“

| Tlačítko | Co dělá |
|---|---|
| **Podrobnosti** | Otevře k úpravě název, **Proces se týká** a popis; **Uložit** je uloží. |
| **Archivovat** / **Obnovit** | Archivovanou šablonou nelze zahajovat nové procesy; běžící pokračují. |
| **Smazat** | Jen dokud z šablony nebyl zahájen žádný proces, po dotazu **Opravdu smazat tuto šablonu?** Jinak ji archivujte. |

### Fáze {#stages}

Levá karta vypisuje **Fáze** v pořadí s počtem jejich polí. Kliknutím
na jednu ji upravíte. Pořadí změníte přetažením fáze za její úchyt.
Fázi přidáte napsáním názvu do **Nová fáze, např. „Prohlídka“** a
kliknutím na **Přidat**.

Vybraná fáze se zobrazuje vpravo:

- Její **název** a **Popis (volitelné)** lze upravit přímo na místě.
  Popis se zobrazuje nahoře ve fázi běžícího procesu.
- Menu **⋮** (**Akce fáze**) obsahuje **Nahoru**, **Dolů** a **Smazat
  fázi** (po dotazu **Smazat tuto fázi se všemi poli?**).

### Pole {#fields}

Záložka **Pole** vypisuje pole fáze s jejich typem, možnostmi, textem
nápovědy a odznakem **Povinné**. Fáze bez polí je jednoduchý krok k
odškrtnutí.

Pole přidáte napsáním jeho popisku do **Nové pole: napište název a
stiskněte Enter**, výběrem **Typ**, případně zaškrtnutím **Povinné** a
stiskem Enter nebo kliknutím na **Přidat pole**. U **Výběr ze seznamu**
se nejprve otevře boční panel, protože výběr potřebuje své možnosti.

Pořadí polí změníte přetažením za jejich úchyt. Kliknutím na pole
otevřete panel **Upravit pole**:

| Pole / tlačítko | Co dělá |
|---|---|
| **Popisek** | Povinné, nejvýše 200 znaků. |
| **Typ** | Jeden z [typů polí](#field-types). |
| **Možnosti (jen u výběru, jedna na řádek)** | Povinné u **Výběr ze seznamu**: alespoň jedna možnost. |
| **Povinné** | Proces se může posunout dál, až když je toto pole vyplněno. |
| **Nápověda (volitelné)** | Zobrazí se pod polem v běžícím procesu. |
| **Uložit** / **Zavřít** | Uloží pole / zavře panel. |
| **Přesunout do fáze** + tlačítko šipky | Přesune pole na konec jiné fáze. |
| **Nahoru** / **Dolů** | Změní pořadí bez přetahování. |
| **Duplikovat** | Přidá kopii hned pod. |
| **Smazat pole** | Odebere pole ze šablony. |

Záložka **Náhled** ukazuje, jak fáze vypadá v běžícím procesu, s
neaktivními vstupy.

## Příklad z praxe: předání zahrádky {#worked-example-a-plot-handover}

Nájemce zahrádky 17 dal výpověď. Takto výbor předání provede s příkladem
**Předání zahrádky**.

**Jednou: připravte šablonu.** Otevřete **Procesy → Šablony**, klikněte
na **Použít** vedle **Předání zahrádky**. Dostanete šablonu týkající se
typu **Zahrádka** se šesti fázemi:

| # | Fáze | Pole (* = povinné) |
|---|---|---|
| 1 | Prohlídka | Datum prohlídky*, Zjištěné závady, Fotky závad, Všechny závady odstraněny* |
| 2 | Ocenění | Odhadce*, Datum ocenění*, Posudek* (soubor) |
| 3 | Inzerát | Text inzerátu*, Fotky k inzerátu, Zveřejněno dne* |
| 4 | Nový nájemce | Nový nájemce* (uchazeč), Kontakt navázán*, Dokumenty odeslány* |
| 5 | Smlouva a kauce | Kupní smlouva potvrzena*, Kauce (částka), Kauce přijata dne |
| 6 | Předání | Podepsáno novým nájemcem*, Spolupodepsáno výborem*, Klíče předány*, Měřiče odečteny*, Předávací protokol (soubor) |

Přizpůsobte ji svému spolku: například udělejte **Kauce** povinnou nebo
přidejte pole **Výběr ze seznamu** „Výsledek ocenění“ s možnostmi
„Převzetí za odhadní cenu“ a „Zahrádka k vyklizení“.

**Pokaždé: spusťte ji.**

1. Otevřete zahrádku 17 a klikněte na **Zahájit proces** v její kartě
   **Procesy**. **Předání zahrádky** i zahrádka jsou už vybrané. Zadejte
   název „Předání zahrádky 17“ a klikněte na **Zahájit**.
2. **Prohlídka**: po obchůzce zadejte datum, vypište závady, nahrajte
   fotky a klikněte na **Uložit**. Fázi zatím nelze dokončit: ještě chybí
   **Všechny závady odstraněny**. Jakmile nájemce vše opraví, zaškrtněte
   to, **Uložit**, pak **Hotovo -- další fáze**.
3. **Ocenění**: zadejte odhadce a datum, nahrajte posudek jako PDF. Pokud
   má zahrádka cloudovou složku, posudek skončí tam v podsložce pro toto
   předání. **Hotovo -- další fáze**.
4. **Inzerát** a **Nový nájemce**: zaznamenejte inzerát, pak ze seznamu
   uchazečů vyberte vybranou osobu a zaškrtněte obě políčka.
5. **Smlouva a kauce**: potvrďte smlouvu, zadejte kauci a den, kdy
   přišla.
6. **Předání**: zaškrtněte podpisy, klíče a odečty měřidel, nahrajte
   předávací protokol a klikněte na **Dokončit proces**.

Pokud nový nájemce ve fázi 5 odstoupí, použijte **Vrátit se** a vraťte
se na **Inzerát** s důvodem „Uchazeč odstoupil“. Dosud zadané hodnoty
zůstanou a historie ukáže, co se stalo.

Samotný proces předání jen zaznamenává. Ukončení starého nájmu, zahájení
nového a odečty měřidel v Parcelle se dělají v modulech
[parcel](parcels.md) a [měření](metering.md) -- viz
[návod k předání parcely](../guides/parcel-handover.md).

## Související {#related}

- [Předání parcely](../guides/parcel-handover.md)
- [Parcely](parcels.md), [Členové](members.md),
  [Uchazeči](applicants.md) -- karta **Procesy** na jejich stránkách.
- [Integrace](../administration/integrations.md) -- složka pro soubory
  procesů.
- [Skupiny](../administration/groups.md) -- udělení oprávnění k
  procesům.

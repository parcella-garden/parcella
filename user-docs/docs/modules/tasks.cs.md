# Nástěnka úkolů {#task-board}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Společná tabule úkolů pro vlastní záležitosti výboru, které nesouvisejí
s pracovní směnou: „obnovit pojistnou smlouvu“, „zavolat elektrikáři“,
„ozvat se pokrývači“. Úkoly jsou karty ve sloupcích, které posouváte
zleva doprava, jak práce postupuje.

!!! info "Kdo to může používat"
    - Přepínač modulu je **Nástěnka úkolů** v **Administrace → Zapínání
      a vypínání modulů**. Ve výchozím stavu je **zapnutý**.
    - **Nástěnka úkolů** v menu vidí jen role **Výbor** a **Správce** a
      členové skupiny s **Plný přístup ke každému modulu**. Žádné
      oprávnění skupiny ji neotevře dalším uživatelům, ke čtení ani k
      zápisu.
    - Volitelně lze karty převzít z tabule Nextcloud Deck (přepínač
      modulu **Synchronizace Nextcloud Deck**, ve výchozím stavu
      vypnutý). Viz [Karty z Nextcloud Deck](#cards-from-nextcloud-deck).

!!! note "Není to totéž co úkoly pracovních směn"
    Práce, které členové dělají během pracovní směny („ostříhat živý
    plot“), jsou v modulu [pracovních hodin](work-hours.md) v části
    **Úkoly**. Nástěnka úkolů je pro vlastní seznam úkolů výboru.

## Tabule {#the-board}

![Nástěnka úkolů](../assets/screenshots/tasks/board.png)

Tabule ukazuje všechny seznamy (sloupce) vedle sebe; pokud se na
obrazovku nevejdou, posouvejte do strany. Nové instalace začínají třemi
seznamy, „To Do“, „In Progress“ a „Done“. Seznamy můžete libovolně
přejmenovávat, přidávat, přeřazovat a mazat.

Položka menu **Nástěnka úkolů** ukazuje červené číslo, když jsou úkoly
po termínu. Dashboard má kartu **Úkoly po termínu** se stejným číslem;
její tlačítko **Zobrazit vše** otevře tabuli s již zaškrtnutým
**Pouze po termínu**.

### Tlačítka nahoře {#buttons-at-the-top}

| Tlačítko | Co dělá |
|---|---|
| **Přidat seznam** | Otevře malé okno pro přidání seznamu. Zadejte **Název** (nejvýše 100 znaků) a klikněte na **Přidat**. Nový seznam se přidá na pravý konec tabule. |
| **Spravovat štítky** | Otevře [Štítky úkolů](#task-tags). |
| **Exportovat report** | Otevře [Export reportu aktivity](#export-activity-report). |
| **Nový úkol** | Otevře [okno úkolu](#the-task-window) pro novou kartu. |

### Seznam (sloupec) {#a-list-column}

Záhlaví každého sloupce ukazuje název seznamu, zelenou ikonu zaškrtnutí,
pokud jde o [seznam hotových](#done-lists), a počet karet v něm.

| Akce | Co dělá |
|---|---|
| Přetažení záhlaví | Přesune celý seznam na nové místo tabule. |
| **⋮** → **Přejmenovat** | Otevře **Přejmenovat seznam**; změňte **Název** a klikněte na **Uložit změny**. |
| **⋮** → **Označit jako seznam hotových** / **Zrušit označení seznamu hotových** | Zapne nebo vypne pro tento seznam funkci seznamu hotových. Viz [Seznamy hotových](#done-lists). |
| **⋮** → **Smazat** | Otevře **Smazat seznam**. U posledního zbývajícího seznamu to nejde. |

Když mažete seznam, který ještě obsahuje karty, okno uvádí **Tento
seznam stále obsahuje karty. Před smazáním vyberte jiný seznam, do
kterého se mají přesunout.** Vyberte cíl v **Přesunout karty do** a
klikněte na **Smazat seznam**. Karty se přidají na konec tohoto seznamu
ve svém současném pořadí -- se seznamem se nikdy žádná karta nesmaže.
Prázdný seznam se zeptá **Smazat seznam „{name}“? Tuto akci nelze vrátit
zpět.**

### Karta {#a-card}

Každá karta ukazuje:

- odznak **priority** (**Vysoká**, **Střední** nebo **Nízká**), pokud je
  nastavena;
- ikonu mraku, pokud karta pochází z Nextcloud Deck;
- **název** -- kliknutím otevřete [okno úkolu](#the-task-window);
- komu je přidělena a **termín**. Termín po splatnosti se zobrazuje
  červeně;
- **Hotovo {date}** zeleně u dokončených karet, které jsou také
  zobrazeny vybledle a přeškrtnuté;
- své **štítky** jako barevné popisky.

Prázdný seznam ukazuje **Žádné úkoly**.

**Přetažením karty** do jiného seznamu, nebo nahoru a dolů v rámci
seznamu, změníte její místo. Pořadí se ukládá okamžitě. Pokud se uložení
nezdaří, stránka se znovu načte a ukáže skutečný stav.

!!! note "Kdy je přetahování vypnuté"
    Dokud je aktivní vyhledávání, filtr nebo jiné řazení než **Ručně
    (pořadí přetažení)**, karty nelze přetahovat, protože tabule pak
    neukazuje každou kartu v jejím skutečném pořadí. Klikněte na
    **Zrušit filtry** a nastavte řazení zpět na **Ručně (pořadí
    přetažení)**. Přesouvání celých seznamů funguje i nadále.

### Hledání, filtry a řazení {#search-filters-and-sort}

Lišta nad tabulkou zužuje, co vidíte. Vše se děje okamžitě ve vašem
prohlížeči a na samotné tabuli nic nemění.

| Pole / tlačítko | Co dělá |
|---|---|
| Pole hledání | Hledá v názvu, popisu, štítcích a komentářích. |
| **Libovolná priorita** | Ukáže jen karty s prioritou **Vysoká**, **Střední** nebo **Nízká**. |
| **Libovolný štítek** | Ukáže jen karty s tímto štítkem. Nabízejí se jen štítky použité na tabuli. |
| **Libovolný řešitel** | Ukáže jen karty přidělené této osobě. Nabízejí se jen lidé s kartami. |
| **Libovolný měsíc splatnosti** | Ukáže jen karty s termínem v tomto měsíci (např. „červenec 2026“). Nabízejí se jen vyskytující se měsíce. |
| **Pouze po termínu** | Ukáže jen karty po termínu: termín v minulosti a nehotové. |
| **Zrušit filtry** | Vynuluje hledání a filtry. |
| Řazení (**Ručně (pořadí přetažení)**, **Termín splnění**, **Priorita**) | Přeřadí karty v každém seznamu pro zobrazení: podle měsíce termínu, nebo Vysoká → Střední → Nízká s kartami bez priority na konci. **Ručně (pořadí přetažení)** opět ukáže vaše vlastní pořadí. Řazení se nikdy neukládá. |

Pokud nic neodpovídá: **Žádné úkoly neodpovídají vyhledávání/filtrům.**

## Okno úkolu {#the-task-window}

![Okno úkolu](../assets/screenshots/tasks/task-modal.png)

Kliknutím na **Nový úkol** nebo na název karty se nad tabulkou otevře
okno s nadpisem **Nový úkol** nebo **Upravit úkol**. Každá karta má
vlastní webovou adresu, takže si ji můžete uložit do záložek nebo poslat
odkaz jinému členovi výboru. Zavřením okna (X, **Zrušit**, Esc nebo
kliknutím vedle) se vrátíte na tabuli bez uložení.

| Pole / tlačítko | Co dělá |
|---|---|
| **Název** | Povinné. |
| **Popis** | Volitelný volný text. |
| **Termín splnění** | Volitelné. Karta, jejíž termín uplynul, se počítá jako po termínu, dokud není hotová. |
| **Priorita** | **Bez priority** (výchozí), **Nízká**, **Střední** nebo **Vysoká**. Priorita nemění pořadí karet; jen ukazuje odznak a lze podle ní filtrovat a řadit. |
| **Štítky** | Zaškrtněte libovolné [štítky úkolů](#task-tags) spolku. Pokud zatím žádné neexistují: **Zatím nejsou definovány žádné štítky.** s odkazem na **Spravovat štítky**. Nové štítky zde psát nelze. |
| **Seznam** | Ve kterém seznamu karta je. Nová karta jde do prvního seznamu, pokud nevyberete jiný; přidá se na konec. |
| **Hotovo** | Označí kartu jako hotovou (s datem a časem dokončení). Hotové úkoly se nikdy nezobrazují jako po termínu. Přesunutí karty do seznamu hotových ji označí jako hotovou automaticky. Odškrtnutím ji znovu otevřete. |
| **Přiděleno komu** | Zaškrtněte libovolný počet lidí. Uvedeny jsou jen aktivní uživatelské účty. |
| **Vytvořit** / **Uložit změny** | Uloží kartu a vrátí se na tabuli. |
| **Smazat úkol** | Jen u existujících karet. Po dotazu **Smazat tento úkol? Tuto akci nelze vrátit zpět.** smaže kartu i s komentáři. |

### Komentáře {#comments}

Existující karty mají sekci **Komentáře**: průběžný záznam poznámek pro
toho, kdo úkol převezme příště. Každý komentář ukazuje autora a čas.

- Napište do **Nový komentář** a klikněte na **Přidat komentář**.
- Každý komentář má pod sebou malý červený odkaz **Smazat komentář**,
  který komentář po dotazu **Smazat tento komentář? Tuto akci nelze
  vrátit zpět.** odstraní. Kterýkoli člen výboru může smazat jakýkoli
  komentář. Komentáře nelze upravovat.


### Historie změn {#change-history}

Pod komentáři **Historie změn** vypisuje každou zaznamenanou změnu,
nejnovější první: **Časová značka**, **Pole**, **Původní hodnota**,
**Nová hodnota** a **Změnil**. Zaznamenávají se změny názvu, popisu,
termínu, priority, štítků, seznamu (zobrazeného názvem seznamu) a
označení hotovo. Změny toho, komu je karta přidělena, se nezaznamenávají.
Pokud zatím žádné nejsou: **Zatím nebyly zaznamenány žádné změny.**

## Seznamy hotových {#done-lists}

Karta je „hotová“, jen když je jako hotová označena -- nikdy jen proto,
že je ve sloupci nazvaném „Done“. Aby přesunutí karty do sloupce
znamenalo její dokončení, označte tento sloupec jako seznam hotových:

1. Otevřete menu **⋮** seznamu, který používáte pro dokončené úkoly.
2. Zvolte **Označit jako seznam hotových**. Vedle jeho názvu se objeví
   zelené zaškrtnutí.

Od té doby:

- přesunutí karty **do** seznamu hotových ji označí jako hotovou
  (přetažením, změnou **Seznam** v okně úkolu nebo vytvořením karty
  tam);
- přesunutí **ven** do běžného seznamu ji znovu otevře;
- přesun mezi dvěma běžnými seznamy nic nemění;
- zaškrtávací políčko **Hotovo** označí nebo znovu otevře kartu v
  jakémkoli seznamu.

Označením seznamu se karty, které už v něm jsou, označí jako hotové.
Zrušení označení seznamu ponechá jeho karty, jak jsou.

Dokud není označen žádný seznam, tabule ukazuje modrou poznámku, která
to vysvětluje.

## Štítky úkolů {#task-tags}

![Štítky úkolů](../assets/screenshots/tasks/tags.png)

**Spravovat štítky** na tabuli otevře **Štítky úkolů**: pevný seznam
štítků, které mohou karty nést. Karty mohou nést jen zde definované
štítky. **Zpět na tabuli** vás vrátí na tabuli.

| Pole / tlačítko | Co dělá |
|---|---|
| **Název** + barva + **Přidat štítek** | Vytvoří štítek. Název je povinný, nejvýše 100 znaků, a musí být jedinečný (na velikosti písmen nezáleží). Barvy: **Šedá** (výchozí), **Červená**, **Oranžová**, **Žlutá**, **Zelená**, **Tyrkysová**, **Modrá**, **Fialová**. |
| Název a barva existujícího štítku + tlačítko zaškrtnutí | Přejmenuje nebo přebarví štítek. Změna se okamžitě projeví na každé kartě. |
| „Úkoly: {count}“ | Kolik karet štítek nese. |
| Tlačítko koše | Po dotazu **Smazat štítek „{name}“? Bude odebrán ze všech úkolů.** štítek smaže. Karty zůstanou. |

Možné chyby: **Štítek musí mít název.**, **Štítek s tímto názvem už
existuje.**, **Neznámá barva.** Bez štítků: **Zatím žádné štítky.**

## Export reportu aktivity {#export-activity-report}

![Export reportu aktivity](../assets/screenshots/tasks/export.png)

**Exportovat report** stáhne textový soubor v Markdownu o aktivitě na
tabuli, například pro přípravu zápisu ze schůze výboru nebo měsíčního
shrnutí (i s pomocí asistenta AI).

| Pole / tlačítko | Co dělá |
|---|---|
| **Od** | Začátek období. Výchozí je před 30 dny. |
| **Do** | Konec období. Výchozí je dnešek. |
| **Stáhnout** | Stáhne report. |

Report má tři části: karty vytvořené nebo změněné v daném období,
komentáře napsané v daném období a snímek všech karet na tabuli právě
teď (hotové karty s datem dokončení).

!!! warning "Co znamená „změněno v období“"
    Karta se počítá jako dotčená, pokud byla v daném období vytvořena
    nebo upravena. Report nedokáže přesně říct, kdy byla karta přesunuta
    do svého současného seznamu. Soubor to sám uvádí, aby si ten, kdo ho
    čte, nevymýšlel časovou osu.

## Karty z Nextcloud Deck {#cards-from-nextcloud-deck}

Pokud váš spolek dříve plánoval v Nextcloud Deck, může Parcella zkopírovat
jednu tabuli Deck na nástěnku úkolů a udržovat ji aktuální. Jde o
jednosměrné zrcadlo, které má pomoci s přechodem.

Nastavuje administrátor: zapne **Synchronizace Nextcloud Deck** v
**Zapínání a vypínání modulů** a pak zadá server, uživatele, heslo
aplikace a **ID nástěnky Deck** v **Administrace → Integrace →
Nextcloud Deck** (viz [Integrace](../administration/integrations.md)).
Parcella pak kontroluje Deck každých 15 minut; **Synchronizovat nyní**
tam to udělá hned.

Co uvidíte na tabuli:

- Každý sloupec Deck se stane seznamem se stejným názvem (v případě
  potřeby se vytvoří).
- Synchronizované karty mají ikonu mraku (**Synchronizováno z Nextcloud
  Deck**).
- V okně úkolu šedá poznámka uvádí: **Tato karta je synchronizována z
  Nextcloud Deck -- název, popis, termín a seznam jsou spravovány tam a
  aktualizují se automaticky. Priorita, štítky, přiřazení a komentáře
  existují pouze v Parcelle a lze je vždy upravovat.** Název, popis,
  termín a seznam nelze v Parcelle měnit.
- **Převzít do Parcelly** zruší propojení: od té doby je karta běžnou
  kartou Parcelly, plně upravitelnou, a Deck ji už nemění.
- Karta smazaná nebo archivovaná v Deck se v Parcelle nikdy nesmaže.
  Prostě se přestane synchronizovat, jako byste ji převzali.
- Archivované karty Deck se vůbec nekopírují.

## Související {#related}

- [Dashboard](../getting-started/dashboard.md) -- karta **Úkoly po
  termínu**.
- [Pracovní hodiny](work-hours.md) -- úkoly pro pracovní směny.
- [Integrace](../administration/integrations.md) -- propojení s
  Nextcloud Deck.
- [Zapínání a vypínání modulů](../administration/modules.md)

# Orientace v aplikaci {#finding-your-way-around}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Každá stránka v Parcelle má stejný rámec: zelený **postranní panel**
vlevo s navigací a bílou **horní lištu** nad stránkou s názvem stránky
a tlačítky pro tuto stránku.

!!! info "Kdo to může používat"
    Každý, kdo je přihlášen. Které položky vidíte *vy*, závisí na
    modulech, které má váš spolek zapnuté, a na vašich oprávněních --
    viz [Proč se položky objevují a mizí](#why-entries-appear-and-disappear).

![Postranní panel a horní lišta](../assets/screenshots/getting-started/navigation.png)

## Postranní panel {#the-sidebar}

Shora dolů postranní panel obsahuje:

1. **Název a logo vašeho spolku**, pod nimi slovo **Správa**.
2. **Položky navigace** -- jedna pro každý modul.
3. **Administrace** -- jen pro administrátory, vždy úplně dole v
   seznamu.
4. **Zápatí** s vaším vlastním účtem.

### Jednotlivé položky a skupiny {#single-entries-and-groups}

Menší moduly jsou jediný odkaz, například **Členové**, **Parcely**,
**Inventář** nebo **Poznámky**. Klikněte na něj a modul se otevře.

Větší moduly jsou **skupina**: nadpis velkými písmeny s malou šipkou.
Kliknutím na nadpis se rozbalí jeho stránky:

| Skupina | Stránky v ní |
|---|---|
| **Pracovní sezení** | **Sezení a přehled**, **Roční hodnocení**, **Sponzoringy**, **Převod hodin**, **Úkoly** |
| **Voda** | **Přehled**, **Měrná místa**, **Odečty**, **Vyhodnocení**, **Konfigurace** |
| **Elektřina** | **Přehled**, **Měrná místa**, **Odečty**, **Vyhodnocení**, **Konfigurace** |
| **Pojištění** | **Přehled**, **Parcely**, **Konfigurace**, **Vyhodnocení** |
| **Kalendář** | **Kalendář spolku**, **Narozeniny**, **Přítomnost výboru**, **Nepřítomnost výboru**, **Vlastní kalendáře** |
| **Finance** | **Přehled**, **Vydané faktury**, **Upomínky**, **Přijaté faktury** |
| **Administrace** | **Systém**, **Uživatelé**, **Skupiny**, **API tokeny**, **Nastavení**, **Integrace**, **Protokol e-mailů**, **Ukázková data**, **API dokumentace (Swagger)** |

Otevřená je vždy **jen jedna skupina**: otevřením skupiny se dříve
otevřená sbalí, takže postranní panel zůstává krátký. Skupina, která
obsahuje stránku, na které jste, se vždy otevře sama. Jinak si prohlížeč
pamatuje, kterou skupinu jste otevřeli naposledy.

Stránka, na které jste, je zvýrazněna světlým pruhem na levém okraji.

**API dokumentace (Swagger)** otevře v nové záložce prohlížeče technický
popis programového rozhraní Parcelly. Je určena lidem, kteří připojují
jiný software, a jinak ji můžete ignorovat.

### Odznaky: věci, které vyžadují pozornost {#badges-things-that-need-attention}

Některé položky ukazují malé červené číslo. Říká vám, kolik věcí tam
čeká. Najeďte na něj myší a uvidíte, co počítá.

| Položka | Odznak počítá |
|---|---|
| **Pracovní sezení** a **Sezení a přehled** | Nová přihlášení na nadcházející pracovní směny za posledních 14 dní, která zatím nikdo neoznačil jako zkontrolovaná. |
| **Žádosti o nákup** | Žádosti, které stále čekají na rozhodnutí. |
| **Uchazeči** | Nové přihlášky, na které se zatím nikdo nepodíval. |
| **Podpora** | Otevřené konverzace (aktivní nebo čekající) v helpdesku spolku. |
| **Nástěnka úkolů** | Úkoly, jejichž termín uplynul a které nejsou hotové. |

Odznak zmizí sám, jakmile se věc vyřeší -- například když je žádost o
nákup schválena nebo zamítnuta, nebo když je úkol hotový. Možnost
„označit jako přečtené“ neexistuje. Stejná čísla se zobrazují jako
dlaždice na [Dashboardu](dashboard.md).

### Zápatí: váš účet {#the-footer-your-account}

Dole v postranním panelu vidíte svůj avatar a jméno a pod nimi skupiny,
do kterých patříte (nebo **Správce** / **Výbor** u starších účtů, které
mají místo skupin roli -- viz
[Role, skupiny a oprávnění](roles-and-permissions.md)).

| Tlačítko | Co dělá |
|---|---|
| **Změnit heslo** | Otevře váš profil: heslo, avatar a API tokeny. Viz [První přihlášení a váš účet](first-login.md#change-password). |
| **Odhlásit** | Odhlásí vás a vrátí na přihlašovací stránku. |

## Horní lišta {#the-top-bar}

Horní lišta ukazuje vlevo název aktuální stránky. Vpravo jsou akce pro
tuto stránku, například **Nový člen**, export nebo tlačítko zpět. Horní
lišta zůstává viditelná, i když se posouváte dolů dlouhým seznamem.

## Proč se položky objevují a mizí {#why-entries-appear-and-disappear}

Položka se zobrazí, jen když platí **obojí**:

1. **Modul je pro váš spolek zapnutý.** Administrátoři zapínají a
   vypínají moduly v části
   [Zapínání a vypínání modulů](../administration/modules.md). Vypnutý
   modul zmizí pro všechny -- jeho data se zachovají a vrátí se, až se
   modul znovu zapne.
2. **Smíte ho číst.** Členové výboru a administrátoři vidí každý
   zapnutý modul. Všichni ostatní vidí **Členové** a **Parcely** a k
   tomu moduly, pro které jim některá z jejich skupin dává **Čtení**.
   Viz [Role, skupiny a oprávnění](roles-and-permissions.md).

Několik položek se řídí vlastním pravidlem:

- **Nástěnka úkolů** a **Oznámení** se zobrazují jen lidem s plným
  přístupem (členům výboru, administrátorům nebo skupině s **Plný
  přístup ke každému modulu**). Skupiny je nemohou udělit zvlášť.
- **Podpora**: s oprávněním ke čtení pro **Podpora (helpdesk)** dostanete
  vlastní seznam konverzací v Parcelle. Bez něj se položka přesto
  zobrazí, pokud má helpdesk vašeho spolku webovou adresu, a pak otevře
  samotný helpdesk v nové záložce.
- **Administrace** se zobrazuje jen administrátorům.

Pokud otevřete stránku, kterou nesmíte vidět -- ze záložky nebo z odkazu
od kolegy --, dostanete zprávu **K tomu nemáte oprávnění**. Stránka
vypnutého modulu odpoví stránkou „nenalezeno“: „Tato funkce je v tomto
spolku vypnutá.“

### Pořadí položek {#the-order-of-the-entries}

O pořadí položek rozhoduje váš spolek. Nastavuje ho administrátor v
[Nastavení spolku](../administration/settings.md#navigation-order).
Pořadí je pro všechny stejné.

## Klávesová zkratka pro stránky detailu {#keyboard-shortcut-for-detail-pages}

Na stránkách detailu, které mají tlačítka **Předchozí** a **Další** --
členové, parcely, měrná místa, stránka pojištění parcely a externí
kontakty --, skočí **Ctrl + ←** a **Ctrl + →** na předchozí a další
záznam, stejně jako tato tlačítka. Když píšete do pole, zkratka nic
nedělá.

!!! note "Uživatelé Macu"
    Na Macu Ctrl + šipky obvykle přepínají mezi plochami („Spaces“),
    takže systém zkratku zachytí dřív, než ji Parcella uvidí. Použijte
    místo toho tlačítka na stránce, nebo tuto systémovou zkratku vypněte.

## V telefonu nebo malém tabletu {#on-a-phone-or-small-tablet}

Na úzkých obrazovkách je postranní panel skrytý, aby uvolnil místo
stránce.

- Klepnutím na tlačítko **☰** vlevo nahoře v horní liště panel vysunete.
- Klepnutím na položku na ni přejdete; panel se zavře sám.
- Chcete-li ho zavřít, aniž byste někam šli, klepněte na ztmavenou
  stránku vedle něj nebo na klávesnici stiskněte **Esc**.

Tlačítka a vstupní pole jsou na dotykových obrazovkách o něco větší a
řady tlačítek filtrů se zalamují na více řádků, místo aby přesahovaly
obrazovku. Širokými tabulkami lze posouvat prstem do stran.

## Související {#related}

- [Dashboard](dashboard.md)
- [Role, skupiny a oprávnění](roles-and-permissions.md)
- [Zapínání a vypínání modulů](../administration/modules.md)

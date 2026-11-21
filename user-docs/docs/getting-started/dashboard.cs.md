# Dashboard {#dashboard}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Dashboard je úvodní stránka, kterou vidíte po přihlášení. Na první
pohled ukazuje hlavní údaje spolku a upozorňuje na věci, které vyžadují
pozornost. Zpět se na něj dostanete kliknutím na **Dashboard** nahoře v
postranním panelu.

!!! info "Kdo to může používat"
    Každý, kdo je přihlášen. Některé dlaždice se zobrazí, jen když je
    zapnutý jejich modul, a několik z nich navíc vyžaduje oprávnění ke
    čtení daného modulu (uvedeno níže).

![Dashboard](../assets/screenshots/getting-started/dashboard.png)

Všechny údaje se počítají znovu při každém otevření stránky.

## Dlaždice {#the-tiles}

Dlaždice nahoře mají pevné pořadí. První čtyři se zobrazují vždy;
ostatní podle modulů vašeho spolku.

| Dlaždice | Co počítá | Kdy se zobrazí | Tlačítko |
|---|---|---|---|
| **Členové** | Velké číslo: současní členové -- nesmazaní, s neukončeným členstvím a buď již započatým, nebo bez data **Členem od**. Pod ním: **... aktivní** -- ti z nich, kteří mají datum **Členem od**. Pokud má alespoň jeden současný člen zadané datum narození: **Průměrný věk ... let**, počítaný jen z těchto členů. | Vždy | **Zobrazit** otevře seznam členů vyfiltrovaný na aktivní členy. |
| **Aktivní parcely** | Parcely se stavem *aktivní*. Pod tím oranžově: **... volné** -- aktivní parcely bez současného nebo budoucího nájemce (parcela, jejíž poslední nájem skončil, se počítá jako volná; parcela, jejíž nájemce dal výpověď nebo jejíž nový nájemce nastupuje později, ne); nebo **všechny obsazeny**, pokud žádné volné nejsou. | Vždy | **Zobrazit vše** otevře seznam parcel. |
| **Ukončené** | Parcely se stavem *ukončená*. | Vždy | **Zobrazit** otevře seznam parcel vyfiltrovaný na ukončené parcely. |
| **Celková rozloha (m²)** | Součet rozloh všech parcel, aktivních i ukončených. Smazané parcely a společné plochy se nepočítají. Je to stejný údaj jako **Rozloha A** v [nastavení spolku](../administration/settings.md#areas-sqm). | Vždy | -- |
| **Otevřené žádosti o nákup** | Žádosti, které stále **čeká na schválení**. | Modul **Žádosti o nákup** zapnutý a smíte číst žádosti o nákup | **Zobrazit vše** |
| **Nové přihlášky** | Přihlášky se stavem *nová*, tj. **zatím nevyřízené**. | Modul **Uchazeči** zapnutý a smíte číst uchazeče | **Zobrazit vše** otevře seznam uchazečů vyfiltrovaný na nové. |
| **Otevřené procesy** | Procesy, které **probíhá**. | Modul **Procesy** zapnutý a smíte číst procesy | **Zobrazit vše** otevře otevřené procesy. |
| **Otevřené konverzace podpory** | **Aktivní nebo čekající konverzace v helpdesku** spolku. | Modul **Podpora (helpdesk)** zapnutý a smíte ho číst | **Zobrazit vše** |
| **Úkoly po termínu** | Úkoly na nástěnce úkolů, jejichž termín uplynul a které nejsou hotové. | Modul **Nástěnka úkolů** zapnutý a máte plný přístup (nástěnka úkolů je jen pro uživatele s plným přístupem) | **Zobrazit vše** otevře nástěnku úkolů jen s úkoly po termínu. |
| **Nová přihlášení** | Přihlášení **k pracovním směnám** za posledních 14 dní, na pravidelné směny, které ještě neproběhly. Přihlášení na směnu, kterou někdo označil jako zkontrolovanou, se už nepočítají. | Modul **Správa pracovních hodin** zapnutý a smíte číst pracovní hodiny | **Zobrazit vše** otevře **Sezení a přehled**. |

Čísla na dlaždicích **Otevřené žádosti o nákup**, **Nové přihlášky**,
**Otevřené konverzace podpory**, **Úkoly po termínu** a **Nová
přihlášení** jsou stejná jako červené odznaky v postranním panelu (viz
[Orientace v aplikaci](navigation.md#badges-things-that-need-attention)).
Stejně jako odznaky klesají sama, jakmile se věc vyřeší.

## Narozeniny tento týden {#birthdays-this-week}

Tato karta se zobrazí, jen když má alespoň jeden současný člen narozeniny
v příštích sedmi dnech, včetně dneška. Uvádí tyto členy, nejbližší
první:

- jméno člena s odkazem na jeho stránku,
- **dnes oslaví ...** u narozenin dnes, jinak datum a **oslaví ...**,
- zvýrazněný odznak **Kulaté** u kulatých narozenin (30, 40, 50, ...).

Členové bez zadaného data narození se neuvádějí. Karta se zobrazuje i
při vypnutém modulu **Kalendář**; její tlačítko **Zobrazit vše** vede na
úplný seznam narozenin v kalendáři, který vyžaduje modul kalendáře a
oprávnění.

## Nedávní členové {#recent-members}

Pět současných členů, kteří byli **zadáni do Parcelly** naposledy, s
datem **Členem od** vpravo (–, pokud není nastaveno). Kliknutím na jméno
člena otevřete. V nové instalaci se zobrazí **Zatím nebyli vytvořeni
žádní členové.**

**Nový člen** otevře formulář pro nového člena.

## Rychlý přístup {#quick-access}

Zkratky pro časté úkony:

| Tlačítko | Co dělá |
|---|---|
| **Vytvořit nového člena** | Otevře formulář pro nového člena. |
| **Vytvořit novou parcelu** | Otevře formulář pro novou parcelu. |
| **Exportovat členy jako CSV** | Stáhne seznam členů jako soubor CSV, např. pro tabulkový procesor. |
| **Exportovat parcely jako CSV** | Stáhne seznam parcel jako soubor CSV. |

Vytváření členů a parcel vyžaduje **Zápis** u **Členové a parcely**. Bez
něj formulář odpoví **K tomu nemáte oprávnění**.

## Související {#related}

- [Členové](../modules/members.md) a [Parcely](../modules/parcels.md)
- [Orientace v aplikaci](navigation.md)
- [Zapínání a vypínání modulů](../administration/modules.md)

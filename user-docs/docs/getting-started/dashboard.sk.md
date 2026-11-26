# Dashboard {#dashboard}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Dashboard je úvodná stránka, ktorú uvidíte po prihlásení. Na prvý
pohľad ukazuje kľúčové čísla spolku a upozorňuje na veci, ktoré si
vyžadujú pozornosť. Späť sa k nemu dostanete kliknutím na **Dashboard**
v hornej časti bočného panela.

!!! info "Kto to môže používať"
    Každý, kto je prihlásený. Niektoré dlaždice sa objavia, len keď je
    ich modul zapnutý, a niekoľko z nich potrebuje aj oprávnenie na
    čítanie pre tento modul (uvedené nižšie).

![Dashboard](../assets/screenshots/getting-started/dashboard.png)

Všetky čísla sa počítajú nanovo pri každom otvorení stránky.

## Dlaždice {#the-tiles}

Dlaždice hore majú pevné poradie. Prvé štyri sa zobrazujú vždy;
ostatné sa objavia podľa modulov vášho spolku.

| Dlaždica | Čo počíta | Kedy sa zobrazí | Tlačidlo |
|---|---|---|---|
| **Členovia** | Veľké číslo: súčasní členovia -- nezmazaní, členstvo neukončené a buď už začalo, alebo bez dátumu **Členom od**. Pod ním: **... aktívni** -- tí z nich, ktorí majú dátum **Členom od**. Ak má aspoň jeden súčasný člen zadaný dátum narodenia: **Priemerný vek ... rokov**, vypočítaný len z týchto členov. | Vždy | **Zobraziť** otvorí zoznam členov filtrovaný na aktívnych členov. |
| **Aktívne parcely** | Parcely so stavom *aktívna*. Pod tým oranžovo: **... voľné** -- aktívne parcely bez súčasného alebo budúceho nájomcu (parcela, ktorej posledný nájom skončil, sa počíta ako voľná; parcela, ktorej nájomca dal výpoveď alebo ktorej nový nájomca nastupuje neskôr, nie); alebo **všetky obsadené**, ak takáto nie je žiadna. | Vždy | **Zobraziť všetko** otvorí zoznam parciel. |
| **Ukončené** | Parcely so stavom *ukončená*. | Vždy | **Zobraziť** otvorí zoznam parciel filtrovaný na ukončené parcely. |
| **Celková rozloha (m²)** | Súčet rozlôh všetkých parciel, aktívnych aj ukončených. Zmazané parcely a spoločné plochy sa nepočítajú. Je to to isté číslo ako **Rozloha A (parcely, m²)** v [nastaveniach spolku](../administration/settings.md#areas-sqm). | Vždy | -- |
| **Otvorené žiadosti o nákup** | Žiadosti, ktoré stále **čaká na schválenie**. | Modul **Žiadosti o nákup** je zapnutý a smiete čítať žiadosti o nákup | **Zobraziť všetko** |
| **Nové prihlášky** | Prihlášky so stavom *nová*, teda **zatiaľ nevybavené**. | Modul **Uchádzači** je zapnutý a smiete čítať uchádzačov | **Zobraziť všetko** otvorí zoznam uchádzačov filtrovaný na nové. |
| **Otvorené procesy** | Procesy, ktoré **prebieha**. | Modul **Procesy** je zapnutý a smiete čítať procesy | **Zobraziť všetko** otvorí otvorené procesy. |
| **Otvorené konverzácie podpory** | **Aktívne alebo čakajúce konverzácie v helpdesku** spolku. | Modul **Podpora (helpdesk)** je zapnutý a smiete ho čítať | **Zobraziť všetko** |
| **Úlohy po termíne** | Úlohy na nástenke úloh, ktorých termín uplynul a ktoré nie sú hotové. | Modul **Nástenka úloh** je zapnutý a máte plný prístup (nástenka úloh je len pre používateľov s plným prístupom) | **Zobraziť všetko** otvorí nástenku úloh len s úlohami po termíne. |
| **Nové prihlásenia** | Prihlásenia **na pracovné zmeny** za posledných 14 dní, na bežné zmeny, ktoré sa ešte nekonali. Prihlásenia na zmenu, ktorú niekto označil ako skontrolovanú, sa už nepočítajú. | Modul **Správa pracovných hodín** je zapnutý a smiete čítať pracovné hodiny | **Zobraziť všetko** otvorí **Sedenia a prehľad**. |

Čísla na dlaždiciach **Otvorené žiadosti o nákup**, **Nové prihlášky**,
**Otvorené konverzácie podpory**, **Úlohy po termíne** a **Nové
prihlásenia** sú rovnaké ako červené odznaky v bočnom paneli (pozri
[Orientácia v aplikácii](navigation.md#badges-things-that-need-attention)).
Rovnako ako odznaky sa samy znížia, keď je niečo vybavené.

## Narodeniny tento týždeň {#birthdays-this-week}

Táto karta sa zobrazí, len keď má aspoň jeden súčasný člen narodeniny v
nasledujúcich siedmich dňoch vrátane dneška. Uvádza týchto členov,
najbližších ako prvých:

- meno člena s odkazom na jeho stránku,
- **dnes oslávi ...** pri narodeninách dnes, inak dátum a **oslávi ...**,
- zvýraznený odznak **Okrúhle** pri okrúhlych narodeninách (30, 40, 50, ...).

Členovia bez zadaného dátumu narodenia sa neuvádzajú. Karta sa
zobrazuje aj vtedy, keď je modul **Kalendár** vypnutý; jej tlačidlo
**Zobraziť všetko** vedie na úplný zoznam narodenín v kalendári, na
ktorý je potrebný modul kalendára a oprávnenie.

## Nedávni členovia {#recent-members}

Päť súčasných členov, ktorí boli **zadaní do Parcelly** najnovšie, s
dátumom **Členom od** vpravo (– ak nie je nastavený). Kliknutím na meno
otvoríte člena. V novej inštalácii sa zobrazí **Zatiaľ neboli vytvorení
žiadni členovia.**

**Nový člen** otvorí formulár pre nového člena.

## Rýchly prístup {#quick-access}

Skratky pre časté úlohy:

| Tlačidlo | Čo robí |
|---|---|
| **Vytvoriť nového člena** | Otvorí formulár pre nového člena. |
| **Vytvoriť novú parcelu** | Otvorí formulár pre novú parcelu. |
| **Exportovať členov ako CSV** | Stiahne zoznam členov ako súbor CSV, napríklad pre tabuľkový procesor. |
| **Exportovať parcely ako CSV** | Stiahne zoznam parciel ako súbor CSV. |

Vytváranie členov a parciel potrebuje **Zápis** pre **Členovia a
parcely**. Bez neho formulár odpovie hlásením **Na to nemáte
oprávnenie**.

## Súvisiace {#related}

- [Členovia](../modules/members.md) a [Parcely](../modules/parcels.md)
- [Orientácia v aplikácii](navigation.md)
- [Zapínanie a vypínanie modulov](../administration/modules.md)

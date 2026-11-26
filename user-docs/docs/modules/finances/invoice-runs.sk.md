# Vyúčtovania {#invoice-runs}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Vyúčtovanie je jedna dávka faktúr, zvyčajne „ročné faktúry 2026“.
Raz opíšete, ktoré riadky idú na faktúry a ako sa každá suma počíta.
Parcella potom vypočíta faktúru pre každú parcelu (a pre každého člena
fakturovaného priamo), umožní vám každú skontrolovať ako PDF a čísla
faktúr pridelí až pri dokončení.

!!! info "Kto to môže používať"
    Súčasť modulu **Financie** (predvolene vypnutý). Čítanie potrebuje
    oprávnenie na čítanie pre **Financie**; vytváranie vyúčtovaní,
    úprava položiek, dokončenie a odosielanie potrebujú oprávnenie na
    zápis; mazanie vyúčtovania alebo položky potrebuje oprávnenie na
    mazanie. Členovia výboru a administrátori môžu všetko. Pozri
    [Financie](index.md).

Vyúčtovanie je vždy v jednom z dvoch stavov:

| Stav | Význam |
|---|---|
| **Koncept** | Vyúčtovanie sa pripravuje. Položky možno voľne pridávať, meniť a odstraňovať, náhľad sa prepočíta pri každom otvorení a celé vyúčtovanie sa ešte dá zmazať. Zatiaľ neexistuje žiadna faktúra. |
| **Dokončené** | Vytvorili sa faktúry s trvalými číslami. Položky sú zmrazené, vyúčtovanie sa už nedá zmazať a teraz faktúry posielate a zaznamenávate platby. Cesta späť ku konceptu neexistuje. |

## Ročné faktúry (zoznam vyúčtovaní) {#annual-invoices-list-of-runs}

![Ročné faktúry](../../assets/screenshots/finances/run-list.png)

Otvoríte ich cez **Financie → Vydané faktúry** alebo kartou **Vydané
faktúry** na prehľade. Uvádza každé vyúčtovanie, najnovší rok prvý.

**Horný pruh**

| Tlačidlo | Čo robí |
|---|---|
| **Nové vyúčtovanie** | Otvorí formulár pre nové vyúčtovanie (pozri nižšie). Zobrazí sa len s oprávnením na zápis. |
| **Všetky faktúry** | Otvorí zoznam všetkých faktúr zo všetkých vyúčtovaní, pozri [Faktúry](invoices.md#invoices-all-runs). |
| **Späť na Financie** | Späť na finančný prehľad. |

**Filter**

| Filter | Čo robí |
|---|---|
| **Rok** | Ukáže len vyúčtovania presne tohto roka. |
| **Predmet** | Ukáže vyúčtovania, ktorých predmet obsahuje tento text (na veľkosti písmen nezáleží). |
| **Stav** | **Všetky**, **Koncept** alebo **Dokončené**. |
| **Filtrovať** / **Zrušiť filter** | Použije filter / zruší všetky filtre. |

**Tabuľka vyúčtovaní**

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Rok** | Rok, ktorý vyúčtovanie fakturuje. |
| **Predmet** | Predmet vyúčtovania, ako sa tlačí na faktúrach. |
| **Stav** | **Koncept** (žltý) alebo **Dokončené** (zelené). |
| **Položky** | Koľko definícií položiek (riadkov faktúry) vyúčtovanie má. |
| **Otvoriť** | Otvorí vyúčtovanie. |
| Ikona koša | Po potvrdení zmaže vyúčtovanie so všetkými definíciami položiek. Zobrazí sa len pri konceptoch a s oprávnením na mazanie. Dokončené vyúčtovanie sa nikdy nedá zmazať. |

Ak ešte nie sú žiadne vyúčtovania, tabuľka hovorí „Zatiaľ žiadne
vyúčtovania.“; ak váš filter nič nenájde, „Filtru nezodpovedá žiadne
vyúčtovanie.“

### Nové vyúčtovanie {#new-invoice-run}

Kliknite na **Nové vyúčtovanie** v hornom pruhu. Otvorí sa dialóg:

| Pole | Čo robí |
|---|---|
| **Rok** | Povinné. Predvyplnené aktuálnym rokom. Tento rok rozhoduje, ktoré odpočty meradiel, záznamy poistenia a vyhodnotenie pracovných hodín položky podľa spotreby použijú a v ktorom roku sa čísla faktúr počítajú. |
| **Predmet** | Povinné. Nadpis každej faktúry, napr. „Ročná faktúra 2026“. |
| **Dátum vystavenia** | Povinné. Predvyplnené dnešným dňom. Tlačí sa na faktúrach ako dátum faktúry. |
| **Dátum splatnosti** | Povinné. Tlačí sa na faktúrach. Rozhoduje aj o tom, kedy sa nezaplatená faktúra počíta ako faktúra po splatnosti a objaví sa v časti [Upomienky](invoices.md#reminders). |
| **Text pätičky** | Voliteľné. Tlačí sa pod riadkami položiek na každej faktúre vyúčtovania, napr. vaše platobné pokyny. Môžete použiť tieto zástupné symboly, ktoré sa vyplnia pre každú faktúru: `{invoice_number}`, `{parcel_number}`, `{invoice_address}` (mená a adresa príjemcov), `{due_date}`. |
| **Vytvoriť** | Vytvorí vyúčtovanie ako koncept a otvorí ho. |
| **Zrušiť** | Zatvorí dialóg bez uloženia. |

!!! tip "Zástupné symboly v texte pätičky"
    Typická pätička je „Sumu prosím uhraďte do {due_date} s uvedením
    {invoice_number} ako referencie.“ Ak text pätičky obsahuje zloženú
    zátvorku, ktorá nie je jedným zo štyroch zástupných symbolov, text sa
    vytlačí presne tak, ako ste ho napísali, bez vyplnenia čohokoľvek.
    Na faktúre členovi (bez parcely) nie je číslo parcely, ktoré by sa
    dalo vyplniť, preto sa vyhnite `{parcel_number}`, ak vyúčtovanie
    vytvorí aj faktúry členom.
    <!-- TODO(verify): by the code, a member invoice's footer prints the literal word "None" for {parcel_number}; confirm in a real PDF. -->

Rok, predmet, dátumy a text pätičky sa po vytvorení vyúčtovania nedajú
zmeniť. <!-- TODO(verify): no edit route for run header fields exists; if a mistake is made in a draft run, the only way is to delete and recreate it. -->

## Vyúčtovanie (koncept) {#invoice-run-draft}

![Koncept vyúčtovania](../../assets/screenshots/finances/run-detail.png)

Názov stránky ukazuje rok a predmet, napr. „2026 — Ročná faktúra“.
Kým je vyúčtovanie koncept, na tejto stránke skladáte jeho riadky
(„definície položiek“).

**Horný pruh**

| Tlačidlo | Čo robí |
|---|---|
| **Náhľad** | Otvorí [náhľad](#preview-invoices). Zobrazí sa, až keď má vyúčtovanie aspoň jednu položku. |
| **Späť na vyúčtovania** | Späť do zoznamu. |

### Definície položiek {#item-definitions}

Každý riadok je jeden druh riadku, ktorý sa môže objaviť na faktúrach.
S oprávnením na zápis sa každý riadok dá priamo upravovať; zmeňte polia
a kliknite na ikonu fajky na konci riadku, aby ste ho uložili. Bez
oprávnenia na zápis vidíte tie isté informácie ako obyčajný text.

| Stĺpec / pole | Čo robí |
|---|---|
| **Poradie** | Číslo na zoradenie. Riadky sa na faktúre objavia v tomto poradí. Nová položka je predvyplnená číslom o desať vyšším ako doterajšie najvyššie poradie, takže neskôr zostane miesto vložiť položku medzi ne. |
| **Názov** | Povinné. Text riadku na faktúre, napr. „Nájom“. |
| **Popis** | Voliteľné, malé sivé pole pod názvom. Na faktúre sa tlačí malým písmom pod názvom. |
| **Výpočet** | Ako sa suma počíta, pozri [Základy výpočtu](#calculation-bases) nižšie. Jeho zmena mení, ktoré z ostatných polí sa zobrazia. |
| **Jednotková cena** | Cena za jednotku (za parcelu, za osobu, za m² ...). Pri všeobecnej dávke je to celková suma na rozdelenie. Pri štyroch automatických spôsoboch výpočtu je skrytá a namiesto nej sa zobrazí „Počíta sa automaticky“. Zadajte ju s desatinnou čiarkou alebo bodkou, napr. `12,50`. |
| **Platí pre** | Pre koho je riadok. Podľa spôsobu výpočtu je to prepínač **Všetky parcely** / *n* parciel, prepínač **Všetci členovia** / *n* členov alebo pevná poznámka ako „Automaticky (na základe vyhodnotenia poistenia)“. Pozri [Kto dostane riadok](#who-gets-a-line). |
| **Kategória** | Voliteľná [účtovná kategória](bookkeeping.md#bookkeeping-categories). Skopíruje sa na každý riadok faktúry, takže platby tejto faktúry sa v [účtovnom prehľade](bookkeeping.md#accounting-statement) rozdelia do správnych kategórií. |
| Ikona fajky | Uloží riadok. Potrebuje oprávnenie na zápis. |
| Ikona koša | Po potvrdení („Zmazať túto definíciu položky?“) položku zmaže. Potrebuje oprávnenie na mazanie. |

Keď v riadku vypnete prepínač **Platí pre**, pod ním sa otvorí ďalší
riadok s výberom parciel alebo členov (pozri [Výber](#the-picker)).

!!! note
    Položky sa dajú meniť, len kým je vyúčtovanie koncept. Pokus o
    uloženie položky pri dokončenom vyúčtovaní sa odmietne hlásením
    „Toto vyúčtovanie je už dokončené; jeho definície položiek už
    nemožno meniť.“

### Pridať z katalógu položiek {#add-from-item-catalog}

Zobrazí sa s oprávnením na zápis, keď váš [katalóg položiek](#item-catalog)
obsahuje šablóny, ktoré toto vyúčtovanie ešte nemá. Každá zostávajúca
šablóna je uvedená so spôsobom výpočtu, jednotkovou cenou a rozsahom a
**je predvolene zaškrtnutá**. Odškrtnite, čo nechcete, a kliknite na
**Pridať vybrané položky**. Každá zaškrtnutá šablóna sa stane novou
položkou tohto vyúčtovania so všetkými svojimi nastaveniami, vrátane
konkrétneho výberu parciel alebo členov.

**Spravovať katalóg** vás zavedie do katalógu položiek.

Šablóna sa považuje za „už pridanú“, keď má vyúčtovanie položku s
presne rovnakým názvom. Ak teda položku vo vyúčtovaní premenujete alebo
zmažete, šablóna sa ponúkne znova; ak po pridaní premenujete šablónu,
ponúkne sa tiež znova.

Keď už nie je čo ponúknuť, uvidíte namiesto toho krátku poznámku:
„Všetky položky z katalógu už boli do tohto behu pridané.“ alebo, ak je
katalóg prázdny, „Zatiaľ žiadne položky v katalógu -- pridajte
opakujúce sa položky raz a vyberajte ich tu každý rok.“ Obe majú
tlačidlo **Spravovať katalóg**.

### Pridať položku {#add-item}

Pod katalógom je formulár na ručné pridanie jednorazovej položky. Má
tie isté polia ako tabuľka (**Poradie**, **Názov**, **Popis**,
**Spôsob výpočtu**, **Jednotková cena**, **Kategória**), potom prepínač
rozsahu (**Platí pre každú parcelu** alebo **Platí pre každého člena**,
oba predvolene zapnuté) a, keď ho vypnete, výber. Položku pridáte
tlačidlom **+**.

## Základy výpočtu {#calculation-bases}

**Spôsob výpočtu** rozhoduje, ako Parcella vypočíta riadok pre každú
parcelu alebo člena. Každá suma sa zaokrúhli na centy za riadok; súčet
faktúry je súčet jej riadkov.

| Spôsob výpočtu | Fakturuje sa | Množstvo × cena | Odkiaľ sú čísla |
|---|---|---|---|
| **Pevná suma za parcelu** | Každej parcele v rozsahu | 1 × jednotková cena | Sumu zadáte vy, napr. poplatok spolku za parcelu. |
| **Pevná suma za osobu** | Každému členovi v rozsahu, na jeho vlastnej faktúre | 1 × jednotková cena | Sumu zadáte vy, napr. členský príspevok. Fakturuje sa na člena, bez ohľadu na to, či má parcelu. |
| **Za prenajatý m²** | Každej parcele v rozsahu | rozloha parcely × jednotková cena | Rozloha uložená pri parcele. Parcela bez rozlohy riadok nedostane. |
| **Podiel na nájme spoločnej plochy** | Každej parcele v rozsahu | (spoločná plocha ÷ počet fakturovaných parciel) × jednotková cena | Spoločná plocha („Rozloha B“) z [Nastavení spolku](../../administration/settings.md). Podiel sa zaokrúhli na 0,1 m². |
| **Verejné dávky (vlastná plocha + podiel na spoločnej ploche)** | Každej parcele v rozsahu | (rozloha parcely + podiel na spoločnej ploche) × jednotková cena | Ako vyššie, plus vlastná rozloha parcely, jednou sadzbou za m². |
| **Všeobecná dávka (rozdelená rovnomerne medzi všetky parcely)** | Každej parcele v rozsahu | 1 × (celková suma ÷ počet fakturovaných parciel) | Ako jednotkovú cenu zadáte **celkovú** sumu, ktorú spolok potrebuje vybrať; každá parcela platí rovnaký podiel, zaokrúhlený na centy. |
| **Spotreba vody (z modúlu)** | Každej parcele s vodomerom | spotreba roka × cena za jednotku | Spotreba aj cena pochádzajú z [Voda a elektrina](../metering.md). |
| **Spotreba elektriny (z modúlu)** | Každej parcele s elektromerom | spotreba roka × cena za jednotku | Ako pri vode. |
| **Náklady na poistenie (z modúlu)** | Každej parcele s poistením na daný rok | jeden riadok na každú zložku poistenia | Z [Poistenia](../insurance.md). |
| **Nedoplatok pracovných hodín (z modulu)** | Každej parcele alebo členovi, ktorí dlžia peniaze za chýbajúce pracovné hodiny | 1 × dlžná suma | Z [vyhodnotenia pracovných hodín](../work-hours.md) roka vyúčtovania. |

Podrobnosti ku každému spôsobu:

**Pevná suma za parcelu / za osobu.** Ak necháte **Jednotková cena**
prázdnu, položka nefakturuje nič.

**Za prenajatý m².** Používa rozlohu zaznamenanú pri každej parcele.
Pred dokončením skontrolujte, či má každá parcela vyplnenú rozlohu --
parcela bez nej potichu nedostane riadok nájmu.

**Podiel na nájme spoločnej plochy.** Spoločná plocha sa rovnomerne
rozdelí medzi presne tie parcely, ktoré túto položku dostanú (tie v jej
rozsahu, ktoré majú aj niekoho, komu fakturovať). Podiely tak dajú
dokopy celú spoločnú plochu a spolok vyberie celý nájom. Ak je
spoločná plocha nulová alebo nie je nastavená, položka nefakturuje
vôbec nič. Spoločná plocha sa v Nastaveniach spolku počíta ako celková
rozloha mínus rozloha parciel mínus obecná rozloha.

**Verejné dávky** (pozri [slovník](../../glossary.md)). Ako podiel na
spoločnej ploche, ale pripočítaný k vlastnej rozlohe parcely a
fakturovaný jednou spoločnou sadzbou. Ak spoločná plocha nie je
nastavená, vlastná rozloha parcely sa fakturuje aj tak -- spoločná časť
sa jednoducho počíta ako 0 m².

**Všeobecná dávka** („Umlage“, pozri [slovník](../../glossary.md)).
Použite ju na jednorazový náklad, ktorý spolok prenáša na členov, napr.
právne trovy 1 200,00 rozdelené medzi 40 parciel = 30,00 na každú.
Počítajú sa len parcely, ktoré sa naozaj fakturujú, takže voľné parcely
nikdy „nezjedia“ podiel. Keďže sa každý podiel zaokrúhľuje na centy,
vybraná suma sa môže od zadanej sumy líšiť o niekoľko centov.

**Spotreba vody / Spotreba elektriny.** Pre každú parcelu s meracím
bodom parcely daného druhu Parcella vezme spotrebu aktuálneho meradla v
roku vyúčtovania (odpočet toho roka mínus predchádzajúci odpočet) a
vynásobí ju cenou za jednotku nastavenou pre ten rok v module merania.
Jednotkovú cenu tu nezadávate.

- Parcela bez odpočtu za daný rok riadok nedostane.
- Ak pre dané médium a rok nie je nastavená cena, nikomu sa nefakturuje.
- Po výmene meradla počas roka sa fakturuje spotreba **oboch** meradiel:
  starého až po jeho konečný stav (zadaný vo formulári výmeny) a nového
  od jeho počiatočného stavu.

!!! warning "Meracie body s násobiteľom"
    Ak má merací bod v module merania násobiteľ, obrazovky merania
    ukazujú vynásobenú spotrebu, ale faktúra fakturuje **surový** rozdiel
    odpočtov. Takéto parcely skontrolujte v náhľade.


**Náklady na poistenie.** Fakturujú sa každej parcele, ktorá má záznam
poistenia na rok vyúčtovania. Namiesto jednej súhrnnej sumy faktúra
ukazuje jeden riadok na každú zložku, ktorú parcela naozaj má: „Poistenie
majetku (*balík*)“, „Úrazové poistenie (domácnosť)“ a prípadne „Úrazové
poistenie (+*n* ďalších osôb)“. Tieto texty riadkov sú pevné, v jazyku
spolku -- vlastný názov položky sa pre ne nepoužije. Sumy pochádzajú z
cien poistenia nastavených pre ten rok.

**Nedoplatok pracovných hodín.** Fakturuje presne to, čo podľa
vyhodnotenia pracovných hodín za rok vyúčtovania zostáva dlžné.
Oslobodené parcely a parcely alebo členovia, ktorí povinnosť splnili, sa
nefakturujú. Či to skončí na faktúre parcely alebo na samostatnej
faktúre členovi, závisí od toho, ako sa v danom roku počítajú pracovné
hodiny: na parcelu to dá na faktúru parcely, na člena na vlastnú
faktúru každého člena.

## Kto dostane riadok {#who-gets-a-line}

**Spôsoby podľa parciel** (pevná suma za parcelu, za m², podiel na
spoločnej ploche, verejné dávky, všeobecná dávka) používajú prepínač
**Platí pre každú parcelu**:

- Zapnutý (predvolene): každá parcela, ktorej sa dá fakturovať.
- Vypnutý: len parcely, ktoré zaškrtnete vo výbere.

**Pevná suma za osobu** namiesto toho používa **Platí pre každého
člena**:

- Zapnutý (predvolene): každý aktívny člen.
- Vypnutý: len členovia, ktorých zaškrtnete.

**Štyri automatické spôsoby** (voda, elektrina, poistenie, nedoplatok
pracovných hodín) nemajú výber. Komu sa fakturuje, vyplýva z druhého
modulu: z meradla, záznamu poistenia alebo nedoplatku. Namiesto výberu
sa zobrazí poznámka ako „Automaticky (parcely s aktívnym vodomerom)“.
(Napriek tomuto zneniu je vo vyúčtovaní zahrnutý aj vypnutý merací
bod.)

Ktorým parcelám sa vôbec dá fakturovať:

- Parcela dostane faktúru, len ak je aspoň jeden **súčasný** nájomca
  označený **Použiť ako fakturačnú adresu**. Nájomcovia, ktorí dali
  výpoveď k budúcemu dátumu, sa počítajú, kým naozaj neodídu.
- Ukončenej parcele sa fakturuje, ak má takého nájomcu (napríklad
  nového nájomcu, ktorý ju prevzal skôr, než sa stav zmenil späť).
  Vždy sa preskakujú len zmazané parcely.
- Ak nájomcovia s fakturačnou adresou bývajú na rôznych adresách,
  parcela aj tak dostane **jednu** faktúru (jedno číslo, jedna suma), s
  **výtlačkom pre každú adresu**. Nájomcovia so spoločnou adresou sú
  uvedení spolu na jednom výtlačku. Výtlačky sa líšia len okienkom s
  adresou.
- Parcela, ktorej všetky riadky vyjdú prázdne, faktúru nedostane.

Faktúry členom (z **Pevná suma za osobu** alebo z nedoplatku pracovných
hodín počítaného na člena) sú samostatné faktúry adresované členovi na
jeho vlastnú adresu. Namiesto čísla parcely ukazujú **Bez parcely
(člen)**. Nájomca, ktorému sa fakturuje aj poplatok za osobu, preto
dostane dve faktúry: jednu za parcelu, jednu za seba. Všetky riadky za
osobu pre toho istého člena sú spojené na jednej faktúre.

### Výber {#the-picker}

Keď je prepínač rozsahu vypnutý, objaví sa výber s označením
**Parcely** alebo **Členovia**.

| Ovládací prvok | Čo robí |
|---|---|
| **Zobraziť zoznam** / **Skryť zoznam** | Otvorí alebo zatvorí zoznam zaškrtávacích políčok. |
| **Hľadať…** | Zúži zoznam na zodpovedajúce čísla parciel alebo mená. Keď nič nevyhovuje, zobrazí sa „Žiadne výsledky“. |
| **Vybrať všetko** / **Zrušiť výber** | Zaškrtne alebo odškrtne každú **práve viditeľnú** položku -- môžete teda najprv hľadať a potom vybrať len tie. |

Výber parciel uvádza aktívne parcely; výber členov uvádza aktívnych
členov.

!!! tip
    Rozsah sa dá upravovať až do dokončenia. Pri príprave vyúčtovania
    ho môžete meniť, koľkokrát chcete.

## Náhľad faktúr {#preview-invoices}

<!-- TODO(verify): no screenshot -- the preview page is two clicks away from a fixed URL (run list -> run -> Preview), which the screenshot tool can't follow, and the sample data has no invoice runs. -->

Kliknite na **Náhľad** pri koncepte vyúčtovania. Parcella hneď vypočíta
každú faktúru, ktorú by vyúčtovanie vytvorilo, bez uloženia alebo
odoslania čohokoľvek. Názov stránky je „Náhľad — *rok* *predmet*“.

Modré pole hore hovorí, koľko faktúr by sa vytvorilo, a pripomína:
„Zatiaľ nič nie je uložené ani odoslané — skontrolujte PDF nižšie a
potom dokončite.“

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Parcela** | Číslo parcely alebo **Bez parcely (člen)** pri faktúre členovi. |
| **Príjemca** | Mená, na ktoré bude faktúra adresovaná. |
| **Medzisúčet** | Celková suma faktúry. |
| **PDF** | Otvorí faktúru ako PDF v novej karte, presne tak, ako bude vyzerať, s „Náhľad“ ako číslom faktúry a pruhom „Náhľad — zatiaľ nedokončené ani neodoslané“. |
| **Dokončiť a prideliť čísla faktúr** | Po potvrdení dokončí vyúčtovanie. Zobrazí sa len s oprávnením na zápis, kým je vyúčtovanie koncept. |
| **Späť na vyúčtovanie** | Späť na vyúčtovanie, aby ste opravili položky. |

Ak je zoznam prázdny, stránka hovorí „Nebudú vytvorené žiadne faktúry —
skontrolujte rozsah paciel v definíciách položiek a príznak
fakturačnej adresy u dotknutých členov.“

!!! tip "Náhľad je vždy aktuálny"
    Pre náhľad sa nič neukladá. Pri každom otvorení načíta aktuálne
    parcely, nájomcov, odpočty meradiel, poistenie a pracovné hodiny.
    Opravte dáta v týchto moduloch a jednoducho stránku načítajte znova.

### Čo urobí dokončenie {#what-finalizing-does}

Keď kliknete na **Dokončiť a prideliť čísla faktúr** a potvrdíte
(„Dokončiť toto vyúčtovanie? Čísla faktúr budú trvalo pridelené,
definície položiek už nebude možné meniť. Túto akciu nemožno vrátiť
späť.“):

1. Parcella naposledy vypočíta faktúry, presne ako v náhľade.
2. Každá faktúra dostane trvalé číslo v poradí zoznamu náhľadu. Formát
   pochádza z **Formát čísla faktúry** v
   [Nastaveniach spolku](../../administration/settings.md) (predvolene
   *rok*/*číslo*, napr. `2026/1`). Číslovanie pokračuje od najvyššieho
   čísla už použitého v tom istom roku, vo všetkých vyúčtovaniach, a pri
   prvej faktúre roka začína od 1.
3. Mená a adresy príjemcov sa skopírujú na faktúry. Neskoršie zmeny
   adresy člena už vystavenú faktúru neprepíšu.
4. Vyúčtovanie sa stane **Dokončené** a jeho položky sa zmrazia.

Ak je v Nastaveniach spolku vyplnené **Ďalšie číslo faktúry
(prepísať)**, toto vyúčtovanie namiesto toho začne od tohto čísla a
nastavenie sa potom vymaže. Ak by sa tým znova použilo číslo už
pridelené v tom istom roku, dokončenie sa zastaví s chybovým hlásením a
nič sa nevytvorí.

Vyúčtovanie bez akejkoľvek položky sa nedá dokončiť: „Toto vyúčtovanie
zatiaľ nemá žiadne definície položiek — pred dokončením pridajte aspoň
jednu.“

## Vyúčtovanie (dokončené) {#invoice-run-finalized}

Po dokončení stránka vyúčtovania ukazuje zelenú poznámku „Toto
vyúčtovanie je dokončené. Čísla faktúr sú trvalé, definície položiek už
nemožno meniť.“ Zoznam položiek zmizne; namiesto neho vidíte doručenie a
faktúry vyúčtovania.

### Doručenie {#delivery}

Zobrazí sa s oprávnením na zápis.

| Tlačidlo | Čo robí |
|---|---|
| **Odoslať e-maily a nahrať do cloudu** | Pošle e-mailom každú faktúru vyúčtovania, ktorá ešte nebola odoslaná, s priloženým PDF, a nahrá každú faktúru, ktorá ešte nebola nahraná, do cloudového priečinka jej parcely. Opätovné spustenie spracuje len to, čo ešte chýba. |
| **Stiahnuť tlačový balík** | Stiahne jedno PDF s listom pre každého nájomcu, ktorý nedostáva faktúry e-mailom -- jeden list na adresu, s menami ľudí tam bez e-mailu --, pripravené na tlač a vloženie do obálok s okienkom. Tieto faktúry sa označia ako vytlačené. |

**Kto dostane e-mail:** každý nájomca s fakturačnou adresou uvedený na
faktúre (alebo, pri faktúre členovi, člen), ktorý má zapnuté **Môže
dostávať informácie e-mailom** a aspoň jednu uloženú e-mailovú adresu.
Každý dostane výtlačok pre svoju vlastnú adresu; použije sa primárna
e-mailová adresa. Všetci ostatní dostanú vytlačený list z tlačového
balíka -- **aj** vtedy, keď niekto, s kým bývajú, dostal e-mail.
Nájomcovia bez e-mailu so spoločnou adresou dostanú jeden spoločný
list: „Členovia bez e-mailových upozornení zostávajú pre tlačový balík
nižšie.“

**Nahratie do cloudu** prebehne, len ak je nastavené cloudové úložisko a
parcela má cloudový priečinok. Faktúry členom sa nikdy nenahrávajú,
pretože neexistuje priečinok člena. Neúspešné nahratia sa potichu
preskočia a nabudúce sa skúsia znova.

!!! note "Tlačový balík"
    Balík sa skladá podľa toho, kto je dostupný e-mailom, nie podľa
    toho, čo bolo odoslané. Môžete ho stiahnuť pred odoslaním e-mailov
    aj po ňom a vždy obsahuje tie isté výtlačky -- vrátane tých, ktoré
    ste vytlačili minule. Ak môže každá faktúra ísť e-mailom, dostanete
    hlásenie „Pri všetkých faktúrach v tomto vyúčtovaní je člen dostupný
    e-mailom -- nie je čo tlačiť.“

### Filter {#filter}

Nad tabuľkou faktúr môžete zoznam zúžiť. Funguje ako filter pri
[Všetkých faktúrach](invoices.md#invoices-all-runs): **Č. faktúry**,
**Príjemca**, **Parcela** (obsahuje tento text), **Suma od**, **Suma
do** (medzisúčet faktúry) a **Stav** (**Všetky**, **Otvorená**,
**Čiastočne uhradená**, **Uhradená**). **Filtrovať** ho použije,
**Zrušiť filter** ho zruší.

### Faktúry {#invoices}

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Č. faktúry** | Číslo faktúry; kliknutím otvoríte [faktúru](invoices.md#invoice). |
| **Parcela** | Číslo parcely alebo **Bez parcely (člen)**. |
| **Príjemca** | Mená príjemcov. |
| **Medzisúčet** | Suma faktúry. |
| **Stav platby** | **Otvorená** (červená, nič nezaplatené), **Čiastočne uhradená** (žltá) alebo **Uhradená** (zelená). |
| **Doručenie** | Ikony toho, čo sa stalo: obálka = „Odoslané e-mailom“, tlačiareň = „Zahrnuté v tlačovom balíku“, oblak = „Nahrané do cloudového úložiska“. Podržte myš nad ikonou a uvidíte jej význam. |
| **Platba** | Otvorí dialóg platby pre túto faktúru (pozri nižšie). Potrebuje oprávnenie na zápis. |
| **PDF** | Otvorí PDF faktúry v novej karte. |

### Dialóg platby {#payment-dialog}

Najrýchlejší spôsob, ako zaznamenať platby mnohých faktúr: kliknite na
**Platba** v riadku, zadajte platbu a ste späť na stránke vyúčtovania,
pripravení na ďalšiu. Názov dialógu je „Platba — Faktúra *číslo*“.

Uvádza doteraz zaznamenané platby (dátum, suma, účet, poznámka), každú
s ikonou koša na zmazanie (potrebuje oprávnenie na mazanie, pýta sa
„Zmazať túto platbu?“). Ak žiadne nie sú: „Zatiaľ neboli zaznamenané
žiadne platby.“

| Pole | Čo robí |
|---|---|
| **Suma** | Povinné. Prijatá suma, napr. `45,00`. Čiastočné platby sú v poriadku; každú zaznamenajte samostatne. |
| **Uhradené dňa** | Povinné. Predvyplnené dnešným dňom. Tento dátum rozhoduje, v ktorom roku sa príjem v účtovnom prehľade započíta. |
| **Poznámka** | Voliteľné, napr. „bankový prevod“. |
| **Účet** | Voliteľné. [Účet](bank-accounts.md#accounts), na ktorý peniaze prišli. Ponúkajú sa len aktívne účty. Platba sa potom zobrazí v zápisoch tohto účtu. |
| **Pridať platbu** | Uloží platbu. |

Stav platby sa aktualizuje sám: keď platby dosiahnu sumu faktúry plus
prípadné poplatky za upomienky, faktúra je **Uhradená**. Pozri
[Platby](invoices.md#payments).

## Katalóg položiek {#item-catalog}

![Katalóg položiek](../../assets/screenshots/finances/item-templates.png)

Otvoríte ho kartou **Katalóg položiek** na prehľade alebo tlačidlom
**Spravovať katalóg** pri koncepte vyúčtovania. Katalóg uchováva vaše
opakujúce sa riadky faktúr („šablóny položiek“), aby ste ich nemuseli
každý rok písať znova. Šablóny sú nezávislé od akéhokoľvek vyúčtovania;
do vyúčtovania ich prenesiete cez [Pridať z katalógu
položiek](#add-from-item-catalog).

Obrazovka má tie isté polia ako položky vyúčtovania:

- **Nová šablóna položky** (s oprávnením na zápis): **Poradie**,
  **Názov**, **Popis**, **Spôsob výpočtu**, **Jednotková cena**,
  **Kategória**, prepínač rozsahu (**Platí pre každú parcelu** /
  **Platí pre každého člena**) a [výber](#the-picker). Uložíte ju
  tlačidlom **+**.
- **Šablóny položiek**: jeden upraviteľný riadok na šablónu so
  stĺpcami **Poradie**, **Názov**, **Výpočet**, **Jednotková cena**,
  **Platí pre** a **Kategória**. Zmeňte riadok a uložte ho kliknutím na
  jeho ikonu fajky; ikona koša ho zmaže (potrebuje oprávnenie na
  mazanie).

Po uložení uvidíte „Uložené.“. Ak je katalóg prázdny: „Zatiaľ žiadne
šablóny položiek -- pridajte jednu vyššie.“

Spôsoby výpočtu a pravidlá rozsahu sú presne tie, ktoré sú opísané v
častiach [Základy výpočtu](#calculation-bases) a [Kto dostane
riadok](#who-gets-a-line).

!!! note "Šablóny a vyúčtovania sú nezávislé"
    Pridanie šablóny do vyúčtovania ju skopíruje. Neskoršia zmena
    šablóny nezmení vyúčtovania, ktoré ju už použili, a zmazanie šablóny
    nechá položky týchto vyúčtovaní nedotknuté („Odstrániť túto šablónu
    položky? Vyúčtovania, ktoré ju už použili, si zachovajú svoje
    položky, len bez odkazu na šablónu.“). Ceny, ktoré sa každý rok
    menia, je najlepšie aktualizovať v katalógu skôr, než položky
    pridáte do nového vyúčtovania.

## Súvisiace {#related}

- [Ročné vyúčtovanie](../../guides/annual-invoicing.md) -- celý postup
  krok za krokom.
- [Faktúry, platby a upomienky](invoices.md)
- [Voda a elektrina](../metering.md), [Poistenie](../insurance.md),
  [Pracovné hodiny](../work-hours.md) -- odkiaľ pochádzajú automatické
  sumy.
- [Nastavenia spolku](../../administration/settings.md) -- formát čísla
  faktúry, bankové údaje, rozlohy.

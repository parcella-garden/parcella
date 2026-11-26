# Prijaté faktúry {#incoming-invoices}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Prijaté faktúry sú účty, ktoré spolok dostáva: od dodávateľa vody, od
poisťovne, zo železiarstva. Ak ich tu zaznamenáte, rozdelené do položiek
s účtovnou kategóriou pri každej, a poznačíte si, kedy boli zaplatené,
získate výdavkovú stranu
[účtovného prehľadu](bookkeeping.md#accounting-statement).

!!! info "Kto to môže používať"
    Súčasť modulu **Financie** (predvolene vypnutý). Prezeranie
    potrebuje oprávnenie na čítanie pre **Financie**; zaznamenávanie
    faktúr, prepájanie kontaktov a pridávanie platieb potrebuje
    oprávnenie na zápis; mazanie faktúry alebo platby potrebuje
    oprávnenie na mazanie. Nahrávanie a sťahovanie naskenovaného účtu
    (prílohy) je možné len pre členov výboru a administrátorov, a len
    keď je zapnutý modul **Cloudové úložisko** a nastavený priečinok
    pre prijaté faktúry. Pozri [Financie](index.md).

## Zoznam prijatých faktúr {#incoming-invoices-list}

![Prijaté faktúry](../../assets/screenshots/finances/incoming-invoice-list.png)

Otvoríte ho cez **Financie → Prijaté faktúry** alebo kartou **Prijaté
faktúry** na prehľade. Zoznam je zoradený podľa dátumu faktúry,
najnovšie navrchu.

**Horný pruh**

| Tlačidlo | Čo robí |
|---|---|
| **Zaznamenať prijatú faktúru** | Otvorí formulár pre novú prijatú faktúru (pozri nižšie). Potrebuje oprávnenie na zápis. |
| **Späť na Financie** | Späť na finančný prehľad. |

**Filter**

| Filter | Čo robí |
|---|---|
| **Č. faktúry** | Faktúry, ktorých číslo obsahuje tento text. |
| **Odosielateľ** | Faktúry, ktorých odosielateľ obsahuje tento text. |
| **Suma od** / **Suma do** | Celková suma faktúry aspoň / najviac toľko. |
| **Stav platby** | **Všetky**, **Otvorená**, **Čiastočne uhradená** alebo **Uhradená**. |
| **Filtrovať** / **Zrušiť filter** | Použije filter / zruší ho. |

**Tabuľka**

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Dátum** | Dátum faktúry. |
| **Odosielateľ** | Kto poslal účet; kliknutím otvoríte [prijatú faktúru](#incoming-invoice). |
| **Č. faktúry** | Číslo faktúry dodávateľa, ak bolo zadané. |
| **Kategórie** | Jeden riadok na položku: jej kategória (alebo „Bez kategórie“) a jej popis. |
| **Suma** | Celková suma faktúry (súčet všetkých položiek). |
| **Stav platby** | **Otvorená**, **Čiastočne uhradená** alebo **Uhradená**, podľa zaznamenaných platieb. |
| Ikona sťahovania | Stiahne priložený účet. Zobrazí sa len vtedy, keď je príloha a smiete používať cloudové úložisko. |
| Ikona koša | Po potvrdení zmaže prijatú faktúru s jej položkami a platbami. Potrebuje oprávnenie na mazanie. |

Ak ešte nič nebolo zaznamenané: „Zatiaľ neboli zaznamenané žiadne
prijaté faktúry.“

!!! note "Mazanie ponechá prílohu"
    „Naozaj vymazať túto prijatú faktúru? Príloha sa tým z cloudového
    priečinka nevymaže.“ Naskenovaný účet zostane v zdieľanom
    priečinku; ak treba, odstráňte ho tam ručne.

## Zaznamenať prijatú faktúru {#record-incoming-invoice}

Kliknite na **Zaznamenať prijatú faktúru**. Otvorí sa dialóg:

| Pole | Čo robí |
|---|---|
| **Kontakt** | Voliteľné. Zobrazí sa len vtedy, keď je zapnutý modul [Externé kontakty](../external-contacts.md) a smiete čítať kontakty. Výber dodávateľa z vašich kontaktov za vás vyplní **Odosielateľ** („Výber kontaktu vyplní odosielateľa.“), pokiaľ ste ho už nenapísali. **— žiadny —** neprepojí žiadny kontakt. |
| **Odosielateľ** | Povinné. Názov dodávateľa tak, ako sa má zobrazovať v zoznamoch, pri párovaní s bankou a v účtovnom prehľade. |
| **Č. faktúry** | Voliteľné. Číslo faktúry dodávateľa. |
| **Dátum faktúry** | Povinné, predvyplnené dnešným dňom. |
| **Poznámka** | Voliteľné. |
| **Položky** | Jeden riadok na každú nákladovú položku (pozri nižšie). |
| **Pridať položku** | Pridá ďalší riadok položky. Každý riadok okrem prvého má tlačidlo na odstránenie. |
| **Príloha** | Voliteľné. Naskenovaný alebo odfotený účet. „Nahrané do zdieľaného cloudového priečinka vyššie.“ Zobrazí sa len členom výboru a administrátorom, keď je nastavené cloudové úložisko a priečinok pre prijaté faktúry. |
| **Uložiť** | Uloží faktúru. Uvidíte „Uložené.“. |
| **Zrušiť** | Zatvorí dialóg bez uloženia. |

Každá položka má tri polia:

| Pole | Čo robí |
|---|---|
| Kategória | Voliteľná [účtovná kategória](bookkeeping.md#bookkeeping-categories). „—“ znamená žiadna; položka sa potom zobrazí ako „Bez kategórie“. |
| **Popis (čo bolo zakúpené)** | Voliteľný voľný text, napr. „Servis kosačky“. Viac položiek môže mať rovnakú kategóriu, ale opisovať rôzne nákupy. |
| Suma | Suma položky, napr. `249,90`. Položka bez platnej sumy sa vynechá. |

!!! warning "Pred uložením skontrolujte"
    Odosielateľa, dátum, položky a sumy po uložení nemožno upraviť;
    neskôr sa dá meniť len prepojený kontakt a platby. Ak je niečo
    nesprávne, prijatú faktúru zmažte a zaznamenajte ju znova.

Ak sa prílohu nepodarí nahrať, faktúra sa aj tak uloží a chyba
cloudového úložiska sa zobrazí v hornej časti zoznamu. Názov súboru
prílohy v cloudovom priečinku začína interným číslom, takže dva účty s
rovnakým názvom súboru sa nikdy neprepíšu. Samotný priečinok sa
nastavuje v **Integrácie** → **Priečinok pre prijaté faktúry**, pozri
[Integrácie](../../administration/integrations.md).

## Prijatá faktúra {#incoming-invoice}

![Prijatá faktúra](../../assets/screenshots/finances/incoming-invoice-detail.png)

Otvorí sa, keď v zozname kliknete na odosielateľa. Názov je „Prijatá
faktúra — *odosielateľ*“.

**Horný pruh**

| Tlačidlo | Čo robí |
|---|---|
| **Stiahnuť prílohu** | Stiahne priložený účet z cloudového priečinka. Zobrazí sa len vtedy, keď je príloha a smiete používať cloudové úložisko. |
| **Späť na prijaté faktúry** | Späť do zoznamu. |

Karta **Faktúra**

| Pole | Čo ukazuje |
|---|---|
| **Odosielateľ** | Odosielateľ tak, ako bol zadaný. |
| **Kontakt** | Prepojený externý kontakt, ako odkaz na kontakt, ak smiete vidieť kontakty („zmazaný“, ak bol kontakt medzitým zmazaný). S oprávnením na zápis vám rozbaľovací zoznam a **Uložiť** umožnia prepojiť iný kontakt alebo žiadny. Zmena kontaktu **nezmení** text **Odosielateľ**. |
| **Č. faktúry** | Číslo faktúry dodávateľa. |
| **Dátum** | Dátum faktúry. |
| **Poznámka** | Poznámka. |
| **Suma** | Celková suma faktúry. |
| **Stav platby** | **Otvorená**, **Čiastočne uhradená** alebo **Uhradená**. |

Karta **Položky**: každá položka so svojou kategóriou („kód · názov“
alebo „Bez kategórie“), popisom a sumou a **Medzisúčet**.

Karta **Platby**: každá platba zaznamenaná k tomuto účtu s dátumom,
sumou, účtom a poznámkou. Ikona koša platbu zmaže (potrebuje oprávnenie
na mazanie, pýta sa „Zmazať túto platbu?“). Ak žiadne nie sú: „Zatiaľ
neboli zaznamenané žiadne platby.“

Zaznamenanie platby (oprávnenie na zápis):

| Pole | Čo robí |
|---|---|
| **Suma** | Povinné. Čo spolok zaplatil, ako kladné číslo. Čiastočné platby sú v poriadku. |
| **Uhradené dňa** | Povinné, predvyplnené dnešným dňom. Tento dátum rozhoduje, v ktorom roku sa výdavok započíta v účtovnom prehľade. |
| **Poznámka** | Voliteľné. |
| **Účet** | Voliteľné. [Účet](bank-accounts.md#accounts), z ktorého peniaze odišli; ponúkajú sa len aktívne účty. Platba sa potom zobrazí, ako záporná suma, v zaúčtovaniach tohto účtu. |
| **Pridať platbu** | Uloží platbu. |

Stav sa zmení na **Uhradená**, keď platby dosiahnu celkovú sumu
faktúry. Prijaté faktúry nemajú upomienky ani poplatky.

!!! tip "Platba z bankového výpisu"
    Namiesto zadania platby tu môžete importovať bankový výpis na
    stránke zaúčtovaní účtu: záporné zaúčtovanie s rovnakou sumou ako
    otvorená prijatá faktúra sa ponúkne ako zhoda a zaznamená sa ako jej
    platba. Pozri
    [Bankové účty a zaúčtovania](bank-accounts.md#possible-matching-invoices).

!!! note "Počítajú sa len zaplatené účty"
    Účtovný prehľad a rozpočet započítavajú výdavok v deň, keď bol
    zaplatený. Prijatá faktúra bez platby sa tam vôbec nezobrazí.

## Súvisiace {#related}

- [Externé kontakty](../external-contacts.md) -- stránka kontaktu
  dodávateľa uvádza prijaté faktúry, ktoré sú s ním prepojené.
- [Žiadosti o nákup](../purchase-requests.md) -- schválenie nákupu sa
  deje tam; výsledný účet sa tu zaznamenáva ručne.
  <!-- TODO(verify): there is no link between a purchase request and an incoming invoice in the code; confirm this is the intended workflow. -->
- [Kategórie, rozpočet a prehľad](bookkeeping.md)
- [Integrácie](../../administration/integrations.md) -- zdieľaný
  cloudový priečinok pre prílohy.

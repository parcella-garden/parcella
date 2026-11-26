# Financie {#finances}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

V module Financie pracuje pokladník. Vytvára ročné faktúry spolku za
každú parcelu a každého člena, sleduje, kto zaplatil, posiela
upomienky a zaznamenáva faktúry, ktoré dostáva samotný spolok. Vedie aj
jednoduchú pokladničnú knihu pre každý bankový účet. Zo všetkého toho
vytvára účtovný prehľad na hotovostnej báze pre daňový úrad a rozpočet
na ďalší rok.

!!! info "Kto to môže používať"
    - Modul je **predvolene vypnutý**. Administrátor ho zapne v
      **Nastavenia spolku** (prepínač sa volá **Financie**), pozri
      [Zapínanie a vypínanie modulov](../../administration/modules.md).
      Pred odoslaním prvých faktúr vyplňte **Finančné nastavenia**
      (bankové údaje, formát čísla faktúry) v
      [Nastaveniach spolku](../../administration/settings.md) -- tlačia
      sa v päte každej faktúry.
    - Členovia výboru a administrátori (a ktokoľvek v skupine s plným
      prístupom) môžu všetko.
    - Všetci ostatní potrebujú [skupinu](../../administration/groups.md),
      ktorá udeľuje oprávnenia pre **Financie**:
        - **čítanie** -- vidieť každú obrazovku, otvárať PDF, exportovať
          súbory CSV;
        - **zápis** -- vytvárať a meniť vyúčtovania, položky, platby,
          upomienky, účty, zaúčtovania, prijaté faktúry, kategórie a
          rozpočet;
        - **mazanie** -- tieto veci znova mazať.
    - Niekoľko akcií okolo príloh prijatých faktúr v cloudovom úložisku
      je len pre členov výboru a administrátorov, pozri
      [Prijaté faktúry](incoming-invoices.md).

    Pozri [Roly, skupiny a oprávnenia](../../getting-started/roles-and-permissions.md).

## Kde ho nájdete {#where-to-find-it}

Keď je modul zapnutý a smiete ho čítať, bočný panel ukazuje skupinu
**Financie** so štyrmi položkami:

| Položka menu | Otvorí |
|---|---|
| **Prehľad** | Finančný prehľad opísaný nižšie. |
| **Vydané faktúry** | Zoznam vyúčtovaní, pozri [Vyúčtovania](invoice-runs.md). |
| **Upomienky** | Zoznam faktúr po splatnosti, pozri [Faktúry, platby a upomienky](invoices.md#reminders). |
| **Prijaté faktúry** | Faktúry, ktoré spolok dostal, pozri [Prijaté faktúry](incoming-invoices.md). |

Všetko ostatné (účty, kategórie, katalóg položiek, zaúčtovania, prehľad,
rozpočet) otvoríte z kariet prehľadu.

## Finančný prehľad {#finances-dashboard}

![Finančný prehľad](../../assets/screenshots/finances/dashboard.png)

Úvodná stránka modulu. Tri čísla hore vám na prvý pohľad ukážu stav
vašich vydaných faktúr. Pod nimi vás jedna karta na každú oblasť modulu
zavedie tam.

| Číslo | Čo ukazuje |
|---|---|
| **Otvorené faktúry** | Koľko vydaných faktúr ešte nie je úplne zaplatených. Čiastočne zaplatené faktúry sa tu počítajú ako otvorené. |
| **Dlžná suma** | Suma, ktorá z týchto faktúr ešte nebola zaplatená (suma faktúry mínus zaznamenané platby). Poplatky za upomienky v tomto čísle nie sú. |
| **Po splatnosti** | Koľko otvorených faktúr je po termíne splatnosti svojho vyúčtovania. Zobrazuje sa červeno, keď je väčšie ako nula. |

| Karta | Popis pod názvom | Otvorí |
|---|---|---|
| **Vydané faktúry** | *n* vyúčtovaní | [Vyúčtovania](invoice-runs.md) |
| **Kategórie** | *n* definovaných kategórií | [Účtovné kategórie](bookkeeping.md#bookkeeping-categories) |
| **Katalóg položiek** | *n* definovaných šablón položiek | [Katalóg položiek](invoice-runs.md#item-catalog) |
| **Účty** | *n* definovaných účtov | [Účty](bank-accounts.md#accounts) |
| **Upomienky** | *n* faktúr po splatnosti | [Upomienky](invoices.md#reminders) |
| **Prijaté faktúry** | *n* prijatých faktúr | [Prijaté faktúry](incoming-invoices.md) |
| **Všetky platby** | Všetky platby z prijatých a vydaných faktúr | [Všetky platby](bookkeeping.md#all-bookings) |
| **Účtovný prehľad** | Prehľad na hotovostnej báze pre daňový úrad | [Účtovný prehľad](bookkeeping.md#accounting-statement) |
| **Rozpočet** | Plánované príjmy a výdavky podľa kategórií na budúci rok, vedľa skutočnosti minulých rokov | [Rozpočet](bookkeeping.md#budget-plan) |

Väčšina podstránok má v hornom pruhu tlačidlo **Späť na Financie**,
ktoré vás sem vráti.

<!-- TODO(verify): finances/coming_soon.html ("This feature is coming soon.") exists, but no route renders it any more, so it is not documented as a screen. -->

## Ako peniaze prechádzajú rokom {#how-the-money-flows-through-a-year}

Typický rok spolku v Parcelle vyzerá takto:

1. **Raz nastaviť.** Vytvorte si [účtovné kategórie](bookkeeping.md#bookkeeping-categories)
   (alebo importujte svoju účtovú osnovu), [bankové a pokladničné účty](bank-accounts.md#accounts)
   a opakujúce sa riadky faktúr v [katalógu položiek](invoice-runs.md#item-catalog)
   (nájom za m², členský príspevok, voda, elektrina, poistenie ...).
2. **Pripraviť ročné faktúry.** Vytvorte [vyúčtovanie](invoice-runs.md)
   za rok, pridajte položky z katalógu, upravte ceny a skontrolujte
   [náhľad](invoice-runs.md#preview-invoices). Odpočty meradiel,
   poistenie a pracovné hodiny za daný rok by v tejto chvíli mali byť
   úplné -- položky podľa spotreby ich čítajú priebežne.
3. **Dokončiť a odoslať.** Dokončenie pridelí trvalé čísla faktúr.
   Potom faktúry pošlite e-mailom, nahrajte ich do cloudových priečinkov
   parciel a stiahnite balík na tlač pre všetkých, ktorí dostávajú papier.
4. **Zaznamenať platby.** Platby zadajte ručne v zozname faktúr
   vyúčtovania alebo importujte bankový výpis na [stránke zaúčtovaní
   účtu](bank-accounts.md#bookings-of-an-account) a každý riadok
   priraďte k faktúre, ktorú platí.
5. **Upomínať neplatičov.** Stránka [Upomienky](invoices.md#reminders)
   uvádza každú faktúru po splatnosti; prvú, druhú, tretiu upomienku
   pošlite z faktúry, s poplatkom alebo bez neho.
6. **Zaznamenať vlastné faktúry spolku** ako [prijaté faktúry](incoming-invoices.md)
   a označiť ich ako zaplatené, keď peniaze odídu.
7. **Uzavrieť rok.** [Účtovný prehľad](bookkeeping.md#accounting-statement)
   ukazuje príjmy a výdavky podľa kategórií, počítané v deň, keď sa
   peniaze naozaj pohli. Použite ho pre daňový úrad a výročnú členskú
   schôdzu a ďalší rok naplánujte v [rozpočte](bookkeeping.md#budget-plan).

Návod [Ročné vyúčtovanie](../../guides/annual-invoicing.md) prechádza
krokmi 2 až 5 v poradí.

## Kapitoly {#chapters}

- [Vyúčtovania](invoice-runs.md) -- ročná dávka faktúr, jej položky a
  ako sa každá suma počíta, katalóg položiek, náhľad a dokončenie.
- [Faktúry, platby a upomienky](invoices.md) -- každá faktúra zo
  všetkých vyúčtovaní, doručenie, platby a postup upomínania.
- [Bankové účty a zaúčtovania](bank-accounts.md) -- vaše účty, ich
  zaúčtovania a import bankového výpisu s priraďovaním faktúr.
- [Prijaté faktúry](incoming-invoices.md) -- faktúry, ktoré spolok
  dostal, a ich platby.
- [Kategórie, rozpočet a prehľad](bookkeeping.md) -- účtovné kategórie,
  zoznam zaúčtovaní celého spolku, účtovný prehľad a rozpočet.

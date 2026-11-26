# Ročné vyúčtovanie {#running-the-annual-invoices}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Raz za rok spolok vyfakturuje každú parcelu: nájom, vodu, elektrinu,
poistenie, chýbajúce pracovné hodiny, možno členský príspevok alebo
jednorazovú [všeobecnú dávku](../glossary.md#general-levy). V Parcelle
je to [vyúčtovanie](../glossary.md#invoice-run): raz definujete riadky,
skontrolujete náhľad každej jednej faktúry, dokončíte ho, aby sa
pridelili čísla faktúr, a potom ich rozošlete -- e-mailom, na papieri
alebo do cloudového priečinka každej parcely. Potom zaznamenávate
platby a posielate [upomienky](../glossary.md#dunning).

!!! info "Kto to môže robiť"
    Všetko tu potrebuje oprávnenie **zápis** pre **Financie**. Modul
    **Financie** je v novej inštalácii **vypnutý**; zapnite ho v
    **Administrácia → Nastavenia → Funkčné oblasti** (pozri
    [Zapínanie a vypínanie modulov](../administration/modules.md)).

!!! warning "Dokončenie sa nedá vrátiť späť"
    Kým vyúčtovanie nedokončíte, nič sa neukladá ako faktúra a nič sa
    neodosiela -- položky meňte, koľkokrát chcete. Dokončenie pridelí
    trvalé čísla faktúr a vyúčtovanie uzamkne. Najprv si stiahnite zálohu
    (**Administrácia → Systém → Stiahnuť zálohu**).

## 1. Skontrolujte finančné nastavenia (raz) {#1-check-the-finance-settings-once}

1. Otvorte **Administrácia → Nastavenia** a nájdite **Finančné
   nastavenia**.
2. Vyplňte bankové údaje spolku: **Názov banky**, **IBAN**, **BIC**,
   **Majiteľ účtu**. Zobrazujú sa v päte každej faktúry.
3. Skontrolujte **Formát čísla faktúry**. Predvolene je to rok a
   priebežné číslo; môžete použiť vlastný, napríklad `R-{year}-{number}`.
   `{number}` je povinné.
4. Nechajte **Ďalšie číslo faktúry (prepísať)** prázdne, pokiaľ prvé
   vyúčtovanie v Parcelle nemusí pokračovať v číslovaní, ktoré ste
   používali predtým. Použije sa raz a potom sa vymaže.
5. Ak chcete faktúry posielať e-mailom, uistite sa, že je nastavený
   **E-mail (SMTP)**.
6. Kliknite na **Uložiť nastavenia**.

## 2. Pripravte katalóg položiek (raz, potom používajte znova) {#2-prepare-the-item-catalog-once-then-reuse}

Katalóg položiek uchováva riadky, ktoré fakturujete každý rok, aby ste
ich nemuseli pre každé vyúčtovanie definovať znova.

1. Otvorte **Financie → Prehľad** a kliknite na **Katalóg položiek**.
2. V **Nová šablóna položky** vyplňte **Poradie** (pozícia na faktúre),
   **Názov**, **Popis**, **Spôsob výpočtu**, **Jednotková cena** a
   voliteľne **Kategória**.
3. Vyberte, koho sa týka (pozri nižšie), a kliknite na tlačidlo **+**.

| Spôsob výpočtu | Čo fakturuje |
|---|---|
| **Pevná suma za parcelu** | Jednotkovú cenu raz za parcelu -- napr. nájom. |
| **Pevná suma za osobu** | Jednotkovú cenu raz za *člena* -- napr. členský príspevok, aj pre členov bez parcely. |
| **Za prenajatý m²** | Jednotková cena × rozloha parcely. |
| **Podiel na nájme spoločnej plochy** | Spoločná plocha (Rozloha B), rovnomerne rozdelená medzi fakturované parcely, × jednotková cena. |
| **Verejné dávky (vlastná plocha + podiel na spoločnej ploche)** | Vlastná rozloha parcely plus jej podiel na spoločnej ploche, × jednotková cena. |
| **Všeobecná dávka (rozdelená rovnomerne medzi všetky parcely)** | Jednotková cena je *celková* suma, ktorá sa rovnomerne rozdelí medzi všetky fakturované parcely. |
| **Spotreba vody (z modúlu)** | Spotreba vody parcely × cena vody za rok. |
| **Spotreba elektriny (z modúlu)** | Spotreba elektriny parcely × cena elektriny za rok. |
| **Náklady na poistenie (z modúlu)** | Poistenie parcely, jeden riadok na druh poistenia. |
| **Nedoplatok pracovných hodín (z modulu)** | Chýbajúce [povinné hodiny](../glossary.md#mandatory-hours) × hodinová sadzba. |

**Koho sa položka týka.** Položky podľa parciel majú **Platí pre každú
parcelu**; odškrtnite to, ak chcete vybrať jednotlivé **Parcely**.
**Pevná suma za osobu** má namiesto toho **Platí pre každého člena** a
výber **Členovia**. Štyri položky „z modulu“ si parcely vyberajú samy --
namiesto výberu sa zobrazí **Automaticky (...)** -- a ich jednotková
cena je **Počíta sa automaticky**.

Viac: [Vyúčtovania](../modules/finances/invoice-runs.md).

## 3. Skontrolujte čísla, ktoré používajú automatické položky {#3-check-the-numbers-the-automatic-items-use}

Položky „z modulu“ berú svoje čísla z iných modulov. Skontrolujte ich
za fakturovaný rok **pred** dokončením.

**Voda a elektrina**

1. Otvorte **Voda → Konfigurácia** a skontrolujte, či pre rok existuje
   cena (**Cena za m³**) (v **História cien**). Ak nie, zadajte **Rok** a
   cenu v **Nová/aktualizovaná cena** a kliknite na **Uložiť**. To isté
   urobte v **Elektrina → Konfigurácia**.
2. Otvorte **Voda → Prehľad**. Ak hovorí, že niektoré meracie body ešte
   nemajú odpočet za rok, najprv ich zozbierajte -- pozri [Odpočty
   meradiel](meter-readings.md). Parcela bez odpočtu za rok nedostane
   vôbec žiadny riadok vody.
3. Otvorte **Voda → Hodnotenie** za rok a hľadajte parcely so
   **žiadny odpočet** alebo s nepravdepodobnou spotrebou.

**Pracovné hodiny**

1. Otvorte **Pracovné sedenia → Sedenia a prehľad** a skontrolujte
   **Konfigurácia hodín** roka: požadované hodiny a **Hodinová sadzba**.
2. Otvorte **Pracovné sedenia → Ročné hodnotenie** za rok. Skontrolujte
   stĺpce **Otvorené** a **Dlh** -- to sa bude fakturovať. Chýba účasť,
   sponzorstvá alebo oslobodenia? Opravte ich teraz (pozri
   [Organizácia pracovnej zmeny](work-session.md)).

**Poistenie**

1. Otvorte **Poistenie → Konfigurácia** a **Poistenie → Parcely** a
   skontrolujte ceny roka a poistenie každej parcely.

!!! tip "Kto dostane faktúru"
    Faktúra parcely ide súčasným nájomcom parcely označeným **Použiť ako
    fakturačnú adresu**. Parcely bez takého nájomcu faktúru nedostanú.
    Skontrolujte to pred dokončením na stránkach parciel -- najmä po
    odovzdaní.

## 4. Vytvorte vyúčtovanie {#4-create-the-invoice-run}

1. Otvorte **Financie → Vydané faktúry** (stránka sa volá **Ročné
   faktúry**).
2. Kliknite na **Nové vyúčtovanie**.
3. Zadajte fakturovaný **Rok**, **Predmet** (napr. „Ročná faktúra
   2026“), **Dátum vystavenia** a **Dátum splatnosti**.
4. Voliteľne napíšte **Text pätičky**. Môže obsahovať
   `{invoice_number}`, `{parcel_number}`, `{invoice_address}` a
   `{due_date}`, ktoré sa vyplnia pre každú faktúru.
5. Kliknite na **Vytvoriť**.

Vyúčtovanie je **Koncept**. Otvoríte ho tlačidlom **Otvoriť**.

## 5. Pridajte riadky {#5-add-the-line-items}

1. Na stránke vyúčtovania, v **Pridať z katalógu položiek**, zaškrtnite
   položky katalógu na tento rok a kliknite na **Pridať vybrané
   položky**.
2. Pre všetko, čo sa fakturuje len tento rok, vyplňte dole **Pridať
   položku**, rovnako ako v katalógu.
3. Skontrolujte tabuľku **Definície položiek**: poradie, ceny, koho sa
   každá položka týka. Kým je vyúčtovanie koncept, položky môžete ešte
   upravovať alebo mazať.

## 6. Náhľad {#6-preview}

1. Kliknite na **Náhľad** hore na stránke vyúčtovania.
2. Stránka povie, koľko faktúr by sa vytvorilo, a uvedie ich v
   **Vypočítané faktúry**, s príjemcom a medzisúčtom.
3. Niekoľko otvorte tlačidlom **PDF** a skontrolujte ich: adresu,
   riadky, sumy, pätičku.
4. Ak chcete niečo opraviť, prejdite **Späť na vyúčtovanie**, zmeňte
   položky a znova otvorte náhľad. Zatiaľ sa nič neuložilo ani
   neodoslalo.

Ak stránka hovorí *„Nebudú vytvorené žiadne faktúry“*, skontrolujte
rozsah parciel v položkách a príznak **Použiť ako fakturačnú adresu** pri
nájomcoch.

## 7. Dokončite {#7-finalize}

1. Na stránke náhľadu kliknite na **Dokončiť a prideliť čísla faktúr** a
   potvrďte.
2. Parcella vytvorí faktúry s trvalými číslami. Stránka vyúčtovania teraz
   hovorí, že je dokončené, a uvádza **Faktúry**.

Mená a adresy príjemcov sa na každú faktúru uložia v stave v tejto
chvíli. Neskoršie zmeny adresy dokončené faktúry neprepíšu.

## 8. Rozošlite faktúry {#8-send-the-invoices}

1. Na stránke dokončeného vyúčtovania nájdite kartu **Doručenie**.
2. Kliknite na **Odoslať e-maily a nahrať do cloudu**.
    - Faktúry sa pošlú e-mailom (s priloženým PDF) príjemcom faktúr,
      ktorí majú **Môže dostávať informácie e-mailom** a e-mailovú
      adresu.
    - Ak má parcela priečinok dokumentov v cloudovom úložisku, faktúra sa
      nahrá aj tam.
    - Opätovné kliknutie pošle len to, čo ešte nebolo odoslané.
3. Kliknite na **Stiahnuť tlačový balík**. Obsahuje list pre každého
   nájomcu, ktorý nedostáva faktúry e-mailom, ako jedno PDF na tlač a
   odoslanie poštou: jeden list na adresu, s menami ľudí tam bez
   e-mailu. To platí aj pre niekoho, koho spolubývajúci dostal e-mail.
   Tí sa potom označia ako zahrnutí v tlačovom balíku.

Stĺpec **Doručenie** ukazuje pri každej faktúre, či bola **Odoslané
e-mailom**, **Zahrnuté v tlačovom balíku** alebo **Nahrané do cloudového
úložiska**. Ak chcete jednu faktúru poslať znova, otvorte ju a kliknite
na **Znova odoslať e-mail**.

Viac: [Faktúry, platby a upomienky](../modules/finances/invoices.md).

## 9. Zaznamenajte platby {#9-record-payments}

**Ručne**

1. Otvorte vyúčtovanie (alebo **Všetky faktúry** v **Ročné faktúry**,
   ak chcete hľadať vo všetkých vyúčtovaniach podľa čísla faktúry,
   príjemcu alebo sumy).
2. Kliknite na **Platba** v riadku faktúry.
3. Zadajte **Suma**, **Uhradené dňa**, voliteľne **Poznámka** a
   **Účet**, na ktorý peniaze prišli, a kliknite na **Pridať platbu**.

Čiastočné platby sú v poriadku; stav sa sám zmení z **Otvorená** na
**Čiastočne uhradená** a na **Uhradená**.

**Z bankového výpisu**

1. Raz: otvorte **Financie → Prehľad → Účty** a pridajte svoj bankový
   účet v **Nový účet**.
2. Kliknite na **Zápisy** vedľa účtu, potom na **Import CSV**.
3. Nahrajte výpis exportovaný z internetového bankovníctva. Na
   **Mapovanie stĺpcov CSV** priraďte aspoň **Dátum** a **Suma**;
   **Popis**, **Odosielateľ / príjemca** a **IBAN** pomáhajú pri
   priraďovaní.
4. Na **Priradiť riadky k faktúram** Parcella ku každej prichádzajúcej
   platbe navrhne otvorené faktúry s rovnakou sumou. Vyberte tú
   správnu, aby sa zaznamenala ako platba tejto faktúry, alebo vyberte
   **Zaznamenať ako všeobecnú platbu**.
5. Kliknutím na **Import CSV** na konci stránky vytvoríte zápisy a
   platby.

Viac: [Bankové účty a zaúčtovania](../modules/finances/bank-accounts.md).

## 10. Rozošlite upomienky {#10-send-reminders}

1. Po dátume splatnosti otvorte **Financie → Upomienky**. **Faktúry po
   splatnosti** uvádza každú nezaplatenú faktúru po splatnosti, s tým,
   ako dlho je po splatnosti a koľko upomienok bolo odoslaných.
2. Kliknite na **Otvoriť** vedľa faktúry.
3. Voliteľne zadajte **Poplatok (voliteľné)** a **Správa (voliteľné)**.
4. Kliknite na **Odoslať upomienku**.

Parcella vytvorí ďalšiu upomienku ako PDF (**Upomienka č. 1**, **č.
2**, …), pripočíta poplatok k dlžnej sume a pošle ju e-mailom, ak člen
súhlasil s e-mailom; inak sa označí **Na tlač/poštové odoslanie**, aby
ste ju vytlačili a poslali. Pevné stupne upomínania neexistujú -- vy
rozhodujete, kedy poslať ďalšiu.

## Súvisiace {#related}

- [Financie](../modules/finances/index.md)
- [Vyúčtovania](../modules/finances/invoice-runs.md)
- [Faktúry, platby a upomienky](../modules/finances/invoices.md)
- [Bankové účty a zaúčtovania](../modules/finances/bank-accounts.md)
- [Kategórie, rozpočet a prehľad](../modules/finances/bookkeeping.md)
- [Voda a elektrina](../modules/metering.md)
- [Pracovné hodiny](../modules/work-hours.md)
- [Poistenie](../modules/insurance.md)
- [Odpočty meradiel](meter-readings.md)

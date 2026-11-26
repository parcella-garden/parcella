# Bankové účty a zaúčtovania {#bank-accounts-and-bookings}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Tu evidujete skutočné účty spolku -- bežné účty, sporiaci účet,
pokladňu -- a vidíte všetko, čo bolo na každý z nich zaúčtované. Zápisy
môžete pridávať ručne alebo importovať bankový výpis ako súbor CSV.
Pritom vám Parcella ponúkne priradiť každý zápis k otvorenej faktúre,
takže prichádzajúci prevod sa hneď zaznamená ako platba člena.

!!! info "Kto to môže používať"
    Súčasť modulu **Financie** (predvolene vypnutý). Prezeranie účtov a
    zápisov a export CSV potrebuje oprávnenie na čítanie pre
    **Financie**. Vytváranie alebo zmena účtov, pridávanie zápisov a
    import potrebujú oprávnenie na zápis; mazanie účtov alebo zápisov
    potrebuje oprávnenie na mazanie. Členovia výboru a administrátori
    môžu všetko. Pozri [Financie](index.md).

!!! note "Nie je to úplná účtovná kniha"
    Zoznam zápisov účtu je záznam pohybov peňazí, nie podvojné
    účtovníctvo. Neexistuje počiatočný ani priebežný zostatok. Zápisy,
    ktoré nie sú viazané na faktúru (bankový poplatok, vrátenie), nemajú
    kategóriu, takže sa nezobrazujú v
    [účtovnom prehľade](bookkeeping.md#accounting-statement).

## Účty {#accounts}

![Účty](../../assets/screenshots/finances/account-list.png)

Otvoríte ich kartou **Účty** na finančnom prehľade. **Späť na
Financie** v hornom pruhu vás vráti späť.

### Nový účet {#new-account}

Zobrazí sa s oprávnením na zápis.

| Pole | Čo robí |
|---|---|
| **Názov** | Povinné, napr. „Bežný účet SLSP“ alebo „Pokladňa“. Uloženie bez názvu ukáže „Meno je povinné“. |
| **Typ** | **Banka** alebo **Hotovosť**. |
| **Číslo účtu/IBAN** | Voliteľné, pre vašu orientáciu. |
| **Poznámka** | Voliteľné. |
| **Aktívny** | Predvolene zapnuté. Pri zaznamenávaní platby sa ponúkajú len aktívne účty. Vypnite to pri účte, ktorý ste zrušili: jeho história zostane, ale už sa neponúka. |
| **Pridať účet** | Uloží účet. Uvidíte „Hotovo.“. |

### Zoznam účtov {#accounts-list}

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Názov**, **Typ**, **Číslo účtu/IBAN**, **Poznámka**, **Aktívny** | Údaje účtu. S oprávnením na zápis sa dajú upravovať priamo v riadku; uložíte ich kliknutím na ikonu fajky. |
| **Zaznamenané platby** | Súčet všetkých platieb vydaných faktúr zaznamenaných na tento účet. Platby prijatých faktúr a iné zápisy nie sú zahrnuté. |
| Ikona zápisov | Otvorí [zápisy](#bookings-of-an-account) účtu. |
| Ikona fajky | Uloží riadok. Potrebuje oprávnenie na zápis. |
| Ikona koša | Zmaže účet po otázke „Zmazať tento účet? Nemá žiadne zaúčtovania.“ Potrebuje oprávnenie na mazanie. Pri účte so zápismi je sivá (pozri nižšie). |

Ak ešte nie sú žiadne účty: „Zatiaľ žiadne účty -- pridajte jeden
vyššie.“

!!! note "Účty so zápismi sa nedajú zmazať"
    Zmazať sa dá len účet bez akýchkoľvek zápisov -- bez ručne zadaného
    alebo importovaného zápisu, bez zaznamenanej platby faktúry. Pri
    každom inom účte je kôš sivý („Má zaúčtovania: namiesto toho zrušte
    začiarknutie „Aktívny“.“). Vypnutie **Aktívny** skryje účet z
    formulárov platieb a zachová všetky jeho zápisy.

## Zápisy účtu {#bookings-of-an-account}

![Zápisy účtu](../../assets/screenshots/finances/account-bookings.png)

Otvoríte ich ikonou zápisov v zozname účtov. Názov je „Zápisy —
*názov účtu*“. Ukazuje všetko zaúčtované na tomto účte, najnovšie
navrchu:

- platby vydaných faktúr zaznamenané s týmto účtom (kladné sumy),
- platby [prijatých faktúr](incoming-invoices.md) zaznamenané s týmto
  účtom (záporné sumy),
- iné zápisy, ktoré ste zadali ručne alebo importovali (kladné alebo
  záporné, ako boli zadané).

Zobrazí sa prvých 50 zápisov; ďalšie sa načítavajú automaticky pri
posúvaní nadol. Tlačidlo **Späť na Financie** v hornom pruhu vás vráti
do zoznamu účtov (napriek svojmu názvu). Na obrazovkách importu nižšie
vás to isté tlačidlo vráti na zápisy účtu bez importovania čohokoľvek.

### Filter a akcie {#filter-and-actions}

| Pole / tlačidlo | Čo robí |
|---|---|
| **Hľadať** | Nájde zápisy, ktorých referencia, popis alebo odosielateľ/príjemca obsahuje tento text. |
| **Od** / **Do** | Len zápisy v tento deň alebo medzi týmito dátumami. |
| **Suma od** / **Suma do** | Len zápisy so sumou v tomto rozsahu. Pamätajte, že odchádzajúce peniaze sú záporné: ak chcete nájsť výdavky od 100 vyššie, nastavte **Suma do** na `-100`. |
| **Priradenie** | **Všetky**, **Priradené k faktúre** (platby faktúr) alebo **Nepriradené** (iné zápisy). Šikovné na nájdenie bankových riadkov, ktoré treba ešte skontrolovať. |
| **Filtrovať** / **Zrušiť filter** | Použije filter / zruší ho. |
| **Export CSV** | Stiahne zápisy zodpovedajúce aktuálnemu filtru ako súbor CSV (oddelený bodkočiarkou: dátum, suma, referencia, popis, protistrana). Stačí oprávnenie na čítanie. |
| **Import CSV** | Otvorí dialóg importu, pozri [Import bankového výpisu](#importing-a-bank-statement). Potrebuje oprávnenie na zápis. |
| **Pridať zápis** | Otvorí dialóg pre ručný zápis, pozri [Ručné pridanie zápisu](#adding-a-booking-by-hand). Potrebuje oprávnenie na zápis. |

### Tabuľka zápisov {#bookings-table}

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Dátum** | Dátum zápisu. |
| **Suma** | Suma; odchádzajúce peniaze sa zobrazujú červene so znamienkom mínus. |
| **Referencia** | Pri platbe faktúry číslo faktúry ako odkaz na faktúru (alebo prijatú faktúru). Pri iných zápisoch prázdne. |
| **Popis** | Poznámka k platbe alebo popis zápisu. |
| **Odosielateľ / príjemca** | Kto platil alebo komu sa platilo: príjemca faktúry, odosielateľ prijatej faktúry alebo protistrana, ktorú ste zadali. |
| Ikona koša | Zmaže zápis po otázke „Naozaj vymazať tento zápis?“. Len pri ručne zadaných alebo importovaných zápisoch a len s oprávnením na mazanie. Platby faktúr sa tu zmazať nedajú -- zmažte ich namiesto toho pri faktúre. |

Ak účet nemá žiadne zápisy: „Zatiaľ žiadne zápisy.“

Po importe alebo priradení vám zelené hlásenie hore povie, čo sa stalo,
napr. „Importovaných 12, preskočených 1.“, „3 platieb priradených k
existujúcej faktúre.“, „Z importu bolo doplnené IBAN pre 2 členov.“
alebo po jednom zápise „Zaznamenané ako platba k priradenej faktúre.“

## Ručné pridanie zápisu {#adding-a-booking-by-hand}

Kliknite na **Pridať zápis**. Dialóg sa pýta na:

| Pole | Čo robí |
|---|---|
| **Dátum** | Povinné, predvyplnené dnešným dňom. |
| **Suma** | Povinné. Kladná pre prichádzajúce peniaze, záporná pre odchádzajúce, napr. `-12,50`. |
| **Popis** | Voliteľné. |
| **Odosielateľ / príjemca** | Voliteľné. Používa sa aj na návrh zodpovedajúcej faktúry. |
| **Pridať zápis** | Pokračuje na krok priradenia. |

### Možné zodpovedajúce faktúry {#possible-matching-invoices}

<!-- No screenshot: this page is only reached by submitting the form above. -->

Skôr než sa čokoľvek uloží, Parcella hľadá otvorené faktúry s rovnakou
sumou: pri kladnej sume vydané faktúry, ktoré majú presne toľko ešte
na úhradu; pri zápornej sume prijaté faktúry, z ktorých je toľko ešte
nezaplatené. Ukáže **Dátum**, **Suma** a **Odosielateľ / príjemca**
zápisu a potom možnosti:

| Možnosť | Čo sa stane |
|---|---|
| **Zaznamenať ako všeobecnú platbu** | Uloží bežný zápis na účte, neviazaný na žiadnu faktúru. |
| Jeden riadok na každú zodpovedajúcu faktúru | Ukazuje faktúru (číslo a príjemcu, alebo odosielateľa a číslo) a „zostáva: *suma*“. Zelený odznak „meno zodpovedá“ sa zobrazí, keď zadaný odosielateľ/príjemca má spoločné meno s príjemcom alebo odosielateľom faktúry. Jeho výberom sa zápis zaznamená ako **platba tejto faktúry**, s týmto účtom, dátumom a popisom ako poznámkou. |
| **Pridať zápis** | Uloží váš výber. |

Navrhne sa najviac päť faktúr, najprv tie so zhodným menom. Ak má
zhodné meno práve jeden návrh, je predvybraný; inak je predvybrané
**Zaznamenať ako všeobecnú platbu**. Ak nezodpovedá žiadna faktúra:
„Žiadna otvorená faktúra nezodpovedá tejto sume.“

!!! tip
    Priraďovanie porovnáva len sumu, ktorá ešte zostáva na úhradu, na
    cent presne. Faktúra s poplatkom za upomienku je splatná vrátane
    poplatku a čiastočne zaplatená faktúra len vo výške zvyšku.

## Import bankového výpisu {#importing-a-bank-statement}

Väčšina bánk umožňuje stiahnuť výpis z účtu ako súbor CSV. Funguje
akékoľvek usporiadanie stĺpcov. Import má tri kroky.

**1. Nahrať.** Kliknite na **Import CSV**, vyberte súbor a kliknite na
**Import CSV**. „Funguje akékoľvek CSV -- nahrajte ho a na ďalšej
obrazovke priraďte stĺpce k poliam Parcella.“ Rozpoznajú sa súbory
oddelené bodkočiarkou aj čiarkou, ako aj UTF-8 a staršie kódovania
Windows. Prázdny súbor sa odmietne hlásením „Tento súbor CSV sa zdá byť
prázdny.“

**2. Mapovanie stĺpcov CSV.** <!-- No screenshot: reached only by uploading a file. -->
„Pre každý stĺpec vyberte, ktorému poľu Parcella zodpovedá (alebo ho
ponechajte ignorovaný). Dátum a Suma sú povinné.“ Stránka ukazuje
nadpisy stĺpcov vášho súboru, každý s rozbaľovacím zoznamom, a prvých
päť riadkov ako ukážku.

| Pole | Význam |
|---|---|
| **— Ignorovať —** | Stĺpec sa nepoužije. |
| **Dátum** | Povinné. Dátum zápisu. Prijímané formáty: `2026-03-31`, `31.03.2026` a `31.03.26`. |
| **Suma** | Povinné. Suma so znamienkom, s desatinnou čiarkou alebo bodkou (`-12,50` alebo `-12.50`). Oddeľovače tisícov sú v poriadku, tak ako ich exportuje vaša banka: `1.234,56`, `1,234.56` alebo `1 234,56`. |
| **Popis** | Voliteľné, napr. účel platby. |
| **Odosielateľ / príjemca** | Voliteľné. Používa sa na priraďovanie a zobrazuje sa v zozname. |
| **IBAN** | Voliteľné. Pozri tip nižšie. |

Bežné nemecké a anglické nadpisy („Buchungsdatum“, „Betrag“,
„Verwendungszweck“, „Auftraggeber“, „IBAN“ ...) sú predvybrané;
napriek tomu ich skontrolujte. Kliknutím na **Import CSV** pokračujete.
Ak nie je priradený **Dátum** alebo **Suma**, vrátite sa s hlásením
„Priraďte prosím aspoň jeden stĺpec k Dátumu a Sume.“

**3. Priradiť riadky k faktúram.** <!-- No screenshot: reached only through the import. -->
„Pre každý riadok vyberte zodpovedajúcu otvorenú faktúru na
zaznamenanie skutočnej platby, alebo ho ponechajte ako všeobecnú
platbu.“ Každý riadok ukazuje **Dátum**, **Suma**, **Odosielateľ /
príjemca** a rozbaľovací zoznam **Zhoda** s **Neimportovať**,
**Zaznamenať ako všeobecnú platbu** a navrhnutými faktúrami (zostávajúca
suma v zátvorkách, ✓ pri zhode mena). Predvýber funguje ako pri
jednotlivom zápise. Riadky, ktorých dátum alebo sumu nebolo možné
prečítať, ukazujú „Neplatný riadok — bude preskočený“. Riadok, ktorý už
na tomto účte je, dostane odznak **Už importované** a je prednastavený
na **Neimportovať**. Kliknutím na **Import CSV** všetko uložíte.

Čo sa uloží:

- každý riadok s vybranou faktúrou sa stane platbou tejto faktúry na
  tomto účte -- pokiaľ medzitým nebola faktúra zaplatená v plnej
  výške: potom sa nič nezaznamená a hlásenie o výsledku to uvedie;
- každý iný platný riadok sa stane bežným zápisom;
- riadky nastavené na **Neimportovať** a neplatné riadky sa preskočia
  a započítajú do hlásenia o výsledku.

!!! tip "Doplnenie IBAN členov"
    Ak priradíte **Odosielateľ / príjemca** aj **IBAN**, Parcella hľadá
    člena, ktorého meno je presne meno odosielateľa (meno priezvisko
    alebo priezvisko meno, bez ohľadu na veľkosť písmen). Ak tento člen
    ešte nemá uložený IBAN, doplní sa IBAN z výpisu. Existujúce IBAN sa
    nikdy neprepisujú.

!!! tip "Dvojitý import toho istého výpisu"
    Riadok sa považuje za už importovaný, keď tento účet už má zápis s
    rovnakým dátumom, sumou a popisom (počíta sa aj platba zaznamenaná
    k faktúre). Prekrývajúce sa exporty sú teda bezpečné: pridajú sa
    len nové riadky. Parcella počíta, nielen porovnáva -- ak súbor
    obsahuje ten istý nákup kávy v jeden deň dvakrát a účet ho má raz,
    jeden z nich je nový.

    Riadok, ktorý už existuje, sa importuje len vtedy, ak jeho
    **Neimportovať** zmeníte na niečo iné. Dvojité kliknutie na **Import
    CSV** alebo opätovné odoslanie stránky tlačidlom späť nepridá nič.

## Súvisiace {#related}

- [Faktúry, platby a upomienky](invoices.md)
- [Prijaté faktúry](incoming-invoices.md)
- [Všetky platby](bookkeeping.md#all-bookings) -- každá platba faktúry
  zo všetkých účtov.
- [Členovia](../members.md) -- kde je uložený IBAN.

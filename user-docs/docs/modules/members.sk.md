# Členovia {#members}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Zoznam členov je srdcom Parcelly: všetci, ktorí patria do vášho spolku,
s adresou, bankovým spojením, kontaktnými údajmi a parcelami, ktoré
majú. Faktúry, pracovné hodiny, rozosielanie, zoznam narodenín aj
prezenčná listina zo schôdze čítajú odtiaľto.

!!! info "Kto to môže používať"
    Členovia sú súčasťou jadra a sú vždy zapnutí. Nedajú sa vypnúť.

    - **Každý, kto sa môže prihlásiť**, si môže pozrieť zoznam členov,
      stránky členov, zoznam štítkov, export CSV a prezenčnú listinu.
    - **Pridávanie a úprava** členov, telefónnych čísel, e-mailových
      adries, štítkov a priradení parciel potrebuje oprávnenie *zápis*
      pre **Členovia a parcely**.
    - **Mazanie** člena, telefónneho čísla, e-mailovej adresy alebo
      štítku potrebuje oprávnenie *mazanie* pre **Členovia a parcely**.

    Členovia výboru a administrátori majú všetky tieto oprávnenia.
    Ktokoľvek iný dostane zápis alebo mazanie cez skupinu (pozri
    [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md)).

## Zoznam členov {#member-list}

![Zoznam členov](../assets/screenshots/members/list.png)

Otvorte **Členovia** v hlavnom menu. Zoznam ukazuje aktívnych členov,
zoradených podľa priezviska a potom mena. Päta ukazuje, koľko členov je
práve v zozname.

### Tlačidlá hore {#buttons-at-the-top}

| Tlačidlo | Čo robí |
|---|---|
| **CSV import** | Otvorí dialóg importu súboru CSV (pozri [Import členov zo súboru CSV](#importing-members-from-a-csv-file)). Potrebuje oprávnenie na zápis. |
| **CSV export** | Stiahne *práve zobrazených* členov ako súbor CSV. Uplatní sa vyhľadávanie, zaškrtávacie políčka aj filter štítkov (pozri [Export CSV](#csv-export)). |
| **Napísať týmto členom (*N*)** | Začne nový oznam presne členom vo vyfiltrovanom zozname. Zobrazí sa, až keď ste hľadali alebo filtrovali, kým je zapnutý modul **Oznamy**, a len členom výboru a administrátorom. Ak chcete napísať všetkým, začnite oznam namiesto toho v časti [Oznamy](announcements.md). |
| **Spravovať štítky** | Otvorí stránku [Štítky členov](#member-tags). |
| **Prezenčná listina** | Otvorí [Prezenčnú listinu zo schôdze](#meeting-sign-in-sheet). |
| **Nový člen** | Otvorí prázdny [formulár člena](#new-member-and-edit-member). Potrebuje oprávnenie na zápis. |

### Vyhľadávanie a filtre {#search-and-filters}

| Pole / tlačidlo | Čo robí |
|---|---|
| Pole vyhľadávania | Nájde členov podľa mena alebo priezviska, ulice, PSČ, mesta, IBAN, poznámok, e-mailovej adresy, telefónneho čísla a čísla parcely. Číslo parcely nájde len *súčasných* nájomcov parcely -- pokiaľ nie je zaškrtnuté **Zobraziť iba neaktívnych**, vtedy nájde aj bývalých nájomcov. Keďže sa prehľadávajú aj poznámky, číslo tiketu, ktoré ste si pri členovi poznačili, tohto člena nájde. |
| **Zobraziť iba neaktívnych** | Ukáže *len* členov, ktorí nie sú aktívni: ich dátum **Členom do** uplynul alebo ich dátum **Členom od** je ešte v budúcnosti. Použite to na vyhľadanie bývalých alebo zosnulých členov. |
| **Iba potvrdení aktívni** | Ukáže len aktívnych členov, ktorí majú dátum **Členom od**. Členovia bez dátumu začiatku (zobrazení ako *čakajúci*) sú vynechaní. |
| **Iba s e-mailovými informáciami = áno** | Ukáže len členov, ktorí zaškrtli **Môže dostávať informácie e-mailom**. |
| Rozbaľovací zoznam štítkov (**Všetky štítky**) | Ukáže len členov s vybraným štítkom. Zoznam sa objaví, keď existuje aspoň jeden štítok. Filtrovať môžete naraz podľa jedného štítku. |
| **Hľadať** | Použije hľadaný text. Zaškrtávacie políčka a zoznam štítkov sa uplatnia hneď po zmene. |
| **Resetovať** | Zruší všetky filtre. Zobrazí sa len, kým je filter aktívny. |

Keď je zaškrtnuté **Zobraziť iba neaktívnych**, má prednosť pred **Iba
potvrdení aktívni**. Modré upozornenie nad tabuľkou vám pripomína,
ktorý z týchto dvoch filtrov je zapnutý.

Váš filter zostáva s vami: ak otvoríte člena z vyfiltrovaného zoznamu,
tlačidlá **Predchádzajúci** a **Ďalší** na stránke člena prechádzajú tým
istým vyfiltrovaným zoznamom a **Späť** vás doň vráti.

### Stĺpce {#columns}

| Stĺpec | Čo ukazuje |
|---|---|
| Zaškrtávacie políčko | Vyberie člena pre **Exportovať vybraté** alebo **Napísať vybratým** (pozri nižšie). |
| **Meno** | Priezvisko, meno -- kliknutím otvoríte člena. Štítky člena sa zobrazujú ako malé sivé značky vedľa mena; kliknutím na značku zoznam podľa tohto štítku vyfiltrujete. |
| **Členom od** | Začiatok členstva alebo „–“, ak nie je zaznamenaný. |
| **Parcely** | Čísla parciel pridelených členovi. <!-- TODO(verify): the list shows every parcel assignment of the member, including tenancies that have already ended -- confirm whether former parcels are meant to appear here. --> |
| **Stav** | **aktívny**, **neaktívny** alebo **čakajúci** (pozri nižšie). |
| Tlačidlo s okom | Otvorí stránku člena, rovnako ako kliknutie na meno. |

Odznak stavu znamená:

- **aktívny** -- členstvo začalo a neskončilo.
- **čakajúci** -- zatiaľ nie je zaznamenaný dátum **Členom od**.
  Čakajúci člen sa všade inde počíta ako aktívny (faktúry, prezenčná
  listina, počty na dashboarde); odznak vám len hovorí, že dátum
  začiatku nebol potvrdený.
- **neaktívny** -- členstvo skončilo alebo ešte nezačalo. Ak je zadaný
  dátum **Členom do**, odznak ukazuje „od“ tohto dátumu.

### Ručný výber členov {#picking-members-by-hand}

Každý riadok má zaškrtávacie políčko, takže môžete zo zoznamu vybrať
niekoľkých členov -- napríklad vyfiltrovať všetkých, ktorí povoľujú
e-mailové informácie, a potom zaškrtnúť 12 z nich.

| Tlačidlo | Čo robí |
|---|---|
| **Vybrať všetky** | Zaškrtne každého člena v aktuálnom zozname. |
| **Zrušiť výber** | Zruší všetky zaškrtnutia. |
| **Vybraté: *N*** | Počíta zaškrtnutých členov. |
| **Exportovať vybraté** | Stiahne súbor CSV len so zaškrtnutými členmi. Kým nikoho nezaškrtnete, je neaktívne. |
| **Napísať vybratým** | Začne nový oznam len zaškrtnutým členom. Zobrazí sa len, kým je zapnutý modul **Oznamy**, a len členom výboru a administrátorom. |

!!! warning "Pri zmene filtra sa zaškrtnutia stratia"
    Zmena vyhľadávania, zaškrtávacieho políčka alebo zoznamu štítkov
    stránku znova načíta a vaše zaškrtnutia zmiznú. Najprv nastavte
    filter, potom zaškrtávajte.

Keď použijete odkaz na zoznam členov z oznamu, ktorý bol odoslaný
vybratým členom, zoznam ukáže len týchto členov s upozornením
„Zobrazení sú len vybratí členovia (*N*).“ Kliknutím na **Zobraziť celý
zoznam** sa vrátite k bežnému zoznamu. Naraz môžete vybrať až 2 000
členov.

### Export CSV {#csv-export}

**CSV export** stiahne súbor `members.csv`, oddelený bodkočiarkami, s
jedným riadkom na každého člena v aktuálnom zozname. Nadpisy stĺpcov
sú po nemecky, aby sa súbor dal tak, ako je, znova importovať:

Vorname, Nachname, Strasse, PLZ, Ort, Geburtsdatum, IBAN, Member seit,
Member bis, E-Mail-Benachrichtigungen, E-Mail-Adressen, Telefonnummern,
Parzellen, Notizen, Tags.

- Dátumy sa zapisujú ako rok-mesiac-deň (2024-03-01).
- E-mailové informácie sa zapisujú ako „Ja“ alebo „Nein“.
- Viac e-mailových adries, telefónnych čísel, parciel alebo štítkov je
  v jednej bunke, oddelených bodkočiarkami.
- Štítky sa exportujú s názvom, ktorý ste napísali, nie s prekladom.
- Či člen odmieta narodeninové darčeky, sa neexportuje.

!!! tip
    Export vždy zodpovedá tomu, čo je na obrazovke. Ak chcete exportovať
    každého aktívneho člena, najprv kliknite na **Resetovať**. Ak chcete
    exportovať bývalých členov, najprv zaškrtnite **Zobraziť iba
    neaktívnych**.

## Import členov zo súboru CSV {#importing-members-from-a-csv-file}

Import použite na prenesenie existujúceho zoznamu členov -- z tabuľky
alebo zo staršieho programu -- do Parcelly. Funguje v dvoch krokoch:
nahráte súbor a potom poviete Parcelle, ktorý stĺpec obsahuje čo. Kým
nepotvrdíte druhý krok, nič sa neuloží.

Postup pri prvom importe nájdete v časti
[Import členov a parciel](../guides/csv-import.md).

### Krok 1: nahratie súboru {#step-1-upload-the-file}

Kliknite na **CSV import** v zozname členov. Otvorí sa dialóg **CSV
import**.

| Pole / tlačidlo | Čo robí |
|---|---|
| Pole súboru | Vyberte súbor `.csv`. |
| **Importovať** | Nahrá súbor a otvorí priradenie stĺpcov. Zatiaľ sa nič neuloží. |

Dialóg uvádza stĺpce, ktorým Parcella rozumie. Tieto nadpisy nemusíte
použiť -- stĺpce priradíte v ďalšom kroku. Niekoľko vecí o súbore:

- Stĺpce môžu byť oddelené bodkočiarkami alebo čiarkami. Parcella to
  rozpozná; ak to nevie určiť, predpokladá bodkočiarky.
- Prvý riadok musí byť hlavičkový.
- Dátumy môžu byť zapísané ako 2024-03-01, 01.03.2024 alebo 01.03.24.
- Viac e-mailových adries alebo telefónnych čísel v jednej bunke sa
  oddeľuje bodkočiarkami.
- Najjednoduchšou šablónou je **CSV export** zo samotnej Parcelly --
  odkaz v dialógu stiahne úplný, nefiltrovaný export.

Ak je súbor prázdny, vrátite sa do zoznamu s hlásením „Tento súbor CSV
sa zdá byť prázdny.“

### Krok 2: priradenie stĺpcov {#step-2-map-the-columns}

<!-- TODO(verify): no screenshot -- this page is only reached by uploading a file, which the screenshot tool can't do. -->

Stránka **Mapovanie stĺpcov CSV** ukazuje každý stĺpec vášho súboru s
jeho nadpisom a prvými piatimi riadkami dát pod ním, aby ste videli, čo
obsahuje. Nad každým stĺpcom je rozbaľovací zoznam.

| Pole / tlačidlo | Čo robí |
|---|---|
| Rozbaľovací zoznam pri každom stĺpci | Vyberte pole Parcelly, ku ktorému tento stĺpec patrí: **Meno**, **Priezvisko**, **Ulica**, **PSČ**, **Mesto**, **Dátum narodenia**, **IBAN**, **Členom od**, **Členom do**, **E-mailové upozornenia**, **E-mailové adresy**, **Telefónne čísla**, **Poznámky** -- alebo **— Ignorovať —**, ak chcete stĺpec preskočiť. Parcella predvyberie pole, keď nadpis rozpozná (po anglicky alebo po nemecky, napr. „Nachname“ alebo „Last name“). |
| **Importovať** | Importuje riadky a vráti vás do zoznamu členov. **Meno** a **Priezvisko** musia byť každé priradené k stĺpcu, inak dostanete „Pred importom prosím priraďte stĺpce mena a priezviska.“ |
| **Späť** | Vráti sa do zoznamu členov bez importovania čohokoľvek. |

### Čo sa pri importe stane {#what-happens-on-import}

Pre každý riadok Parcella hľadá existujúceho člena s rovnakým menom a
priezviskom. Ak ste priradili stĺpec **Dátum narodenia** a riadok má
dátum narodenia, musí sa zhodovať aj ten.

- **Bez zhody**: vytvorí sa nový člen vrátane e-mailových adries a
  telefónnych čísel z riadku.
- **Zhoda**: existujúci člen sa aktualizuje, ale len tým, čo riadok
  naozaj obsahuje (pozri nižšie). E-mailové adresy a telefónne čísla sa
  pri aktualizácii **nemenia** -- pridajte ich alebo odstráňte na
  stránke člena.
- **Viac členov s týmto menom**: Parcella použije dátum narodenia,
  e-mailové adresy a telefónne čísla z riadku, aby našla toho správneho.
  Aktualizuje sa člen, ktorý má niektoré z nich; na veľkosti písmen,
  medzerách a pomlčkách nezáleží („0171 234-5678“ je to isté ako
  „01712345678“). Ak riadok stále pasuje na viac členov, preskočí sa
  hlásením „Riadok 4: viacerí členovia sa volajú Hans Meier,
  preskočené. ...“ a nikto sa nezmení. Samotná e-mailová adresa alebo
  telefónne číslo nikdy nezodpovedá členovi s iným menom, pretože páry
  často jednu zdieľajú.
- **Prázdne meno alebo priezvisko**: riadok sa preskočí.

**Aktualizácia mení len to, čo hovorí súbor.** Stĺpec nastavený na
**— Ignorovať —** alebo prázdna bunka nechá uloženú hodnotu člena tak,
ako je. Súbor len s menami a novými adresami teda aktualizuje adresy a
nič iné.

Stĺpec **E-mailové upozornenia** sa počíta ako „nie“, keď obsahuje
*nein*, *no*, *false* alebo *0*, a ako „áno“ pri čomkoľvek inom
vyplnenom. Pri existujúcom členovi prázdna bunka alebo chýbajúci stĺpec
nechá jeho voľbu nezmenenú -- kto sa odhlásil, zostane odhlásený. Nový
člen bez hodnoty dostane „áno“.

Potom zoznam členov ukáže zhrnutie ako „12 nových importovaných, 3
aktualizovaných“. Ak boli riadky preskočené, zhrnutie pridá počet chýb a
podrobnosti prvých troch.

!!! tip "Členovia s rovnakým menom"
    Ak má váš spolok členov s rovnakými menami, priraďte stĺpec **Dátum
    narodenia**, **E-mailové adresy** alebo **Telefónne čísla**: potom
    každý riadok aktualizuje správnu osobu. Bez nich sa takéto riadky
    preskočia namiesto hádania.

## Stránka člena {#member-page}

![Stránka člena](../assets/screenshots/members/detail.png)

Kliknutím na meno v zozname členov otvoríte stránku člena. Ukazuje
všetko, čo Parcella o členovi vie, a umožňuje priamo pridávať telefónne
čísla, e-mailové adresy, štítky a parcely.

### Tlačidlá hore {#buttons-at-the-top_1}

| Tlačidlo | Čo robí |
|---|---|
| **Upraviť** | Otvorí [formulár úprav](#new-member-and-edit-member). Potrebuje oprávnenie na zápis. |
| **Predchádzajúci** / **Ďalší** | Skočí na predchádzajúceho alebo ďalšieho člena *v zozname, z ktorého ste prišli*, s rovnakým filtrom. Môžete stlačiť aj ++ctrl+left++ a ++ctrl+right++ (nie počas písania do poľa). Na Macu môže systém tieto klávesy používať na prepínanie plôch. |
| **Späť** | Vráti sa do zoznamu členov s vaším filtrom. |

### Hlavné údaje {#master-data}

Ukazuje **Meno**, **Dátum narodenia**, **Adresa**, **IBAN**, **Členom
od**, **Členom do**, **E-mail info** (či člen smie dostávať informácie
e-mailom) a **Neželá si narodeninové darčeky**. Ak chcete niečo z toho
zmeniť, kliknite na **Upraviť**.

### Štítky {#tags}

Uvádza štítky člena. Kliknutím na štítok uvidíte každého člena s týmto
štítkom.

| Pole / tlačidlo | Čo robí |
|---|---|
| **×** vedľa štítku | Odoberie štítok tomuto členovi (**Odobrať štítok**). Samotný štítok zostáva pre ostatných členov. Potrebuje oprávnenie na zápis. |
| **Pridať štítok, napr. zodpovedný za vodu** | Napíšte názov štítku a kliknite na **+** (**Pridať štítok**). Ak štítok s týmto názvom už existuje -- na veľkých písmenách a medzerách navyše nezáleží --, použije sa znova; inak sa vytvorí nový. Pole počas písania navrhuje existujúce štítky. Potrebuje oprávnenie na zápis. |
| **Spravovať štítky** | Otvorí stránku [Štítky členov](#member-tags). |

Odobratie štítku členovi nezanecháva záznam v histórii: štítky sú
značky na vyhľadávanie ľudí, nie záznamy spolku.

### Telefónne čísla a e-mailové adresy {#phone-numbers-and-email-addresses}

| Pole / tlačidlo | Čo robí |
|---|---|
| Pole telefónneho čísla + **+** | Pridá ďalšie telefónne číslo. Potrebuje oprávnenie na zápis. |
| Pole e-mailu + **+** | Pridá ďalšiu e-mailovú adresu. Musí vyzerať ako e-mailová adresa. Potrebuje oprávnenie na zápis. |
| Tlačidlo koša | Odstráni toto telefónne číslo alebo e-mailovú adresu (**Odstrániť**). Potrebuje oprávnenie na mazanie. |

Kliknutím na e-mailovú adresu napíšete členovi zo svojho poštového
programu.

### Pridelené parcely {#assigned-parcels}

Uvádza parcely pridelené členovi.

| Stĺpec | Čo ukazuje |
|---|---|
| **Číslo parcely** | Kliknutím naň (alebo na tlačidlo so šípkou) otvoríte parcelu. |
| **Rozloha** | Rozloha parcely v metroch štvorcových. |
| **Stav** | Stav parcely: **aktívna**, **ukončená** alebo **vymazaná**. |
| **Fakturačná adresa** | Či sa adresa tohto člena používa pre faktúry parcely. |
| **Od** | Začiatok nájmu. |

<!-- TODO(verify): this table lists every assignment of the member, including ended tenancies, and has no "until" column -- confirm whether former parcels are meant to appear here. Also, a communal parcel would show as "deleted" here because the badge only knows active/terminated. -->

Pridelenie parcely členovi (potrebuje oprávnenie na zápis):

| Pole / tlačidlo | Čo robí |
|---|---|
| **Vyberte parcelu…** | Parcela na pridelenie. Ponúka sa každá parcela, zoradená podľa čísla. |
| **Použiť ako fakturačnú adresu** | Predvolene zaškrtnuté. Faktúry za túto parcelu idú na adresu tohto člena. |
| **Priradiť** | Pridelí parcelu a otvorí stránku parcely. |

Nájom začína bez dátumu. Ak chcete nastaviť dátum začiatku alebo nájom
ukončiť, použite stránku parcely -- pozri
[Súčasní nájomcovia](parcels.md#current-tenants).

### Procesy {#processes}

Ak je zapnutý modul [Procesy](processes.md) a smiete vidieť procesy,
karta **Procesy** uvádza procesy týkajúce sa tohto člena. **Začať
proces** pre neho spustí nový.

### Poznámky {#notes}

Interné poznámky člena, ak nejaké sú. Upravíte ich vo formulári člena.

### Nebezpečná zóna {#danger-zone}

Zobrazí sa len používateľom s oprávnením na mazanie.

**Zmazať člena** po potvrdení označí člena ako zmazaného. Člen zmizne zo
všetkých zoznamov a vyhľadávaní. Jeho dáta zostanú v databáze a
existujúce priradenia parciel, pracovné zmeny a iné záznamy zostanú, ako
sú.

!!! warning "Ukončenie členstva nie je zmazanie"
    Pri členovi, ktorý zo spolku odchádza -- alebo zomrel --, nastavte
    namiesto toho vo formulári úprav **Členom do** a jeho nájmy ukončite
    na stránke parcely. Potom sa presunie do **Zobraziť iba
    neaktívnych** a jeho história zostane viditeľná. Mazanie je určené
    pre záznamy, ktoré nikdy nemali existovať, napríklad duplikát.
    <!-- TODO(verify): there's no way to restore a deleted member in the app; confirm. Also confirm how a deleted member who is still assigned to a parcel shows up on the parcel page. -->

## Nový člen a úprava člena {#new-member-and-edit-member}

![Formulár nového člena](../assets/screenshots/members/form-new.png)

Kliknite na **Nový člen** v zozname členov alebo na **Upraviť** na
stránke člena. Oba formuláre vyzerajú rovnako; formulár nového člena sa
navyše pýta na prvú e-mailovú adresu a telefónne číslo. Polia označené
červenou hviezdičkou sú povinné.

### Osobné údaje {#personal-data}

| Pole | Čo robí |
|---|---|
| **Meno** \* | Povinné. |
| **Priezvisko** \* | Povinné. |
| **Dátum narodenia** | Používa sa pre zoznam narodenín a priemerný vek na dashboarde. Pomáha aj importu CSV rozlíšiť členov s rovnakým menom. |
| **IBAN** | Bankový účet člena, napr. pre inkaso. |

### Adresa {#address}

| Pole | Čo robí |
|---|---|
| **Ulica a číslo domu** | |
| **PSČ** | Najviac 10 znakov. |
| **Mesto** | |

Adresa sa používa pre listy a faktúry. Ak je člen fakturačnou adresou
parcely, faktúry za túto parcelu idú sem.

### Členstvo {#membership}

| Pole | Čo robí |
|---|---|
| **Členom od** | Prvý deň členstva. Ak je prázdne, člen je uvedený ako *čakajúci*, ale stále sa počíta ako aktívny. Ak je v budúcnosti, člen sa do tohto dňa počíta ako neaktívny. |
| **Členom do** | Posledný deň členstva. „Nechajte prázdne = aktívny člen“. Od nasledujúceho dňa sa člen počíta ako neaktívny. |
| **E-mailová adresa** | Len pri nových členoch. Voliteľné -- ďalšie adresy sa dajú pridať neskôr na stránke člena. |
| **Telefónne číslo** | Len pri nových členoch. Voliteľné -- ďalšie čísla sa dajú pridať neskôr na stránke člena. |
| **Môže dostávať informácie e-mailom** | Pri nových členoch predvolene zaškrtnuté. Odškrtnite, ak člen nechce dostávať informácie spolku e-mailom. Zoznam členov podľa toho vie filtrovať. |
| **Neželá si narodeninové darčeky** | Zaškrtnite, ak člen nechce narodeninové darčeky. Zobrazí sa v zozname narodenín, aby o tom vedeli tí, ktorí sa starajú o darčeky. |

### Poznámky {#notes_1}

| Pole | Čo robí |
|---|---|
| **Interné poznámky…** | Voľný text pre výbor. Vyhľadávanie v zozname členov prehľadáva aj poznámky. |

### Štítky {#tags_1}

| Pole | Čo robí |
|---|---|
| Zaškrtávacie políčka štítkov | Jedno políčko na každý existujúci štítok. Zaškrtnutím alebo odškrtnutím ho pridáte alebo odoberiete. Zobrazí sa, až keď existujú štítky. |
| **Nové štítky oddelené čiarkou** | Napíšte nové štítky oddelené čiarkami, napr. „zodpovedný za vodu, tím živého plota“. Názov, ktorý už existuje, sa použije znova. |

### Uloženie {#saving}

| Tlačidlo | Čo robí |
|---|---|
| **Vytvoriť člena** / **Uložiť zmeny** | Uloží člena a otvorí stránku člena. |
| **Zrušiť** | Odíde bez uloženia. |

Ak sa názov nového štítku neprijme (napríklad je dlhší ako 100 znakov),
zvyšok člena sa aj tak uloží a formulár úprav sa znova otvorí, aby ste
štítok opravili.
<!-- TODO(verify): in that case the form reopens without an error message. -->

## Štítky členov {#member-tags}

![Štítky členov](../assets/screenshots/members/tags.png)

Štítky sú voľné značky na opätovné vyhľadanie členov -- „zodpovedný za
vodu“, „rozšírený výbor“, „tím živého plota“. Pridávajte ich na stránke
člena alebo vo formulári člena; tu ich premenujete alebo zmažete.
Stránku otvoríte tlačidlom **Spravovať štítky** v zozname členov alebo
na stránke člena.

Každý štítok má jeden riadok:

| Pole / tlačidlo | Čo robí |
|---|---|
| Názov štítku + tlačidlo s fajkou | Zmeňte názov a kliknite na tlačidlo s fajkou (**Premenovať**). Nový názov sa zobrazí pri každom členovi, ktorý štítok má. Odmietne sa, ak iný štítok už má tento názov. Potrebuje oprávnenie na zápis; bez neho vidíte len názov. |
| **Členov: *N*** | Otvorí zoznam členov filtrovaný podľa tohto štítku. |
| Tlačidlo koša | **Zmazať štítok** po potvrdení. Štítok sa odstráni u každého člena. Potrebuje oprávnenie na mazanie. |
| Tlačidlo prekladu | Otvorí **Preklady** štítku: jeden názov na každý jazyk, ktorý Parcella podporuje. Kým spolok beží v nejakom jazyku, zoznamy, formuláre a filtre ukazujú názov štítku v tomto jazyku; prázdne pole ukazuje názov, ktorý ste napísali. Kliknutím na **Uložiť preklady** ich uložíte. Potrebuje oprávnenie na zápis; bez neho vidíte preklady ako zoznam. Malé číslo na tlačidle hovorí, koľko prekladov existuje. |
| **Späť na členov** | Vráti sa do zoznamu členov. |

Export CSV vždy používa názov, ktorý ste napísali, nie preklad.

## Prezenčná listina zo schôdze {#meeting-sign-in-sheet}

![Prezenčná listina zo schôdze](../assets/screenshots/members/signin-sheet.png)

Otvoríte ju tlačidlom **Prezenčná listina** v zozname členov. Vytvorí
zoznam v PDF na vytlačenie a prinesenie na členskú schôdzu: každý
súčasný nájomca, zoskupený podľa parcely, s podpisovým riadkom pre
každého.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Nadpis** | Zobrazí sa v hornej časti PDF. Začína ako „Členská schôdza dňa“ (v jazyku spolku) plus dnešný dátum; zmeňte ho na čokoľvek. Ak ho vyprázdnite, použije sa predvolený. |
| **Vytvoriť PDF** | Stiahne prezenčnú listinu ako súbor PDF. |
| **Zrušiť** | Vráti sa do zoznamu členov. |

Čo je na listine:

- Jeden riadok na osobu so stĺpcami **Parcela**, **Meno** a **Podpis**,
  zoradený podľa čísla parcely a potom podľa priezviska.
- Ak má jednu parcelu viac ľudí, číslo parcely sa objaví raz a každý z
  nich dostane vlastný podpisový riadok.
- Uvedení sú len **aktívni členovia**, ktorí sú **súčasnými nájomcami**
  parcely. Členovia bez parcely a nájomcovia, ktorí už odišli, na
  listine nie sú.
- PDF nesie logo spolku a rovnakú hlavičku a pätu ako ostatné dokumenty
  spolku. Dlhý zoznam jednoducho pokračuje na viacerých stranách.

!!! tip
    Členovia, ktorí nemajú parcelu -- napríklad čestní členovia --, na
    listine nie sú. Ak sa môžu zúčastniť, dopíšte ich ručne.

## Súvisiace {#related}

- [Parcely](parcels.md) -- prideľovanie a ukončovanie nájmov
- [Uchádzači](applicants.md) -- ako sa z uchádzača stane člen
- [Prijatie nového člena](../guides/new-member.md)
- [Odovzdanie parcely](../guides/parcel-handover.md)
- [Import členov a parciel](../guides/csv-import.md)
- [Oznamy](announcements.md) -- písanie vyfiltrovaným alebo vybratým členom

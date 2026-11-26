# Slovník {#glossary}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Pojmy zo života spolku a z Parcelly, v abecednom poradí.

Kapitoly odkazujú priamo na heslo, napríklad
`glossary.md#deposit`.

## Aktívna, ukončená, spoločná, vymazaná {#parcel-status}

Štyri stavy [parcely](#parcel):

- **aktívna** -- bežná parcela, zvyčajne niekomu prenajatá.
- **ukončená** -- nájomca dal [výpoveď](#notice-of-termination) a
  parcela je na ceste k novému nájomcovi. Len ukončené parcely sa dajú
  odovzdať [uchádzačovi](#applicant).
- **spoločná** -- pozemok spolku evidovaný ako parcela (chodníky,
  ihrisko), nikdy neprenajímaný. Nezapočítava sa do prenajatej plochy.
- **vymazaná** -- už sa nepoužíva, ale zachováva sa s históriou.

## Bývalý, súčasný a budúci nájomca {#former-tenant}

[Nájom](#tenancy) je **súčasný**, kým trvá, **budúci**, ak začína k
budúcemu dátumu (po odovzdaní k budúcemu dátumu), a **bývalý**, keď
skončil. Bývalí nájomcovia zostávajú na stránke parcely v časti
**Bývalí nájomcovia**; [fakturačnou adresou](#invoice-address) môžu byť
len súčasní (a budúci) nájomcovia.

## Člen {#member}

Osoba, ktorá patrí do spolku. Zvyčajne aj [nájomca](#tenant), ale nie
nevyhnutne (podporujúci alebo čestní členovia). Člen sa počíta ako
aktívny až do svojho dátumu **Členom do**.

## Externý kontakt {#external-contact}

Dodávateľ, remeselník, úrad alebo iná organizácia, s ktorou spolok
jedná -- firma a/alebo kontaktná osoba. Nie je to člen. Pozri
[Externé kontakty](modules/external-contacts.md).

## Fakturačná adresa {#invoice-address}

Nájomca parcely, na ktorého adresu idú faktúry parcely -- **Použiť ako
fakturačnú adresu** pri nájme. Môže ju mať viac nájomcov jednej
parcely; parcela aj tak dostane jednu faktúru. Parcela bez nej faktúru
nedostane.

## Hlavný merač {#main-meter}

Meradlo, kde spolok preberá vodu alebo elektrinu od dodávateľa. Jeho
spotreba by sa mala približne rovnať súčtu všetkých meradiel parciel a
spolku; Parcella upozorní, ak parcely spolu spotrebovali viac.

## Kalibrácia {#calibration}

Vodomery a elektromery sa na vyúčtovanie smú používať len do
uplynutia kalibrácie. Parcella ukladá rok ako **Kalibrovaný do** a
meradlá po kalibrácii označí **Kalibrácia vypršala**. Bežným riešením je
[výmena meradla](guides/meter-readings.md#a-meter-is-replaced).

## Katalóg položiek {#item-catalog}

Váš zoznam opakovane použiteľných riadkov faktúr (nájom, voda,
poistenie, ...), ktoré sa vyberajú do [vyúčtovania](#invoice-run) každého
roka. Nájdete ho v **Financie → Prehľad → Katalóg položiek**.

## Kaucia {#deposit}

Suma, ktorú nový nájomca zaplatí pri prevzatí parcely a ktorú spolok
drží a pri odchode nájomcu vráti -- alebo si časť ponechá. Parcella
nemá samostatnú funkciu kaucie: sumu a dátum si poznačte v
[procese](#process) odovzdania a peniaze zaúčtujte vo **Financie**.
Pozri [Odovzdanie parcely](guides/parcel-handover.md#7-deposit-and-money).

## Merací bod {#metering-point}

Miesto, kde sa meria voda alebo elektrina: prípojka parcely,
[hlavný merač](#main-meter) alebo prípojka spolku (klubovňa, umývacie
miesto). Merací bod zostáva; [meradlo](#meter) v ňom nainštalované sa
môže meniť.

## Meradlo {#meter}

Fyzický vodomer alebo elektromer s číslom, rokom kalibrácie a
počiatočným stavom. [Merací bod](#metering-point) má naraz jedno
meradlo; keď sa vymení, staré sa zachová ako predchádzajúce meradlo.

## Modul {#module}

Funkčná oblasť Parcelly -- Pracovné hodiny, Voda, Financie, Procesy
atď. --, ktorú môžete pre svoj spolok zapnúť alebo vypnúť v
**Administrácia → Nastavenia → Funkčné oblasti**. Vypnutie ju skryje;
jej dáta zostanú. Pozri [Zapínanie a vypínanie modulov](administration/modules.md).

## Nájom {#tenancy}

Prenájom parcely členom, od dátumu začiatku po voliteľný dátum konca.
Ukončenie nájmu ho zachová ako históriu; jednu parcelu môže zdieľať viac
členov. Pozri aj [bývalý nájomca](#former-tenant).

## Nájomca {#tenant}

Člen, ktorý má [nájom](#tenancy) parcely.

## Násobiteľ {#factor}

Násobiteľ pri [meracom bode](#metering-point) pre meradlá, ktoré
ukazujú len časť skutočnej hodnoty (napríklad 20 pri elektromere s
meracími transformátormi). Odpočty sa zadávajú tak, ako sú zobrazené;
hodnotenie ich vynásobí násobiteľom. Zvyčajne 1.

## Obhliadka {#inspection}

Prechádzka výboru po parcele, keď nájomca odchádza, na zaznamenanie
nedostatkov pred [ocenením](#valuation). Sleduje sa v
[procese](#process) odovzdania.

## Ocenenie {#valuation}

Odborný posudok, akú hodnotu majú záhradná chatka, rastliny a vybavenie
parcely, keď nájomca odchádza. Parcella ho nepočíta; posudok uložíte v
[procese](#process) odovzdania.

## Odovzdanie {#handover}

Zmena zo starého na nového nájomcu parcely. V Parcelle **Prideliť
parcelu** pri prihláške ukončí starý [nájom](#tenancy), urobí z
uchádzača člena a nájomcu a parcelu znova nastaví ako aktívnu. Pozri
[Odovzdanie parcely](guides/parcel-handover.md).

## Odpočet {#reading}

Hodnota na displeji meradla. Parcella uchováva jeden odpočet na
[meradlo](#meter) a rok; spotreba roka je tento odpočet mínus
predchádzajúci.

## Oprávnenie {#permission}

Čo smie používateľ robiť v [module](#module): **Čítanie** (pozerať),
**Zápis** (pridávať a meniť) alebo **Mazanie**. Každý, kto sa môže
prihlásiť, si smie pozrieť členov a parcely. Pozri
[Roly, skupiny a oprávnenia](getting-started/roles-and-permissions.md).

## Oslobodenie {#exemption}

Člen, ktorý v danom roku nemusí odpracovať [povinné
hodiny](#mandatory-hours) -- zvyčajne kvôli [role v spolku](#club-role),
zdraviu alebo veku. Ak je oslobodený jeden nájomca parcely, je
oslobodená celá parcela, a oslobodenie vždy platí pre celý kalendárny
rok.

## Parcela {#parcel}

Jedna záhradka, označená **Číslo parcely**. Na niekoľkých miestach v
aplikácii sa nazýva „Záhradka“.

## Podiel na nájme spoločnej plochy {#communal-area-share}

Položka faktúry, ktorá účtuje nájom spoločného pozemku spolku
([Rozloha B](#areas)), rovnomerne rozdelený medzi parcely, ktorých sa
týka. V aplikácii: **Podiel na nájme spoločnej plochy**.

## Pokladník {#treasurer}

Člen výboru zodpovedný za peniaze spolku. V Parcelle dajte pokladníkovi
[skupinu](#group) s plnými právami pre **Financie**.

## Poradovník {#waiting-list}

[Uchádzači](#applicant), ktorí čakajú na parcelu, v poradí, v akom sa
prihlásili. V Parcelle: **Uchádzači** s filtrom **Otvorené**.

## Povinné hodiny {#mandatory-hours}

Hodiny prác pre spoločenstvo, ktoré parcela alebo člen dlží spolku
každý rok, ako rozhodla členská schôdza. Neodpracované hodiny sa platia
hodinovou sadzbou. Parcella do nich započítava navštívené [pracovné
zmeny](#work-session), [sponzorstvá](#sponsorship) a [prevody
hodín](#hours-transfer) a nedoplatok sa dá vyúčtovať v ročnom
[vyúčtovaní](#invoice-run). Pozri [Pracovné hodiny](modules/work-hours.md).

## Pracovná zmena {#work-session}

Termín, keď členovia robia práce pre spolok, započítavané do ich
[povinných hodín](#mandatory-hours). Zmeny **Štandard** sú plánované a
dajú sa zverejniť na webe spolku; zmeny **Špeciál** sú spontánne a
interné. Pozri [Organizácia pracovnej zmeny](guides/work-session.md).

## Prevod hodín {#hours-transfer}

Člen, ktorý odpracoval viac [povinných hodín](#mandatory-hours), ako sa
vyžadovalo, dá časť prebytku inému členovi za ten istý rok. Pozri
**Pracovné sedenia → Prevody hodín**.

## Proces {#process}

Kontrolný zoznam krok za krokom, ktorý si navrhnete sami -- napríklad
odovzdanie parcely alebo prijatie člena --, spustený pre jednu parcelu,
člena alebo uchádzača. Každá fáza má polia na vyplnenie; povinné polia
treba vyplniť pred posunom ďalej. Pozri [Procesy](modules/processes.md).

## Rola {#role}

Staršie účty majú pevnú rolu (**Administrátor**, **Výbor**,
**Pokladník**, **Iba na čítanie (len prehliadanie)**). Nové účty
dostávajú prístup namiesto toho zo [skupín](#group). Nie je to to isté
ako [rola v spolku](#club-role).

## Rola v spolku {#club-role}

Funkcia v spolku -- predseda, pokladník, správca vody --, ktorú člen
zastáva počas roka. Rola v spolku môže svojho nositeľa
[oslobodiť](#exemption) od [povinných hodín](#mandatory-hours).
Nastavuje sa v **Pracovné sedenia → Sedenia a prehľad → Roly v
spolku**. Nezamieňať s [rolou](#role) v Parcelle.

## Rozloha A, B a C {#areas}

Celková rozloha spolku rozdelená na tri časti, nastavená v
**Administrácia → Nastavenia → Rozlohy (m²)**:

- **Rozloha A (parcely, m²)** -- súčet rozlôh všetkých parciel,
  vypočítaný Parcellou.
- **Rozloha B (spoločná, m²)** -- chodníky, zeleň a iný spoločný pozemok
  spolku: celok mínus A a C, vypočítaný Parcellou.
- **Rozloha C (obecná, m²)** -- pozemok, ktorý spolok spravuje, ale
  patrí obci, zadaný ručne.

Z rozlohy B vychádza [podiel na nájme spoločnej plochy](#communal-area-share)
a [verejné dávky](#public-burdens).

## Schválenie dvoma osobami {#two-person-approval}

[Žiadosť o nákup](#purchase-request) je schválená, až keď ju schválili
dvaja rôzni členovia výboru -- a ani jeden z nich nesmie byť osoba,
ktorá o ňu požiadala. Jeden člen výboru ju môže zamietnuť.

## Skupina {#group}

Sada [oprávnení](#permission) v Parcelle -- čítanie, zápis alebo mazanie
pre jednotlivé [moduly](#module) alebo plný prístup --, ktorú dávate
používateľským účtom. Noví používatelia dostávajú prístup len cez
skupiny. Pozri [Skupiny](administration/groups.md).

## Sponzorstvo {#sponsorship}

Člen sa počas roka stará o časť areálu spolku -- živý plot, ihrisko --
a dostane za to pripísaný pevný počet [povinných
hodín](#mandatory-hours). Pozri **Pracovné sedenia → Sponzorstvá**.

## Štítok {#tag}

Voľná značka pri členovi, napríklad „tím živého plota“ alebo
„zodpovedný za vodu“, na vyhľadávanie a filtrovanie ľudí. Štítky
existujú aj pre externé kontakty.

## Tlačový balík {#print-bundle}

Jedno PDF so všetkými faktúrami vyúčtovania, ktorých príjemcu nemožno
zastihnúť e-mailom, pripravené na tlač a odoslanie poštou.

## Uchádzač {#applicant}

Niekto, kto požiadal o záhradku a je v [poradovníku](#waiting-list).
Uchádzači sú oddelení od [členov](#member): členmi sa stanú, až keď
naozaj dostanú parcelu. Pozri [Uchádzači](modules/applicants.md).

## Ukážkové dáta {#sample-data}

Vymyslení členovia, parcely a iné záznamy, ktoré môžete pridať do novej
inštalácie, aby ste si Parcellu vyskúšali, a jedným kliknutím ich znova
odstrániť. Pozri [Ukážkové dáta](administration/sample-data.md).

## Upomínanie {#dunning}

Pripomenutie nezaplatenej faktúry členovi. V Parcelle: **Odoslať
upomienku** pri faktúre po splatnosti vytvorí **Upomienka č. 1**, **č.
2** atď., s voliteľným poplatkom. Pevné stupne upomínania neexistujú;
výbor rozhoduje, kedy poslať ďalšiu. Pozri
[Faktúry, platby a upomienky](modules/finances/invoices.md).

## Verejné dávky {#public-burdens}

Poplatky, ktoré vlastník pozemku prenáša na spolok -- daň z
nehnuteľností, čistenie ulíc a podobné obecné poplatky --, zvyčajne za
meter štvorcový. Spolok ich prenáša na parcely, vrátane podielu za
spoločný pozemok. V aplikácii: **Verejné dávky (vlastná plocha +
podiel na spoločnej ploche)**: vlastná rozloha parcely plus jej rovný
podiel na [rozlohe B](#areas), krát sadzba, ktorú zadáte.

## Všeobecná dávka {#general-levy}

Jednorazová suma, ktorú musí spolok vybrať od všetkých parciel spolu --
právne trovy, oprava, zvýšenie poistného --, rozdelená rovným dielom. V
aplikácii: **Všeobecná dávka (rozdelená rovnomerne medzi všetky
parcely)**. Ako jednotkovú cenu zadáte *celkovú* sumu; Parcella ju
vydelí počtom fakturovaných parciel a každý podiel dá na faktúru
parcely.

## Vyúčtovanie {#invoice-run}

Jedna dávka faktúr, zvyčajne ročné faktúry za rok. Pridáte riadky,
skontrolujete náhľad, potom ho **dokončíte** -- čím sa pridelia trvalé
čísla faktúr -- a odošlete. Pozri [Ročné vyúčtovanie](guides/annual-invoicing.md).

## Výbor {#board}

Zvolený výbor spolku. V Parcelle majú členovia výboru zvyčajne plný
prístup ku každému modulu. Súčasný výbor uvediete v **Administrácia →
Nastavenia → Členovia výboru**; ich prístup pochádza zo
[skupiny](#group) s **Plný prístup ku každému modulu** (alebo, pri
starších účtoch, z roly **Výbor**).

## Výpoveď {#notice-of-termination}

Oznámenie nájomcu (alebo spolku), že nájom končí. V Parcelle nastavíte
stav parcely na **ukončená**; dátum sa zaznamená automaticky.

## Žiadosť o nákup {#purchase-request}

Žiadosť o minutie peňazí spolku, ktorá pred nákupom potrebuje
[schválenie dvoma osobami](#two-person-approval). Pozri
[Žiadosti o nákup](modules/purchase-requests.md).

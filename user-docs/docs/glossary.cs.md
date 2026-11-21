# Slovníček {#glossary}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Pojmy ze života spolku a z Parcelly, v abecedním pořadí.

Kapitoly odkazují přímo na heslo, například
`glossary.md#deposit`.

## Aktivní, ukončená, společná, smazaná {#parcel-status}

Čtyři stavy [parcely](#parcel):

- **aktivní** -- běžná parcela, obvykle někomu pronajatá.
- **ukončená** -- nájemce dal [výpověď](#notice-of-termination) a
  parcela je na cestě k novému nájemci. Předat [uchazeči](#applicant)
  lze jen ukončené parcely.
- **společná** -- pozemek spolku vedený jako parcela (cesty, hřiště),
  nikdy se nepronajímá. Nezapočítává se do pronajaté plochy.
- **smazaná** -- už se nepoužívá, ale zůstává i s historií.

## Bývalý, současný a budoucí nájemce {#former-tenant}

[Nájem](#tenancy) je **současný**, dokud trvá, **budoucí**, pokud začíná
k budoucímu datu (po předání s budoucím datem), a **bývalý**, jakmile
skončil. Bývalí nájemci zůstávají na stránce parcely v části **Bývalí
nájemci**; [fakturační adresou](#invoice-address) mohou být jen současní
(a budoucí) nájemci.

## Člen {#member}

Osoba, která patří do spolku. Obvykle zároveň [nájemce](#tenant), ale ne
nutně (podporující nebo čestní členové). Člen se počítá jako aktivní do
data **Členem do**.

## Externí kontakt {#external-contact}

Dodavatel, řemeslník, úřad nebo jiná organizace, se kterou spolek jedná
-- firma a/nebo kontaktní osoba. Není to člen. Viz
[Externí kontakty](modules/external-contacts.md).

## Fakturační adresa {#invoice-address}

Nájemce parcely, na jehož adresu se posílají faktury parcely -- volba
**Použít jako fakturační adresu** u nájmu. Může ji mít více nájemců
jedné parcely; parcela přesto dostane jednu fakturu. Parcela bez
fakturační adresy fakturu nedostane.

## Hlavní měřidlo {#main-meter}

Měřidlo, kde spolek přebírá vodu nebo elektřinu od dodavatele. Jeho
spotřeba by měla zhruba odpovídat součtu všech měřidel parcel a spolku;
Parcella varuje, pokud parcely dohromady spotřebovaly více.

## Kalibrace {#calibration}

Vodoměry a elektroměry se smějí k vyúčtování používat jen do vypršení
jejich kalibrace (ověření). Parcella ukládá rok jako **Kalibrováno do**
a měřidla s prošlou kalibrací označuje **Kalibrace vypršela**. Obvyklým
řešením je [výměna měřidla](guides/meter-readings.md#a-meter-is-replaced).

## Katalog položek {#item-catalog}

Váš seznam opakovaně použitelných položek faktur (nájem, voda, pojištění,
...), které vybíráte do každoročního [vyúčtování](#invoice-run). Najdete
ho v **Finance → Přehled → Katalog položek**.

## Kauce {#deposit}

Částka, kterou nový nájemce zaplatí při převzetí parcely; spolek ji drží
a při odchodu nájemce ji vrátí -- nebo si její část ponechá. Parcella
nemá samostatnou funkci pro kauce: částku a datum si poznamenejte v
[procesu](#process) předání a peníze zaúčtujte ve **Finance**. Viz
[Předání parcely](guides/parcel-handover.md#7-deposit-and-money).

## Měrné místo {#metering-point}

Místo, kde se měří voda nebo elektřina: přípojka parcely,
[hlavní měřidlo](#main-meter) nebo přípojka spolku (klubovna, mycí
místo). Měrné místo zůstává; [měřidlo](#meter) v něm nainstalované se
může měnit.

## Měřidlo {#meter}

Fyzický vodoměr nebo elektroměr s číslem, rokem kalibrace a počátečním
stavem. [Měrné místo](#metering-point) má vždy jedno měřidlo; při výměně
se staré uchová jako bývalé měřidlo.

## Modul {#module}

Funkční oblast Parcelly -- pracovní hodiny, voda, finance, procesy a tak
dále --, kterou lze pro váš spolek zapnout nebo vypnout v
**Administrace → Nastavení → Funkční oblasti**. Vypnutím se modul skryje;
jeho data zůstanou. Viz
[Zapínání a vypínání modulů](administration/modules.md).

## Nájem {#tenancy}

Pronájem parcely členem, od data začátku do volitelného data konce.
Ukončený nájem zůstává jako historie; jednu parcelu může sdílet více
členů. Viz také [bývalý nájemce](#former-tenant).

## Nájemce {#tenant}

Člen, který má k parcele [nájem](#tenancy).

## Násobitel {#factor}

Násobitel u [měrného místa](#metering-point) pro měřidla, která ukazují
jen zlomek skutečné hodnoty (například 20 u elektroměru s měřicími
transformátory proudu). Odečty se zadávají tak, jak jsou zobrazeny;
vyhodnocení je násobí faktorem. Obvykle 1.

## Obecná dávka {#general-levy}

Jednorázová částka, kterou musí spolek vybrat od všech parcel společně
-- účet za právníka, oprava, zvýšení pojistného --, rozdělená rovným
dílem. V aplikaci: **Obecná dávka (rozdělena rovnoměrně mezi všechny
parcely)**. Jako jednotkovou cenu zadáte *celkovou* částku; Parcella ji
vydělí počtem fakturovaných parcel a každý podíl uvede na faktuře
parcely.

## Ocenění {#valuation}

Odborný posudek hodnoty zahradní chatky, rostlin a vybavení na parcele
při odchodu nájemce. Parcella ho nepočítá; posudek uložíte v
[procesu](#process) předání.

## Odečet {#reading}

Hodnota na displeji měřidla. Parcella uchovává jeden odečet na
[měřidlo](#meter) a rok; roční spotřeba je tento odečet minus předchozí.

## Oprávnění {#permission}

Co smí uživatel v [modulu](#module) dělat: **Čtení** (prohlížet),
**Zápis** (přidávat a měnit) nebo **Mazání**. Každý, kdo se může
přihlásit, si smí prohlížet členy a parcely. Viz
[Role, skupiny a oprávnění](getting-started/roles-and-permissions.md).

## Osvobození {#exemption}

Člen, který v daném roce nemusí odpracovat [povinné hodiny](#mandatory-hours)
-- obvykle kvůli [roli ve spolku](#club-role), zdraví nebo věku. Je-li
osvobozen jeden nájemce parcely, je osvobozena celá parcela, a
osvobození vždy platí pro celý kalendářní rok.

## Parcela {#parcel}

Jedna zahrádka, označená svým **Číslo parcely**. Na několika místech
aplikace se jí říká také „pozemek“.

## Podíl na nájmu společné plochy {#communal-area-share}

Položka faktury, která účtuje nájem společných pozemků spolku
([rozloha B](#areas)), rozdělený rovnoměrně mezi parcely, kterých se
týká. V aplikaci: **Podíl na nájmu společné plochy**.

## Pokladník {#treasurer}

Člen výboru odpovědný za peníze spolku. V Parcelle dejte pokladníkovi
[skupinu](#group) s plnými právy u **Finance**.

## Pořadník {#waiting-list}

[Uchazeči](#applicant), kteří čekají na parcelu, v pořadí, v jakém se
přihlásili. V Parcelle: **Uchazeči** s filtrem **Otevřené**.

## Povinné hodiny {#mandatory-hours}

Hodiny společné práce, které parcela nebo člen každoročně dluží spolku,
jak rozhodla členská schůze. Neodpracované hodiny se platí hodinovou
sazbou. Parcella do nich započítává navštívené
[pracovní směny](#work-session), [sponzoringy](#sponsorship) a
[převody hodin](#hours-transfer) a chybějící hodiny lze vyúčtovat v
ročním [vyúčtování](#invoice-run). Viz
[Pracovní hodiny](modules/work-hours.md).

## Pracovní směna {#work-session}

Termín, kdy členové odvádějí společnou práci pro spolek, započítávanou
do jejich [povinných hodin](#mandatory-hours). **Standard** směny jsou
plánované a lze je zveřejnit na webu spolku; **Speciál** směny jsou
spontánní a interní. Viz
[Organizace pracovní směny](guides/work-session.md).

## Proces {#process}

Kontrolní seznam krok za krokem, který si sami navrhnete -- například
předání parcely nebo přijetí člena --, spouštěný pro jednu parcelu, člena
nebo uchazeče. Každá fáze má pole k vyplnění; povinná pole musí být
vyplněna, než se pokračuje dál. Viz [Procesy](modules/processes.md).

## Prohlídka {#inspection}

Obchůzka parcely výborem při odchodu nájemce, aby se zaznamenaly závady
před [oceněním](#valuation). Eviduje se v [procesu](#process) předání.

## Předání {#handover}

Změna starého nájemce parcely za nového. V Parcelle tlačítko **Přidělit
parcelu** u přihlášky ukončí starý [nájem](#tenancy), udělá z uchazeče
člena a nájemce a parcelu opět nastaví jako aktivní. Viz
[Předání parcely](guides/parcel-handover.md).

## Převod hodin {#hours-transfer}

Člen, který odpracoval více [povinných hodin](#mandatory-hours), než
musel, daruje část přebytku jinému členovi za stejný rok. Viz
**Pracovní sezení → Převod hodin**.

## Role {#role}

Starší účty mají pevnou roli (**Správce**, **Výbor**, **Pokladník**,
**Pouze pro čtení**). Nové účty získávají přístup místo toho ze
[skupin](#group). Není to totéž co [role ve spolku](#club-role).

## Role ve spolku {#club-role}

Funkce ve spolku -- předseda, pokladník, správce vody --, kterou člen
zastává po dobu jednoho roku. Role ve spolku může svého nositele
[osvobodit](#exemption) od [povinných hodin](#mandatory-hours).
Nastavuje se v **Pracovní sezení → Sezení a přehled → Role ve spolku**.
Nezaměňovat s [rolí](#role) v Parcelle.

## Rozloha A, B a C {#areas}

Celková rozloha spolku rozdělená na tři části, nastavené v
**Administrace → Nastavení → Rozlohy (m²)**:

- **Rozloha A (parcely, m²)** -- součet rozloh všech parcel, vypočítá
  ho Parcella.
- **Rozloha B (společná, m²)** -- cesty, zeleň a další společné
  pozemky spolku: celek minus A a C, vypočítá ji Parcella.
- **Rozloha C (obecní, m²)** -- pozemky, které spolek spravuje, ale
  patří obci; zadávají se ručně.

Z rozlohy B vychází [podíl na nájmu společné plochy](#communal-area-share)
a [veřejné dávky](#public-burdens).

## Schválení dvěma osobami {#two-person-approval}

[Žádost o nákup](#purchase-request) je schválena, až když ji schválí dva
různí členové výboru -- a žádný z nich nesmí být ten, kdo o ni požádal.
Zamítnout ji může jediný člen výboru.

## Skupina {#group}

Sada [oprávnění](#permission) v Parcelle -- čtení, zápis nebo mazání pro
jednotlivé [moduly](#module), nebo plný přístup --, kterou přidělujete
uživatelským účtům. Noví uživatelé získávají přístup jen přes skupiny.
Viz [Skupiny](administration/groups.md).

## Sponzoring {#sponsorship}

Člen se po celý rok stará o část areálu spolku -- živý plot, hřiště -- a
dostane za to připsaný pevný počet [povinných hodin](#mandatory-hours).
Viz **Pracovní sezení → Sponzoringy**.

## Štítek {#tag}

Volný popisek u člena, například „tým živého plotu“ nebo „odpovědný za
vodu“, pro vyhledávání a filtrování lidí. Štítky existují i u externích
kontaktů.

## Tiskový balík {#print-bundle}

Jedno PDF se všemi fakturami vyúčtování, jejichž příjemce nelze zastihnout
e-mailem, připravené k tisku a odeslání poštou.

## Uchazeč {#applicant}

Někdo, kdo se přihlásil o zahrádku a je v [pořadníku](#waiting-list).
Uchazeči se vedou odděleně od [členů](#member): členy se stanou, až když
parcelu skutečně dostanou. Viz [Uchazeči](modules/applicants.md).

## Ukázková data {#sample-data}

Smyšlení členové, parcely a další záznamy, které můžete přidat do nové
instalace, abyste si Parcellu vyzkoušeli, a jedním kliknutím je zase
odstranit. Viz [Ukázková data](administration/sample-data.md).

## Upomínání {#dunning}

Připomenutí nezaplacené faktury členovi. V Parcelle: **Odeslat
upomínku** u faktury po splatnosti vytvoří **Upomínka č. 1**, **č. 2**
atd., s volitelným poplatkem. Pevné stupně upomínek neexistují; kdy
poslat další, rozhoduje výbor. Viz
[Faktury, platby a upomínky](modules/finances/invoices.md).

## Veřejné dávky {#public-burdens}

Poplatky, které vlastník pozemku přenáší na spolek -- daň z nemovitosti,
čištění ulic a podobné obecní poplatky --, obvykle za metr čtvereční.
Spolek je přenáší na parcely, včetně podílu za společné pozemky. V
aplikaci: **Veřejné dávky (vlastní plocha + podíl na společné ploše)**:
vlastní plocha parcely plus její rovný podíl na [rozloze B](#areas),
krát sazba, kterou zadáte.

## Výbor {#board}

Zvolený výbor spolku. V Parcelle mají členové výboru obvykle plný
přístup ke každému modulu. Současný výbor uvedete v
**Administrace → Nastavení → Členové výboru**; jejich přístup pochází ze
[skupiny](#group) s **Plný přístup ke každému modulu** (nebo, u starších
účtů, z role **Výbor**).

## Výpověď {#notice-of-termination}

Oznámení nájemce (nebo spolku), že nájem končí. V Parcelle nastavíte
stav parcely na **ukončená**; datum se zaznamená automaticky.

## Vyúčtování {#invoice-run}

Jedna dávka faktur, obvykle roční faktury za rok. Přidáte položky,
zkontrolujete náhled, pak ji **dokončíte** -- čímž se přidělí trvalá
čísla faktur -- a odešlete. Viz
[Roční vyúčtování](guides/annual-invoicing.md).

## Žádost o nákup {#purchase-request}

Žádost o utracení peněz spolku, která před nákupem potřebuje
[schválení dvěma osobami](#two-person-approval). Viz
[Žádosti o nákup](modules/purchase-requests.md).

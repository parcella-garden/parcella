# Externí kontakty {#external-contacts}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Externí kontakty jsou adresář spolku pro všechny, kdo nejsou členy:
dodavatele, řemeslníky, vodárnu, městský úřad. Kontakt je buď **firma**,
nebo **osoba**, a osoba může pracovat ve firmě. Kontakty můžete propojit
s přijatými fakturami a žádostmi o nákup, označit je štítky a uchovávat
jejich dokumenty v cloudu spolku.

!!! info "Kdo to může používat"
    Členové výboru a administrátoři mají vždy plný přístup. Všichni
    ostatní z tohoto modulu nevidí nic, dokud jim skupina nedá oprávnění
    pro **Externí kontakty** (viz [Skupiny](../administration/groups.md)):

    - **Čtení** -- vidět seznam a stránky kontaktů, exportovat CSV, vidět
      stránku štítků, stahovat dokumenty.
    - **Zápis** -- vytvářet a upravovat kontakty, přidávat telefonní
      čísla, e-mailové adresy a štítky, přejmenovávat štítky, importovat
      CSV, vybrat složku dokumentů kontaktu a nahrávat dokumenty.
    - **Mazání** -- mazat kontakty, telefonní čísla, e-mailové adresy a
      štítky a slučovat firmy.

    Modul se zapíná přepínačem **Externí kontakty** v části
    [Zapínání a vypínání modulů](../administration/modules.md). Ve
    výchozím stavu je zapnutý.

## Firmy a osoby {#companies-and-people}

- **Firma** má název firmy, adresu, IBAN a vlastní telefonní čísla a
  e-mailové adresy.
- **Osoba** má jméno a příjmení, pozici (např. „Referent“, „Majitel“) a
  volitelně firmu. Pokud osoba nemá vlastní adresu nebo IBAN, její
  stránka ukazuje údaje firmy.
- Zda je kontakt firma, nebo osoba, se rozhoduje při vytvoření a později
  to nelze změnit.
- Název firmy smí existovat jen jednou, stejně jako jméno osoby (na
  velkých písmenech nezáleží). Členové se nepočítají -- kontakt může mít
  stejné jméno jako člen.
- Každé pole je volitelné. Kontakt bez jakéhokoli jména se zobrazí jako
  **Kontakt bez názvu**.

## Seznam kontaktů {#contact-list}

![Externí kontakty](../assets/screenshots/external-contacts/list.png)

**Externí kontakty** v navigaci vypisuje každou firmu s jejími lidmi
odsazenými pod ní a každou osobu, která nepatří k žádné firmě. Seznam je
seřazený abecedně podle názvu firmy, u osob bez firmy podle příjmení.

| Pole / tlačítko | Co dělá |
|---|---|
| **Import CSV** | Otevře [dialog importu](#csv-import). Vyžaduje oprávnění k zápisu. |
| **Export CSV** | Stáhne seznam jako soubor CSV (viz [Export CSV](#csv-export)). Použije aktuální hledání a filtr štítku. |
| **Spravovat štítky** | Otevře [stránku štítků](#contact-tags). |
| **Nový kontakt** | Otevře [formulář kontaktu](#contact-form). Vyžaduje oprávnění k zápisu. |
| Pole hledání | Hledá v názvu firmy, jménu a příjmení, pozici, ulici, PSČ, městě, IBAN, poznámkách, telefonních číslech a e-mailových adresách. Použijete kliknutím na **Hledat**. |
| **Všechny štítky** / štítek | Ukáže jen kontakty s tímto štítkem. Zobrazí se, až štítky existují. |
| **Zrušit filtr** | Zruší hledání a filtr štítku. Zobrazí se, jen dokud je filtr aktivní. |

| Sloupec | Co ukazuje |
|---|---|
| **Název** | Ikona budovy u firem, ikona osoby u osob; název odkazuje na stránku kontaktu. Osoby mají za jménem uvedenou pozici. |
| **Štítky** | Štítky kontaktu. Kliknutím na štítek podle něj seznam vyfiltrujete. |
| **Telefon** | První telefonní číslo. |
| **E-mail** | První e-mailová adresa jako odkaz pro e-mail. |
| Tlačítko s okem | Otevře kontakt. |

Když hledání nebo štítek odpovídá osobě, je uvedena i její firma a
odpovídající osoba je pod ní zvýrazněna. Zápatí ukazuje, kolik položek
(firem a osob bez firmy) je uvedeno.

## Formulář kontaktu {#contact-form}

![Nový externí kontakt](../assets/screenshots/external-contacts/form-new.png)

**Nový kontakt** otevře prázdný formulář, **Upravit** na stránce
kontaktu vyplněný. **Přidat osobu** na stránce firmy ho otevře jako
novou osobu s již vyplněnou firmou.

U nového kontaktu nejprve nahoře vyberte **Firma** nebo **Osoba**.
Formulář pak ukáže jen pole pro daný druh.

### Firma / Osoba {#company-person}

| Pole | Zobrazí se u | Co dělá |
|---|---|---|
| **Jméno**, **Příjmení** | Osoba | Jméno osoby. Stačí kterákoli část. |
| **Název firmy** | Firma | Název firmy. |
| **Firma (nepovinné)** | Osoba | Firma, ve které osoba pracuje. Při psaní navrhuje existující firmy. Existující firma se propojí; nový název tuto firmu vytvoří. Pro samostatnou osobu nechte prázdné. Při **Upravit** vymazáním osobu z firmy odeberete. |
| **Pozice** | Osoba | Např. „Referent, Majitel“. |
| **E-mail**, **Telefon** | Nové kontakty | První e-mailová adresa a telefonní číslo. Další přidáte později na stránce kontaktu. |

Poznámka „Všechna pole jsou nepovinná. Název firmy i jméno osoby smí
existovat jen jednou.“ připomíná [pravidla výše](#companies-and-people).

### Adresa a bankovní spojení {#address-bank-details}

| Pole | Co dělá |
|---|---|
| **Ulice**, **PSČ**, **Město** | Poštovní adresa. |
| **IBAN** | Bankovní účet, např. pro placení faktur dodavatele. Nejvýše 34 znaků. |

U osoby ve firmě: „Nechte prázdné pro použití údajů firmy. Zadáno spolu
s novou firmou se stane adresou firmy.“ Pokud firma ještě nemá adresu
nebo IBAN, zadané údaje se uloží k firmě; pokud jsou stejné jako u
firmy, neukládají se dvakrát. U osoby zůstane jen adresa nebo IBAN,
které se skutečně liší.

### Poznámky a štítky {#notes-and-tags}

| Pole | Co dělá |
|---|---|
| **Poznámky** | Volný text -- otevírací doba, zákaznické číslo, číslo tiketu. Hledání v seznamu ho najde. |
| Zaškrtávací políčka štítků | Zaškrtněte existující štítky. |
| **Nové štítky oddělené čárkou** | Napište nové štítky; vytvoří se a přidají. |

Klikněte na **Vytvořit kontakt** (nový) nebo **Uložit změny** (úprava),
nebo **Zrušit**. Pokud firma nebo osoba se stejným jménem už existuje,
formulář se vrátí se zprávou jako „Firma … už existuje.“ a ponechá, co
jste napsali.

## Stránka kontaktu {#contact-page}

<!-- TODO(verify): no screenshot -- the sample data contains no external contacts, so the screenshot tool has no contact page to open. Add one once sample data seeds contacts. -->

### Tlačítka {#buttons}

| Tlačítko | Co dělá |
|---|---|
| **Upravit** | Otevře formulář kontaktu. Vyžaduje oprávnění k zápisu. |
| **Předchozí** / **Další** | Předchozí nebo další položka seznamu, se zachováním vašeho hledání a filtru štítku. Klávesnice: ++ctrl+left++ a ++ctrl+right++. |
| **Zpět na seznam** | Vrátí se na seznam se stejným filtrem. |

### Firma / Osoba {#company-person_1}

| Pole | Co ukazuje |
|---|---|
| **Firma** (firma) | Název firmy. |
| **Jméno**, **Pozice**, **Firma** (osoba) | Jméno a pozice osoby a odkaz na její firmu. Smazaná firma je označena „(smazána)“. |
| **Adresa** | Adresa kontaktu. U osoby bez adresy adresa firmy, označená **Adresa firmy**. |
| **IBAN** | IBAN kontaktu. U osoby bez IBAN IBAN firmy, označený **IBAN firmy**. |

### Osoby {#people}

Jen na stránce firmy: každá osoba ve firmě s pozicí, telefonními čísly
a e-mailovými adresami. **Přidat osobu** vytvoří novou osobu v této
firmě (oprávnění k zápisu). Pokud žádné nejsou: „U této firmy zatím
nejsou žádné osoby.“

### Štítky {#tags}

Štítky kontaktu; kliknutím na jeden uvidíte všechny kontakty s ním. S
oprávněním k zápisu **x** na štítku ho z tohoto kontaktu odebere a pole
**Přidat štítek…** přidá existující nebo nový štítek (nejvýše 100
znaků). **Spravovat štítky** otevře [stránku štítků](#contact-tags).

### Telefonní čísla a e-mailové adresy {#phone-numbers-and-email-addresses}

| Pole / tlačítko | Co dělá |
|---|---|
| Číslo / adresa | Kliknutím zavoláte nebo napíšete e-mail. Popis se zobrazí v závorce. |
| Pole čísla / adresy, **Popis (nepovinné)**, **+** | Přidá další číslo nebo adresu, např. s popisem „Kancelář“ nebo „Faktury“. Vyžaduje oprávnění k zápisu. |
| Tlačítko koše | Odebere číslo nebo adresu. Vyžaduje oprávnění k mazání. |

### Přijaté faktury a žádosti o nákup {#incoming-invoices-and-purchase-requests}

Vypisuje [přijaté faktury](finances/incoming-invoices.md) a
[žádosti o nákup](purchase-requests.md) propojené s tímto kontaktem --
na stránce firmy i ty propojené s jejími lidmi, se jménem osoby za
položkou. Každá karta se zobrazí, jen pokud je daný modul zapnutý a
smíte ho číst.

| Karta | Sloupce |
|---|---|
| **Přijaté faktury** | Datum faktury, číslo faktury (nebo odesílatel), celková částka. |
| **Žádosti o nákup** | Datum vytvoření, název, odhadované náklady. |

### Dokumenty {#documents}

Zobrazí se, když je zapnutý modul cloudového úložiště. Dopisy, nabídky a
smlouvy se neukládají v Parcelle, ale ve složce v cloudu spolku; tato
karta tuto složku ukazuje.

- Administrátor nejprve nastaví základní složku v
  [Integrace](../administration/integrations.md) (**Složka pro dokumenty
  externích kontaktů**). Do té doby to karta uvádí.
- Složka pro každý kontakt se vytváří ručně v cloudu, uvnitř základní
  složky. Na stránce kontaktu ji pak někdo s oprávněním k zápisu vybere
  ze seznamu **Složka** a klikne na **Uložit složku**. **Změnit složku**
  vybere jinou; **— žádná složka —** propojení zruší (soubory zůstanou v
  cloudu).
- Jakmile je složka vybraná, karta vypisuje její soubory a podsložky.
  Kliknutím na podsložku ji otevřete, na soubor ho stáhnete. Cesta nad
  seznamem vede zpět nahoru.
- S oprávněním k zápisu **Nahrát** vloží soubor do právě zobrazené
  složky.
- Mazání, přejmenování a přesouvání souborů se dělá přímo v cloudu.

Dokumenty patří firmě: stránka osoby místo toho odkazuje na dokumenty
firmy („Dokumenty jsou uloženy u firmy:“).

!!! warning "Varování"
    Pokud složku kontaktu v cloudu přejmenujete, Parcella o ni přijde.
    Vyberte ji znovu na stránce kontaktu.

### Poznámky {#notes}

Poznámky, pokud nějaké jsou.

### Nebezpečná zóna {#danger-zone}

Zobrazí se s oprávněním k mazání.

| Pole / tlačítko | Co dělá |
|---|---|
| **Sloučit do** + **Sloučit** | Jen na stránce firmy. Pro dva záznamy téže firmy (např. „Müller s.r.o.“ a „Mueller s.r.o.“): vyberte firmu, která má zůstat, klikněte na **Sloučit** a potvrďte. Osoby, telefonní čísla, e-mailové adresy, štítky a propojené faktury a žádosti o nákup se přesunou k vybrané firmě. Její adresa, IBAN a složka dokumentů se doplní z této, kde je nemá; poznámky se připojí k jejím poznámkám. Tato firma se pak smaže a otevře se ponechaná. |
| **Smazat kontakt** | Po potvrzení smaže kontakt. Zmizí ze seznamu a z výběrů, ale propojené faktury a žádosti o nákup ho stále ukazují (tam, kde ho ukazují, s označením „smazán“). Jeho jméno se opět uvolní. Firmu, která ještě má osoby, smazat nelze: „Tato firma má ještě osoby. Nejprve je přesuňte nebo smažte.“ |

## Štítky kontaktů {#contact-tags}

![Štítky kontaktů](../assets/screenshots/external-contacts/tags.png)

**Spravovat štítky** otevře **Štítky kontaktů**. Štítky kontaktů jsou
oddělené od štítků členů. **Zpět na kontakty** vás vrátí na seznam.

| Pole / tlačítko | Co dělá |
|---|---|
| **Označuje uchazeče:** | Vyberte jeden štítek (nebo **— žádný —**) a klikněte na **Uložit**. Uchazeči, jejichž jméno, e-mailová adresa nebo telefonní číslo odpovídá kontaktu s tímto štítkem, dostanou v seznamu uchazečů červenou vlajku a na své stránce varování -- užitečné pro štítek „nepronajímat“. Firma se štítkem označí i své osoby. Zobrazí se, jen když je zapnutý modul uchazečů a štítky existují; změna vyžaduje oprávnění k zápisu. Viz [Uchazeči](applicants.md). |
| Název štítku + tlačítko zaškrtnutí | Přejmenuje štítek u každého kontaktu. Vyžaduje oprávnění k zápisu. Název, který už existuje, se odmítne. |
| **Kontakty: {count}** | Otevře seznam vyfiltrovaný podle tohoto štítku. |
| Tlačítko koše | Po potvrzení smaže štítek ze všech kontaktů. Vyžaduje oprávnění k mazání. |
| **Překlady** | Otevře jedno pole pro každý jazyk. Název štítku lze v každém jazyce zobrazit jinak; prázdná pole ukazují vlastní název štítku. **Uložit překlady** je uloží (oprávnění k zápisu). |

Nové štítky se vytvářejí u kontaktu nebo ve formuláři kontaktu, ne na
této stránce.

## Export CSV {#csv-export}

**Export CSV** stáhne `external-contacts.csv`: oddělený středníky, jeden
řádek na firmu nebo osobu, se sloupci Typ, Firma, Vorname, Nachname,
Position, Strasse, PLZ, Ort, IBAN, E-Mail-Adressen, Telefonnummern,
Tags, Notizen (typ, firma, jméno, příjmení, pozice, ulice, PSČ, město,
IBAN, e-mailové adresy, telefonní čísla, štítky, poznámky). „Typ“ je
„Firma“ nebo „Person“. Každá firma je první, za ní následují její osoby.
Více e-mailových adres, čísel nebo štítků sdílí jednu buňku, oddělené
středníky.

Soubor lze beze změny znovu importovat.

## Import CSV {#csv-import}

Import má dva kroky a vyžaduje oprávnění k zápisu.

### Krok 1: výběr souboru {#step-1-choose-the-file}

**Import CSV** v seznamu otevře **Import kontaktů z CSV**. Vyberte
soubor `.csv` (oddělený středníkem nebo čárkou, s řádkem záhlaví) a
klikněte na **Importovat**. Zatím se nic neuloží.

### Krok 2: Import kontaktů {#step-2-import-contacts}

<!-- TODO(verify): no screenshot -- this screen is only reachable by uploading a file, which the screenshot tool can't do from a URL. -->

Karta **Přiřadit sloupce** ukazuje každý sloupec vašeho souboru s jeho
záhlavím a prvními pěti řádky. U každého sloupce vyberte pole, do
kterého patří, nebo **— ignorovat —**:

**Typ (firma/osoba)**, **Název firmy**, **Jméno**, **Příjmení**,
**Pozice**, **Ulice**, **PSČ**, **Město**, **IBAN**, **E-mailové
adresy**, **Telefonní čísla**, **Štítky**, **Poznámky**.

Parcella předvybere pole pro běžná německá a anglická záhlaví a vlastní
export přiřadí úplně. Žádné pole není povinné. Kliknutím na
**Importovat** import spustíte; **Zpět** ho zruší.

Jak se zpracuje každý řádek:

- **Firma nebo osoba:** sloupec typu uvádí „Firma“/„Company“ nebo
  „Person“. Bez něj je řádek s jménem nebo příjmením osobou, jinak
  firmou.
- **Existující kontakty se aktualizují:** firma se páruje podle názvu,
  osoba podle jména a příjmení (na velkých písmenech nezáleží). Shoda
  dostane každé pole vyplněné v souboru; telefonní čísla, e-mailové
  adresy a štítky, které ještě nemá, se přidají. Nic se nikdy
  neodstraňuje ani nevyprazdňuje.
- **Nové kontakty** se vytvoří pro řádky bez shody.
- **Firma osoby:** sloupec firmy propojí osobu s firmou tohoto názvu,
  která se v případě potřeby vytvoří. Adresa a IBAN z řádku doplní, co
  firmě chybí, a u osoby zůstanou jen tam, kde se liší.
- Zcela prázdné řádky se přeskočí.

Poté seznam ukáže souhrn, např. „Vytvořeno kontaktů: 3, aktualizováno:
1.“, a první problémy, pokud byly řádky přeskočeny (např. duplicitní
jméno).

## Kde se kontakty vybírají jinde {#where-contacts-are-picked-elsewhere}

Když je tento modul zapnutý a smíte číst kontakty, nabízejí jiné moduly
výběr kontaktu. Firmy se zobrazují jako skupina s lidmi pod nimi;
smazané kontakty se nenabízejí.

| Kde | Popisek | Co dělá |
|---|---|---|
| [Přijaté faktury](finances/incoming-invoices.md) -- nová faktura | **Kontakt** | Výběr kontaktu vyplní odesílatele. Odesílatel zůstává polem s volným textem. |
| Stránka přijaté faktury | **Kontakt** | Nastavení nebo pozdější změna propojeného kontaktu. |
| [Žádosti o nákup](purchase-requests.md) -- nová žádost a stránka žádosti | **Dodavatel (kontakt)** | Dodavatel nákupu. Lze změnit v jakémkoli stavu. |

## Související {#related}

- [Uchazeči](applicants.md) -- červené vlajky z kontaktů se štítkem
- [Integrace](../administration/integrations.md) -- cloudové úložiště a
  základní složka dokumentů
- [Skupiny](../administration/groups.md) -- přístup pokladníka ke
  kontaktům

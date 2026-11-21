# Import členů a parcel {#importing-members-and-parcels}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Pokud váš spolek už vede seznam členů, parcel nebo měřidel v tabulce,
nemusíte vše přepisovat znovu. Uložte tabulku jako soubor CSV, nahrajte
ji, řekněte Parcelle, který sloupec je který, a importujte.

Stejně to funguje pro **parcely**, **členy**, **měrná místa**, **odečty
měřidel** a **externí kontakty**. Tento návod je prochází v pořadí,
které dává smysl pro novou instalaci.

!!! info "Kdo to může dělat"
    Import členů a parcel vyžaduje oprávnění k **zápisu** u **Členové a
    parcely**; měrná místa a odečty vyžadují zápis u **Voda** nebo
    **Elektřina**; externí kontakty vyžadují zápis u **Externí
    kontakty**. Členové výboru a administrátoři mají všechna tato
    oprávnění.

!!! warning "Nejprve si stáhněte zálohu"
    Import zapíše mnoho záznamů najednou a „zpět“ neexistuje. Než
    začnete, otevřete **Administrace → Uživatelé** a klikněte na
    **Stáhnout zálohu**. Viz [Zálohování a obnova](../administration/backup.md).

## Jak funguje každý import {#how-every-import-works}

Všech pět importů má stejné dva kroky.

1. **Nahrát.** Na stránce seznamu klikněte na **CSV import** (u
   externích kontaktů: **Import CSV**), vyberte soubor a klikněte na
   **Importovat**. Zatím se nic neuloží.
2. **Mapování sloupců CSV.** Parcella ukáže tabulku: jeden sloupec pro
   každý sloupec vašeho souboru, s vaším záhlavím nahoře a prvními pěti
   řádky dat pod ním. Nad každým sloupcem je rozbalovací seznam.
   Parcella už podle záhlaví odhadla odpovídající pole (fungují anglická
   i německá záhlaví, například „Nachname“ nebo „Last name“).
   Zkontrolujte každý rozbalovací seznam, opravte špatné a sloupce,
   které nechcete, nastavte na **— Ignorovat —**. Pak klikněte na
   **Importovat**.

Potom jste zpět na stránce seznamu s krátkým souhrnem: kolik řádků bylo
vytvořeno, aktualizováno nebo přeskočeno, a důvody u prvních několika
přeskočených řádků.

### Jak by měl soubor vypadat {#what-your-file-should-look-like}

- **První řádek obsahuje záhlaví sloupců.** Každý řádek pod ním je jeden
  záznam. Záhlaví nemusí přesně odpovídat -- přiřadíte je v kroku 2.
- **Středník nebo čárka** mezi sloupci: Parcella pozná, kterou váš
  soubor používá.
- **Nejlepší je UTF-8.** Většina tabulkových procesorů nabízí při
  ukládání „CSV UTF-8“. Funguje i obyčejné „CSV“ z Excelu
  (Windows/ANSI): diakritika projde v obou případech.
- **Data** jako `2026-03-15` nebo `15.03.2026` (také `15.03.26`).
- **Desetinná čísla** s čárkou nebo tečkou: `312,5` i `312.5` fungují.
  Bankovní částky a odečty měřidel mohou mít i oddělovače tisíců,
  německy nebo anglicky: `12.345,6` a `12,345.6`.
- **Více hodnot v jedné buňce** (e-mailové adresy, telefonní čísla,
  štítky) se oddělují středníkem. Tabulkový procesor dá při ukládání
  takovou buňku do uvozovek -- to je v pořádku.

!!! tip "Začněte exportem"
    Nejjednodušší šablonou je export z Parcelly. Každý seznam s importem
    má také **CSV export**. Exportujte (ještě prázdný nebo ukázkovými
    daty naplněný) seznam, vyplňte soubor v tabulkovém procesoru a znovu
    ho importujte: záhlaví pak odpovídají bez jakéhokoli mapování.

## 1. Parcely {#1-parcels}

Parcely importujte jako první. Členové, měrná místa a odečty odkazují na
parcely jejich číslem.

1. Otevřete **Parcely** a klikněte na **CSV import**.
2. Vyberte soubor a klikněte na **Importovat**.
3. Na stránce **Mapování sloupců CSV** přiřaďte alespoň **Číslo
   parcely**. Ostatní pole jsou volitelná.
4. Klikněte na **Importovat**. Souhrn zní například *„24 importováno, 0
   přeskočeno“*.

| Pole | Co Parcella očekává |
|---|---|
| **Číslo parcely** | Povinné. Ukládá se velkými písmeny („g12“ se změní na „G12“). |
| **Rozloha (m²)** | Číslo, s čárkou nebo tečkou jako desetinným oddělovačem. Cokoli jiného zůstane prázdné. |
| **Zeměpisná šířka** / **Zeměpisná délka** | Volitelná poloha GPS ve stupních s desetinnou částí (např. `51,339695`). |
| **Stav** | `ACTIVE`, `TERMINATED`, `COMMUNAL` nebo `DELETED` (velkými nebo malými písmeny). Prázdné nebo cokoli jiného znamená aktivní. |
| **Poznámky** | Volný text. |

!!! warning "Existující parcely se přeskočí, neaktualizují"
    Pokud číslo parcely v Parcelle už existuje, řádek se **přeskočí** a
    existující parcela zůstane přesně taková, jaká je. Existující parcely
    měňte ručně. Řádky bez čísla parcely se ignorují a v souhrnu se
    počítají zvlášť.

Import parcel **nepřiřazuje** nájemce. Export parcel má sloupec se jmény
nájemců, ale import ho ignoruje -- viz krok 3 níže.

## 2. Členové {#2-members}

1. Otevřete **Členové** a klikněte na **CSV import**.
2. Vyberte soubor a klikněte na **Importovat**.
3. Na stránce **Mapování sloupců CSV** přiřaďte alespoň **Jméno** a
   **Příjmení**. Bez obou se import zastaví se zprávou *„Před importem
   prosím přiřaďte sloupce jména a příjmení.“*
4. Klikněte na **Importovat**. Souhrn zní například *„80 nově
   importováno, 0 aktualizováno“*.

| Pole | Co Parcella očekává |
|---|---|
| **Jméno**, **Příjmení** | Povinné. Řádek, kde jedno z nich chybí, se přeskočí. |
| **Ulice**, **PSČ**, **Město** | Volný text. |
| **Datum narození** | Datum (viz výše). Slouží také k rozlišení dvou členů se stejným jménem. |
| **IBAN** | Volný text, nekontroluje se. |
| **Členem od**, **Členem do** | Data. Prázdné **Členem do** znamená aktivního člena. |
| **E-mailová upozornění** | „No“, „Nein“, „false“ nebo „0“ znamená, že člen **nechce** dostávat informace spolku e-mailem; cokoli jiného vyplněného znamená ano. Prázdná buňka nebo nepřiřazený sloupec znamená ano u nového člena a „beze změny“ u existujícího. |
| **E-mailové adresy** | Jedna nebo více, oddělené středníky. První se stane hlavní adresou. |
| **Telefonní čísla** | Jedno nebo více, oddělená středníky. První se stane hlavním číslem. |
| **Poznámky** | Volný text. |

**Párování s existujícími členy.** U každého řádku Parcella hledá
existujícího člena se stejným jménem a příjmením -- a pokud má řádek
datum narození, i se stejným datem narození. Pokud najde právě jednoho,
tohoto člena **aktualizuje**, místo aby vytvořila druhého. Pokud má
stejné jméno více členů, vybere toho správného podle e-mailových adres a
telefonních čísel v řádku; pokud řádek stále odpovídá více než jednomu,
přeskočí se a v souhrnu se uvede. Samotný e-mail nebo telefon nikdy
nespáruje člena s jiným jménem.

Aktualizace mění jen to, co řádek obsahuje: sloupec nastavený na **—
Ignorovat —** nebo prázdná buňka ponechá uloženou hodnotu beze změny.
Můžete tedy aktualizovat jen adresy souborem, který obsahuje jen jména a
adresy. E-mailové adresy a telefonní čísla se při aktualizaci nikdy
nemění; přidávají se jen u nových členů.

Štítky, přiřazení k parcelám a nastavení **Nepřeje si narozeninové
dárky** nejsou součástí importu. Export sice obsahuje sloupce **Parcely**
a **Štítky**, ale import je ignoruje.

## 3. Přiřaďte členy k jejich parcelám {#3-assign-members-to-their-parcels}

Import nájmů neexistuje. Jakmile existují členové i parcely, přiřaďte je
ručně:

1. Otevřete parcelu v **Parcely**.
2. V části **Současní nájemci** začněte psát jméno člena do **Vyberte
   člena…** a vyberte ho ze seznamu.
3. Volitelně zadejte datum začátku nájmu.
4. U nájemce, který má dostávat faktury parcely, ponechte zaškrtnuté
   **Použít jako fakturační adresu**.
5. Klikněte na **Přidělit**.

Při mnoha parcelách vás tlačítko **Další** nahoře na stránce parcely
přenese rovnou na další.

Více: [Parcely](../modules/parcels.md).

## 4. Měrná místa {#4-metering-points}

Měrná místa jsou přípojky vody a elektřiny (hlavní měřidlo, jedna pro
každou parcelu, přípojky spolku). Voda a elektřina se importují zvlášť,
každá ve vlastním menu.

1. Otevřete **Voda → Měrná místa** (nebo **Elektřina → Měrná místa**) a
   klikněte na **CSV import**.
2. Vyberte soubor a klikněte na **Importovat**.
3. Přiřaďte sloupce a klikněte na **Importovat**. Přiřazen musí být
   alespoň jeden sloupec.

| Pole | Co Parcella očekává |
|---|---|
| **Typ** | `PARCEL`, `MAIN_METER` nebo `CLUB`. Pokud tento sloupec vůbec nepřiřadíte, každý řádek se počítá jako přípojka parcely. Pokud ho přiřadíte, řádek s prázdným nebo neznámým typem se přeskočí („neplatný typ“). |
| **Číslo parcely** | Povinné u přípojek parcel; musí odpovídat existujícímu číslu parcely, jinak se řádek přeskočí („parcela nenalezena“). |
| **Označení** | Název hlavního měřidla nebo přípojky spolku, např. „Klubovna“. |
| **Číslo měřiče** | Číslo vytištěné na měřidle. |
| **Instalováno** | Datum. |
| **Kalibrováno do** | Jen **rok**, např. `2031`. |
| **Počáteční stav** | Stav při instalaci měřidla. Prázdné znamená 0. |
| **Násobitel** | Obvykle prázdné (= 1). U měřidel, která ukazují jen zlomek skutečné hodnoty, např. `20`. Musí být větší než 0. |

Import měrná místa jen **vytváří**. Parcela, která už pro dané médium má
měrné místo, nebo hlavní měřidlo či přípojka spolku se stejným označením
se přeskočí jako „již existuje“ -- opakovaný import stejného exportu
tedy nic nepokazí. Nová měrná místa jsou vždy zapnutá.

!!! note "Poznámka"
    **Kalibrováno do** je rok. Datum v tomto sloupci (`30.06.2027`,
    `2027-06`, `06/2027`) je také v pořádku: Parcella z něj vezme rok.
    Řádek, jehož hodnota nemá čtyřmístný rok (`06/27`, `brzy`), se
    přeskočí s důvodem „„Kalibrováno do“ není rok“; ostatní řádky se
    importují.

Více: [Voda a elektřina](../modules/metering.md).

## 5. Odečty měřidel {#5-meter-readings}

Odečty se připojují k měrným místům, která už existují; import nikdy
nevytvoří měrné místo.

1. Otevřete **Voda → Odečty** (nebo **Elektřina → Odečty**) a klikněte
   na **CSV import**.
2. Vyberte soubor a klikněte na **Importovat**.
3. Přiřaďte sloupce. Pokud váš soubor nemá sloupec s rokem nebo ho
   některé řádky nechávají prázdný, zadejte rok do **Výchozí rok
   (volitelné)**.
4. Klikněte na **Importovat**.

| Pole | Co Parcella očekává |
|---|---|
| **Typ** | Jako u měrných míst. Nepřiřazeno = každý řádek je přípojka parcely. |
| **Číslo parcely** / **Označení** | Najdou měrné místo, stejně jako výše. |
| **Číslo měřiče** | Volitelná kontrola. Pokud neodpovídá aktuálně instalovanému měřidlu, řádek se přeskočí („neshodné číslo měřiče“) -- pravděpodobně patří měřidlu, které bylo mezitím vyměněno. |
| **Rok** | Rok, ke kterému odečet patří. Má přednost před **Výchozí rok (volitelné)**. |
| **Datum** | Den, kdy byl stav odečten. Povinné. |
| **Stav měřiče** | Hodnota na displeji. Povinné. |
| **Poznámka** | Volný text. |

Parcella nikdy neodhaduje rok z data. Odečet z ledna může stále patřit
k vyúčtování předchozího roku, takže rok určíte vy.

Jeden soubor může obsahovat více let. Pokud měrné místo už má pro daný
rok odečet, import ho **nahradí**.

Odečet, který vypadá nevěrohodně -- například nižší než předchozí --, se
přesto uloží. Souhrn pak ukáže samostatné varování s dotčenými řádky,
abyste je mohli zkontrolovat.

Více: [Odečty měřidel](meter-readings.md).

## 6. Externí kontakty {#6-external-contacts}

Dodavatelé, řemeslníci a úřady, pokud používáte modul **Externí
kontakty**.

1. Otevřete **Externí kontakty** a klikněte na **Import CSV**.
2. Vyberte soubor a klikněte na **Importovat**.
3. Na stránce **Přiřadit sloupce** přiřaďte sloupce. Žádné pole není
   povinné; zcela prázdné řádky se přeskočí.
4. Klikněte na **Importovat**.

| Pole | Co Parcella očekává |
|---|---|
| **Typ (firma/osoba)** | „Firma“, „Company“ nebo „Unternehmen“ pro firmu; „Person“ pro osobu. Bez něj je řádek s jménem nebo příjmením osobou, jinak firmou. |
| **Název firmy** | U firmy: její název. U osoby: firma, ke které patří -- vytvoří se, pokud ještě neexistuje. |
| **Jméno**, **Příjmení**, **Pozice** | U osob. |
| **Ulice**, **PSČ**, **Město**, **IBAN** | Adresa a bankovní údaje. U osoby ve firmě vyplní prázdná pole firmy. |
| **E-mailové adresy**, **Telefonní čísla**, **Štítky** | Více hodnot oddělených středníky. |
| **Poznámky** | Volný text. |

Firma, která už existuje (stejný název, bez ohledu na velká a malá
písmena), nebo osoba se stejným jménem se **aktualizuje** z neprázdných
buněk řádku. Chybějící telefonní čísla, e-maily a štítky se přidají. Na
rozdíl od importu členů se nikdy nic nemaže ani neodstraňuje.

Více: [Externí kontakty](../modules/external-contacts.md).

## Časté problémy {#common-problems}

| Co vidíte | Proč a co dělat |
|---|---|
| *„Tento soubor CSV se zdá být prázdný.“* | Soubor nemá vůbec žádné řádky. Zkontrolujte, že jste uložili správný list. |
| Všechna data skončí na obrazovce mapování v jednom sloupci | Parcella nepoznala oddělovač. Uložte soubor znovu jako „CSV (oddělený středníkem)“ nebo „CSV (oddělený čárkou)“. |
| Podivné znaky místo diakritiky | Soubor používá neobvyklé kódování (ani UTF-8, ani Windows/ANSI, např. ze starého Macu). Uložte ho znovu jako „CSV UTF-8“. |
| Členové přeskočeni s důvodem „chybí jméno nebo příjmení“ | Tyto řádky mají prázdnou buňku jména, nebo sloupec jména nebyl přiřazen. |
| Člen se objeví dvakrát | Oba řádky se liší pravopisem nebo datem narození, takže je Parcella považuje za různé lidi. Duplikát smažte ručně. |
| Adresa existujícího člena je najednou prázdná | Člen byl aktualizován z řádku nebo souboru bez tohoto sloupce. Viz varování v kroku 2; v případě potřeby obnovte ze zálohy. |
| Parcely „přeskočeno“ | Číslo parcely už existuje. Existující parcely upravte ručně. |
| Měrná místa „parcela nenalezena“ | Číslo parcely ze souboru v Parcelle neexistuje -- nejprve importujte parcely a zkontrolujte pravopis („G12“ vs. „G 12“). |
| Odečty „měrné místo nenalezeno“ | Nejprve importujte nebo vytvořte měrná místa. Pokud jste přiřadili **Typ**, zkontrolujte jeho hodnotu. |
| Odečty „neplatný řádek“ | **Datum** nebo **Stav měřiče** je prázdné nebo nesrozumitelné, nebo chybí rok (ani sloupec **Rok**, ani **Výchozí rok (volitelné)**). |
| Odečty „žádný aktivní měřič“ | Měrné místo nemá nainstalované měřidlo. Přidejte ho na stránce měrného místa. |
| Úvodní `'` v exportovaných telefonních číslech | Parcella ho přidává do buněk začínajících na `+`, `-`, `=` nebo `@`, aby je tabulkové procesory nepovažovaly za vzorce. Před importem členů ho odstraňte, nebo ho nechte -- import externích kontaktů ho odstraní sám. |

## Související {#related}

- [Členové](../modules/members.md)
- [Parcely](../modules/parcels.md)
- [Voda a elektřina](../modules/metering.md)
- [Externí kontakty](../modules/external-contacts.md)
- [Založení nového spolku](new-club-setup.md)
- [Odečty měřidel](meter-readings.md)

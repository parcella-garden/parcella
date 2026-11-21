# Odečty měřidel {#collecting-meter-readings}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Jednou ročně někdo obejde areál a odečte každý vodoměr a elektroměr:
hlavní měřidlo spolku, jedno měřidlo na každé parcele a vlastní přípojky
spolku (klubovna, mycí místo). Tento návod popisuje zadávání těchto
odečtů -- v telefonu během obchůzky, nebo později ze seznamu -- a také
výměnu měřidla a kontrolu výsledků.

Voda a elektřina fungují úplně stejně; každá má vlastní menu. Kroky níže
uvádějí **Voda**; pro elektřinu použijte místo toho menu **Elektřina**.

!!! info "Kdo to může dělat"
    Zadávání odečtů vyžaduje oprávnění k **zápisu** u **Voda** (nebo
    **Elektřina**); smazání odečtu vyžaduje **mazání**. Oba moduly jsou
    ve výchozím stavu zapnuté. Spolek může týmu odečítačů dát skupinu s
    přesně těmito právy -- viz [Skupiny](../administration/groups.md).

## Jak Parcella počítá spotřebu {#how-parcella-counts-consumption}

- Každé **[měrné místo](../glossary.md#metering-point)** (přípojka
  parcely, hlavní měřidlo, přípojka spolku) má vždy nainstalované jedno
  **měřidlo**.
- Měřidlo má **jeden odečet za rok**. Roční spotřeba je tento odečet
  minus odečet předchozího roku -- nebo minus **Počáteční stav**
  měřidla, pokud jde o první odečet.
- Zadání odečtu za rok, který už odečet má, ho **nahradí**.
- Odečty se zadávají přesně tak, jak je ukazuje displej. Některé
  elektroměry ukazují jen zlomek skutečné hodnoty; jejich měrné místo
  pak má **Násobitel** (např. 20), kterým vyhodnocení násobí.

## 1. Před obchůzkou: zkontrolujte seznam měrných míst {#1-before-the-round-check-the-list-of-metering-points}

1. Otevřete **Voda → Přehled**. Dlaždice ukazují, kolik existuje
   hlavních měřidel, přípojek parcel a spolku, a **Chybějící měřicí
   body**: parcely bez přípojky vody v Parcelle.
2. Klikněte na **Zobrazit** pod **Chybějící měřicí body** a uvidíte tyto
   parcely; každá odkazuje na **Nové měrné místo** s již vybranou
   parcelou. Přidejte ty, které měřidlo opravdu mají.
3. Přípojka je nějakou dobu bez dodávky (voda zavřená na volné parcele)?
   Otevřete její měrné místo, nastavte **Vypnout od** a klikněte na
   **Vypnout**. Ze seznamu odečtů vypadne, dokud ji **Znovu zapnout**.

Pokud je váš seznam měřidel ještě v tabulce, importujte ho -- viz
[Import členů a parcel](csv-import.md#4-metering-points).

## 2. Možnost A: zadávejte odečty v telefonu během obchůzky {#2-option-a-enter-readings-on-your-phone-while-you-walk}

1. Otevřete v telefonu **Voda → Odečty**. Stránka ukazuje aktuální rok;
   v případě potřeby vyberte jiný v rozbalovacím seznamu roku nahoře.
2. Stránka vypisuje **Hlavní měřidlo**, **Parcely** (seřazené podle čísla
   parcely) a **Přípojky spolku**. Každý řádek ukazuje číslo měřidla a
   pro kontrolu odečet za **Předchozí rok**.
3. Napište odečet do pole v řádku a klepněte na tlačítko uložení vedle
   něj. Řádek pak ukáže hodnotu jako **zaznamenáno**.
4. Pokračujte dalším měřidlem. Řádky bez hodnoty uvádějí **Zatím
   nezadáno**.

Odečty zadané zde dostanou dnešní datum. Chcete-li použít jiné datum
nebo přidat poznámku, zadejte odečet místo toho na stránce měrného místa
(možnost C).

## 3. Možnost B: sbírejte na papír nebo do tabulky, pak importujte {#3-option-b-collect-on-paper-or-in-a-spreadsheet-then-import}

1. Otevřete **Voda → Odečty**, vyberte rok a klikněte na **CSV export**.
   Dostanete soubor s jedním řádkem na měřidlo: **Typ**, **Číslo
   parcely**, **Označení**, **Číslo měřiče**, **Rok** a prázdné sloupce
   **Datum**, **Stav měřiče** a **Poznámka**.
2. Vytiskněte ho nebo vyplňujte na tabletu. U každého odečteného měřidla
   vyplňte **Datum** a **Stav měřiče**.
3. Zpět na **Voda → Odečty** klikněte na **CSV import**, vyberte soubor
   a klikněte na **Importovat**.
4. Na stránce **Mapování sloupců CSV** zkontrolujte přiřazení. Pokud váš
   soubor nemá sloupec s rokem, zadejte ho do **Výchozí rok
   (volitelné)**. Klikněte na **Importovat**.
5. Přečtěte si souhrn na stránce odečtů: kolik odečtů bylo zaznamenáno
   a kolik řádků bylo přeskočeno a proč.

Řádky bez odečtu se přeskočí jako „neplatný řádek“ -- to se u měřidel,
která jste ještě neodečetli, očekává. Podrobnosti ke sloupcům a
chybovým zprávám: [Import členů a parcel](csv-import.md#5-meter-readings).

## 4. Možnost C: zadejte jednotlivý odečet s datem a poznámkou {#4-option-c-enter-a-single-reading-with-date-and-note}

1. Otevřete **Voda → Měrná místa** a klikněte na měrné místo.
2. Dole v části **Odečty** vyplňte **Rok**, **Datum**, **Odečet
   měřidla** a volitelně **Poznámka**.
3. Klikněte na **Zaznamenat odečet**.

Tabulka **Odečty** na téže stránce uvádí každý rok s odečtem a
spotřebou. Chybný odečet tam lze smazat.

## 5. Když odečet vypadá špatně {#5-when-a-reading-looks-wrong}

Odečet nižší než v předchozím roce (nebo vyšší než již zaznamenaný
pozdější) se **přesto uloží**, s varováním jako *„Odečet uložen, ale
zkontrolujte ho prosím: …“* a vysvětlením, že stav měřidla je nižší
než předchozí odečet téhož měřidla a zda nebyl dřívější odečet odhadnut.
Odečet si na stránce odečtů i u měrného místa ponechá značku varování.

Časté příčiny: překlep, špatně přečtená číslice, dřívější odečet
odhadnutý příliš vysoko nebo měřidlo, které bylo ve skutečnosti
vyměněno (krok 6). Hodnotu opravíte opětovným zadáním odečtu za stejný
rok.

## 6. Výměna měřidla {#a-meter-is-replaced}

Když se měřidlo fyzicky vymění -- například proto, že mu končí
kalibrace:

1. Pokud to ještě jde, odečtěte staré měřidlo naposledy a zadejte odečet
   na stránce měrného místa jako odečet za rok (možnost C).
2. V kartě **Aktuální měřidlo vody** (u elektřiny **Aktuální měřidlo
   elektřiny**) otevřete **Vyměnit měřidlo**.
3. Zadejte **Staré měřidlo odstraněno dne**, **Nové měřidlo
   nainstalováno dne**, **Nové číslo**, **Kalibrováno do** (rok) a
   **Počáteční stav** nového měřidla (obvykle to, co ukazuje displej při
   instalaci).
4. Klikněte na **Vyměnit** a potvrďte.

Staré měřidlo se nesmaže: přesune se do **Předchozí měřidla** s daty
instalace a odstranění a s **Poslední odečet**. Od teď jdou odečty k
novému měřidlu, jehož spotřeba začíná od jeho **Počáteční stav**.

!!! tip "Spotřeba v roce výměny"
    Ve formuláři výměny vyplňte **Konečný stav starého měřiče** -- co
    staré měřidlo ukazuje v den odstranění. Roční spotřeba pak sečte
    obě měřidla (staré do výměny, nové od jeho počátečního stavu) a
    tento součet vyúčtuje roční faktura. Bez konečného stavu se podíl
    starého měřidla od jeho posledního odečtu nevyúčtuje.

!!! tip "Překlep, ne nové měřidlo?"
    Pokud jste jen špatně napsali číslo měřidla nebo počáteční stav,
    použijte místo toho **Upravit měřidlo**. **Vyměnit měřidlo** je pro
    skutečnou výměnu.

## 7. Zkontrolujte rok {#7-check-the-year}

1. Otevřete **Voda → Vyhodnocení** a vyberte rok.
2. Dlaždice porovnávají **Hlavní měřidlo** s **Parcely celkem** a
   **Spolek celkem**; tabulky níže vypisují každé měrné místo s jeho
   **Spotřeba**. Místa, kterým ještě chybí odečet, ukazují **žádný
   odečet**.
3. Pokud parcely a přípojky spolku dohromady spotřebovaly více než
   hlavní měřidlo, Parcella ukáže varování. To je normální, dokud se
   odečty ještě zadávají; až budou všechny zadané, ukazuje to na špatně
   odečtené měřidlo.
4. **CSV export** stáhne vyhodnocení pro vaše záznamy nebo pro
   dodavatele.

**Voda → Přehled** vám také řekne, kolika měrným místům ještě chybí
odečet za rok, s odkazem **Zaznamenat nyní →**.

## 8. Nastavte cenu pro vyúčtování {#8-set-the-price-for-billing}

Pokud vodu a elektřinu účtujete ročními fakturami v Parcelle:

1. Otevřete **Voda → Konfigurace**.
2. V části **Nová/aktualizovaná cena** zadejte **Rok** a **Cena za m³**
   a volitelně **Poznámka** (např. „změna sazby dodavatele“).
3. Klikněte na **Uložit**.

Bez ceny za daný rok vyúčtování za tento rok vodu neúčtuje. Pak
pokračujte návodem [Roční vyúčtování](annual-invoicing.md).

## Související {#related}

- [Voda a elektřina](../modules/metering.md)
- [Import členů a parcel](csv-import.md)
- [Roční vyúčtování](annual-invoicing.md)
- [Předání parcely](parcel-handover.md)
- Slovníček: [měrné místo](../glossary.md#metering-point),
  [měřidlo](../glossary.md#meter)

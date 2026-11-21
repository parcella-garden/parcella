# Roční vyúčtování {#running-the-annual-invoices}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Jednou ročně spolek vyúčtuje každou parcelu: nájem, vodu, elektřinu,
pojištění, neodpracované hodiny, případně členský příspěvek nebo
jednorázovou [dávku](../glossary.md#general-levy). V Parcelle je to
[vyúčtování](../glossary.md#invoice-run): jednou definujete položky,
zkontrolujete náhled každé jednotlivé faktury, dokončením přidělíte
čísla faktur a pak je rozešlete -- e-mailem, na papíře nebo do cloudové
složky každé parcely. Potom zaznamenáváte platby a posíláte
[upomínky](../glossary.md#dunning).

!!! info "Kdo to může dělat"
    Vše zde vyžaduje oprávnění k **zápisu** u **Finance**. Modul
    **Finance** je v nové instalaci **vypnutý**; zapněte ho v
    **Administrace → Nastavení → Funkční oblasti** (viz
    [Zapínání a vypínání modulů](../administration/modules.md)).

!!! warning "Dokončení nelze vrátit"
    Dokud vyúčtování nedokončíte, nic se neuloží jako faktura a nic se
    neodešle -- položky můžete měnit, jak často chcete. Dokončení
    přidělí trvalá čísla faktur a vyúčtování uzamkne. Nejprve si
    stáhněte zálohu (**Administrace → Uživatelé → Stáhnout zálohu**).

## 1. Zkontrolujte finanční nastavení (jednou) {#1-check-the-finance-settings-once}

1. Otevřete **Administrace → Nastavení** a najděte **Finanční
   nastavení**.
2. Vyplňte bankovní údaje spolku: **Název banky**, **IBAN**, **BIC**,
   **Majitel účtu**. Zobrazují se v zápatí každé faktury.
3. Zkontrolujte **Formát čísla faktury**. Výchozí je rok a pořadové
   číslo; můžete použít vlastní, například `R-{year}-{number}`.
   `{number}` je povinné.
4. **Další číslo faktury (přepsat)** nechte prázdné, pokud první
   vyúčtování v Parcelle nemusí navázat na dříve používané číslování.
   Použije se jednou a pak se vymaže.
5. Pokud chcete faktury posílat e-mailem, ujistěte se, že je nastaven
   **E-mail (SMTP)**.
6. Klikněte na **Uložit nastavení**.

## 2. Připravte katalog položek (jednou, pak opakovaně používejte) {#2-prepare-the-item-catalog-once-then-reuse}

Katalog položek obsahuje položky, které účtujete každý rok, abyste je
nemuseli definovat znovu pro každé vyúčtování.

1. Otevřete **Finance → Přehled** a klikněte na **Katalog položek**.
2. V části **Nová šablona položky** vyplňte **Pořadí** (pozice na
   faktuře), **Název**, **Popis**, **Způsob výpočtu**, **Jednotková
   cena** a volitelně **Kategorie**.
3. Vyberte, pro koho platí (viz níže), a klikněte na tlačítko **+**.

| Způsob výpočtu | Co účtuje |
|---|---|
| **Pevná částka za parcelu** | Jednotkovou cenu jednou za parcelu -- např. nájem. |
| **Pevná částka za osobu** | Jednotkovou cenu jednou za *člena* -- např. členský příspěvek, i u členů bez parcely. |
| **Za pronajatý m²** | Jednotková cena × rozloha parcely. |
| **Podíl na nájmu společné plochy** | Společná plocha (rozloha B), rozdělená rovnoměrně mezi fakturované parcely, × jednotková cena. |
| **Veřejné dávky (vlastní plocha + podíl na společné ploše)** | Vlastní plocha parcely plus její podíl na společné ploše, × jednotková cena. |
| **Obecná dávka (rozdělena rovnoměrně mezi všechny parcely)** | Jednotková cena je *celková* částka, která se rovnoměrně rozdělí mezi všechny fakturované parcely. |
| **Spotřeba vody (z modulu)** | Spotřeba vody parcely × cena vody za rok. |
| **Spotřeba elektřiny (z modulu)** | Spotřeba elektřiny parcely × cena elektřiny za rok. |
| **Náklady na pojištění (z modulu)** | Pojištění parcely, jeden řádek za každý druh pojištění. |
| **Nedoplatek pracovních hodin (z modulu)** | Chybějící [povinné hodiny](../glossary.md#mandatory-hours) × hodinová sazba. |

**Pro koho položka platí.** Položky podle parcel mají **Platí pro
každou parcelu**; odškrtnutím můžete vybrat jednotlivé **Parcely**.
**Pevná částka za osobu** má místo toho **Platí pro každého člena** a
výběr **Členové**. Čtyři položky „z modulu“ si parcely vybírají samy --
místo výběru se zobrazí **Automaticky (...)** -- a jejich jednotková
cena je **Počítá se automaticky**.

Více: [Vyúčtování](../modules/finances/invoice-runs.md).

## 3. Zkontrolujte čísla, která používají automatické položky {#3-check-the-numbers-the-automatic-items-use}

Položky „z modulu“ berou svá čísla z jiných modulů. Pro rok, který
účtujete, je zkontrolujte **před** dokončením.

**Voda a elektřina**

1. Otevřete **Voda → Konfigurace** a zkontrolujte, že pro daný rok
   existuje cena (**Cena za m³**) (v **Historie cen**). Pokud ne,
   zadejte **Rok** a cenu v **Nová/aktualizovaná cena** a klikněte na
   **Uložit**. Totéž udělejte v **Elektřina → Konfigurace**.
2. Otevřete **Voda → Přehled**. Pokud uvádí, že některá měrná místa
   ještě nemají odečet za daný rok, nejprve je doplňte -- viz
   [Odečty měřidel](meter-readings.md). Parcela bez odečtu za rok
   nedostane žádný řádek za vodu.
3. Otevřete **Voda → Vyhodnocení** za daný rok a hledejte parcely s
   **žádný odečet** nebo nevěrohodnou spotřebou.

**Pracovní hodiny**

1. Otevřete **Pracovní sezení → Sezení a přehled** a zkontrolujte
   **Konfigurace hodin** pro daný rok: povinné hodiny a **Hodinová
   sazba**.
2. Otevřete **Pracovní sezení → Roční hodnocení** za daný rok.
   Zkontrolujte sloupce **Otevřené** a **Dluh** -- to se bude účtovat.
   Chybí docházka, sponzoringy nebo osvobození? Opravte je teď (viz
   [Organizace pracovní směny](work-session.md)).

**Pojištění**

1. Otevřete **Pojištění → Konfigurace** a **Pojištění → Parcely** a
   zkontrolujte ceny za daný rok a pojištění každé parcely.

!!! tip "Kdo dostane fakturu"
    Faktura parcely jde současným nájemcům parcely označeným **Použít
    jako fakturační adresu**. Parcely bez takového nájemce fakturu
    nedostanou. Před dokončením to zkontrolujte na stránkách parcel --
    zvláště po předání.

## 4. Vytvořte vyúčtování {#4-create-the-invoice-run}

1. Otevřete **Finance → Vydané faktury** (stránka se jmenuje **Roční
   vyúčtování**).
2. Klikněte na **Nové vyúčtování**.
3. Zadejte účtovaný **Rok**, **Předmět** (např. „Roční faktura 2026“),
   **Datum vystavení** a **Datum splatnosti**.
4. Volitelně napište **Text patičky**. Může obsahovat
   `{invoice_number}`, `{parcel_number}`, `{invoice_address}` a
   `{due_date}`, které se vyplní pro každou fakturu.
5. Klikněte na **Vytvořit**.

Vyúčtování je **Koncept**. Otevřete ho tlačítkem **Otevřít**.

## 5. Přidejte položky {#5-add-the-line-items}

1. Na stránce vyúčtování v části **Přidat z katalogu položek**
   zaškrtněte položky katalogu pro tento rok a klikněte na **Přidat
   vybrané položky**.
2. Cokoli, co se účtuje jen letos, vyplňte dole v **Přidat položku**,
   stejně jako v katalogu.
3. Zkontrolujte tabulku **Definice položek**: pořadí, ceny, pro koho
   která položka platí. Dokud je vyúčtování konceptem, můžete položky
   ještě upravovat nebo mazat.

## 6. Náhled {#6-preview}

1. Klikněte na **Náhled** nahoře na stránce vyúčtování.
2. Stránka uvádí, kolik faktur by se vytvořilo, a vypisuje je v
   **Vypočtené faktury** s příjemcem a mezisoučtem.
3. Několik jich otevřete tlačítkem **PDF** a zkontrolujte: adresu,
   položky, částky, patičku.
4. Chcete-li něco opravit, jděte **Zpět na vyúčtování**, změňte položky
   a zobrazte náhled znovu. Zatím se nic neuložilo ani neodeslalo.

Pokud se zobrazí *„Nebyly by vytvořeny žádné faktury“*, zkontrolujte
rozsah parcel u položek a příznak **Použít jako fakturační adresu** u
nájemců.

## 7. Dokončení {#7-finalize}

1. Na stránce náhledu klikněte na **Dokončit a přidělit čísla faktur** a
   potvrďte.
2. Parcella vytvoří faktury s trvalými čísly. Stránka vyúčtování teď
   uvádí, že je dokončené, a vypisuje **Faktury**.

Jména a adresy příjemců se u každé faktury uloží v podobě z tohoto
okamžiku. Pozdější změny adres dokončené faktury nepřepisují.

## 8. Rozešlete faktury {#8-send-the-invoices}

1. Na stránce dokončeného vyúčtování najděte kartu **Doručení**.
2. Klikněte na **Odeslat e-maily a nahrát do cloudu**.
    - Faktury se pošlou e-mailem (s PDF v příloze) příjemcům faktur,
      kteří mají **Může dostávat informace e-mailem** a e-mailovou
      adresu.
    - Pokud má parcela složku dokumentů v cloudovém úložišti, faktura se
      nahraje i tam.
    - Opětovné kliknutí odešle jen to, co ještě odesláno nebylo.
3. Klikněte na **Stáhnout tiskový balíček**. Obsahuje dopis pro každého
   nájemce, který faktury e-mailem nedostává, jako jedno PDF k tisku a
   odeslání poštou: jeden dopis na adresu, s uvedením lidí na ní bez
   e-mailu. Patří sem i ten, jehož spolubydlící dostal e-mail. Ti se
   pak označí jako zahrnutí do tiskového balíčku.

Sloupec **Doručení** ukazuje u každé faktury, zda byla **Odesláno
e-mailem**, **Zahrnuto v tiskovém balíčku** nebo **Nahráno do cloudového
úložiště**. Chcete-li jednu fakturu odeslat znovu, otevřete ji a
klikněte na **Znovu odeslat e-mail**.

Více: [Faktury, platby a upomínky](../modules/finances/invoices.md).

## 9. Zaznamenejte platby {#9-record-payments}

**Ručně**

1. Otevřete vyúčtování (nebo **Všechny faktury** na stránce **Roční
   vyúčtování** pro hledání napříč vyúčtováními podle čísla faktury,
   příjemce nebo částky).
2. Klikněte na **Platba** v řádku faktury.
3. Zadejte **Částka**, **Uhrazeno dne**, volitelně **Poznámka** a
   **Účet**, na který platba přišla, a klikněte na **Přidat platbu**.

Částečné platby jsou v pořádku; stav se sám mění z **Otevřená** na
**Částečně uhrazená** a na **Uhrazená**.

**Z bankovního výpisu**

1. Jednou: otevřete **Finance → Přehled → Účty** a přidejte svůj
   bankovní účet v **Nový účet**.
2. Klikněte na **Zápisy** vedle účtu a pak na **Import CSV**.
3. Nahrajte výpis exportovaný z internetového bankovnictví. Na stránce
   **Mapování sloupců CSV** přiřaďte alespoň **Datum** a **Částka**;
   **Popis**, **Odesílatel / příjemce** a **IBAN** pomáhají s
   párováním.
4. Na stránce **Přiřadit řádky k fakturám** navrhne Parcella pro každou
   příchozí platbu otevřené faktury se stejnou částkou. Vyberte
   správnou, chcete-li platbu zaznamenat u této faktury, nebo zvolte
   **Zaznamenat jako obecnou platbu**.
5. Kliknutím na **Import CSV** dole na stránce vytvoříte zápisy a
   platby.

Více: [Bankovní účty a zaúčtování](../modules/finances/bank-accounts.md).

## 10. Rozešlete upomínky {#10-send-reminders}

1. Po datu splatnosti otevřete **Finance → Upomínky**. **Faktury po
   splatnosti** uvádí každou nezaplacenou fakturu po splatnosti s
   údajem, jak dlouho je po splatnosti a kolik upomínek bylo odesláno.
2. Klikněte na **Otevřít** vedle faktury.
3. Volitelně zadejte **Poplatek (volitelné)** a **Zpráva (volitelné)**.
4. Klikněte na **Odeslat upomínku**.

Parcella vytvoří další upomínku jako PDF (**Upomínka č. 1**, **č. 2**,
…), přičte poplatek k dlužné částce a pošle ji e-mailem, pokud člen
s e-mailem souhlasil; jinak se označí **K tisku/poštovnímu odeslání**,
abyste ji vytiskli a poslali poštou. Pevné stupně upomínek neexistují --
kdy poslat další, rozhodujete vy.

## Související {#related}

- [Finance](../modules/finances/index.md)
- [Vyúčtování](../modules/finances/invoice-runs.md)
- [Faktury, platby a upomínky](../modules/finances/invoices.md)
- [Bankovní účty a zaúčtování](../modules/finances/bank-accounts.md)
- [Kategorie, rozpočet a přehled](../modules/finances/bookkeeping.md)
- [Voda a elektřina](../modules/metering.md)
- [Pracovní hodiny](../modules/work-hours.md)
- [Pojištění](../modules/insurance.md)
- [Odečty měřidel](meter-readings.md)

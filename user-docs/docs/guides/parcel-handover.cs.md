# Předání parcely {#handing-over-a-parcel}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Nájemce dá výpověď, parcela se prohlédne a ocení, nabídne se lidem z
pořadníku a nakonec nový nájemce podepíše a dostane klíče. Trvá to
týdny nebo měsíce a podílí se na tom několik členů výboru. Tento návod
ukazuje, co Parcella cestou zaznamenává a jak
[proces](../glossary.md#process) hlídá kroky, které sama nezaznamenává.

## Co Parcella eviduje -- a co ne {#what-parcella-does-and-doesnt-track}

| Část předání | V Parcelle |
|---|---|
| Výpověď | Stav parcely **ukončená**, s automaticky zaznamenaným datem a volitelnou **Poznámka k ukončení**. |
| Starý a nový nájemce | Ukončení starého [nájmu](../glossary.md#tenancy) ho zachová jako historii; nový nájem začíná dnem předání. **Přidělit parcelu** u přihlášky udělá obojí v jednom kroku. |
| Členství starého nájemce | Skončí automaticky s **Přidělit parcelu**, pokud nemá jinou parcelu. |
| Složka dokumentů | Cloudová složka starých nájemců se ke dni předání vyřadí; převezme ji nová. |
| Prohlídka, [ocenění](../glossary.md#valuation), nabídka, prohlídka zájemců, smlouva, klíče | Není zabudováno. Evidujte je pomocí **procesu** (krok 1). |
| [Kauce](../glossary.md#deposit) | Žádná funkce pro kauce. Částku a datum si poznamenejte v procesu; peníze zaúčtujte ve **Finance**, pokud je používáte (krok 7). |
| Konečné odečty měřidel | Parcella uchovává **jeden odečet na měřidlo a rok**. Odečty při předání si poznamenejte v procesu (krok 6). |
| Cena mezi starým a novým nájemcem | **Záměrně se neeviduje.** Kolik nový nájemce zaplatí starému za chatku a rostliny, je soukromá věc mezi nimi dvěma. Parcella pro to nemá žádné pole -- nepřidávejte ho ani do šablony procesu. |

!!! info "Kdo to může dělat"
    Změny parcel a nájmů vyžadují **zápis** u **Členové a parcely**;
    **Přidělit parcelu** vyžaduje navíc **zápis** u **Uchazeči**. Šablony
    procesů vyžadují plný přístup (výbor nebo administrátor); práce s
    procesem vyžaduje **zápis** u **Procesy**.

## 1. Připravte šablonu procesu předání (jednou) {#1-prepare-a-handover-process-template-once}

Modul **Procesy** obsahuje ukázkovou šablonu **Předání zahrádky**.
Vyjděte z ní a přizpůsobte ji postupu svého spolku.

1. Otevřete **Procesy → Šablony** (stránka se jmenuje **Šablony
   procesů**).
2. V části **Začít příkladem** klikněte na **Použít** vedle **Předání
   zahrádky**. Parcella vytvoří běžnou šablonu, kterou můžete libovolně
   měnit. Týká se typu **Zahrádka**, takže každý proces patří k jedné
   parcele a zobrazuje se na její stránce.
3. Příklad má šest fází: **Prohlídka**, **Ocenění**, **Inzerát**,
   **Nový nájemce**, **Smlouva a kauce** a **Předání**. Aby odpovídal
   obvyklému postupu níže, přidejte a přejmenujte fáze v editoru
   (napište **Název fáze** a klikněte na **Přidat**; fáze přetažením
   přeřadíte; pole přidáte napsáním popisku a stiskem Enter):

| Fáze | Příklady polí | Typ pole |
|---|---|---|
| Výpověď *(nová, první)* | Výpověď přijata dne (povinné) · Výpovědní dopis | Datum · Soubory (PDF, fotky) |
| **Prohlídka** | **Datum prohlídky** · **Zjištěné závady** · **Fotky závad** · **Všechny závady odstraněny** | z příkladu |
| **Ocenění** | **Odhadce** · **Datum ocenění** · **Posudek** | z příkladu |
| **Inzerát** → přejmenovat na „Nabídka pořadníku“ | **Text inzerátu** · **Zveřejněno dne** | z příkladu |
| Prohlídka zájemců *(nová)* | Datum prohlídky · Zájemci (poznámky) | Datum · Dlouhý text |
| **Nový nájemce** | **Nový nájemce** (uchazeč) · **Kontakt navázán** · **Dokumenty odeslány** | z příkladu |
| **Smlouva a kauce** | **Kupní smlouva potvrzena** · **Kauce** · **Kauce přijata dne** | z příkladu |
| **Předání** → rozdělit na „Podpis“ a „Závěrečný kontrolní seznam“ | Podpis: **Podepsáno novým nájemcem**, **Spolupodepsáno výborem**. Závěrečný kontrolní seznam: **Klíče předány**, **Měřiče odečteny**, **Předávací protokol** | z příkladu |

4. Do fáze „Závěrečný kontrolní seznam“ přidejte pole typu **Číslo** pro
   odečty měřidel při předání, např. „Stav vodoměru při předání“ a
   „Stav elektroměru při předání“ (viz krok 6).

Pole označte jako **Povinné**, pokud proces nesmí bez něj pokračovat.
Změny šablony ovlivní jen procesy zahájené poté.

!!! tip "Tip"
    **Kupní smlouva potvrzena** je jen zaškrtávací políčko: výbor
    potvrzuje, že se starý a nový nájemce dohodli. Samotná cena zůstává
    mezi nimi dvěma.

Více: [Procesy](../modules/processes.md).

## 2. Zaznamenejte výpověď {#2-record-the-notice}

Když přijde výpověď nájemce:

1. Otevřete parcelu v **Parcely** a klikněte na **Upravit**.
2. Nastavte **Stav** na **ukončená**. Parcella zaznamená čas změny
   stavu; stránka parcely pak ukazuje **Ukončena dne**.
3. Volitelně přidejte **Poznámka k ukončení** (důvod, datum výpovědi,
   poznámky).
4. Klikněte na **Uložit změny**.

Nájemce zůstává současným nájemcem -- a dál dostává faktury parcely --,
dokud nájem skutečně neskončí. Nájem teď neukončujte; to udělá
**Přidělit parcelu** ke dni předání (krok 5).

## 3. Zahajte proces {#3-start-the-process}

1. Na stránce parcely v kartě **Procesy** klikněte na **Zahájit proces**.
2. Vyberte svou **Šablona** předání. Volitelně dejte procesu **Název**.
3. Klikněte na **Zahájit**.
4. Vyplňte pole první fáze a klikněte na **Uložit**. Když je fáze
   hotová, klikněte na **Hotovo -- další fáze**.

Proces se objeví na stránce parcely se svou aktuální fází a v
**Procesy** pro všechny, kdo na něm pracují. Nahrané soubory (dopisy,
fotky, posudek) jdou do cloudové složky parcely, pokud je nastavena,
jinak do vlastního úložiště Parcelly.

Chcete-li se vrátit k dřívější fázi, klikněte na **Vrátit se**, vyberte
fázi a uveďte **Důvod**. Pokud předání padne, použijte **Přerušit
proces** s důvodem.

## 4. Prohlídka, ocenění, nabídka, prohlídka zájemců {#4-inspection-valuation-offer-viewing}

Procházejte tyto fáze v procesu, jak probíhají. Posudek o
[ocenění](../glossary.md#valuation) patří do **Posudek**; text nabídky
do **Text inzerátu**.

Zájemce najdete v **Uchazeči** s filtrem **Otevřené** -- seznam je
seřazený podle data přihlášky. Těm, kterým parcelu nabídnete, nastavte
**Zahrada nabídnuta**, a tomu, kdo ji vezme, **Přijato**. Se zapnutým
modulem **Oznámení** zaškrtněte více uchazečů a klikněte na **Napsat
vybraným uchazečům**, abyste nabídku poslali e-mailem.

Více: [Uchazeči](../modules/applicants.md).

## 5. Předejte parcelu novému nájemci {#5-hand-the-parcel-over-to-the-new-tenant}

Jakmile je smlouva podepsaná -- nebo s budoucím datem, jakmile je
pevně dané:

1. Otevřete přihlášku nového nájemce a klikněte na **Přidělit parcelu**.
2. Vyberte tuto parcelu v **Ukončená parcela** a nastavte **Datum
   předání**.
3. Pokud parcelu přebírá spolu s partnerem, přidejte ho v **Další
   uchazeči (spolunájemci)**.
4. Pokud používáte cloudové úložiště, zadejte **Složka dokumentů pro
   nové nájemce**. Složka starých nájemců se ke dni předání vyřadí v
   každém případě.
5. Klikněte na **Náhled**, zkontrolujte staré a nové nájemce, pak
   klikněte na **Předat parcelu** a potvrďte.

Ke dni předání:

- starý nájem skončí a přesune se do **Bývalí nájemci** na stránce
  parcely;
- starý nájemce bez jiné parcely odchází ze spolku (**Členem do** je den
  před datem předání);
- z uchazečů se stanou členové, nájemci a příjemci faktur;
- parcela je opět **aktivní**.

Podrobnosti a doplnění záznamu nového člena najdete v návodu
[Přijetí nového člena](new-member.md), kroky 5 a 6.

### Pokud nový nájemce není uchazeč {#if-the-new-tenant-isnt-an-applicant}

Například člen rodiny, který parcelu přebírá. Udělejte to ručně:

1. Na stránce parcely v **Současní nájemci** klikněte na ikonu tužky
   vedle starého nájemce (**Upravit nájem**), nastavte **Nájemce do** na
   poslední den a klikněte na **Uložit změny**. Nebo, chcete-li nájem
   ukončit dnes, klikněte na ikonu **Ukončit nájem** a potvrďte
   *„Ukončit toto nájemné? (historie zůstává zachována)“*.
2. Pokud starý nájemce odchází ze spolku, otevřete jeho stránku člena,
   klikněte na **Upravit**, nastavte **Členem do** a klikněte na
   **Uložit změny**. Nemažte ho -- viz varování níže.
3. Přidělte nového nájemce: **Vyberte člena…**, datum začátku, **Použít
   jako fakturační adresu**, **Přidělit**. V případě potřeby ho nejprve
   vytvořte v **Členové → Nový člen**.
4. Upravte parcelu a nastavte **Stav** zpět na **aktivní**.

!!! tip "Zaznamenání výpovědi"
    Nájemce, který dal výpověď, zůstává fakturační adresou, dokud
    neodejde: nastavte mu **Nájemce do** v **Upravit nájem** a nechte
    zaškrtnuté **Použít jako fakturační adresu**. Jakmile ten den
    uplyne, políčko se samo zruší -- do té doby zajistěte, aby
    fakturační adresou byl nový nájemce.

!!! warning "Ukončit, ne smazat"
    Ukončení nájmu nebo členství zachová historii: kdo měl kterou
    parcelu kdy a které hodiny a faktury patřily komu. Smazání člena ho
    odstraní ze všech vyhodnocení, včetně pracovních hodin z let, kdy byl
    nájemcem.

## 6. Konečné odečty měřidel {#6-final-meter-readings}

Parcella ukládá jeden odečet na měřidlo a rok a z tohoto odečtu vychází
roční faktura. Samostatný „odečet při předání“ neexistuje.

- Odečty ze dne předání zapište do procesu (fáze „Závěrečný kontrolní
  seznam“ z kroku 1) a zaškrtněte **Měřiče odečteny**.
- Nezadávejte je jako roční odečet na měrném místě, pokud to opravdu
  nechcete: roční odečet později v roce ho **nahradí**.
- Roční faktura za vodu a elektřinu pro parcelu jde tomu, kdo je
  příjemcem faktur v okamžiku dokončení
  [vyúčtování](../glossary.md#invoice-run) -- po předání tedy novému
  nájemci -- za spotřebu celého roku. Jak si ji starý a nový nájemce
  rozdělí, je na nich a na pravidlech vašeho spolku; vyřešte to mimo
  Parcellu pomocí odečtů v procesu.

Pokud se při předání měřidlo vyměňuje, viz
[Odečty měřidel](meter-readings.md#a-meter-is-replaced).

## 7. Kauce a peníze {#7-deposit-and-money}

Parcella nemá u parcely ani u člena pole pro kauci. Pro záznam použijte
proces: **Kauce** (částka) a **Kauce přijata dne** ve fázi **Smlouva a
kauce**.

Pokud používáte modul **Finance**, zaúčtujte i samotné peníze:

- **Přijatá kauce**: otevřete **Finance → Přehled → Účty**, klikněte na
  **Zápisy** vedle účtu, na který peníze přišly, a použijte **Přidat
  zápis** (nebo **Import CSV** s výpisem z banky).
- **Vrácení kauce starému nájemci**: totéž se zápornou částkou.

<!-- TODO(verify): confirm with the treasurer whether a deposit should rather be billed as a one-off invoice run (a "Fixed amount per parcel" item scoped to this parcel) so it gets an invoice number. -->

**Pracovní hodiny.** Nájemce, který odejde v průběhu roku, stále dluží
[povinné hodiny](../glossary.md#mandatory-hours) za tento rok. Při
vyúčtování po parcelách se jeho hodiny počítají společně s hodinami
nového nájemce a chybějící hodiny se vyúčtují příjemci faktur parcely v
době vyúčtování -- novému nájemci. Pokud to váš spolek nechce, vyřešte
to ručně. Viz [Roční vyúčtování](annual-invoicing.md).

**Otevřené faktury** starého nájemce zůstávají, jak jsou; číslo faktury,
příjemce a adresa zůstávají uloženy u každé faktury, takže je můžete
dál vymáhat a upomínat.

## 8. Uzavřete proces {#8-close-the-process}

Když je poslední fáze hotová, klikněte na **Dokončit proces**. Dokončený
proces je jen pro čtení a zůstává na stránce parcely i s celou
**Historie**.

## Související {#related}

- [Parcely](../modules/parcels.md)
- [Uchazeči](../modules/applicants.md)
- [Členové](../modules/members.md)
- [Procesy](../modules/processes.md)
- [Voda a elektřina](../modules/metering.md)
- [Bankovní účty a zaúčtování](../modules/finances/bank-accounts.md)
- [Přijetí nového člena](new-member.md)
- Slovníček: [kauce](../glossary.md#deposit),
  [ocenění](../glossary.md#valuation),
  [výpověď](../glossary.md#notice-of-termination),
  [nájem](../glossary.md#tenancy)

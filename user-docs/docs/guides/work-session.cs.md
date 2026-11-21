# Organizace pracovní směny {#organising-a-work-session}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Většina spolků žádá od každé parcely (nebo každého člena) určitý počet
[povinných hodin](../glossary.md#mandatory-hours) společné práce ročně
-- stříhání živého plotu, opravy cest, jarní úklid. Tento návod provede
jednu [pracovní směnu](../glossary.md#work-session) od plánování po
vyhodnocení na konci roku: vytvoříte ji, necháte členy přihlásit se na
webu spolku, zaznamenáte, kdo skutečně přišel, a uvidíte, kdo ještě
dluží hodiny.

!!! info "Kdo to může dělat"
    Vytváření směn a zaznamenávání docházky vyžaduje oprávnění k
    **zápisu** u **Pracovní sezení**; odebrání účastníka nebo převodu
    vyžaduje **mazání**. Modul (**Správa pracovních hodin**) je ve
    výchozím stavu zapnutý. Zveřejnění na webu vyžaduje jednorázové
    nastavení administrátorem v kroku 3.

## 1. Nastavte pravidla roku (jednou ročně) {#1-set-the-years-rules-once-a-year}

1. Otevřete **Pracovní sezení → Sezení a přehled**. Pokud rok ještě
   nemá pravidla, stránka uvádí *„Pro … zatím neexistuje konfigurace
   povinných hodin.“* -- klikněte na **Vytvořit nyní →** (nebo dole na
   **Konfigurace hodin**).
2. V části **Vytvořit / aktualizovat rok** zadejte:
    - **Rok**
    - **Celkové povinné hodiny** -- hodiny dlužné za rok;
    - **Hodinová sazba** -- kolik stojí neodpracovaná hodina;
    - **Fakturační režim** -- **Na nájem / parcelu** (všichni nájemci
      parcely odpracovávají hodiny společně) nebo **Na člena** (každý
      člen sám za sebe);
    - volitelně **Poznámka**, např. usnesení členské schůze.
3. Klikněte na **Uložit**.

Na téže stránce karta **Potvrzovací e-mail k přihlášce** řídí e-mail,
který členové dostanou po přihlášení na webu (krok 3).

**Osvobození.** Členové výboru, lidé se zdravotními důvody nebo nad
určitou věkovou hranicí bývají často osvobozeni. Nastavíte to v
**Sezení a přehled → Role ve spolku**: vytvořte roli s **Osvobozen od
povinných hodin** a **Důvod osvobození** a pak k ní na daný rok přiřaďte
členy. Je-li osvobozen jeden nájemce parcely, je osvobozena celá
parcela; osvobození platí pro celý kalendářní rok.

## 2. Vytvořte směnu {#2-create-the-session}

1. Otevřete **Pracovní sezení → Sezení a přehled** a klikněte na **Nové
   sezení**.
2. Vyplňte:
    - **Název**, např. „Jarní úklid“;
    - **Typ**: **Standard (plánované)** pro směny, které ohlašujete,
      nebo **Speciál (spontánní)** pro neplánované -- speciální směny se
      na webu nikdy nezobrazí;
    - **Datum**, **Od** a **Do**;
    - **Max. účastníků** -- prázdné znamená bez omezení;
    - **Uzávěrka přihlášek (dní předem)** -- přihlašování na webu se
      uzavře tolik dní před směnou (1 = den předem); prázdné znamená, že
      se uzavře, až směna proběhne;
    - **Hodiny na účastníka** -- připíšou se každému, kdo se zúčastní,
      později lze upravit pro každou osobu;
    - **Popis** -- úkoly, nářadí, co si přinést.
3. Klikněte na **Vytvořit sezení**.

Směna se zobrazí v seznamu **Pracovní sezení …** pro svůj rok.

## 3. Zveřejněte přihlašování na webu spolku (jednorázové nastavení) {#3-publish-the-sign-up-on-the-club-website-one-time-setup}

Členové se přihlašují na webu spolku svým **číslem parcely** a
volitelně jménem -- bez přihlášení do Parcelly. Web nikdy neukazuje,
kteří členové mají kterou parcelu.

Administrátor to jednou nastaví:

1. **Administrace → Nastavení → Funkční oblasti**: zaškrtněte **Veřejné
   API pro přihlášky** a klikněte na **Uložit nastavení**. Ve výchozím
   stavu je vypnuté, protože otevírá veřejný formulář.
2. **Administrace → Integrace → Veřejné API pro přihlášky**: poznamenejte
   si **API token** (pro konektor na straně serveru) a přidejte svůj web
   do **Povolené adresy webů** (např. `https://example.org`), pak
   **Uložit adresy**. Volitelně zaškrtněte **Vyžadovat ALTCHA** proti
   spamu.
3. Na web přidejte přihlašovací formulář -- pomocí pluginu Parcella
   Connector pro WordPress nebo jednoduchého HTML formuláře pro jakýkoli
   jiný web. Správce vašeho webu najde podrobnosti v dokumentaci pro
   vývojáře.
   <!-- TODO(verify): link to the gardeners/website-form instructions once that page exists. -->

Poté se každá nová **Standard** směna zobrazí na webu sama, dokud
neuplynulo její datum, neuplynula uzávěrka přihlášek a není plná.

**Co se stane při přihlášení.** Parcella vyhledá současné nájemce
parcely. Pokud zadané jméno odpovídá právě jednomu z nich, přihlásí se
jen tento člen. Pokud jméno nebylo zadáno nebo jednoznačně neodpovídá,
přihlásí se **všichni** současní nájemci parcely, s poznámkou, která
výbor žádá o kontrolu -- odeberte ty, kdo se ve skutečnosti
nepřihlásili. Každý nově přihlášený člen dostane potvrzovací e-mail na
adresu uloženou v Parcelle (ne na tu zadanou do formuláře).

Více: [Integrace](../administration/integrations.md) a
[Pro zahrádkáře](../gardeners/index.md).

## 4. Sledujte přihlášky {#4-keep-an-eye-on-sign-ups}

- Nová přihlášení ukazují počítadlo vedle **Pracovní sezení** v
  postranním panelu a na dashboardu.
- Otevřete směnu (klikněte na ni v seznamu na **Sezení a přehled**).
  Noví účastníci mají odznak **Nový**. Jakmile jste je prohlédli,
  klikněte na **Označit jako zkontrolováno**.
- Zkontrolujte sloupec **Poznámka**: přihlášky z webu tam mají poznámky
  a kontaktní údaje návštěvníka a varování, pokud byla přihlášena celá
  parcela.
- Chcete-li někoho přidat ručně (přihlášení telefonem), použijte
  **Vyberte člena…** dole v tabulce účastníků, zvolte **Zaregistrován**
  a klikněte na **Přidat**.

**Úkoly (volitelné).** Pokud vedete seznam prací v **Pracovní sezení →
Úkoly**, naplánujte tam některé na tuto směnu. Na stránce směny pak
můžete každý přidělit účastníkovi (**Přiděleno komu**) a vidět jeho
**Náročnost** (**Lehká**, **Střední**, **Náročná**). **Spravovat úkoly**
vede na úplný seznam.

## 5. V den směny: vytiskněte seznam účastníků {#5-on-the-day-print-the-attendee-sheet}

1. Otevřete směnu a klikněte na **Seznam účastníků**.
2. Vytiskněte PDF. Uvádí každého přihlášeného účastníka s parcelou,
   jménem, očekávanými hodinami, přiděleným úkolem a řádkem pro podpis.

Hodiny podle potřeby opravte na papíře; do aplikace je zadáte potom.
Seznam v Parcelle nic nemění.

## 6. Potom: zaznamenejte docházku {#6-afterwards-record-attendance}

1. Otevřete směnu.
2. U každého účastníka vyberte v rozbalovacím seznamu **Stav** možnost
   **Zúčastnil se** nebo **Nedostavil se**. Uloží se okamžitě.
3. Pokud někdo pracoval více nebo méně než **Hodiny na účastníka**,
   napište skutečné hodiny do jeho pole **Hodiny** a klikněte na
   tlačítko ✓.
4. Lidé, kteří přišli bez přihlášení: **Vyberte člena…**, stav
   **Zúčastnil se**, jejich hodiny, **Přidat**.
5. Pole hledání nad tabulkou vám pomůže najít někoho podle jména nebo
   čísla parcely.

Do hodin se počítají jen účasti se stavem **Zúčastnil se**.

## 7. Sponzoringy a převody hodin {#7-sponsorships-and-hours-transfers}

**[Sponzoringy](../glossary.md#sponsorship)** jsou oblasti, o které se
člen stará celý rok (živý plot, hřiště) místo účasti na směnách nebo
navíc k ní.

1. Otevřete **Pracovní sezení → Sponzoringy**.
2. V části **Vytvořit sponzoring / přidat člena** zadejte **Oblast**,
   **Člen** (nebo ponechte **– zatím nepřiděleno –**, chcete-li oblast
   nejprve nabídnout), **Popis**, **Připsané hodiny/rok** a **Platné
   od** / **Platné do**.
3. Klikněte na **Uložit**.

Sponzoring připisuje hodiny, až když má datum **Platné od** a člena.
Oblast může sdílet více členů -- přidejte řádek pro každého člena se
stejným názvem oblasti; každý dostane plné připsání.

**[Převody hodin](../glossary.md#hours-transfer)**: člen, který
odpracoval víc, než musel, může hodiny darovat někomu jinému.

1. Otevřete **Pracovní sezení → Převod hodin**.
2. V části **Převést hodiny** vyberte **Od (předává)**, **Komu
   (přijímá)**, **Hodiny** a volitelně **Poznámka**.
3. Klikněte na **Převést hodiny**.

Darovat lze jen přebytek dárce za daný rok. Členové bez parcely a
osvobození členové mohou darovat všechny své hodiny.

## 8. Vyhodnocení na konci roku {#8-the-year-end-evaluation}

1. Otevřete **Pracovní sezení → Roční hodnocení** a vyberte rok.
2. Každý řádek je parcela (nebo člen, podle **Fakturační režim**) s
   údaji **Požadováno**, **Sezení**, **Sponzoring**, **Převody**,
   **Celkem**, **Otevřené** a **Dluh** a se **Stav** **Splněno**,
   **Otevřené** nebo **Osvobozeno**.
3. Kliknutím na šipku na začátku řádku (**Zobrazit pracovní sezení**)
   uvidíte, ze kterých směn hodiny pocházejí.
4. **CSV export** stáhne vyhodnocení.

Nájemci, kteří v průběhu roku odešli, stále dluží hodiny za tento rok;
jejich řádek nese odznak „pacht ukončen …“.

Chcete-li otevřené hodiny vyúčtovat, přidejte do ročního vyúčtování
položku **Nedoplatek pracovních hodin (z modulu)** -- viz
[Roční vyúčtování](annual-invoicing.md).

## Související {#related}

- [Pracovní hodiny](../modules/work-hours.md)
- [Kalendář](../modules/calendar.md)
- [Integrace](../administration/integrations.md)
- [Roční vyúčtování](annual-invoicing.md)
- Slovníček: [povinné hodiny](../glossary.md#mandatory-hours),
  [osvobození](../glossary.md#exemption),
  [sponzoring](../glossary.md#sponsorship),
  [převod hodin](../glossary.md#hours-transfer)

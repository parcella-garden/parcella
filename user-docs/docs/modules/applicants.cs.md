# Uchazeči {#applicants}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Seznam uchazečů je pořadník vašeho spolku na volné zahrádky. Přihlášky z
formuláře na vašem webu sem přicházejí samy; můžete zadávat i přihlášky,
které přišly telefonicky nebo na papíře. Sledujete, koho jste
kontaktovali a komu jste nabídli zahrádku, a když se zahrádka uvolní,
předáte ji -- uchazeč se v jednom kroku stane členem i novým nájemcem.

Uchazeči jsou záměrně vedeni odděleně od seznamu členů. Většina
uchazečů zahrádku nikdy nedostane, takže jejich údaje nesmějí skončit v
počtech členů, fakturách, pracovních hodinách ani rozesílkách.

!!! info "Kdo to může používat"
    Modul **Uchazeči** je ve výchozím stavu zapnutý. Vypnout ho lze v
    části [Zapínání a vypínání modulů](../administration/modules.md).

    - **Prohlížení** seznamu a přihlášek vyžaduje oprávnění ke *čtení*
      u **Uchazeči**.
    - **Přidání** uchazeče, **úprava** kontaktních údajů, stavu a
      poznámky výboru a **kontaktování** nového uchazeče vyžadují
      oprávnění k *zápisu*.
    - **Trvalé smazání** uchazeče vyžaduje oprávnění k *mazání*.
    - **Přidělit parcelu** vyžaduje oprávnění k *zápisu* u **Uchazeči**
      i **Členové a parcely**.

    Členové výboru a administrátoři mají všechna tato oprávnění. Skupina
    je může udělit i dalším, např. tomu, kdo má na starosti přidělování
    zahrádek (viz [Skupiny](../administration/groups.md)).

    Přihlášky z vašeho webu přicházejí, jen dokud je zapnutý samostatný
    modul **Veřejné API formuláře přihlášek**. Ve výchozím stavu je
    vypnutý, protože umožňuje lidem mimo spolek zapisovat do Parcelly.
    Viz [Přihlášky z vašeho webu](#applications-from-your-website).

## Kde si všimnete nových přihlášek {#where-you-notice-new-applications}

- Položka **Uchazeči** v hlavním menu ukazuje červené číslo: přihlášky,
  na které se zatím nikdo nepodíval (stav **Nová**). Zmizí, jakmile je
  každá nová přihláška posunuta do jiného stavu.
- [Dashboard](../getting-started/dashboard.md) má kartu **Nové
  přihlášky** se stejným číslem, „zatím nevyřízené“. Otevře seznam
  vyfiltrovaný na nové přihlášky.

Parcella výboru o nové přihlášce e-mail neposílá -- signálem je číslo v
menu a na dashboardu.

## Stavy {#statuses}

Každá přihláška prochází těmito stavy. Nastavujete je na
[stránce přihlášky](#application-page); jen **Uzavřeno (zahrada
přidělena)** nastavuje Parcella sama.

| Stav | Význam |
|---|---|
| **Nová** | Právě přišla; zatím se na ni nikdo nepodíval. |
| **Kontaktován** | Výbor se ozval -- např. poslal první e-mail. Uchazeč je v pořadníku. |
| **Zahrada nabídnuta** | Byla nabídnuta zahrádka. |
| **Přijato** | Uchazeč nabízenou zahrádku chce; předání se ještě domlouvá. |
| **Zamítnuto** | Spolek odmítl, nebo uchazeč nechce další nabídky. |
| **Uzavřeno (zahrada přidělena)** | Uchazeč dostal parcelu přes **Přidělit parcelu**. |

**Nová**, **Kontaktován**, **Zahrada nabídnuta** a **Přijato** se
počítají jako *otevřené*. Pokud uchazeč nabídku odmítne, ale chce
zůstat v pořadníku, vraťte ho na **Kontaktován**. Pokud nechce další
nabídky, nastavte **Zamítnuto**.

## Seznam uchazečů {#applicant-list}

![Seznam uchazečů](../assets/screenshots/applicants/list.png)

Otevřete **Uchazeči** v hlavním menu. Seznam ukazuje přihlášky,
nejnovější datum přihlášky první.

### Filtr a hledání {#filter-and-search}

| Pole / tlačítko | Co dělá |
|---|---|
| **Nové** | Jen přihlášky se stavem **Nová**. Zobrazí se, jen dokud nové přihlášky existují -- a pak se seznam otevírá s tímto filtrem. |
| **Otevřené** | Přihlášky ve stavu **Nová**, **Kontaktován**, **Zahrada nabídnuta** nebo **Přijato**. Seznam se s tímto filtrem otevírá, když nové přihlášky nejsou. |
| **Uzavřené** | Přihlášky ve stavu **Uzavřeno (zahrada přidělena)** nebo **Zamítnuto**. |
| **Vše** | Každá přihláška. |
| **Jméno, e-mail, telefon, zpráva, poznámky…** | Hledá ve jménu a příjmení, e-mailové adrese, telefonním čísle, zprávě uchazeče a poznámce výboru. Kombinuje se s tlačítky filtru. Protože se prohledává i poznámka výboru, najdete uchazeče i podle čísla tiketu, které jste si tam poznamenali. |
| **Hledat** | Použije hledání. |
| **Zrušit filtr** | Zruší hledání, ponechá tlačítko filtru. |

### Sloupce {#columns}

| Sloupec | Co ukazuje |
|---|---|
| Zaškrtávací políčko | Vybere uchazeče pro **Napsat vybraným uchazečům** (viz níže). |
| **Jméno** | Jméno a příjmení, nebo e-mailová adresa, pokud jméno nebylo uvedeno. Kliknutím otevřete přihlášku. |
| **E-mail** | Kliknutím napíšete ze svého poštovního programu. |
| **Telefon** | |
| **Přihlášeno** | Datum přihlášky. Určuje pořadí v pořadníku. |
| **Stav** | Viz [Stavy](#statuses). |
| Tlačítko s okem | Otevře přihlášku. |

Vedle jména se mohou objevit dva druhy odznaků:

- **2×**, **3×** … -- tato e-mailová adresa se přihlásila více než
  jednou. Parcella opakované přihlášky neslučuje; každá zůstává
  samostatným záznamem, aby se žádná zpráva neztratila. Co s nimi, je na
  vás. Stránka přihlášky vypisuje ty ostatní.
- **Červená vlajka** -- jméno, e-mailová adresa nebo telefonní číslo
  uchazeče odpovídá [externímu kontaktu](external-contacts.md), který
  nese štítek červené vlajky vašeho spolku. Najeďte na odznak myší a
  uvidíte, který kontakt a které údaje odpovídají. Dokud je modul
  Externí kontakty vypnutý, červené vlajky nejsou.

### Psaní vybraným uchazečům {#writing-to-selected-applicants}

Dokud je zapnutý modul **Oznámení**, vidí členové výboru a
administrátoři v každém řádku zaškrtávací políčko.

| Tlačítko | Co dělá |
|---|---|
| **Vybrat vše** | Zaškrtne každého uchazeče, kterého ukazuje aktuální filtr a hledání. |
| **Zrušit výběr** | Zruší všechna zaškrtnutí. |
| **Vybráno: *N*** | Počítá zaškrtnuté uchazeče. |
| **Napsat vybraným uchazečům** | Zahájí nové [oznámení](announcements.md) zaškrtnutým uchazečům. Odchází jen e-mailem, jednou na adresu -- kdo se přihlásil dvakrát, dostane jeden e-mail. Neaktivní, dokud někoho nezaškrtnete. |

### Ruční přidání uchazeče {#adding-an-applicant-by-hand}

**Přidat uchazeče** (vpravo nahoře, vyžaduje oprávnění k zápisu) otevře
formulář [Nový uchazeč](#new-applicant).

## Nový uchazeč {#new-applicant}

![Formulář nového uchazeče](../assets/screenshots/applicants/form-new.png)

Pro přihlášky, které nepřišly přes web -- telefonicky, dopisem nebo ze
starého papírového pořadníku. Přihlášky z formuláře na webu se v
seznamu objeví samy.

| Pole | Co dělá |
|---|---|
| **E-mailová adresa** \* | Povinné -- jediné povinné pole. Musí to být platná e-mailová adresa, jinak „Zadejte prosím platnou e-mailovou adresu.“ |
| **Jméno** / **Příjmení** | Zde volitelné, ale potřebné, než můžete přidělit parcelu. |
| **Telefon** | |
| **Přihlášeno** | Datum přihlášky. „Ponechte prázdné pro dnešní datum. Změňte ho při zadávání starší žádosti, např. z papírového pořadníku -- určuje pořadí.“ Datum v budoucnosti se odmítne. |
| **Zpráva uchazeče** | Co vám uchazeč napsal nebo řekl. |
| **Poznámka výboru** | „Interní -- uchazeči se nikdy nezobrazí.“ |

Klikněte na **Uložit**. Přihláška začíná se stavem **Nová**, jejím
zdrojem je **Zadáno ručně** (s vaším jménem) a nemá datum souhlasu se
zpracováním údajů -- to se zaznamenává jen u přihlášek z webu. **Zpět**
vás vrátí na seznam bez uložení.

## Stránka přihlášky {#application-page}

![Stránka přihlášky](../assets/screenshots/applicants/detail.png)

Kliknutím na uchazeče v seznamu otevřete jeho přihlášku.

Pokud uchazeč odpovídá externímu kontaktu s červenou vlajkou, červený
rámeček **Červená vlajka** nahoře uvádí kontakt a odpovídající údaje
(jméno, e-mail, telefon). Uživatelé, kteří smějí vidět externí kontakty,
se mohou proklikat na kontakt.

### Přihláška {#application}

Levá karta obsahuje vše, co můžete upravit.

| Pole | Co dělá |
|---|---|
| **Stav** | Viz [Stavy](#statuses). Každá změna se zaznamená v **Historie stavu**. |
| **E-mailová adresa** \*, **Jméno**, **Příjmení**, **Telefon** | Kontaktní údaje uchazeče. |
| **Přihlášeno** | Datum přihlášky. Změňte ho, chcete-li přihlášku přesunout na správné místo ve frontě, např. když zadáváte starou papírovou přihlášku. Změna se zaznamená v historii stavu, protože uchazeče posouvá nahoru nebo dolů. Budoucí data se odmítnou. |
| **Zpráva uchazeče** | Text, který uchazeč poslal. |
| **Poznámka výboru** | Interní poznámky, uchazeči se nikdy nezobrazí -- např. „volal 3. května, chce menší zahrádku“. |

Změny uložíte kliknutím na **Uložit**. Bez oprávnění k zápisu údaje
vidíte, ale nemůžete je uložit. Změny kontaktních údajů a poznámky
výboru se do historie nezaznamenávají.

### Tlačítka nahoře {#buttons-at-the-top}

| Tlačítko | Co dělá |
|---|---|
| **Zpět** | Vrátí se na seznam uchazečů. |
| **Smazat** | Po potvrzení „Trvale smazat tohoto uchazeče? Nelze vrátit zpět.“ přihlášku trvale smaže. Smaže se i její historie stavu. Vyžaduje oprávnění k mazání. |

!!! info "Proč lze uchazeče smazat natrvalo"
    Téměř vše ostatní v Parcelle si uchovává historii. Uchazeči jsou
    výjimkou: jejich údaje se uchovávají jen kvůli přihlášce, takže je
    musíte mít možnost úplně odstranit -- když o to někdo požádá, nebo
    když přihláška skončí. Váš spolek může nechat staré přihlášky mazat
    i automaticky; viz [Automatické mazání](#automatic-deletion).

### Kontaktovat žadatele {#contact-applicant}

Zobrazí se jen u přihlášky ve stavu **Nová**, uživatelům s oprávněním k
zápisu. Je to první krok postupu: děkovný e-mail, který potvrzuje, že je
uchazeč v pořadníku.

| Pole / tlačítko | Co dělá |
|---|---|
| **Komu:** | E-mailová adresa uchazeče. |
| **Předmět:** | „Děkujeme za registraci na náš pořadník!“ (v jazyce, ve kterém Parcellu používáte). |
| Zpráva | Text e-mailu připravený k úpravě. Jméno uchazeče a název spolku jsou už vyplněné. |
| **Odeslat** | Po potvrzení pošle text uchazeči e-mailem a nastaví stav na **Kontaktován**. |

Po odeslání zelené upozornění uvádí „E-mail byl odeslán a stav nastaven
na „Kontaktován“.“ Rámeček pak zmizí, protože přihláška už není nová.

Pokud e-mail nelze odeslat, nic se nezmění: stav zůstane **Nová**, váš
upravený text zůstane v rámečku a uvidíte „E-mail se nepodařilo odeslat
– zkontrolujte prosím nastavení SMTP. Stav nebyl změněn.“ Opravte
nastavení pošty a zkuste to znovu.

Výchozí text pochází z **Text e-mailu novým žadatelům** v
[Nastavení spolku](../administration/settings.md) → **Uchazeči**. Pokud
je prázdný, použije Parcella svůj vestavěný text v jazyce, ve kterém
Parcellu používáte. Uchazeči nemají vlastní nastavení jazyka, takže
pokud váš spolek píše vlastní text, napište ho v jazyce, kterým mluví
vaši uchazeči.

!!! note "Poznámka"
    Parcella si kopii e-mailu neuchovává. Že odešel, ukazuje jen změna
    stavu na **Kontaktován**.

### Přidělit parcelu {#assign-a-parcel}

Zobrazí se jen u otevřené přihlášky, uživatelům s oprávněním k zápisu
u **Uchazeči** i **Členové a parcely**. **Přidělit parcelu** předá
ukončenou parcelu uchazeči -- viz [Přidělit parcelu](#assign-a-parcel_1)
níže.

### Podrobnosti {#details}

| Řádek | Co ukazuje |
|---|---|
| **Přihlášeno** | Datum přihlášky. |
| **Zdroj** | **Formulář na webu**, nebo **Zadáno ručně** se jménem uživatele, který přihlášku zadal. |
| **Souhlas se zpracováním údajů (uchazeč)** | Kdy uchazeč zaškrtl políčko ochrany osobních údajů ve formuláři na webu. U ručně zadaných přihlášek prázdné. Je to souhlas uchazeče -- ne schválení výborem. |
| **Stav změněn** | Kdy se stav naposledy změnil. |

Všechna data se zobrazují bez času.

### Další přihlášky z této adresy {#other-applications-from-this-address}

Zobrazí se, jen pokud se stejná e-mailová adresa přihlásila více než
jednou. Vypisuje ostatní přihlášky s datem a stavem; kliknutím na datum
jednu otevřete.

### Procesy {#processes}

Pokud je zapnutý modul [Procesy](processes.md) a smíte procesy vidět,
karta **Procesy** vypisuje procesy týkající se tohoto uchazeče. **Zahájit
proces** zahájí nový.

### Historie stavu {#status-history}

Každá změna stavu a každá změna data přihlášky, s datem, časem a
uživatelem, který ji provedl -- nejnovější první. Objevují se zde i
změny provedené samotnou Parcellou (předání).

## Přidělit parcelu {#assign-a-parcel_1}

![Přidělit parcelu](../assets/screenshots/applicants/assign-parcel.png)

Když se parcela uvolní, tato stránka ji v jednom kroku předá jednomu
nebo více uchazečům. Otevřete ji tlačítkem **Přidělit parcelu** u
přihlášky.

!!! info "Než začnete"
    - Parcela musí mít stav **ukončená**. Nejprve ho nastavte ve
      [formuláři parcely](parcels.md#new-parcel-and-edit-parcel). Pokud
      žádná parcela není ukončená, stránka vám to řekne.
    - Každý uchazeč, který parcelu přebírá, potřebuje v přihlášce jméno
      a příjmení.

### Krok 1: parcela a datum předání {#step-1-parcel-and-handover-date}

| Pole | Co dělá |
|---|---|
| **Ukončená parcela** | Parcela k předání. Nabízejí se jen ukončené parcely, každá se jmény současných nájemců. |
| **Datum předání** | Den, kdy noví nájemci přebírají. Výchozí je dnešek. Může ležet v budoucnosti: staří nájemci pak do toho dne zůstávají nájemci, členy a příjemci faktur a noví nájemci se na stránce parcely zobrazují jako budoucí. |
| **Další uchazeči (spolunájemci)** | Volitelné: další otevření uchazeči, kteří parcelu přebírají společně s tímto, např. pár, který se přihlásil zvlášť. |
| **Složka dokumentů pro nové nájemce** | Jen pro členy výboru a administrátory, dokud je zapnutý modul **Cloudové úložiště**. Složka, která se ke dni předání stane složkou dokumentů parcely. **Procházet cloudové úložiště** vám umožní proklikat se úložištěm a zvolit **Použít tuto složku**. Složku vytvořte a nasdílejte ve svém cloudovém úložišti sami. Volitelné -- lze ji nastavit i později na stránce parcely. |
| **Náhled** | Ukáže, co se stane. Zatím se nic nemění. |

### Krok 2: zkontrolujte náhled {#step-2-check-the-preview}

Karta náhledu, **Předání parcely *X* dne *datum***, přesně uvádí, co se
stane:

- **Dosavadní nájemci** -- nájem každého současného nájemce končí dnem
  předání. Pokud nemají jinou parcelu, jejich členství končí den předtím
  („členství končí po *datum*.“). Pokud mají ještě jinou parcelu,
  členství si ponechají; náhled tuto parcelu uvádí.
- **Noví nájemci a příjemci faktur** -- každý uchazeč se buď „stane
  novým členem“ (jméno, e-mail a telefon se převezmou z přihlášky),
  nebo, pokud aktivní člen už má e-mailovou adresu uchazeče, se propojí
  s tímto členem („již člen“).
- **Složka dokumentů** -- která složka se ke dni předání vyřadí a která
  ji nahradí. Pokud složky sami spravovat nemůžete, poznámka uvádí, že
  novou složku později nastaví někdo s plným přístupem.

Pokud je něco špatně -- parcela není ukončená, přihláška uchazeče je už
uzavřená nebo nemá jméno --, chybová zpráva to vysvětlí a nic se nestane.

Klikněte na **Předat parcelu** a potvrďte. Parcella pak najednou:

1. ukončí staré nájmy ke dni předání (zůstanou v historii parcely jako
   bývalí nájemci),
2. ukončí členství starých nájemců, kteří nemají jinou parcelu,
3. vytvoří nové členy -- jejich **Členem od** je datum předání -- a
   udělá z nich nájemce a příjemce faktur parcely,
4. nastaví parcelu zpět na **aktivní**,
5. nastaví přihlášky na **Uzavřeno (zahrada přidělena)**.

Poté se ocitnete na stránce parcely.


!!! tip "Nového člena potom doplňte"
    Z přihlášky se kopíruje jen jméno, e-mailová adresa a telefonní
    číslo. Otevřete nového člena a doplňte adresu a IBAN. **Může
    dostávat informace e-mailem** je zaškrtnuté, jako u každého nového
    člena; odškrtněte ho, pokud chce jen papír.

## Přihlášky z vašeho webu {#applications-from-your-website}

Většina přihlášek přichází přes formulář na webu vašeho spolku. Jakmile
je nastaven, každý odeslaný formulář se objeví v seznamu uchazečů jako
přihláška **Nová** se zdrojem **Formulář na webu** a datem, kdy uchazeč
udělil souhlas se zpracováním údajů.

Na co se formulář ptá: e-mailová adresa (povinné), jméno a příjmení,
telefon, zpráva a zaškrtávací políčko souhlasu se zpracováním údajů,
které musí být zaškrtnuté. Parcella chrání formulář proti spamu:
skrytá pole, která vyplňují jen boti, volitelná captcha a limit několika
odeslání za hodinu od stejného návštěvníka.

Nastavení:

1. Zapněte modul **Veřejné API formuláře přihlášek** v části
   [Zapínání a vypínání modulů](../administration/modules.md).
2. V [Integrace](../administration/integrations.md) zadejte adresu
   svého webu, aby z něj Parcella formuláře přijímala. Stránka také
   uvádí adresy, na které formulář odesílá.
3. Umístěte formulář na svůj web:
    - **WordPress**: nainstalujte plugin Parcella Connector a na stránku
      vložte shortcode `[parcella_applicant_form]`.
    - **Jakýkoli jiný web**: jednoduchý HTML formulář, který odesílá
      výše uvedená pole do Parcelly. Váš webdesignér najde podrobnosti v
      Integrace.

Co uchazeči vidí, popisuje stránka [Pro zahrádkáře](../gardeners/index.md).

!!! note "Poznámka"
    Parcella uchazeči neposílá automatické potvrzení. Pro první odpověď
    použijte [Kontaktovat žadatele](#contact-applicant).

## Automatické mazání {#automatic-deletion}

V [Nastavení spolku](../administration/settings.md) → **Uchazeči**
umožňuje **Mazat přihlášky po (měsících)** nechat Parcellu mazat staré
přihlášky za vás. Každá přihláška, jejíž stav se tolik měsíců nezměnil,
se trvale smaže -- **bez ohledu na stav** a bez upozornění. Měsíce se
počítají od poslední změny stavu, nebo od data přihlášky, pokud se stav
nikdy nezměnil.

Ponechte pole prázdné nebo na 0 (výchozí), chcete-li přihlášky
uchovávat, dokud je nesmažete ručně. Kontrola běží na pozadí, zatímco
lidé Parcellu používají, nejvýše jednou za hodinu.

!!! warning "Varování"
    Automatické mazání odstraňuje i otevřené přihlášky, které prostě
    dlouho čekají. Pokud je váš pořadník dlouhý, zvolte období delší než
    obvyklé čekání, nebo stav dlouho čekajících uchazečů čas od času
    posuňte.

## Související {#related}

- [Parcely](parcels.md) -- ukončení parcely před předáním
- [Členové](members.md) -- doplnění údajů nového člena
- [Předání parcely](../guides/parcel-handover.md)
- [Oznámení](announcements.md) -- psaní vybraným uchazečům
- [Externí kontakty](external-contacts.md) -- štítek červené vlajky
- [Integrace](../administration/integrations.md) -- formulář na webu

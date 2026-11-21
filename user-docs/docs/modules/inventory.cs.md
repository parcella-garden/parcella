# Inventář {#inventory}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Inventář je evidence majetku spolku: vše, co spolek vlastní, a věci, které
členové vlastní osobně, ale mají je uložené na pozemku spolku. Předměty
jsou seskupené do kategorií, které si sami definujete, nesou nákupní
cenu, aktuální hodnotu a cenu za náhradu a lze je jednoduchým systémem
půjčování a vracení půjčovat členům.

!!! info "Kdo to může používat"
    Členové výboru a administrátoři mají vždy plný přístup. Ostatní
    uživatelé potřebují skupinu, která dává oprávnění pro **Inventář**
    (viz [Skupiny](../administration/groups.md)):

    - **Čtení** -- vidět seznam předmětů, stránky předmětů a aktivní
      výpůjčky.
    - **Zápis** -- vytvářet, upravovat a vyřazovat předměty, spravovat
      kategorie, půjčovat předměty a označovat je jako vrácené.
    - **Mazání** -- trvale mazat předměty a kategorie.

    Modul se zapíná přepínačem **Inventář** v části
    [Zapínání a vypínání modulů](../administration/modules.md). Ve
    výchozím stavu je zapnutý.

## Seznam inventáře {#inventory-list}

![Seznam inventáře](../assets/screenshots/inventory/list.png)

**Inventář** v navigaci vypisuje všechny předměty, seskupené do jedné
karty na kategorii v abecedním pořadí. Předměty bez kategorie jsou
poslední v **Bez kategorie**. V rámci karty jsou předměty seřazené podle
názvu.

| Pole / tlačítko | Co dělá |
|---|---|
| **Aktivní výpůjčky** | Otevře [seznam všeho, co je právě zapůjčeno](#active-loans). |
| **Spravovat kategorie** | Otevře [kategorie](#inventory-categories). Zobrazí se jen s oprávněním k zápisu. |
| **Nová položka** | Otevře prázdný [formulář předmětu](#item-form). Zobrazí se jen s oprávněním k zápisu. |
| **Všechny kategorie** / kategorie | Ukáže jen předměty jedné kategorie. |
| **Zahrnout vyřazené položky** | Vypíše i [vyřazené](#retiring-and-deleting) předměty, šedě s odznakem **Vyřazeno**. Ve výchozím stavu vypnuto. |

| Sloupec | Co ukazuje |
|---|---|
| **Název** | Předmět s odkazem na jeho stránku. Odznaky: **Vyřazeno**, **K zapůjčení**. |
| **Vlastník** | **Vlastnictví klubu** nebo **Vlastnictví člena**. |
| **Uložení** | Místo uložení. |
| **Množství** | U předmětů k zapůjčení dostupné / vlastněné (např. **1 / 2**, když je jeden ze dvou zapůjčený); jinak vlastněné množství. |
| **Hodnota** | Aktuální hodnota, pokud je zadána. |
| Tlačítko s okem | Otevře předmět. |

## Stránka předmětu {#item-page}

![Stránka předmětu](../assets/screenshots/inventory/detail.png)

Kliknutím na název předmětu otevřete jeho stránku.

### Tlačítka {#buttons}

| Tlačítko | Co dělá |
|---|---|
| **Upravit** | Otevře [formulář předmětu](#item-form). Vyžaduje oprávnění k zápisu. |
| **Vyřadit** | Po potvrzení označí předmět jako již nevlastněný nebo mimo provoz. Vyžaduje oprávnění k zápisu; po vyřazení se nezobrazuje. Viz [Vyřazení a smazání](#retiring-and-deleting). |
| **Smazat** | Po potvrzení trvale smaže předmět i celou historii výpůjček. Vyžaduje oprávnění k mazání. |
| **Zpět** | Vrátí se na seznam inventáře. |

Vyřazený předmět ukazuje nahoře upozornění „Tato položka je vyřazena --
již ve vlastnictví/provozu.“ (tj. už není ve vlastnictví ani v provozu).

### Přehled {#overview}

| Pole | Co ukazuje |
|---|---|
| **Kategorie** | Kategorie, nebo **Bez kategorie**. |
| **Vlastník** | **Vlastnictví klubu**, nebo jméno člena, který předmět vlastní. |
| **Místo uložení** | Kde je předmět uložen, nebo „-“. |
| **Množství** | U předmětů k zapůjčení „dostupné / vlastněné **k dispozici**“, jinak vlastněné množství. |
| **Popis**, **Poznámky** | Zobrazí se, jen pokud jsou vyplněné. |

### Finance {#financials}

| Pole | Co ukazuje |
|---|---|
| **Datum nákupu** | Kdy byl koupen. |
| **Nákupní cena** | Kolik stál. |
| **Aktuální hodnota** | Aktuální odhad výboru, s „k“ a datem poslední kontroly, pokud je zadán. |
| **Cena za náhradu** | Kolik by stálo ho nahradit. |

Prázdná pole ukazují „-“.

### Půjčit {#check-out}

Zobrazí se jen u předmětů označených k zapůjčení. Pokud nic není k
dispozici, uvádí **Momentálně nic k zapůjčení k dispozici.** Formulář
vyžaduje oprávnění k zápisu.

| Pole / tlačítko | Co dělá |
|---|---|
| **Člen** | Kdo si předmět půjčuje. Nabízí současné členy. Povinné. |
| **Množství** | Kolik kusů. Nejméně 1, nejvýše počet aktuálně dostupných. Výchozí 1. |
| **Datum** | Den zapůjčení. Výchozí je dnešek. |
| **Poplatek** | Volitelné. Jen číslo, např. `5` nebo `2,50` -- bez symbolu měny a textu. Pokud zůstane prázdné, účtuje se **Navrhovaný poplatek za půjčení** předmětu (ukazuje ho nápověda pod polem). |
| **Poznámka** | Volitelný volný text, např. „vrátit do neděle“. |
| **Půjčit** | Zaznamená výpůjčku. Dostupné množství se odpovídajícím způsobem sníží. |

Pokud je něco špatně -- není vybrán člen, více kusů, než je k dispozici
(„Nyní je k dispozici pouze 1 z 2.“), poplatek s textem, neplatné datum
--, stránka ukáže zprávu nad formulářem a ponechá, co jste napsali.

!!! note "Poplatky se zaznamenávají, nefakturují"
    Poplatek se uloží s výpůjčkou, aby výbor věděl, co bylo dohodnuto.
    Parcella k němu nevytváří fakturu ani zápis.

### Historie výpůjček {#loan-history}

Každá výpůjčka tohoto předmětu, nejnovější první.

| Sloupec | Co ukazuje |
|---|---|
| **Člen** | Kdo si ho půjčil. |
| **Množ.** | Kolik kusů. |
| **Půjčeno** | Datum zapůjčení. |
| **Vráceno** | Datum vrácení, nebo odznak **Nevráceno**, dokud je předmět venku. |
| **Poplatek** | Účtovaný poplatek, nebo „-“. |
| **Označit jako vráceno** | Zaznamená vrácení s dnešním datem. Zobrazí se u nevrácených výpůjček s oprávněním k zápisu. |

## Formulář předmětu {#item-form}

![Nová položka](../assets/screenshots/inventory/form-new.png)

Stejný formulář se používá pro **Nová položka** i **Upravit**, s
titulkem **Položka inventáře**.

### Obecné {#general}

| Pole | Co dělá |
|---|---|
| **Název** | Co je předmět zač. Povinné. |
| **Kategorie** | Jedna z vašich [kategorií](#inventory-categories), nebo **Žádná kategorie**. |
| **Popis** | Volitelný delší popis. |
| **Místo uložení** | Kde je uložen, např. „Kůlna na nářadí“. |

### Vlastnictví {#ownership}

| Pole | Co dělá |
|---|---|
| **Vlastnictví klubu** | Výchozí. |
| **Osobní vlastnictví člena** | Pro věci, které členové mají na pozemku spolku, ale vlastní je sami -- stojí za zaznamenání kvůli pojištění a odpovědnosti. Zobrazí **Vlastnící člen**. |
| **Vlastnící člen** | Člen, který předmět vlastní. Povinné, pokud předmět vlastní člen; nabízí současné členy. |

### Finance {#financials_1}

Aktuální hodnota se zadává ručně, kdykoli ji někdo zkontroluje.
Parcella nic automaticky neodepisuje.

| Pole | Co dělá |
|---|---|
| **Datum nákupu** | Volitelné. |
| **Nákupní cena** | Volitelné. |
| **Aktuální hodnota** | Volitelné. Váš aktuální nejlepší odhad. |
| **Cena za náhradu** | Volitelné. |
| **Hodnota naposledy zkontrolována** | Volitelné datum, aby všichni viděli, jak aktuální je aktuální hodnota. |

Částky jsou jen čísla: `5`, `2,50` nebo `2.50`. Text, symbol měny nebo
záporná částka se odmítnou se zprávou.

### Půjčování {#lending}

| Pole | Co dělá |
|---|---|
| **Vlastněné množství** | Kolik stejných kusů tento záznam představuje -- tři kolečka mohou být jeden předmět s množstvím 3. Celé číslo 1 nebo více; výchozí 1. |
| **Členové si to mohou půjčit** | Zapne pro tento předmět půjčování a vracení. Zobrazí **Navrhovaný poplatek za půjčení**. |
| **Navrhovaný poplatek za půjčení** | Volitelné. Použije se jako poplatek, když se výpůjčka zadá bez něj; u každé výpůjčky ho lze změnit. |

### Poznámky {#notes}

Volný text pro cokoli dalšího.

Kliknutím na **Uložit** předmět uložíte a otevřete jeho stránku, nebo
**Zrušit**.

!!! tip "Jeden záznam na druh věci"
    Stejné věci evidujte jako jeden předmět s množstvím, ne jako
    samostatné předměty. Půjčování pak ukazuje „K dispozici 2 z 3“ a
    změna ceny se dělá jednou.

## Vyřazení a smazání {#retiring-and-deleting}

- **Vyřaďte** předmět, který skutečně existoval a teď je prodaný,
  sešrotovaný nebo ztracený. Zůstane v evidenci s cenami a historií
  výpůjček, ale je ze seznamu skrytý, pokud nezaškrtnete **Zahrnout
  vyřazené položky**. Tlačítko pro zrušení vyřazení neexistuje.
- **Smažte** jen skutečnou chybu, např. předmět zadaný dvakrát. Trvale
  odstraní předmět a všechny jeho výpůjčky.
<!-- TODO(verify): a retired borrowable item still shows the Check out form and can still be lent; and there is no way in the web UI to un-retire an item. Confirm both are intended. -->

## Kategorie inventáře {#inventory-categories}

![Kategorie inventáře](../assets/screenshots/inventory/categories.png)

**Spravovat kategorie** v seznamu inventáře otevře tuto stránku.
Vyžaduje oprávnění k zápisu. **Zpět** vás vrátí na seznam.

| Pole / tlačítko | Co dělá |
|---|---|
| Název (např. „Hřiště, ploty, zámky a klíče“) | Název nové kategorie. Povinné; nesmí ještě existovat („Kategorie s tímto názvem již existuje.“). |
| **Volitelný popis** | Krátký popis. |
| **Přidat** | Vytvoří kategorii. |
| Sloupce **Název**, **Popis** | Existující kategorie. |
| Tlačítko koše | Po potvrzení smaže kategorii. Její předměty se **nesmažou** -- stanou se **Bez kategorie**. Vyžaduje oprávnění k mazání. |

Kategorie nelze na této stránce přejmenovat. Chcete-li jednu
přejmenovat, vytvořte novou kategorii, přesuňte do ní předměty jejich
úpravou a starou smažte.

## Aktivní výpůjčky {#active-loans}

![Aktivní výpůjčky](../assets/screenshots/inventory/active-loans.png)

**Aktivní výpůjčky** v seznamu inventáře ukazuje vše, co je právě
zapůjčené, napříč všemi předměty, nejstarší výpůjčka první. Použijte to
k zjištění, kdo co má, před pracovní směnou nebo na konci sezóny.

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Položka** | Předmět s odkazem na jeho stránku. |
| **Člen** | Kdo ho má. |
| **Množ.** | Kolik kusů. |
| **Od** | Datum zapůjčení. |
| **Poplatek** | Účtovaný poplatek, nebo „-“. |
| **Označit jako vráceno** | Zaznamená vrácení s dnešním datem a otevře stránku předmětu. Vyžaduje oprávnění k zápisu. |

Pokud nic není venku, stránka uvádí **Momentálně nic není zapůjčeno.**

!!! tip "Dostupnost v kalendáři"
    Pokud je zapnutý modul kalendáře, **Kalendář → Vlastní kalendáře →
    Zdroje** vypisuje předměty k zapůjčení ve vlastnictví spolku (bez
    vyřazených) s jejich stavem -- **K dispozici**, **Zapůjčeno** nebo
    „K dispozici 1 z 2“ -- a kdo je má od kdy. Vyžaduje také oprávnění
    ke čtení inventáře. Viz [Kalendář](calendar.md).

## Související {#related}

- [Členové](members.md) -- vypůjčitelé a vlastníci předmětů ve
  vlastnictví členů
- [Žádosti o nákup](purchase-requests.md) -- získání schválení před
  nákupem něčeho nového
- [Skupiny](../administration/groups.md) -- přístup k inventáři pro
  někoho bez plných práv výboru

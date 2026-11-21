# Role, skupiny a oprávnění {#roles-groups-and-permissions}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Ne každý, kdo pomáhá vést spolek, potřebuje vidět všechno. Člověk, který
odečítá vodoměry, nepotřebuje bankovní údaje, a pokladník nepotřebuje
plánovat pracovní směny. Parcella vám umožní dát každému přesně takový
přístup, jaký jeho funkce vyžaduje.

!!! info "Kdo to může používat"
    Tato stránka vysvětluje přístup pro všechny. Kdo má jaký přístup,
    mohou měnit jen **administrátoři**, v části
    [Uživatelé a pozvánky](../administration/users.md) a
    [Skupiny](../administration/groups.md).

## Tři úrovně přístupu {#the-three-levels-of-access}

Každý účet spadá do jedné ze tří úrovní.

| Úroveň | Vidí a mění | Otevře **Administrace** | Jak ji získáte |
|---|---|---|---|
| **Správce** | Vše ve všech zapnutých modulech | Ano | Skupina s **Přístup k administračnímu panelu**, nebo starší role **Správce** |
| **Plný přístup** (typicky výbor) | Vše ve všech zapnutých modulech | Ne | Skupina s **Plný přístup ke každému modulu**, nebo starší role **Výbor** |
| **Omezený** | Co dovolují jeho skupiny, modul po modulu; nejméně přístup ke čtení členů a parcel | Ne | Členství v jedné nebo více skupinách bez zaškrtnutí těchto dvou políček |

Oblast **Administrace** -- uživatelé, skupiny, nastavení spolku,
integrace, zálohy -- je záměrně oddělena od plného přístupu. Členství ve
výboru z nikoho automaticky nedělá člověka, který se stará o instalaci,
a naopak. Administrátoři mají vždy také plný přístup k modulům.

## Skupiny {#groups}

**Skupina** je pojmenovaná sada oprávnění, například „Vodní tým“,
„Pokladník“ nebo „Výbor“. Administrátoři vytvářejí skupiny a zařazují do
nich účty. Člověk může být ve více skupinách.

Skupina dává buď:

- **Plný přístup ke každému modulu**, nebo
- **Přístup k administračnímu panelu** (který zahrnuje plný přístup),
  nebo
- **Čtení**, **Zápis** a **Mazání** pro jednotlivé moduly, zaškrtávané
  zvlášť.

### Co znamená Čtení, Zápis a Mazání {#what-read-write-and-delete-mean}

| Oprávnění | Umožňuje |
|---|---|
| **Čtení** | Otevřít modul, vidět jeho seznamy a stránky detailu a stahovat jeho exporty a přehledy. Bez něj se modul v postranním panelu neobjeví. |
| **Zápis** | Vytvářet nové záznamy a měnit stávající -- přidat odečet měřidla, upravit člena, zaznamenat platbu faktury. |
| **Mazání** | Odstraňovat záznamy, pokud modul mazání vůbec umožňuje. |

!!! tip "Zaškrtněte i Čtení"
    Zápis a Mazání jsou míněny navíc ke Čtení. Kdo nemůže modul číst,
    nevidí ho v postranním panelu a nemůže otevřít jeho stránky, takže
    samotný Zápis je k ničemu. Každá kapitola o modulu uvádí, které akce
    potřebují které oprávnění.

### Moduly, které může skupina udělit {#the-modules-a-group-can-grant}

| Modul ve formuláři skupiny | Pokrývá |
|---|---|
| **Členové a parcely** | [Členové](../modules/members.md) a [Parcely](../modules/parcels.md) |
| **Pracovní sezení** | [Pracovní hodiny](../modules/work-hours.md) |
| **Voda** | Vodní část kapitoly [Voda a elektřina](../modules/metering.md) |
| **Elektřina** | Elektrická část kapitoly [Voda a elektřina](../modules/metering.md) |
| **Pojištění** | [Pojištění](../modules/insurance.md) |
| **Žádosti o nákup** | [Žádosti o nákup](../modules/purchase-requests.md) |
| **Kalendář** | [Kalendář](../modules/calendar.md) |
| **Inventář** | [Inventář](../modules/inventory.md) |
| **Finance** | [Finance](../modules/finances/index.md) |
| **Podpora (helpdesk)** | [Podpora](../modules/support.md) |
| **Uchazeči** | [Uchazeči](../modules/applicants.md) |
| **Externí kontakty** | [Externí kontakty](../modules/external-contacts.md) |
| **Přehledy** | [Přehledy](../modules/reporting.md) |
| **Poznámky** | [Poznámky](../modules/notes.md) |
| **Procesy** | [Procesy](../modules/processes.md) |

### Více skupin: vyhrává ta nejštědřejší {#several-groups-the-most-generous-wins}

Pokud je člověk ve více skupinách, jeho oprávnění se sčítají. Pro každý
modul a každou úroveň stačí, aby ji udělila jedna skupina. Příklad:
skupina „Vodní tým“ dává Voda čtení + zápis, skupina „Kalendář“ dává
Kalendář čtení. Kdo je v obou, smí číst a měnit údaje o vodě a číst
kalendář.

### Členy a parcely si může prohlédnout každý {#everybody-can-look-up-members-and-parcels}

Každý účet, i ten, který není v žádné skupině, může **číst** členy a
parcely. Kdo pomáhá vést spolek, potřebuje vědět, kdo je kdo a čí je
která parcela. Jejich změny vyžadují **Zápis** u **Členové a parcely**.

## Co smí jen plný přístup {#things-only-full-access-can-do}

Několik oblastí nelze udělit po modulech. Jsou vždy vyhrazeny lidem s
plným přístupem (výbor, administrátoři nebo skupina s **Plný přístup ke
každému modulu**):

- [Nástěnka úkolů](../modules/tasks.md),
- [Oznámení](../modules/announcements.md),
- schválení nebo zamítnutí [žádosti o nákup](../modules/purchase-requests.md)
  -- obě požadovaná schválení musí přijít od lidí s plným přístupem,
- vytváření a úpravy kalendářů v **Vlastní kalendáře** v modulu
  [Kalendář](../modules/calendar.md),
- cloudová složka parcely (procházení, nahrávání, stahování) a stažení
  přílohy přijaté faktury,
- vytvoření úkolu z konverzace podpory nebo propojení konverzace s
  úkolem.

## Starší role: Správce, Výbor, Pokladník, Pouze pro čtení {#the-older-roles-administrator-board-treasurer-read-only}

Dřívější verze Parcelly dávaly každému účtu pevnou **roli**. Účty
vytvořené v té době ji mohou mít stále:

| Role | Účinek dnes |
|---|---|
| **Správce** | Plný přístup a k tomu administrace, bez potřeby skupiny. Úplně první účet nové instalace má tuto roli. |
| **Výbor** | Plný přístup, bez potřeby skupiny. |
| **Pokladník** | Nic nad základní přístup ke čtení členů a parcel. Pro více použijte skupinu. |
| **Pouze pro čtení (pouze prohlížení)** | Stejně jako Pokladník: jen základní přístup, vše ostatní pochází ze skupin. |

Nové účty dostávají neúčinnou roli **Pouze pro čtení**; jejich skutečný
přístup pochází jen ze skupin. Administrátor může účet Správce nebo
Výboru převést na skupiny tlačítkem **Odebrat starou roli** (viz
[Uživatelé a pozvánky](../administration/users.md)). Účet *nejprve*
zařaďte do správné skupiny, jinak klesne na základní přístup.

Zápatí postranního panelu ukazuje skupiny, ve kterých jste. Bez skupiny
ukazuje **Správce** nebo **Výbor**, pokud máte tuto roli, jinak pomlčku.

## Pojistka: poslední administrátor {#safety-net-the-last-administrator}

Parcella odmítne jakoukoli změnu, po které by **nezůstal žádný aktivní
účet schopný otevřít administraci**. Dostanete zprávu **Poslednímu
zbývajícímu účtu Správce/Výboru nelze odebrat administrátorský
přístup**, když se pokusíte poslední takový účet deaktivovat, smazat,
snížit mu práva nebo ho odebrat z jeho skupiny, nebo smazat či
odškrtnout poslední skupinu, která tento přístup dává. Bez alespoň
jednoho administrátora by už nikdo nemohl opravit problémy s přístupem.

## REST API a API tokeny {#the-rest-api-and-api-tokens}

Programy, které s Parcellou komunikují přes její programové rozhraní,
používají [API token](../administration/api-tokens.md). Osobní token
jedná s oprávněními účtu, ke kterému patří.
<!-- TODO(verify): several REST API endpoints still check only the old role (Administrator/Board) rather than group permissions, so a group-based full-access account may be refused some API writes. Confirm before stating this to users. -->

## Související {#related}

- [Skupiny](../administration/groups.md) -- vytváření skupin a zaškrtávání oprávnění
- [Uživatelé a pozvánky](../administration/users.md) -- přidávání lidí do skupin
- [Orientace v aplikaci](navigation.md#why-entries-appear-and-disappear)

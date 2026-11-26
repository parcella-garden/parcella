# Roly, skupiny a oprávnenia {#roles-groups-and-permissions}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Nie každý, kto pomáha viesť spolok, potrebuje vidieť všetko. Kto
odčítava meradlá vody, nepotrebuje bankové údaje, a pokladník nemusí
plánovať pracovné zmeny. Parcella vám umožňuje dať každému presne taký
prístup, aký jeho úloha potrebuje.

!!! info "Kto to môže používať"
    Táto stránka vysvetľuje prístup pre všetkých. Kto má aký prístup,
    môžu meniť len **administrátori**, v častiach
    [Používatelia a pozvánky](../administration/users.md) a
    [Skupiny](../administration/groups.md).

## Tri úrovne prístupu {#the-three-levels-of-access}

Každý účet patrí do jednej z troch úrovní.

| Úroveň | Vidí a mení | Otvára **Administrácia** | Ako ju získa |
|---|---|---|---|
| **Administrátor** | Všetko v každom zapnutom module | Áno | Skupina s **Prístup k administračnému panelu** alebo staršia rola **Administrátor** |
| **Plný prístup** (zvyčajne výbor) | Všetko v každom zapnutom module | Nie | Skupina s **Plný prístup ku každému modulu** alebo staršia rola **Výbor** |
| **Obmedzený** | To, čo povoľujú jeho skupiny, modul po module; minimálne čítanie členov a parciel | Nie | Členstvo v jednej alebo viacerých skupinách bez zaškrtnutia týchto dvoch políčok |

Oblasť **Administrácia** -- používatelia, skupiny, nastavenia spolku,
integrácie, zálohy -- je zámerne oddelená od plného prístupu. Byť vo
výbore ešte neznamená byť osobou, ktorá sa stará o inštaláciu, a
naopak. Administrátori majú vždy aj plný prístup k modulom.

## Skupiny {#groups}

**Skupina** je pomenovaná sada oprávnení, napríklad „Tím vody“,
„Pokladník“ alebo „Výbor“. Administrátori vytvárajú skupiny a zaraďujú
do nich účty. Jedna osoba môže byť vo viacerých skupinách.

Skupina udeľuje buď:

- **Plný prístup ku každému modulu**, alebo
- **Prístup k administračnému panelu** (ktorý zahŕňa plný prístup),
  alebo
- **Čítanie**, **Zápis** a **Mazanie** pre jednotlivé moduly,
  zaškrtnuté samostatne.

### Čo znamená Čítanie, Zápis a Mazanie {#what-read-write-and-delete-mean}

| Oprávnenie | Umožňuje |
|---|---|
| **Čítanie** | Otvoriť modul, vidieť jeho zoznamy a stránky detailu a sťahovať jeho exporty a prehľady. Bez neho sa modul v bočnom paneli nezobrazí. |
| **Zápis** | Vytvárať nové záznamy a meniť existujúce -- pridať odpočet meradla, upraviť člena, zaznamenať platbu faktúry. |
| **Mazanie** | Odstraňovať záznamy, ak modul mazanie vôbec umožňuje. |

!!! tip "Zaškrtnite aj Čítanie"
    Zápis a Mazanie sú myslené navyše k Čítaniu. Kto nemôže modul
    čítať, nevidí ho v bočnom paneli a nemôže otvoriť jeho stránky,
    takže samotný Zápis je mu na nič. Každá kapitola o module uvádza,
    ktoré akcie potrebujú ktoré oprávnenie.

### Moduly, ktoré môže skupina udeliť {#the-modules-a-group-can-grant}

| Modul vo formulári skupiny | Pokrýva |
|---|---|
| **Členovia a parcely** | [Členovia](../modules/members.md) a [Parcely](../modules/parcels.md) |
| **Pracovné sedenia** | [Pracovné hodiny](../modules/work-hours.md) |
| **Voda** | Časť o vode v [Voda a elektrina](../modules/metering.md) |
| **Elektrina** | Časť o elektrine v [Voda a elektrina](../modules/metering.md) |
| **Poistenie** | [Poistenie](../modules/insurance.md) |
| **Žiadosti o nákup** | [Žiadosti o nákup](../modules/purchase-requests.md) |
| **Kalendár** | [Kalendár](../modules/calendar.md) |
| **Inventár** | [Inventár](../modules/inventory.md) |
| **Financie** | [Financie](../modules/finances/index.md) |
| **Podpora (helpdesk)** | [Podpora](../modules/support.md) |
| **Uchádzači** | [Uchádzači](../modules/applicants.md) |
| **Externé kontakty** | [Externé kontakty](../modules/external-contacts.md) |
| **Prehľady** | [Prehľady](../modules/reporting.md) |
| **Poznámky** | [Poznámky](../modules/notes.md) |
| **Procesy** | [Procesy](../modules/processes.md) |

### Viac skupín: vyhráva tá najštedrejšia {#several-groups-the-most-generous-wins}

Ak je osoba vo viacerých skupinách, jej oprávnenia sa sčítajú. Pre
každý modul a každú úroveň stačí, keď ju udeľuje jedna skupina.
Príklad: skupina „Tím vody“ udeľuje pre Vodu čítanie + zápis, skupina
„Kalendár“ udeľuje čítanie Kalendára. Kto je v oboch, smie čítať a
meniť dáta o vode a čítať kalendár.

### Členov a parcely si môže pozrieť každý {#everybody-can-look-up-members-and-parcels}

Každý účet, aj ten, ktorý nie je v žiadnej skupine, môže **čítať**
členov a parcely. Každý, kto pomáha viesť spolok, potrebuje vedieť, kto
je kto a ktorá parcela patrí komu. Na ich zmenu je potrebný **Zápis**
pre **Členovia a parcely**.

## Čo smie len plný prístup {#things-only-full-access-can-do}

Niektoré oblasti sa nedajú udeliť po moduloch. Sú vždy vyhradené
ľuďom s plným prístupom (výbor, administrátori alebo skupina s **Plný
prístup ku každému modulu**):

- [Nástenka úloh](../modules/tasks.md),
- [Oznamy](../modules/announcements.md),
- schválenie alebo zamietnutie [žiadosti o nákup](../modules/purchase-requests.md)
  -- dve požadované schválenia musia prísť od ľudí s plným prístupom,
- vytváranie a úprava kalendárov v časti **Vlastné kalendáre** v
  [Kalendári](../modules/calendar.md),
- cloudový priečinok parcely (prehliadanie, nahrávanie, sťahovanie) a
  stiahnutie prílohy prijatej faktúry,
- vytvorenie úlohy z konverzácie podpory alebo jej prepojenie s úlohou.

## Staršie roly: Administrátor, Výbor, Pokladník, Iba na čítanie {#the-older-roles-administrator-board-treasurer-read-only}

Skoršie verzie Parcelly dávali každému účtu pevnú **rolu**. Účty
vytvorené v tom čase ju môžu mať stále:

| Rola | Účinok dnes |
|---|---|
| **Administrátor** | Plný prístup plus administrácia, bez potreby skupiny. Úplne prvý účet novej inštalácie má túto rolu. |
| **Výbor** | Plný prístup, bez potreby skupiny. |
| **Pokladník** | Nič navyše okrem základného čítania členov a parciel. Viac udelíte pomocou skupiny. |
| **Iba na čítanie (len prehliadanie)** | To isté ako Pokladník: len základný prístup, všetko ostatné pochádza zo skupín. |

Nové účty dostávajú neutrálnu rolu **Iba na čítanie (len
prehliadanie)**; ich skutočný prístup pochádza len zo skupín.
Administrátor môže prepnúť účet s rolou Administrátor alebo Výbor na
skupiny tlačidlom **Odstrániť starú rolu** (pozri
[Používatelia a pozvánky](../administration/users.md)). Účet *najprv*
zaraďte do správnej skupiny, inak klesne na základný prístup.

Päta bočného panela ukazuje skupiny, v ktorých ste. Bez skupiny ukazuje
**Administrátor** alebo **Výbor**, ak máte túto rolu, inak pomlčku.

## Poistka: posledný administrátor {#safety-net-the-last-administrator}

Parcella odmietne každú zmenu, po ktorej by **nezostal žiadny aktívny
účet schopný otvoriť administráciu**. Dostanete hlásenie
**Poslednému zostávajúcemu účtu Administrátora/Výboru nie je možné
odobrať administrátorský prístup**, keď sa pokúsite deaktivovať,
zmazať, degradovať alebo odobrať zo skupiny posledný takýto účet, alebo
zmazať či odškrtnúť poslednú skupinu, ktorá tento prístup udeľuje. Bez
aspoň jedného administrátora by už nikto nemohol opraviť problémy s
prístupom.

## REST API a API tokeny {#the-rest-api-and-api-tokens}

Programy, ktoré s Parcellou komunikujú cez jej programové rozhranie,
používajú [API token](../administration/api-tokens.md). Osobný token
koná s oprávneniami účtu, ku ktorému patrí.
<!-- TODO(verify): several REST API endpoints still check only the old role (Administrator/Board) rather than group permissions, so a group-based full-access account may be refused some API writes. Confirm before stating this to users. -->

## Súvisiace {#related}

- [Skupiny](../administration/groups.md) -- vytváranie skupín a zaškrtávanie oprávnení
- [Používatelia a pozvánky](../administration/users.md) -- pridávanie ľudí do skupín
- [Orientácia v aplikácii](navigation.md#why-entries-appear-and-disappear)

# Skupiny {#groups}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Skupiny rozhodujú, čo smie každý vidieť a meniť. Vytvoríte skupinu pre
úlohu vo vašom spolku -- „Výbor“, „Pokladník“, „Tím vody“ --, zaškrtnete,
čo táto úloha potrebuje, a zaradíte do nej správnych ľudí.

!!! info "Kto to môže používať"
    Len administrátori. Otvorte **Administrácia → Skupiny**.

Myšlienky, na ktorých skupiny stoja -- Čítanie, Zápis a Mazanie, plný
prístup, administrácia --, vysvetľuje
[Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md).
Táto stránka opisuje obrazovku.

![Skupiny](../assets/screenshots/administration/groups.png)

## Vytvoriť skupinu {#create-group}

| Pole / tlačidlo | Čo robí |
|---|---|
| **Názov** | Povinný a musí byť jedinečný (**Skupina s týmto názvom už existuje**). |
| **Popis** | Voliteľná poznámka, na čo skupina slúži. |
| **Plný prístup ku každému modulu** | Členovia skupiny smú čítať, meniť a mazať všetko v každom zapnutom module, ako výbor. |
| **Prístup k administračnému panelu** | Členovia skupiny smú otvoriť aj **Administrácia**. Zaškrtnutie zahŕňa plný prístup, preto políčko plného prístupu zmizne. |
| **Vytvoriť skupinu** | Vytvorí skupinu. Uvidíte **Skupina vytvorená**. |

Nová skupina bez zaškrtnutého niektorého z políčok zatiaľ nič
neudeľuje. Otvorte ju nižšie a zaškrtnite jej oprávnenia.

## Karty skupín {#the-group-cards}

Každá skupina sa zobrazuje ako zbalená karta pod formulárom. Nadpis
ukazuje jej názov a odznak **Administrácia** alebo **Plný prístup**, ak
niečo z toho udeľuje. Kliknutím na nadpis kartu rozbalíte.

Tlačidlo s **košom** v nadpise po potvrdení skupinu zmaže. Jej členovia
stratia všetko, čo im skupina dávala. Parcella odmietne zmazať poslednú
skupinu, ktorá niekomu dáva prístup do administrácie, ak ho nemá žiadny
iný účet.

### Nastavenia a oprávnenia {#settings-and-permissions}

| Pole / tlačidlo | Čo robí |
|---|---|
| **Názov**, **Popis** | Ako pri vytváraní. |
| **Plný prístup ku každému modulu**, **Prístup k administračnému panelu** | Ako pri vytváraní. Keď je niektoré zaškrtnuté, tabuľka oprávnení sa skryje, pretože nie je potrebná. |
| Tabuľka oprávnení | Jeden riadok na každý **Modul** so zaškrtávacími políčkami **Čítanie**, **Zápis** a **Mazanie**. Pozri tabuľku modulov nižšie. |
| **Uložiť** | Uloží názov, popis, obe políčka a celú tabuľku. Uvidíte **Skupina aktualizovaná**. |

Moduly v tabuľke: **Členovia a parcely**, **Pracovné sedenia**,
**Voda**, **Elektrina**, **Poistenie**, **Žiadosti o nákup**,
**Kalendár**, **Inventár**, **Financie**, **Podpora (helpdesk)**,
**Uchádzači**, **Externé kontakty**, **Prehľady**, **Poznámky**,
**Procesy**. Moduly, ktoré má váš spolok vypnuté, sú uvedené aj tak;
ich zaškrtnutia začnú platiť, keď sa modul zapne.

!!! tip "Čítanie je na prvom mieste"
    Všade, kde zaškrtnete **Zápis** alebo **Mazanie**, zaškrtnite aj
    **Čítanie**. Bez Čítania sa modul v bočnom paneli danej osoby ani
    nezobrazí.

Nástenka úloh a oznamy v tabuľke nie sú: sú dostupné vždy len s plným
prístupom.

### Priradení používatelia {#assigned-users}

Uvádza účty v skupine, s avatarom, menom a e-mailovou adresou.

| Prvok | Čo robí |
|---|---|
| **×** vedľa osoby | Okamžite ju zo skupiny odoberie (**Používateľ odstránený**). |
| **Pridať používateľa...** + **Pridať** | Vyberte účet a pridajte ho (**Používateľ pridaný**). |

Zoznam **Pridať používateľa...** ponúka len účty, ktoré dostávajú
prístup zo skupín. Staršie účty s rolou **Administrátor** alebo
**Výbor** už plný prístup majú a nie sú tu ponúkané; ak ich chcete
prepnúť na skupiny, pridajte ich na ich stránke
[Upraviť používateľa](users.md#edit-user). Keď sú všetky vhodné účty už
v skupine, uvidíte namiesto zoznamu krátku poznámku; keď žiadne nie sú,
odkaz **Pozvať teraz**.

Zmeny oprávnení platia od ďalšieho kliknutia danej osoby -- nemusí sa
znova prihlasovať.

## Príklad nastavenia {#example-set-up}

| Skupina | Zaškrtnuté |
|---|---|
| Administrátori | **Prístup k administračnému panelu** |
| Výbor | **Plný prístup ku každému modulu** |
| Pokladník | Financie: Čítanie, Zápis, Mazanie. Členovia a parcely: Čítanie, Zápis. Žiadosti o nákup: Čítanie. Poistenie: Čítanie. |
| Odpočtári meradiel | Voda: Čítanie, Zápis. Elektrina: Čítanie, Zápis. |
| Tím pracovných zmien | Pracovné sedenia: Čítanie, Zápis. Kalendár: Čítanie. |

Osoba môže byť vo viacerých skupinách; jej oprávnenia sa sčítajú.

## Súvisiace {#related}

- [Používatelia a pozvánky](users.md)
- [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md)
- [Zapínanie a vypínanie modulov](modules.md)

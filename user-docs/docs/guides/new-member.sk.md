# Prijatie nového člena {#welcoming-a-new-member}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Niekto požiada o záhradku, dostane ponuku parcely, súhlasí -- a stane
sa členom a nájomcom. Tento návod sleduje túto cestu cez Parcellu, od
prihlášky po privítanie.

Členom môžete niekoho urobiť dvoma spôsobmi:

- **Z prihlášky** (kroky 1-6): osoba je vo vašom
  [poradovníku](../glossary.md#applicant) v časti **Uchádzači**.
  **Prideliť parcelu** potom naraz vytvorí záznam člena,
  [nájom](../glossary.md#tenancy) a fakturačnú adresu. Je to bežný
  spôsob.
- **Ručne** (krok 7): pre niekoho, kto nikdy neprešiel poradovníkom,
  alebo pre parcelu, ktorá nie je ukončená.

!!! info "Kto to môže robiť"
    Práca s prihláškami potrebuje oprávnenie **zápis** pre
    **Uchádzači**; pridelenie parcely potrebuje aj **zápis** pre
    **Členovia a parcely**. Členovia výboru a administrátori majú oboje.
    Modul **Uchádzači** je predvolene zapnutý.

## 1. Príde prihláška {#1-the-application-comes-in}

Prihlášky prichádzajú dvoma spôsobmi:

- **Z vášho webu**, ak tam má spolok formulár prihlášky a je zapnuté
  **Verejné API formulára prihlášok** (pozri
  [Integrácie](../administration/integrations.md)). Objavia sa samy.
- **Ručne**, pri prihláškach telefonicky, listom alebo osobne: otvorte
  **Uchádzači**, kliknite na **Pridať uchádzača**, vyplňte aspoň
  **E-mailová adresa** (jediné povinné pole), podľa potreby aj **Meno**,
  **Priezvisko**, **Telefón**, **Správa uchádzača** a **Poznámka
  výboru** a kliknite na **Uložiť**.

Ak chcete zadať starú prihlášku z papierového poradovníka, nastavte
**Prihlásené** na pôvodný dátum. Dátum prihlášky rozhoduje o poradí v
poradovníku.

Nové prihlášky ukazujú počítadlo vedľa **Uchádzači** v bočnom paneli a
na dashboarde, kým ich niekto neposunie ďalej.

!!! tip "Červená vlajka"
    Ak sa meno, e-mail alebo telefón uchádzača zhoduje s externým
    kontaktom so štítkom „červenej vlajky“ vášho spolku, zoznam aj
    stránka uchádzača ukážu varovanie **Červená vlajka**. Pozri
    [Uchádzači](../modules/applicants.md).

## 2. Ozvite sa {#2-get-in-touch}

1. Otvorte **Uchádzači** a kliknite na novú prihlášku.
2. V poli **Kontaktovať žiadateľa** skontrolujte a upravte text
   e-mailu. Predmet je *„Ďakujeme za registráciu do nášho
   poradovníka!“*.
3. Kliknite na **Odoslať** a potvrďte.

Parcella pošle text uchádzačovi e-mailom a nastaví stav na
**Kontaktovaný**. Pole je tam len, kým je stav **Nová**. Ak ste sa
ozvali inak, jednoducho zmeňte stav ručne (ďalší krok).

Predvolený text tohto e-mailu sa dá zmeniť v **Administrácia →
Nastavenia → Uchádzači → Text e-mailu novým žiadateľom**.

## 3. Sledujte stav prihlášky {#3-track-the-applications-status}

Ako veci postupujú, otvorte prihlášku, vyberte nový **Stav** a kliknite
na **Uložiť**:

| Stav | Význam |
|---|---|
| **Nová** | Práve prišla. |
| **Kontaktovaný** | Ozvali ste sa; uchádzač je v poradovníku. |
| **Záhrada ponúknutá** | Ponúkli ste konkrétnu parcelu. |
| **Prijaté** | Uchádzač chce parcelu; odovzdanie sa pripravuje. |
| **Zamietnuté** | Žiadne ďalšie ponuky. |
| **Uzavreté (záhrada pridelená)** | Nastaví sa automaticky cez **Prideliť parcelu** (krok 5). |

Ak uchádzač odmietne parcelu, ale chce zostať v zozname, nastavte ho
späť na **Kontaktovaný**. Každá zmena stavu je uvedená v **História
stavu** na stránke prihlášky.

## 4. Uistite sa, že parcela je ukončená {#4-make-sure-the-parcel-is-terminated}

**Prideliť parcelu** ponúka len parcely so stavom **ukončená** --
parcelu, ktorú niekto opustil alebo práve opúšťa.

1. Otvorte parcelu v **Parcely** a kliknite na **Upraviť**.
2. Nastavte **Stav** na **ukončená**, voliteľne pridajte **Poznámka k
   ukončeniu** a kliknite na **Uložiť zmeny**.

Ak je doterajší nájomca ešte v procese odchodu, pozri [Odovzdanie
parcely](parcel-handover.md) -- opisuje celé odovzdanie vrátane strany
doterajšieho nájomcu.

## 5. Prideľte parcelu {#5-assign-the-parcel}

1. Otvorte prihlášku a kliknite na **Prideliť parcelu**. (Tlačidlo je
   tam pri každej otvorenej prihláške -- **Nová**, **Kontaktovaný**,
   **Záhrada ponúknutá** alebo **Prijaté**.)
2. Vyberte **Ukončená parcela**. Zoznam ukazuje každú parcelu s jej
   súčasnými nájomcami.
3. Nastavte **Dátum odovzdania** -- deň, keď nový nájomca preberá
   parcelu. Môže byť v budúcnosti.
4. Voliteľne zaškrtnite **Ďalší uchádzači (spolunájomcovia)** --
   napríklad partnera, ktorý sa prihlásil osobitne a preberá parcelu
   spolu s týmto uchádzačom.
5. Voliteľne zadajte **Priečinok dokumentov pre nových nájomcov**
   (zobrazí sa len, ak smiete spravovať cloudové priečinky).
6. Kliknite na **Náhľad**.
7. Skontrolujte pole **Odovzdanie parcely … dňa …**:
    - **Doterajší nájomcovia**: ich nájom končí dňom odovzdania. Ak
      nemajú inú parcelu, ich členstvo končí deň predtým.
    - **Noví nájomcovia a príjemcovia faktúr**: každý uchádzač sa buď
      **stane novým členom** (meno, e-mail a telefón sa prevezmú z
      prihlášky), alebo, ak aktívny člen už používa tú istú e-mailovú
      adresu, sa prepojí s týmto existujúcim členom.
8. Kliknite na **Odovzdať parcelu** a potvrďte.

Čo sa stane v jednom kroku:

- Uchádzači sa stanú členmi, s **Členom od** nastaveným na dátum
  odovzdania.
- Stanú sa nájomcami parcely odo dňa odovzdania, s nastaveným **Použiť
  ako fakturačnú adresu**.
- Doterajší nájomcovia sa stanú bývalými nájomcami -- história zostane
  na stránke parcely.
- Stav parcely sa vráti na **aktívna**.
- Prihlášky sa nastavia na **Uzavreté (záhrada pridelená)**.

Pri dátume odovzdania v budúcnosti zostávajú doterajší nájomcovia
nájomcami, členmi a príjemcami faktúr až do tohto dňa; noví sú na
stránke parcely zobrazení ako budúci („od …“) a v ten deň preberajú.

## 6. Doplňte záznam nového člena {#6-complete-the-new-members-record}

Odovzdanie kopíruje len meno, e-mail a telefón. Doplňte zvyšok:

1. Otvorte **Členovia** a kliknite na nového člena (alebo použite odkaz
   zo stránky parcely).
2. Kliknite na **Upraviť** a doplňte **Dátum narodenia**, **IBAN** a
   adresu (**Ulica a číslo domu**, **PSČ**, **Mesto**).
3. Skontrolujte **Môže dostávať informácie e-mailom**. Pri členoch
   vytvorených cez **Prideliť parcelu** je zaškrtnuté, pretože uchádzač
   uviedol e-mailovú adresu; odškrtnite ho, ak člen chce len papier.
   Bez neho idú faktúry a oznamy do kôpky na tlač namiesto do schránky.
4. V **Štítky** zaškrtnite existujúce štítky alebo napíšte nové
   (napríklad „tím živého plota“), oddelené čiarkami.
5. Kliknite na **Uložiť zmeny**.

Štítky môžete pridať aj priamo na stránke člena, na karte **Štítky**,
tlačidlom **Pridať štítok**.

## 7. Bez prihlášky: vytvorte člena ručne {#7-without-an-application-create-the-member-by-hand}

1. Otvorte **Členovia** a kliknite na **Nový člen**.
2. Vyplňte **Meno** a **Priezvisko** (povinné), adresu, **Dátum
   narodenia**, **IBAN**, **Členom od**, **E-mailová adresa** a
   **Telefónne číslo**, **Môže dostávať informácie e-mailom** a
   prípadné **Štítky**.
3. Kliknite na **Vytvoriť člena**.
4. Na stránke člena v **Pridelené parcely** vyberte parcelu v
   **Vyberte parcelu…**, nechajte zaškrtnuté **Použiť ako fakturačnú
   adresu**, ak má tento člen dostávať faktúry parcely, a kliknite na
   **Priradiť**.

Prípadne priraďte zo stránky parcely: **Súčasní nájomcovia → Vyberte
člena… → Priradiť**, kde môžete zadať aj dátum začiatku. Ak chcete
dátum začiatku neskôr opraviť, použite ikonu ceruzky vedľa nájomcu na
stránke parcely (**Upraviť nájom**, pole **Nájomca od**).

Ak je na parcele ešte doterajší nájomca, najprv ukončite jeho nájom --
pozri [Odovzdanie parcely](parcel-handover.md).

## 8. Privítajte nového člena {#8-welcome-the-new-member}

Parcella nemá automatický uvítací e-mail. Pomôžu dve veci:

**Proces prijatia.** Modul **Procesy** obsahuje príkladovú šablónu
**Prijatie nového člena** s tromi fázami: **Privítanie** (**Uvítacie
stretnutie**, **Stanovy a záhradný poriadok odovzdané**), **Dokumenty**
(**Podpísaná prihláška**, **Súhlas s inkasom prijatý**) a
**Dokončenie** (**Pridaný do rozosielacieho zoznamu**, **Poznámky**).

1. Raz: otvorte **Procesy → Šablóny** a v **Začať príkladom** kliknite
   na **Použiť** vedľa **Prijatie nového člena**. Fázy a polia podľa
   potreby upravte. (Vytváranie šablón potrebuje plný prístup.)
2. Pre každého nového člena: na stránke člena, na karte **Procesy**,
   kliknite na **Začať proces**, vyberte **Šablóna** a kliknite na
   **Začať**.
3. Vypĺňajte polia, ako sa veci vybavujú, a klikajte na **Hotovo --
   ďalšia fáza**. Povinné polia treba vyplniť, kým sa posuniete ďalej.

**Osobná správa.** Pri zapnutom module **Oznamy** zaškrtnite nového
člena v zozname **Členovia** a kliknite na **Napísať vybratým**.

## Súvisiace {#related}

- [Uchádzači](../modules/applicants.md)
- [Členovia](../modules/members.md)
- [Parcely](../modules/parcels.md)
- [Procesy](../modules/processes.md)
- [Oznamy](../modules/announcements.md)
- [Odovzdanie parcely](parcel-handover.md)
- Slovník: [uchádzač](../glossary.md#applicant),
  [nájom](../glossary.md#tenancy),
  [fakturačná adresa](../glossary.md#invoice-address)

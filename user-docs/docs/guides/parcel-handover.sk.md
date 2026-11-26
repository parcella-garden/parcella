# Odovzdanie parcely {#handing-over-a-parcel}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Nájomca dá výpoveď, parcela sa obhliadne a ocení, ponúkne sa ľuďom z
poradovníka a nakoniec nový nájomca podpíše a dostane kľúče. Trvá to
týždne alebo mesiace a zapája to viacerých členov výboru. Tento návod
ukazuje, čo Parcella po ceste zaznamenáva a ako
[proces](../glossary.md#process) sleduje kroky, ktoré sama
nezaznamenáva.

## Čo Parcella sleduje -- a čo nie {#what-parcella-does-and-doesnt-track}

| Časť odovzdania | V Parcelle |
|---|---|
| Výpoveď | Stav parcely **ukončená**, s dátumom zaznamenaným automaticky a voliteľnou **Poznámka k ukončeniu**. |
| Doterajší a noví nájomcovia | Ukončenie doterajšieho [nájmu](../glossary.md#tenancy) ho zachová ako históriu; nový nájom začína dňom odovzdania. **Prideliť parcelu** pri prihláške urobí oboje jedným krokom. |
| Členstvo doterajšieho nájomcu | Skončí automaticky pri **Prideliť parcelu**, ak nemá inú parcelu. |
| Priečinok dokumentov | Cloudový priečinok doterajších nájomcov sa v deň odovzdania vyradí; nahradí ho nový. |
| Obhliadka, [ocenenie](../glossary.md#valuation), ponuka, prehliadka, zmluva, kľúče | Nie sú vstavané. Sledujte ich **procesom** (krok 1). |
| [Kaucia](../glossary.md#deposit) | Žiadna funkcia kaucie. Sumu a dátum si poznačte v procese; peniaze zaúčtujte vo **Financie**, ak ich používate (krok 7). |
| Konečné stavy meradiel | Parcella uchováva **jeden odpočet na meradlo a rok**. Stavy pri odovzdaní si poznačte v procese (krok 6). |
| Cena medzi doterajším a novým nájomcom | **Zámerne sa nesleduje.** Čo nový nájomca platí doterajšiemu za záhradnú chatku a rastliny, je súkromná vec medzi nimi dvoma. Parcella na to nemá pole -- nepridávajte ho ani do svojej šablóny procesu. |

!!! info "Kto to môže robiť"
    Zmeny parciel a nájmov potrebujú **zápis** pre **Členovia a
    parcely**; **Prideliť parcelu** potrebuje aj **zápis** pre
    **Uchádzači**. Šablóny procesov potrebujú plný prístup (výbor alebo
    administrátor); práca na procese potrebuje **zápis** pre **Procesy**.

## 1. Pripravte šablónu procesu odovzdania (raz) {#1-prepare-a-handover-process-template-once}

Modul **Procesy** obsahuje príkladovú šablónu **Odovzdanie záhradky**.
Začnite od nej a prispôsobte ju postupu vášho spolku.

1. Otvorte **Procesy → Šablóny** (stránka sa volá **Šablóny procesov**).
2. V **Začať príkladom** kliknite na **Použiť** vedľa **Odovzdanie
   záhradky**. Parcella vytvorí bežnú šablónu, ktorú môžete voľne
   meniť. Týka sa **Záhradka**, takže každý proces patrí jednej parcele
   a zobrazí sa na jej stránke.
3. Príklad má šesť fáz: **Obhliadka**, **Ocenenie**, **Inzerát**,
   **Nový nájomca**, **Zmluva a kaucia** a **Odovzdanie**. Aby
   zodpovedal bežnému postupu nižšie, pridajte a premenujte fázy v
   editore (napíšte **Názov fázy** a kliknite na **Pridať**; fázy
   presúvajte ťahaním; polia pridáte napísaním názvu a stlačením
   Enter):

| Fáza | Príkladové polia | Typ poľa |
|---|---|---|
| Výpoveď *(nová, prvá)* | Výpoveď prijatá dňa (povinné) · List s výpoveďou | Dátum · Súbory (PDF, fotky) |
| **Obhliadka** | **Dátum obhliadky** · **Zistené nedostatky** · **Fotky nedostatkov** · **Všetky nedostatky odstránené** | z príkladu |
| **Ocenenie** | **Odhadca** · **Dátum ocenenia** · **Posudok** | z príkladu |
| **Inzerát** → premenujte na „Ponuka pre poradovník“ | **Text inzerátu** · **Zverejnené dňa** | z príkladu |
| Prehliadka *(nová)* | Dátum prehliadky · Záujemcovia (poznámky) | Dátum · Dlhý text |
| **Nový nájomca** | **Nový nájomca** (uchádzač) · **Kontakt nadviazaný** · **Dokumenty odoslané** | z príkladu |
| **Zmluva a kaucia** | **Kúpna zmluva potvrdená** · **Kaucia** · **Kaucia prijatá dňa** | z príkladu |
| **Odovzdanie** → rozdeľte na „Podpis“ a „Záverečný zoznam“ | Podpis: **Podpísané novým nájomcom**, **Spolupodpísané výborom**. Záverečný zoznam: **Kľúče odovzdané**, **Merače odčítané**, **Odovzdávací protokol** | z príkladu |

4. Vo fáze „Záverečný zoznam“ pridajte polia **Číslo** pre stavy
   meradiel pri odovzdaní, napr. „Stav vodomera pri odovzdaní“ a „Stav
   elektromera pri odovzdaní“ (pozri krok 6).

Pole označte ako **Povinné**, ak proces nesmie bez neho pokračovať.
Zmeny šablóny ovplyvnia len procesy začaté neskôr.

!!! tip
    **Kúpna zmluva potvrdená** je len zaškrtávacie pole: výbor potvrdí,
    že doterajší a nový nájomca sa dohodli. Samotná cena zostáva medzi
    nimi dvoma.

Viac: [Procesy](../modules/processes.md).

## 2. Zaznamenajte výpoveď {#2-record-the-notice}

Keď príde výpoveď nájomcu:

1. Otvorte parcelu v **Parcely** a kliknite na **Upraviť**.
2. Nastavte **Stav** na **ukončená**. Parcella zaznamená čas zmeny
   stavu; stránka parcely potom ukazuje **Ukončená dňa**.
3. Voliteľne pridajte **Poznámka k ukončeniu** (dôvod, dátum výpovede,
   pripomienky).
4. Kliknite na **Uložiť zmeny**.

Nájomca zostáva súčasným nájomcom -- a ďalej dostáva faktúry parcely --,
kým nájom naozaj neskončí. Nájom teraz neukončujte; **Prideliť
parcelu** to urobí v deň odovzdania (krok 5).

## 3. Začnite proces {#3-start-the-process}

1. Na stránke parcely, na karte **Procesy**, kliknite na **Začať
   proces**.
2. Vyberte svoju **Šablóna** odovzdania. Voliteľne dajte procesu
   **Názov**.
3. Kliknite na **Začať**.
4. Vyplňte polia prvej fázy a kliknite na **Uložiť**. Keď je fáza
   hotová, kliknite na **Hotovo -- ďalšia fáza**.

Proces sa zobrazí na stránke parcely so svojou aktuálnou fázou a v
**Procesy** pre všetkých, ktorí na ňom pracujú. Nahrané súbory (listy,
fotky, posudok) idú do cloudového priečinka parcely, ak je nastavený,
inak do vlastného úložiska Parcelly.

Ak sa chcete vrátiť na skoršiu fázu, kliknite na **Vrátiť sa**, vyberte
fázu a uveďte **Dôvod**. Ak odovzdanie stroskotá, použite **Prerušiť
proces** s dôvodom.

## 4. Obhliadka, ocenenie, ponuka, prehliadka {#4-inspection-valuation-offer-viewing}

Tieto fázy procesu prechádzajte, ako sa dejú. Posudok
[ocenenia](../glossary.md#valuation) ide do **Posudok**; text ponuky do
**Text inzerátu**.

Záujemcov nájdete tak, že otvoríte **Uchádzači** s filtrom
**Otvorené** -- zoznam je zoradený podľa dátumu prihlášky. Tým, ktorým
parcelu ponúknete, nastavte **Záhrada ponúknutá** a tomu, kto ju
prevezme, **Prijaté**. Pri zapnutom module **Oznamy** zaškrtnite
viacerých uchádzačov a kliknite na **Napísať vybraným uchádzačom**, aby
ste ponuku poslali e-mailom.

Viac: [Uchádzači](../modules/applicants.md).

## 5. Odovzdajte parcelu novému nájomcovi {#5-hand-the-parcel-over-to-the-new-tenant}

Keď je zmluva podpísaná -- alebo, s dátumom v budúcnosti, hneď ako je
termín pevný:

1. Otvorte prihlášku nového nájomcu a kliknite na **Prideliť parcelu**.
2. Vyberte túto parcelu v **Ukončená parcela** a nastavte **Dátum
   odovzdania**.
3. Pridajte partnera v **Ďalší uchádzači (spolunájomcovia)**, ak
   preberajú parcelu spolu.
4. Ak používate cloudové úložisko, zadajte **Priečinok dokumentov pre
   nových nájomcov**. Priečinok doterajších nájomcov sa v deň odovzdania
   vyradí v každom prípade.
5. Kliknite na **Náhľad**, skontrolujte doterajších a nových nájomcov,
   potom kliknite na **Odovzdať parcelu** a potvrďte.

V deň odovzdania:

- doterajší nájom skončí a presunie sa do **Bývalí nájomcovia** na
  stránke parcely;
- doterajší nájomca bez inej parcely odíde zo spolku (**Členom do** je
  deň pred dátumom odovzdania);
- uchádzači sa stanú členmi, nájomcami a príjemcami faktúr;
- parcela je znova **aktívna**.

Podrobnosti a doplnenie záznamu nového člena nájdete v časti [Prijatie
nového člena](new-member.md), kroky 5 a 6.

### Ak nový nájomca nie je uchádzač {#if-the-new-tenant-isnt-an-applicant}

Napríklad člen rodiny, ktorý preberá parcelu. Urobte to ručne:

1. Na stránke parcely, v **Súčasní nájomcovia**, kliknite na ikonu
   ceruzky vedľa doterajšieho nájomcu (**Upraviť nájom**), nastavte
   **Nájomca do** na posledný deň a kliknite na **Uložiť zmeny**.
   Alebo, ak ho chcete ukončiť dnes, kliknite na ikonu **Ukončiť nájom**
   a potvrďte *„Ukončiť toto nájomné? (história zostáva zachovaná)“*.
2. Ak doterajší nájomca odchádza zo spolku, otvorte jeho stránku člena,
   kliknite na **Upraviť**, nastavte **Členom do** a kliknite na
   **Uložiť zmeny**. Nemažte ho -- pozri varovanie nižšie.
3. Priraďte nového nájomcu: **Vyberte člena…**, dátum začiatku,
   **Použiť ako fakturačnú adresu**, **Priradiť**. V prípade potreby ho
   najprv vytvorte v **Členovia → Nový člen**.
4. Upravte parcelu a nastavte **Stav** späť na **aktívna**.

!!! tip "Zaznamenanie výpovede"
    Nájomca, ktorý dal výpoveď, zostáva fakturačnou adresou, kým
    neodíde: nastavte jeho **Nájomca do** v **Upraviť nájom** a nechajte
    zaškrtnuté **Použiť ako fakturačnú adresu**. Keď ten deň uplynie,
    políčko sa samo zruší -- dovtedy zaistite, aby fakturačnou adresou
    bol nový nájomca.

!!! warning "Ukončujte, nemažte"
    Ukončenie nájmu alebo členstva zachová históriu: kto mal ktorú
    parcelu a kedy a ktoré hodiny a faktúry patrili komu. Zmazanie člena
    ho odstráni z každého hodnotenia, vrátane pracovných hodín rokov, v
    ktorých bol nájomcom.

## 6. Konečné stavy meradiel {#6-final-meter-readings}

Parcella ukladá jeden odpočet na meradlo a rok a z neho vychádza ročná
faktúra. Samostatný „odpočet pri odovzdaní“ neexistuje.

- Stavy v deň odovzdania zapíšte do procesu (fáza „Záverečný zoznam“
  z kroku 1) a zaškrtnite **Merače odčítané**.
- Nezadávajte ich ako odpočet roka pri meracom bode, pokiaľ to naozaj
  nechcete: ročný odpočet neskôr v roku ich **nahradí**.
- Ročná faktúra za vodu a elektrinu parcely ide tomu, kto je príjemcom
  faktúr v čase dokončenia [vyúčtovania](../glossary.md#invoice-run) --
  po odovzdaní novému nájomcovi -- za spotrebu celého roka. Ako si to
  doterajší a nový nájomca rozdelia, závisí od nich a od pravidiel
  vášho spolku; vyrovnajte to mimo Parcelly s pomocou stavov v procese.

Ak sa pri odovzdaní vymieňa meradlo, pozri [Odpočty
meradiel](meter-readings.md#a-meter-is-replaced).

## 7. Kaucia a peniaze {#7-deposit-and-money}

Parcella nemá pole kaucie pri parcele ani pri členovi. Na evidenciu
použite proces: **Kaucia** (suma) a **Kaucia prijatá dňa** vo fáze
**Zmluva a kaucia**.

Ak používate modul **Financie**, zaúčtujte aj samotné peniaze:

- **Prijatá kaucia**: otvorte **Financie → Prehľad → Účty**, kliknite
  na **Zápisy** vedľa účtu, na ktorý peniaze prišli, a použite **Pridať
  zápis** (alebo **Import CSV** s bankovým výpisom).
- **Vrátenie kaucie doterajšiemu nájomcovi**: to isté, ako záporná suma.

<!-- TODO(verify): confirm with the treasurer whether a deposit should rather be billed as a one-off invoice run (a "Fixed amount per parcel" item scoped to this parcel) so it gets an invoice number. -->

**Pracovné hodiny.** Nájomca, ktorý odchádza počas roka, stále dlží
[povinné hodiny](../glossary.md#mandatory-hours) za tento rok. Pri
fakturácii na parcelu sa jeho hodiny počítajú spolu s hodinami nového
nájomcu a nedoplatok sa fakturuje príjemcovi faktúr parcely v čase
vyúčtovania -- novému nájomcovi. Ak to váš spolok nechce, vyrovnajte to
ručne. Pozri [Ročné vyúčtovanie](annual-invoicing.md).

**Otvorené faktúry** doterajšieho nájomcu zostávajú, ako sú; číslo
faktúry, príjemca a adresa sú uložené pri každej faktúre, takže ich
stále môžete vymáhať a upomínať.

## 8. Uzavrite proces {#8-close-the-process}

Keď je posledná fáza hotová, kliknite na **Dokončiť proces**. Dokončený
proces je len na čítanie a zostáva na stránke parcely s celou
**História**.

## Súvisiace {#related}

- [Parcely](../modules/parcels.md)
- [Uchádzači](../modules/applicants.md)
- [Členovia](../modules/members.md)
- [Procesy](../modules/processes.md)
- [Voda a elektrina](../modules/metering.md)
- [Bankové účty a zaúčtovania](../modules/finances/bank-accounts.md)
- [Prijatie nového člena](new-member.md)
- Slovník: [kaucia](../glossary.md#deposit),
  [ocenenie](../glossary.md#valuation),
  [výpoveď](../glossary.md#notice-of-termination),
  [nájom](../glossary.md#tenancy)

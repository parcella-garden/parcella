# Import členov a parciel {#importing-members-and-parcels}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Ak váš spolok už vedie zoznam členov, parciel alebo meradiel v tabuľke,
nemusíte všetko písať znova. Uložte tabuľku ako súbor CSV, nahrajte ho,
povedzte Parcelle, ktorý stĺpec je ktorý, a importujte.

Funguje to rovnako pre **parcely**, **členov**, **meracie body**,
**odpočty meradiel** a **externé kontakty**. Tento návod ich prechádza v
poradí, ktoré má zmysel pre novú inštaláciu.

!!! info "Kto to môže robiť"
    Import členov a parciel potrebuje oprávnenie **zápis** pre **Členovia
    a parcely**; meracie body a odpočty potrebujú zápis pre **Voda**
    alebo **Elektrina**; externé kontakty potrebujú zápis pre **Externé
    kontakty**. Členovia výboru a administrátori majú všetky.

!!! warning "Najprv si stiahnite zálohu"
    Import zapíše veľa záznamov naraz a „späť“ neexistuje. Skôr než
    začnete, otvorte **Administrácia → Systém** a kliknite na **Stiahnuť
    zálohu**. Pozri [Zálohovanie a obnova](../administration/backup.md).

## Ako funguje každý import {#how-every-import-works}

Všetkých päť importov má tie isté dva kroky.

1. **Nahrať.** Na stránke zoznamu kliknite na **CSV import**, vyberte
   súbor a kliknite na **Importovať**. Zatiaľ sa nič neuloží.
2. **Mapovanie stĺpcov CSV.** Parcella ukáže tabuľku: jeden stĺpec na
   každý stĺpec vášho súboru, s vaším nadpisom hore a prvými piatimi
   riadkami dát pod ním. Nad každým stĺpcom je rozbaľovací zoznam.
   Parcella už z nadpisu odhadla zodpovedajúce pole (fungujú anglické aj
   nemecké nadpisy, napríklad „Nachname“ alebo „Last name“).
   Skontrolujte každý zoznam, opravte nesprávne a stĺpce, ktoré
   nechcete, nastavte na **— Ignorovať —**. Potom kliknite na
   **Importovať**.

Potom ste späť na stránke zoznamu s krátkym zhrnutím: koľko riadkov bolo
vytvorených, aktualizovaných alebo preskočených a dôvody pre prvých pár
preskočených riadkov.

### Ako by mal súbor vyzerať {#what-your-file-should-look-like}

- **Prvý riadok obsahuje nadpisy stĺpcov.** Každý riadok pod ním je
  jeden záznam. Nadpisy sa nemusia presne zhodovať -- priradíte ich v
  kroku 2.
- **Bodkočiarka alebo čiarka** medzi stĺpcami: Parcella rozpozná, ktorú
  váš súbor používa.
- **Najlepšie UTF-8.** Väčšina tabuľkových programov pri ukladaní ponúka
  „CSV UTF-8“. Funguje aj obyčajné „CSV“ z Excelu (Windows/ANSI):
  diakritika prejde v oboch prípadoch.
- **Dátumy** ako `2026-03-15` alebo `15.03.2026` (aj `15.03.26`).
- **Desatinné čísla** s čiarkou alebo bodkou: funguje `312,5` aj
  `312.5`. Bankové sumy a odpočty meradiel môžu mať aj oddeľovače
  tisícov, po nemecky alebo po anglicky: `12.345,6` a `12,345.6`.
- **Viac hodnôt v jednej bunke** (e-mailové adresy, telefónne čísla,
  štítky) sa oddeľuje bodkočiarkou. Tabuľkový program takúto bunku pri
  ukladaní dá do úvodzoviek -- to je v poriadku.

!!! tip "Začnite od exportu"
    Najjednoduchšou šablónou je vlastný export Parcelly. Každý zoznam s
    importom má aj **CSV export**. Exportujte (ešte prázdny alebo
    ukážkovými dátami naplnený) zoznam, vyplňte súbor v tabuľkovom
    programe a znova ho importujte: nadpisy potom sedia bez akéhokoľvek
    priraďovania.

## 1. Parcely {#1-parcels}

Najprv importujte parcely. Členovia, meracie body a odpočty sa na
parcely odvolávajú ich číslom.

1. Otvorte **Parcely** a kliknite na **CSV import**.
2. Vyberte súbor a kliknite na **Importovať**.
3. Na **Mapovanie stĺpcov CSV** priraďte aspoň **Číslo parcely**.
   Ostatné polia sú voliteľné.
4. Kliknite na **Importovať**. Zhrnutie znie napríklad *„24
   importovaných, 0 preskočených“*.

| Pole | Čo Parcella očakáva |
|---|---|
| **Číslo parcely** | Povinné. Ukladá sa veľkými písmenami („g12“ sa stane „G12“). |
| **Rozloha (m²)** | Číslo, s čiarkou alebo bodkou ako desatinným oddeľovačom. Čokoľvek iné zostane prázdne. |
| **Zemepisná šírka** / **Zemepisná dĺžka** | Voliteľná poloha GPS, v desatinných stupňoch (napr. `51,339695`). |
| **Stav** | `ACTIVE`, `TERMINATED`, `COMMUNAL` alebo `DELETED` (veľkými alebo malými písmenami). Prázdne alebo čokoľvek iné znamená aktívna. |
| **Poznámky** | Voľný text. |

!!! warning "Existujúce parcely sa preskočia, neaktualizujú"
    Ak číslo parcely v Parcelle už existuje, tento riadok sa
    **preskočí** a existujúca parcela zostane presne taká, aká je. Ak
    chcete existujúce parcely zmeniť, upravte ich ručne. Riadky bez
    čísla parcely sa ignorujú a v zhrnutí sa počítajú zvlášť.

Import parciel **nepriraďuje** nájomcov. Export parciel má stĺpec s
menami nájomcov, ale import ho ignoruje -- pozri krok 3 nižšie.

## 2. Členovia {#2-members}

1. Otvorte **Členovia** a kliknite na **CSV import**.
2. Vyberte súbor a kliknite na **Importovať**.
3. Na **Mapovanie stĺpcov CSV** priraďte aspoň **Meno** a
   **Priezvisko**. Bez oboch sa import zastaví hlásením *„Pred importom
   prosím priraďte stĺpce mena a priezviska.“*
4. Kliknite na **Importovať**. Zhrnutie znie napríklad *„80 nových
   importovaných, 0 aktualizovaných“*.

| Pole | Čo Parcella očakáva |
|---|---|
| **Meno**, **Priezvisko** | Povinné. Riadok s jedným z nich prázdnym sa preskočí. |
| **Ulica**, **PSČ**, **Mesto** | Voľný text. |
| **Dátum narodenia** | Dátum (pozri vyššie). Používa sa aj na rozlíšenie dvoch členov s rovnakým menom. |
| **IBAN** | Voľný text, nekontroluje sa. |
| **Členom od**, **Členom do** | Dátumy. Prázdne **Členom do** znamená aktívneho člena. |
| **E-mailové upozornenia** | „No“, „Nein“, „false“ alebo „0“ znamená, že člen **nechce** informácie spolku e-mailom; čokoľvek iné vyplnené znamená áno. Prázdna bunka alebo nepriradený stĺpec znamená áno pre nového člena a „bez zmeny“ pre existujúceho. |
| **E-mailové adresy** | Jedna alebo viac, oddelené bodkočiarkami. Prvá sa stane hlavnou adresou. |
| **Telefónne čísla** | Jedno alebo viac, oddelené bodkočiarkami. Prvé sa stane hlavným číslom. |
| **Poznámky** | Voľný text. |

**Párovanie existujúcich členov.** Pre každý riadok Parcella hľadá
existujúceho člena s rovnakým menom a priezviskom -- a ak má riadok
dátum narodenia, aj s rovnakým dátumom narodenia. Ak nájde práve
jedného, **aktualizuje** tohto člena namiesto vytvorenia druhého. Ak má
toto meno viac členov, správneho vyberú e-mailové adresy a telefónne
čísla z riadku; ak riadok stále pasuje na viac ako jedného, preskočí sa
a uvedie v zhrnutí. Samotný e-mail alebo telefón nikdy nespáruje člena s
iným menom.

Aktualizácia mení len to, čo riadok obsahuje: stĺpec nastavený na **—
Ignorovať —** alebo prázdna bunka nechá uloženú hodnotu tak. Môžete
teda aktualizovať len adresy súborom, ktorý obsahuje len mená a adresy.
E-mailové adresy a telefónne čísla sa pri aktualizácii nikdy nemenia;
pridávajú sa len pre nových členov.

Štítky, priradenia parciel a nastavenie **Neželá si narodeninové
darčeky** nie sú súčasťou importu. Export obsahuje stĺpce **Parcely** a
**Štítky**, ale import ich ignoruje.

## 3. Priraďte členov k ich parcelám {#3-assign-members-to-their-parcels}

Import nájmov neexistuje. Keď členovia a parcely existujú, priraďte ich
ručne:

1. Otvorte parcelu v **Parcely**.
2. V **Súčasní nájomcovia** začnite písať meno člena do **Vyberte
   člena…** a vyberte ho zo zoznamu.
3. Voliteľne zadajte dátum začiatku nájmu.
4. Nechajte zaškrtnuté **Použiť ako fakturačnú adresu** pri nájomcovi,
   ktorý má dostávať faktúry parcely.
5. Kliknite na **Priradiť**.

Pri mnohých parcelách vás tlačidlo **Ďalší** hore na stránke parcely
zavedie rovno na ďalšiu.

Viac: [Parcely](../modules/parcels.md).

## 4. Meracie body {#4-metering-points}

Meracie body sú prípojky vody a elektriny (hlavný merač, jedna na
parcelu, prípojky spolku). Voda a elektrina sa importujú zvlášť, každá
vo vlastnom menu.

1. Otvorte **Voda → Meracie body** (alebo **Elektrina → Meracie body**)
   a kliknite na **CSV import**.
2. Vyberte súbor a kliknite na **Importovať**.
3. Priraďte stĺpce a kliknite na **Importovať**. Aspoň jeden stĺpec
   musí byť priradený.

| Pole | Čo Parcella očakáva |
|---|---|
| **Typ** | `PARCEL`, `MAIN_METER` alebo `CLUB`. Ak tento stĺpec vôbec nepriradíte, každý riadok sa počíta ako prípojka parcely. Ak ho priradíte, riadok s prázdnym alebo neznámym typom sa preskočí („neplatný typ“). |
| **Číslo parcely** | Povinné pre prípojky parciel; musí zodpovedať existujúcemu číslu parcely, inak sa riadok preskočí („parcela nenájdená“). |
| **Označenie** | Názov hlavného merača alebo prípojky spolku, napr. „Klubovňa“. |
| **Číslo meradla** | Číslo vytlačené na meradle. |
| **Inštalované** | Dátum. |
| **Kalibrovaný do** | Len **rok**, napr. `2031`. |
| **Počiatočný stav** | Odpočet pri inštalácii meradla. Prázdne znamená 0. |
| **Násobiteľ** | Zvyčajne prázdne (= 1). Pri meradlách, ktoré ukazujú len časť skutočnej hodnoty, napr. `20`. Musí byť väčší ako 0. |

Import meracie body len **vytvára**. Parcela, ktorá už má merací bod pre
toto médium, alebo hlavný merač či prípojka spolku s rovnakým
označením, sa preskočí ako „už existuje“ -- dvojitý import toho istého
exportu teda neuškodí. Nové meracie body vždy začínajú zapnuté.

!!! note
    **Kalibrovaný do** je rok. Dátum v tomto stĺpci (`30.06.2027`,
    `2027-06`, `06/2027`) je tiež v poriadku: Parcella z neho vezme rok.
    Riadok, ktorého hodnota nemá štvorciferný rok (`06/27`, `čoskoro`),
    sa preskočí s hlásením „„Kalibrovaný do“ nie je rok“; ostatné
    riadky sa importujú.

Viac: [Voda a elektrina](../modules/metering.md).

## 5. Odpočty meradiel {#5-meter-readings}

Odpočty sa pripájajú k meracím bodom, ktoré už existujú; import nikdy
nevytvorí merací bod.

1. Otvorte **Voda → Odpočty** (alebo **Elektrina → Odpočty**) a kliknite
   na **CSV import**.
2. Vyberte súbor a kliknite na **Importovať**.
3. Priraďte stĺpce. Ak váš súbor nemá stĺpec s rokom alebo ho niektoré
   riadky nechávajú prázdny, zadajte rok do **Predvolený rok
   (voliteľné)**.
4. Kliknite na **Importovať**.

| Pole | Čo Parcella očakáva |
|---|---|
| **Typ** | Ako pri meracích bodoch. Nepriradené = každý riadok je prípojka parcely. |
| **Číslo parcely** / **Označenie** | Nájdu merací bod, rovnako ako vyššie. |
| **Číslo meradla** | Voliteľná kontrola. Ak nezodpovedá práve nainštalovanému meradlu, riadok sa preskočí („nezhodné číslo merača“) -- pravdepodobne patrí meradlu, ktoré bolo medzitým vymenené. |
| **Rok** | Rok, ku ktorému odpočet patrí. Má prednosť pred **Predvolený rok (voliteľné)**. |
| **Dátum** | Deň odčítania meradla. Povinné. |
| **Stav meradla** | Hodnota na displeji. Povinné. |
| **Poznámka** | Voľný text. |

Parcella nikdy neháda rok z dátumu. Odpočet urobený v januári môže stále
patriť k vyúčtovaniu minulého roka, takže vy poviete, ktorý rok to je.

Jeden súbor môže obsahovať viac rokov. Ak merací bod už má odpočet za
daný rok, import ho **nahradí**.

Odpočet, ktorý vyzerá nevierohodne -- napríklad nižší ako
predchádzajúci --, sa aj tak uloží. Zhrnutie potom ukáže samostatné
upozornenie s dotknutými riadkami, aby ste ich mohli skontrolovať.

Viac: [Odpočty meradiel](meter-readings.md).

## 6. Externé kontakty {#6-external-contacts}

Dodávatelia, remeselníci a úrady, ak používate modul **Externé
kontakty**.

1. Otvorte **Externé kontakty** a kliknite na **Import CSV**.
2. Vyberte súbor a kliknite na **Importovať**.
3. Na **Priradiť stĺpce** priraďte stĺpce. Žiadne pole nie je povinné;
   úplne prázdne riadky sa preskočia.
4. Kliknite na **Importovať**.

| Pole | Čo Parcella očakáva |
|---|---|
| **Typ (firma/osoba)** | „Firma“, „Company“ alebo „Unternehmen“ pre firmu; „Person“ pre osobu. Bez neho je riadok s menom alebo priezviskom osoba, inak firma. |
| **Názov firmy** | Pri firme: jej názov. Pri osobe: firma, ku ktorej patrí -- vytvorí sa, ak ešte neexistuje. |
| **Meno**, **Priezvisko**, **Pozícia** | Pri osobách. |
| **Ulica**, **PSČ**, **Mesto**, **IBAN** | Adresa a bankové údaje. Pri osobe vo firme doplnia prázdne polia firmy. |
| **E-mailové adresy**, **Telefónne čísla**, **Štítky** | Viac hodnôt oddelených bodkočiarkami. |
| **Poznámky** | Voľný text. |

Firma, ktorá už existuje (rovnaký názov, bez ohľadu na veľkosť písmen),
alebo osoba s rovnakým menom sa **aktualizuje** z neprázdnych buniek
riadku. Chýbajúce telefónne čísla, e-maily a štítky sa pridajú. Na
rozdiel od importu členov sa nikdy nič nevymaže ani neodstráni.

Viac: [Externé kontakty](../modules/external-contacts.md).

## Časté problémy {#common-problems}

| Čo vidíte | Prečo a čo robiť |
|---|---|
| *„Tento súbor CSV sa zdá byť prázdny.“* | Súbor nemá vôbec žiadne riadky. Skontrolujte, či ste uložili správny hárok. |
| Všetky dáta skončia na obrazovke priradenia v jednom stĺpci | Parcella nevedela určiť oddeľovač. Uložte súbor znova ako „CSV (oddelené bodkočiarkou)“ alebo „CSV (oddelené čiarkou)“. |
| Čudné znaky namiesto diakritiky | Súbor používa nezvyčajné kódovanie (ani UTF-8, ani Windows/ANSI, napr. zo starého Macu). Uložte ho znova ako „CSV UTF-8“. |
| Členovia preskočení s „chýba meno alebo priezvisko“ | Tieto riadky majú prázdnu bunku s menom alebo stĺpec s menom nebol priradený. |
| Člen sa objaví dvakrát | Dva riadky sa líšia pravopisom alebo dátumom narodenia, takže ich Parcella považuje za rôznych ľudí. Duplikát zmažte ručne. |
| Adresa existujúceho člena je zrazu prázdna | Člen bol aktualizovaný z riadku alebo súboru bez tohto stĺpca. Pozri varovanie v kroku 2; v prípade potreby obnovte dáta zo zálohy. |
| Parcely „preskočené“ | Číslo parcely už existuje. Existujúce parcely upravte ručne. |
| Meracie body „parcela nenájdená“ | Číslo parcely zo súboru v Parcelle neexistuje -- najprv importujte parcely a skontrolujte pravopis („G12“ verzus „G 12“). |
| Odpočty „merací bod nenájdený“ | Najprv importujte alebo vytvorte meracie body. Ak ste priradili **Typ**, skontrolujte jeho hodnotu. |
| Odpočty „neplatný riadok“ | **Dátum** alebo **Stav meradla** je prázdny alebo nezrozumiteľný, alebo chýba rok (ani stĺpec **Rok**, ani **Predvolený rok (voliteľné)**). |
| Odpočty „žiadny aktívny merač“ | Merací bod nemá nainštalované meradlo. Pridajte ho na stránke meracieho bodu. |
| `'` na začiatku exportovaných telefónnych čísel | Parcella ho pridáva k bunkám, ktoré začínajú `+`, `-`, `=` alebo `@`, aby ich tabuľkové programy nepovažovali za vzorce. Pred importom členov ho odstráňte, alebo ho nechajte -- import externých kontaktov ho odstráni za vás. |

## Súvisiace {#related}

- [Členovia](../modules/members.md)
- [Parcely](../modules/parcels.md)
- [Voda a elektrina](../modules/metering.md)
- [Externé kontakty](../modules/external-contacts.md)
- [Založenie nového spolku](new-club-setup.md)
- [Odpočty meradiel](meter-readings.md)

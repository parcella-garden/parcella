# Odpočty meradiel {#collecting-meter-readings}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Raz za rok niekto obíde areál a odčíta každý vodomer a elektromer:
hlavný merač spolku, jedno meradlo na parcelu a vlastné prípojky spolku
(klubovňa, umývacie miesto). Tento návod opisuje zadávanie týchto
odpočtov -- v telefóne počas obchôdzky alebo potom zo zoznamu -- plus
výmenu meradla a kontrolu výsledkov.

Voda a elektrina fungujú úplne rovnako; každá má vlastné menu. Kroky
nižšie hovoria o **Voda**; pre elektrinu použite namiesto toho menu
**Elektrina**.

!!! info "Kto to môže robiť"
    Zadávanie odpočtov potrebuje oprávnenie **zápis** pre **Voda** (alebo
    **Elektrina**); mazanie odpočtu potrebuje **mazanie**. Oba moduly sú
    predvolene zapnuté. Spolok môže dať tímu odpočtárov skupinu s presne
    týmito právami -- pozri [Skupiny](../administration/groups.md).

## Ako Parcella počíta spotrebu {#how-parcella-counts-consumption}

- Každý **[merací bod](../glossary.md#metering-point)** (prípojka
  parcely, hlavný merač, prípojka spolku) má naraz nainštalované jedno
  **meradlo**.
- Meradlo má **jeden odpočet za rok**. Spotreba roka je tento odpočet
  mínus odpočet predchádzajúceho roka -- alebo mínus **Počiatočný stav**
  meradla, ak ide o prvý odpočet.
- Zadanie odpočtu za rok, ktorý už nejaký má, ho **nahradí**.
- Odpočty sa zadávajú presne tak, ako ich ukazuje displej. Niektoré
  elektromery ukazujú len časť skutočnej hodnoty; ich merací bod má
  potom **Násobiteľ** (napr. 20), ktorým hodnotenie násobí.

## 1. Pred obchôdzkou: skontrolujte zoznam meracích bodov {#1-before-the-round-check-the-list-of-metering-points}

1. Otvorte **Voda → Prehľad**. Dlaždice ukazujú, koľko existuje
   hlavných meračov, prípojok parciel a spolku, a **Chýbajúce merné
   body**: parcely bez prípojky vody v Parcelle.
2. Kliknite na **Zobraziť** pod **Chýbajúce merné body** a uvidíte tieto
   parcely; každá odkazuje na **Nový merací bod** s už vybranou
   parcelou. Pridajte tie, ktoré naozaj majú meradlo.
3. Prípojka nejaký čas bez dodávky (voda zastavená na voľnej parcele)?
   Otvorte jej merací bod, nastavte **Vypnúť od** a kliknite na
   **Vypnúť**. Vypadne zo zoznamu odpočtov, kým ju **Znova zapnúť**.

Ak máte zoznam meradiel ešte v tabuľke, importujte ho -- pozri
[Import členov a parciel](csv-import.md#4-metering-points).

## 2. Možnosť A: zadávajte odpočty v telefóne počas obchôdzky {#2-option-a-enter-readings-on-your-phone-while-you-walk}

1. Otvorte v telefóne **Voda → Odpočty**. Stránka ukazuje aktuálny rok;
   v prípade potreby vyberte iný v zozname rokov hore.
2. Stránka uvádza **Hlavný merač**, **Parcely** (zoradené podľa čísla
   parcely) a **Prípojky spolku**. Každý riadok ukazuje číslo meradla a
   odpočet z **Predchádzajúci rok** na kontrolu.
3. Napíšte odpočet do poľa v riadku a ťuknite na tlačidlo uloženia vedľa
   neho. Riadok potom ukáže hodnotu ako **zaznamenané**.
4. Pokračujte ďalším meradlom. Riadky bez hodnoty hovoria **Zatiaľ
   nezadané**.

Odpočty zadané tu dostanú dnešný dátum. Ak chcete použiť iný dátum
alebo pridať poznámku, zadajte odpočet namiesto toho na stránke
meracieho bodu (možnosť C).

## 3. Možnosť B: zbierajte na papier alebo do tabuľky, potom importujte {#3-option-b-collect-on-paper-or-in-a-spreadsheet-then-import}

1. Otvorte **Voda → Odpočty**, vyberte rok a kliknite na **CSV
   export**. Dostanete súbor s jedným riadkom na meradlo: **Typ**,
   **Číslo parcely**, **Označenie**, **Číslo meradla**, **Rok** a
   prázdne stĺpce **Dátum**, **Stav meradla** a **Poznámka**.
2. Vytlačte ho alebo ho vypĺňajte na tablete. Vyplňte **Dátum** a
   **Stav meradla** pre každé odčítané meradlo.
3. Späť na **Voda → Odpočty** kliknite na **CSV import**, vyberte súbor
   a kliknite na **Importovať**.
4. Na **Mapovanie stĺpcov CSV** skontrolujte priradenie. Ak váš súbor
   nemá stĺpec s rokom, zadajte ho do **Predvolený rok (voliteľné)**.
   Kliknite na **Importovať**.
5. Prečítajte si zhrnutie na stránke odpočtov: koľko odpočtov bolo
   zaznamenaných a koľko riadkov bolo preskočených a prečo.

Riadky bez odpočtu sa preskočia ako „neplatný riadok“ -- to je pri
meradlách, ktoré ste ešte neodčítali, normálne. Podrobnosti o stĺpcoch
a chybových hláseniach: [Import členov a
parciel](csv-import.md#5-meter-readings).

## 4. Možnosť C: zadajte jednotlivý odpočet s dátumom a poznámkou {#4-option-c-enter-a-single-reading-with-date-and-note}

1. Otvorte **Voda → Meracie body** a kliknite na merací bod.
2. Dole, v **Odpočty**, vyplňte **Rok**, **Dátum**, **Odpočet merača**
   a voliteľne **Poznámka**.
3. Kliknite na **Zaznamenať odpočet**.

Tabuľka **Odpočty** na tej istej stránke uvádza každý rok s odpočtom a
spotrebou. Chybný odpočet sa tam dá zmazať.

## 5. Keď odpočet vyzerá nesprávne {#5-when-a-reading-looks-wrong}

Odpočet nižší ako minuloročný (alebo vyšší ako už zaznamenaný neskorší)
sa **aj tak uloží**, s upozornením ako *„Odpočet uložený, ale
skontrolujte ho, prosím: Odpočet merača (…) je menší ako predchádzajúci
odpočet (…) toho istého merača. Bol skorší odpočet odhadnutý?
Skontrolujte to, prosím.“* Odpočet si ponechá značku upozornenia na
stránke odpočtov aj na meracom bode.

Časté príčiny: preklep, zle prečítaná číslica, skorší odpočet odhadnutý
príliš vysoko alebo meradlo, ktoré bolo naozaj vymenené (krok 6). Opravte
hodnotu tak, že odpočet za ten istý rok zaznamenáte znova.

## 6. Výmena meradla {#a-meter-is-replaced}

Keď sa meradlo fyzicky vymení -- napríklad preto, že mu končí
kalibrácia:

1. Odčítajte staré meradlo naposledy, ak ešte môžete, a zadajte to na
   stránke meracieho bodu ako odpočet roka (možnosť C).
2. Na karte **Aktuálny merač Voda** (pri elektrine **Aktuálny merač
   Elektrina**) otvorte **Vymeniť merač**.
3. Zadajte **Starý merač odstránený dňa**, **Nový merač nainštalovaný
   dňa**, **Nové číslo**, **Kalibrovaný do** (rok) a **Počiatočný
   odpočet** nového meradla (zvyčajne to, čo ukazuje jeho displej pri
   inštalácii).
4. Kliknite na **Vymeniť** a potvrďte.

Staré meradlo sa nezmaže: presunie sa do **Predchádzajúce merače** s
dátumami inštalácie a demontáže a svojím **Posledný odpočet**. Odteraz
idú odpočty na nové meradlo, ktorého spotreba začína od jeho
**Počiatočný odpočet**.

!!! tip "Spotreba v roku výmeny"
    Vo formulári výmeny vyplňte **Konečný stav starého meradla** -- to,
    čo staré meradlo ukazuje v deň demontáže. Spotreba roka potom sčíta
    obe meradlá (staré po výmenu, nové od jeho počiatočného stavu) a
    tento súčet vyúčtuje ročná faktúra. Bez konečného stavu sa časť
    starého meradla od jeho posledného odpočtu nevyúčtuje.

!!! tip "Preklep, nie nové meradlo?"
    Ak ste sa len pomýlili v čísle meradla alebo v počiatočnom stave,
    použite namiesto toho **Upraviť merač**. **Vymeniť merač** je na
    skutočnú výmenu.

## 7. Skontrolujte rok {#7-check-the-year}

1. Otvorte **Voda → Hodnotenie** a vyberte rok.
2. Dlaždice porovnávajú **Hlavný merač** s **Parcely celkom** a
   **Spolok celkom**; tabuľky nižšie uvádzajú každý merací bod s jeho
   **Spotreba**. Body, ktorým ešte chýba odpočet, ukazujú **žiadny
   odpočet**.
3. Ak parcely a prípojky spolku spolu spotrebovali viac ako hlavný
   merač, Parcella ukáže upozornenie. To je normálne, kým sa odpočty
   ešte zadávajú; keď sú všetky zadané, poukazuje to na zle odčítané
   meradlo.
4. **CSV export** stiahne hodnotenie pre vašu evidenciu alebo pre
   dodávateľa.

**Voda → Prehľad** vám povie aj to, koľko meracím bodom ešte chýba
odpočet za rok, s odkazom **Zaznamenať teraz →**.

## 8. Nastavte cenu na vyúčtovanie {#8-set-the-price-for-billing}

Ak vodu a elektrinu účtujete ročnými faktúrami Parcelly:

1. Otvorte **Voda → Konfigurácia**.
2. V **Nová/aktualizovaná cena** zadajte **Rok** a **Cena za m³** a
   voliteľne **Poznámka** (napr. „zmena tarify dodávateľa“).
3. Kliknite na **Uložiť**.

Bez ceny na rok vyúčtovanie za ten rok neúčtuje žiadnu vodu. Potom
pokračujte v časti [Ročné vyúčtovanie](annual-invoicing.md).

## Súvisiace {#related}

- [Voda a elektrina](../modules/metering.md)
- [Import členov a parciel](csv-import.md)
- [Ročné vyúčtovanie](annual-invoicing.md)
- [Odovzdanie parcely](parcel-handover.md)
- Slovník: [merací bod](../glossary.md#metering-point),
  [meradlo](../glossary.md#meter)

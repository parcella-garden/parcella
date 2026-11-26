# Nastavenia spolku {#club-settings}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Stránka nastavení obsahuje kmeňové údaje vášho spolku a prepínače,
ktoré platia pre celú inštaláciu: jazyk, logo, e-mailový server,
finančné údaje a ďalšie.

!!! info "Kto to môže používať"
    Len administrátori. Otvorte **Administrácia → Nastavenia**.

![Nastavenia spolku](../assets/screenshots/administration/settings.png)

## Ako stránka funguje {#how-the-page-works}

Stránka je stĺpec kariet. Každá karta je zbalená; kliknutím na jej
nadpis ju otvoríte. Otvorenie jednej karty zbalí ostatné.

| Prvok | Čo robí |
|---|---|
| **Hľadať v nastaveniach...** | Napíšte slovo, napríklad „logo“ alebo „IBAN“. Karty, ktoré ho obsahujú, sa otvoria a slovo sa zvýrazní; všetky ostatné karty sa skryjú. Ak nič nevyhovuje, uvidíte **Žiadne nastavenia nezodpovedajú vyhľadávaniu.** |
| **Uložiť nastavenia** | Hore a dole na stránke. Uloží **všetky karty naraz**, bez ohľadu na to, ktorú ste zmenili. Uvidíte **Nastavenia uložené.** |

!!! warning "Jedno tlačidlo na uloženie pre všetko"
    Zmeny sa uložia, len keď kliknete na **Uložiť nastavenia**. Ak
    stránku predtým opustíte, stratia sa.

Karty zhora nadol:

## Jazyk {#language}

Jazyk celej inštalácie: menu, tlačidlá, hlásenia, prihlasovacia stránka
a e-maily a PDF, ktoré Parcella vytvára. Všetci vidia rovnaký jazyk;
osobné nastavenie jazyka neexistuje.

Vyberte z možností **Deutsch**, **English**, **Polski**, **Čeština**,
**Slovenčina**, **Français** a **Nederlands**. Nová inštalácia začína v
angličtine.

Kde text ešte nie je preložený do zvoleného jazyka, Parcella namiesto
neho ukáže anglický text.

Jazyk nemení vzhľad čísel, dátumov a peňažných súm -- na to je karta
**Región a mena**.

## Branding {#branding}

| Pole | Čo robí |
|---|---|
| **Logo klubu** | Ukazuje vaše aktuálne logo (alebo ikonu Parcelly). Vyberte nový súbor -- PNG, JPEG, WebP alebo SVG, najviac 2 MB --, ktorý ho nahradí. Logo sa zobrazuje na prihlasovacej stránke, v hornej časti bočného panela a v hlavičke vytvorených PDF. |
| **Odstrániť logo (späť na predvolenú ikonu)** | Zobrazí sa len vtedy, keď je logo nahrané. Zaškrtnite a uložte, aby ste sa vrátili k ikone Parcelly. |

Nesprávny typ súboru alebo príliš veľký súbor sa odmietne s hlásením;
zvyšok stránky sa aj tak uloží.

## Región a mena {#region-currency}

| Pole | Čo robí |
|---|---|
| **Región** | Ako sa píšu čísla a adresy -- oddeľovač tisícov, desatinná čiarka alebo bodka, či PSČ ide pred mesto alebo za neho. Rozhoduje aj o časovom pásme kalendárových kanálov. Možnosti: Nemecko, Spojené kráľovstvo, Francúzsko, Holandsko, Poľsko, Česká republika, Slovensko. Predvolené: Nemecko. |
| **Mena** | Symbol meny a jeho umiestnenie („19,99 €“ alebo „£19.99“). Možnosti: euro (€), britská libra (£), poľský zlotý (zł), česká koruna (Kč). Predvolené: euro. |

Obe sú nezávislé od jazyka: holandsky hovoriaci spolok môže používať
holandské menu so sumami v eurách, anglická inštalácia môže používať
nemecké formáty čísel.

## Funkčné oblasti {#feature-areas}

Prepínače, ktoré zapínajú a vypínajú moduly. Podrobne opísané v časti
[Zapínanie a vypínanie modulov](modules.md).

## Poradie navigácie {#navigation-order}

Určuje poradie položiek v bočnom paneli všetkých používateľov. Každá
položka má číselné pole: **Dashboard**, **Členovia**, **Parcely**,
**Podpora**, **Žiadosti o nákup**, **Pracovné sedenia**, **Voda**,
**Elektrina**, **Poistenie**, **Kalendár**, **Oznamy**, **Inventár**,
**Nástenka úloh**, **Financie**, **Uchádzači**, **Externé kontakty**,
**Prehľady**, **Poznámky**, **Procesy**.

Nižšie čísla idú prvé. Predvolene sú čísla 100, 200, 300 ... v poradí
uvedenom vyššie, takže položku môžete presunúť medzi dve iné tak, že jej
dáte napríklad 150. Prázdne polia sa vrátia na predvolené číslo;
čokoľvek, čo nie je celé číslo, sa ignoruje.

**Administrácia** v zozname nie je: je vždy posledná.

## Aktualizácie {#updates}

| Pole | Čo robí |
|---|---|
| **Automaticky kontrolovať aktualizácie** | Predvolene zapnuté. Parcella sa potom každých pár hodín pýta GitHubu, či vyšla novšia verzia, a zobrazí upozornenie na stránke [Systém](system.md). O vašom spolku sa nič neposiela. Vypnite to, ak váš server nesmie kontaktovať internet; stránka Systém potom neukazuje vôbec žiadne informácie o aktualizáciách. |

## Uchádzači {#applicants}

Relevantné len vtedy, keď používate modul [Uchádzači](../modules/applicants.md).

| Pole | Čo robí |
|---|---|
| **Mazať prihlášky po (mesiacoch)** | Každá prihláška, ktorej stav sa toľko mesiacov nezmenil, sa **natrvalo zmaže**, bez ohľadu na stav a bez upozornenia. Počíta sa od poslednej zmeny stavu alebo od dátumu prihlášky, ak sa stav nikdy nezmenil. Nechajte prázdne alebo zadajte 0, ak chcete prihlášky ponechať, kým ich nezmažete ručne. Užitočné pre ochranu údajov. |
| **Text e-mailu novým žiadateľom** | Text, ktorý používa **Kontaktovať žiadateľa** pri novej prihláške; pred každým odoslaním sa dá ešte zmeniť. `{name}` sa nahradí menom uchádzača, `{club}` názvom spolku. Nechajte prázdne, ak chcete použiť vstavaný text, zobrazený sivo. |

## Protokol e-mailov {#email-log}

| Pole | Čo robí |
|---|---|
| **Uchovávať záznamy protokolu e-mailov (dni)** | Ako dlho [Protokol e-mailov](email-log.md) uchováva svoje záznamy. Staršie sa mažú automaticky, pretože adresy príjemcov sú osobné údaje. Predvolene 90 dní, možné 1 až 3650. |

## Údaje spolku {#club-data}

| Pole | Na čo sa používa |
|---|---|
| **Názov spolku** | Zobrazuje sa v hornej časti bočného panela, na prihlasovacej stránke a na tlačených dokumentoch. Prázdne: „Parcella“. |
| **Ulica**, **PSČ**, **Mesto** | Adresa spolku v päte vytvorených PDF (faktúry, oznamy, zoznamy). |
| **Registračné číslo spolku**, **Obchodný register** | Tlačia sa tiež v päte PDF, pretože spolky registrované v Nemecku ich musia uvádzať. |

## Členovia výboru {#board-members}

Ktorí členovia sú momentálne vo výbore. Ich mená sa tlačia v päte
vytvorených dokumentov.

| Prvok | Čo robí |
|---|---|
| **Členovia výboru** / **Zobraziť zoznam** | Rozbalí zoznam všetkých súčasných členov, každého so zaškrtávacím políčkom. **Skryť zoznam** ho znova zbalí. |
| **Hľadať…** | Zúži zoznam na vyhovujúce mená. **Žiadne výsledky**, ak nevyhovuje žiadne. |
| **Vybrať všetko** / **Zrušiť výber** | Zaškrtne alebo odškrtne všetkých viditeľných členov. |

Člen, ktorý zo spolku odíde, z tlačeného zoznamu automaticky vypadne.

## Rozlohy (m²) {#areas-sqm}

Pozemky spolku, rozdelené tak, ako ich nemecké záhradkárske spolky
zvyčajne vykazujú.

| Pole | Čo robí |
|---|---|
| **Celková rozloha (m²)** | Celý areál spolku. Zadajte ho sami. |
| **Rozloha A (parcely, m²)** | Vypočítaná, nedá sa upraviť: súčet rozlôh všetkých parciel, prenajatých aj ukončených. Zmazané parcely a spoločné plochy sa nepočítajú. To isté číslo ako **Celková rozloha (m²)** na [Dashboarde](../getting-started/dashboard.md). |
| **Rozloha B (spoločná, m²)** | Vypočítaná: celková rozloha mínus rozloha A mínus rozloha C. |
| **Rozloha C (obecná, m²)** | Zadajte ju sami. |

Tieto čísla sa používajú, keď [vyúčtovanie](../modules/finances/invoice-runs.md)
rozdeľuje náklady podľa podielu každej parcely na spoločnej ploche.

## Finančné nastavenia {#finance-settings}

Používa ich modul [Financie](../modules/finances/index.md).

| Pole | Čo robí |
|---|---|
| **Názov banky**, **IBAN**, **BIC**, **Majiteľ účtu** | Tlačia sa v päte každej faktúry, aby členovia vedeli, kam platiť. |
| **Ďalšie číslo faktúry (prepísať)** | Zvyčajne prázdne: čísla jednoducho pokračujú. Zadajte číslo, ak má hneď nasledujúce vyúčtovanie -- v ktoromkoľvek roku -- začať od neho. Parcella kontroluje, či číslo nie je obsadené, až pri dokončení tohto vyúčtovania. Pole sa po použití samo vyprázdni. |
| **Formát čísla faktúry** | Ako vyzerajú čísla faktúr. `{number}` je povinné, `{year}` voliteľné; akýkoľvek iný text sa použije tak, ako je napísaný, napr. `R-{year}-{number}`. Pod poľom vidíte **Aktuálne používaný:** s príkladom; **(predvolený, nič vlastné nie je uložené)** znamená, že platí predvolený `{year}/{number}`. Pole ponúka niekoľko príkladov. |

Formát ovplyvní len faktúry vytvorené odteraz. Už pridelené čísla sa
nikdy nemenia. Neplatný formát sa neuloží; uvidíte **Neplatný formát
čísla faktúry -- musí obsahovať práve raz {number} (voliteľne aj
{year}), žiadne iné zástupné symboly.**

## E-mail (SMTP) {#email-smtp}

Každý e-mail, ktorý Parcella posiela -- pozvánky, upozornenia, oznamy,
faktúry --, odchádza cez tento poštový server. Parcella nečíta žiadnu
schránku.

| Pole | Čo robí |
|---|---|
| **SMTP server** | Adresa poštového servera od vášho poskytovateľa e-mailu. |
| **SMTP port** | Zvyčajne 587 (alebo čo uvádza poskytovateľ). |
| **SMTP používateľ** | Prihlasovacie meno pre poštový server, často e-mailová adresa. |
| **SMTP heslo** | Zobrazuje sa ako **Zatiaľ nenastavené** alebo **•••••••• (nastavené -- znova zadajte pre zmenu)**. Nechajte prázdne, ak chcete ponechať uložené heslo; napíšte nové, ak ho chcete nahradiť. Ukladá sa šifrovane. |
| **E-mail odosielateľa** | Adresa, z ktorej e-maily prichádzajú. |

!!! tip "Overte, že to funguje"
    Po uložení pozvite sami seba na druhú adresu alebo pošlite
    ľubovoľný e-mail a potom sa pozrite do [Protokolu
    e-mailov](email-log.md). **Zlyhalo** s chybou vám povie, čo sa
    poštovému serveru nepáčilo.

Ak sú tieto polia prázdne, Parcella použije nastavenia pošty, ktoré
mohol do konfigurácie servera zadať ten, kto ju inštaloval.

Parcella šifruje spojenie s poštovým serverom pomocou STARTTLS, metódy
bežne používanej na porte 587. Na stránke nastavení na to nie je
prepínač; dá sa to zmeniť len v konfigurácii servera.
<!-- TODO(verify): whether mail servers that only offer implicit TLS on port 465 work at all. -->

## Súvisiace {#related}

- [Zapínanie a vypínanie modulov](modules.md)
- [Integrácie](integrations.md)
- [Založenie nového spolku](../guides/new-club-setup.md)

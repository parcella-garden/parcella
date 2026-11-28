# Oznamy {#announcements}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Správu napíšete raz a pošlete ju až štyrmi kanálmi: e-mailom, ako
koncept príspevku na webe spolku, ako jednostranový oznam na vytlačenie
a vyvesenie v záhrade a ako osobné listy pre obálky s okienkom. Platí to
pre novinky spolku aj pre správy vybraným členom, nájomcom parciel
alebo uchádzačom (uchádzači listy nedostávajú, pretože pri nich nie je
uložená poštová adresa).

!!! info "Kto to môže používať"
    - Prepínač modulu je **Oznamy** v časti **Administrácia →
      Zapínanie a vypínanie modulov**. Predvolene je **vypnutý**,
      pretože môže poslať e-mail každému členovi a ukladá prihlasovacie
      údaje k vášmu webu.
    - **Oznamy** v menu vidia a používať ich môžu len roly **Výbor** a
      **Administrátor** a členovia skupiny s **Plný prístup ku každému
      modulu**. Neexistuje oprávnenie skupiny, ktoré by dalo prístup
      iným používateľom.
    - Kanál webu potrebuje prepojenie s webom v časti **Administrácia →
      Integrácie → Webová stránka (koncepty z oznámení)**. Pozri
      [Integrácie](../administration/integrations.md).

## Tri druhy oznamov {#three-kinds-of-announcement}

| Druh | Ako ho začnete | Kanály |
|---|---|---|
| Novinky spolku | **Nový oznam** v zozname oznamov. | E-mail, koncept na webe, oznam, listy |
| Správa vyfiltrovaným členom | **Napísať týmto členom ({count})** na vyfiltrovanom [zozname členov](members.md) alebo označte členov a kliknite na **Napísať vybratým**. | E-mail, koncept na webe, oznam, listy |
| Oznámenie nájomcom vybraných parciel | Označte parcely v [zozname parciel](parcels.md#picking-parcels) a kliknite na **Napísať nájomcom**. Týka sa nájmu, nie členstva: jedno oznámenie na parcelu, s jej číslom; e-mail len nájomcom, ktorí s tým súhlasia, jeden list na adresu pre ostatných. | E-mail, koncept na webe, oznam, listy |
| Správa vybraným uchádzačom | Označte uchádzačov v [zozname uchádzačov](applicants.md) a kliknite na **Napísať vybraným uchádzačom**. | E-mail, koncept na webe, oznam |

Všetky sa píšu v tom istom formulári a uvádzajú na tej istej stránke.

## Zoznam oznamov {#announcement-list}

![Zoznam oznamov](../assets/screenshots/announcements/list.png)

Otvorte **Oznamy** v menu. Zoznam ukazuje všetky oznamy, najnovšie
navrchu.

| Stĺpec / tlačidlo | Čo ukazuje |
|---|---|
| **Nový oznam** | Otvorí prázdny formulár pre novinky spolku. |
| Obrázok | Obrázok oznamu ako náhľad alebo ikona megafónu, ak žiadny nemá. |
| **Názov** | Názov s odkazom na stránku úprav. Odznak označuje správy **Vybraní členovia** alebo **Uchádzači**. |
| **Kanály** | Jedna ikona na kanál: obálka (e-mail), zemeguľa (web), tlačiareň (oznam) a poštová schránka (listy; nie pre uchádzačov). Zelená znamená **hotovo**, červená **zlyhalo**, modrá **odosiela sa**, sivá **zatiaľ nie**. Podržte myš nad ikonou a prečítate si jej stav. |
| **Vytvorené** | Dátum vytvorenia oznamu. |
| Ceruzka | Otvorí stránku úprav. |

Keď ešte nie sú žiadne oznamy, zoznam hovorí **Zatiaľ žiadne oznamy.**

Celkový stav „koncept / zverejnené“ neexistuje. Čo kam odišlo, sa
sleduje len po kanáloch.

## Písanie oznamu {#writing-an-announcement}

![Nový oznam](../assets/screenshots/announcements/form-new.png)

Formulár je rovnaký pre nové aj existujúce oznamy.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Názov** | Povinné. Používa sa ako predmet e-mailu, názov príspevku a nadpis vytlačeného oznamu. |
| **Zhrnutie** | Voliteľné, obyčajný text, najviac 300 znakov. Zobrazí sa ako náhľadový riadok pod predmetom e-mailu a ako perex na webe. Počítadlo ukazuje, koľko znakov ste použili; nad 160 zoranžovie, čo je asi to, čo ukazujú vyhľadávače. |
| **Obrázok** | Voliteľné. PNG, JPEG alebo WebP, do 5 MB. Používa sa ako obrázok príspevku na webe, zobrazuje sa v e-maile a na vytlačenom ozname. Väčší súbor sa hneď odmietne a **Uložiť** je neaktívne, kým nevyberiete iný. |
| **Odstrániť obrázok** | Zobrazí sa, až keď je obrázok uložený. Zaškrtnite a uložte, aby ste ho odstránili. |
| **Popis obrázka (alternatívny text)** | Voliteľné, najviac 255 znakov. Opíšte, čo je na obrázku, pre ľudí s čítačkou obrazovky a pre vyhľadávače. Ak zostane prázdny, web dostane názov. |
| **Text** | Povinné. Písaný v Markdowne. Rovnaký text sa použije pre koncept na webe aj pre e-mail členom. |
| **Tlačová verzia (voliteľné)** | Len pri ozname, ktorý bol aspoň raz uložený. Pozri [Vytlačený oznam](#the-printed-notice). |
| **QR kód k príspevku na webe** | Na tom istom mieste ako tlačová verzia. Pozri [Vytlačený oznam](#the-printed-notice). |
| **Uložiť** | Uloží vaše zmeny a otvorí stránku úprav. Uloženie iba ukladá vaše zmeny -- nič sa tým neodosiela ani nezverejňuje. |
| **Zrušiť** | Späť do zoznamu bez uloženia. |

Ak chýba názov alebo text, formulár ukáže **Zadajte prosím názov aj
text.** a zachová, čo ste napísali.

### Textový editor {#the-text-editor}

Pole **Text** je editor Markdown s panelom nástrojov: tučné písmo,
kurzíva, preškrtnutie, nadpis, kód, citát, odrážkové a číslované
zoznamy, odkaz, obrázok, tabuľka a vodorovná čiara. Ikona oka prepne na
náhľad, ikona rozdelenia ukáže text a náhľad vedľa seba a šípky otvoria
editor na celú obrazovku. Otáznik otvorí v novej karte krátky návod k
Markdownu.

Tlačidlo obrázka vloží obrázok *podľa jeho webovej adresy*; nenahráva
súbor. Pre hlavný obrázok oznamu použite pole **Obrázok**.

## Stránka úprav {#the-edit-page}

![Úprava oznamu](../assets/screenshots/announcements/form-edit.png)

Po prvom uložení sa ocitnete na stránke úprav. Má formulár zhora a pod
ním ďalšie tri karty.

### Odoslať testovací e-mail {#send-a-test-email}

Odošle aktuálny obsah na jednu adresu na kontrolu. Nikdy sa nepočíta
ako skutočné odoslanie a nikdy nejde členom. Zadajte adresu a kliknite
na **Odoslať test**. Testovací e-mail nesie viditeľnú poznámku, že ide o
test.

Stránka potom ukáže **Testovací e-mail bol úspešne odoslaný** s
adresou alebo **Testovací e-mail sa nepodarilo odoslať -- skontrolujte
konfiguráciu SMTP v Administrácia -> Nastavenia.**

!!! tip
    Najprv uložte. Test používa uložený obsah, nie to, čo je ešte vo
    formulári.

### Distribučné kanály {#delivery-channels}

Každý kanál má riadok so svojím stavom a, keď je čo robiť, jedno
tlačidlo. Každý kanál sa vykoná raz. Po zmene obsahu a uložení možno
príspevok na webe a PDF aktualizovať; e-mail sa odosiela len raz.

| Stav | Význam |
|---|---|
| **Zatiaľ neodoslané** | Na tomto kanáli sa ešte nič nestalo. |
| **Odoslané** / **PDF vytvorené** | Hotovo, s dátumom a časom. |
| **Odosiela sa...** | E-mail práve odchádza. |
| **Zlyhalo** / **Príliš dlhé na jednu stranu** | Posledný pokus nevyšiel. Dôvod je uvedený pod tým a tlačidlo sa znova ponúkne na opakovanie. |
| **Obsah sa odvtedy zmenil.** | Oznam ste upravili potom, čo bol tento kanál hotový. |

#### E-mail členom {#member-email}

**Odoslať teraz** pošle oznam všetkým súčasným členom, ktorí majú
zapnuté e-mailové upozornenia (nastavenie „súhlas s e-mailom“ pri
členovi). Dostanú ho členovia, ktorých členstvo ešte trvá, či už majú
parcelu, alebo nie. Členovia bez e-mailovej adresy sa preskočia.

Najprv potvrdíte: **Odoslať tento oznam e-mailom všetkým aktuálnym
členom s povolenými e-mailovými upozorneniami? Je to možné iba raz.**

- E-maily odchádzajú po malých dávkach s prestávkami, aby sa váš
  poštový server nezahltil. Pri niekoľkých stovkách členov to trvá
  desiatky minút. Stránku môžete opustiť; odosielanie pokračuje.
- Kým beží, riadok ukazuje **Odosiela sa...** a priebežný počet.
  Načítajte stránku znova, aby ste videli aktuálny počet.
- Ak niektoré adresy zlyhajú, kanál napriek tomu ukazuje **Odoslané** s
  uvedeným počtom zlyhaní. Ak sa nepodarilo odoslať ani jeden e-mail,
  ukáže **Zlyhalo** a môžete to skúsiť znova.
- Po odoslaní sa tlačidlo už nikdy nevráti, ani po úprave. Ak potom
  zmeníte text, stránka povie **Obsah bol zmenený po odoslaní e-mailu.
  Členovia dostali skoršiu verziu.**

#### Koncept na webe {#website-draft}

Vedľa **Koncept na webe** vidíte, ktorý web je pripojený:
**WordPress**, **Priečinok Markdown (cloudové úložisko)** alebo
**Plugin Parcella (TYPO3, Contao, Drupal, Joomla, ...)**.

- **Vytvoriť koncept** pošle názov, text, zhrnutie a obrázok na web ako
  nezverejnený koncept. Parcella nikdy nič nezverejňuje; o tom
  rozhodujete vy vo vlastnej administrácii webu.
- Po úspešnom odoslaní **Otvoriť koncept** odkazuje na koncept v
  editore vášho webu (WordPress, pluginy). Pri priečinku Markdown sa
  namiesto toho ukáže cesta k súboru; zverejníte ho odstránením riadku
  `draft: true` zo súboru.
- Keď zmeníte názov, text, zhrnutie alebo obrázok a uložíte, tlačidlo
  sa zmení na **Aktualizovať koncept na webe**. Prepíše ten istý
  príspevok namiesto vytvorenia druhého a zachová jeho stav
  zverejnenia, takže zverejnený príspevok zostane zverejnený. Najprv
  potvrdíte, pretože úpravy textu urobené priamo na webe sa stratia.
- Ak bol príspevok medzitým na webe zmazaný, vytvorí sa nový koncept.
- Bez prepojenia s webom pokus zlyhá s hlásením, že zatiaľ nie je
  nastavený žiadny web -- vyberte ho v Admin -> Integrácie -> Webová
  stránka.

#### Tlačiteľné PDF {#printable-pdf}

**Vytvoriť PDF** vytvorí jednostranový oznam a stiahne ho. Pozri
[Vytlačený oznam](#the-printed-notice). Potom riadok ponúka **Stiahnuť**
pre uložené PDF. **Vytvoriť PDF** sa vráti, keď zmeníte názov, text,
tlačovú verziu, nastavenie QR kódu alebo obrázok, alebo keď bol oznam
skrátený bez QR kódu a príspevok na webe medzitým mohol byť zverejnený.

### Odstrániť oznámenie {#delete-announcement}

Trvalo odstráni toto oznámenie bez ohľadu na to, čo už bolo odoslané.
Najprv potvrdíte: **Naozaj odstrániť toto oznámenie? Túto akciu nemožno
vrátiť späť.** Spolu s ním sa zmaže obrázok a uložené PDF na tlač. Už
odoslané e-maily a už vytvorené príspevky na webe to neovplyvní.

## Vytlačený oznam {#the-printed-notice}

Kanál **Tlačiteľné PDF** vytvorí jednu stranu A4 pre nástenku s
hlavičkou spolku, obrázkom, názvom, riadkom „Zverejnené <dátum>, autor:
<meno>“ (dátum vytvorenia PDF a meno autora) a textom.

| Pole | Čo robí |
|---|---|
| **Tlačová verzia (voliteľné)** | Ponechajte prázdne pre tlač celého textu vyššie. Ak sa nezmestí na jednu stranu, tu bude navrhnutá skrátená verzia -- dá sa upraviť. Pod ním formulár hovorí **Zmestí sa na jednu tlačenú stranu.** alebo **Pravdepodobne príliš dlhé na jednu stranu -- zvážte skrátenie.** Editor je rovnaký ako pri texte, bez tlačidla obrázka. |
| **QR kód k príspevku na webe** | Vytlačí QR kód k príspevku na webe, aj keď sa text zmestí na jednu stranu -- pre tlačový text, ktorý je len upútavkou. Predvolene vypnuté. |

Čo sa stane pri **Vytvoriť PDF**:

1. Parcella vyskúša tlačovú verziu, alebo celý text, ak je prázdna.
2. Ak sa zmestí na jednu stranu, hotovo.
3. Ak nie, odoberá odseky od konca, kým sa nezmestí, a pridá QR kód s
   „Celé oznámenie si prečítajte online:“. Skrátený text sa uloží do
   **Tlačová verzia (voliteľné)**, takže ho môžete skontrolovať a
   upraviť.
4. Ak sa vedľa obrázka a hlavičky nezmestí ani jeden odsek, PDF sa
   nevytvorí. Kanál ukáže **Príliš dlhé na jednu stranu** a tlačovú
   verziu musíte skrátiť sami.

QR kód vedie na krátky odkaz v Parcelle, nie priamo na príspevok. Hneď
ako je príspevok na vašom webe zverejnený, odkaz tam presmeruje. Dovtedy
každý, kto ho naskenuje, uvidí malú stránku s textom **Toto oznámenie
zatiaľ nie je na webe. Skúste to prosím neskôr.** -- bez názvu alebo
akýchkoľvek podrobností. Oznam teda môžete vytlačiť a vyvesiť ešte
predtým, než príspevok pôjde online. Bez prepojenia s webom QR kód
vôbec nie je.

Ak bol skrátený oznam vytlačený, kým bol príspevok ešte koncept, stránka
uvádza **Text bol skrátený bez QR kódu, pretože príspevok na webe ešte
nebol verejný. Keď bude zverejnený, vytvorte PDF znova a QR kód sa
pridá.**

!!! tip "Uloženie PDF do cloudu"
    Pri zapnutom module cloudového úložiska a nastavenom **Priečinok pre
    tlačené oznamy** v časti **Administrácia → Integrácie** sa každé
    vytvorené PDF uloží aj tam, pomenované podľa názvu a dátumu. Druhé
    PDF v ten istý deň nahradí súbor toho dňa. Ak nahratie zlyhá, PDF
    aj tak dostanete na stiahnutie; zlyhanie sa poznamená pri kanáli.

## Správy vyfiltrovaným členom {#messages-to-filtered-members}

![Správa vyfiltrovaným členom](../assets/screenshots/announcements/form-audience.png)

Použite to pre prevádzkové správy časti spolku: „všetci so štítkom
*zodpovedný za vodu*“, „všetci čakajúci členovia“.

1. Na [zozname členov](members.md) zoznam vyfiltrujte (vyhľadávanie,
   štítok, zaškrtávacie políčka). Potom kliknite na **Napísať týmto
   členom ({count})** alebo označte jednotlivých členov a kliknite na
   **Napísať vybratým**.
2. Otvorí sa formulár oznamu s kartou **Správa pre členov: {count}**
   nad ním.

Karta ukazuje:

| Položka | Čo ukazuje |
|---|---|
| **Výber:** | Filter, na ktorom správa stojí, ako odznaky: štítok, hľadaný text, **Zobraziť iba neaktívnych**, **Iba potvrdení aktívni**, **Iba so súhlasom s e-mailom = áno**, „Ručne vybraté: {count}“. |
| **Zobraziť týchto členov** | Otvorí zoznam členov s týmto filtrom. |
| „E-mailom: {count}“ | Členovia, ktorí povoľujú informácie e-mailom (**Môže dostávať informácie e-mailom**) a majú adresu. |
| „Listom: {count}“ | Listy pre ostatných členov s poštovou adresou -- jeden na adresu, takže spolubývajúci členovia majú jeden spoločný. Nasledujú ich mená. |
| „Nedosiahnuteľní: {count} (bez súhlasu alebo e-mailovej adresy, bez poštovej adresy)“ | Zobrazí sa červeno, s odkazmi na členov, aby ste mohli opraviť ich záznamy. |
| **Poslať list aj členom, ktorí dostanú e-mail** | Zaškrtnite, ak chcete poslať list každému členovi s poštovou adresou, nielen tým bez e-mailu. |

Príjemcovia sa pri odoslaní určia znova, podľa filtra zoznamu členov
zobrazeného vyššie. Kto dostane štítok zajtra, bude v zajtrajších
listoch. Ručne vybraní členovia, ktorí filtru už nezodpovedajú,
vypadnú.

!!! note "E-mail len so súhlasom"
    Správa členom ide e-mailom len členom, ktorí povoľujú informácie
    e-mailom. Všetci ostatní s poštovou adresou dostanú list -- aj
    vtedy, keď niekto, s kým bývajú, dostal e-mail, pretože každý člen
    je oslovený osobne. Členovia bez súhlasu so spoločnou adresou
    dostanú **jeden** list s menami všetkých. Ak začnete z
    nefiltrovaného zoznamu členov, vznikne namiesto toho bežná novinka
    spolku.

Kanály sú **E-mail členom** (odosiela sa raz, rovnako ako vyššie, po
potvrdení **Odoslať túto správu teraz e-mailom členom ({count})? Nedá
sa to vrátiť späť.**) a **Listy**:

- **Vytvoriť listy ({count})** vytvorí jedno PDF s listom na každú
  poštovú adresu, rozložené pre obálky s okienkom (DIN 5008 tvar B, so
  značkami na prehnutie), s názvom a textom ako v e-maile. Nepridáva sa
  žiadne oslovenie ani obrázok.
- Listy sa vytvoria po kliknutí a nikdy sa neukladajú, pretože obsahujú
  mená a adresy. Kedykoľvek ich môžete vytvoriť znova.

Koncept na webe a vytlačený oznam sa ponúkajú ako pri novinkách spolku.
Listy pri novinkách spolku idú každému aktívnemu členovi bez súhlasu s
e-mailom, ktorý má poštovú adresu, jeden na adresu (alebo všetkým s
**Poslať list aj členom, ktorí dostanú e-mail**).

## Správy vybraným uchádzačom {#messages-to-selected-applicants}

V [zozname uchádzačov](applicants.md) označte uchádzačov a kliknite na
**Napísať vybraným uchádzačom**. Formulár ukáže kartu **Správa na
{count} adries uchádzačov** s menami uchádzačov (s odkazmi) a
**Zobraziť uchádzačov**.

- Ak viac vybraných prihlášok zdieľa e-mailovú adresu, táto adresa
  dostane správu len raz; karta uvádza, koľko ich bolo zlúčených.
- Iba e-mailom. Výber je pevný: neskôr označení uchádzači sa nepridajú.
- Potrebujete aj prístup k modulu uchádzačov.
- **Odoslať teraz** sa pýta **Odoslať túto správu teraz e-mailom na
  {count} adries uchádzačov? Nedá sa to vrátiť späť.**

## Stránka „zatiaľ nie je online“ {#the-not-online-yet-page}

![Zatiaľ nie je online](../assets/screenshots/announcements/not-online.png)

Toto je verejná stránka, ktorú ľudia vidia, keď naskenujú QR kód z
vytlačeného oznamu predtým, než je príspevok zverejnený, alebo keď je
odkaz neznámy. Ukazuje len logo a názov vášho spolku a vetu **Toto
oznámenie zatiaľ nie je na webe. Skúste to prosím neskôr.**

## Súvisiace {#related}

- [Integrácie](../administration/integrations.md) -- prepojenie webu a
  cloudový priečinok pre vytlačené oznamy.
- [Členovia](members.md) -- nastavenie „súhlas s e-mailom“, štítky a
  začatie správy vyfiltrovaným členom.
- [Uchádzači](applicants.md) -- písanie vybraným uchádzačom.
- [Protokol e-mailov](../administration/email-log.md)
- [Zapínanie a vypínanie modulov](../administration/modules.md)

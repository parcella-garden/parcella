# Žiadosti o nákup {#purchase-requests}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Žiadosti o nákup zaisťujú, že sa peniaze spolku neminú bez súhlasu:
skôr než niekto pre spolok niečo kúpi, podá žiadosť a **dvaja rôzni
členovia výboru** ju musia schváliť. Jeden člen výboru ju môže zastaviť
sám. Všetci zúčastnení môžu o žiadosti diskutovať priamo na jej
stránke.

!!! info "Kto to môže používať"
    - **Vidieť žiadosti a komentovať:** každý, koho skupina udeľuje
      **Čítanie** pre **Žiadosti o nákup** (pozri [Skupiny](../administration/groups.md)).
    - **Vytvárať žiadosti a meniť dodávateľa:** **Zápis** pre **Žiadosti
      o nákup**.
    - **Schvaľovať alebo zamietať:** len členovia výboru a
      administrátori alebo používatelia v skupine s plným prístupom.
      Bežné oprávnenie **Zápis** nestačí.

    Modul sa zapína prepínačom **Žiadosti o nákup** v časti
    [Zapínanie a vypínanie modulov](../administration/modules.md).
    Predvolene je zapnutý.

Položka navigácie **Žiadosti o nákup** ukazuje červený odznak s počtom
otvorených žiadostí -- rovnaké číslo ako dlaždica na dashboarde. Počíta
každú otvorenú žiadosť, vrátane tých, ktoré ste už schválili a ktoré
čakajú na druhé schválenie.

## Princíp schvaľovania dvoma osobami {#the-two-person-approval-principle}

Tieto pravidlá platia vždy, bez ohľadu na to, kto aplikáciu používa:

1. Žiadosť je po vytvorení **Otvorená**.
2. Stane sa **Schválená**, hneď ako na **Schváliť** klikli **dvaja
   rôzni** členovia výboru. Každý člen výboru môže žiadosť schváliť len
   raz.
3. **Žiadateľ ani osoba, ktorá žiadosť zadala,** ju nesmú schváliť. Je
   to dôležité, keď člen výboru zadá žiadosť v mene niekoho iného:
   počíta sa na strane žiadateľa a nemôže sám dať jedno z dvoch
   schválení.
4. **Stačí jedno zamietnutie.** Ktorýkoľvek člen výboru môže otvorenú
   žiadosť zamietnuť s uvedením dôvodu. Aj žiadateľ môže vlastnú
   žiadosť zamietnuť -- napríklad aby ju stiahol.
5. Keď je žiadosť **Schválená** alebo **Zamietnutá**, je to konečné.
   Ďalšie schválenia ani zamietnutia nie sú možné a znova ju otvoriť sa
   nedá.

!!! note
    Schválenia a zamietnutia neposielajú e-maily. Posielajú ich len
    nové komentáre (pozri [Diskusia](#discussion)).

## Prehľad {#overview}

![Prehľad žiadostí o nákup](../assets/screenshots/purchase-requests/list.png)

**Žiadosti o nákup** uvádza žiadosti, najnovšie navrchu.

| Pole / tlačidlo | Čo robí |
|---|---|
| **Nová žiadosť o nákup** | Otvorí [formulár](#new-purchase-request). Zobrazí sa len s oprávnením na zápis. |
| **Otvorené** / **Schválené** / **Zamietnuté** / **Všetky** | Ukáže len žiadosti v danom stave alebo všetky. Keď na stránku prídete, je vybrané **Otvorené**. |
| **Názov** | Čo sa má kúpiť; odkazuje na žiadosť. |
| **Žiadateľ** | Meno žiadateľa. Pri žiadosti zadanej v mene niekoho iného napísané meno (alebo jeho e-mailová adresa, ak meno nebolo zadané). |
| **Odhadované náklady** | Odhadované náklady alebo „–“, ak neboli zadané. |
| **Schválenia** | Pri otvorených žiadostiach koľko z dvoch potrebných schválení existuje, napr. **1 / 2**. „–“ pri uzavretých žiadostiach. |
| **Stav** | **Otvorená**, **Schválená** alebo **Zamietnutá**. |
| Tlačidlo s okom | Otvorí žiadosť. |

## Nová žiadosť o nákup {#new-purchase-request}

![Nová žiadosť o nákup](../assets/screenshots/purchase-requests/form.png)

Kliknite na **Nová žiadosť o nákup** v prehľade.

### Žiadosť o nákup {#purchase-request}

| Pole | Čo robí |
|---|---|
| **Čo sa má kúpiť?** | Názov žiadosti. Povinné. |
| **Odôvodnenie** | Prečo to spolok potrebuje. Povinné. |
| **Odkaz na miesto nákupu** | Voliteľná webová adresa obchodu alebo ponuky. Musí to byť úplná adresa začínajúca `http://` alebo `https://`. |
| **Dodávateľ (kontakt)** | Voliteľný dodávateľ z [Externých kontaktov](external-contacts.md). Firmy sú uvedené s ich ľuďmi pod nimi. Zobrazí sa len vtedy, keď je modul externých kontaktov zapnutý a smiete čítať kontakty. |
| **Odhadované náklady** | Voliteľné. Prijíma čiarku alebo bodku ako desatinný oddeľovač. Nechajte prázdne, ak cena ešte nie je známa. Ak Parcella hodnotu nedokáže prečítať ako číslo, žiadosť sa uloží bez nákladov. |

### Žiadateľ {#requester}

| Pole | Čo robí |
|---|---|
| **Vytvoriť v mene inej osoby (ktorá nemá vlastný účet)** | Zaškrtnite, keď zadávate žiadosť za niekoho iného, napr. za člena, ktorý vás požiadal telefonicky. Zobrazí dve polia nižšie. Ak to necháte nezaškrtnuté, žiadateľ ste vy. |
| **Meno osoby** | Meno žiadateľa. |
| **E-mailová adresa** | E-mailová adresa žiadateľa. Dostane odkaz na potvrdenie údajov (pozri [Potvrdenie žiadateľom](#confirmation-by-the-requester)). |

Kliknite na **Vytvoriť žiadosť o nákup**, aby ste ju uložili, alebo na
**Zrušiť**, aby ste sa vrátili. Po uložení sa otvorí stránka žiadosti.

!!! note "Bez e-mailovej adresy"
    **E-mailovú adresu** môžete nechať prázdnu: žiadosť sa uloží so
    zadaným menom ako žiadateľom, len bez potvrdzujúceho e-mailu. Ak
    políčko zaškrtnete, ale meno aj adresu necháte prázdne, žiadosť sa
    počíta ako *vaša vlastná*. V každom prípade nemôžete schváliť
    žiadosť, ktorú ste sami zadali.

## Stránka žiadosti {#request-page}

![Žiadosť o nákup](../assets/screenshots/purchase-requests/detail.png)

Otvorenie žiadosti ukáže jej údaje, diskusiu a schválenia. **Späť** vás
vráti do prehľadu.

### Údaje {#details}

| Pole | Čo ukazuje |
|---|---|
| **Žiadateľ** | Kto o nákup žiadal. Pri žiadosti zadanej v mene niekoho iného aj jeho e-mailová adresa a odznak: **Čaká na potvrdenie** alebo **Potvrdené žiadateľom**. |
| **Vytvoril** | Kto žiadosť zadal a kedy. |
| **Odôvodnenie** | Uvedený dôvod. |
| **Odkaz** | Odkaz na obchod, ak bol zadaný. Otvorí sa v novej karte. |
| **Dodávateľ (kontakt)** | Prepojený externý kontakt alebo „–“. S oprávnením na zápis môžete vybrať iný kontakt (alebo **— žiadny —**) a kliknúť na **Uložiť** -- v akomkoľvek stave, pretože dodávateľ nie je súčasťou schvaľovania. Kontakt, ktorý bol medzitým zmazaný, sa zobrazí s „(zmazaný)“. |
| **Odhadované náklady** | Zobrazí sa len vtedy, keď boli náklady zadané. |

Pod údajmi uzavretá žiadosť ukazuje pruh:

- **Schválená** -- s dátumom a časom druhého schválenia.
- **Zamietnutá** -- s tým, kto ju zamietol, kedy a s dôvodom.

### Diskusia {#discussion}

Karta **Diskusia ({count})** uvádza všetky komentáre, najstaršie prvé,
s autorom a časom. Komentovať môže každý, kto žiadosť vidí, v každom
stave -- práve pri zamietnutej žiadosti chce niekto často niečo
vysvetliť.

| Pole / tlačidlo | Čo robí |
|---|---|
| Pole komentára | Vaša otázka alebo poznámka, najviac 5 000 znakov. Prázdny komentár sa odmietne. |
| **Komentovať** | Pridá komentár a pošle ho e-mailom. |

Komentáre sa potom nedajú upraviť ani zmazať.

Každý nový komentár sa pošle e-mailom:

- žiadateľovi -- na adresu jeho účtu alebo, pri žiadosti zadanej v mene
  niekoho iného, na tam uvedenú e-mailovú adresu;
- každému aktívnemu používateľovi, ktorý žiadosť predtým komentoval
  alebo schválil.

Autor komentára e-mail nedostane a nikto nedostane ten istý komentár
dvakrát. Používatelia dostanú tlačidlo, ktoré otvorí žiadosť, aby mohli
odpovedať v Parcelle. Žiadateľ bez účtu nemôže odpovedať v Parcelle;
jeho e-mail ho žiada, aby sa ozval výboru.

### Schválenia (…/2) {#approvals-count2}

Uvádza každé schválenie s menom člena výboru a dátumom a časom. **Zatiaľ
žiadne schválenia.**, ak žiadne nie sú.

Kým je žiadosť **Otvorená**, členovia výboru vidia aj:

| Tlačidlo / hlásenie | Čo robí |
|---|---|
| **Schváliť** | Zaznamená vaše schválenie. Druhé schválenie od iného člena výboru nastaví žiadosť na **Schválená**. |
| „Ako žiadateľ nemôžete schváliť vlastnú žiadosť o nákup …“ | Zobrazí sa namiesto **Schváliť**, ak ste žiadateľ alebo ste žiadosť zadali. |
| „Toto ste už schválili.“ | Zobrazí sa namiesto **Schváliť** po vašom schválení. |
| **Zamietnuť** | Otvorí pole pre dôvod zamietnutia. |
| **Natrvalo zamietnuť** | Zamietne žiadosť so zadaným dôvodom (povinné). Žiadosť sa okamžite uzavrie. |

## Potvrdenie žiadateľom {#confirmation-by-the-requester}

Keď vytvoríte žiadosť v mene niekoho iného s e-mailovou adresou,
Parcella mu pošle e-mail „Potvrďte prosím: nákupná požiadavka
„{title}““. Uvádza vás ako osobu, ktorá ju zadala, zopakuje názov a
odôvodnenie a obsahuje tlačidlo **Potvrdiť údaje**.

Potvrdenie je **len informatívne**. Ukazuje výboru, že osoba žiadosť
naozaj myslela tak, ako bola zadaná. Na schválenie *nie je* potrebné:
členovia výboru môžu žiadosť schváliť alebo zamietnuť bez ohľadu na to,
či ju žiadateľ potvrdil. Ak má žiadateľ vlastný účet a žiadosť vytvorí
sám, krok potvrdenia vôbec nie je.

### Potvrdiť žiadosť o nákup {#confirm-purchase-request}

Odkaz v e-maile otvorí stránku, ktorá funguje **bez prihlásenia**.
Ukazuje **Názov**, **Odôvodnenie**, **Odkaz** (ak je) a **Odhadované
náklady** (ak sú) žiadosti s vysvetlením, že žiadosť bola zadaná v mene
tejto osoby.

| Tlačidlo / hlásenie | Čo robí |
|---|---|
| **Potvrdiť údaje** | Zaznamená potvrdenie. Na stránke žiadosti sa odznak zmení z **Čaká na potvrdenie** na **Potvrdené žiadateľom**. |
| „Tieto údaje ste už potvrdili.“ | Zobrazí sa namiesto tlačidla, ak bol odkaz už použitý. Opätovné otvorenie odkazu neuškodí. |

Po potvrdení osoba uvidí stránku **Ďakujeme!**, ktorá hovorí, že jej
potvrdenie žiadosti bolo uložené.
<!-- Screenshots of the confirm and thank-you pages are not generated: the sample data contains no request with a confirmation link. -->

### Odkaz nenájdený {#link-not-found}

![Odkaz nenájdený](../assets/screenshots/purchase-requests/confirmation-invalid.png)

Stránka **Odkaz nenájdený** sa zobrazí, keď je odkaz nesprávny alebo
neúplný, alebo keď bola žiadosť vytvorená **pred viac ako 30 dňami**
-- potvrdzovacie odkazy po 30 dňoch prestanú fungovať. Žiadateľ by sa
potom mal obrátiť priamo na výbor; výbor môže o žiadosti aj tak
rozhodnúť.

!!! note
    Text stránky hovorí, že odkaz „je neplatný alebo už bol použitý“.
    Už použitý odkaz počas 30 dní stále funguje -- ukáže „Tieto údaje
    ste už potvrdili.“

## Súvisiace {#related}

- [Externé kontakty](external-contacts.md) -- dodávatelia, ktorých
  môžete prepojiť so žiadosťou; stránka kontaktu uvádza jeho žiadosti o
  nákup
- [Prijaté faktúry](finances/incoming-invoices.md) -- zaznamenanie
  faktúry po uskutočnení schváleného nákupu
- [Dashboard](../getting-started/dashboard.md) -- dlaždica otvorených
  žiadostí o nákup
- [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md)

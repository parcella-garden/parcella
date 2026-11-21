# Žádosti o nákup {#purchase-requests}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Žádosti o nákup zajišťují, že se žádné peníze spolku neutratí bez
souhlasu: než kdokoli pro spolek něco koupí, podá žádost a **dva různí
členové výboru** ji musí schválit. Jediný člen výboru ji může sám
zastavit. Všichni zúčastnění mohou žádost probírat přímo na její
stránce.

!!! info "Kdo to může používat"
    - **Prohlížet žádosti a komentovat:** každý, jehož skupina dává
      **Čtení** pro **Žádosti o nákup** (viz [Skupiny](../administration/groups.md)).
    - **Vytvářet žádosti a měnit dodavatele:** **Zápis** pro **Žádosti o
      nákup**.
    - **Schvalovat nebo zamítat:** jen členové výboru a administrátoři,
      nebo uživatelé ve skupině s plným přístupem. Běžné oprávnění
      **Zápis** nestačí.

    Modul se zapíná přepínačem **Žádosti o nákup** v části
    [Zapínání a vypínání modulů](../administration/modules.md). Ve
    výchozím stavu je zapnutý.

Položka navigace **Žádosti o nákup** ukazuje červený odznak s počtem
otevřených žádostí -- stejné číslo jako dlaždice na dashboardu. Počítá
každou otevřenou žádost, včetně těch, které jste už schválili a které
čekají na druhé schválení.

## Princip schvalování dvěma osobami {#the-two-person-approval-principle}

Tato pravidla platí vždy, ať aplikaci používá kdokoli:

1. Žádost je po vytvoření **Otevřená**.
2. Stane se **Schválená**, jakmile na **Schválit** kliknou **dva různí**
   členové výboru. Každý člen výboru může žádost schválit jen jednou.
3. **Ani žadatel, ani osoba, která žádost zadala,** ji nesmí schválit.
   To je důležité, když člen výboru zadá žádost za někoho jiného:
   počítá se na stranu žadatele a nemůže sám dát jedno ze dvou
   schválení.
4. **Stačí jedno zamítnutí.** Kterýkoli člen výboru může otevřenou
   žádost zamítnout s uvedením důvodu. Svou vlastní žádost může zamítnout
   i žadatel -- například aby ji stáhl.
5. Jakmile je žádost **Schválená** nebo **Zamítnutá**, je to konečné.
   Další schválení ani zamítnutí už nejsou možná a žádost nelze znovu
   otevřít.

!!! note "Poznámka"
    Schválení a zamítnutí neposílají e-maily. Posílají je jen nové
    komentáře (viz [Diskuse](#discussion)).

## Přehled {#overview}

![Přehled žádostí o nákup](../assets/screenshots/purchase-requests/list.png)

**Žádosti o nákup** vypisuje žádosti, nejnovější první.

| Pole / tlačítko | Co dělá |
|---|---|
| **Nová žádost o nákup** | Otevře [formulář](#new-purchase-request). Zobrazí se jen s oprávněním k zápisu. |
| **Otevřené** / **Schválené** / **Zamítnuté** / **Vše** | Ukáže jen žádosti v daném stavu, nebo všechny. Při příchodu na stránku je vybráno **Otevřené**. |
| **Název** | Co se má koupit; odkazuje na žádost. |
| **Žadatel** | Jméno žadatele. U žádosti zadané za někoho jiného zadané jméno (nebo jeho e-mailová adresa, pokud jméno nebylo uvedeno). |
| **Odhadované náklady** | Odhadované náklady, nebo „–“, pokud nebyly zadány. |
| **Schválení** | U otevřených žádostí, kolik ze dvou požadovaných schválení existuje, např. **1 / 2**. „–“ u uzavřených žádostí. |
| **Stav** | **Otevřená**, **Schválená** nebo **Zamítnutá**. |
| Tlačítko s okem | Otevře žádost. |

## Nová žádost o nákup {#new-purchase-request}

![Nová žádost o nákup](../assets/screenshots/purchase-requests/form.png)

Klikněte na **Nová žádost o nákup** v přehledu.

### Žádost o nákup {#purchase-request}

| Pole | Co dělá |
|---|---|
| **Co se má koupit?** | Název žádosti. Povinné. |
| **Odůvodnění** | Proč to spolek potřebuje. Povinné. |
| **Odkaz na místo nákupu** | Volitelná webová adresa obchodu nebo nabídky. Musí to být úplná adresa začínající `http://` nebo `https://`. |
| **Dodavatel (kontakt)** | Volitelný dodavatel z [Externí kontakty](external-contacts.md). Firmy jsou uvedeny s lidmi pod nimi. Zobrazí se, jen pokud je zapnutý modul externích kontaktů a smíte číst kontakty. |
| **Odhadované náklady** | Volitelné. Přijímá čárku nebo tečku jako desetinný oddělovač. Pokud cena ještě není známá, nechte prázdné. Pokud Parcella hodnotu nedokáže přečíst jako číslo, žádost se uloží bez nákladů. |

### Žadatel {#requester}

| Pole | Co dělá |
|---|---|
| **Vytvořit jménem jiné osoby (která nemá vlastní účet)** | Zaškrtněte, když zadáváte žádost za někoho jiného, např. za člena, který vás požádal telefonicky. Zobrazí dvě pole níže. Pokud to necháte nezaškrtnuté, žadatelem jste vy. |
| **Jméno osoby** | Jméno žadatele. |
| **E-mailová adresa** | E-mailová adresa žadatele. Dostane odkaz k potvrzení údajů (viz [Potvrzení žadatelem](#confirmation-by-the-requester)). |

Uložíte kliknutím na **Vytvořit žádost o nákup**, zpět se vrátíte
tlačítkem **Zrušit**. Po uložení se otevře stránka žádosti.

!!! note "Bez e-mailové adresy"
    **E-mailová adresa** můžete nechat prázdnou: žádost se uloží se
    zadaným jménem jako žadatelem, jen bez potvrzovacího e-mailu. Pokud
    políčko zaškrtnete, ale jméno i adresu necháte prázdné, žádost se
    počítá jako *vaše vlastní*. V obou případech nemůžete schválit
    žádost, kterou jste sami zadali.

## Stránka žádosti {#request-page}

![Žádost o nákup](../assets/screenshots/purchase-requests/detail.png)

Otevření žádosti ukáže její údaje, diskusi a schválení. **Zpět** vás
vrátí na přehled.

### Údaje {#details}

| Pole | Co ukazuje |
|---|---|
| **Žadatel** | Kdo o nákup žádal. U žádosti zadané za někoho jiného také jeho e-mailová adresa a odznak: **Čeká na potvrzení** nebo **Potvrzeno žadatelem**. |
| **Vytvořil** | Kdo žádost zadal a kdy. |
| **Odůvodnění** | Uvedený důvod. |
| **Odkaz** | Odkaz na obchod, pokud byl zadán. Otevře se v nové záložce. |
| **Dodavatel (kontakt)** | Propojený externí kontakt, nebo „–“. S oprávněním k zápisu můžete vybrat jiný kontakt (nebo **— žádný —**) a kliknout na **Uložit** -- v jakémkoli stavu, protože dodavatel není součástí schvalování. Kontakt, který byl mezitím smazán, se zobrazí s „(smazán)“. |
| **Odhadované náklady** | Zobrazí se, jen pokud byly zadány náklady. |

Pod údaji ukazuje uzavřená žádost pruh:

- **Schválená** -- s datem a časem druhého schválení.
- **Zamítnutá** -- s tím, kdo ji zamítl, kdy a z jakého důvodu.

### Diskuse {#discussion}

Karta **Diskuse ({count})** vypisuje všechny komentáře, nejstarší
první, s autorem a časem. Komentovat může každý, kdo žádost vidí, v
jakémkoli stavu -- u zamítnuté žádosti chce často někdo něco vysvětlit.

| Pole / tlačítko | Co dělá |
|---|---|
| Pole komentáře | Vaše otázka nebo poznámka, nejvýše 5 000 znaků. Prázdný komentář se odmítne. |
| **Komentovat** | Přidá komentář a pošle ho e-mailem. |

Komentáře nelze dodatečně upravit ani smazat.

Každý nový komentář se pošle e-mailem:

- žadateli -- na adresu jeho účtu, nebo u žádosti zadané za někoho
  jiného na tam uvedenou e-mailovou adresu;
- každému aktivnímu uživateli, který žádost dříve komentoval nebo
  schválil.

Autor komentáře e-mail nedostane a nikdo nedostane stejný komentář
dvakrát. Uživatelé dostanou tlačítko, které otevře žádost, aby mohli
odpovědět v Parcelle. Žadatel bez účtu v Parcelle odpovědět nemůže;
jeho e-mail ho žádá, aby se obrátil na výbor.

### Schválení (…/2) {#approvals-count2}

Uvádí každé schválení se jménem člena výboru a datem a časem. Pokud
žádné není, zobrazí se **Zatím žádná schválení.**

Dokud je žádost **Otevřená**, vidí členové výboru také:

| Tlačítko / zpráva | Co dělá |
|---|---|
| **Schválit** | Zaznamená vaše schválení. Druhé schválení od jiného člena výboru nastaví žádost na **Schválená**. |
| „Jako žadatel nemůžete schválit vlastní žádost o nákup …“ | Zobrazí se místo **Schválit**, pokud jste žadatel nebo jste žádost zadali. |
| „Toto jste již schválili.“ | Zobrazí se místo **Schválit** poté, co jste schválili. |
| **Zamítnout** | Otevře pole pro důvod zamítnutí. |
| **Trvale zamítnout** | Zamítne žádost se zadaným důvodem (povinný). Žádost se okamžitě uzavře. |

## Potvrzení žadatelem {#confirmation-by-the-requester}

Když vytvoříte žádost za někoho jiného s e-mailovou adresou, Parcella
mu pošle e-mail „Potvrďte prosím: požadavek na nákup „{title}““. Uvádí
vás jako osobu, která ji zadala, opakuje název a odůvodnění a obsahuje
tlačítko **Potvrdit údaje**.

Potvrzení je **jen pro informaci**. Ukazuje výboru, že osoba žádost
opravdu myslela tak, jak byla zadána. Ke schválení *není* potřeba:
členové výboru mohou schvalovat nebo zamítat bez ohledu na to, zda
žadatel potvrdil. Pokud má žadatel vlastní účet a žádost vytvoří sám,
krok potvrzení vůbec není.

### Potvrzení žádosti o nákup {#confirm-purchase-request}

Odkaz v e-mailu otevře stránku, která funguje **bez přihlášení**.
Ukazuje **Název**, **Odůvodnění**, **Odkaz** (pokud je) a **Odhadované
náklady** (pokud jsou) žádosti s vysvětlením, že žádost byla zadána
jménem této osoby.

| Tlačítko / zpráva | Co dělá |
|---|---|
| **Potvrdit údaje** | Zaznamená potvrzení. Na stránce žádosti se odznak změní z **Čeká na potvrzení** na **Potvrzeno žadatelem**. |
| „Tyto údaje jste již potvrdili.“ | Zobrazí se místo tlačítka, pokud byl odkaz již použit. Opětovné otevření odkazu nic nepokazí. |

Po potvrzení osoba uvidí stránku **Děkujeme!**, která uvádí, že její
potvrzení žádosti bylo uloženo.
<!-- Screenshots of the confirm and thank-you pages are not generated: the sample data contains no request with a confirmation link. -->

### Odkaz nenalezen {#link-not-found}

![Odkaz nenalezen](../assets/screenshots/purchase-requests/confirmation-invalid.png)

Stránka **Odkaz nenalezen** se zobrazí, když je odkaz chybný nebo
neúplný, nebo když byla žádost vytvořena **před více než 30 dny** --
potvrzovací odkazy po 30 dnech přestanou fungovat. Žadatel by se pak
měl obrátit přímo na výbor; výbor může o žádosti rozhodnout i tak.

!!! note "Poznámka"
    Text stránky uvádí, že odkaz „je neplatný nebo již byl použit“.
    Již použitý odkaz během 30 dnů stále funguje -- ukáže „Tyto údaje
    jste již potvrdili.“

## Související {#related}

- [Externí kontakty](external-contacts.md) -- dodavatelé, které můžete k
  žádosti propojit; stránka kontaktu vypisuje jeho žádosti o nákup
- [Přijaté faktury](finances/incoming-invoices.md) -- evidence faktury
  po uskutečnění schváleného nákupu
- [Dashboard](../getting-started/dashboard.md) -- dlaždice otevřených
  žádostí o nákup
- [Role, skupiny a oprávnění](../getting-started/roles-and-permissions.md)

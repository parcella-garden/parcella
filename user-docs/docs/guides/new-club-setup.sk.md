# Založenie nového spolku {#setting-up-a-new-club}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Parcella je nainštalovaná a beží. Tento návod vás prevedie od úplne
prvého prihlásenia k inštalácii, s ktorou môže pracovať celý výbor:
bezpečné heslo administrátora, údaje a logo vášho spolku, správny
jazyk, len moduly, ktoré potrebujete, účty pre ostatných členov výboru
a -- ak chcete -- najprv kolo skúšania s ukážkovými dátami.

Počítajte asi s hodinou. Potrebujete administrátorský účet, ktorý
vznikol pri inštalácii.

!!! info "Kto to môže robiť"
    Všetko sa tu deje v **Administrácia**, ktorú môžu otvoriť len
    administrátori (a skupiny s **Prístup k administračnému panelu**).
    Pozri [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md).

## 1. Prihláste sa a zmeňte heslo administrátora {#1-log-in-and-change-the-admin-password}

1. Otvorte Parcellu v prehliadači a prihláste sa administrátorským
   účtom z inštalácie.
   <!-- TODO(verify): the default login (admin@parcella.local / admin1234) is documented for developers; confirm whether self-hosters get the same default or set their own during installation before naming it here. -->
2. Ak účet stále používa predvolené heslo z nastavenia, Parcella hneď
   otvorí **Zmeniť heslo** a ukáže: *„Tento účet stále používa
   predvolené heslo z prvotného nastavenia. Zvoľte prosím nové --
   dovtedy zostáva zvyšok aplikácie uzamknutý.“*
3. Zadajte **Aktuálne heslo**, potom **Nové heslo** a **Potvrďte nové
   heslo** a kliknite na **Zmeniť heslo**.

Heslo môžete kedykoľvek znova zmeniť v používateľskom menu v dolnej
časti bočného panela: **Zmeniť heslo**.

!!! warning
    Nevynechávajte to pri inštalácii dostupnej z internetu. Ktokoľvek,
    kto pozná predvolené heslo, by sa inak mohol prihlásiť ako
    administrátor.

Viac: [Prvé prihlásenie a váš účet](../getting-started/first-login.md).

## 2. Zadajte údaje svojho spolku {#2-enter-your-clubs-details}

1. V bočnom paneli otvorte **Administrácia → Nastavenia**. Stránka sa
   volá **Nastavenia spolku**.
2. Na karte **Údaje spolku** vyplňte **Názov spolku**, **Ulica**,
   **PSČ**, **Mesto**, **Registračné číslo spolku** a **Obchodný
   register**. Názov sa zobrazuje v nadpisoch stránok; zvyšok ide do
   päty listov a faktúr.
3. V **Členovia výboru** vyhľadajte a zaškrtnite členov, ktorí sú
   momentálne vo výbore. Vybrať môžete len ľudí, ktorí už existujú ako
   členovia -- vráťte sa k tomu po kroku 9 alebo po
   [importe](csv-import.md).
4. V **Rozlohy (m²)** zadajte **Celková rozloha (m²)** areálu a
   **Rozloha C (obecná, m²)**, ak ju máte. **Rozloha A (parcely, m²)**
   a **Rozloha B (spoločná, m²)** vypočíta Parcella z vašich parciel.
5. Kliknite na **Uložiť nastavenia**. Uvidíte *„Nastavenia uložené.“*

!!! tip
    Stránka nastavení je dlhá. Použite pole **Hľadať v nastaveniach...**
    hore, aby ste skočili na pole podľa názvu.

## 3. Pridajte logo {#3-add-your-logo}

1. Stále v **Administrácia → Nastavenia** nájdite kartu **Branding**.
2. V **Logo klubu** vyberte súbor PNG, JPEG, WebP alebo SVG s veľkosťou
   najviac 2 MB.
3. Kliknite na **Uložiť nastavenia**.

Logo nahradí logo Parcelly na prihlasovacej stránke a v bočnom paneli.
Ak sa chcete vrátiť k predvolenému, zaškrtnite **Odstrániť logo (späť na
predvolenú ikonu)** a uložte.

## 4. Vyberte jazyk, región a menu {#4-choose-language-region-and-currency}

Sú to zámerne tri samostatné nastavenia: spolok môže napríklad
používať anglické rozhranie, ale nemecké formáty čísel a adries.

1. **Jazyk** -- jazyk celej inštalácie. Každý používateľ vidí ten istý.
2. **Región** -- formát čísel a adries (oddeľovač tisícov, poradie PSČ a
   mesta).
3. **Mena** -- symbol a jeho umiestnenie („19,99 €“ alebo „£19.99“).
4. Kliknite na **Uložiť nastavenia**.

## 5. Nastavte odchádzajúci e-mail {#5-set-up-outgoing-email}

Parcella posiela e-mailom pozvánky, upozornenia, oznamy a faktúry. Bez
poštového servera sa pozvánky v kroku 9 nedajú odoslať.

1. V **Administrácia → Nastavenia** nájdite kartu **E-mail (SMTP)**.
2. Vyplňte **SMTP server**, **SMTP port**, **SMTP používateľ**, **SMTP
   heslo** a **E-mail odosielateľa** -- tieto hodnoty vám povie váš
   poskytovateľ pošty.
3. Kliknite na **Uložiť nastavenia**.

Po uložení pole hesla ukazuje len to, že heslo je nastavené; ak ho
chcete zmeniť, napíšte nové.

## 6. Zapnite a vypnite moduly {#6-turn-modules-on-and-off}

Nie každý spolok používa každú funkčnú oblasť. Vypnutie modulu ho skryje
z navigácie; jeho dáta zostanú a vrátia sa, keď ho znova zapnete.

1. V **Administrácia → Nastavenia** nájdite kartu **Funkčné oblasti**.
2. Zaškrtnite moduly, ktoré váš spolok používa, a ostatné odškrtnite.
   Každý má pod sebou krátky popis.
3. Kliknite na **Uložiť nastavenia**.

Niekoľko modulov je v novej inštalácii **vypnutých**, pretože posielajú
dáta von alebo niečo otvárajú verejnosti: **Financie**, **Oznamy**,
**Cloudové úložisko**, **Podpora (helpdesk)**, **Synchronizácia
Nextcloud Deck**, **Konektor MCP pre klientov AI** a tri verejné API
pre web. Zapnite ich, až keď ich budete potrebovať.

Viac: [Zapínanie a vypínanie modulov](../administration/modules.md).

## 7. Vyskúšajte si to s ukážkovými dátami (voliteľné) {#7-try-things-out-with-sample-data-optional}

Skôr než zadáte skutočné dáta, môžete prázdnu inštaláciu naplniť
vymyslenými členmi, parcelami, meradlami, pracovnými zmenami a ďalším,
preklikať sa a všetko to znova odstrániť.

1. Otvorte **Administrácia → Ukážkové dáta**.
2. Prečítajte si **Čo sa pridá**, potom kliknite na **Pridať ukážkové
   dáta** a potvrďte.
3. Preskúmajte moduly. Vyskúšajte vyúčtovanie, zaznamenajte odpočet
   meradla, odovzdajte parcelu.
4. Keď skončíte, vráťte sa do **Administrácia → Ukážkové dáta** a
   kliknite na **Odstrániť všetky ukážkové dáta**, potom potvrďte.

!!! warning "Odstráňte ukážkové dáta skôr, než začnete naostro"
    - Ukážkové dáta sa dajú **pridať** len do novej inštalácie. Hneď ako
      existuje jeden skutočný člen alebo parcela, tlačidlo je
      zablokované.
    - **Odstrániť všetky ukážkové dáta** zmaže presne to, čo vytvoril
      generátor, a nič, čo ste zadali sami. Čokoľvek, čo počas skúšania
      pripojíte *k* ukážkovému záznamu (odpočet na ukážkovom meradle,
      platba na ukážkovej faktúre), sa nemusí čisto odstrániť. Najprv
      odstráňte ukážkové dáta, potom zadajte skutočné.
      <!-- TODO(verify): what happens on removal if a real record references a sample record (e.g. a finalized invoice run built from sample parcels)? -->
    - Ukážkové dáta nevytvárajú ani nemenia používateľské účty.

Viac: [Ukážkové dáta](../administration/sample-data.md).

## 8. Vytvorte skupiny {#8-create-groups}

Nové používateľské účty dostávajú prístup zo **skupín**, nie z pevnej
roly. Najprv vytvorte skupiny, potom do nich pozvite ľudí.

1. Otvorte **Administrácia → Skupiny**.
2. V **Vytvoriť skupinu** zadajte **Názov** (napríklad „Výbor“) a
   **Popis**.
3. Pre výbor zaškrtnite **Plný prístup ku každému modulu**. **Prístup k
   administračnému panelu** zaškrtnite len pre ľudí, ktorí majú
   spravovať aj používateľov a nastavenia.
4. Kliknite na **Vytvoriť skupinu**.
5. Pre užšie úlohy vytvorte ďalšie skupiny a v tabuľke oprávnení
   zaškrtnite **Čítanie**, **Zápis** a **Mazanie** pre každý **Modul**
   -- napríklad „Tím vody“ s čítaním a zápisom pre **Voda** alebo
   „Pokladník“ s plnými právami pre **Financie**. Kliknite na
   **Uložiť**.

!!! tip
    Každý, kto sa môže prihlásiť, si vždy môže *pozrieť* členov a
    parcely. Skupiny prístup od toho rozširujú; nikdy ho neodoberajú.

Viac: [Skupiny](../administration/groups.md) a
[Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md).

## 9. Pozvite ostatných členov výboru {#9-invite-the-other-board-members}

1. Otvorte **Administrácia → Používatelia** (stránka sa volá **Správa
   používateľov**).
2. V **Pozvať používateľa** zadajte **E-mailová adresa** osoby a
   zaškrtnite jej **Skupiny**.
3. Kliknite na **Odoslať pozvánku**.
4. Osoba dostane e-mail s odkazom. Na **Nastavte si svoj účet** zadá
   svoje **Meno** a **Heslo** (aspoň 8 znakov) a klikne na **Vytvoriť
   účet**.

Pozvánka platí 7 dní a zobrazuje sa v **Čakajúce pozvánky**, kým nie je
prijatá. Odtiaľ ju môžete **Znovu odoslať pozvánku** (čím ju aj
predĺžite) alebo **Vymazať pozvánku**.

!!! warning
    Pozvánka odchádza e-mailom, preto najprv nastavte **E-mail (SMTP)**
    (krok 5). Ak sa nedá odoslať, stránka to povie; opravte nastavenia
    pošty a použite **Znovu odoslať pozvánku**.

Viac: [Používatelia a pozvánky](../administration/users.md).

## 10. Pripojte cloudové úložisko (voliteľné) {#10-connect-cloud-storage-optional}

Ak váš spolok uchováva nájomné zmluvy a iné dokumenty v Nextcloude
(alebo v inom podporovanom úložisku), Parcella môže na stránke každej
parcely ukazovať priečinok dokumentov.

1. Otvorte **Administrácia → Integrácie** a nájdite **Cloudové úložisko
   (dokumenty parciel, faktúry, zálohy)**.
2. Vyberte **Typ úložiska** a zadajte údaje pripojenia, ktoré žiada.
   Kliknite na **Uložiť**, potom na **Otestovať pripojenie**.
3. Voliteľne nastavte nižšie zdieľané priečinky: **Priečinok pre
   prijaté faktúry**, **Priečinok pre dokumenty externých kontaktov**,
   **Priečinok poznámok**, **Priečinok pre súbory procesov**,
   **Priečinok pre tlačené oznamy**.
4. Prejdite do **Administrácia → Nastavenia → Funkčné oblasti**,
   zaškrtnite **Cloudové úložisko** a kliknite na **Uložiť nastavenia**.
5. Na stránke každej parcely nastavte **Cesta k priečinku** v
   **Dokumenty (cloudové úložisko)** -- napíšte ju alebo použite
   **Prehľadávať…** -- a kliknite na **Uložiť**.

Cesty sú vždy relatívne k zvolenému úložisku. Parcella priečinky za vás
nevytvára ani nezdieľa; urobte to najprv vo svojom cloude.

Viac: [Integrácie](../administration/integrations.md).

## 11. Zadajte alebo importujte skutočné dáta {#11-enter-or-import-your-real-data}

Teraz pridajte svoje parcely a členov -- ručne v **Parcely → Nová
parcela** a **Členovia → Nový člen** alebo naraz z tabuľky: pozri
[Import členov a parciel](csv-import.md). Potom každého člena priraďte k
jeho parcele (pozri [Prijatie nového člena](new-member.md), krok 7).

## 12. Urobte prvú zálohu {#12-make-your-first-backup}

1. Otvorte **Administrácia → Systém** a nájdite kartu **Záloha**.
2. Kliknite na **Stiahnuť zálohu** a súbor zip uložte na bezpečné
   miesto.

Záloha obsahuje databázu, nahrané súbory a šifrovací kľúč. Zaobchádzajte
s ňou ako so samotným zoznamom členov.

Viac: [Zálohovanie a obnova](../administration/backup.md).

## Súvisiace {#related}

- [Nastavenia spolku](../administration/settings.md)
- [Zapínanie a vypínanie modulov](../administration/modules.md)
- [Používatelia a pozvánky](../administration/users.md)
- [Skupiny](../administration/groups.md)
- [Integrácie](../administration/integrations.md)
- [Ukážkové dáta](../administration/sample-data.md)
- [Zálohovanie a obnova](../administration/backup.md)
- [Import členov a parciel](csv-import.md)

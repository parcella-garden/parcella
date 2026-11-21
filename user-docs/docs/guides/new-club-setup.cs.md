# Založení nového spolku {#setting-up-a-new-club}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Parcella je nainstalovaná a běží. Tento návod vás provede od úplně
prvního přihlášení k instalaci, se kterou může pracovat celý výbor:
bezpečné heslo administrátora, údaje a logo vašeho spolku, správný
jazyk, jen moduly, které potřebujete, účty pro ostatní členy výboru a
-- pokud chcete -- nejprve cvičné kolo s ukázkovými daty.

Počítejte zhruba s hodinou. Potřebujete účet administrátora, který byl
součástí instalace.

!!! info "Kdo to může dělat"
    Vše se odehrává v **Administrace**, kterou mohou otevřít jen
    administrátoři (a skupiny s **Přístup k administračnímu panelu**).
    Viz [Role, skupiny a oprávnění](../getting-started/roles-and-permissions.md).

## 1. Přihlaste se a změňte heslo administrátora {#1-log-in-and-change-the-admin-password}

1. Otevřete Parcellu v prohlížeči a přihlaste se účtem administrátora
   z instalace.
   <!-- TODO(verify): the default login (admin@parcella.local / admin1234) is documented for developers; confirm whether self-hosters get the same default or set their own during installation before naming it here. -->
2. Pokud účet stále používá výchozí heslo z instalace, Parcella hned
   otevře **Změnit heslo** a ukáže: *„Tento účet stále používá výchozí
   heslo z prvotního nastavení. Zvolte prosím nové -- do té doby zůstává
   zbytek aplikace uzamčen.“*
3. Zadejte **Aktuální heslo**, potom **Nové heslo** a **Potvrďte nové
   heslo** a klikněte na **Změnit heslo**.

Heslo můžete kdykoli znovu změnit v uživatelském menu dole v postranním
panelu: **Změnit heslo**.

!!! warning "Varování"
    U instalace dostupné z internetu tento krok nevynechávejte. Kdokoli,
    kdo zná výchozí heslo, by se jinak mohl přihlásit jako
    administrátor.

Více: [První přihlášení a váš účet](../getting-started/first-login.md).

## 2. Zadejte údaje svého spolku {#2-enter-your-clubs-details}

1. V postranním panelu otevřete **Administrace → Nastavení**. Stránka se
   jmenuje **Nastavení spolku**.
2. V kartě **Údaje spolku** vyplňte **Název spolku**, **Ulice**,
   **PSČ**, **Město**, **Registrační číslo spolku** a **Obchodní
   rejstřík**. Název se zobrazuje v titulcích stránek; zbytek jde do
   zápatí dopisů a faktur.
3. V **Členové výboru** vyhledejte a zaškrtněte členy, kteří jsou
   momentálně ve výboru. Vybrat lze jen lidi, kteří už existují jako
   členové -- vraťte se k tomu po kroku 9 nebo po
   [importu](csv-import.md).
4. V **Rozlohy (m²)** zadejte **Celková rozloha (m²)** areálu a
   případně **Rozloha C (obecní, m²)**. **Rozloha A (parcely, m²)** a
   **Rozloha B (společná, m²)** vypočítá Parcella z vašich parcel.
5. Klikněte na **Uložit nastavení**. Uvidíte *„Nastavení uložena.“*

!!! tip "Tip"
    Stránka nastavení je dlouhá. Pole podle názvu rychle najdete
    vyhledávacím polem **Hledat v nastavení...** nahoře.

## 3. Přidejte své logo {#3-add-your-logo}

1. Stále na stránce **Administrace → Nastavení** najděte kartu
   **Branding**.
2. V **Logo spolku** vyberte soubor PNG, JPEG, WebP nebo SVG o velikosti
   nejvýše 2 MB.
3. Klikněte na **Uložit nastavení**.

Logo nahradí logo Parcelly na přihlašovací stránce a v postranním
panelu. Chcete-li se vrátit k výchozímu, zaškrtněte **Odstranit logo
(zpět na výchozí ikonu)** a uložte.

## 4. Vyberte jazyk, region a měnu {#4-choose-language-region-and-currency}

Jde záměrně o tři samostatná nastavení: spolek může například používat
anglické rozhraní, ale německé formáty čísel a adres.

1. **Jazyk** -- jazyk celé instalace. Všichni uživatelé vidí stejný.
2. **Region** -- formát čísel a adres (oddělovač tisíců, pořadí PSČ a
   města).
3. **Měna** -- symbol a jeho umístění („19,99 €“ nebo „£19.99“).
4. Klikněte na **Uložit nastavení**.

## 5. Nastavte odchozí e-mail {#5-set-up-outgoing-email}

Parcella posílá pozvánky, upozornění, oznámení a faktury e-mailem. Bez
poštovního serveru nelze odeslat pozvánky v kroku 9.

1. Na stránce **Administrace → Nastavení** najděte kartu **E-mail
   (SMTP)**.
2. Vyplňte **SMTP server**, **SMTP port**, **SMTP uživatel**, **SMTP
   heslo** a **E-mail odesílatele** -- tyto hodnoty vám sdělí váš
   poskytovatel e-mailu.
3. Klikněte na **Uložit nastavení**.

Po uložení pole hesla jen ukazuje, že heslo je nastaveno; chcete-li ho
změnit, zadejte nové.

## 6. Zapněte a vypněte moduly {#6-turn-modules-on-and-off}

Ne každý spolek používá všechny funkční oblasti. Vypnutím se oblast
skryje z navigace; její data zůstanou a vrátí se, když ji znovu
zapnete.

1. Na stránce **Administrace → Nastavení** najděte kartu **Funkční
   oblasti**.
2. Zaškrtněte moduly, které váš spolek používá, a ostatní odškrtněte.
   Každý má pod sebou krátký popis.
3. Klikněte na **Uložit nastavení**.

Několik modulů je v nové instalaci **vypnutých**, protože odesílají data
ven nebo něco otevírají veřejnosti: **Finance**, **Oznámení**,
**Cloudové úložiště**, **Podpora (helpdesk)**, **Synchronizace Nextcloud
Deck**, **Konektor MCP pro klienty AI** a tři veřejná API pro web.
Zapněte je, až je budete potřebovat.

Více: [Zapínání a vypínání modulů](../administration/modules.md).

## 7. Vyzkoušejte si to s ukázkovými daty (volitelné) {#7-try-things-out-with-sample-data-optional}

Než zadáte skutečná data, můžete prázdnou instalaci naplnit smyšlenými
členy, parcelami, měřidly, pracovními směnami a dalším, proklikat se a
zase vše odstranit.

1. Otevřete **Administrace → Ukázková data**.
2. Přečtěte si **Co se přidá**, pak klikněte na **Přidat ukázková data**
   a potvrďte.
3. Prozkoumejte moduly. Vyzkoušejte vyúčtování, zadejte odečet měřidla,
   předejte parcelu.
4. Až skončíte, vraťte se do **Administrace → Ukázková data**, klikněte
   na **Odstranit veškerá ukázková data** a potvrďte.

!!! warning "Než začnete naostro, odstraňte ukázková data"
    - Ukázková data lze **přidat** jen do nové instalace. Jakmile
      existuje jeden skutečný člen nebo parcela, je tlačítko blokované.
    - **Odstranit veškerá ukázková data** smaže přesně to, co generátor
      vytvořil, a nic, co jste zadali sami. Cokoli, co při cvičení
      připojíte *k* ukázkovému záznamu (odečet na ukázkovém měřidle,
      platbu u ukázkové faktury), se nemusí odstranit čistě. Nejprve
      odstraňte ukázková data, pak zadejte skutečná.
      <!-- TODO(verify): what happens on removal if a real record references a sample record (e.g. a finalized invoice run built from sample parcels)? -->
    - Ukázková data nevytvářejí ani nemění žádné uživatelské účty.

Více: [Ukázková data](../administration/sample-data.md).

## 8. Vytvořte skupiny {#8-create-groups}

Nové uživatelské účty získávají přístup ze **skupin**, ne z pevné role.
Nejprve vytvořte skupiny, pak do nich pozvěte lidi.

1. Otevřete **Administrace → Skupiny**.
2. V části **Vytvořit skupinu** zadejte **Název** (například „Výbor“) a
   **Popis**.
3. Pro výbor zaškrtněte **Plný přístup ke každému modulu**. **Přístup k
   administračnímu panelu** zaškrtněte jen pro lidi, kteří mají také
   spravovat uživatele a nastavení.
4. Klikněte na **Vytvořit skupinu**.
5. Pro užší funkce vytvořte další skupiny a v tabulce oprávnění
   zaškrtněte **Čtení**, **Zápis** a **Mazání** pro každý **Modul** --
   například „Vodní tým“ se čtením a zápisem u **Voda** nebo „Pokladník“
   s plnými právy u **Finance**. Klikněte na **Uložit**.

!!! tip "Tip"
    Každý, kdo se může přihlásit, si vždy může *prohlížet* členy a
    parcely. Skupiny přístup od toho rozšiřují; nikdy ho neodebírají.

Více: [Skupiny](../administration/groups.md) a
[Role, skupiny a oprávnění](../getting-started/roles-and-permissions.md).

## 9. Pozvěte ostatní členy výboru {#9-invite-the-other-board-members}

1. Otevřete **Administrace → Uživatelé** (stránka se jmenuje **Správa
   uživatelů**).
2. V části **Pozvat uživatele** zadejte **E-mailová adresa** osoby a
   zaškrtněte její **Skupiny**.
3. Klikněte na **Odeslat pozvánku**.
4. Osoba dostane e-mail s odkazem. Na stránce **Nastavte si svůj účet**
   zadá své **Jméno** a **Heslo** (nejméně 8 znaků) a klikne na
   **Vytvořit účet**.

Pozvánka platí 7 dní a do přijetí se zobrazuje v **Čekající pozvánky**.
Odtud ji můžete **Znovu odeslat pozvánku** (čímž se zároveň prodlouží)
nebo **Smazat pozvánku**.

!!! warning "Varování"
    Pozvánka odchází e-mailem, takže nejprve nastavte **E-mail (SMTP)**
    (krok 5). Pokud ji nelze odeslat, stránka to oznámí; opravte
    nastavení pošty a použijte **Znovu odeslat pozvánku**.

Více: [Uživatelé a pozvánky](../administration/users.md).

## 10. Připojte cloudové úložiště (volitelné) {#10-connect-cloud-storage-optional}

Pokud váš spolek uchovává nájemní smlouvy a další dokumenty v Nextcloudu
(nebo v jiném podporovaném úložišti), může Parcella na stránce každé
parcely zobrazit složku s dokumenty.

1. Otevřete **Administrace → Integrace** a najděte **Cloudové úložiště
   (dokumenty parcel, faktury, zálohy)**.
2. Vyberte **Typ úložiště** a zadejte požadované údaje o připojení.
   Klikněte na **Uložit** a pak na **Otestovat připojení**.
3. Volitelně nastavte společné složky níže: **Složka pro přijaté
   faktury**, **Složka pro dokumenty externích kontaktů**, **Složka
   poznámek**, **Složka pro soubory procesů**, **Složka pro tištěná
   oznámení**.
4. Přejděte do **Administrace → Nastavení → Funkční oblasti**,
   zaškrtněte **Cloudové úložiště** a klikněte na **Uložit nastavení**.
5. Na stránce každé parcely nastavte **Cesta ke složce** v
   **Dokumenty (cloudové úložiště)** -- napište ji nebo použijte
   **Procházet…** -- a klikněte na **Uložit**.

Cesty jsou vždy relativní k vybranému úložišti. Parcella složky
nevytváří ani nesdílí; udělejte to nejprve ve svém cloudu.

Více: [Integrace](../administration/integrations.md).

## 11. Zadejte nebo importujte skutečná data {#11-enter-or-import-your-real-data}

Teď přidejte své parcely a členy -- ručně v **Parcely → Nová parcela** a
**Členové → Nový člen**, nebo najednou z tabulky: viz
[Import členů a parcel](csv-import.md). Potom každého člena přiřaďte k
jeho parcele (viz [Přijetí nového člena](new-member.md), krok 6).

## 12. Vytvořte první zálohu {#12-make-your-first-backup}

1. Otevřete **Administrace → Uživatelé** a najděte kartu **Záloha**.
2. Klikněte na **Stáhnout zálohu** a soubor zip uložte na bezpečné
   místo.

Záloha obsahuje databázi, nahrané soubory a šifrovací klíč. Zacházejte
s ní jako se samotným seznamem členů.

Více: [Zálohování a obnova](../administration/backup.md).

## Související {#related}

- [Nastavení spolku](../administration/settings.md)
- [Zapínání a vypínání modulů](../administration/modules.md)
- [Uživatelé a pozvánky](../administration/users.md)
- [Skupiny](../administration/groups.md)
- [Integrace](../administration/integrations.md)
- [Ukázková data](../administration/sample-data.md)
- [Zálohování a obnova](../administration/backup.md)
- [Import členů a parcel](csv-import.md)

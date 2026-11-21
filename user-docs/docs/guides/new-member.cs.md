# Přijetí nového člena {#welcoming-a-new-member}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Někdo se přihlásí o zahrádku, dostane nabídku parcely, řekne ano -- a
stane se členem a nájemcem. Tento návod sleduje tuto cestu Parcellou, od
přihlášky po přivítání.

Členem lze někoho udělat dvěma způsoby:

- **Z přihlášky** (kroky 1–6): osoba je ve vašem
  [pořadníku](../glossary.md#applicant) v modulu **Uchazeči**.
  **Přidělit parcelu** pak najednou vytvoří záznam člena,
  [nájem](../glossary.md#tenancy) i fakturační adresu. To je obvyklý
  postup.
- **Ručně** (krok 7): pro někoho, kdo pořadníkem nikdy neprošel, nebo
  pro parcelu, která není ukončená.

!!! info "Kdo to může dělat"
    Práce s přihláškami vyžaduje oprávnění k **zápisu** u **Uchazeči**;
    přidělení parcely navíc vyžaduje **zápis** u **Členové a parcely**.
    Členové výboru a administrátoři mají obojí. Modul **Uchazeči** je ve
    výchozím stavu zapnutý.

## 1. Přijde přihláška {#1-the-application-comes-in}

Přihlášky přicházejí dvěma způsoby:

- **Z vašeho webu**, pokud tam spolek má formulář přihlášky a je zapnuté
  **Veřejné API formuláře přihlášek** (viz
  [Integrace](../administration/integrations.md)). Objeví se samy.
- **Ručně**, u přihlášek telefonem, dopisem nebo osobně: otevřete
  **Uchazeči**, klikněte na **Nový uchazeč**, vyplňte alespoň
  **E-mailová adresa** (jediné povinné pole) a případně **Jméno**,
  **Příjmení**, **Telefon**, **Zpráva uchazeče** a **Poznámka výboru** a
  klikněte na **Uložit**.

Chcete-li zadat starou přihlášku z papírového pořadníku, nastavte
**Přihlášeno** na původní datum. Datum přihlášky určuje pořadí v
pořadníku.

Nové přihlášky ukazují počítadlo vedle **Uchazeči** v postranním panelu
a na dashboardu, dokud je někdo neposune dál.

!!! tip "Červená vlajka"
    Pokud jméno, e-mail nebo telefon uchazeče odpovídá externímu
    kontaktu se štítkem „červená vlajka“, seznam i stránka uchazeče
    ukážou varování **Červená vlajka**. Viz
    [Uchazeči](../modules/applicants.md).

## 2. Ozvěte se {#2-get-in-touch}

1. Otevřete **Uchazeči** a klikněte na novou přihlášku.
2. V rámečku **Kontaktovat žadatele** zkontrolujte a upravte text
   e-mailu. Předmět zní *„Děkujeme za registraci na náš pořadník!“*.
3. Klikněte na **Odeslat** a potvrďte.

Parcella pošle text uchazeči e-mailem a nastaví stav na **Kontaktován**.
Rámeček je zobrazen, jen dokud je stav **Nový**. Pokud jste se ozvali
jinak, stačí stav změnit ručně (další krok).

Výchozí text tohoto e-mailu lze změnit v **Administrace → Nastavení →
Uchazeči → Text e-mailu novým žadatelům**.

## 3. Sledujte stav přihlášky {#3-track-the-applications-status}

Jak se věci posouvají, otevřete přihlášku, vyberte nový **Stav** a
klikněte na **Uložit**:

| Stav | Význam |
|---|---|
| **Nový** | Právě přišla. |
| **Kontaktován** | Ozvali jste se; uchazeč je v pořadníku. |
| **Zahrada nabídnuta** | Nabídli jste konkrétní parcelu. |
| **Přijato** | Uchazeč parcelu chce; předání se domlouvá. |
| **Zamítnuto** | Žádné další nabídky. |
| **Uzavřeno (zahrada přidělena)** | Nastaví se automaticky tlačítkem **Přidělit parcelu** (krok 5). |

Pokud uchazeč parcelu odmítne, ale chce zůstat v pořadníku, vraťte ho na
**Kontaktován**. Každá změna stavu je uvedena v **Historie stavu** na
stránce přihlášky.

## 4. Ujistěte se, že je parcela ukončená {#4-make-sure-the-parcel-is-terminated}

**Přidělit parcelu** nabízí jen parcely se stavem **ukončená** --
parcelu, kterou někdo opustil nebo se ji chystá opustit.

1. Otevřete parcelu v **Parcely** a klikněte na **Upravit**.
2. Nastavte **Stav** na **ukončená**, případně přidejte **Poznámka k
   ukončení**, a klikněte na **Uložit změny**.

Pokud odcházející nájemce ještě odchází, viz
[Předání parcely](parcel-handover.md) -- pokrývá celé předání včetně
strany starého nájemce.

## 5. Přidělte parcelu {#5-assign-the-parcel}

1. Otevřete přihlášku a klikněte na **Přidělit parcelu**. (Tlačítko je u
   každé otevřené přihlášky -- **Nový**, **Kontaktován**, **Zahrada
   nabídnuta** nebo **Přijato**.)
2. Vyberte **Ukončená parcela**. Seznam ukazuje každou parcelu s jejími
   současnými nájemci.
3. Nastavte **Datum předání** -- den, kdy nový nájemce parcelu přebírá.
   Může ležet v budoucnosti.
4. Volitelně zaškrtněte **Další uchazeči (spolunájemci)** -- například
   partnera, který se přihlásil zvlášť a parcelu přebírá společně s
   tímto uchazečem.
5. Volitelně zadejte **Složka dokumentů pro nové nájemce** (zobrazí se,
   jen pokud smíte spravovat cloudové složky).
6. Klikněte na **Náhled**.
7. Zkontrolujte rámeček **Předání parcely … dne …**:
    - **Dosavadní nájemci**: jejich nájem končí dnem předání. Pokud
      nemají jinou parcelu, jejich členství končí den předtím.
    - **Noví nájemci a příjemci faktur**: každý uchazeč se buď **stane
      novým členem** (jméno, e-mail a telefon se převezmou z přihlášky),
      nebo, pokud stejnou e-mailovou adresu už používá aktivní člen, se
      propojí s tímto existujícím členem.
8. Klikněte na **Předat parcelu** a potvrďte.

Co se stane v jednom kroku:

- Z uchazečů se stanou členové s **Členem od** nastaveným na datum
  předání.
- Od data předání se stanou nájemci parcely s nastaveným **Použít jako
  fakturační adresu**.
- Ze starých nájemců se stanou bývalí nájemci -- historie zůstává na
  stránce parcely.
- Stav parcely se vrátí na **aktivní**.
- Přihlášky se nastaví na **Uzavřeno (zahrada přidělena)**.

Při datu předání v budoucnosti zůstávají staří nájemci až do toho dne
nájemci, členy a příjemci faktur; noví se na stránce parcely zobrazují
jako budoucí („od …“) a k datu převezmou.

## 6. Doplňte záznam nového člena {#6-complete-the-new-members-record}

Předání zkopíruje jen jméno, e-mail a telefon. Doplňte zbytek:

1. Otevřete **Členové** a klikněte na nového člena (nebo použijte odkaz
   ze stránky parcely).
2. Klikněte na **Upravit** a doplňte **Datum narození**, **IBAN** a
   adresu (**Ulice a číslo popisné**, **PSČ**, **Město**).
3. Zkontrolujte **Může dostávat informace e-mailem**. U členů
   vytvořených přes **Přidělit parcelu** je zaškrtnuté, protože uchazeč
   uvedl e-mailovou adresu; odškrtněte ho, pokud člen chce jen papír.
   Bez něj jdou faktury a oznámení na hromádku k tisku místo do
   schránky.
4. V **Štítky** zaškrtněte existující štítky nebo napište nové
   (například „tým živého plotu“), oddělené čárkou.
5. Klikněte na **Uložit změny**.

Štítky můžete přidat i přímo na stránce člena, v kartě **Štítky**,
tlačítkem **Přidat štítek**.

## 7. Bez přihlášky: vytvořte člena ručně {#7-without-an-application-create-the-member-by-hand}

1. Otevřete **Členové** a klikněte na **Nový člen**.
2. Vyplňte **Jméno** a **Příjmení** (povinné), adresu, **Datum
   narození**, **IBAN**, **Členem od**, **E-mailová adresa** a
   **Telefonní číslo**, **Může dostávat informace e-mailem** a případné
   **Štítky**.
3. Klikněte na **Vytvořit člena**.
4. Na stránce člena v **Přidělené parcely** vyberte parcelu v **Vyberte
   parcelu…**, ponechte zaškrtnuté **Použít jako fakturační adresu**,
   pokud má tento člen dostávat faktury parcely, a klikněte na
   **Přidělit**.

Případně přidělte ze stránky parcely: **Současní nájemci → Vyberte
člena… → Přidělit**, kde můžete zadat i datum začátku. Chcete-li datum
začátku později opravit, použijte ikonu tužky vedle nájemce na stránce
parcely (**Upravit nájem**, pole **Nájemce od**).

Pokud je na parcele ještě starý nájemce, nejprve ukončete jeho nájem --
viz [Předání parcely](parcel-handover.md).

## 8. Přivítejte nového člena {#8-welcome-the-new-member}

Parcella nemá automatický uvítací e-mail. Pomohou dvě věci:

**Proces pro přijetí.** Modul **Procesy** obsahuje ukázkovou šablonu
**Přijetí nového člena** se třemi fázemi: **Přivítání** (**Uvítací
schůzka**, **Stanovy a zahradní řád předány**), **Dokumenty**
(**Podepsaná přihláška**, **Souhlas s inkasem přijat**) a **Dokončení**
(**Přidán do rozesílacího seznamu**, **Poznámky**).

1. Jednou: otevřete **Procesy → Šablony** a v části **Začít příkladem**
   klikněte na **Použít** vedle **Přijetí nového člena**. Fáze a pole
   můžete upravit. (Vytváření šablon vyžaduje plný přístup.)
2. Pro každého nového člena: na stránce člena v kartě **Procesy**
   klikněte na **Zahájit proces**, vyberte **Šablona** a klikněte na
   **Zahájit**.
3. Jak se věci vyřizují, vyplňujte pole a klikejte na **Hotovo --
   další fáze**. Povinná pole musí být vyplněna, než můžete pokračovat.

**Osobní zpráva.** Se zapnutým modulem **Oznámení** zaškrtněte nového
člena v seznamu **Členové** a klikněte na **Napsat vybraným**.

## Související {#related}

- [Uchazeči](../modules/applicants.md)
- [Členové](../modules/members.md)
- [Parcely](../modules/parcels.md)
- [Procesy](../modules/processes.md)
- [Oznámení](../modules/announcements.md)
- [Předání parcely](parcel-handover.md)
- Slovníček: [uchazeč](../glossary.md#applicant),
  [nájem](../glossary.md#tenancy),
  [fakturační adresa](../glossary.md#invoice-address)

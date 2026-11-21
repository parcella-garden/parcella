# Nastavení spolku {#club-settings}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Stránka nastavení obsahuje základní údaje vašeho spolku a přepínače,
které platí pro celou instalaci: jazyk, logo, e-mailový server, finanční
údaje a další.

!!! info "Kdo to může používat"
    Jen administrátoři. Otevřete **Administrace → Nastavení**.

![Nastavení spolku](../assets/screenshots/administration/settings.png)

## Jak stránka funguje {#how-the-page-works}

Stránka je sloupec karet. Každá karta je sbalená; kliknutím na záhlaví ji
otevřete. Otevřením jedné karty se ostatní sbalí.

| Prvek | Co dělá |
|---|---|
| **Hledat v nastavení...** | Napište slovo, například „logo“ nebo „IBAN“. Karty, které ho obsahují, se otevřou a slovo se zvýrazní; všechny ostatní karty se skryjí. Pokud nic neodpovídá, uvidíte **Žádná nastavení neodpovídají vyhledávání.** |
| **Uložit nastavení** | Nahoře i dole na stránce. Uloží **všechny karty najednou**, bez ohledu na to, kterou jste změnili. Uvidíte **Nastavení uložena.** |

!!! warning "Jedno tlačítko pro uložení všeho"
    Změny se uloží, jen když kliknete na **Uložit nastavení**. Pokud
    stránku předtím opustíte, ztratí se.

Karty shora dolů:

## Jazyk {#language}

Jazyk celé instalace: menu, tlačítka, zprávy, přihlašovací stránka a
e-maily a PDF, které Parcella vytváří. Všichni vidí stejný jazyk;
osobní nastavení jazyka neexistuje.

Vybírejte z **Deutsch**, **English**, **Polski**, **Čeština**,
**Slovenčina**, **Français** a **Nederlands**. Nová instalace začíná v
angličtině.

Kde text do zvoleného jazyka ještě není přeložen, ukáže Parcella místo
něj anglický text.

Jazyk nemění vzhled čísel, dat a peněžních částek -- to řídí karta
**Region a měna**.

## Branding {#branding}

| Pole | Co dělá |
|---|---|
| **Logo spolku** | Ukazuje vaše aktuální logo (nebo ikonu Parcelly). Chcete-li ho nahradit, vyberte nový soubor -- PNG, JPEG, WebP nebo SVG, nejvýše 2 MB. Logo se zobrazuje na přihlašovací stránce, nahoře v postranním panelu a v záhlaví vytvářených PDF. |
| **Odstranit logo (zpět na výchozí ikonu)** | Zobrazí se jen při nahraném logu. Zaškrtněte a uložte, chcete-li se vrátit k ikoně Parcelly. |

Špatný typ souboru nebo příliš velký soubor se odmítne se zprávou;
zbytek stránky se přesto uloží.

## Region a měna {#region-currency}

| Pole | Co dělá |
|---|---|
| **Region** | Jak se zapisují čísla a adresy -- oddělovač tisíců, desetinná čárka nebo tečka, zda PSČ stojí před městem, nebo za ním. Určuje také časové pásmo kalendářových kanálů. Možnosti: Německo, Spojené království, Francie, Nizozemsko, Polsko, Česká republika, Slovensko. Výchozí: Německo. |
| **Měna** | Symbol měny a jeho umístění („19,99 €“ nebo „£19.99“). Možnosti: euro (€), britská libra (£), polský zlotý (zł), česká koruna (Kč). Výchozí: euro. |

Obojí je nezávislé na jazyce: nizozemsky mluvící spolek může mít
nizozemská menu s částkami v eurech, anglická instalace může používat
německé formáty čísel.

## Funkční oblasti {#feature-areas}

Přepínače, které zapínají a vypínají moduly. Podrobně je popisuje
stránka [Zapínání a vypínání modulů](modules.md).

## Pořadí navigace {#navigation-order}

Určuje pořadí položek v postranním panelu všech uživatelů. Každá položka
má číselné pole: **Dashboard**, **Členové**, **Parcely**, **Podpora**,
**Žádosti o nákup**, **Pracovní sezení**, **Voda**, **Elektřina**,
**Pojištění**, **Kalendář**, **Oznámení**, **Inventář**, **Nástěnka
úkolů**, **Finance**, **Uchazeči**, **Externí kontakty**, **Přehledy**,
**Poznámky**, **Procesy**.

Nižší čísla jsou první. Výchozí čísla jsou 100, 200, 300 ... v pořadí
uvedeném výše, takže položku můžete přesunout mezi dvě jiné tím, že jí
dáte například 150. Prázdná pole se vrátí na výchozí číslo; cokoli, co
není celé číslo, se ignoruje.

**Administrace** v seznamu není: je vždy poslední.

## Aktualizace {#updates}

| Pole | Co dělá |
|---|---|
| **Automaticky kontrolovat aktualizace** | Ve výchozím stavu zapnuto. Parcella se pak každých několik hodin ptá GitHubu, zda vyšla novější verze, a ukáže upozornění na stránce [Systém](system.md). Nic o vašem spolku se neodesílá. Vypněte to, pokud váš server nesmí kontaktovat internet; stránka Systém pak neukazuje žádné informace o aktualizacích. |

## Uchazeči {#applicants}

Má význam, jen když používáte modul [Uchazeči](../modules/applicants.md).

| Pole | Co dělá |
|---|---|
| **Mazat přihlášky po (měsících)** | Každá přihláška, jejíž stav se tolik měsíců nezměnil, se **trvale smaže**, bez ohledu na stav a bez upozornění. Počítá se od poslední změny stavu, nebo od data přihlášky, pokud se stav nikdy nezměnil. Ponechte prázdné nebo zadejte 0, chcete-li přihlášky ponechat, dokud je nesmažete ručně. Užitečné pro ochranu osobních údajů. |
| **Text e-mailu novým žadatelům** | Text, který používá tlačítko **Kontaktovat žadatele** u nové přihlášky; před každým odesláním ho lze ještě změnit. `{name}` se nahradí jménem uchazeče, `{club}` názvem spolku. Ponechte prázdné, chcete-li použít vestavěný text, zobrazený šedě. |

## Protokol e-mailů {#email-log}

| Pole | Co dělá |
|---|---|
| **Uchovávat záznamy protokolu e-mailů (dny)** | Jak dlouho [Protokol e-mailů](email-log.md) uchovává své záznamy. Starší se automaticky mažou, protože adresy příjemců jsou osobní údaje. Výchozí 90 dní, možné 1 až 3650. |

## Údaje spolku {#club-data}

| Pole | Použití |
|---|---|
| **Název spolku** | Zobrazuje se nahoře v postranním panelu, na přihlašovací stránce a na tištěných dokumentech. Prázdné: „Parcella“. |
| **Ulice**, **PSČ**, **Město** | Adresa spolku v zápatí vytvářených PDF (faktury, oznámení, seznamy). |
| **Registrační číslo spolku**, **Obchodní rejstřík** | Také se tisknou v zápatí PDF, protože spolky registrované v Německu je musí uvádět. |

## Členové výboru {#board-members}

Kteří členové jsou momentálně ve výboru. Jejich jména se tisknou v
zápatí vytvářených dokumentů.

| Prvek | Co dělá |
|---|---|
| **Členové výboru** / **Zobrazit seznam** | Rozbalí seznam všech současných členů, každého se zaškrtávacím políčkem. **Skrýt seznam** ho opět sbalí. |
| **Hledat…** | Zúží seznam na odpovídající jména. **Žádné výsledky**, pokud nic neodpovídá. |
| **Vybrat vše** / **Zrušit výběr** | Zaškrtne nebo odškrtne všechny viditelné členy. |

Člen, který ze spolku odejde, automaticky z tištěného seznamu zmizí.

## Rozlohy (m²) {#areas-sqm}

Pozemky spolku, rozdělené tak, jak je obvykle vykazují německé
zahrádkářské spolky.

| Pole | Co dělá |
|---|---|
| **Celková rozloha (m²)** | Celý areál spolku. Zadáváte ji sami. |
| **Rozloha A (parcely, m²)** | Vypočítaná, nelze ji upravit: součet rozloh všech parcel, pronajatých i vypovězených. Smazané parcely a společné plochy se nepočítají. Stejný údaj jako **Celková rozloha (m²)** na [Dashboardu](../getting-started/dashboard.md). |
| **Rozloha B (společná, m²)** | Vypočítaná: celková rozloha minus rozloha A minus rozloha C. |
| **Rozloha C (obecní, m²)** | Zadáváte ji sami. |

Tyto údaje se používají, když [vyúčtování](../modules/finances/invoice-runs.md)
rozděluje náklady podle podílu každé parcely na společné ploše.

## Finanční nastavení {#finance-settings}

Používá je modul [Finance](../modules/finances/index.md).

| Pole | Co dělá |
|---|---|
| **Název banky**, **IBAN**, **BIC**, **Majitel účtu** | Tisknou se v zápatí každé faktury, aby členové věděli, kam platit. |
| **Další číslo faktury (přepsat)** | Obvykle prázdné: čísla prostě pokračují. Zadejte číslo, chcete-li, aby hned příští vyúčtování -- v kterémkoli roce -- začalo od něj. Parcella kontroluje, zda číslo není obsazené, až při dokončení onoho vyúčtování. Po použití se pole samo vyprázdní. |
| **Formát čísla faktury** | Jak vypadají čísla faktur. `{number}` je povinné, `{year}` volitelné; jakýkoli jiný text se použije tak, jak je napsán, např. `R-{year}-{number}`. Pod polem vidíte **Aktuálně používaný:** s příkladem; **(výchozí, nic vlastního není uloženo)** znamená, že platí výchozí `{year}/{number}`. Pole nabízí několik příkladů. |

Formát ovlivňuje jen faktury vytvořené od této chvíle. Již přidělená
čísla se nikdy nemění. Neplatný formát se neuloží; uvidíte zprávu, že
formát čísla faktury musí obsahovat {number} právě jednou (volitelně
také {year}) a žádné jiné zástupné symboly.

## E-mail (SMTP) {#email-smtp}

Každý e-mail, který Parcella posílá -- pozvánky, upozornění, oznámení,
faktury --, odchází přes tento poštovní server. Parcella nečte žádnou
schránku.

| Pole | Co dělá |
|---|---|
| **SMTP server** | Adresa poštovního serveru od vašeho poskytovatele e-mailu. |
| **SMTP port** | Obvykle 587 (nebo co uvádí poskytovatel). |
| **SMTP uživatel** | Přihlašovací jméno k poštovnímu serveru, často e-mailová adresa. |
| **SMTP heslo** | Zobrazuje se jako **Zatím nenastaveno** nebo **•••••••• (nastaveno -- znovu zadejte pro změnu)**. Ponechte prázdné, chcete-li zachovat uložené heslo; zadejte nové, chcete-li ho nahradit. Ukládá se šifrovaně. |
| **E-mail odesílatele** | Adresa, ze které e-maily přicházejí. |

!!! tip "Ověřte, že to funguje"
    Po uložení pozvěte sami sebe na druhou adresu nebo pošlete libovolný
    e-mail a pak se podívejte do [protokolu e-mailů](email-log.md).
    **Selhalo** s chybou vám řekne, co se poštovnímu serveru nelíbilo.

Pokud jsou tato pole prázdná, použije Parcella nastavení pošty, které
mohl do konfigurace serveru zadat ten, kdo ji instaloval.

Parcella šifruje spojení s poštovním serverem pomocí STARTTLS, metody
běžně používané na portu 587. Na stránce nastavení pro to není žádný
přepínač; lze to změnit jen v konfiguraci serveru.
<!-- TODO(verify): whether mail servers that only offer implicit TLS on port 465 work at all. -->

## Související {#related}

- [Zapínání a vypínání modulů](modules.md)
- [Integrace](integrations.md)
- [Založení nového spolku](../guides/new-club-setup.md)

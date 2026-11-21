# Poznámky {#notes}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Zápisy z členských schůzí, schůzí výboru, jednání s lidmi zvenčí a
cokoli dalšího, co stojí za zapsání. Poznámky se píší v Markdownu, řadí
se do kategorie a štítků a lze je vyhledávat, filtrovat a řadit. Pokud
váš spolek používá cloudové úložiště, může každá poznámka žít tam jako
soubor `.md`, který můžete otevřít a upravit i v cloudu.

!!! info "Kdo to může používat"
    - Přepínač modulu je **Poznámky** v **Administrace → Zapínání a
      vypínání modulů**. Ve výchozím stavu je **zapnutý**.
    - Role **Výbor** a **Správce** a členové skupiny s **Plný přístup ke
      každému modulu** mohou vše.
    - Všichni ostatní potřebují oprávnění **Poznámky** v některé ze
      svých [skupin](../administration/groups.md):
        - *čtení*: vidět seznam a poznámky, stahovat je, spouštět
          **Synchronizovat**;
        - *zápis*: vytvářet a upravovat poznámky, importovat záložky,
          přidávat, přejmenovávat a překládat kategorie a štítky;
        - *mazání*: mazat poznámky, kategorie a štítky.
    - Ukládání poznámek do cloudu vyžaduje také modul **Cloudové
      úložiště** a složku poznámek, viz [Poznámky v cloudu](#notes-in-the-cloud).

## Seznam poznámek {#note-list}

![Seznam poznámek](../assets/screenshots/notes/list.png)

Otevřete **Poznámky** v menu.

### Tlačítka nahoře {#buttons-at-the-top}

| Tlačítko | Co dělá |
|---|---|
| **Synchronizovat** | Zobrazí se, jen když je nastavená složka poznámek. Hned načte změny z cloudové složky (viz [Poznámky v cloudu](#notes-in-the-cloud)). |
| **Kategorie a štítky** | Otevře [Kategorie a štítky](#categories-tags). |
| **Importovat záložky** | Otevře [Import záložek](#import-bookmarks). Vyžaduje *zápis*. |
| **Nová poznámka** | Otevře prázdný [formulář poznámky](#writing-a-note). Vyžaduje *zápis*. |

### Hledání a filtry {#search-and-filters}

| Pole / tlačítko | Co dělá |
|---|---|
| **Hledat** | Hledá v názvu, textu a názvech štítků. Na velikosti písmen nezáleží. |
| **Kategorie** | **Vše**, **Žádná kategorie** nebo jedna kategorie. |
| **Štítky** | **Vše** nebo jeden štítek. |
| **Od** / **Do** | Jen poznámky, jejichž datum spadá do tohoto rozmezí. |
| **Řadit podle** | **Datum, nejnovější první** (výchozí), **Datum, nejstarší první**, **Název**, **Poslední změna**. |
| **Použít** | Použije hledání, filtry a řazení. |
| **Zrušit filtr** | Zobrazí se, jakmile je něco nastaveno. Zpět na všechny poznámky, nejnovější první. |

### Sloupce {#columns}

| Sloupec | Co ukazuje |
|---|---|
| **Datum** | Den, o kterém poznámka je (u zápisu: den schůze). |
| **Název** | Odkaz na poznámku. Ikona šipky otevře zdrojový odkaz poznámky v nové záložce (záložky). Oranžová ikona mraku znamená **Zatím neuloženo v cloudu**. |
| **Kategorie** | Kliknutím podle ní seznam vyfiltrujete. |
| **Štítky** | Kliknutím na jeden podle něj seznam vyfiltrujete. |
| **Změněno** | Kdy byla poznámka naposledy uložena (na malých obrazovkách skryto). |

Když je seznam prázdný, uvádí **Zatím žádné poznámky.**, nebo
**Těmto filtrům neodpovídá žádná poznámka.**, když je nastaven filtr.

## Čtení poznámky {#reading-a-note}

![Poznámka](../assets/screenshots/notes/detail.png)

Klikněte na název poznámky. Uvidíte název, datum, kategorii a štítky
(každý lze kliknutím použít jako filtr seznamu), **Zdroj (odkaz)**, pokud
jde o záložku, a formátovaný text. Zápatí ukazuje, kdo poznámku vytvořil
a kdo ji naposledy změnil, a s cloudovou složkou cestu k souboru
poznámky.

| Tlačítko | Co dělá |
|---|---|
| **Všechny poznámky** | Zpět na seznam. |
| **Stáhnout .md** | Stáhne poznámku jako soubor Markdown, s názvem, datem, kategorií a štítky v záhlaví nahoře. |
| **Stáhnout PDF** | Stáhne poznámku jako PDF s hlavičkovým papírem vašeho spolku. Obrázky, které jsou jen odkazované z webu, se vynechají. |
| **Upravit** | Otevře formulář. Vyžaduje *zápis*. |
| **Smazat poznámku** | Vyžaduje *mazání*. Zeptá se **Smazat tuto poznámku? Smaže se i její soubor v cloudu.** |

Otevření poznámky nejprve znovu načte její soubor z cloudu, takže vždy
vidíte aktuální text. Pokud se to nezdaří, stránka ukáže **Soubor v
cloudu nelze přečíst, zobrazena je naposledy synchronizovaná verze:
...** s důvodem.

## Psaní poznámky {#writing-a-note}

![Formulář poznámky](../assets/screenshots/notes/form.png)

**Nová poznámka** nebo **Upravit** otevře formulář (**Nová poznámka** /
**Upravit poznámku**).

| Pole / tlačítko | Co dělá |
|---|---|
| **Název** | Povinné, nejvýše 255 znaků. |
| **Datum** | Povinné. Den, o kterém poznámka je, ne den, kdy ji píšete. |
| **Kategorie** | **Žádná kategorie** nebo jedna z kategorií spolku. |
| **Štítky** | Zaškrtněte existující štítky. |
| **Nové štítky oddělené čárkou** | Napište nové štítky oddělené čárkami. Vytvoří se při uložení a přidají se do seznamu štítků spolku. |
| **Zdroj (odkaz)** | Volitelné: webová stránka, o které poznámka je. Poznámka se zdrojem je záložka. Musí začínat `http://` nebo `https://`. |
| **Poznámka** | Text v Markdownu. S cloudovou složkou pole uvádí, kam se soubor ukládá. |
| **Uložit** | Uloží poznámku. |
| **Zrušit** | Zpět bez uložení. |

Editor má panel nástrojů pro tučné písmo, kurzívu, přeškrtnutí, nadpis,
citaci, seznamy, kód, odkaz, tabulku a vodorovnou čáru. Ikona oka ukáže
náhled, ikona rozdělení ukáže text a náhled vedle sebe, šipky přepnou na
celou obrazovku a otazník otevře návod k Markdownu.

Možné zprávy: **Zadejte název.**, **Zadejte datum.**, **Zdroj musí být
webová adresa začínající http:// nebo https://.**, **Tato kategorie
(už) neexistuje.**, **Tento štítek (už) neexistuje.**

## Poznámky v cloudu {#notes-in-the-cloud}

Když je zapnutý modul **Cloudové úložiště** a administrátor nastavil
**Složka poznámek** v **Administrace → Integrace → Cloudové úložiště
(dokumenty parcel, faktury, zálohy)**, je text každé poznámky souborem
Markdown v této složce.

!!! note "Soubor je hlavní kopií textu"
    Text v souboru v cloudu má přednost. Vy i ostatní můžete tyto
    soubory otevírat a měnit libovolným editorem v cloudu (Nextcloud
    Text, Obsidian a tak dále); změny se objeví v Parcelle. Název,
    datum, kategorie, štítky a zdroj existují jen v Parcelle a do
    souboru se nezapisují.

Jak to funguje v praxi:

- **Uložení** nejprve zapíše soubor. Pokud soubor nelze zapsat,
  poznámka se neuloží a uvidíte **Neuloženo, soubor v cloudu nelze
  zapsat: ...** a váš text zůstane ve formuláři. Změna jen názvu, data,
  štítků nebo zdroje se souboru vůbec nedotkne.
- **Podsložky jsou kategorie.** Poznámka ve složce „Schůze výboru/“
  dostane kategorii „Schůze výboru“ (v případě potřeby se vytvoří).
  Uložení poznámky s jinou kategorií přesune její soubor do složky této
  kategorie. Poznámky bez kategorie leží přímo ve složce poznámek.
- **Nové soubory** se pojmenovávají podle data a názvu, např.
  `20261108-schuze-vyboru.md`. Parcella soubor nikdy dodatečně
  nepřejmenuje.
- **Soubory vytvořené v cloudu** se stanou poznámkami. Jejich datum se
  vezme ze začátku názvu souboru (`2026-11-08`, `20261108` nebo
  `202506` pro 1. den daného měsíce), jinak z data poslední změny
  souboru.
- **Synchronizace**: seznam poznámek čte změny z cloudu sám, nejvýše
  jednou za minutu. **Synchronizovat** to udělá hned a oznámí
  **Synchronizováno: {n} nových, {n} změněných, {n} odebraných, {n}
  nahraných.** Soubor smazaný v cloudu odstraní svou poznámku ze
  seznamu.
- **Smazání** poznámky v Parcelle smaže i její soubor. Pokud se to
  nezdaří, poznámka se nesmaže: **Nesmazáno, soubor v cloudu nelze
  smazat: ...**
- **Ještě žádná složka?** Poznámky se uchovávají jen v Parcelle a jsou
  označeny **Zatím neuloženo v cloudu**. Nahrají se při první
  synchronizaci po nastavení složky.

### Když někdo změnil soubor současně {#when-someone-changed-the-file-at-the-same-time}

Pokud byl soubor během vaší úpravy změněn v cloudu, uložení se zastaví
se zprávou **Neuloženo: poznámka byla mezitím změněna v cloudu.** Žlutá
karta **Mezitím změněno v cloudu** ukazuje verzi z cloudu (s **Zobrazit
jako Markdown** pro surový text) a váš vlastní text zůstává ve formuláři
níže. Zkopírujte, co potřebujete, a klikněte znovu na **Uložit**, čímž
verzi v cloudu přepíšete.

Pokud byla poznámka změněna jak v Parcelle (když nebyla nastavena
žádná složka), tak v cloudu, synchronizace ponechá verzi z cloudu a vaši
uloží jako samostatnou poznámku označenou „conflict copy“ (konfliktní
kopie). Seznam pak uvede, kolik takových kopií vzniklo. Nic se neztratí.

## Kategorie a štítky {#categories-tags}

![Kategorie a štítky](../assets/screenshots/notes/taxonomy.png)

**Kategorie a štítky** ukazuje kategorie a štítky spolku. Každá poznámka
má jednu kategorii a libovolný počet štítků. Stejné kategorie a štítky
má používat i budoucí znalostní báze. Nové instalace začínají čtyřmi
kategoriemi: „General meeting“, „Board meeting“, „Meeting with
externals“ a „Other“. **Poznámky** (vpravo nahoře) vás vrátí zpět.

Stránka má dvě karty, **Kategorie** a **Štítky**, které fungují stejně:

| Pole / tlačítko | Co dělá |
|---|---|
| Název + tlačítko zaškrtnutí | Přejmenuje kategorii nebo štítek. Vyžaduje *zápis*; jinak se název jen zobrazí. Přejmenování kategorie při další synchronizaci přesune soubory jejích poznámek do složky s novým názvem; stará prázdná složka zůstane. |
| „Poznámky: {count}“ | Otevře seznam poznámek vyfiltrovaný podle ní. |
| Tlačítko překladu | Otevře názvy pro jednotlivé jazyky. Se *zápisem* můžete zadat název pro každý jazyk, který Parcella podporuje, a kliknout na **Uložit překlady**; prázdná pole ukazují hlavní název. |
| Tlačítko koše | Po dotazu **Smazat "{name}"? Poznámky zůstanou, jen bez této položky.** smaže kategorii nebo štítek. Vyžaduje *mazání*. |
| **Nová kategorie** / **Nový štítek** + **Přidat** | Přidá novou. Vyžaduje *zápis*. |

## Import záložek {#import-bookmarks}

![Import záložek](../assets/screenshots/notes/import-bookmarks.png)

Pokud váš spolek shromažďuje užitečné odkazy (dodavatelé, úřady, návody)
v Nextcloud Bookmarks nebo v prohlížeči, můžete je najednou převést na
poznámky. Každá záložka se stane poznámkou s odkazem jako zdrojem.

1. Exportujte záložky jako soubor HTML. Umí to Nextcloud Bookmarks i
   každý prohlížeč.
2. Klikněte na **Importovat záložky**, vyberte soubor a klikněte na
   **Zobrazit náhled**. Zatím se nic neuloží.
3. Náhled uvádí, kolik je „nová“, „už je poznámkou“ (poznámka se stejným
   odkazem existuje -- přeskočí se) a „není webový odkaz“ (přeskočí se).
   Tabulka uvádí **Datum**, **Název** (s odkazem a popisem), **Štítky** a
   **Stav** každé záložky.
4. Klikněte na **Importovat záložky ({count})**, nebo **Vybrat jiný
   soubor**.

Nové poznámky nedostanou žádnou kategorii; s cloudovou složkou se uloží
do kořene složky poznámek. Složky záložky se stanou štítky, popis textem
a datum přidání záložky datem poznámky. Parcella odkazované stránky
nikdy neotevírá.

Pokud soubor neobsahuje žádné záložky: **V tomto souboru nebyly nalezeny
žádné záložky.**

## Poznámky a asistenti AI {#notes-and-ai-assistants}

Administrátor může zapnout modul **Konektor MCP pro klienty AI**.
Asistent AI, například Claude, pak může vyhledávat, číst a zapisovat
poznámky -- ale jen poznámky nesoucí štítek uvolnění (ve výchozím stavu
`ki-freigegeben`). Každá jiná poznámka pro něj zůstává neviditelná.
Poznámky, které AI napíše, dostanou štítek (ve výchozím stavu
`ki-erstellt`), abyste věděli, co zkontrolovat. Ve výchozím stavu je to
vypnuté, protože to předává poznámky spolku externí službě.

<!-- TODO(verify): where the release and created tag names are configured in the UI (stored as club settings); and link to the API tokens page section on "MCP connector only" tokens. -->

## Související {#related}

- [Integrace](../administration/integrations.md) -- cloudové úložiště a
  složka poznámek.
- [API tokeny](../administration/api-tokens.md)
- [Skupiny](../administration/groups.md) -- udělení oprávnění k
  poznámkám.
- [Zapínání a vypínání modulů](../administration/modules.md)

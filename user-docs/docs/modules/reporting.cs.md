# Přehledy {#reporting}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Hlavní údaje vašeho spolku v průběhu času jako grafy: jak staří jsou
vaši členové, jak se vyvíjelo členství, kolik parcel bylo vypovězeno,
kolik lidí se hlásí a jak dopadly pracovní hodiny. Hodí se pro výroční
zprávu nebo členskou schůzi.

!!! info "Kdo to může používat"
    - Přepínač modulu je **Přehledy** v **Administrace → Zapínání a
      vypínání modulů**. Ve výchozím stavu je **zapnutý**.
    - Role **Výbor** a **Správce** a členové skupiny s **Plný přístup ke
      každému modulu** ho vidí vždy.
    - Všichni ostatní potřebují *čtení* u **Přehledy** v některé ze svých
      [skupin](../administration/groups.md). Stránka ukazuje jen součty
      a počty, nikdy jména, takže nepotřebuje přístup ke členům,
      pracovním hodinám ani uchazečům.

## Stránka přehledů {#reporting-page}

![Přehledy](../assets/screenshots/reporting/index.png)

Otevřete **Přehledy** v menu. Stránka je jen pro čtení. Každý údaj se
při každém otevření stránky počítá z vašich aktuálních dat; nic se
neukládá ani nemusí aktualizovat. Časové řady ukazují nejvýše posledních
10 let, od prvního roku s daty po aktuální rok. Minulý rok se počítá ve
stavu k 31. prosinci, aktuální rok ve stavu k dnešku.

Každý graf je karta s:

- samotným grafem (najeďte na něj myší a uvidíte přesná čísla);
- šedou poznámkou s ikonou informace tam, kde je potřeba něco
  vysvětlit, například kolik členů bylo vynecháno;
- **Zobrazit údaje jako tabulku**, které rozbalí stejná čísla jako
  tabulku připravenou ke zkopírování. Koláčové grafy přidávají sloupec
  **Podíl / součet** s procenty, skládané grafy sloupec se součtem za
  rok.

Graf bez dat uvádí **Zatím žádná data.**

Některé grafy se zobrazí, jen když je zapnutý jejich modul: grafy
uchazečů potřebují **Uchazeči**, grafy pracovních hodin **Správa
pracovních hodin** a graf elektřiny **Správa elektřiny**.

## Grafy {#the-charts}

| Graf | Co počítá |
|---|---|
| **Členové podle generace** | Koláčový graf dnešních aktivních členů podle roku narození: **Tichá generace (do 1945)**, **Baby boomers (1946–1964)**, **Generace X (1965–1980)**, **Mileniálové (1981–1996)**, **Generace Z (1997–2012)**, **Generace Alfa (od 2013)**. Členové bez data narození jsou vynecháni; poznámka uvádí kolik. |
| **Členové po letech** | Spojnicový graf počtu **Členové** v každém roce: každý, jehož datum „členem od“ je nejpozději na konci daného roku a kdo do té doby neodešel. Členové bez data vstupu se počítají v každém roce; poznámka uvádí kolik. |
| **Vypovězené parcely po letech** | Sloupcový graf **Ukončené nájmy** po letech: každý nájem, jehož datum konce připadá na daný rok, včetně dat konce již nastavených na později v tomto roce. Parcela předaná od jednoho nájemce dalšímu se počítá jako jeden ukončený nájem. |
| **Žadatelé po čtvrtletích** | Sloupcový graf nových **Uchazeči** podle data přihlášky, pro každé čtvrtletí loňského a letošního roku. |
| **Žadatelé po letech** | Totéž po letech. |
| **Pracovní hodiny po letech** | Skládané sloupce pro každý rok s nastavením pracovních hodin. Každá parcela (nebo člen, viz níže) se počítá v právě jedné skupině, kontrolované v tomto pořadí: **Osvobozeno**, **Platí náhradu (chybí hodiny)**, **Splněno díky patronátu**, **Splněno brigádami**. V letech, kdy se pracovní hodiny dlužily po členech místo po parcelách, uvádí poznámka „Počítáno po členech místo po parcelách v ...“. |
| **Převody hodin po letech** | Dva sloupce za rok: počet **Převody** hodin a celkové **Převedené hodiny**. |
| **Parcely s elektřinou** | Koláčový graf dnešních aktivních parcel **S elektrickou přípojkou** (alespoň jeden elektroměr na parcele) a **Bez elektrické přípojky**. |

!!! note "Na co pamatovat"
    - **Členové podle generace** a **Parcely s elektřinou** ukazují jen
      dnešek. Parcella neukládá snímky, takže nemůže říct, jak to
      vypadalo v dřívějším roce.
    - Člen, který byl smazán (místo nastavení data konce), zmizí i ze
      všech minulých let. Členství ukončujte místo mazání členů a
      historie zůstane správná.
    - Údaje pocházejí z dat, jak byla zadána. Chybějící datum vstupu
      nebo datum narození se objeví v poznámkách; opravte ho u
      [člena](members.md) a stránku znovu načtěte.

Pro grafy neexistuje tlačítko exportu. Čísla zkopírujete pomocí
**Zobrazit údaje jako tabulku**, například do tabulky nebo výroční
zprávy.

## Související {#related}

- [Členové](members.md) -- data vstupu a data narození.
- [Parcely](parcels.md) -- nájmy a jejich data konce.
- [Uchazeči](applicants.md)
- [Pracovní hodiny](work-hours.md) -- osvobození, sponzoring a převody
  hodin.
- [Voda a elektřina](metering.md) -- elektroměry na parcelách.

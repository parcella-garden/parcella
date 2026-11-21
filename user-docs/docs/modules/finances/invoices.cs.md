# Faktury, platby a upomínky {#invoices-payments-and-reminders}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Jakmile je vyúčtování dokončeno, jeho faktury žijí dál. Tato kapitola
popisuje, jak fakturu najít, znovu odeslat, zaznamenat, co bylo
zaplaceno, a upomenout členy, kteří do data splatnosti nezaplatili.

!!! info "Kdo to může používat"
    Součást modulu **Finance** (ve výchozím stavu vypnutý). Prohlížení
    faktur, PDF a seznamu upomínek vyžaduje oprávnění ke čtení u
    **Finance**. Zaznamenávání plateb, opětovné odesílání e-mailů a
    odesílání upomínek vyžaduje oprávnění k zápisu; smazání platby
    vyžaduje oprávnění k mazání. Členové výboru a administrátoři mohou
    vše. Viz [Finance](index.md).

Faktury vznikají vždy jen [dokončením vyúčtování](invoice-runs.md#what-finalizing-does).
Jednotlivou fakturu nelze ručně vytvořit, upravit ani smazat a funkce
storna nebo dobropisu neexistuje.
<!-- TODO(verify): no cancel/credit-note feature exists in the code; if a finalized invoice is wrong, the club has to handle the correction outside Parcella (e.g. record a payment with a note). Confirm the recommended workaround with the maintainers. -->

## Faktury (všechna vyúčtování) {#invoices-all-runs}

![Faktury](../../assets/screenshots/finances/invoice-list.png)

Otevřete je tlačítkem **Všechny faktury** na stránce
[Roční vyúčtování](invoice-runs.md#annual-invoices-list-of-runs).
Uvádí každou fakturu ze všech dokončených vyúčtování, nejvyšší číslo
faktury první. **Zpět na vyúčtování** v horní liště vás vrátí zpět.

**Filtr**

| Filtr | Co dělá |
|---|---|
| **Parcela** | Faktury, jejichž číslo parcely obsahuje tento text. |
| **Č. faktury** | Faktury, jejichž číslo obsahuje tento text, např. `2026/` pro celý rok 2026. |
| **Příjemce** | Faktury, jejichž jména příjemců obsahují tento text. |
| **Částka od** / **Částka do** | Částka faktury (součet, bez poplatků za upomínky) nejméně / nejvýše tolik. |
| **Stav** | **Vše**, **Otevřená**, **Částečně uhrazená** nebo **Uhrazená**. |
| **Filtrovat** / **Zrušit filtr** | Použije filtr / zruší všechny filtry. |

**Tabulka**

| Sloupec | Co ukazuje |
|---|---|
| **Č. faktury** | Číslo faktury; kliknutím otevřete [fakturu](#invoice). |
| **Parcela** | Číslo parcely, nebo **Bez parcely (člen)** u faktury adresované přímo členovi. |
| **Příjemce** | Jména, na která byla faktura při vystavení adresována. |
| **Součet** | Částka faktury. |
| **Uhrazeno** | Součet všech dosud zaznamenaných plateb. |
| **Stav** | **Otevřená** (červeně), **Částečně uhrazená** (žlutě) nebo **Uhrazená** (zeleně), viz [Stav platby](#payment-status). |
| **Uhrazeno dne** | Data všech plateb oddělená čárkami. |

Pokud nic neodpovídá: „Žádné faktury neodpovídají těmto filtrům.“

Stejný seznam, omezený na jedno vyúčtování a s tlačítky pro platby a
PDF, je na [stránce dokončeného vyúčtování](invoice-runs.md#invoice-run-finalized).

## Faktura {#invoice}

![Faktura](../../assets/screenshots/finances/invoice-detail.png)

Otevře se, když kliknete na číslo faktury. Titulek je „Faktura
*číslo*“.

**Horní lišta**

| Tlačítko | Co dělá |
|---|---|
| **PDF** | Otevře PDF faktury v nové záložce. |
| **Znovu odeslat e-mail** | Pošle PDF faktury e-mailem znovu, i když už bylo odesláno. Vyžaduje oprávnění k zápisu. Pokud nikoho nelze zastihnout, uvidíte „Pro tuto fakturu nebyl nalezen žádný dostupný člen s fakturační adresou (e-mailová upozornění + uložená e-mailová adresa).“ |
| **Zpět na faktury** | Zpět na seznam všech faktur. |

Karta **Faktura**

| Pole | Co ukazuje |
|---|---|
| **Parcela** | Číslo parcely, nebo **Bez parcely (člen)**. |
| **Příjemce** | Jména a adresa, jak jsou vytištěny na faktuře. Byly pevně stanoveny při dokončení vyúčtování; pozdější změny adresy je nemění. Pokud nájemci bydlí na různých adresách, uvidíte „*n* kopií, jedna na adresu“ a jména a adresu každé kopie. |
| **Součet** | Částka faktury. |
| **Termín splnění** | Datum splatnosti vyúčtování. |
| **Stav** | Stav platby, za ním „dosud uhrazeno / celkem dlužno“. Celkem dlužno zahrnuje případné poplatky za upomínky. |

Karta **Upomínky**: upomínky odeslané k této faktuře a formulář pro
odeslání další, viz [Odeslání upomínky](#sending-a-reminder).

!!! note "Kde jsou platby?"
    Platby se zaznamenávají v dialogu platby v seznamu faktur
    vyúčtování, viz [Platby](#payments). Stránka faktury ukazuje
    výsledek v řádku **Stav**.

### PDF faktury {#the-invoice-pdf}

PDF je uspořádáno jako německý obchodní dopis pro obálky s okénkem: logo
a název spolku nahoře, adresa příjemce tam, kde ji ukazuje okénko
obálky, pak číslo faktury, datum, datum splatnosti a parcela, tabulka
řádků (**Popis**, **Množ.**, **Jednotková cena**, **Celkem**),
**Součet**, text patičky vyúčtování a údaje vašeho spolku (adresa,
banka) v zápatí stránky. Tyto údaje spolku pocházejí z
[Nastavení spolku](../../administration/settings.md).

Rozvržení odpovídá normě **DIN 5008 tvar B**: adresa je v okénku obálky
DL nebo C6/5 a krátké značky na levém okraji ukazují, kde přeložit (v
jedné a dvou třetinách stránky) a kde děrovat. Upomínky a dopisy s
oznámeními používají stejné rozvržení.

Název souboru začíná datem vystavení a číslem parcely (nebo příjmením
člena), za nimi následuje číslo faktury. Faktura s jednou kopií na
adresu má v PDF všechny kopie, každou na vlastních stránkách.

## Platby {#payments}

Platba jsou peníze přijaté za fakturu. Zaznamenat ji můžete dvěma
způsoby:

- **Ručně:** na [stránce dokončeného vyúčtování](invoice-runs.md#payment-dialog)
  klikněte na **Platba** vedle faktury, zadejte **Částka**, **Uhrazeno
  dne**, volitelně **Poznámka** a **Účet** a klikněte na **Přidat
  platbu**.
- **Z bankovního výpisu:** na [stránce zápisů účtu](bank-accounts.md#bookings-of-an-account)
  přidejte zápis nebo importujte soubor CSV a vyberte odpovídající
  otevřenou fakturu. Parcella pak platbu zaznamená za vás, s již
  nastaveným účtem.

Faktura může mít libovolný počet plateb, takže částečné platby a splátky
nejsou problém. Chybnou platbu opravíte tak, že ji smažete (ikona koše v
dialogu platby, vyžaduje oprávnění k mazání) a zadáte znovu.

!!! tip "Uhrazeno dne určuje rok"
    [Účetní přehled](bookkeeping.md#accounting-statement) počítá příjem
    ke dni **Uhrazeno dne**, ne k datu faktury. Faktura za rok 2026
    zaplacená v lednu 2027 je příjmem roku 2027.

### Stav platby {#payment-status}

Stav se pokaždé počítá z plateb, takže nikdy není zastaralý:

| Stav | Kdy |
|---|---|
| **Otevřená** | Zatím nic nezaplaceno. |
| **Částečně uhrazená** | Něco zaplaceno, ale méně než částka faktury plus všechny poplatky za upomínky. |
| **Uhrazená** | Platby dosáhnou částky faktury plus všech poplatků za upomínky (nebo více). |

Přeplatky se přijímají a jednoduše se zobrazí jako **Uhrazená**;
Parcella nevede zůstatek přeplatku.

## Upomínky {#reminders}

![Upomínky](../../assets/screenshots/finances/reminders.png)

Otevřete je přes **Finance → Upomínky** nebo kartou **Upomínky** na
přehledu. Seznam **Faktury po splatnosti** ukazuje každou fakturu, která
není plně zaplacena a jejíž datum splatnosti vyúčtování uplynulo, nejdéle
po splatnosti první. Je to pracovní seznam pro pokladníka: otevřete
každou fakturu a rozhodněte, zda poslat upomínku.

| Sloupec / tlačítko | Co ukazuje |
|---|---|
| **Parcela** | Číslo parcely. U faktury člena prázdné. |
| **Příjemce** | Jména příjemců. |
| **Č. faktury** | Číslo faktury. |
| **Termín splnění** | Datum splatnosti vyúčtování. |
| **Po splatnosti** | Kolik dní uplynulo od data splatnosti, např. „14 dní“. |
| **Dlužná částka** | Co se ještě dluží: částka faktury plus poplatky za upomínky minus platby. |
| **Odeslané upomínky** | Kolik upomínek bylo odesláno, s datem poslední, nebo „Zatím žádná odeslána“. |
| **Otevřít** | Otevře fakturu, kde upomínku odešlete. |

Pokud nic není po splatnosti: „Žádné faktury po splatnosti — není co
upomínat.“

Faktura z tohoto seznamu zmizí, jakmile je plně zaplacena.

### Odeslání upomínky {#sending-a-reminder}

Na [faktuře](#invoice) karta **Upomínky** uvádí každou již odeslanou
upomínku:

| Sloupec | Co ukazuje |
|---|---|
| „Upomínka č. *n*“ | Stupeň upomínky: první upomínka je č. 1, další č. 2 a tak dále. |
| Datum | Kdy byla vytvořena. |
| Doručení | „Odesláno e-mailem“, „K tisku/poštovnímu odeslání“, pokud ji nešlo poslat e-mailem, nebo „Odesláno e-mailem, k tomu výtisky k poštovnímu odeslání“, pokud ji některé adresy dostaly e-mailem a jiné potřebují dopis. |
| Poplatek | Poplatek účtovaný s touto upomínkou, pokud nějaký je. |
| Ikona PDF | Otevře PDF upomínky v nové záložce -- odtud ji vytiskněte pro poštovní doručení. Obsahuje dopisy, které je třeba poslat poštou, jeden na adresu pro lidi bez e-mailu (všechny kopie, pokud všichni dostali e-mail). |

Pokud žádná ještě nebyla odeslána: „Zatím nebyla odeslána žádná
upomínka.“

Pod seznamem, dokud faktura není plně zaplacena a máte oprávnění k
zápisu:

| Pole | Co dělá |
|---|---|
| **Poplatek (volitelné)** | Poplatek za upomínku, např. `5,00`. Přičte se k dlužné částce faktury. Bez poplatku nechte prázdné. |
| **Zpráva (volitelné)** | Krátký text vytištěný dole na upomínce. |
| **Odeslat upomínku** | Vytvoří další upomínku a doručí ji. |

Co udělá **Odeslat upomínku**: „Vygeneruje další upomínku jako PDF --
poplatek (pokud je zadán) se přičte k dlužné částce. Odešle ji e-mailem,
pokud s tím člen souhlasil a má uloženou adresu, jinak ji připraví k
tisku/poštovnímu doručení.“

- Upomínka je vždy o stupeň vyšší než poslední. Pevné stupně upomínek
  neexistují; kolik upomínek a kdy poslat, rozhoduje váš spolek.
- E-mail jde téže osobě, které by šla faktura (viz
  [kdo dostane e-mail](invoice-runs.md#delivery)), s předmětem
  „Upomínka č. *n* k faktuře *číslo* — *název spolku*“ a s PDF v
  příloze.
- Pokud e-mail nelze odeslat, upomínka se zachová a označí „K
  tisku/poštovnímu odeslání“. Vytiskněte ji přes ikonu PDF.

PDF upomínky má nadpis „Upomínka k platbě č. *n*“, odkazuje na fakturu a
její datum a uvádí **Původní částka**, **Dosud uhrazeno**, **Předchozí
poplatky za upomínky** a **Poplatek za tuto upomínku** (řádky poplatků
jen tehdy, když nějaký poplatek je), nyní dlužnou částku, vaši zprávu a
závěrečnou větu s žádostí o zaplacení.

!!! warning "Poplatky nelze odstranit"
    Upomínku ani její poplatek nelze po odeslání smazat ani změnit.
    Před kliknutím na **Odeslat upomínku** poplatek ještě jednou
    zkontrolujte. Pokud do **Poplatek (volitelné)** zadáte něco, co
    není číslo, upomínka se odešle bez poplatku.

## Související {#related}

- [Vyúčtování](invoice-runs.md) -- odkud faktury pocházejí.
- [Bankovní účty a zaúčtování](bank-accounts.md) -- zaznamenávání plateb
  z bankovního výpisu.
- [Roční vyúčtování](../../guides/annual-invoicing.md)
- [Protokol e-mailů](../../administration/email-log.md) -- kontrola, zda
  poštovní server přijal e-mail s fakturou nebo upomínkou.

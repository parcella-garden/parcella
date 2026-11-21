# Podpora {#support}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

Parcella nemá vlastní systém tiketů. Váš spolek odpovídá na e-maily a
dotazy z kontaktního formuláře v helpdesku -- FreeScout, Zammad, Znuny /
OTRS, osTicket, Zendesk nebo Freshdesk -- a modul podpory tento helpdesk
propojuje s Parcellou: vidíte, která konverzace patří ke kterému členovi
a parcele, čtete konverzaci a můžete z ní udělat kartu na nástěnce
úkolů. Odpovědi se vždy píší v samotném helpdesku.

!!! info "Kdo to může používat"
    - Modul se zapíná přepínačem **Podpora (helpdesk)** v části
      [Zapínání a vypínání modulů](../administration/modules.md). Ve
      výchozím stavu je **vypnutý**, protože ukládá přístupové údaje k
      helpdesku. Samotný helpdesk vybírá a připojuje administrátor v
      [Integrace](../administration/integrations.md).
    - **Konverzace podpory v Parcelle:** členové výboru a
      administrátoři a uživatelé, jejichž skupina dává **Čtení** pro
      **Podpora (helpdesk)** (viz [Skupiny](../administration/groups.md)).
      K propojení konverzace se členem nebo parcelou je potřeba
      **Zápis**.
    - **Vytvořit úkol:** jen členové výboru a administrátoři (nebo
      uživatelé ve skupině s plným přístupem), stejně jako samotná
      nástěnka úkolů.
    - **Všichni ostatní** dostanou v navigaci odkaz **Podpora**, jakmile
      je modul zapnutý a helpdesk má webovou adresu: otevře helpdesk
      přímo v nové záložce.

## Odkud konverzace pocházejí {#where-conversations-come-from}

Parcella kontroluje helpdesk na nové a změněné konverzace zhruba každých
pět minut. Ukládá jen křížový odkaz -- předmět, zákazníka, stav, počet
zpráv a odkazy na člena, parcelu a úkol. Samotné zprávy zůstávají v
helpdesku a při každém otevření konverzace se načtou znovu.

**Párování se členy:** když konverzace přijde, Parcella hledá člena, ke
kterému patří:

1. Pokud byl tento zákazník helpdesku už dříve propojen se členem,
   použije se tento člen.
2. Jinak, pokud má e-mailovou adresu zákazníka **právě jeden** člen,
   propojí se automaticky.
3. Pokud adresu sdílí více členů (např. pár s jednou schránkou) nebo ji
   nemá nikdo (soused, dodavatel), konverzace zůstane bez člena. Můžete
   ho propojit ručně.

Pokud má propojený člen právě jednu současnou parcelu, propojí se i ta.
Konverzace, která má člena -- automaticky nebo nastaveného vámi --, se
později už znovu nepáruje.

Když se v Parcelle změní jméno člena, přejmenuje se i jeho záznam
zákazníka v helpdesku, pokud to helpdesk podporuje.

**Stavy:** každý helpdesk pojmenovává své stavy jinak; Parcella je
zobrazuje jako `active`, `pending`, `closed`, `spam` nebo `deleted`.
Uzavřené, spamové a smazané konverzace jsou skryté ze seznamu, odznaku
i dashboardu. Pokud se konverzace v helpdesku znovu otevře, objeví se
znovu i s propojeným členem.

### Co který helpdesk podporuje {#what-each-helpdesk-supports}

| Helpdesk | Seznam konverzací a odznak | Čtení konverzací | Kontaktní formulář vytvoří konverzaci | Synchronizace jmen zákazníků |
|---|---|---|---|---|
| FreeScout | ano | ano | ano | ano |
| Zammad | ano | ano | ano | ano |
| Znuny / OTRS | ano | ano | ano | ne |
| osTicket | ne | ne | ano | ne |
| Zendesk | ano | ano | ano | ano |
| Freshdesk | ano | ano | ano | ano |

S osTicketem může Parcella jen předávat dotazy z kontaktního formuláře
na webu; pracujete s nimi pouze v osTicketu.

Zobrazují se jen zprávy, které zákazník vidí -- interní poznámky
zůstávají v helpdesku. Přílohy se nezobrazují; kvůli nim otevřete
konverzaci v helpdesku.

## Konverzace podpory {#support-conversations}

![Konverzace podpory](../assets/screenshots/support/list.png)

**Podpora** v navigaci otevře seznam otevřených konverzací aktivního
helpdesku, naposledy aktualizované první. Červený odznak vedle
**Podpora** -- a dlaždice **Otevřené konverzace podpory** na
[dashboardu](../getting-started/dashboard.md) -- počítá tytéž
konverzace, ať mají člena, nebo ne.

| Pole / tlačítko | Co dělá |
|---|---|
| **Otevřít v {helpdesk}** | Otevře helpdesk v nové záložce. Zobrazí se, jen pokud je nastavena webová adresa helpdesku. |
| **Předmět** | Předmět konverzace. Kliknutím kamkoli do řádku konverzaci otevřete. |
| **Zákazník** | Jméno odesílatele nebo jeho e-mailová adresa. |
| **Člen** | Propojený člen, nebo „—“. |
| **Stav** | `active` nebo `pending` (uzavřené se nevypisují). |
| **Zprávy** | Počet zpráv, jak ho naposledy hlásil helpdesk. |
| **Aktualizováno** | Kdy se konverzace v helpdesku naposledy změnila. |
| **Úkol** | Ikona tabule, pokud je konverzace propojena s úkolem. |

Místo seznamu můžete vidět:

- „Zatím není nastaven žádný helpdesk. …“ -- administrátor ho ještě
  musí vybrat v [Integrace](../administration/integrations.md).
- „{helpdesk} nedokáže vypsat konverzace přes své rozhraní. …“ --
  helpdesk je osTicket.
- „Zatím žádné konverzace podpory.“ -- právě teď není nic otevřeného.

## Stránka konverzace {#conversation-page}

<!-- TODO(verify): no screenshot -- the list's rows open conversations by click, not by a link, so the screenshot tool can't follow one; without a connected helpdesk the transcript would only show an error anyway. -->

Ukazuje jednu konverzaci s jejím předmětem jako titulkem.

| Tlačítko | Co dělá |
|---|---|
| **Zpět** | Vrátí se na seznam. |
| **Otevřít v {helpdesk}** | Otevře tuto konverzaci v helpdesku -- tam na ni odpovídáte. |

### Konverzace {#conversation}

Zprávy, nejstarší první, každá s autorem a časem. Pokud je nelze
načíst, poznámka vysvětlí proč -- helpdesk není dostupný, nedokáže
konverzace zobrazit (osTicket), nebo „Helpdesk této konverzace není
(už) nastaven.“, když spolek mezitím přešel na jiný helpdesk. „Zprávy se
nepodařilo načíst.“ znamená, že helpdesk žádné nevrátil.

### Člen {#member}

Ukazuje propojeného člena (s odkazem na jeho stránku), nebo „Nebyl
přiřazen žádný člen.“.

S oprávněním k zápisu vyberte člena a klikněte na **Uložit**:

- Členové s e-mailovou adresou zákazníka jsou uvedeni první, označení
  **navrhováno**. Pokud adresu sdílí více členů, poznámka vás požádá o
  výběr toho správného.
- Pod nimi všichni současní členové.
- **-- žádný --** propojení odstraní.

Uložením člena se resetuje i parcela: pokud má člen právě jednu
současnou parcelu, propojí se; jinak žádná.

### Parcela {#parcel}

Zobrazí se, jakmile je propojen člen. S oprávněním k zápisu vyberte
jednu ze současných parcel člena, nebo **-- žádný --**, a klikněte na
**Uložit**.
<!-- TODO(verify): without write permission the Parcel card is empty -- the linked parcel isn't displayed at all for read-only users. -->

### Nástěnka úkolů {#task-board}

| Pole / tlačítko | Co dělá |
|---|---|
| **Otevřít úkol** | Zobrazí se, když je konverzace propojena s úkolem; otevře úkol. |
| Seznam + **Vytvořit úkol** | Vytvoří novou kartu ve vybraném seznamu [nástěnky úkolů](tasks.md) a propojí ji s konverzací. Název karty je předmět; její popis uvádí helpdesk, číslo konverzace a případně propojeného člena. Jen pro členy výboru a administrátory. |

Pokud nástěnka úkolů zatím nemá žádné seznamy, vytvoření úkolu selže se
zprávou „Na nástěnce úkolů zatím nejsou žádné seznamy“.
<!-- TODO(verify): there is a route to link an existing task to a conversation, but no form on the page uses it. -->

!!! note "Odpovídá se v helpdesku"
    Parcella záměrně nemá pole pro odpověď. Klikněte na **Otevřít v
    {helpdesk}** a odpovězte tam; nová zpráva se v Parcelle objeví při
    dalším otevření konverzace.

## Kontaktní formulář na webu {#the-website-contact-form}

Pokud má web vašeho spolku kontaktní formulář, může přes Parcellu
vytvořit konverzaci přímo v helpdesku. Jde o samostatný přepínač,
**Veřejné API kontaktního formuláře**, rovněž ve výchozím stavu vypnutý.
Nastavení popisuje stránka [Integrace](../administration/integrations.md).

## Související {#related}

- [Integrace](../administration/integrations.md) -- výběr a připojení
  helpdesku
- [Nástěnka úkolů](tasks.md) -- další postup u konverzace
- [Členové](members.md) -- e-mailové adresy používané k párování
- [Dashboard](../getting-started/dashboard.md)

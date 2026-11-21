# API tokeny {#api-tokens}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

API token je klíč, který umožňuje jinému programu používat Parcellu
jménem určitého uživatele, bez jeho hesla -- například skriptu, který
exportuje data, nebo asistentovi AI, který čte poznámky spolku. Většina
spolků ho nikdy nepotřebuje.

!!! info "Kdo to může používat"
    Každý uživatel může spravovat **své vlastní** tokeny: **Změnit heslo**
    v postranním panelu → **API tokeny pro integrace** → **Spravovat**
    (stránka **Moje API tokeny**). Administrátoři navíc vidí tokeny
    **všech uživatelů** v **Administrace → API tokeny**.

![API tokeny](../assets/screenshots/administration/api-tokens.png)

## Jak se token chová {#how-a-token-behaves}

- Jedná **přesně s oprávněními účtu, ke kterému patří**. Token
  odečítače měřidel může dělat jen to, co může odečítač.
- Zobrazí se **jen jednou**, hned po vytvoření. Tehdy si ho zkopírujte;
  později ho nelze zjistit.
- Přestane fungovat, když vyprší, když je zrušen nebo když se heslo
  účtu změní či resetuje. Zastaví ho i deaktivace účtu.

Zacházejte s tokenem jako s heslem. Pokud mohl uniknout, zrušte ho.

## Nový token {#new-token}

| Pole / tlačítko | Co dělá |
|---|---|
| **Uživatel** | *Jen na stránce administrátorů.* Za čí účet token jedná. Tokeny můžete vytvářet pro sebe a pro účty **bez** plného přístupu -- typicky pro samostatný účet integrace, který se sám nikdy nepřihlašuje. Tokeny pro jiné účty s plným přístupem nejsou možné, protože token by tiše jednal jménem té osoby. |
| **Název** | Povinné, nejvýše 100 znaků. Uveďte, k čemu slouží, např. „Znalostní báze Claude“. |
| **Platnost** | **30 dní**, **90 dní**, **365 dní** (výchozí) nebo **bez omezení**. Dejte přednost omezené platnosti. |
| **Jen konektor MCP (pro klienta AI)** | Zobrazí se jen při zapnutém modulu **Konektor MCP pro klienty AI**. Takový token funguje jen pro připojení AI a jen s poznámkami uvolněnými pro AI; jakékoli jiné použití je odmítnuto. Pro asistenta AI vždy používejte tento druh. |
| **Vytvořit token** | Vytvoří token a ukáže ho v zeleném rámečku: *Zkopírujte si ho hned: zobrazí se jen tentokrát ...* |

## Seznam tokenů {#the-token-list}

| Sloupec / tlačítko | Co ukazuje nebo dělá |
|---|---|
| **Název** | Název, prvních několik znaků tokenu (pro rozpoznání) a případně odznak **Jen MCP**. |
| **Uživatel** | *Jen na stránce administrátorů.* Čí token to je. |
| **Vytvořeno** | Datum vytvoření. |
| **Naposledy použit** | Kdy ho program naposledy použil, nebo **nikdy**. |
| **Platnost** | Datum vypršení nebo **bez omezení**. |
| **Stav** | **aktivní**, **vypršel**, **zrušen** nebo **ukončen** (heslo bylo změněno po vytvoření tokenu). |
| **Zrušit** | Jen u aktivních tokenů. Po potvrzení token okamžitě přestane fungovat. |

Když žádné tokeny nejsou, zobrazí se **Zatím žádné API tokeny.**

## Připojení asistenta AI k poznámkám {#connecting-an-ai-assistant-to-the-notes}

S modulem **Konektor MCP pro klienty AI** může asistent AI, například
Claude, vyhledávat a číst -- a pokud to povolíte, i zapisovat --
[poznámky](../modules/notes.md), které jste pro něj uvolnili, a nic
jiného. Stručně:

1. Zapněte **Konektor MCP pro klienty AI** (a **Poznámky**) v části
   [Zapínání a vypínání modulů](modules.md).
2. [Pozvěte](users.md) pro asistenta samostatný účet a zařaďte ho do
   [skupiny](groups.md), která dává jen **Čtení** (případně i zápis)
   u modulu **Poznámky**.
3. Zde pro tento účet vytvořte token se zaškrtnutou volbou **Jen
   konektor MCP (pro klienta AI)**.
4. Uvolněte poznámky pro AI tím, že jim dáte štítek pro uvolnění
   popsaný v kapitole o poznámkách.

Uvolňujte jen poznámky, které neobsahují žádné osobní údaje: odcházejí
do externí služby AI. Nastavení krok za krokem pro jednotlivé klienty AI
je v [návodu k nastavení MCP](https://github.com/parcella-garden/parcella/blob/main/docs/mcp-setup.md).

## Pro vývojáře {#for-developers}

Samotné REST API -- koncové body, ověřování, příklady -- je popsáno v
[dokumentaci pro vývojáře](https://github.com/parcella-garden/parcella#rest-api)
a interaktivně v **Administrace → API dokumentace (Swagger)**.

## Související {#related}

- [První přihlášení a váš účet](../getting-started/first-login.md#change-password)
- [Uživatelé a pozvánky](users.md)

# API tokeny {#api-tokens}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

API token je kľúč, ktorý umožňuje inému programu používať Parcellu v
mene niekoho, bez jeho hesla -- napríklad skriptu, ktorý exportuje
dáta, alebo AI asistentovi, ktorý číta poznámky spolku. Väčšina
spolkov ho nikdy nepotrebuje.

!!! info "Kto to môže používať"
    Každý používateľ môže spravovať **svoje vlastné** tokeny: **Zmeniť
    heslo** v bočnom paneli → **API tokeny pre integrácie** →
    **Spravovať** (stránka **Moje API tokeny**). Administrátori vidia aj
    tokeny **všetkých** v časti **Administrácia → API tokeny**.

![API tokeny](../assets/screenshots/administration/api-tokens.png)

## Ako sa token správa {#how-a-token-behaves}

- Koná **presne s oprávneniami účtu, ku ktorému patrí**. Token
  odpočtára meradiel môže robiť len to, čo môže odpočtár.
- Zobrazí sa **len raz**, hneď po vytvorení. Vtedy si ho skopírujte;
  neskôr sa nedá zistiť.
- Prestane fungovať, keď vyprší, keď je zrušený alebo keď sa heslo
  účtu zmení alebo obnoví. Zastaví ho aj deaktivácia účtu.

Zaobchádzajte s tokenom ako s heslom. Ak mohol uniknúť, zrušte ho.

## Nový token {#new-token}

| Pole / tlačidlo | Čo robí |
|---|---|
| **Používateľ** | *Len na stránke administrátorov.* V mene ktorého účtu token koná. Tokeny môžete vytvárať pre seba a pre účty **bez** plného prístupu -- zvyčajne vyhradený účet pre integráciu, ktorý sa sám nikdy neprihlasuje. Tokeny pre iné účty s plným prístupom nie sú možné, pretože token by v mene tejto osoby konal nepozorovane. |
| **Názov** | Povinný, najviac 100 znakov. Uveďte, na čo slúži, napr. „znalostná báza Claude“. |
| **Platnosť** | **30 dní**, **90 dní**, **365 dní** (predvolené) alebo **bez obmedzenia**. Uprednostnite obmedzenú platnosť. |
| **Len konektor MCP (pre klienta AI)** | Zobrazí sa, len keď je zapnutý modul **Konektor MCP pre klientov AI**. Takýto token funguje len pre pripojenie AI a len s poznámkami uvoľnenými pre AI; každé iné použitie sa odmietne. Pre AI asistenta vždy použite tento druh. |
| **Vytvoriť token** | Vytvorí token a ukáže ho v zelenom poli: *Skopírujte si ho teraz: zobrazí sa iba tentoraz ...* |

## Zoznam tokenov {#the-token-list}

| Stĺpec / tlačidlo | Čo ukazuje alebo robí |
|---|---|
| **Názov** | Názov, prvé znaky tokenu (aby ste ho spoznali) a prípadne odznak **Len MCP**. |
| **Používateľ** | *Len na stránke administrátorov.* Čí token to je. |
| **Vytvorené** | Dátum vytvorenia. |
| **Naposledy použitý** | Kedy ho program naposledy použil, alebo **nikdy**. |
| **Platnosť** | Dátum vypršania alebo **bez obmedzenia**. |
| **Stav** | **aktívny**, **vypršal**, **zrušený** alebo **ukončený** (heslo sa zmenilo po vytvorení tokenu). |
| **Zrušiť** | Len pri aktívnych tokenoch. Po potvrdení token okamžite prestane fungovať. |

**Zatiaľ žiadne API tokeny.** sa zobrazí, keď žiadne nie sú.

## Pripojenie AI asistenta k poznámkam {#connecting-an-ai-assistant-to-the-notes}

S modulom **Konektor MCP pre klientov AI** môže AI asistent, napríklad
Claude, vyhľadávať a čítať -- a ak to povolíte, aj zapisovať --
[poznámky](../modules/notes.md), ktoré ste preň uvoľnili, a nič iné.
Stručne:

1. Zapnite **Konektor MCP pre klientov AI** (a **Poznámky**) v časti
   [Zapínanie a vypínanie modulov](modules.md).
2. [Pozvite](users.md) samostatný účet pre asistenta a zaraďte ho do
   [skupiny](groups.md), ktorá udeľuje len čítanie (a podľa potreby
   zápis) pre **Poznámky**.
3. Tu vytvorte pre tento účet token so zaškrtnutým **Len konektor MCP
   (pre klienta AI)**.
4. Uvoľnite poznámky pre AI tak, že im dáte štítok uvoľnenia opísaný v
   kapitole o poznámkach.

Uvoľňujte len poznámky bez osobných údajov: idú do externej služby AI.
Postup nastavenia krok za krokom pre každého klienta AI je v
[návode na nastavenie MCP](https://github.com/parcella-garden/parcella/blob/main/docs/mcp-setup.md).

## Pre vývojárov {#for-developers}

Samotné REST API -- koncové body, autentifikácia, príklady -- je
opísané v
[dokumentácii pre vývojárov](https://github.com/parcella-garden/parcella#rest-api)
a interaktívne v časti **Administrácia → API dokumentácia (Swagger)**.

## Súvisiace {#related}

- [Prvé prihlásenie a váš účet](../getting-started/first-login.md#change-password)
- [Používatelia a pozvánky](users.md)

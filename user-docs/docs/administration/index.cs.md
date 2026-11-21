# Administrace {#administration}

!!! note "Strojový překlad"
    Tato stránka byla strojově přeložena z angličtiny a dosud nebyla zkontrolována. Pokud je něco nejasné, platí anglická verze (jazyk přepnete nahoře).

V administraci se nastavuje a udržuje vaše instalace Parcelly: kdo se
smí přihlásit, co smí dělat, základní údaje spolku, propojení s jinými
službami a zálohy.

!!! info "Kdo to může používat"
    Jen **administrátoři**: účty se starší rolí **Správce** nebo ve
    skupině s oprávněním **Přístup k administračnímu panelu**. Členové
    výboru s plným přístupem k modulům ji nevidí, pokud nejsou zároveň
    administrátory. Viz
    [Role, skupiny a oprávnění](../getting-started/roles-and-permissions.md).

Najdete ji dole v postranním panelu pod **Administrace**.

## Stránky {#the-pages}

| Položka v postranním panelu | Stránka | Co tam děláte |
|---|---|---|
| **Systém** | [Informace o systému a aktualizace](system.md) | Zjistíte svou verzi a zda existuje aktualizace; stáhnete zálohu. |
| | [Zálohování a obnova](backup.md) | Obnovení ze zálohy; plánování automatických záloh do cloudu. |
| **Uživatelé** | [Uživatelé a pozvánky](users.md) | Zvaní lidí, úpravy, deaktivace a mazání účtů, resetování hesel. |
| **Skupiny** | [Skupiny](groups.md) | Rozhodujete, kdo smí co číst, zapisovat a mazat. |
| **API tokeny** | [API tokeny](api-tokens.md) | Zobrazení a odvolání tokenů všech uživatelů; vytváření tokenů pro integrační účty. |
| **Nastavení** | [Nastavení spolku](settings.md) | Název a adresa spolku, logo, jazyk, region a měna, e-mailový server, finanční údaje, pořadí navigace a další. |
| | [Zapínání a vypínání modulů](modules.md) | Karta **Funkční oblasti** na stránce nastavení. |
| **Integrace** | [Integrace](integrations.md) | Formuláře na webu, koncepty pro web, cloudové úložiště, helpdesk, Nextcloud Deck, odkazy na kalendářové kanály. |
| **Protokol e-mailů** | [Protokol e-mailů](email-log.md) | Kontrola, zda e-mail odešel. |
| **Ukázková data** | [Ukázková data](sample-data.md) | Naplnění nové instalace ukázkovými daty na vyzkoušení a jejich opětovné odstranění. |
| **API dokumentace (Swagger)** | -- | Technický popis programového rozhraní, pro vývojáře. |

## Nastavení nové instalace {#setting-up-a-new-installation}

Rozumné pořadí pro zcela novou instalaci:

1. Přihlaste se vestavěným účtem administrátora a změňte jeho heslo --
   viz [První přihlášení](../getting-started/first-login.md#the-very-first-login-after-installation).
2. V [Nastavení spolku](settings.md): jazyk, region a měna, údaje
   spolku, logo a e-mailový server (bez něj Parcella nemůže posílat
   pozvánky).
3. V [Zapínání a vypínání modulů](modules.md): vypněte, co
   nepotřebujete, a zapněte, co potřebujete.
4. Vytvořte [skupiny](groups.md) pro jednotlivé funkce ve spolku.
5. [Pozvěte](users.md) do těchto skupin ostatní členy výboru.
6. Nastavte [zálohy](backup.md).

Návod [Založení nového spolku](../guides/new-club-setup.md) tím provede
společně se zadáním členů a parcel.

Instalace samotné Parcelly (server, Docker, webová adresa) je popsána v
[dokumentaci pro vývojáře](https://github.com/parcella-garden/parcella#install-self-hosting).

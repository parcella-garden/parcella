# Administrácia {#administration}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

V administrácii sa vaša inštalácia Parcelly nastavuje a udržiava: kto
sa smie prihlásiť, čo smie robiť, kmeňové údaje spolku, prepojenia s
inými službami a zálohy.

!!! info "Kto to môže používať"
    Len **administrátori**: účty so staršou rolou **Administrátor**
    alebo v skupine s **Prístup k administračnému panelu**. Členovia
    výboru s plným prístupom k modulom ju nevidia, pokiaľ nie sú zároveň
    administrátormi. Pozri
    [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md).

Nájdete ju v dolnej časti bočného panela pod **Administrácia**.

## Stránky {#the-pages}

| Položka v bočnom paneli | Stránka | Čo tam robíte |
|---|---|---|
| **Systém** | [Informácie o systéme a aktualizácie](system.md) | Zistíte svoju verziu a či existuje aktualizácia; stiahnete zálohu. |
| | [Zálohovanie a obnova](backup.md) | Obnova zo zálohy; plánovanie automatických záloh do cloudu. |
| **Používatelia** | [Používatelia a pozvánky](users.md) | Pozývanie ľudí, úprava, deaktivácia a mazanie účtov, obnovenie hesiel. |
| **Skupiny** | [Skupiny](groups.md) | Rozhodnete, kto smie čo čítať, zapisovať a mazať. |
| **API tokeny** | [API tokeny](api-tokens.md) | Zobrazenie a odvolanie tokenov všetkých používateľov; vytvorenie tokenov pre integračné účty. |
| **Nastavenia** | [Nastavenia spolku](settings.md) | Názov a adresa spolku, logo, jazyk, región a mena, e-mailový server, finančné údaje, poradie navigácie a ďalšie. |
| | [Zapínanie a vypínanie modulov](modules.md) | Karta **Funkčné oblasti** na stránke nastavení. |
| **Integrácie** | [Integrácie](integrations.md) | Formuláre na webe, koncepty pre web, cloudové úložisko, helpdesk, Nextcloud Deck, odkazy na kalendárové kanály. |
| **Protokol e-mailov** | [Protokol e-mailov](email-log.md) | Overenie, či e-mail odišiel. |
| **Ukážkové dáta** | [Ukážkové dáta](sample-data.md) | Naplnenie novej inštalácie ukážkovými dátami na vyskúšanie a ich opätovné odstránenie. |
| **API dokumentácia (Swagger)** | -- | Technický popis programového rozhrania pre vývojárov. |

## Nastavenie novej inštalácie {#setting-up-a-new-installation}

Rozumné poradie pre úplne novú inštaláciu:

1. Prihláste sa vstavaným administrátorským účtom a zmeňte jeho heslo
   -- pozri [Prvé prihlásenie](../getting-started/first-login.md#the-very-first-login-after-installation).
2. V [Nastaveniach spolku](settings.md): jazyk, región a mena, údaje
   spolku, logo a e-mailový server (bez neho Parcella nemôže posielať
   pozvánky).
3. V časti [Zapínanie a vypínanie modulov](modules.md): vypnite, čo
   nepotrebujete, a zapnite, čo potrebujete.
4. Vytvorte [skupiny](groups.md) pre úlohy vo vašom spolku.
5. [Pozvite](users.md) ostatných členov výboru do týchto skupín.
6. Nastavte [zálohy](backup.md).

Návod [Založenie nového spolku](../guides/new-club-setup.md) prechádza
týmto spolu so zadávaním členov a parciel.

Inštalácia samotnej Parcelly (server, Docker, webová adresa) je opísaná
v [dokumentácii pre
vývojárov](https://github.com/parcella-garden/parcella#install-self-hosting).

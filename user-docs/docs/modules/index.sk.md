# Moduly {#modules}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Parcella sa skladá z modulov: jeden na každú oblasť práce spolku. Váš
spolok zapína len tie, ktoré potrebuje; ostatné z navigácie zmiznú pre
všetkých. Vypnutie modulu nikdy nezmaže jeho dáta -- zapnite ho znova
a všetko je späť.

Administrátor zapína a vypína moduly v časti
[Zapínanie a vypínanie modulov](../administration/modules.md). Kto smie
zapnutý modul používať, sa nastavuje pomocou
[skupín](../administration/groups.md).

## Prehľad {#overview}

| Modul | Na čo slúži | Zapnutý po inštalácii? |
|---|---|---|
| [Členovia](members.md) | Všetci, ktorí patria do spolku: kontaktné údaje, dátumy členstva, roly, história. | Vždy zapnutý |
| [Parcely](parcels.md) | Záhradky, ich nájmy a nájomcovia, minulí aj súčasní. | Vždy zapnutý |
| [Uchádzači](applicants.md) | Ľudia, ktorí požiadali o voľnú záhradku, ich stav a poznámky výboru. | Áno |
| [Pracovné hodiny](work-hours.md) | Pracovné zmeny, prihlášky a dochádzka, sponzorstvá, prevody hodín a ročné hodnotenie povinných hodín. | Áno |
| [Voda a elektrina](metering.md) | Meradlá, odpočty a prehľady spotreby. Voda a elektrina sa zapínajú samostatne. | Áno |
| [Poistenie](insurance.md) | Poistenie majetku a úrazové poistenie pre každú parcelu a rok, s ročným prehľadom. | Áno |
| [Financie](finances/index.md) | Ročné faktúry za parcely, platby, upomienky, bankové účty, prijaté faktúry a účtovníctvo. | Nie |
| [Žiadosti o nákup](purchase-requests.md) | Výdavky spolku, ktoré pred minutím peňazí schvália dvaja členovia výboru. | Áno |
| [Kalendár](calendar.md) | Kalendár spolku, narodeniny, prítomnosť a neprítomnosť výboru, vlastné kalendáre -- každý aj ako odoberateľný kalendárový kanál. | Áno |
| [Oznamy](announcements.md) | Novinky spolku napíšete raz a pošlete na web, e-mailom aj ako oznam na vytlačenie. | Nie |
| [Nástenka úloh](tasks.md) | Nástenka Na spracovanie / Rozpracované / Hotovo pre záležitosti spolku. Len výbor a administrátori. | Áno |
| [Inventár](inventory.md) | Všetko, čo spolok vlastní (aj veci členov uložené na pozemku spolku), s požičiavaním. | Áno |
| [Poznámky](notes.md) | Zápisnice zo schôdzí a iné poznámky, s kategóriami a štítkami, voliteľne uložené ako súbory v cloude. | Áno |
| [Procesy](processes.md) | Vaše vlastné postupy krok za krokom, napríklad odovzdanie parcely, spustené pre parcelu, člena alebo uchádzača. | Áno |
| [Externé kontakty](external-contacts.md) | Dodávatelia, remeselníci a úrady, prepojení s faktúrami a žiadosťami o nákup. | Áno |
| [Podpora](support.md) | Konverzácie helpdesku vášho spolku, prepojené s členmi, parcelami a úlohami. | Nie |
| [Prehľady](reporting.md) | Čísla spolku v priebehu rokov ako grafy. Len na čítanie. | Áno |

## Prečo sú niektoré moduly na začiatku vypnuté {#why-some-modules-start-switched-off}

Moduly, ktoré sú po inštalácii vypnuté, robia každý niečo, o čom by sa
mal spolok rozhodnúť vedome:

- **Financie** pracujú s peniazmi členov a posielajú faktúry hromadne.
- **Oznamy** môžu poslať e-mail každému členovi a publikovať na vašom
  webe.
- **Podpora** sa pripája na externý helpdesk a potrebuje jeho
  prístupové údaje.

To isté platí pre doplnky v zozname modulov, ktoré nemajú vlastnú
kapitolu: **Cloudové úložisko**, **Synchronizácia Nextcloud Deck**,
**Konektor MCP pre klientov AI** a tri verejné formuláre pre web
(**Verejné API pre prihlášky**, **Verejné API kontaktného formulára**,
**Verejné API formulára prihlášok**). Buď ukladajú heslá k externým
službám, alebo otvárajú formulár do verejného internetu. Pozri
[Zapínanie a vypínanie modulov](../administration/modules.md) a
[Integrácie](../administration/integrations.md).

## Súvisiace {#related}

- [Roly, skupiny a oprávnenia](../getting-started/roles-and-permissions.md)
- [Orientácia v aplikácii](../getting-started/navigation.md)

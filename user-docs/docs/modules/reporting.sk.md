# Prehľady {#reporting}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Kľúčové čísla vášho spolku v čase, ako grafy: aký je vek členov, ako sa
vyvíjalo členstvo, koľko parciel bolo vypovedaných, koľko ľudí sa
hlási a ako dopadli pracovné hodiny. Hodí sa pre výročnú správu alebo
členskú schôdzu.

!!! info "Kto to môže používať"
    - Prepínač modulu je **Prehľady** v časti **Administrácia →
      Zapínanie a vypínanie modulov**. Predvolene je **zapnutý**.
    - Roly **Výbor** a **Administrátor** a členovia skupiny s **Plný
      prístup ku každému modulu** ho vidia vždy.
    - Všetci ostatní potrebujú *čítanie* pre **Prehľady** v niektorej zo
      svojich [skupín](../administration/groups.md). Stránka ukazuje len
      súčty a počty, nikdy mená, takže nepotrebuje aj prístup k členom,
      pracovným hodinám alebo uchádzačom.

## Stránka prehľadov {#reporting-page}

![Prehľady](../assets/screenshots/reporting/index.png)

Otvorte **Prehľady** v menu. Stránka je len na čítanie. Každé číslo sa
pri každom otvorení stránky vypočíta z vašich aktuálnych dát; nič sa
neukladá ani nemusí aktualizovať. Časové rady ukazujú najviac
posledných 10 rokov, od prvého roka s dátami po aktuálny rok. Minulý
rok sa počíta podľa stavu k 31. decembru, aktuálny rok podľa stavu
dnes.

Každý graf je karta s:

- samotným grafom (podržte nad ním myš a uvidíte presné čísla);
- sivou poznámkou s ikonou informácie tam, kde treba niečo vysvetliť,
  napríklad koľko členov bolo vynechaných;
- **Zobraziť údaje ako tabuľku**, čo rozbalí tie isté čísla ako
  tabuľku pripravenú na kopírovanie. Koláčové grafy pridávajú stĺpec
  **Podiel / súčet** s percentami, skladané grafy stĺpec so súčtom za
  rok.

Graf bez dát hovorí **Zatiaľ žiadne údaje.**

Niektoré grafy sa zobrazujú, len keď je ich modul zapnutý: grafy
uchádzačov potrebujú **Uchádzači**, grafy pracovných hodín **Správa
pracovných hodín** a graf elektriny **Správa elektriny**.

## Grafy {#the-charts}

| Graf | Čo počíta |
|---|---|
| **Členovia podľa generácie** | Koláčový graf dnešných aktívnych členov podľa roku narodenia: **Tichá generácia (do 1945)**, **Baby boomers (1946–1964)**, **Generácia X (1965–1980)**, **Mileniáli (1981–1996)**, **Generácia Z (1997–2012)**, **Generácia Alfa (od 2013)**. Členovia bez dátumu narodenia sú vynechaní; poznámka uvádza koľko. |
| **Členovia po rokoch** | Čiarový graf počtu **Členovia** v každom roku: každý, koho dátum „Členom od“ je k koncu tohto roka alebo skôr a kto dovtedy neodišiel. Členovia bez dátumu vstupu sa počítajú v každom roku; poznámka uvádza koľko. |
| **Vypovedané parcely po rokoch** | Stĺpcový graf **Ukončené nájmy** po rokoch: každý nájom, ktorého dátum ukončenia pripadá na tento rok, vrátane dátumov ukončenia už nastavených na neskôr v tomto roku. Parcela odovzdaná od jedného nájomcu ďalšiemu sa počíta ako jeden ukončený nájom. |
| **Žiadatelia po štvrťrokoch** | Stĺpcový graf nových **Uchádzači** podľa dátumu prihlášky, za každý štvrťrok minulého a tohto roka. |
| **Žiadatelia po rokoch** | To isté po rokoch. |
| **Pracovné hodiny po rokoch** | Skladané stĺpce pre každý rok, ktorý má nastavenie pracovných hodín. Každá parcela (alebo člen, pozri nižšie) sa počíta presne v jednej skupine, kontrolované v tomto poradí: **Oslobodené**, **Platí náhradu (chýbajú hodiny)**, **Splnené vďaka patronátu**, **Splnené brigádami**. V rokoch, keď sa pracovné hodiny dlžili na člena namiesto na parcelu, poznámka hovorí „V rokoch ... počítané na člena namiesto na parcelu.“ |
| **Prevody hodín po rokoch** | Dva stĺpce za rok: počet **Prevody** hodín a celkové **Prevedené hodiny**. |
| **Parcely s elektrinou** | Koláčový graf dnešných aktívnych parciel **S elektrickou prípojkou** (na parcele je aspoň jeden elektromer) a **Bez elektrickej prípojky**. |

!!! note "Čo mať na pamäti"
    - **Členovia podľa generácie** a **Parcely s elektrinou** ukazujú
      len dnešok. Parcella si neuchováva snímky, takže nevie povedať,
      ako to vyzeralo v skoršom roku.
    - Člen, ktorý bol zmazaný (namiesto zadania dátumu ukončenia),
      zmizne aj zo všetkých minulých rokov. Členstvá ukončujte namiesto
      mazania členov a história zostane správna.
    - Čísla pochádzajú z dát tak, ako boli zadané. Chýbajúci dátum
      vstupu alebo narodenia sa objaví v poznámkach; opravte ho pri
      [členovi](members.md) a stránku načítajte znova.

Tlačidlo na export grafov neexistuje. Na skopírovanie čísel, napríklad
do tabuľky alebo výročnej správy, použite **Zobraziť údaje ako
tabuľku**.

## Súvisiace {#related}

- [Členovia](members.md) -- dátumy vstupu a narodenia.
- [Parcely](parcels.md) -- nájmy a ich dátumy ukončenia.
- [Uchádzači](applicants.md)
- [Pracovné hodiny](work-hours.md) -- oslobodenia, sponzorstvo a prevody
  hodín.
- [Voda a elektrina](metering.md) -- elektromery na parcelách.

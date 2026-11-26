# Protokol e-mailov {#e-mail-log}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Protokol e-mailov uvádza každý e-mail, ktorý sa Parcella pokúsila
odoslať -- pozvánky, upozornenia, oznamy, faktúry, potvrdenia
prihlásení -- a čo odpovedal poštový server. Pozrite sa sem, keď niekto
povie „ten e-mail mi nikdy neprišiel“.

!!! info "Kto to môže používať"
    Len administrátori. Otvorte **Administrácia → Protokol e-mailov**.

![Protokol e-mailov](../assets/screenshots/administration/email-log.png)

## Čítanie protokolu {#reading-the-log}

Hore krátka poznámka vysvetľuje stránku a koľko dní sa záznamy
uchovávajú, s odkazom **Zmeniť** na
[nastavenie](settings.md#email-log).

Karta **Odchádzajúce e-maily** ukazuje počet nájdených záznamov a
tabuľku, najnovšie navrchu, 50 na stránku:

| Stĺpec | Čo ukazuje |
|---|---|
| **Dátum/čas** | Kedy Parcella odovzdala e-mail poštovému serveru, v časovom pásme vášho spolku. |
| **Príjemca** | Adresa, na ktorú odišiel. |
| **Predmet** | Riadok predmetu. Kancelárska spinka znamená, že mal prílohy; podržte nad ňou myš a uvidíte koľko. |
| **Stav** | **Odoslané** alebo **Zlyhalo**. Pod **Zlyhalo** vidíte chybové hlásenie poštového servera. |

Tlačidlá **Novšie** a **Staršie** na konci listujú protokolom
(**Strana ... z ...**).

### Čo znamená „Odoslané“ a „Zlyhalo“ {#what-sent-and-failed-mean}

- **Odoslané** znamená, že váš poštový server e-mail **prijal**.
  Nedokazuje to, že prišiel: ak je schránka plná alebo adresa už
  neexistuje, správa o nedoručení príde do odosielacej schránky vášho
  spolku, nie do tohto protokolu.
- **Zlyhalo** znamená, že ho poštový server hneď odmietol alebo nebol
  dostupný -- napríklad nesprávne heslo, neznámy príjemca alebo vôbec
  nenastavený poštový server.

Ak veľa e-mailov zlyhá s rovnakou chybou, skontrolujte nastavenia
poštového servera v [Nastaveniach spolku](settings.md#email-smtp).

## Vyhľadávanie a filtrovanie {#searching-and-filtering}

| Prvok | Čo robí |
|---|---|
| **Hľadať príjemcu…** | Ukáže len e-maily, ktorých adresa príjemcu obsahuje, čo napíšete. |
| Zoznam stavov | **Všetky stavy**, **Odoslané** alebo **Zlyhalo**. Zmena filtruje okamžite. |
| **Filtrovať** | Použije vyhľadávanie. |
| **Zrušiť filter** | Objaví sa, kým je filter aktívny; znova ukáže všetko. |

**Zatiaľ neboli zaznamenané žiadne e-maily.** sa zobrazí, keď nič
nevyhovuje.

## Ako dlho sa záznamy uchovávajú {#how-long-entries-are-kept}

Adresy príjemcov sú osobné údaje, preto sa záznamy automaticky mažú po
počte dní nastavenom v
[Nastaveniach spolku → Protokol e-mailov](settings.md#email-log) -- 90
dní, ak to nezmeníte. Protokol ukladá len príjemcu, predmet, stav a
chybu a počet príloh -- nie text e-mailu.

## Súvisiace {#related}

- [Nastavenia spolku](settings.md#email-smtp)
- [Používatelia a pozvánky](users.md)

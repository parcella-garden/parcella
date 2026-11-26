# Organizácia pracovnej zmeny {#organising-a-work-session}

!!! note "Strojový preklad"
    Táto stránka bola strojovo preložená z angličtiny a zatiaľ nebola skontrolovaná. Ak je niečo nejasné, platí anglická verzia (jazyk prepnete hore).

Väčšina spolkov žiada, aby každá parcela (alebo každý člen) odpracovala
za rok určitý počet [povinných hodín](../glossary.md#mandatory-hours)
prác pre spoločenstvo -- strihanie živého plota, oprava chodníkov,
jarné upratovanie. Tento návod prevedie jednu [pracovnú
zmenu](../glossary.md#work-session) od plánovania po hodnotenie na
konci roka: vytvorte ju, nechajte členov prihlásiť sa na webe spolku,
zaznamenajte, kto naozaj prišiel, a pozrite sa, kto ešte dlží hodiny.

!!! info "Kto to môže robiť"
    Vytváranie zmien a zaznamenávanie účasti potrebuje oprávnenie
    **zápis** pre **Pracovné sedenia**; odstránenie účastníka alebo
    prevodu potrebuje **mazanie**. Modul (**Správa pracovných hodín**)
    je predvolene zapnutý. Zverejnenie na webe potrebuje administrátora
    na jednorazové nastavenie v kroku 3.

## 1. Nastavte pravidlá roka (raz za rok) {#1-set-the-years-rules-once-a-year}

1. Otvorte **Pracovné sedenia → Sedenia a prehľad**. Ak rok ešte nemá
   pravidlá, stránka hovorí *„Pre … zatiaľ neexistuje konfigurácia
   povinných hodín.“* -- kliknite na **Vytvoriť teraz →** (alebo
   **Konfigurácia hodín** dole).
2. V **Vytvoriť / aktualizovať rok** zadajte:
    - **Rok**;
    - **Celkové povinné hodiny** -- hodiny dlžné za rok;
    - **Hodinová sadzba** -- koľko stojí neodpracovaná hodina;
    - **Fakturačný režim** -- **Na nájom / parcelu** (všetci nájomcovia
      parcely odpracúvajú hodiny spolu) alebo **Na člena** (každý člen
      sám);
    - voliteľne **Poznámka**, napr. uznesenie členskej schôdze.
3. Kliknite na **Uložiť**.

Na tej istej stránke karta **Potvrdzovací e-mail k prihláške** riadi
e-mail, ktorý členovia dostanú po prihlásení na webe (krok 3).

**Oslobodenia.** Členovia výboru, ľudia so zdravotnými dôvodmi alebo
nad určitý vek sú často oslobodení. Nastavíte to v **Sedenia a
prehľad → Roly v spolku**: vytvorte rolu s **Oslobodený od povinných
hodín** a **Dôvod oslobodenia** a potom k nej na daný rok priraďte
členov. Ak je jeden nájomca parcely oslobodený, je oslobodená celá
parcela; oslobodenie platí pre celý kalendárny rok.

## 2. Vytvorte zmenu {#2-create-the-session}

1. Otvorte **Pracovné sedenia → Sedenia a prehľad** a kliknite na
   **Nové sedenie**.
2. Vyplňte:
    - **Názov**, napr. „Jarný upratovací deň“;
    - **Typ**: **Štandard (plánované)** pre zmeny, ktoré ohlasujete,
      alebo **Špeciál (spontánne)** pre neplánované -- špeciálne zmeny
      sa na webe nikdy nezobrazia;
    - **Dátum**, **Od** a **Do**;
    - **Max. účastníkov** -- nechajte prázdne pre neobmedzené;
    - **Uzávierka prihlášok (dní vopred)** -- prihlasovanie na webe sa
      uzavrie toľko dní pred zmenou (1 = deň vopred); prázdne znamená,
      že sa uzavrie, keď zmena uplynie;
    - **Hodiny na účastníka** -- pripíšu sa každému, kto príde, neskôr
      sa dajú upraviť pre každú osobu;
    - **Popis** -- úlohy, náradie, čo si priniesť.
3. Kliknite na **Vytvoriť sedenie**.

Zmena sa zobrazí v **Pracovné sedenia …** svojho roka.

## 3. Zverejnite prihlasovanie na webe spolku (jednorazové nastavenie) {#3-publish-the-sign-up-on-the-club-website-one-time-setup}

Členovia sa prihlasujú na webe spolku svojím **číslom parcely** a
voliteľne menom -- bez prihlásenia do Parcelly. Web nikdy neukazuje,
ktorí členovia sú na ktorej parcele.

Administrátor to nastaví raz:

1. **Administrácia → Nastavenia → Funkčné oblasti**: zaškrtnite
   **Verejné API pre prihlášky** a kliknite na **Uložiť nastavenia**.
   Predvolene je vypnuté, pretože otvára verejný formulár.
2. **Administrácia → Integrácie → Verejné API pre prihlášky**: poznačte
   si **API token** (pre konektor na strane servera) a pridajte svoj web
   do **Povolené adresy webov** (napr. `https://example.org`), potom
   **Uložiť adresy**. Voliteľne zaškrtnite **Vyžadovať ALTCHA** proti
   spamu.
3. Na web pridajte prihlasovací formulár -- pluginom Parcella Connector
   pre WordPress alebo obyčajným formulárom HTML pre akýkoľvek iný web.
   Váš správca webu nájde podrobnosti v dokumentácii pre vývojárov.
   <!-- TODO(verify): link to the gardeners/website-form instructions once that page exists. -->

Odvtedy sa každá nová zmena **Štandard** zobrazí na webe sama, pokiaľ
jej dátum neuplynul, uzávierka prihlášok neuplynula a nie je plná.

**Čo sa stane pri prihlásení.** Parcella vyhľadá súčasných nájomcov
parcely. Ak sa napísané meno zhoduje s presne jedným z nich, prihlási sa
len tento člen. Ak meno nebolo zadané alebo sa jednoznačne nezhoduje,
prihlásia sa **všetci** súčasní nájomcovia parcely, s poznámkou, ktorá
žiada výbor o kontrolu -- odstráňte tých, ktorí sa v skutočnosti
neprihlásili. Každý novo prihlásený člen dostane potvrdzujúci e-mail na
adresu uloženú v Parcelle (nie tú, ktorá bola napísaná vo formulári).

Viac: [Integrácie](../administration/integrations.md) a [Pre
záhradkárov](../gardeners/index.md).

## 4. Sledujte prihlásenia {#4-keep-an-eye-on-sign-ups}

- Nové prihlásenia ukazujú počítadlo vedľa **Pracovné sedenia** v
  bočnom paneli a na dashboarde.
- Otvorte zmenu (kliknite na ňu v zozname v **Sedenia a prehľad**).
  Noví účastníci majú odznak **Nový**. Keď si ich pozriete, kliknite na
  **Označiť ako skontrolované**.
- Skontrolujte stĺpec **Poznámka**: prihlásenia z webu tam majú poznámky
  a kontaktné údaje návštevníka a varovanie, ak bola prihlásená celá
  parcela.
- Ak chcete niekoho pridať ručne (prihlásenie telefonicky), použite
  **Vyberte člena…** na konci tabuľky účastníkov, zvoľte
  **Zaregistrovaný** a kliknite na **Pridať**.

**Úlohy (voliteľné).** Ak vediete zoznam prác v **Pracovné sedenia →
Úlohy**, niektoré tam naplánujte na túto zmenu. Na stránke zmeny potom
môžete každú prideliť účastníkovi (**Pridelené komu**) a vidieť jej
**Náročnosť** (**Ľahká**, **Stredná**, **Náročná**). **Spravovať
úlohy** vedie na celý zoznam.

## 5. V deň zmeny: vytlačte zoznam účastníkov {#5-on-the-day-print-the-attendee-sheet}

1. Otvorte zmenu a kliknite na **Zoznam účastníkov**.
2. Vytlačte PDF. Uvádza každého prihláseného účastníka s parcelou,
   menom, očakávanými hodinami, pridelenou úlohou a riadkom na podpis.

Hodiny podľa potreby opravte na papieri; zadáte ich neskôr. Zoznam v
Parcelle nič nemení.

## 6. Potom: zaznamenajte účasť {#6-afterwards-record-attendance}

1. Otvorte zmenu.
2. Pri každom účastníkovi vyberte v zozname **Stav** **Zúčastnený**
   alebo **Nedostavil sa**. Uloží sa to hneď.
3. Ak niekto pracoval viac alebo menej ako **Hodiny na účastníka**,
   napíšte skutočné hodiny do jeho poľa **Hodiny** a kliknite na
   tlačidlo ✓.
4. Ľudia, ktorí prišli bez prihlásenia: **Vyberte člena…**, stav
   **Zúčastnený**, ich hodiny, **Pridať**.
5. Pole vyhľadávania nad tabuľkou použite na nájdenie niekoho podľa
   mena alebo čísla parcely.

Do hodín sa počítajú len účasti so stavom **Zúčastnený**.

## 7. Sponzorstvá a prevody hodín {#7-sponsorships-and-hours-transfers}

**[Sponzorstvá](../glossary.md#sponsorship)** sú časti areálu, o ktoré
sa člen stará celý rok (živý plot, ihrisko), namiesto účasti na
zmenách alebo navyše k nej.

1. Otvorte **Pracovné sedenia → Sponzorstvá**.
2. V **Vytvoriť sponzorstvo / pridať člena** zadajte **Oblasť**,
   **Člen** (alebo nechajte **– zatiaľ nepriradené –**, ak chcete
   oblasť najprv ponúknuť), **Popis**, **Pripísané hodiny/rok** a
   **Platné od** / **Platné do**.
3. Kliknite na **Uložiť**.

Sponzorstvo pripisuje hodiny, až keď má dátum **Platné od** a člena.
Oblasť môže zdieľať viac členov -- pridajte riadok na každého člena s
rovnakým názvom oblasti; každý dostane plné pripísanie.

**[Prevody hodín](../glossary.md#hours-transfer)**: člen, ktorý
odpracoval viac, ako sa vyžadovalo, môže hodiny dať niekomu inému.

1. Otvorte **Pracovné sedenia → Prevody hodín**.
2. V **Previesť hodiny** vyberte **Od (odovzdáva)**, **Komu
   (prijíma)**, **Hodiny** a voliteľne **Poznámka**.
3. Kliknite na **Previesť hodiny**.

Dať sa dá len prebytok odovzdávajúceho za daný rok. Členovia bez
parcely a oslobodení členovia môžu dať všetky svoje hodiny.

## 8. Hodnotenie na konci roka {#8-the-year-end-evaluation}

1. Otvorte **Pracovné sedenia → Ročné hodnotenie** a vyberte rok.
2. Každý riadok je parcela (alebo člen, podľa **Fakturačný režim**) s
   **Požadované**, **Sedenia**, **Sponzorstvo**, **Prevedené**,
   **Celkom**, **Otvorené** a **Dlh** a **Stav** **Splnené**,
   **Otvorené** alebo **Oslobodený**.
3. Kliknite na šípku na začiatku riadku (**Zobraziť pracovné
   sedenia**) a uvidíte, z ktorých zmien hodiny pochádzajú.
4. **CSV export** stiahne hodnotenie.

Nájomcovia, ktorí počas roka odišli, stále dlžia hodiny za tento rok;
ich riadok má odznak „nájom ukončený …“.

Ak chcete vyúčtovať otvorené hodiny, pridajte do ročného vyúčtovania
položku **Nedoplatok pracovných hodín (z modulu)** -- pozri [Ročné
vyúčtovanie](annual-invoicing.md).

## Súvisiace {#related}

- [Pracovné hodiny](../modules/work-hours.md)
- [Kalendár](../modules/calendar.md)
- [Integrácie](../administration/integrations.md)
- [Ročné vyúčtovanie](annual-invoicing.md)
- Slovník: [povinné hodiny](../glossary.md#mandatory-hours),
  [oslobodenie](../glossary.md#exemption),
  [sponzorstvo](../glossary.md#sponsorship),
  [prevod hodín](../glossary.md#hours-transfer)

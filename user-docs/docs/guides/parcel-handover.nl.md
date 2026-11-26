# Een perceel overdragen {#handing-over-a-parcel}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Een huurder zegt op, het perceel wordt geïnspecteerd en getaxeerd, aan de
wachtlijst aangeboden, en ten slotte tekent een nieuwe huurder en krijgt
de sleutels. Dat duurt weken of maanden en er zijn meerdere bestuursleden
bij betrokken. Dit stappenplan toont wat Parcella onderweg vastlegt en
hoe een [proces](../glossary.md#process) de stappen bijhoudt die het niet
vanzelf vastlegt.

## Wat Parcella wel -- en niet -- bijhoudt {#what-parcella-does-and-doesnt-track}

| Deel van de overdracht | In Parcella |
|---|---|
| De opzegging | Perceelstatus **beëindigd**, met de datum automatisch vastgelegd en een optionele **Beëindigingsnotitie**. |
| Oude en nieuwe huurders | De oude [huur](../glossary.md#tenancy) beëindigen bewaart haar als geschiedenis; de nieuwe huur begint op de overdrachtsdatum. **Perceel toewijzen** bij een aanmelding doet beide in één stap. |
| Het lidmaatschap van de oude huurder | Eindigt automatisch met **Perceel toewijzen** als hij geen ander perceel huurt. |
| Documentenmap | De cloudmap van de oude huurders wordt op de overdrachtsdatum buiten gebruik gesteld; een nieuwe neemt over. |
| Inspectie, [taxatie](../glossary.md#valuation), aanbod, bezichtiging, contract, sleutels | Niet ingebouwd. Houd ze bij met een **proces** (stap 1). |
| [Borg](../glossary.md#deposit) | Geen borgfunctie. Noteer bedrag en datum in het proces; leg het geld vast in **Financiën** als u die gebruikt (stap 7). |
| Eindstanden van meters | Parcella bewaart **één stand per meter per jaar**. Noteer overdrachtsstanden in het proces (stap 6). |
| Prijs tussen oude en nieuwe huurder | **Bewust niet bijgehouden.** Wat de nieuwe huurder de oude betaalt voor tuinhuis en beplanting is een privézaak tussen die twee. Parcella heeft er geen veld voor -- voeg er ook geen toe aan uw processjabloon. |

!!! info "Wie kan dit doen"
    Wijzigingen aan perceel en huur vragen **schrijven** op **Leden en
    percelen**; **Perceel toewijzen** vraagt ook **schrijven** op
    **Aanmelders**. Processjablonen vragen volledige toegang (bestuur of
    beheerder); werken aan een proces vraagt **schrijven** op
    **Processen**.

## 1. Een processjabloon voor de overdracht voorbereiden (één keer) {#1-prepare-a-handover-process-template-once}

De module **Processen** heeft een voorbeeldsjabloon **Overdracht van een
tuin**. Begin daarmee en pas het aan de volgorde van uw vereniging aan.

1. Open **Processen → Sjablonen** (de pagina heet **Processjablonen**).
2. Klik onder **Beginnen met een voorbeeld** op **Gebruiken** naast
   **Overdracht van een tuin**. Parcella maakt een gewoon sjabloon dat u
   vrij kunt aanpassen. Het gaat over een **Tuin**, dus elk proces hoort
   bij één perceel en verschijnt op de pagina van dat perceel.
3. Het voorbeeld heeft zes fasen: **Inspectie**, **Taxatie**,
   **Advertentie**, **Nieuwe huurder**, **Contract en borg** en
   **Overdracht**. Om de gebruikelijke volgorde hieronder te volgen,
   voegt u in de editor fasen toe en hernoemt u ze (typ een naam in
   **Nieuwe fase, bijv. ‘Inspectie’** en klik op **Toevoegen**; sleep
   fasen om ze te ordenen; voeg velden toe door een naam te typen en op
   Enter te drukken):

| Fase | Voorbeeldvelden | Veldsoort |
|---|---|---|
| Opzegging *(nieuw, eerste)* | Opzegging ontvangen op (verplicht) · Opzeggingsbrief | Datum · Bestanden (PDF, foto's) |
| **Inspectie** | **Datum van de inspectie** · **Gevonden gebreken** · **Foto's van de gebreken** · **Alle gebreken verholpen** | uit het voorbeeld |
| **Taxatie** | **Taxateur** · **Datum van de taxatie** · **Taxatierapport** | uit het voorbeeld |
| **Advertentie** → hernoemen naar „Aanbod aan de wachtlijst“ | **Advertentietekst** · **Gepubliceerd op** | uit het voorbeeld |
| Bezichtiging *(nieuw)* | Datum bezichtiging · Geïnteresseerde aanmelders (notities) | Datum · Lange tekst |
| **Nieuwe huurder** | **Nieuwe huurder** (een aanmelder) · **Contact gelegd** · **Documenten verstuurd** | uit het voorbeeld |
| **Contract en borg** | **Koopovereenkomst bevestigd** · **Borg** · **Borg ontvangen op** | uit het voorbeeld |
| **Overdracht** → splitsen in „Ondertekening“ en „Eindcontrole“ | Ondertekening: **Ondertekend door de nieuwe huurder**, **Medeondertekend door het bestuur**. Eindcontrole: **Sleutels overhandigd**, **Meters afgelezen**, **Overdrachtsprotocol** | uit het voorbeeld |

4. Voeg in de fase „Eindcontrole“ velden van het soort **Getal** toe voor
   de meterstanden bij de overdracht, bijv. „Stand watermeter bij
   overdracht“ en „Stand elektriciteitsmeter bij overdracht“ (zie stap
   6).

Markeer een veld als **Verplicht** als het proces zonder dat veld niet
verder mag. Wijzigingen aan een sjabloon gelden alleen voor processen die
daarna worden gestart.

!!! tip
    **Koopovereenkomst bevestigd** is alleen een vinkje: het bestuur
    bevestigt dat oude en nieuwe huurder het eens zijn geworden. De prijs
    zelf blijft tussen hen beiden.

Meer: [Processen](../modules/processes.md).

## 2. De opzegging vastleggen {#2-record-the-notice}

Komt de opzegging van de huurder binnen:

1. Open het perceel onder **Percelen** en klik op **Bewerken**.
2. Zet **Status** op **beëindigd**. Parcella legt het tijdstip van de
   statuswijziging vast; de perceelpagina toont dan **Beëindigd op**.
3. Voeg eventueel een **Beëindigingsnotitie** toe (reden,
   opzeggingsdatum, opmerkingen).
4. Klik op **Wijzigingen opslaan**.

De huurder blijft huidige huurder -- en blijft de facturen van het
perceel krijgen -- tot de huur echt eindigt. Beëindig de huur nu niet;
**Perceel toewijzen** doet dat op de overdrachtsdatum (stap 5).

## 3. Het proces starten {#3-start-the-process}

1. Klik op de pagina van het perceel, in de kaart **Processen**, op
   **Proces starten**.
2. Kies uw overdrachts**sjabloon**. Geef het proces eventueel een
   **Titel**.
3. Klik op **Starten**.
4. Vul de velden van de eerste fase in en klik op **Opslaan**. Is de fase
   compleet, klik dan op **Klaar -- volgende fase**.

Het proces verschijnt op de perceelpagina met zijn huidige fase, en in
**Processen** voor iedereen die eraan werkt. Bestanden die u uploadt
(brieven, foto's, het taxatierapport) gaan naar de cloudmap van het
perceel als die is ingesteld, anders naar de eigen opslag van Parcella.

Om terug te gaan naar een eerdere fase, klikt u op **Teruggaan**, kiest u
de fase en geeft u een **Reden**. Gaat de overdracht niet door, gebruik
dan **Proces afbreken** met een reden.

## 4. Inspectie, taxatie, aanbod, bezichtiging {#4-inspection-valuation-offer-viewing}

Werk deze fasen in het proces af zoals ze gebeuren. Het
[taxatie](../glossary.md#valuation)rapport gaat in **Taxatierapport**; de
tekst van het aanbod in **Advertentietekst**.

Om geïnteresseerden te vinden, opent u **Aanmelders** met het filter
**Open** -- de lijst is gesorteerd op aanmeldingsdatum. Zet wie u het
perceel aanbiedt op **Tuin aangeboden**, en wie het neemt op
**Geaccepteerd**. Staat de module **Mededelingen** aan, vink dan meerdere
aanmelders aan en klik op **Schrijf naar de geselecteerde aanvragers**
om het aanbod per e-mail te versturen.

Meer: [Aanmelders](../modules/applicants.md).

## 5. Het perceel aan de nieuwe huurder overdragen {#5-hand-the-parcel-over-to-the-new-tenant}

Zodra het contract is getekend -- of met een latere datum, zodra die
vaststaat:

1. Open de aanmelding van de nieuwe huurder en klik op **Perceel
   toewijzen**.
2. Kies dit perceel onder **Beëindigd perceel** en stel de
   **Overdrachtsdatum** in.
3. Voeg een partner toe onder **Verdere kandidaten (medepachters)** als
   die het perceel samen overneemt.
4. Gebruikt u cloudopslag, vul dan de **Documentenmap voor de nieuwe
   pachters** in. De map van de oude huurders wordt op de
   overdrachtsdatum hoe dan ook buiten gebruik gesteld.
5. Klik op **Voorbeeld**, controleer de oude en nieuwe huurders, klik dan
   op **Perceel overdragen** en bevestig.

Op de overdrachtsdatum:

- eindigt de oude huur en verschuift ze naar **Voormalige huurders** op
  de perceelpagina;
- verlaat een oude huurder zonder ander perceel de vereniging (**Lid
  tot** is de dag vóór de overdrachtsdatum);
- worden de aanmelders lid, huurder en factuurontvanger;
- is het perceel weer **actief**.

Zie [Een nieuw lid verwelkomen](new-member.md), stap 5 en 6, voor de
details en voor het aanvullen van de gegevens van het nieuwe lid.

### Als de nieuwe huurder geen aanmelder is {#if-the-new-tenant-isnt-an-applicant}

Bijvoorbeeld een familielid dat overneemt. Doe het met de hand:

1. Klik op de perceelpagina, in **Huidige huurders**, op het
   potloodpictogram naast de oude huurder (**Huur bewerken**), zet
   **Huurder tot** op de laatste dag en klik op **Wijzigingen opslaan**.
   Of, om de huur vandaag te beëindigen, klik op het pictogram **Huur
   beëindigen** en bevestig *„Beëindig deze huur? (geschiedenis blijft
   behouden)“*.
2. Verlaat de oude huurder de vereniging, open dan zijn ledenpagina,
   klik op **Bewerken**, vul **Lid tot** in en klik op **Wijzigingen
   opslaan**. Verwijder hem niet -- zie de waarschuwing hieronder.
3. Wijs de nieuwe huurder toe: **Kies lid…**, de begindatum,
   **Gebruiken als factuuradres**, **Toewijzen**. Maak hem zo nodig eerst
   aan onder **Leden → Nieuw lid**.
4. Bewerk het perceel en zet **Status** terug op **actief**.

!!! tip "Een opzegging vastleggen"
    Een huurder die heeft opgezegd, blijft het factuuradres tot hij
    vertrekt: vul zijn **Huurder tot** in bij **Huur bewerken** en laat
    **Gebruiken als factuuradres** aangevinkt. Is die dag voorbij, dan
    wordt het vakje vanzelf uitgevinkt -- zorg dat de nieuwe huurder tegen
    die tijd het factuuradres is.

!!! warning "Beëindigen, niet verwijderen"
    Een huur of lidmaatschap beëindigen bewaart de geschiedenis: wie welk
    perceel wanneer huurde, en welke uren en facturen bij wie hoorden.
    Een lid verwijderen haalt hem uit elke evaluatie, ook uit de werkuren
    van jaren waarin hij huurder was.

## 6. Eindstanden van de meters {#6-final-meter-readings}

Parcella bewaart één stand per meter en jaar, en dat is de stand waarop
de jaarfactuur is gebaseerd. Er is geen aparte „overdrachtsstand“.

- Noteer de standen op de dag van de overdracht in het proces (de fase
  „Eindcontrole“ uit stap 1) en vink **Meters afgelezen** aan.
- Voer ze niet als stand van het jaar bij het meetpunt in, tenzij u dat
  echt wilt: de jaarstand later in het jaar **vervangt** haar.
- De jaarlijkse water- en elektriciteitsfactuur van het perceel gaat naar
  wie factuurontvanger is als de
  [factuurronde](../glossary.md#invoice-run) wordt afgerond -- na een
  overdracht de nieuwe huurder -- voor het verbruik van het hele jaar.
  Hoe oude en nieuwe huurder dat verdelen, is aan hen en de regels van
  uw vereniging; regel het buiten Parcella, met de standen in het
  proces.

Wordt bij de overdracht een meter gewisseld, zie dan
[Meterstanden opnemen](meter-readings.md#a-meter-is-replaced).

## 7. Borg en geld {#7-deposit-and-money}

Parcella heeft geen borgveld bij het perceel of het lid. Gebruik het
proces voor de administratie: **Borg** (bedrag) en **Borg ontvangen op**
in de fase **Contract en borg**.

Gebruikt u de module **Financiën**, leg dan ook het geld zelf vast:

- **Ontvangen borg**: open **Financiën → Overzicht → Rekeningen**, klik
  op het boekingenpictogram naast de rekening waarop het geld binnenkwam,
  en gebruik **Boeking toevoegen** (of **CSV importeren** met uw
  bankafschrift).
- **De borg van de oude huurder terugbetalen**: hetzelfde, als negatief
  bedrag.

<!-- TODO(verify): confirm with the treasurer whether a deposit should rather be billed as a one-off invoice run (a "Fixed amount per parcel" item scoped to this parcel) so it gets an invoice number. -->

**Werkuren.** Een huurder die in de loop van het jaar vertrekt, is de
[verplichte uren](../glossary.md#mandatory-hours) van dat jaar nog steeds
verschuldigd. Bij facturatie per perceel tellen zijn uren samen met die
van de nieuwe huurder, en een tekort wordt gefactureerd aan wie op het
moment van de factuurronde factuurontvanger van het perceel is -- de
nieuwe huurder. Wil uw vereniging dat niet, regel het dan met de hand.
Zie [De jaarfacturen opmaken](annual-invoicing.md).

**Open facturen** van de oude huurder blijven zoals ze zijn; het
factuurnummer, de ontvanger en het adres blijven bij elke factuur
bewaard, zodat u nog steeds kunt innen en herinneren.

## 8. Het proces afsluiten {#8-close-the-process}

Is de laatste fase klaar, klik dan op **Proces afronden**. Een afgerond
proces is alleen-lezen en blijft op de perceelpagina staan, met zijn
volledige **Geschiedenis**.

## Gerelateerd {#related}

- [Percelen](../modules/parcels.md)
- [Aanmelders](../modules/applicants.md)
- [Leden](../modules/members.md)
- [Processen](../modules/processes.md)
- [Water en elektriciteit](../modules/metering.md)
- [Bankrekeningen en boekingen](../modules/finances/bank-accounts.md)
- [Een nieuw lid verwelkomen](new-member.md)
- Woordenlijst: [borg](../glossary.md#deposit),
  [taxatie](../glossary.md#valuation),
  [opzegging](../glossary.md#notice-of-termination),
  [huur](../glossary.md#tenancy)

# Aankoopaanvragen {#purchase-requests}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Aankoopaanvragen zorgen ervoor dat er geen geld van de vereniging wordt
uitgegeven zonder overeenstemming: voordat iemand iets voor de
vereniging koopt, dient hij een aanvraag in, en **twee verschillende
bestuursleden** moeten die goedkeuren. Eén bestuurslid kan haar in zijn
eentje tegenhouden. Iedereen die erbij betrokken is, kan de aanvraag
direct op haar pagina bespreken.

!!! info "Wie kan dit gebruiken"
    - **Aanvragen zien en reageren:** iedereen wiens groep **Lezen** voor
      **Aankoopaanvragen** geeft (zie [Groepen](../administration/groups.md)).
    - **Aanvragen aanmaken en de leverancier wijzigen:** **Schrijven**
      voor **Aankoopaanvragen**.
    - **Goedkeuren of afwijzen:** alleen bestuursleden en beheerders, of
      gebruikers in een groep met volledige toegang. Een gewoon
      **Schrijven**-recht is niet genoeg.

    De module wordt ingeschakeld met **Aankoopaanvragen** onder
    [Modules in- en uitschakelen](../administration/modules.md). Ze staat
    standaard aan.

Het navigatie-item **Aankoopaanvragen** toont een rode badge met het
aantal open aanvragen -- hetzelfde getal als de dashboardtegel. Het telt
elke open aanvraag, ook die u al hebt goedgekeurd en die op een tweede
goedkeuring wachten.

## Het vier-ogenprincipe {#the-two-person-approval-principle}

Deze regels gelden altijd, wie de app ook gebruikt:

1. Een aanvraag is **Open** wanneer ze wordt aangemaakt.
2. Ze wordt **Goedgekeurd** zodra **twee verschillende** bestuursleden op
   **Goedkeuren** hebben geklikt. Elk bestuurslid kan een aanvraag maar
   één keer goedkeuren.
3. **Noch de aanvrager, noch wie de aanvraag invoerde** mag haar
   goedkeuren. Dat is van belang als een bestuurslid een aanvraag namens
   iemand anders invoert: hij telt dan als de kant van de aanvrager en
   kan zelf geen van de twee goedkeuringen geven.
4. **Eén afwijzing is genoeg.** Elk bestuurslid kan een open aanvraag
   afwijzen, met een reden. De aanvrager kan zijn eigen aanvraag ook
   afwijzen -- bijvoorbeeld om haar in te trekken.
5. Is een aanvraag eenmaal **Goedgekeurd** of **Afgewezen**, dan is dat
   definitief. Er zijn geen goedkeuringen of afwijzingen meer mogelijk,
   en heropenen kan niet.

!!! note
    Goedkeuringen en afwijzingen versturen geen e-mails. Alleen nieuwe
    reacties doen dat (zie [Discussie](#discussion)).

## Overzicht {#overview}

![Overzicht aankoopaanvragen](../assets/screenshots/purchase-requests/list.png)

**Aankoopaanvragen** toont de aanvragen, de nieuwste eerst.

| Veld / knop | Wat het doet |
|---|---|
| **Nieuwe aankoopaanvraag** | Opent het [formulier](#new-purchase-request). Alleen zichtbaar met schrijfrecht. |
| **Open** / **Goedgekeurd** / **Afgewezen** / **Alles** | Toont alleen aanvragen met die status, of allemaal. **Open** is gekozen als u op de pagina komt. |
| **Titel** | Wat er gekocht moet worden; linkt naar de aanvraag. |
| **Aanvrager** | De naam van de aanvrager. Bij een aanvraag namens iemand anders de ingetypte naam (of het e-mailadres als er geen naam is opgegeven). |
| **Geschatte kosten** | De geschatte kosten, of „–“ als er niets is ingevuld. |
| **Goedkeuringen** | Bij open aanvragen hoeveel van de twee vereiste goedkeuringen er zijn, bijv. **1 / 2**. „–“ bij afgesloten aanvragen. |
| **Status** | **Open**, **Goedgekeurd** of **Afgewezen**. |
| Oogknop | Opent de aanvraag. |

## Nieuwe aankoopaanvraag {#new-purchase-request}

![Nieuwe aankoopaanvraag](../assets/screenshots/purchase-requests/form.png)

Klik op **Nieuwe aankoopaanvraag** in het overzicht.

### Aankoopaanvraag {#purchase-request}

| Veld | Wat het doet |
|---|---|
| **Wat moet er gekocht worden?** | De titel van de aanvraag. Verplicht. |
| **Motivering** | Waarom de vereniging het nodig heeft. Verplicht. |
| **Link naar waar het gekocht kan worden** | Optioneel webadres van een winkel of aanbieding. Moet een volledig adres zijn dat begint met `http://` of `https://`. |
| **Leverancier (contact)** | Optionele leverancier uit [Externe contacten](external-contacts.md). Bedrijven staan er met hun personen eronder. Alleen zichtbaar als de module Externe contacten aan staat en u contacten mag lezen. |
| **Geschatte kosten** | Optioneel. Accepteert een komma of een punt als decimaalteken. Laat leeg als de prijs nog niet bekend is. Kan Parcella de waarde niet als getal lezen, dan wordt de aanvraag zonder kosten opgeslagen. |

### Aanvrager {#requester}

| Veld | Wat het doet |
|---|---|
| **Aanmaken namens een andere persoon (die geen eigen account heeft)** | Vink dit aan als u een aanvraag voor iemand anders invoert, bijv. een lid dat het u telefonisch vroeg. Toont de twee velden hieronder. Laat u het uit, dan bent u de aanvrager. |
| **Naam van de persoon** | De naam van de aanvrager. |
| **E-mailadres** | Het e-mailadres van de aanvrager. Die krijgt een link om de gegevens te bevestigen (zie [Bevestiging door de aanvrager](#confirmation-by-the-requester)). |

Klik op **Aankoopaanvraag aanmaken** om op te slaan, of op **Annuleren**
om terug te gaan. Na het opslaan opent de pagina van de aanvraag.

!!! note "Zonder e-mailadres"
    U kunt het **E-mailadres** leeg laten: de aanvraag wordt opgeslagen
    met de ingetypte naam als aanvrager, alleen zonder
    bevestigingsmail. Vinkt u het vakje aan maar laat u naam en adres
    allebei leeg, dan telt de aanvraag als *uw eigen*. Hoe dan ook kunt u
    een aanvraag die u zelf invoerde niet goedkeuren.

## Pagina van een aanvraag {#request-page}

![Aankoopaanvraag](../assets/screenshots/purchase-requests/detail.png)

Een aanvraag openen toont de gegevens, de discussie en de goedkeuringen.
**Terug** brengt u naar het overzicht.

### Details {#details}

| Veld | Wat het toont |
|---|---|
| **Aanvrager** | Wie om de aankoop vroeg. Bij een aanvraag namens iemand anders ook het e-mailadres en een badge: **Bevestiging in afwachting** of **Bevestigd door aanvrager**. |
| **Aangemaakt door** | Wie de aanvraag invoerde, en wanneer. |
| **Motivering** | De opgegeven reden. |
| **Link** | De winkellink, als die is ingevuld. Opent in een nieuw tabblad. |
| **Leverancier (contact)** | Het gekoppelde externe contact, of „–“. Met schrijfrecht kunt u een ander contact kiezen (of **— geen —**) en op **Opslaan** klikken -- in elke status, omdat de leverancier geen deel van de goedkeuring is. Een contact dat intussen is verwijderd, wordt met „(verwijderd)“ getoond. |
| **Geschatte kosten** | Alleen getoond als er kosten zijn ingevuld. |

Onder de gegevens toont een afgesloten aanvraag een balk:

- **Goedgekeurd** -- met datum en tijd van de tweede goedkeuring.
- **Afgewezen** -- met wie haar afwees, wanneer, en de reden.

### Discussie {#discussion}

De kaart **Discussie ({aantal})** toont alle reacties, de oudste eerst,
met auteur en tijd. Iedereen die de aanvraag kan zien, kan reageren, in
elke status -- juist bij een afgewezen aanvraag wil iemand vaak iets
uitleggen.

| Veld / knop | Wat het doet |
|---|---|
| Reactieveld | Uw vraag of opmerking, maximaal 5.000 tekens. Een lege reactie wordt geweigerd. |
| **Reageren** | Voegt de reactie toe en mailt haar. |

Reacties kunnen achteraf niet worden bewerkt of verwijderd.

Elke nieuwe reactie wordt gemaild naar:

- de aanvrager -- het adres van zijn account, of, bij een aanvraag
  namens iemand anders, het daar opgegeven e-mailadres;
- elke actieve gebruiker die eerder op de aanvraag heeft gereageerd of
  haar heeft goedgekeurd.

De auteur van de reactie krijgt geen e-mail, en niemand krijgt dezelfde
reactie twee keer. Gebruikers krijgen een knop die de aanvraag opent,
zodat ze in Parcella kunnen antwoorden. Een aanvrager zonder account kan
niet in Parcella antwoorden; zijn e-mail vraagt hem contact op te nemen
met het bestuur.

### Goedkeuringen ({aantal}/2) {#approvals-count2}

Toont elke goedkeuring met de naam van het bestuurslid en de datum en
tijd. **Nog geen goedkeuringen.** als er geen zijn.

Zolang de aanvraag **Open** is, zien bestuursleden ook:

| Knop / melding | Wat het doet |
|---|---|
| **Goedkeuren** | Legt uw goedkeuring vast. De tweede goedkeuring door een ander bestuurslid zet de aanvraag op **Goedgekeurd**. |
| „Als aanvrager kunt u uw eigen aankoopaanvraag niet goedkeuren …“ | Getoond in plaats van **Goedkeuren** als u de aanvrager bent of de aanvraag invoerde. |
| „U heeft dit al goedgekeurd.“ | Getoond in plaats van **Goedkeuren** nadat u hebt goedgekeurd. |
| **Afwijzen** | Opent een veld voor de reden van afwijzing. |
| **Definitief afwijzen** | Wijst de aanvraag af met de reden die u invulde (verplicht). De aanvraag is meteen afgesloten. |

## Bevestiging door de aanvrager {#confirmation-by-the-requester}

Maakt u een aanvraag namens iemand aan met een e-mailadres, dan stuurt
Parcella die persoon een e-mail „Gelieve te bevestigen: aankoopverzoek
"{titel}"“. Die noemt u als degene die de aanvraag invoerde, herhaalt
titel en motivering en bevat een knop **Gegevens bevestigen**.

De bevestiging is **alleen ter informatie**. Ze laat het bestuur zien dat
de persoon de aanvraag echt zo bedoelde. Ze is *niet* nodig voor de
goedkeuring: bestuursleden kunnen goedkeuren of afwijzen, of de
aanvrager nu heeft bevestigd of niet. Heeft de aanvrager een eigen
account en maakt hij de aanvraag zelf aan, dan is er helemaal geen
bevestigingsstap.

### Aankoopaanvraag bevestigen {#confirm-purchase-request}

De link in de e-mail opent een pagina die **zonder inloggen** werkt. Ze
toont **Titel**, **Motivering**, **Link** (als die er is) en **Geschatte
kosten** (als die er zijn) van de aanvraag, met de uitleg dat de
aanvraag namens de persoon is ingevoerd.

| Knop / melding | Wat het doet |
|---|---|
| **Gegevens bevestigen** | Legt de bevestiging vast. Op de pagina van de aanvraag verandert de badge van **Bevestiging in afwachting** in **Bevestigd door aanvrager**. |
| „U heeft deze gegevens al bevestigd.“ | Getoond in plaats van de knop als de link al eerder is gebruikt. De link opnieuw openen kan geen kwaad. |

Na het bevestigen ziet de persoon een pagina **Dank u!** die zegt dat
de bevestiging voor de aanvraag is opgeslagen.
<!-- Screenshots of the confirm and thank-you pages are not generated: the sample data contains no request with a confirmation link. -->

### Link niet gevonden {#link-not-found}

![Link niet gevonden](../assets/screenshots/purchase-requests/confirmation-invalid.png)

De pagina **Link niet gevonden** verschijnt als de link fout of
onvolledig is, of als de aanvraag **meer dan 30 dagen geleden** is
aangemaakt -- bevestigingslinks werken na 30 dagen niet meer. De
aanvrager neemt dan rechtstreeks contact op met het bestuur; het bestuur
kan nog steeds over de aanvraag beslissen.

!!! note
    De paginatekst zegt dat de link „ongeldig is of al is gebruikt“. Een
    al gebruikte link werkt binnen de 30 dagen nog steeds -- hij toont
    „U heeft deze gegevens al bevestigd.“

## Gerelateerd {#related}

- [Externe contacten](external-contacts.md) -- leveranciers die u aan
  een aanvraag kunt koppelen; de pagina van een contact toont zijn
  aankoopaanvragen
- [Inkomende facturen](finances/incoming-invoices.md) -- de factuur
  vastleggen nadat de goedgekeurde aankoop is gedaan
- [Dashboard](../getting-started/dashboard.md) -- de tegel met open
  aankoopaanvragen
- [Rollen, groepen en rechten](../getting-started/roles-and-permissions.md)

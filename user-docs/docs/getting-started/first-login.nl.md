# Eerste aanmelding en uw account {#first-login-and-your-account}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Deze pagina gaat over alles rond uw eigen account: hoe u er een krijgt,
hoe u inlogt en hoe u uw wachtwoord en afbeelding wijzigt.

!!! info "Wie kan dit gebruiken"
    Iedereen met een Parcella-account. Er is geen openbare registratie:
    een account bestaat pas nadat een beheerder u heeft uitgenodigd.

## Een account krijgen: de uitnodiging {#getting-an-account-the-invitation}

Een beheerder van uw installatie nodigt u per e-mail uit (zie
[Gebruikers en uitnodigingen](../administration/users.md)). U ontvangt
een e-mail met het onderwerp **Uitnodiging voor Parcella** en een knop
**Uitnodiging accepteren**. De link daarin is **7 dagen** geldig.

!!! tip "Geen e-mail ontvangen?"
    Kijk eerst in uw spammap. Staat hij daar niet, vraag de beheerder dan
    het [E-maillogboek](../administration/email-log.md) te controleren en
    zo nodig de uitnodiging opnieuw te versturen. Opnieuw versturen geeft
    de link nog eens 7 dagen; de link in de eerste e-mail blijft werken.

### Uitnodiging accepteren {#accept-invitation}

<!-- TODO(verify): no screenshot of "Set up your account" -- it needs a valid invitation link, which the screenshot tool can't produce from the sample data. -->

Met de link opent u de pagina **Stel uw account in**. Onder de kop ziet
u het adres waarnaar de uitnodiging is gestuurd (**Uitnodiging voor**
...). Dat adres wordt uw inlognaam; u kunt het hier niet wijzigen.

| Veld / knop | Wat het doet |
|---|---|
| **Naam** | Uw voor- en achternaam. Andere bestuursleden zien die in lijsten, bij taken, goedkeuringen en in de wijzigingsgeschiedenis. |
| **Wachtwoord** | Minstens 8 tekens. |
| **Bevestig wachtwoord** | Typ hetzelfde wachtwoord nog eens. Komen ze niet overeen, dan ziet u **Wachtwoorden komen niet overeen.** |
| **Account aanmaken** | Maakt uw account aan en logt u meteen in. U komt op het [Dashboard](dashboard.md). |

Wat u daarna ziet, hangt af van de groepen die de beheerder bij het
uitnodigen heeft gekozen. Koos hij er geen, dan kunt u alleen leden en
percelen opzoeken -- vraag dan of u aan een groep wordt toegevoegd. Zie
[Rollen, groepen en rechten](roles-and-permissions.md).

### Uitnodiging verlopen {#invitation-expired}

![Uitnodiging verlopen](../assets/screenshots/getting-started/invitation-expired.png)

U ziet **Uitnodiging verlopen** -- *Deze uitnodigingslink is niet langer
geldig of is al gebruikt.* -- wanneer:

- er meer dan 7 dagen zijn verstreken sinds de uitnodiging is verstuurd
  (of voor het laatst opnieuw verstuurd),
- u met deze link al uw account hebt aangemaakt, of
- de beheerder de uitnodiging heeft verwijderd of hetzelfde adres
  opnieuw heeft uitgenodigd (alleen de nieuwste uitnodiging werkt).

Vraag een beheerder u opnieuw uit te nodigen. **Terug naar inloggen**
brengt u naar de inlogpagina, wat alleen helpt als u al een account
hebt.

## Inloggen {#signing-in}

![Inlogpagina](../assets/screenshots/getting-started/login.png)

Open het Parcella-adres van uw vereniging in een webbrowser. De
inlogpagina toont het logo en de naam van uw vereniging (beide ingesteld
door een beheerder onder [Verenigingsinstellingen](../administration/settings.md)).

| Veld / knop | Wat het doet |
|---|---|
| **E-mail** | Het adres waarnaar uw uitnodiging is gestuurd. Hoofdletters en kleine letters maken niet uit. |
| **Wachtwoord** | Uw wachtwoord. |
| **Inloggen** | Logt u in en opent het [Dashboard](dashboard.md). |

De meldingen die u kunt zien:

| Melding | Betekenis |
|---|---|
| **E-mail of wachtwoord is onjuist.** | Een van beide klopt niet. Voor uw bescherming zegt Parcella niet welke. |
| **Uw account is gedeactiveerd.** | Een beheerder heeft uw account uitgeschakeld. Uw gegevens zijn er nog; vraag om het weer te activeren. |
| **Te veel mislukte inlogpogingen. Wacht een paar minuten en probeer het opnieuw.** | Na herhaalde verkeerde wachtwoorden pauzeert Parcella de inlogpogingen voor dit account ongeveer 15 minuten. |

U blijft **8 uur** ingelogd (tenzij degene die uw installatie host dat
heeft gewijzigd). Daarna vraagt Parcella u opnieuw in te loggen, ook als
u al die tijd hebt gewerkt.

Om uit te loggen klikt u op **Uitloggen** onderaan de zijbalk. Doe dat
op elke gedeelde of openbare computer.

!!! note "Wachtwoord vergeten?"
    Er is bewust geen link „wachtwoord vergeten“. Vraag een beheerder:
    die kan uw wachtwoord resetten en u een tijdelijk wachtwoord geven
    (zie [Gebruikers en uitnodigingen](../administration/users.md#reset-password)).
    Bij de volgende keer inloggen moet u dan een nieuw wachtwoord
    kiezen.

## De allereerste aanmelding na de installatie {#the-very-first-login-after-installation}

Wanneer Parcella voor het eerst start, maakt het zelf één
beheerdersaccount aan:

- **E-mail:** `admin@parcella.local`
- **Wachtwoord:** `admin1234`

Deze gegevens staan in de installatie-instructies van Parcella en zijn
op elke nieuwe installatie gelijk, dus iedereen zou ze kunnen
gebruiken. Daarom is dit account vergrendeld tot het wachtwoord is
gewijzigd: na het inloggen komt u direct op **Wachtwoord wijzigen**,
met de melding

> Dit account gebruikt nog het standaardwachtwoord van de eerste
> installatie. Kies een nieuw wachtwoord -- tot die tijd blijft de rest
> van de applicatie vergrendeld.

Elke andere pagina stuurt u hierheen terug tot u een nieuw wachtwoord
hebt opgeslagen.

!!! warning "Doe dit vóór al het andere"
    Wijzig het wachtwoord meteen, ook op een testinstallatie die vanaf
    internet bereikbaar is. Wijzig daarna onder
    [Gebruikers en uitnodigingen](../administration/users.md) de naam en
    het e-mailadres van het account naar die van een echte persoon, of
    nodig de echte beheerders uit en werk met hun eigen accounts.

Dezelfde gedwongen wijziging volgt nadat een beheerder uw wachtwoord
heeft gereset: het tijdelijke wachtwoord brengt u alleen naar de pagina
**Wachtwoord wijzigen**.

## Wachtwoord wijzigen {#change-password}

![Wachtwoord wijzigen](../assets/screenshots/getting-started/change-password.png)

Open deze pagina met **Wachtwoord wijzigen** onderaan de zijbalk. De
pagina is uw persoonlijke profiel: er staan ook uw avatar en een link
naar uw API-tokens.

### Avatar {#avatar}

Uw avatar is de kleine ronde afbeelding naast uw naam in de zijbalk, in
gebruikerslijsten en bij taken. Zonder avatar toont Parcella een
eenvoudig persoonspictogram.

| Veld / knop | Wat het doet |
|---|---|
| Bestandsveld | Kies een afbeelding: PNG, JPEG of WebP, maximaal 2 MB. |
| **Uploaden** | Slaat de afbeelding op. U ziet **Avatar succesvol geüpload.** Een verkeerd bestandstype of een te groot bestand wordt met een melding geweigerd. |
| **Avatar verwijderen** | Alleen zichtbaar als u er een hebt. Verwijdert hem weer. |

### API-tokens voor integraties {#api-tokens-for-integrations}

**Beheren** opent **Mijn API-tokens**. U hebt dit alleen nodig als u een
ander programma (bijvoorbeeld een AI-assistent) met Parcella wilt
verbinden. Zie [API-tokens](../administration/api-tokens.md).

### Het wachtwoord wijzigen {#changing-the-password}

| Veld / knop | Wat het doet |
|---|---|
| **Huidig wachtwoord** | Uw huidige wachtwoord, zodat niemand het kan wijzigen op een computer waarop u ingelogd bleef. |
| **Nieuw wachtwoord** | Minstens 8 tekens, en anders dan het huidige. |
| **Bevestig nieuw wachtwoord** | Het nieuwe wachtwoord nog eens. |
| **Wachtwoord wijzigen** | Slaat het nieuwe wachtwoord op. U ziet **Wachtwoord succesvol gewijzigd.** |

Mogelijke fouten: **Huidig wachtwoord is onjuist.**, **Wachtwoorden
komen niet overeen.**, **Wachtwoord moet minimaal 8 tekens bevatten.** en
**Het nieuwe wachtwoord moet verschillen van het huidige.**

Wat er gebeurt als u opslaat:

- In deze browser blijft u ingelogd.
- **Overal waar u verder ingelogd was, wordt u uitgelogd** -- een
  andere computer, uw telefoon of een browser die iemand anders met uw
  account gebruikt. Gebruik dit als u vermoedt dat iemand uw wachtwoord
  kent.
- Al uw **API-tokens werken niet meer** (ze staan als **beëindigd**).
  Maak nieuwe aan als u ze nog nodig hebt.

## Taal {#language}

Parcella toont iedereen in uw vereniging dezelfde taal. Er is geen
taalkeuze per gebruiker. Een beheerder kiest de taal onder
[Verenigingsinstellingen](../administration/settings.md#language) --
English, Deutsch, Polski, Čeština, Slovenčina, Français of Nederlands.
De inlogpagina en de uitnodigingspagina's gebruiken die taal ook.

Notatie van getallen, datums en valuta is een aparte instelling
(**Regio** en **Valuta**), zodat een vereniging bijvoorbeeld Engelse
menu's kan gebruiken met Duitse getalnotatie.

## Gerelateerd {#related}

- [Uw weg vinden](navigation.md)
- [Rollen, groepen en rechten](roles-and-permissions.md)
- [Gebruikers en uitnodigingen](../administration/users.md) -- voor beheerders

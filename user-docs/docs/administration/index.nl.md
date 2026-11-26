# Administratie {#administration}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

In de administratie wordt uw Parcella-installatie ingericht en
onderhouden: wie mag inloggen, wat ze mogen doen, de stamgegevens van de
vereniging, koppelingen met andere diensten en back-ups.

!!! info "Wie kan dit gebruiken"
    Alleen **beheerders**: accounts met de oudere rol **Beheerder** of
    in een groep met **Toegang tot het administratiepaneel**.
    Bestuursleden met volledige toegang tot de modules zien het niet,
    tenzij ze ook beheerder zijn. Zie
    [Rollen, groepen en rechten](../getting-started/roles-and-permissions.md).

U vindt het onderaan de zijbalk onder **Administratie**.

## De pagina's {#the-pages}

| Item in de zijbalk | Pagina | Wat u daar doet |
|---|---|---|
| **Systeem** | [Systeeminformatie en updates](system.md) | Uw versie zien en of er een update is; een back-up downloaden. |
| | [Back-up en herstel](backup.md) | Herstellen vanuit een back-up; automatische back-ups naar de cloud plannen. |
| **Gebruikers** | [Gebruikers en uitnodigingen](users.md) | Mensen uitnodigen, accounts bewerken, deactiveren en verwijderen, wachtwoorden resetten. |
| **Groepen** | [Groepen](groups.md) | Bepalen wie wat mag lezen, schrijven en verwijderen. |
| **API-tokens** | [API-tokens](api-tokens.md) | De tokens van iedereen bekijken en intrekken; tokens maken voor integratieaccounts. |
| **Instellingen** | [Verenigingsinstellingen](settings.md) | Naam en adres van de vereniging, logo, taal, regio en valuta, e-mailserver, financiële gegevens, volgorde van de navigatie en meer. |
| | [Modules in- en uitschakelen](modules.md) | De kaart **Functiegebieden** op de instellingenpagina. |
| **Integraties** | [Integraties](integrations.md) | Websiteformulieren, websiteconcepten, cloudopslag, helpdesk, Nextcloud Deck, links voor agendafeeds. |
| **E-maillogboek** | [E-maillogboek](email-log.md) | Controleren of een e-mail is verstuurd. |
| **Voorbeeldgegevens** | [Voorbeeldgegevens](sample-data.md) | Een nieuwe installatie vullen met demogegevens om dingen uit te proberen, en ze weer verwijderen. |
| **API-documentatie (Swagger)** | -- | De technische beschrijving van de programmeerinterface, voor ontwikkelaars. |

## Een nieuwe installatie inrichten {#setting-up-a-new-installation}

Een verstandige volgorde voor een gloednieuwe installatie:

1. Log in met het ingebouwde beheerdersaccount en wijzig het wachtwoord
   -- zie [Eerste aanmelding](../getting-started/first-login.md#the-very-first-login-after-installation).
2. Onder [Verenigingsinstellingen](settings.md): taal, regio en valuta,
   verenigingsgegevens, logo en de e-mailserver (zonder die kan
   Parcella geen uitnodigingen versturen).
3. Onder [Modules in- en uitschakelen](modules.md): schakel uit wat u
   niet nodig hebt en in wat u wel nodig hebt.
4. Maak [groepen](groups.md) voor de taken in uw vereniging.
5. [Nodig](users.md) de andere bestuursleden in die groepen uit.
6. Richt [back-ups](backup.md) in.

Het stappenplan [Een nieuwe vereniging inrichten](../guides/new-club-setup.md)
loopt dit samen met het invoeren van leden en percelen door.

Hoe Parcella zelf wordt geïnstalleerd (de server, Docker, het webadres)
staat in de
[ontwikkelaarsdocumentatie](https://github.com/parcella-garden/parcella#install-self-hosting).

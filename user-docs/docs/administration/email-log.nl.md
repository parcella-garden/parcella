# E-maillogboek {#e-mail-log}

!!! note "Machinevertaling"
    Deze pagina is machinaal vertaald uit het Engels en nog niet nagekeken. Als iets onduidelijk is, geldt de Engelse versie (taal wisselt u bovenaan).

Het e-maillogboek toont elke e-mail die Parcella heeft geprobeerd te
versturen -- uitnodigingen, meldingen, mededelingen, facturen,
aanmeldbevestigingen -- en wat de mailserver antwoordde. Kijk hier als
iemand zegt „die e-mail heb ik nooit gekregen“.

!!! info "Wie kan dit gebruiken"
    Alleen beheerders. Open **Administratie → E-maillogboek**.

![E-maillogboek](../assets/screenshots/administration/email-log.png)

## Het logboek lezen {#reading-the-log}

Bovenaan legt een korte notitie de pagina uit en hoeveel dagen regels
worden bewaard, met een link **Wijzigen** naar de
[instelling](settings.md#email-log).

De kaart **Uitgaande e-mails** toont het aantal gevonden regels en een
tabel, de nieuwste eerst, 50 per pagina:

| Kolom | Wat ze toont |
|---|---|
| **Datum/tijd** | Wanneer Parcella de e-mail aan de mailserver gaf, in de tijdzone van uw vereniging. |
| **Ontvanger** | Het adres waar hij heen ging. |
| **Onderwerp** | De onderwerpregel. Een paperclip betekent dat er bijlagen waren; beweeg de muis erover om te zien hoeveel. |
| **Status** | **Verzonden** of **Mislukt**. Onder **Mislukt** ziet u de foutmelding van de mailserver. |

**Nieuwer** en **Ouder** onderaan bladeren door het logboek (**Pagina
... van ...**).

### Wat „Verzonden“ en „Mislukt“ betekenen {#what-sent-and-failed-mean}

- **Verzonden** betekent dat uw mailserver de e-mail heeft
  **aangenomen**. Het bewijst niet dat hij is aangekomen: is de mailbox
  vol of bestaat het adres niet meer, dan gaat het foutbericht naar de
  verzendmailbox van uw vereniging, niet in dit logboek.
- **Mislukt** betekent dat de mailserver hem meteen weigerde of niet
  bereikbaar was -- bijvoorbeeld een verkeerd wachtwoord, een onbekende
  ontvanger, of helemaal geen mailserver ingericht.

Mislukken veel e-mails met dezelfde fout, controleer dan de
instellingen van de mailserver onder
[Verenigingsinstellingen](settings.md#email-smtp).

## Zoeken en filteren {#searching-and-filtering}

| Element | Wat het doet |
|---|---|
| **Ontvanger zoeken…** | Toont alleen e-mails waarvan het adres van de ontvanger bevat wat u typt. |
| Statuslijst | **Alle statussen**, **Verzonden** of **Mislukt**. Een wijziging filtert meteen. |
| **Filteren** | Past de zoekopdracht toe. |
| **Herstellen** | Verschijnt zolang er een filter actief is; toont weer alles. |

**Nog geen e-mails gelogd.** verschijnt als niets past.

## Hoe lang regels worden bewaard {#how-long-entries-are-kept}

Adressen van ontvangers zijn persoonsgegevens, dus regels worden
automatisch verwijderd na het aantal dagen dat is ingesteld onder
[Verenigingsinstellingen → E-maillogboek](settings.md#email-log) -- 90
dagen, tenzij u dat wijzigt. Het logboek bewaart alleen ontvanger,
onderwerp, status en fout en het aantal bijlagen -- niet de tekst van de
e-mail.

## Gerelateerd {#related}

- [Verenigingsinstellingen](settings.md#email-smtp)
- [Gebruikers en uitnodigingen](users.md)

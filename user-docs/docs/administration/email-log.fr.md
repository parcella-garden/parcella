# Journal des e-mails {#e-mail-log}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Le journal des e-mails liste chaque e-mail que Parcella a tenté
d'envoyer -- invitations, notifications, annonces, factures,
confirmations d'inscription -- et la réponse du serveur de messagerie.
Regardez ici quand quelqu'un dit « je n'ai jamais reçu cet e-mail ».

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Journal des e-mails**.

![Journal des e-mails](../assets/screenshots/administration/email-log.png)

## Lire le journal {#reading-the-log}

En haut, une courte note explique la page et le nombre de jours pendant
lesquels les entrées sont conservées, avec un lien **Modifier** vers le
[paramètre](settings.md#email-log).

La carte **E-mails sortants** affiche le nombre d'entrées trouvées et un
tableau, les plus récentes en premier, 50 par page :

| Colonne | Ce qu'elle affiche |
|---|---|
| **Date/heure** | Le moment où Parcella a remis l'e-mail au serveur de messagerie, dans le fuseau horaire de votre association. |
| **Destinataire** | L'adresse à laquelle il a été envoyé. |
| **Objet** | La ligne d'objet. Un trombone signifie qu'il avait des pièces jointes ; survolez-le pour voir combien. |
| **Statut** | **Envoyé** ou **Échec**. Sous **Échec**, vous voyez le message d'erreur du serveur de messagerie. |

**Plus récents** et **Plus anciens** en bas permettent de feuilleter le
journal (**Page ... sur ...**).

### Ce que signifient « Envoyé » et « Échec » {#what-sent-and-failed-mean}

- **Envoyé** signifie que votre serveur de messagerie a **accepté**
  l'e-mail. Cela ne prouve pas qu'il est arrivé : si la boîte est pleine
  ou si l'adresse n'existe plus, le message de non-remise arrive dans la
  boîte d'envoi de votre association, pas dans ce journal.
- **Échec** signifie que le serveur de messagerie l'a refusé
  immédiatement ou n'a pas pu être joint -- par exemple un mauvais mot de
  passe, un destinataire inconnu, ou aucun serveur de messagerie
  configuré.

Si de nombreux e-mails échouent avec la même erreur, vérifiez les
paramètres du serveur de messagerie dans les
[Paramètres de l'association](settings.md#email-smtp).

## Rechercher et filtrer {#searching-and-filtering}

| Élément | Ce qu'il fait |
|---|---|
| **Rechercher un destinataire…** | N'affiche que les e-mails dont l'adresse du destinataire contient ce que vous tapez. |
| Liste des statuts | **Tous les statuts**, **Envoyé** ou **Échec**. Le changement filtre immédiatement. |
| **Filtrer** | Applique la recherche. |
| **Réinitialiser** | Apparaît tant qu'un filtre est actif ; réaffiche tout. |

**Aucun e-mail enregistré pour l'instant.** apparaît quand rien ne
correspond.

## Durée de conservation des entrées {#how-long-entries-are-kept}

Les adresses des destinataires sont des données personnelles : les
entrées sont donc supprimées automatiquement après le nombre de jours
défini sous
[Paramètres de l'association → Journal des e-mails](settings.md#email-log)
-- 90 jours sauf si vous le modifiez. Le journal ne conserve que le
destinataire, l'objet, le statut, l'erreur et le nombre de pièces
jointes -- pas le texte de l'e-mail.

## Voir aussi {#related}

- [Paramètres de l'association](settings.md#email-smtp)
- [Utilisateurs et invitations](users.md)

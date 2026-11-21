# Paramètres de l'association {#club-settings}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

La page des paramètres contient les données de base de votre association
et les réglages qui s'appliquent à toute l'installation : langue, logo,
serveur e-mail, données financières et plus.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Paramètres**.

![Paramètres de l'association](../assets/screenshots/administration/settings.png)

## Fonctionnement de la page {#how-the-page-works}

La page est une colonne de cartes. Chaque carte est repliée ; cliquez
sur son titre pour l'ouvrir. Ouvrir une carte replie les autres.

| Élément | Ce qu'il fait |
|---|---|
| **Rechercher dans les paramètres...** | Tapez un mot, par exemple « logo » ou « IBAN ». Les cartes qui le contiennent s'ouvrent et le mot est mis en évidence ; toutes les autres cartes sont masquées. Si rien ne correspond, vous voyez **Aucun paramètre ne correspond à votre recherche.** |
| **Enregistrer les paramètres** | En haut et en bas de la page. Enregistre **toutes les cartes d'un coup**, quelle que soit celle que vous avez modifiée. Vous voyez **Paramètres enregistrés.** |

!!! warning "Un seul bouton d'enregistrement pour tout"
    Les modifications ne sont stockées que lorsque vous cliquez sur
    **Enregistrer les paramètres**. Si vous quittez la page avant, elles
    sont perdues.

Les cartes, de haut en bas :

## Langue {#language}

La langue de toute l'installation : menus, boutons, messages, page de
connexion, ainsi que les e-mails et PDF produits par Parcella. Tout le
monde voit la même langue ; il n'y a pas de réglage de langue personnel.

Choisissez entre **Deutsch**, **English**, **Polski**, **Čeština**,
**Slovenčina**, **Français** et **Nederlands**. Une nouvelle installation
démarre en anglais.

Quand un texte n'a pas encore été traduit dans la langue choisie,
Parcella affiche le texte anglais à la place.

La langue ne change pas l'apparence des nombres, des dates et des
montants -- c'est le rôle de la carte **Région**.

## Image de marque {#branding}

| Champ | Ce qu'il fait |
|---|---|
| **Logo du club** | Affiche votre logo actuel (ou l'icône Parcella). Choisissez un nouveau fichier -- PNG, JPEG, WebP ou SVG, 2 Mo au maximum -- pour le remplacer. Le logo apparaît sur la page de connexion, en haut de la barre latérale et dans l'en-tête des PDF générés. |
| **Supprimer le logo (revenir à l'icône par défaut)** | Affiché seulement si un logo est téléversé. Cochez-le et enregistrez pour revenir à l'icône Parcella. |

Un mauvais type de fichier ou un fichier trop volumineux est refusé avec
un message ; le reste de la page est quand même enregistré.

## Région et devise {#region-currency}

| Champ | Ce qu'il fait |
|---|---|
| **Région** | La façon d'écrire les nombres et les adresses -- séparateur de milliers, virgule ou point décimal, code postal avant ou après la ville. Détermine aussi le fuseau horaire des flux de calendrier. Choix : Allemagne, Royaume-Uni, France, Pays-Bas, Pologne, République tchèque, Slovaquie. Par défaut : Allemagne. |
| **Devise** | Le symbole monétaire et sa position (« 19,99 € » ou « £19.99 »). Choix : euro (€), livre sterling (£), złoty polonais (zł), couronne tchèque (Kč). Par défaut : euro. |

Les deux sont indépendants de la langue : une association néerlandophone
peut utiliser des menus en néerlandais avec des montants en euros, une
installation en anglais peut utiliser les formats de nombre allemands.

## Domaines fonctionnels {#feature-areas}

Les interrupteurs qui activent et désactivent les modules. Décrits en
détail dans [Activer et désactiver les modules](modules.md).

## Ordre de navigation {#navigation-order}

Détermine l'ordre des entrées dans la barre latérale de tout le monde.
Chaque entrée a un champ numérique : **Tableau de bord**, **Membres**,
**Parcelles**, **Assistance**, **Demandes d'achat**, **Sessions de
travail**, **Eau**, **Électricité**, **Assurance**, **Calendrier**,
**Annonces**, **Inventaire**, **Tableau des tâches**, **Finances**,
**Candidats**, **Contacts externes**, **Rapports**, **Notes**,
**Procédures**.

Les plus petits nombres viennent en premier. Au départ, les nombres sont
100, 200, 300 ... dans l'ordre ci-dessus : vous pouvez donc placer une
entrée entre deux autres en lui donnant, par exemple, 150. Les champs
vides reprennent le nombre par défaut ; tout ce qui n'est pas un nombre
entier est ignoré.

**Administration** ne figure pas dans la liste : elle est toujours en
dernier.

## Mises à jour {#updates}

| Champ | Ce qu'il fait |
|---|---|
| **Vérifier automatiquement les mises à jour** | Activé par défaut. Parcella demande alors à GitHub toutes les quelques heures si une nouvelle version est sortie, et affiche un avis sur la page [Système](system.md). Rien concernant votre association n'est transmis. Désactivez-le si votre serveur ne doit pas contacter internet ; la page Système n'affiche alors plus aucune information de mise à jour. |

## Candidats {#applicants}

Utile seulement si vous utilisez le module
[Candidats](../modules/applicants.md).

| Champ | Ce qu'il fait |
|---|---|
| **Supprimer les candidatures après (mois)** | Toute candidature dont le statut n'a pas changé depuis ce nombre de mois est **définitivement supprimée**, quel que soit son statut, sans prévenir personne. Compté à partir du dernier changement de statut, ou de la date de candidature si le statut n'a jamais changé. Laissez vide ou saisissez 0 pour conserver les candidatures jusqu'à ce que vous les supprimiez à la main. Utile pour la protection des données. |
| **Texte de l'e-mail aux nouveaux candidats** | Le texte utilisé par **Contacter le candidat** sur une nouvelle candidature ; il peut encore être modifié avant chaque envoi. `{name}` devient le nom du candidat, `{club}` le nom de l'association. Laissez vide pour utiliser le texte intégré, affiché en gris. |

## Journal des e-mails {#email-log}

| Champ | Ce qu'il fait |
|---|---|
| **Conserver les entrées du journal des e-mails (jours)** | Durée pendant laquelle le [Journal des e-mails](email-log.md) conserve ses entrées. Les plus anciennes sont supprimées automatiquement car les adresses des destinataires sont des données personnelles. 90 jours par défaut, de 1 à 3650 possibles. |

## Données du club {#club-data}

| Champ | Utilisé pour |
|---|---|
| **Nom du club** | Affiché en haut de la barre latérale, sur la page de connexion et sur les documents imprimés. Vide : « Parcella ». |
| **Rue**, **Code postal**, **Ville** | L'adresse de l'association dans le pied de page des PDF générés (factures, avis, listes). |
| **Numéro d'enregistrement du club**, **Registre du commerce** | Également imprimés dans le pied de page des PDF, car les associations enregistrées en Allemagne doivent les indiquer. |

## Membres du bureau {#board-members}

Les membres qui font actuellement partie du bureau. Leurs noms sont
imprimés dans le pied de page des documents générés.

| Élément | Ce qu'il fait |
|---|---|
| **Membres du bureau** / **Afficher la liste** | Déplie la liste de tous les membres actuels, chacun avec une case à cocher. **Masquer la liste** la replie. |
| **Rechercher…** | Restreint la liste aux noms correspondants. **Aucun résultat** si aucun ne correspond. |
| **Tout sélectionner** / **Tout désélectionner** | Coche ou décoche tous les membres visibles. |

Un membre qui quitte l'association disparaît automatiquement de la
liste imprimée.

## Superficies (m²) {#areas-sqm}

Le terrain de l'association, réparti comme les associations de jardins
familiaux allemandes le déclarent habituellement.

| Champ | Ce qu'il fait |
|---|---|
| **Superficie totale (m²)** | L'ensemble du site de l'association. À saisir vous-même. |
| **Superficie A (parcelles, m²)** | Calculée, non modifiable : la somme des superficies de toutes les parcelles, louées ou résiliées. Les parcelles supprimées et les espaces communs ne comptent pas. Même chiffre que **Superficie totale (m²)** sur le [Tableau de bord](../getting-started/dashboard.md). |
| **Superficie B (communale, m²)** | Calculée : superficie totale moins superficie A moins superficie C. |
| **Superficie C (municipale, m²)** | À saisir vous-même. |

Ces chiffres sont utilisés quand une [série de factures](../modules/finances/invoice-runs.md)
répartit des coûts selon la part de chaque parcelle dans la superficie
commune.

## Paramètres financiers {#finance-settings}

Utilisés par le module [Finances](../modules/finances/index.md).

| Champ | Ce qu'il fait |
|---|---|
| **Nom de la banque**, **IBAN**, **BIC**, **Titulaire du compte** | Imprimés en pied de page de chaque facture, pour que les membres sachent où payer. |
| **Prochain numéro de facture (remplacer)** | Généralement vide : les numéros continuent simplement. Saisissez un nombre pour que la toute prochaine série de factures -- quelle que soit l'année -- commence à ce numéro. Parcella vérifie seulement que le numéro n'est pas déjà pris au moment de la finalisation de cette série. Le champ se vide de lui-même une fois utilisé. |
| **Format du numéro de facture** | L'apparence des numéros de facture. `{number}` est obligatoire, `{year}` facultatif ; tout autre texte est repris tel quel, par ex. `R-{year}-{number}`. Sous le champ, vous voyez **Actuellement utilisé :** avec un exemple ; **(par défaut, rien de personnalisé enregistré)** signifie que le format par défaut `{year}/{number}` s'applique. Le champ propose quelques exemples. |

Le format ne concerne que les factures créées à partir de maintenant.
Les numéros déjà attribués ne changent jamais. Un format invalide n'est
pas enregistré ; vous voyez **Format de numéro de facture invalide -- il
doit contenir {number} exactement une fois (et éventuellement {year}),
aucun autre paramètre.**

## E-mail (SMTP) {#email-smtp}

Chaque e-mail envoyé par Parcella -- invitations, notifications,
annonces, factures -- passe par ce serveur de messagerie. Parcella ne
lit aucune boîte aux lettres.

| Champ | Ce qu'il fait |
|---|---|
| **Serveur SMTP** | L'adresse du serveur de messagerie, fournie par votre fournisseur e-mail. |
| **Port SMTP** | Généralement 587 (ou ce qu'indique votre fournisseur). |
| **Utilisateur SMTP** | L'identifiant du serveur de messagerie, souvent l'adresse e-mail. |
| **Mot de passe SMTP** | Affiché comme **Pas encore défini** ou **•••••••• (défini -- ressaisir pour modifier)**. Laissez-le vide pour conserver le mot de passe enregistré ; tapez-en un nouveau pour le remplacer. Stocké chiffré. |
| **E-mail de l'expéditeur** | L'adresse d'où partent les e-mails. |

!!! tip "Vérifiez que cela fonctionne"
    Après l'enregistrement, invitez-vous avec une seconde adresse ou
    envoyez un e-mail quelconque, puis regardez le
    [Journal des e-mails](email-log.md). **Échec** avec une erreur vous
    indique ce qui n'a pas plu au serveur de messagerie.

Si ces champs sont vides, Parcella utilise les paramètres e-mail que la
personne qui l'a installé a éventuellement placés dans la configuration
du serveur.

Parcella chiffre la connexion au serveur de messagerie avec STARTTLS, la
méthode normalement utilisée sur le port 587. Il n'y a pas
d'interrupteur pour cela sur la page des paramètres ; cela ne peut être
modifié que dans la configuration du serveur.
<!-- TODO(verify): whether mail servers that only offer implicit TLS on port 465 work at all. -->

## Voir aussi {#related}

- [Activer et désactiver les modules](modules.md)
- [Intégrations](integrations.md)
- [Configurer une nouvelle association](../guides/new-club-setup.md)

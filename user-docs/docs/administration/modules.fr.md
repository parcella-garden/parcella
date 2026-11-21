# Activer et désactiver les modules {#turning-modules-on-and-off}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Toutes les associations n'utilisent pas toutes les parties de Parcella.
Une association sans réseau d'eau propre n'a pas besoin de relevés de
compteurs ; une association qui n'exige pas d'heures de travail n'a pas
besoin de sessions de travail. C'est vous qui décidez quels modules
votre association utilise.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Paramètres** et
    dépliez la carte **Domaines fonctionnels**.

Chaque module a un interrupteur, son nom et une courte description.
Basculez les interrupteurs que vous voulez changer et cliquez sur
**Enregistrer les paramètres**.

## Ce qui se passe quand vous désactivez un module {#what-happens-when-you-switch-a-module-off}

- Il **disparaît de la barre latérale et du tableau de bord** pour tout
  le monde, administrateurs compris. (Exception : la tuile
  *Anniversaires cette semaine* reste sur le tableau de bord même si le
  calendrier est désactivé.)
- Ses pages ne peuvent plus être ouvertes, même depuis un favori.
- **Rien n'est supprimé.** Toutes ses données restent dans la base de
  données et reviennent, inchangées, dès que vous réactivez le module.
- Les droits des groupes pour le module restent tels quels : les mêmes
  personnes y ont de nouveau accès après sa réactivation.

Activer un module le rend immédiatement visible pour toutes les personnes
ayant un accès complet. Les autres ne le voient dans la barre latérale
qu'une fois qu'un groupe leur accorde la **Lecture** dessus -- voir
[Groupes](groups.md).

## Les interrupteurs {#the-switches}

Ils apparaissent sur la carte dans cet ordre.

| Interrupteur | Ce qu'il fait | Activé par défaut |
|---|---|---|
| **Gestion des heures de travail** | Sessions de travail, parrainages, fonctions dans l'association et rapport annuel des heures de travail. Voir [Heures de travail](../modules/work-hours.md). | Oui |
| **Gestion de l'eau** | Compteurs d'eau, relevés et rapports de consommation. Voir [Eau et électricité](../modules/metering.md). | Oui |
| **Gestion de l'électricité** | Compteurs d'électricité, relevés et rapports de consommation. | Oui |
| **Gestion des assurances** | Assurance de biens et assurance accidents par parcelle, avec rapport annuel. Voir [Assurances](../modules/insurance.md). | Oui |
| **Assistance (helpdesk)** | Relie les conversations de votre helpdesk aux membres et au tableau des tâches. Choisissez d'abord le helpdesk sous [Intégrations](integrations.md#support-helpdesk). Voir [Assistance](../modules/support.md). | Non |
| **Demandes d'achat** | Dépenses de l'association avec approbation par deux personnes. Voir [Demandes d'achat](../modules/purchase-requests.md). | Oui |
| **Calendrier** | Calendrier communautaire, anniversaires, présence et absence du bureau, chacun avec un flux de calendrier. Voir [Calendrier](../modules/calendar.md). | Oui |
| **Inventaire** | Tout ce que possède l'association, avec catégories et prêts. Voir [Inventaire](../modules/inventory.md). | Oui |
| **Tableau des tâches** | Un tableau À faire / En cours / Terminé pour les affaires de l'association. Réservé aux utilisateurs à accès complet (bureau, administrateurs et groupes à accès complet). Voir [Tableau des tâches](../modules/tasks.md). | Oui |
| **Candidats** | Les personnes qui ont demandé une parcelle libre. Voir [Candidats](../modules/applicants.md). | Oui |
| **Contacts externes** | Fournisseurs, artisans, administrations. Voir [Contacts externes](../modules/external-contacts.md). | Oui |
| **Rapports** | Les chiffres de l'association au fil du temps sous forme de graphiques, en lecture seule. Voir [Rapports](../modules/reporting.md). | Oui |
| **Notes** | Notes avec catégories et étiquettes, éventuellement stockées sous forme de fichiers dans le cloud. Voir [Notes](../modules/notes.md). | Oui |
| **Procédures** | Vos propres procédures pas à pas. Voir [Procédures](../modules/processes.md). | Oui |
| **Connecteur MCP pour clients IA** | Permet à un assistant IA (Claude, ChatGPT, ...) de rechercher, lire et écrire **uniquement les notes que vous avez libérées pour l'IA**, rien d'autre. Nécessite un [jeton API](api-tokens.md) du type **Connecteur MCP uniquement**. | Non |
| **API publique d'inscription** | Permet au formulaire du site web de l'association d'inscrire des jardiniers aux sessions de travail sans connexion. Voir [Intégrations](integrations.md#public-signup-api) et [Pour les jardiniers](../gardeners/index.md). | Non |
| **API publique de formulaire de contact** | Permet au formulaire de contact du site web de créer une nouvelle demande dans votre helpdesk au lieu d'envoyer un e-mail. | Non |
| **API publique du formulaire de candidature** | Permet au formulaire de candidature à une parcelle du site web de créer directement des candidats. Le module **Candidats** peut être utilisé sans lui, pour des candidatures saisies à la main. | Non |
| **Annonces** | Rédiger une fois les nouvelles de l'association et les préparer pour le site web, l'e-mail aux membres et un avis imprimable. Voir [Annonces](../modules/announcements.md). | Non |
| **Stockage cloud** | Un dossier cloud par parcelle pour les contrats de bail et les documents ; nécessaire aussi pour les pièces jointes des factures reçues, les documents des contacts, les fichiers de notes et les sauvegardes cloud. Choisissez d'abord le stockage sous [Intégrations](integrations.md#cloud-storage). | Non |
| **Finances** | Factures annuelles par parcelle, paiements et comptabilité. Remplissez d'abord les [paramètres financiers](settings.md#finance-settings). Voir [Finances](../modules/finances/index.md). | Non |
| **Synchronisation Nextcloud Deck** | Copie les cartes d'un tableau Nextcloud Deck sur le tableau des tâches, tenues à jour automatiquement. Configurez d'abord la connexion sous [Intégrations](integrations.md#nextcloud-deck). | Non |

**Membres** et **Parcelles** n'ont pas d'interrupteur : ils sont le cœur
de Parcella et toujours actifs.

## Pourquoi certains interrupteurs sont désactivés au départ {#why-some-switches-start-off}

Les interrupteurs désactivés sur une nouvelle installation font l'une de
ces choses :

- **Ils ouvrent une porte sur l'internet public.** Les trois
  interrupteurs *API publique ...* permettent à n'importe quel visiteur
  de votre site web d'envoyer des données dans Parcella. N'en activez un
  que si votre site web a vraiment le formulaire correspondant, et
  seulement celui dont vous avez besoin.
- **Ils stockent des mots de passe d'autres services**, ou permettent à
  Parcella d'y agir : stockage cloud, helpdesk, Nextcloud Deck, la
  connexion au site web des annonces.
- **Ils manipulent de l'argent ou touchent tous les membres à la fois :**
  finances et annonces.
- **Ils transmettent des données à une entreprise externe :** le
  connecteur MCP donne à un service d'IA l'accès aux notes que vous
  libérez.

Rien ne casse si vous les laissez désactivés. Activez-les délibérément,
une fois que vous savez que vous en avez besoin.

## Voir aussi {#related}

- [Modules](../modules/index.md) -- ce que fait chaque module
- [Groupes](groups.md) -- qui peut utiliser un module activé
- [Intégrations](integrations.md) -- connexions dont plusieurs modules ont besoin

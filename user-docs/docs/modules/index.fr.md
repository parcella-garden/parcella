# Modules {#modules}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Parcella se compose de modules : un par domaine d'activité de
l'association. Votre association n'active que ceux dont elle a besoin ;
les autres disparaissent de la navigation pour tout le monde. Désactiver
un module ne supprime jamais ses données -- réactivez-le et tout est de
retour.

Un administrateur active et désactive les modules sous
[Activer et désactiver les modules](../administration/modules.md). Qui
peut utiliser un module activé se règle avec les
[groupes](../administration/groups.md).

## Vue d'ensemble {#overview}

| Module | À quoi il sert | Activé après l'installation ? |
|---|---|---|
| [Membres](members.md) | Toutes les personnes qui font partie de l'association : coordonnées, dates d'adhésion, rôles, historique. | Toujours |
| [Parcelles](parcels.md) | Les parcelles de jardin, leurs baux et leurs locataires, passés et actuels. | Toujours |
| [Candidats](applicants.md) | Les personnes qui ont demandé une parcelle libre, leur statut et les notes du bureau. | Oui |
| [Heures de travail](work-hours.md) | Sessions de travail, inscriptions et présences, parrainages, transferts d'heures et évaluation annuelle des heures dues. | Oui |
| [Eau et électricité](metering.md) | Compteurs, relevés et rapports de consommation. L'eau et l'électricité s'activent séparément. | Oui |
| [Assurances](insurance.md) | Assurance de biens et assurance accidents par parcelle et par année, avec un rapport annuel. | Oui |
| [Finances](finances/index.md) | Factures annuelles par parcelle, paiements, relances, comptes bancaires, factures reçues et comptabilité. | Non |
| [Demandes d'achat](purchase-requests.md) | Dépenses de l'association approuvées par deux membres du bureau avant que l'argent soit dépensé. | Oui |
| [Calendrier](calendar.md) | Calendrier communautaire, anniversaires, présence et absence du bureau, vos propres calendriers -- chacun aussi sous forme de flux de calendrier auquel s'abonner. | Oui |
| [Annonces](announcements.md) | Rédiger une fois les nouvelles de l'association et les envoyer sur le site web, par e-mail et sous forme d'avis imprimable. | Non |
| [Tableau des tâches](tasks.md) | Un tableau À faire / En cours / Terminé pour les affaires de l'association. Réservé au bureau et aux administrateurs. | Oui |
| [Inventaire](inventory.md) | Tout ce que possède l'association (et les objets des membres gardés sur le terrain de l'association), avec les prêts. | Oui |
| [Notes](notes.md) | Procès-verbaux de réunion et autres notes, avec catégories et étiquettes, éventuellement conservées sous forme de fichiers dans le cloud. | Oui |
| [Procédures](processes.md) | Vos propres procédures pas à pas, comme la transmission d'une parcelle, menées pour une parcelle, un membre ou un candidat. | Oui |
| [Contacts externes](external-contacts.md) | Fournisseurs, artisans et administrations, liés aux factures et aux demandes d'achat. | Oui |
| [Assistance](support.md) | Les conversations du helpdesk de votre association, liées aux membres, aux parcelles et aux tâches. | Non |
| [Rapports](reporting.md) | Les chiffres de l'association au fil des années sous forme de graphiques. En lecture seule. | Oui |

## Pourquoi certains modules sont désactivés au départ {#why-some-modules-start-switched-off}

Les modules désactivés après l'installation font chacun quelque chose
qu'une association doit décider en connaissance de cause :

- **Finances** gère l'argent des membres et envoie des factures en masse.
- **Annonces** peut envoyer un e-mail à chaque membre et publier sur
  votre site web.
- **Assistance** se connecte à un helpdesk externe et a besoin de ses
  identifiants d'accès.

Il en va de même pour les extensions de la liste des modules qui n'ont
pas de chapitre propre : **Stockage cloud**, **Synchronisation Nextcloud
Deck**, **Connecteur MCP pour clients IA**, et les trois formulaires
publics du site web (**API publique d'inscription**, **API publique de
formulaire de contact**, **API publique du formulaire de candidature**).
Ils stockent soit des mots de passe de services externes, soit ouvrent
un formulaire sur l'internet public. Voir
[Activer et désactiver les modules](../administration/modules.md) et
[Intégrations](../administration/integrations.md).

## Voir aussi {#related}

- [Rôles, groupes et droits](../getting-started/roles-and-permissions.md)
- [S'orienter dans l'application](../getting-started/navigation.md)

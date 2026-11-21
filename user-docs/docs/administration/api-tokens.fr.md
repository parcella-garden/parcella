# Jetons API {#api-tokens}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Un jeton API est une clé qui permet à un autre programme d'utiliser
Parcella au nom de quelqu'un, sans son mot de passe -- par exemple un
script qui exporte des données, ou un assistant IA qui lit les notes de
l'association. La plupart des associations n'en ont jamais besoin.

!!! info "Qui peut l'utiliser"
    Chaque utilisateur peut gérer **ses propres** jetons :
    **Changer le mot de passe** dans la barre latérale →
    **Jetons API pour les intégrations** → **Gérer** (page
    **Mes jetons API**). Les administrateurs voient aussi les jetons de
    **tout le monde** sous **Administration → Jetons API**.

![Jetons API](../assets/screenshots/administration/api-tokens.png)

## Comment se comporte un jeton {#how-a-token-behaves}

- Il agit **avec exactement les droits du compte auquel il
  appartient**. Le jeton d'un releveur de compteurs ne peut faire que ce
  que le releveur de compteurs peut faire.
- Il n'est affiché **qu'une seule fois**, juste après sa création.
  Copiez-le à ce moment-là ; il est impossible de le retrouver plus tard.
- Il cesse de fonctionner quand il expire, quand il est révoqué, ou quand
  le mot de passe du compte est changé ou réinitialisé. Désactiver le
  compte l'arrête aussi.

Traitez un jeton comme un mot de passe. S'il a pu fuiter, révoquez-le.

## Nouveau jeton {#new-token}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Utilisateur** | *Uniquement sur la page des administrateurs.* Le compte au nom duquel le jeton agit. Vous pouvez créer des jetons pour vous-même et pour des comptes **sans** accès complet -- typiquement un compte dédié à une intégration, qui ne se connecte jamais lui-même. Les jetons pour d'autres comptes à accès complet ne sont pas possibles, car un jeton agirait silencieusement au nom de cette personne. |
| **Nom** | Obligatoire, jusqu'à 100 caractères. Indiquez à quoi il sert, par ex. « Base de connaissances Claude ». |
| **Expire** | **après 30 jours**, **après 90 jours**, **après 365 jours** (par défaut) ou **jamais**. Préférez une expiration. |
| **Connecteur MCP uniquement (pour un client IA)** | Affiché seulement quand le module **Connecteur MCP pour clients IA** est activé. Un tel jeton ne fonctionne que pour la connexion IA et uniquement avec les notes libérées pour l'IA ; toute autre utilisation est refusée. Utilisez toujours ce type pour un assistant IA. |
| **Créer le jeton** | Crée le jeton et l'affiche dans un encadré vert : *Copiez-le maintenant : il n'est affiché qu'une seule fois ...* |

## La liste des jetons {#the-token-list}

| Colonne / bouton | Ce qu'elle affiche ou fait |
|---|---|
| **Nom** | Le nom, les premiers caractères du jeton (pour le reconnaître), et un badge **MCP uniquement** le cas échéant. |
| **Utilisateur** | *Uniquement sur la page des administrateurs.* À qui appartient le jeton. |
| **Créé** | Date de création. |
| **Dernière utilisation** | Quand un programme l'a utilisé pour la dernière fois, ou **jamais**. |
| **Expire** | Date d'expiration ou **jamais**. |
| **Statut** | **actif**, **expiré**, **révoqué** ou **terminé** (le mot de passe a été changé après la création du jeton). |
| **Révoquer** | Seulement pour les jetons actifs. Après confirmation, le jeton cesse immédiatement de fonctionner. |

**Aucun jeton API pour l'instant.** apparaît quand il n'y en a aucun.

## Connecter un assistant IA aux notes {#connecting-an-ai-assistant-to-the-notes}

Avec le module **Connecteur MCP pour clients IA**, un assistant IA comme
Claude peut rechercher et lire -- et, si vous l'autorisez, écrire -- les
[notes](../modules/notes.md) que vous avez libérées pour lui, et rien
d'autre. En bref :

1. Activez **Connecteur MCP pour clients IA** (et **Notes**) sous
   [Activer et désactiver les modules](modules.md).
2. [Invitez](users.md) un compte séparé pour l'assistant et placez-le
   dans un [groupe](groups.md) qui n'accorde que la lecture des
   **Notes** (et l'écriture, si vous le souhaitez).
3. Ici, créez un jeton pour ce compte en cochant
   **Connecteur MCP uniquement**.
4. Libérez des notes pour l'IA en leur attribuant l'étiquette de
   libération décrite dans le chapitre sur les notes.

Ne libérez que des notes qui ne contiennent aucune donnée personnelle :
elles partent vers un service d'IA externe. La configuration pas à pas
pour chaque client IA se trouve dans le
[guide de configuration MCP](https://github.com/parcella-garden/parcella/blob/main/docs/mcp-setup.md).

## Pour les développeurs {#for-developers}

L'API REST elle-même -- points d'accès, authentification, exemples --
est décrite dans la
[documentation développeur](https://github.com/parcella-garden/parcella#rest-api),
et de manière interactive sous **Administration → Documentation API
(Swagger)**.

## Voir aussi {#related}

- [Première connexion et votre compte](../getting-started/first-login.md#change-password)
- [Utilisateurs et invitations](users.md)

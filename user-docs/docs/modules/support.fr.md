# Assistance {#support}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Parcella n'a pas son propre système de tickets. Votre association répond
aux e-mails et aux demandes du formulaire de contact dans un helpdesk --
FreeScout, Zammad, Znuny / OTRS, osTicket, Zendesk ou Freshdesk -- et le
module d'assistance relie ce helpdesk à Parcella : vous voyez quelle
conversation appartient à quel membre et à quelle parcelle, vous lisez la
conversation, et vous la transformez en carte sur le tableau des tâches.
Les réponses s'écrivent toujours dans le helpdesk lui-même.

!!! info "Qui peut l'utiliser"
    - Le module s'active avec **Assistance (helpdesk)** sous
      [Activer et désactiver les modules](../administration/modules.md).
      Il est **désactivé par défaut**, car il stocke les identifiants
      d'accès du helpdesk. Le helpdesk lui-même est choisi et connecté
      par un administrateur sous
      [Intégrations](../administration/integrations.md).
    - **Conversations d'assistance dans Parcella :** les membres du
      bureau et les administrateurs, et les utilisateurs dont le groupe
      accorde la **Lecture** sur **Assistance (helpdesk)** (voir
      [Groupes](../administration/groups.md)). L'**Écriture** est
      nécessaire pour relier une conversation à un membre ou une
      parcelle.
    - **Créer une tâche :** seulement les membres du bureau et les
      administrateurs (ou les utilisateurs d'un groupe à accès complet),
      comme pour le tableau des tâches lui-même.
    - **Tous les autres** ont quand même un lien **Assistance** dans la
      navigation une fois le module activé et si le helpdesk a une
      adresse web : il ouvre directement le helpdesk dans un nouvel
      onglet.

## D'où viennent les conversations {#where-conversations-come-from}

Parcella interroge le helpdesk environ toutes les cinq minutes pour les
conversations nouvelles ou modifiées. Il ne stocke qu'une référence --
objet, client, statut, nombre de messages, et les liens vers le membre,
la parcelle et la tâche. Les messages eux-mêmes restent dans le helpdesk
et sont rechargés à chaque ouverture d'une conversation.

**Association aux membres :** quand une conversation arrive, Parcella
cherche le membre auquel elle appartient :

1. Si ce client du helpdesk a déjà été relié à un membre, ce membre est
   utilisé.
2. Sinon, si **exactement un** membre a l'adresse e-mail du client, ce
   membre est relié automatiquement.
3. Si plusieurs membres partagent l'adresse (par ex. un couple avec une
   seule boîte), ou si personne ne l'a (un voisin, un fournisseur), la
   conversation reste sans membre. Vous pouvez en relier un à la main.

Si le membre relié a exactement une parcelle actuelle, cette parcelle
est reliée aussi. Une conversation qui a un membre -- automatiquement ou
par vous -- n'est jamais réassociée ensuite.

Quand le nom d'un membre change dans Parcella, sa fiche client dans le
helpdesk est aussi renommée, si le helpdesk le permet.

**Statuts :** chaque helpdesk nomme ses états différemment ; Parcella
les affiche comme `active`, `pending`, `closed`, `spam` ou `deleted`.
Les conversations fermées, spam et supprimées sont masquées de la liste,
du badge et du tableau de bord. Si une conversation est rouverte dans le
helpdesk, elle réapparaît avec son lien au membre intact.

### Ce que permet chaque helpdesk {#what-each-helpdesk-supports}

| Helpdesk | Liste des conversations et badge | Lire les conversations | Le formulaire de contact crée une conversation | Noms des clients synchronisés |
|---|---|---|---|---|
| FreeScout | oui | oui | oui | oui |
| Zammad | oui | oui | oui | oui |
| Znuny / OTRS | oui | oui | oui | non |
| osTicket | non | non | oui | non |
| Zendesk | oui | oui | oui | oui |
| Freshdesk | oui | oui | oui | oui |

Avec osTicket, Parcella ne peut que transmettre les demandes du
formulaire de contact du site web ; vous les traitez uniquement dans
osTicket.

Seuls les messages visibles par le client sont affichés -- les notes
internes restent dans le helpdesk. Les pièces jointes ne sont pas
affichées ; ouvrez la conversation dans le helpdesk pour les voir.

## Conversations d'assistance {#support-conversations}

![Conversations d'assistance](../assets/screenshots/support/list.png)

**Assistance** dans la navigation ouvre la liste des conversations
ouvertes du helpdesk actif, les plus récemment mises à jour en premier.
Le badge rouge à côté d'**Assistance** -- et la tuile **Conversations
d'assistance ouvertes** du [tableau de bord](../getting-started/dashboard.md)
-- comptent les mêmes conversations, qu'elles aient un membre ou non.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Ouvrir dans {helpdesk}** | Ouvre le helpdesk dans un nouvel onglet. Affiché seulement si l'adresse web du helpdesk est définie. |
| **Objet** | L'objet de la conversation. Cliquez n'importe où sur la ligne pour ouvrir la conversation. |
| **Client** | Le nom de l'expéditeur, ou son adresse e-mail. |
| **Membre** | Le membre relié, ou « — ». |
| **Statut** | `active` ou `pending` (les conversations fermées ne sont pas listées). |
| **Messages** | Nombre de messages, tel que le helpdesk l'a indiqué en dernier. |
| **Mis à jour** | Dernière modification de la conversation dans le helpdesk. |
| **Tâche** | Une icône de tableau si la conversation est reliée à une tâche. |

À la place de la liste, vous pouvez voir :

- « Aucun helpdesk n'est encore configuré. … » -- un administrateur doit
  encore en choisir un sous [Intégrations](../administration/integrations.md).
- « {helpdesk} ne peut pas lister les conversations via son
  interface. … » -- le helpdesk est osTicket.
- « Aucune conversation d'assistance pour l'instant. » -- rien d'ouvert
  pour le moment.

## Page d'une conversation {#conversation-page}

<!-- TODO(verify): no screenshot -- the list's rows open conversations by click, not by a link, so the screenshot tool can't follow one; without a connected helpdesk the transcript would only show an error anyway. -->

Affiche une conversation, avec son objet comme titre.

| Bouton | Ce qu'il fait |
|---|---|
| **Retour** | Revient à la liste. |
| **Ouvrir dans {helpdesk}** | Ouvre cette conversation dans le helpdesk -- c'est là que vous y répondez. |

### Conversation {#conversation}

Les messages, du plus ancien au plus récent, chacun avec son auteur et
l'heure. S'ils ne peuvent pas être chargés, un avis explique pourquoi --
le helpdesk est injoignable, il ne peut pas afficher les conversations
(osTicket), ou « Le helpdesk de cette conversation n'est pas (ou plus)
configuré. » quand l'association a changé de helpdesk depuis.
« Impossible de charger les messages. » signifie que le helpdesk n'en a
renvoyé aucun.

### Membre {#member}

Affiche le membre relié (avec un lien vers sa page), ou « Aucun membre
associé. ».

Avec le droit d'écriture, choisissez un membre et cliquez sur
**Enregistrer** :

- Les membres ayant l'adresse e-mail du client sont listés en premier,
  marqués **suggéré**. Si plusieurs membres partagent l'adresse, une
  note vous demande de choisir le bon.
- En dessous, tous les membres actuels.
- **-- aucun --** supprime le lien.

Enregistrer un membre réinitialise aussi la parcelle : si le membre a
exactement une parcelle actuelle, elle est reliée ; sinon, aucune.

### Parcelle {#parcel}

Affichée dès qu'un membre est relié. Avec le droit d'écriture,
choisissez l'une des parcelles actuelles du membre, ou **-- aucune --**,
et cliquez sur **Enregistrer**.
<!-- TODO(verify): without write permission the Parcel card is empty -- the linked parcel isn't displayed at all for read-only users. -->

### Tableau des tâches {#task-board}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Ouvrir la tâche** | Affiché quand la conversation est reliée à une tâche ; ouvre la tâche. |
| Liste + **Créer une tâche** | Crée une nouvelle carte dans la liste choisie du [tableau des tâches](tasks.md) et la relie à la conversation. Le titre de la carte est l'objet ; sa description nomme le helpdesk, le numéro de la conversation et, s'il est relié, le membre. Réservé aux membres du bureau et aux administrateurs. |

Si le tableau des tâches n'a encore aucune liste, la création échoue
avec « Aucune liste n'existe encore sur le tableau des tâches ».
<!-- TODO(verify): there is a route to link an existing task to a conversation, but no form on the page uses it. -->

!!! note "On répond dans le helpdesk"
    Parcella n'a volontairement pas de zone de réponse. Cliquez sur
    **Ouvrir dans {helpdesk}** et répondez là-bas ; le nouveau message
    apparaît dans Parcella la prochaine fois que vous ouvrez la
    conversation.

## Le formulaire de contact du site web {#the-website-contact-form}

Si le site web de votre association a un formulaire de contact, il peut
créer une conversation dans le helpdesk directement via Parcella. C'est
un interrupteur séparé, **API publique de formulaire de contact**, lui
aussi désactivé par défaut. La configuration est décrite sous
[Intégrations](../administration/integrations.md).

## Voir aussi {#related}

- [Intégrations](../administration/integrations.md) -- choisir et
  connecter le helpdesk
- [Tableau des tâches](tasks.md) -- assurer le suivi d'une conversation
- [Membres](members.md) -- adresses e-mail utilisées pour l'association
- [Tableau de bord](../getting-started/dashboard.md)

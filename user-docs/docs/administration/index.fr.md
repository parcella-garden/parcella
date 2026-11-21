# Administration {#administration}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

L'espace d'administration est l'endroit où votre installation de Parcella
est configurée et entretenue : qui peut se connecter, ce que chacun peut
faire, les données de base de l'association, les connexions à d'autres
services et les sauvegardes.

!!! info "Qui peut l'utiliser"
    Seulement les **administrateurs** : les comptes ayant l'ancien rôle
    **Administrateur**, ou membres d'un groupe disposant de
    **Accès au panneau d'administration**. Les membres du bureau ayant un
    accès complet aux modules ne le voient pas, sauf s'ils sont aussi
    administrateurs. Voir
    [Rôles, groupes et droits](../getting-started/roles-and-permissions.md).

Vous le trouvez en bas de la barre latérale, sous **Administration**.

## Les pages {#the-pages}

| Entrée de la barre latérale | Page | Ce que vous y faites |
|---|---|---|
| **Système** | [Informations système et mises à jour](system.md) | Voir votre version et si une mise à jour existe ; télécharger une sauvegarde. |
| | [Sauvegarde et restauration](backup.md) | Restaurer depuis une sauvegarde ; planifier des sauvegardes automatiques vers le cloud. |
| **Utilisateurs** | [Utilisateurs et invitations](users.md) | Inviter des personnes, modifier, désactiver et supprimer des comptes, réinitialiser des mots de passe. |
| **Groupes** | [Groupes](groups.md) | Décider qui peut lire, modifier et supprimer quoi. |
| **Jetons API** | [Jetons API](api-tokens.md) | Voir et révoquer les jetons de tout le monde ; créer des jetons pour des comptes d'intégration. |
| **Paramètres** | [Paramètres de l'association](settings.md) | Nom et adresse de l'association, logo, langue, région et devise, serveur e-mail, données financières, ordre de la navigation et plus. |
| | [Activer et désactiver les modules](modules.md) | La carte **Domaines fonctionnels** de la page des paramètres. |
| **Intégrations** | [Intégrations](integrations.md) | Formulaires du site web, brouillons pour le site, stockage cloud, helpdesk, Nextcloud Deck, liens de flux de calendrier. |
| **Journal des e-mails** | [Journal des e-mails](email-log.md) | Vérifier si un e-mail est bien parti. |
| **Données d'exemple** | [Données d'exemple](sample-data.md) | Remplir une nouvelle installation avec des données de démonstration pour essayer, puis les supprimer. |
| **Documentation API (Swagger)** | -- | La description technique de l'interface de programmation, pour les développeurs. |

## Configurer une nouvelle installation {#setting-up-a-new-installation}

Un ordre raisonnable pour une toute nouvelle installation :

1. Connectez-vous avec le compte administrateur intégré et changez son
   mot de passe -- voir [Première connexion](../getting-started/first-login.md#the-very-first-login-after-installation).
2. Dans les [Paramètres de l'association](settings.md) : langue, région et
   devise, données de l'association, logo, et le serveur e-mail (sans lui,
   Parcella ne peut pas envoyer d'invitations).
3. Dans [Activer et désactiver les modules](modules.md) : désactivez ce
   dont vous n'avez pas besoin, activez ce qu'il vous faut.
4. Créez des [groupes](groups.md) pour les fonctions de votre association.
5. [Invitez](users.md) les autres membres du bureau dans ces groupes.
6. Mettez en place les [sauvegardes](backup.md).

Le guide pratique [Configurer une nouvelle association](../guides/new-club-setup.md)
reprend tout cela, avec la saisie des membres et des parcelles.

L'installation de Parcella lui-même (le serveur, Docker, l'adresse web)
est décrite dans la
[documentation développeur](https://github.com/parcella-garden/parcella#install-self-hosting).

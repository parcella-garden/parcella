# Informations système et mises à jour {#system-information-and-updates}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

La page Système indique quelle version de Parcella vous utilisez, si une
version plus récente est disponible, et sert de point de départ pour les
sauvegardes.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Système**.

![Système](../assets/screenshots/administration/system.png)

## Avis de mise à jour {#update-notice}

Parcella demande régulièrement à GitHub, où il est publié, si une
nouvelle version est sortie. Rien concernant votre association n'est
transmis. Vous pouvez désactiver cela sous
[Paramètres de l'association → Mises à jour](settings.md#updates) ;
l'avis de mise à jour disparaît alors de cette page.

**Si vous êtes à jour**, vous voyez

> Version v1.2.3 -- à jour (dernière vérification : 18.11.2026 14:05)

ou **... pas encore vérifié** juste après l'installation.

**Si une version plus récente existe**, un encadré mis en évidence
affiche **Mise à jour disponible :** avec le nouveau numéro de version,
la version que vous utilisez, et les quatre commandes qui installent la
mise à jour sur le serveur.

| Bouton | Ce qu'il fait |
|---|---|
| **Vérifier maintenant** | Interroge GitHub immédiatement au lieu d'attendre la prochaine vérification automatique (toutes les six heures). |

!!! note "La mise à jour se fait sur le serveur"
    La mise à jour elle-même n'est pas un bouton dans Parcella. La
    personne qui gère le serveur saisit les commandes affichées dans
    l'encadré. Transmettez-les-lui si ce n'est pas vous. Téléchargez
    d'abord une [sauvegarde](backup.md).

    L'encadré avertit aussi que la première commande remplace le fichier
    de configuration du serveur par la version actuelle. Les
    modifications faites par l'administrateur du serveur dans ce fichier
    sont perdues, sauf s'il les conserve dans un fichier de surcharge
    séparé, comme l'expliquent les instructions d'installation.

Lisez les notes de version sur GitHub avant de mettre à jour, pour voir
ce qui a changé.

## Sauvegarde {#backup}

La carte **Sauvegarde** a trois boutons :

| Bouton | Ce qu'il fait |
|---|---|
| **Sauvegardes cloud** | Ouvre la planification des sauvegardes automatiques vers votre stockage cloud. |
| **Restaurer depuis une sauvegarde** | Ouvre la page de restauration. |
| **Télécharger la sauvegarde** | Télécharge immédiatement une sauvegarde complète. |

Les trois sont décrits dans [Sauvegarde et restauration](backup.md).

## Voir aussi {#related}

- [Sauvegarde et restauration](backup.md)
- [Paramètres de l'association](settings.md#updates)

# Données d'exemple {#sample-data}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les données d'exemple remplissent une nouvelle installation avec des
enregistrements fictifs mais réalistes dans chaque module, pour que vous
puissiez parcourir Parcella et faire des essais avant de saisir votre
vraie association. Une fois terminé, un clic supprime tout.

!!! info "Qui peut l'utiliser"
    Administrateurs uniquement. Ouvrez **Administration → Données d'exemple**.

![Données d'exemple](../assets/screenshots/administration/sample-data.png)

## Ce qui est ajouté {#what-this-adds}

La carte de gauche liste ce qui est créé :

- **Base :** 6 membres, 5 parcelles et leurs attributions, dont un foyer
  partagé et un ancien locataire.
- **Heures de travail :** une configuration annuelle, une session de
  travail passée et une à venir avec des participants, et quelques
  tâches.
- **Comptage :** un compteur d'eau et un compteur d'électricité avec deux
  années de relevés.
- **Assurance :** configuration annuelle, formules d'assurance de biens et
  couverture pour deux parcelles.
- **Assistance :** quelques conversations de helpdesk d'exemple dans
  différents états.
- **Demandes d'achat :** une demande ouverte, une approuvée et une
  refusée.
- **Calendrier :** quelques événements communautaires passés et à venir.
- **Inventaire :** des catégories, quelques objets et un objet
  actuellement prêté.
- **Tableau des tâches :** quelques cartes réparties sur les trois
  colonnes.
- **Finances :** quelques catégories comptables d'exemple.

Parcella mémorise chaque enregistrement créé de cette façon.
**Supprimer toutes les données d'exemple** supprime exactement ces
enregistrements et rien de ce que vous avez saisi vous-même. Aucun
compte utilisateur n'est jamais créé ni modifié.

Les données d'exemple arrivent dans les modules même s'ils sont
désactivés ; activez un module pour les voir.

## Ajouter ou supprimer {#add-or-remove}

Ce qu'affiche la carte de droite dépend de l'état de votre installation :

| Situation | Ce que vous voyez |
|---|---|
| Nouvelle installation, pas encore de membres ni de parcelles | *Cette installation semble vierge -- aucune donnée de membre ou de parcelle pour l'instant.* et le bouton **Ajouter des données d'exemple**. Après confirmation, les données sont créées (**Données d'exemple ajoutées.**). |
| Données d'exemple présentes | **Des données d'exemple sont actuellement présentes :** avec un nombre par domaine, et le bouton **Supprimer toutes les données d'exemple**. Après confirmation, elles sont supprimées (**Toutes les données d'exemple ont été supprimées.**). C'est irréversible. |
| De vrais membres ou parcelles existent déjà | Une note indiquant que les données d'exemple ne peuvent être ajoutées qu'à une nouvelle installation. Il n'y a pas de bouton. |

!!! warning "Supprimez-les avant la mise en service"
    Ne mélangez pas données d'exemple et données réelles. Supprimez-les
    avant de commencer à saisir les vrais membres et parcelles de votre
    association -- une fois que des données réelles existent, les données
    d'exemple ne peuvent plus être ajoutées, et vous devriez distinguer
    les enregistrements fictifs à la main.

## Voir aussi {#related}

- [Configurer une nouvelle association](../guides/new-club-setup.md)
- [Activer et désactiver les modules](modules.md)

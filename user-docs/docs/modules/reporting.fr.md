# Rapports {#reporting}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Les chiffres clés de votre association au fil du temps, sous forme de
graphiques : l'âge de vos membres, l'évolution des adhésions, le nombre
de parcelles rendues, le nombre de candidats, et le bilan des heures de
travail. Pratique pour le rapport annuel ou l'assemblée générale.

!!! info "Qui peut l'utiliser"
    - L'interrupteur du module est **Rapports** sous **Administration →
      Activer et désactiver les modules**. Il est **activé** par défaut.
    - Les rôles **Conseil d'administration** et **Administrateur**, et
      les membres d'un groupe avec **Accès complet à chaque module**,
      le voient toujours.
    - Tous les autres ont besoin de la *lecture* sur **Rapports** dans
      l'un de leurs [groupes](../administration/groups.md). La page
      n'affiche que des totaux et des nombres, jamais de noms : elle ne
      nécessite donc pas en plus l'accès aux membres, aux heures de
      travail ou aux candidats.

## Page des rapports {#reporting-page}

![Rapports](../assets/screenshots/reporting/index.png)

Ouvrez **Rapports** dans le menu. La page est en lecture seule. Chaque
chiffre est calculé à partir de vos données actuelles à chaque ouverture
de la page ; rien n'est stocké ni n'a besoin d'être mis à jour. Les
séries temporelles couvrent jusqu'aux 10 dernières années, de la
première année avec des données jusqu'à l'année en cours. Une année
passée est comptée telle qu'elle était au 31 décembre, l'année en cours
telle qu'elle est aujourd'hui.

Chaque graphique est une carte avec :

- le graphique lui-même (survolez-le pour voir les chiffres exacts) ;
- une note grise avec une icône d'information quand quelque chose doit
  être expliqué, par exemple combien de membres ont été laissés de côté ;
- **Afficher les chiffres sous forme de tableau**, qui déplie les mêmes
  chiffres sous forme de tableau, prêts à copier. Les graphiques en
  camembert ajoutent une colonne **Part / total** avec les pourcentages,
  les graphiques empilés une colonne avec le total par année.

Un graphique sans aucune donnée indique **Pas encore de données.**

Certains graphiques n'apparaissent que si leur module est activé : les
graphiques sur les candidats nécessitent **Candidats**, ceux sur les
heures de travail **Gestion des heures de travail**, et celui sur
l'électricité **Gestion de l'électricité**.

## Les graphiques {#the-charts}

| Graphique | Ce qu'il compte |
|---|---|
| **Membres par génération** | Camembert des membres actifs d'aujourd'hui par année de naissance : **Génération silencieuse (jusqu'à 1945)**, **Baby-boomers (1946–1964)**, **Génération X (1965–1980)**, **Milléniaux (1981–1996)**, **Génération Z (1997–2012)**, **Génération Alpha (depuis 2013)**. Les membres sans date de naissance sont laissés de côté ; la note indique combien. |
| **Membres par année** | Courbe du nombre de **Membres** chaque année : toutes les personnes dont la date « membre depuis » est au plus tard la fin de cette année et qui n'étaient pas parties à ce moment-là. Les membres sans date d'adhésion sont comptés chaque année ; la note indique combien. |
| **Parcelles résiliées par année** | Histogramme des **Baux terminés** par année : chaque bail dont la date de fin tombe dans cette année, y compris les dates de fin déjà fixées pour plus tard dans l'année. Une parcelle transmise d'un locataire au suivant compte comme un bail terminé. |
| **Candidats par trimestre** | Histogramme des nouveaux **Candidats** selon leur date de candidature, pour chaque trimestre de l'année dernière et de cette année. |
| **Candidats par année** | La même chose par année. |
| **Heures de travail par année** | Barres empilées pour chaque année disposant d'une configuration des heures de travail. Chaque parcelle (ou membre, voir ci-dessous) est comptée dans exactement un groupe, vérifié dans cet ordre : **Exempté**, **Paie la contribution (heures manquantes)**, **Accompli grâce au parrainage**, **Accompli par les journées de travail**. Les années où les heures étaient dues par membre plutôt que par parcelle, la note indique « Compté par membre au lieu de par parcelle en ... ». |
| **Transferts d'heures par année** | Deux barres par année : le nombre de **Transferts** d'heures, et le total des **Heures transférées**. |
| **Parcelles avec électricité** | Camembert des parcelles actives d'aujourd'hui **Avec raccordement électrique** (au moins un compteur d'électricité sur la parcelle) et **Sans raccordement électrique**. |

!!! note "À garder en tête"
    - **Membres par génération** et **Parcelles avec électricité**
      montrent seulement la situation actuelle. Parcella ne conserve pas
      d'instantanés et ne peut donc pas dire à quoi ils ressemblaient une
      année antérieure.
    - Un membre supprimé (au lieu de recevoir une date de fin) disparaît
      aussi de toutes les années passées. Terminez les adhésions au lieu
      de supprimer les membres, et l'historique reste juste.
    - Les chiffres proviennent des données telles que saisies. Une date
      d'adhésion ou de naissance manquante apparaît dans les notes ;
      corrigez-la sur le [membre](members.md) et rechargez la page.

Il n'y a pas de bouton d'export pour les graphiques. Utilisez
**Afficher les chiffres sous forme de tableau** pour copier les chiffres,
par exemple dans un tableur ou le rapport annuel.

## Voir aussi {#related}

- [Membres](members.md) -- dates d'adhésion et dates de naissance.
- [Parcelles](parcels.md) -- baux et leurs dates de fin.
- [Candidats](applicants.md)
- [Heures de travail](work-hours.md) -- exemptions, parrainage et
  transferts d'heures.
- [Eau et électricité](metering.md) -- compteurs d'électricité par parcelle.

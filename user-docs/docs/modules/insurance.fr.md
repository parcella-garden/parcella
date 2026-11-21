# Assurances {#insurance}

!!! note "Traduction automatique"
    Cette page a été traduite automatiquement de l'anglais et n'a pas encore été relue. En cas de doute, la version anglaise fait foi (changez de langue en haut de la page).

Le module des assurances suit quelles parcelles ont souscrit l'assurance
de groupe de l'association une année donnée -- un forfait d'**assurance
habitation** et/ou une **assurance accident** -- et calcule ce que chaque
parcelle doit pour cela. Tout est conservé par année : les chiffres de
l'année précédente restent tels quels quand vous configurez la nouvelle
année.

!!! info "Qui peut l'utiliser"
    Les membres du bureau et les administrateurs ont toujours un accès
    complet. Les autres utilisateurs ont besoin d'un groupe qui accorde
    des droits sur **Assurance** (voir
    [Groupes](../administration/groups.md)) :

    - **Lecture** -- voir l'aperçu, la liste des parcelles, la page
      d'assurance de chaque parcelle, la configuration et le rapport
      annuel, et télécharger l'export CSV.
    - **Écriture** -- modifier l'assurance d'une parcelle, les montants
      de l'assurance accident et les forfaits.
    - **Suppression** -- supprimer un forfait d'assurance habitation.

    Le module s'active avec **Gestion des assurances** sous
    [Activer et désactiver les modules](../administration/modules.md).
    Il est activé par défaut.

Vous trouvez le module dans la navigation sous **Assurance**, avec les
entrées **Aperçu**, **Parcelles**, **Configuration** et **Évaluation**.

## Comment le coût est calculé {#how-the-cost-is-calculated}

Le coût d'une parcelle pour une année est la somme de deux parties.

**Assurance habitation :** si la parcelle a une assurance habitation et
qu'un forfait est choisi, elle paie le montant de ce forfait. Une
assurance habitation activée sans forfait choisi ne coûte rien.

**Assurance accident :** si la parcelle a une assurance accident et
qu'une configuration d'assurance accident existe pour cette année, elle
paie :

- le **Montant de base par parcelle** une fois, si au moins une personne
  du foyer de la parcelle est cochée comme couverte, plus
- le **Montant supplémentaire par personne supplémentaire** pour chaque
  personne cochée qui n'appartient *pas* au foyer.

Si personne du foyer n'est coché, le montant de base n'est pas facturé,
même si des personnes supplémentaires sont assurées. Sans configuration
pour l'année, l'assurance accident ne coûte rien.

**Exemple :** montant de base 3,00, montant supplémentaire 3,00. Une
parcelle avec le forfait « Forfait 2 » (60,00), une assurance accident
pour le couple vivant à la même adresse et un co-locataire vivant
ailleurs paie 60,00 + 3,00 + 1 × 3,00 = **66,00**.

### Qui compte comme foyer {#who-counts-as-the-household}

Parcella regarde les locataires actuels de la parcelle -- les personnes
dont le bail est en cours et dont l'adhésion n'est ni terminée ni
supprimée -- et compare leurs adresses (rue, code postal et ville ; les
majuscules et espaces superflus n'ont pas d'importance).

- Le plus grand groupe de locataires partageant la même adresse est le
  **foyer**. Si deux groupes ont la même taille, le premier trouvé
  l'emporte.
- Tous les autres sont listés comme **autres membres de la parcelle**,
  qui peuvent être assurés en plus pour le montant supplémentaire.
- Un locataire sans adresse enregistrée ne forme jamais de foyer avec
  personne, même avec un autre locataire lui aussi sans adresse.
- Une parcelle avec un seul locataire : cette personne est le foyer,
  avec ou sans adresse.

!!! tip "Gardez des adresses cohérentes"
    « 5 rue Principale » et « 5 r. Principale » sont des adresses
    différentes pour Parcella. Si un couple apparaît comme foyer plus
    « autre membre de la parcelle », vérifiez l'orthographe dans les
    deux fiches membres.

Quand l'assurance d'une parcelle est ouverte pour la première fois pour
une année, chaque membre du foyer est coché comme couvert. Ensuite, ce
sont les coches qui comptent : un membre qui déménage plus tard ne change
pas la facture d'une année déjà configurée, et un nouveau membre du foyer
qui arrive plus tard apparaît non coché jusqu'à ce que vous le cochiez.

Le module de facturation utilise le même calcul quand il ajoute
l'assurance à la facture annuelle d'une parcelle, avec une ligne par
partie (forfait habitation, montant de base du foyer, personnes
supplémentaires). Voir [Séries de factures](finances/invoice-runs.md).

## Aperçu {#overview}

![Aperçu](../assets/screenshots/insurance/overview.png)

La page d'accueil du module (**Assurance → Aperçu**). Elle affiche d'un
coup d'œil les chiffres d'une année.

| Champ / bouton | Ce qu'il fait |
|---|---|
| Sélecteur d'année (en haut à droite) | Fait passer tous les chiffres à une autre année. Il liste chaque année ayant une configuration d'assurance accident, plus l'année en cours. |
| **Gérer les parcelles** | Ouvre la [liste des parcelles](#parcels) pour l'année choisie. |
| Avertissement « Aucune configuration d'assurance n'existe pour … » | Affiché quand l'année n'a pas encore de montants d'assurance accident. **Créer maintenant →** ouvre la [configuration](#configuration) de cette année. |
| **Assurance habitation** | Nombre de parcelles avec assurance habitation cette année. |
| **Assurance accident** | Nombre de parcelles avec assurance accident dont au moins un membre du foyer est couvert. Une parcelle où seule une personne supplémentaire est assurée n'est pas comptée. |
| **Revenus habitation** | Somme du coût d'assurance habitation de toutes les parcelles pour l'année. |
| **Revenus accident** | Somme du coût d'assurance accident de toutes les parcelles pour l'année. |
| **Forfaits d'assurance habitation {year}** | Les forfaits de l'année avec leurs montants. Affiché seulement s'il existe des forfaits. |
| **Configuration** | Ouvre la [configuration](#configuration). |
| **Gérer les parcelles** | Ouvre la [liste des parcelles](#parcels). |
| **Rapport annuel** | Ouvre le [rapport annuel](#annual-report). |

## Parcelles {#parcels}

![Parcelles](../assets/screenshots/insurance/parcels-list.png)

**Assurance → Parcelles** liste les parcelles avec leur statut
d'assurance et leur coût pour une année. Ouvrez-la depuis l'aperçu pour
garder l'année choisie là-bas ; depuis la navigation, elle affiche
l'année en cours.

La liste contient chaque parcelle active. Les parcelles résiliées sont
listées aussi, marquées **résilié**, car la fin d'un bail n'annule pas
d'elle-même le contrat d'assurance. Une parcelle résiliée reste dans la
liste jusqu'à ce que vous ouvriez sa page d'assurance, désactiviez les
deux types d'assurance et cliquiez sur **Enregistrer** -- cela enregistre
« vérifié, plus rien à assurer », et la parcelle disparaît de la liste de
cette année.

**Filtres** (au-dessus du tableau ; ils s'appliquent dès que vous
choisissez une valeur) :

| Filtre | Ce qu'il fait |
|---|---|
| **Assurance habitation** | **Tous**, **Aucune** (parcelles sans assurance habitation), ou un forfait de l'année (parcelles assurées avec exactement ce forfait). |
| **Assurance accident** | **Tous**, **Oui** (assurance accident activée) ou **Aucune** (désactivée ou jamais configurée). |
| **Réinitialiser** | Efface les deux filtres. Affiché seulement tant qu'un filtre est actif. |

**Colonnes :**

| Colonne | Ce qu'elle affiche |
|---|---|
| **Parcelle** | Numéro de parcelle, avec un lien vers la page d'assurance de la parcelle. Cliquez sur l'en-tête de colonne pour trier par numéro ; cliquez à nouveau pour inverser. |
| **Assurance habitation** | Le nom du forfait, **Oui** si l'assurance habitation est activée sans forfait choisi, ou « – ». |
| **Assurance accident** | **Oui** si l'assurance accident est activée, avec le nombre de personnes supplémentaires entre parenthèses, par ex. **Oui (+1)** ; sinon « – ». |
| **Coût total** | Le coût total d'assurance de la parcelle pour l'année. Cliquez sur l'en-tête pour trier par coût. |
| Bouton crayon | Ouvre la page d'assurance de la parcelle. |

La ligne **Somme** en bas compte les parcelles avec assurance habitation
et avec assurance accident (là aussi seulement celles avec au moins un
membre du foyer couvert) et additionne le coût total des parcelles
listées. Sous le tableau, vous voyez combien de parcelles sont listées.

## Page d'assurance d'une parcelle {#parcel-insurance-page}

![Page d'assurance d'une parcelle](../assets/screenshots/insurance/detail.png)

Ouverte depuis la liste des parcelles ou le rapport annuel, avec le
titre **Assurance pour la parcelle {numéro}**. C'est ici que vous
enregistrez ce qu'une parcelle a souscrit pour l'année indiquée dans le
lien par lequel vous êtes arrivé.

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Précédent** / **Suivant** | Va à la parcelle précédente ou suivante dans l'ordre de la liste des parcelles (par numéro). Clavier : ++ctrl+left++ et ++ctrl+right++. |
| **Retour** | Revient à la liste des parcelles de cette année. |
| Avertissement « Aucune configuration d'assurance n'existe pour … » | L'année n'a pas encore de montants d'assurance accident, donc l'assurance accident ne coûte rien. **Créer maintenant →** ouvre la configuration. |
| **Assurance habitation souscrite** | Interrupteur. Activé, le champ **Forfait** apparaît. |
| **Forfait** | Le forfait d'assurance habitation pour cette année. Si l'année n'a pas de forfaits, un avertissement avec **Créer maintenant →** apparaît à la place. |
| **Assurance accident souscrite** | Interrupteur. Activé, les listes de personnes apparaissent. |
| **Foyer (partagent une adresse avec d'autres occupants) :** | Le foyer détecté (voir [Qui compte comme foyer](#who-counts-as-the-household)). Chaque personne cochée est couverte ; décochez celle qui refuse. Le montant de base est facturé une fois si au moins une personne ici est cochée. |
| **Autres membres de la parcelle (adresse différente) …** | Les locataires hors du foyer. Cochez une personne pour l'assurer pour le montant supplémentaire. Affiché seulement s'il existe de tels locataires. |
| **Coûts {year}** | **Assurance habitation**, **Assurance accident** et **Total** pour cette parcelle, tels qu'actuellement enregistrés. Les chiffres se mettent à jour après l'enregistrement. |
| **Enregistrer** | Enregistre l'assurance de la parcelle pour cette année et recharge la page. Affiché seulement avec le droit d'écriture ; sans lui, tous les champs sont en lecture seule. |

!!! warning "Désactiver l'assurance accident efface les coches"
    Quand vous enregistrez avec **Assurance accident souscrite**
    désactivée, les membres du foyer et les personnes supplémentaires
    cochés sont retirés. Si vous la réactivez plus tard, recochez les
    personnes avant d'enregistrer.

!!! note
    Désactiver l'assurance habitation efface aussi le forfait choisi.

## Configuration {#configuration}

![Configuration](../assets/screenshots/insurance/configuration.png)

**Assurance → Configuration** contient les prix de l'année. Choisissez
l'année avec le sélecteur en haut à droite ; **Retour** revient à
l'aperçu. Sans droit d'écriture, vous ne voyez que les montants et les
forfaits.

### Assurance accident … {#accident-insurance}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Montant de base par parcelle** | Facturé une fois par parcelle avec assurance accident, pour son foyer. Prérempli avec 3,00 quand l'année n'a pas encore de configuration. |
| **Montant supplémentaire par personne supplémentaire** | Facturé pour chaque membre assuré de la parcelle hors du foyer. Prérempli avec 3,00 quand l'année n'a pas encore de configuration. |
| **Enregistrer** | Enregistre les deux montants pour l'année choisie. L'enregistrement crée la configuration de l'année si elle n'existe pas ; dès lors l'année apparaît dans les sélecteurs d'année. |

Les montants acceptent une virgule ou un point comme séparateur décimal
(`3,50` ou `3.50`). Un montant que Parcella ne peut pas lire comme un
nombre est enregistré comme 0 -- vérifiez le chiffre après
l'enregistrement.

### Nouveau forfait d'assurance habitation {#new-property-insurance-package}

| Champ / bouton | Ce qu'il fait |
|---|---|
| **Nom** | Le nom du forfait, par ex. « Forfait 1 ». Obligatoire. |
| **Montant** | Ce que paie par an une parcelle avec ce forfait. Obligatoire. |
| **Ordre de tri** | Les forfaits sont listés selon ce nombre, le plus petit en premier, puis par montant. 0 par défaut. |
| **+** | Ajoute le forfait à l'année choisie. |

### Forfaits … {#packages}

Les forfaits de l'année. Avec le droit d'écriture, vous pouvez modifier
**Nom** et **Montant** directement dans la ligne et confirmer avec le
bouton de coche. Le bouton corbeille supprime le forfait après
confirmation (nécessite le droit de suppression).

!!! warning "Supprimer un forfait utilisé"
    Les parcelles qui avaient le forfait supprimé gardent « assurance
    habitation souscrite », mais sans forfait -- elles ne coûtent alors
    rien en assurance habitation et affichent **Oui** au lieu d'un nom de
    forfait. Choisissez un nouveau forfait sur chacune de ces parcelles.

!!! tip "Configurer une nouvelle année"
    Les forfaits et les montants appartiennent à une année et ne sont
    pas copiés automatiquement. Au début d'une nouvelle année, ouvrez la
    configuration de cette année, saisissez les montants de l'assurance
    accident et recréez les forfaits, puis parcourez la liste des
    parcelles. Chaque parcelle commence la nouvelle année sans assurance
    enregistrée.

## Rapport annuel {#annual-report}

![Rapport annuel](../assets/screenshots/insurance/evaluation.png)

**Assurance → Évaluation** (ou **Rapport annuel** dans l'aperçu), avec
le titre **Rapport d'assurance {year}**, liste chaque parcelle ayant une
assurance habitation ou accident une année donnée, avec ses coûts.
Utilisez-le pour vérifier les totaux par rapport à la facture de
l'assureur.

**Filtres** (s'appliquent dès que vous choisissez une valeur) :

| Filtre | Ce qu'il fait |
|---|---|
| Année | L'année du rapport. |
| **Tous les types** / **Assurance habitation** / **Assurance accident** | Toutes les parcelles assurées, ou seulement celles avec ce type d'assurance. |
| **Tous les forfaits** / un forfait | Seulement les parcelles assurées avec ce forfait habitation. |
| **Tous** / **Avec personnes supplémentaires** / **Sans personnes supplémentaires** | Les parcelles avec au moins une personne supplémentaire assurée, ou les parcelles avec assurance accident sans aucune. |

| Champ / colonne | Ce qu'il affiche |
|---|---|
| **Parcelles assurées** | Nombre de parcelles listées avec les filtres actuels. |
| **Revenus totaux** | Somme de la colonne **Total**. |
| **Parcelle** | Numéro de parcelle, avec un lien vers la page d'assurance de la parcelle. |
| **Assurance habitation** | Le nom du forfait, ou « – ». |
| **Coût habitation** | Le coût d'assurance habitation de la parcelle. |
| **Assurance accident** | **Oui** ou « – ». |
| **Personnes supplémentaires** | Nombre de personnes supplémentaires assurées hors du foyer. |
| **Coût accident** | Le coût d'assurance accident de la parcelle. |
| **Total** | Le coût total d'assurance de la parcelle. |
| **Export CSV** | Télécharge la liste telle qu'elle est filtrée, sous forme de fichier séparé par des points-virgules avec virgule décimale (s'ouvre directement dans un tableur en allemand). |
| **Retour** | Revient à l'aperçu. |

!!! note "En-têtes de colonnes du CSV"
    Le fichier CSV utilise les mêmes en-têtes de colonnes que cette page,
    dans la langue de l'association : Parcelle, Assurance habitation,
    Forfait, Coût habitation (EUR), Assurance accident, Personnes
    supplémentaires, Coût accident (EUR), Total (EUR). Les valeurs oui/non
    sont aussi écrites dans cette langue.

!!! note "Deux façons de compter"
    **Parcelles assurées** compte ici chaque parcelle listée. La tuile
    **Assurance accident** de l'aperçu ne compte que les parcelles avec
    au moins un membre du foyer couvert, les deux nombres peuvent donc
    différer.

## Voir aussi {#related}

- [Parcelles](parcels.md) -- baux et résiliation, qui déterminent qui
  apparaît sur la page d'assurance d'une parcelle
- [Membres](members.md) -- les adresses utilisées pour détecter le foyer
- [Séries de factures](finances/invoice-runs.md) -- facturer l'assurance
  avec la facture annuelle
- [Groupes](../administration/groups.md) -- donner à un trésorier
  l'accès à ce module

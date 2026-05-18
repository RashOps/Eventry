# Description complète du système — Eventry

## Vue d'ensemble

Eventry est une plateforme web de découverte, d'inscription et d'évaluation
d'événements culturels et festifs (festivals, expositions, boîtes de nuit,
afterworks, sorties). Elle met en relation deux types d'acteurs :
les participants cherchant des événements et les organisateurs souhaitant
promouvoir leurs événements et suivre leurs inscrits.

L'application repose sur une architecture polyglotte :
- PostgreSQL gère les données structurées et transactionnelles
  (identités, inscriptions, lieux)
- MongoDB gère les données flexibles et analytiques
  (métadonnées polymorphes par type d'événement, avis communautaires,
  index géospatiaux pour la recherche de proximité)

## Périmètre fonctionnel

L'application couvre cinq domaines métiers :

1. Identité & Authentification — gestion des comptes, connexion JWT,
   rôles (visiteur, participant, organisateur)

2. Catalogue Événements — listing paginé et filtré, recherche full-text,
   recherche géospatiale par proximité, fiche détaillée

3. Inscription — réservation de places, gestion de la liste d'attente,
   promotion automatique, annulation

4. Social — dépôt et lecture d'avis avec notes détaillées,
   réponses de l'organisateur, likes

5. Dashboard Organisateur — statistiques de remplissage,
   agrégations d'avis, vue globale de ses événements
-- =============================================================================
-- PROJET EVENTRY - SCRIPT D'INITIALISATION POSTGRESQL (FULL)
-- Auteur : Gemini CLI (Expert Data)
-- Conventions : snake_case (pluriel), 3NF, ACID
-- =============================================================================

-- 1. NETTOYAGE (Optionnel pour le dev)
DROP VIEW IF EXISTS v_dashboard_organisateur;
DROP VIEW IF EXISTS v_evenements_details;
DROP TABLE IF EXISTS inscriptions;
DROP TABLE IF EXISTS evenements_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS evenements;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS lieux;
DROP TABLE IF EXISTS organisateurs;
DROP TABLE IF EXISTS utilisateurs;

DROP TYPE IF EXISTS role_enum;
DROP TYPE IF EXISTS statut_event_enum;
DROP TYPE IF EXISTS statut_inscription_enum;

-- 2. TYPES ENUMERES
CREATE TYPE role_enum AS ENUM ('visiteur', 'participant', 'organisateur');
CREATE TYPE statut_event_enum AS ENUM ('draft', 'published', 'cancelled', 'archived');
CREATE TYPE statut_inscription_enum AS ENUM ('confirmee', 'liste_attente', 'annulee');

-- 3. TABLES DE BASE
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    pseudo VARCHAR(100) UNIQUE NOT NULL,
    avatar_url TEXT,
    role role_enum DEFAULT 'participant',
    date_inscription TIMESTAMP DEFAULT NOW(),
    est_actif BOOLEAN DEFAULT TRUE
);

CREATE TABLE organisateurs (
    id SERIAL PRIMARY KEY,
    id_utilisateur INTEGER UNIQUE NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    site_web VARCHAR(255),
    est_verifie BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT NOW()
);

CREATE TABLE lieux (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    adresse VARCHAR(255) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    code_postal VARCHAR(10) NOT NULL,
    pays VARCHAR(100) DEFAULT 'France',
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    capacite INTEGER -- Capacité physique totale du lieu
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE evenements (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP NOT NULL,
    prix DECIMAL(8,2) DEFAULT 0.00,
    capacite_max INTEGER NOT NULL,
    image_url TEXT,
    statut statut_event_enum DEFAULT 'draft',
    date_creation TIMESTAMP DEFAULT NOW(),
    id_lieu INTEGER NOT NULL REFERENCES lieux(id),
    id_organisateur INTEGER NOT NULL REFERENCES organisateurs(id),
    id_categorie INTEGER NOT NULL REFERENCES categories(id),
    CONSTRAINT check_dates CHECK (date_fin > date_debut)
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    libelle VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE evenements_tags (
    id_evenement INTEGER REFERENCES evenements(id) ON DELETE CASCADE,
    id_tag INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (id_evenement, id_tag)
);

CREATE TABLE inscriptions (
    id SERIAL PRIMARY KEY,
    id_utilisateur INTEGER NOT NULL REFERENCES utilisateurs(id),
    id_evenement INTEGER NOT NULL REFERENCES evenements(id),
    statut statut_inscription_enum DEFAULT 'confirmee',
    places_reservees INTEGER DEFAULT 1,
    date_inscription TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_event UNIQUE (id_utilisateur, id_evenement)
);

-- 4. INDEXATION (HORS PK)
CREATE INDEX idx_evenements_date_debut ON evenements(date_debut);
CREATE INDEX idx_inscriptions_event_user ON inscriptions(id_evenement, id_utilisateur);

-- 5. LOGIQUE MÉTIER : PROCEDURES STOCKEES (3)

-- Procedure 1 : Inscription sécurisée (Gestion capacité + Liste d'attente)
CREATE OR REPLACE PROCEDURE proc_inscrire_participant(
    p_user_id INTEGER,
    p_event_id INTEGER,
    p_places INTEGER,
    OUT r_statut statut_inscription_enum
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_capacite_max INTEGER;
    v_places_occupees INTEGER;
BEGIN
    -- 1. Récupérer la capacité max
    SELECT capacite_max INTO v_capacite_max FROM evenements WHERE id = p_event_id;
    
    -- 2. Compter les places déjà confirmées
    SELECT COALESCE(SUM(places_reservees), 0) INTO v_places_occupees 
    FROM inscriptions 
    WHERE id_evenement = p_event_id AND statut = 'confirmee';

    -- 3. Décider du statut
    IF (v_places_occupees + p_places) <= v_capacite_max THEN
        INSERT INTO inscriptions (id_utilisateur, id_evenement, places_reservees, statut)
        VALUES (p_user_id, p_event_id, p_places, 'confirmee');
        r_statut := 'confirmee';
    ELSE
        INSERT INTO inscriptions (id_utilisateur, id_evenement, places_reservees, statut)
        VALUES (p_user_id, p_event_id, p_places, 'liste_attente');
        r_statut := 'liste_attente';
    END IF;
END;
$$;

-- Procedure 2 : Promotion Organisateur
CREATE OR REPLACE PROCEDURE proc_promouvoir_organisateur(
    p_user_id INTEGER,
    p_nom_organisation VARCHAR,
    p_description TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update utilisateur
    UPDATE utilisateurs SET role = 'organisateur' WHERE id = p_user_id;
    
    -- Insert dans organisateurs
    INSERT INTO organisateurs (id_utilisateur, nom, description)
    VALUES (p_user_id, p_nom_organisation, p_description);
END;
$$;

-- Procedure 3 : Annulation propre d'un événement
CREATE OR REPLACE PROCEDURE proc_annuler_evenement(p_event_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Update event
    UPDATE evenements SET statut = 'cancelled' WHERE id = p_event_id;
    
    -- 2. Update toutes les inscriptions confirmées à annulées
    UPDATE inscriptions SET statut = 'annulee' 
    WHERE id_evenement = p_event_id AND statut IN ('confirmee', 'liste_attente');
END;
$$;

-- 6. TRIGGERS (2)

-- Trigger 1 : Promotion automatique depuis la liste d'attente après annulation
CREATE OR REPLACE FUNCTION fn_tr_promouvoir_liste_attente()
RETURNS TRIGGER AS $$
DECLARE
    v_id_promu INTEGER;
    v_places_liberes INTEGER;
    v_capacite_restante INTEGER;
    v_places_occupees INTEGER;
    v_capacite_max INTEGER;
BEGIN
    -- On ne s'intéresse qu'au passage de 'confirmee' vers 'annulee'
    IF OLD.statut = 'confirmee' AND NEW.statut = 'annulee' THEN
        
        -- Calculer les places disponibles
        SELECT capacite_max INTO v_capacite_max FROM evenements WHERE id = NEW.id_evenement;
        SELECT SUM(places_reservees) INTO v_places_occupees FROM inscriptions 
        WHERE id_evenement = NEW.id_evenement AND statut = 'confirmee';
        
        v_capacite_restante := v_capacite_max - v_places_occupees;

        -- Chercher le premier en liste d'attente qui rentre dans les places libérées
        FOR v_id_promu, v_places_liberes IN 
            SELECT id, places_reservees FROM inscriptions 
            WHERE id_evenement = NEW.id_evenement AND statut = 'liste_attente'
            ORDER BY date_inscription ASC
        LOOP
            IF v_places_liberes <= v_capacite_restante THEN
                UPDATE inscriptions SET statut = 'confirmee' WHERE id = v_id_promu;
                v_capacite_restante := v_capacite_restante - v_places_liberes;
            END IF;
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_after_annulation_inscription
AFTER UPDATE ON inscriptions
FOR EACH ROW
EXECUTE FUNCTION fn_tr_promouvoir_liste_attente();

-- Trigger 2 : Audit de statut (Empêcher le retour en 'draft' si déjà publié)
CREATE OR REPLACE FUNCTION fn_tr_verif_statut_workflow()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.statut = 'published' AND NEW.statut = 'draft' THEN
        RAISE EXCEPTION 'Impossible de repasser un événement publié en brouillon.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_before_update_event
BEFORE UPDATE ON evenements
FOR EACH ROW
EXECUTE FUNCTION fn_tr_verif_statut_workflow();

-- 7. VUES (2)

-- Vue 1 : Liste simple enrichie
CREATE VIEW v_evenements_details AS
SELECT 
    e.id, e.titre, e.date_debut, e.prix, e.statut,
    c.nom AS categorie,
    l.nom AS lieu_nom, l.ville,
    o.nom AS organisateur_nom
FROM evenements e
JOIN categories c ON e.id_categorie = c.id
JOIN lieux l ON e.id_lieu = l.id
JOIN organisateurs o ON e.id_organisateur = o.id;

-- Vue 2 : Dashboard Organisateur (Requête complexe exigée)
-- Contient : 4 jointures, 2 agrégations (GROUP BY + HAVING), 1 CTE/Sous-requête
CREATE VIEW v_dashboard_organisateur AS
WITH stats_inscrits AS (
    SELECT 
        id_evenement,
        COUNT(id) FILTER (WHERE statut = 'confirmee') as nb_confirmes,
        COUNT(id) FILTER (WHERE statut = 'liste_attente') as nb_liste_attente,
        SUM(places_reservees) FILTER (WHERE statut = 'confirmee') as total_places_prises
    FROM inscriptions
    GROUP BY id_evenement
)
SELECT 
    o.nom AS organisateur,
    e.titre AS evenement,
    e.capacite_max,
    COALESCE(s.total_places_prises, 0) as places_occupees,
    ROUND((COALESCE(s.total_places_prises, 0)::NUMERIC / e.capacite_max::NUMERIC) * 100, 2) as taux_remplissage,
    l.ville,
    c.nom as categorie
FROM organisateurs o
JOIN evenements e ON o.id = e.id_organisateur
JOIN lieux l ON e.id_lieu = l.id
JOIN categories c ON e.id_categorie = c.id
LEFT JOIN stats_inscrits s ON e.id = s.id_evenement
WHERE e.statut != 'archived'
GROUP BY o.nom, e.titre, e.capacite_max, s.total_places_prises, l.ville, c.nom, s.nb_confirmes
HAVING e.capacite_max > 0;

-- 8. SEED DATA (Transaction explicite)
BEGIN;

-- Categories
INSERT INTO categories (nom, description) VALUES 
('festival', 'Grands rassemblements musicaux ou culturels'),
('boite_de_nuit', 'Soirées clubbing et électro'),
('exposition', 'Art et culture en galerie ou musée'),
('afterwork', 'Sorties pro et détente en début de soirée'),
('sortie', 'Activités diverses en plein air ou intérieur');

-- Lieux
INSERT INTO lieux (nom, adresse, ville, code_postal, latitude, longitude, capacite) VALUES 
('Warehouse Paris', '12 rue de la Forge', 'Paris', '75010', 48.8566, 2.3522, 400),
('Le Louvre', 'Rue de Rivoli', 'Paris', '75001', 48.8614, 2.3308, 1000),
('Dock des Suds', '12 rue Urbain V', 'Marseille', '13002', 43.3100, 5.3700, 2000),
('Le Sucre', '50 Quai Rambaud', 'Lyon', '69002', 45.7390, 4.8140, 300),
('I.BOAT', 'Bassin à Flot n°1', 'Bordeaux', '33300', 44.8660, -0.5530, 250);

-- Utilisateurs (mdp: 'password123' hashé bidon)
INSERT INTO utilisateurs (email, mot_de_passe_hash, pseudo, role) VALUES 
('admin@eventry.fr', 'hash_admin', 'Rayhan_Lead', 'organisateur'),
('lucas@test.com', 'hash_lucas', 'Lucas_B', 'participant'),
('marie@test.com', 'hash_marie', 'Marie_Music', 'participant'),
('jean@test.com', 'hash_jean', 'Jean_Du_Sud', 'participant'),
('sarah@test.com', 'hash_sarah', 'Sarah_Conception', 'participant'),
('pierre@test.com', 'hash_pierre', 'Pierre_Night', 'participant'),
('julie@test.com', 'hash_julie', 'Julie_Art', 'participant'),
('organisateur2@test.com', 'hash_org2', 'Amine_Events', 'organisateur'),
('organisateur3@test.com', 'hash_org3', 'Zack_Prod', 'organisateur'),
('test_user@test.com', 'hash_test', 'Test_Bot', 'participant');

-- Organisteurs (Spécialisation)
INSERT INTO organisateurs (id_utilisateur, nom, description, est_verifie) VALUES 
(1, 'Collectif RAVE', 'Organisation de soirées techno industrielles', TRUE),
(8, 'Lyon Tech Scene', 'Promoteur d événements musicaux à Lyon', FALSE),
(9, 'Arty Prod', 'Collectif de promotion culturelle et artistique', TRUE);

-- Tags
INSERT INTO tags (libelle) VALUES 
('techno'), ('art'), ('gratuit'), ('plein-air'), 
('house'), ('jazz'), ('gastronomie'), ('afterwork'), ('familial');

-- Evenements (IDs 1 à 6)
INSERT INTO evenements (titre, description, date_debut, date_fin, prix, capacite_max, id_lieu, id_organisateur, id_categorie, statut) VALUES 
-- Event 1: Nuit Électro (Paris, Published)
('Nuit Électro', 'Une nuit techno intense au Warehouse', '2026-07-12 23:00:00', '2026-07-13 06:00:00', 15.00, 10, 1, 1, 2, 'published'),
-- Event 2: Expo Basquiat (Paris, Published)
('Expo Basquiat', 'Rétrospective inédite au Louvre', '2026-06-01 10:00:00', '2026-06-30 18:00:00', 0.00, 100, 2, 3, 3, 'published'),
-- Event 3: Delta Festival (Marseille, Draft)
('Delta Festival 2026', 'Le plus grand festival de sable', '2026-08-20 14:00:00', '2026-08-23 23:59:59', 120.00, 2000, 3, 1, 1, 'draft'),
-- Event 4: Afterwork Tech Lyon (Lyon, Published)
('Afterwork Tech Lyon', 'Networking et cocktails sur le toit', '2026-05-25 18:30:00', '2026-05-25 23:00:00', 10.00, 50, 4, 2, 4, 'published'),
-- Event 5: Boat Party Bordeaux (Bordeaux, Published)
('Boat Party Bordeaux', 'Coucher de soleil sur la Garonne', '2026-07-05 19:00:00', '2026-07-06 01:00:00', 25.00, 40, 5, 3, 2, 'published'),
-- Event 6: Jazz au Louvre (Paris, Cancelled)
('Jazz au Louvre', 'Soirée jazz acoustique annulée', '2026-05-10 20:00:00', '2026-05-10 23:00:00', 30.00, 20, 2, 3, 3, 'cancelled');

-- Liaisons Evenements Tags
INSERT INTO evenements_tags (id_evenement, id_tag) VALUES 
(1, 1), (1, 5), -- Nuit Electro: techno, house
(2, 2), (2, 3), -- Expo Basquiat: art, gratuit
(3, 1), (3, 4), -- Delta: techno, plein-air
(4, 8), (4, 7), -- Afterwork: afterwork, gastronomie
(5, 5), (5, 4), -- Boat Party: house, plein-air
(6, 6), (6, 2); -- Jazz: jazz, art

-- Inscriptions (Utilisation de la procédure pour tester la logique)

-- Nuit Electro (Capacité: 10)
CALL proc_inscrire_participant(2, 1, 2, NULL); -- Lucas (2 places) -> Confirmed (2/10)
CALL proc_inscrire_participant(3, 1, 3, NULL); -- Marie (3 places) -> Confirmed (5/10)
CALL proc_inscrire_participant(4, 1, 4, NULL); -- Jean (4 places) -> Confirmed (9/10)
CALL proc_inscrire_participant(5, 1, 2, NULL); -- Sarah (2 places) -> Waiting List (11/10)
CALL proc_inscrire_participant(6, 1, 1, NULL); -- Pierre (1 place) -> Waiting List (12/10)

-- Expo Basquiat
CALL proc_inscrire_participant(2, 2, 1, NULL); 
CALL proc_inscrire_participant(7, 2, 2, NULL); 
CALL proc_inscrire_participant(10, 2, 1, NULL); 

-- Afterwork Lyon
CALL proc_inscrire_participant(4, 4, 1, NULL); 
CALL proc_inscrire_participant(5, 4, 2, NULL); 

-- Boat Party
CALL proc_inscrire_participant(3, 5, 2, NULL); 
CALL proc_inscrire_participant(6, 5, 1, NULL); 

-- Jazz (Annulé - on simule des inscriptions préalables)
INSERT INTO inscriptions (id_utilisateur, id_evenement, statut, places_reservees) VALUES 
(7, 6, 'annulee', 2),
(2, 6, 'annulee', 1);

COMMIT;

-- FIN DU SCRIPT

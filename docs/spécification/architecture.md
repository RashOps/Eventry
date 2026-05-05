# Architecture projet et politique

## Architecture du projet
Adoption du style monorepo pour une gestion plus simple et efficace du projet.

Eventry/
├── backend/                ← API REST (Python + FastAPI)
├── frontend/               ← Vitejs + React
├── db/
│   ├── sql/                ← scripts PostgreSQL
│   └── nosql/              ← scripts MongoDB
├── docker/                 ← Les Dockerfile front + back
├── docs/
│   ├── spécification/      ← Décision sur le projet (architecture + versionning git + naming-convention + ...)        
│   ├── schema-mcd-mld/     ← Schema MCD/MLD du projet    
│   ├── schema-uml/         ← Schema UML du projet
│   └── sujet/              ← Cahier des charges inital du projet
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md

## POLITIQUE D'UTILISATION DE L'IA (MANDATAIRE)
L'utilisation de l'IA (ChatGPT, Copilot, Cursor) est autorisée mais doit être **déclarée et justifiée**, sous peine de sanctions.

1.  **Traçabilité** : Tout code généré ou debuggé par IA doit être documenté.
2.  **Fichier dédié** : Nous maintiendrons un fichier `AI_LOGS.md` à la racine ou une section dans les PRs.
3.  **Format attendu par usage** : 
    *   Outil utilisé (ex: GPT-4).
    *   Prompt utilisé.
    *   Justification (ex: "Gain de temps sur la génération du squelette du controller").
    *   Adaptation (ex: "Modifié pour utiliser notre convention snake_case sur les variables BDD").

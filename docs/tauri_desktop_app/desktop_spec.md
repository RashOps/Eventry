# 📑 CAHIER DES CHARGES : INDUSTRIALISATION DESKTOP (TAURI)

---

## 1. Nouvelle Structure du Monorepo Évolutif

Pour intégrer Tauri sans polluer l'architecture actuelle et respecter le fonctionnement monorepo d'Eventry, le dossier `src-tauri` (le cœur en Rust de l'application desktop) sera encapsulé directement dans le répertoire `frontend/`. Cela permet à `bun` de piloter le pipeline de build web tout en laissant `cargo` gérer l'artillerie Windows.

```plaintext
Eventry/
├── .github/
│   └── workflows/
│       └── build-desktop.yml  ← NOUVEAU : Pipeline CI/CD de Release (.exe)
├── backend/                   ← API REST (Python + FastAPI)
├── frontend/                  ← Workspace Vite.js + React
│   ├── src/                   ← Code source de l'UI React
│   ├── src-tauri/             ← NOUVEAU : Cœur de l'application native Rust
│   │   ├── src/               ← Main.rs et commandes système
│   │   ├── capabilities/      ← NOUVEAU (Tauri v2) : Droits et permissions réseau
│   │   ├── Cargo.toml         ← Dépendances Rust du client léger
│   │   └── tauri.conf.json    ← Configuration globale de l'application de bureau
│   ├── package.json           ← Scripts de build Bun
│   └── vite.config.js         ← Configuration Vite adaptée pour Tauri
├── db/                        ← Scripts SQL & NoSQL
├── docker/                    ← Configuration de conteneurisation
├── docs/                      ← Spécifications et MCD
├── AI_LOGS.md                 ← Journal obligatoire d'utilisation de l'IA
└── global.json / mise.toml    ← Gestionnaire d'environnement global
```

---

## 2. Dépendances et Packages Requis

### Côté Frontend (`frontend/package.json`)

Ajout des outils CLI et des APIs de Tauri à l'écosystème `bun`.

- **Dépendances de développement :** `@tauri-apps/cli` (V2) pour orchestrer les builds.
- **Dépendances de production :** `@tauri-apps/api` pour interagir avec la fenêtre native si besoin (notifications, fenêtres).

```json
{
  "name": "eventry-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "@tauri-apps/api": "^2.0.0",
    "axios": "^1.x.x",
    "@tanstack/react-query": "^5.x.x",
    "react": "^18.x.x"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "vite": "^5.x.x"
  }
}
```

### Côté Rust (`frontend/src-tauri/Cargo.toml`)

Client léger → dépendances Rust minimales, compilation ultra-rapide sous **Rust 1.96.0**.

```toml
[package]
name        = "eventry-desktop"
version     = "0.1.0"
description = "Eventry Desktop Client"
authors     = ["Rayhan alias RashOps"]
edition     = "2021"

[build-dependencies]
tauri-build = { version = "2.0", features = [] }

[dependencies]
tauri      = { version = "2.0", features = [] }
serde      = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

---

## 3. Configuration de Sécurité & CORS (FastAPI backend)

L'application de bureau sert les fichiers web via `tauri://localhost` ou `http://tauri.localhost`. L'API FastAPI hébergée sur Hugging Face doit explicitement autoriser ces origines lors des **Preflight Requests**.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Eventry API")

# Configuration stricte des origines autorisées
origins = [
    "https://eventry.vercel.app",   # Frontend web de production
    "http://localhost:5173",        # Dev local (Vite)
    "tauri://localhost",            # Origine standard Tauri (Windows/macOS)
    "http://tauri.localhost",       # Alternative selon la version de WebView2
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)
```

---

## 4. Pipeline CI/CD : GitHub Actions

**Fichier :** `.github/workflows/build-desktop.yml`

Ce workflow s'exécute sur un runner Windows à chaque push sur `main`. Il exploite la mise en cache native de `mise`, `bun` et `cargo` pour optimiser les temps de build.

```yaml
name: Release Desktop Application

on:
  push:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup mise (Environment Manager)
        uses: jdx/mise-action@v2

      - name: Setup Bun Environment
        uses: oven-sh/setup-bun@v2
        with:
          bun-version: 1.3.10

      - name: Rust Cache Setup
        uses: swatinem/rust-cache@v2
        with:
          workspaces: "frontend/src-tauri -> target"

      - name: Install Frontend Dependencies
        run: |
          cd frontend
          bun install

      - name: Build Tauri Desktop Application (.exe)
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tagName:      eventry-v__VERSION__
          releaseName:  "Eventry v__VERSION__"
          releaseBody:  "Release automatisée du client léger Eventry pour Windows."
          releaseDraft: true
          prerelease:   false
          projectPath:  "./frontend"
```

---

## 📋 ROADMAP DU SPRINT : INDUSTRIALISATION DESKTOP

> **Durée cible :** 1 à 2 semaines

### [TASK-01] Initialisation et Synchronisation de l'Écosystème
**Priorité :** Haute | **Temps estimé :** 2h

- Se positionner dans `./frontend` et exécuter `bunx tauri init`.
- Renseigner les paramètres demandés :
  - **Window title :** `Eventry`
  - **Dist dir :** `../dist` (dossier de sortie du build Vite.js)
  - **Dev path :** `http://localhost:5173`

---

### [TASK-02] Injection des Variables d'Environnement de Production
**Priorité :** Haute | **Temps estimé :** 3h

Adapter le client Axios / React Query côté frontend. Si l'application tourne dans un contexte de bureau (détectable via `window.__TAURI_INTERNALS__`), l'URL de base d'Axios doit pointer vers l'API de production hébergée sur Hugging Face, et non vers un hôte local.

---

### [TASK-03] Durcissement des Politiques de Sécurité (CSP)
**Priorité :** Critique | **Temps estimé :** 4h

Configurer `frontend/src-tauri/tauri.conf.json`. Dans la section `security > csp`, restreindre les connexions réseau uniquement vers l'adresse de l'API Hugging Face afin d'éviter toute injection malveillante de scripts tiers (XSS).

---

### [TASK-04] Déploiement et Test du CORS sur le Backend Python
**Priorité :** Haute | **Temps estimé :** 2h

Mettre à jour l'API FastAPI avec le middleware CORS détaillé ci-dessus. Déployer la mise à jour sur Hugging Face via `uv`. Vérifier avec un client REST que les en-têtes `Access-Control-Allow-Origin` retournent correctement les origines Tauri.

---

### [TASK-05] Validation du Pipeline CI/CD sur GitHub
**Priorité :** Moyenne | **Temps estimé :** 4h

Pousser le workflow `.github/workflows/build-desktop.yml`. Surveiller l'exécution de l'action. Résoudre les éventuels problèmes liés au linker Windows et valider la bonne génération du fichier `.exe` d'installation dans les drafts de releases du dépôt.
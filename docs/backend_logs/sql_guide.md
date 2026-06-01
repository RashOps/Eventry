# 📘 Guide : Requêtage SQL Programmique avec SQLModel & SQLAlchemy

L'objectif de ce guide est d'apprendre à interagir avec PostgreSQL sans jamais écrire de chaînes de caractères SQL (`"SELECT * FROM..."`), en utilisant **SQLModel** (une surcouche de SQLAlchemy et Pydantic).

---

## 🚀 Pourquoi éviter le SQL Brut ?

1.  **Sécurité** : Protection native contre les **injections SQL**.
2.  **Auto-complétion** : Ton éditeur (VS Code, Cursor) connaît tes colonnes et suggère les noms.
3.  **Refactorisation** : Si tu renommes une colonne dans ton code, l'IDE peut mettre à jour toutes tes requêtes automatiquement.
4.  **Validation** : Les données récupérées sont automatiquement converties en objets Python typés.

---

## 1. Définir un Modèle (La Table)

Au lieu de `CREATE TABLE`, on définit une classe Python qui hérite de `SQLModel`.

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Utilisateur(SQLModel, table=True):
    __tablename__ = "utilisateurs" # Nom exact de la table SQL
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    pseudo: str = Field(unique=True)
    mot_de_passe_hash: str
    role: str = "participant"
    date_inscription: datetime = Field(default_factory=datetime.now)
```

---

## 2. Opérations CRUD (Programmiques)

### A. Créer (INSERT)
```python
from sqlmodel import Session
from src.utils.postegre_connexion import async_engine

async def create_user(new_user: Utilisateur):
    async with AsyncSession(async_engine) as session:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
```

### B. Lire (SELECT)
C'est ici que SQLModel brille. On utilise des fonctions Python pour filtrer.

```python
from sqlmodel import select

# 1. Récupérer TOUS les utilisateurs
statement = select(Utilisateur)
results = await session.execute(statement)
users = results.scalars().all()

# 2. Récupérer UN utilisateur par son email (Equivalent WHERE)
statement = select(Utilisateur).where(Utilisateur.email == "test@test.com")
result = await session.execute(statement)
user = result.scalar_one_or_none()

# 3. Filtrage complexe (Plusieurs conditions)
statement = (
    select(Utilisateur)
    .where(Utilisateur.role == "organisateur")
    .where(Utilisateur.est_actif == True)
    .order_by(Utilisateur.date_inscription.desc()) # Tri décroissant
    .limit(10) # Pagination
)
```

### C. Mettre à jour (UPDATE)
```python
async def update_pseudo(user_id: int, new_pseudo: str):
    statement = select(Utilisateur).where(Utilisateur.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one()
    
    user.pseudo = new_pseudo # On modifie l'objet Python
    session.add(user) # On notifie SQLModel du changement
    await session.commit()
```

### D. Supprimer (DELETE)
```python
async def delete_user(user_id: int):
    statement = select(Utilisateur).where(Utilisateur.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one()
    
    await session.delete(user)
    await session.commit()
```

---

## 3. Jointures (JOINS)

Fini les jointures manuelles complexes. Si tu as défini des relations :

```python
from sqlmodel import select

# Récupérer l'événement ET son lieu associé
statement = (
    select(Evenement, Lieu)
    .join(Lieu)
    .where(Lieu.ville == "Paris")
)
results = await session.execute(statement)
for event, lieu in results:
    print(f"L'event {event.titre} se passe à {lieu.nom}")
```

---

## 🧪 Comparaison Directe

| Action | SQL Brut (Actuel) | SQLModel (Recommandé) |
| :--- | :--- | :--- |
| **Sélection** | `"SELECT * FROM users WHERE id = 1"` | `select(User).where(User.id == 1)` |
| **Erreur de frappe** | Détectée à l'exécution (Crash) | Détectée à l'écriture (Souligné en rouge) |
| **Injection SQL** | Risque élevé (si f-string) | Impossible par design |
| **Type de retour** | Liste de tuples (Besoin de transformer) | Objets Python prêts à l'emploi |

---
*Ce guide a été rédigé pour aider l'équipe Eventry à monter en compétence sur l'ORM asynchrone.*

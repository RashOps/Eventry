from enum import Enum

class RoleEnum(str, Enum):
    visiteur = "visiteur"
    participant = "participant"
    organisateur = "organisateur"

class StatutEventEnum(str, Enum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"
    archived = "archived"

class StatutInscriptionEnum(str, Enum):
    confirmee = "confirmee"
    liste_attente = "liste_attente"
    annulee = "annulee"

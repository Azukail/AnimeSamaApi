# AnimeSamaApi - Version Corrigée (Mars 2026)

API REST pour accéder au contenu d'anime-sama avec **détection automatique de l'URL active**.

## 🔧 Corrections apportées

- ✅ **URL dynamique** : Détecte automatiquement l'URL active d'anime-sama (`.tv`, `.to`, `.si`, etc.)
- ✅ **Portail de redirection** : Utilise `anime-sama.pw` pour trouver la bonne URL
- ✅ **Fallback intelligent** : Teste plusieurs URLs en cas d'échec
- ✅ **CORS activé** : Prêt pour une utilisation depuis un frontend web
- ✅ **Resolvers HTTP** : Extraction des liens vidéo sans navigateur headless

## 📦 Installation

```bash
# Cloner le projet
git clone <votre-repo>
cd AnimeSamaApi

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
python main.py
```

## 🚀 Utilisation rapide

```python
from main import Api

# Lancer sur le port par défaut (5000)
Api.launch()

# Ou avec configuration personnalisée
Api.launch(port=8080, ip="0.0.0.0", debug_state=False)
```

## 📡 Endpoints de l'API

### Test de l'API
```
GET /
```

### Catalogue complet
```
GET /api/getAllAnime
GET /api/getAllAnime?r=True  # Force le refresh
```

### Charger les données locales
```
GET /api/loadBaseAnimeData
```

### Rechercher un anime
```
GET /api/getSerchAnime?q=Frieren&l=5
```

### Informations sur un anime (saisons)
```
GET /api/getInfoAnime?q=Demon%20Slayer
```

### Saison spécifique
```
GET /api/getSpecificAnime?q=One%20Piece&s=saison1&v=vostfr
```

### Liens de streaming
```
GET /api/getAnimeLink?n=Spy%20x%20Family&s=saison1&v=vostfr
```

### URL active d'anime-sama
```
GET /api/getAnimeSamaURL
GET /api/refreshURL  # Force la redécouverte
```

## 🌐 Intégration Frontend

L'API est prête pour être utilisée avec un frontend. Exemple avec JavaScript :

```javascript
// Rechercher un anime
const response = await fetch('http://localhost:5000/api/getSerchAnime?q=Frieren&l=5');
const animes = await response.json();

// Obtenir les liens de streaming
const links = await fetch(`http://localhost:5000/api/getAnimeLink?n=${animes[0].title}&s=saison1`);
const episodes = await links.json();
```

## 📁 Structure du projet

```
AnimeSamaApi/
├── main.py              # Point d'entrée
├── requirements.txt     # Dépendances
├── README.md
├── src/
│   ├── __init__.py
│   ├── api.py           # Routes Flask
│   ├── backend.py       # Logique métier
│   └── utils/
│       ├── __init__.py
│       ├── config.py    # Configuration & URL dynamique
│       └── resolvers.py # Extraction liens vidéo
└── data/
    └── json/
        └── AnimeInfo.json  # Cache du catalogue
```

## ⚠️ Notes importantes

1. **Première utilisation** : Appelez `/api/getAllAnime` pour construire le cache local
2. **Changement d'URL** : L'API détecte automatiquement la nouvelle URL, mais vous pouvez forcer avec `/api/refreshURL`
3. **Blocage FAI** : Si vous êtes en France, certains FAI bloquent l'accès. Utilisez un VPN ou changez vos DNS.

## 🔒 Déploiement

Pour un déploiement en production :

```python
from main import Api

Api.launch(
    port=5000,
    ip="0.0.0.0",      # Écoute sur toutes les interfaces
    debug_state=False,  # Désactiver le debug
    reload_status=False # Désactiver le reloader
)
```

Ou avec Gunicorn :

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.api:app"
```

## 📜 Licence

GPL-3.0 (basé sur le projet original de TMCooper)

"""
API Flask pour AnimeSama
Routes REST pour accéder aux fonctionnalités
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from .backend import Cardinal

# Création de l'application Flask
app = Flask(__name__)
CORS(app)  # Activer CORS pour les requêtes cross-origin


class Yui:
    """Wrapper pour l'application Flask"""
    app = app


@app.route('/')
def index():
    """Route de test"""
    q = request.args.get('q', '')
    return jsonify({
        "Bonjours": "Je suis une API pour anime-sama",
        "Valeur q": q,
        "Cardinal value": Cardinal.test(),
        "URL active": Cardinal.get_base_url()
    })


@app.route('/api/getAllAnime')
def get_all_anime():
    """
    Récupère le catalogue complet des animes
    
    Params:
        r (optionnel): True pour forcer le refresh
    """
    force_refresh = request.args.get('r', 'False').lower() == 'true'
    result = Cardinal.getAllAnime(force_refresh=force_refresh)
    return jsonify({"message": result})


@app.route('/api/loadBaseAnimeData')
def load_base_anime_data():
    """Retourne le contenu du fichier AnimeInfo.json"""
    data = Cardinal.loadBaseAnimeData()
    return jsonify(data)


@app.route('/api/getSerchAnime')
def get_search_anime():
    """
    Recherche d'animes par nom
    
    Params:
        q (obligatoire): Terme de recherche
        l (optionnel): Limite de résultats (défaut: 5)
    """
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Paramètre 'q' manquant"}), 400
    
    limit = request.args.get('l', '5')
    try:
        limit = int(limit)
    except ValueError:
        limit = 5
    
    results = Cardinal.searchAnime(query, limit=limit)
    return jsonify(results)


@app.route('/api/getInfoAnime')
def get_info_anime():
    """
    Récupère les saisons disponibles pour un anime
    
    Params:
        q (obligatoire): Nom de l'anime
    """
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Paramètre 'q' manquant"}), 400
    
    results = Cardinal.getInfoAnime(query)
    return jsonify(results)


@app.route('/api/getSpecificAnime')
def get_specific_anime():
    """
    Récupère une saison spécifique
    
    Params:
        q (obligatoire): Nom de l'anime
        s (optionnel): Saison (défaut: saison1)
        v (optionnel): Version (défaut: vostfr)
    """
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Paramètre 'q' manquant"}), 400
    
    season = request.args.get('s', 'saison1')
    version = request.args.get('v', 'vostfr')
    
    result = Cardinal.getSpecificAnime(query, season=season, version=version)
    return jsonify(result)


@app.route('/api/getAnimeLink')
def get_anime_link():
    """
    Récupère les liens de streaming pour une saison
    
    Params:
        n (obligatoire): Nom de l'anime
        s (optionnel): Saison (défaut: saison1)
        v (optionnel): Version (défaut: vostfr)
    """
    name = request.args.get('n')
    
    if not name:
        return jsonify({"error": "Paramètre 'n' manquant"}), 400
    
    season = request.args.get('s', 'saison1')
    version = request.args.get('v', 'vostfr')
    
    results = Cardinal.getAnimeLinks(name, season=season, version=version)
    return jsonify(results)


@app.route('/api/getAnimeSamaURL')
def get_anime_sama_url():
    """Retourne l'URL active d'anime-sama"""
    return jsonify(Cardinal.getAnimeSamaURL())


@app.route('/api/refreshURL')
def refresh_url():
    """Force la redécouverte de l'URL active"""
    return jsonify(Cardinal.refreshURL())


# Route d'erreur 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Route non trouvée",
        "routes_disponibles": [
            "/",
            "/api/getAllAnime",
            "/api/loadBaseAnimeData",
            "/api/getSerchAnime?q=<query>&l=<limit>",
            "/api/getInfoAnime?q=<anime>",
            "/api/getSpecificAnime?q=<anime>&s=<saison>&v=<version>",
            "/api/getAnimeLink?n=<anime>&s=<saison>&v=<version>",
            "/api/getAnimeSamaURL",
            "/api/refreshURL"
        ]
    }), 404

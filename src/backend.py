"""
Backend - Logique métier pour le scraping d'anime-sama
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from pathlib import Path
from rapidfuzz import fuzz
from typing import Optional
from .utils.config import Config
from .utils.resolvers import resolve_url

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://anime-sama.tv/',
}

# Chemin vers le fichier de données
DATA_DIR = Path(__file__).parent.parent / "data" / "json"
ANIME_DATA_FILE = DATA_DIR / "AnimeInfo.json"


class Cardinal:
    """Classe principale pour les opérations de scraping"""
    
    @staticmethod
    def test():
        """Test de l'API"""
        return "Cardinal fonctionne correctement!"
    
    @staticmethod
    def get_base_url() -> str:
        """Récupère l'URL de base active"""
        return Config.get_active_url()
    
    @staticmethod
    def getAllAnime(force_refresh: bool = False) -> str:
        """
        Récupère le catalogue complet des animes et le sauvegarde en JSON
        
        Args:
            force_refresh: Force la mise à jour même si le fichier existe
        
        Returns:
            Message de confirmation
        """
        # Créer le dossier si nécessaire
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Vérifier si on doit rafraîchir
        if ANIME_DATA_FILE.exists() and not force_refresh:
            return "Base de données existante. Utilisez r=True pour forcer le refresh."
        
        base_url = Config.get_active_url()
        catalogue_url = f"{base_url}/catalogue/"
        
        try:
            all_animes = []
            page = 1
            
            while True:
                url = f"{catalogue_url}?page={page}" if page > 1 else catalogue_url
                print(f"[Cardinal] Scraping page {page}...")
                
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Trouver les cartes d'anime
                anime_cards = soup.select('.cardListAnime, .anime-card, [class*="card"]')
                
                if not anime_cards:
                    # Essayer d'autres sélecteurs
                    anime_cards = soup.find_all('a', href=re.compile(r'/catalogue/[^/]+/?$'))
                
                if not anime_cards:
                    break
                
                found_new = False
                for card in anime_cards:
                    try:
                        # Extraire le lien
                        if card.name == 'a':
                            link = card.get('href', '')
                        else:
                            link_tag = card.find('a', href=True)
                            link = link_tag['href'] if link_tag else ''
                        
                        if not link or '/catalogue/' not in link:
                            continue
                        
                        # Normaliser le lien
                        if not link.startswith('http'):
                            link = base_url + link
                        
                        # Extraire le titre
                        title_tag = card.find(['h2', 'h3', 'h4', '.title', '[class*="title"]'])
                        if title_tag:
                            title = title_tag.get_text(strip=True)
                        else:
                            # Extraire depuis l'URL
                            title = link.rstrip('/').split('/')[-1].replace('-', ' ').title()
                        
                        # Titre alternatif
                        alt_tag = card.find('.alt-title, [class*="alt"]')
                        alter_title = alt_tag.get_text(strip=True) if alt_tag else ""
                        
                        anime_data = {
                            "title": title,
                            "AlterTitle": alter_title,
                            "link": link
                        }
                        
                        # Éviter les doublons
                        if not any(a['link'] == link for a in all_animes):
                            all_animes.append(anime_data)
                            found_new = True
                            
                    except Exception as e:
                        print(f"[Cardinal] Erreur parsing carte: {e}")
                        continue
                
                if not found_new:
                    break
                    
                page += 1
                
                # Limite de sécurité
                if page > 500:
                    break
            
            # Sauvegarder
            with open(ANIME_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_animes, f, ensure_ascii=False, indent=2)
            
            return f"Récupération achevée: {len(all_animes)} animes"
            
        except Exception as e:
            return f"Erreur lors de la récupération: {str(e)}"
    
    @staticmethod
    def loadBaseAnimeData() -> list | dict:
        """Charge les données du fichier JSON local"""
        if not ANIME_DATA_FILE.exists():
            return {
                "error": "Fichier non existant",
                "message": "Veuillez d'abord appeler /api/getAllAnime"
            }
        
        with open(ANIME_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def searchAnime(query: str, limit: int = 5) -> list:
        """
        Recherche des animes par nom avec scoring intelligent
        
        Args:
            query: Terme de recherche
            limit: Nombre max de résultats
        
        Returns:
            Liste des résultats avec scores
        """
        data = Cardinal.loadBaseAnimeData()
        
        if isinstance(data, dict) and "error" in data:
            return []
        
        results = []
        query_lower = query.lower()
        query_len = len(query)
        
        for anime in data:
            title = anime.get('title', '')
            alter_title = anime.get('AlterTitle', '')
            link = anime.get('link', '')
            
            # Calculer le score avec RapidFuzz
            score_title = fuzz.token_set_ratio(query_lower, title.lower())
            score_alter = fuzz.token_set_ratio(query_lower, alter_title.lower()) if alter_title else 0
            
            # Prendre le meilleur score
            base_score = max(score_title, score_alter)
            
            # Bonus de spécificité
            title_len = len(title)
            if title_len > 0:
                ratio = query_len / title_len
                if 0.9 <= ratio <= 1.1:
                    base_score += 10
                elif ratio < 0.5:
                    base_score -= 15
            
            # Match exact
            if query_lower == title.lower() or query_lower == alter_title.lower():
                base_score = 100
            
            # Seuil minimum
            if base_score >= 75:
                results.append({
                    "title": title,
                    "lien": link,
                    "score": min(base_score, 100)
                })
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    @staticmethod
    def getInfoAnime(anime_name: str) -> list:
        """
        Récupère les saisons disponibles pour un anime
        
        Args:
            anime_name: Nom de l'anime
        
        Returns:
            Liste des saisons avec URLs
        """
        # D'abord rechercher l'anime
        search_results = Cardinal.searchAnime(anime_name, limit=1)
        
        if not search_results:
            return []
        
        anime_url = search_results[0]['lien']
        anime_title = search_results[0]['title']
        
        try:
            response = requests.get(anime_url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            seasons = []
            
            # Chercher les liens de saisons
            season_links = soup.find_all('a', href=re.compile(r'saison\d+|season\d+|film|ova|special', re.I))
            
            if not season_links:
                # Essayer d'autres patterns
                season_links = soup.select('[href*="saison"], [href*="season"], .season-link')
            
            seen_urls = set()
            
            for link in season_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Normaliser l'URL
                if not href.startswith('http'):
                    href = anime_url.rstrip('/') + '/' + href.lstrip('/')
                
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Extraire le nom de la saison
                link_text = link.get_text(strip=True)
                if not link_text:
                    # Extraire depuis l'URL
                    match = re.search(r'(saison\d+|season\d+|film|ova|special)', href, re.I)
                    link_text = match.group(1).title() if match else "Saison"
                
                seasons.append({
                    "base_url": anime_url,
                    "title": anime_title,
                    "Saison": link_text,
                    "url": href
                })
            
            # Si aucune saison trouvée, essayer de créer saison1 par défaut
            if not seasons:
                seasons.append({
                    "base_url": anime_url,
                    "title": anime_title,
                    "Saison": "Saison 1",
                    "url": anime_url.rstrip('/') + '/saison1/'
                })
            
            return seasons
            
        except Exception as e:
            print(f"[Cardinal] Erreur getInfoAnime: {e}")
            return []
    
    @staticmethod
    def getSpecificAnime(anime_name: str, season: str = "saison1", version: str = "vostfr") -> dict:
        """
        Récupère une saison spécifique
        
        Args:
            anime_name: Nom de l'anime
            season: Saison (ex: "saison1", "saison2")
            version: Version ("vostfr" ou "vf")
        
        Returns:
            Informations de la saison
        """
        search_results = Cardinal.searchAnime(anime_name, limit=1)
        
        if not search_results:
            return {"error": "Anime non trouvé"}
        
        anime_url = search_results[0]['lien']
        anime_title = search_results[0]['title']
        
        # Construire l'URL de la saison
        season_url = f"{anime_url.rstrip('/')}/{season}/{version}"
        
        return {
            "base_url": anime_url,
            "title": anime_title,
            "Saison": season.title().replace("Saison", "Saison "),
            "url": season_url
        }
    
    @staticmethod
    def getAnimeLinks(anime_name: str, season: str = "saison1", version: str = "vostfr") -> list:
        """
        Récupère tous les liens de streaming pour une saison
        
        Args:
            anime_name: Nom de l'anime
            season: Saison
            version: Version (vostfr/vf)
        
        Returns:
            Liste des épisodes avec liens
        """
        specific = Cardinal.getSpecificAnime(anime_name, season, version)
        
        if "error" in specific:
            return []
        
        season_url = specific['url']
        
        try:
            response = requests.get(season_url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                # Essayer sans la version
                season_url_alt = f"{specific['base_url'].rstrip('/')}/{season}/"
                response = requests.get(season_url_alt, headers=HEADERS, timeout=15)
                if response.status_code != 200:
                    return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            episodes = []
            
            # Chercher les scripts contenant les épisodes
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string:
                    # Pattern pour les tableaux d'épisodes
                    patterns = [
                        r'eps\d*\s*=\s*\[(.*?)\];',
                        r'episodes\s*=\s*\[(.*?)\];',
                        r'var\s+\w+\s*=\s*\[(.*?)\];',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, script.string, re.DOTALL)
                        for match in matches:
                            # Extraire les URLs
                            urls = re.findall(r'["\']([^"\']+)["\']', match)
                            for i, url in enumerate(urls):
                                if url.startswith('http') and 'embed' in url.lower():
                                    # Résoudre vers le lien direct
                                    direct_url = resolve_url(url)
                                    episodes.append({
                                        "episode": i,
                                        "url": direct_url or url,
                                        "iframe_url": url
                                    })
            
            # Alternative: chercher les iframes directement
            if not episodes:
                iframes = soup.find_all('iframe', src=True)
                for i, iframe in enumerate(iframes):
                    src = iframe.get('src', '')
                    if src:
                        direct_url = resolve_url(src)
                        episodes.append({
                            "episode": i,
                            "url": direct_url or src,
                            "iframe_url": src
                        })
            
            # Alternative: chercher les boutons d'épisodes
            if not episodes:
                ep_buttons = soup.select('[data-episode], .episode-btn, [class*="episode"]')
                for i, btn in enumerate(ep_buttons):
                    ep_url = btn.get('data-url') or btn.get('href', '')
                    if ep_url:
                        direct_url = resolve_url(ep_url)
                        episodes.append({
                            "episode": i,
                            "url": direct_url or ep_url
                        })
            
            # Trier par numéro d'épisode
            episodes.sort(key=lambda x: x.get('episode', 0))
            
            return episodes
            
        except Exception as e:
            print(f"[Cardinal] Erreur getAnimeLinks: {e}")
            return []
    
    @staticmethod
    def getAnimeSamaURL() -> dict:
        """Retourne l'URL active d'anime-sama"""
        return {"url": Config.get_active_url()}
    
    @staticmethod
    def refreshURL() -> dict:
        """Force la redécouverte de l'URL active"""
        new_url = Config.reset_url()
        return {"url": new_url, "message": "URL rafraîchie"}

"""
Configuration globale de l'API AnimeSama
"""
import requests
from bs4 import BeautifulSoup
import re

class Config:
    """Configuration globale"""
    IP = "127.0.0.1"
    PORT = 5000
    
    # URLs de fallback (mise à jour Mars 2026)
    FALLBACK_URLS = [
        "https://anime-sama.tv",
        "https://anime-sama.to", 
        "https://anime-sama.si",
        "https://anime-sama.org",
    ]
    
    # URL du portail de redirection officiel
    REDIRECT_PORTAL = "https://anime-sama.pw"
    
    # URL active (sera mise à jour dynamiquement)
    _active_url = None
    
    @classmethod
    def get_active_url(cls):
        """Récupère l'URL active d'anime-sama"""
        if cls._active_url:
            return cls._active_url
        
        # Tenter de récupérer depuis le portail de redirection
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(cls.REDIRECT_PORTAL, headers=headers, timeout=10)
            if response.status_code == 200:
                # Chercher l'URL active dans la page
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if 'anime-sama' in href and href.startswith('http'):
                        cls._active_url = href.rstrip('/')
                        return cls._active_url
        except Exception as e:
            print(f"[Config] Erreur portail redirection: {e}")
        
        # Fallback: tester les URLs connues
        for url in cls.FALLBACK_URLS:
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    cls._active_url = url
                    return cls._active_url
            except:
                continue
        
        # Dernier recours
        cls._active_url = cls.FALLBACK_URLS[0]
        return cls._active_url
    
    @classmethod
    def reset_url(cls):
        """Force la redécouverte de l'URL"""
        cls._active_url = None
        return cls.get_active_url()


class Utils:
    """Utilitaires divers"""
    
    @staticmethod
    def hashCheck():
        """Vérification de hash (placeholder)"""
        pass
    
    @staticmethod
    def gitCheck():
        """Vérification git (placeholder)"""
        pass

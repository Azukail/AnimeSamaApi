"""
Resolvers pour extraire les liens de streaming directs
Supporte: Sibnet, Vidmoly, SendVid, VidCDN, etc.
"""
import requests
import re
from urllib.parse import urlparse, urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}


def resolve_sibnet(url: str) -> str | None:
    """Résout les liens Sibnet pour obtenir le MP4 direct"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        # Patterns pour trouver le lien vidéo
        patterns = [
            r'player\.src\s*\(\s*\[\s*\{\s*src:\s*["\']([^"\']+)["\']',
            r'src:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'file:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'video\.src\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                video_url = match.group(1)
                if not video_url.startswith('http'):
                    video_url = urljoin('https://video.sibnet.ru', video_url)
                return video_url
                
        return None
    except Exception as e:
        print(f"[Sibnet] Erreur: {e}")
        return None


def resolve_vidmoly(url: str) -> str | None:
    """Résout les liens Vidmoly"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        # Chercher le fichier m3u8 ou mp4
        patterns = [
            r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'sources:\s*\[\s*\{\s*file:\s*["\']([^"\']+)["\']',
            r'src:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']+master\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        
        return None
    except Exception as e:
        print(f"[Vidmoly] Erreur: {e}")
        return None


def resolve_sendvid(url: str) -> str | None:
    """Résout les liens SendVid"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        patterns = [
            r'source\s+src=["\']([^"\']+\.mp4[^"\']*)["\']',
            r'video_source:\s*["\']([^"\']+)["\']',
            r'og:video"\s+content="([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        
        return None
    except Exception as e:
        print(f"[SendVid] Erreur: {e}")
        return None


def resolve_smoothpre(url: str) -> str | None:
    """Résout les liens SmoothPre/Smoothprev"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        patterns = [
            r'file:\s*["\']([^"\']+)["\']',
            r'sources:\s*\[\{\s*src:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        
        return None
    except Exception as e:
        print(f"[SmoothPre] Erreur: {e}")
        return None


def resolve_vidcdn(url: str) -> str | None:
    """Résout les liens VidCDN / Vidsrc"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        patterns = [
            r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        
        return None
    except Exception as e:
        print(f"[VidCDN] Erreur: {e}")
        return None


def resolve_generic(url: str) -> str | None:
    """Resolver générique pour sources inconnues"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        
        # Patterns génériques pour trouver des liens vidéo
        patterns = [
            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']+\.mp4[^"\']*)["\']',
            r'file:\s*["\']([^"\']+)["\']',
            r'source:\s*["\']([^"\']+)["\']',
            r'src:\s*["\']([^"\']+(?:\.mp4|\.m3u8)[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                # Filtrer les URLs valides
                if any(ext in match.lower() for ext in ['.mp4', '.m3u8', 'video', 'stream']):
                    if 'javascript' not in match.lower() and 'css' not in match.lower():
                        return match
        
        return None
    except Exception as e:
        print(f"[Generic] Erreur: {e}")
        return None


def resolve_url(url: str) -> str | None:
    """
    Résout automatiquement une URL de lecteur vers le lien direct
    
    Args:
        url: URL du lecteur (iframe src)
    
    Returns:
        URL directe du fichier vidéo ou None
    """
    if not url:
        return None
    
    url_lower = url.lower()
    
    # Router vers le bon resolver
    if 'sibnet' in url_lower:
        return resolve_sibnet(url)
    elif 'vidmoly' in url_lower:
        return resolve_vidmoly(url)
    elif 'sendvid' in url_lower:
        return resolve_sendvid(url)
    elif 'smoothpre' in url_lower or 'smoothprev' in url_lower:
        return resolve_smoothpre(url)
    elif 'vidcdn' in url_lower or 'vidsrc' in url_lower:
        return resolve_vidcdn(url)
    else:
        return resolve_generic(url)


# Liste des domaines supportés
SUPPORTED_HOSTS = [
    'sibnet.ru',
    'video.sibnet.ru',
    'vidmoly.to',
    'vidmoly.me',
    'sendvid.com',
    'sendvid.net',
    'smoothpre.com',
    'vidcdn.co',
    'vidsrc.me',
]


def is_supported_host(url: str) -> bool:
    """Vérifie si l'hôte est supporté"""
    try:
        parsed = urlparse(url)
        return any(host in parsed.netloc for host in SUPPORTED_HOSTS)
    except:
        return False

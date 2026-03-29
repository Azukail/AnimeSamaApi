"""
AnimeSamaApi - Point d'entrée principal
Version corrigée avec URL dynamique (Mars 2026)
"""

try:
    from .src.api import Yui
    from .src.utils.config import Config, Utils
except ImportError:
    from src.api import Yui
    from src.utils.config import Config, Utils


class Api:
    """Classe principale pour lancer l'API"""
    
    @staticmethod
    def launch(port=5000, ip="0.0.0.0", debug_state: bool = True, reload_status: bool = True):
        """
        Lance l'application avec les paramètres spécifiés.
        
        Args:
            port (int): Port sur lequel l'application sera accessible. Default 5000.
            ip (str): Adresse IP d'écoute. Default "0.0.0.0" (toutes les interfaces).
            debug_state (bool): Active le mode debug. Default True.
            reload_status (bool): Active le reloader automatique. Default True.
        """
        # Vérifications initiales
        Utils.hashCheck()
        Utils.gitCheck()
        
        # Configuration
        Config.IP = ip
        Config.PORT = port
        
        # Afficher l'URL active au démarrage
        active_url = Config.get_active_url()
        print(f"\n{'='*50}")
        print(f"AnimeSamaApi - Version Corrigée")
        print(f"{'='*50}")
        print(f"URL anime-sama active: {active_url}")
        print(f"API accessible sur: http://{ip}:{port}")
        print(f"{'='*50}\n")
        
        # Lancer le serveur Flask
        Yui.app.run(
            host=ip,
            port=port,
            debug=debug_state,
            use_reloader=reload_status
        )


if __name__ == "__main__":
    Api.launch()

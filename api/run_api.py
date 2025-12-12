"""
Script de démarrage pour l'API Flask.
Utilise les variables d'environnement pour la configuration.
"""
from app import create_app
from backend.src.config import Config

if __name__ == '__main__':
    app = create_app()
    print("="*60)
    print("Chip-and-Hole Detection API")
    print("="*60)
    print(f"Environnement: {Config.FLASK_ENV}")
    print(f"Debug: {Config.FLASK_DEBUG}")
    print(f"API disponible sur: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Documentation: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/")
    print(f"Health check: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/health")
    print("="*60)
    app.run(
        debug=Config.FLASK_DEBUG,
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT
    )


"""
Script pour télécharger les assets CDN en local.
À exécuter sur la machine avec accès Internet (ta machine),
puis copier le dossier static/ sur la machine cible.
"""
import os
import urllib.request
import ssl
 
# Désactiver la vérification SSL si nécessaire (certains réseaux corporatifs)
ssl._create_default_https_context = ssl._create_unverified_context
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_VENDOR = os.path.join(BASE_DIR, 'static', 'vendor')
 
ASSETS = {
    # TailwindCSS
    'tailwindcss.js': 'https://cdn.tailwindcss.com',
    # ECharts
    'echarts.min.js': 'https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js',
    # html2canvas
    'html2canvas.min.js': 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js',
    # xlsx
    'xlsx.full.min.js': 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
    # ApexCharts
    'apexcharts.min.js': 'https://cdn.jsdelivr.net/npm/apexcharts@3.44.0/dist/apexcharts.min.js',
    # marked
    'marked.min.js': 'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
    # Alpine.js
    'alpinejs.min.js': 'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js',
    # Leaflet CSS
    'leaflet.css': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    # Leaflet JS
    'leaflet.js': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
}
 
 
def download_file(url, dest_path):
    """Télécharge un fichier depuis une URL."""
    try:
        print(f"Téléchargement: {url}")
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(dest_path, 'wb') as f:
                f.write(response.read())
        print(f"  ✓ Sauvegardé: {dest_path}")
        return True
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return False
 
 
def main():
    # Créer le dossier vendor
    os.makedirs(STATIC_VENDOR, exist_ok=True)
    print(f"Dossier de destination: {STATIC_VENDOR}\n")
 
    success_count = 0
    for filename, url in ASSETS.items():
        dest_path = os.path.join(STATIC_VENDOR, filename)
        if download_file(url, dest_path):
            success_count += 1
        print()
 
    print(f"\n{'='*50}")
    print(f"Téléchargement terminé: {success_count}/{len(ASSETS)} fichiers")
    print(f"\nProchaines étapes:")
    print(f"1. Copier le dossier 'static/vendor/' sur la machine cible")
    print(f"2. Utiliser 'templates/base_local.html' au lieu de 'base.html'")
    print(f"   (ou renommer base.html -> base_cdn.html et base_local.html -> base.html)")
 
 
if __name__ == '__main__':
    main()
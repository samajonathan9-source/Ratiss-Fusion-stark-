#!/usr/bin/env bash
# setup_offline.sh — prépare RATIS-Fusion-stark- pour un runtime 100% offline.
#
# 1. Installe les dépendances Python.
# 2. Pré-cache le moteur Needle (libneedle.so, 14 Mo) depuis HuggingFace.
#    → après cela, l'inférence ne touche plus le réseau.
# 3. Installe espeak-ng pour le TTS offline (nécessite root).
#
# Usage : bash setup_offline.sh
set -e

echo "=== RATIS-Fusion-stark- : setup offline ==="

echo "[1/3] Installation des dépendances Python..."
pip install -r requirements.txt

echo "[2/3] Pré-cache du moteur Needle (14 Mo, une fois)..."
python -c "
import os, zipfile
from huggingface_hub import hf_hub_download
from needle.agent import fetch
cache = os.path.join(os.path.expanduser('~'), '.cache', 'cactus-needle', fetch.ENGINE_VERSION)
os.makedirs(cache, exist_ok=True)
lib = os.path.join(cache, fetch._lib_name())
if os.path.exists(lib):
    print(f'  moteur déjà caché : {lib}')
else:
    wheel = f'python/cactus_needle-{fetch.ENGINE_VERSION}-py3-none-manylinux2014_x86_64.whl'
    print(f'  téléchargement : {wheel}')
    path = hf_hub_download(repo_id=fetch.HF_REPO, filename=wheel, repo_type='model')
    with zipfile.ZipFile(path) as a:
        data = a.read('needle/' + fetch._lib_name())
    with open(lib, 'wb') as h:
        h.write(data)
    print(f'  moteur caché : {lib} ({len(data)} bytes)')
print('  → l\\'inférence est maintenant 100% offline.')
"

echo "[3/3] TTS offline (espeak-ng)..."
if command -v apt-get &>/dev/null; then
    sudo apt-get install -y espeak-ng 2>/dev/null && echo "  espeak-ng installé (TTS offline)" \
        || echo "  ATTENTION : espeak-ng non installé (gTTS fallback online sera utilisé)"
else
    echo "  apt-get non disponible — installez espeak-ng manuellement pour le TTS offline"
fi

echo ""
echo "=== Setup terminé. Test rapide : ==="
python -c "
import needle
@needle.tool
def hello(name: str):
    'Say hello to someone.'
    return {'greeting': f'Hello {name}!'}
agent = needle.Needle(tools=[hello])
r = agent.run('say hello to Jonathan')
print('Needle OK :', r.get('results'))
print('Confiance :', r.get('confidence'))
print('RAM :', r.get('peak_ram_mb'), 'Mo')
"

#!/usr/bin/env bash
set -e

echo "🔽 Descargando modelo desde Google Drive…"
# Instalamos gdown si no existe
pip install --no-cache-dir  v

# Usamos el ID de tu archivo de Drive:
#   https://drive.google.com/file/d/1vYDBecyjRa5-Z9uJVXmkNmjKec0gOlry/view
gdown --id 1vYDBecyjRa5-Z9uJVXmkNmjKec0gOlry -O ./model.pth

echo "✅ model.pth descargado en: $(pwd)/ViTImproved_trained.pth"

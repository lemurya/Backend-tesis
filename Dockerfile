# Usa la variante slim de Python
FROM python:3.10-slim

WORKDIR /app

# Copia y instala solo ruedas de CPU-only
COPY requirements.txt .
# Reemplaza torch por la versión CPU-only
RUN pip install --no-cache-dir \
    torch==2.0.1+cpu \
    torchvision==0.15.2+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt

# Copia todo tu código + script
COPY . .

# Descarga el modelo en tiempo de arranque y lanza uvicorn
CMD bash download_model.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT

FROM python:3.11-slim

WORKDIR /app

# Instala dependencias necesarias para SSH y curl
RUN apt-get update && apt-get install -y \
    openssh-client \
    curl \
 && apt-get clean

# Copia requirements e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script que descarga el modelo por SSH
COPY download_model.sh .

# Dale permisos de ejecución y ejecútalo
#RUN chmod +x download_model.sh && ./download_model.sh

# Copia el resto del código de tu app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Dockerfile pentru HR Contracte
FROM node:20-slim

# Instalare Python și pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Instalare python-docx
RUN pip3 install python-docx --break-system-packages

# Director aplicație
WORKDIR /app

# Copiere package.json și instalare dependințe Node
COPY package*.json ./
RUN npm install

# Copiere toate fișierele
COPY . .

# Port
EXPOSE 3000

# Start
CMD ["node", "server.js"]

FROM python:3.12.3-slim

# Instalacija LibreOffice i Jave
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-java-common \
    default-jre \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Radni direktorijum
WORKDIR /app

# Kopiraj requirements.txt i instaliraj Python zavisnosti
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopiraj ostatak projekta
COPY . .

# Dozvoli izvršavanje skripti
RUN chmod +x convert.sh
RUN chmod +x run.sh

# Podrazumevana komanda
ENTRYPOINT ["bash", "-c", "./run.sh"]

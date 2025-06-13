# 11_DOCKER.md

# Docker för Geometra AI

Detta dokument beskriver hur du paketerar och kör Geometra AI som en Docker-container. Vi går igenom hur du skapar en Dockerfile, bygger och testar containern lokalt samt integrerar Docker i CI/CD-pipelinen och deployment till Railway.

---

## 1. Varför Docker?

- Säkerställer att applikationen körs i en konsekvent miljö oavsett plattform
- Gör det enkelt att distribuera till molnleverantörer som Railway, DigitalOcean, AWS m.fl.
- Underlättar CI/CD genom att bygga versionerade images
- Isolerar beroenden och miljöinställningar

---

## 2. Dockerfile – Exempel

```dockerfile
# Använd officiell Python 3.11-image som bas
FROM python:3.11-slim

# Sätt arbetskatalog i containern
WORKDIR /app

# Kopiera dependenciesfiler först för att utnyttja cache
COPY requirements.txt .

# Installera Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera all övrig kod
COPY . .

# Exponera port som FastAPI använder (ska matcha PORT i .env)
EXPOSE 8000

# Sätt miljövariabler för produktion (kan överridas i Railway)
ENV LOG_DIR=logs
ENV ENV=production

# Starta FastAPI via Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
3. Bygga och köra containern lokalt
bash
Kopiera kod
# Bygg Docker-image (byt 'geometra-ai' till önskat namn)
docker build -t geometra-ai .

# Kör containern lokalt och mappa port 8000
docker run -p 8000:8000 --env-file .env geometra-ai
Testa sedan API:et via http://localhost:8000/chat eller motsvarande endpoint.

4. Miljövariabler
Använd .env-filen i projektroten

Skicka med --env-file .env vid docker run för att ladda in miljövariabler

I produktion kan dessa sättas via Railway UI eller andra molnplattformar

5. Integrera Docker i CI/CD med GitHub Actions
Exempel på steg i .github/workflows/deploy.yml:

yaml
Kopiera kod
jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Build Docker image
        run: docker build -t geometra-ai .

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Push Docker image
        run: |
          docker tag geometra-ai:latest yourdockerhubuser/geometra-ai:latest
          docker push yourdockerhubuser/geometra-ai:latest

      - name: Deploy to Railway
        run: railway up --service geometra-ai
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
Justera efter din setup och autentiseringsmetoder.

6. Rekommenderade nästa steg
Testa bygget och kör containern lokalt

Lägg till rollback-script (scripts/rollback.sh) som kan rulla tillbaka till tidigare Docker-image

Konfigurera Railway att använda rätt Docker-image för staging och production

Säkerställ att .env är komplett och korrekt i alla miljöer

7. Felsökningstips
Kontrollera att alla beroenden finns i requirements.txt

Se till att miljövariabler är korrekt laddade i containern

Använd docker logs <container-id> för att läsa loggar vid fel

För debug, kör containern med -it och bash:
docker run -it --env-file .env geometra-ai /bin/bash

8. Referenser
Docker Official Docs

FastAPI Deployment with Docker

Railway Docker Deploy

Slut på dokument
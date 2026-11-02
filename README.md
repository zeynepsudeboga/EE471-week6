# EE471 – Week 6: Docker & Cog

| Folder | What it is |
|---|---|
| `speech-studio/` | Week 5 Azure Speech Studio website, containerized (Dockerfile) |
| `voice-calculator/` | Week 5 voice-activated calculator, containerized (Dockerfile) |
| `compose.yaml` | Runs both week-5 apps together |
| `cat-classifier/` | Cog model (ResNet50, cat kinds) + website, run with its own `compose.yaml` |

## Requirements
Docker Desktop, [Cog](https://github.com/replicate/cog) (`brew install replicate/tap/cog`), and an Azure Speech key for Task 1.

## Task 1 – Containerized week-5 apps
```bash
cp .env.example .env          # then fill in SPEECH_KEY and SPEECH_REGION
docker compose up --build
```
- Speech Studio: http://localhost:5001
- Voice Calculator: http://localhost:5002

The key is passed in at run time with `env_file`, so it is never copied into an image (`.env` is in `.dockerignore` and `.gitignore`).

## Task 2 – Cat-kind classifier (Cog)
```bash
cd cat-classifier
cog run -i image=@cat.jpg          # first run: builds the env and downloads the ResNet50 weights
cog build -t cat-classifier        # bakes code + weights into a Docker image
docker compose up --build          # model on :5050, website on :8000
```
- Website: http://localhost:8000 – upload a cat photo and press **Classify**.
- API: `POST http://localhost:5050/predictions` with `{"input": {"image": "data:image/jpeg;base64,..."}}`
- Live prediction logs from inside the container:
  ```bash
  docker exec -it cat-model bash
  tail -f /tmp/predictions.log
  ```

The model only knows ImageNet's five domestic-cat classes (tabby, tiger cat, Persian, Siamese, Egyptian). The website merges "tabby" and "tiger cat" into one "Tabby (striped)" result, because both labels describe striped tabby cats.

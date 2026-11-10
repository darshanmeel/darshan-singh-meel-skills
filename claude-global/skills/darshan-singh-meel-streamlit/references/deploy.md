# Run and deploy

## Local
- Virtual environment, pinned install: `pip install -r requirements.txt` (`streamlit==<version>` in the file).
- Run: `streamlit run app.py` (script arguments after `--`). `python -m streamlit run app.py` is the same; handy for IDE debuggers.
- Develop on the Python version the host runs.

## Before any deploy
- Dependencies pinned; one dependency file only.
- Secrets in the host's store; `secrets.toml` not in the repo or the image.
- Every `conn.query` and `cache_data` has a `ttl`; login `redirect_uri` set for the target URL.
- `client.toolbarMode = "viewer"`; no debug output left in the UI.
- AppTest suite passes.

## Docker (any container host)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home app
USER app
EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
- `WORKDIR` must not be `/` (running from the root directory is unsupported).
- `.dockerignore`: `.git`, `.venv`, `.streamlit/secrets.toml`, `tests/`, `analysis/`.
- Secrets at run time: environment variables or a mounted `secrets.toml`.
- Health endpoint: `/_stcore/health`.
- Docs: docs.streamlit.io/deploy/tutorials/docker

## Behind a proxy or load balancer
- The app uses WebSockets → the proxy must pass upgrades and not time them out early.
- More than one replica → session affinity (sticky sessions); without it uploads and media fail (`MediaFileStorageError`, HTTP 400).
- Session state and caches live in each replica's memory: not shared between replicas, lost on restart. State that must survive → a database.
- TLS and authentication at the proxy, or `st.login`.
- Docs: docs.streamlit.io/develop/concepts/architecture/architecture

## Community Cloud
- Deploys from a GitHub repo with "Create app". It uploads code to a hosted service → only when the user asks for it.
- Dependency file, first found wins (entrypoint folder, then repo root): `uv.lock`, `Pipfile`, `environment.yml`, `requirements.txt`, `pyproject.toml`.
- `streamlit` is preinstalled; list it to pin it.
- Defaults to the newest supported Python → set it to match development.
- Secrets: the app's Secrets console.
- No persistent local disk.
- Docs: docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

## Snowflake
- Runtimes, `CREATE STREAMLIT`, version caps, limits, privileges, secrets: `darshan-singh-meel-streamlit-snowflake`. App code rules stay here.

# Python (pipelines and general)

- One file if it fits (~200 lines); plain functions; no classes unless state truly needs one.
- Type hints on public functions.
- `pathlib`, context managers for files/connections, no mutable default arguments.
- `logging` (not `print`) in pipelines — once per meaningful step.
- Catch specific exceptions and re-raise with context; never bare `except:`.
- SQL from Python: bind parameters, never f-strings with external input.
- pandas: vectorized ops; no `iterrows()`/row `apply` when vectorized works; set `dtype`s on read for big files.
- Don't pull large data into pandas — push transformations to the warehouse or Spark.
- Config and secrets from environment / secrets manager.
- Cloud SDKs (`boto3`, Azure SDK): default credential chain (IAM role, managed identity) — never keys in code.
- Small pure transform functions so they're testable with tiny in-memory inputs.
- Pin dependencies (`requirements.txt` / lockfile); add one only if it saves real effort.

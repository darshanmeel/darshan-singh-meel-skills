"""Python half of the fetch bridge: answer a batch of requests through an in-process API. Stdlib only."""
import json
import time

# Warehouse runtime caps a message at 32 MB; leave room for the rest of the message.
MAX_BYTES = 24 * 1024 * 1024
# The client has already decoded the body, and the browser works out the length.
DROP_HEADERS = {"content-length", "content-encoding", "transfer-encoding"}
JSON = {"content-type": "application/json"}


def reply(req, status, detail):
    return {"id": req["id"], "path": req["path"].split("?")[0], "status": status, "headers": JSON,
            "body": json.dumps({"detail": detail}), "server_ms": 0}


def answer(req, call, allowed_writes=frozenset()):
    """One request. call(method, path, body, headers) -> (status, text, headers) is the in-process API.
    The hosted copy is read-only: a write would reach every viewer, so only allowed_writes pass."""
    path = req["path"].split("?")[0]
    if req["method"] not in ("GET", "HEAD") and (req["method"], path) not in allowed_writes:
        return reply(req, 409, "Read-only in the hosted app.")
    start = time.perf_counter()
    try:
        status, text, headers = call(req["method"], req["path"], req.get("body"), req.get("headers"))
    except Exception as exc:  # the page gets a failed response; the type only, never the message or data
        return reply(req, 500, type(exc).__name__)
    return {"id": req["id"], "path": path, "status": status, "body": text,
            "headers": {k: v for k, v in headers.items() if k.lower() not in DROP_HEADERS},
            "server_ms": (time.perf_counter() - start) * 1000}


def pack(responses, max_bytes=MAX_BYTES):
    """Keep what fits in one message. One response too large alone -> 413; the rest -> retry next batch."""
    kept, retry, used = [], [], 0
    for res in responses:
        size = len(json.dumps(res))
        if size > max_bytes:
            res = reply(res, 413, "This result is too large to send here.")
            size = len(json.dumps(res))
        if kept and used + size > max_bytes:
            retry.append(res["id"])
        else:
            kept.append(res)
            used += size
    return kept, retry

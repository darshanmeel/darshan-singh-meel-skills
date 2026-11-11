"""Pure logic under test: no I/O, no terminal code, no globals. This file is what gets absorbed.
Replace the sample (an order with a submit rule) with the model the question is about."""


def initial():
    return {"status": "draft", "items": 0, "error": None}


def step(state, action):
    s = {**state, "error": None}
    if action == "add" and s["status"] == "draft":
        s["items"] += 1
    elif action == "submit" and s["status"] == "draft" and s["items"] > 0:
        s["status"] = "submitted"
    elif action == "cancel" and s["status"] != "cancelled":
        s["status"] = "cancelled"
    else:
        s["error"] = f"'{action}' not allowed in status '{s['status']}' with {s['items']} items"
    return s

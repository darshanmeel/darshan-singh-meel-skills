"""Pipeline stand-in: runs stub tasks in dependency order without Airflow and prints every task state.
Run: python prototypes/<name>/flow.py
Replace the sample tasks; stubs only print, write STORE, or raise."""
import graphlib

STORE = {}  # stands in for the target tables: {(table, interval): value}


def extract(ds, try_no):
    if try_no == 1:
        raise RuntimeError("source timeout (planned failure on try 1)")
    STORE["raw", ds] = 3


def choose(ds, try_no):
    return ["full_load"] if ds.endswith("-01") else ["delta_load"]  # branch: ids that run


def full_load(ds, try_no):
    STORE["orders", ds] = STORE["raw", ds]  # overwrites the interval: rerun-safe


def delta_load(ds, try_no):
    STORE["orders", ds] = STORE["raw", ds]


def publish(ds, try_no):
    STORE["published", ds] = STORE["orders", ds]


# id: (stub, upstream ids, retries, trigger rule)
TASKS = {
    "extract": (extract, [], 1, "all_success"),
    "choose": (choose, ["extract"], 0, "all_success"),
    "full_load": (full_load, ["choose"], 0, "all_success"),
    "delta_load": (delta_load, ["choose"], 0, "all_success"),
    "publish": (publish, ["full_load", "delta_load"], 0, "none_failed_min_one_success"),
}


def run(ds):
    state = {}
    order = graphlib.TopologicalSorter({t: v[1] for t, v in TASKS.items()}).static_order()
    for tid in order:
        fn, ups, retries, rule = TASKS[tid]
        up = [state[u] for u in ups]
        if state.get(tid) == "skipped":  # not chosen by a branch
            pass
        elif "failed" in up or "upstream_failed" in up:
            state[tid] = "upstream_failed"
        elif "skipped" in up and (rule == "all_success" or "success" not in up):
            state[tid] = "skipped"
        else:
            for try_no in range(1, retries + 2):
                try:
                    chosen = fn(ds, try_no)
                    state[tid] = "success"
                    break
                except Exception as e:
                    state[tid] = "failed"
                    print(f"  {tid} try {try_no} of {retries + 1}: {e}")
            if state[tid] == "success" and isinstance(chosen, list):  # only a list of ids is a branch
                for t, v in TASKS.items():
                    if tid in v[1] and t not in chosen:
                        state[t] = "skipped"
        print(f"  {tid:<12}", "  ".join(f"{t}={state.get(t, '-')}" for t in TASKS))
    return state


def main():
    for ds in ("2026-03-01", "2026-03-01", "2026-03-02"):  # same interval twice = rerun
        before = dict(STORE)
        print(f"run {ds}")
        run(ds)
        print(f"  store: {STORE}")
        if any(k[1] == ds for k in before):
            print(f"  rerun left the store unchanged: {before == STORE}")


main()

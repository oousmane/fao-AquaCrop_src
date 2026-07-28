import queue
import threading

try:
    import tkinter as tk
    from tkinter import ttk
except Exception:  # pragma: no cover - fallback for environments without Tk
    tk = None
    ttk = None


class _NullProgressReporter:
    def start(self, total_runs: int) -> None:
        pass

    def advance(self, step: int = 1) -> None:
        pass

    def finish(self) -> None:
        pass

    def fail(self, message: str) -> None:
        pass


class _TkProgressReporter:
    def __init__(self) -> None:
        self.events = queue.Queue()

    def start(self, total_runs: int) -> None:
        self.events.put(("start", max(0, int(total_runs))))

    def advance(self, step: int = 1) -> None:
        self.events.put(("advance", max(1, int(step))))

    def finish(self) -> None:
        self.events.put(("finish",))

    def fail(self, message: str) -> None:
        self.events.put(("fail", str(message)))


_progress_reporter = _NullProgressReporter()


def set_progress_reporter(reporter) -> None:
    global _progress_reporter
    _progress_reporter = reporter if reporter is not None else _NullProgressReporter()


def start_progress(total_runs: int) -> None:
    _progress_reporter.start(total_runs)


def advance_progress(step: int = 1) -> None:
    _progress_reporter.advance(step)


def finish_progress() -> None:
    _progress_reporter.finish()


def fail_progress(message: str) -> None:
    _progress_reporter.fail(message)


def run_with_progress(task) -> None:
    if tk is None or ttk is None:
        task()
        return

    try:
        root = tk.Tk()
    except Exception:
        task()
        return

    reporter = _TkProgressReporter()
    set_progress_reporter(reporter)

    worker_error = {"exception": None}
    ui_state = {
        "total_runs": 0,
        "completed_runs": 0,
        "closing": False,
    }

    root.title("AquaCrop")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)

    container = ttk.Frame(root, padding=16)
    container.grid(row=0, column=0, sticky="nsew")

    title_var = tk.StringVar(value="Running simulations")
    status_var = tk.StringVar(value="Preparing execution...")
    percent_var = tk.StringVar(value="0 %")
    progress_var = tk.DoubleVar(value=0.0)

    ttk.Label(container, textvariable=title_var).grid(row=0, column=0, sticky="w")
    ttk.Label(container, textvariable=status_var).grid(row=1, column=0, sticky="w", pady=(6, 10))
    ttk.Progressbar(
        container,
        orient="horizontal",
        mode="determinate",
        maximum=100.0,
        variable=progress_var,
        length=320,
    ).grid(row=2, column=0, sticky="ew")
    ttk.Label(container, textvariable=percent_var).grid(row=3, column=0, sticky="e", pady=(8, 0))

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x_pos = max(0, (root.winfo_screenwidth() - width) // 2)
    y_pos = max(0, (root.winfo_screenheight() - height) // 3)
    root.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

    def refresh_progress() -> None:
        total_runs = ui_state["total_runs"]
        completed_runs = ui_state["completed_runs"]

        if total_runs > 0:
            percent = min(100.0, (completed_runs * 100.0) / total_runs)
            current_run = min(completed_runs, total_runs)
            if total_runs > 0 and current_run == 0:
                current_run = 1
            status_var.set(f"Simulation {current_run} of {total_runs}")
        else:
            percent = 0.0
            status_var.set("Preparing simulations...")

        progress_var.set(percent)
        percent_var.set(f"{percent:.0f} %")

    def close_after_delay() -> None:
        if ui_state["closing"]:
            return
        ui_state["closing"] = True
        root.after(400, root.destroy)

    def process_events() -> None:
        try:
            while True:
                event = reporter.events.get_nowait()
                kind = event[0]

                if kind == "start":
                    ui_state["total_runs"] = event[1]
                    ui_state["completed_runs"] = 0
                    refresh_progress()
                elif kind == "advance":
                    ui_state["completed_runs"] += event[1]
                    refresh_progress()
                elif kind == "finish":
                    if ui_state["total_runs"] > 0:
                        ui_state["completed_runs"] = ui_state["total_runs"]
                        refresh_progress()
                    status_var.set("Simulations completed")
                    percent_var.set("100 %")
                    progress_var.set(100.0)
                    close_after_delay()
                elif kind == "fail":
                    status_var.set("Execution failed")
                    close_after_delay()
        except queue.Empty:
            pass

        if not ui_state["closing"]:
            root.after(100, process_events)

    def worker() -> None:
        try:
            task()
        except Exception as exc:  # pragma: no cover - surfaced after GUI loop
            worker_error["exception"] = exc
            fail_progress(str(exc))
        else:
            finish_progress()

    threading.Thread(target=worker, daemon=True).start()
    root.after(100, process_events)

    try:
        root.mainloop()
    finally:
        set_progress_reporter(None)

    if worker_error["exception"] is not None:
        raise worker_error["exception"]

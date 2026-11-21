"""Finite weighted admission machine. Policy changes signal recipients only."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Worker:
    phase: str = "new"
    leaf: str = "absent"
    pending: bool = False
    leaf_pending: bool = False
    started: bool = False
    outcome: str | None = None


@dataclass
class Run:
    weights: tuple[int, ...]
    direction: str
    cleanup: str
    consume: bool
    cut: int | None
    trace: list[dict] = field(default_factory=list)
    stopped: str = ""

    @property
    def final(self) -> dict:
        return self.trace[-1]["state"]


class Machine:
    """One dispatcher and up to three worker/leaf chains; no external effects."""

    def __init__(self, weights: tuple[int, ...], direction: str, cleanup: str,
                 consume: bool, cut: int | None):
        if not 1 <= len(weights) <= 3 or any(type(w) is not int or w not in (1, 2, 3)
                                              for w in weights):
            raise ValueError("frozen workload: one to three weights in {1,2,3}")
        if direction not in ("bottom_up", "simultaneous"):
            raise ValueError("unknown cancellation direction")
        if cleanup not in ("owner", "worker"):
            raise ValueError("unknown cleanup protocol")
        if type(consume) is not bool:
            raise ValueError("leaf treatment must be boolean")
        if cut is not None and (type(cut) is not int or cut < 0):
            raise ValueError("cancellation cut must be a nonnegative integer")
        self.run = Run(weights, direction, cleanup, consume, cut)
        self.queue = list(range(len(weights)))
        self.returned: list[int] = []
        self.completed: list[int] = []
        self.held: dict[int, int] = {}
        self.workers: dict[int, Worker] = {}
        self.parent = "fill"
        self.parent_pending = False
        self.awaited: int | None = None
        self.cursor = 0
        self.record("initial")

    def snapshot(self) -> dict:
        return {"queue": self.queue.copy(), "returned": self.returned.copy(),
                "completed": self.completed.copy(),
                "live": [j for j, w in self.workers.items() if w.phase != "done"],
                "registry": [j for j in self.held if self.workers[j].phase == "done"
                             and self.run.cleanup == "owner" and self.parent != "done"],
                "held": self.held.copy(), "free": 3 - sum(self.held.values()),
                "terminal": self.parent == "done", "parent": self.parent,
                "awaited": self.awaited, "parent_pending": self.parent_pending,
                "workers": {j: vars(w).copy() for j, w in self.workers.items()}}

    def record(self, action: str) -> None:
        self.run.trace.append({"action": action, "state": self.snapshot()})

    def cancel_worker(self, job: int, simultaneous: bool) -> None:
        worker = self.workers[job]
        if worker.phase == "done":
            return
        if worker.phase == "leaf" and worker.leaf == "waiting":
            worker.leaf_pending = True
            if simultaneous:
                worker.pending = True
        else:
            worker.pending = True

    def cancel(self) -> None:
        if self.parent == "done":
            self.record("cancel ignored: dispatcher already finished")
            return
        simultaneous = self.run.direction == "simultaneous"
        if self.parent == "wait" and self.awaited is not None:
            worker = self.workers[self.awaited]
            if worker.phase != "done":
                self.cancel_worker(self.awaited, simultaneous)
                if simultaneous:
                    self.parent_pending = True
            else:
                self.parent_pending = True
        else:
            self.parent_pending = True
        self.record("cancel dispatcher: " + self.run.direction)

    def finish_worker(self, job: int, outcome: str) -> None:
        worker = self.workers[job]
        worker.phase = "done"
        worker.outcome = outcome
        if worker.started:
            self.held.pop(job)
            (self.completed if outcome == "ok" else self.returned).append(job)

    def parent_step(self) -> str | None:
        if self.parent == "fill":
            if self.parent_pending:
                self.parent_pending = False
                self.parent = "shutdown"
                return "dispatcher observes cancellation"
            if self.queue and self.run.weights[self.queue[0]] <= 3 - sum(self.held.values()):
                job = self.queue.pop(0)
                self.held[job] = self.run.weights[job]
                self.workers[job] = Worker()
                return f"admit {job}: reserve and spawn lazily"
            # Completed workers still need joining: an unobserved cancellation
            # must propagate even if it happened before the dispatcher awaited.
            joinable = [j for j in self.workers if self.workers[j].outcome != "joined"]
            if joinable:
                self.awaited = joinable[0]
                self.parent = "wait"
                return f"dispatcher awaits {self.awaited}"
            if not self.queue:
                self.parent = "done"
                return "dispatcher finished"
            return None  # capacity stranded by the deliberately broken protocol
        if self.parent == "wait":
            worker = self.workers[self.awaited]
            if worker.phase != "done":
                return None
            cancelled = self.parent_pending or worker.outcome == "cancelled"
            self.parent_pending = False
            worker.outcome = "joined"
            self.awaited = None
            self.parent = "shutdown" if cancelled else "fill"
            return "join: cancellation" if cancelled else "join: success"
        if self.parent == "shutdown":
            # Application cleanup is identical in both direction treatments.
            for job in self.workers:
                self.cancel_worker(job, False)
            self.parent = "settle"
            return "shutdown: cancel every remaining worker bottom-up"
        if self.parent == "settle":
            if any(w.phase != "done" for w in self.workers.values()):
                return None
            if self.run.cleanup == "owner":
                for job in list(self.held):
                    self.held.pop(job)
                    self.returned.append(job)
            self.parent = "done"
            return "shutdown: settle and reconcile admission registry"
        return None

    def worker_step(self, job: int) -> str | None:
        worker = self.workers.get(job)
        if worker is None or worker.phase == "done":
            return None
        if worker.phase == "new":
            if worker.pending:
                worker.pending = False
                self.finish_worker(job, "cancelled")
                return f"worker {job}: cancelled before first instruction"
            worker.started = True
            worker.phase = "work"
            return f"worker {job}: enter finally-protected body"
        if worker.phase == "work":
            if worker.pending:
                worker.pending = False
                self.finish_worker(job, "cancelled")
                return f"worker {job}: cancellation and finally"
            worker.phase = "leaf"
            worker.leaf = "waiting"
            return f"worker {job}: await leaf"
        if worker.leaf == "waiting":
            return None
        cancelled = worker.pending or worker.leaf == "cancelled"
        worker.pending = False
        self.finish_worker(job, "cancelled" if cancelled else "ok")
        return f"worker {job}: {'cancel' if cancelled else 'complete'} and finally"

    def leaf_step(self, job: int) -> str | None:
        worker = self.workers.get(job)
        if worker is None or worker.phase != "leaf" or worker.leaf != "waiting":
            return None
        if worker.leaf_pending:
            worker.leaf_pending = False
            worker.leaf = "ok" if self.run.consume else "cancelled"
            return f"leaf {job}: {'consume' if self.run.consume else 'propagate'} cancellation"
        worker.leaf = "ok"
        return f"leaf {job}: normal completion"

    def step(self) -> bool:
        actors = 1 + 2 * len(self.run.weights)
        for _ in range(actors):
            actor = self.cursor
            self.cursor = (self.cursor + 1) % actors
            if actor == 0:
                action = self.parent_step()
            elif actor % 2:
                action = self.worker_step((actor - 1) // 2)
            else:
                action = self.leaf_step((actor - 2) // 2)
            if action is not None:
                self.record(action)
                return True
        return False


def execute(weights: tuple[int, ...], direction: str = "bottom_up",
            cleanup: str = "owner", consume: bool = False,
            cut: int | None = None) -> Run:
    machine = Machine(weights, direction, cleanup, consume, cut)
    ordinary_steps = 0
    injected = False
    while True:
        if cut == ordinary_steps and not injected:
            machine.cancel()
            injected = True
        if machine.parent == "done":
            machine.run.stopped = "finished"
            break
        if len(machine.run.trace) - 1 >= 128:
            machine.run.stopped = "bound"
            break
        if not machine.step():
            machine.run.stopped = "stuck"
            break
        ordinary_steps += 1
    if cut is not None and not injected:
        raise ValueError("cut is beyond this execution's common prefix")
    return machine.run

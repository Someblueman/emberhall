"""Native asyncio observations, not a simultaneous-cancellation emulator."""
from __future__ import annotations

import asyncio
import platform

from ownership_oracle import violations


class Ledger:
    def __init__(self, weights: tuple[int, ...]):
        self.weights = weights
        self.queue = list(range(len(weights)))
        self.completed: list[int] = []
        self.returned: list[int] = []
        self.held: dict[int, int] = {}
        self.tasks: dict[int, asyncio.Task] = {}
        self.events: list[str] = []

    def reserve(self, job: int) -> None:
        assert self.weights[job] <= 3 - sum(self.held.values())
        self.queue.remove(job)
        self.held[job] = self.weights[job]
        self.events.append(f"reserve {job} weight {self.weights[job]}")

    def release(self, job: int, complete: bool) -> None:
        self.held.pop(job)
        (self.completed if complete else self.returned).append(job)
        self.events.append(f"{'complete' if complete else 'return'} {job}; release")

    def reconcile(self) -> None:
        for job in list(self.held):
            assert self.tasks[job].done()
            self.release(job, False)

    def snapshot(self) -> dict:
        return {"queue": self.queue.copy(), "returned": self.returned.copy(),
                "completed": self.completed.copy(), "registry": [],
                "live": [job for job, task in self.tasks.items() if not task.done()],
                "held": self.held.copy(), "free": 3 - sum(self.held.values()),
                "terminal": True}


async def before_start(repair: bool) -> dict:
    ledger = Ledger((2,))
    entered = False

    async def worker() -> None:
        nonlocal entered
        entered = True
        try:
            await asyncio.Event().wait()
        finally:
            ledger.release(0, False)

    ledger.reserve(0)
    task = asyncio.create_task(worker(), name="admission-prestart")
    ledger.tasks[0] = task
    # No intervening await: the default lazy factory cannot start the worker.
    accepted = task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    ledger.events.append(f"cancel accepted={accepted}, body entered={entered}")
    assert not entered and task.cancelled()
    if repair:
        ledger.reconcile()
    state = ledger.snapshot()
    return {"case": "before_start_owner" if repair else "before_start_worker",
            "events": ledger.events, "state": state,
            "violations": violations(ledger.weights, state)}


async def swallowed_leaf() -> dict:
    ledger = Ledger((1, 2, 1))
    ready = [asyncio.Event() for _ in ledger.weights]
    parent_waiting = asyncio.Event()
    leaves: dict[int, asyncio.Task] = {}

    async def leaf(job: int) -> None:
        ready[job].set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            ledger.events.append(f"leaf {job} receives cancellation")
            if job != 0:
                raise
            ledger.events.append("leaf 0 consumes cancellation")

    async def worker(job: int) -> None:
        complete = False
        try:
            leaves[job] = asyncio.create_task(leaf(job), name=f"admission-leaf-{job}")
            await leaves[job]
            complete = True
        finally:
            ledger.release(job, complete)

    def admit(job: int) -> None:
        ledger.reserve(job)
        ledger.tasks[job] = asyncio.create_task(worker(job), name=f"admission-worker-{job}")

    async def dispatcher() -> None:
        try:
            admit(0)
            admit(1)  # Weight 1 + 2 fills capacity; job 2 cannot yet fit.
            parent_waiting.set()
            await ledger.tasks[0]
            ledger.events.append("dispatcher continued after cancellation request")
            admit(2)
        finally:
            for task in ledger.tasks.values():
                if not task.done():
                    task.cancel()
            await asyncio.gather(*ledger.tasks.values(), return_exceptions=True)
            await asyncio.gather(*leaves.values(), return_exceptions=True)
            ledger.reconcile()

    parent = asyncio.create_task(dispatcher(), name="admission-dispatcher")
    await parent_waiting.wait()
    await ready[0].wait()
    await ready[1].wait()
    # Both the dispatcher->worker and worker->leaf awaits are now installed.
    accepted = parent.cancel()
    await asyncio.gather(parent, return_exceptions=True)
    ledger.events.append(f"parent request accepted={accepted}, cancelled={parent.cancelled()}")
    assert accepted and not parent.cancelled()
    assert 2 in ledger.tasks and ledger.completed == [0]
    assert all(task.done() for task in [parent, *ledger.tasks.values(), *leaves.values()])
    state = ledger.snapshot()
    return {"case": "bottom_up_swallowed_leaf", "events": ledger.events,
            "state": state, "violations": violations(ledger.weights, state)}


async def _witnesses() -> dict:
    loop = asyncio.get_running_loop()
    # Explicitly freeze default lazy start; do not inherit an eager factory.
    loop.set_task_factory(None)
    async with asyncio.timeout(5):
        cases = [await before_start(False), await before_start(True), await swallowed_leaf()]
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "loop": type(loop).__name__, "task_factory": "default lazy", "cases": cases}


def witnesses() -> dict:
    return asyncio.run(_witnesses())

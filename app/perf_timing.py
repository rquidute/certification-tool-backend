#
# Copyright (c) 2026 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Opt-in cumulative timers, to find where a test run spends its time.

Enabled with ENABLE_PERF_TIMING=True in the root .env (needs a backend
restart). Disabled, every helper is a no-op. Totals are logged once per run
by TestRunner. Timers can nest or overlap (e.g. a UI observer timer runs
inside the log handler's flush timer), so totals are NOT additive: read each
line on its own.
"""
import os
import threading
import time
from typing import Optional

ENABLED = os.environ.get("ENABLE_PERF_TIMING", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)

_lock = threading.Lock()
_totals: dict[str, float] = {}
_counts: dict[str, int] = {}
_extras: dict[str, int] = {}


def add(name: str, seconds: float, count: int = 1) -> None:
    if not ENABLED:
        return
    with _lock:
        _totals[name] = _totals.get(name, 0.0) + seconds
        _counts[name] = _counts.get(name, 0) + count


def add_extra(name: str, value: int) -> None:
    """Accumulate a plain counter (e.g. bytes sent)."""
    if not ENABLED:
        return
    with _lock:
        _extras[name] = _extras.get(name, 0) + value


class _Timer:
    __slots__ = ("name", "count", "_start")

    def __init__(self, name: str, count: int) -> None:
        self.name = name
        self.count = count
        self._start = 0.0

    def __enter__(self) -> "_Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc: object) -> None:
        add(self.name, time.perf_counter() - self._start, self.count)


class _NoopTimer:
    def __enter__(self) -> "_NoopTimer":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


_NOOP = _NoopTimer()


def timer(name: str, count: int = 1) -> "_Timer | _NoopTimer":
    """Context manager adding the elapsed time (and `count` calls) to `name`."""
    return _Timer(name, count) if ENABLED else _NOOP


def now() -> Optional[float]:
    """perf_counter() when enabled, else None. For hot loops: `if t0 is not None`."""
    return time.perf_counter() if ENABLED else None


def reset() -> None:
    with _lock:
        _totals.clear()
        _counts.clear()
        _extras.clear()


def summary() -> list[str]:
    with _lock:
        lines = []
        for name in sorted(_totals):
            total, count = _totals[name], _counts[name]
            avg_us = total / count * 1e6 if count else 0.0
            lines.append(
                f"PERF {name}: total={total:.2f}s count={count} avg={avg_us:.1f}us"
            )
        for name in sorted(_extras):
            lines.append(f"PERF {name}: {_extras[name]}")
        return lines

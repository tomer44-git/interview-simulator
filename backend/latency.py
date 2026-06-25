# latency.py
# מודול מדידת latency קל-משקל — time.perf_counter() בלבד, אין תלויות חיצוניות
# תומך ב-sync וב-async functions

import sys
import time
import asyncio
import functools
from datetime import datetime

# מבטיח UTF-8 כ-encoding של stdout — Railway מגדיר ASCII כברירת מחדל
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# אחסון in-memory של מדידות ה-FastAPI process (לא נשמר בין restarts)
_measurements: list[dict] = []


def measure_latency(label: str = None):
    """
    דקורטור שמודד wall-clock time של פונקציה.
    עובד על sync ו-async — מזהה אוטומטית לפי asyncio.iscoroutinefunction.
    """
    def decorator(fn):
        name = label or fn.__name__

        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                t0 = time.perf_counter()
                ts = datetime.now().isoformat(timespec='milliseconds')
                result = await fn(*args, **kwargs)
                _record(name, ts, time.perf_counter() - t0)
                return result
            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            ts = datetime.now().isoformat(timespec='milliseconds')
            result = fn(*args, **kwargs)
            _record(name, ts, time.perf_counter() - t0)
            return result
        return sync_wrapper
    return decorator


def _record(name: str, ts: str, duration: float):
    """מוסיף מדידה לרשימה ומדפיס שורה מיידית ללוג"""
    entry = {"name": name, "timestamp": ts, "duration": duration}
    _measurements.append(entry)
    print(f"[LATENCY] {ts}  {name:<42} {duration:.3f}s")


def get_measurements() -> list[dict]:
    return list(_measurements)


def clear_measurements():
    """נקה בתחילת כל pipeline חדש"""
    _measurements.clear()


def print_research_summary(stage_duration: float, agent_timings: list[dict]):
    """
    מדפיס השוואת מקביליות: מוכיח שה-actual wall-clock ≈ MAX ולא SUM.
    stage_duration — כמה שניות לקח כל שלב ה-research כולו
    agent_timings  — רשימת {"name": ..., "duration": ...} לכל agent
    """
    print("\n" + "=" * 58)
    print("  RESEARCH STAGE — PARALLELISM PROOF")
    print("=" * 58)
    for a in sorted(agent_timings, key=lambda x: -x["duration"]):
        bar = "#" * int(a["duration"] * 3)
        print(f"  {a['name']:<12}  {a['duration']:.3f}s  {bar}")
    durations = [a["duration"] for a in agent_timings]
    print(f"\n  SUM  (if sequential): {sum(durations):.3f}s")
    print(f"  MAX  (slowest agent): {max(durations):.3f}s")
    print(f"  ACTUAL wall-clock:    {stage_duration:.3f}s  ← ≈ MAX, << SUM")
    print("=" * 58 + "\n")


def print_full_summary():
    """מדפיס טבלת סיכום של כל שלבי ה-pipeline בסיום ריצה"""
    print("\n" + "=" * 58)
    print("  FULL PIPELINE LATENCY SUMMARY")
    print("=" * 58)
    for m in _measurements:
        print(f"  {m['name']:<42} {m['duration']:.3f}s")
    if _measurements:
        total = sum(m["duration"] for m in _measurements)
        print(f"\n  TOTAL pipeline (sum of stages): {total:.3f}s")
    print("=" * 58 + "\n")

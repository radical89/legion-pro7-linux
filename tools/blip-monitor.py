#!/usr/bin/env python3
"""Blip monitor — wall-clock-timestamped log of scheduler stalls + PipeWire xruns.

Run it while listening; when you hear a blip, note the clock time (or hit a
key in another terminal: `date +%T.%3N`). Then grep the log around that time
to see whether the blip lines up with an xrun, a stall, both, or neither.

Usage (RT priority recommended for the stall canary):
    chrt -f 70 python3 blip-monitor.py [--duration 600] [--log blips.log]

Log lines:
    09:48:59.240 STALL 4.32ms
    09:48:59.900 XRUN node=Firefox err=222 (+1)

History: built 2026-07-19 after proving stalls (278 in 60 s) and xruns
(zero in the same window) are uncorrelated — blips arrive in bursts and
needed wall-clock alignment with what Karlos actually hears.
"""

import argparse
import subprocess
import threading
import time
from datetime import datetime


def now() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def canary(stop: threading.Event, threshold_ms: float, out) -> None:
    interval = 0.001
    while not stop.is_set():
        t0 = time.monotonic()
        time.sleep(interval)
        overshoot = (time.monotonic() - t0) * 1000.0 - 1.0
        if overshoot > threshold_ms:
            print(f"{now()} STALL {overshoot:.2f}ms", file=out, flush=True)


def xrun_sampler(stop: threading.Event, out) -> None:
    prev: dict[str, int] = {}
    while not stop.is_set():
        try:
            res = subprocess.run(["pw-top", "-b", "-n", "1"],
                                 capture_output=True, text=True, timeout=5)
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) < 10 or parts[0] != "R":
                    continue
                name = " ".join(parts[10:]).lstrip("+ ").strip() or parts[1]
                err = int(parts[8])
                if name in prev and err > prev[name]:
                    print(f"{now()} XRUN node={name} err={err} "
                          f"(+{err - prev[name]})", file=out, flush=True)
                prev[name] = err
        except (subprocess.SubprocessError, ValueError, OSError):
            pass
        stop.wait(0.5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--threshold-ms", type=float, default=3.0)
    parser.add_argument("--log", default=None,
                        help="Append to this file instead of stdout")
    args = parser.parse_args()

    out = open(args.log, "a") if args.log else __import__("sys").stdout
    print(f"{now()} MONITOR START duration={args.duration}s", file=out, flush=True)
    stop = threading.Event()
    threads = [
        threading.Thread(target=canary, args=(stop, args.threshold_ms, out), daemon=True),
        threading.Thread(target=xrun_sampler, args=(stop, out), daemon=True),
    ]
    for t in threads:
        t.start()
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        pass
    stop.set()
    for t in threads:
        t.join(timeout=2)
    print(f"{now()} MONITOR END", file=out, flush=True)


if __name__ == "__main__":
    main()

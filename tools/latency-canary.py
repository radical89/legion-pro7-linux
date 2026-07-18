#!/usr/bin/env python3
"""RT latency canary — detects whole-machine scheduler stalls.

Sleeps 1 ms in a loop at RT priority and logs every overshoot beyond the
threshold. A healthy machine overshoots by scheduler jitter only (<1 ms);
GPU-poll bus stalls show up as 3-5 ms spikes.

Run with RT priority (needs @audio rtprio limit or root):
    chrt -f 70 ./latency-canary.py --duration 60

History: first used 2026-07-17 to prove nvidia-powerd caused ~4 ms stalls
~2-3x/s under gaming load (see NVIDIA/open-gpu-kernel-modules#1248).
Re-created 2026-07-19 to hunt the residual staller.
"""

import argparse
import time
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--duration", type=float, default=60.0,
                        help="Seconds to run (default: 60)")
    parser.add_argument("--threshold-ms", type=float, default=3.0,
                        help="Log overshoots beyond this (default: 3.0 ms)")
    parser.add_argument("--interval-ms", type=float, default=1.0,
                        help="Sleep interval (default: 1.0 ms)")
    args = parser.parse_args()

    interval = args.interval_ms / 1000.0
    start = time.monotonic()
    end = start + args.duration
    stalls = []
    worst = 0.0

    while True:
        t0 = time.monotonic()
        if t0 >= end:
            break
        time.sleep(interval)
        dt_ms = (time.monotonic() - t0) * 1000.0
        overshoot = dt_ms - args.interval_ms
        if overshoot > args.threshold_ms:
            elapsed = t0 - start
            stalls.append((elapsed, overshoot))
            worst = max(worst, overshoot)
            print(f"{elapsed:8.2f}s  stall {overshoot:6.2f} ms", flush=True)

    ran = time.monotonic() - start
    rate = len(stalls) / ran if ran > 0 else 0.0
    print(f"--- {len(stalls)} stalls >{args.threshold_ms} ms in {ran:.1f} s "
          f"({rate:.2f}/s), worst {worst:.2f} ms", flush=True)


if __name__ == "__main__":
    sys.exit(main())

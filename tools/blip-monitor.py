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
    09:49:00.100 GPU pstate=P0 sm=2175MHz mem=10251MHz pw=150.4W util=67% pcie=gen4

Note: the GPU sampler itself costs ~1 stall per query (every NVML read
stalls the bus on this platform) — negligible against 20-30/s storms.

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
    # pw-top's first batch frame carries stale/zero ERR counters; request two
    # frames and read only the last one.
    prev: dict[str, int] = {}
    while not stop.is_set():
        try:
            res = subprocess.run(["pw-top", "-b", "-n", "2"],
                                 capture_output=True, text=True, timeout=5)
            frames: list[list[str]] = []
            for line in res.stdout.splitlines():
                if line.startswith("S ") and " ID " in line:
                    frames.append([])
                elif frames:
                    frames[-1].append(line)
            for line in (frames[-1] if frames else []):
                parts = line.split()
                if len(parts) < 10 or parts[0] != "R":
                    continue
                # columns: S ID QUANT RATE WAIT BUSY W/Q B/Q ERR FMT CH RATE NAME
                # key by node ID: multiple nodes can share a name (e.g. "Pal")
                nid = parts[1]
                name = " ".join(p for p in parts[12:] if p != "+") or nid
                err = int(parts[8])
                if nid in prev and err > prev[nid]:
                    print(f"{now()} XRUN node={name}({nid}) err={err} "
                          f"(+{err - prev[nid]})", file=out, flush=True)
                prev[nid] = err
        except (subprocess.SubprocessError, ValueError, OSError):
            pass
        stop.wait(0.5)


def gpu_sampler(stop: threading.Event, out, interval: float = 2.0) -> None:
    # pcie.link.gen.gpucurrent: extra diagnostic, UNPROVEN motivation. In the
    # 2022 PipeWire #2375 thread one reporter correlated blips with the PCIe
    # link-gen up-switch, but another could not reproduce it and saw no change
    # after disabling PCIe/ASPM power management. Open question for the residual
    # storm mode: does the link even flip while the mem clock is -lmc-pinned?
    # (link gen may already sit pinned high with the forced P0 pstate.) Cheap
    # to log either way; don't treat a gen-flip as a confirmed cause.
    query = ("pstate,clocks.sm,clocks.mem,power.draw,utilization.gpu,"
             "pcie.link.gen.gpucurrent")
    while not stop.is_set():
        try:
            res = subprocess.run(
                ["nvidia-smi", f"--query-gpu={query}",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=3)
            v = [x.strip() for x in res.stdout.strip().split(",")]
            if len(v) == 6:
                print(f"{now()} GPU pstate={v[0]} sm={v[1]}MHz mem={v[2]}MHz "
                      f"pw={v[3]}W util={v[4]}% pcie=gen{v[5]}", file=out, flush=True)
        except (subprocess.SubprocessError, OSError):
            pass
        stop.wait(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--threshold-ms", type=float, default=3.0)
    parser.add_argument("--log", default=None,
                        help="Append to this file instead of stdout")
    parser.add_argument("--gpu-interval", type=float, default=2.0,
                        help="GPU sample period in seconds (default 2.0). "
                             "Lower it (e.g. 0.2) for a short window to catch "
                             "PCIe-gen/clock flips near an xrun — but each "
                             "sample costs ~1 stall, so don't leave it low.")
    args = parser.parse_args()

    out = open(args.log, "a") if args.log else __import__("sys").stdout
    print(f"{now()} MONITOR START duration={args.duration}s", file=out, flush=True)
    stop = threading.Event()
    threads = [
        threading.Thread(target=canary, args=(stop, args.threshold_ms, out), daemon=True),
        threading.Thread(target=xrun_sampler, args=(stop, out), daemon=True),
        threading.Thread(target=gpu_sampler, args=(stop, out, args.gpu_interval), daemon=True),
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

#!/usr/bin/env python3
"""Start one or more servers, wait until their ports are accepting connections,
run a target command, then shut the servers down. Standard library only — no
external dependencies.

This is a black-box helper: run it with --help, then invoke it. You should not
need to read this source. It exists so testing agents don't reinvent server
lifecycle management (and don't clutter their context window) every run.

USAGE
    python with_server.py --server "<cmd>" --port <N> [more --server/--port] \
        -- <command to run once servers are up>

    Each --server must be followed (in order) by its --port. The command after
    the `--` separator runs once every port is reachable; when it exits (or on
    Ctrl-C), every server is terminated.

EXAMPLES
    # Single dev server, then run an automation/test command
    python with_server.py --server "npm run dev" --port 5173 -- pytest e2e/

    # Backend + frontend together
    python with_server.py \
        --server "cd backend && python server.py" --port 3000 \
        --server "cd frontend && npm run dev" --port 5173 \
        -- python run_flows.py

    # Just wait for readiness then exit 0 (smoke check the port opens)
    python with_server.py --server "npm run preview" --port 4173 -- true

OPTIONS
    --server CMD     Shell command that starts a server (repeatable).
    --port N         Port to wait on for the preceding --server (repeatable).
    --host HOST      Host to probe (default 127.0.0.1).
    --timeout SEC    Max seconds to wait per port (default 60).
    --                Everything after this is the command to run.

EXIT CODES
    Propagates the target command's exit code. Returns 1 if a server fails to
    become ready within the timeout (and reports which one).
"""
import argparse
import socket
import subprocess
import sys
import time


def wait_for_port(host, port, timeout):
    """Return True once (host, port) accepts a TCP connection, else False."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def parse_args(argv):
    if "--" in argv:
        sep = argv.index("--")
        head, target = argv[:sep], argv[sep + 1:]
    else:
        head, target = argv, []

    p = argparse.ArgumentParser(add_help=True, description="Run servers around a command.")
    p.add_argument("--server", action="append", default=[], metavar="CMD")
    p.add_argument("--port", action="append", default=[], type=int, metavar="N")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--timeout", type=float, default=60.0)
    args = p.parse_args(head)
    return args, target


def main(argv):
    args, target = parse_args(argv)

    if len(args.server) != len(args.port):
        print("error: each --server needs exactly one matching --port", file=sys.stderr)
        return 2
    if not target:
        print("error: no target command given after `--`", file=sys.stderr)
        return 2

    procs = []
    try:
        # Launch every server.
        for cmd, port in zip(args.server, args.port):
            print(f"[with_server] starting: {cmd}  (port {port})", file=sys.stderr)
            procs.append(subprocess.Popen(cmd, shell=True))

        # Wait for each port to open.
        for cmd, port in zip(args.server, args.port):
            if not wait_for_port(args.host, port, args.timeout):
                print(f"[with_server] TIMEOUT: {args.host}:{port} not ready "
                      f"in {args.timeout}s (server: {cmd})", file=sys.stderr)
                return 1
            print(f"[with_server] ready: {args.host}:{port}", file=sys.stderr)

        # Run the target command with servers up.
        print(f"[with_server] running: {' '.join(target)}", file=sys.stderr)
        return subprocess.call(target)
    finally:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        deadline = time.time() + 10
        for proc in procs:
            try:
                proc.wait(timeout=max(0.1, deadline - time.time()))
            except subprocess.TimeoutExpired:
                proc.kill()
        print("[with_server] servers stopped", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/python3
import os
import subprocess


def cprint(*args, level: int = 1):
    """
    logs colorful messages
    level = 1 : RED
    level = 2 : GREEN
    level = 3 : YELLOW

    default level = 1
    """
    CRED = "\033[31m"
    CGRN = "\33[92m"
    CYLW = "\33[93m"
    reset = "\033[0m"
    message = " ".join(map(str, args))
    if level == 1:
        print(CRED, message, reset)  # noqa: T001
    if level == 2:
        print(CGRN, message, reset)  # noqa: T001
    if level == 3:
        print(CYLW, message, reset)  # noqa: T001


def setup_k8s_bench():
    cprint("Setup k8s_bench", level=2)
    try:
        subprocess.call(
            [
                "git",
                "clone",
                "https://gitlab.com/castlecraft/k8s_bench",
            ],
            cwd="/workspace/development",
        )
        subprocess.call(
            ["python3", "-m", "venv", "env"],
            cwd="/workspace/development/k8s_bench",
        )
        subprocess.call(
            ["./env/bin/pip", "install", "-e", "."],
            cwd="/workspace/development/k8s_bench",
        )
    except subprocess.CalledProcessError as e:
        cprint(e.output, level=1)


def setup_frappe_bench():
    cprint("Setup frappe-bench", level=2)
    try:
        subprocess.call(
            [
                "bench",
                "init",
                "--skip-redis-config-generation",
                "--verbose",
                "--frappe-branch=version-14",
                "frappe-bench",
            ],
            cwd="/workspace/development",
        )
        cprint("Configuring Bench ...", level=2)
        cprint("Set db_host to mariadb", level=3)
        subprocess.call(
            ["bench", "set-config", "-g", "db_host", "mariadb"],
            cwd="/workspace/development/frappe-bench",
        )
        cprint("Set redis_cache to redis://redis-cache:6379", level=3)
        subprocess.call(
            [
                "bench",
                "set-config",
                "-g",
                "redis_cache",
                "redis://redis-cache:6379",
            ],
            cwd="/workspace/development/frappe-bench",
        )
        cprint("Set redis_queue to redis://redis-queue:6379", level=3)
        subprocess.call(
            [
                "bench",
                "set-config",
                "-g",
                "redis_queue",
                "redis://redis-queue:6379",
            ],
            cwd="/workspace/development/frappe-bench",
        )
        cprint("Set redis_socketio to redis://redis-socketio:6379", level=3)
        subprocess.call(
            [
                "bench",
                "set-config",
                "-g",
                "redis_socketio",
                "redis://redis-socketio:6379",
            ],
            cwd="/workspace/development/frappe-bench",
        )
        cprint("Set developer_mode", level=3)
        subprocess.call(
            ["bench", "set-config", "-gp", "developer_mode", "1"],
            cwd="/workspace/development/frappe-bench",
        )
    except subprocess.CalledProcessError as e:
        cprint(e.output, level=1)


def setup_k8s_bench_interface():
    # Set global bench configs
    cprint("Symlink workspace as k8s_bench_interface", level=2)
    os.symlink(
        "/workspace",
        "/workspace/development/frappe-bench/apps/k8s_bench_interface",
    )
    try:
        cprint("Setup requirements", level=2)
        subprocess.call(
            ["bench", "setup", "requirements"],
            cwd="/workspace/development/frappe-bench",
        )
        cprint("Create http://k8s-bench-ui.localhost:8000 site", level=2)
        subprocess.call(
            [
                "bench",
                "new-site",
                "--no-mariadb-socket",
                "--db-root-password=123",
                "--install-app=k8s_bench_interface",
                "--admin-password=admin",
                "k8s-bench-ui.localhost",
            ],
            cwd="/workspace/development/frappe-bench",
        )
        cprint("Add k8s_bench config to site_config.json", level=2)
        subprocess.call(
            [
                "bench",
                "--site",
                "k8s-bench-ui.localhost",
                "set-config",
                "k8s_bench_url",
                "http://localhost:3000",
            ],
            cwd="/workspace/development/frappe-bench",
        )
        subprocess.call(
            [
                "bench",
                "--site",
                "k8s-bench-ui.localhost",
                "set-config",
                "k8s_bench_key",
                "admin",
            ],
            cwd="/workspace/development/frappe-bench",
        )
        subprocess.call(
            [
                "bench",
                "--site",
                "k8s-bench-ui.localhost",
                "set-config",
                "k8s_bench_secret",
                "changeit",
            ],
            cwd="/workspace/development/frappe-bench",
        )
    except subprocess.CalledProcessError as e:
        cprint(e.output, level=1)

    cprint("Add k8s_bench start script to Procfile / bench start", level=2)
    with open("/workspace/development/frappe-bench/Procfile", "a") as procfile:
        procfile.write(
            "\nk8s_bench: /workspace/development/k8s_bench/env/bin/uvicorn --host 0.0.0.0 --reload --port 3000 --reload-dir /workspace/development/k8s_bench k8s_bench.main:app"  # noqa: E501
        )


if __name__ == "__main__":
    setup_k8s_bench()
    setup_frappe_bench()
    setup_k8s_bench_interface()

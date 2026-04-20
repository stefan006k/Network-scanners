import argparse
import ipaddress
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:
    Fore = None
    Style = None
    colorama_init = None


def setup_colors() -> None:
    if colorama_init:
        colorama_init()


def color_text(text: str, color_code: str | None) -> str:
    if not color_code or not Style:
        return text
    return f"{color_code}{text}{Style.RESET_ALL}"


def ping_ip(ip: str, timeout_ms: int = 800) -> bool:
    system_name = platform.system().lower()

    if "windows" in system_name:
        # Windows: -n count, -w timeout_ms
        command = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    else:
        # Linux/macOS: -c count, -W timeout (seconds on Linux)
        timeout_s = max(1, int(round(timeout_ms / 1000)))
        command = ["ping", "-c", "1", "-W", str(timeout_s), ip]

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def ip_range(start_ip: str, end_ip: str) -> list[str]:
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)

    if start > end:
        raise ValueError("Start IP must be less than or equal to end IP.")

    return [str(ipaddress.IPv4Address(ip)) for ip in range(int(start), int(end) + 1)]


def scan_network(start_ip: str, end_ip: str, workers: int, timeout_ms: int) -> tuple[list[str], list[str]]:
    ips = ip_range(start_ip, end_ip)
    active: list[str] = []
    inactive: list[str] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_ip = {executor.submit(ping_ip, ip, timeout_ms): ip for ip in ips}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    active.append(ip)
                else:
                    inactive.append(ip)
            except Exception:
                inactive.append(ip)

    active.sort(key=lambda ip: int(ipaddress.IPv4Address(ip)))
    inactive.sort(key=lambda ip: int(ipaddress.IPv4Address(ip)))
    return active, inactive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan an IPv4 range by pinging each address."
    )
    parser.add_argument("start_ip", help="Start IPv4 address (e.g. 192.168.1.1)")
    parser.add_argument("end_ip", help="End IPv4 address (e.g. 192.168.1.254)")
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=100,
        help="Number of parallel ping workers (default: 100)",
    )
    parser.add_argument(
        "-t",
        "--timeout-ms",
        type=int,
        default=800,
        help="Ping timeout in milliseconds (default: 800)",
    )
    return parser.parse_args()


def main() -> None:
    setup_colors()
    args = parse_args()
    try:
        active, inactive = scan_network(
            start_ip=args.start_ip,
            end_ip=args.end_ip,
            workers=max(1, args.workers),
            timeout_ms=max(100, args.timeout_ms),
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    print(f"\n{color_text('=== Active IPs (In Use) ===', Fore.RED if Fore else None)}")
    for ip in active:
        print(color_text(f"{ip} - in use", Fore.RED if Fore else None))
    if not active:
        print(color_text("None", Fore.RED if Fore else None))

    print(f"\n{color_text('=== Non-active IPs (Possibly Free) ===', Fore.GREEN if Fore else None)}")
    for ip in inactive:
        print(color_text(f"{ip} - possibly free", Fore.GREEN if Fore else None))
    if not inactive:
        print(color_text("None", Fore.GREEN if Fore else None))

    print(f"\nScanned: {len(active) + len(inactive)} | Active: {len(active)} | Non-active: {len(inactive)}")


if __name__ == "__main__":
    main()

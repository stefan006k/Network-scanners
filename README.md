# Python Network Scanner

A simple Python network scanner that pings IPv4 addresses in a given range and shows whether each IP is likely **in use** or **possibly free**.

## What This Project Does

- Scans a start-to-end IPv4 range (for example, `192.168.1.1` to `192.168.1.254`)
- Sends one ping request to each IP address
- Displays results in two groups:
  - **Active IPs** -> marked as `in use` (red)
  - **Non-active IPs** -> marked as `possibly free` (green)
- Prints a final summary with total scanned, active, and non-active counts

## Features

- Fast scanning with parallel workers (thread pool)
- Configurable ping timeout
- Automatic IP sorting in output
- Colored terminal output (using `colorama`)
- Works on Windows and Linux/macOS (uses OS-specific ping flags)

## Requirements

- Python 3.10+
- `colorama` (for colored output)

Install dependency:

```bash
pip install colorama
```

## Usage

Run the scanner with:

```bash
python network_scanner.py <start_ip> <end_ip>
```

Example:

```bash
python network_scanner.py 192.168.1.1 192.168.1.254
```

### Optional Arguments

- `-w, --workers` -> number of parallel ping workers (default: `100`)
- `-t, --timeout-ms` -> ping timeout in milliseconds (default: `800`)

Example with options:

```bash
python network_scanner.py 192.168.1.1 192.168.1.254 -w 150 -t 1000
```

## Notes

- `in use` means the host responded to ping.
- `possibly free` means no ping response was received. Some devices block ping, so this does not always guarantee the IP is truly free.
- Use this tool only on networks you own or have permission to scan.

## File Structure

- `network_scanner.py` -> main scanner script
- `README.md` -> project documentation

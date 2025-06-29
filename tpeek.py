#!/usr/bin/env python3

import os
import subprocess
import datetime
from pathlib import Path
import re

OUTPUT_DIR = Path("scan_results")
OUTPUT_DIR.mkdir(exist_ok=True)

def banner():
    print("""\033[95m
┌────────────────────────────────────────────┐
│                 Tpeek                      │
│      Tactical Network Peek Tool 🕵         │
│     Made by: OmarTamer0 (Egypt) 🔧         │
└────────────────────────────────────────────┘
\033[0m""")
                 
                 
def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def beautify_port_output(line):
    parts = re.split(r'\s{2,}', line.strip())
    return " | ".join(parts)

def live_scan(command):
    print("\n\033[96m[~] Scanning... Showing OPEN ports and services:\033[0m\n")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    print("\033[93m{:<10} {:<10} {:<15} {}[0m".format("PORT", "STATE", "SERVICE", "VERSION"))
    print("\033[93m" + "-" * 60 + "\033[0m")
    for line in process.stdout:
        if "open" in line and "/tcp" in line:
            if re.search(r"\d+/tcp\s+open", line):
                line_clean = beautify_port_output(line)
                print(f"\033[92m[+] {line_clean}\033[0m")

def full_scan(target, verbose):
    cmd = ["nmap", "-p-", "-A", target]
    if verbose:
        cmd.append("-v")
    live_scan(cmd)

def stealth_scan(target, verbose):
    cmd = ["nmap", "-sS", "-Pn", target]
    if verbose:
        cmd.append("-v")
    live_scan(cmd)

def port_scan(target, port, verbose):
    cmd = ["nmap", "-p", str(port), "-sV", target]
    if verbose:
        cmd.append("-v")
    live_scan(cmd)

def os_detection(target, verbose):
    cmd = ["nmap", "-O", target]
    if verbose:
        cmd.append("-v")
    live_scan(cmd)

def top_ports(target, verbose):
    cmd = ["nmap", "--top-ports", "100", "-sV", target]
    if verbose:
        cmd.append("-v")
    live_scan(cmd)

def scan_vulnerable_versions(target, service):
    print(f"[*] Scanning for known vulnerabilities in {service.upper()} on {target}...")
    output_file = OUTPUT_DIR / f"vuln_scan_{service}_{target}_{timestamp()}.txt"
    scripts = {
        "smb": ["nmap", "-p", "445", "--script", "smb-vuln*", target],
        "ssh": ["nmap", "-p", "22", "--script", "sshv1,ssh2-enum-algos", target],
        "ldap": ["nmap", "-p", "389", "--script", "ldap*", target]
    }
    if service in scripts:
        with open(output_file, "w") as f:
            subprocess.run(scripts[service], stdout=f)
        print(f"\033[92m[+] Vulnerability scan complete. Results saved to: {output_file}\033[0m\n")
    else:
        print("\033[91m[!] Invalid service type. Choose smb, ssh, or ldap.\033[0m")

def main():
    banner()
    print("""
Choose an option:
1. Full TCP Scan with OS and Version Detection
2. Stealth SYN Scan
3. Specific Port Scan
4. OS Detection Only
5. Top 100 Ports Scan
6. Scan for Known Vulnerabilities (SMB, SSH, LDAP)
    """)
    choice = input("[?] Enter your choice (1-6): ").strip()
    target = input("[?] Enter the target IP or domain: ").strip()
    verbose = input("[?] Enable verbose mode? (y/n): ").strip().lower() == "y"

    if choice == "1":
        full_scan(target, verbose)
    elif choice == "2":
        stealth_scan(target, verbose)
    elif choice == "3":
        port = input("[?] Enter the port number to scan: ").strip()
        port_scan(target, port, verbose)
    elif choice == "4":
        os_detection(target, verbose)
    elif choice == "5":
        top_ports(target, verbose)
    elif choice == "6":
        service = input("[?] Enter service name (smb / ssh / ldap): ").strip().lower()
        scan_vulnerable_versions(target, service)
    else:
        print("\033[91m[!] Invalid option. Exiting.\033[0m")

if __name__ == "__main__":
    main()

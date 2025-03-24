import subprocess
import json
import sys
import time
import os

target = "10.0.0.186"
def run_nmap_scan(target):
    command = ["nmap", "-A", target]  # Using -A for a detailed scan
    
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            print("Error executing nmap:", result.stderr)
            sys.exit(1)
        return result.stdout
    except Exception as e:
        print("An error occurred while executing nmap:", str(e))
        sys.exit(1)

def parse_nmap_output(output):
    scan_results = {"hosts": []}
    lines = output.split("\n")
    host_info = {}
    
    for line in lines:
        if "Nmap scan report for" in line:
            if host_info:
                scan_results["hosts"].append(host_info)
                host_info = {}
            host = line.split(" ")[-1]
            if "(" in host and ")" in host:
                host = host[host.find("(")+1:host.find(")")]
            host_info = {
                "host": host, 
                "status": "Unknown", 
                "os": "Unknown", 
                "ports": [], 
                "services": [], 
                "traceroute": "Unknown", 
                "mac_address": "Unknown",
                "manufacturer": "Unknown",
                "hostnames": [],
                "service_versions": [],
                "os_fingerprint": "Unknown",
                "host_up_time": "Unknown"
            }
        
        elif "Host is up" in line:
            host_info["status"] = "Up"
        elif "Host is down" in line:
            host_info["status"] = "Down"
        elif "MAC Address:" in line:
            parts = line.split(" ", 3)
            if len(parts) > 2:
                host_info["mac_address"] = parts[2]
                host_info["manufacturer"] = parts[3].strip("()") if len(parts) == 4 else "Unknown"
        elif "Hostnames:" in line:
            hostnames = line.split("Hostnames:")[-1].strip()
            host_info["hostnames"] = hostnames.split(", ")
        elif "OS details:" in line:
            host_info["os"] = line.split("OS details:")[1].strip()
        elif "Running:" in line:
            host_info["os"] = line.split("Running:")[1].strip()
        elif "/tcp" in line or "/udp" in line:
            port_info = line.strip()
            host_info["ports"].append(port_info)
        elif "open" in line and ("/tcp" in line or "/udp" in line):
            port_info = line.split()[0]  # Extracting port number and protocol
            host_info["ports"].append(port_info)
        elif "Service Info:" in line:
            service_info = line.split("Service Info:")[-1].strip()
            host_info["services"].append(service_info)
        elif "TRACEROUTE" in line:
            host_info["traceroute"] = "Available"
        elif "OS fingerprint" in line:
            host_info["os_fingerprint"] = line.split(":")[1].strip()
        elif "Uptime:" in line:
            host_info["host_up_time"] = line.split(":")[1].strip()
    
    if host_info:
        scan_results["hosts"].append(host_info)
    
    return scan_results

def save_results(scan_results, filename='wieye_app/lib/DetailedResult.json'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # ✅ Create folders if missing
    with open(filename, 'w') as file:
        json.dump(scan_results, file, indent=4)
    print(f"Nmap scan results saved to {filename}")


def nmapScan(target):
    print("Starting scan...")
    
    start_time = time.time()  # Record the start time
    output = run_nmap_scan(target)
    scan_results = parse_nmap_output(output)
    save_results(scan_results)
    end_time = time.time()  # Record the end time
    
    scan_duration = end_time - start_time  # Calculate the scan duration
    print(f"Scan completed in {scan_duration:.2f} seconds.")  # Display the time taken

nmapScan(target)

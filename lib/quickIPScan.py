import subprocess
import json
import sys
import time

def run_ping_scan(target):
    command = ["nmap", "-sP", target]
    
    try:
        start_time = time.time()
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        
        if result.stderr:
            print("Error executing nmap:", result.stderr)
            sys.exit(1)
        
        scan_duration = end_time - start_time
        print(f"Ping scan completed in {scan_duration:.2f} seconds.")
        
        return result.stdout, scan_duration
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
            if "." in host:  # This condition filters out hostnames and includes only IP addresses
                host_info = {"host": host, "status": "up"}
    
    if host_info:
        scan_results["hosts"].append(host_info)
    
    return scan_results

def save_results(scan_results, scan_duration, filename='wieye_app/lib/IPResult.json'): # Save result to a JSON file
    scan_results["scan_duration"] = f"{scan_duration:.2f} seconds"
    with open(filename, 'w') as file:
        json.dump(scan_results, file, indent=4)
    print(f"Ping scan results saved to {filename}")

def pingScan(networkIP):
    target = networkIP
    print("Scanning for IPs...")
    output, scan_duration = run_ping_scan(target)
    scan_results = parse_nmap_output(output)
    save_results(scan_results, scan_duration)

def constantPingScan(networkIP):
    while True:
        pingScan(networkIP)

if __name__ == "__main__":
    constantPingScan("10.0.1.0/24")

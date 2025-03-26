import subprocess
import json
import sys
import time

def run_osscan(target):
    command = ["nmap", "-O", "-T4", target]  # Added -T4 for faster scanning
    
    try:
        start_time = time.time()
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        
        if result.stderr:
            print("Error executing osscan:", result.stderr)
            sys.exit(1)
        
        scan_duration = end_time - start_time
        print(f"Scan completed in {scan_duration:.2f} seconds.")
        
        return result.stdout, scan_duration
    except Exception as e:
        print("An error occurred while executing osscan:", str(e))
        sys.exit(1)

def parse_osscan_output(output):
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
            host_info = {"host": host, "os": "Unknown"}
        elif "OS details:" in line:
            host_info["os"] = line.split("OS details:")[1].strip()
        elif "Running:" in line:
            host_info["os"] = line.split("Running:")[1].strip()
    
    if host_info:
        scan_results["hosts"].append(host_info)
    
    return scan_results

def save_results(scan_results, scan_duration, filename='../lib/OSResult.json'):
    scan_results["scan_duration"] = f"{scan_duration:.2f} seconds"
    with open(filename, 'w') as file:
        json.dump(scan_results, file, indent=4)
    print(f"OS scan results saved to {filename}")

def osscan(IPAddress):
    target = IPAddress
    print("Scanning for OS...")
    output, scan_duration = run_osscan(target)
    scan_results = parse_osscan_output(output)
    save_results(scan_results, scan_duration)

def constantOSScan(IPAddress):
    while True:
        osscan(IPAddress)

if __name__ == "__main__":
    constantOSScan("10.0.1.0/24")
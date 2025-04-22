import subprocess
import json
import sys
import time
from networkManagement import blockUser
import os
from logger import log_event
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
        log_event(f"Scan completed in {scan_duration:.2f} seconds.")
        
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

def save_results(scan_results, scan_duration):
    FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','wieye_app', 'lib'))
    filename = os.path.join(FLUTTER_LIB_PATH, 'OSResult.json')

    scan_results["scan_duration"] = f"{scan_duration:.2f} seconds"
    with open(filename, 'w') as file:
        json.dump(scan_results, file, indent=4)
    print(f"OS scan results saved to {filename}")
    log_event(f"OS scan results saved")

def osscan(IPAddress):
    target = IPAddress
    print("Scanning for OS...")
    log_event("Scanning for OS...")
    output, scan_duration = run_osscan(target)
    scan_results = parse_osscan_output(output)
    save_results(scan_results, scan_duration)
    process_os_results()

def process_os_results():
    # Open and load the JSON data
    os_result_path = os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib', 'OSResult.json')
    with open(os.path.abspath(os_result_path), 'r') as file:
        data = json.load(file)

    # Define allowed OS patterns
    allowed_keywords = ["Windows 10", "Windows 11", "iOS", "Android", "Unknown"]

    # Block any host whose OS is NOT in the allowed list
    for host in data.get("hosts", []):
        os_info = host.get("os", "")
        if not any(keyword.lower() in os_info.lower() for keyword in allowed_keywords):
            # Ensure the 'host' key is correct (contains the IP)
            ip_address = host["host"]
            print(f"Blocking IP: {host['host']}")
            blockUser(ip_address)
            osscan("10.0.1.0/24")

    return data



def constantOSScan(IPAddress):
    while True:
        osscan(IPAddress)

if __name__ == "__main__":
    constantOSScan("10.0.1.0/24")
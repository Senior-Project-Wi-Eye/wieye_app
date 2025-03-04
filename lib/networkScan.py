import subprocess
import json
import sys
def run_nmap_scan(target):
    command = ["nmap", "-sS", "-O", target]  # Added -O for OS fingerprinting
    
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
            host_info = {"host": host, "status": "up", "manufacturer": "Unknown", "os": "Unknown"}
        elif "MAC Address:" in line:
            parts = line.split(" ", 3)
            if len(parts) > 2:
                host_info["mac"] = parts[2]
                host_info["manufacturer"] = parts[3].strip("()") if len(parts) == 4 else "Unknown"
        elif "OS details:" in line:
            host_info["os"] = line.split("OS details:")[1].strip()
        elif "Running:" in line:
            host_info["os"] = line.split("Running:")[1].strip()
    
    if host_info:
        scan_results["hosts"].append(host_info)
    
    return scan_results

def save_results(scan_results, filename='wieye_app/lib/NmapScanResult.json'):
    with open(filename, 'w') as file:
        json.dump(scan_results, file, indent=4)
    print(f"Nmap scan results saved to {filename}")

def nmapScan():
    # Change the 10 dot to whatever the network local ip is
    print ("Starting scan...")
    target = "10.15.0.0/20"
    # target = input("Enter the target IP (e.g., '192.168.1.0/24'): ")
    output = run_nmap_scan(target)
    scan_results = parse_nmap_output(output)
    save_results(scan_results)

while(True):
    nmapScan()

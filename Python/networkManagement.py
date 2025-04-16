from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scapy.all import ARP, Ether, srp
import os
import json

def scan_network():
    iface = "Ethernet 2"
    network_range = "10.0.1.0/24"

    print(f"Scanning network {network_range} on interface '{iface}'...")
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered_list = srp(broadcast / arp_request, timeout=2, iface=iface, verbose=False)[0]

    devices = {resp.psrc: resp.hwsrc for _, resp in answered_list}
    return devices

def get_mac_address(ip, devices):
    return devices.get(ip, "MAC address not found")

def show_devices(devices):
    print("\nConnected Devices:")
    print("IP Address\t\tMAC Address")
    print("-" * 50)
    for ip, mac in devices.items():
        print(f"{ip}\t{mac}")
    print()

def block_mac_address(mac_address):
    # Set Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    
    # Launch Chrome with options
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    
    try:
        # Open the target page
        driver.get("http://10.0.1.1")
        
        # Wait for the login input field to be visible
        wait = WebDriverWait(driver, 10)
        login = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/form/div/div[2]/div/div/div/div/input')))
        login.send_keys('Zq59@@ugu2')
        
        # Wait for login button and click
        loginbutton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/button')))
        loginbutton.click()
        
        advancebutton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div[2]/div/div[2]/div[5]')))
        advancebutton.click()
        
        SecurityPanel = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[1]/div/ul/li[8]/div/div')))
        SecurityPanel.click()
        
        accessControl = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[1]/div/ul/li[8]/ul/li[2]/div/span[1]')))
        accessControl.click()
        
        AddDeny = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div[1]/div/div[1]/div/div/div/div/div/div[2]/form/div[2]/div[2]/div')))
        AddDeny.click()
        
        Manual = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[1]/div[2]/label')))
        Manual.click()
        
        MACAddress = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/form/div[2]/div[2]/div/div/input[1]')))
        MACAddress.send_keys(mac_address)
        
        Finalize = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[3]/button[2]')))
        Finalize.click()
        
    finally:
        # Close the driver after execution
        driver.quit()

# Example usage:
# block_mac_address("F834412B9F17")


def save_results(mac_address, ip_address):  # Save result to a JSON file with index
    # Construct the path to the Flutter app's 'lib' directory
    FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))
    
    # Define the filename for the JSON file
    filename = os.path.join(FLUTTER_LIB_PATH, 'BlockedDevices.json')
    
    # Check if the file already exists
    if os.path.exists(filename):
        # Read the existing content of the JSON file
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        # Initialize an empty dictionary if the file doesn't exist
        data = {}

    # Convert keys to integers for index comparison and find the highest index
    numeric_keys = [int(key) for key in data.keys() if key.isdigit()]
    max_index = max(numeric_keys, default=0)
    
    # Create the entry for the new device at index 1
    new_data = {
        "1": {
            "mac_address": mac_address,
            "ip_address": ip_address,
            "status": "blocked"
        }
    }
    
    # Shift all existing devices by incrementing their indices
    for idx in range(max_index, 0, -1):
        data[str(idx + 1)] = data.pop(str(idx))

    # Add the new device at index 1
    data.update(new_data)

    # Write the updated data back to the JSON file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Blocked device (MAC: {mac_address}, IP: {ip_address}) saved to {filename} with index 1")



def blockUser(ipaddress):
    # Construct the path to the Flutter app's 'lib' directory
    FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))
    filename = os.path.join(FLUTTER_LIB_PATH, 'BlockedDevices.json')

    # Check if the IP address already exists in the JSON file
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            for entry in data.values():
                if entry.get("ip_address") == ipaddress:
                    print(f"IP address {ipaddress} is already blocked.")
                    return

    devices = scan_network()

    if not devices:
        print("No devices found.")
        return

    mac = get_mac_address(ipaddress, devices)

    if mac == "MAC address not found":
        print(f"MAC address for IP {ipaddress} not found. Aborting block operation. Please try again.")
        return

    block_mac_address(mac.replace(":", ""))
    save_results(mac, ipaddress)

    
def unblockUser(mac):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    
    # Launch Chrome with options
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    
    try:
        # Open the target page
        driver.get("http://10.0.1.1")
        
        # Wait for the login input field to be visible
        wait = WebDriverWait(driver, 10)
        login = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/form/div/div[2]/div/div/div/div/input')))
        login.send_keys('Zq59@@ugu2')
        
        # Wait for login button and click
        loginbutton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/button')))
        loginbutton.click()
        
        advancebutton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div[2]/div/div[2]/div[5]')))
        advancebutton.click()
        
        SecurityPanel = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[1]/div/ul/li[8]/div/div')))
        SecurityPanel.click()
        
        accessControl = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[1]/div/ul/li[8]/ul/li[2]/div/span[1]')))
        accessControl.click()
        
        xpath = configureXPath(mac)
        # print(xpath)
        
        TrashIcon = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        TrashIcon.click()
        
        confirm = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[2]/button[2]')))
        confirm.click()

    finally:
        # Close the driver after execution
        driver.quit()

def configureXPath(mac):
    # Normalize input MAC address
    normalized_mac = mac.lower().replace('-', ':')

    # Set path to JSON file
    FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))
    filename = os.path.join(FLUTTER_LIB_PATH, 'BlockedDevices.json')

    # Read the blocked devices data from the JSON file
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        print("BlockedDevices.json not found.")
        return None

    # Search for MAC address
    for index, device in data.items():
        device_mac = device.get('mac_address', '').lower().replace('-', ':')
        if device_mac == normalized_mac:
            xpath = f'//*[@id="app"]/div/div/div[2]/div/div[2]/div[1]/div/div[1]/div/div/div/div/div/div[2]/form/div[2]/div[3]/div[1]/div[2]/div/div[1]/div/table/tbody/tr[{index}]/td[4]/div/div/div/div'
            removeBlockedDeviceFromList(index)
            return xpath

    print(f"MAC address {mac} not found in blocked devices.")
    return None

def removeBlockedDeviceFromList(index_to_remove):
    # Set path to JSON file
    FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))
    filename = os.path.join(FLUTTER_LIB_PATH, 'BlockedDevices.json')

    # Check if file exists
    if not os.path.exists(filename):
        print("BlockedDevices.json not found.")
        return False

    # Load current data
    with open(filename, 'r') as f:
        data = json.load(f)

    index_str = str(index_to_remove)

    if index_str not in data:
        print(f"Index {index_to_remove} not found in blocked devices.")
        return False

    # Remove the specified device
    del data[index_str]

    # Reorder entries starting from 1
    temp = []
    for key in sorted(data.keys(), key=int):
        temp.append(data[key])  # Collect values in ascending order

    # Assign new keys starting from 1
    reordered = {}
    for new_index, entry in enumerate(temp, start=1):
        reordered[str(new_index)] = entry

    # Reverse keys to descending order
    descending_ordered = dict(sorted(reordered.items(), key=lambda x: int(x[0]), reverse=True))

    # Save back to JSON
    with open(filename, 'w') as f:
        json.dump(descending_ordered, f, indent=4)

    print(f"Device at index {index_to_remove} removed. Indices updated and saved in descending order.")
    return True

def main():
    blockUser("10.0.1.172")
    # unblockUser("a6:5d:22:a7:04:eb")
    # devices = scan_network()
    # show_devices(devices)

if __name__ == "__main__":
    main()
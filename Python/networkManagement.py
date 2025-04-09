from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scapy.all import ARP, Ether, srp

def scan_network():
    network_range = "10.0.1.0/24"  # Modify if your network uses a different subnet
    print(f"Scanning network {network_range}...")
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered_list = srp(broadcast / arp_request, timeout=2, verbose=False)[0]

    devices = {}
    for element in answered_list:
        devices[element[1].psrc] = element[1].hwsrc

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


def blockUser(ipaddress):
    devices = scan_network()
    
    if not devices:
        print("No devices found.")
        return
    mac = get_mac_address(ipaddress, devices)
    block_mac_address(mac.replace(":", ""))
    
def main():
    blockUser("10.0.1.172")

if __name__ == "__main__":
    main()

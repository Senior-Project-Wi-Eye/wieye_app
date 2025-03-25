import requests
from bs4 import BeautifulSoup

# Router credentials and details
ROUTER_IP = "http://10.0.1.1"  # Change this if needed
# USERNAME = "admin"  # Your router's username
PASSWORD = "Z959@@ugu2"  # Your router's password
TARGET_IP = "10.0.1.168"  # IP address of the unwanted device

# Create a session to maintain login
session = requests.Session()

def login_to_router():
    """Logs into the router and returns the session if successful."""
    login_url = f"{ROUTER_IP}/login.cgi"
    login_payload = {
        # "username": USERNAME,
        "password": PASSWORD
    }
    
    response = session.post(login_url, data=login_payload)
    
    if response.status_code == 200:
        print("Login successful!")
        return True
    else:
        print("Login failed! Check credentials and try again.")
        return False

def get_security_token(response):
    """Extracts a token from the response (if needed by the router)."""
    soup = BeautifulSoup(response.text, 'html.parser')
    # Example: Extract token if it's required, adjust accordingly for your router
    token = None
    token_tag = soup.find("input", {"name": "csrf_token"})
    if token_tag:
        token = token_tag.get('value')
    return token

def block_device(ip_address, token=None):
    """Blocks the device by its IP address."""
    block_url = f"{ROUTER_IP}/access_control.cgi"  # Adjust this URL for your model
    block_payload = {
        "ip": ip_address,
        "action": "block",  # This might vary depending on your router
        "token": token if token else ""  # Include token if needed
    }
    
    block_response = session.post(block_url, data=block_payload)
    if block_response.status_code == 200:
        print(f"Device with IP {ip_address} has been blocked!")
    else:
        print("Failed to block the device. Check router settings.")
    
def logout_from_router():
    """Logs out from the router."""
    logout_url = f"{ROUTER_IP}/logout.cgi"
    session.get(logout_url)
    print("Logged out.")

def main():
    """Main function to handle the workflow."""
    if login_to_router():
        # Step 1: Get the security token if required
        response = session.get(ROUTER_IP)  # Or wherever you get the initial page
        token = get_security_token(response)
        
        # Step 2: Block the unwanted device
        block_device(TARGET_IP, token)
        
        # Step 3: Log out after the operation
        logout_from_router()

if __name__ == "__main__":
    main()

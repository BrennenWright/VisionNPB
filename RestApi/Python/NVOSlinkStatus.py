###########################################################################
#  linkStatus.py uses the NVOS RESTAPI to poll a list of ports
###########################################################################

import requests
import time
from tabulate import tabulate
import os
requests.packages.urllib3.disable_warnings() 

# Constants
API_URL = "https://10.10.4.236:8000/api/ports/"
AUTH_USER = "admin"
AUTH_PASS = "admin"
PORTS_TO_WATCH = ['P01','P02','P52']
POLL_INTERVAL = 2  # seconds

# Globals
auth_token = ""

# Function to fetch data from the API
def fetch_port_status(port="01"):
    global auth_token
    # Use basic authentication for the first request
    auth = (AUTH_USER, AUTH_PASS)
    
    headers = {}
    if auth_token:
        headers = {
            "Authentication": auth_token
        }
    else:
        response = requests.get(API_URL+port+"?properties=link_status", auth=auth, verify=False)  # Use basic auth for the first request
        if response and "X-auth-token" in response.headers:
            auth_token = response.headers["X-auth-token"]
        else:
            print("Failed to authenticate or retrieve auth token.")
            return None

    try:
        response = requests.get(API_URL+port+"?properties=link_status", headers=headers, verify=False)  # Disable SSL verification for localhost
        response.raise_for_status()  # Raise an error for bad status codes
        return response

    except requests.exceptions.RequestException as e:
        
        if "401" in f'{e}':
            response = requests.get(API_URL+port+"?properties=link_status", auth=auth, verify=False)  # Use basic auth for the first request
            if response and "X-auth-token" in response.headers:
                auth_token = response.headers["X-auth-token"]
                return fetch_port_status(port)
            else:
                print("Failed to authenticate or retrieve auth token.")
                return None
        else:
            print(f"Error fetching data: {e}")
            return None    
        return fetch_port_status(port)

# Function to clear the terminal screen
def clear_screen():
    # Clear the terminal screen
    os.system("cls" if os.name == "nt" else "clear")


# Main loop
def main():
    try:
        while True:

            table = [["Port", "Duplex" ,"Link Up","Pause", "Speed"]]

            for port in PORTS_TO_WATCH:

                # Fetch data from the API
                response = fetch_port_status(port)

                if response:
                    data = response.json()
                    table.append([port,data["link_status"]["duplex"], data["link_status"]["link_up"], data["link_status"]["pause"], data["link_status"]["speed"]])

            # Clear the screen before displaying the new table
            clear_screen()

            # Display the result
            print("[                    Link Status                    ]")
            print(tabulate(table, headers="firstrow", tablefmt="simple_grid"))


            # Wait for the next poll
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()

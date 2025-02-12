###########################################################################
#  KVOdevices.py prints all devices in inventory and
#   all device live ports
#   all device negative alarms
###########################################################################

import requests
import time
from tabulate import tabulate
import os
requests.packages.urllib3.disable_warnings() 

# Constants
API_URL = "https://10.10.4.21/api/v2/"
AUTH_URL = "https://10.10.4.21/auth/realms/keysight/protocol/openid-connect/token"
AUTH_REFRESH__TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJiYThiNDRjZS1lYTk4LTRiZmItYjA4OC04YjEwNmFmZTMzMmEifQ.eyJpYXQiOjE3Mzg4ODMwNTYsImp0aSI6IjliOTJhY2JjLTY2ZmYtNDg5MS1hYzQ1LTI0MGFjMjcwNmUzMSIsImlzcyI6Imh0dHBzOi8vMTAuMTAuNC4yMS9hdXRoL3JlYWxtcy9rZXlzaWdodCIsImF1ZCI6Imh0dHBzOi8vMTAuMTAuNC4yMS9hdXRoL3JlYWxtcy9rZXlzaWdodCIsInN1YiI6IjU3YTM0NWVjLTEwNjgtNDRlZC04ZmM4LWYwOGZhYmVjYmU5ZCIsInR5cCI6Ik9mZmxpbmUiLCJhenAiOiJ2aXNpb24tb3JjaGVzdHJhdG9yIiwibm9uY2UiOiJjNTMxZjY2MS1jYTYxLTQ4OGUtODcxZS0yMWEzZmZkNmFhZTQiLCJzZXNzaW9uX3N0YXRlIjoiYmVjZTgzYjAtZWQ3ZC00MThjLTlmZGUtNzdjNjk4OTVjOWViIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsInNpZCI6ImJlY2U4M2IwLWVkN2QtNDE4Yy05ZmRlLTc3YzY5ODk1YzllYiJ9.Q1IJUzBqg1W56xfrWUeBkfLjPWX6vyOQOPfAxpy-Ac8"
AUTH_USER = "admin"
AUTH_PASS = "admin"
POLL_INTERVAL = 60  # seconds

# Globals
auth_token = ""

# Function to fetch the list of managed devices from KVO
def fetch_devices():
    global auth_token    
    API_ENDPOINT = "inventory/devices"

    headers = {}
    if auth_token:
        headers = {
            "Authorization": "Bearer "+auth_token
        }
    try:
        response = requests.get(API_URL+API_ENDPOINT, headers=headers, verify=False)  # Disable SSL verification for localhost
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        # On an authentication error
        if "401" in f'{e}':
            #Refresh the token
            if authorize():
                return fetch_device_port_status(DEVICE_TO_WATCH)
            else:
                print("Failed to authenticate or retrieve auth token.")
                return None
        elif "connect timeout" in f'{e}':
            print(f"Connection to {API_URL} timeout. Please check your connection and restart the script")
            sys.exit()
        else:
            print(f"Error fetching data: {e}")
        return response

# Function to get port status
# /inventory/devices/{uid}/status/ports
def fetch_device_port_status(uid):
    global auth_token    
    API_ENDPOINT = f"inventory/devices/{uid}/status/ports"

    headers = {}
    if auth_token:
        headers = {
            "Authorization": "Bearer "+auth_token
        }
    try:
        response = requests.get(API_URL+API_ENDPOINT, headers=headers, verify=False)  # Disable SSL verification for localhost
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        # On an authentication error
        if "401" in f'{e}':
            #Refresh the token
            if authorize():
                return fetch_device_port_status(DEVICE_TO_WATCH)
            else:
                print("Failed to authenticate or retrieve auth token.")
                return None
        elif "connect timeout" in f'{e}':
            print(f"Connection to {API_URL} timeout. Please check your connection and restart the script")
            sys.exit()
        else:
            print(f"Error fetching data: {e}") 
        return response

# Function to clear the terminal screen
def clear_screen():
    # Clear the terminal screen
    os.system("cls" if os.name == "nt" else "clear")

# Function to authorize with Keysight Vision Orchestrator
# Returns true and false for success and failure
def authorize():
    global auth_token
    try: 
        authData = {
            "client_id":"vision-orchestrator",
            "refresh_token": AUTH_REFRESH__TOKEN,
            "grant_type":"refresh_token"
        }
        response = requests.post(AUTH_URL, data=authData, verify=False)
        response.raise_for_status()  # Raise an error for bad status codes
        auth_token = response.json()["access_token"]
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error authorizing: {e}")
        return False

# Main loop
def main():
    # First authorize and get a 15min token
    if not authorize():
        sys.exit()
     
    try:
        while True:
            # Display the result
            devices = fetch_devices().json()
            table = [["Device", "UID", "Cluster","IP"]]
            table_ports = [["Device","Port","LinkUp"]]
            table_alarms = [["Device","Alarm","State"]]

            for device in devices:
                table.append([device['name'],device['uid'],device['cluster'],device['ip']])
                ports = fetch_device_port_status(device['uid']).json()
                for port in ports[0]['portsStatus']:
                    if port['linkUp']:
                        table_ports.append([ports[0]['name'],port['portName'],port['linkUp']])
                if device['subsystemAlarms']:
                    for alarm in device['subsystemAlarms']:
                        if alarm['state'] != 'OK':
                            table_alarms.append([device['name'],alarm['name'],alarm['state']])

            # Clear the screen before displaying the new table
            clear_screen()
            # Print our tables
            print("                                     Devices in KVO")
            print(tabulate(table, headers="firstrow", tablefmt="simple_grid"))

            print("\n\n                                     Ports on Devices")
            print(tabulate(table_ports, headers="firstrow", tablefmt="simple_grid"))

            print("\n\n                                     Alarms on Devices")
            print(tabulate(table_alarms, headers="firstrow", tablefmt="simple_grid"))

            # Wait for the next poll
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()

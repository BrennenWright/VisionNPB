###########################################################################
#  portWatch.py follows a ports link status and tracks any changes
#  the seconds since launch are tracked and used to time the delay between
#  port status changes
###########################################################################

import requests
import time
import os
requests.packages.urllib3.disable_warnings() 

# Constants
API_URL = "https://10.10.4.21/api/v2/"
AUTH_URL = "https://10.10.4.21/auth/realms/keysight/protocol/openid-connect/token"
AUTH_REFRESH__TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJiYThiNDRjZS1lYTk4LTRiZmItYjA4OC04YjEwNmFmZTMzMmEifQ.eyJpYXQiOjE3Mzg4ODMwNTYsImp0aSI6IjliOTJhY2JjLTY2ZmYtNDg5MS1hYzQ1LTI0MGFjMjcwNmUzMSIsImlzcyI6Imh0dHBzOi8vMTAuMTAuNC4yMS9hdXRoL3JlYWxtcy9rZXlzaWdodCIsImF1ZCI6Imh0dHBzOi8vMTAuMTAuNC4yMS9hdXRoL3JlYWxtcy9rZXlzaWdodCIsInN1YiI6IjU3YTM0NWVjLTEwNjgtNDRlZC04ZmM4LWYwOGZhYmVjYmU5ZCIsInR5cCI6Ik9mZmxpbmUiLCJhenAiOiJ2aXNpb24tb3JjaGVzdHJhdG9yIiwibm9uY2UiOiJjNTMxZjY2MS1jYTYxLTQ4OGUtODcxZS0yMWEzZmZkNmFhZTQiLCJzZXNzaW9uX3N0YXRlIjoiYmVjZTgzYjAtZWQ3ZC00MThjLTlmZGUtNzdjNjk4OTVjOWViIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsInNpZCI6ImJlY2U4M2IwLWVkN2QtNDE4Yy05ZmRlLTc3YzY5ODk1YzllYiJ9.Q1IJUzBqg1W56xfrWUeBkfLjPWX6vyOQOPfAxpy-Ac8"
AUTH_USER = "admin"
AUTH_PASS = "admin"
POLL_INTERVAL = 2  # seconds
DEVICE_TO_WATCH = "a59786e2-30a7-4838-8732-b83c7056a57a"
PORT_TO_WATCH = "P01"

# Globals
auth_token = ""

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

# Function to authorize
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

    started = time.time()
    last=started
    logs = []

    try:
        while True:
            # Fetch data from the API
            response = fetch_device_port_status(DEVICE_TO_WATCH)

            # Clear the screen before displaying the new table
            clear_screen()
            for log in logs:
                print(log)
            if response:
                # Display the result
                ports = response.json()
                for port in ports[0]['portsStatus']:
                    if port['portId'] == PORT_TO_WATCH:
                        if port['linkUp']:
                            if not logs:
                                logs.append(f" {round(time.time()-started)} - PORT STATUS {PORT_TO_WATCH} : CONNECTED")
                            if "DOWN" in logs[-1]:
                                logs.append(f" {round(time.time()-started)} - PORT STATUS {PORT_TO_WATCH} : CONNECTED")
                            print(f" {round(time.time()-started)} - PORT STATUS {PORT_TO_WATCH} : CONNECTED")
                        else:
                            if not logs:
                                logs.append(f" {round(time.time()-started)} - PORT STATUS {PORT_TO_WATCH} : DOWN DOWN DOWN!!!")
                            if "CONNECTED" in logs[-1]:
                                logs.append(f" {round(time.time()-started)} - PORT STATUS {PORT_TO_WATCH} : DOWN DOWN DOWN!!!") 
                            print(f" {round(time.time()-started)} - PORT STATUS {PORT_TO_WATCH} : DOWN DOWN DOWN!!!")    
                        break

            # Wait for the next poll
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()

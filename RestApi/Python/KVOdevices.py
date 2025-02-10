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

# Function to fetch data from the API
def fetch_deviceconfigs(auth_token=None):
    API_ENDPOINT = "fabric/deviceconfigs"

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
        print(f"Error fetching data: {e}")
        return None

# Function to clear the terminal screen
def clear_screen():
    # Clear the terminal screen
    os.system("cls" if os.name == "nt" else "clear")

# Function to authorize
def authorize():
    try: 
        authData = {
            "client_id":"vision-orchestrator",
	    "refresh_token": AUTH_REFRESH__TOKEN,
	    "grant_type":"refresh_token"
        }
        response = requests.post(AUTH_URL, data=authData, verify=False)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Main loop
def main():
    # First authorize and get a 15min token
    auth_token=authorize()
     
    try:
        while True:
            # Fetch data from the API
            response = fetch_deviceconfigs(auth_token)
            if response.status_code == 401:
                auth_token=authorize()
                response = fetch_deviceconfigs(auth_token)

            # Clear the screen before displaying the new table
            clear_screen()
            if response:
                # Display the result
                data = response.json()
                table = [["Device", "UID"]]
                for device in data:
                    table.append([device['name'],device['uid']])
                print("[                      Devices                    ]")
                print(tabulate(table, headers="firstrow", tablefmt="simple_grid"))
            # Wait for the next poll
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()

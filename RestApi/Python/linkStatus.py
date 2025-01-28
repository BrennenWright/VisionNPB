#! /usr/bin/env python

################################################################################
#
# File:   linkStatus.py
# Date:   Jan 28, 2025
# Author: Brennen Wright (brennen.wright@keysight.com)
#
# History:

# Description:
# This script polls the REST API interface for port link status and prints a
# table of the requested ports.
#
# This requires the tabulate and os packages for tables and clearing
#
# To install the required libraries:
# pip install requests tabulate
#
# COPYRIGHT 2017-2025 Keysight Technologies.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################
import requests
import time
from tabulate import tabulate
import os

# uncomment to suppress SSL warnings
#requests.packages.urllib3.disable_warnings() 

# Constants
API_URL = "https://localhost:9000/api/ports/P"
AUTH_USER = "admin"
AUTH_PASS = "admin"
POLL_INTERVAL = 2  # seconds

# Function to fetch data from the API
def fetch_port_status(auth_token=None,port="01"):
    # Use basic authentication for the first request
    auth = (AUTH_USER, AUTH_PASS)
    
    headers = {}
    if auth_token:
        headers = {
            "Authentication": auth_token
        }

    try:
        if auth_token:
            response = requests.get(API_URL+port, headers=headers, verify=False)  # Disable SSL verification for localhost
        else:
            response = requests.get(API_URL+port, auth=auth, verify=False)  # Use basic auth for the first request
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to clear the terminal screen
def clear_screen():
    # Clear the terminal screen
    os.system("cls" if os.name == "nt" else "clear")


# Main loop
def main():
    
    # First request with basic authentication
    response = fetch_port_status()
    if response and "X-auth-token" in response.headers:
        auth_token = response.headers["X-auth-token"]
    else:
        print("Failed to authenticate or retrieve auth token.")
        return None
        
    try:
        while True:
            # Clear the screen before displaying the new table
            clear_screen()
            
            # Fetch data from the API
            response = fetch_port_status(auth_token,"01")

            table = [["Port", "Duplex" ,"Link Up","Pause", "Speed"]]
            
            if response:
                # Extract the X-auth-token from the first response
                if "X-auth-token" in response.headers:
                    auth_token=response.headers["X-auth-token"]

                # Display the result
                data = response.json()
                table.append(["P01",data["link_status"]["duplex"], data["link_status"]["link_up"], data["link_status"]["pause"], data["link_status"]["speed"]])
                
            # Fetch data from the API
            response = fetch_port_status(auth_token,"02")

            if response:
                # Extract the X-auth-token from the first response
                if "X-auth-token" in response.headers:
                    auth_token=response.headers["X-auth-token"]

                # Display the result
                data = response.json()
                table.append(["P02",data["link_status"]["duplex"], data["link_status"]["link_up"], data["link_status"]["pause"], data["link_status"]["speed"]])
                

            print("[                    Link Status                    ]")
            print(tabulate(table, headers="firstrow", tablefmt="grid"))


            # Wait for the next poll
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()

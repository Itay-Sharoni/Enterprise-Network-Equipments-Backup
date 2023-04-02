#!/usr/bin/python3
import requests
import xml.etree.ElementTree as ET
import os
import sys
import datetime
import time
import getpass
import urllib3
import shutil
import argparse
import signal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def signal_handler(signal, frame):
    print("\nAborting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)



def get_inputs():
    parser = argparse.ArgumentParser(description="Backup Palo Alto firewall config and state")
    parser.add_argument("--firewall_ip", help="Firewall IP or hostname")
    parser.add_argument("--username", help="Firewall username")
    parser.add_argument("--password", help="Firewall password")
    parser.add_argument("--api_key", help="Optional - API Key")
    args = parser.parse_args()

    firewall_ip = args.firewall_ip or input("Enter the firewall IP or hostname: ")
    if not args.api_key:
        username = args.username or input("Enter the firewall username: ")
        password = args.password or getpass.getpass("Enter the firewall password: ")
        api_key = "skip"


        print(f"Connecting to {firewall_ip} using username/password")
        return firewall_ip, username, password, api_key
    else:
        api_key = args.api_key
        username = "none"
        password = "none"

        print(f"Connecting to {firewall_ip} using API key")
        return firewall_ip, username, password, api_key

def generate_api_key(firewall_ip, username, password):
    try:
        url_key = f"https://{firewall_ip}/api/?type=keygen&user={username}&password={password}"
        response_key = requests.get(url_key, verify=False)
        if response_key.status_code == 200:
            root = ET.fromstring(response_key.text)
            api_key = root.find("./result/key").text
            print(f"API Key generated succsecfuly\nAPI Key: {api_key}")
            return api_key
        else:
            api_key ="none"
            return api_key
    except:
        api_key ="none"
        return api_key



def get_device_name(firewall_ip, api_key):
    url_device = f"https://{firewall_ip}/api/?type=op&cmd=<show><system><info></info></system></show>&key={api_key}"
    response_device = requests.get(url_device, verify=False)
    if response_device.status_code == 200:
        root_device = ET.fromstring(response_device.text)
        device_name = root_device.find("./result/system/hostname").text
        print("Connection established")
        print(f"Device Name: {device_name}")
        return device_name
    else:
        device_name = "unknown"
        print("Error: failed to retrieve hostname from device")
        return device_name





def backup_config(firewall_ip, api_key, now, folder_path):
    url_config = f"https://{firewall_ip}/api/?type=export&category=configuration&key={api_key}"
    response_config = requests.get(url_config, verify=False)
    if response_config.status_code == 200:
        config = response_config.text
        file_name = f"{device_name}_config_{now.strftime('%d-%m-%y-%H-%M-%S')}.xml"
        file_path = os.path.join(folder_path, file_name)
        file_path_backup = file_path
        with open(file_path, "w") as file:
            file.write(config)
        print("Backup of configuration saved to:", file_path)
    else:
        print("Failed to retrieve configuration data from firewall. Error code:", response_config.status_code)

def backup_device_state(firewall_ip, api_key, now, folder_path):
    url_device_state = f"https://{firewall_ip}/api/?type=export&category=device-state&key={api_key}"
    response_device_state = requests.get(url_device_state, verify=False)
    if response_device_state.status_code == 200:
        file_name = f"{device_name}_device_state_{now.strftime('%d-%m-%y-%H-%M-%S')}.tgz"
        file_path = os.path.join(folder_path, file_name)
        file_path_device_state = file_path
        with open(file_path, "wb") as file:
            file.write(response_device_state.content)
        print("Backup file saved to:", file_path)
    else:
        print("Failed to retrieve device state data from firewall. Error code:", response_device_state.status_code)

def clean_backups(days_to_save):
    now = datetime.datetime.now()
    backup_folder = "backup"
    for root, dirs, files in os.walk(backup_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if (now - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))).days >= days_to_save:
                os.remove(file_path)
                print(f"Cleaned backup file older then {days_to_save} days: {file_path}")
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if (now - datetime.datetime.fromtimestamp(os.path.getmtime(dir_path))).days >= days_to_save:
                shutil.rmtree(dir_path)
                print(f"Cleaned backup file older then {days_to_save} days: {file_path}")


if __name__ == "__main__":
    firewall_ip, username, password, api_key = get_inputs()
    if api_key == "skip":
        api_key = generate_api_key(firewall_ip, username, password)
    if api_key != "none":
        now = datetime.datetime.now()
        year = str(now.year)
        month_name = now.strftime("%B")
        day_number = str(now.day)
        device_name = get_device_name(firewall_ip, api_key)
        backup_folder = f"backup/{year}/{month_name}/{day_number}/{device_name}"
        if not os.path.exists(backup_folder):
            if device_name != "unknown":
                os.makedirs(backup_folder)
        backup_config(firewall_ip, api_key, now, backup_folder)
        backup_device_state(firewall_ip, api_key, now, backup_folder)
        clean_backups(1) # or other number of days to save
    else:
        print("Failed to generate API key.")

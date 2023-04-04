#!/usr/bin/python3
import os
import sys
import time
import datetime
import shutil
import getpass
import urllib3
import argparse
import signal
import PaloAlto as palo
import Cisco as cisco


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def signal_handler(signal, frame):
    print("\nAborting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def get_inputs():
    #Vendor List
    vendor_list = [
            "PaloAlto",
            "CISCO_IOS",
            "CISCO_S300",
            "Clean Old Backups"
            ]

    parser = argparse.ArgumentParser(description="Backup Palo Alto firewall config and state")
    parser.add_argument("--vendor", help="Device Vendor", type=str, choices=vendor_list)
    parser.add_argument("--firewall_ip", help="Firewall IP or hostname")
    parser.add_argument("--username", help="Firewall username")
    parser.add_argument("--password", help="Firewall password")
    parser.add_argument("--api_key", help="Optional - API Key")
    args = parser.parse_args()

    if args.vendor:
        vendor = args.vendor
        vendor = vendor.lower()
    else:
        valid_choice = False
        while not valid_choice:
            print("Select a device vendor from the list:")
            i = 0
            for vendor in vendor_list:
                i += 1
                print(f"{i}. {vendor}")

            choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= choice <= len(vendor_list):
                valid_choice = True
                vendor = vendor_list[choice - 1]
                vendor = vendor.lower()
            else:
                print("Option not valid. Please enter a valid number.")


    firewall_ip = args.firewall_ip or input("Enter the device IP or hostname: ")
    if not args.api_key:
        username = args.username or input("Enter the device username: ")
        password = args.password or getpass.getpass("Enter the firewall password: ")
        api_key = "skip"

        print(f"Connecting to {firewall_ip} using username/password")
        return vendor, firewall_ip, username, password, api_key
    else:
        api_key = args.api_key
        username = "none"
        password = "none"

        print(f"Connecting to {firewall_ip} using API key")
        return vendor, firewall_ip, username, password, api_key


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
    #Get User Inputs from User or Args
    vendor, firewall_ip, username, password, api_key = get_inputs()
    #PaloAlto
    if vendor == "paloalto":
        if api_key == "skip":
            api_key = palo.generate_api_key(firewall_ip, username, password)
        if api_key != "none":
            now = datetime.datetime.now()
            year = str(now.year)
            month_name = now.strftime("%B")
            day_number = str(now.day)
            device_name = palo.get_device_name(firewall_ip, api_key)
            backup_folder = f"backup/{year}/{month_name}/{day_number}/{vendor}/{device_name}"
            if not os.path.exists(backup_folder):
                if device_name != "unknown":
                    os.makedirs(backup_folder)
            palo.backup_config(firewall_ip, api_key, now, backup_folder, device_name)
            palo.backup_device_state(firewall_ip, api_key, now, backup_folder, device_name)
        else:
            print("Failed to generate API Key.")
            print("Aborting...")
            sys.exit(0)

    #CISCO
    elif vendor == "cisco_ios" or vendor == "cisco_s300":
        vendor = vendor.lower()
        if api_key != "skip":
            print("API Key is not supported for CISCO devices, please use Username/Password.")
            print("Aborting...")
            sys.exit(0)

        ssh = cisco.connect_cisco_ssh(vendor, firewall_ip, username, password)
        if ssh is None:
            print("Failed to establish SSH connection. Exiting.")
            sys.exit(0)

        now = datetime.datetime.now()
        year = str(now.year)
        month_name = now.strftime("%B")
        day_number = str(now.day)

        device_name = cisco.get_device_name(ssh, vendor)

        backup_folder = f"backup/{year}/{month_name}/{day_number}/{vendor}/{device_name}"
        #backup_folder = "backup/"
        if not os.path.exists(backup_folder):
            if device_name != "unknown":
                os.makedirs(backup_folder)

        cisco.get_device_config(ssh, now, backup_folder, device_name)


    #CLEANUP
    elif vendor == "clean old backups":
        print("Cleanup.")


    else:
        print(f"Vendor {vendor} not supported")

    #clean_backups(1) # or other number of days to save

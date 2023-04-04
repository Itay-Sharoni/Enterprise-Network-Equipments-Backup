import os
import sys
import time
import datetime
from netmiko import ConnectHandler


def connect_cisco_ssh(device_type, device_ip, username, password):
    device = {
            'device_type': device_type,
            'ip': device_ip,
            'username': username,
            'password': password,
            'read_timeout_override': 20,
    }
    try:
        ssh = ConnectHandler(**device)
        return ssh
    except Exception as error:
        print(error)
        print("Aborting...")
        sys.exit(0)


def get_device_name(ssh, device_type):
    output = ssh.send_command("show run | include hostname", read_timeout=20)
    if device_type == "cisco_ios":
        output = output.split('\n')
        for line in output:
            if line.startswith("hostname "):
                output = line
                output = output.split()[1]

    elif device_type == "cisco_s300":
        output = output.split()
        output = output[1]

    if output == "":
        print("Could not retrive device hostname")
        print("Aborting...")
        sys.exit(0)
    device_name = output
    print(f"Device Name: {device_name}")
    return device_name

def get_device_config(ssh, now, folder_path, device_name):
    output = ssh.send_command("show run", read_timeout=20)
    #print(output)
    file_name = f"{device_name}_config_{now.strftime('%d-%m-%y-%H-%M-%S')}.txt"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "w") as file:
        file.write(output)
    print("Backup of configuration saved to:", file_path)




def main():
    print("Please use main.py")



if __name__ == "__main__":
    main()

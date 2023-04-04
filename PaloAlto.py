import requests
import xml.etree.ElementTree as ET
import os



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


def backup_config(firewall_ip, api_key, now, folder_path, device_name):
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


def backup_device_state(firewall_ip, api_key, now, folder_path, device_name):
    url_device_state = f"https://{firewall_ip}/api/?type=export&category=device-state&key={api_key}"
    response_device_state = requests.get(url_device_state, verify=False)
    if response_device_state.status_code == 200:
        file_name = f"{device_name}_device_state_{now.strftime('%d-%m-%y-%H-%M-%S')}.tgz"
        file_path = os.path.join(folder_path, file_name)
        file_path_device_state = file_path
        with open(file_path, "wb") as file:
            file.write(response_device_state.content)
        print("Backup of device state saved to:", file_path)
    else:
        print("Failed to retrieve device state data from firewall. Error code:", response_device_state.status_code)


def main():
    print("Please use main.py")



if __name__ == "__main__":
    main()

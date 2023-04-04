# Enterprise-Network-Equipments-Backup
The Ultimate backup server - work in progress

# Usage
Method 1 - Interactive Mode<br>
```
itay@WSL:~/opt$ ./main.py

Enter the firewall IP or hostname: fw1.test.local
Enter the firewall username: test
Enter the firewall password: 123456
Connecting to fw1.test.local using username/password
API Key generated succsecfuly
API Key: ....ucj34Zg==
Connection established
Device Name: TEST-FW1
Backup of configuration saved to: backup/2023/April/2/TEST-FW1/TEST-FW1_config_02-04-23-15-00-38.xml
Backup file saved to: backup/2023/April/2/TEST-FW1/TEST-FW1_device_state_02-04-23-15-00-38.tgz
```

Method 2 - Arg/Script Mode (note you can use user/pass or API)<br>
```
itay@WSL:~/opt$ ./main.py --vendor paloalto --firewall_ip fw1.test.local --username test --password 123456
itay@WSL:~/opt$ ./main.py --vendor paloalto --firewall_ip fw1.test.local --api_key "....ucj34Zg=="
```

Method 3 - Batch Mode (service) - Todo<br>


# Supported Devices
* PaloAlto PanOS 9+
* CISCO IOS
* CISCO S300


# Todo
* Add Support for Fortigate Firewalls
* Better Error Handling
* Review and Fix Cleanup
* Add Support for Batch mode (from CSV)
* Create Systemd Service (Batch mode)

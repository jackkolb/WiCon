"""
Contains support functions for the GUI
"""

import subprocess
import urllib.request


def parse_settings():
    settings = {}
    with open("./settings.cfg", "r") as settings_file:
        lines = settings_file.readlines()
    for line in lines:
        if line[0] == "#" or line == "\n" or line == "":
            continue
        key = line[:line.find('=')]
        value = line[line.find('=')+1:-1]
        settings[key] = value

    if settings['WIFI_INTERFACE'] == "AUTO":
        settings['WIFI_INTERFACE'] = get_default_interface()

    return settings


def create_connections_file():
    with open("./connections.cfg", "w") as connections_file:
        connections_file.write("# Listing of known WiFi logins, to append just follow the example formats.\n")
        connections_file.write("# Empty lines and lines starting with '#' are disregarded\n")
        connections_file.write("\n")
        connections_file.write("# For Open Networks\n")
        connections_file.write("#SSID\n")
        connections_file.write("SomeOpenWifi\n")
        connections_file.write("\n")
        connections_file.write("# For Password-Protected Networks\n")
        connections_file.write("#SSID\:|PASSWORD\n")
        connections_file.write("MyHomeWifi\:|SecretPassword\n")
        connections_file.write("\n")
        connections_file.write("# For Username & Password Networks ('WPA2-Enterprise')\n")
        connections_file.write("#SSID\:|USERNAME\:|PASSWORD\n")
        connections_file.write("MyWorkWifi\:|User123\:|SecretPassword\n")
        connections_file.write("\n")


def kill_wpa_supplicant():
    command = "killall wpa_supplicant"
    subprocess.run(command, shell=True)


def get_all_interfaces():
    output = str(subprocess.check_output(['ip', 'link'])).replace(" ", "").split('\\n')
    interfaces = []
    for i in range(0, len(output)):
        line = output[i]
        if ":<" in line:
            interfaces.append(line[line.find(":") + 1:line.find(":<")])

    if "lo" in interfaces:
        interfaces.remove("lo")
    return interfaces


def get_default_interface():
    interfaces = get_all_interfaces()

    # With the interface list, figure out which is the wifi interface
    interface = ""
    for i in interfaces:
        if "lo" in i:
            interfaces.remove(i)
        if "enp" in i:
            interfaces.remove(i)

    if len(interfaces) == 1:
        interface = interfaces[0]

    for i in interfaces:
        if "wlan" in i or "wlp" in i:
            interface = i
    return interface


def is_wifi_up():
    try:
        urllib.request.urlopen("https://www.google.com")
        return True
    except urllib.request.URLError:
        return False


def replaced_settings(settings):
    new_settings = settings
    for key in settings.keys():
        for subkey in settings.keys():
            new_settings[key] = settings[key].replace(subkey, settings[subkey])
    return new_settings


def get_connections():
    known_networks = get_known_connections()
    result = subprocess.run(['iwlist', 'wlp4s0', 'scan'], stdout=subprocess.PIPE)
    result = str(result.stdout).split("Cell ")
    networks = []
    for cell in result:
        items = cell.split('\\n')
        ssid = ""
        strength = ""
        sec_type = ""
        for line in items:

            if 'ESSID'in line:
                ssid = line[27:-1]

            if "Signal level=" in line:
                strength = line[line.find("Signal level")+13:-6]

            if "Encryption key:off" in line:
                sec_type = "OPEN"

            elif "Authentication Suites " in line:
                if "PSK" in line:
                    sec_type = "WPA2-PSK"
                else:
                    sec_type = "WPA2-ENT"

        if ssid != "" and sec_type != "" and strength != "":
            networks.append([ssid, sec_type, strength])

    networks.sort(key=lambda x: x[2])

    # go through and reject duplicate networks (preferring strongest) and hidden networks
    seen_networks = []
    refined_networks = []
    for network in networks:
        ssid = network[0]
        if ssid not in seen_networks and "\\\\x00" not in ssid and len(ssid) < 30:
            seen_networks.append(ssid)
            refined_networks.append(network)

    networks = refined_networks

    refined_networks = []
    for network in networks:
        if network[0] in known_networks.keys():
            network.append(True)
            network.append(False)
            refined_networks.append(network)
        else:
            network.append(False)
            network.append(False)
            refined_networks.append(network)

    networks = refined_networks
    return networks


def activate_wifi():
    settings = parse_settings()
    new_settings = replaced_settings(settings)
    command = new_settings['INTERFACE_ACTIVATE_COMMAND']
    command = command.replace('AUTO', get_default_interface())
    command = command.split(' ')
    subprocess.run(command)


def deactivate_wifi():
    settings = parse_settings()
    new_settings = replaced_settings(settings)
    command = new_settings['INTERFACE_DEACTIVATE_COMMAND']
    command = command.replace('AUTO', get_default_interface())
    command = command.split(' ')
    subprocess.run(command)


def get_known_connections():
    known_connections = {}
    with open("./connections.cfg", "r") as connections_file:
        lines = connections_file.readlines()
        for line in lines:
            if line == "" or line[0] == "#" or line == "\n":
                continue
            connection_info = line.split("\:|")
            ssid = connection_info[0]
            known_connections[ssid] = {}

            if len(connection_info) == 2:
                known_connections[ssid]['password'] = connection_info[1][:-1]
            if len(connection_info) == 3:
                known_connections[ssid]['username'] = connection_info[1]
                known_connections[ssid]['password'] = connection_info[2][:-1]
    return known_connections


def is_device_up():
    result = subprocess.run(['ip', 'link'], stdout=subprocess.PIPE)
    result = str(result.stdout).split('\\n')
    devices = {}
    for device in result:
        device = device.split(': ')
        if len(device) > 1:
            device_attributes = device[2].split(" ")
            devices[device[1]] = device_attributes[device_attributes.index("state")+1]
    settings = parse_settings()
    if settings['WIFI_INTERFACE'] == "AUTO" and get_default_interface() in devices.keys():
        status = devices[get_default_interface()]
    elif settings['WIFI_INTERFACE'] in devices.keys():
        status = devices[settings['WIFI_INTERFACE']]
    else:
        status = "UNKNOWN"

    if status == "UP":
        return True
    else:
        return False

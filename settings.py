"""
"Settings" window for changing WiCon settings
"""

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from wicon import *


class GridWindow(Gtk.Window):

    def __init__(self):
        # create window, title it "WiCon"
        Gtk.Window.__init__(self, title="WiCon - Settings")

        self.settings = parse_settings()

        # using grid layout container
        self.grid = Gtk.Grid()
        self.add(self.grid)

        # list all interfaces
        self.wifi_interface_label = Gtk.Label("WiFi Interface:")
        self.grid.attach(self.wifi_interface_label, 0, 1, 1, 1)

        interfaces = get_all_interfaces()
        col = 1

        self.interface_button = Gtk.RadioButton.new_with_label_from_widget(None, "AUTO")
        self.interface_button.connect("toggled", self.on_button_toggled, "inter")

        self.interface_dict = {}
        for i in interfaces:
            self.interface_button = Gtk.RadioButton.new_with_label_from_widget(self.interface_button, i)
            self.interface_button.connect("toggled", self.interface_toggle, i)
            self.grid.attach(self.interface_button, col, 1, 1, 1)

            self.interface_dict[i] = self.interface_button
            col += 1

        # Scanning Tools
        self.scanning_tool_label = Gtk.Label("Scanning Tool:")
        self.grid.attach(self.scanning_tool_label, 0, 3, 1, 1)

        self.scan_iw_button = Gtk.RadioButton.new_with_label_from_widget(None, "iw")
        self.scan_iw_button.connect("toggled", self.scan_tool_toggle, "iw")
        self.grid.attach(self.scan_iw_button, 1, 3, 1, 1)
        # Connection Manager

        self.connection_tool_label = Gtk.Label("Connection Tool:")
        self.grid.attach(self.connection_tool_label, 0, 4, 1, 1)

        self.conn_wpasupplicant_button = Gtk.RadioButton.new_with_label_from_widget(None, "wpa_supplicant")
        self.conn_wpasupplicant_button.connect("toggled", self.connection_toggle, "wpa_supplicant")
        self.grid.attach(self.conn_wpasupplicant_button, 1, 4, 1, 1)

        # DHCP Manager

        self.dhcp_tool_label = Gtk.Label("DHCP Tool:")
        self.grid.attach(self.dhcp_tool_label, 0, 5, 1, 1)

        self.dhcp_dhcpcd_button = Gtk.RadioButton.new_with_label_from_widget(None, "dhcpcd")
        self.dhcp_dhcpcd_button.connect("toggled", self.dhcp_toggle, "dhcpcd")
        self.grid.attach(self.dhcp_dhcpcd_button, 1, 5, 1, 1)

        # create "Save Settings" button, attach to grid container
        self.save_settings_button = Gtk.Button(label="Save Settings")
        self.save_settings_button.connect("clicked", self.on_save_clicked)
        self.grid.attach(self.save_settings_button, 0, 6, 3, 1)

        # create "Default Settings" button, attach to grid container
        self.default_settings_button = Gtk.Button(label="Default Settings")
        self.default_settings_button.connect("clicked", self.on_defaults_clicked)
        self.grid.attach(self.default_settings_button, 3, 6, 3, 1)

        self.load_settings()

    def load_settings(self):
        if self.settings["WIFI_INTERFACE"] == "AUTO":
            self.interface_dict[get_default_interface()].set_active("on")
        if self.settings["WIFI_INTERFACE"] != "AUTO":
            print(self.settings["WIFI_INTERFACE"])
            self.interface_dict[self.settings["WIFI_INTERFACE"]].set_active("on")

        if self.settings["SCAN_TOOL"] == "iw":
            self.scan_iw_button.set_active("on")

        if self.settings["CONNECTION_TOOL"] == "wpa_supplicant":
            self.conn_wpasupplicant_button.set_active("on")

        if self.settings["DHCP_TOOL"] == "dhcpcd":
            self.dhcp_dhcpcd_button.set_active("on")

    def on_button_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        print("Button", name, "was turned", state)

    def interface_toggle(self, button, name):
        if button.get_active():
            state = "TRUE"
            self.settings['WIFI_INTERFACE'] = name
        else:
            state = "FALSE"
        print("WIFI_INTERFACE:", name, ":", state)

    def scan_tool_toggle(self, button, name):
        if button.get_active():
            state = "TRUE"
            self.settings['SCAN_TOOL'] = name
        else:
            state = "FALSE"
        print("SCAN_TOOL:", name, ":", state)

    def connection_toggle(self, button, name):
        if button.get_active():
            state = "TRUE"
            self.settings['CONNECTION_TOOL'] = name
        else:
            state = "FALSE"
        print("CONNECTION_TOOL:", name, ":", state)

    def dhcp_toggle(self, button, name):
        if button.get_active():
            state = "TRUE"
            self.settings['POST_CONNECTION_TOOL'] = name
        else:
            state = "FALSE"
        print("POST_CONNECTION_TOOL:", name, ":", state)

    def on_save_clicked(self, button):
        self.save_settings()
        print("Settings saved")
        self.close()

    def on_defaults_clicked(self, button):
        self.settings['WIFI_INTERFACE'] = 'AUTO'
        self.settings['SCAN_TOOL'] = 'iw'
        self.settings['CONNECTION_TOOL'] = 'wpa_supplicant'
        self.settings['WPA_SUPPLICANT_CONF'] = '/etc/wpa_supplicant.conf'
        self.settings['WPA_SUPPLICANT_START_COMMAND'] = 'wpa_supplicant -B -i interface -c WPA_SUPPLICANT_CONF'
        self.settings['WPA_PASSPHRASE_COMMAND'] = 'wpa_passphrase SSID PASSPHRASE'
        self.settings['POST_CONNECTION_TOOL'] = 'dhcpcd'
        self.settings['DHCPCD_COMMAND'] = 'dhcpcd WIFI_INTERFACE'

        self.save_settings()
        print("Default settings saved")
        self.close()

    def save_settings(self, button):
        with open("./settings.cfg", 'w') as settings_file:
            settings_file.write('# WiCon Settings! These get read when WiCon is started or "Refreshed", and can mostly\n')
            settings_file.write('# be changed through the GUI "Settings" popup. The GUI will rewrite this file on every settings save!!\n')
            settings_file.write("\n")
            settings_file.write("# Feel free to edit this file, just DO NOT COMMENT/UNCOMMENT ANYTHING!\n")
            settings_file.write("# These comments will do their best to help :)\n")
            settings_file.write("# Honestly though, just best to handle most of this through the GUI..\n")
            settings_file.write("\n")
            settings_file.write("\n")
            settings_file.write("### Devices and Scanning ###\n")
            settings_file.write("\n")
            settings_file.write("# Which wifi interface should WiCon use? Common ones look like wlp5s0 or wlan0\n")
            settings_file.write("# You can also use AUTO to have it auto-detect (using 'ip link')\n")
            settings_file.write("WIFI_INTERFACE=" + self.settings["WIFI_INTERFACE"] + "\n")
            settings_file.write("\n")
            settings_file.write("# How should WiCon turn on the wifi interface? (uses 'ip' by default)\n")
            settings_file.write("INTERFACE_ACTIVATE_COMMAND=" + self.settings["INTERFACE_ACTIVATE_COMMAND"] + "\n")
            settings_file.write("INTERFACE_DEACTIVATE_COMMAND=" + self.settings["INTERFACE_DEACTIVATE_COMMAND"] + "\n")
            settings_file.write("\n")
            settings_file.write("# Which scanning tool should WiCon use? Valid inputs: 'iw'\n")
            settings_file.write("SCAN_TOOL=" + self.settings["SCAN_TOOL"] + "\n")
            settings_file.write("\n")
            settings_file.write("\n")
            settings_file.write("### Connection ###\n")
            settings_file.write("\n")
            settings_file.write("# Which connection tool should WiCon use? Valid inputs: 'wpa_supplicant'\n")
            settings_file.write("CONNECTION_TOOL=" + self.settings["CONNECTION_TOOL"] + "\n")
            settings_file.write("\n")
            settings_file.write("# Leave these uncommented, even if CONNECTION_TOOL is not wpa_supplicant\n")
            settings_file.write("# Change /etc/wpa_supplicant.conf to another wireless configuration file if desired\n")
            settings_file.write("WPA_SUPPLICANT_CONF=" + self.settings["WPA_SUPPLICANT_CONF"] + "\n")
            settings_file.write("WPA_SUPPLICANT_START_COMMAND=" + self.settings["WPA_SUPPLICANT_START_COMMAND"] + "\n")
            settings_file.write("WPA_PASSPHRASE_COMMAND=" + self.settings["WPA_PASSPHRASE_COMMAND"] + "\n")
            settings_file.write("\n")
            settings_file.write("SAVE_CONNECTIONS=TRUE")
            settings_file.write("\n")
            settings_file.write("### DHCP ###\n")
            settings_file.write("\n")
            settings_file.write("# Which dhcp tool should WiCon use? Valid inputs: 'dhcpcd'\n")
            settings_file.write("DHCP_TOOL=" + self.settings["DHCP_TOOL"] + "\n")
            settings_file.write("\n")
            settings_file.write("DHCPCD_COMMAND=" + self.settings["DHCPCD_COMMAND"] + "\n")
            settings_file.write("\n")
            settings_file.write("#END")


def open_settings_window():
    win = GridWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

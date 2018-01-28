"""
"Connect" window for entering the username/password of a new WiFi connection
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from wicon import *


class GridWindow(Gtk.Window):

    def __init__(self, ssid="", sec_type=""):
        # create window, title it "WiCon - Connect"
        Gtk.Window.__init__(self, title="WiCon - Connect")

        self.settings = parse_settings()

        self.ssid = ssid
        self.sec_type = sec_type

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.scanning_tool_label = Gtk.Label("Add New Connection")
        self.grid.attach(self.scanning_tool_label, 0, 0, 4, 1)

        self.ssid_label = Gtk.Label("SSID: ")
        self.grid.attach(self.ssid_label, 0, 1, 1, 1)

        self.ssid_entry = Gtk.Entry()
        self.ssid_entry.set_text(ssid)
        self.grid.attach(self.ssid_entry, 1, 1, 3, 1)

        # Security Type

        self.scanning_tool_label = Gtk.Label("Security Type:")
        self.grid.attach(self.scanning_tool_label, 0, 2, 1, 1)

        self.open_button = Gtk.RadioButton.new_with_label_from_widget(None, "Open")
        self.open_button.connect("toggled", self.sec_type_toggle, "open")
        self.grid.attach(self.open_button, 1, 2, 1, 1)

        # set focus to a button (so the entry field is not highlighted)
        self.open_button.grab_focus()

        self.password_button = Gtk.RadioButton.new_with_label_from_widget(self.open_button, "Password")
        self.password_button.connect("toggled", self.sec_type_toggle, "pass")
        self.grid.attach(self.password_button, 2, 2, 1, 1)

        self.userpass_button = Gtk.RadioButton.new_with_label_from_widget(self.open_button, "User/Pass")
        self.userpass_button.connect("toggled", self.sec_type_toggle, "userpass")
        self.grid.attach(self.userpass_button, 3, 2, 1, 1)

        # Login Info
        self.username_label = Gtk.Label("Username:")
        self.grid.attach(self.username_label, 0, 3, 1, 1)
        self.username_entry = Gtk.Entry()
        self.grid.attach(self.username_entry, 1, 3, 3, 1)

        self.password_label = Gtk.Label("Password:")
        self.grid.attach(self.password_label, 0, 4, 1, 1)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.grid.attach(self.password_entry, 1, 4, 2, 1)

        self.show_password_button = Gtk.ToggleButton("Show")
        self.show_password_button.connect("toggled", self.show_password_toggle, "open")
        self.grid.attach(self.show_password_button, 3, 4, 1, 1)

        # create "Connect" button, attach to grid container
        self.connect_button = Gtk.Button(label="Connect!")
        self.connect_button.connect("clicked", self.on_connect_clicked)
        self.grid.attach(self.connect_button, 0, 5, 5, 1)

        if self.sec_type == "OPEN":
            self.set_open()
        elif self.sec_type == "WPA2-PSK":
            self.set_password()
        elif self.sec_type == "WPA2-ENT":
            self.set_userpass()

    def set_open(self):
        self.username_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('grey'))
        self.password_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('grey'))

        self.username_entry.set_editable(False)
        self.password_entry.set_editable(False)

        self.username_entry.set_text("")
        self.password_entry.set_text("")

        self.open_button.set_active("on")

    def set_password(self):
        self.username_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('grey'))
        self.password_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('default'))

        self.username_entry.set_editable(False)
        self.password_entry.set_editable(True)

        self.username_entry.set_text("")

        self.password_button.set_active("on")

    def set_userpass(self):
        self.username_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('default'))
        self.password_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('default'))

        self.username_entry.set_editable(True)
        self.password_entry.set_editable(True)

        self.userpass_button.set_active("on")

    def show_password_toggle(self, button):
        if button.get_active():
            self.password_entry.set_visibility(True)

        else:
            self.password_entry.set_visibility(False)

    def sec_type_toggle(self, button, name):
        if button.get_active():
            self.sec_type = name

            if name == "open":
                self.set_open()
            if name == "pass":
                self.set_password()
            if name == "userpass":
                self.set_userpass()

            self.grid.attach(self.connect_button, 0, 10, 5, 1)

    def on_connect_clicked(self, button):
        self.sec_type = self.sec_type.lower()

        if self.sec_type == "open":
            connect(ssid=self.ssid, sec_type=self.sec_type, username="", password="")

        elif self.sec_type == "pass":
            connect(ssid=self.ssid, sec_type=self.sec_type, username="", password=self.password_entry.get_text())

        elif self.sec_type == "userpass":
            connect(ssid=self.ssid, sec_type=self.sec_type, username=self.username_entry.get_text(),
                    password=self.password_entry.get_text())

        self.close()


def add_wpa_supplicant_userpass(ssid, username, password):
    with open(parse_settings()['WPA_SUPPLICANT_CONF'], "a") as conf_file:
        conf_file.write("ctrl_interface=/var/run/wpa_supplicant" + "\n")
        conf_file.write("ap_scan=1" + "\n")
        conf_file.write("\n")
        conf_file.write("network={" + "\n")
        conf_file.write("   ssid=" + '"' + ssid + '"' + "\n")
        conf_file.write("   proto=RSN" + "\n")
        conf_file.write("   pairwise=CCMP" + "\n")
        conf_file.write("   eap=PEAP" + "\n")
        conf_file.write("   identity=" + '"' + username + '"' + "\n")
        conf_file.write("   password=" + '"' + password + '"' + "\n")
        conf_file.write("   key_mgmt=WPA-EAP" + "\n")
        conf_file.write("}" + "\n")


def add_wpa_supplicant_pass(ssid, password):
    with open(parse_settings()['WPA_SUPPLICANT_CONF'], "a") as conf_file:
        conf_file.write("ctrl_interface=/var/run/wpa_supplicant" + "\n")
        conf_file.write("ap_scan=1" + "\n")
        conf_file.write("\n")
        conf_file.write("network={" + "\n")
        conf_file.write("   ssid=" + '"' + ssid + '"' + "\n")
        conf_file.write("   psk=" + '"' + password + '"' + "\n")
        conf_file.write("}" + "\n")


def add_wpa_supplicant_open(ssid):
    with open(parse_settings()['WPA_SUPPLICANT_CONF'], "a") as conf_file:
        conf_file.write("ctrl_interface=/var/run/wpa_supplicant" + "\n")
        conf_file.write("ap_scan=1" + "\n")
        conf_file.write("\n")
        conf_file.write("network={" + "\n")
        conf_file.write("   ssid=" + '"' + ssid + '"' + "\n")
        conf_file.write("   key_mgmt=NONE" + "\n")
        conf_file.write("}" + "\n")


def remove_temp_wpa_supplicant_file():
    open(parse_settings()['WPA_SUPPLICANT_CONF'], 'w').close()


def connect(ssid="", sec_type="", username="", password=""):
    settings = parse_settings()
    settings = replaced_settings(settings)
    if settings["CONNECTION_TOOL"] == "wpa_supplicant":
        write = ""
        if sec_type == "open":
            kill_wpa_supplicant()
            interface = settings['WIFI_INTERFACE']
            add_wpa_supplicant_open(ssid=ssid)
            command = "sudo wpa_supplicant -B -i " + interface + " -c " + settings["WPA_SUPPLICANT_CONF"]
            print("Running connect command")
            subprocess.run(command, shell=True)
            write = ssid + "\n"

        elif sec_type == "pass":
            kill_wpa_supplicant()
            interface = settings['WIFI_INTERFACE']
            command = "sudo su -c 'wpa_supplicant -B -i " + interface + " -c <(wpa_passphrase " + '"' + ssid + '"'\
                      + " " + '"' + password + '"' + ")" + "'"
            print("Running connect command")
            subprocess.run(command, shell=True)
            write = ssid + "\:|" + password + "\n"

        elif sec_type == "userpass":
            kill_wpa_supplicant()
            interface = settings['WIFI_INTERFACE']
            add_wpa_supplicant_userpass(ssid=ssid, username=username, password=password)
            command = "sudo wpa_supplicant -B -i " + interface + " -c " + settings["WPA_SUPPLICANT_CONF"]
            print("Running connect command")
            subprocess.run(command, shell=True)
            write = ssid + "\:|" + username + "\:|" + password + "\n"

        if settings['SAVE_CONNECTIONS'] == "TRUE" and ssid not in get_known_connections().keys():
            with open("temp_wifi", "a") as temp_file:
                temp_file.write(write)
        remove_temp_wpa_supplicant_file()

    if settings['DHCP_TOOL'] == "dhcpcd":
        command = "sudo " + settings["DHCPCD_COMMAND"]
        print("Running dhcp command")
        subprocess.run(command, shell=True)


def open_connect_window(ssid="", sec_type=""):
    win = GridWindow(ssid=ssid, sec_type=sec_type)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return 1


def connect_known(ssid="BAD"):
    if ssid == "BAD":
        return
    connections = get_known_connections()
    sec_type = "open"
    username = ""
    password = ""
    if "username" in connections[ssid].keys():
        username = connections[ssid]["username"]
        sec_type = "userpass"
    elif "password" in connections[ssid].keys():
        password = connections[ssid]["password"]
        sec_type = "pass"
    connect(ssid, sec_type=sec_type, username=username, password=password)

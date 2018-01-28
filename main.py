"""
"Main" window for managing WiFi
"""

import os.path
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib
from wicon import *
from settings import open_settings_window
from connect import open_connect_window, connect_known


class GridWindow(Gtk.Window):

    def __init__(self):
        # create window, title it "WiCon"
        Gtk.Window.__init__(self, title="WiCon")

        # using grid layout container
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.ssid = ""
        self.sec_type = ""
        self.known = False

        # check connections.cfg
        self.check_connections_file()

        # create "scan", "Settings", and "Toggle WiFi" buttons
        self.button_scan = Gtk.Button(label="Scan")
        self.button_settings = Gtk.Button(label="Settings")
        self.button_togglewifi = Gtk.Button(label="Reset Wifi")

        self.button_scan.connect("clicked", self.on_scan_clicked)
        self.button_settings.connect("clicked", self.on_settings_clicked)
        self.button_togglewifi.connect("clicked", self.on_togglewifi_clicked)

        # attach buttons to grid container
        self.grid.attach(self.button_scan, 0, 0, 1, 1)
        self.grid.attach(self.button_settings, 1, 0, 1, 1)
        self.grid.attach(self.button_togglewifi, 2, 0, 1, 1)

        # create scrollable container (to house the wifi scan results)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_property('height_request', 300)  # set container height to 300px

        # create wifi scan TreeView, add to scrollable container
        self.create_wifi_gtk_section()
        self.scrolled_window.add(self.wifi_view)

        # attach scrollable container (with wifi_list attached) to grid container
        self.grid.attach(self.scrolled_window, 0, 1, 3, 5)

        # create status bar
        self.status = Gtk.Label("")
        self.grid.attach(self.status, 0, 6, 3, 1)

        # create "Connect" button, attach to grid container
        self.button_connect = Gtk.Button(label="Connect")
        self.button_connect.connect("clicked", self.on_connect_clicked)
        self.grid.attach(self.button_connect, 0, 7, 3, 1)

        self.settings = parse_settings()
        self.new_settings = self.replaced_settings()

        self.update_flag = True
        self.scan_flag = False

        self.status_update()

    def check_connections_file(self):
        if not os.path.isfile("./connections.cfg"):
            print("connections.cfg does not exist, creating default")
            create_connections_file()

    def replaced_settings(self):
        settings = self.settings
        for key in settings.keys():
            for subkey in settings.keys():
                settings[key] = settings[key].replace(subkey, settings[subkey])
        return settings

    def reset_wifi(self):
        kill_wpa_supplicant()
        deactivate_wifi()
        activate_wifi()

    def create_wifi_gtk_section(self):
        # Scan available networks, consolidate into list of lists: [[SSID, Type, Strength, Known]]
        self.store = Gtk.ListStore(str, str, str, bool, bool)
        self.wifi_view = Gtk.TreeView(self.store)
        renderer = Gtk.CellRendererText()
        renderer_toggle = Gtk.CellRendererToggle()

        ssid_column = Gtk.TreeViewColumn("SSID", renderer, text=0)
        type_column = Gtk.TreeViewColumn("Type", renderer, text=1)
        strength_column = Gtk.TreeViewColumn("dB", renderer, text=2)

        known_column = Gtk.TreeViewColumn("Known", renderer_toggle, active=3)
        self.wifi_view.append_column(ssid_column)
        self.wifi_view.append_column(type_column)
        self.wifi_view.append_column(strength_column)
        self.wifi_view.append_column(known_column)

        select = self.wifi_view.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

    def status_update(self):
        if self.scan_flag:
            self.status.set_text("Scanning")
        elif is_wifi_up():
            self.status.set_text("Connected!")
            with open("temp_wifi", "r") as temp_file:
                line = temp_file.readline()
                if line != "":
                    with open("connections.cfg", "a") as connections_file:
                        connections_file.write(line)
            open("temp_wifi", "w").close()

        else:
            self.status.set_text("Not Connected")

        GLib.timeout_add_seconds(.5, self.status_update)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter:
            self.ssid = model[treeiter][0]
            self.sec_type = model[treeiter][1]
            self.known = model[treeiter][3]

    def on_scan_clicked(self, button):
        print("scanning...")
        self.scan_flag = True
        Gtk.main_iteration()
        self.store.clear()
        wifi_list = get_connections()

        for wifi_info in wifi_list:
            self.store.append(wifi_info)

        self.wifi_view.set_model(self.store)

        self.scan_flag = False
        print("...complete")

    def on_settings_clicked(self, button):
        print("Opening Settings")
        open_settings_window()

    def on_togglewifi_clicked(self, button):
        print("Resetting WiFi")
        self.reset_wifi()
        print("...complete")

    def on_connect_clicked(self, button):
        print("Connecting...")
        if self.known:
            self.status.set_text("Connecting to known network")
            connect_known(self.ssid)
        else:
            self.status.set_text("Opening connecting window")
            open_connect_window(ssid=self.ssid, sec_type=self.sec_type)


win = GridWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
win.update_flag = False

WiCon ReadMe!

WiCon comes from a personal need: a simple, straightforward, wifi connection tool for ArchLinux.
In the current form, it is essentially a GUI wrapper for iw list, wpa_supplicant, and dhcpcd, however
can be expanded to support networkmanager, wicd, and other command-line managers.

To run, simply cd to the WiCon directory and run 'sudo python3 main.py'. The tool itself is pretty intuitive.

The tool is GTK3-based, however outputs useful information to the terminal, which is great when things
are not working.

Usage:
1. It's generally best to start with "Reset WiFi", to flush out other wifi processes
2. Press "Scan", wait a bit, the wifi list will populate
3. Select an access point, press "Connect"
4a. If the access point is known (in connections.cfg), it will connect automatically
4b. If not, a popup window will appear asking for the login information; press "Connect", and WiCon will try to connect
5. If the connection is successful, the login information will be added to "connections.cfg"

Notes:
- The tool does nothing particularly fancy, just sending terminal commands (so you don't have to!)
- Appending the above, if things aren't working out check the terminal output
- The "Reset" button kills wpa_supplicant and restarts the wireless device, usually this will fix problems
- Sometimes there are too many access points for "iw list" to process - keep scanning, it will work out eventually
- When multiple access points have the same name (like on University campuses), only the strongest signal is shown
- WiCon is intended for Open, WPA2, and WPA2-Enterprise networks only! (99.99% of the networks you see)
- Made in ArchLinux, should work for other distributions

Looking to contribute? Wish List:
- Tray icon! (I could not figure out how to do this in Python, may need C++?)
- Integration with networkmanager (nmcli) and/or wicd (wicd-cli), message me about this!
- Self-troubleshooting mechanisms for wpa_supplicant
- More settings ("Don't save connections", "Show repeated SSIDs", "Show hidden networks")
- Better hidden network filter
- Any other improvements you can see!

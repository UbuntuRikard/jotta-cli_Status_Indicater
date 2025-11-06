#Required Dependencies

This script is a System Tray GUI for an external application's status and requires the following system libraries and Python packages to be installed to function correctly on a Debian or Ubuntu system.

1. GNOME AppIndicator Libraries: For the system tray icon (AppIndicator3 in gi.repository).
2. Python Package Pillow (PIL): For image manipulation (flipping the icon).

---

###Step 1: Install System Dependencies (Debian/Ubuntu)

The script uses PyGObject to bind to GTK and AppIndicator3. You must install the necessary system packages using apt.

Open a terminal and run the following command:

```
sudo apt update
sudo apt install python3-gi gir1.2-appindicator3-0.1 libappindicator3-1 python3-pil python3-pil.imagetk
```

| Package | Purpose |
| :--- | :--- |
| python3-gi | Python bindings for GTK/GObject (PyGObject). |
| gir1.2-appindicator3-0.1 | GObject Introspection data for AppIndicator3 (required to import AppIndicator3). |
| libappindicator3-1 | The AppIndicator system library itself (may be needed for modern Ubuntu/Debian). |
| python3-pil | The Python Pillow (PIL) library for image handling. |
| python3-pil.imagetk | Additional PIL library (often required with GTK integration). |

Note: On newer Ubuntu versions, libappindicator3-1 may be replaced by libayatana-appindicator3-1 (and corresponding development packages). If the command above fails, you can try replacing libappindicator3-1 with libayatana-appindicator3-1.

---

###Step 2: Get Script and Icon Files

The easiest way to get the script and the required 'icons/' folder is by cloning the Git repository into your home directory (~/).

Open a terminal and run the following command:

```bash
cd ~
git clone https://github.com/UbuntuRikard/Make_ClusterProcessing_for_Shotcut
```

---

###Step 3: Run the Script

Once all dependencies are met, you can run the script directly from the terminal:

**Setting Up Automatic Startup via GUI (Startup Applications)**

This method ensures your script starts automatically every time you log into your graphical desktop environment (like GNOME/Ubuntu).

**Access Startup Applications**

    Open your computer's Activities/Applications Menu.

    Search for "Startup Applications" or "Startup Applications Preferences".

    Open the settings window.

**Add Your Script**

In the Startup Applications Preferences window:

    Click the "Add" button.

    Fill in the fields with the following details:

| Field	| Value
| :--- | :--- |
| Name	| Jotta Status Indicator (or a name of your choice)|
| Command	| python3 /home/USERNAME/Make_ClusterProcessing_for_Shotcut/jotta_status_indicator.py|
| Comment	| Displays status for Jotta-cli in the system tray. (Optional)|

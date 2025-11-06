#!/usr/bin/env python3
###
# This file is part of jotta_status_indicator - made by:
# Copyright (C) 2025 Rikard Svenningsen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
####
import pathlib
import os
import time
import signal
import threading
import gi
import re
from PIL import Image

# ----------------------------------------------------------------------
# Setup for GNOME AppIndicator (requires libappindicator3)
# ----------------------------------------------------------------------
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3, Gtk, GLib

# --------------------------- Path configuration ------------------------
# Base directory = folder where this script lives
BASE_DIR = pathlib.Path(__file__).resolve().parent
ICONS_DIR = BASE_DIR / "icons"

# Icon files (relative to the repository)
ICON_GREEN  = str(ICONS_DIR / "emblem-default.png")          # Up‑to‑date (OK)
ICON_ORANGE = str(ICONS_DIR / "emblem-synchronizing.png")   # Active transfer
ICON_RED    = str(ICONS_DIR / "emblem-important.png")      # Error / unknown state
# Temporary file used when we flip the green icon vertically
TEMP_FLIPPED_ICON = str(ICONS_DIR / "emblem-default-flipped.png")

# --------------------------- Log File Configuration ---------------------
# Define the path to the log file (tilde ~ is expanded to the user's home directory)
LOG_FILE_PATH = os.path.expanduser("~/.jottad/jottabackup.log")

# ----------------------------------------------------------------------
class StatusWindow(Gtk.Window):
    """A separate window that displays and periodically updates the jotta-cli status output."""
    def __init__(self):
        Gtk.Window.__init__(self, title="Jotta-cli Actual Status")
        self.set_default_size(500, 300)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_buffer = self.text_view.get_buffer()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.text_view)
        
        self.add(scrolled_window)
        
        # Start the periodic update function (5 seconds for status)
        self.timeout_id = GLib.timeout_add_seconds(5, self.update_content)
        
        # When the window is closed, stop the periodic updates
        self.connect("destroy", self._on_window_destroy)
        
        self.update_content()
        self.show_all()

    def update_content(self):
        """Fetches jotta-cli status and updates the text buffer."""
        status_output = os.popen("jotta-cli status").read()
        self.text_buffer.set_text(status_output)
        
        # Scroll to bottom after updating
        end_iter = self.text_buffer.get_end_iter()
        self.text_view.scroll_to_iter(end_iter, 0.0, False, 0.0, 0.0)

        return True
        
    def _on_window_destroy(self, widget):
        """Called when the window is closed. Stops the update timer."""
        GLib.source_remove(self.timeout_id)


# ----------------------------------------------------------------------
class JottaIndicator:
    """Main class that creates the tray indicator and updates its icon."""
    def __init__(self):
        # Create the AppIndicator object
        self.indicator = AppIndicator3.Indicator.new(
            "jotta-cli-status",          # Unique identifier
            ICON_GREEN,                  # Default icon
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.green_state = True
        self.status_window = None

        # Build the right‑click menu
        self.menu = Gtk.Menu()
        
        # 1. Menu Item: Actual Status (Opens GTK StatusWindow)
        status_item = Gtk.MenuItem(label="Actual Status")
        status_item.connect("activate", self.show_status_window)
        self.menu.append(status_item)
        
        # 2. Menu Item: Open Log File
        log_item = Gtk.MenuItem(label="Open Log File")
        log_item.connect("activate", self.open_log) 
        self.menu.append(log_item)
        
        # 3. Menu Item: About
        about_item = Gtk.MenuItem(label="About Jotta Status Indicator")
        about_item.connect("activate", self.show_about_dialog)
        self.menu.append(about_item)
        
        # Add a separator line
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # 4. Quit Item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        # Background thread that periodically checks Jotta‑CLI status
        self.running = True
        threading.Thread(target=self.update_status, daemon=True).start()
        
    # ------------------------------------------------------------------
    def show_status_window(self, source) -> None:
        """Opens a window displaying the continuously updated status output."""
        if self.status_window is None or not self.status_window.is_visible():
            self.status_window = StatusWindow()
        else:
            self.status_window.present()

    # ------------------------------------------------------------------
    def show_about_dialog(self, source) -> None:
        """Shows the GTK About dialog with license and author information (in English)."""
        about = Gtk.AboutDialog()
        
        # English content as requested
        about.set_program_name("Jotta Status Indicator")
        about.set_version("1.0.0.0") 
        about.set_copyright("Copyright © 2025 Rikard Svenningsen") 
        about.set_comments("A system tray utility for monitoring jotta-cli status.")
        
        # Authors/Credits including AI
        about.set_authors([
            "Designed by Rikard Svenningsen", 
            "Code generated by AI (Google Gemini)"
        ])

        # License Information (GNU GPL v3)
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_website("https://www.gnu.org/licenses/gpl-3.0.html")
        about.set_website_label("GNU General Public License v3")
        
        # Run the dialog
        about.run()
        about.destroy()

    # ------------------------------------------------------------------
    def open_log(self, source) -> None:
        """Opens the jottabackup.log file using the system's default text editor (via xdg-open)."""
        os.system(f"xdg-open {LOG_FILE_PATH} &")

    # ------------------------------------------------------------------
    def flip_icon(self, icon_path: str, output_path: str) -> None:
        """
        Flip the supplied icon vertically and save it to ``output_path``.
        Errors are silently ignored – the visual cue is optional.
        """
        try:
            image = Image.open(icon_path)
            flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            flipped_image.save(output_path)
        except Exception:
            pass

    # ------------------------------------------------------------------
    def update_status(self) -> None:
        """Poll ``jotta-cli status`` every few seconds and adjust the tray icon."""
        while self.running:
            # Run the external command and split its output into lines
            status_output = os.popen("jotta-cli status").read().splitlines()

            # Keep only lines that start with “Status”
            statuses = [
                line.strip()
                for line in status_output
                if line.strip().lower().startswith("status")
            ]

            # If no status line is found, show the error (red) icon
            if not statuses:
                self.indicator.set_icon(ICON_RED)
                time.sleep(5)
                continue

            # Regex patterns for the two states we care about
            up_to_date_pattern = re.compile(r"up to date", re.IGNORECASE)
            active_transfer_pattern = re.compile(r"(uploading|download|performing)", re.IGNORECASE)

            # Determine overall state
            all_up_to_date = all(up_to_date_pattern.search(s) for s in statuses)
            has_active_transfer = any(active_transfer_pattern.search(s) for s in statuses)

            # Choose the appropriate icon
            if all_up_to_date:
                if self.green_state:
                    self.indicator.set_icon(ICON_GREEN)
                else:
                    # Show a flipped version of the green icon for a subtle animation effect
                    self.flip_icon(ICON_GREEN, TEMP_FLIPPED_ICON)
                    self.indicator.set_icon(TEMP_FLIPPED_ICON)
                # Toggle the flag so the next cycle shows the opposite version
                self.green_state = not self.green_state
            elif has_active_transfer:
                self.indicator.set_icon(ICON_ORANGE)
            else:
                self.indicator.set_icon(ICON_RED)

            # Wait before checking again
            time.sleep(5)

    # ------------------------------------------------------------------
    def quit(self, source) -> None:
        """Stop the background thread and exit the GTK main loop."""
        # Ensure the status windows are also closed cleanly
        if self.status_window and self.status_window.is_visible():
            self.status_window.destroy()
            
        self.running = False
        Gtk.main_quit()


# ----------------------------------------------------------------------
# Proper handling of Ctrl+C (SIGINT) so the program terminates cleanly
# ----------------------------------------------------------------------
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Instantiate the indicator and start the GTK event loop
JottaIndicator()
Gtk.main()

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from subprocess import Popen, PIPE


class Screenshot:
    def capture(self, file, area, output):
        # TODO: Add save to file with output_mode
        grim_subprocess = Popen(["grim", "-g", area, file], stdout=PIPE)
        return grim_subprocess

    def area(self):
        geom_subprocess = Popen(["slurp", "-d"], stdout=PIPE, stderr=PIPE)
        (geom, _) = geom_subprocess.communicate()
        if geom_subprocess.returncode != 0:
            print("Area selection cancelled")
            return

        image = self.capture("-", geom.strip().decode("utf-8"), "")
        copy_subprocess = Popen(
            ["wl-copy", "--type", "image/png"], stdin=image.stdout, stdout=PIPE
        )
        # TODO: error handling
        image.wait()
        copy_subprocess.wait()
        tray.showMessage("grim-tray", "Screenshot has been copied to clipboard", icon)

    def window(self):
        # swaymsg -t get_tree | jq -r '.. | select(.pid? and .visible?) | .rect | "\(.x),\(.y) \(.width)x\(.height)"' | slurp
        swaymsg_subprocess = Popen(["swaymsg", "-t", "get_tree"], stdout=PIPE)
        jq_subprocess = Popen(
            [
                "jq",
                "-r",
                r'.. | select(.pid? and .visible?) | .rect | "\(.x),\(.y) \(.width)x\(.height)"',
            ],
            stdin=swaymsg_subprocess.stdout,
            stdout=PIPE,
        )
        # geomatry_subprocess.wait()
        # jq_subprocess.wait()

        geom_subprocess = Popen(
            ["slurp"], stdin=jq_subprocess.stdout, stdout=PIPE, stderr=PIPE
        )
        (geom, _) = geom_subprocess.communicate()
        if geom_subprocess.returncode != 0:
            print("Window selection canceled")
            return

        image = self.capture("-", geom.strip().decode("utf-8"), "")
        copy_subprocess = Popen(
            ["wl-copy", "--type", "image/png"], stdin=image.stdout, stdout=PIPE
        )
        # TODO: error handling
        image.wait()
        copy_subprocess.wait()
        tray.showMessage("grim-tray", "Screenshot has been copied to clipboard", icon)


screenshot = Screenshot()

ui = QApplication([])
ui.setQuitOnLastWindowClosed(False)

# Adding an icon
icon = QIcon("icon.svg")  # TODO: fix icon not showing

# Adding item on the menu bar
tray = QSystemTrayIcon()
tray.setIcon(icon)

# Creating the options
menu = QMenu()
option_area = QAction("Area")
option_area.triggered.connect(screenshot.area)
option_window = QAction("Window")
option_window.triggered.connect(screenshot.window)

menu.addAction(option_area)
menu.addAction(option_window)

# To quit the app
menu.addSeparator()
quit = QAction("Quit")
quit.triggered.connect(ui.quit)
menu.addAction(quit)

# Adding options to the System Tray
tray.setContextMenu(menu)
# tray.setVisible(True)
tray.show()

ui.exec()

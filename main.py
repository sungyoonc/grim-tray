from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from subprocess import Popen, PIPE
from enum import Enum, auto


class Mode(Enum):
    AREA = auto()
    WINDOW = auto()
    SCREEN = auto()
    OUTPUT = auto()


class Screenshot:
    def capture(self, mode, file="-", area="", output=""):
        # TODO: Add save to file with output_mode
        if mode == Mode.AREA or mode == Mode.WINDOW:
            grim_subprocess = Popen(["grim", "-g", area, file], stdout=PIPE)
        elif mode == Mode.SCREEN:
            grim_subprocess = Popen(["grim", file], stdout=PIPE)
        elif mode == Mode.OUTPUT:
            grim_subprocess = Popen(["grim", "-o", output, file], stdout=PIPE)
        else:
            return None
        return grim_subprocess

    def area(self):
        geom_subprocess = Popen(["slurp", "-d"], stdout=PIPE, stderr=PIPE)
        (geom, _) = geom_subprocess.communicate()
        if geom_subprocess.returncode != 0:
            print("Area selection cancelled")
            return

        image = self.capture(Mode.AREA, area=geom.strip().decode("utf-8"))
        if image == None:
            return
        copy_subprocess = Popen(
            ["wl-copy", "--type", "image/png"], stdin=image.stdout, stdout=PIPE
        )
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

        image = self.capture(Mode.WINDOW, area=geom.strip().decode("utf-8"))
        if image == None:
            return
        copy_subprocess = Popen(
            ["wl-copy", "--type", "image/png"], stdin=image.stdout, stdout=PIPE
        )
        # TODO: error handling
        image.wait()
        copy_subprocess.wait()
        tray.showMessage("grim-tray", "Screenshot has been copied to clipboard", icon)

    def screen(self):
        image = self.capture(Mode.SCREEN)
        if image == None:
            return
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
option_screen = QAction("Screen")
option_screen.triggered.connect(screenshot.screen)

menu.addAction(option_area)
menu.addAction(option_window)
menu.addAction(option_screen)

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

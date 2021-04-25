from GUI.socket_client import Ui_MainWindow
import Wiki_Scraper.scraper as Scraper
import subprocess
from sys import stderr

from PyQt5 import QtCore as qtc, QtGui, QtWidgets as qtw


class SocketWindow(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow() 
        self.ui.setupUi(self) # Build the UI
        self.ui.server_button.clicked.connect(self.start_server) # Connect the button to the start server function

        self.user_settings = Scraper.Settings() # Give the window a set of Scraper settings

    def log_message(self, message):
        self.ui.logging_box.appendPlainText(message)

    def run_in_background(self):
        # print("This ran in a separate thread wow!")
        Scraper.socketings(self.user_settings)
        exit(0)

    def update_settings(self):
        self.user_settings.set_socket_num(int(self.ui.socket_box_3.text()))
        if (self.ui.full_urls_3.isChecked() and self.user_settings.url_format != "Full"):
            self.user_settings.set_url_format("Full")
            self.log_message("Set URL Format to Full")
        if self.ui.include_titles_3.isChecked() != self.user_settings.titles:
            self.user_settings.set_titles(self.ui.include_titles_3.isChecked())
            self.log_message("Set titles to " + str(self.ui.include_titles_3.isChecked()))
        if self.ui.standard_filters_3.isChecked():
            self.user_settings.add_exclusion("wiki/Category:")
            self.user_settings.add_exclusion("wiki/Help:")
            self.user_settings.add_exclusion("wiki/Template")
            self.user_settings.add_exclusion("wiki/Wikipedia:")
            self.log_message("Added standard filters")
        self.log_message("Updated the settings")
    def start_server(self):
        # print("This is not a thing yet :)")
        self.update_settings()
        print(self.user_settings.get_commandline(), file=stderr)
        if self.user_settings.validate():
            # Scraper.socketings(self.user_settings) # This needs to be ran in separate thread !!!
            processholder = subprocess.Popen(self.user_settings.get_commandline(), shell=False)
            self.log_message("Started a server on port " + str(self.user_settings.socket_num))
            qtw.QMessageBox.information(self, "Nice", "The server is now running in the background.\nPress \"Ok\" to stop the server")
            try:
                processholder.kill() # hopefully this will actually kill the loop
                self.log_message("Killed server on port " + str(self.user_settings.socket_num))
            except:
                self.log_message("Failed to kill server.")
            # thread1.join()
            # Kill the thread here !!!
        else:
            qtw.QMessageBox.critical(self, "Invalid settings!", "Double check your settings!") # Would be cool to capture this stuff in the logging box :)


if __name__ == "__main__":
    app = qtw.QApplication([])
    window = SocketWindow()
    window.show()

    app.exec_()
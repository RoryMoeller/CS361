from design import Ui_MainWindow
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from pathlib import Path
try:
    from sys import _MEIPASS
except ImportError:
    _MEIPASS = None
import requests
import base64
from os import path, makedirs


class CiphertextGeneratorSettings():
    def __init__(self):
        self.save_input = False
        self.save_plain = False
        self.save_enc = False
        self.font_size = 1
        self.color_set = 0
        self.save_subdir = ""
        self.word_list = []


class SettingsHistory():
    def __init__(self):
        self.possible_indexes = [False] * 20  # No redo's are accessible
        self.possible_indexes[0] = True  # First (current) is accessible
        self.current_index = 0
        self.settings_list = []
        for _ in range(20):
            self.settings_list.append(CiphertextGeneratorSettings())

    def set_setting_spot(self,index,cp):
        self.settings_list[index].save_input = cp.save_input
        self.settings_list[index].save_plain = cp.save_plain
        self.settings_list[index].save_enc = cp.save_enc
        self.settings_list[index].save_subdir = cp.save_subdir
        self.settings_list[index].color_set = cp.color_set
        self.settings_list[index].font_size = cp.font_size
        self.settings_list[index].word_list = cp.word_list

    def add_setting_to_end(self,cp):
        for i in range(len(self.possible_indexes) - 1):
            self.settings_list[i] = self.settings_list[i + 1]
        self.set_setting_spot(self,19,cp)

    def add_settings_to_index(self, cp):
        self.current_index += 1  # advance pointer to current
        self.set_setting_spot(self.current_index,cp)
        self.possible_indexes[self.current_index] = True


    def add_settings_set(self, setting):
        if self.current_index == 19:  # if at end of settings array
            self.add_setting_to_end(setting)
        else:
            self.add_settings_to_index(setting)
            i = self.current_index + 1
            while i < len(self.possible_indexes):
                # Unset redo history after making a change
                self.possible_indexes[i] = False
                i += 1

    def get_previous_setting(self):
        if self.current_index < 1:
            return 0  # Cannot get previous if there is no previous
        self.current_index -= 1
        return self.settings_list[self.current_index]

    def get_next_setting(self):
        if self.current_index == 19:
            return 0
        if self.possible_indexes[self.current_index + 1]:  # If the next index is available
            self.current_index += 1
            return self.settings_list[self.current_index]
        return 0


class M_Window(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_icon()
        self.settings = CiphertextGeneratorSettings()
        self.ui.save_files_button.clicked.connect(self.save_button)
        self.ui.actionQuit.triggered.connect(self.close_app)
        self.ui.actionUndo.triggered.connect(self.undo_act)
        self.ui.actionRedo.triggered.connect(self.redo_act)
        self.setting_history = SettingsHistory()

        # Update the settings when these are clicked
        self.ui.save_input_txt.clicked.connect(self.update_settings)
        self.ui.save_plain_png.clicked.connect(self.update_settings)
        self.ui.save_enc_png.clicked.connect(self.update_settings)

    def set_icon(self):
        try:
            bundle = Path(_MEIPASS)  # Temp dir where executable stuff is
            path = str(bundle) + "\\icon.ico"  # Path to icon file from the temp dir
        except TypeError:
            # Currently breaks if ran from parent directory. Need fix.
            path = str(Path.cwd())
            path += "\\icon.ico"
        icon = qtg.QIcon()
        icon.addPixmap(qtg.QPixmap(path), qtg.QIcon.Normal, qtg.QIcon.Off)
        self.setWindowIcon(icon)

    def save_button(self):
        self.settings.word_list = self.ui.word_list.toPlainText().split()
        self.settings.save_subdir = self.ui.subfolder_dir.text()
        self.log_message("Started saving process...")
        if (self.settings.save_subdir == ""):
            self.log_message("Fatal Error: No provided subdirectory to save files to." + \
                "Please supply a folder name to \"Subfolder To Save to\" in Save Options ...")
            return
        else:
            if not path.exists(self.settings.save_subdir):
                makedirs(self.settings.save_subdir)
                self.log_message("Made subdirectory: " + self.settings.save_subdir)
        if not (self.settings.save_plain or self.settings.save_input or self.settings.save_enc):
            self.log_message("Cancelling: there is nothing to save. Please select at least one of the file types to save in Save Options...")
            return
        if self.settings.save_enc or self.settings.save_plain:
            wc = self.get_wordcloud()
            if wc != 0:
                if self.settings.save_plain:
                    file = open(self.settings.save_subdir + "/" + "".join(self.settings.word_list) + "_plain.png", "wb")
                    file.write(wc)
                    file.close()
                    self.log_message("Saved the plain .png file: " + "".join(self.settings.word_list) + "_plain.png")
                if self.settings.save_enc:
                    self.log_message("Saving encrypted files not supported yet")
            else:
                self.log_message("Internal Error: Recieved wordcloud is empty. Abandoned saving unrecieved data.")
        if self.settings.save_input:
            with open(self.settings.save_subdir + "/" + "".join(self.settings.word_list) + "_input.txt", "w") as file:
                file.write(" ".join(self.settings.word_list))
            self.log_message("Saved the input .txt file: " + "".join(self.settings.word_list) + "_input.txt")

    def close_app(self):
        exit(0)

    def undo_act(self):
        prev_set = self.setting_history.get_previous_setting()
        if prev_set == 0:
            self.log_message("No undo history available")
            return
        self.settings = prev_set
        self.equate_settings()
        self.repaint()
        self.log_message("Undid last setting change")

    def redo_act(self):
        next_set = self.setting_history.get_next_setting()
        if next_set == 0:
            self.log_message("No redo history available")
            return
        self.settings = next_set
        self.equate_settings()
        self.repaint()
        self.log_message("Redid last undo")

    def get_wordcloud(self):
        wc_settings = {
            'text': " ".join(self.settings.word_list),
            'size': str(self.settings.font_size),
            'color': str(self.settings.color_set)
        }
        response = requests.post("https://word-cloud-leungd.wn.r.appspot.com/cloud", json=wc_settings)
        try:
            return base64.b64decode(response.text[31:-2])
        except IndexError:
            self.log_message("Internal Error: unexpected response from wordcloud microservice")
            return 0
        except base64.binascii.Error:
            self.log_message("Internal Error: unexpected response from wordcloud microservice")
            return 0

    def log_message(self, message):
        self.ui.response_log.appendPlainText(message)
        self.repaint()  

    def update_settings(self):
        self.settings.save_input = self.ui.save_input_txt.isChecked()
        self.settings.save_plain = self.ui.save_plain_png.isChecked()
        self.settings.save_enc = self.ui.save_enc_png.isChecked()
        self.settings.save_subdir = self.ui.subfolder_dir.text()
        self.settings.font_size = self.ui.font_size.value()
        if self.ui.color_set_1.isChecked():
            self.settings.color_set = 0
        elif self.ui.color_set_2.isChecked():
            self.settings.color_set = 1
        else:
            self.settings.color_set = 2
        self.settings.word_list = self.ui.word_list.toPlainText().split()
        self.setting_history.add_settings_set(self.settings)

    def equate_settings(self):  # Update the UI to match the current self.settings
        self.ui.save_input_txt.setChecked(self.settings.save_input)
        self.ui.save_plain_png.setChecked(self.settings.save_plain)
        self.ui.save_enc_png.setChecked(self.settings.save_enc)
        self.ui.font_size.setValue(self.settings.font_size)
        self.ui.subfolder_dir.setText(self.settings.save_subdir)
        if self.settings.color_set == 0:
            self.ui.color_set_1.setChecked(True)
        elif self.settings.color_set == 1:
            self.ui.color_set_2.setChecked(True)
        else:
            self.ui.color_set_3.setChecked(True)


if __name__ == "__main__":
    app = qtw.QApplication([])
    window = M_Window()
    window.show()
    app.exec()

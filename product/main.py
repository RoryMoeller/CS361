from design import Ui_MainWindow
from PyQt5 import QtWidgets as qtw
import requests
# from bs4 import BeautifulSoup
# import re
import base64
from os import path, makedirs
# from sys import stderr


class CiphertextGeneratorSettings():
    def __init__(self):
        self.save_input = False
        self.save_plain = False
        self.save_enc = False
        self.save_subdir = ""
        self.word_list = []

    def __str__(self):
        res = ""
        res += "save input: " + str(self.save_input)
        res += "\nsave plain: " + str(self.save_plain)
        res += "\nsave enc: " + str(self.save_enc)
        res += "\nsave dir: " + self.save_subdir
        res += "\nwordlist: " + str(self.word_list)
        return res


class SettingsHistory():
    def __init__(self):
        self.possible_indexes = [False] * 20  # No redo's are accessible
        self.possible_indexes[0] = True  # First (current) is accessible
        self.current_index = 0
        self.settings_list = []
        for i in range(20):
            self.settings_list.append(CiphertextGeneratorSettings())

    def add_settings_set(self, setting):
        cp = setting
        if self.current_index == 19:  # if at end of settings array
            for i in range(len(self.possible_indexes) - 1):
                self.settings_list[i] = self.settings_list[i + 1]
            self.settings_list[19].save_input = cp.save_input
            self.settings_list[19].save_plain = cp.save_plain
            self.settings_list[19].save_enc = cp.save_enc
            self.settings_list[19].save_subdir = cp.save_subdir
            self.settings_list[19].word_list = cp.word_list
        else:
            self.current_index += 1  # advance pointer to current
            self.settings_list[self.current_index].save_input = cp.save_input
            self.settings_list[self.current_index].save_plain = cp.save_plain
            self.settings_list[self.current_index].save_enc = cp.save_enc
            self.settings_list[self.current_index].save_subdir = cp.save_subdir
            self.settings_list[self.current_index].word_list = cp.word_list
            self.possible_indexes[self.current_index] = True
            i = self.current_index + 1
            while i < len(self.possible_indexes):
                self.possible_indexes[i] = False  # Unset redo history after making a change
                i += 1

    def get_previous_setting(self):
        if self.current_index < 1:
            return 0  # Cannot get previous if there is no previous
        self.current_index -= 1
        # print("Returning ", self.settings_list[self.current_index])
        return self.settings_list[self.current_index]

    def get_next_setting(self):
        if self.current_index == 19:
            print("At end")
            return 0
        if self.possible_indexes[self.current_index + 1]:  # If the next index is available
            self.current_index += 1
            # print("Returning ", self.settings_list[self.current_index])
            return self.settings_list[self.current_index]
        # print("Set to False")
        return 0

    def __str__(self):
        l1 = ""
        for i in range(len(self.possible_indexes)):
            if self.possible_indexes[i]:
                l1 += "(T"
            else:
                l1 += "(F"
            count = 0
            if self.settings_list[i].save_plain:
                count += 1
            if self.settings_list[i].save_enc:
                count += 1
            if self.settings_list[i].save_input:
                count += 1
            l1 += str(count) + ")"
        l1 += '\n'
        l2 = ""
        for i in range(len(self.possible_indexes)):
            if i == self.current_index:
                l2 += " ^  "
            else:
                l2 += "    "
        return (l1 + l2)


class M_Window(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
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

    def save_button(self):
        # self.update_settings()
        self.settings.word_list = self.ui.word_list.toPlainText().split()
        self.settings.save_subdir = self.ui.subfolder_dir.text()

        if (self.settings.save_subdir == ""):
            self.log_message("No provided subdirectory to save to. Cancelling...")
            return
        else:
            if not path.exists(self.settings.save_subdir):
                makedirs(self.settings.save_subdir)
                self.log_message("Made subdirectory: " + self.settings.save_subdir)
        if not (self.settings.save_plain or self.settings.save_input or self.settings.save_enc):
            self.log_message("There is nothing to save.")
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
                self.log_message("Abandoned saving unrecieved data")
        if self.settings.save_input:
            with open(self.settings.save_subdir + "/" + "".join(self.settings.word_list) + "_input.txt", "w") as file:
                file.write(" ".join(self.settings.word_list))
            self.log_message("Saved the input .txt file: " + "".join(self.settings.word_list) + "_input.txt")

    def close_app(self):
        # print(self.setting_history)
        exit(0)

    def undo_act(self):
        prev_set = self.setting_history.get_previous_setting()
        if prev_set == 0:
            self.log_message("No undo history available")
            return
        self.settings = prev_set
        self.equate_settings()
        self.log_message("Undid last setting change")

    def redo_act(self):
        next_set = self.setting_history.get_next_setting()
        if next_set == 0:
            self.log_message("No redo history available")
            return
        self.settings = next_set
        self.equate_settings()
        self.log_message("Redid last undo")
        # self.log_message(wc)

    def get_wordcloud(self):
        data = {
            'text': " ".join(self.settings.word_list)
        }
        res = requests.post("https://word-cloud-leungd.wn.r.appspot.com/cloud", json=data)
        # print(re.findall(string=res.text, pattern="<img src=.*alt=\"\">")[0])
        # print(res.text, file=stderr)
        try:
            # return base64.b64decode(re.findall(string=res.text, pattern="<img src=.*alt=\"\">")[0][32:])
            # First 32 chars are tag & meta garb dont care about
            # return base64.b64decode(res.json()['image'][21:])
            return base64.b64decode(res.text[31:-2])
        except IndexError:
            self.log_message("Unexpected response from wordcloud microservice")
            return 0

    def log_message(self, message):
        self.ui.response_log.appendPlainText(message)

    def update_settings(self):
        self.settings.save_input = self.ui.save_input_txt.isChecked()
        self.settings.save_plain = self.ui.save_plain_png.isChecked()
        self.settings.save_enc = self.ui.save_enc_png.isChecked()
        self.settings.save_subdir = self.ui.subfolder_dir.text()
        self.settings.word_list = self.ui.word_list.toPlainText().split()
        self.setting_history.add_settings_set(self.settings)
        # self.log_message(str(self.settings))

    def equate_settings(self):  # Update the UI to match the current self.settings
        self.ui.save_input_txt.setChecked(self.settings.save_input)
        self.ui.save_plain_png.setChecked(self.settings.save_plain)
        self.ui.save_enc_png.setChecked(self.settings.save_enc)
        self.ui.subfolder_dir.setText(self.settings.save_subdir)


if __name__ == "__main__":
    app = qtw.QApplication([])
    window = M_Window()
    window.show()
    app.exec()

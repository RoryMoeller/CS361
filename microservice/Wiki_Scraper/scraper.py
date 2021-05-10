import getopt
import requests
import socket
import flask
from bs4 import BeautifulSoup
from os import path, makedirs
from sys import argv, stderr

# -s [socket number]
# -o [output file]
# -i [input URL]
# -d [delimiter]
# -e [substring to filter from results]
# --URL_Format [Full / Short]
# --titles (adds a tab character and appends the title of the page a link goes to)
# --std_filters (adds a set of common non-useful internal links to the exclusion list)
#       ['wiki/Category:', 'wiki/Help:', 'wiki/Template', 'wiki/Wikipedia:']
# --other_target [tag-to-find,sub-attribute-to-report]
# --require [substring to require in each attribute]
# --save_image [subfolder to save images in]

# Class for handling, setting & validating the various settings that can be passed when running the file


class Settings:
    def __init__(self):
        self.input_url = False
        self.output_file = False
        self.socket_num = False
        self.titles = False
        self.save_image = False
        self.url_format = "Short"
        self.delimiter = '\n'
        self.target = ["a", "href"]
        self.requirements = []
        self.exclusions = []

    def __str__(self):
        return \
            "input_url = " + str(self.input_url) +\
            "\noutput_file = " + str(self.output_file) +\
            "\nsocket_num = " + str(self.socket_num) +\
            "\nurl_format = " + str(self.url_format) +\
            "\ndelimiter = \"" + str(self.delimiter) + "\"" +\
            "\ntitles = \"" + str(self.titles) + "\"" +\
            "\nexclusion_list = " + str(self.exclusions) + \
            "\nrequirement_list = " + str(self.requirements) + \
            "\ntarget tag = " + str(self.target[0]) + \
            "\ntarget attribute = " + str(self.target[1]) +\
            "\nsave image location = " + str(self.save_image)

    def set_input_url(self, url):
        if self.socket_num:
            print("Cannot set input URL when using socket I/O", file=stderr)
            exit(1)
        self.input_url = url

    def set_output_file(self, output):
        if self.socket_num:
            print("Cannot set output file when using socket I/O", file=stderr)
            exit(1)
        self.output_file = output

    def set_socket_num(self, num):
        if self.input_url or self.output_file:
            print("Cannot use socket I/O with other I/O methods", file=stderr)
            exit(1)
        else:
            self.socket_num = num

    def set_delimiter(self, string):
        self.delimiter = string

    def set_url_format(self, urlformat):
        if urlformat not in ["Short", "Full"]:
            print("Invalid URL Format. Valid inputs are \"Short\" and \"Full\"", file=stderr)
            exit(1)
        else:
            self.url_format = urlformat

    def set_titles(self, boolarg):
        self.titles = boolarg

    def add_exclusion(self, string):
        if string not in self.exclusions:
            self.exclusions.append(string)
            return True
        return False

    def add_requirement(self, string):
        if string not in self.requirements:
            self.requirements.append(string)
            return True
        return False

    def set_target(self, string):
        lst = string.split(',')
        self.target[0] = lst[0]
        self.target[1] = lst[1]

    def set_save_location(self, string):
        self.save_image = string
        if len(string) > 0 and not path.exists(string):
            makedirs(string)
            print("[+] Made directory named " + string, file=stderr)

    def validate(self):
        if (self.socket_num) or (self.output_file and self.input_url):
            pass
        else:
            print("[!] Invalid options set.\nMake sure one I/O method is set.\nIf not using sockets, ensure both an input URL and an output file are set.\nCurrent settings:", file=stderr)
            print(self, file=stderr)
            return False
        if self.target != ['a', "href"]:
            if self.url_format != "Short":
                print("[!] Warning: URL format should often be set to short when using other target\nContinuing...", file=stderr)
            if self.titles:
                print("[!] Warning: Turning on titles may add unexpected text when using non-default target\nContinuing...", file=stderr)
        # if self.save_image and self.target != ["img","src"]:
        #     print("[!] Cannot save images if target is not img,src", file=stderr)
        #     return False
        return True

    def get_commandline(self):
        command_list = ["python", "Wiki_Scraper/scraper.py"]
        if self.input_url:
            command_list.append("-i")
            command_list.append(str(self.input_url))
        if self.output_file:
            command_list.append("-o")
            command_list.append(str(self.output_file))
        if self.socket_num:
            command_list.append("-s")
            command_list.append(str(self.socket_num))
        if self.titles:
            command_list.append("--titles")
        if self.save_image:
            command_list.append("--save_image")
            command_list.append(self.save_image)
        for i in self.requirements:
            command_list.append("--require")
            command_list.append(i)
        for i in self.requirements:
            command_list.append("-e")
            command_list.append(i)
        command_list.append("-d")
        command_list.append(str(self.delimiter))
        command_list.append("--URL_Format")
        command_list.append(self.url_format)
        command_list.append("--other_target")
        command_list.append(",".join(self.target))
        return command_list


# Functions for helping users when incorrect usage is noticed
def print_option():
    print("Valid options are: \n\
    -s [socket number] \n\
    -o [output file] \n\
    -i [input URL] \n\
    -d [delimiter] \n\
    -e [substring to filter from results] \n\
    --require [substring to require in result attribute] \n\
    --titles (adds a tab character and appends the title of the page a link goes to) \n\
    --URL_Format [Full / Short] \n\
    --std_filters (adds a set of common internal links to non-article pages to the exclusion list) \n\
    --other_target [tag,attribute] \n\
    --save_image [subfolder]", file=stderr)


def print_options(problem):
    print(problem, file=stderr)
    print("Valid options are: \n\
    -s [socket number] \n\
    -o [output file] \n\
    -i [input URL] \n\
    -d [delimiter] \n\
    -e [substring to filter from results] \n\
    --require [substring to require in result attribute] \n\
    --titles (adds a tab character and appends the title of the page a link goes to) \n\
    --URL_Format [Full / Short] \n\
    --std_filters (adds a set of common internal links to non-article pages to the exclusion list) \n\
    --other_target [tag,attribute] \n\
    --save_image [subfolder]", file=stderr)


# Take settings out of argv and put them into a Settings object
def set_settings(argv, settings):
    if len(argv) < 2:
        print_options("Expected at least one option")
        exit(1)
    try:
        options_and_vals, otherargs = getopt.getopt(argv[1:], "s:o:i:d:e:", ["URL_Format=", "std_filters", "titles", "other_target=", "require=", "save_image="])
    except getopt.GetoptError:
        print_options("Invalid option passed.")
        exit(1)

    for i in options_and_vals:
        if i[0] == "-i":
            settings.set_input_url(i[1])
        elif i[0] == "-o":
            settings.set_output_file(i[1])
        elif i[0] == "-s":
            settings.set_socket_num(i[1])
        elif i[0] == "-d":
            settings.set_delimiter(i[1])
        elif i[0] == "-e":
            settings.add_exclusion(i[1])
        elif i[0] == "--titles":
            settings.set_titles(True)
        elif i[0] == "--std_filters":  # Why did I do it like this instead of putting it in the actual class :)
            settings.add_exclusion("wiki/Category:")
            settings.add_exclusion("wiki/Help:")
            settings.add_exclusion("wiki/Template")
            settings.add_exclusion("wiki/Wikipedia:")
        elif i[0] == "--require":
            settings.add_requirement(i[1])
        elif i[0] == "--URL_Format":
            settings.set_url_format(i[1])
        elif i[0] == "--other_target":
            settings.set_target(i[1])
        elif i[0] == "--save_image":
            settings.set_save_location(i[1])
    if len(otherargs) > 0:
        print("[!] Warning:\tIgnoring the following args:", file=stderr)
        for i in otherargs:
            print("\t" + i, file=stderr)


# Validate links as internal
def valid_link(attribute_value):
    if "/wiki/" != str(attribute_value)[:6]:
        return False
    else:
        return True


# Return a long string of all the links
def get_links(url, settings):
    returner = ""
    response = requests.get(url=url)
    data = response.text
    BSObject = BeautifulSoup(data, "html.parser")
    body = BSObject.find("div", {"id": "content"})
    all_links = body.find_all(settings.target[0])
    for i in all_links:
        attr_val = i.get(settings.target[1])
        if (valid_link(attr_val) and len(str(i.get_text())) > 0) or settings.target != ['a', "href"]:
            add_link = True
            if attr_val is None:
                add_link = False
            for j in settings.exclusions:
                if add_link and j in attr_val:
                    add_link = False
                    break
            for j in settings.requirements:
                if add_link and j not in attr_val:
                    add_link = False
                    break
            if add_link:
                if settings.save_image and settings.target == ["img", "src"]:
                    save_image_to_file(settings, attr_val)
                if settings.url_format == "Full" and attr_val[:2] != "//":
                    returner += "https://en.wikipedia.org"
                try:
                    returner += attr_val
                except TypeError:  # This should be caught by checking attr_val is None.
                    print("[!] Warning: Fetched invalid data from attribute.", file=stderr)
                if settings.titles:
                    returner += ("\n\t" + i.get_text())
                returner += settings.delimiter
    return returner


# Process input/output from the commandline parameters
def cl_io(settings):
    output = open(settings.output_file, 'w')
    links = get_links(settings.input_url, settings)
    output.write(links)


def save_image_to_file(settings, src):
    if src[:2] == "//":
        src = src[2:]
    if src[len(src) - 4] != ".":  # Avoid trying to save non-directly linked images
        # print("Skipping " + src, file=stderr)
        return
    if src[:5] != "http":
        src = "https://" + src
    file_name = settings.save_image
    pos = src.rfind("/")  # Should capture position of last /
    file_name += src[pos:]  # Appends the file name from wikipedia
    print("Saving image to " + file_name, file=stderr)
    image_file = open(file_name, 'wb')  # Create the file
    response = requests.get(url=src)  # Get the image
    image_file.write(response.content)  # Print to file
    image_file.close()  # Done with file


# Process continuous input/output from HTTP requests.
def flaskified_sockets(settings):
    app = flask.Flask(__name__)

    @app.route("/saveimgs/<path:pagelink>", methods=["POST"])
    def defaultpost(pagelink):
        try:
            if len(settings.save_image) == 0:
                return "Path not supplied to save image locations."
        except TypeError:
            return "Path not supplied to save image locations."
        current_settings = settings
        current_settings.set_target("img,src")
        print(current_settings)
        response = get_links(pagelink, current_settings)
        return response

    @app.route("/get/<path:pagelink>", methods=["GET"])  # Handle get requests
    def index(pagelink):
        print(settings)
        print("New connection", file=stderr)
        print("Request:")
        print(flask.request)
        return get_links(pagelink, settings)

    app.run(port=settings.socket_num)


# Process continuous input/output from a socket connection. This was removed in favor of HTTP requests
def socketings(settings):
    s = socket.socket()
    try:
        s.bind(('localhost', int(settings.socket_num)))
    except OSError:
        print("[!] Unable to bind on that port.\nExiting...", file=stderr)
        exit(1)
    s.listen(1)
    print("\nNow listening on port ", settings.socket_num, file=stderr)
    while 1:
        connection, address = s.accept()
        print("connected", address, file=stderr)
        req = connection.recv(1024).decode()  # what to do about size limit...
        if len(req) > 100:
            connection.send("Length of request is too long".encode())
            connection.close()
        else:
            print("Fetching URL " + str(req), file=stderr)
            links = get_links(req, settings)
            connection.send(links.encode())
            connection.close()


# Set & validate settings. Run appropriate I/O mode function
def main(argv):
    settings = Settings()
    set_settings(argv, settings)
    if not settings.validate():
        exit(1)
    # print(settings, file=stderr) # Don't really need this outside of debugging. Could add as option maybe
    if settings.socket_num == 0:
        cl_io(settings)
    else:
        flaskified_sockets(settings)


if __name__ == "__main__":
    main(argv)

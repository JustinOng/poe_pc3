import configparser
import argparse
import shlex
import re
import time
import traceback
import win32gui
import win32api
import win32con
from pathofexiletrade import Trade

def display(text):
    g_hwnd = win32gui.FindWindow(None, "Path of Exile")
    print(text)

    if not g_hwnd:
        print("Cannot locate window with \"Path of Exile\"!")
        return
    
    win32api.PostMessage(g_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)

    time.sleep(0.1)
    
    for c in text:
        win32api.PostMessage(g_hwnd, win32con.WM_CHAR, ord(c), 0)
    
    win32api.PostMessage(g_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

config = configparser.ConfigParser()
config.read("config.ini")

market = Trade()

pc_parser = argparse.ArgumentParser(usage=argparse.SUPPRESS)
pc_parser.add_argument("--base", nargs="?", const=None)
pc_parser.add_argument("--corrupted", help="'any', 'yes', or 'no'", nargs="?", const="yes")
pc_parser.add_argument("--quality", nargs="?", const=None)
pc_parser.add_argument("--links", nargs="?", const=None)
pc_parser.add_argument("name", nargs="?", default="", help="name of item")

line_regex = re.compile(r"\[INFO Client [0-9]+\] (.*?): (.*)")
range_regex = re.compile(r"(\d*)\-(\d*)")

log_file_handler = open(config["CONFIG"]["log_path"], "r", encoding="latin-1")
#read and "dump" all the contents so readline() will only get new lines
log_file_handler.read()

while True:
    try:
        line = log_file_handler.readline()
        
        if not line:
            time.sleep(0.1)
            continue
        
        line = line.strip()
        match = re.findall(line_regex, line)

        if not match:
            continue
        
        match = match[0]
        if not match[0].startswith("&"):
            continue
        
        simple_args = match[1].split(" ")

        # do a simple split to test for the first word being pc as shlex.split will choke on unclosed '
        if len(simple_args) == 0:# or simple_args[0] not in POSSIBLE_MODULES:
            continue
        
        # replace ' before parsing because item names can contain unclosed '
        args = shlex.split(match[1].replace("'", "&QUOTE"))
        args = [i.replace("&QUOTE", "'") for i in args]

        if not args[0] == "pc":
            continue
        
        args = args[1:]
        options, unknown = pc_parser.parse_known_args(args)
        options = vars(options)

        # join unmatched parameters so that we can issue commands like "&pc searing touch"
        if unknown:
            options["name"] = options["name"] + " " + " ".join(unknown)
        
        #validate yes/no/any options
        ARGUMENTS_YES_NO_ANY = ["corrupted"]
        
        for argument in ARGUMENTS_YES_NO_ANY:
            if options[argument] not in [0, None, "yes", "no", "any"]:
                display("&Unknown parameter for --"+argument+": "+options[argument])
                continue
        
        result = market.query("Delve", { "name": options["name"] })

        if "error" in result:
            display(f'&Error: {result["error"]["message"]}')
            continue
        
        if "result" in result:
            display(f'&{result["result"]}')
    except KeyboardInterrupt:
        break
    except:
        print(traceback.format_exc())


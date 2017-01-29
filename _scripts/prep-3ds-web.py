#!/usr/bin/env python

import csv
import getopt
import math
import operator
import os
import re
import sys

def roman_to_int(roman_str):
    roman_dict = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9}
    return roman_dict[roman_str];

def get_simple_filename(filename):
    filename_components = os.path.splitext(filename)
    filename = filename_components[0]
    ext = filename_components[1]

    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]

    token_list = []
    for word in filename.split():
        if word == "-":
            continue
        elif word in romans:
            token_list.append(str(roman_to_int(word)))
        elif re.match(r"^[a-zA-Z0-9_\-']+$", word): 
            token_list.append(re.sub(r"'", "", word.lower()))

    region = get_region(filename).lower()

    return "-".join(token for token in token_list) + "-" + region + ext

def get_title(filename):
    filename_components = os.path.splitext(filename)
    filename = filename_components[0]

    region = get_region(filename)
    filename = filename.replace(" - ", ": ", 1).replace(" (" + region + ")", "")

    return filename

def get_region(filename):
    return re.findall('\((.*?)\)',filename)[0]

def convert_size(size_bytes):
    if (size_bytes == 0):
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])

def bytes_to_blocks(size_bytes):
    if (size_bytes == 0):
        return 0

    return size_bytes / (128 * 1024)

def print_help():
    script_name = os.path.basename(__file__)
    # TODO: Generate proper help message
    print(os.path.basename(__file__) + " args incorrect")

def validate_dirs(dir_list):
    for directory in dir_list:
        if not os.path.exists(directory):
            print("Directory " + directory + " does not exist.")
            return False
    return True

def create_csv(src_dir, dest_dir, out_filename):
    if dest_dir is None:
        sys.exit("No destination directory specified.")

    if out_filename is None:
        sys.exit("No output file specified.")

    if validate_dirs([src_dir, dest_dir]):
        rows = []
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                abs_path = os.path.join(root, file)

                title = get_title(file)
                simple_filename = get_simple_filename(file)
                size_bytes = convert_size(os.path.getsize(abs_path))
                size_blocks = str(bytes_to_blocks(os.path.getsize(abs_path))) + " Blocks"
                
                rows.append([title, simple_filename, size_bytes, size_blocks])

        rows.sort(key=lambda x : x[1])

        with open(os.path.join(dest_dir, out_filename), "wb") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["title", "filename", "size_bytes", "size_blocks"])

            for row in rows:
                csv_writer.writerow(row)

        print("Created csv at " + os.path.join(dest_dir, out_filename))


def create_symlinks(src_dir, dest_dir):
    if dest_dir is None:
        sys.exit("No destination directory specified.")

    if validate_dirs([src_dir, dest_dir]):
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                simple_filename = get_simple_filename(file)
                abs_path = os.path.join(root, file)
                sym_path = os.path.join(dest_dir, simple_filename)

                if os.path.exists(sym_path):
                    os.remove(sym_path)
                os.symlink(abs_path, sym_path)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:s:d:o:", ["help", "cmd=", "src-dir=", "dest-dir=", "output-file="])
    except getopt.GetoptError:
        print_help()
        sys.exit(1)

    cmd = None
    src_dir = os.getcwd()
    dest_dir = None
    out_filename = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
        elif opt in ("-c", "--cmd"):
            cmd = arg
        elif opt in ("-s", "--src-dir"):
            src_dir = os.path.abspath(arg)
        elif opt in ("-d", "--dest-dir"):
            dest_dir = os.path.abspath(arg)
        elif opt in ("-o", "--output-file"):
            out_filename = os.path.abspath(arg)

    if cmd in ("ln", "link"):
        create_symlinks(src_dir, dest_dir)
    elif cmd == "csv":
        if dest_dir is None:
            dest_dir = os.getcwd()
        if out_filename is None:
            out_filename = "games.csv"
        create_csv(src_dir, dest_dir, out_filename)
    else:
        print("Unrecognized command")


if __name__ == "__main__":
    main(sys.argv[1:])

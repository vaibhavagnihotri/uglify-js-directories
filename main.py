# -*- coding: utf-8 -*-
import os
import sys

uuid = sys.argv[1]
mangle_cache = f"src/dj/static/deps/{uuid}/mangle.map.json"
mangle_regex = r"/^_.*\$/g;"
mangle_reserved = r"[F2,F3,F4,F5,F6,F7,F8,F9,A2,A3,A4,A5,A6,A7,A8,A9]"


def help_message():
    print("uglifyjs.py <uuid> <path> [--override-input] [-o <output>] [--mangle]")
    sys.exit(2)


def compress_js(input_file_path, output_file_path, mangle):
    if mangle:
        cmd = [
            " ./node_modules/.bin/uglifyjs %r -o %r "
            " -c -m toplevel,eval,reserved=%r "
            " --mangle-props regex=%r --name-cache %r "
            % (
                input_file_path,
                output_file_path,
                mangle_reserved,
                mangle_regex,
                mangle_cache,
            )
        ][0]
    else:
        cmd = "./node_modules/.bin/uglifyjs %r -o %r -c" % (
            input_file_path,
            output_file_path,
        )
    os.system(cmd)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        help_message()
    if "--override-input" in sys.argv and ("-o" in sys.argv or "--output" in sys.argv):
        print("Output path not required when overriding input")
        help_message()
    if "--output" in sys.argv and sys.argv[3] != "--output":
        help_message()
    if "-o" in sys.argv and sys.argv[3] != "-o":
        help_message()

    override = False
    output_path = None

    # Second arg is input path
    input_path = sys.argv[2]

    # Rest of the args
    uglify_args = sys.argv[3:]

    # Next arg is either --override-input or --output or -o
    if sys.argv[3] == "--override-input":
        override = True
        uglify_args = sys.argv[4:]

    # if output arg, next arg after output is output path
    if sys.argv[3] == "--output" or sys.argv[3] == "-o":
        output_path = sys.argv[4]
        if output_path.endswith("/"):
            output_path = output_path[:-1]
        uglify_args = sys.argv[5:]

    # is mangle
    mangle = "--mangle" in uglify_args

    if input_path.endswith("/"):
        input_path = input_path[:-1]

    # compress js in a directory
    if os.path.isdir(input_path):
        if not output_path:
            output_path = input_path + "-uglified"
            os.makedirs(output_path, exist_ok=False)

        for dirpath, dirs, files in os.walk(input_path):
            for file_name in files:
                file_path = os.path.join(dirpath, file_name)
                if os.path.isdir(output_path):
                    output_file_path = os.path.join(
                        output_path, os.path.relpath(dirpath, input_path), file_name
                    )
                else:
                    print("Output Path %s not a directory" % output_path)
                    sys.exit(2)

                if file_path.endswith(".js"):
                    compress_js(
                        file_path, file_path if override else output_file_path, mangle
                    )
        if override:
            os.removedirs(output_path)

    # compress specific js file
    elif input_path.endswith(".js"):
        if not output_path:
            output_path = os.path.dirname(input_path)
        if output_path == "":
            output_path = "."
        if os.path.isdir(output_path):
            file_name = input_path.rsplit("/", 1)[-1].rsplit(".", 1)[0] + "-uglified.js"
            output_file_path = os.path.join(output_path, file_name)
        else:
            output_file_path = output_path

        compress_js(input_path, input_path if override else output_file_path, mangle)


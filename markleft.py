# MARKLEFT v1.3.0 CLI Demo
# Fully compatible with v1.1.0 and v1.2.0 files
# Changes: Makes text editor based on the command line
import sys

HEADER_START = "|====================|"
HEADER_END   = "|--------------------|"
EOF_MARKER   = "[eof]"
FOOTER_MARKER = "[footer]"

INNER_WIDTH = 20
FULL_WIDTH = 22

# =========================
# HELPERS
# =========================

def make_line(text):
    if len(text) > INNER_WIDTH:
        parts = []

        while len(text) > INNER_WIDTH:
            part = text[:INNER_WIDTH - 1] + ">"
            parts.append(part)
            text = text[INNER_WIDTH - 1:]

        parts.append(text)

        return ["|" + p.ljust(INNER_WIDTH) + "|" for p in parts]

    return ["|" + text.ljust(INNER_WIDTH) + "|"]


def validate_line(line):
    if len(line) != FULL_WIDTH:
        return False

    if line[0] != "|" or line[-1] != "|":
        return False

    try:
        line.encode("ascii")
    except UnicodeEncodeError:
        return False

    return True

# =========================
# VALIDATE / PARSE
# =========================

def validate_markleft(filename):
    try:
        with open(filename, "rb") as f:
            raw = f.read()

    except FileNotFoundError:
        return False, "File not found"

    try:
        text = raw.decode("ascii")

    except UnicodeDecodeError:
        return False, "File is not ASCII"

    lines = text.splitlines()

    if len(lines) < 5:
        return False, "File too short"

    if lines[-1] != EOF_MARKER:
        return False, "Missing [eof]"

    if lines[-2].strip() != "":
        return False, "Missing blank line before [eof]"

    if lines[0] != HEADER_START:
        return False, "Missing header start"

    try:
        header_end = lines.index(HEADER_END)

    except ValueError:
        return False, "Missing header end"

    if header_end < 3:
        return False, "Header must include TITLE and AUTHOR"

    # Validate TITLE / AUTHOR lines first

    if not validate_line(lines[1]):
        return False, "Invalid TITLE line"

    if not validate_line(lines[2]):
        return False, "Invalid AUTHOR line"

    header_title = lines[1][1:-1].rstrip()
    header_author = lines[2][1:-1].rstrip()

    if not header_title:
        return False, "Missing TITLE"

    if not header_author.startswith("AUTHOR="):
        return False, "Missing AUTHOR line"

    in_footer = False

    for line in lines[1:-2]:

        if line == HEADER_END:
            continue

        if line.strip() == "":
            continue

        if line == FOOTER_MARKER:
            in_footer = True
            continue

        if not in_footer:

            if not validate_line(line):
                return False, f"Invalid line: {line}"

            content = line[1:-1]

            if content.rstrip().endswith(">") and content[-1] != ">":
                return False, (
                    f"Continuation '>' must be last character: {line}"
                )

        else:
            if not (line.startswith("[") and line.endswith("]")):
                return False, f"Invalid footer line: {line}"

    return True, "Valid MARKLEFT file"

# =========================
# READ
# =========================

def read_markleft(filename):
    valid, message = validate_markleft(filename)

    if not valid:
        print("ERROR:", message)
        return

    with open(filename, "r", encoding="ascii") as f:
        lines = f.read().splitlines()

    print("\n===== HEADER =====")

    in_header = False
    in_footer = False
    after_header = False
    body_buffer = ""

    for line in lines:

        if line == HEADER_START:
            in_header = True
            continue

        if line == HEADER_END:
            in_header = False
            after_header = True

            print("\n===== BODY =====")
            continue

        if line == FOOTER_MARKER:
            in_footer = True

            if body_buffer:
                print(body_buffer)
                body_buffer = ""

            print("\n===== FOOTER =====")
            continue

        if line == "":
            continue

        if line == EOF_MARKER:

            if body_buffer:
                print(body_buffer)

            break

        if in_footer:

            if line.startswith("[") and line.endswith("]"):
                print(line[1:-1])

            else:
                print(line)

            continue

        content = line[1:-1].rstrip()

        if in_header:

            if content.startswith("AUTHOR="):
                print("AUTHOR:", content[len("AUTHOR="):])

            else:
                print(content)

        elif after_header and not in_footer:

            if content.startswith("#"):
                continue

            if content.endswith(">"):
                body_buffer += content[:-1]

            else:
                body_buffer += content
                print(body_buffer)
                body_buffer = ""

# =========================
# EDITOR
# =========================

def editor_loop(title, author, body_lines):

    while True:

        print(f"\n[{title}] ({author})")

        cmd = input("> ").strip()

        if cmd == "":
            continue

        parts = cmd.split(maxsplit=2)
        command = parts[0].lower()

        # =========================
        # HELP
        # =========================

        if command == "help":

            print("""
commands:
help                    - show this list
list/ls                 - show current body
+/add [line] (pos)      - add line to bottom or insert at pos
-/del [pos]             - delete line
edit [pos] [text]       - replace line
title [title]           - set title
author [author]         - set author
save/s                  - save file
sq                      - save + quit
quit/q                  - quit without saving
""")

        # =========================
        # LIST
        # =========================

        elif command in ("list", "ls"):

            print("\n====================")
            print("TITLE :", title)
            print("AUTHOR:", author)
            print("====================")

            if body_lines:

                for i, line in enumerate(body_lines, 1):
                    print(f"{i:03}: {line}")

            else:
                print("(empty body)")

        # =========================
        # ADD
        # =========================

        elif command in ("+", "add"):

            if len(parts) < 2:
                print("Usage: add <text> [pos]")
                continue

            rest = cmd[len(parts[0]):].strip()

            pos = None

            split_rest = rest.rsplit(" ", 1)

            if len(split_rest) == 2 and split_rest[1].isdigit():
                text = split_rest[0]
                pos = int(split_rest[1])

            else:
                text = rest

            if pos is None:
                body_lines.append(text)

            else:
                pos -= 1

                if pos < 0 or pos > len(body_lines):
                    print("Invalid position")
                    continue

                body_lines.insert(pos, text)

        # =========================
        # DELETE
        # =========================

        elif command in ("-", "del"):

            if len(parts) < 2:
                print("Usage: del <pos>")
                continue

            try:
                pos = int(parts[1]) - 1

                if pos < 0 or pos >= len(body_lines):
                    print("Invalid position")
                    continue

                del body_lines[pos]

            except ValueError:
                print("Invalid number")

        # =========================
        # EDIT
        # =========================

        elif command == "edit":

            if len(parts) < 3:
                print("Usage: edit <pos> <text>")
                continue

            try:
                pos = int(parts[1]) - 1

                if pos < 0 or pos >= len(body_lines):
                    print("Invalid position")
                    continue

                body_lines[pos] = parts[2]

            except ValueError:
                print("Invalid number")

        # =========================
        # TITLE
        # =========================

        elif command == "title":

            new_title = cmd[len("title"):].strip()

            if not new_title:
                print("Missing title")
                continue

            if len(new_title) > INNER_WIDTH:
                print("Title too long")
                continue

            title = new_title

        # =========================
        # AUTHOR
        # =========================

        elif command == "author":

            new_author = cmd[len("author"):].strip()

            if not new_author:
                print("Missing author")
                continue

            if len(new_author) > INNER_WIDTH - 7:
                print("Author too long")
                continue

            author = new_author

        # =========================
        # SAVE
        # =========================

        elif command in ("save", "s"):
            return title, author, body_lines, False

        elif command == "sq":
            return title, author, body_lines, True

        # =========================
        # QUIT
        # =========================

        elif command in ("quit", "q"):
            return None

        else:
            print("Unknown command")

# =========================
# WRITE / EDIT
# =========================

def write_markleft(filename=None):

    existing_title = ""
    existing_author = ""
    existing_body = []

    # =========================
    # LOAD EXISTING FILE
    # =========================

    if filename:

        try:
            valid, message = validate_markleft(filename)

            if valid:

                with open(filename, "r", encoding="ascii") as f:
                    lines = f.read().splitlines()

                in_header = False
                after_header = False
                in_footer = False

                body_buffer = ""

                for line in lines:

                    if line == HEADER_START:
                        in_header = True
                        continue

                    if line == HEADER_END:
                        in_header = False
                        after_header = True
                        continue

                    if line == FOOTER_MARKER:
                        in_footer = True
                        continue

                    if line == EOF_MARKER:
                        break

                    if line.strip() == "":
                        continue

                    if in_header:

                        content = line[1:-1].rstrip()

                        if content.startswith("AUTHOR="):
                            existing_author = (
                                content[len("AUTHOR="):]
                            )

                        else:
                            existing_title = content

                    elif after_header and not in_footer:

                        content = line[1:-1].rstrip()

                        if content.endswith(">"):
                            body_buffer += content[:-1]

                        else:
                            body_buffer += content
                            existing_body.append(body_buffer)
                            body_buffer = ""

        except FileNotFoundError:
            pass

    # =========================
    # FILE NAME
    # =========================

    if not filename:

        filename = input("Output file name: ").strip()

        if not filename.endswith(".h39"):
            filename += ".h39"

    # Defaults

    if not existing_title:
        existing_title = "UNTITLED"

    if not existing_author:
        existing_author = "unknown"

    # =========================
    # EDITOR
    # =========================

    result = editor_loop(
        existing_title,
        existing_author,
        existing_body
    )

    if result is None:
        print("Quit without saving.")
        return

    title, author, body_content, should_quit = result

    author_line = "AUTHOR=" + author

    # =========================
    # WRITE FILE
    # =========================

    with open(filename, "w", encoding="ascii", newline="\n") as f:

        f.write(HEADER_START + "\n")

        for line in [title, author_line]:
            f.write(make_line(line)[0] + "\n")

        f.write(HEADER_END + "\n")

        for line in body_content:

            split_lines = make_line(line)

            for split in split_lines:
                f.write(split + "\n")

        f.write("\n")
        f.write(FOOTER_MARKER + "\n")
        f.write("[mlfver=1.3.0]\n")
        f.write("\n")
        f.write(EOF_MARKER + "\n")

    print("\nFile written:", filename)

    if should_quit:
        return

# =========================
# CLI
# =========================

def cli():

    args = sys.argv[1:]

    if not args:
        interactive_menu()
        return

    if args[0] in ("-p", "-v"):

        if len(args) < 2:
            print("Usage: python Markleft.py -p <file>")
            return

        read_markleft(args[1])
        return

    if args[0] == "-w":

        if len(args) >= 2:
            write_markleft(args[1])

        else:
            write_markleft()

        return

    # default = read

    read_markleft(args[0])

# =========================
# INTERACTIVE MENU
# =========================

def interactive_menu():

    while True:

        print("\n==== MARKLEFT v1.2 TOOL ====")
        print("1. Validate / Parse")
        print("2. Read")
        print("3. Write / Edit")
        print("4. Exit")

        choice = input("\nSelect option: ")

        if choice == "1":

            path = input("File path: ")

            valid, message = validate_markleft(path)

            print("\nRESULT:", message)

        elif choice == "2":

            path = input("File path: ")

            read_markleft(path)

        elif choice == "3":

            path = input(
                "File path (or leave blank for new): "
            ).strip()

            write_markleft(path if path else None)

        elif choice == "4":

            print("Goodbye.")
            break

        else:
            print("Invalid option")

# =========================
# ENTRY
# =========================

if __name__ == "__main__":
    cli()
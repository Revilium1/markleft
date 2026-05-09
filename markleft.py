# MARKLEFT v1.2.0 CLI Demo
# Fully compatible with v1.1.0 files
# Adds QoL: auto continuation, padding, and CLI++ with MSBASIC-style editing

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
        # Auto-split for continuation
        parts = []
        while len(text) > INNER_WIDTH:
            part = text[:INNER_WIDTH-1] + ">"
            parts.append(part)
            text = text[INNER_WIDTH-1:]
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

    header_title = lines[1][1:-1].rstrip()
    header_author = lines[2][1:-1].rstrip()
    if not header_title or not header_author.startswith("AUTHOR="):
        return False, "Header must include TITLE and AUTHOR lines"

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
                return False, f"Continuation '>' must be last character: {line}"
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
# WRITE / EDIT
# =========================

def write_markleft(filename=None):
    if not filename:
        filename = input("Output file name: ")
        if not filename.endswith(".h39"):
            filename += ".h39"

    print("\nEnter TITLE for header:")
    title = input("TITLE> ").strip()
    if len(title) > INNER_WIDTH:
        print("Title too long")
        return

    print("Enter AUTHOR for header:")
    author = input("AUTHOR> ").strip()
    if len(author) > INNER_WIDTH - 7:
        print("AUTHOR value too long")
        return
    author = "AUTHOR=" + author

    header_lines = [title, author]

    print("\nEnter body lines (20 char max). Leave blank to finish.\n")
    body_lines = []
    while True:
        line = input("BODY> ").strip()
        if line == "":
            break
        # Auto-split if longer than INNER_WIDTH
        split_lines = make_line(line)
        body_lines.extend([l[1:-1] for l in split_lines])  # store without pipes

    with open(filename, "w", encoding="ascii", newline="\n") as f:
        f.write(HEADER_START + "\n")
        for line in header_lines:
            f.write(make_line(line)[0] + "\n")
        f.write(HEADER_END + "\n")
        for line in body_lines:
            f.write(make_line(line)[0] + "\n")
        f.write("\n")
        f.write(FOOTER_MARKER + "\n")
        f.write("[mlfver=1.2.0]\n")
        f.write("\n")
        f.write(EOF_MARKER + "\n")

    print("\nFile written:", filename)

# =========================
# CLI
# =========================

def cli():
    args = sys.argv[1:]
    if not args:
        # No args → open interactive menu
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

    # default: assume first arg is filename to read
    read_markleft(args[0])

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
            path = input("File path (or leave blank for new): ").strip()
            write_markleft(path if path else None)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    cli()# MARKLEFT v1.2.0 CLI Demo
# Fully compatible with v1.1.0 files
# Adds QoL: auto continuation, padding, and CLI++ with MSBASIC-style editing

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
        # Auto-split for continuation
        parts = []
        while len(text) > INNER_WIDTH:
            part = text[:INNER_WIDTH-1] + ">"
            parts.append(part)
            text = text[INNER_WIDTH-1:]
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

    header_title = lines[1][1:-1].rstrip()
    header_author = lines[2][1:-1].rstrip()
    if not header_title or not header_author.startswith("AUTHOR="):
        return False, "Header must include TITLE and AUTHOR lines"

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
                return False, f"Continuation '>' must be last character: {line}"
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
# WRITE / EDIT
# =========================

def write_markleft(filename=None):
    if not filename:
        filename = input("Output file name: ")

    print("\nEnter TITLE for header:")
    title = input("TITLE> ").strip()
    if len(title) > INNER_WIDTH:
        print("Title too long")
        return

    print("Enter AUTHOR for header:")
    author = input("AUTHOR> ").strip()
    if len(author) > INNER_WIDTH - 7:
        print("AUTHOR value too long")
        return
    author = "AUTHOR=" + author

    header_lines = [title, author]

    print("\nEnter body lines (20 char max). Leave blank to finish.\n")
    body_lines = []
    while True:
        line = input("BODY> ").strip()
        if line == "":
            break
        # Auto-split if longer than INNER_WIDTH
        split_lines = make_line(line)
        body_lines.extend([l[1:-1] for l in split_lines])  # store without pipes

    with open(filename, "w", encoding="ascii", newline="\n") as f:
        f.write(HEADER_START + "\n")
        for line in header_lines:
            f.write(make_line(line)[0] + "\n")
        f.write(HEADER_END + "\n")
        for line in body_lines:
            f.write(make_line(line)[0] + "\n")
        f.write("\n")
        f.write(FOOTER_MARKER + "\n")
        f.write("[mlfver=1.2.0]\n")
        f.write(EOF_MARKER + "\n")

    print("\nFile written:", filename)

# =========================
# CLI
# =========================

def cli():
    args = sys.argv[1:]
    if not args:
        # No args → open interactive menu
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

    # default: assume first arg is filename to read
    read_markleft(args[0])

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
            path = input("File path (or leave blank for new): ").strip()
            write_markleft(path if path else None)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    cli()
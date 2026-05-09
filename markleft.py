# MARKLEFT v1
# Simple CLI demo

HEADER_START = "|====================|"
HEADER_END   = "|--------------------|"
EOF_MARKER   = "[eof]"

INNER_WIDTH = 20
FULL_WIDTH = 22


# =========================
# HELPERS
# =========================

def make_line(text):

    if len(text) > INNER_WIDTH:
        raise ValueError("Text too long (max 20 chars)")

    return "|" + text.ljust(INNER_WIDTH) + "|"


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
# VALIDATE
# =========================

def validate_markleft(filename):

    try:
        with open(filename, "rb") as f:
            raw = f.read()

    except FileNotFoundError:
        return False, "File not found"

    # ASCII check
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        return False, "File is not ASCII"

    lines = text.splitlines()

    if len(lines) < 4:
        return False, "File too short"

    # EOF rules
    if lines[-1] != EOF_MARKER:
        return False, "Missing [eof]"

    if lines[-2] != "":
        return False, "Missing blank line before [eof]"

    # Header start
    if lines[0] != HEADER_START:
        return False, "Missing header start"

    # Header end
    try:
        header_end = lines.index(HEADER_END)
    except ValueError:
        return False, "Missing header end"

    # At least one header line
    if header_end < 2:
        return False, "Header empty"

    # Validate all normal lines
    for line in lines[:-2]:

        if line == HEADER_START:
            continue

        if line == HEADER_END:
            continue

        if not validate_line(line):
            return False, f"Invalid line: {line}"

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
    after_header = False

    for line in lines:

        if line == HEADER_START:
            in_header = True
            continue

        if line == HEADER_END:
            in_header = False
            after_header = True
            print("\n===== BODY =====")
            continue

        if line == "":
            continue

        if line == EOF_MARKER:
            break

        content = line[1:-1].rstrip()

        print(content)


# =========================
# WRITE
# =========================

def write_markleft():

    filename = input("Output file name: ")

    print("\nEnter header lines.")
    print("Leave blank to finish.\n")

    header_lines = []

    while True:

        line = input("HEADER> ")

        if line == "":
            break

        if len(line) > INNER_WIDTH:
            print("Too long (20 max)")
            continue

        header_lines.append(line)

    if len(header_lines) == 0:
        print("Header required")
        return

    print("\nEnter body lines.")
    print("Leave blank to finish.\n")

    body_lines = []

    while True:

        line = input("BODY> ")

        if line == "":
            break

        if len(line) > INNER_WIDTH:
            print("Too long (20 max)")
            continue

        body_lines.append(line)

    with open(filename, "w", encoding="ascii", newline="\n") as f:

        f.write(HEADER_START + "\n")

        for line in header_lines:
            f.write(make_line(line) + "\n")

        f.write(HEADER_END + "\n")

        for line in body_lines:
            f.write(make_line(line) + "\n")

        f.write("\n")
        f.write(EOF_MARKER + "\n")

    print("\nFile written:", filename)


# =========================
# MAIN MENU
# =========================

while True:

    print("\n==== MARKLEFT TOOL ====")
    print("1. Validate")
    print("2. Read")
    print("3. Write")
    print("4. Exit")

    choice = input("\nSelect option: ")

    # VALIDATE
    if choice == "1":

        path = input("File path: ")

        valid, message = validate_markleft(path)

        print("\nRESULT:")
        print(message)

    # READ
    elif choice == "2":

        path = input("File path: ")

        read_markleft(path)

    # WRITE
    elif choice == "3":

        write_markleft()

    # EXIT
    elif choice == "4":

        print("Goodbye.")
        break

    else:
        print("Invalid option")
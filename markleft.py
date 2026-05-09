# MARKLEFT v1.1.0 CLI demo
# Supports HEADER, BODY with continuation, FOOTER, and EOF

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

    if len(lines) < 5:
        return False, "File too short"

    # EOF rules
    if lines[-1] != EOF_MARKER:
        return False, "Missing [eof]"
    if lines[-2].strip() != "":
        return False, "Missing blank line before [eof]"

    # Header start
    if lines[0] != HEADER_START:
        return False, "Missing header start"

    # Header end
    try:
        header_end = lines.index(HEADER_END)
    except ValueError:
        return False, "Missing header end"

    # Must have TITLE and AUTHOR in header
    if header_end < 3:
        return False, "Header must include TITLE and AUTHOR"

    header_title = lines[1][1:-1].rstrip()
    header_author = lines[2][1:-1].rstrip()
    if not header_title or not header_author.startswith("AUTHOR="):
        return False, "Header must include TITLE and AUTHOR lines"

    # Validate all normal lines in header/body
    in_footer = False
    for line in lines[1:-2]:  # skip HEADER_START and final blank line + EOF
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
            # Check continuation line rule
            content = line[1:-1]
            if content.rstrip().endswith(">") and content[-1] != ">":
                return False, f"Continuation '>' must be last character: {line}"
        else:
            # Footer lines must be [mlfver=...] or ignored
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
            # Footer lines: just strip brackets if they exist
            if line.startswith("[") and line.endswith("]"):
                print(line[1:-1])
            else:
                print(line)  # any optional ignored variables
            continue

        content = line[1:-1].rstrip()  # strip pipes for header/body

        if in_header:
            if content.startswith("AUTHOR="):
                print("AUTHOR:", content[len("AUTHOR="):])
            else:
                print(content)
        elif after_header and not in_footer:
            # BODY section
            if content.startswith("#"):
                continue  # skip comments
            if content.endswith(">"):
                body_buffer += content[:-1]  # remove '>' and append
            else:
                body_buffer += content
                print(body_buffer)
                body_buffer = ""
# =========================
# WRITE
# =========================

def write_markleft():
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

    print("\nEnter body lines (20 char max). Use '>' at end for continuation. Leave blank to finish.\n")
    body_lines = []
    while True:
        line = input("BODY> ").strip()
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
        f.write(FOOTER_MARKER + "\n")
        f.write("[mlfver=1.1.0]\n")
        f.write(EOF_MARKER + "\n")

    print("\nFile written:", filename)

# =========================
# MAIN MENU
# =========================

while True:
    print("\n==== MARKLEFT v1.1.0 TOOL ====")
    print("1. Validate")
    print("2. Read")
    print("3. Write")
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
        write_markleft()

    elif choice == "4":
        print("Goodbye.")
        break

    else:
        print("Invalid option")
MARKLEFT v1.2.0 — CLI update
=======================================================

MARKLEFT is a plain-text, fixed-width file format designed for
structured notes, demos, and lightweight metadata. Version 1.2.0
introduces headers with required metadata, body continuation lines,
and a structured footer for versioning.

File Extension
--------------

.h39

File Structure
--------------

A .h39 file has three main sections:

1. Header
2. Body
3. Footer

All lines (except in the footer) are exactly 20 characters wide
inside pipes |...|. Files must be ASCII only.

Header
------

- Starts with:
  |====================|
- Ends with:
  |--------------------|

- Required lines:
  - TITLE — the title of the file
  - AUTHOR — the author (formatted as AUTHOR=yourname in file)

Example:

```
|====================|  
|MARKLEFT FULL DEMO  |  
|AUTHOR=human39      |  
|--------------------|  
```

In output, AUTHOR=human39 is displayed as AUTHOR: human39.

Body
----

- Fixed-width lines (20 characters)
- Comments start with # and are ignored in output
- Continuation lines: lines ending with > are concatenated with
  the next line(s)

Example:
```
|HELLO WORLD         |
|THIS IS MARKLEFT    |
|#COMMENT LINE       |
|CONTINUATION LINE 1>|
|CONTINUATION LINE 2>|
|CONTINUATION LINE 3 |
```
Output:
```
HELLO WORLD
THIS IS MARKLEFT
CONTINUATION LINE 1CONTINUATION LINE 2CONTINUATION LINE 3
```
Footer
------

- Begins with:
  [footer]
- Required variables:
  - [mlfver=1.2.0] — markleft version
  - [eof] — end of file marker
- A blank line must appear before [eof]

Example:
```
[footer]
[mlfver=1.2.0]
[eof]
```
Output:

mlfver=1.2.0

Rules Summary
-------------

1. All header and body lines must be exactly 20 characters wide
   inside pipes |...|.
2. Header must include TITLE and AUTHOR.
3. Body comments start with # and are ignored in read output.
4. Continuation lines end with > and are concatenated.
5. Footer starts with [footer] and must include [mlfver=1.2.0]
   and [eof].
6. ASCII only.
7. Blank line required before [eof].

CLI Usage
---------

MARKLEFT v1.2.0 comes with command-line flags and an interactive menu:

Flags:
- `-v` or `-p` — read/print a .h39 file with formatted output
  Usage: `python markleft.py -p <filename>`
- `-w` — write/create a new .h39 file interactively
  Usage: `python markleft.py -w` (prompts for filename) or 
         `python markleft.py -w <filename>`

Interactive Menu (no arguments):

==== MARKLEFT v1.2.0 TOOL ====
1. Validate / Parse
2. Read
3. Write / Edit
4. Exit

Example Full File
-----------------
```
|====================|
|MARKLEFT FULL DEMO  |
|AUTHOR=human39      |
|--------------------|
|HELLO WORLD         |
|THIS IS MARKLEFT    |
|FIXED WIDTH TEXT    |
|#COMMENT LINE       |
|CONTINUATION LINE 1>|
|CONTINUATION LINE 2>|
|CONTINUATION LINE 3 |
|ANOTHER BODY LINE   |
|FINAL BODY LINE     |

[footer]
[mlfver=1.2.0]
[eof]
```
Output
------
```
===== HEADER =====
MARKLEFT FULL DEMO
AUTHOR: human39

===== BODY =====
HELLO WORLD
THIS IS MARKLEFT
FIXED WIDTH TEXT
CONTINUATION LINE 1CONTINUATION LINE 2CONTINUATION LINE 3
ANOTHER BODY LINE
FINAL BODY LINE

===== FOOTER =====
mlfver=1.2.0
```
Notes
-----

- .h39 files are designed for readability and lightweight structured data.
- Header metadata and versioning make it easy to manage demos or structured notes.
- Comments and continuation lines allow for flexible formatting in the body.
- Fully ASCII-compatible and portable across platforms.

Version: 1.2.0 — The Wow I'm Getting Somewhere Update
Author: human39
# Pynosaur Tools

A complete catalog of the Pynosaur ecosystem. Each tool is built in pure Python using only the standard library.

[Back to Main](../) · [Creating a Program](/creating-a-program/)

---

### [pget](/pget/) — Package Manager
Install, update, and manage Pynosaur tools from the command line. The backbone of the ecosystem.
- **Equivalent:** `apt` / `brew`
- **Install:** `git clone https://github.com/pynosaur/pget.git && cd pget && bazel build //:pget_bin`

---

### [see](/see/) — File Viewer
View files with line numbers, slicing, and syntax highlighting. A modern take on `cat`.
- **Equivalent:** `cat`
- **Install:** `pget install see`

---

### [purl](/purl/) — URL Transfer Tool
Make HTTP requests, download files, and inspect headers — all from pure Python.
- **Equivalent:** `curl`
- **Install:** `pget install purl`

---

### [yday](/yday/) — Day of Year
Display the current day of the year (1–366). Simple, fast, useful.
- **Equivalent:** `date +%j`
- **Install:** `pget install yday`

---

### [doc](/doc/) — Documentation Viewer
Browse and read documentation for Pynosaur tools from the terminal.
- **Equivalent:** `man`
- **Install:** `pget install doc`

---

### [sock](/sock/) — Socket Communication
Send and receive messages and files over TCP sockets. Supports interactive chat, one-shot messages, and file transfer.
- **Equivalent:** `netcat` / `telnet`
- **Install:** `pget install sock`

---

### [path](/path/) — File & Directory Finder
Find files and directories with glob patterns, depth control (layers), size filtering, and tree view. Powered by `pathlib`.
- **Equivalent:** `find`
- **Install:** `pget install path`

---

### [pyle](/pyle/) — Disk Usage Explorer
Interactive disk usage explorer with a curses TUI. Browse directories sorted by size with color-coded bars and vim-style navigation.
- **Equivalent:** `ncdu` / `du`
- **Install:** `pget install pyle`

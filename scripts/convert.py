import requests
import re
import json
import os

URL = "https://imtheo.lol/Offsets/Offsets.hpp"


def download(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.text


OFFSET_REGEX = re.compile(
    r"constexpr\s+[a-zA-Z0-9_:<>]+\s+([a-zA-Z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+)"
)

NAMESPACE_REGEX = re.compile(r"namespace\s+([a-zA-Z0-9_]+)")

VERSION_REGEX = re.compile(
    r'ClientVersion\s*=\s*"([^"]+)"'
)


def parse_hpp(text):

    result = {}
    namespace_stack = []

    # capturar versão
    version_match = VERSION_REGEX.search(text)
    if version_match:
        result["ClientVersion"] = version_match.group(1)

    for line in text.splitlines():

        line = line.strip()

        # detectar namespace
        ns = NAMESPACE_REGEX.search(line)
        if ns:
            namespace_stack.append(ns.group(1))
            continue

        # fechar namespace
        if line.startswith("}"):
            if namespace_stack:
                namespace_stack.pop()
            continue

        # detectar offsets
        match = OFFSET_REGEX.search(line)
        if match:

            name = match.group(1)
            value = match.group(2)

            # remover apenas namespace raiz
            clean_stack = [
                ns for ns in namespace_stack
                if ns != "Offsets"
            ]

            key = clean_stack[-1] if clean_stack else "global"

            if key not in result:
                result[key] = {}

            result[key][name] = value

    return result


def main():

    print("Downloading offsets...")

    text = download(URL)

    final = parse_hpp(text)

    os.makedirs("output", exist_ok=True)

    with open("output/offsets_single.json", "w") as f:
        json.dump(final, f, indent=4)

    print("Offsets updated successfully.")


if __name__ == "__main__":
    main()

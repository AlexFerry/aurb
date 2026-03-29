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


def parse_hpp(text):

    result = {}
    namespace_stack = []

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

        # detectar offset
        match = OFFSET_REGEX.search(line)
        if match:

            name = match.group(1)
            value = match.group(2)

            # limpar namespaces indesejados
            clean_stack = [
                ns for ns in namespace_stack
                if ns not in ("cs2_dumper", "offsets")
            ]

            key = "_".join(clean_stack) if clean_stack else "global"

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

    print("Offsets single updated.")


if __name__ == "__main__":
    main()

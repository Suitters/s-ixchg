"""Python s-ixchg loader."""

import os

# import json
from pathlib import Path

from jsonc_parser.parser import JsoncParser
from model import *


def load(pss_spec: str) -> Library:
    """load loads a s-ixchg library along with builder defs and user module transactions defs.

    :param pss_spec: path to s-ixchg library
    :type pss_spec: str
    """
    # Load the base
    lib_path = Path(os.path.expanduser(pss_spec))
    base = lib_path.joinpath("builder.jsonc")
    # Construct the core base function model
    library = Library.from_dict(JsoncParser.parse_file(base))
    base_ext = lib_path.joinpath("builder_extension.jsonc")
    # # If exists, construct the base extension function model and 'merge' with base
    if base_ext.exists():
        library.extend_base(LibraryExtension.from_dict(JsoncParser.parse_file(base_ext)))

    # For demo, load any/all user module in repository that are not builder focused
    for child in lib_path.iterdir():
        if not (child.stem == "builder" or child.stem == "builder_extension") and child.suffix == ".jsonc":
            library.add_module(Module.from_dict(JsoncParser.parse_file(child)))
    return library


def summary(slib: Library) -> None:
    """Summarize."""
    # list the build defs
    print(f"\nLibrary version {slib.version}")
    print(f"Builder context {slib.extension_for if slib.extension_for else 'standard'}")
    print("Builder functions:")
    for builder_name in slib.builder_functions.keys():
        print(f"  {builder_name}")

    print("\nModules / transactions / commands")
    for mname, module in slib.modules.items():
        print(f" {mname}")
        for txn in module.transactions:
            print(f"   Transaction -> {txn.name}")
            for cmd in txn.commands:
                print(f"     Command -> {cmd.name} -> {cmd.builder_command}")

    print()


if __name__ == "__main__":
    # For just a summary
    # summary(load("Library"))
    # For a full library dump
    print(load("Library").to_json(indent=2))

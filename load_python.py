"""Python s-ixchg loader."""

import os

# import json
from pathlib import Path
from jsonc_parser.parser import JsoncParser
from model import *


def read_it(pss_spec: str) -> Library:
    """read_it _summary_.

    :param pss_spec: _description_
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


if __name__ == "__main__":
    print(read_it("Library").to_json(indent=2))

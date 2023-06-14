"""Python s-ixchg loader."""

import os
import json
from pathlib import Path
from model import *


def read_it(pss_spec: str) -> None:
    """read_it _summary_.

    :param pss_spec: _description_
    :type pss_spec: str
    """
    # Load the base
    lib_path = Path(os.path.expanduser(pss_spec))
    base = lib_path.joinpath("builder.json")
    library = Library.from_dict(json.loads(base.read_bytes()))
    base_ext = lib_path.joinpath("builder_extension.json")
    if base_ext.exists():
        library.extend_base(LibraryExtension.from_dict(json.loads(base_ext.read_bytes())))
    for child in lib_path.iterdir():
        if not (child.stem == "builder" or child.stem == "builder_extension") and child.suffix == ".json":
            # in_data = json.loads(child.read_bytes())
            # library.add_module(Module.debug(in_data))
            library.add_module(Module.from_dict(json.loads(child.read_bytes())))
    print(library.to_json(indent=2))


if __name__ == "__main__":
    read_it("Library")

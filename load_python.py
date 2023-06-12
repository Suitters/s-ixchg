"""Sample."""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Union, Any
from dataclasses_json import DataClassJsonMixin, LetterCase, config


@dataclass
class AddressAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    value: Union[str, dict]

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class ObjectAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    value: Union[str, dict]

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class MoveFunctionAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    value: Any
    has_return: bool
    returns: str
    return_id: str

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class BuilderFunctionAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    value: Any
    has_return: bool
    returns: str
    return_id: str

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class StringAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    value: Union[str, dict]

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


def _build_alias_definition(alias_def: dict) -> Union[tuple[str, Any], Exception]:
    """."""
    if "type" in alias_def:
        name = alias_def["name"]
        alias_def["alias_type"] = alias_def.pop("type")
        match alias_def["alias_type"]:
            case "address":
                a_alias = AddressAlias.from_dict(alias_def)
            case "object":
                a_alias = ObjectAlias.from_dict(alias_def)
            case "builder-function":
                a_alias = BuilderFunctionAlias.from_dict(alias_def)
            case "move-function":
                a_alias = MoveFunctionAlias.from_dict(alias_def)
            case "string":
                a_alias = StringAlias.from_dict(alias_def)
            case _:
                raise ValueError(f"Alias type {alias_def['alias_type']} not implemented")
        return name, a_alias
    raise ValueError(f"Unknown alias type {alias_def}")


@dataclass
class Transaction(DataClassJsonMixin):
    """."""

    name: str
    sender: Optional[Union[str, dict]] = field(default_factory=str)
    sponsor: Optional[Union[str, dict]] = field(default_factory=str)
    aliases: Optional[Union[dict, list[dict]]] = field(default_factory=list)
    commands: Optional[list[dict]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """."""
        # Convert aliases
        alias_map = {}
        for alias in self.aliases:
            a_key, a_value = _build_alias_definition(alias)
            alias_map[a_key] = a_value
        self.aliases = alias_map

    def reconcile_alias_scope(self, global_alias: dict) -> None:
        """."""
        for a_key, a_value in self.aliases.items():
            if isinstance(a_value.value, dict):
                if "$ref" in a_value.value and a_value.value["$ref"][0] == "#":
                    target: str = a_value.value["$ref"][1:]
                    if target.count("/"):
                        components = target.split("/")
                        target = self.aliases[components[0]]
                        for comp in components[1:]:
                            target = getattr(target, comp)
                        a_value.value = target
                    else:
                        self.aliases[a_key] = self.aliases[target]


@dataclass
class Module(DataClassJsonMixin):
    """."""

    name: str
    version: str

    aliases: Optional[Union[dict, list[dict]]] = field(default_factory=list)
    transactions: Optional[list[Transaction]] = field(default_factory=list)

    # Convert aliases
    def __post_init__(self) -> None:
        """."""
        alias_map = {}
        for alias in self.aliases:
            a_key, a_value = _build_alias_definition(alias)
            alias_map[a_key] = a_value
        self.aliases = alias_map
        # Reconcile global 'ref' types
        for a_key, a_value in self.aliases.items():
            if isinstance(a_value.value, dict):
                if "$ref" in a_value.value and a_value.value["$ref"][0] == "#":
                    target: str = a_value.value["$ref"][1:]
                    if target.count("/"):
                        components = target.split("/")
                        target = self.aliases[components[0]]
                        for comp in components[1:]:
                            target = getattr(target, comp)
                        a_value.value = target
                    else:
                        self.aliases[a_key] = self.aliases[target]

        # Reconcile transaction scope alias 'ref' types
        for txn in self.transactions:
            txn.reconcile_alias_scope(self.aliases)


@dataclass
class BuilderArguments(DataClassJsonMixin):
    """."""

    name: str
    required: bool
    arg_type: list[str] = field(metadata=config(field_name="type"))
    items: Optional[list[str]] = field(default_factory=list)


@dataclass
class BuilderFunction(DataClassJsonMixin):
    """."""

    name: str
    has_return: bool
    arguments: Optional[list[BuilderArguments]] = field(default_factory=list)
    returns: Optional[str] = field(default_factory=str)
    return_id: Optional[str] = field(default_factory=str)


@dataclass
class LibraryExtension(DataClassJsonMixin):
    """."""

    version: str
    extends_for: str
    builder_functions: Union[list[dict], dict] = field(metadata=config(letter_case=LetterCase.CAMEL))

    # Convert builder functions to map
    def __post_init__(self) -> None:
        """."""
        if self.extends_for == "pysui":
            b_func_map: dict = {}
            for func in self.builder_functions:
                bfunc = BuilderFunction.from_dict(func)
                b_func_map[bfunc.name] = bfunc
            self.builder_functions = b_func_map
        else:
            raise ValueError(f"Extensions for {self.extends_for} not supported")


@dataclass
class Library(DataClassJsonMixin):
    """."""

    version: str
    builder_functions: Union[list[dict], dict] = field(metadata=config(letter_case=LetterCase.CAMEL))
    modules: Optional[dict[str, Module]] = field(default_factory=dict)
    extended_for: str = field(default_factory=str)

    # Convert builder functions to map
    def __post_init__(self) -> None:
        """."""
        b_func_map: dict = {}
        for func in self.builder_functions:
            bfunc = BuilderFunction.from_dict(func)
            b_func_map[bfunc.name] = bfunc
        self.builder_functions = b_func_map

    def extend_base(self, extension: LibraryExtension):
        """Extend/override from extension."""
        self.builder_functions = self.builder_functions | extension.builder_functions
        self.extended_for = extension.extends_for

    def add_module(self, module: Module):
        """Append new module."""
        self.modules[module.name] = module


def read_it(pss_spec: str) -> None:
    """read_it _summary_.

    :param pss_spec: _description_
    :type pss_spec: str
    """
    # Load the base
    lib_path = Path(os.path.expanduser(pss_spec))
    base = lib_path.joinpath("base.json")
    library = Library.from_dict(json.loads(base.read_bytes()))
    base_ext = lib_path.joinpath("base_extension.json")
    if base_ext.exists():
        library.extend_base(LibraryExtension.from_dict(json.loads(base_ext.read_bytes())))
    for child in lib_path.iterdir():
        if not (child.stem == "base" or child.stem == "base_extension") and child.suffix == ".json":
            library.add_module(Module.from_dict(json.loads(child.read_bytes())))
    print(library.to_json(indent=2))


if __name__ == "__main__":
    read_it("Library")

"""Model."""

from dataclasses import dataclass, field
from typing import Optional, Union, Any
from dataclasses_json import DataClassJsonMixin, LetterCase, config


@dataclass
class NumberAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    alias_value: Union[str, dict]

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
    alias_value: Union[str, dict]

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class AddressAlias(DataClassJsonMixin):
    """."""

    alias_type: str
    alias_value: Union[str, dict]

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
    alias_value: Union[str, dict]

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
    alias_value: Union[str, dict]
    has_return: bool
    returns: str
    result: str

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


def _build_alias_definition(alias_def: dict) -> Union[tuple[str, Any], Exception]:
    """."""
    if "alias_type" in alias_def:
        name = alias_def["name"]
        # alias_def["alias_type"] = alias_def.pop("type")
        match alias_def["alias_type"]:
            case "number":
                a_alias = NumberAlias.from_dict(alias_def)
            case "string":
                a_alias = StringAlias.from_dict(alias_def)
            case "address":
                a_alias = AddressAlias.from_dict(alias_def)
            case "object":
                a_alias = ObjectAlias.from_dict(alias_def)
            case "move-function":
                a_alias = MoveFunctionAlias.from_dict(alias_def)
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
            if isinstance(a_value.alias_value, dict):
                if "$ref" in a_value.alias_value and a_value.alias_value["$ref"][0] == "#":
                    target: str = a_value.alias_value["$ref"][1:]
                    if target.count("/"):
                        components = target.split("/")
                        target = self.aliases[components[0]]
                        for comp in components[1:]:
                            target = getattr(target, comp)
                        a_value.alias_value = target
                    else:
                        self.aliases[a_key] = self.aliases[target]


@dataclass
class Module(DataClassJsonMixin):
    """."""

    name: str
    version: str
    description: Optional[str] = field(default_factory=str)
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
            if isinstance(a_value.alias_value, dict):
                if "$ref" in a_value.alias_value and a_value.alias_value["$ref"][0] == "#":
                    target: str = a_value.alias_value["$ref"][1:]
                    if target.count("/"):
                        components = target.split("/")
                        target = self.aliases[components[0]]
                        for comp in components[1:]:
                            target = getattr(target, comp)
                        a_value.alias_value = target
                    else:
                        self.aliases[a_key] = self.aliases[target]

        # Reconcile transaction scope alias 'ref' types
        for txn in self.transactions:
            txn.reconcile_alias_scope(self.aliases)

    @classmethod
    def debug(cls, in_data: dict):
        """."""
        print(in_data)


@dataclass
class BuilderArguments(DataClassJsonMixin):
    """."""

    name: str
    required: bool
    argument_type: list[str]
    item: Optional[list[str]] = field(default_factory=list)

    # TODO: type and item verifications
    def __post_init__(self) -> None:
        """."""


@dataclass
class BuilderFunction(DataClassJsonMixin):
    """."""

    name: str
    has_return: bool
    function_arguments: Optional[list[BuilderArguments]] = field(default_factory=list)
    returns: Optional[str] = field(default_factory=str)
    result: Optional[str] = field(default_factory=str)


@dataclass
class LibraryExtension(DataClassJsonMixin):
    """."""

    version: str
    extension_for: str
    builder_functions: Union[list[dict], dict] = field(metadata=config(letter_case=LetterCase.CAMEL))

    # Convert builder functions to map
    def __post_init__(self) -> None:
        """."""
        if self.extension_for == "pysui":
            b_func_map: dict = {}
            for func in self.builder_functions:
                bfunc = BuilderFunction.from_dict(func)
                b_func_map[bfunc.name] = bfunc
            self.builder_functions = b_func_map
        else:
            raise ValueError(f"Extensions for {self.extension_for} not supported")


@dataclass
class Library(DataClassJsonMixin):
    """."""

    version: str
    builder_functions: Union[list[dict], dict] = field(metadata=config(letter_case=LetterCase.CAMEL))
    modules: Optional[dict[str, Module]] = field(default_factory=dict)
    extension_for: str = field(default_factory=str)

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
        self.extension_for = extension.extension_for

    def add_module(self, module: Module):
        """Append new module."""
        self.modules[module.name] = module

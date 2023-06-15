"""Model."""

from dataclasses import dataclass, field
from typing import Optional, Union, Any
from dataclasses_json import DataClassJsonMixin, LetterCase, config

#####################
# Aliases           #
#####################


@dataclass
class Alias(DataClassJsonMixin):
    """."""

    alias_type: str
    alias_value: Union[str, dict]


@dataclass
class NumberAlias(Alias):
    """."""

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class StringAlias(Alias):
    """."""

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class AddressAlias(Alias):
    """."""

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class ObjectAlias(Alias):
    """."""

    def as_pysui_type(self) -> Any:
        """."""
        return self

    def as_bcs_type(self) -> Any:
        """."""
        return self


@dataclass
class MoveFunctionAlias(Alias):
    """."""

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


#####################
# Commands          #
#####################


@dataclass
class Command(DataClassJsonMixin):
    """."""

    name: str
    builder_command: str


@dataclass
class SplitCoinsCommand(Command):
    """."""

    coin: Union[str, dict]
    amounts: list[Union[str, dict]]


@dataclass
class MergeCoinsCommand(Command):
    """."""

    destination_coin: Union[str, dict]
    source_coins: list[Union[str, dict]]


@dataclass
class TransferObjectsCommand(Command):
    """."""

    objects: list[Union[str, dict]]
    recipient: Union[str, dict]


@dataclass
class MoveCallCommand(Command):
    """."""

    target: Union[str, dict]
    arguments: list[Union[str, dict]]
    type_arguments: list[Union[str, dict]]


@dataclass
class MakeMoveVecCommand(Command):
    """."""

    objects: list[Union[str, dict]]


@dataclass
class PublishCommand(Command):
    """."""


@dataclass
class PublishUpgrade(Command):
    """."""


@dataclass
class PublicTransferObject(Command):
    """."""


@dataclass
class TransferSuiCommand(Command):
    """."""


@dataclass
class SplitCoinEqualCommand(Command):
    """."""


@dataclass
class SplitCoinAndReturnCommand(Command):
    """."""


@dataclass
class StakeCoinCommand(Command):
    """."""


@dataclass
class UnstakeCoinCommand(Command):
    """."""


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
        # Convert commands
        c_list: list[Command] = []
        for cmd in self.commands:
            match cmd["builder_command"]:
                case "split_coins":
                    c_list.append(SplitCoinsCommand.from_dict(cmd))
                case "merge_coins":
                    c_list.append(MergeCoinsCommand.from_dict(cmd))
                case "transfer_objects":
                    c_list.append(TransferObjectsCommand.from_dict(cmd))
                case "move_call":
                    c_list.append(MoveCallCommand.from_dict(cmd))
                case "make_move_vec":
                    c_list.append(MakeMoveVecCommand.from_dict(cmd))
                case "publish":
                    c_list.append(PublishCommand.from_dict(cmd))
                case _:
                    raise ValueError(f"Unable to parse command {cmd}")

    def reconcile_alias_scope(self, global_alias: dict) -> None:
        """."""
        # Reconcile tx aliases with module alias
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
        # Reconcile global 'ref' types within global scope
        # Refs can only refer to aliases within this scope
        # This should be refactored along with Transaction.reconcile_alias_scope
        for a_key, a_value in self.aliases.items():
            if isinstance(a_value.alias_value, dict):
                if "$ref" in a_value.alias_value and a_value.alias_value["$ref"][0] == "#":
                    self.aliases[a_key] = self.aliases[a_value.alias_value["$ref"][1:]]
                    # Ignore
                    # target: str = a_value.alias_value["$ref"][1:]
                    # if target.count("/"):
                    #     components = target.split("/")
                    #     target = self.aliases[components[0]]
                    #     for comp in components[1:]:
                    #         target = getattr(target, comp)
                    #     a_value.alias_value = target
                    # else:
                    #     self.aliases[a_key] = self.aliases[target]
                elif "$ref" in a_value.alias_value:
                    raise ValueError(f"{a_key} {a_value.alias_value} syntax error. Expected '#' reference symbol")

        # Reconcile transaction scope alias 'ref' types
        for txn in self.transactions:
            txn.reconcile_alias_scope(self.aliases)


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
        """Append new module and resolve references."""
        self.modules[module.name] = module

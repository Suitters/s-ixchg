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


# pysui treatments


@dataclass
class PublishCommand(Command):
    """."""

    project_path: str
    with_unpublished_dependencies: Optional[bool]
    skip_fetch_latest_git_deps: Optional[bool]
    legacy_digest: Optional[bool]


@dataclass
class PublishUpgradeCommand(Command):
    """."""

    project_path: str
    package_id: str
    upgrade_cap: str
    with_unpublished_dependencies: Optional[bool]
    skip_fetch_latest_git_deps: Optional[bool]
    legacy_digest: Optional[bool]


@dataclass
class PublicTransferObjectCommand(Command):
    """."""

    object_to_send: str
    recipient: str
    object_type: str


@dataclass
class TransferSuiCommand(Command):
    """."""

    recipient: str
    from_coin: str
    amount: str


@dataclass
class SplitCoinEqualCommand(Command):
    """."""

    coin: str
    split_count: str
    coin_type: str


@dataclass
class SplitCoinAndReturnCommand(Command):
    """."""

    coin: str
    split_count: str
    coin_type: str


@dataclass
class StakeCoinCommand(Command):
    """."""

    coins: list[str]
    validator_address: str
    amount: str


@dataclass
class UnstakeCoinCommand(Command):
    """."""

    staked_coin: str


def _resolve_simple_alias(base_alias: dict, value: dict, global_alias: Optional[dict] = None) -> dict:
    """."""
    if "$ref" in value.alias_value and value.alias_value["$ref"][0] == "#":
        target: str = value.alias_value["$ref"][1:]
        if target in base_alias:
            target = base_alias[target]
        elif global_alias and target in global_alias:
            target = global_alias[target]
        else:
            raise ValueError(f"Unable to resolve {target}")
    else:
        target = value
    return target


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
                case "publish_upgrade":
                    c_list.append(PublishUpgradeCommand.from_dict(cmd))
                case "public_transfer_object":
                    c_list.append(PublicTransferObjectCommand.from_dict(cmd))
                case "transfer_sui":
                    c_list.append(TransferSuiCommand.from_dict(cmd))
                case "split_coin_equal":
                    c_list.append(SplitCoinEqualCommand.from_dict(cmd))
                case "split_coin_and_return":
                    c_list.append(SplitCoinAndReturnCommand.from_dict(cmd))
                case "stake_coin":
                    c_list.append(StakeCoinCommand.from_dict(cmd))
                case "unstake_coin":
                    c_list.append(UnstakeCoinCommand.from_dict(cmd))
                case _:
                    raise ValueError(f"Unable to parse command {cmd}")
        self.commands = c_list

    def reconcile_alias_scope(self, global_alias: dict) -> None:
        """."""
        # Reconcile tx aliases with module alias
        for a_key, a_value in self.aliases.items():
            if isinstance(a_value.alias_value, dict):
                self.aliases[a_key] = _resolve_simple_alias(self.aliases, a_value, global_alias).alias_value

        # Resolve sender and sponsor aliases (if needed)
        if self.sender:
            if isinstance(self.sender, dict):
                sender_alias = Alias.from_dict({"alias_type": "", "alias_value": self.sender})
                self.sender = _resolve_simple_alias(self.aliases, sender_alias, global_alias).alias_value
        if self.sponsor:
            if isinstance(self.sponsor, dict):
                sponsor_alias = Alias.from_dict({"alias_type": "", "alias_value": self.sponsor})
                self.sponsor = _resolve_simple_alias(self.aliases, sponsor_alias, global_alias).alias_value

    def verify_commands(self, build_funcs: dict) -> None:
        """."""

        def is_alias_arg(in_bound: dict) -> tuple[bool, bool]:
            """."""
            is_alias: bool = False
            is_cmd_alias: bool = False
            if "$ref" in in_bound and in_bound["$ref"][0] == "#":
                is_alias = True
                if len(in_bound["$ref"][1:].split("/")) > 1:
                    is_cmd_alias = True
            return (is_alias, is_cmd_alias)

        for cmd in self.commands:
            if cmd.builder_command in build_funcs:
                for f_args in build_funcs[cmd.builder_command].function_arguments:
                    c_arg = getattr(cmd, f_args.name)
                    # Check for aliases in a list
                    if isinstance(c_arg, list):
                        for c_index, c_item in enumerate(c_arg):
                            if isinstance(c_item, dict):
                                is_alias, is_cmd_alias = is_alias_arg(c_item)
                                # Command aliases are resolved at runtime
                                if is_alias and not is_cmd_alias:
                                    temp_alias = Alias.from_dict({"alias_type": "", "alias_value": c_item})
                                    c_arg[c_index] = _resolve_simple_alias(self.aliases, temp_alias)
                    # Check if alias instance
                    elif isinstance(c_arg, dict):
                        is_alias, is_cmd_alias = is_alias_arg(c_arg)
                        if is_alias and not is_cmd_alias:
                            temp_alias = Alias.from_dict({"alias_type": "", "alias_value": c_arg})
                            setattr(cmd, f_args.name, _resolve_simple_alias(self.aliases, temp_alias))
                    else:
                        pass
            else:
                raise ValueError(f"Unknown builder function {cmd.builder_command}")


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
        for a_key, a_value in self.aliases.items():
            if isinstance(a_value.alias_value, dict):
                if "$ref" in a_value.alias_value and a_value.alias_value["$ref"][0] == "#":
                    self.aliases[a_key] = _resolve_simple_alias(self.aliases, a_value)

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
        # Perform validations and alias reconcilliations
        for txn in module.transactions:
            txn.verify_commands(self.builder_functions)

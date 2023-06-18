# s-ixchg

(rename pending)

Sui transaction interchange specification

While I put as much as I can to demonstrate **THIS IS A WIP** and open to constructive criticisms and ideas!
Just post them in the Issues....

### What it is

`s-ixchg` is a specification, codified as JSON in this repo, to exchange Sui transactions
in a declarative way.

### Features

- Aligns to Sui transaction capabilities
- Human readable/writeable
- Library orientation
  - Builder Functions (static)
  - User modules contain transactions and commands
- Library transaction builder function declarations
- Supports adding to (extending) or overriding (subsumming) builder functions
- Module global type aliases (DSL)
- Module transaction type aliases (DSL) (extend/subsume)

## Use Cases

- Compose a transaciton in typescript/javascript and send it to a backend process supporting the s-ixchg specification
- Export transactions to s-ixchg format for storage and versioning
- Hide complexity of building transactionse
- Enable a DSL veneer suited to domain usage

### L-EBNF

The 'lazy' EBNF spec is in **SPEC.md**

## Caveats

- Security: Need to think this through. For example:
  - Becuase transactions require signing (senders, sponsors) it would imply two applications communicating
    s-ixchg need to be aware of those address keys

## Layout

Note: Library json files are jsonc (JSON with comments). This is not set in stone as other
languages may not support or have libraries for it, but is currently used to provide more details in
the files about their constructs.

- README.md - This
- SPEC.md - Hacked EBNF
- modely.py - dataclasses for python (faux implementation)
- load_python.py - demo loader
- Library - Sample repository (assume maintained by SDK if persisted)
  - builder.jsonc - Base SDK programmable transaction builder capabilities
  - builder_extension.jsonc - `pysui` builder extensions/overrides
  - sample.jsonc - Contrived

## Running python example

Included is an incomplete yet demonstrable ingestion of s-ixchg using Python

From repo root:

```bash
python3 -m venv env
. env/bin/activate
pip install -U pip
pip install -r requirements.txt
python load_python.py
```

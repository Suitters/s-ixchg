# s-ixchg

(rename pending)

Sui transaction interchange specification

THIS IS A WIP and open to constructive criticisms and ideas! Just post them in the Issues....

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

- Security: Becuase transactions require signing (senders, sponsors) it would mean two applications communicating
  s-ixchg need to be aware of those keys

## Layout

- README.md - This
- SPEC.md - Hacked EBNF
- modely.py - dataclasses for python only
- load_python.py - demo loader
- Library - Sample repository (assume maintained by SDK if persisted)
  - builder.json - Base SDK programmable transaction builder capabilities
  - builder_extension.json - `pysui` builder extensions/overrides
  - sample.json - Contrived

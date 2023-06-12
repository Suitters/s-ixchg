# s-ixchg

(rename pending)

Sui transaction interchange specification

## What it is

`s-ixchg` is a specification, codified as JSON in this repo, to exchange Sui transactions
in a declarative way.

## Features

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
- Hide complexity of building transactions

## Caveats

- Security: Becuase transactions require signing (senders, sponsors) it would mean two applications communicating
  s-ixchg need to be aware of those keys

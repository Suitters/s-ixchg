# s-ixchg spec L-EBNF

L-EBNF: Lazy (me) with very rusty EBNF memory... but here goes

Hints:

- \+ = One or more
- \* = Zero or more
- ? = Zero or one
- (\* ... \*) = comment

```
(* start... library is implementation specific, listed here for containment representation  *)
library
    : builder module*
    ;

(***************************************************************************************)
(* builder and builder_extension are stock SDK capabilities and should not be modified *)
(* builder and builder_extension are visible to grammar designers                      *)
(***************************************************************************************)

(* base, common, declarations of capabilities of all transaction builders *)

builder
    : version builder_functions+ builder_extension?
    ;

(* SDK builder additions and/or overrides of base builder functions                     *)
(* e.g. TS-SDK "publish(modules, dependencies)" vs pysui "publish(project_source_path)" *)

builder_extension
    : version extension_for builder_functions+
    ;

(* identifies extensions are specific to certain SDK        *)
(* e.g. pysui, sui4j, sui-go-sdk, go-sui-sdk, sui-net, etc. *)

extension_for
    : name
    ;

(* functions in 'builder' are required, in 'builder_extension' in addition at the SDK level *)
builder_functions
    : name function_arguments has_return (returns result)?
    ;

function_arguments
    : function_argument*
    ;

function_argument
    : name required type item?
    ;


(***************************************************************************************)
(* module contains domain specific transaction and command representation              *)
(* it is what/how DSL writers organize the concrete declarations                       *)
(***************************************************************************************)

module
    : name version description? aliases transactions
    ;

aliases:
    : alias*
    ;

alias
    : name alias_type value

(***************************************************************************************)
(* low level productions and terminals                                                 *)
(***************************************************************************************)

(* type describes the form an argument can take *)
type
    : ("string"? | "number"? | "object-id"? | "gas"? | result? | alias?)*
    | "list" item
    ;

(* list items *)
item
    : ("string"? | "number"? | "object-id"? | result? | alias?)*
    ;

result
    : name
    ;

(* single (Result), multiple (list of NestedResult) *)
returns
    : "single" | "multiple"
    ;

has_return
    : "true" | "false"
    ;

required
    : "true" | "false"
    ;

name
    : [a-zA-Z][a-zA-Z0-9]{1,20}
    ;

(* Should be standardized, consider semantic versioning as well *)
version
    : [a-zA-Z][a-zA-Z0-9]{0,10}
    ;

description
    : (* utf-8 regex for one or more words in quotes *)
    ;

```

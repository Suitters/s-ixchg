# s-ixchg spec EBNF

I'm so very rusty with EBNF, but here goes

```
library = builder (module*)?;

(* base, common, builder declarations *)
builder
    : version builder_functions+ builder_extension?
    ;

(* builder additions and/or overrides of base builder functions *)
builder_extension
    : version extension_for builder_functions*
    ;

(* identifies SDK potential extensions to a builder that are well known *)
extension_for
    : "pysui"
    ;

(* *)
builder_functions
    : name function_arguments has_return (returns result)?
    ;

function_arguments
    : function_argument*
    ;

function_argument
    : name required type items?
    ;

type
    : "string"
    | "object-id" | "gas" | result | alias
    |
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
```

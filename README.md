# mus2muc

`mus2muc` is a software to enumerate MUCs of LTLf specifications in conjunctive forms. It leverages Answer Set Programming (ASP) minimal unsatisfiable subprograms algorithms, as implemented in the WASP solver.

## Installation

This repository should be cloned using the `--recurse-submodules` option, to clone the `wasp` and `aaltaf` repository. 

The repository is a `uv` project, you can install dependencies by `uv build`, `uv pip install .`.

The ASP solver `wasp` is a required dependency to enumerate MUSes. Refer to the repository for installation instructions:

* WASP: `https://github.com/alviano/wasp`

:warning: In order to be used with our tool, the `wasp` solver must be _patched_ to provide time-stamps in MUC computations. Follow the installation instructions. Please check the `patch_wasp` goal in the `Makefile`.

Additionally, `black` and `aaltaf` are required in order to be used as certifiers. Refer to the corresponding repositories for installation instructions:

* `https://github.com/black-sat/black`
* `https://github.com/lijwen2748/aaltaf`

:warning: We assume that either `black` or `aaltaf` are available as executables in `/usr/bin`. This path can be customized by means of the `--bin-folder` flag, but it is not possible to customize the executable names. Please perform a copy/symlink your executables!


## Input format 

The expected input format is a file containing a labeled LTLf formula on each line:

```
<identifier> := <ltlf_formula>
```

where `identifier` can be any string, and `ltlf_formula` is an LTLf formula.

## Example usage

You can check all the command line arguments by means of `--help`. This is an example:

```
mus2mus --bin-folder bin/ --certifier aaltaf <input formula> -t 60
```

This runs the system with a timeout of 60 seconds on `<input formula>`, using `wasp` and `aaltaf` executables in the `bin/` folder. The system producs in `stdout` JSON items which contain information about found MUCs. The `-v` flag allows for a richer set of events (e.g., MUSes that are disproved, `wasp` restarts, and so on).

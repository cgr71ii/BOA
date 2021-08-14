# BOA - Buffer Overflow Annihilator

`BOA` is a software analyzer which attempts to search software vulnerabilities. This tool has been developed trying to maximize the modularity in order to write new modules which might, for instance, add support for unsupported programming languages, add new techniques in order to search vulnerabilities, use other parsers, etc.

There are different type of modules, and due to these modules, the main features of `BOA` are:

* Programming language-independent.
* Generic software analyzer.
* High modularity.
* Granularity might differ depending on the specific modules.
* **Static** and **dynamic** analysis support.

## Requirements

In order to install and run `BOA` successfully, you will need, at least, python>=3.8.5. If you have another version, you can use [Miniconda](https://docs.conda.io/en/latest/miniconda.html):

```bash
# Install Miniconda3 (x86_64)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create new environment
conda create -n your_environment_name python=3.8.5
# Activate environment
conda activate your_environment_name
```

The following dependencies might also be installed in a conda environment (is so, you will need to look for the dependencies in the [Anacoda Repository](https://anaconda.org/anaconda/repo)), but we will use an apt-like package manager:

```bash
# general dependencies
sudo apt install git
```

### Dynamic analysis

For dynamic analysis, the main requirement is [Intel PIN](https://software.intel.com/content/www/us/en/develop/articles/pin-a-binary-instrumentation-tool-downloads.html), a tool for binary instrumentation. All you will need to do is download the latest kit (BOA has been tested with kit [version 3.20](https://software.intel.com/sites/landingpage/pintool/downloads/pin-3.20-98437-gf02b61307-gcc-linux.tar.gz)). Once it is downloaded, depending on the module you will use, you will need to provide the path to the kit.

## Installation

To install `BOA`, first clone the repository:

```bash
git clone https://github.com/cgr71ii/BOA.git
```

Once the repository has been cloned, run:

```bash
cd BOA

# create virtual environment & activate
python3 -m venv /path/to/virtual/environment
source /path/to/virtual/environment/bin/activate

# install dependencies in virtual enviroment
pip3 install --upgrade pip
pip3 install -r requirements.txt
## skip those that you expect to do not use
pip3 install -r requirements-static-analyzer.txt
pip3 install -r requirements-dynamic-analyzer.txt
```

## Usage

You can easily check the different options running:

```bash
python3 boa/boa.py --help
```

The different parameters are:

```bash
usage: boa.py [-h] [-v] [--no-fail] [--print-traceback] [--logging-level N]
              [--log-file PATH] [--log-display]
              target rules-file
```

### Parameters

There are different parameters in order to achieve different behaviours:

* Mandatory/Positional:
  1. `target`: path to source code file (static analysis) or full path to binary (dynamic analysis) which is the target of the analysis.
  2. `rules-file`: path to rules file where all the directives of the analysis are defined (you may find these files at `boa/rules`). This file is the configuration for a specific analysis.
* Optional:
  * Meta:
    * `-h, --help`: help message and exit.
    * `-v, --version`: show version and exit.
  * Modules:
    * `--no-fail`: when optional modules are being loaded, if some of them could not been loaded, the execution finishes. Since these modules might be considered optional, the execution may carry on if this option is set.
  * Other:
    * `--print-traceback`: by default, exceptions are handled and verbose messages are displayed. In the case that you want to display the traceback when something fails, use this option (it might be useful for debugging).
  * Other (logging):
    * `--logging-level N`: level of logging to show the different lines related to a concrete severity. The more verbose value is a value of 0, but the default value is to show info messages (i.e. info and above).
    * `--log-file PATH`: log file where all the logging entries will be stored. When this option is set, the logging messages will only stored in the provided file and not displayed in the terminal.
    * `--log-display`: since when you provide a file with `--log-file PATH` the messages are not displayed on the terminal, you might want to see them as well on the terminal, and this behaviour can be achieved with this option.

## Modules

Different modules are available and they achieve specific goals. General modules are:

* `LifeCycle`: general modules which define the main flow of execution (i.e. order and information provided to the different modules). These modules might be used either for static or dynamic analysis, but there might be lifecycle modules which only support a specific analysis (this may be set).
* `Security Modules`: general modules which should contain the behaviour of a specific technique in order to look for vulnerabilities (e.g. detect calls to dangerous functions).
* `Report`: general modules which define the way the results are generated (e.g. terminal output, HTML).
* `Runner`: general modules which analyze or run the provided code or binary. These modules might be totally dependent of the analysis, so different modules have been defined (check [static analysis](#static-analysis) and [dynamic analysis](#dynamic-analysis) modules).
* `[Enumerations] Severity`: this is not exactly a module, but an enumeration. Anyway, this module behaves like the others but only contain data, not behaviour. The data of these modules contain different values of severity which may be used by the other modules in order to report vulnerabilities and assign them a specific vulnerability.

### Static analysis

There are modules which can only be used when the analysis is static analysis:

* `Parser`: modules which parse code files in order to obtain information. Usually, these modules use a specific parser (e.g. pycparser), builds the AST (Abstract Syntax Tree) and give nodes of the AST to a `Vulnerability Module`.

### Dynamic analysis

There are modules which can only be used when the analysis is dynamic analysis:

* `Input`: modules whose goal is generate random inputs. Specific modules might be coded, but general ones are provided (e.g. module which you can provide a grammar and likelihoods of each rule).
* `Fail`: modules whose goal is detect when an execution failed. The most basic way is check out the exit status, but more semantic ways might be coded (e.g. check if a software which generates images generated the image you were expecting).

## Input file format

TODO

### Dependencies

TODO: only a few notes have been added (these notes are not about the format, but about the behaviour of the dependencies, and maybe these notes might be set elsewhere like in the internal documentation):

* The dependencies are security modules which can be a dependency of other security module. These dependencies have to be defined as a security module and as dependency.
* The execution order will be resolved creating a DAG (if is not acyclic, it will be detected and the execution stopped), and the dependencies will be executed before of the security modules which have these dependencies.
* The dependencies can also be directly executed by the security modules if liked. In this case, you will need to get the instance of the dependency from the security module.
* When a dependency is defined also as module, is in the module definition where the arguments have to be set. In the dependency definition is where a callback is set and this callback is what the security module which have this module as dependency will call in order to interact with the dependency.

### Static analysis

TODO

### Dynamic analysis

TODO

## Implementing new modules

If you want to implement new [modules](#modules), all is ready to only write the new modules in the correct directory. For instance, if you want to implement a new `Report` module, you would only need to write a new file on `boa/reports`, and this file should:

* Have a similar name to the other modules.
* Have a class where all the behaviour should be contained.
* Inherit from the base class (e.g. in the case of `Report` modules, the base class is on the file `boar_abstract.py`).

## Example

Example where we load a module which looks for 'dangerous' functions calls in C files:

```bash
BOA_PATH="/path/to/BOA"

python3 $BOA_PATH/boa/boa.py \
        $BOA_PATH/tests/C/synthetic/test_basic_buffer_overflow.c \
        $BOA_PATH/boa/rules/rules_static_function_match_pycparser.xml
```

The output of the previous execution should be:
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~ boam_function_match.BOAModuleFunctionMatch ~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 + Threat (10, 9): strcpy: destination pointer (first argument) length has to be greater or equal than origin (second argument) to avoid buffer overflow threats.
   Severity: FREQUENTLY MISUSED.
   Advice: You can use 'strcpy', but be sure about the length problem (check boundaries) and set correctly the end character. If you want a safer function, check 'strncpy', which is safer but not safe or 'strlcpy'.

 + Threat (14, 9): strcpy: destination pointer (first argument) length has to be greater or equal than origin (second argument) to avoid buffer overflow threats.
   Severity: FREQUENTLY MISUSED.
   Advice: You can use 'strcpy', but be sure about the length problem (check boundaries) and set correctly the end character. If you want a safer function, check 'strncpy', which is safer but not safe or 'strlcpy'.

 + Threat (17, 5): printf: first argument has to be constant and not an user controlled input to avoid buffer overflow and data leakage.
   Severity: MISUSED.
   Advice: Use a constant value as first parameter.

   Total threats: 3

~~~~~~~~~~~
~ Summary ~
~~~~~~~~~~~
 - Total threats (all modules): 3

```

## Documentation

Full documentation may be found at `boa/docs`.

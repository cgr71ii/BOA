
.. toctree::
   :hidden:

   parser_modules/boapm_abstract
   parser_modules/boapm_pycparser
   
.. _parser-modules:

Parser Modules
==============
The parser modules are the one which works directly with a
parser in order to process a code file and get processed
data structures. With these datastructures you will be able
to work in your security modules.

You should have a parser module for each programming language
you want to work with, but can have different parser for the
same programming language if you like.

These modules can be found in the main directory of BOA,
concretely in the directory "parser_modules". The files you will find
there will have a name like "boapm_whatever.py", but is not
necessary to follow the nomenclature. You can name your modules
as you like. If you want to write your own, you will have to
store your module in the expected directory
(i.e. /path/to/BOA/parser_modules).

All your parser modules will need to inherit from
*BOAParserModuleAbstract* in order to work as a parser module.

BOA internals
-------------
* :ref:`parser-modules-boapm-abstract`

Modules
-------
* :ref:`parser-modules-boapm-pycparser`

.. include:: ../footer.rst
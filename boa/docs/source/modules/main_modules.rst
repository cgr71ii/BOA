
.. toctree::
   :hidden:

   main_modules/boa
   main_modules/boa_internals
   main_modules/args_manager
   main_modules/constants
   main_modules/rules_manager
   main_modules/modules_importer
   main_modules/own_exceptions
   main_modules/util
   main_modules/severity_enums

.. _main-modules:

Main Modules
============
The modules which BOA uses for making the core works.

Modules
-------
* :ref:`main-modules-boa`
   * BOA main flow. It is the entry point.
* :ref:`main-modules-boa-internals`
   * It has methods which BOA uses in the main flow.
* :ref:`main-modules-args-manager`
   * It is an utility which works with ArgParse and helps us to manage the BOA args.
* :ref:`main-modules-constants`
   * Constant values definitions.
* :ref:`main-modules-rules-manager`
   * It handles the rules files checking they are well formatted and it gives us the information.
* :ref:`main-modules-modules-importer`
   * It handles the modules importing, focusing the security modules. It has utilities for importing other modules.
* :ref:`main-modules-severity-enums`
   * It contains enumerations which defines different levels of severity.
* :ref:`main-modules-own-exceptions`
   * It defines own exceptions.
* :ref:`main-modules-util`
   * General utilities.

.. include:: ../footer.rst
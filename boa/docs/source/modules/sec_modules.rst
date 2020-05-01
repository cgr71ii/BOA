
.. toctree::
   :hidden:

   sec_modules/boam_abstract
   sec_modules/boam_function_match
   sec_modules/boam_cfg
   sec_modules/boam_taint_analysis
   sec_modules/boam_test

.. _sec-modules:

Security Modules
================
Security modules are the main way a user can define its own
modules in order to look for a concrete threat.

These modules can be found in the main directory of BOA,
concretely in the directory "modules". The files you will find
there will have a name like "boam_whatever.py", but is not
necessary to follow the nomenclature. You can name your modules
as you like. If you want to write your own, you will have to
store your module in the expected directory
(i.e. /path/to/BOA/modules).

All your security modules will need to inherit from *BOAModuleAbstract*
in order to work as a security module.

BOA internals
-------------
* :ref:`sec-modules-boam-abstract`

Modules
-------
* :ref:`sec-modules-boam-function-match`
* :ref:`sec-modules-boam-cfg`
* :ref:`sec-modules-boam-test`
* :ref:`sec-modules-boam-taint-analysis`

.. include:: ../footer.rst
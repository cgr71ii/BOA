
.. toctree::
   :hidden:

.. _changelog:

Changelog
=========
You will find here the main changes from one version to others.

Version 0.3
-----------
Dependencies among modules are possible.

Changes:

* The results of a module can be a dependency for others.

Fixed errors:

* Main argument "--no-fail" was not working as expected.
* When a module loading failed and the execution continued,
  was not being correctly removed.
* Minnor fixes.

Version 0.2
-----------
This version has made other elements to be customizable.

Changes:

* Support for other programming lenguages.
   * Customizable parser modules.

* Customizable lifecycles.
* Customizable reports.

Fixed errors:

* When a module could not load properly its arguments, was smashing
  all the arguments of the other modules.
* Some checks were not being done to avoid that customizable elements
  did not inherit from the defined abstract class.

Version 0.1
-----------
This version has finished BOA core implementation.

Changes:

* Support for C programming language (with pycparser).
   * Support only for AST.

* Rules files parsing.
   * Very flexible with arguments for modules.

* Unique lifecycle.
* Multiple modules execution.
* Modules customizable.
* Threats report.
   * Severity customizable.

.. include:: footer.rst


.. toctree::
   :hidden:

   lifecycles/boalc_manager
   lifecycles/boalc_abstract
   lifecycles/boalc_basic
   lifecycles/boalc_pycparser_ast

.. _lifecycles:

Lifecycles
==========
These modules are the ones which defines the way the execution is driven.
When you want to perform a concrete execution of your security modules, a
lifecycle might do what you want do. In the lifecycles are defined the methods
and the order in which they will be invoked, and you can take the decision
of what information will need your security modules, use callbacks as
arguments to make a call back to a method of your lifecycle and take that
feedback to your lifecycle for taking decisions, etz.

These modules can be found in the main directory of BOA,
concretely in the directory "lifecycles". The files you will find
there will have a name like "boalc_whatever.py", but is not
necessary to follow the nomenclature. You can name your modules
as you like. If you want to write your own, you will have to
store your module in the expected directory
(i.e. /path/to/BOA/lifecycles).

All your lifecycles will need to inherit from *BOALifeCycleAbstract* in order
to work as a lifecycle.

BOA internals
-------------
* :ref:`lifecycles-boalc-manager`
* :ref:`lifecycles-boalc-abstract`

Modules
-------
* :ref:`lifecycles-boalc-basic`
* :ref:`lifecycles-boalc-pycparser-ast`

.. include:: ../footer.rst
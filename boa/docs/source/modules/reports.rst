
.. toctree::
   :hidden:

   reports/boar_abstract
   reports/boar_stdout
   reports/boar_basic_html

.. _reports:

Reports
=======
The reports are the last phase of BOA and is where all the
found threats are displayed. The way the reports can be displayed
is customizable. There are basic Report implementation like
*BOARStdout* or *BOARBasicHTML*, but you can define your own.

These modules can be found in the main directory of BOA,
concretely in the directory "reports". The files you will find
there will have a name like "boar_whatever.py", but is not
necessary to follow the nomenclature. You can name your modules
as you like. If you want to write your own, you will have to
store your module in the expected directory
(i.e. /path/to/BOA/reports).

All your report modules will need to inherit from *BOAReportAbstract*
in order to work as a report module.

BOA internals
-------------
* :ref:`reports-boar-abstract`

Modules
-------
* :ref:`reports-boar-stdout`
* :ref:`reports-boar-basic-html`

.. include:: ../footer.rst
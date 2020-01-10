.. BOA documentation master file, created by
   sphinx-quickstart on Fri Jan 10 08:43:44 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


BOA's documentation
===================

BOA (Buffer Overflow Annihilator) is a vulnerability analyzer of general purpose.
It is written in Python, and the main principle which it has coded has been to
give the maximum flexibility to the user, and for that reason, modularity is a
BOA's priority. Through dynamic modules loading, it is possible to use the language
parser which the user wants and use it to focus their own security needs.

.. toctree::
   :hidden:

   modules/main_modules
   modules/sec_modules
   modules/parser_modules

.. include:: footer.rst

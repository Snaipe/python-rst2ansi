rst2ansi
========

A python module dedicated to rendering RST (reStructuredText) documents
to ansi-escaped strings suitable for display in a terminal.

|asciicast|

Installation
------------

Requirements
~~~~~~~~~~~~

Python 3.3+

PyPi package
~~~~~~~~~~~~

.. code:: bash

    pip install rst2ansi

Usage
-----

As a CLI utility:
~~~~~~~~~~~~~~~~~

.. code:: bash

    usage: rst2ansi [-h] [file]

    Prints a reStructuredText input in an ansi-decorated format suitable for
    console output.

    positional arguments:
      file        A path to the file to open

    optional arguments:
      -h, --help  show this help message and exit

As a python module:
~~~~~~~~~~~~~~~~~~~

.. code:: python

    from rst2ansi import rst2ansi

    print(rst2ansi('I **love** reStructuredText!'))

.. |asciicast| image:: https://asciinema.org/a/drykz69gtn557z3hxnbb1jybq.png
   :target: https://asciinema.org/a/drykz69gtn557z3hxnbb1jybq

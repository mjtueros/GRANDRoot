Welcome to the How To
*********************

This page has a summary of the steps necessary to generate this documentation.

Requirements
============

The requirements to generate this documentation are `Sphinx <https://www.sphinx-doc.org/en/master/>`_ and `sphinx-rtd-theme <https://pypi.org/project/sphinx-rtd-theme/>`_::

    pip install -U Sphinx
    pip install sphinx-rtd-theme

The theme `python_docs_theme <https://pypi.org/project/python-docs-theme/>`_ can also be a nice choice.

Configuration
=============

Create a ``doc`` directory to host the documentation::

    mkdir doc; cd doc

Run the configuration script from the ``doc`` directory as follows::

    sphinx-quickstart

You can answer ``y``, ``GRANDRoot``, ``GRAND Collaboration``, ``0.0.1``. Ths can be changed later on the ``conf.py`` file that will be created in the ``source`` folder.

Changing the ``conf.py`` file
-----------------------------

Uncomment the following lines on the ``conf.py`` file in the ``source`` folder::

    import os
    import sys

And include the following line::

    sys.path.insert(0, os.path.abspath('../../'))

Change the ``extensions`` and ``html_theme`` variables

.. code-block::

    extensions = ['sphinx.ext.autodoc',
        'sphinx.ext.napoleon',
        'sphinx.ext.mathjax',
        'sphinx.ext.autosummary'
    ]

    html_theme = 'sphinx_rtd_theme'

Creating a documentation page
=============================

Create a file inside the ``source`` directory named ``GRANDRoot.rst`` and include the following lines

.. code-block::

    GRANDRoot
    =====================

    .. automodule:: GRANDRoot
        :members:
        :show-inheritance:

Now you need to include the reference to this file in the ``index.rst``, for example

.. code-block::

    Modules
    -------

    .. toctree::
        :maxdepth: 2
        :caption: Contents:

        GRANDRoot

Here is an example of code documentation

.. code-block::

    def Setup_SimShowerRun_Branches(tree,create_branches=True):
        """
        Create or Set rhe TTree branches for SimShower_Run (Simulated Showeer Run Level information )

        Args:
            tree (string): a TTree
            create_branches (bool): toggles the branch creation on and off

        Returns:
            values: the current values for the branches
        """

Building the documentation
==========================

In order to build the documentation, go to the ``doc`` directory and run ``make html``.
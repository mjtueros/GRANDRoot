Welcome to the How To {#HowTo}
=====================

This page has a summary of the steps necessary to generate this
documentation.

Requirements
------------

The requirement to generate this documentation is the 
[Doxygen](https://www.doxygen.nl/index.html):

    sudo apt install doxygen

Configuration
-------------

Create a `doc` directory to host the documentation:

    mkdir doc; cd doc

Run the configuration script from the `doc` directory as follows:

    doxygen -g


### Changing the Doxyfile file

Set the variables as follows:

	PROJECT_NAME           = "GRANDRoot doxygen documentation"
	JAVADOC_AUTOBRIEF      = YES
	OPTIMIZE_OUTPUT_JAVA   = YES
	EXTRACT_ALL            = YES
	EXTRACT_PRIVATE        = YES
	EXTRACT_STATIC         = YES
	HIDE_SCOPE_NAMES       = YES
	SORT_BRIEF_DOCS        = YES
	GENERATE_LATEX         = NO
	INPUT                  = ../ ./ *.md
	USE_MDFILE_AS_MAINPAGE = index.md


Creating a documentation page
-----------------------------

This documentation uses [Markdown](https://www.markdownguide.org/) files. You need to include a source file for the main page `index.md`, for example:

    Welcome to GRANDRoot's documentation!
    ======================================

    Introduction
    ------------

    [HowTo](@ref HowTo)

    Modules
    -------

    GRANDRoot

The referenced pages have to be named. The header of the ``HowTo.md`` file is the following in this example:

    Welcome to the How To {#HowTo}
    =====================

    This page has a summary of the steps necessary to generate this
    documentation.


Here is an example of code documentation for the function GRANDRoot.Setup_SimShowerRun_Branches:

    """!
    Create or Set rhe TTree branches for SimShower_Run (Simulated Showeer Run Level information )
    
    @param tree (string) a TTree
    @param create_branches (bool) toggles the branch creation on and off
    
    @return The current values for the branches
    """


Building the documentation
--------------------------

In order to build the documentation, go to the `doc` directory and run
`doxygen`.

Generating using Sphinx
-----------------------

Installing the [Breathe](https://pypi.org/project/breathe/) extension:

    pip install breathe

Makes it possible to generate Sphinx documentation from the `xml` output from `Doxygen`.

The requirements to generate this documentation are
[Sphinx](https://www.sphinx-doc.org/en/master/) and
[sphinx-rtd-theme](https://pypi.org/project/sphinx-rtd-theme/):

    pip install -U Sphinx
    pip install sphinx-rtd-theme

The theme
[python\_docs\_theme](https://pypi.org/project/python-docs-theme/) can
also be a nice choice.

Configuration
-------------

You need to set the xml output in the `Doxyfile` changing the line:

    GENERATE_XML           = YES

Run the configuration script from the `doc` directory as follows:

    sphinx-quickstart

You can answer `y`, `GRANDRoot`, `GRAND Collaboration`, `0.0.1`. Ths can
be changed later on the `conf.py` file that will be created in the
`source` folder.

### Changing the conf.py file

Change the `extensions` and `html_theme` variables:

    extensions = [ "breathe" ]

    html_theme = 'sphinx_rtd_theme'

Include these configuration lines:
   
    # Breathe Configuration
    breathe_projects = { "GRANDRoot": "../xml/" }
    breathe_default_project = "GRANDRoot"

Creating a documentation page
-----------------------------

Create a file inside the `source` directory named `GRANDRoot.rst` and
include the following lines:

    GRANDRoot
    =====================

    .. doxygennamespace:: GRANDRoot

Another file inside the `source` directory named `HowTo.rst` can handle a custom page as follows:

    Welcome to the How To
    *********************

    .. doxygenpage:: HowTo
        :content-only:

Now you need to include the reference to this file in the `index.rst`,
for example:

    Modules
    -------

    .. toctree::
        :maxdepth: 2
    
        GRANDRoot


Building the documentation
--------------------------

In order to build the documentation, go to the `doc` directory and run
`make html`.
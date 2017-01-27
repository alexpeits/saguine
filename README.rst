saguine
=======

Simple static site generator


Installation
------------

::

    $ git clone https://github.com/alexpeits/saguine.git saguine && cd saguine
    $ mkvirtualenv --python=`which python3` saguine
    $ pip install .  # or "pip install -e ." for editable


Usage
-----

First, create a project directory with the following structure::

    myblog/
    |- config.yml
    |- site/
       |- ...


``config.yml`` must have the following format::

    pages:
        - Home: index.md
        - Blog: blog
        - About: about.md
    sitename: My Blog

In this case, the ``site`` directory will look like this::

    myblog/
    |- config.yml
    |- site/
       |- index.md
       |- about.md
       |- blog/
          |- post1.md
          |- post2.md
          |- ...


Then, run::

    $ saguine /path/to/myblog  # or "saguine ." if in the same directory

This will copy any templates and static files, and generate the static site inside
the "web" directory. This is the directory that should be served (github pages etc.)


Note
----

The "web" folder gets deleted and re-generated at each invocation of the cli script
(for now), so don't put anything else in there (also don't make it a git repo).

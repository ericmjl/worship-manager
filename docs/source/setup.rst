Setup
=====

Read this page for documentation on how to set up the application.

Overview
--------

The application is structured in two parts: app logic is stored in the
GitHub repository, while the data are stored in the `$HOME` directory of the
user that is running the app.

    ~/path/to/worship-manager/
        |- run.py
        |- app/
        |- ...
    ~/.worship-manager/
        |- data/
            |- database/
                |- coworker.db
                |- program.db
                |- song.db
            |- files/
                |- *.pdf

PDFs for sheet music are stored under the ``files/`` directory, while the
TinyDB database files are stored under the ``database/`` directory.

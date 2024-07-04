Calibre Babelio Parser metadata
==========================

Scraps metadata from Babelio database and updates the metadata in the calibre library.

Inspired and copied from Calibre Babelio plugin and Calibre Comic Vine Scraper project

Can run without Calibre installation throught docker container

.. warning::
    Only update metadata when only one book match with babelio db

Install
-------

```pip install -r requirements.txt```

Configure
---------

Rename `config.json.sample` to `config.json` and update the values accordingly.

- CALIBRE_LIBRARY_PATH: The path to the calibre library. This is the path to the folder that contains the metadata.db file.
- UNIQUE_AGENT_ID: This is the unique agent ID used to fetch data on ComicVine as per the API documentation. It says to use something unique and meaningful. E.g: "ajite super manga fet
- BABELIO_URL: "https://www.babelio.com" (should not change :D )
- QUERY_WITH_IDENTIFIER": false, (Deprecated) let stay at FALSE
- DEBUG: false/true For verbose mode

Feature in progress
-------------------

- List of books based from Virtual library
- list of books base from Query (calibre query like)
- set pause between Scraps
- Perform right selection when found more than 1 book

.. warning::
    Take care about number of requests to Babelio web site 😈
    You could be banned by Babelio

Run
---

```./run.sh```

Will create/launch the Calibre docker container and run the run.py file


At the moment I only fetch the following metadata:
- Authors
- Title
- Rating
- Description
- Identifier
- Tags

when only one book match 


Disclaimer
----------

These scripts are provided as is and I take no responsibility for any damage they might cause to your calibre library. Use at your own risk.
I made these scripts quickly to update my own library and I am sharing them in case they are useful to someone else.

Feel free to fork and improve them.

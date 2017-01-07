The Beer Archive
================

The Homebrewer's blog software

Currently in development.

[Pretty much all documentation.](LOG.md)

License
-------

Copyright &copy; 2017 - Dries007
License: [MIT](LICENSE.md)


## Original design document
### Structure

Every beer has it's own micro blog:
- Name
- Description
- Style
- Recipe
- Source
- Recipe
- Brewer(s)
- Volume
- Batch number
- Current state (planned, brewing, bottled, scrapped, ...)
- Graphs with API to automatically add data points
- Updates (Blog style)
	- Text
	- Photo
	- State changes

Not linked to any beer:
- Home
	- List of most recent updates
	- Beers in progress
- The Beer List
	- Filter / Sort by date, type, brewer, ...

### Software

- Docker
- Nginx
- Let's Encrypt
- PostgreSQL
- Python (uwsgi)
	- SQLAlchemy
	- Flask (Jinja2)
- Bootstrap (+ Font Awesome)
	- jQ / Ajax

Installation Instructions
-------------------------

Find installation instructions in [HOWTO.md](HOWTO.md).


License
-------

Copyright &copy; 2016 - 2017 Dries007
License: See [LICENSE.md](LICENSE.md)

(You are not allowed to remove the HTML "generator" meta tag.)


Installation manual
===================


Database init
-------------

prerequisites:
- Docker running

Join Flask session interactively: 
- `# docker exec -it thebeerarchive_app_1 bash`
- `python -m uBlog db init`
- `python -m uBlog db migrate`
- `python -m uBlog db upgrade`

`import sqlalchemy_utils` was added to script.py.mako to allow the password type to be used.

Initial pages
-------------

- Make a new account.
  You will become Überadmin (userid 1). 
- Make an index page (pageid 1).
- Make a Terms & Conditions page (/terms) 



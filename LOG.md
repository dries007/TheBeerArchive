Captain's Log
=============

This file is meant as tutorial-esque log.

This file tries to be platform indepentant.

Docker & Docker Compose
-----------------------

- Install Docker & Docker-Compose.
- Create [docker-compose.yml](docker-compose.yml)
- Start with `docker-compose up`

The resulting yml file is a combination of the referenced tutorials & docs,
[3][compose tut 1] was closed to what's needed for this project, but uses the old v1 syntax.
So I consulted the official documentation [1][compose overview] & [2][compose file].
The second tutorial's yml file ([4][compose tut 2]) was used as a starting point for the v2 syntax.

The configuration files, run commands, file locations, ... are based on the default 
configuration / readme for the different images. The debug start for Flask is from [5][flask quickstart]

The 'app' image is a bit of a cheat. To make debugging easy, I set flask to run directly instead of
via uwsgi. This allows for on-the-fly python edits *if* the container's files are also updated live.
To do this I mount the app directory where it would nomaly have been copied on build of 'app'.
Now the only thing that require a relaunch (and thus rebuild) of the 'app' container are dependency or
configuration changed.

**Usefull later on:**
Excecute commands inside an already running docker container:

- Get a list of running docker instances: `docker ps`
- Attach to the container: `docker exec -it <name> bash`

Now you are root in the container.

Used images & README links:
- Database: [postgres][docker postgres]
- Webserver: [nginx][docker nginx]
- Python: [python:onbuild][docker python]

References: [1][compose overview] [2][compose file] [3][compose tut 1] [4][compose tut 2] [5][flask quickstart]

**Note for windows:** 

Nginx
-----

- The required directory `conf/nginx` should have been created after first launch of the containers.
- Remove `conf/nginx/default.conf`, if it exists.
- Create [conf/nginx/app.conf](conf/nginx/app.conf)
- Reload nginx config: Run `service nginx reload` inside container 'nginx'.

The default nginx config file was modified to work with the volume path from the python image.

Refereces: [1][nginx docs] (in particular [2][nginx docs core])

Sources
-------

List of source references (in the raw text).
Github will link the annotations in the text above.

[compose overview]: https://docs.docker.com/compose/overview/
[compose file]: https://docs.docker.com/compose/compose-file/#/version-2
[compose tut 1]: http://containertutorials.com/docker-compose/nginx-flask-postgresql.html
[compose tut 2]: http://nickjanetakis.com/blog/dockerize-a-flask-celery-and-redis-application-with-docker-compose
[flask quickstart]: http://flask.pocoo.org/docs/0.11/quickstart/

[docker postgres]: https://hub.docker.com/_/postgres/
[docker nginx]: https://hub.docker.com/_/nginx/
[docker python]: https://hub.docker.com/_/nginx/

[nginx docs]: http://nginx.org/en/docs/
[nginx docs core]: http://nginx.org/en/docs/http/ngx_http_core_module.html

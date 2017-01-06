Captain's Log
=============

This document is meant as a loose guide on how to set up a fork of this software.
It will take some minor adjustments to fully match your setup, but this and some Google'ing should get you there. 

Chapter 0: Introduction
-----------------------

I'm assuming a Linux environment. If you are developing on Windows, I suggest getting a small VPS to use as a playground.
You can develop on Windows and deploy and debug on there, it will save you a load of pain with Docker and File permissions. 
(NTFS won't be your friend in this story)

Command prefixes:
- `#` Root user on the host machine. (This is usually in the run environment.)
- `$` Normal user on the host machine, in virtual environment. (This is always in development environment.)
- `'name'>` Inside a docker interactive mode, with `'name'` specifying which container. (See §2.1 Commands to remember)

### Used software/technologies

- Backend structure
    - Docker                (Containerize)
        - Nginx             (Static files + front end + HTTPS)
        - Certbot           (Renews Let's Encrypt HTTPS cert)
        - PostgreSQL        (Database)
        - Flask             (Python 3 web framework)
            - Jinja2        (Template language)
            - SQLAlchemy    (Database models)
            - ....
- Web frontend
    - Gravatar          (Universal User avatars)
    - Markdown          (User friendly markup language)
    - Bootstrap 4.0 α5  (HTML, CSS, and JS framework, includes jQuery)
    - Font Awesome      (Icon font)
    - emojify.js        (Browser side emoji rendering)
    - cdnjs             (Content Delivery Framework for all JS & CSS frameworks)
    - SimpleMDE         (In browser WYSIWYG markdown editor)
    
For a full list of Python packages, see the [requirements.txt](app/requirements.txt) file.
There are way too many Flask plugins to list them all here.

### Acknowledgments

Most sources will be listed where appropriate, along side links to the documentation used.
But some sources are more equal than others, and so deserve a special extra thanks:
 
- [Richard Campen](https://campen.co/):
    My friend who got me using Python and Flask, and he recommended me: 
- [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world):
    A sometimes outdated but still really helpful tutorial. This was the stepping stone for this app.
- [The Bash Hackers Wiki](http://wiki.bash-hackers.org/start)
    For making the custom certbot script possible.

Chapter 1: Software installations
---------------------------------

- Install all the required software:
    - Dev environment
        - Git
        - Pycharm (see note below)
        - Python 3, with pip and buildtools
    - Run environment
        - Git
        - Docker
            - Engine: https://docs.docker.com/engine/installation/
            - Compose: https://docs.docker.com/compose/install/
- Fork and clone this repo in a work folder. (Both dev and run.)
    All commands are now issues from here, unless otherwise noted.
- Create a clean python virtual environment.
    Do not inherit global packages!
- Open the repo in Pycharm
    - You can dismiss the "Dockerfile detection" event.
        We won't be using Pycharm's docker integration, it appears to be buggy.
    - Do enable the version control integration, if asked. (Click 'add VCS root')
    - Mark the following directories:
        - app/migrations        -> Exclude
        - app/venv              -> Exclude
        - app                   -> Sources Root
        - app/uBlog/templates   -> Templates
    - Via Settings -> Project -> Python interpreter, use the virtual environment.
        This may require a pycharm restart.
    - Setup autodeploy (Optional, rec)
        - Tools -> Deployment -> Configuration...
        - Add a server and fill out the login details (For ssh used sftp)
            Under Root path, set something the user has full access too. eg `/home/server`
        - 'Mappings' tab: Add the deployment path.
            (I recommend something under `/home/user/` while developing. Less permission issues that way.)
        - 'Excluded Paths':
            - Exclude the 'Local Path' `/venv/`
        - Enable 'Automatic Upload' and open the 'Browse Remote Host' tab (Tools -> Deployment)
        - Do the initial upload.
            - Select the root folder in the Project tab (left)
            - Via Tools -> Deployment -> Upload to ...
            - SSH into the server, `cd` into the folder.
              **Any command for the run environment are supposed to be run here.** 
        

**All commands issues on the dev environment are assumed as being executed in the root folder of the git clone.
With the virtual environment activated!**

- Check to make sure you didn't import any global packages.
    `$ pip freeze` should output nothing.
- Install the required packages.
    `$ pip install -r app/requirements.txt`

It is important this file it kept up to date, because it gets read by our docker container to know what to install.
If you add a package, make sure you update the file. `$ pip freeze > app/requirements.txt`. 
If you do this, know you'll have to restart (rebuild actually) the docker image!

**Note about LetsEncrypt**: You'll need a domain tied to the IP of your run environment.
If you, like me at home, can't reach your own external IP from inside the network, (Thanks Telenet...)
you can add the domain to your hosts file so that you can use the actual full domain to test your site.
This will make sure that you'll get the green lock when your browser accepts the certificate.

If you want a domain name, I recommend Versio. They don't have all of the TDL's, but they are super cheap.
If you do want to use them, I have a referral link [here](https://www.versio.eu/?pa=19390geoxr) ;-).

**Note on Pycharm**
If you can, get the professional edition. 
It has things like auto-upload on save, which make debugging on a VPS a whole lot easier.
[You can request a free license as a student, or for open source projects.](https://www.jetbrains.com/pycharm/buy/#edition=discounts)

Chapter 2: Docker
-----------------

We are using docker to containerize all of our software.
This makes deploying and scaling easy if its ever required.
While you don't need to do this, I'm assuming you are.

If you are running windows: Welcome to your worst nightmare; File permissions.

**Run environment assumed.**

Make sure the Docker service is running.
`# docker ps` shows the list of running docker instances.
    
Have a look in the [docker-compose.yml](/docker-compose.yml) file.
The `Fixme` notes indicate where you should look and see if settings are appropriate for your environment.

The reason why there are so many host->container volumes instead of plain named volumes is for easier debug access.
*Flask supports live code updating*, and it detects changes though the mounting barrier of docker.
If this wasn't the case, you would have to rebuild and restart the entire composition for every single change made.
It also helps you not getting blocked by LetsEncrypt for going over the 5 certs/domain/week limit.

You will need to adapt the `settings.env` file and make a `passwords.env` file to provide the required configuration.

I highly recommend using `tmux` to split your terminal so you can have one running the docker-compose on top.
And have one shell ready to jump into any running container below. 
(Scrolling up in tmux is done with 'Control-b' + '['. This is called copy mode. Hit 'q' to exit it.)

If something errors and not all of the containers are started, use `# docker ps` to see what all is running.
Then, with the IDs listed here, you can stop any that did start: `# docker stop <id [more ids ...]>`.

The container ids will be a hexadecimal string, the names something like `thebeerarchive_app_1`.
I'll be referring to the containers by there names inside the `docker-compose.xml` file.

### Commands to remember

**Run environment assumed.**

- To build everything: `# docker-compose build`
- To run everything: `# docker-compose up`
- Your new 2 best friends: 
    - Build and start all containers: `# docker-compose build && docker-compose up`
    - Jump into a running container with a shell: `# docker exec -it <container name> bash`
- End all the containers by Control-Cing in the `docker-compose` terminal.
- End an interactive session by `exit` (or Control-D, for EndOfFile).


Chapter 2: A virgin start
--------------------------

The fist start requires all the container images to be downloaded, and the custom ones to be build.
This 

- Start all containers.
    This will take a while the first time.
    Every container's output stream will get a prefix in a different color.
- If you browse to your domain now, should give you a `sqlalchemy.exc.ProgrammingError` error page.
    Do this, to verify that everything started up correctly.
    - If you have no connection at all, look at `nginx`'s output.
    - The HTTPS should be valid, if not, restart all containers.
        If the HTTPS still isn't valid, look at `certbot`'s output.
        It may indicate that it can't reach your server.
        Port forwarding or firewall rules are a good first guess if something is wrong. 
- Try and initialize the database with `app> python -m uBlog db upgrade`.
    The result should be something along these lines:
    ```
    INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    INFO  [alembic.runtime.migration] Will assume transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade  -> 4701d5186146, The base revision. Manually tweaked. (user.password kwarg 'length' removed, user.json kwarg 'astext' removed)
    ```
    If not, look at the output of the containers:
    - Did the `db` container say this anywhere? `PostgreSQL init process complete; ready for start up.`
    - Is `db` complaining about file permissions being wrong?
- Open the domain again. You should get a 404.
- Register an account. The fist account will become the Überadmin.
    No verification email will be send.
    You will be redirected to create a first page, which will always the the root page.

Chapter 3: Using the website 
----------------------------

You should be on the 'Edit New Page'-page right now.

- Give you index page a title eg `Home`. This the name by which they will appear in the menu.
- The page name eg `index`, is the URL of the page. The has to be unique and alphanumerical and underscore only.
- After you make a basic page, you'll be redirected to `/admin`.
- You should probably make yourself a brewer, but it's not required.
- Make a new page with name `/terms`, it is linked to in the footer.

### Pages

Every page has a name, a title and content.
The name is the page's URL and must thus be unique and allows word characters (`[A-z_]`) only.
A page does not have to appear in the top menu, if if you set it to do so, it will be sorted based on ID.

### Beers

New beers can be made by all brewers. Brewers can only edit there own beer pages, and can only post to there own beers.
Every beer needs a unique name, but it can contain spaces and special characters since the URL is based on the ID.

Unlisted beers appear only for other brewers. This allows posts to be made and saved over a period of time, but the
published date will be the time of first creation.

A beer or post can be edited without notice for 10 minutes after its first saved.
After that it will show a "Last edited some time ago." marker.

#### Posts

A post is an appendage to a beer page, meant to provide updates.

### Profiles

Your own profile page shows all information, use the public link to view your profile like someone else would see it.
You can show or hide your email address, and globally disable emoji rendering for your user.

### Admins

The admin dashboard has a list of all pages, users and beers.
User permissions can be edited here.
**Be careful who you make admin!** Admins can appoint other admins, and can also demote other admins!
(Userid 1 is an exception. They can never be demoted.)

An admin can edit all pages and beers & posts. If an edit (or new) button is orange, it indicated that you are editing
a beer or post belonging to someone else. Admins can only erase user's bio, not edit it.

### Markdown quirks

- It is assumed that whomever writes the content has a basic understanding of Markdown and HTML.
- You can't use all HTML elements. No content that could be considered unsafe, such as styles and scripts.
- There may also be differences between SimpleMDE (the content editor) and Python Markdown.
- All markdown rendered by Python is surrounded by a div with class 'md'; this makes jQ/CSS selecting easier.

### Special pages

You can't use these as a page urls, except for `/terms`.

- `/` (root)    Always the page with ID = 1.
- `/terms`      Linked to via the footer link and the link on the register page, should be created ASAP.
- `/login`
- `/logout`
- `/register`
- `/brews`
- `/profile`
- `/admin`

Chapter 4: How it was made 
--------------------------

This is a retrospective look at how I ended up making most of the systems.
Also contains links to relevant documentation.

### Docker & Docker-Compose

The resulting yml file is a combination of the referenced tutorials & docs,
[1][compose tut 1] was closed to what's needed for this project, but uses the old v1 syntax.
So I consulted the official documentation [2][compose overview] & [3][compose file].
The second tutorial's yml file ([4][compose tut 2]) was used as a starting point for the v2 syntax.

The configuration files, run commands, file locations, ... are based on the default 
configuration / readme for the different images. The debug start for Flask is from [5][flask quickstart]

The 'app' image is a bit of a cheat. To make debugging easy, I set flask to run directly instead of
via uwsgi. This allows for on-the-fly python edits *if* the container's files are also updated live.
To do this I mount the app directory where it would normally have been copied on build of 'app'.
Now the only thing that require a relaunch (and thus rebuild) of the 'app' container are dependency or
configuration changed.

Docker images used: 
- [db][docker postgres]     (Official PostgreSQL)
- [nginx][docker nginx]     (Official Nginx)
- [certbot][docker debian]  (Custom Debian)
- [app][docker python]      (Custom Python)

[compose overview]: https://docs.docker.com/compose/overview/
[compose file]: https://docs.docker.com/compose/compose-file/#/version-2
[compose tut 1]: http://containertutorials.com/docker-compose/nginx-flask-postgresql.html
[compose tut 2]: http://nickjanetakis.com/blog/dockerize-a-flask-celery-and-redis-application-with-docker-compose
[flask quickstart]: http://flask.pocoo.org/docs/0.11/quickstart/

[docker postgres]: https://hub.docker.com/_/postgres/
[docker nginx]: https://hub.docker.com/_/nginx/
[docker python]: https://hub.docker.com/_/nginx/
[docker debian]: https://hub.docker.com/_/debian/

### app (Nginx)

Most of the nginx configs are based on nginx configs I have used for years.
All http traffic gets rerouted to https. (As it should, now that https is basically free.)

The `/static/` block serves static files, `/.well-known/` serves files from LetsEncrypt.
Any other requests are routed to `app`. When the Flask internal server is used, it routes to port 5000.
In a production environment this should be changed to using a uwsgi socket.

If any changes are made to config and if you want to reload the configs without restarting the whole docker:
`# docker kill -s HUP $(docker ps -q -f "label=${CERT_LABEL}")` (`CERT_LABEL` is defined in `settings.env`) 

`/robots.txt` and `/favicon.ico` are served from the static folder too. Any file starting with `.ht` is blocked.

Any errors outside of `app` are routed to `/static/[404|403|50x].html`. 
They are only really used when the `app` container is down, or when the error happens inside of the `static` folder.

Because all volumes from `app` and `certbot` are mounted:
- `/etc/letsencrypt` is mapped to `./run/le`, and `/var/log` is mapped to `./run/log` via `certbot`
- `/usr/src/app` is mapped to `./app` via `app`. (`/static/` is served from here.)

References: [1][nginx docs] (and in particular [2][nginx docs core])

[nginx docs]: http://nginx.org/en/docs/
[nginx docs core]: http://nginx.org/en/docs/http/ngx_http_core_module.html

### db (PostgreSQL)

Nothing much special here, except that, I would have liked to have the data folder as a Host->Container volume.
This would have made it easier to backup, but because PostgreSQL is *very* picky about file permissions, this made
it impossible to use at all on Windows. Although I later dropped caring about Windows at all, I did start out developing
on 2 machines. A Windows 10 laptop for school and an ArchLinux desktop at home.
 
I don't recommend removing the external port binding. You are probably better off blocking the port with a firewall rule.
That way you could still SSH tunnel and connect to debug issues. (And connect the Database explorer from Pycharm!)

### certbot (LetsEncrypt)

The is a fully custom Docker image, build on top of Debian (with jessie backports).
Debian with jessie backports is fully supported by certbot: [1][certbot install].

This container also does some minor other things, like make sure the `./run/log/nginx` folder exists.

Other references: ['Official' certbot dockerfile][docker certbot]

[certbot install]: https://certbot.eff.org/#debianjessie-nginx
[docker certbot]: https://github.com/certbot/certbot/blob/master/Dockerfile

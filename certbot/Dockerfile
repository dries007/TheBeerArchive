FROM debian

RUN echo "deb http://ftp.debian.org/debian jessie-backports main" > /etc/apt/sources.list.d/jessie-backports.list
RUN apt-get update && apt-get install -y certbot -t jessie-backports

ENTRYPOINT [ "certbot" ]
FROM debian

RUN echo "deb http://ftp.debian.org/debian jessie-backports main" > /etc/apt/sources.list.d/jessie-backports.list
RUN apt-get update && apt-get install -y certbot -t jessie-backports
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

WORKDIR /root

COPY certbot_script.sh /root/
RUN chmod +x /root/certbot_script.sh

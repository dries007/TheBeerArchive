FROM debian:jessie-backports

# Only required if NOT building from jessie-backports image.
# RUN echo "deb http://ftp.debian.org/debian jessie-backports main" > /etc/apt/sources.list.d/jessie-backports.list

RUN apt-get update && apt-get install -y certbot -t jessie-backports

# To avoid issues with the custom script later
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Interactive sessions start here too
WORKDIR /root

# This does mean any changes to the script require a rebuild!
COPY certbot_script.sh /root/
RUN chmod +x /root/certbot_script.sh

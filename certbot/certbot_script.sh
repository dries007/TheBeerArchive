#!/bin/bash


# Custom script by Dries007
#
# Do make sure this runs in an actual BASH shell!
# I recommend adding "RUN rm /bin/sh && ln -s /bin/bash /bin/sh" in your Dockerfile.
#
# Makes temp cert if required, to keep nginx for crashing if there is no cert present.
# It keeps the VM alive, so no need for cron stuff.
# It also nudges the Nginx to update its config, which is why it needs access to the docker executable and socket.
# This poses a possible security risk, but since this VM should have no open ports it should be fine.
# (This is a lot more secure than having the nginx or python VM do it for sure)

# Make all commands echo and variables expand. Debug is a lot easier that way.
set -x

# Function that joins the argument array by the first argument (equ to "arg1.join(*rest_of_args)" in python)
function join_by { local d=$1; shift; printf "%s" "${@/#/$d}"; }

# Split CERT_DOMAINS by space
CERT_DOMAINS=($CERT_DOMAINS)
# All domains, seperated by ' -d ', later used as arg for certbot
ALL_DOMAINS_D=$(join_by ' -d ' "${CERT_DOMAINS[@]}")
# All domains, seperated by ',', later used as arg for openssl
ALL_DOMAINS_C=$(join_by ',' "${CERT_DOMAINS[@]}")

# Doing this here to avoid having issues if they end up not existing
mkdir -p /etc/letsencrypt/nginx/
mkdir -p /var/log/letsencrypt/
mkdir -p /var/log/nginx/

# Is a self signed cert required?
if [ ! -f /etc/letsencrypt/nginx/privkey.pem ]; then
    echo "Generating startup cert"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/letsencrypt/nginx/privkey.pem -out /etc/letsencrypt/nginx/fullchain.pem -subj "/C=BE/ST=Tmp/L=Tmp/O=Tmp/OU=Tmp/CN=${ALL_DOMAINS_C#','}"
fi

# The real job of this script
while true; do
    echo "Running certbot"
    certbot certonly -n -t --email ${CERT_EMAIL} --agree-tos --webroot -w "/etc/letsencrypt" ${ALL_DOMAINS_D#' '}
    echo "Copy certs and keys"
    cp -v /etc/letsencrypt/live/${CERT_DOMAINS[0]}/* /etc/letsencrypt/nginx/
    sleep 10s
    echo "Reloading nginx config"
    docker kill -s HUP $(docker ps -q -f "label=${CERT_LABEL}")
    echo "Sleeping for a small random time and a day"
    sleep $[ ( $RANDOM % 100 ) + 1 ]m
    sleep 1d
done

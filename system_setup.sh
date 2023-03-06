#!/usr/bin/env bash

# ----------------------------------------------------------------------
# Copyright © 2023 Hosung Kim <hk196@duke.edu>
#
# All rights reserved
# ----------------------------------------------------------------------

# ---------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------
Setup(){
    BASEDIR=$(pwd)

    # Install Docker
    if [ -x "$(command -v docker)" ]; then
        echo "Docker installed at $(command -v docker)"
    else
        echo "Install docker"
        # command
        ./setup_scripts/setup_docker.sh
    fi

    # Pre-setup for nginx webserver
    # Step 1. Check for hostname
    echo "Please input hostname.."
    read SERVER_NAME

    export SERVER_NAME=$SERVER_NAME
    source ~/.bashrc

    # Step 2. Set env variable for server_name and create conf file for nginx
    cd $BASEDIR/nginx-https/nginx/setup_conf
    envsubst < ./default.conf.template > ./default.conf

    # Start nginx webserver for certificates
    echo "Starting nginx server for SSL certificate using Let's Encrypt"
    cd $BASEDIR/nginx-https
    docker compose up -d webserver_setup

    # Start Certbot for HTTPS
    docker compose run --rm certbot_setup certonly --webroot --webroot-path /var/www/certbot/ -d $SERVER_NAME

    # After success delete the default.conf file
    rm -rf $BASEDIR/nginx-https/nginx/setup_conf/default.conf

    # Delete All running Docker Container
    docker compose down
}

Django(){
    # Go to conf files
    cd $BASEDIR/nginx-https/nginx/conf
    envsubst '${SERVER_NAME}' < ./default.conf.template > ./default.conf
    docker compose up -d webserver_deployment
    docker compose up -d certbot_deployment

    echo "Create Static Media Server for Books"
    sudo mkdir /srv/media/books
}

Jenkins(){
    # Go to conf files
    cd $BASEDIR/nginx-https/nginx/conf
    envsubst '${SERVER_NAME}' < ./jenkins.conf.template > ./default.conf
    docker compose up -d webserver_deployment
    docker compose up -d certbot_deployment
}

Database(){
    # Go to conf files
    cd $BASEDIR/nginx-https/nginx/conf
    envsubst '${SERVER_NAME}' < ./database.conf.template > ./default.conf
    sudo docker compose up -d dbserver_deployment
    docker compose up -d certbot_deployment
}

Help()
{
   # Display Help
   echo "Script to add Setup System for Django/Jenkins/Database"
   echo
   echo "Syntax: ./system_setup.sh [-h] [-t django|jenkins|database]"
   echo "options:"
   echo "h     Print this Help."
   echo "t     Select type of system setup [django|jenkins|database]"
   echo
}

# ---------------------------------------------------------------------
# Main body of script starts here
# ---------------------------------------------------------------------
while getopts ":ht:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) # Enter Users
        userargs=${OPTARG}
        if [ $userargs == "django" ]; then
            Setup;
            Django
        elif [ $userargs == "jenkins" ]; then
            Setup;
            Jenkins
        elif [ $userargs == "database" ]; then
            Setup;
            Database
        else
            Help
        fi
	 exit;;
      \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

Help
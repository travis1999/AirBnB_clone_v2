#!/usr/bin/env bash
#detup ci/cd environment


#install nginx
echo "Installing nginx"
sudo apt-get update
sudo apt-get install nginx -y

#folders
folders=("/data/web_static"
         "/data/web_static/releases"
         "/data/web_static/shared"
         "/data/web_static/releases/test/")

for str in "${folders[@]}"; do
    echo "creating folder structure $str"
    mkdir -p $str
done

#create fake index.html
echo "creating index.html"

touch /data/web_static/releases/test/index.html
echo "Hello World" > /data/web_static/releases/test/index.html

#create symlink to current test release
echo "creating symlink to current test release"

ln -s /data/web_static/releases/test /data/web_static/current

#give ownership of /data/ to ubuntu
echo "giving ownership of /data/ to ubuntu"
chown -R ubuntu:ubuntu /data/
chgrp -R ubuntu /data/

# Update the Nginx configuration to serve the content 
# of /data/web_static/current/ to https://travortech.tech/hbnb_static
printf %s "server {
    listen 80 default_server;
    listen [::]:80 default_server;
    add_header X-Served-By $HOSTNAME;
    root   /var/www/html;
    index  index.html index.htm;
    
    location /hbnb_static {
        alias /data/web_static/current;
        index index.html index.htm;
    }
    error_page 404 /404.html;
    location /404 {
      root /var/www/html;
      internal;
    }
}" > /etc/nginx/sites-available/default


service nginx restart


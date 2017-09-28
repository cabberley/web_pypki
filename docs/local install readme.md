# Local installation

Note: this installation guide assumes that: 
- you will use a dedicated user named pki for PKI related activities and files
- the pki user is available on your system and has a home directory in /home/pki
- by default our configuration assumes that you have created the PKI structure in the /pkiroot folder

The pkiweb interface allows you to configure the following settings by using environment variables:
- PYPKI_PKIROOT defaults to: /pkiroot
- PYPKI_OPENSSLCONFIGFILE defaults to: /pkiroot/openssl.cnf
- PYPKI_CANAMES defaults to: 'RootCA', 'IntermCA'
- PYPKI_DEBUG default to: False

## Step 1: Prepare OS

### RedHat based systems
```bash
yum update -y
yum install -y epel-release 
yum install -y python python-devel python-pip python-webpy git gcc nginx uwsgi
``` 

## Prepare pkiweb configuration 

### OpenSSL configuration file 

- The pypki_canames variable mentioned above needs to match the names of your CA sections in the openssl.cnf file
- Add the following options in your openssl.cnf file for each CA:

```bash
# Section for pyPKI  
use_smartcard = False  
smartcard_slot = 0:2  
chain_file = $dir/ca_chain.crt 
```

- Ensure you generated the ca chain file before using pyPKI.
- As of version 1.1 pypki will copy the commom name value in the SAN field of the generated certificates to avoid issues like "NET::ERR_CERT_COMMON_NAME_INVALID" (missing_subjectAltName)". In order to enable this please add the following line to your interim CA section inside the openssl.cnf file:

```bash
copy_extensions = copy
```

### Register users 
Users with access to pyPKI are stored in pypki/core/users.py. You can edit this file to reflect the users and passwords which you would like to grant access. The default user and password is admin:admin. 

### Generate new server certificate 
pyPKI uses SSL to secure communications between the browser and the application. You should generate a certfiicate for the pkiweb
application and copy the generated certificates to /pkiroot/ssl/pypki.crt and /pkiroot/ssl/pypki.key.

```bash
openssl req -newkey rsa:2048 -keyout /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.key -nodes -config openssl.cnf -out /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.csr 
openssl ca -config openssl.cnf -name IntermCA -out /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.crt -infiles /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.csr

cp /pkiroot/IntermCA/ca.db.certs/{pkiweb.test.local.crt, pkiweb.test.local.key} /pkiroot/ssl
```

## Install pyPKI

### Install
Clone GIT into directory:

```bash
cd /home/pki
git clone https://dverslegers@bitbucket.org/dverslegers/pypki.git
```

> Make sure the git utility is available on the system before attempting to use this command. 

Install pyPKI and it’s dependencies: 
```bash
cd /home/pki
pip install ./pypki
```

> Make sure pip is available on your system. If this is not yet the case you can add it by issuing sudo apt-get install python-pip

### Put static files in place
```bash
mkdir -p /usr/share/nginx/html/pkiweb
cp -R /home/pki/pypki/static /usr/share/nginx/html/pkiweb
```
### wsgi configuration
```bash
mkdir -p /etc/uwsgi/sites

vi /etc/uwsgi/pkiweb.demo.local

[uwsgi]
# -------------
# Settings:
# key = value
# Comments >> #
# -------------

# socket = [addr:port]
socket = 127.0.0.1:8080

# Base application directory
# chdir = /full/path
chdir  = /home/pki/pypki

# WSGI module and callable
# module = [wsgi_module_name]:[application_callable_name]
module = pypki.web.pki_web:app

# master = [master process (true of false)]
master = true

# processes = [number of processes]
processes = 5
```

```bash
/usr/bin/uwsgi --emperor /etc/uwsgi/sites
```

> If you want to test your uwsgi configuration directly you can run the above command with the --http-socket flag
uwsgi --http-socket :8000 --emperor /etc/uwsgi/sites

### nginx configuration
```bash
vi /etc/nginx/nginx.conf

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for" "$http_host"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;
    gzip              on;
    gzip_http_version 1.0;
    gzip_proxied      any;
    gzip_min_length   500;
    gzip_disable      "MSIE [1-6]\.";
    gzip_types        text/plain text/xml text/css
                      text/comma-separated-values
                      text/javascript
                      application/x-javascript
                      application/atom+xml;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    # Configuration containing list of application servers
    upstream uwsgicluster {

       server 127.0.0.1:8080;

    }

    server {
        listen 0.0.0.0:8443 ssl default_server;
        ssl_certificate /pkiroot/ssl/pypki.crt;
        ssl_certificate_key /pkiroot/ssl/pypki.key;

        ########################################################################
        # from https://cipherli.st/                                            #
        # and https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html #
        ########################################################################

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
        ssl_ecdh_curve secp384r1;
        ssl_session_cache shared:SSL:10m;
        ssl_session_tickets off;
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 8.8.8.8 8.8.4.4 valid=300s;
        resolver_timeout 5s;
        # Disable preloading HSTS for now.  You can use the commented out header line that includes
        # the "preload" directive if you understand the implications.
        add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
        add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;

        ##################################
        # END https://cipherli.st/ BLOCK #
        ##################################

        access_log            /var/log/nginx/pypki.access.log main;
        error_log            /var/log/nginx/pypki.error.log;

        location / {
          include            uwsgi_params;
          uwsgi_pass         uwsgicluster;

          proxy_redirect     off;
          proxy_set_header   Host $host;
          proxy_set_header   X-Real-IP $remote_addr;
          proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header   X-Forwarded-Host $server_name;
        }

        location /static {
          root /usr/share/nginx/html/pypki;
	  autoindex off;
        }
	}
}
```

### Optional: Enabling smartcard fo CA private key storage 
Follow the instructions available at my blog on how to enable a yubikey with PIV applet to store your Certificate Authority private key. Once the required modifications have been performed it suffices to change the user smartcard and smartcard slot options in openssl.cnf for the relevant CA(’s): 

```bash
# Section for pyPKI  
use_smartcard = True  
smartcard_slot = 0:2 
```

Make sure to refer to the correct smartcard and slot when specifying the smartcard slot parameter.
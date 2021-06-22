# pyPKI Installation & Configuration 

## Introduction

This readme provides the required installation and configuration instructions to use the pypki module and the simple web
interface we wrote for it. If you want you can also import the pypki.core package directly in your own project to provide a
python interface to common openssl actions.

The pyPKI web interface can be installed manually on any OS or you can initiate a docker container which runs the application
and provides access to it through uwsgi and nginx. In both cases you must first follow the instruction in the *"pki setup"*
document to initialize the pkiroot and openssl configuration which you want the pki web application to serve.
- for **docker**: prepare a volume based on the pki setup instructions
- for **local install**: prepare the /pkiroot directory based on the pki setup instructions

You can find the installation or docker instructions in the *local install* and *docker* readme files.

The pypki module assumes you have a openssl based PKI infrastructure setup according to some conventions such as
certain attributes being available in the openssl.cnf file. It is adviced to follow the instructions provided
in the *"pki setup"* doc.

Another option to use the pypki and pkiweb distribution is by using our docker image or docker file to generate your
own.


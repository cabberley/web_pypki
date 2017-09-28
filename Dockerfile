FROM centos:latest
MAINTAINER dv@arkeon.eu


# Install required OS packages
RUN echo "Installing OS packages"
RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y \
python \
python-devel \
python-pip \
python-webpy \
git \
gcc \
nginx \
uwsgi \
uwsgi-plugin-python \
supervisor \
net-tools

# Create user
RUN useradd -ms /bin/bash pki

# Obtain and install pypki
RUN echo "Installing pypki"
RUN cd /home/pki && git clone -b release/Release_1.1 https://dverslegers@bitbucket.org/dverslegers/pypki.git
RUN cd /home/pki && pip install ./pypki
RUN echo "Copying static files"
RUN mkdir -p /usr/share/nginx/html/pkiweb
RUN cp -R /home/pki/pypki/static /usr/share/nginx/html/pkiweb
RUN echo "Setting up wsgi"
RUN mkdir -p /etc/uwsgi/sites
ADD sysfiles/pypki.wsgi.ini /etc/uwsgi/sites
ADD sysfiles/nginx.conf /etc/nginx

ADD sysfiles/printenv.py /tmp

# Expose services and enable
EXPOSE 9443
ADD sysfiles/supervisord.conf /etc/supervisord.conf
#CMD /usr/sbin/uwsgi --emperor /etc/uwsgi/sites & \
#    /bin/bash
#CMD /usr/sbin/uwsgi --emperor /etc/uwsgi/sites & \
#    /usr/sbin/nginx & \
#    /bin/bash
#CMD /usr/bin/supervisord -c /etc/supervisord.conf
CMD /bin/bash
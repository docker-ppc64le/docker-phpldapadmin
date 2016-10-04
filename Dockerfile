FROM ppc64le/php:7.1-fpm

MAINTAINER Jacob Zak <jagu.sayan@gmail.com>

# phpLDAPadmin version
ENV PHPLDAPADMIN_VERSION 1.2.3
ENV PHPLDAPADMIN_SHA1 669fca66c75e24137e106fdd02e3832f81146e23

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
     ca-certificates \
     nginx-light \
     curl \
     vim \
     libldb-dev \
     libldap2-dev \
 && ln -s $(find / -name "libldap.so") /usr/lib/libldap.so \
 && ln -s $(find / -name "liblber.so") /usr/lib/liblber.so \
 && docker-php-ext-install ldap gettext \
 && curl -o /tmp/phpldapadmin.tgz -SL https://downloads.sourceforge.net/project/phpldapadmin/phpldapadmin-php5/${PHPLDAPADMIN_VERSION}/phpldapadmin-${PHPLDAPADMIN_VERSION}.tgz \
 && echo "$PHPLDAPADMIN_SHA1 /tmp/phpldapadmin.tgz" | sha1sum -c - \
 && mkdir -p /usr/share/phpldapadmin \
 && tar -xzf /tmp/phpldapadmin.tgz --strip 1 -C /usr/share/phpldapadmin \
 && apt-get autoremove --purge -y libldb-dev libldap2-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /tmp/*

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
 && ln -sf /dev/stderr /var/log/nginx/error.log \
 && rm -rf /var/www \
 && ln -sf /usr/share/phpldapadmin /var/www \
 && rm /usr/local/etc/php-fpm.d/zz-docker.conf \
 && mv /var/www/config/config.php.example /var/www/config/config.php

# See https://bugs.launchpad.net/ubuntu/+source/phpldapadmin/+bug/1241425
RUN sed -i -e 's/password_hash/password_ldap_hash/g' /var/www/lib/*.php /var/www/config/*.php

COPY conf/nginx.conf /etc/nginx
COPY conf/default.conf /etc/nginx/conf.d/
COPY conf/www.conf /usr/local/etc/php-fpm.d/
COPY conf/php.ini /usr/local/etc/php/

COPY bootstrap.sh /
COPY run.sh /

EXPOSE 80

ENTRYPOINT ["/bootstrap.sh"]
CMD ["/run.sh"]

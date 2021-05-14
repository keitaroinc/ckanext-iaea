FROM openknowledge/ckan-base:2.8

MAINTAINER Open Knowledge International <info@okfn.org>

ENV APP_DIR=/srv/app
ENV SRC_EXTENSIONS_DIR=/srv/app/src_extensions
ENV IAEA_EXTENSION_DIR=/srv/app/src_extensions/ckanext-iaea

# Set timezone
ARG TZ
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone

# Install packages needed by the dev requirements
RUN apk add --no-cache libffi-dev

# Install CKAN dev requirements
RUN pip install --no-binary :all: -r https://raw.githubusercontent.com/ckan/ckan/${GIT_BRANCH}/dev-requirements.txt


# Install CKAN extensions
RUN pip install -e git+https://github.com/ckan/ckanext-pdfview.git#egg=ckanext-pdfview && \
    pip install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages

# Create folder for local extensions sources
RUN mkdir $SRC_EXTENSIONS_DIR
RUN mkdir $IAEA_EXTENSION_DIR

COPY setup/start_ckan_development.sh ${APP_DIR}


CMD ["/srv/app/start_ckan_development.sh"]

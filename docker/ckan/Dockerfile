FROM ckan/ckan-base:2.9

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
#RUN pip install --no-binary :all: -r https://raw.githubusercontent.com/ckan/ckan/${GIT_BRANCH}/dev-requirements.txt
RUN pip install flask-debugtoolbar


# Install CKAN extensions
RUN pip install -e "git+https://github.com/ckan/ckanext-pdfview.git@0.0.7#egg=ckanext-pdfview" && \
    pip install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages

# Install ckanext-harvest
RUN pip install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest
RUN pip install -r ./src/ckanext-harvest/requirements.txt

# ckanext-autz-service
RUN pip install -e git+https://github.com/datopian/ckanext-authz-service.git#egg=ckanext-authz-service && \
    pip install -r ./src/ckanext-authz-service/requirements.py2.txt

# ckanext-sentry
RUN pip install -e git+https://github.com/okfn/ckanext-sentry.git#egg=ckanext-sentry && \
    pip install -r ./src/ckanext-sentry/requirements.txt

# ckanext-basiccharts
RUN pip install -e git+https://github.com/ckan/ckanext-basiccharts.git#egg=ckanext-basiccharts

# ckanext-visualize
RUN pip install -e git+https://github.com/datopian/ckanext-visualize.git#egg=ckanext-visualize && \
    pip install -r ./src/ckanext-visualize/requirements.txt

# ckanext-geoview
RUN pip install -e "git+https://github.com/keitaroinc/ckanext-geoview.git@iaea#egg=ckanext-geoview"

RUN pip install -e "git+https://github.com/ckan/ckanext-pages.git@v0.3.7#egg=ckanext-pages" && \
    pip install -r ./src/ckanext-pages/requirements.txt

# ckanext-dataexplorer-react
RUN pip install -e "git+https://github.com/keitaroinc/ckanext-dataexplorer-react.git@iaea#egg=ckanext-dataexplorer-react" && \
    pip install -r ./src/ckanext-dataexplorer-react/requirements.txt

# ckanext-dcat
RUN pip install -e "git+https://github.com/ckan/ckanext-dcat.git@v1.3.0#egg=ckanext-dcat" && \
    pip install -r ./src/ckanext-dcat/requirements-py2.txt

# ckanext-report
RUN pip install -e "git+https://github.com/ckan/ckanext-report.git#egg=ckanext-report" && \
    pip install -r ./src/ckanext-report/requirements.txt

# ckanext-archiver
RUN pip install -e "git+http://github.com/ckan/ckanext-archiver.git#egg=ckanext-archiver" && \
    pip install -r ./src/ckanext-archiver/requirements.txt

# ckanext-qa
RUN pip install -e "git+http://github.com/keitaroinc/ckanext-qa.git@qa-iaea#egg=ckanext-qa" && \
    pip install -r ./src/ckanext-qa/requirements.txt

# ckanext-validation
RUN pip install -e "git+https://github.com/keitaroinc/ckanext-validation.git@ckan-2.8.2#egg=ckanext-validation" && \
    pip install -r ./src/ckanext-validation/requirements.txt

# ckanext-scheming
RUN pip install --exists-action=w -e "git+https://github.com/keitaroinc/ckanext-scheming.git@ckan-2.8#egg=ckanext-scheming"

# Create folder for local extensions sources
RUN mkdir $SRC_EXTENSIONS_DIR
RUN mkdir $IAEA_EXTENSION_DIR

COPY setup/start_ckan_development.sh ${APP_DIR}
COPY setup/start_ckan_worker.sh ${APP_DIR}


CMD ["/srv/app/start_ckan_development.sh"]

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

# # Install CKAN dev requirements
# #RUN pip install --no-binary :all: -r https://raw.githubusercontent.com/ckan/ckan/${GIT_BRANCH}/dev-requirements.txt
RUN pip install flask-debugtoolbar


# Install CKAN extensions

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-xloader@rewrite-site-url#egg=ckanext-xloader" && \
    pip install -r "./src/ckanext-xloader/requirements.txt"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-validation@iaea-2.9#egg=ckanext-validation" && \
    pip install -r "./src/ckanext-validation/requirements.txt"

RUN pip install -e "git+https://github.com/ckan/ckanext-report#egg=ckanext-report" && \
    pip install -r "./src/ckanext-report/requirements.txt"

RUN pip install -e "git+https://github.com/ckan/ckanext-archiver#egg=ckanext-archiver" && \
    sed -i '/ckanext-report/d' "./src/ckanext-archiver/requirements.txt" && \
    pip install -r "./src/ckanext-archiver/requirements.txt"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-qa@qa-iaea#egg=ckanext-qa" && \
    pip install -r "./src/ckanext-qa/requirements.txt"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-harvest@montreal-fix#egg=ckanext-harvest" && \
    pip install -r "./src/ckanext-harvest/pip-requirements.txt"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-basiccharts@iaea#egg=ckanext-basiccharts"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-visualize#egg=ckanext-visualize" && \
    pip install -r "./src/ckanext-visualize/requirements.txt"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-pdfview#egg=ckanext-pdfview"

RUN pip install -e "git+https://github.com/ckan/ckanext-geoview@v0.1.0#egg=ckanext-geoview"

RUN pip install -e "git+https://github.com/ckan/ckanext-pages@v0.5.2#egg=ckanext-pages" && \
    pip install -r "./src/ckanext-pages/requirements.txt"

RUN pip install -e "git+https://github.com/datopian/ckanext-dataexplorer-react#egg=ckanext-dataexplorer-react" && \
    pip install -r "./src/ckanext-dataexplorer-react/requirements.txt"

RUN pip install -e "git+https://github.com/ckan/ckanext-dcat@v1.5.1#egg=ckanext-dcat" && \
    pip install -r "./src/ckanext-dcat/requirements.txt"

RUN pip install -e "git+https://github.com/ckan/ckanext-scheming@release-3.0.0#egg=ckanext-scheming"

RUN pip install -e "git+https://github.com/keitaroinc/ckanext-saml2auth@ckan-2.9-iaea#egg=ckanext-saml2auth"


# Create folder for local extensions sources
RUN mkdir $SRC_EXTENSIONS_DIR
RUN mkdir $IAEA_EXTENSION_DIR

COPY setup/start_ckan_development.sh ${APP_DIR}
COPY setup/start_ckan_worker.sh ${APP_DIR}
COPY ckan.ini ${APP_DIR}


CMD ["/srv/app/start_ckan_development.sh"]

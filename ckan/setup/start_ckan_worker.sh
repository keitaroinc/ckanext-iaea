#!/bin/bash

# Install any local extensions in the src_extensions volume
echo "Looking for local extensions to install..."
echo "Extension dir contents:"
ls -la $SRC_EXTENSIONS_DIR
for i in $SRC_EXTENSIONS_DIR/*
do
    if [ -d $i ];
    then

        if [ -f $i/pip-requirements.txt ];
        then
            pip install -r $i/pip-requirements.txt
            echo "Found requirements file in $i"
        fi
        if [ -f $i/requirements.txt ];
        then
            pip install -r $i/requirements.txt
            echo "Found requirements file in $i"
        fi
        if [ -f $i/dev-requirements.txt ];
        then
            pip install -r $i/dev-requirements.txt
            echo "Found dev-requirements file in $i"
        fi
        if [ -f $i/setup.py ];
        then
            cd $i
            python $i/setup.py develop
            echo "Found setup.py file in $i"
            cd $APP_DIR
        fi

        # Point `use` in test.ini to location of `test-core.ini`
        if [ -f $i/test.ini ];
        then
            echo "Updating \`test.ini\` reference to \`test-core.ini\` for plugin $i"
            paster --plugin=ckan config-tool $i/test.ini "use = config:../../src/ckan/test-core.ini"
        fi
    fi
done


# Set debug to true
echo "Enabling debug mode"
paster --plugin=ckan config-tool $CKAN_INI -s DEFAULT "debug = true"

# Update the plugins setting in the ini file with the values defined in the env var
echo "Loading the following plugins: $CKAN__PLUGINS"
paster --plugin=ckan config-tool $CKAN_INI "ckan.plugins = $CKAN__PLUGINS"

paster --plugin=ckan config-tool $CKAN_INI "ckan.site_url = $CKAN_SITE_URL"

echo "Running worker: $1"
paster --plugin=ckan jobs worker "$1" -c "$CKAN_INI"
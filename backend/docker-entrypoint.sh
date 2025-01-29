#! /usr/bin/bash

echo "Starting init script"

# Check if the media path exists and has write permissions
if [ ! -z "$MEDIA_ROOT" ]; then
    echo "MEDIA_ROOT is set to $MEDIA_ROOT"

    if [ ! -d "$MEDIA_ROOT" ]; then
        echo "Creating MEDIA_ROOT directory $MEDIA_ROOT"

        # Check if running as root
        if [ "$(id -u)" -eq 0 ]; then
            # Running as root
            mkdir -p ${MEDIA_ROOT}
            chown -R ${USER}:${USER} ${MEDIA_ROOT}
        else
            # Running as non-root user
            sudo mkdir -p ${MEDIA_ROOT}
            sudo chown -R ${USER}:${USER} ${MEDIA_ROOT}
        fi
    fi

     if [ ! -w "$MEDIA_ROOT" ]; then
        echo "Media path $MEDIA_ROOT is not writable"
        exit 1
    fi
fi

./manage.py init_setup

echo "Starting ropon wagtail server"
./manage.py runserver 0.0.0.0:${DJANGO_PORT:-8000}

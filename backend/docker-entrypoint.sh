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


# Initialize setup
./manage.py init_setup

# Check if gunicorn is available in the environment
if command -v gunicorn &> /dev/null; then
    echo "Starting ropon wagtail server with gunicorn"
    
    # Check if we have a custom gunicorn config file
    if [ -f "gunicorn_conf.py" ]; then
        echo "Using gunicorn configuration from gunicorn_conf.py"
        exec gunicorn -c gunicorn_conf.py ropon.wsgi:application
    else
        # Use default gunicorn settings if no config file is available
        echo "Using default gunicorn configuration"
        exec gunicorn \
            --bind 0.0.0.0:${DJANGO_PORT:-8000} \
            --workers=${GUNICORN_WORKERS:-2} \
            --worker-class=gthread \
            --threads=${GUNICORN_THREADS:-2} \
            --timeout=${GUNICORN_TIMEOUT:-120} \
            ropon.wsgi:application
    fi
else
    # Fallback to Django's development server if gunicorn is not available
    echo "Gunicorn not found, starting ropon wagtail server with Django runserver"
    ./manage.py runserver 0.0.0.0:${DJANGO_PORT:-8000}
fi

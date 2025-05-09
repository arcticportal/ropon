# Initial draft Docker file that should be used to build the Docker image for the project.

# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.12-slim

# Add user that will be used in the container.
# RUN useradd wagtail

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

    
# setup user permissions with ID
# staff user has ID 1001 and staff group as ID 50 on debian 
# adm group has ID 4
ARG PID=1001
ARG PGID=1001
ARG PUSER=wagtail
ARG DOCKERGID=1000
# Set build argument for environment (defaults to production)
ARG ENVIRONMENT=prd

# Create the user with a proper home directory
RUN groupadd -g $PGID $PUSER && \
    useradd -u $PID -g $PGID -m -d /home/$PUSER $PUSER && \
    chown -R ${PUSER}:${PUSER} /home/${PUSER}

# SET docker group ID, which matches with group ID of host machine
RUN groupadd -g $DOCKERGID docker
RUN usermod -aG docker $PUSER

# Install system packages required by Wagtail and Django.
# TODO- are these all need for prod as well ?
# RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     libmariadbclient-dev \
#     libjpeg62-turbo-dev \
#     zlib1g-dev \
#     libwebp-dev \
#  && rm -rf /var/lib/apt/lists/*

# # Install the application server.
# RUN pip install "gunicorn==20.0.4"


# Set default MEDIA_ROOT if not provided
ENV MEDIA_ROOT=/srv/media

RUN mkdir -p ${MEDIA_ROOT}
RUN chown -R ${PUSER}:${PUSER} ${MEDIA_ROOT}

VOLUME ["${MEDIA_ROOT}"]


# Use /app folder as a directory where the source code is stored.
WORKDIR /app


# Set this directory to be owned by the "$PUSER=wagtail" user.
RUN chown ${PUSER}:${PUSER} /app


# Install the project requirements based on environment
COPY deploy/backend/requirements.$ENVIRONMENT.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt


# Copy the source code of the project into the container.
COPY --chown=${PUSER}:${PUSER} backend/ .

# Use user "wagtail" to run the build commands below and the server itself.
USER ${PUSER}

# Create migrations.
RUN python manage.py makemigrations


# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Port used by this container to serve HTTP.
EXPOSE 8000

# Runtime command that executes the docker-entrypoint.sh
CMD [ "./docker-entrypoint.sh"]
# Initial draft Docker file that should be used to build the Docker image for the project.

# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.12-slim-bookworm

# Add user that will be used in the container.
# RUN useradd wagtail

# Set environment variables and default MEDIA_ROOT if not provided.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    MEDIA_ROOT=/srv/media


# Install system packages required by Wagtail and Django, create user/group, set permissions, and prepare media directory in a single RUN.
ARG PID=1001
ARG PGID=1001
ARG PUSER=wagtail
ARG DOCKERGID=1000
ARG ENVIRONMENT=prd

RUN apt-get update --yes --quiet && \
    apt-get install --yes --quiet --no-install-recommends nano && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g $PGID $PUSER && \
    useradd -u $PID -g $PGID -m -d /home/$PUSER $PUSER && \
    chown -R ${PUSER}:${PUSER} /home/${PUSER} && \
    groupadd -g $DOCKERGID docker && \
    usermod -aG docker $PUSER && \
    mkdir -p ${MEDIA_ROOT} && \
    chown -R ${PUSER}:${PUSER} ${MEDIA_ROOT}

VOLUME ["${MEDIA_ROOT}"]


# Use /app folder as a directory where the source code is stored.
WORKDIR /app


# Set this directory to be owned by the "$PUSER=wagtail" user.
RUN chown ${PUSER}:${PUSER} /app


# Install the project requirements based on environment
COPY deploy/backend/requirements.$ENVIRONMENT.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm -rf requirements.txt


# Copy the source code of the project into the container.
COPY --chown=${PUSER}:${PUSER} backend/ .

# Use user "wagtail" to run the build commands below and the server itself.
USER ${PUSER}


# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Port used by this container to serve HTTP.
EXPOSE 8000

# Runtime command that executes the docker-entrypoint.sh
CMD [ "./docker-entrypoint.sh"]
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm
# FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm
ENV PYTHONUNBUFFERED=1

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
ARG USER=vscode

# Set default MEDIA_ROOT if not provided
ENV MEDIA_ROOT=/srv/media

RUN mkdir -p ${MEDIA_ROOT}
RUN chown -R ${USER}:${USER} ${MEDIA_ROOT}

VOLUME ["${MEDIA_ROOT}"]


# #Update PATH variable
# ENV PATH="/home/${USER}/.local/bin:${PATH}"




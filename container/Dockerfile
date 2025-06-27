# ------------------------------------------------------------------------------
#
# Dockerfile for building a container image with the Amazon Q CLI.
#
# ------------------------------------------------------------------------------

# The base image should be passed in as a build arg. The default value here just
# prevents docker from printing out a warning.
ARG BASE_IMAGE=registry.access.redhat.com/ubi9/ubi-minimal
FROM ${BASE_IMAGE}

# Define user/group configuration.
ARG CONTAINER_USER=quser
ARG CONTAINER_GROUP=develop
ARG CONTAINER_HOME=/opt/amazon-q

# Perform all tasks in a single RUN directive to reduce the number of fs layers
# and minimize our image size.
RUN echo "===> Installing os packages" \
  && microdnf install -y \
    python3.12 \
    python3.12-pip \
    unzip \
    which \
  \
  && echo "===> Installing python packages" \
  && pip3.12 install --no-cache-dir --upgrade pip \
  && pip install pygame \
  && ln -s /usr/bin/python3.12 /usr/bin/python3 \
  && ln -s /usr/bin/python3.12 /usr/bin/python \
  \
  && echo "===> Adding container user" \
  && groupadd --system ${CONTAINER_GROUP} \
  && useradd --system --gid ${CONTAINER_GROUP} --shell /bin/bash --create-home --home-dir ${CONTAINER_HOME} ${CONTAINER_USER} \
  \
  && echo "===> Installing Amazon Q AppImage" \
  && cd /opt/amazon-q \
  && curl -O "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-aarch64-linux.zip" \
  && unzip q-aarch64-linux.zip \
  && mv q/* . \
  && chown -R ${CONTAINER_USER}:${CONTAINER_GROUP} ${CONTAINER_HOME} \
  && chmod -R 755 ${CONTAINER_HOME} \
  \
  && echo "===> Cleaning up" \
  && rm -rf ${CONTAINER_HOME}/q ${CONTAINER_HOME}/q-aarch64-linux.zip

#
USER ${CONTAINER_USER}
WORKDIR ${CONTAINER_HOME}

# Default command is to run the q in chat mode.
CMD [ "${CONTAINER_HOME}/bin/qchat" ]

# Set some application environment variables.
ENV \
  PATH=${CONTAINER_HOME}/bin:${PATH} \
  Q_SHELL=/usr/bin/bash

# The following variables should be passed in via build args.
ARG APP_DESC
ARG APP_MAINTAINER
ARG APP_NAME
ARG APP_VERSION
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_URL

# Add some hopefully useful labels based on specifications at:
#   https://github.com/opencontainers/image-spec/blob/main/annotations.md
#
LABEL \
    maintainer=${APP_MAINTAINER} \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.title=${APP_NAME} \
    org.opencontainers.image.description=${APP_DESC} \
    org.opencontainers.image.revision=${GIT_COMMIT} \
    org.opencontainers.image.source=${GIT_URL} \
    org.opencontainers.image.version=${APP_VERSION}

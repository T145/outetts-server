FROM python:3.10

# ARG DEPENDENCIES="  \
#     ca-certificates \
#     libsox-dev \
#     build-essential \
#     cmake \
#     libasound-dev \
#     portaudio19-dev \
#     libportaudio2 \
#     libportaudiocpp0 \
#     ffmpeg"

ARG DEPENDENCIES="ca-certificates ffmpeg"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -ex \
    && rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache \
    && apt-get update \
    && apt-get -y install --no-install-recommends ${DEPENDENCIES} \
    && echo "no" | dpkg-reconfigure dash

WORKDIR "/app"

COPY ./app/ ./
RUN pip install -r requirements.txt
#pip install flash-attn --no-build-isolation

ENTRYPOINT ["fastapi", "run", "app.py"]

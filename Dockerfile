FROM pytorch/pytorch:2.7.0-cuda12.6-cudnn9-devel

ENV HOST=docker
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV MPLLOCALFREETYPE=1
# https://serverfault.com/questions/683605/docker-container-time-timezone-will-not-reflect-changes
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    ulimit -n 4096 && \
    ulimit -s 16384

ARG DEPENDENCIES="  \
    ca-certificates \
    libsox-dev \
    build-essential \
    cmake \
    libasound-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    git"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -ex \
    && rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends ${DEPENDENCIES} \
    && echo "no" | dpkg-reconfigure dash

WORKDIR "/app"

COPY ./app/ ./

# https://github.com/Dao-AILab/flash-attention/issues/1038#issuecomment-2439430999
# https://github.com/Dao-AILab/flash-attention/issues/1038#issuecomment-2459598112
RUN python -m pip install --upgrade pip wheel setuptools \
    && pip install -r requirements.txt \
    && CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir \
    # https://github.com/edwko/OuteTTS?tab=readme-ov-file#pip
    && CMAKE_ARGS="-DGGML_CUDA=on" pip install outetts --upgrade

#RUN MAX_JOBS=4 pip -v install flash-attn --no-build-isolation

ENTRYPOINT ["fastapi", "run", "app.py"]

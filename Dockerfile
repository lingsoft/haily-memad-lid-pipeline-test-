FROM python:3.7-slim

# Install toolkits
RUN apt-get update \
    && apt-get install -y git build-essential locales && \
    locale-gen en_US.UTF-8 && apt-get install ffmpeg -y && apt-get install sox -y && apt-get install jq -y

# Install tini and create an unprivileged user
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /sbin/tini
RUN addgroup --gid 1001 "elg" && adduser --disabled-password --gecos "ELG User,,," --home /elg --ingroup elg --uid 1001 elg && chmod +x /sbin/tini



# Copy in just the requirements file
COPY --chown=elg:elg requirements.txt /elg/

# Copy plda_bkp
COPY --chown=elg:elg plda_bkp /elg/plda_bkp/

# Everything from here down runs as the unprivileged user account
USER elg:elg

WORKDIR /elg

# Create a Python virtual environment for the dependencies
ENV VIRTUAL_ENV=/elg/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN  pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir lidbox -e git+https://github.com/py-lidbox/lidbox.git@e60d5ad2ff4d6076f9afaa780972c0301ee71ac8#egg=lidbox && \
  pip install --no-cache-dir tensorflow

# Install plda
# RUN cd plda_bkp && /elg/venv/bin/pip --no-cache-dir install . && cd ..
RUN cd plda_bkp && pip install --no-cache-dir . && cd ..

# Copy ini the entrypoint script and everything else our app needs
COPY --chown=elg:elg memad_lid_models /elg/memad_lid_models/
COPY --chown=elg:elg resources /elg/resources/
COPY --chown=elg:elg predict_scripts /elg/predict_scripts/
COPY --chown=elg:elg utils /elg/utils/

COPY --chown=elg:elg app.py docker-entrypoint.sh utils.py  /elg/

ENV WORKERS=2
ENV TIMEOUT=60
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO
ENV PYTHON_PATH=${VIRTUAL_ENV}/bin

RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
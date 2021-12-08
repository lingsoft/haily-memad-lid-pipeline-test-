FROM python:3.7-slim

# Install toolkits
RUN apt-get update \
    && apt-get install -y git build-essential locales && \
    locale-gen en_US.UTF-8 && apt-get install ffmpeg -y && apt-get install sox -y && apt-get install jq -y

# Install tini and create an unprivileged user
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /sbin/tini
RUN addgroup --gid 1001 "elg" && adduser --disabled-password --gecos "ELG User,,," --home /elg --ingroup elg --uid 1001 elg && chmod +x /sbin/tini



# Copy in just the requirements file
COPY --chown=elg:elg requirements.txt  /elg/

# Copy plda_bkp
COPY --chown=elg:elg plda_bkp /elg/plda_bkp/


# Everything from here down runs as the unprivileged user account
USER elg:elg

WORKDIR /elg



# Create a Python virtual environment for the dependencies
# RUN python -m venv venv 
# RUN /elg/venv/bin/python -m pip install --upgrade pip
RUN  pip install --upgrade pip
# RUN venv/bin/pip --no-cache-dir install -r requirements.txt && \
#   venv/bin/pip --no-cache-dir install lidbox -e git+https://github.com/py-lidbox/lidbox.git@e60d5ad2ff4d6076f9afaa780972c0301ee71ac8#egg=lidbox && \
#   venv/bin/pip --no-cache-dir install tensorflow && venv/bin/pip --no-cache-dir install elg && venv/bin/pip --no-cache-dir install "elg[flask]"

RUN pip --no-cache-dir install -r requirements.txt && \
  pip --no-cache-dir install lidbox -e git+https://github.com/py-lidbox/lidbox.git@e60d5ad2ff4d6076f9afaa780972c0301ee71ac8#egg=lidbox && \
  pip --no-cache-dir install tensorflow && pip --no-cache-dir install elg && pip --no-cache-dir install "elg[flask]"

# Install plda
RUN cd plda_bkp && pip --no-cache-dir install . && cd ..

# Copy ini the entrypoint script and everything else our app needs
COPY --chown=elg:elg memad_lid_models /elg/memad_lid_models/

COPY --chown=elg:elg classifier.py embedding_model.py feature_extraction.py generate_utts.sh lid_prediction_pipeline.py predict.sh \
split_wav_to_segments_by2s.sh split_wav_to_segments.sh  predict_n_test_yle1.sh split_file_map.py utils.py docker-entrypoint.sh app.py evaluation.py metadata.py /elg/

# Copy resources
COPY --chown=elg:elg resources /elg/resources/

ENV WORKERS=2
ENV TIMEOUT=60
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO


RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
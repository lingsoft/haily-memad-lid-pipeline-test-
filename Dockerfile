FROM python:3.7

RUN apt-get update && apt-get install ffmpeg -y && apt-get install sox -y && apt-get install jq -y

WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt

RUN pip install lidbox -e git+https://github.com/py-lidbox/lidbox.git@e60d5ad2ff4d6076f9afaa780972c0301ee71ac8#egg=lidbox\
  && pip install tensorflow

# Install plda
RUN cd plda_bkp && pip install . && cd ..

# for yle2
CMD bash ./predict_n_test_yle1.sh


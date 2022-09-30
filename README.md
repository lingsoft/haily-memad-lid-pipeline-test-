# ELG API for MeMAD lidbox language identification pipeline

This git repository contains [ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html) Flask based REST API for [MeMAD](https://memad.eu) language identification project.


The ELG API was developed based on the project [memad-lid-pipeline](https://github.com/MeMAD-project/memad-lid-pipeline), the author of the pipeline is [LimeCraft](https://www.limecraft.com/team/) while the tool [lidbox](https://github.com/py-lidbox/lidbox) is developed by Matias Lindgren with MIT license. The API is in EU's CEF project: [Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry).


## Use cases
The API can identify these languages: fi, sv, fr, de, en, and x-nolang (denotes no language detected).
The pipeline works in two scenarios:
- if there is an audio file in the request, the API splits the input audio into 2-second chunks and predicts corresponding spoken languages for each chunk.
- if there is an audio file and corresponding annotation/diarization json, defining the starting and ending times of speech fragments and their optional language labels, the API returns prediction results for the corresponding fragments. 

## Development

```
git clone --recurse-submodules https://github.com/lingsoft/memad-lidbox-elg.git memad-lidbox
cd memad-lidbox
docker build -t memad-lidbox-dev -f Dockerfile.dev .
docker run -it --rm -p 8000:8000 memad-lidbox-dev bash
# flask run --host 0.0.0.0 --port 8000
```
To make an [example call](https://github.com/lingsoft/memad-lidbox-elg/#example-call) or to [run tests](https://github.com/lingsoft/memad-lidbox-elg/#test-the-service), you first need to open a separate terminal window and find out the ID of the running container:
```
docker ps
```
Then you can get into the Docker container's shell and run some tests:
```
docker exec -it [container id] bash 
# python multi_form_req.py
# python test.py
```

## Building the docker image

```
docker build -t memad-lidbox .
```

Or pull directly ready-made image `docker pull lingsoft/memad-lidbox:tagname`.

## Deploying the service

```
docker run -d -p <port>:8000 --init --memory="2g" --restart always memad-lidbox
```

## REST API
The ELG Audio service accepts POST requests of Content-Type: multipart/form-data with two parts, the first part with name `request` has type: `application/json`, and the second part with name `content` will be audio/x-wav type which contains the actual audio data file.

### Call pattern

#### URL

```
http://<host>:<port>/process
```

place `<host>` and `<port>` with the hostname and port where the 
service is running.

#### HEADERS

```
Content-type : multipart/form-data
```

#### BODY

Part 1 with the name `request`

```
{
  "type":"audio",
  "format":"string",
  "sampleRate":number,
  "annotations": "object",
}
```

The property `format` is required and `LINEAR16` value is expected while the property `sampleRate` and `annotations` are optional. For the [second use case](#use-cases), the `annotations` file is required and should contain annotation data of the format:
```
[
  {
    "id": lang,
    "start": number,
    "end": number
  }
]
```
- `lang` (str)
  - one of these labels: 'de', 'en', 'fi', 'fr', 'sv', and 'x-nolang'. The `"id": lang` pair is optional.
- `start` and `end` (float)
  - the time indices of the recognized language parts (in second). 
  
Part 2 with the name `content`
- read in the audio file content
- maximum file size support: 100MB
- `WAV`format only, with an expected 16khz sample rate and a 16-bit sample size.


#### RESPONSE

```
{
   "response":{
      "type":"annotations",
      "annotations": {
         lang: [
            {
               "start": number,
               "end": number
            }
         ]
      }
   }
}    
```

### Response structure

- `lang` (str)
  - the corresponding identified language ('de', 'en', 'fi', 'fr' or 'sv'). Only one language is returned.
- `start` and `end` (float)
  - the time indices of the recognized language parts (in second). If use case 1, each start and end pair has a time interval of 2 seconds.

### Example call

The script `multi_form_req.py` sends multipart/form-data POST request with the audio file under `test_samples/memad_test.wav`
`memad_test.wav` is a concatenated audio of five short independent samples in 'de', 'en', 'fi', 'fr', 'sv' languages taken from the VOX dev dataset. Here are the following sample files that were concatenated (in order):
   - -7hqy7xahkM__U__S106---0752.680-0761.950.wav (de)
   - _EHGqmRh9Es__U__S130---0840.140-0846.350.wav (en)
   - 1WCI1U2iEGQ__U__S122---1453.730-1472.010.wav (fi)
   - 0A42eBNqp2Q__U__S0---0753.910-0762.010.wav (fr)
   - _8h3f0QoF5Q__U__S109---0347.590-0361.420.wav (sv)

The true lables of `memad_test.wav` (see `test_samples/memad_test_anno.json`) were manually annotated using Audacity software.

```
python3 multi_form_req.py
```

### Response should be


```
{
  "response": {
    "type": "annotations",
    "annotations": {
      "de": [
        {
          "start": 2.297,
          "end": 4.613
        }
      ],
      "en": [
        {
          "start": 4.765,
          "end": 9.278
        },
        {
          "start": 9.297,
          "end": 15.18
        }
      ],
      "fi": [
        {
          "start": 15.958,
          "end": 33.572
        }
      ],
      "fr": [
        {
          "start": 34.57,
          "end": 41.602
        }
      ],
      "sv": [
        {
          "start": 42.058,
          "end": 55.345
        }
      ]
    }
  }
}
```

## Test the service
`test_samples` directory contains two audio files: `memad_test.wav` and `olen_kehittaja.mp3` for testing purpose `olen_kehittaja.mp3` file was captured from Google translation text to speech fo the phrase "Olen kehittäjä" and used for testing wrong audio format purpose.

To run test

```
python -m unittest test -v
```

## Evaluation

Evaluation data can be found [here](https://github.com/lingsoft/memad-lidbox-elg/blob/main/Evaluation.md).

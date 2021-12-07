
import utils
# from elg_adaptor import RequestUploadedFileSizeTooLarge, AnnotationsResponse, RequestTypeUnsupport, RequestInvalid, AudioRequestUnsupportedAudioFormat, AudioRequestUnsupportedSampleRate
from elg import FlaskService
from elg.model import Failure, AudioRequest, AnnotationsResponse, Annotation

import os
import shutil # for housekeeping of files and dir created during audio processing

import uuid # for creatig random filename when needed

import json

import logging
logging.basicConfig(level=logging.DEBUG)

# set the MAX SIZE of file can be upload to 1000MB,
# app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024 

# This prevent from sorting by jsonify by default key
# app.config['JSON_SORT_KEYS'] = False
curr_dir = os.getcwd()

class MemadLID(FlaskService):
  def process_audio(self, request: AudioRequest):
      f = request.content
      try:
        fname = request.features['fname'] # if meta data contains fname we use fname to create temp file
      except:
        if request.format == 'LINEAR16': # generate random fname
          fname = str(uuid.uuid4()) + '.wav'

      audio_save_path = os.path.join(curr_dir, 'raw', fname[:-4], fname)
      audio_dir = os.path.join(curr_dir, 'raw', fname[:-4])
      os.makedirs(audio_dir)

      # Have to save audio file here
      with open(audio_save_path, 'wb') as fp:
        fp.write(f)

      if request.annotations != None: # If we get annotation file/ Annotation object in sent request
        lang_segments = request.annotations['lang_segments']
        # Have to do this since AudioRequest generate Annotation object automatically when json is sent through POST request
        lang_segments = [{"id": anno_obj.features['label'] ,"start": str(anno_obj.start) , "end": str(anno_obj.end)} for anno_obj in lang_segments] 

        # Save annotation here
        segment_save_path = os.path.join(curr_dir, 'raw', fname[:-4], fname[:-4] + '.json')
        logging.debug('segment save path %s', segment_save_path)
        with open(segment_save_path, 'w') as fp:
          json.dump(lang_segments, fp)

      else: # We split audio into chunks and predict each chunk
        segment_save_path = None

      try:
        prediction = utils.predict(audio_save_path, segment_save_path)
        shutil.rmtree(audio_dir)
        return AnnotationsResponse(annotations=prediction)
      except Exception as e:
        shutil.rmtree(audio_dir)
        return Failure(errors=[e])


memad_lid_service = MemadLID("memad-lid-service")
app = memad_lid_service.app


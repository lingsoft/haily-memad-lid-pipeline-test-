from elg import FlaskService
from elg.model import Failure, AudioRequest, AnnotationsResponse
from elg.model.base import StandardMessages

import os
import sys
import io
import shutil
import uuid
import json
import logging

import utils

from mutagen.wave import WAVE  # for audio info check

logging.basicConfig(level=logging.DEBUG)
curr_dir = os.getcwd()


class MemadLID(FlaskService):
    def process_audio(self, request: AudioRequest):
        audio_file = request.content

        # validating file size
        audio_file_size = sys.getsizeof(audio_file) / 1024
        if audio_file_size == 0 or audio_file_size < 20:
            err_msg = StandardMessages.generate_elg_request_invalid(
                detail={'audio': 'File is empty or too small'})
            return Failure(errors=[err_msg])
        if audio_file_size > 100 * 1024:  # maximum allow is 100MB
            err_msg = StandardMessages.generate_elg_upload_too_large(
                detail={'audio': 'File is over 100MB'})
            return Failure(errors=[err_msg])

        # validating file format
        try:
            audio_info = WAVE(io.BytesIO(audio_file)).info
        except Exception:
            err_msg = StandardMessages.generate_elg_request_invalid(
                detail={'audio': 'Audio is not in WAV format'})
            return Failure(errors=[err_msg])

        logging.info('Sent audio info: ', audio_info.pprint())

        audio_name = str(uuid.uuid4()) + '.wav'

        audio_save_path = os.path.join(curr_dir, 'raw', audio_name[:-4],
                                       audio_name)
        audio_dir = os.path.join(curr_dir, 'raw', audio_name[:-4])
        os.makedirs(audio_dir)

        # Save audio file here
        with open(audio_save_path, 'wb') as fp:
            fp.write(audio_file)
        logging.debug('audio save path %s', audio_save_path)
        # If we get annotation file/ Annotation object in sent request
        if request.annotations is not None:
            lang_segments = request.annotations['lang_segments']
            # reconstruct annotation json that the pipeline accepts
            lang_segments = [{
                "id": anno_obj.features['label'],
                "start": str(anno_obj.start),
                "end": str(anno_obj.end)
            } for anno_obj in lang_segments]

            # Save annotation here
            segment_save_path = os.path.join(curr_dir, 'raw', audio_name[:-4],
                                             audio_name[:-4] + '.json')
            logging.debug('segment save path %s', segment_save_path)
            with open(segment_save_path, 'w') as fp:
                json.dump(lang_segments, fp)

        else:  # We split audio into chunks and predict each chunk
            segment_save_path = None

        try:
            prediction = utils.predict(audio_save_path, segment_save_path)
            shutil.rmtree(audio_dir)
            return AnnotationsResponse(annotations=prediction)
        except Exception as e:
            logging.error(e)
            shutil.rmtree(audio_dir)
            error = StandardMessages.generate_elg_service_internalerror(
                params=[str(e)])
            return Failure(errors=[error])


memad_lid_service = MemadLID("memad-lid-service")
app = memad_lid_service.app

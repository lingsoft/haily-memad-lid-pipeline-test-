import unittest
import json
import requests
import os


class TestResponseStucture(unittest.TestCase):
    url = 'http://localhost:8000/process'
    lang_codes = ('de', 'en', 'fi', 'fr', 'sv', 'x-nolang')
    audio = os.path.join(os.getcwd(), 'test_samples/memad_test.wav')
    anno = os.path.join(os.getcwd(), 'test_samples/memad_test_anno.json')

    with open(anno, 'r') as f:
        true_labels = json.load(f)

    def make_audio_req(self, audio, has_annot):
        """Prepare Audio Request based on
        lang code endpoint, audio, and text"""
        if has_annot:
            anno_lst = [_.copy() for _ in self.true_labels]
            for anno_ in anno_lst:
                anno_["features"] = {"label": anno_.pop("id") if "id" in anno_ else "x-nolang"}
                anno_["start"] = float(anno_["start"])
                anno_["end"] = float(anno_["end"])
                anno_ = json.dumps(anno_)
            annots = {"lang_segments": anno_lst}

            payload = {
                "type": "audio",
                "format": "LINEAR16",
                "sampleRate": 16000,
                "annotations": annots
            }
        else:
            payload = {
                "type": "audio",
                "format": "LINEAR16",
                "sampleRate": 16000
            }

        try:
            _ = os.path.isfile(audio)
            with open(audio, 'rb') as f:
                files = {
                    'request': (None, json.dumps(payload), 'application/json'),
                    'content':
                    (os.path.basename(audio), f.read(), 'audio/x-wav')
                }
        except Exception:
            files = {
                'request': (None, json.dumps(payload), 'application/json'),
                'content': (None, audio, 'audio/x-wav')
            }

        return files

    def test_api_response_status_code_with_full_request(self):
        """Should return status code 200 when sending both audio and
        annotation
        """
        files = self.make_audio_req(self.audio, has_annot=True)
        status_code = requests.post(self.url, files=files).status_code
        self.assertEqual(status_code, 200)

    def test_api_response_result_with_full_request(self):
        """Should return ELG annotation response with original timestamps
        and true lables when given full request.
        """

        files = self.make_audio_req(self.audio, has_annot=True)
        response = requests.post(self.url, files=files).json()
        print(response)

        self.assertEqual(response['response'].get('type'), 'annotations')
        
        segments = []
        for lang in response['response']['annotations']:
            self.assertIn(lang, self.lang_codes)
            for res in response['response']['annotations'][lang]:
                segments.append(res)
        segments_sorted = sorted(segments, key=lambda d: d['start'])
        for i, segment in enumerate(segments_sorted):
            self.assertEqual(segment['start'], float(self.true_labels[i]['start']))
            self.assertEqual(segment['end'], float(self.true_labels[i]['end']))

    def test_api_response_too_small_audio_request(self):
        """Service should return ELG failure when
        too small audio file is sent
        """

        too_short_audio = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\
            \x01\x00\x00\x04\x00\x00\x00\x04\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00'

        files = self.make_audio_req(too_short_audio, has_annot=False)
        response = requests.post(self.url, files=files).json()
        print(response)
        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['detail']['audio'],
                         'File is empty or too small')

    def test_api_response_invalid_audio_format_request(self):
        """Service should return ELG failure when mp3 audio file is sent
        """

        mp3_audio = os.path.join(os.getcwd(),
                                 'test_samples/olen_kehittäjä.mp3')

        files = self.make_audio_req(mp3_audio, has_annot=False)
        response = requests.post(self.url, files=files).json()
        print(response)
        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['detail']['audio'],
                         'Audio is not in WAV format')

    def test_api_response_status_code_with_audio_only_request(self):
        """Should return status code 200 with only audio request
        """
        files = self.make_audio_req(self.audio, has_annot=False)
        status_code = requests.post(self.url, files=files).status_code
        self.assertEqual(status_code, 200)

    def test_api_response_result_with_audio_only_request(self):
        """Should return ELG annotation response with 2 second interval
        timestamps and lang in allowed lang codes
        """
        files = self.make_audio_req(self.audio, has_annot=False)
        response = requests.post(self.url, files=files).json()
        print(response)

        self.assertEqual(response['response'].get('type'), 'annotations')
        s = 0
        segments = []
        for lang in response['response']['annotations']:
            self.assertIn(lang, self.lang_codes)
            for res in response['response']['annotations'][lang]:
                segments.append(res)
        segments_sorted = sorted(segments, key=lambda d: d['start'])
        for segment in segments_sorted:
            self.assertEqual(segment['start'], s * 2)
            self.assertEqual(segment['end'], s * 2 + 2)
            s += 1

    def test_mismatch_audio_format(self):
        """Service should return an error when user sends mismatching
        audio format"""

        url = self.url
        audio = self.audio
        payload = {
            "type": "audio",
            "format": "mp3",
            "sampleRate": 16000,
        }

        with open(audio, 'rb') as f:
            files = {
                'request': (None, json.dumps(payload), 'application/json'),
                'content': (os.path.basename(audio), f.read(), 'audio/x-wav')
            }

        response = requests.post(url, files=files).json()
        print(response)

        self.assertEqual(response['failure']['errors'][0]['code'], 
                         'elg.request.audio.format.unsupported')

    def test_mismatch_audio_sampleRate_request_and_sent_file(self):
        """Service should return additional warning when user send mismatch
        audio sampleRate w.r.t the sent audio file"""

        url = self.url
        audio = self.audio
        payload = {
            "type": "audio",
            "format": "LINEAR16",
            "sampleRate": 12000,
        }

        with open(audio, 'rb') as f:
            files = {
                'request': (None, json.dumps(payload), 'application/json'),
                'content': (os.path.basename(audio), f.read(), 'audio/x-wav')
            }

        response = requests.post(url, files=files).json()
        print(response)

        self.assertEqual(response['response'].get('type'), 'annotations')
        self.assertEqual(response['response']['warnings'][0]['code'],
                         'elg.request.parameter.sampleRate.value.mismatch')


if __name__ == '__main__':
    unittest.main()

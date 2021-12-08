from elg.model import AudioRequest
from elg import Service
service = Service.from_docker_image("memad-elg:latest", "http://localhost:3000/process",3000)
audio_req = AudioRequest.from_file("00200000_00217960_fi.wav", sample_rate=16000)
print(service(audio_req,sync_mode=True))

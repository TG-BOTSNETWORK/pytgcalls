from typing import Union

from ntgcalls import MediaSource

from ...media_devices.speaker_device import SpeakerDevice
from ...statictypes import statictypes
from ..raw.audio_parameters import AudioParameters
from ..raw.audio_stream import AudioStream
from ..raw.stream import Stream
from ..raw.video_parameters import VideoParameters
from ..raw.video_stream import VideoStream
from ..stream.audio_quality import AudioQuality


class RecordStream(Stream):
    @statictypes
    def __init__(
        self,
        audio: Union[bool, str, SpeakerDevice] = False,
        audio_parameters: Union[
            AudioParameters,
            AudioQuality,
        ] = AudioQuality.HIGH,
        camera: bool = False,
        screen: bool = False,
    ):
        raw_audio_parameters = (
            audio_parameters
            if isinstance(audio_parameters, AudioParameters)
            else AudioParameters(*audio_parameters.value)
            if isinstance(audio_parameters, AudioQuality)
            else ValueError('Invalid audio parameters')
        )

        microphone = self._get_microphone(audio, raw_audio_parameters)

        super().__init__(
            microphone=microphone,
            speaker=None,
            camera=self._get_video_stream(camera),
            screen=self._get_video_stream(screen),
        )

    def _get_microphone(self, audio, raw_audio_parameters):
        if isinstance(audio, bool) and audio:
            return AudioStream(
                media_source=MediaSource.EXTERNAL,
                path='',
                parameters=raw_audio_parameters,
            )
        if isinstance(audio, str):
            is_lossless = raw_audio_parameters.bitrate > 48000
            commands = [
                'ffmpeg',
                '-loglevel',
                'quiet',
                '-f',
                's16le',
                '-ar',
                str(raw_audio_parameters.bitrate),
                '-ac',
                str(raw_audio_parameters.channels),
                '-i',
                'pipe:0',
                '-codec:a',
                'flac' if is_lossless else 'libmp3lame',
                audio,
            ]
            return AudioStream(
                media_source=MediaSource.SHELL,
                path=' '.join(commands),
                parameters=raw_audio_parameters,
            )
        if isinstance(audio, SpeakerDevice):
            return AudioStream(
                media_source=MediaSource.DEVICE,
                path=audio.metadata,
                parameters=raw_audio_parameters,
            )

    def _get_video_stream(self, enable):
        return (
            VideoStream(
                media_source=MediaSource.EXTERNAL,
                path='',
                parameters=VideoParameters(
                    width=-1,
                    height=-1,
                    frame_rate=-1,
                ),
            )
            if enable
            else None
        )
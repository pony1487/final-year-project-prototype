import pyaudio
import wave
import struct


class MicrophoneRecorder:
    """
    This class uses the Pyaudio library to capture audio from the microphone for x seconds or the size of a chunk(block)
    of audio
    The docs at https://people.csail.mit.edu/hubert/pyaudio/docs/ were used and the following stack overflow posts
    https://stackoverflow.com/questions/35344649/reading-input-sound-signal-using-python
    https://stackoverflow.com/questions/47189624/maintain-a-streaming-microphone-input-in-python
    """
    def __init__(self, chunk, channels, rate, record_seconds):
        self.CHUNK = chunk
        self.CHANNELS = channels
        self.RATE = rate
        self.RECORD_SECONDS = record_seconds
        self.FORMAT = pyaudio.paInt16

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

    def record_one_chunk(self):
        print("* recording")
        data = self.stream.read(self.CHUNK)
        print("* done recording")
        data_int = struct.unpack(str(2 * self.CHUNK) + 'B', data)
        print(data_int)

    def record_for_seconds(self):
        frames = []
        graph_data = []
        print("* recording")
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
            data_int = struct.unpack(str(2 * self.CHUNK) + 'B', data)
            graph_data.append(data_int)

        print("* done recording")
        # print(graph_data)
        return frames

    def write_recording_to_file(self, frames, wave_output_filename):
        print("Writing file.....")
        wf = wave.open(wave_output_filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("Success! File written")

    def __str__(self):
        return "CHUNK: {}\nCHANNELS: {}\nRATE: {}\nRECORD_SECONDS".format(self.CHUNK, self.CHANNELS, self.RATE,
                                                                          self.RECORD_SECONDS)

import wave
import librosa
import aubio

from scipy import fftpack, signal
from scipy.io import wavfile as scipy_wav


import numpy as np
import matplotlib.pyplot as plt


class FFTProcessor:
    """
    This class was originally used to try and determine the frequency of notes but proved that it would not work.
    See the interim report for more details regarding The Missing Fundamental Problem.
    There may be a use for this class in future pending further research.
    """
    def __init__(self, filename, chunk):
        self.filename = filename
        self.CHUNK = chunk

    def get_frequency(self):
        """
        Taken from https://docs.scipy.org/doc/numpy/reference/generated/numpy.fft.fftfreq.html
        This method was used to test whether using FFT was a viable option.
        :return:
        """
        sample_rate, data = scipy_wav.read(self.filename)

        fft_out = fftpack.fft(data)
        print(len(fft_out))
        freqs = np.fft.fftfreq(len(fft_out))

        # Find the peak in the coefficients
        idx = np.argmax(np.abs(fft_out))

        freq = freqs[idx]
        count = 0

        f = open("freqs.txt", "w")

        freq_in_hertz = abs(freq * sample_rate)
        return freq_in_hertz

    def fft_with_scipy(self):
        """
        Taken from https://docs.scipy.org/doc/scipy/reference/fftpack.html
        This method was used to test whether using FFT was a viable option.
        :return:
        """
        sample_rate, data = scipy_wav.read(self.filename)
        fft_out = fftpack.fft(data)
        freqs = np.fft.fftfreq(len(fft_out))
        # Convert freq list in hz
        freqs_as_hz = [i * sample_rate for i in freqs]
        plt.plot(np.abs(freqs_as_hz) , np.abs(fft_out))
        plt.xlim(80, 10000)
        plt.xlabel('frequency')
        plt.ylabel('Amplitude')
        plt.savefig("./images/fft_scipy.png")
        plt.show()
        return np.abs(fft_out)

    def fft_with_librosa(self):
        """
        Taken https://librosa.github.io/librosa/generated/librosa.core.stft.html
        This method was used to test whether using FFT was a viable option.
        :return:
        """
        y, sr = librosa.load(self.filename)
        fft_out = np.abs(librosa.stft(y))
        max_idx = np.argmax(fft_out)
        print(max_idx)
        freqs = librosa.fft_frequencies(sr, len(fft_out))
        print(freqs)
        return fft_out



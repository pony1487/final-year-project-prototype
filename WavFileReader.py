import wave
import pyaudio
import itertools
import aubio
import numpy as np
import matplotlib.pyplot as plt
import librosa

from aubio import source, notes, onset, source, pitch
from numpy import hstack, zeros
from FFTProcessor import FFTProcessor
from scipy import fftpack, signal
from librosa import display
from PitchSpeller import PitchSpeller


class WavFileReader:

    def __init__(self, filename):
        self.CHUNK = 2048
        self.filename = filename
        self.p = pyaudio.PyAudio()

    def play_file(self):
        """
        Taken from https://people.csail.mit.edu/hubert/pyaudio/docs/
        Opens a wav file and reads the data in CHUNKS and then writes the chunks to a stream which is the audio device
        :return:
        """
        file = wave.open(self.filename, 'r')

        stream = self.p.open(format=self.p.get_format_from_width(file.getsampwidth()),
                             channels=file.getnchannels(),
                             rate=file.getframerate(),
                             output=True)
        data = file.readframes(self.CHUNK)
        # play stream
        while data:
            stream.write(data)
            data = file.readframes(self.CHUNK)

        # stop stream
        stream.stop_stream()
        stream.close()

        # close PyAudio
        self.p.terminate()
        file.close()

    def plot_wav_file(self):
        """
        This method draw a plot of an audio file.
        This was used as a guide/reference https://matplotlib.org/
        :return:
        """
        # Extract Raw Audio from Wav File
        file = wave.open(self.filename, 'r')
        signal = file.readframes(-1)
        signal = np.fromstring(signal, 'Int16')

        plt.figure(1)
        plt.title('Guitar Wave...')

        plt.plot(signal)
        plt.savefig('./images/guitar_wav.png', dpi=300)
        plt.show()

        file.close()

    def get_fft_of_wave_file(self):
        """
        This uses custom class FFTProcessor which has various libraries implementations of the FFT in it.
        Currently the FFT is not being used as it does not work with guitar audio but may be useful in future,
        see the interim report for more details.

        """
        fft_processor = FFTProcessor(self.filename, self.CHUNK)

        # Scipy Library
        print("fft with Scipy: \n" + str(fft_processor.fft_with_scipy()))

    def print_frequency(self):
        """
        This uses custom class FFTProcessor which has various libraries implementations of the FFT in it.
        Currently the FFT is not being used as it does not work with guitar audio but may be useful in future,
        see the interim report for more details.

        """
        fft_processor = FFTProcessor(self.filename, self.CHUNK)
        print("Frequency: " + str(fft_processor.get_frequency()))

    def plot_chromagram_with_librosa(self, lesson_name):
        """
        Taken from https://librosa.github.io/librosa/
        This shows the frequencies of chords. Currently is is only accurate with two note chords
        :param lesson_name:
        :return:
        """
        y, sr = librosa.load(self.filename)

        # This seems to be clearest
        # Precomputed power spectrum
        S = np.abs(librosa.stft(y, n_fft=4096)) ** 2
        chroma = librosa.feature.chroma_stft(S=S, sr=sr)

        plt.figure(figsize=(10, 4))
        display.specshow(chroma, y_axis='chroma', x_axis='time')
        plt.colorbar()
        plt.title(str(lesson_name))
        plt.tight_layout()
        plt.savefig('./images/power_chords_chroma.png', dpi=300)
        plt.show()

    def aubio_test(self):
        """
        Taken from https://github.com/aubio/aubio/tree/master/python/demos
        This is a simple test of the aubio libary. It prints out the frequency in Hz as the audio is read
        """
        samplerate = 0  # use original source samplerate
        hop_size = 256  # number of frames to read in one block
        s = aubio.source(self.filename, samplerate, hop_size)
        total_frames = 0

        while True:  # reading loop
            samples, read = s()
            total_frames += read
            if read < hop_size: break  # end of file reached

        fmt_string = "read {:d} frames at {:d}Hz from {:s}"
        print(fmt_string.format(total_frames, s.samplerate, self.filename))

    def aubio_lib_frequency(self):
        """
        Taken from https://github.com/aubio/aubio/tree/master/python/demos and slightly modified
        This uses the pitch method in aubio. It reads the audio file and gives a list of frequencies and the proability
        that it is that note.
        """

        filename = self.filename

        downsample = 1
        samplerate = 44100 // downsample

        win_s = 4096 // downsample  # fft size
        hop_s = 512 // downsample  # hop size

        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate

        tolerance = 0.8

        # uses the yin algorithm to determine pitch
        pitch_o = aubio.pitch("yin", win_s, hop_s, samplerate)
        pitch_o.set_unit("Hz")
        pitch_o.set_tolerance(tolerance)

        pitches = []
        confidences = []

        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            pitch = pitch_o(samples)[0]
            pitch = int(round(pitch))
            confidence = pitch_o.get_confidence()
            # set the threshold high to ignore frequencies such as random string noise before audio start playing
            if confidence < 0.99:pitch = 0.

            pitches += [pitch]
            confidences += [confidence]
            total_frames += read
            if read < hop_s: break

        pitch_list_minus_duplicates = remove_consecutive_duplicates(pitches)
        return pitch_list_minus_duplicates

    def plot_onset_for_direct_recording(self):
        """
        Taken directly from here:
        https://github.com/aubio/aubio/blob/master/python/demos/demo_onset_plot.py
        The threshold is set differently for direct signal from audio device as it is cleaner
        :return:
        """
        import sys
        from aubio import onset, source
        from numpy import hstack, zeros

        win_s = 512  # fft size
        hop_s = win_s // 2  # hop size

        filename = self.filename

        samplerate = 0

        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        o = onset("default", win_s, hop_s, samplerate)

        # One threshold does not seem to work for all cases
        # set threshold so it doesnt pick up string noise or movement 0.5 is too low, 5.0 is too big
        o.set_threshold(1.2)

        # list of when peaks happen at time t(seconds)
        onset_time_list = []
        # list of onsets, in samples
        onsets = []

        # storage for plotted data
        desc = []
        tdesc = []
        allsamples_max = zeros(0, )
        downsample = 2  # to plot n samples / hop_s

        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()

            if o(samples):
                # print("%f" % (o.get_last_s()))
                onset_time_list.append(o.get_last_s())
                onsets.append(o.get_last())
            # keep some data to plot it later
            new_maxes = (abs(samples.reshape(hop_s // downsample, downsample))).max(axis=0)
            allsamples_max = hstack([allsamples_max, new_maxes])
            desc.append(o.get_descriptor())
            tdesc.append(o.get_thresholded_descriptor())
            total_frames += read
            if read < hop_s: break

        # print(onsets)

        if 1:
            # do plotting
            import matplotlib.pyplot as plt
            allsamples_max = (allsamples_max > 0) * allsamples_max
            allsamples_max_times = [float(t) * hop_s / downsample / samplerate for t in range(len(allsamples_max))]
            plt1 = plt.axes([0.1, 0.75, 0.8, 0.19])
            plt2 = plt.axes([0.1, 0.1, 0.8, 0.65], sharex=plt1)
            plt.rc('lines', linewidth='.8')
            plt1.plot(allsamples_max_times, allsamples_max, '-b')
            plt1.plot(allsamples_max_times, -allsamples_max, '-b')
            for stamp in onsets:
                stamp /= float(samplerate)
                plt1.plot([stamp, stamp], [-1., 1.], '-r')
            plt1.axis(xmin=0., xmax=max(allsamples_max_times))
            plt1.xaxis.set_visible(False)
            plt1.yaxis.set_visible(False)
            desc_times = [float(t) * hop_s / samplerate for t in range(len(desc))]
            desc_max = max(desc) if max(desc) != 0 else 1.
            desc_plot = [d / desc_max for d in desc]
            plt2.plot(desc_times, desc_plot, '-g')
            tdesc_plot = [d / desc_max for d in tdesc]
            for stamp in onsets:
                stamp /= float(samplerate)
                plt2.plot([stamp, stamp], [min(tdesc_plot), max(desc_plot)], '-r')
            plt2.plot(desc_times, tdesc_plot, '-y')
            plt2.axis(ymin=min(tdesc_plot), ymax=max(desc_plot))
            plt.xlabel('time (s)')
            # plt.savefig('./images/threshold_correct.png', dpi=300)
            plt.show()

        return onset_time_list

    def plot_onset_for_mic_recording(self):
        """
        Taken directly from here:
        https://github.com/aubio/aubio/blob/master/python/demos/demo_onset_plot.py

        However the threshold is set different to compensate for the different signal level of the microphone compared
        to the direct signal
        :return:
        """

        win_s = 512  # fft size
        hop_s = win_s // 2  # hop size

        filename = self.filename

        samplerate = 0

        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        o = onset("default", win_s, hop_s, samplerate)

        # One threshold does not seem to work for all cases
        o.set_threshold(0.45)

        # list of when peaks happen at time t(seconds)
        onset_time_list = []
        # list of onsets, in samples
        onsets = []

        # storage for plotted data
        desc = []
        tdesc = []
        allsamples_max = zeros(0, )
        downsample = 2  # to plot n samples / hop_s

        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()

            if o(samples):
                # print("%f" % (o.get_last_s()))
                onset_time_list.append(o.get_last_s())
                onsets.append(o.get_last())
            # keep some data to plot it later
            new_maxes = (abs(samples.reshape(hop_s // downsample, downsample))).max(axis=0)
            allsamples_max = hstack([allsamples_max, new_maxes])
            desc.append(o.get_descriptor())
            tdesc.append(o.get_thresholded_descriptor())
            total_frames += read
            if read < hop_s: break

        # print(onsets)

        if 1:
            # do plotting
            import matplotlib.pyplot as plt
            allsamples_max = (allsamples_max > 0) * allsamples_max
            allsamples_max_times = [float(t) * hop_s / downsample / samplerate for t in range(len(allsamples_max))]
            plt1 = plt.axes([0.1, 0.75, 0.8, 0.19])
            plt2 = plt.axes([0.1, 0.1, 0.8, 0.65], sharex=plt1)
            plt.rc('lines', linewidth='.8')
            plt1.plot(allsamples_max_times, allsamples_max, '-b')
            plt1.plot(allsamples_max_times, -allsamples_max, '-b')
            for stamp in onsets:
                stamp /= float(samplerate)
                plt1.plot([stamp, stamp], [-1., 1.], '-r')
            plt1.axis(xmin=0., xmax=max(allsamples_max_times))
            plt1.xaxis.set_visible(False)
            plt1.yaxis.set_visible(False)
            desc_times = [float(t) * hop_s / samplerate for t in range(len(desc))]
            desc_max = max(desc) if max(desc) != 0 else 1.
            desc_plot = [d / desc_max for d in desc]
            plt2.plot(desc_times, desc_plot, '-g')
            tdesc_plot = [d / desc_max for d in tdesc]
            for stamp in onsets:
                stamp /= float(samplerate)
                plt2.plot([stamp, stamp], [min(tdesc_plot), max(desc_plot)], '-r')
            plt2.plot(desc_times, tdesc_plot, '-y')
            plt2.axis(ymin=min(tdesc_plot), ymax=max(desc_plot))
            plt.xlabel('time (s)')
            plt.savefig('./images/noise_at_start_and_wrong_transient.png', dpi=300)
            plt.show()

        return onset_time_list

    def audio_filter(self):
        """
        Taken from https://github.com/aubio/aubio/tree/master/python/demos
        This was used for testing high and low pass filters which clean up the unwanted low and high frequencies.
        This was done in an attempt to remove unwanted noise from the microphone signal. It may be useful in the
        future
        """
        # open input file, get its samplerate
        s = aubio.source(self.filename)
        samplerate = s.samplerate

        target = "./audio/filteredAudio/filter.wav"

        # A-weighting filter is 7, C-weighting is 5
        # See https://en.wikipedia.org/wiki/A-weighting for a brief overview
        f = aubio.digital_filter(7)
        f.set_a_weighting(samplerate)

        # create output file
        o = aubio.sink(target, samplerate)

        total_frames = 0
        while True:
            # read from source
            samples, read = s()
            # filter samples
            filtered_samples = f(samples)
            # write to sink
            o(filtered_samples, read)
            # count frames read
            total_frames += read
            # end of file reached
            if read < s.hop_size:
                break

        # print some info
        duration = total_frames / float(samplerate)
        input_str = "input: {:s} ({:.2f} s, {:d} Hz)"
        output_str = "output: {:s}, A-weighting filtered ({:d} frames total)"
        print(input_str.format(s.uri, duration, samplerate))
        print(output_str.format(o.uri, total_frames))

    def __str__(self):
        return "{}".format(self.CHUNK)


"""
The below methods are implemented by myself
"""


def compare_onsets(correct_onset_list, onset_list_to_compare):
    """
    This method takes to lists of times and subtracts one from the other to get the difference
    This idea will be used to determine the timing of the notes played
    :param onset_list_one:
    :param onset_list_two:
    :return: empty string for now
    """
    timing_diff_list = []

    for i in range(0, len(correct_onset_list)):
        if i > len(onset_list_to_compare):
            break
        print(abs(correct_onset_list[i] - onset_list_to_compare[i]))

    return ""


def compare_notes_played(lesson_list, list_to_compare):
    """
    This method takes two lists of notes(chars) and checks the difference of between them.
    :param lesson_list:
    :param list_to_compare:
    :return:
    """
    list_of_note_indexes = []
    expected_len_of_list = len(lesson_list)
    counter = 0

    # Determine the index of the incorrect note
    while counter < expected_len_of_list:
        if counter == len(list_to_compare):
            print("You didnt play the correct number of notes!")
            break
        if lesson_list[counter] != list_to_compare[counter]:
            list_of_note_indexes.append(counter)
        counter += 1

    # Display the position of the note that the user played wrong
    for i in range(0, len(lesson_list)):
        if i in list_of_note_indexes:
            # i + plus so user doenst have to start counting at 0
            print("The {} note was meant to be a {}, You played a {}".format(i + 1, lesson_list[i], list_to_compare[i]))

    print("List indexes of wrong played notes")
    print(list_of_note_indexes)

    print("Notes that dont match original")
    print(set(list_to_compare) - set(lesson_list))


def remove_consecutive_duplicates(freq_list):
    """
    This method reduces repeating characters to more accurately represent the notes being played.
    The frequencies in freq_list first converted to the appropriate notes using PitchSpeller.
    The Aubio library method that returns the frequencies that fill the freq_list is constantly checking the frequency
    until the audio is over. This leads to for example multiple A notes being put in the list for the duration of a
    single A note. For example, the notes played could be A B C D and the freq_list after being pitch spelt would be
    something like A A A A A A A A A B B B B B B B B C C C C C C C D D D D D D D. Which is note wrong, but messy to
    look at an gives the impression that the notes were played multiple times as opposed to once each.


    :param freq_list:
    :return:
    """
    pitch_speller = PitchSpeller()
    pitch_spelled_list = []

    for freq in freq_list:
        if freq != 0:
            pitch_spelled_list.append(pitch_speller.spell(freq))

    pitch_list_minus_duplicates = [k for k, g in itertools.groupby(pitch_spelled_list)]

    print(pitch_list_minus_duplicates)

    return pitch_list_minus_duplicates

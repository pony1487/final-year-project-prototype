from MicrophoneRecorder import MicrophoneRecorder
from WavFileReader import WavFileReader, compare_onsets, compare_notes_played
from PitchSpeller import PitchSpeller
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10


def menu():
    running = True
    while running:
        print("""
        1.Record Audio
        2.Compare Two Sine Waves
        3.Lesson Material compare
        4.Timing compare
        5.Filter test
        6.Power chords Electric Guitar Direct
        7.Analyse mic recording Chords
        8.Analyse mic recording Notes
        20.Exit/Quit
        """)
        ans = input("What would you like to do? ")
        if ans == "1":
            mic = MicrophoneRecorder(CHUNK, CHANNELS, RATE, RECORD_SECONDS)
            frames = mic.record_for_seconds()
            file_name = "mictest.wav"
            mic.write_recording_to_file(frames, file_name)
        elif ans == "2":
            pitch_speller = PitchSpeller()

            file_one = "./audio/440hzSine.wav"
            file_two = "./audio/523.25hzSine.wav"

            print("\n------------Frequences 440hz and 523.5hz sine waves using FFT----------------")
            # use fft to get frequency of sine wave
            wav_reader_one = WavFileReader(file_one)
            wav_reader_one.print_frequency()

            wav_reader_two = WavFileReader(file_two)
            wav_reader_two.print_frequency()

            # Difference between F and A
            print("\n------------Hardcoded Frequences in function call----------------")
            pitch_speller.get_num_of_notes_between_notes(349.00, 440.00, )
            print("Pitch of 440.00: " + str(pitch_speller.spell(440.00)))

        elif ans == "3":
            lesson_file = "./audio/LessonTest/Notes/A_minor_scale_frag_1/A_minor_scale_frag_1_LESSON.wav"
            correct_file = "./audio/LessonTest/Notes/A_minor_scale_frag_1/A_minor_scale_frag_1_CORRECT.wav"
            incorrect_file = "./audio/LessonTest/Notes/A_minor_scale_frag_1/A_minor_scale_frag_1_INCORRECT.wav"
            one_off_file = "./audio/LessonTest/Notes/A_minor_scale_frag_1/A_minor_scale_frag_1_ONE_OFF.wav"

            lesson_wav_reader = WavFileReader(lesson_file)
            correct_wav_reader = WavFileReader(correct_file)
            incorrect_wav_reader = WavFileReader(incorrect_file)

            lesson_wav_reader.play_file()
            print("Lesson Notes")
            lesson_note_list = lesson_wav_reader.aubio_lib_frequency()

            correct_wav_reader.play_file()
            print("Played Correctly Notes")
            correct_note_list = correct_wav_reader.aubio_lib_frequency()

            incorrect_wav_reader.play_file()
            print("Played Wrong Notes")
            incorrect_note_list = incorrect_wav_reader.aubio_lib_frequency()

            print("wrong notes played: ")
            compare_notes_played(lesson_note_list, incorrect_note_list)

        elif ans == "4":
            print("timing test")
            """
            lesson_file = "./audio/LessonTest/Timing/120_bpm_A_pentatonic/A_pentatonic_timing_LESSON.wav"
            correct_file = "./audio/LessonTest/Timing/120_bpm_A_pentatonic/A_pentatonic_timing_CORRECT.wav"
            incorrect_file = "./audio/LessonTest/Timing/120_bpm_A_pentatonic/A_pentatonic_timing_INCORRECT.wav"
            """

            lesson_file = "./audio/LessonTest/Timing/120_bpm_E_string_rhythm/E_String_timing_LESSON.wav"
            correct_file = "./audio/LessonTest/Timing/120_bpm_E_string_rhythm/E_String_timing_CORRECT.wav"
            incorrect_file = "./audio/LessonTest/Timing/120_bpm_E_string_rhythm/E_String_timing_INCORRECT.wav"

            lesson_wav_reader = WavFileReader(lesson_file)
            correct_wav_reader = WavFileReader(correct_file)
            incorrect_wav_reader = WavFileReader(incorrect_file)

            lesson_onset_list_in_seconds = lesson_wav_reader.plot_onset_for_direct_recording()

            print("Lesson:")
            print(lesson_onset_list_in_seconds)

            correct_onset_list_in_seconds = correct_wav_reader.plot_onset_for_direct_recording()

            print("Correctly Played:")
            print(correct_onset_list_in_seconds)

            incorrect_onset_list_in_seconds = incorrect_wav_reader.plot_onset_for_direct_recording()

            print("Incorrectly Played:")
            print(incorrect_onset_list_in_seconds)

            print("\ntime diff between lesson and correct")
            compare_onsets(lesson_onset_list_in_seconds, correct_onset_list_in_seconds)

            print("\ntime diff between lesson and INCORRECT")
            compare_onsets(lesson_onset_list_in_seconds, incorrect_onset_list_in_seconds)

        elif ans == "5":
            print("Apply filter")
            lesson_file = "./audio/LessonTest/Notes/A_minor_scale_frag_1/A_minor_scale_frag_1_LESSON.wav"
            lesson_wav_reader = WavFileReader(lesson_file)
            lesson_wav_reader.play_file()
            lesson_wav_reader.audio_filter()

            filter_file = "./audio/filteredAudio/filter.wav"
            lesson_wav_reader = WavFileReader(filter_file)

            lesson_wav_reader.play_file()

            lesson_onset_list_in_seconds = lesson_wav_reader.plot_onset_for_direct_recording()

            lesson_wav_reader.aubio_lib_frequency()

        elif ans == "6":
            lesson_file = "./audio/LessonTest/Notes/PowerChords/E_E_G_A_LESSON.wav"

            correct_file = "./audio/LessonTest/Notes/PowerChords/E_E_G_A_CORRECT.wav"

            incorrect_file = "./audio/LessonTest/Notes/PowerChords/E_E_G_A_INCORRECT.wav"

            lesson_wav_reader = WavFileReader(lesson_file)
            lesson_wav_reader.play_file()
            lesson_wav_reader.plot_chromagram_with_librosa("Lesson")

            correct_wav_reader = WavFileReader(correct_file)
            correct_wav_reader.play_file()
            correct_wav_reader.plot_chromagram_with_librosa("Correct")

            incorrect_wav_reader = WavFileReader(incorrect_file)
            incorrect_wav_reader.play_file()
            incorrect_wav_reader.plot_chromagram_with_librosa("Incorrect")
            incorrect_wav_reader.aubio_lib_frequency()

        elif ans == "7":
            print("analyse mic recording chords")
            mic_lesson = "./audio/LessonTest/Acoustic/E_E_A_G_E_Lesson.wav"
            mic_lesson_wave_reader = WavFileReader(mic_lesson)

            mic_correct = "./audio/LessonTest/Acoustic/E_E_A_G_E_Correct.wav"
            mic_correct_wave_reader = WavFileReader(mic_correct)

            mic_incorrect = "./audio/LessonTest/Acoustic/E_E_A_G_E_Incorrect.wav"
            mic_incorrect_wave_reader = WavFileReader(mic_incorrect)

            mic_lesson_wave_reader.play_file()
            mic_lesson_wave_reader.plot_chromagram_with_librosa("Lesson")
            mic_lesson_wave_reader.plot_onset_for_mic_recording()

            mic_correct_wave_reader.play_file()
            mic_correct_wave_reader.plot_chromagram_with_librosa("Correct")
            mic_correct_wave_reader.plot_onset_for_mic_recording()

            mic_incorrect_wave_reader.play_file()
            mic_incorrect_wave_reader.plot_chromagram_with_librosa("Incorrect")
            mic_incorrect_wave_reader.plot_onset_for_mic_recording()

        elif ans == "8":
            print("analyse mic recording notes")
            mic_lesson = "./audio/LessonTest/Acoustic/Ascending_Descending_LESSON.wav"
            mic_lesson_wave_reader = WavFileReader(mic_lesson)

            mic_correct = "./audio/LessonTest/Acoustic/Ascending_Descending_CORRECT.wav"
            mic_correct_wave_reader = WavFileReader(mic_correct)

            mic_incorrect = "./audio/LessonTest/Acoustic/Ascending_Descending_ONEWRONG.wav"
            mic_incorrect_wave_reader = WavFileReader(mic_incorrect)

            mic_lesson_wave_reader.play_file()
            lesson_note_list = mic_lesson_wave_reader.aubio_lib_frequency()
            mic_lesson_wave_reader.plot_onset_for_mic_recording()

            mic_correct_wave_reader.play_file()
            correct_note_list = mic_correct_wave_reader.aubio_lib_frequency()
            mic_correct_wave_reader.plot_onset_for_mic_recording()

            mic_incorrect_wave_reader.play_file()
            incorrect_note_list = mic_incorrect_wave_reader.aubio_lib_frequency()
            mic_incorrect_wave_reader.plot_onset_for_mic_recording()

            compare_notes_played(lesson_note_list, incorrect_note_list)

        elif ans == "20":
            print("\n Goodbye")
            running = False
        elif ans != "":
            print("\n Not Valid Choice Try again")


def main():
    menu()


main()

#!/usr/bin/python3

import numpy as np
import librosa
from pydub import AudioSegment
#import wave
#import array
import soundfile as sf

def joinAudioFiles(firstAudioFile, secondAudioFile, destination_path):
	sound1 = AudioSegment.from_wav(firstAudioFile)
	sound2 = AudioSegment.from_wav(secondAudioFile)
	sound3 = sound1.append(sound2,crossfade=0)
	sound3.export(destination_path, format="wav")

def analyzeAudio(audio_url):
	y, sr = librosa.load(audio_url)
	tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
	beat_times = librosa.frames_to_time(beat_frames, sr=sr)
	return tempo, beat_times

def trimAudio(audio_url, time_in_seconds, output_file):
	t1 = time_in_seconds * 1000 #Works in milliseconds
	newAudio = AudioSegment.from_wav(audio_url)
	newAudio = newAudio[t1:]
	newAudio.export(output_file, format="wav") 
	return output_file

def convertMP3ToWav(mp3_audio_url, output_file):
	src = mp3_audio_url
	sound = AudioSegment.from_mp3(src)
	sound.export(output_file, format="wav")
	return output_file

def convertM4AToWav(m4a_audio_url, output_file):
	audio = AudioSegment.from_file(m4a_audio_url, format="m4a")
	audio.export(output_file, format="wav")
	return output_file

def convertWavToMP3(wav_audio_url, output_file):
	audio = AudioSegment.from_wav(wav_audio_url)
	audio.export(output_file, format="mp3", bitrate="192k")
	return output_file

def merge_audio_files(file1, file2, output_file):
	audio1 = AudioSegment.from_file(file1)
	audio2 = AudioSegment.from_file(file2)

	max_length = max(len(audio1), len(audio2))
	audio1 = audio1 + AudioSegment.silent(duration=max_length - len(audio1))
	audio2 = audio2 + AudioSegment.silent(duration=max_length - len(audio2))

	merged_audio = audio1.overlay(audio2)
	merged_audio.export(output_file, format="wav")

def insert_silence_to_beginning(input_path, output_path, silence_duration_seconds):
	original_audio = AudioSegment.from_wav(input_path)
	silence = AudioSegment.silent(duration=silence_duration_seconds * 1000)
	new_audio = silence + original_audio
	new_audio.export(output_path, format="wav")

def pitch_shift_wav(input_file, output_file, semitones):
    y, sr = librosa.load(input_file, sr=None)
    pitch_shift_factor = 2 ** (semitones / 12.0)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)
    sf.write(output_file, y_shifted, sr)

def createCountInTrack(config_file, output_file):
	bpm = config_file.bpm
	number_of_beats = config_file.number_of_beats
	measures = config_file.measures
	segments = []
	ms = (60/bpm) * 1000
	duration_ms = 100
	silence = AudioSegment.silent(duration=ms-duration_ms)
	
	for j in range(0, measures):
		for i in range(1, number_of_beats+1):
			file = "resources/click_stick_lowest_100ms.wav"
			if i == 1:
				file = "resources/click_stick_low_100ms.wav"
			segments.append(AudioSegment.from_wav(file))

	for i in range(0, config_file.additional_beats):
		file = "resources/click_HH_lowest_100ms.wav"
		if i % number_of_beats == 0:
			file = "resources/click_HH_low_100ms.wav"
		segments.append(AudioSegment.from_wav(file))

	output_segment = segments[0] + silence
	for segment in segments[1:]:
		output_segment = output_segment + segment + silence
	
	output_segment.export(output_file, format="wav")
	return output_file

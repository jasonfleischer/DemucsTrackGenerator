#!/usr/bin/python

# change to directory of script
# $ cd /Users/jason/Files/demucs_track_generator
# run the following
# $ python3 demucs_track_generator.py
# -or- run the following to build from scratch
# $ rm -R output; python3 demucs_track_generator.py

# Errors
# if, ModuleNotFoundError: No module named '<library name>'
# then, $ pip3 install <library name>
# ex: pip3 install demucs, pip3 install librosa

import subprocess
import os

from sources.log import Log
from sources.config_file import ConfigFile
from sources.beat_generator import BeepGenerator
from sources.file_util import *
from sources.audio_util import *

cwd = os.getcwd()
output_folder = f"{cwd}/output"
input_directory = f"{cwd}/input"

def main():

	if not os.path.isdir(output_folder):
		os.mkdir(output_folder)
	
	for filename in os.listdir(input_directory):
	    if os.path.isfile(os.path.join(input_directory, filename)):
	    	if filename != ".DS_Store" and not filename.endswith("json"):
	        	doWork(input_directory + "/" + filename)

	convertFilesToMP3()
	removeAllWAVFiles()

	remove_folder(f"{cwd}/separated")
	#copyBackingTracks()

def doWork(audio_url):
	Log.i("------------------------------")
	Log.i(f"Input file: {audio_url}")
	
	file_name = getFileName(audio_url)
	Log.accent(file_name)

	Log.i(f"Current working directory: {cwd}")
	output_dir = output_folder + "/" + file_name
	if os.path.isdir(output_dir):
		Log.w(f"!!! Skipping {file_name} : already created, remove folder if you want regeneration !!!\n")
		return
	else:
		os.mkdir(output_dir)
	
	if not audio_url.lower().endswith("wav"):
		Log.i("... Converting to Wav")
		output_file = f"{output_dir}/{file_name}.wav"
		if audio_url.lower().endswith("mp3"):
			audio_url = convertMP3ToWav(audio_url, output_file)
		elif audio_url.lower().endswith("m4a"):
			audio_url = convertM4AToWav("/" + audio_url, output_file)
		else:
			Log.i("!!! conversion only works with mp3 and m4a !!!\n")
			return

	Log.i(f"... Analyzing {audio_url}")
	bpms, beat_times = analyzeAudio(audio_url)
	first_beat_time = beat_times[0]

	first_found_bpm = bpms[0]

	Log.i(f"... found {first_found_bpm:.1f} BPM, first beat: {first_beat_time:.4f} secs, beat times count: {len(beat_times)}")


	Log.i("... Creating click track")
	click_file  = f"{output_dir}/{file_name} (click track ~{first_found_bpm:.1f} BPM).wav"
	count_in_url = createClickTrack(beat_times, click_file)

	Log.i("... Demucs audio seperation")
	runDemucs(audio_url, output_dir)
	demucs_output_dir = f"{cwd}/separated/htdemucs/{file_name}"
	drum_file = demucs_output_dir + "/drums.wav"
	vocal_file = demucs_output_dir + "/vocals.wav"
	other_file = demucs_output_dir + "/other.wav"
	bass_file = demucs_output_dir + "/bass.wav"

	Log.i("... Merging files")

	if os.path.exists(drum_file):	
		output_file = output_dir + "/" + file_name + " (no drums).wav"
		input_directory = demucs_output_dir
		instrument_file_names = []
		for filename in os.listdir(input_directory):
			if os.path.isfile(os.path.join(input_directory, filename)) and filename != "drums.wav":
				instrument_file_names.append(filename)
		if len(instrument_file_names) > 0:
			prev_instrument_file_path = demucs_output_dir + "/" + instrument_file_names[0]
			for i in range(1, len(instrument_file_names)):
				instrument_file_name = demucs_output_dir + "/" + instrument_file_names[i]
				merge_audio_files(prev_instrument_file_path, instrument_file_name, output_file)
				prev_instrument_file_path = output_file
		else:
			Log.e("!!! nothing to merge !!!")

	if os.path.exists(drum_file):
		output_file = f"{output_dir}/{file_name} (no vocals).wav"
		input_directory = demucs_output_dir
		instrument_file_names = []
		for filename in os.listdir(input_directory):
			if os.path.isfile(os.path.join(input_directory, filename)) and filename != "vocals.wav":
				instrument_file_names.append(filename)
		if len(instrument_file_names) > 0:
			prev_instrument_file_path = demucs_output_dir + "/" + instrument_file_names[0]
			for i in range(1, len(instrument_file_names)):
				instrument_file_name = demucs_output_dir + "/" + instrument_file_names[i]
				merge_audio_files(prev_instrument_file_path, instrument_file_name, output_file)
				prev_instrument_file_path = output_file
		else:
			Log.e("!!! nothing to merge !!!")


	pitchShift(file_name, [drum_file, vocal_file, other_file, bass_file])

	#if os.path.exists(drum_file) and os.path.exists(vocal_file):
	#	Log.i("... Merging vocal and drum files")
	#	output_file = output_dir + "/" + file_name + " (drums + vocal).wav"
	#	merge_audio_files(drum_file, vocal_file, output_file)

	drum_and_bass_file = f"{output_dir}/{file_name} (bass + drums).wav"
	if os.path.exists(drum_file) and os.path.exists(bass_file):
		Log.i("... Merging bass and drum files")
		merge_audio_files(drum_file, bass_file, drum_and_bass_file)
	else:
		Log.e(f"Error: missing either '{drum_file}' or '{bass_file}'")

	files_to_add_count_in_to = [audio_url, drum_and_bass_file]
	count_in_work(audio_url, file_name, first_found_bpm, first_beat_time, files_to_add_count_in_to)

	bass_drum_count_in = f"{output_dir}/{file_name} (bass + drums) (count in).wav"
	if file_exists(bass_drum_count_in):
		pre_append_silence(bass_drum_count_in, f"{output_dir}/{file_name} (bass + drums) (count in) (pre-silence).wav")

	Log.i("... Cleaning")
	for file in [drum_file, bass_file, other_file, vocal_file]:
		if os.path.exists(file):
			ext = file[file.index(".")+1:]
			copy_file(file, f"{output_dir}/{file_name} ({getFileName(file)}).{ext}")

	
	Log.i("------------------------------\n")

def count_in_work(audio_url, file_name, bpm, first_beat_time, files_to_add_count_in_to):

	json_data = get_file_contents(f'input/{file_name}.json')
	config_file = ConfigFile(bpm, 4, first_beat_time, 1, 0)
	
	if json_data is not None:
		config_file.from_json(json_data)

	Log.i(f"... Adding count in to file(s) with data:\n    {str(config_file)}") 
	count_in_audio_file = f"output/{file_name}/count_in.wav"
	createCountInTrack(config_file, count_in_audio_file)

	count_in_duration = config_file.duration()
	for file in files_to_add_count_in_to:

		if config_file.pitch_shift != 0:
			Log.i(f"... Pitch shifting {config_file.pitch_shift} semi-tones")
			output_url = file.replace(".wav", f" (shifted {config_file.pitch_shift} ST).wav") 
			pitch_shift_wav(file, output_url, config_file.pitch_shift)
			pre_append_silence(output_url, output_url.replace(".wav", " (pre-silence).wav"))
			file = output_url
		
		if config_file.first_beat_time < count_in_duration:
			diff = count_in_duration - config_file.first_beat_time
			
			audio_with_silence_file = f"output/{file_name}/{getFileName(file)}_silence_added.wav"
			insert_silence_to_beginning(file, audio_with_silence_file, diff)
			merge_audio_files(count_in_audio_file, audio_with_silence_file, f"output/{file_name}/{getFileName(file)} (count in).wav")
			remove_file(audio_with_silence_file)
		else:
			diff = config_file.first_beat_time - count_in_duration
			
			new_count_in_file = f"output/{file_name}/{getFileName(file)}_new_count_in.wav"
			insert_silence_to_beginning(count_in_audio_file, new_count_in_file, diff)
			merge_audio_files(new_count_in_file, file, f"output/{file_name}/{getFileName(file)} (count in).wav")
			remove_file(new_count_in_file)

	remove_file(count_in_audio_file)

def pitchShift(file_name, file_paths):

	json_data = get_file_contents(f'input/{file_name}.json')
	config_file = ConfigFile(-1, 4, -1, 1, 0)
	
	if json_data is not None:
		config_file.from_json(json_data)

	if config_file.pitch_shift == 0:
		return

	for file in file_paths:
		pitch_shift = config_file.pitch_shift
		Log.i(f"... Pitch shifting '{file}'' {pitch_shift} semi-tones")
		instrument_type = file[file.rfind('/') + 1: file.rfind('.')]
		output_url = f"{output_folder}/{file_name}/{file_name} ({instrument_type}) (shifted {pitch_shift} ST).wav" 
		pitch_shift_wav(file, output_url, pitch_shift)


def createClickTrack(beat_times, output_file):
	bg = BeepGenerator()
	prev_wave_duration = 0
	prev_beat_time = 0
	for beat_time in beat_times:
		ms = beat_time * 1000
		bg.append_silence(duration_milliseconds=ms-prev_wave_duration-prev_beat_time)
		volume = 0.75
		freq = 440
		duration_ms = 30
		bg.append_sinewave(volume=volume, duration_milliseconds=duration_ms, freq=freq)
		prev_wave_duration = duration_ms
		prev_beat_time = ms
	bg.save_wav(output_file)
	return output_file

def createCountInTrackOld(config_file, output_file):
	bg = BeepGenerator()
	bpm = config_file.bpm
	number_of_beats = config_file.number_of_beats
	measures = config_file.measures
	for j in range(0, measures):
		for i in range(1, number_of_beats+1):
			volume = 0.5
			freq = 220
			duration_ms = 30
			if i == 1:
				freq = 320
				volume = 0.75			
			ms = (60/bpm) * 1000
			bg.append_sinewave(volume=volume, duration_milliseconds=duration_ms, freq=freq)
			bg.append_silence(duration_milliseconds=ms-duration_ms)

	for i in range(0, config_file.additional_beats):
		volume = 0.25
		freq = 200
		duration_ms = 30
		if i % number_of_beats == 0:
			volume = 0.30
		ms = (60/bpm) * 1000
		bg.append_sinewave(volume=volume, duration_milliseconds=duration_ms, freq=freq)
		bg.append_silence(duration_milliseconds=ms-duration_ms)

	bg.save_wav(output_file)
	return output_file

def pre_append_silence(source_path, destination_path):
	insert_silence_to_beginning(source_path, destination_path, 1.5)

def runDemucs(source_path, destination_path):	
	p = subprocess.Popen('python3 -m demucs.separate "' + source_path + '"', stdout=subprocess.PIPE, shell=True )
	Log.i(p.communicate())
	Log.i("Finished demucs")

def convertFilesToMP3():
	for root, dirs, files in os.walk(output_folder):
		Log.i(f"... Converting files to mp3 in: {root}")
		for file in files:
			if file.endswith(".wav"):
				file_path = os.path.join(root, file)
				output_path = file_path.replace(".wav", ".mp3")
				if file_exists(output_path):
					Log.w(f"!!! Skipping {output_path} : already exists")
				else:
					convertWavToMP3(file_path, output_path)

def removeAllWAVFiles():
	for root, dirs, files in os.walk(output_folder):
		Log.i(f"... Removing WAV files in: {root}")
		for file in files:
			if file.endswith(".wav"):
				file_path = os.path.join(root, file)
				remove_file(file_path)

def copyBackingTracks():
	backing_track_output_folder = f"{cwd}/output - backing tracks"
	if not os.path.isdir(backing_track_output_folder):
		os.mkdir(backing_track_output_folder)
	Log.i(f"... Copying files to: {backing_track_output_folder}")
	for root, dirs, files in os.walk(output_folder):
		for file in files:
			if file.endswith("(bass + drums) (count in).mp3"):
				file_path = os.path.join(root, file)
				copy_file_to_folder(file_path, backing_track_output_folder)				

os.system('clear')	
Log.i("\nSTART demucs_track_generator\n")
main()
Log.i("FINISHED")

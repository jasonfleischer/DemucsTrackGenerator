#!/usr/bin/python3

import numpy as np
import scipy.io.wavfile

class BeepGenerator:
	def __init__(self):
		self.audio = []
		self.sample_rate = 44100.0

	def append_silence(self, duration_milliseconds=500):
		num_samples = duration_milliseconds * (self.sample_rate / 1000.0)
		for x in range(int(num_samples)):
			self.audio.append(0.0)
		return

	def append_sinewave(
			self,
			freq=440.0,
			duration_milliseconds=500,
			volume=1.0):

		num_samples = duration_milliseconds * (self.sample_rate / 1000.0)
		x = np.array([i for i in range(int(num_samples))])
		sine_wave = volume * np.sin(2 * np.pi * freq * (x / self.sample_rate))
		self.audio.extend(list(sine_wave))
		return

	def append_sinewaves(
			self,
			freqs=[440.0],
			duration_milliseconds=500,
			volumes=[1.0]):

		volumes = list(np.array(volumes)/sum(volumes))
		num_samples = duration_milliseconds * (self.sample_rate / 1000.0)
		x = np.array([i for i in range(int(num_samples))])

		first_it = True
		for volume, freq in zip(volumes, freqs):
			print(freq)
			if first_it:
				sine_wave = volume * np.sin(2 * np.pi * freq * (x / self.sample_rate))
				first_it = False
			else:
				sine_wave += volume * np.sin(2 * np.pi * freq * (x / self.sample_rate))

		self.audio.extend(list(sine_wave))
		return

	def save_wav(self, file_name):
		self.audio = np.array(self.audio).astype(np.float32)
		scipy.io.wavfile.write(file_name, int(self.sample_rate), np.array(self.audio))
		return

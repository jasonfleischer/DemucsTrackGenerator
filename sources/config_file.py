#!/usr/bin/python3

import json

class ConfigFile:
	def __init__(self, bpm=120, number_of_beats=4, first_beat_time=0.0, measures=1, beat_offset=0, pitch_shift=0, additional_beats=0):
		self.bpm = bpm
		self.number_of_beats = number_of_beats
		self.first_beat_time = first_beat_time
		self.measures = measures
		self.beat_offset = beat_offset
		self.pitch_shift = pitch_shift
		self.additional_beats = additional_beats

	def from_json(self, json_data):
		data = json.loads(json_data)
		self.bpm = data.get('bpm', self.bpm)
		self.number_of_beats = data.get('number_of_beats', self.number_of_beats)
		self.first_beat_time = data.get('first_beat_time', self.first_beat_time)
		self.measures = data.get('measures', self.measures)
		self.beat_offset = data.get('beat_offset', self.beat_offset)
		self.pitch_shift = data.get('pitch_shift', self.pitch_shift)
		self.additional_beats = data.get('additional_beats', self.additional_beats)

	def duration(self):
		return ((60/self.bpm) * self.number_of_beats * self.measures) - ((60/self.bpm)*self.beat_offset)

	def __str__(self):
		return f"count-in: {self.bpm:.1f} BPM, {self.number_of_beats} beats for {self.measures} measure(s), first beat time: {self.first_beat_time:.4f} secs, offset: {self.beat_offset}, pitch shift: {self.pitch_shift} semi-tones, additional beats: { self.additional_beats }"

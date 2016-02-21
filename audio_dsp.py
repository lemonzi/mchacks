#! /usr/bin/env python

""" This module contains the DSP pipeline """

import sys
from aubio import onset, pitch
import numpy as np
import scipy.io.wavfile as sciwav
from math import ceil
import time
from pv import PhaseVocoder
import subprocess
import os


def detect_onset(sig, fs):
    """ Detect the onset of sound event
    Returns: (onset, offset) tuple of indecies """
    win_s = 512          # fft size
    hop_s = win_s / 2    # hop size

    o = onset("hfc", win_s, hop_s, fs)

    # list of onsets, in samples
    onsets = []

    # storage for plotted data
    desc = []
    tdesc = []
    allsamples_max = np.zeros(0,)
    downsample = 2  # to plot n samples / hop_s

    # total number of frames read
    total_frames = 0
    i = 0
    while i + hop_s < len(sig[:,0]):
        samples = sig[i:i+hop_s][:,0] # LEFT CHANNEL!
        if o(samples):
            # print "%f" % (o.get_last_s())
            # onsets.append((o.get_last(), samples))
            onsets.append(o.get_last())

        # keep some data to plot it later
        new_maxes = (abs(samples.reshape(hop_s/downsample, downsample))).max(axis=0)
        allsamples_max = np.hstack([allsamples_max, new_maxes])
        desc.append(o.get_descriptor())
        tdesc.append(o.get_thresholded_descriptor())
        total_frames += hop_s
        i += hop_s

    allsamples_max = (allsamples_max > 0) * allsamples_max
    allsamples_max_times = [float(t) * hop_s / downsample / fs for t in range(len(allsamples_max)) ]

    # this is the onset corr. to the peak in energy in signal
    max_energy_onset = int(float(np.argmax(allsamples_max)) * hop_s / downsample)
    return min(onsets, key=lambda x:abs(x - max_energy_onset))


def extract_pitch(sig, fs):
    """ Extract MIDI pitch of signal """
    downsample = 1
    samplerate =  fs

    win_s = 4096 / downsample # fft size
    hop_s = 512  / downsample # hop size

    tolerance = 0.8

    #['default', 'schmitt', 'fcomb', 'mcomb', 'yin', 'yinfft']
    pitch_o = pitch("default", win_s, hop_s, samplerate)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)

    pitches = []
    confidences = []

    # total number of frames read
    i = 0
    while i + hop_s < len(sig[:,0]):
        samples = sig[i:i+hop_s][:,0]
        my_pitch = pitch_o(samples)
        #pitch = int(round(pitch))
        confidence = pitch_o.get_confidence()
        #if confidence < 0.8: pitch = 0.
        #print "%f %f %f" % (total_frames / float(samplerate), pitch, confidence)
        pitches += [my_pitch]
        confidences += [confidences]
        i += hop_s

    pitches = np.array(pitches)
    pitches = pitches[pitches > 10]
    return np.median(pitches)    # we return the median of the frequencies found


def speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[ indices.astype(int) ]


def stretch(sound_array, f, window_size, h):
    """ Stretches the sound by a factor `f` """

    phase  = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros( len(sound_array) /f + window_size)

    for i in np.arange(0, len(sound_array)-(window_size+h), h*f):

        # two potentially overlapping subarrays
        a1 = sound_array[i:i+window_size]
        a2 = sound_array[i+h:i+window_size+h]

        # resynchronize the second array on the first
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)
        phase = (phase + np.angle(s2/s1)) % 2*np.pi
        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))

        # add to result
        i2 = int(i/f)
        result[i2:i2+window_size] += hanning_window * a2_rephased

    result = ((2**(16-4)) * result/result.max())  # normalize (16bit)

    return result.astype('int16')


def pitchshift(snd_array, n, window_size=2**10, h=2**8):
    """ Changes the pitch of a sound by ``n`` semitones. """
    # factor = 2**(1.0 * n / 12.0)
    snd_array = snd_array[:, 0]    # Use left channel
    factor = n
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)


def midi2Hz(midi_pitch):
    """ Convert from MIDI notes to Hz """
    return 2**((midi_pitch-69.)/12.) * 440


def Hz2midi(f):
    """ Convert from Hz to MIDI notes """
    return 69 + 12*np.log2(f/440.)

def fade_in_out(new_sig):
    N = 1024*8
    triag = np.ones(len(new_sig))
    triag[:N] = np.arange(N) / N
    #triag[-N:] = np.arange(N, 0, -1) / N
    new_sig = new_sig * triag
    #new_sig[:,1] = new_sig[:,1] * triag
    return new_sig


def process_audio(filename, sound=None):
    if not sound: sound = filename[:-4]

    fs, stereo_data = sciwav.read(filename)
    norm = abs(stereo_data.max()) * 1.3
    stereo_data = np.array(stereo_data / norm, dtype='float32')

    # detect onset of sound action and apply to signal
    onset_pos = detect_onset(stereo_data, fs)
    sig = stereo_data[onset_pos:]

    # Quantize pitch to nearest semitone
    midi_pitch = extract_pitch(sig, fs)
    base_pitch = ceil(midi_pitch)

    tones = range(-5, 5)  # scope of midi pitches
    upper_limit = fs      # one second of data

    pv = PhaseVocoder()

    epoch_time = str(int(time.time()))
    midi_notes = []
    filenames = []
    for t in tones:
        scaling_factor = midi2Hz(base_pitch+t) / midi2Hz(midi_pitch)
        #new_sig = speedx(sig[:,0], scaling_factor)
        new_sig = pv.pitchshift(sig[:,0], scaling_factor)
        if len(new_sig) > upper_limit:
            new_sig = new_sig[:upper_limit]
        new_sig = fade_in_out(new_sig)

        # filename: {sound}_{midi}_{time since epoch}.wav
        midi_note = str(int(base_pitch+t))
        midi_notes.append(midi_note)

        new_filename = "{}_{}_{}.wav".format(sound, midi_note, epoch_time)
        filenames.append(new_filename)
        new_sig = new_sig * 32768;
        sciwav.write(new_filename, fs, new_sig.astype(np.int16))

        # convert to mp3
        file = new_filename[:-4]


    for f in filenames:
        cmd = ["ffmpeg", "-loglevel", "panic", "-i", f, f[:-4] + '.mp3']
        subprocess.call(cmd, shell=False)
        os.remove(f)

    return midi_notes, epoch_time


if __name__ == '__main__':
    process_audio(sys.argv[1])

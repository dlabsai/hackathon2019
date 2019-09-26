import pyaudio
import wave
import os
import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from tts import synthesize_text_with_audio_profile

RETRY_COUNT = 0

def listen_for_speech(time: int):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second
    seconds = time
    filename = "output.wav"
    
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    
    print('Recording')
    
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    
    frames = []  # Initialize array to store frames
    
    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
    
    print('Finished recording')
    
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


def save_speech(data, p):
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """

    filename = 'output_'+str(int(time.time()))
    # writes data to WAV file
    data = ''.join(data)
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)  # TODO make this value a function parameter?
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'


def stt_google_wav(audio_fname):
    """ Sends audio file (audio_fname) to Google's text to speech 
        service and returns service's response. We need a FLAC 
        converter if audio is not FLAC (check FLAC_CONV). """

    print("Sending ", audio_fname)
    #Convert to flac first
    filename = audio_fname

    # Instantiates a client
    client = speech.SpeechClient()
    
    # The name of the audio file to transcribe
    file_name = 'output.wav'
    
    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
    
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='pl-pl')
    
    # Detects speech in the audio file
    response = client.recognize(config, audio)
    
    if len(response.results) == 0:
        synthesize_text_with_audio_profile('Przepraszam, nic nie słyszę.')
    
    for result in response.results:
        if result == "":
            synthesize_text_with_audio_profile('Przepraszam, nic nie słyszę.')
            break
        print('Transcript: {}'.format(result.alternatives[0].transcript))
        if result.alternatives[0].confidence < 0.75:
            synthesize_text_with_audio_profile('Przepraszam, nie zrozumiałam. Czy możesz powtórzyć?')
        else:
            return result.alternatives[0].transcript
            
    os.remove(filename)  # Remove temp file
    return ""


if(__name__ == '__main__'):
    while 1:
        listen_for_speech(4)  # listen to mic.
        result = stt_google_wav('output.wav')  # translate audio file
        if result != "":
            break
        RETRY_COUNT += 1
        if RETRY_COUNT == 3:
           synthesize_text_with_audio_profile('Chyba nie mogę Ci pomóc, przekieruje Naszą rozmowe do innego konsultanta')
           break
        
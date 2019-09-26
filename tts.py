def synthesize_text_with_audio_profile(text, effects_profile_id='handset-class-device'):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech
    import pyaudio
    import wave
    import sys

    # length of data to read.
    chunk = 1024
    
    # create an audio object
    p = pyaudio.PyAudio()
    
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(ssml=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(language_code='pl-pl', ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    # Note: you can pass in multiple effects_profile_id. They will be applied
    # in the same order they are provided.
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        effects_profile_id=[effects_profile_id])

    response = client.synthesize_speech(input_text, voice, audio_config)


    # The response's audio_content is binary.
    with open('output.wav', 'wb') as out:
        out.write(response.audio_content)
        
    wf = wave.open('output.wav', 'rb')
    # open stream based on the wave object which has been input.
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
    
    # read data (based on the chunk size)
    data = wf.readframes(chunk)
    
    # play stream (looping from beginning of file to the end)
    while data != b'':
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)
        
    # cleanup stuff.
    stream.close()    
    p.terminate()
    wf.close()
    return


if(__name__ == '__main__'):
    synthesize_text_with_audio_profile('<speak>Siema Aleks<break time="500ms"/> jestem Alicja z Medicover!</speak>', "handset-class-device")
    #synthesize_text_with_audio_profile('Przepraszam, nic nie słyszę.')


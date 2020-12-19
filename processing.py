def jinglematic(music_file):
    import librosa,librosa.display
    import librosa,librosa.display
    import numpy as np
    import soundfile as sf
    from os.path import isfile, join
    from os import listdir, path, remove
    import os, time

    from pydub import AudioSegment
    import pychorus as pyc
    import pyloudnorm as pyln
    import random as rnd

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    NumJingle = 5
    include_upbeats = False
    tightness = 200
    bellvol_adj = 1  # higher values reduce volume of bells.  (1 - 4)
    rnd.seed()

    xy, sr = librosa.load(music_file, sr=44100)

    song_file_path = music_file
    #output_file = root.file + "_jingled.mp3"
    song_file = os.path.basename(music_file)
    song_name = os.path.splitext(song_file)[0]
    output_file = os.path.dirname(music_file) + "/" + os.path.splitext(song_file)[0] + "_jingled.mp3"

    ps_files_path = dname + '/output files/'
    jingle_path = dname + '/SFX/jingle/'

    # fetch the bells
    jingle = [j for j in sorted(listdir(jingle_path)) if isfile(join(jingle_path,j))]

    # fetch the horses
    clipclop1, sr = librosa.load(dname +"/SFX/woodblock1.wav", sr=44100)
    clipclop2, sr = librosa.load(dname +"/SFX/woodblock2.wav", sr=44100)
    harp, sr = librosa.load(dname +"/SFX/harp.wav", sr=44100)
    whip, sr = librosa.load(dname +"/SFX/whip.wav", sr=44100)
    handbell, sr = librosa.load(dname +"/SFX/bell_c.wav", sr=44100)
    hoho1, sr = librosa.load(dname +"/SFX/ho_01.wav", sr=44100)
    hoho2, sr = librosa.load(dname +"/SFX/ho_02.wav", sr=44100)
    hoho3, sr = librosa.load(dname +"/SFX/ho_03.wav", sr=44100)


    # each sleighbell sound effect is ever so slightly off the beat
    # this finetunes the timing so they hit directly on downbeats
    finetune = [3,3,7,3,5,3]


    # Load file
    #xy, sr = librosa.load(song_file_path, sr=44100)
    bell, sr = librosa.load(jingle_path + jingle[NumJingle], sr=44100)
    sleighbell, sr = librosa.load(jingle_path + jingle[2], sr=44100)

    # find tempo and beats
    tempo, beat_frames = librosa.beat.beat_track(y=xy, sr=sr, tightness=tightness, trim=True)

    # calculate the average loudness of the track to help set jingle audio levels
    meter = pyln.Meter(sr) # create BS.1770 meter
    loudness = meter.integrated_loudness(xy) # measure loudness

    # sloppy curve fitting to slightly adjust bell volume based on detected loudness
    bellvol_adj = 4.02933 + (1.128807 - 4.02933)/(1 + (-loudness/15.20084)**22.80542)

    # Determine the key of the song and load the appropriate church bells

    # get song chroma
    chroma_cq = librosa.feature.chroma_cqt(xy, sr)
    song_chroma = list(np.mean(chroma_cq,1))

    # pitches in 12 tone equal temperament
    pitches = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

    # print note to value relations
    # for y in range(len(song_chroma)):
    #    print(str(pitches[y]) + '\t' + str(song_chroma[y]))

    # select the most dominant pitch
    pitch_id = song_chroma.index(max(song_chroma))
    pitch = pitches[pitch_id]

    min_third_id = (pitch_id+3)%12
    maj_third_id = (pitch_id+4)%12

    #check if the musical 3rd is major or minor
    if song_chroma[min_third_id] < song_chroma[maj_third_id]:
        third = 'major'
    elif song_chroma[min_third_id] > song_chroma[maj_third_id]:
        third = 'minor'


    # if minor key go three half steps up.
    if third == 'minor':
        adj_key = pitch_id + 3
    else:
        adj_key = pitch_id

    if adj_key > 11:
        adj_key = adj_key - 12

    songkey = pitches[adj_key]
    if adj_key > 6:
        adj_key = adj_key-12

    if third == 'minor':
        print(str.format('Adjusted to {} major',pitches[adj_key]))

    # shift the pitch of the handbells so they're in key
    # default key of C
    # pitches[0] is C

    handbell1 = librosa.effects.pitch_shift(handbell, sr, n_steps=adj_key, bins_per_octave=12)
    handbell2 = librosa.effects.pitch_shift(handbell, sr, n_steps=adj_key-5, bins_per_octave=12)

    #y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=4, bins_per_octave=24)
    #churchbells, sr = librosa.load(dname +'/SFX//churchbells//churchbells_' + songkey + '.wav', sr=44100)

    ## So since pychorus can only find one chorus per audio file
    ## I could divide the audio files into half with np.split, and find the best chorus in first and second half
    ## and add clipclops to both.  Or parameterize it into several splits.

    # take it apart
    xy1, xy2 = np.array_split(xy,2)

    # put 'er back together
    #xyc = np.concatenate((xy1,xy2))

    # it would be nice to find two choruses
    # but we'll settle for one
    chorus_start_1 = pyc.find_and_output_chorus_nparray(xy1, sr, None, 10)
    chorus_start_2 = None

    if chorus_start_1 is None:
        chorus_start_1 = pyc.find_and_output_chorus_nparray(xy, sr , None, 15)
    else:
        chorus_start_2 = pyc.find_and_output_chorus_nparray(xy2, sr, None, 10)
        if chorus_start_2 != None:
                chorus_start_2 = chorus_start_2 + librosa.get_duration(xy1)

    # if there's no chorus found at all, let's just pretend it's at the halfway mark.
    if chorus_start_1 is None:
        chorus_start_1 = librosa.get_duration(xy,sr)/2

    # tweaking the beatmap just a pinch so the jingles land right on the beats
    beat_frames = beat_frames - finetune[NumJingle]

    # delete any that are less than zero after shifting
    beat_frames = beat_frames[beat_frames > 0]

    if tempo <= 100:
       include_upbeats = True

    if include_upbeats == True:
        upbeat_frames = (beat_frames[1:] + beat_frames[:-1]) / 2
        beat_frames = np.sort(np.concatenate((beat_frames,upbeat_frames)))


    # Get the beat times and create click track
    beat_times = librosa.frames_to_time(beat_frames)

    # get frame start for chorus
    librosa.time_to_frames(chorus_start_1, sr, hop_length=1024, n_fft=None)
    chorus1_start_frame = librosa.time_to_frames(chorus_start_1,sr)

    # add clipclops
    clipclop_frames = beat_frames[beat_frames > chorus1_start_frame]

    # limit it to 32 clipclops
    clipclop_frames = clipclop_frames[clipclop_frames < clipclop_frames[32]]

    # and upbeats for a different clop sound
    clipclop_upbeat_frames = (clipclop_frames[1:] + clipclop_frames[:-1]) / 2

    # adding a second upbeat to emulate a horse cadence
    clipclop_quarter_frames = clipclop_upbeat_frames[:-1] + np.diff(clipclop_upbeat_frames)/4
    clipclop_quarter_frames = np.concatenate((clipclop_quarter_frames[:8],clipclop_quarter_frames[20:28]))
    clipclop_upbeat_frames = np.sort(np.concatenate((clipclop_upbeat_frames,clipclop_quarter_frames)))

    # add some jingle to the chorus downbeats.
    # numpy gets sassy with mismatched array sizes, fill the short one with 0s
    clipclop1 = clipclop1 + np.concatenate((sleighbell,np.zeros(len(clipclop1)-len(sleighbell))))

    # build the clipclop track (with slight frame adjustment for timing)
    clip_clops = librosa.clicks(frames=clipclop_frames, sr=sr, click = clipclop1, length=len(xy))
    clip_upclops = librosa.clicks(frames=clipclop_upbeat_frames, sr=sr, click = clipclop2, length=len(xy))

    # Roll all the clipclops back together into a single array
    clip_clops = clip_clops + clip_upclops

    # let's drop in some churchbells to keep the horses company on the 1st and 16th beat of the chorus
    # random hoho preceding chorus
    hoho = eval("hoho" + str(rnd.randint(1,3)))
    harp_indices = [0,28]
    whip_indices = [6,12,20]

    harp_sound = librosa.clicks(frames=np.take(clipclop_frames, harp_indices), sr=sr, click = harp, length=len(xy))
    whip_sound = librosa.clicks(frames=np.take(clipclop_frames, whip_indices), sr=sr, click = whip, length=len(xy))
    hoho_sound = librosa.clicks(frames=librosa.time_to_frames(chorus_start_1-1,sr), sr=sr, click = hoho, length=len(xy))

    # pull the jingles out where clipclops exist.
    beat_frames = np.array([i for i in beat_frames if i not in clipclop_frames])

    # Drop in a second chorus if it exists
    if chorus_start_2 != None:
        # get frame start for chorus to add clipclops
        chorus2_start_frame = librosa.time_to_frames(chorus_start_2,sr,1024)
        clipclop_frames2 = beat_frames[beat_frames > chorus2_start_frame]

        # limit it to 32 clipclops
        clipclop_frames2 = clipclop_frames2[clipclop_frames2 < clipclop_frames2[32]]

        # and upbeats for a different clop sound
        clipclop_upbeat_frames2 = (clipclop_frames2[1:] + clipclop_frames2[:-1]) / 2

        # adding a second upbeat to emulate a horse cadence
        clipclop_quarter_frames2 = clipclop_upbeat_frames2[:-1] + np.diff(clipclop_upbeat_frames2)/4
        clipclop_quarter_frames2 = np.concatenate((clipclop_quarter_frames2[:8],clipclop_quarter_frames2[20:28]))
        clipclop_upbeat_frames2 = np.sort(np.concatenate((clipclop_upbeat_frames2,clipclop_quarter_frames2)))

        # build the clipclop track (with slight frame adjustment for timing)
        clip_clops2 = librosa.clicks(frames=clipclop_frames2, sr=sr, click = clipclop1, length=len(xy))
        clip_upclops2 = librosa.clicks(frames=clipclop_upbeat_frames2, sr=sr, click = clipclop2, length=len(xy))

        clip_clops2 = clip_clops2 + clip_upclops2

        # build the clipclop track (with slight frame adjustment for timing)
        clip_clops = clip_clops + clip_clops2

        # let's drop in some churchbells to keep the horses company on the 1st and 16th beat of the chorus
        # random hoho preceding chorus
        hoho = eval("hoho" + str(rnd.randint(1,3)))
        harp_indices = [0,28]
        whip_indices = [6,12,20]

        harp_sound = harp_sound + librosa.clicks(frames=np.take(clipclop_frames2, harp_indices), sr=sr, click = harp, length=len(xy))
        whip_sound = whip_sound + librosa.clicks(frames=np.take(clipclop_frames2, whip_indices), sr=sr, click = whip, length=len(xy))
        hoho_sound = hoho_sound + librosa.clicks(frames=librosa.time_to_frames(chorus_start_2-1), sr=sr, click = hoho, length=len(xy))

        # pull the jingles out where clipclops exist.
        beat_frames = np.array([i for i in beat_frames if i not in clipclop_frames2])

    # make the jingle track
    beat_clicks = librosa.clicks(frames=beat_frames, sr=sr, click = bell, length=len(xy))

    # Add in some handbells tuned to the key of the song
    handbell_frames = beat_frames[::8]
    handbell2_frames = beat_frames[4::8]

    handbell1_sound = librosa.clicks(frames=handbell_frames, sr=sr, click = handbell1, length=len(xy))
    handbell2_sound = librosa.clicks(frames=handbell2_frames, sr=sr, click = handbell2, length=len(xy))

    handbell_sound = handbell1_sound + handbell2_sound

    # Combine all our ingredients together
    mixed = xy + (
            beat_clicks / bellvol_adj) + (
            clip_clops / (bellvol_adj * 2)) +  (
            harp_sound / (bellvol_adj * 2)) + (
            whip_sound / bellvol_adj) + (
            hoho_sound/ bellvol_adj +
            handbell_sound / (bellvol_adj * 10 )
            )

    sf.write(output_file + ".wav", mixed, sr)
    AudioSegment.from_wav(output_file + ".wav").export(output_file, bitrate="192k", format="mp3") #
    os.remove(output_file + ".wav")
    os.remove(music_file)

    jingled_filename = os.path.basename(output_file)

    # delete any files more than 10 minutes old
    cleanpath = os.path.dirname(music_file)
    now = time.time()

    for filename in os.listdir(cleanpath):
        filestamp = os.stat(os.path.join(cleanpath, filename)).st_mtime
        filecompare = now - 600
        if filestamp < filecompare:
            removefile = cleanpath + '/' + filename
            os.remove(removefile)


    return(jingled_filename)
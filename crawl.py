from abjad import indicatortools, templatetools, Chord, Staff, Note, show, Measure, Duration, NamedPitch, TimeSignature, attach, Score
import itertools
#from pprint import pprint

TARGET_CHORD = Chord("<a, e' a' c''>4")
TARGET_CHORD = Chord("<f c' f' a'>4")

def get_all_source_chords_pitches(target_chord):
    pitch_count = len(target_chord.written_pitches)
    for pitch_shifts in itertools.product([-1, 1], repeat=pitch_count):
        yield list(get_source_chord_pitches(target_chord, pitch_shifts))

def get_source_chord_pitches(target_chord, pitch_shifts):
    for target_pitch, pitch_shift in zip(target_chord.written_pitches, pitch_shifts):
        source_pitch = target_pitch - pitch_shift
        if source_pitch.diatonic_pitch_class_name == target_pitch.diatonic_pitch_class_name:
            source_pitch = flip_accidental(source_pitch)
        yield source_pitch

def flip_accidental(pitch):
    if not pitch.alteration_in_semitones:
        return pitch
    elif pitch.alteration_in_semitones > 0:
        return pitch.respell_with_flats()
    return pitch.respell_with_sharps()

def split_to_hands(pitches):
    righthand_pitches = pitches[1:]
    lefthand_pitches = pitches[:1]
    # for pitch in pitches:
    #     if pitch >= NamedPitch("b"):
    #         righthand_pitches.append(pitch)
    #     else:
    #         lefthand_pitches.append(pitch)
    return Chord(righthand_pitches, Duration(1, 4)), Chord(lefthand_pitches, Duration(1, 4))

def crawl_to_target_chord(target_chord):
    score = templatetools.TwoStaffPianoScoreTemplate()()
    righthand, lefthand = score[0]
    target_chord_righthand, target_chord_lefthand = split_to_hands(target_chord.written_pitches)
    #print target_chord_righthand, target_chord_lefthand

    all_source_chords_pitches = list(get_all_source_chords_pitches(target_chord))
    #pprint(all_source_chords_pitches)
    for source_chord_pitches in all_source_chords_pitches:
        righthand_chord, lefthand_chord = split_to_hands(source_chord_pitches)
        for staff, chord, target_chord in (
            (righthand, righthand_chord, target_chord_righthand),
            (lefthand, lefthand_chord, target_chord_lefthand)
        ):
            staff.append(chord)
            staff.append(Chord(target_chord.written_pitches, Duration(1, 4)))

    time_signature = TimeSignature((2, 4))
    attach(time_signature, score, scope=Score)
    bar_line = indicatortools.BarLine("|.")
    attach(bar_line, righthand[-1])

    return score

def main():
    score = crawl_to_target_chord(TARGET_CHORD)
    show(score)

if __name__ == "__main__":
    main()

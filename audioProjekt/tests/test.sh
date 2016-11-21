#!/bin/bash
for i in *_*_*_*.wav; do
    t="$(echo "$i" |cut -d _ -f 1)"
    f0="$(echo "$i" |cut -d _ -f 2)"
    f1="$(echo "$i" |cut -d _ -f 3)"
    echo ""
    echo "============================================================================="
    echo "      Running at $t symbols per second, Frequencies ${f0}Hz and ${f1}Hz      "
    echo "-----------------------------------------------------------------------------"
    echo __PULSEAUDIO_WAVFILE__="$i" python ./recv.py "$t" "$f0" "$f1"
    echo "-----------------------------------------------------------------------------"
    echo  Result:
    __PULSEAUDIO_WAVFILE__="$i" python ../recv.py "$t" "$f0" "$f1"
    echo ""
    echo "-----------------------------------------------------------------------------"
done

arecord -f cd | aplay


arecord -f cd -d 3 test.wav && aplay test.wav
arecord -D hw:0,0 -f cd -c1 -d 5 test_internal.wav && aplay test_internal.wav

 ./micclient-x86_64.AppImage -t wifi 10.42.0.146

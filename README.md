# Creeksea Sailing Club Timer v1

Press **SEQ 1** or **SEQ 2** start sequences.
The corresponding LED will light for the duration of a sequence.
Press **RESET** button to interrupt a running sequence.
Please wait for green **READY** light before starting a new sequence.

To edit a sequence, connect the Raspberry Pi (RPi) to keyboard using USB and a monitor using HDMI. Boot the RPI, and login using ‘pi’, password ‘raspberry’. Use the nano utility to edit either seq1.csv or seq2.csv:
```
> nano seq2.csv
```

Edit the file, then use CTRL-O to save the file, and CRTL-X to exit.
To shutdown the Rpi type:
```
> sudo shutdown -h now
```

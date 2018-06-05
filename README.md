# wolfenhelper
https://github.com/fizux/wolfenhelper <br>
Assistant for classic Castle Wolfenstein (1981-1984).

## tl;dr:

python3 + tkinter based assistant with some optional light "adjustments" to the save game file.

Version 0.1<br>
Initial commit, we got a long way to go.  Please feel free to help.

run with:<br>
`python3 wolfenhelper.py`

## dosbox / dosbox-x sample config
in dosbox_settings/ :<br>
- dosbox.conf goes in my home directory and mounts the dosbox directory as c: in DOS
- CW.BAT goes in the dosbox directory and sets CPU cycles to 160 before running cw.exe
(otherwise the game is essentially unplayable)


## Basic game controls:
<br>
<b>Movement</b>: use these keys for directional movement.<br>
Q W E<br>
A S D<br>
Z X C<br>

S = stop.

<b>Aiming</b>: use these keys to aim your weapon.<br>
I O P<br>
K L ;<br>
, . /

L = fire bullet.<br>
T = toss grenade (in direction of pistol).<br>
H = holster pistol.<br>

\<space> = all purpose action button.<br>
   (open chest, try to open door with keys, search body or held-up guard)<br>
\<enter> = show inventory.<br>
ESC = return to menu screen; also saves current state in CASTLE file.<br>
U = Use (grab stuff from chests).<br>

Movement and Aiming keys can be reversed with Ctrl-R in the menu.


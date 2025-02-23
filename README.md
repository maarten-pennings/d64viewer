# D64viewer

Python program to dump a Commodore 64 floppy image (D64) in various ways


## Introduction

I wanted to understand the D64 files used in retro Commodore 64 systems.
A D64 file [stores](https://www.c64-wiki.com/wiki/D64) a complete floppy disk of a 1541 drive.
So, understanding D64 also means deepening my knowledge on the 1541 drives.

By the way, I use the term disk _block_ for an arbitrary block of 256 bytes.
Most people use the word sector when I use block, but I wanted to reserve sector 
for a part of a track. 

The program allows to select a _topic_ (an arbitrary disk block, the BAM, a directory, a file, the whole disk).
And the program has different _view_ modes (hex dump, view as bam, dir, basic file).
Finally, there are modifiers for the view mode (show block id, show headers, show help notes)

Here is the command line documentation (use `--help`)

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64 --help
usage: d64viewer [-h] [--tblock blockix | --tbam | --tdir [TDIR] | --tfile filename | --tdisk]
                 [--vhex | --vbam | --vdir | --vbasic] [--mtech [MTECH]] [--mblockid] [--mheader]
                 [--mnotes] [--mcont num] [--msave filename]
                 filename

Prints disk blocks inside a d64 file in hex/bam/dir/basic format

positional arguments:
  filename

options:
  -h, --help        show this help message and exit

topic:
  Select which disk blocks to print, default is --tdir

  --tblock blockix  topic is a disk block, pass either <num> (0..682) or <track>/<sector>
                    (1..35/0..16|17|18|20)
  --tbam            topic is the block availability matrix
  --tdir [TDIR]     topic is the directory, pass nothing or 1..18
  --tfile filename  topic is a file, pass filename (optionally enclosed in '' or "")
  --tdisk           topic is disk overview

view:
  Which view is used for the selected block, default is "implied by topic"

  --vhex            view as raw hex table (always "tech")
  --vbam            view as BAM table
  --vdir            view as directry entries
  --vbasic          view as basic program (must start with first block of program)

modifiers:
  Allows to add/suppress features of the view

  --mtech [MTECH]   modify view to be more tech (0, 1, 2)
  --mblockid        modify view with *no* blockid's
  --mheader         modidy view with *no* column headers
  --mnotes          modify view with documentation notes
  --mcont num       modify view by continuing with next blocks (tdir and vbasic have own defaults)
  --msave filename  saves the selected disk blocks to file (raw, not the view), pass filename
```


## How to use

- The Python program is in [viewer](viewer) directory. Download it on your system.
- Make sure you have the python binary on your system.
  For me it is in `C:\Programs\Python\python.exe`.
- Edit `setup.bat` to ensure the 3rd line (`SET LOCATION=C:\Programs\Python\`) reflects that location.
- Run `setup.bat`. It prepares a virtual environment (in directory local `env`).
- Run the python program via `run`. Pass appropriate arguments, at least a `.d64` file.


This was my `setup` output.

```
C:\Repos\d64viewer\viewer>setup
Requirement already satisfied: pip in c:\repos\d64viewer\viewer\env\lib\site-packages (22.3.1)
Collecting pip
  Using cached pip-25.0.1-py3-none-any.whl (1.8 MB)
Requirement already satisfied: setuptools in c:\repos\d64viewer\viewer\env\lib\site-packages (65.5.0)
Collecting setuptools
  Using cached setuptools-75.8.0-py3-none-any.whl (1.2 MB)
Collecting wheel
  Using cached wheel-0.45.1-py3-none-any.whl (72 kB)
Installing collected packages: wheel, setuptools, pip
  Attempting uninstall: setuptools
    Found existing installation: setuptools 65.5.0
    Uninstalling setuptools-65.5.0:
      Successfully uninstalled setuptools-65.5.0
  Attempting uninstall: pip
    Found existing installation: pip 22.3.1
    Uninstalling pip-22.3.1:
      Successfully uninstalled pip-22.3.1
Successfully installed pip-25.0.1 setuptools-75.8.0 wheel-0.45.1
```

## Examples

As a first example, we pass the test cases image.

By default, the topic is the (root) directory (topic `--tdir`).

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing dir starts at 358 as dir [tech0]

|block 358 zone 1/19 track 18 sector 1 type DIR--|
|blocks| filename           |filetype| block1    |
|------|--------------------|--------|-----------|
|  9   | 'CASES1-7'         |  PRG   | 11/00=336 |
|  2   | 'CASE-08'          |  PRG   | 11/01=337 |
|  2   | 'CASE-09'          |  PRG   | 11/02=338 |
|  3   | 'CASE-10'          |  PRG   | 11/05=341 |
|  3   | 'CASE-11'          |  PRG   | 11/11=353 |
|  3   | 'CASE-12'          |  PRG   | 11/09=345 |
|  3   | 'CASE-13'          |  PRG   | 13/00=376 |
|------|--------------------|--------|-----------|
```

You can always ask for some notes (modifier `--mnotes`).

```
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing dir starts at 358 as dir [tech0 notes]

|block 358 zone 1/19 track 18 sector 1 type DIR--|
|blocks| filename           |filetype| block1    |
|------|--------------------|--------|-----------|
|  9   | 'CASES1-7'         |  PRG   | 11/00=336 |
|  2   | 'CASE-08'          |  PRG   | 11/01=337 |
|  2   | 'CASE-09'          |  PRG   | 11/02=338 |
|  3   | 'CASE-10'          |  PRG   | 11/05=341 |
|  3   | 'CASE-11'          |  PRG   | 11/11=353 |
|  3   | 'CASE-12'          |  PRG   | 11/09=345 |
|  3   | 'CASE-13'          |  PRG   | 13/00=376 |
|------|--------------------|--------|-----------|

Directory entry notes
- blocks is number of disk blocks (of 256 bytes) used by file
  first 2 bytes are not file content but form track/sector link to next block
- filename is the name of teh file (max 16 chars, spaces allowed)
- filetype
  - DEL: deleted (or not yet used)
  - SEQ: sequential (data) file
  - PRG: program file (has load address)
  - USR: user (nearly the same as SEQ)
  - REL: relative (data) file (with side sectors)
- optional flags for filetype
  - ?: should not occur (bit 4 not in use)
  - @: used during save-@
  - >: locked file (scratch not allowed)
  - *: splat file (need to run 'validate' )
- block1 is track/sector link to first block of file
```

We now pick one of the files as topic (topic `--tife CASE-09`); the view by default is hex.

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64  --tfile CASE-09
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing file CASE-09 at 338 as hex [tech0 cont(682)]

|block 338 zone 0/21 track 17 sector 2 type FIL-----------------------------|
|offset| 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | 0123456789ABCDEF |
|------|-------------------------------------------------|------------------|
|  00  | 11 0C 01 08 27 08 32 00 8F 20 54 45 53 54 43 41 | ····'·2°· TESTCA |
|  10  | 53 45 3A 20 4C 49 4E 45 20 43 55 54 20 42 59 20 | SE: LINE CUT BY  |
|  20  | 42 4C 4F 43 4B 20 53 45 50 00 3D 08 64 00 41 B2 | BLOCK SEP°=·d°A· |
|  30  | 38 AC 32 35 36 AA 31 3A 42 B2 30 3A 4F B2 34 00 | 8·256·1:B·0:O·4° |
|  40  | 53 08 6E 00 44 B2 41 3A 8D 33 30 30 3A 99 42 2C | S·n°D·A:·300:·B, |
|  50  | 4F 2C 44 24 2C 00 6C 08 78 00 41 4E B2 C2 28 41 | O,D$,°l·x°AN··(A |
|  60  | AA 30 29 AA 32 35 36 AC C2 28 41 AA 31 29 00 84 | ·0)·256··(A·1)°· |
|  70  | 08 82 00 8B 20 41 4E B2 30 20 A7 20 99 20 22 20 | ··°· AN·0 · · "  |
|  80  | 45 4E 44 22 3A 80 00 9D 08 8C 00 4C 4E B2 C2 28 | END":·°···°LN··( |
|  90  | 41 AA 32 29 AA 32 35 36 AC C2 28 41 AA 33 29 00 | A·2)·256··(A·3)° |
|  A0  | A6 08 96 00 99 20 4C 4E 00 CA 08 A0 00 4F B2 4F | ···°· LN°···°O·O |
|  B0  | AA 41 4E AB 41 3A 8B 4F B1 32 35 35 A7 4F B2 4F | ·AN·A:·O·255·O·O |
|  C0  | AB 32 35 36 AA 32 3A 42 B2 42 AA 31 00 D9 08 AA | ·256·2:B·B·1°··· |
|  D0  | 00 41 B2 41 4E 3A 89 20 31 31 30 00 EC 08 2C 01 | °A·AN:· 110°··,· |
|  E0  | 8F 20 49 4E 20 44 2C 20 4F 55 54 20 44 24 00 08 | · IN D, OUT D$°· |
|  F0  | 09 36 01 44 48 B2 B5 28 44 AD 32 35 36 29 3A 44 | ·6·DH··(D·256):D |
|------|-------------------------------------------------|------------------|
|block 348 zone 0/21 track 17 sector 12 type FIL----------------------------|
|offset| 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | 0123456789ABCDEF |
|------|-------------------------------------------------|------------------|
|  00  | 00 FF 4C B2 44 AB 32 35 36 AC 44 48 00 1D 09 40 | °·L·D·256·DH°··@ |
|  10  | 01 53 B2 44 48 3A 8D 20 34 30 30 3A 44 24 B2 53 | ·S·DH:· 400:D$·S |
|  20  | 24 00 35 09 4A 01 53 B2 44 4C 3A 8D 20 34 30 30 | $°5·J·S·DL:· 400 |
|  30  | 3A 44 24 B2 44 24 AA 53 24 00 3B 09 54 01 8E 00 | :D$·D$·S$°;·T··° |
|  40  | 4E 09 90 01 8F 20 49 4E 20 53 2C 20 4F 55 54 20 | N···· IN S, OUT  |
|  50  | 53 24 00 68 09 9A 01 53 48 B2 B5 28 53 AD 31 36 | S$°h···SH··(S·16 |
|  60  | 29 3A 53 4C B2 53 AB 31 36 AC 53 48 00 7D 09 A4 | ):SL·S·16·SH°}·· |
|  70  | 01 8B 20 53 48 B1 39 20 A7 20 53 48 B2 53 48 AA | ·· SH·9 · SH·SH· |
|  80  | 37 00 92 09 AE 01 8B 20 53 4C B1 39 20 A7 20 53 | 7°····· SL·9 · S |
|  90  | 4C B2 53 4C AA 37 00 AD 09 B8 01 53 24 B2 C7 28 | L·SL·7°····S$··( |
|  A0  | 53 48 AA 34 38 29 AA C7 28 53 4C AA 34 38 29 3A | SH·48)··(SL·48): |
|  B0  | 8E 00 B8 09 F4 01 8F 20 54 43 30 39 00 F9 09 FE | ·°····· TC09°··· |
|  C0  | 01 8F 20 30 31 32 33 34 35 36 37 38 39 30 31 32 | ·· 0123456789012 |
|  D0  | 33 34 35 36 37 38 39 30 31 32 33 34 35 36 37 38 | 3456789012345678 |
|  E0  | 39 30 31 32 33 34 35 36 37 38 39 30 31 32 33 34 | 9012345678901234 |
|  F0  | 35 36 37 38 39 30 31 32 33 34 35 36 37 00 00 00 | 5678901234567°°° |
|------|-------------------------------------------------|------------------|
no next block (request was 681)
```

We now override the view to be Commodore BASIC (view `--vbasic`); make the screen wide enough.

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64 --tfile CASE-09 --vbasic
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing file CASE-09 at 338 as basic [tech0 cont(682)]

|block 338 zone 0/21 track 17 sector 2 type FIL--------------------------------------------------------------------------------------|
| addr |offs|nextaddr|linenum| data                                                                                                  |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| load | 02 |        |       | 01 08 (decimal  2049)                                                                                 |
| 2049 |  4 |   2087 |    50 | REM TESTCASE: LINE CUT BY BLOCK SEP°                                                                  |
| 2087 | 42 |   2109 |   100 | A=8*256+1:B=0:O=4°                                                                                    |
| 2109 | 64 |   2131 |   110 | D=A:GOSUB300:PRINTB,O,D$,°                                                                            |
| 2131 | 86 |   2156 |   120 | AN=PEEK(A+0)+256*PEEK(A+1)°                                                                           |
| 2156 |111 |   2180 |   130 | IF AN=0 THEN PRINT " END":END°                                                                        |
| 2180 |135 |   2205 |   140 | LN=PEEK(A+2)+256*PEEK(A+3)°                                                                           |
| 2205 |160 |   2214 |   150 | PRINT LN°                                                                                             |
| 2214 |169 |   2250 |   160 | O=O+AN-A:IFO>255THENO=O-256+2:B=B+1°                                                                  |
| 2250 |205 |   2265 |   170 | A=AN:GOTO 110°                                                                                        |
| 2265 |220 |   2284 |   300 | REM IN D, OUT D$°                                                                                     |
| 2284 |239 |   2312 |   310 | DH=INT(D/256):D                                                                                       |
|block 348 zone 0/21 track 17 sector 12 type FIL-------------------------------------------------------------------------------------|
| 2301 |  2 |  ..... | ..... | ... L=D-256*DH°                                                                                       |
| 2312 | 13 |   2333 |   320 | S=DH:GOSUB 400:D$=S$°                                                                                 |
| 2333 | 34 |   2357 |   330 | S=DL:GOSUB 400:D$=D$+S$°                                                                              |
| 2357 | 58 |   2363 |   340 | RETURN°                                                                                               |
| 2363 | 64 |   2382 |   400 | REM IN S, OUT S$°                                                                                     |
| 2382 | 83 |   2408 |   410 | SH=INT(S/16):SL=S-16*SH°                                                                              |
| 2408 |109 |   2429 |   420 | IF SH>9 THEN SH=SH+7°                                                                                 |
| 2429 |130 |   2450 |   430 | IF SL>9 THEN SL=SL+7°                                                                                 |
| 2450 |151 |   2477 |   440 | S$=CHR$(SH+48)+CHR$(SL+48):RETURN°                                                                    |
| 2477 |178 |   2488 |   500 | REM TC09°                                                                                             |
| 2488 |189 |   2553 |   510 | REM 0123456789012345678901234567890123456789012345678901234567°                                       |
| 2553 |254 |      0 |       | block link is FF, last offset is FF (ok)                                                              |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 2555 |256 | block  |       |                                                                                                       |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
```

Finally we ask for more tech details (modifier `--mtech 1`).

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64 --tfile CASE-09 --vbasic --mtech 1
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing file CASE-09 at 338 as basic [tech1 cont(682)]

|block 338 zone 0/21 track 17 sector 2 type FIL--------------------------------------------------------------------------------------|
| addr |offs|nextaddr|linenum| data                                                                                                  |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| link | 00 |        |       | 11 0C (decimal 17/12)                                                                                 |
| load | 02 |        |       | 01 08 (decimal  2049)                                                                                 |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0801 | 04 |  27 08 | 32 00 | 8F 20 54 45 53 54 43 41 53 45 3A 20 4C 49 4E 45 20 43 55 54 20 42 59 20 42 4C 4F 43 4B 20 53 45 50 00 |
| 2049 |  4 |   2087 |    50 | REM TESTCASE                  : LINE CUT BY BLOCK SEP                                              °  |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0827 | 2A |  3D 08 | 64 00 | 41 B2 38 AC 32 35 36 AA 31 3A 42 B2 30 3A 4F B2 34 00                                                 |
| 2087 | 42 |   2109 |   100 | A=8*256+1                  :B=0        :O=4        °                                                  |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 083D | 40 |  53 08 | 6E 00 | 44 B2 41 3A 8D 33 30 30 3A 99 42 2C 4F 2C 44 24 2C 00                                                 |
| 2109 | 64 |   2131 |   110 | D=A      :GOSUB300      :PRINTB,O,D$,              °                                                  |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0853 | 56 |  6C 08 | 78 00 | 41 4E B2 C2 28 41 AA 30 29 AA 32 35 36 AC C2 28 41 AA 31 29 00                                        |
| 2131 | 86 |   2156 |   120 | AN=PEEK(A+0)+256*PEEK(A+1)                                  °                                         |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 086C | 6F |  84 08 | 82 00 | 8B 20 41 4E B2 30 20 A7 20 99 20 22 20 45 4E 44 22 3A 80 00                                           |
| 2156 |111 |   2180 |   130 | IF AN=0 THEN PRINT " END"                          :END  °                                            |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0884 | 87 |  9D 08 | 8C 00 | 4C 4E B2 C2 28 41 AA 32 29 AA 32 35 36 AC C2 28 41 AA 33 29 00                                        |
| 2180 |135 |   2205 |   140 | LN=PEEK(A+2)+256*PEEK(A+3)                                  °                                         |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 089D | A0 |  A6 08 | 96 00 | 99 20 4C 4E 00                                                                                        |
| 2205 |160 |   2214 |   150 | PRINT LN    °                                                                                         |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 08A6 | A9 |  CA 08 | A0 00 | 4F B2 4F AA 41 4E AB 41 3A 8B 4F B1 32 35 35 A7 4F B2 4F AB 32 35 36 AA 32 3A 42 B2 42 AA 31 00       |
| 2214 |169 |   2250 |   160 | O=O+AN-A                :IFO>255THENO=O-256+2                              :B=B+1            °        |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 08CA | CD |  D9 08 | AA 00 | 41 B2 41 4E 3A 89 20 31 31 30 00                                                                      |
| 2250 |205 |   2265 |   170 | A=AN        :GOTO 110         °                                                                       |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 08D9 | DC |  EC 08 | 2C 01 | 8F 20 49 4E 20 44 2C 20 4F 55 54 20 44 24 00                                                          |
| 2265 |220 |   2284 |   300 | REM IN D, OUT D$                          °                                                           |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 08EC | EF |  08 09 | 36 01 | 44 48 B2 B5 28 44 AD 32 35 36 29 3A 44                                                                |
| 2284 |239 |   2312 |   310 | DH=INT(D/256)                    :D                                                                   |
|block 348 zone 0/21 track 17 sector 12 type FIL-------------------------------------------------------------------------------------|
| link | 00 |        |       | 00 FF [last byte at offset FF] (decimal 0/255)                                                        |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 08FD | 02 |  .. .. | .. .. | .. .. .. .. .. .. .. .. .. .. .. .. .. 4C B2 44 AB 32 35 36 AC 44 48 00                               |
| 2301 |  2 |  ..... | ..... | .. .. .. .. .. .. .. .. .. .. .. .. .. L=D-256*DH                    °                                |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0908 | 0D |  1D 09 | 40 01 | 53 B2 44 48 3A 8D 20 34 30 30 3A 44 24 B2 53 24 00                                                    |
| 2312 | 13 |   2333 |   320 | S=DH        :GOSUB 400        :D$=S$            °                                                     |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 091D | 22 |  35 09 | 4A 01 | 53 B2 44 4C 3A 8D 20 34 30 30 3A 44 24 B2 44 24 AA 53 24 00                                           |
| 2333 | 34 |   2357 |   330 | S=DL        :GOSUB 400        :D$=D$+S$                  °                                            |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0935 | 3A |  3B 09 | 54 01 | 8E    00                                                                                              |
| 2357 | 58 |   2363 |   340 | RETURN°                                                                                               |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 093B | 40 |  4E 09 | 90 01 | 8F 20 49 4E 20 53 2C 20 4F 55 54 20 53 24 00                                                          |
| 2363 | 64 |   2382 |   400 | REM IN S, OUT S$                          °                                                           |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 094E | 53 |  68 09 | 9A 01 | 53 48 B2 B5 28 53 AD 31 36 29 3A 53 4C B2 53 AB 31 36 AC 53 48 00                                     |
| 2382 | 83 |   2408 |   410 | SH=INT(S/16)                  :SL=S-16*SH                      °                                      |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0968 | 6D |  7D 09 | A4 01 | 8B 20 53 48 B1 39 20 A7 20 53 48 B2 53 48 AA 37 00                                                    |
| 2408 |109 |   2429 |   420 | IF SH>9 THEN SH=SH+7                            °                                                     |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 097D | 82 |  92 09 | AE 01 | 8B 20 53 4C B1 39 20 A7 20 53 4C B2 53 4C AA 37 00                                                    |
| 2429 |130 |   2450 |   430 | IF SL>9 THEN SL=SL+7                            °                                                     |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 0992 | 97 |  AD 09 | B8 01 | 53 24 B2 C7 28 53 48 AA 34 38 29 AA C7 28 53 4C AA 34 38 29 3A 8E  00                                 |
| 2450 |151 |   2477 |   440 | S$=CHR$(SH+48)+CHR$(SL+48)                                  :RETURN°                                  |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 09AD | B2 |  B8 09 | F4 01 | 8F 20 54 43 30 39 00                                                                                  |
| 2477 |178 |   2488 |   500 | REM TC09          °                                                                                   |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 09B8 | BD |  F9 09 | FE 01 | 8F 20 30 31 32 33 34 35 36 37 38 39 30 31 32 33 34 35 36 37 38 39 30 31 32 33 34 35 36 37 38 39 30 31 |
| 2488 |189 |   2553 |   510 | REM 01234567890123456789012345678901                                                                  |
|      |    |        |       | 32 33 34 35 36 37 38 39 30 31 32 33 34 35 36 37 38 39 30 31 32 33 34 35 36 37 00                      |
|      |    |        |       | 23456789012345678901234567                                                    °                       |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 09F9 | FE |  00 00 |       | no more basic line                                                                                    |
| 2553 |254 |      0 |       | block link is FF, last offset is FF (ok)                                                              |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
| 09FB |100 | rest in|       |                                                                                                       |
| 2555 |256 | block  |       |                                                                                                       |
|------|----|--------|-------|-------------------------------------------------------------------------------------------------------|
Done
```

An interesting topic is the whole disk (topic `--tdisk`).

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64 --tdisk
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing disk (all blocks) as disk [tech0]

|track|zone|   blocks    | 000 001 002 003 004 005 006 007 007 009 010 011 012 013 014 015 016 017 018 019 020 |
|-----|----|-------------|-------------------------------------------------------------------------------------|
|  1  | 0  |000..020 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  2  | 0  |021..041 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  3  | 0  |042..062 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  4  | 0  |063..083 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  5  | 0  |084..104 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  6  | 0  |105..125 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  7  | 0  |126..146 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  8  | 0  |147..167 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
|  9  | 0  |168..188 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 10  | 0  |189..209 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 11  | 0  |210..230 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 12  | 0  |231..251 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 13  | 0  |252..272 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 14  | 0  |273..293 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 15  | 0  |294..314 (21)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- |
| 16  | 0  |315..335 (21)| --- --- --- --- --- FIL --- --- --- --- --- --- --- --- --- FIL --- --- --- --- --- |
| 17  | 0  |336..356 (21)| FIL FIL FIL --- FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL FIL |
|-----|----|-------------|-------------------------------------------------------------------------------------|
| 18  | 1  |357..375 (19)| BAM DIR dir dir dir dir dir dir dir dir dir dir dir dir dir dir dir dir dir         |
| 19  | 1  |376..394 (19)| FIL FIL --- --- --- --- --- --- --- --- FIL --- --- --- --- --- --- --- ---         |
| 20  | 1  |395..413 (19)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---         |
| 21  | 1  |414..432 (19)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---         |
| 22  | 1  |433..451 (19)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---         |
| 23  | 1  |452..470 (19)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---         |
| 24  | 1  |471..489 (19)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---         |
|-----|----|-------------|-------------------------------------------------------------------------------------|
| 25  | 2  |490..507 (18)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---             |
| 26  | 2  |508..525 (18)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---             |
| 27  | 2  |526..543 (18)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---             |
| 28  | 2  |544..561 (18)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---             |
| 29  | 2  |562..579 (18)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---             |
| 30  | 2  |580..597 (18)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---             |
|-----|----|-------------|-------------------------------------------------------------------------------------|
| 31  | 3  |598..614 (17)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---                 |
| 32  | 3  |615..631 (17)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---                 |
| 33  | 3  |632..648 (17)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---                 |
| 34  | 3  |649..665 (17)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---                 |
| 35  | 3  |666..682 (17)| --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---                 |
|-----|----|-------------|-------------------------------------------------------------------------------------|
```

## Extract file

Any file can be extracted, saved to the PC disk, with the `--msave` modifier.

```
(env) C:\Repos\d64viewer\viewer>run ..\testcases\cases.d64 --tfile CASE-10 --msave case-10.prg
d64viewer: file '..\testcases\cases.d64' has 683 blocks of 256 bytes
showing file CASE-10 at 341 as hex [tech0 save(case-10.prg) cont(682)]

|block 341 zone 0/21 track 17 sector 5 type FIL-----------------------------|
|offset| 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | 0123456789ABCDEF |
|------|-------------------------------------------------|------------------|
|  00  | 11 0F 01 08 27 08 32 00 8F 20 54 45 53 54 43 41 | ····'·2°· TESTCA |
|  10  | 53 45 3A 20 4C 49 4E 45 20 43 55 54 20 42 59 20 | SE: LINE CUT BY  |
|  20  | 42 4C 4F 43 4B 20 53 45 50 00 3D 08 64 00 41 B2 | BLOCK SEP°=·d°A· |
|  30  | 38 AC 32 35 36 AA 31 3A 42 B2 30 3A 4F B2 34 00 | 8·256·1:B·0:O·4° |
|  40  | 53 08 6E 00 44 B2 41 3A 8D 33 30 30 3A 99 42 2C | S·n°D·A:·300:·B, |
|  50  | 4F 2C 44 24 2C 00 6C 08 78 00 41 4E B2 C2 28 41 | O,D$,°l·x°AN··(A |
|  60  | AA 30 29 AA 32 35 36 AC C2 28 41 AA 31 29 00 84 | ·0)·256··(A·1)°· |
|  70  | 08 82 00 8B 20 41 4E B2 30 20 A7 20 99 20 22 20 | ··°· AN·0 · · "  |
|  80  | 45 4E 44 22 3A 80 00 9D 08 8C 00 4C 4E B2 C2 28 | END":·°···°LN··( |
|  90  | 41 AA 32 29 AA 32 35 36 AC C2 28 41 AA 33 29 00 | A·2)·256··(A·3)° |
|  A0  | A6 08 96 00 99 20 4C 4E 00 CA 08 A0 00 4F B2 4F | ···°· LN°···°O·O |
|  B0  | AA 41 4E AB 41 3A 8B 4F B1 32 35 35 A7 4F B2 4F | ·AN·A:·O·255·O·O |
|  C0  | AB 32 35 36 AA 32 3A 42 B2 42 AA 31 00 D9 08 AA | ·256·2:B·B·1°··· |
|  D0  | 00 41 B2 41 4E 3A 89 20 31 31 30 00 EC 08 2C 01 | °A·AN:· 110°··,· |
|  E0  | 8F 20 49 4E 20 44 2C 20 4F 55 54 20 44 24 00 08 | · IN D, OUT D$°· |
|  F0  | 09 36 01 44 48 B2 B5 28 44 AD 32 35 36 29 3A 44 | ·6·DH··(D·256):D |
|------|-------------------------------------------------|------------------|
|block 351 zone 0/21 track 17 sector 15 type FIL----------------------------|
|offset| 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | 0123456789ABCDEF |
|------|-------------------------------------------------|------------------|
|  00  | 11 07 4C B2 44 AB 32 35 36 AC 44 48 00 1D 09 40 | ··L·D·256·DH°··@ |
|  10  | 01 53 B2 44 48 3A 8D 20 34 30 30 3A 44 24 B2 53 | ·S·DH:· 400:D$·S |
|  20  | 24 00 35 09 4A 01 53 B2 44 4C 3A 8D 20 34 30 30 | $°5·J·S·DL:· 400 |
|  30  | 3A 44 24 B2 44 24 AA 53 24 00 3B 09 54 01 8E 00 | :D$·D$·S$°;·T··° |
|  40  | 4E 09 90 01 8F 20 49 4E 20 53 2C 20 4F 55 54 20 | N···· IN S, OUT  |
|  50  | 53 24 00 68 09 9A 01 53 48 B2 B5 28 53 AD 31 36 | S$°h···SH··(S·16 |
|  60  | 29 3A 53 4C B2 53 AB 31 36 AC 53 48 00 7D 09 A4 | ):SL·S·16·SH°}·· |
|  70  | 01 8B 20 53 48 B1 39 20 A7 20 53 48 B2 53 48 AA | ·· SH·9 · SH·SH· |
|  80  | 37 00 92 09 AE 01 8B 20 53 4C B1 39 20 A7 20 53 | 7°····· SL·9 · S |
|  90  | 4C B2 53 4C AA 37 00 AD 09 B8 01 53 24 B2 C7 28 | L·SL·7°····S$··( |
|  A0  | 53 48 AA 34 38 29 AA C7 28 53 4C AA 34 38 29 3A | SH·48)··(SL·48): |
|  B0  | 8E 00 B8 09 F4 01 8F 20 54 43 31 30 00 FA 09 FE | ·°····· TC10°··· |
|  C0  | 01 8F 20 30 31 32 33 34 35 36 37 38 39 30 31 32 | ·· 0123456789012 |
|  D0  | 33 34 35 36 37 38 39 30 31 32 33 34 35 36 37 38 | 3456789012345678 |
|  E0  | 39 30 31 32 33 34 35 36 37 38 39 30 31 32 33 34 | 9012345678901234 |
|  F0  | 35 36 37 38 39 30 31 32 33 34 35 36 37 38 00 00 | 56789012345678°° |
|------|-------------------------------------------------|------------------|
|block 343 zone 0/21 track 17 sector 7 type FIL-----------------------------|
|offset| 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | 0123456789ABCDEF |
|------|-------------------------------------------------|------------------|
|  00  | 00 02 00*08*27*08*32*00*8F*20*54*45*53*54*43*41*| °·°·'·2°· TESTCA |
|  10  |*53*45*3A*20*4C*49*4E*45*20*43*55*54*20*42*59*20*| SE: LINE CUT BY  |
|  20  |*42*4C*4F*43*4B*20*53*45*50*00*3D*08*64*00*41*B2*| BLOCK SEP°=·d°A· |
|  30  |*38*AC*32*35*36*AA*31*3A*42*B2*30*3A*4F*B2*34*00*| 8·256·1:B·0:O·4° |
|  40  |*53*08*6E*00*44*B2*41*3A*8D*33*30*30*3A*99*42*2C*| S·n°D·A:·300:·B, |
|  50  |*4F*2C*44*24*2C*00*6C*08*78*00*41*4E*B2*C2*28*41*| O,D$,°l·x°AN··(A |
|  60  |*AA*30*29*AA*32*35*36*AC*C2*28*41*AA*31*29*00*84*| ·0)·256··(A·1)°· |
|  70  |*08*82*00*8B*20*41*4E*B2*30*20*A7*20*99*20*22*20*| ··°· AN·0 · · "  |
|  80  |*45*4E*44*22*3A*80*00*9D*08*8C*00*4C*4E*B2*C2*28*| END":·°···°LN··( |
|  90  |*41*AA*32*29*AA*32*35*36*AC*C2*28*41*AA*33*29*00*| A·2)·256··(A·3)° |
|  A0  |*A6*08*96*00*99*20*4C*4E*00*CA*08*A0*00*4F*B2*4F*| ···°· LN°···°O·O |
|  B0  |*AA*41*4E*AB*41*3A*8B*4F*B1*32*35*35*A7*4F*B2*4F*| ·AN·A:·O·255·O·O |
|  C0  |*AB*32*35*36*AA*32*3A*42*B2*42*AA*31*00*D9*08*AA*| ·256·2:B·B·1°··· |
|  D0  |*00*41*B2*41*4E*3A*89*20*31*31*30*00*EC*08*2C*01*| °A·AN:· 110°··,· |
|  E0  |*8F*20*49*4E*20*44*2C*20*4F*55*54*20*44*24*00*08*| · IN D, OUT D$°· |
|  F0  |*09*36*01*44*48*B2*B5*28*44*AD*32*35*36*29*3A*44*| ·6·DH··(D·256):D |
|------|-------------------------------------------------|------------------|
no next block (request was 680)
saved 'case-10.prg'
```

This creates a file `case-10.prg`.
Note that the hex dump showed that the file on the 1541 disk was stored in 3 blocks.
- block 1: 2 bytes (11 0F) link to next block, so 254 bytes payload
- block 2: 2 bytes (11 07) link to next block so 254 bytes payload
- block 3: 2 bytes (00 02) signaling last block (00) and last offset (02), so only one byte payload

Total 254+254+1 = 509 bytes. Windows confirms that.

```
(env) C:\Repos\d64viewer\viewer>dir case-10.prg
2025 02 23  20:50               509 case-10.prg
```


## Resources

I used these resources 
- [baltissen](http://www.baltissen.org/newhtm/1541c.htm) nice intro, not as deep detailed as unusedino.
- [unusedino](http://unusedino.de/ec64/technical/formats/d64.html) good technical write-up
- [1541 manual](https://www.manualslib.com/manual/827205/Commodore-1541-Ii.html?page=97#manual) much more verbose, still missing some details
- [wiki](https://en.wikipedia.org/wiki/Commodore_DOS) good reference for the commands 



(end)
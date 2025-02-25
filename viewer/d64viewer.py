import sys
import os
import argparse
from enum import Enum

# http://unusedino.de/ec64/technical/formats/d64.html
# https://www.manualslib.com/manual/827205/Commodore-1541-Ii.html?page=97#manual
# https://en.wikipedia.org/wiki/Commodore_DOS
# http://www.baltissen.org/newhtm/1541c.htm


#region ### CONSTANTS ###############################################################

BLOCKSPERDISK=683   # We use the term 'block' for what is normally known as sector. We reserve 'sector' for a portion of a track
BYTESPERBLOCK=256   # Each block on the disk stores 256 bytes


SECTORSPERTRACK = [ # Number of sectors per track (there is no track 0, so padded here)
  -1, #   0
  21, #   1
  21, #   2
  21, #   3
  21, #   4
  21, #   5
  21, #   6
  21, #   7
  21, #   8
  21, #   9
  21, #  10
  21, #  11
  21, #  12
  21, #  13
  21, #  14
  21, #  15
  21, #  16
  21, #  17
  19, #  18
  19, #  19
  19, #  20
  19, #  21
  19, #  22
  19, #  23
  19, #  24
  18, #  25
  18, #  26
  18, #  27
  18, #  28
  18, #  29
  18, #  30
  17, #  31
  17, #  32
  17, #  33
  17, #  34
  17, #  35
  -1, #  36
]


BASICTOKEN = [                                
  "END"     , # 0x80/128                                                   
  "FOR"     , # 0x81/129                                            
  "NEXT"    , # 0x82/130                                             
  "DATA"    , # 0x83/131                                             
  "INPUT#"  , # 0x84/132                                               
  "INPUT"   , # 0x85/133                                              
  "DIM"     , # 0x86/134                                            
  "READ"    , # 0x87/135                                             
  "LET"     , # 0x88/136                                            
  "GOTO"    , # 0x89/137                                             
  "RUN"     , # 0x8A/138                                            
  "IF"      , # 0x8B/139                                           
  "RESTORE" , # 0x8C/140                                 
  "GOSUB"   , # 0x8D/141                               
  "RETURN"  , # 0x8E/142                                
  "REM"     , # 0x8F/143                             
  "STOP"    , # 0x90/144                              
  "ON"      , # 0x91/145                            
  "WAIT"    , # 0x92/146                              
  "LOAD"    , # 0x93/147                              
  "SAVE"    , # 0x94/148                              
  "VERIFY"  , # 0x95/149                                
  "DEF"     , # 0x96/150                             
  "POKE"    , # 0x97/151                              
  "PRINT#"  , # 0x98/152                                
  "PRINT"   , # 0x99/153                               
  "CONT"    , # 0x9A/154                              
  "LIST"    , # 0x9B/155                              
  "CLR"     , # 0x9C/156                             
  "CMD"     , # 0x9D/157                             
  "SYS"     , # 0x9E/158                             
  "OPEN"    , # 0x9F/159                              
  "CLOSE"   , # 0xA0/160                               
  "GET"     , # 0xA1/161                             
  "NEW"     , # 0xA2/162                             
  "TAB("    , # 0xA3/163                              
  "TO"      , # 0xA4/164                            
  "FN"      , # 0xA5/165                            
  "SPC("    , # 0xA6/166                              
  "THEN"    , # 0xA7/167                              
  "NOT"     , # 0xA8/168                             
  "STEP"    , # 0xA9/169                              
  "+"       , # 0xAA/170                   
  "-"       , # 0xAB/171                      
  "*"       , # 0xAC/172                         
  "/"       , # 0xAD/173                   
  "↑"       , # 0xAE/174                
  "AND"     , # 0xAF/175          
  "OR"      , # 0xB0/176         
  ">"       , # 0xB1/177                                
  "="       , # 0xB2/178                          
  "<"       , # 0xB3/179                             
  "SGN"     , # 0xB4/180                             
  "INT"     , # 0xB5/181                             
  "ABS"     , # 0xB6/182                             
  "USR"     , # 0xB7/183                             
  "FRE"     , # 0xB8/184                             
  "POS"     , # 0xB9/185                             
  "SQR"     , # 0xBA/186                             
  "RND"     , # 0xBB/187                             
  "LOG"     , # 0xBC/188                             
  "EXP"     , # 0xBD/189                             
  "COS"     , # 0xBE/190                             
  "SIN"     , # 0xBF/191                             
  "TAN"     , # 0xC0/192                             
  "ATN"     , # 0xC1/193                             
  "PEEK"    , # 0xC2/194                              
  "LEN"     , # 0xC3/195                             
  "STR$"    , # 0xC4/196                              
  "VAL"     , # 0xC5/197                             
  "ASC"     , # 0xC6/198                             
  "CHR$"    , # 0xC7/199                              
  "LEFT$"   , # 0xC8/200                               
  "RIGHT$"  , # 0xC9/201                                
  "MID$"    , # 0xCA/202                              
  "GO"      , # 0xCB/203
]


#PRINTABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
PRINTABLE  = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '

#endregion
#region ### HELP ####################################################################


def help_hex() :
  print("Hex layout")
  print("- 16 rows of 16 bytes")
  print("- each row shows offset, 16 bytes in hex, 16 bytes as ASCII")
  print("- non-printable ASCII printed as · (and 00 as °)")
  print("- hex between ** denotes bytes in block past end-of-file")


def help_bam() :
  print("BAM notes")
  print("- offset 02 is DOSVERSION; when not 41 or 00 makes disk non-writable")
  print("- offset A5 is DOSTYPE; always A2 (?)")
  print("- tech view shows 4 bytes per sector (offset 04..90)")
  print("  - first byte is the freecount (number of available sectors in that track)")
  print("  - next 3 bytes is a bit vector (1=available, 0=used) sector")
  print("    unsued bits (tracks with less than 24 bits) are shows as s(et) or c(lear)")
  print("- free blocks is sum of freecount over all rows")
  print("- diskname (offset 90) and diskid (offset A2) are set with format")
  print("- C64 basic shows directory listing starting with a line that shows")
  print("  0 or 1 (drive unit in enclosure), diskname, diskid, dostype")


def help_dir() :
  print("Directory entry notes")
  print("- blocks is number of disk blocks (of 256 bytes) used by file")
  print("  first 2 bytes are not file content but form track/sector link to next block")
  print("- filename is the name of teh file (max 16 chars, spaces allowed)")
  print("- filetype")
  print("  - DEL: deleted (or not yet used)")
  print("  - SEQ: sequential (data) file")
  print("  - PRG: program file (has load address)")
  print("  - USR: user (nearly the same as SEQ)")
  print("  - REL: relative (data) file (with side sectors)")
  print("- optional flags for filetype")
  print("  - ?: should not occur (bit 4 not in use)")
  print("  - @: used during save-@")
  print("  - >: locked file (scratch not allowed)")
  print("  - *: splat file (need to run 'validate' )")
  print("- block1 is track/sector link to first block of file")


def help_disk() :
  print("Types of a disk block")
  print("- BAM: Block Availability Matrix (typically one block at 357:18.0)")
  print("- DIR: stores 8 directory entries (typically 18 blocks at 358:18.1..375:18.19)")
  print("- dir: same as DIR but empty (zeros)")
  print("- FIL: file data (any type)")
  print("- ---: same as FIL but empty (zeros)")
  print("The 35 tracks have varying amount of sectors")
  print("- tracks  1..17 (zone 0) have 21 sectors")
  print("- tracks 18..24 (zone 1) have 19 sectors")
  print("- tracks 25..30 (zone 2) have 18 sectors")
  print("- tracks 31..35 (zone 3) have 17 sectors")
  print("Indices")
  print("- 1..35 for tracks")
  print("- 0..17|18|19|21 for sectors")
  print("- 0..682 for blocks")


def help_basic() :
  print("- as for every block, first two bytes link to next block")
  print("- first block of a basic program has load address at offset 02 and 03")
  print("- then comes a series of basic lines")
  print("  - two bytes for address of next basic line")
  print("  - two bytes for basic line number")
  print("  - basic line content; keywords are tokenized (ASCII 80 and higher)")
  print("  - one byte terminating 00")
  print("- if address of next basic line is 00 00 file is at end")


#endregion
#region ### AUX #####################################################################

CHAR00      = "°" # "¶"
CHARNOGLYPH = "·"


def makeprintable(ch) :
  if ch in PRINTABLE : return ch
  elif ch==chr(0) : return CHAR00
  else: return CHARNOGLYPH


def filetype2str(filetype) :
  s0000xxxx= "???"
  if filetype & 0b00001111 == 0b000 : s0000xxxx= "DEL"
  if filetype & 0b00001111 == 0b001 : s0000xxxx= "SEQ"
  if filetype & 0b00001111 == 0b010 : s0000xxxx= "PRG"
  if filetype & 0b00001111 == 0b011 : s0000xxxx= "USR"
  if filetype & 0b00001111 == 0b100 : s0000xxxx= "REL"
  s000x0000=""
  if filetype & 0b00010000 : s0000x0000 = "?"
  s00x00000=""
  if filetype & 0b00100000 : s00x00000 = "@"
  s0x000000=""
  if filetype & 0b01000000 : s0x000000 = ">"
  sx0000000="*"
  if filetype & 0b10000000 : sx0000000 = ""
  return sx0000000 + s0x000000 + s00x00000 + s000x0000 + s0000xxxx


def filename2str(filename):
  str= ""
  for d in filename:
    if d==160 : break
    str += makeprintable(chr(d))
  return str


def bin2str(binarray) :
  return ' '.join( [f"{bin:02X}" for bin in binarray] )


def token(byte) :
  if 128<=byte and byte<=203: return BASICTOKEN[byte-128]
  return makeprintable(chr(byte))


def bin2bas(binarray) :
  return ''.join( [f"{token(bin)}" for bin in binarray] )


#endregion
#region ### BASIC LINE ITERATOR #####################################################


class BasicLineIter :

  # This is an iterator on a disk block containing a part of a basic program. 
  # Each `gotonext` returns the next line of a basic program.
  # When iterating over a disk block, there are three phases. First, one partial line 
  # (first part is in previous block, second part in current block), then several full 
  # lines, and finally the last partial line (first part in current block, second part 
  # in next block).

  # The iterator returns a 5-tuple:
  #   ( addr   : address of curdata[0]
  #   , offset : offset in block of curdata[0]
  #   , prvdata: data of current basic line from previous block
  #   , curdata: data of current basic line from current block
  #   , nxtdata: data of current basic line for next block
  #   )
  
  # TEST CASES
  # Each has a file in cases.d64
  #
  # Annotation
  #   BB BB block link
  #   AA AA load address
  #   LL LL line link
  #   NN NN line number
  #   xx    (current) line data
  #   ..    non-file data
  #   00    terminating zero
  #   00 00 no more line
  #   |     block sep
  # 
  # case     line in middle
  # CASE-00  .. | .. .. LL LL NN NN xx xx 00 .. .. | ..

  # case     Line is cut by block sep                             [linenum:offset]
  # CASE-01  .. 00 LL LL NN NN xx xx 00 | BB BB LL LL .. .. .. .. .. .. .. [530:2]
  # CASE-02  .. .. 00 LL LL NN NN xx xx | BB BB 00 LL LL .. .. .. .. .. .. [580:3]
  # CASE-03  .. .. .. 00 LL LL NN NN xx | BB BB xx 00 LL LL .. .. .. .. .. [630:4]
  # CASE-04  .. .. .. .. 00 LL LL NN NN | BB BB xx xx 00 LL LL .. .. .. .. [680:5]
  # CASE-05  .. .. .. .. .. 00 LL LL NN | BB BB NN xx xx 00 LL LL .. .. .. [730:6]
  # CASE-06  .. .. .. .. .. .. 00 LL LL | BB BB NN NN xx xx 00 LL LL .. .. [780:7]
  # CASE-07  .. .. .. .. .. .. .. 00 LL | BB BB LL NN NN xx xx 00 LL LL .. [830:8]
  # 
  # case     file ends around block sep
  # CASE-08  xx 00 00 00 .. | .. .. .. .. .. .. ..
  # CASE-09  xx xx 00 00 00 | .. .. .. .. .. .. ..
  # CASE-10  xx xx xx 00 00 | BB BB 00 .. .. .. .. 
  # CASE-11  xx xx xx xx 00 | BB BB 00 00 .. .. ..
  # CASE-12  xx xx xx xx xx | BB BB 00 00 00 .. ..
  # CASE-13  xx xx xx xx xx | BB BB xx 00 00 00 ..

  # Cases
  #   prvdata=[], curdata=* , nxtdata=[] : most of the lines; data comes from "middle" of a block; eg CASE-00
  #   prvdata=* , curdata=* , nxtdata=[] : partial line at the start of a block, the prvdata is from previous block; eg CASE-02..CASE-07,CASE-10,CASE-12,CASE-13
  #   prvdata=[], curdata=[], nxtdata=*  : partial line at the end of a block, but there is second part in next block; eg CASE-02..CASE-07,CASE-12,CASE-13
  #   prvdata=[], curdata=* , nxtdata=*  : special case: curdata=[00 00] i.e. end of file marker, nxtdata is rest of block; CASE-08, CASE-09(nxtdata=[])
  #   prvdata=* , curdata=* , nxtdata=*  : special case: prevdata+curdata=[00 00], nxtdata is rest of block; CASE-10
  #   prvdata=[], curdata=[], nxtdata=[] : special case: previous line ended at end of block, so there is no next line, but not yet at end-of file; CASE-01,CASE-11

  #    + block:Block=block that is iterated
  #    + block1:bool=true if this is the first block of the file (block has t/s-link and load address), false any next block (block has only t/s-link)
  #    + addr:int=load address of the first databyte of this block - ignored if block1
  #    + prvdata:binlist=bytes from previous block
  def __init__(self,block,block1=True,addr=None,prvdata=b"") :
    self.block= block
    self.block1= block1
    self.prvdata= prvdata
    # The following two are the iterator pointer
    self.addr= addr
    self.offset=None

  # Goes to first basic line of the disk block, and returns the following tuple
  def gotofirst(self):
    if self.offset!=None : print("Error: gotonext before gotofirst")
    # Start the iterator at the beginning of the block
    self.offset=2 # skip t/s-link in data[00]/data[01]
    if self.block1 : # first block of basic program file
      if len(self.prvdata)>0 : print("ERROR: first block has no prev sector")
      if self.addr!=None : print("ERROR: addr must be None for 1st block)")
      self.addr= self.block.data[self.offset+0] + 256*self.block.data[self.offset+1]
      self.offset+=2 # skip loadaddr in data[02]/data[03]
      addrnextline= self.block.data[self.offset+0] + 256*self.block.data[self.offset+1]
      offsetnextline= self.offset + addrnextline-self.addr
      prvdata= b""
      curdata= self.block.data[self.offset:offsetnextline]
      nxtdata= b""
    else : # not first block; there might be data from previous block
      if self.addr==None : print("ERROR: addr must be set for non-1st block)")
      prefixedblock = self.prvdata+self.block.data[self.offset:]
      addrnextline= prefixedblock[0] + 256*prefixedblock[1]
      offsetnextline= self.offset + addrnextline-self.addr
      if addrnextline==0 : 
        # next basic line is just 00 00, signalling eof
        prvdata= self.prvdata
        curdata= self.block.data[self.offset:self.offset+2-len(prvdata)] # one/two zeros
        nxtdata= self.block.data[self.offset+2-len(prvdata):] # remainder of block
      else :
        prvdata= self.prvdata
        curdata= self.block.data[self.offset:offsetnextline]
        nxtdata= b""
    if  len(curdata)>0 and curdata[-1]!=0 : print("ERROR: expected 00") # happens to be ok for last line (link is 00 00)
    if addrnextline!=0 and (addrnextline-self.addr<0 or addrnextline-self.addr>80) : 
      print("ERROR: does not seem to be basic")
    tuple=(self.addr,self.offset,prvdata,curdata,nxtdata)
    # move iterator pointer to next basic line
    self.addr  += len(curdata)
    self.offset+= len(curdata)
    return tuple

  # Goes to first basic line of the disk block (usingself.offset=None), and returns the following tuple
  def gotonext(self):
    if self.offset==None : print("Error: gotonext without gotofirst")
    # ignore prvdata (it should have been picked up by gotofirst)

    remainingbytes= BYTESPERBLOCK - self.offset
    if remainingbytes<2 :
      # can't compute addrnextline, push out to next
      prvdata= b""
      curdata= b""
      nxtdata= self.block.data[self.offset:] # WARNING nxtdata could be []
    else : 
      addrnextline= self.block.data[self.offset+0] + 256*self.block.data[self.offset+1]
      offsetnextline= self.offset + addrnextline - self.addr
      if addrnextline==0x0000:
        # next basic line is just 00 00, signalling eof
        prvdata= b""
        curdata= self.block.data[self.offset:self.offset+2] # two zeros
        nxtdata= self.block.data[self.offset+2:] # remainder of block
      elif offsetnextline>BYTESPERBLOCK :
        # basic line not completely in block, push out to next
        prvdata= b""
        curdata= b""
        nxtdata= self.block.data[self.offset:]
      else :
        # basic line extracted from block
        prvdata= b""
        curdata= self.block.data[self.offset:offsetnextline]
        nxtdata= b""
    if len(curdata)>0 and curdata[-1]!=0 : print("ERROR: expected 00")
    if addrnextline!=0 and (addrnextline-self.addr<0 or addrnextline-self.addr>80) : 
      print("ERROR: does not seem to be basic")
    tuple=(self.addr,self.offset,prvdata,curdata,nxtdata)
    # move iterator pointer to next basic line
    self.addr  += len(curdata)
    self.offset+= len(curdata)
    return tuple


#endregion
#region ### DUALLINE ################################################################

class Dualline :

  # (1) accumulates two lines, adding strings or chars via `add`
  # (2) makes sure line are printed using exactly `linelen` characters. 
  # (3) if too short pads with spaces
  # (4) of too long wraps
  # (5) when wraps, prefiexs new lines with `indent`
  # (6) if a char is `add()`ed, and it occurs in `aligners` the shorter of the two accumulated lines is extended with spaces to match the length
  # (7) if `for_human` is False the printing of the first line is suppressed (and so is the length-matchup)


  def __init__(self,linelen,indent,aligners,for_human) : 
    self.line1=""
    self.line2=""
    self.linelen=linelen
    self.indent=indent
    self.aligners= aligners
    self.for_human= for_human

  def _matchlen(self) :
    if self.for_human : return
    l1=len(self.line1)
    l2=len(self.line2) 
    if l1>l2 : self.line2+=" "*(l1-l2)
    if l1<l2 : self.line1+=" "*(l2-l1)

  def add(self,s1,s2) :
    if s2 in self.aligners : self._matchlen()
    fit1 = len(self.line1)+len(s1)<=self.linelen
    fit2 = len(self.line2)+len(s2)<=self.linelen
    fit = (self.for_human or fit1) and fit2
    if fit :
      self.line1+=s1
      self.line2+=s2
    else :
      self.print()
      self.line1=self.indent+s1
      self.line2=self.indent+s2
  
  def print(self) :
    l1=len(self.line1)
    if l1<self.linelen : self.line1+=" "*(self.linelen-l1)
    l2=len(self.line2) 
    if l2<self.linelen : self.line2+=" "*(self.linelen-l2)
    if not self.for_human : print( f"|{self.line1}|" )
    print( f"|{self.line2}|" )


#endregion
#region ### BLOCKS ##################################################################


blocks=[] # The whole d64 file, as a list of Block's (see class below)


# Find a block, given track and sector index
def block_find(tix,six) : 
  for block in blocks:
    if block.tix==tix and block.six==six : return block
  return None


def print_blockmap():
  print( f"|track|zone|   blocks    | 000 001 002 003 004 005 006 007 007 009 010 011 012 013 014 015 016 017 018 019 020 |")
  tix=0
  zix=-1
  for block in blocks:
    if block.zix!=zix :
      print( f"|-----|----|-------------|-------------------------------------------------------------------------------------|")
      zix=block.zix
    if tix!=block.tix : 
      print( f"|{block.tix:^5}|{block.zix:^4}|{block.bix:03}..{block.bix+SECTORSPERTRACK[block.tix]-1:03} ({SECTORSPERTRACK[block.tix]:2})|", end='' )
      tix= block.tix
    typ= block.typ
    if block.isempty(): typ= typ.lower()
    if typ=="fil" : typ='---'
    print( f" {typ}", end='' )
    if block.six+1==SECTORSPERTRACK[block.tix] : 
      print( " "*((21-SECTORSPERTRACK[block.tix])*4)+" |")
  print( f"|-----|----|-------------|-------------------------------------------------------------------------------------|")


def get_dir():
  dir=[]
  for six in range(1,21) :
    block=blocks[357+six]
    for eix in range(0,256,32) :
      ftype = filetype2str(block.data[eix+0x02])
      block1= block_find(block.data[eix+0x03],block.data[eix+0x04])
      bix= None if block1==None else block1.bix
      fname= filename2str( block.data[eix+0x05:eix+0x14+1] )
      fsize= block.data[eix+0x1E] + 256*block.data[eix+0x1F]
      if block.data[eix+0x02] & 0b111 == 0b000 : continue # skip DEL
      dir.append( {'size':fsize,'fname':fname,'ftype':ftype,'block1':bix} )
  return dir


class Block:

  # Returns True iff all data bytes are 0x00
  def isempty(self):
    for b in self.data:
      if b!=0x00: return False
    return True

  # Returns the next block, using the t/s-link in the current (returns None if link is oef)
  def next(self):
    tix= self.data[0x00]
    six= self.data[0x01]
    block= None
    if tix==0x00: 
      # print( f"t/s-link=00/xx: no next")
      pass
    else :
      block= block_find(tix,six)
      if block==None :
        #print( f"t/s-link={tix}/{six}: not found")
        pass
      else :
        #print( f"t/s-link {tix}/{six}")
        pass
    return block

  # Returns the block id as a long string
  def get_blockid(self):
    return f"block {self.bix} zone {self.zix}/{self.zsz} track {self.tix} sector {self.six} type {self.typ}"

  # Returns block and its successors as a bin array
  def tobin(self):
    block= self
    bin=b''
    while block.data[0x00]!=0x00 :
      bin+= block.data[0x02:]
      block= block.next()
    # data[0x00]=tix=00, so last block
    last=block.data[0x01]
    bin+= block.data[0x02:last+1]
    return bin

  # Block prints itself in hex format
  def print_hex(self,with_blockid=True,with_header=True,with_nexts=0):
    if with_blockid : print( f"|{self.get_blockid():-<75}|")
    if with_header : 
      print( f"|offset| 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | 0123456789ABCDEF |")
      print( f"|------|-------------------------------------------------|------------------|")
    if self.data[0x00]==0x00 :
      # tix=00, so last block
      last_dix=self.data[0x01]
    else :
      last_dix=0x255
    linesep=" "
    for dix1 in range(0,BYTESPERBLOCK,16):
      print( f"|  {dix1:^02X}  |", end='' )
      for dix2 in range(dix1,dix1+16):
        if dix2>last_dix: linesep="*"
        print( f"{linesep}{self.data[dix2]:02X}", end='')
      print( f"{linesep}| ", end='' )
      for dix2 in range(dix1,dix1+16):
        ch= makeprintable(chr(self.data[dix2]))
        print( ch, end='')
      print(" |")
    if with_header : 
      print( f"|------|-------------------------------------------------|------------------|")
    if with_nexts>0 :
      block= self.next()
      if block!=None : 
        block.print_hex(with_blockid,with_header,with_nexts-1)
      else : 
        print( f"no next block (request was {with_nexts})")

  # Block prints itself in technical BAM format (all raw bytes annotated)
  def print_bamtech(self,with_blockid=False,with_header=True) :
    if with_blockid : print( f"|{self.get_blockid():-<58}|" )
    if with_header : 
      print( f"|field   | offset | data        | meaning                  |" )
      print( f"|--------|--------|-------------|--------------------------|" )
    print( f"|dir t/s | 00  01 | {self.data[0x00]:02X} {self.data[0x01]:02X}       | {self.data[0x00]:02}/{self.data[0x01]:02}                    |" )
    print( f"|dos ver |     02 | {self.data[0x02]:02X}          | '{filename2str(self.data[0x02:0x03])}'                      |" )
    print( f"|unused  |     03 | {self.data[0x03]:02X}          |                          |" )
    tix=1
    free=0
    for bix in range(0x04,0x90,4) :
      raw = f"{self.data[bix]:02X} {self.data[bix+1]:02X} {self.data[bix+2]:02X} {self.data[bix+3]:02X}"
      if tix!=18 : free += self.data[bix]
      # compute bit vector
      matrix= (self.data[bix+1]<<0) + (self.data[bix+2]<<8) + (self.data[bix+3]<<16)
      bits=f"{matrix:024b}"[::-1]
      len=SECTORSPERTRACK[tix]
      rest=bits[len-24:].replace('0','c').replace('1','s')
      bits=bits[0:len]+rest
      # print
      print( f"|bam t{tix:02} | {bix:02X}..{bix+3:02X} | {raw} | {bits} |")
      tix+=1
    print( f"|bam *   | 04..8F | {free:03X}         | {free:3} blocks free          |")
    dname= "'"+filename2str( self.data[0x90:0xA0] )+"'"
    print( f"|dname0  | 90..93 | {self.data[0x90]:02X} {self.data[0x91]:02X} {self.data[0x92]:02X} {self.data[0x93]:02X} | ...                      |")
    print( f"|dname1  | 93..97 | {self.data[0x94]:02X} {self.data[0x95]:02X} {self.data[0x96]:02X} {self.data[0x97]:02X} | ...                      |")
    print( f"|dname2  | 98..9B | {self.data[0x98]:02X} {self.data[0x99]:02X} {self.data[0x9A]:02X} {self.data[0x9B]:02X} | ...                      |")
    print( f"|dname3  | 9C..9F | {self.data[0x9C]:02X} {self.data[0x9D]:02X} {self.data[0x9E]:02X} {self.data[0x9F]:02X} | ...                      |")
    print( f"|diskname| 90..9F | ...         | {dname:24s} |")
    print( f"|unused  |     A0 | {self.data[0xA0]:02X}          |                          |" )
    print( f"|unused  |     A1 | {self.data[0xA1]:02X}          |                          |" )
    print( f"|diskid  | A2  A3 | {self.data[0xA2]:02X} {self.data[0xA3]:02X}       | '{filename2str(self.data[0xA2:0xA4])}'                     |" )
    print( f"|unused  |     A4 | {self.data[0xA4]:02X}          |                          |" )
    print( f"|dostype | A5  A6 | {self.data[0xA5]:02X} {self.data[0xA6]:02X}       | '{filename2str(self.data[0xA5:0xA7])}'                     |" )
    print( f"|unused  | A7..FF | ...         |                          |")
    if with_header : 
      print( f"|--------|--------|-------------|--------------------------|" )

  # Block prints itself in human BAM format (only the human friendly fields)
  def print_bamhuman(self,with_blockid=False,with_header=True) :
    if with_blockid : print( f"|{self.get_blockid():-<50}|" )
    if with_header : 
      print( f"|field      | value                                |" )
      print( f"|-----------|--------------------------------------|" )
    print( f"|dos version| {self.data[0x02]:02X} = '{filename2str(self.data[0x02:0x03])}'                             |" )
    tix=1
    free=0
    for bix in range(0x04,0x90,4) :
      if tix!=18 : free += self.data[bix]
      tix+=1
    print( f"|blocks free| {free:3} / {BLOCKSPERDISK:3} ({BLOCKSPERDISK-free:3} used)                 |")
    print( f"|           | use --mtech to see available blocks  |")
    dname= "'"+filename2str( self.data[0x90:0xA0] )+"'"
    print( f"|diskname   | {dname:18s} (set with format) |")
    print( f"|diskid     | {self.data[0xA2]:02X} {self.data[0xA3]:02X} = '{filename2str(self.data[0xA2:0xA4])}'       (set with format) |" )
    print( f"|dostype    | {self.data[0xA5]:02X} {self.data[0xA6]:02X} = '{filename2str(self.data[0xA5:0xA7])}'                         |" )
    if with_header : 
      print( f"|-----------|--------------------------------------|" )

  # Block prints itself in technical dir format (all raw bytes annotated)
  def print_dirtech(self,with_blockid=True,with_header=True,with_nexts=0,with_rawdata=True,label=0):
    if with_blockid : print( f"|{self.get_blockid():-<127}|")
    if with_header : 
      print( f"|label|nextdir|filetype| block1| filename                                        | relss |relrecsz| unused            |file size|")
      print( f"|-----|-------|--------|-------|-------------------------------------------------|-------|--------|-------------------|---------|")
    for eix in range(0,256,32) :
      if with_rawdata :
        print( f"|{label:^5}| {self.data[eix+0x00]:02X} {self.data[eix+0x01]:02X} |   {self.data[eix+0x02]:02X}   | {self.data[eix+0x03]:02X} {self.data[eix+0x04]:02X} |", end='' )
        for d in self.data[eix+0x05:eix+0x14+1] : print(f" {d:02X}", end='')
        print( f" | {self.data[eix+0x15]:02X} {self.data[eix+0x16]:02X} |   {self.data[eix+0x17]:02X}   |", end='' )
        for d in self.data[eix+0x18:eix+0x1D+1] : print(f" {d:02X}", end='')
        print( f" |  {self.data[eix+0x1E]:02X} {self.data[eix+0x1F]:02X}  |" )
      # The entry track/sector link (shall be 0/0 exept for first)
      ts_nextdir= f"{self.data[eix+0x00]}/{self.data[eix+0x01]}"
      # Actual file type
      ftype = filetype2str(self.data[eix+0x02])
      # The data track/sector link (to first block of the file)
      ts_block1 = f"{self.data[eix+0x03]}/{self.data[eix+0x04]}" 
      # Filename
      fname= filename2str( self.data[eix+0x05:eix+0x14+1] )
      # The sidesector track/sector link (for REL files only)
      ts_relss = f"{self.data[eix+0x15]}/{self.data[eix+0x16]}" 
      # REL file record length (REL file only, max. value 254)
      relrecsize = self.data[eix+0x017]
      # 18-1D: Unused (except with GEOS disks)
      # self.data[eix+0x018..eix+0x01D]
      # File size in blocks (little endian);  in bytes approx #blocks * 254
      fsize= self.data[eix+0x1E] +256*self.data[eix+0x1F]
      # apply na
      if self.data[eix+0x02] & 0b111 != 0b100 : 
        ts_relss='na'
        relrecsize='na'
      else :
        relrecsize=str(relrecsize)+' byte'
      print( f"|{label:^5}|{ts_nextdir:^7s}|{ftype:^8s}|{ts_block1:^7s}| {fname:{16*3}}|{ts_relss:^7s}|{relrecsize:^8s}|{'':{6*3}} |{str(fsize)+' block':^9s}|" ) 
      label+=1
    if with_header : 
      print( f"|-----|-------|--------|-------|-------------------------------------------------|-------|--------|-------------------|---------|")
    if with_nexts>0 :
      block= self.next()
      if block!=None : 
        block.print_dirtech(with_blockid=with_blockid,with_header=False,with_nexts=with_nexts-1,with_rawdata=with_rawdata,label=label)
      else : 
        print( f"no next block (request was {with_nexts})")

  # Block prints itself in human dir format (filename/filetype)
  def print_dirhuman(self,with_blockid=True,with_header=True,with_nexts=17):
    if with_blockid : print( f"|{self.get_blockid():-<52}|" )
    if with_header : 
      print( f"| blocks | filename           | filetype | block1    |" )
      print( f"|--------|--------------------|----------|-----------|" )
    for eix in range(0,256,32) :
      ftype = filetype2str(self.data[eix+0x02])
      block1= block_find(self.data[eix+0x03],self.data[eix+0x04])
      ts_block1 = f" {self.data[eix+0x03]:02X}/{self.data[eix+0x04]:02X}={'none' if block1==None else f'{block1.bix:3} '}" 
      fname= "'"+filename2str( self.data[eix+0x05:eix+0x14+1] )+"'"
      fsize= self.data[eix+0x1E] +256*self.data[eix+0x1F]
      if self.data[eix+0x02] & 0b111 == 0b000 : continue # skip DEL
      print( f"| {fsize:^6} | {fname:<18s} | {ftype:^8s} |{ts_block1}|" ) 
    if with_nexts>0 :
      block= self.next()
      if block!=None : 
        block.print_dirhuman(with_blockid=with_blockid,with_header=False,with_nexts=with_nexts-1)
      else : 
        print( f"no next block (request was {with_nexts})")

  # Block prints itself in technical basic format (all raw bytes annotated)
  def print_filebasic(self,block1=True,addr=None,prvdata=b"",with_blockid=True,with_header=True,with_nexts=0,for_human=False):

    tablen=132
    def printlink(data) :
      msg=f"[last byte at offset {data[0x01]:02X}] " if data[0x00]==0 else ""
      link= f"| link | 00 |        |       | {data[0x00]:02X} {data[0x01]:02X} {msg}(decimal {data[0x00]}/{data[0x01]})"
      link+=" "*(tablen-len(link))+" |"
      print( link )

    linesep= "|------|----|--------|-------|"
    linesep+="-"*(tablen-len(linesep))+"-|"
    if with_blockid : print( f"|{self.get_blockid():-<{tablen}}|" )
    if with_header :
      header= "| addr |offs|nextaddr|linenum| data"
      header+=" "*(tablen-len(header))+" |"
      print( header ) 
      print( linesep )

    if not for_human : printlink(self.data)
    offset= 2

    if block1 :
      loadaddr=self.data[0x02]+256*self.data[0x03]
      offset= 4
      load= f"| load | 02 |        |       | {self.data[0x02]:02X} {self.data[0x03]:02X} (decimal {loadaddr:5})"
      load+=" "*(tablen-len(load))+" |"
      print( load )

    # Start iterator
    iter = BasicLineIter(self,block1,addr,prvdata)
    (addr,offset,prvdata,curdata,nxtdata)= iter.gotofirst()
    while True :
      # We are goin to print two lines (hex and human)
      if not for_human : print(linesep)
      dual= Dualline(tablen,"      |    |        |       | ",":"+CHAR00,for_human)

      ###### print "header columns":  addr, offs, nextaddr, linenum

      # addr and offset always there
      dual.add( f" {addr:04X} | {offset:02X} ", f"{addr:5} |{offset:3} " )
      
      # Is there data from a previous block? Then it was printed on previous block
      data= prvdata+curdata+nxtdata
      data0= f"{data[0]:02X}" if len(data)>0 else "  " # nextaddr lsb
      data1= f"{data[1]:02X}" if len(data)>1 else "  " # nextaddr msb
      data2= f"{data[2]:02X}" if len(data)>2 else "  " # linnum lsb
      data3= f"{data[3]:02X}" if len(data)>3 else "  " # linenum msb
      nextaddr= f"{data[0]+256*data[1]:5}" if len(data)>1 else "     "
      linenum=  f"{data[2]+256*data[3]:5}" if len(data)>3 else "     "
      if nextaddr=="    0":
        data2="  "
        data3="  "
        linenum="     " 
      
      # start outputting  
      if len(prvdata)==0 :
        dual.add( f"|  {data0} {data1} " , f"|  {nextaddr} " )
        dual.add( f"| {data2} {data3} ", f"| {linenum} ")
      elif len(prvdata)==1 :
        # only lsb of link was printed in previous block
        dual.add( f"|  .. {data1} " , f"|  {nextaddr} " )
        dual.add( f"| {data2} {data3} ", f"| {linenum} ")
      elif len(prvdata)==2 :
        # only lsb and msb of link was printed in previous block
        dual.add( f"|  .. .. " , f"|  ..... " )
        dual.add( f"| {data2} {data3} ", f"| {linenum} ")
      elif len(prvdata)==3 :
        # only lsb and msb of link and lsb of linenum was printed in previous block
        dual.add( f"|  .. .. " , f"|  ..... " )
        dual.add( f"| .. {data3} ", f"| {linenum} ")
      else :
        dual.add( f"|  .. .. " , f"|  ..... " )
        dual.add( f"| .. .. ", f"| ..... ")

      ###### print "data column"

      # start of data column
      dual.add( f"| ", f"| " )

      # indent for prvdata
      data=prvdata[4:]
      if for_human:
        if len(data)>0 : dual.add("","... ")
      else :
        for d in data : 
          dual.add( ".. ", f".. " )

      # print curdata
      data=curdata[4-len(prvdata):] 
      for d in data : 
        dual.add( f"{d:02X} ", f"{token(d)}" )

      # special annotation at end of file
      if nextaddr=="    0" :
        msg= "ok" if iter.block.data[0x01]==offset+1-len(prvdata) else "ERROR" # offset is on first byte of 00 00, but second byte of 00 00 is last of block
        dual.add("no more basic line",f"block link is {iter.block.data[0x01]:02X}, last offset is {offset+1-len(prvdata):02X} ({msg})")
        dual.print()
        print(linesep)         
        dual= Dualline(tablen,"      |    |        |       | ","",for_human)
        dual.add( f" {addr+2:04X} |{f'{offset+2-len(prvdata):02X}':>3} | rest in|       | ", f"{addr+2:5} |{offset+2-len(prvdata):3} | block  |       | " )

      # print part for next block
      data=nxtdata if nextaddr=="    0" else nxtdata[4:]
      for d in data : 
        dual.add( f"{d:02X} ", f"{token(d)}" )

      # actually print all collected data
      dual.print()

      # special annotation at end of file
      if nextaddr=="    0" :
        print(linesep)
        break

      nextblock= len(curdata)==0
      if not nextblock :
        # Next line comes from current block
        (addr,offset,prvdata,curdata,nxtdata)= iter.gotonext()
        # Special case, there was no next line in current block
        if len(curdata)==0 and len(nxtdata)==0 : nextblock=True

      if nextblock :
        # Do we go to next block?
        if with_nexts==0 : 
          print(linesep)
          break
        with_nexts -= 1
        # For next line, we need to go to the next block
        iter = BasicLineIter(iter.block.next(),False,addr+len(nxtdata),nxtdata)
        (addr,offset,prvdata,curdata,nxtdata)= iter.gotofirst()
        if with_blockid : print( f"|{iter.block.get_blockid():-<{tablen}}|" )
        if not for_human : printlink(iter.block.data)


  def __init__(self,bix,data):
    self.data= data  # content of the sector
    self.bix= bix    # index of the block [0,BLOCKSPERDISK)
    tix=1
    zix=0
    while bix >= SECTORSPERTRACK[tix] :
      bix -= SECTORSPERTRACK[tix]
      tix += 1
      if SECTORSPERTRACK[tix-1]!=SECTORSPERTRACK[tix] : zix+=1
    self.tix=tix     # track index
    self.six=bix     # sector index
    self.zsz=SECTORSPERTRACK[tix] # zone size
    self.zix=zix     # zone index
    self.typ='FIL'
    if self.tix==18 :
      self.typ='DIR'
      if self.six==0 :
        self.typ='BAM'



#endregion
#region ### main ####################################################################
  
def main() :
  global blocks

  parser = argparse.ArgumentParser(prog='d64viewer',
                    description='Prints disk blocks inside a d64 file in hex/bam/dir/basic format',
                    epilog='2025 Maarten Pennings')
  parser.add_argument("filename")
  topicgroup = parser.add_argument_group('topic','Select which disk blocks to print, default is --tdir')
  topicgroupx = topicgroup.add_mutually_exclusive_group()
  topicgroupx.add_argument('--tblock', help='topic is a disk block, pass either <num> (0..682) or <track>/<sector> (1..35/0..16|17|18|20)',metavar='blockix')
  topicgroupx.add_argument('--tbam', help='topic is the block availability matrix', action='store_true')
  topicgroupx.add_argument('--tdir', help='topic is the directory, pass nothing or 1..18', nargs='?', type=int, const=0)
  topicgroupx.add_argument('--tfile', help='topic is a file, pass filename (optionally enclosed in \'\' or "")', metavar='filename')
  topicgroupx.add_argument('--tdisk', help='topic is disk overview', action='store_true')
  viewgroup = parser.add_argument_group('view', 'Which view is used for the selected block, default is "implied by topic"')
  viewgroupx = viewgroup.add_mutually_exclusive_group()
  viewgroupx.add_argument('--vhex', help='view as raw hex table (always "tech")', action='store_true')
  viewgroupx.add_argument('--vbam', help='view as BAM table', action='store_true')
  viewgroupx.add_argument('--vdir', help='view as directry entries', action='store_true')
  viewgroupx.add_argument('--vbasic', help='view as basic program (must start with first block of program)', action='store_true')
  modgroup = parser.add_argument_group('modifiers','Allows to add/suppress features of the view')
  modgroup.add_argument('--mtech', help='modify view to be more tech (0, 1, 2)', default=0, nargs='?', type=int, const=1)
  modgroup.add_argument('--mblockid', help='modify view with *no* blockid\'s', action='store_true')
  modgroup.add_argument('--mheader', help='modidy view with *no* column headers', action='store_true')
  modgroup.add_argument('--mnotes', help='modify view with documentation notes', action='store_true')
  modgroup.add_argument('--mcont', help='modify view by continuing with next blocks (tdir and vbasic have own defaults)', metavar='num') # with_next
  modgroup.add_argument('--msave', help='saves the selected disk blocks to file (raw, not the view), pass filename', metavar='filename') # with_next
  #sys.argv= "d64viewer.py cases.d64 --tfile CASE-09".split(" ")
  #sys.argv= "d64viewer.py cases.d64 --tblock 345 --vbasic --mcont 8".split(" ")
  #sys.argv= "d64viewer.py cases.d64 --tfile CASE-08 --vbasic --msave c08-1.txt --mtech 1".split(" ")
  #sys.argv= "d64viewer.py ..\\testcases\\cases.d64 --tfile CASE-09 --vbasic".split(" ")
  args = parser.parse_args()
  #print(args) # todo remove

  # Check if filename maps to an existing file of the correct size
  if not os.path.exists(args.filename):
    sys.exit(f"{parser.prog}: error: {args.filename} not found")
  with open(args.filename, mode='rb') as file: 
    content = file.read()
  if len(content)%BYTESPERBLOCK != 0 :
    sys.exit( f"{parser.prog}: error: {args.filename} has size {len(content)} which is not a multiple of {BYTESPERBLOCK}" )
  if len(content)//BYTESPERBLOCK != BLOCKSPERDISK :
    sys.exit( f"{parser.prog}: error: {args.filename} has {len(content)//BYTESPERBLOCK} blocks, this program is written for disks with {BLOCKSPERDISK} blocks" )
  print( f"{parser.prog}: file '{args.filename}' has {len(content)//BYTESPERBLOCK} blocks of {BYTESPERBLOCK} bytes")
  # load file
  for bix in range(len(content)//BYTESPERBLOCK):
    blocks.append( Block(bix,content[bix*BYTESPERBLOCK:(1+bix)*BYTESPERBLOCK] ) )

  # Determine topic (and block index)
  bix=-1
  topic=""
  tmsg=""
  if args.tblock!=None :
    nums= args.tblock.split("/")
    if len(nums)!=1 and len(nums)!=2 :
      sys.exit( f"{parser.prog}: error: tblock must have form <blockix> or <trackix>/<sectorix>, not {args.tblock}" )
    if not all(map(str.isdigit,nums)) :
      sys.exit( f"{parser.prog}: error: tblock must be num or num/num, not {args.tblock}" )
    if len(nums)==1 :
      bix=int(nums[0])
      if bix<0 or bix>BLOCKSPERDISK:
        sys.exit( f"{parser.prog}: error: tblock its blockix is {bix}, must be 0..{BLOCKSPERDISK-1}, not {bix}" )
      tmsg= f"{bix}"
    else : 
      tix= int(nums[0])
      six= int(nums[1])
      if tix<1 or tix>=len(SECTORSPERTRACK)-2 : # SECTORSPERTRACK has two sentinels (val -1)
        sys.exit( f"{parser.prog}: error: tblock its blockix is {tix}/{six}, but track must be 1..{len(SECTORSPERTRACK)-2}. not {tix}" )
      if six<0 or six>=SECTORSPERTRACK[tix] : 
        sys.exit( f"{parser.prog}: error: tblock its blockix is {tix}/{six}, but track {tix} has sectors 0..{SECTORSPERTRACK[tix]-1}, not {six}" )
      bix= block_find(tix,six).bix
      if bix==None :
        sys.exit( f"{parser.prog}: error: tblock unexpected error in parsing {args.tblock}" )
      tmsg= f"{tix}/{six}={bix}"
    topic="block"
  elif args.tbam:
    bix= 357 # block index of the BAM
    tmsg= f"at {bix}"
    topic="bam"
  elif args.tdir!=None:
    six= args.tdir # we can not distinguish between "--tdir" and "--tdir 0"
    if six==0 : six=1
    if six<1 or six>18 : # directory blocks on track 17
      sys.exit( f"{parser.prog}: error: tdir its sectorix must be 1..18, not {six}" )
    bix=357+six
    tmsg= f"357+{six}={bix}"
    topic="dir"
  elif args.tfile!=None:
    fname= args.tfile
    if fname[0]=='"' and fname[-1]=='"' : fname= fname[1:-1]
    elif fname[0]=="'" and fname[-1]=="'" : fname= fname[1:-1]
    found= None
    for entry in get_dir():
      if entry['fname']==fname : 
        found=entry
        break
    if found==None :
      sys.exit( f"{parser.prog}: error: tfile could not find filename '{fname}'" )
    bix= found['block1']
    tmsg= f"{fname} at {bix}"
    topic="file"
  elif args.tdisk:
    bix=-1
    tmsg="(all blocks)"
    topic="disk"
  else :
    bix=357+1
    tmsg= f"starts at {bix}"
    topic="dir"

  # Determine view
  view=""
  if args.vhex :
    view= "hex"
  elif args.vbam :
    view= "bam"
  elif args.vdir :
    view= "dir"
  elif args.vbasic :
    view= "basic"
  else :
    if   topic=="block" : view= "hex"
    elif topic=="bam"   : view= "bam"
    elif topic=="dir"   : view= "dir"
    elif topic=="file"  : view= "hex" # basic
    elif topic=="disk"  : view= "disk"
    else :
      sys.exit( f"{parser.prog}: error: view unexpected error in parsing" )
  if topic=="disk" and view!="disk" :
    sys.exit( f"{parser.prog}: error: topic disk has dedicated view, not {view}" )

  # Determine modifiers
  mmsg=""
  mcont=0
  if args.mtech<0 or args.mtech>2 : 
    sys.exit( f"{parser.prog}: error: mtech must be 0..2, not {args.mtech}" )
  mmsg+= f" tech{args.mtech}"
  if args.mblockid:
    mmsg+= " blockid"
  if args.mheader:
    mmsg+= " header"
  if args.mnotes:
    mmsg+= " notes"
  if args.mcont!=None:
    if not args.mcont.isdigit() :
      sys.exit( f"{parser.prog}: error: mcont must be num, not {args.tdir}" )
    mcont= int(args.mcont)
    if mcont<0 or mcont>BLOCKSPERDISK : 
      sys.exit( f"{parser.prog}: error: unexpected value for mcont: {mcont}" )
    mmsg+= f" cont({mcont})"
  if args.msave!=None:
    if os.path.exists(args.msave):
      sys.exit( f"{parser.prog}: error: msave file {args.msave} already exists" )
    mmsg+= f" save({args.msave})"
  if mmsg=="" : 
    mmsg="no modifiers"
  else : 
    mmsg= mmsg[1:] # strip leading space
  # convenient defaults
  if args.mcont==None :
    if args.tblock==None and not args.tbam and args.tdir==None and args.tfile==None and not args.tdisk:
      mcont=17 # entire dir
      mmsg+= f" cont({mcont})"
    if args.tdir==0 : 
      mcont=17 # entire dir
      mmsg+= f" cont({mcont})"
    if args.tfile!=None : 
      mcont=682 # ensure whole file
      mmsg+= f" cont({mcont})"

  # feedback
  print( f"showing {topic} {tmsg} as {view} [{mmsg}]")
  print()
  
  # Now run (mtech, mblockid, mheader, mnotes, mcont)
  if view=="hex" : 
    if args.mtech>0 : print( f"{parser.prog}: warning: hex view has no tech levels (ignoring --mtech)\n" )
    blocks[bix].print_hex(with_blockid=not args.mblockid,with_header=not args.mheader,with_nexts=mcont)
    if args.mnotes : 
      print()
      help_hex()
  elif view=="bam" : 
    if args.mtech>1 : print( f"{parser.prog}: warning: mtech {args.mtech} is not applicable to bam view\n" )
    if args.mcont : print( f"{parser.prog}: warning: bam view is always 1 block (ignoring --mcont)\n" )
    if args.mtech==0 :
      blocks[bix].print_bamhuman(with_blockid=not args.mblockid,with_header=not args.mheader)
    else :
      blocks[bix].print_bamtech(with_blockid=not args.mblockid,with_header=not args.mheader)
    if args.mnotes : 
      print()
      help_bam()
  elif view=="dir" : 
    if args.mtech==0 :
      blocks[bix].print_dirhuman(with_blockid=not args.mblockid,with_header=not args.mheader,with_nexts=mcont)
    else :
      blocks[bix].print_dirtech(with_blockid=not args.mblockid,with_header=not args.mheader,with_nexts=mcont,with_rawdata=args.mtech==2)
    if args.mnotes : 
      print()
      help_dir()
  elif view=="basic" : 
    if args.mtech>1 : print( f"{parser.prog}: warning: mtech {args.mtech} is not applicable to basic view\n" )
    blocks[bix].print_filebasic(block1=True,addr=None,prvdata=b"",with_blockid=not args.mblockid,with_header=not args.mheader,with_nexts=mcont,for_human=args.mtech==0)
    if args.mnotes : 
      print()
      help_basic()
  elif view=="disk"  : 
    if args.mtech>0 : print( f"{parser.prog}: warning: disk view is always tech (ignoring --mtech)\n" )
    if args.mblockid : print( f"{parser.prog}: warning: disk view has no blocks (ignoring --mblockid)\n" )
    if args.mheader : print( f"{parser.prog}: warning: disk view has no headers (ignoring --mheader)\n" )
    if args.mcont : print( f"{parser.prog}: warning: disk view has no blocks (ignoring --mcont)\n" )
    print_blockmap()
    if args.mnotes : 
      print()
      help_disk()
  else :
    sys.exit( f"{parser.prog}: error: unexpected error running ({view})" )

  if args.msave!=None :
    bin= blocks[bix].tobin()
    with open(args.msave, mode='wb') as file: 
      content = file.write(bin)
      print( f"saved '{args.msave}'")

  # BAM at 357
  # DIR at 358
  # file CASES1-7 at 336
  # file CASE-08  at 337
  # file CASE-09  at 338
  # file CASE-10  at 341
  # file CASE-11  at 353
  # file CASE-12  at 345
  # file CASE-13  at 376


if __name__ == "__main__":
  main()

#endregion




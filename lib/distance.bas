FUNCTION fastcall distance (a as ubyte, b as ubyte) as uInteger

REM returns a fast approximation of SQRT (a^2 + b^2) - the distance formula, generated from taylor series expansion.
REM This version fundamentally by Alcoholics Anonymous, improving on Britlion's earlier version - which itself
REM was suggested, with thanks, by NA_TH_AN.

asm
 POP HL ;' return address
 ;' First parameter in A
 POP BC ;' second parameter -> B
 PUSH HL ;' put return back

 ;' First find out which is bigger - A or B.
 cp b
 ld c,b
 jr nc, distance_AisMAX
 ld c,a

distance_AisMAX:

 ;' c = MIN(a,b)

 srl c     ;' c = MIN/2
 sub c   ;' a = A - MIN/2
 srl c    ;' c = MIN/4
 sub c   ;' a = A - MIN/2 - MIN/4
 srl c
 srl c    ;' c = MIN/16
 add a,c   ;' a = A - MIN/2 - MIN/4 + MIN/16
 add a,b   ;' a = A + B - MIN/2 - MIN/4 + MIN/16

 ld l,a
 ld h,0     ;' hl = result
 ret nc
 inc h      ;' catch 9th bit
END ASM
END FUNCTION


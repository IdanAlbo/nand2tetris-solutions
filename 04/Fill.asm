// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(INPUT)
    //i=0
    @i
    M=0
    //if (KBD != 0), jump to BLACK
    //else, jump to WHITE
    @KBD
    D=M
    @BLACK
    D;JNE
    @WHITE
    D;JEQ

(BLACK)
    //if (i == 8192), jump back to INPUT
    @i
    D=M
    @8192
    D=A-D
    @INPUT
    D;JEQ
    //set RAM[SCREEN + i] = -1 (to black)
    @SCREEN
    D=A
    @i
    A=D+M
    M=-1
    //i = i + 1
    @i
    M=M+1
    //goto BLACK
    @BLACK
    0;JMP

(WHITE)
    //if (i == 8192), jump back to INPUT
    @i
    D=M
    @8192
    D=A-D
    @INPUT
    D;JEQ
    //set RAM[SCREEN + i] = 0 (to white)
    @SCREEN
    D=A
    @i
    A=D+M
    M=0
    //i = i + 1
    @i
    M=M+1
    //goto WHITE
    @WHITE
    0;JMP
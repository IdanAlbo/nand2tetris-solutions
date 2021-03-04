// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

//sum = 0
//i = 0

//while (i < R1)
//  sum = sum + R0
//  i = i + 1

//R2 = sum
//end

    @sum
    M=0
    @i
    M=0
(LOOP)
    //while (i < R1)
    @i
    D=M
    @R1
    D=D-M
    @CALC
    D;JGE
    //  sum = sum + R0
    @R0
    D=M
    @sum
    M=M+D
    //  i = i + 1
    @i
    M=M+1
    //goto loop
    @LOOP
    0;JMP
(CALC)
    @sum
    D=M
    @R2
    M=D
    @END
    0;JMP
(END)
    @END
    0;JMP
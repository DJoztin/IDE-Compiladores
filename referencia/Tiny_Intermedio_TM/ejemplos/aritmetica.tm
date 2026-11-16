* TINY Compilation to TM Code
* File: ejemplos/aritmetica.tm
* Standard prelude:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* End of standard prelude.
  2:     IN  0,0,0 	read integer value
  3:     ST  0,0(5) 	read: store value
* -> assign
* -> Op
* -> Op
* -> Id
  4:     LD  0,0(5) 	load id value
* <- Id
  5:     ST  0,0(6) 	op: push left
* -> Const
  6:    LDC  0,1(0) 	load const
* <- Const
  7:     LD  1,0(6) 	op: load left
  8:    ADD  0,1,0 	op +
* <- Op
  9:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
 10:     LD  0,0(5) 	load id value
* <- Id
 11:     ST  0,-1(6) 	op: push left
* -> Const
 12:    LDC  0,2(0) 	load const
* <- Const
 13:     LD  1,-1(6) 	op: load left
 14:    SUB  0,1,0 	op -
* <- Op
 15:     LD  1,0(6) 	op: load left
 16:    MUL  0,1,0 	op *
* <- Op
 17:     ST  0,1(5) 	assign: store value
* <- assign
* -> Id
 18:     LD  0,1(5) 	load id value
* <- Id
 19:    OUT  0,0,0 	write ac
* End of execution.
 20:   HALT  0,0,0 	

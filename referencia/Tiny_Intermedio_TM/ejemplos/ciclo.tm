* TINY Compilation to TM Code
* File: ejemplos/ciclo.tm
* Standard prelude:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* End of standard prelude.
  2:     IN  0,0,0 	read integer value
  3:     ST  0,0(5) 	read: store value
* -> repeat
* repeat: jump after body comes back here
* -> assign
* -> Op
* -> Id
  4:     LD  0,0(5) 	load id value
* <- Id
  5:     ST  0,0(6) 	op: push left
* -> Const
  6:    LDC  0,1(0) 	load const
* <- Const
  7:     LD  1,0(6) 	op: load left
  8:    SUB  0,1,0 	op -
* <- Op
  9:     ST  0,0(5) 	assign: store value
* <- assign
* -> Op
* -> Id
 10:     LD  0,0(5) 	load id value
* <- Id
 11:     ST  0,0(6) 	op: push left
* -> Const
 12:    LDC  0,0(0) 	load const
* <- Const
 13:     LD  1,0(6) 	op: load left
 14:    SUB  0,1,0 	op ==
 15:    JEQ  0,2(7) 	br if true
 16:    LDC  0,0(0) 	false case
 17:    LDA  7,1(7) 	unconditional jmp
 18:    LDC  0,1(0) 	true case
* <- Op
 19:    JEQ  0,-16(7) 	repeat: jmp back to body
* <- repeat
* -> Id
 20:     LD  0,0(5) 	load id value
* <- Id
 21:    OUT  0,0,0 	write ac
* End of execution.
 22:   HALT  0,0,0 	

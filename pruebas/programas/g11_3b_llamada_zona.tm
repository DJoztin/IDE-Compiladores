* Compilacion a codigo TM (esquema TINY de Louden)
* File: g11_3b_llamada_zona.tm
* Standard prelude:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* End of standard prelude.
* declaracion int clave, minutos (loc 0, 1)
* declaracion float precio, costo (loc 2, 3)
  2:     IN  0,0,0 	read integer value
  3:     ST  0,0(5) 	read: store value
  4:     IN  0,0,0 	read integer value
  5:     ST  0,1(5) 	read: store value
* -> assign
* -> Const
  6:    LDC  0,0(0) 	load const
* <- Const
  7:    LDC  1,1.0(0) 	conv: load 1.0
  8:    MUL  0,0,1 	conv int->float
  9:     ST  0,2(5) 	assign: store value
* <- assign
* -> if
* -> Op
* -> Id
 10:     LD  0,0(5) 	load id value
* <- Id
 11:     ST  0,0(6) 	op: push left
* -> Const
 12:    LDC  0,12(0) 	load const
* <- Const
 13:     LD  1,0(6) 	op: load left
 14:    SUB  0,1,0 	op ==
 15:    JEQ  0,2(7) 	br if true
 16:    LDC  0,0(0) 	false case
 17:    LDA  7,1(7) 	unconditional jmp
 18:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
 20:    LDC  0,2(0) 	load const
* <- Const
 21:    LDC  1,1.0(0) 	conv: load 1.0
 22:    MUL  0,0,1 	conv int->float
 23:     ST  0,2(5) 	assign: store value
* <- assign
* if: jump to end belongs here
 19:    JEQ  0,5(7) 	if: jmp to else
 24:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
 25:     LD  0,0(5) 	load id value
* <- Id
 26:     ST  0,0(6) 	op: push left
* -> Const
 27:    LDC  0,15(0) 	load const
* <- Const
 28:     LD  1,0(6) 	op: load left
 29:    SUB  0,1,0 	op ==
 30:    JEQ  0,2(7) 	br if true
 31:    LDC  0,0(0) 	false case
 32:    LDA  7,1(7) 	unconditional jmp
 33:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
 35:    LDC  0,2.2(0) 	load const
* <- Const
 36:     ST  0,2(5) 	assign: store value
* <- assign
* if: jump to end belongs here
 34:    JEQ  0,3(7) 	if: jmp to else
 37:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
 38:     LD  0,0(5) 	load id value
* <- Id
 39:     ST  0,0(6) 	op: push left
* -> Const
 40:    LDC  0,18(0) 	load const
* <- Const
 41:     LD  1,0(6) 	op: load left
 42:    SUB  0,1,0 	op ==
 43:    JEQ  0,2(7) 	br if true
 44:    LDC  0,0(0) 	false case
 45:    LDA  7,1(7) 	unconditional jmp
 46:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
 48:    LDC  0,4.5(0) 	load const
* <- Const
 49:     ST  0,2(5) 	assign: store value
* <- assign
* if: jump to end belongs here
 47:    JEQ  0,3(7) 	if: jmp to else
 50:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
 51:     LD  0,0(5) 	load id value
* <- Id
 52:     ST  0,0(6) 	op: push left
* -> Const
 53:    LDC  0,19(0) 	load const
* <- Const
 54:     LD  1,0(6) 	op: load left
 55:    SUB  0,1,0 	op ==
 56:    JEQ  0,2(7) 	br if true
 57:    LDC  0,0(0) 	false case
 58:    LDA  7,1(7) 	unconditional jmp
 59:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
 61:    LDC  0,3.5(0) 	load const
* <- Const
 62:     ST  0,2(5) 	assign: store value
* <- assign
* if: jump to end belongs here
 60:    JEQ  0,3(7) 	if: jmp to else
 63:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Op
* -> Id
 64:     LD  0,0(5) 	load id value
* <- Id
 65:     ST  0,0(6) 	op: push left
* -> Const
 66:    LDC  0,23(0) 	load const
* <- Const
 67:     LD  1,0(6) 	op: load left
 68:    SUB  0,1,0 	op ==
 69:    JEQ  0,2(7) 	br if true
 70:    LDC  0,0(0) 	false case
 71:    LDA  7,1(7) 	unconditional jmp
 72:    LDC  0,1(0) 	true case
* <- Op
 73:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
 74:     LD  0,0(5) 	load id value
* <- Id
 75:     ST  0,-1(6) 	op: push left
* -> Const
 76:    LDC  0,25(0) 	load const
* <- Const
 77:     LD  1,-1(6) 	op: load left
 78:    SUB  0,1,0 	op ==
 79:    JEQ  0,2(7) 	br if true
 80:    LDC  0,0(0) 	false case
 81:    LDA  7,1(7) 	unconditional jmp
 82:    LDC  0,1(0) 	true case
* <- Op
 83:     LD  1,0(6) 	op: load left
 84:    ADD  0,1,0 	op ||
 85:    JEQ  0,1(7) 	|| : false stays 0
 86:    LDC  0,1(0) 	|| : true is 1
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
 88:    LDC  0,6(0) 	load const
* <- Const
 89:    LDC  1,1.0(0) 	conv: load 1.0
 90:    MUL  0,0,1 	conv int->float
 91:     ST  0,2(5) 	assign: store value
* <- assign
* if: jump to end belongs here
 87:    JEQ  0,5(7) 	if: jmp to else
 92:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
 93:     LD  0,0(5) 	load id value
* <- Id
 94:     ST  0,0(6) 	op: push left
* -> Const
 95:    LDC  0,29(0) 	load const
* <- Const
 96:     LD  1,0(6) 	op: load left
 97:    SUB  0,1,0 	op ==
 98:    JEQ  0,2(7) 	br if true
 99:    LDC  0,0(0) 	false case
100:    LDA  7,1(7) 	unconditional jmp
101:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
103:    LDC  0,5(0) 	load const
* <- Const
104:    LDC  1,1.0(0) 	conv: load 1.0
105:    MUL  0,0,1 	conv int->float
106:     ST  0,2(5) 	assign: store value
* <- assign
* if: jump to end belongs here
102:    JEQ  0,5(7) 	if: jmp to else
107:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
108:     LD  0,2(5) 	load id value
* <- Id
109:     ST  0,0(6) 	op: push left
* -> Const
110:    LDC  0,0(0) 	load const
* <- Const
111:    LDC  1,1.0(0) 	conv: load 1.0
112:    MUL  0,0,1 	conv int->float
113:     LD  1,0(6) 	op: load left
114:    SUB  0,1,0 	op >
115:    JGT  0,2(7) 	br if true
116:    LDC  0,0(0) 	false case
117:    LDA  7,1(7) 	unconditional jmp
118:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Op
* -> Id
120:     LD  0,2(5) 	load id value
* <- Id
121:     ST  0,0(6) 	op: push left
* -> Id
122:     LD  0,1(5) 	load id value
* <- Id
123:    LDC  1,1.0(0) 	conv: load 1.0
124:    MUL  0,0,1 	conv int->float
125:     LD  1,0(6) 	op: load left
126:    MUL  0,1,0 	op *
* <- Op
127:     ST  0,3(5) 	assign: store value
* <- assign
* -> Id
128:     LD  0,3(5) 	load id value
* <- Id
129:    OUT  0,0,0 	write ac
* if: jump to end belongs here
119:    JEQ  0,11(7) 	if: jmp to else
* -> Neg
* -> Const
131:    LDC  0,1(0) 	load const
* <- Const
132:    LDC  1,0(0) 	neg: load 0
133:    SUB  0,1,0 	op - (unario)
* <- Neg
134:    OUT  0,0,0 	write ac
130:    LDA  7,4(7) 	jmp to end
* <- if
* End of execution.
135:   HALT  0,0,0 	

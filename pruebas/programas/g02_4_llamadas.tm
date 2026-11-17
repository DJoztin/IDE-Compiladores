* Compilacion a codigo TM (esquema TINY de Louden)
* File: g02_4_llamadas.tm
* Standard prelude:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* End of standard prelude.
* declaracion int tipo, minutos, locales (loc 0, 1, 2)
* declaracion float costo, total (loc 3, 4)
* -> assign
* -> Const
  2:    LDC  0,0(0) 	load const
* <- Const
  3:    LDC  1,1.0(0) 	conv: load 1.0
  4:    MUL  0,0,1 	conv int->float
  5:     ST  0,4(5) 	assign: store value
* <- assign
* -> assign
* -> Const
  6:    LDC  0,0(0) 	load const
* <- Const
  7:     ST  0,2(5) 	assign: store value
* <- assign
* -> do-until
* do-until: jump after body comes back here
  8:     IN  0,0,0 	read integer value: tipo | Tipo de llamada (1 internacional, 2 nacional, 3 local, 0 terminar)
  9:     ST  0,0(5) 	read: store value
* -> if
* -> Op
* -> Op
* -> Id
 10:     LD  0,0(5) 	load id value
* <- Id
 11:     ST  0,0(6) 	op: push left
* -> Const
 12:    LDC  0,0(0) 	load const
* <- Const
 13:     LD  1,0(6) 	op: load left
 14:    SUB  0,1,0 	op <
 15:    JLT  0,2(7) 	br if true
 16:    LDC  0,0(0) 	false case
 17:    LDA  7,1(7) 	unconditional jmp
 18:    LDC  0,1(0) 	true case
* <- Op
 19:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
 20:     LD  0,0(5) 	load id value
* <- Id
 21:     ST  0,-1(6) 	op: push left
* -> Const
 22:    LDC  0,3(0) 	load const
* <- Const
 23:     LD  1,-1(6) 	op: load left
 24:    SUB  0,1,0 	op >
 25:    JGT  0,2(7) 	br if true
 26:    LDC  0,0(0) 	false case
 27:    LDA  7,1(7) 	unconditional jmp
 28:    LDC  0,1(0) 	true case
* <- Op
 29:     LD  1,0(6) 	op: load left
 30:    ADD  0,1,0 	op ||
 31:    JEQ  0,1(7) 	|| : false stays 0
 32:    LDC  0,1(0) 	|| : true is 1
* <- Op
* if: jump to else belongs here
 34:    LDA  0,0(0) 	msg: Tipo invalido: usa 1, 2, 3 o 0
* if: jump to end belongs here
 33:    JEQ  0,2(7) 	if: jmp to else
 35:    LDA  7,0(7) 	jmp to end
* <- if
* -> Op
* -> Op
* -> Id
 36:     LD  0,0(5) 	load id value
* <- Id
 37:     ST  0,0(6) 	op: push left
* -> Const
 38:    LDC  0,0(0) 	load const
* <- Const
 39:     LD  1,0(6) 	op: load left
 40:    SUB  0,1,0 	op >=
 41:    JGE  0,2(7) 	br if true
 42:    LDC  0,0(0) 	false case
 43:    LDA  7,1(7) 	unconditional jmp
 44:    LDC  0,1(0) 	true case
* <- Op
 45:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
 46:     LD  0,0(5) 	load id value
* <- Id
 47:     ST  0,-1(6) 	op: push left
* -> Const
 48:    LDC  0,3(0) 	load const
* <- Const
 49:     LD  1,-1(6) 	op: load left
 50:    SUB  0,1,0 	op <=
 51:    JLE  0,2(7) 	br if true
 52:    LDC  0,0(0) 	false case
 53:    LDA  7,1(7) 	unconditional jmp
 54:    LDC  0,1(0) 	true case
* <- Op
 55:     LD  1,0(6) 	op: load left
 56:    MUL  0,1,0 	op &&
* <- Op
 57:    JEQ  0,-50(7) 	do-until: jmp back to body
* <- do-until
* -> while
* while: condition is evaluated here
* -> Op
* -> Id
 58:     LD  0,0(5) 	load id value
* <- Id
 59:     ST  0,0(6) 	op: push left
* -> Const
 60:    LDC  0,0(0) 	load const
* <- Const
 61:     LD  1,0(6) 	op: load left
 62:    SUB  0,1,0 	op !=
 63:    JNE  0,2(7) 	br if true
 64:    LDC  0,0(0) 	false case
 65:    LDA  7,1(7) 	unconditional jmp
 66:    LDC  0,1(0) 	true case
* <- Op
* while: jump to end belongs here
* -> do-until
* do-until: jump after body comes back here
 68:     IN  0,0,0 	read integer value: minutos | Duracion en minutos (>= 1)
 69:     ST  0,1(5) 	read: store value
* -> if
* -> Op
* -> Id
 70:     LD  0,1(5) 	load id value
* <- Id
 71:     ST  0,0(6) 	op: push left
* -> Const
 72:    LDC  0,1(0) 	load const
* <- Const
 73:     LD  1,0(6) 	op: load left
 74:    SUB  0,1,0 	op <
 75:    JLT  0,2(7) 	br if true
 76:    LDC  0,0(0) 	false case
 77:    LDA  7,1(7) 	unconditional jmp
 78:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
 80:    LDA  0,0(0) 	msg: La duracion debe ser de 1 minuto o mas
* if: jump to end belongs here
 79:    JEQ  0,2(7) 	if: jmp to else
 81:    LDA  7,0(7) 	jmp to end
* <- if
* -> Op
* -> Id
 82:     LD  0,1(5) 	load id value
* <- Id
 83:     ST  0,0(6) 	op: push left
* -> Const
 84:    LDC  0,1(0) 	load const
* <- Const
 85:     LD  1,0(6) 	op: load left
 86:    SUB  0,1,0 	op >=
 87:    JGE  0,2(7) 	br if true
 88:    LDC  0,0(0) 	false case
 89:    LDA  7,1(7) 	unconditional jmp
 90:    LDC  0,1(0) 	true case
* <- Op
 91:    JEQ  0,-24(7) 	do-until: jmp back to body
* <- do-until
* -> assign
* -> Const
 92:    LDC  0,0(0) 	load const
* <- Const
 93:    LDC  1,1.0(0) 	conv: load 1.0
 94:    MUL  0,0,1 	conv int->float
 95:     ST  0,3(5) 	assign: store value
* <- assign
* -> if
* -> Op
* -> Id
 96:     LD  0,0(5) 	load id value
* <- Id
 97:     ST  0,0(6) 	op: push left
* -> Const
 98:    LDC  0,1(0) 	load const
* <- Const
 99:     LD  1,0(6) 	op: load left
100:    SUB  0,1,0 	op ==
101:    JEQ  0,2(7) 	br if true
102:    LDC  0,0(0) 	false case
103:    LDA  7,1(7) 	unconditional jmp
104:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
106:    LDC  0,7.59(0) 	load const
* <- Const
107:     ST  0,3(5) 	assign: store value
* <- assign
* -> if
* -> Op
* -> Id
108:     LD  0,1(5) 	load id value
* <- Id
109:     ST  0,0(6) 	op: push left
* -> Const
110:    LDC  0,3(0) 	load const
* <- Const
111:     LD  1,0(6) 	op: load left
112:    SUB  0,1,0 	op >
113:    JGT  0,2(7) 	br if true
114:    LDC  0,0(0) 	false case
115:    LDA  7,1(7) 	unconditional jmp
116:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Op
* -> Id
118:     LD  0,3(5) 	load id value
* <- Id
119:     ST  0,0(6) 	op: push left
* -> Op
* -> Op
* -> Id
120:     LD  0,1(5) 	load id value
* <- Id
121:     ST  0,-1(6) 	op: push left
* -> Const
122:    LDC  0,3(0) 	load const
* <- Const
123:     LD  1,-1(6) 	op: load left
124:    SUB  0,1,0 	op -
* <- Op
125:    LDC  1,1.0(0) 	conv: load 1.0
126:    MUL  0,0,1 	conv int->float
127:     ST  0,-1(6) 	op: push left
* -> Const
128:    LDC  0,3.03(0) 	load const
* <- Const
129:     LD  1,-1(6) 	op: load left
130:    MUL  0,1,0 	op *
* <- Op
131:     LD  1,0(6) 	op: load left
132:    ADD  0,1,0 	op +
* <- Op
133:     ST  0,3(5) 	assign: store value
* <- assign
* if: jump to end belongs here
117:    JEQ  0,17(7) 	if: jmp to else
134:    LDA  7,0(7) 	jmp to end
* <- if
* if: jump to end belongs here
105:    JEQ  0,30(7) 	if: jmp to else
135:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
136:     LD  0,0(5) 	load id value
* <- Id
137:     ST  0,0(6) 	op: push left
* -> Const
138:    LDC  0,2(0) 	load const
* <- Const
139:     LD  1,0(6) 	op: load left
140:    SUB  0,1,0 	op ==
141:    JEQ  0,2(7) 	br if true
142:    LDC  0,0(0) 	false case
143:    LDA  7,1(7) 	unconditional jmp
144:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
146:    LDC  0,1.2(0) 	load const
* <- Const
147:     ST  0,3(5) 	assign: store value
* <- assign
* -> if
* -> Op
* -> Id
148:     LD  0,1(5) 	load id value
* <- Id
149:     ST  0,0(6) 	op: push left
* -> Const
150:    LDC  0,3(0) 	load const
* <- Const
151:     LD  1,0(6) 	op: load left
152:    SUB  0,1,0 	op >
153:    JGT  0,2(7) 	br if true
154:    LDC  0,0(0) 	false case
155:    LDA  7,1(7) 	unconditional jmp
156:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Op
* -> Id
158:     LD  0,3(5) 	load id value
* <- Id
159:     ST  0,0(6) 	op: push left
* -> Op
* -> Op
* -> Id
160:     LD  0,1(5) 	load id value
* <- Id
161:     ST  0,-1(6) 	op: push left
* -> Const
162:    LDC  0,3(0) 	load const
* <- Const
163:     LD  1,-1(6) 	op: load left
164:    SUB  0,1,0 	op -
* <- Op
165:    LDC  1,1.0(0) 	conv: load 1.0
166:    MUL  0,0,1 	conv int->float
167:     ST  0,-1(6) 	op: push left
* -> Const
168:    LDC  0,0.48(0) 	load const
* <- Const
169:     LD  1,-1(6) 	op: load left
170:    MUL  0,1,0 	op *
* <- Op
171:     LD  1,0(6) 	op: load left
172:    ADD  0,1,0 	op +
* <- Op
173:     ST  0,3(5) 	assign: store value
* <- assign
* if: jump to end belongs here
157:    JEQ  0,17(7) 	if: jmp to else
174:    LDA  7,0(7) 	jmp to end
* <- if
* if: jump to end belongs here
145:    JEQ  0,30(7) 	if: jmp to else
175:    LDA  7,0(7) 	jmp to end
* <- if
* -> if
* -> Op
* -> Id
176:     LD  0,0(5) 	load id value
* <- Id
177:     ST  0,0(6) 	op: push left
* -> Const
178:    LDC  0,3(0) 	load const
* <- Const
179:     LD  1,0(6) 	op: load left
180:    SUB  0,1,0 	op ==
181:    JEQ  0,2(7) 	br if true
182:    LDC  0,0(0) 	false case
183:    LDA  7,1(7) 	unconditional jmp
184:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign (locales++)
* -> Op
* -> Id
186:     LD  0,2(5) 	load id value
* <- Id
187:     ST  0,0(6) 	op: push left
* -> Const
188:    LDC  0,1(0) 	load const
* <- Const
189:     LD  1,0(6) 	op: load left
190:    ADD  0,1,0 	op +
* <- Op
191:     ST  0,2(5) 	assign: store value
* <- assign
* -> if
* -> Op
* -> Id
192:     LD  0,2(5) 	load id value
* <- Id
193:     ST  0,0(6) 	op: push left
* -> Const
194:    LDC  0,50(0) 	load const
* <- Const
195:     LD  1,0(6) 	op: load left
196:    SUB  0,1,0 	op >
197:    JGT  0,2(7) 	br if true
198:    LDC  0,0(0) 	false case
199:    LDA  7,1(7) 	unconditional jmp
200:    LDC  0,1(0) 	true case
* <- Op
* if: jump to else belongs here
* -> assign
* -> Const
202:    LDC  0,0.6(0) 	load const
* <- Const
203:     ST  0,3(5) 	assign: store value
* <- assign
* if: jump to end belongs here
201:    JEQ  0,3(7) 	if: jmp to else
204:    LDA  7,0(7) 	jmp to end
* <- if
* if: jump to end belongs here
185:    JEQ  0,20(7) 	if: jmp to else
205:    LDA  7,0(7) 	jmp to end
* <- if
* -> Id
206:     LD  0,3(5) 	load id value
* <- Id
207:    OUT  0,0,0 	write ac: costo | Costo de la llamada ($)
* -> assign
* -> Op
* -> Id
208:     LD  0,4(5) 	load id value
* <- Id
209:     ST  0,0(6) 	op: push left
* -> Id
210:     LD  0,3(5) 	load id value
* <- Id
211:     LD  1,0(6) 	op: load left
212:    ADD  0,1,0 	op +
* <- Op
213:     ST  0,4(5) 	assign: store value
* <- assign
* -> do-until
* do-until: jump after body comes back here
214:     IN  0,0,0 	read integer value: tipo | Tipo de llamada (1 internacional, 2 nacional, 3 local, 0 terminar)
215:     ST  0,0(5) 	read: store value
* -> if
* -> Op
* -> Op
* -> Id
216:     LD  0,0(5) 	load id value
* <- Id
217:     ST  0,0(6) 	op: push left
* -> Const
218:    LDC  0,0(0) 	load const
* <- Const
219:     LD  1,0(6) 	op: load left
220:    SUB  0,1,0 	op <
221:    JLT  0,2(7) 	br if true
222:    LDC  0,0(0) 	false case
223:    LDA  7,1(7) 	unconditional jmp
224:    LDC  0,1(0) 	true case
* <- Op
225:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
226:     LD  0,0(5) 	load id value
* <- Id
227:     ST  0,-1(6) 	op: push left
* -> Const
228:    LDC  0,3(0) 	load const
* <- Const
229:     LD  1,-1(6) 	op: load left
230:    SUB  0,1,0 	op >
231:    JGT  0,2(7) 	br if true
232:    LDC  0,0(0) 	false case
233:    LDA  7,1(7) 	unconditional jmp
234:    LDC  0,1(0) 	true case
* <- Op
235:     LD  1,0(6) 	op: load left
236:    ADD  0,1,0 	op ||
237:    JEQ  0,1(7) 	|| : false stays 0
238:    LDC  0,1(0) 	|| : true is 1
* <- Op
* if: jump to else belongs here
240:    LDA  0,0(0) 	msg: Tipo invalido: usa 1, 2, 3 o 0
* if: jump to end belongs here
239:    JEQ  0,2(7) 	if: jmp to else
241:    LDA  7,0(7) 	jmp to end
* <- if
* -> Op
* -> Op
* -> Id
242:     LD  0,0(5) 	load id value
* <- Id
243:     ST  0,0(6) 	op: push left
* -> Const
244:    LDC  0,0(0) 	load const
* <- Const
245:     LD  1,0(6) 	op: load left
246:    SUB  0,1,0 	op >=
247:    JGE  0,2(7) 	br if true
248:    LDC  0,0(0) 	false case
249:    LDA  7,1(7) 	unconditional jmp
250:    LDC  0,1(0) 	true case
* <- Op
251:     ST  0,0(6) 	op: push left
* -> Op
* -> Id
252:     LD  0,0(5) 	load id value
* <- Id
253:     ST  0,-1(6) 	op: push left
* -> Const
254:    LDC  0,3(0) 	load const
* <- Const
255:     LD  1,-1(6) 	op: load left
256:    SUB  0,1,0 	op <=
257:    JLE  0,2(7) 	br if true
258:    LDC  0,0(0) 	false case
259:    LDA  7,1(7) 	unconditional jmp
260:    LDC  0,1(0) 	true case
* <- Op
261:     LD  1,0(6) 	op: load left
262:    MUL  0,1,0 	op &&
* <- Op
263:    JEQ  0,-50(7) 	do-until: jmp back to body
* <- do-until
264:    LDA  7,-207(7) 	while: jmp back to condition
 67:    JEQ  0,197(7) 	while: jmp to end
* <- while
* -> Id
265:     LD  0,4(5) 	load id value
* <- Id
266:    OUT  0,0,0 	write ac: total | Total a pagar ($)
* End of execution.
267:   HALT  0,0,0 	

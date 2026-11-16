"""Pruebas de integracion TINY -> CI + TM -> simulador.
Requiere GCC y los binarios tiny y tm compilados; no es necesario para usar el proyecto.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parent

def cmd(args, stdin=''):
    p = subprocess.run(args, input=stdin, text=True, capture_output=True, cwd=root, timeout=10)
    return p.returncode, p.stdout + p.stderr


def verificar(programa, dato, esperado):
    tny = Path('ejemplos') / (programa + '.tny')
    rc, out = cmd([str(root/'tiny'), str(tny)])
    assert rc == 0, (programa, out)
    ci = root/'ejemplos'/(programa+'.ci')
    tm = root/'ejemplos'/(programa+'.tm')
    assert ci.exists() and tm.exists()
    assert ci.read_text().rstrip().endswith('halt')
    rc, out = cmd([str(root/'tm'), str(tm)], 'h\nv\ng\n'+dato+'\nq\n')
    assert rc == 0, (programa, out)
    assert ' v        Ver codigo intermedio' in out
    assert 'CODIGO INTERMEDIO:' in out
    assert esperado in out, (programa, out)
    print(f'{programa}: CORRECTO')

verificar('factorial', '5', 'Resultado del programa (OUT): 120')
verificar('aritmetica', '5', 'Resultado del programa (OUT): 18')
verificar('condicional', '2', 'Resultado del programa (OUT): 1')
verificar('ciclo', '3', 'Resultado del programa (OUT): 0')

# El programa de ejemplo con fallo semantico no debe generar codigo nuevo.
rc, out = cmd([str(root/'tiny'), 'ejemplos/error_semantico.tny'])
assert rc != 0 and 'Type error' in out
assert not (root/'ejemplos/error_semantico.ci').exists()
assert not (root/'ejemplos/error_semantico.tm').exists()
print('error semantico: salida correctamente bloqueada')

# Un .tm externo sin su .ci muestra ayuda explicativa, pero sigue siendo ejecutable.
with tempfile.TemporaryDirectory() as d:
    archivo = Path(d)/'sin_intermedio.tm'
    archivo.write_text('0: HALT 0,0,0\n')
    rc, out = cmd([str(root/'tm'), str(archivo)], 'v\ng\nq\n')
    assert rc == 0 and 'No se encontro el codigo intermedio' in out
    assert 'Ejecucion finalizada (HALT)' in out
print('archivo .ci ausente: aviso y TM ejecutable')

# Las ramas y loops anidados deben utilizar etiquetas distintas.
with tempfile.TemporaryDirectory() as d:
    ruta = Path(d)/'anidado.tny'
    ruta.write_text('read x;\nif 0 < x then\n  repeat\n    if x < 2 then\n      write x\n    else\n      write 99\n    end;\n    x := x - 1\n  until x = 0\nelse\n  write 0\nend\n')
    rc, out = cmd([str(root/'tiny'), str(ruta)])
    assert rc == 0, out
    ci = ruta.with_suffix('.ci').read_text()
    assert len(set(part for part in ci.split() if part.startswith('L') and part[1:].isdigit())) >= 4
    rc, out = cmd([str(root/'tm'), str(ruta.with_suffix('.tm'))], 'g\n3\nq\n')
    assert rc == 0 and out.count('Resultado del programa (OUT):') == 3, out
print('if/repeat anidados: correctos')

# El ejemplo factorial de Louden se mantiene con 42 instrucciones.
import re
codigo = (root/'ejemplos/factorial.tm').read_text()
inst = sorted(int(x) for x in re.findall(r'^\s*(\d+):', codigo, re.M))
assert inst == list(range(42)), inst
print('factorial: 42 instrucciones conservadas')
print('TODAS LAS PRUEBAS PASARON')

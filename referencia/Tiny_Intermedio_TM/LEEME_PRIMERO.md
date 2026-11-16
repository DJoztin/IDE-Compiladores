# TINY + TM: mostrar código intermedio desde el menú de ayuda

**Proyecto de Compiladores II · Universidad Autónoma de Aguascalientes**  
Versión educativa del compilador TINY y simulador TM de Kenneth C. Louden, extendida para visualizar **código intermedio de tres direcciones**.

## 1. ¿Qué se agregó?

Ahora, al compilar un programa TINY, se crean **dos archivos** en la carpeta del `.tny`:

| Archivo | ¿Qué contiene? | ¿Quién lo produce/usa? |
|---|---|---|
| `factorial.tny` | Programa fuente TINY | Lo escribe el alumno. |
| `factorial.ci` | Código **intermedio de tres direcciones**, con temporales y etiquetas | Lo genera `intermedio.c` mediante un recorrido del árbol. **Solo se muestra**, no se ejecuta en TM. |
| `factorial.tm` | Instrucciones de la máquina TM | Lo produce `cgen.c` + `code.c`; lo **ejecuta** el simulador `tm.c`. |

El simulador tiene un comando nuevo: **`v` = ver código intermedio**. Al escribir `h` aparece en su menú de ayuda, y al escribir `v` imprime el archivo `.ci` correspondiente al programa `.tm` abierto.

**Precisión técnica:** el compilador de Louden original **no genera código de tres direcciones como archivo independiente**. Esta nueva salida `.ci` es una *extensión didáctica*, generada en paralelo desde el árbol validado; **el generador de instrucciones TM original sigue recorriendo el árbol**, sin leer el archivo `.ci`. No se ha implementado una conversión física `.ci → .tm`.

## 2. Instalación en Windows con Visual Studio Code

1. Descomprime el ZIP completo, incluida la carpeta `Tiny_Intermedio_TM`.
2. En VS Code selecciona **Archivo → Abrir carpeta** y abre `Tiny_Intermedio_TM`.
3. Abre la terminal integrada (menú **Terminal → Nueva terminal**) y comprueba que GCC esté disponible:

   ```powershell
   gcc --version
   ```

4. Si ya tienes GCC de **MSYS2 UCRT64**, utiliza la terminal adecuada o asegúrate de tener la ruta `C:\msys64\ucrt64\bin` en PATH, según tu instalación.
5. Compila el proyecto desde la terminal **PowerShell** de VS Code:

   ```powershell
   .\compilar_windows.bat
   ```

   Se crearán `tiny.exe` y `tm.exe`. **Importante:** es necesario recompilar ambos programas para que aparezca la nueva función.

## 3. Ejemplo completo: factorial

**Paso 1. Genera los dos archivos.**

```powershell
.\tiny.exe .\ejemplos\factorial.tny
```

En el explorador de VS Code aparecerán:

- `ejemplos/factorial.ci` (código intermedio)
- `ejemplos/factorial.tm` (código destino)

**Paso 2. Abre la máquina TM.**

```powershell
.\tm.exe .\ejemplos\factorial.tm
```

**Paso 3. Escribe estos comandos**, uno por uno, presionando Enter:

```text
h        # Consulta las opciones, incluida la nueva v
v        # Muestra el contenido real de factorial.ci
i 0 5    # Muestra las primeras cinco instrucciones TM
g        # Ejecuta el programa
5        # Es el dato que solicita la instrucción IN
r        # Muestra los ocho registros
d 0 2    # Muestra la memoria de datos: x y fact
q        # Termina la simulación
```

El resultado para entrada 5 es **120**.

## 4. ¿Cómo se ve el código intermedio?

Ejemplo real generado por `intermedio.c` al compilar el factorial:

```text
read x
t1 = 0 < x
if_false t1 goto L1
fact = 1
label L2
t2 = fact * x
fact = t2
t3 = x - 1
x = t3
t4 = x == 0
if_false t4 goto L2
write fact
label L1
halt
```

La comparación `t1 = 0 < x` representa la misma condición que `x > 0`, aunque conserva el orden de operandos del árbol original. Los símbolos `t1`, `t2`, etc. son **temporales del código intermedio**, no nombres de registros físicos.

El archivo `factorial.tm` contiene instrucciones como `LD`, `ST`, `LDC`, `MUL`, `SUB`, `JEQ`, etc. Ahí se observan las decisiones específicas del generador para los registros, las memorias y los saltos.

## 5. ¿Qué se modificó en el código fuente?

| Archivo | Modificación |
|---|---|
| `intermedio.h` | **Nuevo:** declaración de `generarCodigoIntermedio`. |
| `intermedio.c` | **Nuevo:** recorre el árbol validado y escribe las operaciones en tres direcciones; admite asignaciones, expresiones, lectura, escritura, condiciones con o sin `else` y ciclos `repeat/until`. |
| `main.c` | Ahora produce `*.ci` y `*.tm` después de aprobar el análisis sintáctico y semántico. |
| `tm.c` | Nueva opción `v` en `doCommand()` que abre el `.ci` correspondiente; menú y mensajes principales en español. |
| `compilar_windows.bat` y `Makefile` | Incluyen `intermedio.c` al compilar TINY. |

`cgen.c` y `code.c` **no fueron alterados**: siguen produciendo el código TM del libro.

## 6. Otros programas para practicar

| Programa | Qué observar |
|---|---|
| `aritmetica.tny` | Temporales para `(x+1)*(x-2)` y operaciones aritméticas. |
| `condicional.tny` | Etiquetas y saltos de `if/else`. |
| `ciclo.tny` | Etiqueta inicial y salto de `repeat/until`. |
| `factorial.tny` | Traducción combinada de `read`, `if`, `repeat`, asignaciones, operaciones y `write`. |
| `error_semantico.tny` | No debe producir nuevas salidas si hay errores semánticos. |

Puedes cambiar el ejemplo en ambos comandos por cualquier `.tny` válido.

## 7. Si el comando `v` no encuentra el código intermedio

Asegúrate de haber ejecutado **primero `tiny.exe` con el mismo programa** y que el archivo `.ci` se encuentre **junto al `.tm`**:

```text
ejemplos/
  factorial.tny
  factorial.ci
  factorial.tm
```

No sirve iniciar directamente el simulador con un `.tm` externo si no existe también su `.ci`. En ese caso, el simulador muestra un mensaje claro con la ruta que intentó abrir. Las letras de los comandos se mantienen `h`, `v`, `i`, `d`, `g`, `r`, `s`, `t`, `p`, `c`, `q`, aunque las explicaciones estén en español.

## 8. Notas de compatibilidad

- La aplicación se compila con **GCC y C11**. No se necesitan los ejecutables antiguos de MS-DOS.
- En esta sesión, la ejecución y las pruebas se hicieron en **Linux con GCC**, no en Windows. Los comandos `.bat` están preparados para GCC/MSYS2 en Windows.
- La máquina TM ejecuta números enteros y tiene límites de memoria e instrucciones. Para el factorial, utiliza números pequeños, preferentemente entre 1 y 12.
- Para una explicación real del paso **código intermedio → código TM** como fase informática independiente, sería necesario implementar otro generador que **leyera directamente** las instrucciones de tres direcciones. Este proyecto mantiene el esquema de Louden y añade una visualización intermedia para docencia.

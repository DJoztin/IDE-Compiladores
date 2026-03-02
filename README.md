# IDE Compiladores — UAA
### Proyecto de Compiladores 1 · Fase 1
**Dra. Blanca G. Estrada Rentería**

---

## Archivos entregados

| Archivo | Descripción |
|---|---|
| `ide_compilador.py` | **IDE** — interfaz gráfica completa (tkinter) |
| `compilador.py` | **Compilador externo** (stub demo, reemplazar con implementación real) |

---

## Requisitos

- Python 3.8 o superior  
- `tkinter` (incluido en Python estándar)  
- No se requieren paquetes externos

---

## Cómo ejecutar

### Lanzar el IDE
```bash
python ide_compilador.py
```

### Ejecutar el compilador desde consola (sin IDE)
```bash
python compilador.py --lexico      archivo.txt
python compilador.py --sintactico  archivo.txt
python compilador.py --semantico   archivo.txt
python compilador.py --intermedio  archivo.txt
python compilador.py --ejecutar    archivo.txt
```

---

## Arquitectura (cumple requerimientos del proyecto)

```
ide_compilador.py          compilador.py
┌──────────────────┐        ┌──────────────────────┐
│      IDE         │ ──────▶│   Compilador externo │
│  (interfaz GUI)  │ system │   (módulo autónomo)   │
│                  │  call  │                      │
└──────────────────┘        └──────────────────────┘
  comunicación via archivos + parámetros de línea de comandos
```

- El IDE y el compilador son **módulos separados**  
- El compilador se puede ejecutar **desde consola sin el IDE**  
- La comunicación es mediante **archivos y parámetros de ejecución**

---

## Funcionalidades del IDE

### Menú Archivo
- Nuevo, Abrir, Cerrar, Guardar, Guardar como, Salir

### Menú Compilar
- Análisis Léxico (F5)
- Análisis Sintáctico (F6)
- Análisis Semántico (F7)
- Generación de Código Intermedio (F8)
- Ejecutar (F9)

### Barra de herramientas
- Botones rápidos para todas las fases

### Paneles de resultados
1. Editor con **numeración de líneas** y posición del cursor
2. **Tokens** del análisis léxico
3. **Árbol sintáctico** / salida estructurada
4. **Validaciones semánticas**
5. **Código intermedio** (tres direcciones)
6. **Tabla de símbolos**
7. **Lista de errores** (léxicos, sintácticos, semánticos) con número de línea
8. **Resultado de ejecución**

---

## Cómo conectar tu compilador real

En `compilador.py`, reemplaza el contenido de las funciones:

```python
def analisis_lexico(codigo):    # ← tu analizador léxico real
def analisis_sintactico(codigo):# ← tu parser real (LL1, LR, etc.)
def analisis_semantico(codigo): # ← tu analizador semántico real
def codigo_intermedio(codigo):  # ← tu generador de código intermedio
def ejecutar(codigo):           # ← tu intérprete o ejecutable
```

Cada función debe retornar una **tupla `(salida: str, errores: str)`**.

---

## Atajos de teclado

| Atajo | Acción |
|---|---|
| Ctrl+N | Nuevo archivo |
| Ctrl+O | Abrir archivo |
| Ctrl+S | Guardar |
| Ctrl+Shift+S | Guardar como |
| F5 | Análisis Léxico |
| F6 | Análisis Sintáctico |
| F7 | Análisis Semántico |
| F8 | Código Intermedio |
| F9 | Ejecutar |

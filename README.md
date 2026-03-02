# IDE Compiladores — UAA
### Proyecto de Compiladores 1 · Fase 1
---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `ide_compilador.py` | **IDE** — interfaz gráfica (PyQt6) |
| `compilador.py` | **Compilador externo** — módulo autónomo (stub, reemplazar con implementación real) |
| `README.md` | Este archivo |

---

## Requisitos

- Python **3.10** o superior
- **PyQt6**

```bash
pip install PyQt6
```

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

## Arquitectura

```
ide_compilador.py              compilador.py
┌────────────────────┐          ┌───────────────────────┐
│       IDE          │ ────────▶│   Compilador externo  │
│   (interfaz GUI)   │ subprocess│   (módulo autónomo)  │
│                    │◀──────── │                       │
└────────────────────┘ stdout/  └───────────────────────┘
                       stderr
    comunicación via parámetros de ejecución y archivos
```

- El IDE y el compilador son **módulos completamente separados**
- El compilador puede ejecutarse **desde consola sin el IDE**
- La comunicación es mediante **parámetros de ejecución** (`--lexico`, `--sintactico`, etc.)
- El IDE captura `stdout` (resultados) y `stderr` (errores) del compilador

---

## Funcionalidades

### Menú Archivo
| Opción | Atajo |
|---|---|
| Nuevo | Ctrl+N |
| Abrir... | Ctrl+O |
| Abrir carpeta... | Ctrl+K Ctrl+O |
| Cerrar pestaña | Ctrl+W |
| Guardar | Ctrl+S |
| Guardar como... | Ctrl+Shift+S |
| Salir | Alt+F4 |

### Menú Compilar
| Fase | Atajo |
|---|---|
| Análisis Léxico | F5 |
| Análisis Sintáctico | F6 |
| Análisis Semántico | F7 |
| Código Intermedio | F8 |
| Ejecutar | F9 |

### Editor
- Numeración de líneas permanente
- Línea activa resaltada
- Posición del cursor en barra de estado (`Ln X, Col Y`)
- Múltiples archivos abiertos simultáneamente en **pestañas**
- Pestañas movibles (arrastrar para reordenar)
- Indicador `●` en pestaña cuando hay cambios sin guardar
- Drag & drop de archivos directamente al editor

### Paneles de resultados *(dock arrastrable — derecha)*
| Pestaña | Contenido |
|---|---|
| Lexico | Lista de tokens generados |
| Sintactico | Árbol sintáctico / salida estructurada |
| Semantico | Validaciones y verificación de tipos |
| Cod. Intermedio | Código de tres direcciones |
| Tabla de Simbolos | Nombre, Tipo, Valor, Línea, Alcance |

### Panel de errores / salida *(dock arrastrable — abajo)*
| Pestaña | Contenido |
|---|---|
| Errores Lexicos | Errores con número de línea y columna |
| Errores Sintacticos | Errores con número de línea y descripción |
| Errores Semanticos | Errores con número de línea y descripción |
| Resultado Ejecucion | Salida del programa compilado |

> Cuando una fase produce errores, el IDE cambia automáticamente al tab de errores correspondiente.
> Cuando no hay errores, muestra `(sin errores)` en verde.

### Explorador de archivos *(dock arrastrable — izquierda)*
- Árbol de carpetas y archivos
- Doble clic para abrir archivo
- Clic derecho para menú contextual
- Al abrir un archivo, carga automáticamente su carpeta en el explorador
- El archivo abierto queda resaltado y visible en el árbol
- Botón 📂 para abrir carpeta manualmente
- Drag & drop de carpetas para cargarlas

### Docks arrastrables
Los tres paneles (Explorador, Resultados, Errores) son `QDockWidget` que se pueden:
- Arrastrar a cualquier zona de la ventana (izquierda, derecha, arriba, abajo)
- Reorganizar libremente
- Mostrar / ocultar desde el menú **Ver**

### Temas de la interfaz
Selector en la barra de herramientas con 6 temas:

| Tema | Descripción |
|---|---|
| VS Dark | Visual Studio Code oscuro (por defecto) |
| Light | Visual Studio Code claro |
| Monokai | Clásico de Sublime Text |
| Dracula | Púrpura oscuro |
| Solarized | Azul verdoso oscuro |
| Nord | Azul ártico |

El cambio de tema es instantáneo y actualiza todos los paneles.

---

## Cómo conectar el compilador real

El archivo `compilador.py` contiene funciones stub para cada fase. Reemplaza su contenido con tu implementación real. Cada fase debe escribir resultados a `stdout` y errores a `stderr`:

```python
# Ejemplo de estructura esperada por el IDE
import sys

def analisis_lexico(ruta):
    # ... tu analizador léxico ...
    print("TOKEN  ID        'main'   Ln 1")   # stdout → panel Lexico
    # Si hay errores:
    print("[Error Lexico] Linea 3, Col 7: caracter no reconocido '@'",
          file=sys.stderr)                     # stderr → panel Errores Lexicos
```

### Formato de errores recomendado
```
[Error Lexico]     Linea X, Col Y: descripción
[Error Sintactico] Linea X: descripción
[Error Semantico]  Linea X: descripción
```

---

## Atajos de teclado — resumen

| Atajo | Acción |
|---|---|
| Ctrl+N | Nuevo archivo (nueva pestaña) |
| Ctrl+O | Abrir archivo(s) |
| Ctrl+K Ctrl+O | Abrir carpeta en explorador |
| Ctrl+W | Cerrar pestaña actual |
| Ctrl+S | Guardar |
| Ctrl+Shift+S | Guardar como |
| Ctrl+Z | Deshacer |
| Ctrl+Y | Rehacer |
| F5 | Análisis Léxico |
| F6 | Análisis Sintáctico |
| F7 | Análisis Semántico |
| F8 | Código Intermedio |
| F9 | Ejecutar |
| Alt+F4 | Salir |

/***************************************************************/
/* Archivo: intermedio.h                                       */
/* Extension didactica: generacion de codigo de tres direcciones*/
/* a partir del AST TINY, sin cambiar el generador TM de Louden*/
/***************************************************************/
#ifndef INTERMEDIO_H
#define INTERMEDIO_H
#include "globals.h"

/* Emite una representacion textual en tres direcciones.       */
/* Retorna 1 en caso de exito y 0 ante un error de E/S/memoria. */
int generarCodigoIntermedio(TreeNode *raiz, FILE *destino);

#endif

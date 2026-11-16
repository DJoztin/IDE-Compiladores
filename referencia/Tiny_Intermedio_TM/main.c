/****************************************************/
/* File: main.c                                     */
/* Main program for TINY compiler                   */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                                */
/****************************************************/

#include "globals.h"

/* set NO_PARSE to TRUE to get a scanner-only compiler */
#define NO_PARSE FALSE
/* IMPORTANTE: FALSE habilita el analisis semantico y la tabla de simbolos. */
/* set NO_ANALYZE to TRUE to get a parser-only compiler */
#define NO_ANALYZE FALSE

/* IMPORTANTE: FALSE habilita la salida .tm para el simulador. */
/* set NO_CODE to TRUE to get a compiler that does not
 * generate code
 */
#define NO_CODE FALSE

#include "util.h"
#if NO_PARSE
#include "scan.h"
#else
#include "parse.h"
#if !NO_ANALYZE
#include "analyze.h"
#if !NO_CODE
#include "cgen.h"
#include "intermedio.h"
#endif
#endif
#endif

/* allocate global variables */
int lineno = 0;
FILE * source;
FILE * listing;
FILE * code;

/* allocate and set tracing flags */
int EchoSource = FALSE;
int TraceScan = FALSE;
int TraceParse = TRUE;
int TraceAnalyze = TRUE;
int TraceCode = TRUE;

int Error = FALSE;

int main( int argc, char * argv[] )
{ TreeNode * syntaxTree;
   char pgm[1024];
  const char *base;
  if (argc != 2)
  {
    fprintf(stderr,"Uso: %s <archivo.tny>\n", argv[0]);
    return 1;
  }
  if (snprintf(pgm, sizeof(pgm), "%s", argv[1]) >= (int)sizeof(pgm))
  {
    fprintf(stderr,"Ruta del archivo demasiado larga.\n");
    return 1;
  }
  base = strrchr(pgm, '/');
  { const char *winbase = strrchr(pgm, '\\');
    if (winbase && (!base || winbase > base)) base = winbase;
  }
  base = base ? base + 1 : pgm;
  if (strrchr(base, '.') == NULL)
  {
    if (strlen(pgm) + 4 >= sizeof(pgm)) return 1;
    strcat(pgm, ".tny");
  }
  source = fopen(pgm,"r");
  if (source==NULL)
  { fprintf(stderr,"File %s not found\n",pgm);
    exit(1);
  }
  listing = stdout; /* send listing to screen */
  fprintf(listing,"\nTINY COMPILATION: %s\n",pgm);
#if NO_PARSE
  while (getToken()!=ENDFILE);
#else
  syntaxTree = parse();
  if (TraceParse) {
    fprintf(listing,"\nSyntax tree:\n");
    printTree(syntaxTree);
  }
#if !NO_ANALYZE
  if (! Error)
  { if (TraceAnalyze) fprintf(listing,"\nBuilding Symbol Table...\n");
    buildSymtab(syntaxTree);
    if (TraceAnalyze) fprintf(listing,"\nChecking Types...\n");
    typeCheck(syntaxTree);
    if (TraceAnalyze) fprintf(listing,"\nType Checking Finished\n");
  }
#if !NO_CODE
  if (! Error)
  { char codefile[1024];
    char intermediofile[1024];
    char * extension;
    FILE *salidaIntermedia;
    if (snprintf(codefile, sizeof(codefile), "%s", pgm) >= (int)sizeof(codefile)) return 1;
    if (snprintf(intermediofile, sizeof(intermediofile), "%s", pgm) >= (int)sizeof(intermediofile)) return 1;
    extension = strrchr(codefile, '.');
    if (extension == NULL || (size_t)(extension - codefile) + 4 >= sizeof(codefile)) return 1;
    strcpy(extension, ".tm");
    extension = strrchr(intermediofile, '.');
    if (extension == NULL || (size_t)(extension - intermediofile) + 4 >= sizeof(intermediofile)) return 1;
    strcpy(extension, ".ci");

    /* Primera salida: codigo intermedio de tres direcciones (didactico). */
    salidaIntermedia = fopen(intermediofile, "w");
    if (!salidaIntermedia)
    { fprintf(stderr, "No se pudo abrir %s\n", intermediofile); return 1; }
    if (!generarCodigoIntermedio(syntaxTree, salidaIntermedia))
    { fclose(salidaIntermedia);
      remove(intermediofile);
      fprintf(stderr, "Error al escribir el codigo intermedio.\n");
      return 1;
    }
    if (fclose(salidaIntermedia) != 0)
    { remove(intermediofile);
      fprintf(stderr, "Error al cerrar el archivo intermedio.\n");
      return 1;
    }

    /* Segunda salida: codigo de maquina TM, conservando a Louden. */
    code = fopen(codefile,"w");
    if (code == NULL)
    { fprintf(stderr,"No se pudo abrir %s\n",codefile); return 1; }
    codeGen(syntaxTree,codefile);
    if (fclose(code) != 0)
    { fprintf(stderr, "Error al cerrar el codigo TM.\n"); return 1; }
    fprintf(listing,"\nCodigo intermedio generado: %s\n", intermediofile);
    fprintf(listing,"Codigo TM generado: %s\n", codefile);
  }
#endif
#endif
#endif
  fclose(source);
  if (Error)
  {
    fprintf(stderr, "Compilacion cancelada por errores de analisis.\n");
    return 1;
  }
  return 0;
}


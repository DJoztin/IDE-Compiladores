/***************************************************************/
/* Archivo: intermedio.c                                       */
/* Extension didactica del compilador TINY de Kenneth C. Louden*/
/* Genera codigo intermedio de tres direcciones desde el AST.  */
/* No modifica el algoritmo original de generacion para TM.    */
/***************************************************************/
#include "intermedio.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* El contexto pertenece a una compilacion, sin estado global. */
typedef struct {
    FILE *salida;
    unsigned int temporal;
    unsigned int etiqueta;
    int error;
} ContextoIR;

static char *duplicar(const char *texto)
{
    size_t longitud;
    char *nuevo;
    if (!texto) return NULL;
    longitud = strlen(texto) + 1;
    nuevo = (char *)malloc(longitud);
    if (nuevo) memcpy(nuevo, texto, longitud);
    return nuevo;
}

static char *nombreNumerado(ContextoIR *ctx, char prefijo, unsigned int numero)
{
    char buffer[40];
    snprintf(buffer, sizeof(buffer), "%c%u", prefijo, numero);
    {
        char *resultado = duplicar(buffer);
        if (!resultado) ctx->error = 1;
        return resultado;
    }
}

static const char *nombreOperador(TokenType op)
{
    switch (op) {
        case PLUS: return "+";
        case MINUS: return "-";
        case TIMES: return "*";
        case OVER: return "/";
        case LT: return "<";
        case EQ: return "==";
        default: return "?";
    }
}

/* Es una traduccion del arbol en orden postorden:               */
/* t1 = operando_izq OP operando_der.                            */
/* El nombre retornado es del llamador y debe liberarse.        */
static char *generarExpresion(ContextoIR *ctx, const TreeNode *nodo)
{
    char *izq, *der, *tmp;
    char numero[40];
    if (!nodo || ctx->error) {
        ctx->error = 1;
        return NULL;
    }
    if (nodo->nodekind != ExpK) {
        ctx->error = 1;
        return NULL;
    }
    switch (nodo->kind.exp) {
        case ConstK:
            snprintf(numero, sizeof(numero), "%d", nodo->attr.val);
            tmp = duplicar(numero);
            if (!tmp) ctx->error = 1;
            return tmp;
        case IdK:
            tmp = duplicar(nodo->attr.name);
            if (!tmp) ctx->error = 1;
            return tmp;
        case OpK:
            izq = generarExpresion(ctx, nodo->child[0]);
            der = generarExpresion(ctx, nodo->child[1]);
            if (!izq || !der) {
                free(izq);
                free(der);
                ctx->error = 1;
                return NULL;
            }
            tmp = nombreNumerado(ctx, 't', ++ctx->temporal);
            if (tmp && fprintf(ctx->salida, "%s = %s %s %s\n",
                        tmp, izq, nombreOperador(nodo->attr.op), der) < 0)
                ctx->error = 1;
            free(izq);
            free(der);
            if (ctx->error) { free(tmp); return NULL; }
            return tmp;
        default:
            ctx->error = 1;
            return NULL;
    }
}

static void generarSentencias(ContextoIR *ctx, const TreeNode *nodo)
{
    const TreeNode *actual;
    for (actual = nodo; actual && !ctx->error; actual = actual->sibling) {
        char *resultado = NULL;
        char *et1 = NULL;
        char *et2 = NULL;
        if (actual->nodekind != StmtK) {
            ctx->error = 1;
            break;
        }
        switch (actual->kind.stmt) {
            case ReadK:
                if (fprintf(ctx->salida, "read %s\n", actual->attr.name) < 0) ctx->error = 1;
                break;
            case WriteK:
                resultado = generarExpresion(ctx, actual->child[0]);
                if (resultado && fprintf(ctx->salida, "write %s\n", resultado) < 0) ctx->error = 1;
                free(resultado);
                break;
            case AssignK:
                resultado = generarExpresion(ctx, actual->child[0]);
                if (resultado && fprintf(ctx->salida, "%s = %s\n", actual->attr.name, resultado) < 0)
                    ctx->error = 1;
                free(resultado);
                break;
            case IfK:
                resultado = generarExpresion(ctx, actual->child[0]);
                et1 = nombreNumerado(ctx, 'L', ++ctx->etiqueta);
                if (resultado && et1 && fprintf(ctx->salida, "if_false %s goto %s\n", resultado, et1) < 0)
                    ctx->error = 1;
                free(resultado);
                if (ctx->error) { free(et1); break; }
                generarSentencias(ctx, actual->child[1]);
                if (actual->child[2]) {
                    /* Si existe else, se necesita saltar el brazo else. */
                    et2 = nombreNumerado(ctx, 'L', ++ctx->etiqueta);
                    if (et2 && fprintf(ctx->salida, "goto %s\n", et2) < 0) ctx->error = 1;
                }
                if (!ctx->error && fprintf(ctx->salida, "label %s\n", et1) < 0) ctx->error = 1;
                if (actual->child[2]) {
                    generarSentencias(ctx, actual->child[2]);
                    if (!ctx->error && et2 && fprintf(ctx->salida, "label %s\n", et2) < 0)
                        ctx->error = 1;
                }
                free(et1);
                free(et2);
                break;
            case RepeatK:
                et1 = nombreNumerado(ctx, 'L', ++ctx->etiqueta);
                if (et1 && fprintf(ctx->salida, "label %s\n", et1) < 0) ctx->error = 1;
                generarSentencias(ctx, actual->child[0]);
                resultado = generarExpresion(ctx, actual->child[1]);
                if (resultado && et1 && fprintf(ctx->salida, "if_false %s goto %s\n", resultado, et1) < 0)
                    ctx->error = 1;
                free(resultado);
                free(et1);
                break;
            default:
                ctx->error = 1;
                break;
        }
    }
}

int generarCodigoIntermedio(TreeNode *raiz, FILE *destino)
{
    ContextoIR ctx;
    if (!destino) return 0;
    ctx.salida = destino;
    ctx.temporal = 0;
    ctx.etiqueta = 0;
    ctx.error = 0;
    if (fprintf(destino, "# CODIGO INTERMEDIO DE TRES DIRECCIONES - TINY\n"
                         "# Extension didactica: NO es una salida original del compilador de Louden.\n"
                         "# Los temporales t1, t2... y etiquetas L1, L2... son simbolicos.\n\n") < 0)
        return 0;
    generarSentencias(&ctx, raiz);
    if (!ctx.error && fprintf(destino, "halt\n") < 0) ctx.error = 1;
    if (fflush(destino) != 0) ctx.error = 1;
    return !ctx.error;
}

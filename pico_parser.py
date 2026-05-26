#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# Analizador Sintáctico generado automáticamente por YAPar
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# ARCHIVO GENERADO — NO EDITAR MANUALMENTE
# Fuente: especificación .yalp procesada por yapar.py
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import sys
from pico_parser_lexer import gettoken, Token, LexicalError


# ---------------------------------------- TABLAS SLR ----------------------------------------

# Cada entrada: ('shift', next_state) | ('reduce', prod_index) | ('accept',)
_ACTION = {0: {'KW_EMIT': ('shift', 4), 'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10)}, 1: {'LPAREN': ('shift', 91)}, 2: {'$': ('accept',)}, 3: {'$': ('reduce', 6), 'KW_WHEN': ('reduce', 6), 'RBRACE': ('reduce', 6), 'KW_EMIT': ('reduce', 6), 'KW_REPEAT': ('reduce', 6), 'KW_MACRO': ('reduce', 6), 'KW_LET': ('reduce', 6)}, 4: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 5: {'$': ('reduce', 8), 'KW_WHEN': ('reduce', 8), 'RBRACE': ('reduce', 8), 'KW_EMIT': ('reduce', 8), 'KW_REPEAT': ('reduce', 8), 'KW_MACRO': ('reduce', 8), 'KW_LET': ('reduce', 8)}, 6: {'$': ('reduce', 5), 'KW_WHEN': ('reduce', 5), 'RBRACE': ('reduce', 5), 'KW_EMIT': ('reduce', 5), 'KW_REPEAT': ('reduce', 5), 'KW_MACRO': ('reduce', 5), 'KW_LET': ('reduce', 5)}, 7: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), '$': ('reduce', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 8: {'LBRACE': ('shift', 81)}, 9: {'$': ('reduce', 7), 'KW_WHEN': ('reduce', 7), 'RBRACE': ('reduce', 7), 'KW_EMIT': ('reduce', 7), 'KW_REPEAT': ('reduce', 7), 'KW_MACRO': ('reduce', 7), 'KW_LET': ('reduce', 7)}, 10: {'IDENT': ('shift', 66)}, 11: {'IDENT': ('shift', 14)}, 12: {'$': ('reduce', 4), 'KW_WHEN': ('reduce', 4), 'RBRACE': ('reduce', 4), 'KW_EMIT': ('reduce', 4), 'KW_REPEAT': ('reduce', 4), 'KW_MACRO': ('reduce', 4), 'KW_LET': ('reduce', 4)}, 13: {'$': ('reduce', 3), 'KW_WHEN': ('reduce', 3), 'RBRACE': ('reduce', 3), 'KW_EMIT': ('reduce', 3), 'KW_LET': ('reduce', 3), 'KW_MACRO': ('reduce', 3), 'KW_REPEAT': ('reduce', 3)}, 14: {'ASSIGN': ('shift', 15)}, 15: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 16: {'SEMICOLON': ('reduce', 35), 'NEQ': ('reduce', 35), 'LT': ('reduce', 35), 'GT': ('reduce', 35), 'COMMA': ('reduce', 35), 'LEQ': ('reduce', 35), 'DIV': ('reduce', 35), 'AND': ('reduce', 35), 'PLUS': ('reduce', 35), 'OR': ('reduce', 35), 'RPAREN': ('reduce', 35), 'TIMES': ('reduce', 35), 'EQ': ('reduce', 35), 'GEQ': ('reduce', 35), 'MINUS': ('reduce', 35)}, 17: {'SEMICOLON': ('reduce', 37), 'NEQ': ('reduce', 37), 'LT': ('reduce', 37), 'GT': ('reduce', 37), 'COMMA': ('reduce', 37), 'LEQ': ('reduce', 37), 'DIV': ('reduce', 37), 'AND': ('reduce', 37), 'PLUS': ('reduce', 37), 'OR': ('reduce', 37), 'RPAREN': ('reduce', 37), 'TIMES': ('reduce', 37), 'EQ': ('reduce', 37), 'GEQ': ('reduce', 37), 'MINUS': ('reduce', 37)}, 18: {'SEMICOLON': ('reduce', 41), 'NEQ': ('reduce', 41), 'LT': ('reduce', 41), 'GT': ('reduce', 41), 'COMMA': ('reduce', 41), 'LEQ': ('reduce', 41), 'DIV': ('reduce', 41), 'AND': ('reduce', 41), 'PLUS': ('reduce', 41), 'OR': ('reduce', 41), 'RPAREN': ('reduce', 41), 'TIMES': ('reduce', 41), 'EQ': ('reduce', 41), 'GEQ': ('reduce', 41), 'MINUS': ('reduce', 41)}, 19: {'IDENT': ('shift', 22), 'INT_LIT': ('shift', 30), 'LPAREN': ('shift', 21), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 20: {'EQ': ('shift', 37), 'NEQ': ('shift', 36), 'SEMICOLON': ('reduce', 21), 'COMMA': ('reduce', 21), 'OR': ('reduce', 21), 'RPAREN': ('reduce', 21), 'AND': ('reduce', 21)}, 21: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 22: {'LPAREN': ('shift', 56), 'SEMICOLON': ('reduce', 42), 'NEQ': ('reduce', 42), 'LT': ('reduce', 42), 'GT': ('reduce', 42), 'COMMA': ('reduce', 42), 'LEQ': ('reduce', 42), 'DIV': ('reduce', 42), 'AND': ('reduce', 42), 'PLUS': ('reduce', 42), 'OR': ('reduce', 42), 'RPAREN': ('reduce', 42), 'TIMES': ('reduce', 42), 'EQ': ('reduce', 42), 'GEQ': ('reduce', 42), 'MINUS': ('reduce', 42)}, 23: {'MINUS': ('shift', 45), 'SEMICOLON': ('reduce', 29), 'NEQ': ('reduce', 29), 'EQ': ('reduce', 29), 'LT': ('reduce', 29), 'GT': ('reduce', 29), 'COMMA': ('reduce', 29), 'OR': ('reduce', 29), 'LEQ': ('reduce', 29), 'RPAREN': ('reduce', 29), 'AND': ('reduce', 29), 'GEQ': ('reduce', 29), 'PLUS': ('shift', 44)}, 24: {'SEMICOLON': ('reduce', 40), 'NEQ': ('reduce', 40), 'LT': ('reduce', 40), 'GT': ('reduce', 40), 'COMMA': ('reduce', 40), 'LEQ': ('reduce', 40), 'DIV': ('reduce', 40), 'AND': ('reduce', 40), 'PLUS': ('reduce', 40), 'OR': ('reduce', 40), 'RPAREN': ('reduce', 40), 'TIMES': ('reduce', 40), 'EQ': ('reduce', 40), 'GEQ': ('reduce', 40), 'MINUS': ('reduce', 40)}, 25: {'AND': ('shift', 34), 'SEMICOLON': ('reduce', 19), 'RPAREN': ('reduce', 19), 'COMMA': ('reduce', 19), 'OR': ('reduce', 19)}, 26: {'GEQ': ('shift', 41), 'GT': ('shift', 39), 'SEMICOLON': ('reduce', 24), 'NEQ': ('reduce', 24), 'AND': ('reduce', 24), 'COMMA': ('reduce', 24), 'OR': ('reduce', 24), 'RPAREN': ('reduce', 24), 'EQ': ('reduce', 24), 'LEQ': ('shift', 40), 'LT': ('shift', 42)}, 27: {'TIMES': ('shift', 48), 'DIV': ('shift', 47), 'SEMICOLON': ('reduce', 32), 'NEQ': ('reduce', 32), 'LT': ('reduce', 32), 'GT': ('reduce', 32), 'COMMA': ('reduce', 32), 'LEQ': ('reduce', 32), 'AND': ('reduce', 32), 'PLUS': ('reduce', 32), 'OR': ('reduce', 32), 'RPAREN': ('reduce', 32), 'EQ': ('reduce', 32), 'GEQ': ('reduce', 32), 'MINUS': ('reduce', 32)}, 28: {'SEMICOLON': ('reduce', 39), 'NEQ': ('reduce', 39), 'LT': ('reduce', 39), 'GT': ('reduce', 39), 'COMMA': ('reduce', 39), 'LEQ': ('reduce', 39), 'DIV': ('reduce', 39), 'AND': ('reduce', 39), 'PLUS': ('reduce', 39), 'OR': ('reduce', 39), 'RPAREN': ('reduce', 39), 'TIMES': ('reduce', 39), 'EQ': ('reduce', 39), 'GEQ': ('reduce', 39), 'MINUS': ('reduce', 39)}, 29: {'OR': ('shift', 32), 'SEMICOLON': ('shift', 31)}, 30: {'SEMICOLON': ('reduce', 38), 'NEQ': ('reduce', 38), 'LT': ('reduce', 38), 'GT': ('reduce', 38), 'COMMA': ('reduce', 38), 'LEQ': ('reduce', 38), 'DIV': ('reduce', 38), 'AND': ('reduce', 38), 'PLUS': ('reduce', 38), 'OR': ('reduce', 38), 'RPAREN': ('reduce', 38), 'TIMES': ('reduce', 38), 'EQ': ('reduce', 38), 'GEQ': ('reduce', 38), 'MINUS': ('reduce', 38)}, 31: {'$': ('reduce', 9), 'KW_WHEN': ('reduce', 9), 'RBRACE': ('reduce', 9), 'KW_EMIT': ('reduce', 9), 'KW_REPEAT': ('reduce', 9), 'KW_MACRO': ('reduce', 9), 'KW_LET': ('reduce', 9)}, 32: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 33: {'AND': ('shift', 34), 'SEMICOLON': ('reduce', 18), 'RPAREN': ('reduce', 18), 'COMMA': ('reduce', 18), 'OR': ('reduce', 18)}, 34: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 35: {'EQ': ('shift', 37), 'NEQ': ('shift', 36), 'SEMICOLON': ('reduce', 20), 'COMMA': ('reduce', 20), 'OR': ('reduce', 20), 'RPAREN': ('reduce', 20), 'AND': ('reduce', 20)}, 36: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 37: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 38: {'GEQ': ('shift', 41), 'GT': ('shift', 39), 'SEMICOLON': ('reduce', 22), 'NEQ': ('reduce', 22), 'AND': ('reduce', 22), 'COMMA': ('reduce', 22), 'OR': ('reduce', 22), 'RPAREN': ('reduce', 22), 'EQ': ('reduce', 22), 'LEQ': ('shift', 40), 'LT': ('shift', 42)}, 39: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 40: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 41: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 42: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 43: {'MINUS': ('shift', 45), 'SEMICOLON': ('reduce', 25), 'NEQ': ('reduce', 25), 'EQ': ('reduce', 25), 'LT': ('reduce', 25), 'GT': ('reduce', 25), 'COMMA': ('reduce', 25), 'OR': ('reduce', 25), 'LEQ': ('reduce', 25), 'RPAREN': ('reduce', 25), 'AND': ('reduce', 25), 'GEQ': ('reduce', 25), 'PLUS': ('shift', 44)}, 44: {'IDENT': ('shift', 22), 'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'LPAREN': ('shift', 21), 'BOOL_LIT': ('shift', 18), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 45: {'IDENT': ('shift', 22), 'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'LPAREN': ('shift', 21), 'BOOL_LIT': ('shift', 18), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 46: {'TIMES': ('shift', 48), 'DIV': ('shift', 47), 'SEMICOLON': ('reduce', 31), 'NEQ': ('reduce', 31), 'LT': ('reduce', 31), 'GT': ('reduce', 31), 'COMMA': ('reduce', 31), 'LEQ': ('reduce', 31), 'AND': ('reduce', 31), 'PLUS': ('reduce', 31), 'OR': ('reduce', 31), 'RPAREN': ('reduce', 31), 'EQ': ('reduce', 31), 'GEQ': ('reduce', 31), 'MINUS': ('reduce', 31)}, 47: {'IDENT': ('shift', 22), 'INT_LIT': ('shift', 30), 'LPAREN': ('shift', 21), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 48: {'IDENT': ('shift', 22), 'INT_LIT': ('shift', 30), 'LPAREN': ('shift', 21), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 49: {'SEMICOLON': ('reduce', 33), 'NEQ': ('reduce', 33), 'LT': ('reduce', 33), 'GT': ('reduce', 33), 'COMMA': ('reduce', 33), 'LEQ': ('reduce', 33), 'DIV': ('reduce', 33), 'AND': ('reduce', 33), 'PLUS': ('reduce', 33), 'OR': ('reduce', 33), 'RPAREN': ('reduce', 33), 'TIMES': ('reduce', 33), 'EQ': ('reduce', 33), 'GEQ': ('reduce', 33), 'MINUS': ('reduce', 33)}, 50: {'SEMICOLON': ('reduce', 34), 'NEQ': ('reduce', 34), 'LT': ('reduce', 34), 'GT': ('reduce', 34), 'COMMA': ('reduce', 34), 'LEQ': ('reduce', 34), 'DIV': ('reduce', 34), 'AND': ('reduce', 34), 'PLUS': ('reduce', 34), 'OR': ('reduce', 34), 'RPAREN': ('reduce', 34), 'TIMES': ('reduce', 34), 'EQ': ('reduce', 34), 'GEQ': ('reduce', 34), 'MINUS': ('reduce', 34)}, 51: {'TIMES': ('shift', 48), 'SEMICOLON': ('reduce', 30), 'NEQ': ('reduce', 30), 'LT': ('reduce', 30), 'GT': ('reduce', 30), 'COMMA': ('reduce', 30), 'LEQ': ('reduce', 30), 'AND': ('reduce', 30), 'PLUS': ('reduce', 30), 'OR': ('reduce', 30), 'RPAREN': ('reduce', 30), 'EQ': ('reduce', 30), 'GEQ': ('reduce', 30), 'MINUS': ('reduce', 30), 'DIV': ('shift', 47)}, 52: {'MINUS': ('shift', 45), 'SEMICOLON': ('reduce', 28), 'NEQ': ('reduce', 28), 'EQ': ('reduce', 28), 'LT': ('reduce', 28), 'GT': ('reduce', 28), 'COMMA': ('reduce', 28), 'OR': ('reduce', 28), 'LEQ': ('reduce', 28), 'RPAREN': ('reduce', 28), 'AND': ('reduce', 28), 'GEQ': ('reduce', 28), 'PLUS': ('shift', 44)}, 53: {'SEMICOLON': ('reduce', 27), 'NEQ': ('reduce', 27), 'EQ': ('reduce', 27), 'LT': ('reduce', 27), 'GT': ('reduce', 27), 'COMMA': ('reduce', 27), 'OR': ('reduce', 27), 'LEQ': ('reduce', 27), 'RPAREN': ('reduce', 27), 'AND': ('reduce', 27), 'GEQ': ('reduce', 27), 'MINUS': ('shift', 45), 'PLUS': ('shift', 44)}, 54: {'MINUS': ('shift', 45), 'SEMICOLON': ('reduce', 26), 'NEQ': ('reduce', 26), 'EQ': ('reduce', 26), 'LT': ('reduce', 26), 'GT': ('reduce', 26), 'COMMA': ('reduce', 26), 'OR': ('reduce', 26), 'LEQ': ('reduce', 26), 'RPAREN': ('reduce', 26), 'AND': ('reduce', 26), 'GEQ': ('reduce', 26), 'PLUS': ('shift', 44)}, 55: {'GEQ': ('shift', 41), 'GT': ('shift', 39), 'LEQ': ('shift', 40), 'LT': ('shift', 42), 'SEMICOLON': ('reduce', 23), 'NEQ': ('reduce', 23), 'AND': ('reduce', 23), 'COMMA': ('reduce', 23), 'OR': ('reduce', 23), 'RPAREN': ('reduce', 23), 'EQ': ('reduce', 23)}, 56: {'BOOL_LIT': ('shift', 18), 'RPAREN': ('shift', 58), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'FLOAT_LIT': ('shift', 28)}, 57: {'RPAREN': ('reduce', 47), 'COMMA': ('reduce', 47), 'OR': ('shift', 32)}, 58: {'SEMICOLON': ('reduce', 44), 'NEQ': ('reduce', 44), 'LT': ('reduce', 44), 'GT': ('reduce', 44), 'COMMA': ('reduce', 44), 'LEQ': ('reduce', 44), 'DIV': ('reduce', 44), 'AND': ('reduce', 44), 'PLUS': ('reduce', 44), 'OR': ('reduce', 44), 'RPAREN': ('reduce', 44), 'TIMES': ('reduce', 44), 'EQ': ('reduce', 44), 'GEQ': ('reduce', 44), 'MINUS': ('reduce', 44)}, 59: {'RPAREN': ('shift', 60), 'COMMA': ('shift', 61)}, 60: {'SEMICOLON': ('reduce', 43), 'NEQ': ('reduce', 43), 'LT': ('reduce', 43), 'GT': ('reduce', 43), 'COMMA': ('reduce', 43), 'LEQ': ('reduce', 43), 'DIV': ('reduce', 43), 'AND': ('reduce', 43), 'PLUS': ('reduce', 43), 'OR': ('reduce', 43), 'RPAREN': ('reduce', 43), 'TIMES': ('reduce', 43), 'EQ': ('reduce', 43), 'GEQ': ('reduce', 43), 'MINUS': ('reduce', 43)}, 61: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 62: {'RPAREN': ('reduce', 46), 'COMMA': ('reduce', 46), 'OR': ('shift', 32)}, 63: {'OR': ('shift', 32), 'RPAREN': ('shift', 64)}, 64: {'SEMICOLON': ('reduce', 45), 'NEQ': ('reduce', 45), 'LT': ('reduce', 45), 'GT': ('reduce', 45), 'COMMA': ('reduce', 45), 'LEQ': ('reduce', 45), 'DIV': ('reduce', 45), 'AND': ('reduce', 45), 'PLUS': ('reduce', 45), 'OR': ('reduce', 45), 'RPAREN': ('reduce', 45), 'TIMES': ('reduce', 45), 'EQ': ('reduce', 45), 'GEQ': ('reduce', 45), 'MINUS': ('reduce', 45)}, 65: {'SEMICOLON': ('reduce', 36), 'NEQ': ('reduce', 36), 'LT': ('reduce', 36), 'GT': ('reduce', 36), 'COMMA': ('reduce', 36), 'LEQ': ('reduce', 36), 'DIV': ('reduce', 36), 'AND': ('reduce', 36), 'PLUS': ('reduce', 36), 'OR': ('reduce', 36), 'RPAREN': ('reduce', 36), 'TIMES': ('reduce', 36), 'EQ': ('reduce', 36), 'GEQ': ('reduce', 36), 'MINUS': ('reduce', 36)}, 66: {'LPAREN': ('shift', 67)}, 67: {'IDENT': ('shift', 70), 'RPAREN': ('shift', 68)}, 68: {'LBRACE': ('shift', 78)}, 69: {'RPAREN': ('shift', 71), 'COMMA': ('shift', 72)}, 70: {'RPAREN': ('reduce', 17), 'COMMA': ('reduce', 17)}, 71: {'LBRACE': ('shift', 74)}, 72: {'IDENT': ('shift', 73)}, 73: {'RPAREN': ('reduce', 16), 'COMMA': ('reduce', 16)}, 74: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 75: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'RBRACE': ('shift', 76), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 76: {'$': ('reduce', 14), 'KW_WHEN': ('reduce', 14), 'RBRACE': ('reduce', 14), 'KW_EMIT': ('reduce', 14), 'KW_REPEAT': ('reduce', 14), 'KW_MACRO': ('reduce', 14), 'KW_LET': ('reduce', 14)}, 77: {'$': ('reduce', 2), 'KW_WHEN': ('reduce', 2), 'RBRACE': ('reduce', 2), 'KW_EMIT': ('reduce', 2), 'KW_LET': ('reduce', 2), 'KW_MACRO': ('reduce', 2), 'KW_REPEAT': ('reduce', 2)}, 78: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 79: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'RBRACE': ('shift', 80), 'KW_EMIT': ('shift', 4)}, 80: {'$': ('reduce', 15), 'KW_WHEN': ('reduce', 15), 'RBRACE': ('reduce', 15), 'KW_EMIT': ('reduce', 15), 'KW_REPEAT': ('reduce', 15), 'KW_MACRO': ('reduce', 15), 'KW_LET': ('reduce', 15)}, 81: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 82: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'RBRACE': ('shift', 83), 'KW_EMIT': ('shift', 4)}, 83: {'KW_UNTIL': ('shift', 84)}, 84: {'LPAREN': ('shift', 85)}, 85: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 86: {'OR': ('shift', 32), 'RPAREN': ('shift', 87)}, 87: {'SEMICOLON': ('shift', 88)}, 88: {'$': ('reduce', 13), 'KW_WHEN': ('reduce', 13), 'RBRACE': ('reduce', 13), 'KW_EMIT': ('reduce', 13), 'KW_REPEAT': ('reduce', 13), 'KW_MACRO': ('reduce', 13), 'KW_LET': ('reduce', 13)}, 89: {'OR': ('shift', 32), 'SEMICOLON': ('shift', 90)}, 90: {'$': ('reduce', 10), 'KW_WHEN': ('reduce', 10), 'RBRACE': ('reduce', 10), 'KW_EMIT': ('reduce', 10), 'KW_REPEAT': ('reduce', 10), 'KW_MACRO': ('reduce', 10), 'KW_LET': ('reduce', 10)}, 91: {'INT_LIT': ('shift', 30), 'STRING_LIT': ('shift', 24), 'BOOL_LIT': ('shift', 18), 'IDENT': ('shift', 22), 'LPAREN': ('shift', 21), 'NOT': ('shift', 19), 'FLOAT_LIT': ('shift', 28)}, 92: {'RPAREN': ('shift', 93), 'OR': ('shift', 32)}, 93: {'LBRACE': ('shift', 94)}, 94: {'KW_EMIT': ('shift', 4), 'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10)}, 95: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'RBRACE': ('shift', 96), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 96: {'$': ('reduce', 11), 'KW_WHEN': ('reduce', 11), 'RBRACE': ('reduce', 11), 'KW_EMIT': ('reduce', 11), 'KW_REPEAT': ('reduce', 11), 'KW_MACRO': ('reduce', 11), 'KW_LET': ('reduce', 11), 'KW_OTHERWISE': ('shift', 97)}, 97: {'LBRACE': ('shift', 98)}, 98: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 99: {'KW_LET': ('shift', 11), 'KW_WHEN': ('shift', 1), 'RBRACE': ('shift', 100), 'KW_REPEAT': ('shift', 8), 'KW_MACRO': ('shift', 10), 'KW_EMIT': ('shift', 4)}, 100: {'$': ('reduce', 12), 'KW_WHEN': ('reduce', 12), 'RBRACE': ('reduce', 12), 'KW_EMIT': ('reduce', 12), 'KW_REPEAT': ('reduce', 12), 'KW_MACRO': ('reduce', 12), 'KW_LET': ('reduce', 12)}}

# GOTO[estado][no_terminal] → siguiente estado
_GOTO = {0: {'let_stmt': 12, 'repeat_stmt': 9, 'macro_def': 5, 'statement_list': 7, 'program': 2, 'statement': 13, 'emit_stmt': 6, 'when_stmt': 3}, 4: {'expr_cmp': 26, 'expr_primary': 17, 'expr': 89, 'expr_add': 23, 'expr_and': 25, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 7: {'let_stmt': 12, 'statement': 77, 'repeat_stmt': 9, 'macro_def': 5, 'emit_stmt': 6, 'when_stmt': 3}, 15: {'expr_cmp': 26, 'expr_primary': 17, 'expr': 29, 'expr_add': 23, 'expr_and': 25, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 19: {'expr_primary': 17, 'expr_unary': 65}, 21: {'expr_cmp': 26, 'expr': 63, 'expr_primary': 17, 'expr_add': 23, 'expr_and': 25, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 32: {'expr_cmp': 26, 'expr_primary': 17, 'expr_add': 23, 'expr_and': 33, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 34: {'expr_cmp': 26, 'expr_primary': 17, 'expr_add': 23, 'expr_mul': 27, 'expr_eq': 35, 'expr_unary': 16}, 36: {'expr_cmp': 55, 'expr_primary': 17, 'expr_add': 23, 'expr_mul': 27, 'expr_unary': 16}, 37: {'expr_cmp': 38, 'expr_primary': 17, 'expr_add': 23, 'expr_mul': 27, 'expr_unary': 16}, 39: {'expr_primary': 17, 'expr_add': 54, 'expr_mul': 27, 'expr_unary': 16}, 40: {'expr_primary': 17, 'expr_add': 53, 'expr_mul': 27, 'expr_unary': 16}, 41: {'expr_primary': 17, 'expr_add': 52, 'expr_mul': 27, 'expr_unary': 16}, 42: {'expr_primary': 17, 'expr_add': 43, 'expr_mul': 27, 'expr_unary': 16}, 44: {'expr_primary': 17, 'expr_mul': 51, 'expr_unary': 16}, 45: {'expr_primary': 17, 'expr_mul': 46, 'expr_unary': 16}, 47: {'expr_primary': 17, 'expr_unary': 50}, 48: {'expr_primary': 17, 'expr_unary': 49}, 56: {'expr_primary': 17, 'expr_cmp': 26, 'expr_and': 25, 'expr_add': 23, 'expr_mul': 27, 'expr_eq': 20, 'expr': 57, 'arg_list': 59, 'expr_unary': 16}, 61: {'expr_cmp': 26, 'expr_primary': 17, 'expr': 62, 'expr_add': 23, 'expr_and': 25, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 67: {'param_list': 69}, 74: {'let_stmt': 12, 'repeat_stmt': 9, 'statement_list': 75, 'macro_def': 5, 'statement': 13, 'emit_stmt': 6, 'when_stmt': 3}, 75: {'let_stmt': 12, 'statement': 77, 'repeat_stmt': 9, 'macro_def': 5, 'emit_stmt': 6, 'when_stmt': 3}, 78: {'statement_list': 79, 'let_stmt': 12, 'repeat_stmt': 9, 'macro_def': 5, 'statement': 13, 'emit_stmt': 6, 'when_stmt': 3}, 79: {'let_stmt': 12, 'statement': 77, 'repeat_stmt': 9, 'macro_def': 5, 'emit_stmt': 6, 'when_stmt': 3}, 81: {'let_stmt': 12, 'repeat_stmt': 9, 'statement_list': 82, 'macro_def': 5, 'statement': 13, 'emit_stmt': 6, 'when_stmt': 3}, 82: {'let_stmt': 12, 'statement': 77, 'repeat_stmt': 9, 'macro_def': 5, 'emit_stmt': 6, 'when_stmt': 3}, 85: {'expr_cmp': 26, 'expr_primary': 17, 'expr': 86, 'expr_add': 23, 'expr_and': 25, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 91: {'expr_cmp': 26, 'expr_primary': 17, 'expr': 92, 'expr_add': 23, 'expr_and': 25, 'expr_mul': 27, 'expr_eq': 20, 'expr_unary': 16}, 94: {'let_stmt': 12, 'repeat_stmt': 9, 'macro_def': 5, 'statement_list': 95, 'statement': 13, 'emit_stmt': 6, 'when_stmt': 3}, 95: {'let_stmt': 12, 'statement': 77, 'repeat_stmt': 9, 'macro_def': 5, 'emit_stmt': 6, 'when_stmt': 3}, 98: {'let_stmt': 12, 'repeat_stmt': 9, 'statement_list': 99, 'macro_def': 5, 'statement': 13, 'emit_stmt': 6, 'when_stmt': 3}, 99: {'let_stmt': 12, 'statement': 77, 'repeat_stmt': 9, 'macro_def': 5, 'emit_stmt': 6, 'when_stmt': 3}}

# Producciones: (lhs, len_rhs, descripcion_legible)
_PRODUCTIONS = [("S'", 1, 'program'), ('program', 1, 'statement_list'), ('statement_list', 2, 'statement_list statement'), ('statement_list', 1, 'statement'), ('statement', 1, 'let_stmt'), ('statement', 1, 'emit_stmt'), ('statement', 1, 'when_stmt'), ('statement', 1, 'repeat_stmt'), ('statement', 1, 'macro_def'), ('let_stmt', 5, 'KW_LET IDENT ASSIGN expr SEMICOLON'), ('emit_stmt', 3, 'KW_EMIT expr SEMICOLON'), ('when_stmt', 7, 'KW_WHEN LPAREN expr RPAREN LBRACE statement_list RBRACE'), ('when_stmt', 11, 'KW_WHEN LPAREN expr RPAREN LBRACE statement_list RBRACE KW_OTHERWISE LBRACE statement_list RBRACE'), ('repeat_stmt', 9, 'KW_REPEAT LBRACE statement_list RBRACE KW_UNTIL LPAREN expr RPAREN SEMICOLON'), ('macro_def', 8, 'KW_MACRO IDENT LPAREN param_list RPAREN LBRACE statement_list RBRACE'), ('macro_def', 7, 'KW_MACRO IDENT LPAREN RPAREN LBRACE statement_list RBRACE'), ('param_list', 3, 'param_list COMMA IDENT'), ('param_list', 1, 'IDENT'), ('expr', 3, 'expr OR expr_and'), ('expr', 1, 'expr_and'), ('expr_and', 3, 'expr_and AND expr_eq'), ('expr_and', 1, 'expr_eq'), ('expr_eq', 3, 'expr_eq EQ expr_cmp'), ('expr_eq', 3, 'expr_eq NEQ expr_cmp'), ('expr_eq', 1, 'expr_cmp'), ('expr_cmp', 3, 'expr_cmp LT expr_add'), ('expr_cmp', 3, 'expr_cmp GT expr_add'), ('expr_cmp', 3, 'expr_cmp LEQ expr_add'), ('expr_cmp', 3, 'expr_cmp GEQ expr_add'), ('expr_cmp', 1, 'expr_add'), ('expr_add', 3, 'expr_add PLUS expr_mul'), ('expr_add', 3, 'expr_add MINUS expr_mul'), ('expr_add', 1, 'expr_mul'), ('expr_mul', 3, 'expr_mul TIMES expr_unary'), ('expr_mul', 3, 'expr_mul DIV expr_unary'), ('expr_mul', 1, 'expr_unary'), ('expr_unary', 2, 'NOT expr_unary'), ('expr_unary', 1, 'expr_primary'), ('expr_primary', 1, 'INT_LIT'), ('expr_primary', 1, 'FLOAT_LIT'), ('expr_primary', 1, 'STRING_LIT'), ('expr_primary', 1, 'BOOL_LIT'), ('expr_primary', 1, 'IDENT'), ('expr_primary', 4, 'IDENT LPAREN arg_list RPAREN'), ('expr_primary', 3, 'IDENT LPAREN RPAREN'), ('expr_primary', 3, 'LPAREN expr RPAREN'), ('arg_list', 3, 'arg_list COMMA expr'), ('arg_list', 1, 'expr')]

_START_STATE = 0

_IGNORED_TOKENS = {'WS'}


# ---------------------------------------- EXCEPCIÓN DE PARSEO ----------------------------------------

class ParseError(Exception):
    """Error sintáctico con información de posición."""
    def __init__(self, message: str, token=None):
        self.token = token
        super().__init__(message)


# ---------------------------------------- MOTOR SLR ----------------------------------------

def parse(text: str) -> bool:
    """
    Analiza el texto usando el autómata SLR generado.
    Retorna True si la entrada es sintácticamente válida.
    Lanza ParseError en caso de error sintáctico.
    """
    # Obtener tokens del lexer y filtrar los ignorados
    try:
        raw_tokens = gettoken(text)
    except LexicalError as e:
        raise ParseError(str(e))

    tokens = [t for t in raw_tokens if t.kind not in _IGNORED_TOKENS]
    tokens.append(Token('$', '$', -1, -1))  # marcador de fin de entrada

    stack = [_START_STATE]
    tok_pos = 0

    while True:
        state = stack[-1]
        token = tokens[tok_pos]

        action = _ACTION.get(state, {}).get(token.kind)

        if action is None:
            expected = sorted(_ACTION.get(state, {}).keys())
            raise ParseError(
                f"Error sintáctico: token inesperado {token.kind!r} "
                f"(línea {token.line}, col {token.col}). "
                f"Se esperaba uno de: {expected}",
                token=token
            )

        kind = action[0]

        if kind == 'shift':
            stack.append(action[1])
            tok_pos += 1

        elif kind == 'reduce':
            prod_idx = action[1]
            lhs, rhs_len, _ = _PRODUCTIONS[prod_idx]
            for _ in range(rhs_len):
                stack.pop()
            top_state = stack[-1]
            next_state = _GOTO.get(top_state, {}).get(lhs)
            if next_state is None:
                raise ParseError(
                    f"Error interno: GOTO[{top_state}][{lhs!r}] no definido.",
                    token=token
                )
            stack.append(next_state)

        elif kind == 'accept':
            return True

        else:
            raise ParseError(f"Acción desconocida: {action}", token=token)


# ---------------------------------------- PROGRAMA PRINCIPAL ----------------------------------------

def main():
    if len(sys.argv) < 2:
        print("------------------------------------------------------------")
        print(f"  USO: python {sys.argv[0]} <archivo_fuente>")
        print("------------------------------------------------------------")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"  ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)

    try:
        result = parse(source)
        print("------------------------------------------------------------")
        print(f"  RESULTADO DE PARSEO — {filename}")
        print("------------------------------------------------------------")
        if result:
            print("  La entrada es ACEPTADA por la gramática.")
        print("------------------------------------------------------------")
    except (ParseError, LexicalError) as e:
        print("------------------------------------------------------------")
        print(f"  RESULTADO DE PARSEO — {filename}")
        print("------------------------------------------------------------")
        print(f"  La entrada es RECHAZADA.")
        print("  " + str(e))
        print("------------------------------------------------------------")
        sys.exit(1)


if __name__ == "__main__":
    main()

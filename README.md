# Proyecto-2-Teoria-de-la-computacion

## Requisitos

- Python 3.10 o superior.
- No requiere bibliotecas externas.

## Ejecutar

Desde esta carpeta:

```bash
python main.py ejemplos/gramatica_entrada.txt
```

Guardar el resultado en un archivo:

```bash
python main.py ejemplos/gramatica_entrada.txt -o ejemplos/gramatica_cnf.txt
```

## Formato de entrada

Una producción por línea, usando `->` o `→`; las alternativas se separan con `|`. Cada símbolo debe separarse por espacios. Se reconocen `e`, `ε`, `epsilon`, `lambda` y `λ` como epsilon. El primer símbolo del lado izquierdo es el símbolo inicial por defecto. Los no terminales son los símbolos que aparecen en el lado izquierdo; los demás símbolos son terminales.

Ejemplo:

```text
S -> A B | palabra
A -> a | e
B -> b
```

## Procedimiento de conversión

1. Crea un nuevo símbolo inicial para que el inicial original no aparezca en lados derechos y pueda conservar epsilon si pertenece al lenguaje.
2. Elimina producciones epsilon, generando las variantes que omiten símbolos anulables.
3. Elimina producciones unitarias mediante el cierre de alcanzabilidad entre no terminales.
4. Elimina símbolos no generadores y no alcanzables.
5. Sustituye terminales que aparezcan en producciones de longitud mayor que uno por nuevos no terminales.
6. Divide producciones largas en producciones binarias.
7. Valida que las reglas finales sean de la forma `A -> B C`, `A -> terminal` o `S0 -> ε` para el símbolo inicial nuevo.
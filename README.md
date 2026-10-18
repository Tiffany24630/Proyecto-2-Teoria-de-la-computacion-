# Proyecto-2-Teoria-de-la-computacion

## Requisitos

- Python 3.10 o superior.
- No requiere bibliotecas externas.

## Ejecución y pruebas de CYK

Ejecuta los comandos desde la carpeta raíz del proyecto. Las gramáticas de prueba están en `ejemplos/`.

```bash
python main.py ejemplos/ingles.txt -f "She eats a cake with a fork"
python main.py ejemplos/1.txt -f "( id + id ) * id"
```

Si omites `-f` (o `--frase`), el programa solicita la frase por teclado:

```bash
python main.py ejemplos/ingles.txt
```

Para convertir una gramática y guardar el resultado en CNF, usa `-o` (o `--salida`). También puedes combinarlo con la prueba de una frase:

```bash
python main.py ejemplos/1.txt -o salida-cnf.txt -f "id + id"
```

`-o` guarda la gramática convertida; la aceptación de la frase se calcula por separado con CYK. Si no se proporciona `-f`, la frase se lee con `input()`. Por ejemplo, al ingresarla en la solicitud interactiva, los caracteres como `*` no son interpretados por la terminal.

## Qué hace el programa

1. Lee la gramática indicada y la convierte a forma normal de Chomsky (CNF).
2. Muestra la gramática convertida y si cumple las reglas de CNF.
3. Si se especificó `-o`, guarda la gramática CNF en ese archivo.
4. Obtiene la frase desde `-f` o la solicita por teclado. La frase se separa en palabras por espacios; las palabras se comparan sin distinguir mayúsculas cuando no coinciden exactamente con un terminal.
5. Ejecuta CYK usando el nuevo símbolo inicial creado por la conversión y muestra si la frase pertenece al lenguaje. Si hay palabras que no están en la gramática, también las informa.

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
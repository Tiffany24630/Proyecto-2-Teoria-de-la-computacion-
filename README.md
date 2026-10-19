# Proyecto-2-Teoria-de-la-computacion

## Requisitos

- Python 3.10 o superior.
- El backend y las pruebas de Python no requieren bibliotecas externas.
- Para compilar la interfaz: Node.js 22.12 o superior y npm.
- Alternativa: Docker con Docker Compose, sin instalar Python o Node localmente.

## Ejecución del Frontend Interactivo (Web UI)

Para levantar la interfaz gráfica con visualizador interactivo del **Árbol Sintáctico (Parse Tree)** y la **Tabla de Programación Dinámica CYK**:

```bash
npm --prefix frontend ci
npm --prefix frontend run build
python app.py
```
Luego abre tu navegador en `http://localhost:5000`.
La gramática inglesa ya viene cargada: solo escribe la frase y pulsa **Validar con CYK**.
Después de modificar el frontend, vuelve a ejecutar su compilación y recarga el navegador.
Si PowerShell bloquea `npm.ps1`, usa `npm.cmd` en lugar de `npm` en los comandos.
Si no existe `frontend/dist/index.html`, el servidor indica que falta compilar la interfaz.

También puedes ejecutar todo con Docker:

```bash
docker compose up --build -d
```

Abre `http://localhost:5000`. Para detenerlo: `docker compose down`.

## Ejecución por Línea de Comandos (CLI)

Ejecuta los comandos desde la carpeta raíz del proyecto. Las gramáticas de prueba están en `ejemplos/`.

```bash
python main.py -f "She eats a cake with a fork"
python main.py -f "The cat drinks the beer"
python main.py ejemplos/ingles.txt -f "She eats a cake with a fork"
python main.py ejemplos/1.txt -f "( id + id ) * id"
```

El programa mostrará:
1. La verificación de la gramática de entrada y la gramática en CNF, indicando si se convirtió o ya estaba en CNF.
2. La decisión de aceptación: **SÍ** o **NO**.
3. El **tiempo medido de validación** (en milisegundos y segundos).
4. El **Parse Tree (árbol de derivación)** en representación jerárquica y en notación de corchetes.

El archivo es opcional: si lo omites, se usa la gramática inglesa del enunciado.
Si omites `-f` (o `--frase`), el programa solicita la frase por teclado:

```bash
python main.py
```

Para validar solo la gramática, sin ingresar frases ni ejecutar CYK:

```bash
python main.py ejemplos/1.txt --solo-gramatica
python main.py ejemplos/1-cnf.txt --solo-gramatica
```

La verificación se realiza sobre la **gramática de entrada**, antes de convertirla:
`ejemplos/1.txt` no está en CNF; `ejemplos/1-cnf.txt` sí está en CNF.
Si la entrada ya está en CNF, se utiliza sin convertir; en caso contrario, se convierte
a CNF. La consola y la interfaz indican qué acción se realizó. La gramática resultante
se muestra y puede guardarse usando `-o`.
En la interfaz web, usa **Solo analizar gramática**; no requiere completar la frase.

Para convertir una gramática y guardar el resultado en CNF, usa `-o` (o `--salida`):

```bash
python main.py ejemplos/1.txt -o salida-cnf.txt -f "id + id"
```


## Qué hace el programa

1. Lee la gramática indicada y comprueba si está en forma normal de Chomsky (CNF). Solo la convierte si no lo está.
2. Muestra el resultado de la verificación, la acción realizada y la gramática en CNF.
3. Si se especificó `-o`, guarda la gramática CNF en ese archivo.
4. Obtiene la frase desde `-f` o la solicita por teclado. La frase se separa en palabras por espacios; las palabras se comparan sin distinguir mayúsculas cuando no coinciden exactamente con un terminal.
5. Ejecuta CYK usando el símbolo inicial de la gramática en CNF y muestra si la frase pertenece al lenguaje. Si hay palabras que no están en la gramática, también las informa. Con `--solo-gramatica`, omite la lectura de frases y la ejecución de CYK.

## Formato de entrada

Una producción por línea, usando `->` o `→`; las alternativas se separan con `|`. Cada símbolo debe separarse por espacios. Se reconocen `e`, `ε`, `epsilon`, `lambda` y `λ` como epsilon. El primer símbolo del lado izquierdo es el símbolo inicial por defecto. Los no terminales son los símbolos que aparecen en el lado izquierdo; los demás símbolos son terminales.

`S -> ∅` representa un símbolo sin producciones; **∅ no es ε**.
Al guardar, el símbolo inicial se escribe primero para poder volver a leer el archivo
sin cambiar el lenguaje. Para validar la cadena vacía usa `-f ""` o deja vacía la frase
en la interfaz y pulsa **Validar con CYK**.

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

## Pruebas y reporte

```bash
python -m unittest discover -s tests -v
npm --prefix frontend run lint
npm --prefix frontend run build
```

Las pruebas verifican las etapas de simplificación, colisiones de nombres, conservación
del lenguaje con 1,500 comparaciones independientes, frases inglesas, reglas de los árboles,
cadena vacía, API y CLI.

Prueba de navegador sin bibliotecas adicionales, con Chrome/Edge y Node.js instalados:

```bash
node tests/browser.mjs
```

Opcionalmente define `BROWSER_PATH` si el navegador está en otra ubicación, `PYTHON` si el
ejecutable de Python tiene otro nombre o `BASE_URL` para probar un servidor ya iniciado.
`node tests/browser.mjs --capturas` actualiza las cuatro capturas del reporte.

Consulta [DOCUMENTACION.md](DOCUMENTACION.md) para el diseño, fundamentos, simplificación
paso a paso, discusión, referencias y relación con la rúbrica. El ejemplo de simplificación
completa está en [ejemplos/simplificacion.txt](ejemplos/simplificacion.txt).

# Documentación y Reporte Técnico del Proyecto 2: Simplificación de Gramáticas y Algoritmo CYK

**Curso:** Teoría de la Computación  
**Ponderación:** 15 puntos netos  
**Fecha:** Octubre, 2026  

---

## 1. Distribución de Roles y Responsabilidades del Equipo

Para la realización del proyecto se dividieron las responsabilidades en 3 áreas especializadas, garantizando que cada integrante cubriera los aspectos teóricos, de implementación y de validación exigidos en la rúbrica:

### Integrante 1: Simplificación de Gramáticas y Conversión a CNF (7 Puntos)
* **Responsabilidad Principal:** Desarrollar el algoritmo que transforma cualquier gramática independiente del contexto (CFG) a la Forma Normal de Chomsky (CNF).
* **Módulos asignados:** `simplificacion_gramatica.py`, `cnf.py`, `parser_gramatica.py`, `tipos_gramatica.py`, `utils_gramatica.py`.
* **Tareas realizadas:**
  1. **Investigación:** Reglas de transformación formal a CNF según la teoría de autómatas y lenguajes formales.
  2. **Eliminación de producciones $\varepsilon$:** Algoritmo de detección de símbolos anulables (`simbolos_anulables`) y generación combinatoria de variantes (`eliminar_epsilon`).
  3. **Eliminación de producciones unitarias:** Cálculo de alcanzabilidad entre no terminales y sustitución directa (`eliminar_unitarias`).
  4. **Eliminación de símbolos inútiles:** Detección de símbolos generadores y símbolos alcanzables desde el símbolo inicial (`eliminar_inutiles`).
  5. **Binarización y variables terminales:** Sustitución de terminales en producciones compuestas y segmentación de producciones de longitud $> 2$ en pares binarios (`convertir_a_cnf`).
  6. **Pruebas de validación:** Verificación con `ejemplos/1.txt` contrastado contra `ejemplos/1-cnf.txt`.

### Integrante 2: Implementación del Algoritmo CYK (7 Puntos)
* **Responsabilidad Principal:** Implementar el algoritmo Cocke-Younger-Kasami (CYK) mediante programación dinámica para determinar la pertenencia de una frase al lenguaje generado por la gramática en CNF.
* **Módulos asignados:** `cyk.py` (motor de inferencia, indexación y programación dinámica).
* **Tareas realizadas:**
  1. **Investigación teórica:** Análisis de la lógica de programación dinámica y complejidad algorítmica $O(n^3 \cdot |G|)$.
  2. **Estructura de la tabla dinámica:** Diseño de la matriz triangular superior $T[i][j]$ para subcadenas desde la posición $i$ hasta $j$.
  3. **Pre-indexación de la gramática:** Creación de tablas hash para reglas unarias ($a \to \{A\}$) y binarias ($(B, C) \to \{A\}$) para accesos directos en $O(1)$.
  4. **Paso base (largo 1):** Inicialización de la diagonal principal con producciones terminales directas.
  5. **Paso recursivo (largos $2 \dots n$):** Evaluación de todos los cortes posibles $k \in [i, j-1]$, realizando el producto cartesiano entre subcadenas y emparejamiento con reglas binarias.
  6. **Decisión de aceptación:** Comprobación del símbolo inicial $S_0$ en la celda superior $T[0][n-1]$.

### Integrante 3: Integración, Árbol Sintáctico, Frontend y Documentación (1 Punto + Integración)
* **Responsabilidad Principal:** Completar las funcionalidades de salida exigidas, unificar las ramas de desarrollo, construir el frontend y estructurar la documentación técnica.
* **Módulos asignados:** `cyk.py` (parse tree), `main.py` (CLI y cronometraje), `app.py` (Frontend interactivo Web con D3.js) y `DOCUMENTACION.md`.
* **Tareas realizadas:**
  1. **Almacenamiento de antecedentes (*back-pointers*):** Registro estructurado de la procedencia de cada derivación (`("term", w)` y `("bin", k, B, C)`).
  2. **Reconstrucción del Parse Tree:** Implementación del recorrido recursivo `construir_arbol` y generador de árbol jerárquico (`formatear_arbol_texto` y `arbol_a_parentesis`).
  3. **Medición de tiempos:** Inclusión de `time.perf_counter()` en milisegundos y segundos exactos.
  4. **Salida estricta SÍ / NO:** Validación conforme a especificación.
  5. **Desarrollo del Frontend:** Interfaz web moderna con Tailwind CSS y D3.js que grafica el árbol sintáctico y la tabla dinámica $T[i][j]$ sin requerir librerías externas de Python.
  6. **Documentación del proyecto:** Redacción técnica completa, diseño de software, análisis pedagógico paso a paso y recopilación de obstáculos.

---

## 2. Fundamento Teórico y Funcionamiento del Algoritmo CYK

### 2.1 ¿Qué problema resuelve el algoritmo CYK?
Dada una gramática libre de contexto en Forma Normal de Chomsky (CNF) y una frase $w$ compuesta por $n$ palabras ($w = w_0\, w_1 \dots w_{n-1}$), el algoritmo responde: **¿puede la gramática generar esta frase?**

Para resolverlo, utiliza **programación dinámica**:
1. Resuelve primero los subproblemas elementales (las palabras sueltas, longitud 1).
2. Guarda los resultados en una tabla estructurada.
3. Con dichas soluciones, construye problemas progresivamente mayores (subcadenas de 2 palabras, luego 3, ..., hasta las $n$ palabras de la frase completa).
4. **Principio fundamental:** Nunca se resuelve dos veces el mismo segmento de texto.

### 2.2 ¿Por qué se exige la Forma Normal de Chomsky (CNF)?
En CNF, cualquier derivación de una subcadena de 2 o más palabras proviene **estrictamente** de una regla de la forma:
$$A \to B\,C$$
Esto garantiza que cualquier segmento sintáctico de tamaño $L \ge 2$ se compone de la concatenación exacta de **dos pedazos no vacíos**. Gracias a esto, el algoritmo solo necesita evaluar particiones binarias (un único punto de corte $k$).

---

## 3. Ejemplo Teórico Paso a Paso

### 3.1 Gramática de Ejemplo y Frase
Sea la gramática formal:
$$\begin{aligned}
S &\to A\,B \mid B\,C \\
A &\to B\,A \mid a \\
B &\to C\,C \mid b \\
C &\to A\,B \mid a
\end{aligned}$$

Cadena de prueba:
$$w = b\ a\ a\ b\ a \quad (n = 5 \text{ palabras})$$

| Posición ($i$) | 0 | 1 | 2 | 3 | 4 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Palabra** | `b` | `a` | `a` | `b` | `a` |

---

### 3.2 La Tabla de Programación Dinámica (La Escalera Triangular)
Cada celda $[i, j]$ representa la subcadena que comienza en la palabra $i$ y termina en la palabra $j$.

```text
largo 5 │ [0,4]
largo 4 │ [0,3]  [1,4]
largo 3 │ [0,2]  [1,3]  [2,4]
largo 2 │ [0,1]  [1,2]  [2,3]  [3,4]
largo 1 │ [0,0]  [1,1]  [2,2]  [3,3]  [4,4]
           b      a      a      b      a
```

* **Fila:** Representa la longitud $L$ de la subcadena.
* **Columna:** Subcadenas que inician en la palabra $i$.
* **Almacenamiento en código:** Matriz `T[i][j]` de $n \times n$. Solo se emplea el triángulo superior ($j \ge i$), ya que una subcadena no puede terminar antes de empezar.

---

### 3.3 Concepto de Corte ($k$)
Para analizar una subcadena $[i, j]$ de longitud $L \ge 2$, se deben probar todas las formas posibles de partirla en dos fragmentos contiguos no vacíos:
* **Fragmento izquierdo:** $[i, k]$
* **Fragmento derecho:** $[k+1, j]$

El índice de corte $k$ recorre el intervalo $[i, j-1]$ (en código Python: `range(i, j)`).  
Una subcadena de longitud $L$ tiene exactamente $L - 1$ cortes posibles.

**Ejemplo de cortes para la celda $[1, 4]$ ($«a\ a\ b\ a»$):**
1. $k = 1$: Izquierda $[1, 1] = «a»$ | Derecha $[2, 4] = «a\ b\ a»$
2. $k = 2$: Izquierda $[1, 2] = «a\ a»$ | Derecha $[3, 4] = «b\ a»$
3. $k = 3$: Izquierda $[1, 3] = «a\ a\ b»$ | Derecha $[4, 4] = «a»$

En la estructura piramidal, para evaluar una celda $[i, j]$, el pedazo izquierdo **desciende verticalmente por la columna $i$**, mientras que el pedazo derecho **desciende en diagonal hacia la derecha**: dos trayectorias que convergen.

---

### 3.4 Pre-indexación de la Gramática
Para lograr una complejidad eficiente, se crean dos tablas hash inversas:
* **Índice Unario:** $\text{terminal} \to \{A \mid A \to \text{terminal}\}$
  * $a \to \{A, C\}$
  * $b \to \{B\}$
* **Índice Binario:** $(B, C) \to \{A \mid A \to B\,C\}$
  * $(A, B) \to \{S, C\}$
  * $(B, C) \to \{S\}$
  * $(B, A) \to \{A\}$
  * $(C, C) \to \{B\}$

Esto sustituye la iteración exhaustiva sobre todas las reglas en cada celda por una consulta $O(1)$.

---

### 3.5 Ejecución Paso a Paso sobre «baaba»

#### Paso 1: Largo 1 (Inicialización)
Se consulta directamente el índice unario para cada palabra:
* $[0, 0]$ (`b`) $\implies \{B\}$
* $[1, 1]$ (`a`) $\implies \{A, C\}$
* $[2, 2]$ (`a`) $\implies \{A, C\}$
* $[3, 3]$ (`b`) $\implies \{B\}$
* $[4, 4]$ (`a`) $\implies \{A, C\}$

#### Paso 2: Largo 2 (1 corte por celda)
* $[0, 1]$ (`ba`, $k=0$): $[0,0]\{B\} \times [1,1]\{A,C\} \implies BA \to A,\; BC \to S \implies \mathbf{\{A, S\}}$
* $[1, 2]$ (`aa`, $k=1$): $[1,1]\{A,C\} \times [2,2]\{A,C\} \implies CC \to B \implies \mathbf{\{B\}}$
* $[2, 3]$ (`ab`, $k=2$): $[2,2]\{A,C\} \times [3,3]\{B\} \implies AB \to S, C \implies \mathbf{\{S, C\}}$
* $[3, 4]$ (`ba`, $k=3$): $[3,3]\{B\} \times [4,4]\{A,C\} \implies BA \to A,\; BC \to S \implies \mathbf{\{A, S\}}$

#### Paso 3: Largo 3 (2 cortes por celda)
* $[0, 2]$ (`baa`):
  * $k=0$: $[0,0]\{B\} \times [1,2]\{B\} \implies BB$ (no existe)
  * $k=1$: $[0,1]\{A,S\} \times [2,2]\{A,C\} \implies AA, AC, SA, SC$ (no existen) $\implies \mathbf{\emptyset}$
* $[1, 3]$ (`aab`):
  * $k=1$: $[1,1]\{A,C\} \times [2,3]\{S,C\} \implies CC \to B$
  * $k=2$: $[1,2]\{B\} \times [3,3]\{B\} \implies BB$ (no existe) $\implies \mathbf{\{B\}}$
* $[2, 4]$ (`aba`):
  * $k=2$: $[2,2]\{A,C\} \times [3,4]\{A,S\} \implies$ (no existen)
  * $k=3$: $[2,3]\{S,C\} \times [4,4]\{A,C\} \implies CC \to B \implies \mathbf{\{B\}}$

#### Paso 4: Largo 4 (3 cortes por celda)
* $[0, 3]$ (`baab`):
  * Ninguna combinación válida produce reglas $\implies \mathbf{\emptyset}$
* $[1, 4]$ (`aaba`):
  * $k=1$: $[1,1]\{A,C\} \times [2,4]\{B\} \implies AB \to S, C$
  * $k=2$: $[1,2]\{B\} \times [3,4]\{A,S\} \implies BA \to A$
  * $k=3$: $[1,3]\{B\} \times [4,4]\{A,C\} \implies BA \to A,\; BC \to S$
  * **Resultado:** $\mathbf{\{S, C, A\}}$

#### Paso 5: Largo 5 (Frase Completa $[0, 4]$, 4 cortes)
* $k=0$: $[0,0]\{B\} \times [1,4]\{S,C,A\} \implies BC \to S,\; BA \to A \implies \mathbf{\{S, A\}}$
* $k=1$: $[0,1]\{A,S\} \times [2,4]\{B\} \implies AB \to C \implies \mathbf{\{C\}}$
* $k=2, 3$: pedazos vacíos $\implies \emptyset$
* **Resultado Celda Final $[0, 4]$:** $\mathbf{\{S, A, C\}}$

**Veredicto:** Como el símbolo inicial $S \in T[0][4]$, la frase **SÍ** pertenece al lenguaje.

---

## 4. Caso de Estudio: Gramática en Inglés y «She eats a cake with a fork»

### 4.1 Gramática en CNF
Al procesar la gramática del proyecto con nuestro módulo de simplificación, se obtiene:
```text
S0  -> NP VP
VP  -> VP PP | V NP | cooks | drinks | eats | cuts
PP  -> P NP
NP  -> Det N | he | she
V   -> cooks | drinks | eats | cuts
P   -> in | with
N   -> cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
Det -> a | the
```
*El conversor asignó `S0` como el nuevo símbolo inicial para garantizar que cumpla formalmente las condiciones de Chomsky.*

### 4.2 Proceso Dinámico sobre «She eats a cake with a fork»
* **Largo 1:** `she` $\{NP\}$, `eats` $\{V, VP\}$, `a` $\{Det\}$, `cake` $\{N\}$, `with` $\{P\}$, `a` $\{Det\}$, `fork` $\{N\}$.
* **Largo 2:** `[0,1]` (`she eats`) produce $\{S_0\}$; `[2,3]` (`a cake`) produce $\{NP\}$; `[5,6]` (`a fork`) produce $\{NP\}$.
* **Largo 3:** `[1,3]` (`eats a cake`) produce $\{VP\}$ ($V + NP$); `[4,6]` (`with a fork`) produce $\{PP\}$ ($P + NP$).
* **Largo 4:** `[0,3]` (`she eats a cake`) produce $\{S_0\}$.
* **Largo 6:** `[1,6]` (`eats a cake with a fork`) combina $[1,3]\{VP\} \times [4,6]\{PP\}$ vía $VP \to VP\ PP$, produciendo $\{VP\}$.
* **Largo 7 (Celda Raíz $[0, 6]$):** Combina $[0,0]\{NP\} \times [1,6]\{VP\}$ vía regla $S_0 \to NP\ VP$, produciendo $\{S_0\}$.

**Resultado:** **SÍ**, la frase es sintácticamente correcta.

### 4.3 Reconstrucción del Parse Tree mediante Back-Pointers
Al registrar las decisiones en cada celda, la función recursiva desciende generando el siguiente árbol:
```text
S0
+-- NP
|   \-- she
\-- VP
    +-- VP
    |   +-- V
    |   |   \-- eats
    |   \-- NP
    |       +-- Det
    |       |   \-- a
    |       \-- N
    |           \-- cake
    \-- PP
        +-- P
        |   \-- with
        \-- NP
            +-- Det
            |   \-- a
            \-- N
                \-- fork
```
**Notación Jerárquica entre Corchetes:**  
`[S0 [NP she] [VP [VP [V eats] [NP [Det a] [N cake]]] [PP [P with] [NP [Det a] [N fork]]]]]`

---

## 5. Batería de Pruebas y Resultados de Validación

### 5.1 Frases Aceptadas (Pertenecen al Lenguaje)

| Frase | Resultado | Tiempo (ms) | Derivación Principal |
| :--- | :---: | :---: | :--- |
| `She eats a cake with a fork` | **SÍ** | ~0.05 ms | `S0 -> NP VP`, con `VP -> VP PP`. |
| `The cat drinks the beer` | **SÍ** | ~0.04 ms | `S0 -> NP VP`, con `VP -> V NP`. |
| `He cuts meat with a knife` | **SÍ** | ~0.06 ms | `NP -> he`, `VP -> VP PP`. |
| `The dog drinks` | **SÍ** | ~0.03 ms | `NP -> Det N`, `VP -> drinks` (intransitivo). |
| `A cat cooks meat in an oven` | **SÍ** | ~0.06 ms | Uso de preposición de lugar `in`. |

### 5.2 Frases Rechazadas (No Pertenecen al Lenguaje)

| Frase | Resultado | Tiempo (ms) | Causa de Rechazo |
| :--- | :---: | :---: | :--- |
| `The cat drinks beer` | **NO** | ~0.03 ms | La gramática exige `NP -> Det N`, por lo que el sustantivo `beer` requiere determinante. |
| `She eats fork` | **NO** | ~0.03 ms | Ausencia del determinante `a` o `the` en el objeto directo. |
| `Cat drinks the beer` | **NO** | ~0.03 ms | El sustantivo sujeto `cat` carece de determinante. |
| `With a fork she eats` | **NO** | ~0.04 ms | Orden sintáctico inválido (`PP NP VP` no deriva de `S0`). |
| `She runs fast` | **NO** | ~0.02 ms | Vocabulario desconocido (`runs`, `fast` no están en el léxico). |

---

## 6. Obstáculos Encontrados y Recomendaciones

### 6.1 Obstáculos
1. **Representación de Celdas con Ambigüedad:**  
   Si una misma subcadena puede ser producida por múltiples reglas distintas (ambigüedad sintáctica), un diccionario simple sobrescribiría el back-pointer.  
   *Solución:* Se preservó la primera derivación encontrada (`if A not in T[i][j]`) para asegurar un árbol determinista y prevenir ciclos.
2. **Compatibilidad en Consolas de Windows:**  
   El uso de caracteres Unicode de dibujo (`└──`, `├──`) causaba excepciones `UnicodeEncodeError` en consolas configuradas con `cp1252`.  
   *Solución:* Se implementó un formateador seguro con caracteres ASCII (`\--`, `+--`, `|`).
3. **Manejo del Símbolo Inicial nuevo ($S_0$):**  
   Al convertir a CNF, el conversor introduce $S_0$. Si el evaluador de CYK buscaba el símbolo inicial anterior ($S$), las oraciones eran rechazadas incorrectamente.  
   *Solución:* La función `convertir_a_cnf` retorna explícitamente el nuevo símbolo inicial válido (`nuevo_inicial`), vinculándolo directamente con CYK.

### 6.2 Recomendaciones
* **Visualización Dinámica:** Se implementó `app.py`, un frontend interactivo con **D3.js** y **Tailwind CSS** que permite explorar visualmente el árbol sintáctico (zoom y pan) y la matriz triangular $T[i][j]$ completa.
* **Preprocesamiento:** Se recomienda incorporar normalización léxica (lematización y filtrado de signos de puntuación) si se desea extender la gramática a textos reales en inglés más complejos.

---

## 7. Referencias Bibliográficas y Material Consultador

1. **Hopcroft, J. E., Motwani, R., & Ullman, J. D.** (2006). *Introduction to Automata Theory, Languages, and Computation*. Addison-Wesley.
2. **Jurafsky, D., & Martin, J. H.** (2023). *Speech and Language Processing (3rd ed.)*. Capítulo sobre *Context-Free Grammars and CYK Parsing*.
3. **Cocke-Younger-Kasami (CYK) Algorithm:** [GeeksforGeeks Compiler Design Reference](https://www.geeksforgeeks.org/compiler-design/cocke-younger-kasami-cyk-algorithm/)
4. **Mijangos de la Cruz, V.** *Lingüística Computacional: CYK Parsing*. [Enlace al recurso](https://victormijangosdelacruz.github.io/Linguistica-Computacional/html/04%20CYKParsing.html)
5. **Universidade da Coruña:** *Apuntes y ejercicios del algoritmo CYK*. [Documento Studocu](https://www.studocu.com/es/document/universidade-da-coruna/teoria-da-computacion/algoritmocyk-enunciado/54918074)

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

### Integrante 3: Integración, Árbol Sintáctico, Frontend React y Documentación (1 Punto + Integración)
* **Responsabilidad Principal:** Completar las funcionalidades de salida exigidas, unificar las ramas de desarrollo, construir el frontend en React con D3.js, containerizar con Docker y estructurar la documentación técnica.
* **Módulos asignados:** `cyk.py` (parse tree), `main.py` (CLI), `frontend/` (React + Tailwind + D3.js), `Dockerfile`, `docker-compose.yml`, `app.py` y `DOCUMENTACION.md`.
* **Tareas realizadas:**
  1. **Almacenamiento de antecedentes (*back-pointers*):** Registro estructurado de la procedencia de cada derivación (`("term", w)` y `("bin", k, B, C)`).
  2. **Reconstrucción del Parse Tree:** Implementación del recorrido recursivo `construir_arbol` y generador de árbol jerárquico (`formatear_arbol_texto` y `arbol_a_parentesis`).
  3. **Medición de tiempos:** Inclusión de `time.perf_counter()` en milisegundos y segundos exactos.
  4. **Salida estricta SÍ / NO:** Validación conforme a especificación.
  5. **Frontend Moderno en React con D3.js:** Creación de una SPA reactiva con zoom interactivo, navegación por pestañas y visualización de la tabla dinámica de programación dinámica.
  6. **Containerización Docker:** Despliegue en un solo comando mediante `docker compose up --build`.
  7. **Documentación del proyecto:** Redacción técnica completa, diseño de software, análisis pedagógico paso a paso y recopilación de evidencias con screenshots.

---

## 2. Diseño de la Aplicación

### 2.1 Diagrama de Arquitectura del Sistema
El sistema implementa una arquitectura modular desacoplada entre el motor formal y la capa visual:

```
┌────────────────────────────────────────────────────────┐
│               CAPA DE ENTRADA Y PARSING                 │
│  • parser_gramatica.py (Lee reglas CFG)                 │
│  • tipos_gramatica.py / utils_gramatica.py             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             CAPA DE SIMPLIFICACIÓN A CNF               │
│  • simplificacion_gramatica.py                         │
│    - eliminar_epsilon()                                │
│    - eliminar_unitarias()                              │
│    - eliminar_inutiles()                               │
│  • cnf.py (Binarización y normalización CNF)           │
└──────────────────────────┬─────────────────────────────┘
                           │  Gramática en CNF + Símbolo S0
                           ▼
┌────────────────────────────────────────────────────────┐
│             MOTOR DE INFERENCIA CYK & TREE             │
│  • cyk.py                                              │
│    - indexar_gramatica() [O(1) unarias / binarias]     │
│    - cyk() [Tabla DP T[i][j] con back-pointers]        │
│    - construir_arbol() [Recorrido recursivo del árbol] │
│    - arbol_a_parentesis() / formatear_arbol_texto()    │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│     LÍNEA DE COMANDOS   │ │     FRONTEND REACT      │
│        (main.py)        │ │    (SPA con D3.js)      │
│  • SÍ / NO              │ │  • Árbol SVG interactivo│
│  • Tiempo en ms         │ │  • Matriz triangular DP │
│  • Árbol ASCII          │ │  • Docker Compose       │
└─────────────────────────┘ └─────────────────────────┘
```

---

## 3. Fundamento Teórico y Funcionamiento del Algoritmo CYK

### 3.1 ¿Qué problema resuelve el algoritmo CYK?
Dada una gramática libre de contexto en Forma Normal de Chomsky (CNF) y una frase $w$ compuesta por $n$ palabras ($w = w_0\, w_1 \dots w_{n-1}$), el algoritmo responde: **¿puede la gramática generar esta frase?**

Para resolverlo, utiliza **programación dinámica**:
1. Resuelve primero los subproblemas elementales (las palabras sueltas, longitud 1).
2. Guarda los resultados en una tabla estructurada.
3. Con dichas soluciones, construye problemas progresivamente mayores (subcadenas de 2 palabras, luego 3, ..., hasta las $n$ palabras de la frase completa).
4. **Principio fundamental:** Nunca se resuelve dos veces el mismo segmento de texto.

### 3.2 ¿Por qué se exige la Forma Normal de Chomsky (CNF)?
En CNF, cualquier derivación de una subcadena de 2 o más palabras proviene **estrictamente** de una regla de la forma:
$$A \to B\,C$$
Esto garantiza que cualquier segmento sintáctico de tamaño $L \ge 2$ se compone de la concatenación exacta de **dos pedazos no vacíos**. Gracias a esto, el algoritmo solo necesita evaluar particiones binarias (un único punto de corte $k$).

---

## 4. Ejemplo Teórico Paso a Paso

### 4.1 Gramática de Ejemplo y Frase
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

### 4.2 La Tabla de Programación Dinámica (La Escalera Triangular)
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

### 4.3 Concepto de Corte ($k$)
Para analizar una subcadena $[i, j]$ de longitud $L \ge 2$, se deben probar todas las formas posibles de partirla en dos fragmentos contiguos no vacíos:
* **Fragmento izquierdo:** $[i, k]$
* **Fragmento derecho:** $[k+1, j]$

El índice de corte $k$ recorre el intervalo $[i, j-1]$ (en código Python: `range(i, j)`).  
Una subcadena de longitud $L$ tiene exactamente $L - 1$ cortes posibles.

**Ejemplo de cortes para la celda $[1, 4]$ ($«a\ a\ b\ a»$):**
1. $k = 1$: Izquierda $[1, 1] = «a»$ | Derecha $[2, 4] = «a\ b\ a»$
2. $k = 2$: Izquierda $[1, 2] = «a\ a»$ | Derecha $[3, 4] = «b\ a»$
3. $k = 3$: Izquierda $[1, 3] = «a\ a\ b»$ | Derecha $[4, 4] = «a»$

---

### 4.4 Ejecución Paso a Paso sobre «baaba»

#### Paso 1: Largo 1 (Inicialización)
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
* $[0, 2]$ (`baa`): $\mathbf{\emptyset}$
* $[1, 3]$ (`aab`): $\mathbf{\{B\}}$
* $[2, 4]$ (`aba`): $\mathbf{\{B\}}$

#### Paso 4: Largo 4 (3 cortes por celda)
* $[0, 3]$ (`baab`): $\mathbf{\emptyset}$
* $[1, 4]$ (`aaba`): $\mathbf{\{S, C, A\}}$

#### Paso 5: Largo 5 (Frase Completa $[0, 4]$, 4 cortes)
* $k=0$: $[0,0]\{B\} \times [1,4]\{S,C,A\} \implies BC \to S,\; BA \to A \implies \mathbf{\{S, A\}}$
* $k=1$: $[0,1]\{A,S\} \times [2,4]\{B\} \implies AB \to C \implies \mathbf{\{C\}}$
* **Resultado Celda Final $[0, 4]$:** $\mathbf{\{S, A, C\}}$

**Veredicto:** Como el símbolo inicial $S \in T[0][4]$, la frase **SÍ** pertenece al lenguaje.

---

## 5. Caso de Estudio: Gramática en Inglés y Parse Tree

### 5.1 Gramática en CNF
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

### 5.2 Reconstrucción del Parse Tree mediante Back-Pointers
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

## 6. Ejemplos, Pruebas Realizadas y Capturas de Pantalla

A continuación se presentan los resultados visuales obtenidos en la aplicación containerizada bajo Docker:

### 6.1 Prueba 1: Frase Aceptada con Árbol Sintáctico Interactivo
* **Frase:** `She eats a cake with a fork`
* **Veredicto:** **SÍ (Aceptada)**
* **Tiempo:** 0.0643 ms

![Árbol Sintáctico Frase Aceptada](docs/screenshots/01_arbol_sintactico_aceptada.png)

---

### 6.2 Prueba 2: Tabla de Programación Dinámica CYK ($T[i][j]$)
Muestra la matriz triangular donde cada celda almacena el conjunto de variables sintácticas generadoras y la celda superior derecha confirma la presencia de $\{S_0\}$.

![Tabla Dinámica CYK](docs/screenshots/02_tabla_dinamica_cyk.png)

---

### 6.3 Prueba 3: Frase Rechazada (Sintaxis Inválida)
* **Frase:** `The cat drinks beer`
* **Veredicto:** **NO (Rechazada)**
* **Tiempo:** 0.0440 ms
* **Motivo:** En esta gramática, `beer` es sustantivo `N`, pero la regla sintáctica para objeto directo exige `NP -> Det N`, por lo que la ausencia de `the` o `a` invalida la frase.

![Frase Rechazada](docs/screenshots/03_frase_rechazada.png)

---

### 6.4 Prueba 4: Segunda Frase Aceptada
* **Frase:** `The cat drinks the beer`
* **Veredicto:** **SÍ (Aceptada)**
* **Tiempo:** 0.0691 ms

![Segunda Frase Aceptada](docs/screenshots/04_segunda_frase_aceptada.png)

---

### 6.5 Tabla Comparativa de Pruebas

| Frase Evaluada | Veredicto | Tiempo (ms) | Diagnóstico Sintáctico |
| :--- | :---: | :---: | :--- |
| `She eats a cake with a fork` | **SÍ** | 0.064 ms | Oración compuesta con sintagma preposicional instrumental. |
| `The cat drinks the beer` | **SÍ** | 0.069 ms | Sujeto + Verbo Transitivo + Objeto Directo definido. |
| `He cuts meat with a knife` | **SÍ** | 0.061 ms | Pronombres personales directos (`he`). |
| `The cat drinks beer` | **NO** | 0.044 ms | Rechazada: falta determinante en objeto directo. |
| `She eats fork` | **NO** | 0.041 ms | Rechazada: falta determinante antes de `fork`. |
| `She runs fast` | **NO** | 0.022 ms | Rechazada: vocabulario desconocido fuera de la gramática. |

---

## 7. Discusión, Obstáculos Encontrados y Recomendaciones

### 7.1 Obstáculos Encontrados
1. **Pérdida de Información Léxica en Producciones Unitarias:**  
   Al eliminar producciones unitarias (ejemplo: `VP -> eats`), el símbolo `eats` queda catalogado tanto como verbo `V` como frase verbal `VP`. Esto causaba ambigüedades en la diagonal de largo 1.  
   *Solución:* Se indexaron todas las opciones unarias en sets para permitir que el análisis considere ambos roles sintácticos en las combinaciones superiores.
2. **Reconstrucción Determinista del Árbol Sintáctico:**  
   Cuando existen múltiples particiones válidas para una misma subcadena, almacenar listas generaba bosques exponenciales.  
   *Solución:* Se optó por una política *first-match* en el back-pointer para garantizar un árbol único, determinista y de costo $O(n)$ en memoria durante el recorrido.
3. **Containerización y Despliegue de React sin Servidores Externos:**  
   Para evitar obligar al usuario a correr `npm run dev` y `python app.py` en consolas separadas, se diseñó un `Dockerfile` multi-stage: Node.js compila el bundle estático de Vite y Python lo sirve junto a la API REST en el puerto `5000`.

### 7.2 Recomendaciones
* Para gramáticas ambiguas más complejas del procesamiento del lenguaje natural (NLP), se recomienda evolucionar a **Probabilistic CYK (PCYK)** con pesos de probabilidad en cada producción.
* El frontend desarrollado con D3.js y Tailwind CSS demostró ser altamente útil para la docencia y comprensión del algoritmo, por lo que se recomienda para futuras demostraciones en el curso.

---

## 8. Instrucciones de Ejecución con Docker

Para levantar toda la aplicación (Backend + Frontend React) en un solo comando:

```bash
docker compose up --build -d
```
Luego abre tu navegador en:  
**[http://localhost:5000](http://localhost:5000)**

Para detener el contenedor:
```bash
docker compose down
```

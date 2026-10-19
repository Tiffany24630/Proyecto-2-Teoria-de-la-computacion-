# Informe del Proyecto 2: Simplificación de Gramáticas y Algoritmo CYK

**Curso:** Teoría de la Computación  
**Rol / Integrante:** Integrante 3 – Integración, Árbol Sintáctico, Frontend y Documentación  
**Fecha:** Octubre, 2026  

---

## 1. Diseño de la Aplicación

### 1.1 Arquitectura del Sistema
El sistema se diseñó de manera modular en Python, separando responsabilidades en tres capas fundamentales:

1. **Capa de Gramática y CNF (Módulos Base):**
   - `parser_gramatica.py`: Lectura y parsing de reglas en formato CFG.
   - `simplificacion_gramatica.py`: Algoritmos de eliminación de producciones $\varepsilon$ (`eliminar_epsilon`), producciones unitarias (`eliminar_unitarias`) y símbolos inútiles/no generadores/inalcanzables (`eliminar_inutiles`).
   - `cnf.py`: Transformación a Forma Normal de Chomsky mediante la creación de variables para terminales en producciones compuestas y binarización secuencial de producciones de longitud $> 2$.
   - `utils_gramatica.py` y `tipos_gramatica.py`: Tipado estricto (`Gramatica`, `Produccion`) y utilidades para nombres únicos.

2. **Capa del Algoritmo CYK y Árbol Sintáctico (Motor de Inferencia):**
   - `cyk.py`:
     - **Pre-indexación**: Indexación en $O(1)$ de reglas unarias ($A \to a$) y binarias ($A \to B\,C$).
     - **Programación Dinámica**: Construcción de la matriz triangular superior $T[i][j]$ donde cada celda almacena un diccionario de no-terminales alcanzables junto con su tupla de antecedentes (*back-pointers*).
     - **Reconstrucción del Parse Tree**: Función recursiva `construir_arbol` que parte de la raíz `S0` en $T[0][n-1]$ y navega los puntos de división $k$ y los símbolos hijos $(B, C)$ o el token terminal.
     - **Formatos de Salida**: Impresión en árbol jerárquico ASCII, notación entre corchetes y exportación a estructura JSON para el frontend.

3. **Capa de Integración, CLI y Frontend:**
   - `main.py`: Punto de entrada CLI con soporte para argumentos `--frase`, `--salida` y medición de tiempo de ejecución con `time.perf_counter()`.
   - `app.py` / `web/`: Interfaz gráfica interactiva que renderiza en tiempo real la gramática CNF, la tabla dinámica CYK y el diagrama SVG interactivo del árbol sintáctico.

---

## 2. Batería de Pruebas y Ejemplos

Gramática utilizada: `ejemplos/ingles.txt`

### 2.1 Frases Aceptadas (Pertenecen al Lenguaje)

| Frase | Resultado | Tiempo (ms) | Justificación / Estructura Sintáctica |
| :--- | :---: | :---: | :--- |
| `She eats a cake with a fork` | **SÍ** | ~0.05 ms | Derivación válida: `NP VP` donde `VP -> VP PP`. |
| `The cat drinks the beer` | **SÍ** | ~0.04 ms | Estructura clásica: `[NP Det N] [VP V NP]`. |
| `He cuts meat with a knife` | **SÍ** | ~0.06 ms | `VP -> VP PP`, `PP -> with a knife`. |
| `A dog eats soup` | **SÍ** | ~0.04 ms | Frase simple: `[NP a dog] [VP eats [NP soup]]`. |
| `The cat drinks` | **SÍ** | ~0.03 ms | Uso de verbo intransitivo directo en `VP -> drinks`. |
| `She cooks with a spoon in an oven` | **SÍ** | ~0.07 ms | Múltiples sintagmas preposicionales encadenados. |

### 2.2 Frases Rechazadas (No Pertenecen al Lenguaje)

| Frase | Resultado | Tiempo (ms) | Causa de Rechazo |
| :--- | :---: | :---: | :--- |
| `The cat drinks beer` | **NO** | ~0.03 ms | `beer` es sustantivo `N`, pero la gramática exige `NP -> Det N`, requiriendo un determinante. |
| `She eats fork` | **NO** | ~0.03 ms | Falta el determinante `a` o `the` antes de `fork`. |
| `Cat drinks the beer` | **NO** | ~0.03 ms | Sujeto carece de determinante. |
| `With a fork she eats` | **NO** | ~0.04 ms | Orden sintáctico inválido (la gramática solo acepta `S -> NP VP`). |
| `She runs fast` | **NO** | ~0.02 ms | Palabras `runs`, `fast` desconocidas en el léxico. |

---

## 3. Discusión, Obstáculos Encontrados y Recomendaciones

### 3.1 Obstáculos Encontrados
1. **Pérdida de la Estructura Sintáctica en CNF:**
   - Al binarizar producciones complejas (creando variables intermedias `BIN_1`, `BIN_2`, etc.) y al reemplazar terminales con variables (`T_a`, `T_the`), el árbol de derivación directo refleja la gramática CNF en lugar de las reglas originales.
   - *Solución implementada:* Mantener el árbol fiel a las decisiones de la tabla dinámica y ofrecer la representación legible para el análisis sintáctico.

2. **Compatibilidad de Caracteres en Consolas de Windows:**
   - Al renderizar caracteres Unicode para árboles en `cmd.exe` o `PowerShell` con codificación `cp1252`, surgieron errores `UnicodeEncodeError`.
   - *Solución:* Se ajustó la salida por consola con conectores ASCII estándar (`+--`, `\--`, `|`), garantizando compatibilidad universal sin caídas.

3. **Pre-indexación para Rendimiento:**
   - La implementación ingenua de CYK itera sobre todas las reglas de la gramática en cada celda $(i, j)$ y para cada partición $k$, resultando en una complejidad práctica lenta.
   - *Solución:* Se indexaron las reglas invertidas (`(B, C) -> {A}` y `term -> {A}`), reduciendo la búsqueda a un acceso directo $O(1)$ por par de no-terminales.

### 3.2 Recomendaciones
- Para extensiones futuras de gramáticas ambiguas, se recomienda almacenar una lista de alternativas en cada celda para poder explorar todos los árboles posibles (bosque de análisis o *parse forest*).
- Enriquecer el preprocesamiento de texto con soporte automático para puntuación final (`.`, `?`, `!`) y contracciones comunes en inglés.

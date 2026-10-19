import argparse
import sys
import time
from pathlib import Path
from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica
from cyk import cyk, construir_arbol, formatear_arbol_texto, arbol_a_parentesis

# Permite imprimir SÍ, ε y ∅ también en terminales de Windows.
sys.stdout.reconfigure(encoding="utf-8")
parser = argparse.ArgumentParser(
    description="Convierte una gramatica CFG a CNF y valida una frase con el algoritmo CYK."
)
parser.add_argument(
    "archivo",
    nargs="?",
    type=Path,
    default=Path(__file__).resolve().parent / "ejemplos" / "ingles.txt",
    help="Archivo de gramatica; por defecto se usa la gramatica inglesa del enunciado.",
)
parser.add_argument(
    "-o",
    "--salida",
    type=Path,
    help="Archivo opcional donde guardar la gramatica convertida.",
)
parser.add_argument(
    "-f",
    "--frase",
    help="Frase a validar. Si se omite y no se usa --solo-gramatica, se solicita por teclado.",
)
parser.add_argument(
    "--solo-gramatica",
    action="store_true",
    help="Solo convierte y analiza la gramatica sin validar frases con CYK.",
)
args = parser.parse_args()

try:
    texto = args.archivo.read_text(encoding="utf-8")
    gramatica, inicial = leer_gramatica(texto)

    # Evaluar CNF sobre la gramatica ORIGINAL (antes de convertir)
    cnf_original = es_cnf(gramatica, inicial)

    if cnf_original:
        gramatica_cnf, nuevo_inicial = gramatica, inicial
    else:
        gramatica_cnf, nuevo_inicial = convertir_a_cnf(gramatica, inicial)

except (OSError, UnicodeError, ValueError) as error:
    parser.error(str(error))

if not es_cnf(gramatica_cnf, nuevo_inicial):
    parser.error("La gramática resultante no cumple CNF.")
resultado = formatear_gramatica(gramatica_cnf, nuevo_inicial)
print(f"¿La gramatica de entrada ya es CNF?: {'SI' if cnf_original else 'NO'}")
print("Ya esta en CNF: se utiliza sin convertir." if cnf_original
      else "No esta en CNF: se convirtio a CNF.")
print("=== Gramatica en CNF ===")
print(resultado)

if args.salida:
    try:
        args.salida.write_text(resultado + "\n", encoding="utf-8")

    except OSError as error:
        parser.error(f"No se pudo guardar el archivo de salida: {error}")

    print(f"Gramatica guardada en: {args.salida}")

if args.solo_gramatica:
    print("\n[Modo solo gramatica: no se ejecuto CYK]")
else:
    # Parte del algoritmo de CYK
    frase = args.frase if args.frase is not None else input("\nIngrese la frase a validar: ")

    # Terminales de la gramatica CNF (producciones A -> a)
    terminales = {p[0] for ps in gramatica_cnf.values() for p in ps if len(p) == 1}

    # Se respeta la palabra tal cual; si no existe, se prueba en minusculas ("She" -> "she")
    palabras = [w if w in terminales else w.lower() for w in frase.split()]

    # Medicion de tiempo del algoritmo CYK
    inicio_tiempo = time.perf_counter()
    acepta, tabla = cyk(gramatica_cnf, nuevo_inicial, palabras)
    fin_tiempo = time.perf_counter()
    tiempo_total_ms = (fin_tiempo - inicio_tiempo) * 1000

    desconocidas = [w for w in palabras if w not in terminales]

    print("\n=== Resultado CYK ===")
    print(f"Frase: {' '.join(palabras)}")
    print(f"¿Pertenece al lenguaje?: {'SÍ' if acepta else 'NO'}")
    print(f"Tiempo de validacion: {tiempo_total_ms:.4f} ms ({fin_tiempo - inicio_tiempo:.6f} segundos)")

    if desconocidas:
        print(f"Palabras que no estan en la gramatica: {', '.join(desconocidas)}")

    if acepta:
        n = len(palabras)
        arbol = construir_arbol(tabla, nuevo_inicial, 0, n - 1)
        print("\n=== Parse Tree (Arbol de Derivacion) ===")
        print(formatear_arbol_texto(arbol).strip())
        print(f"\nNotacion jerarquica: {arbol_a_parentesis(arbol)}")

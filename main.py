import argparse
from pathlib import Path
from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica
from cyk import cyk

parser = argparse.ArgumentParser(
    description="Convierte una gramática CFG a CNF y valida una frase con el algoritmo CYK."
)
parser.add_argument(
    "archivo",
    type=Path,
    help="Archivo de texto que contiene la gramática de entrada.",
)
parser.add_argument(
    "-o",
    "--salida",
    type=Path,
    help="Archivo opcional donde guardar la gramática convertida.",
)
parser.add_argument(
    "-f",
    "--frase",
    help="Frase a validar. Si se omite, se solicita por teclado.",
)
args = parser.parse_args()

try:
    texto = args.archivo.read_text(encoding="utf-8")
    gramatica, inicial = leer_gramatica(texto)
    gramatica_cnf, nuevo_inicial = convertir_a_cnf(gramatica, inicial)

except (OSError, UnicodeError, ValueError) as error:
    parser.error(str(error))

resultado = formatear_gramatica(gramatica_cnf)
print("=== Gramática en CNF ===")
print(resultado)
print(f"\n¿Es CNF?: {'SÍ' if es_cnf(gramatica_cnf, nuevo_inicial) else 'NO'}")

if args.salida:
    try:
        args.salida.write_text(resultado + "\n", encoding="utf-8")

    except OSError as error:
        parser.error(f"No se pudo guardar el archivo de salida: {error}")

    print(f"Gramática guardada en: {args.salida}")

# Parte del algoritmo de CYK
frase = args.frase if args.frase is not None else input("\nIngrese la frase a validar: ")

# Terminales de la gramática CNF (producciones A -> a)
terminales = {p[0] for ps in gramatica_cnf.values() for p in ps if len(p) == 1}

# Se respeta la palabra tal cual; si no existe, se prueba en minúsculas ("She" -> "she")
palabras = [w if w in terminales else w.lower() for w in frase.split()]

acepta, tabla = cyk(gramatica_cnf, nuevo_inicial, palabras)

desconocidas = [w for w in palabras if w not in terminales]

print("\n=== Resultado CYK ===")
print(f"Frase: {' '.join(palabras)}")
print(f"¿Pertenece al lenguaje?: {'SÍ' if acepta else 'NO'}")

if desconocidas:
    print(f"Palabras que no están en la gramática: {', '.join(desconocidas)}")


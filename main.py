import argparse
from pathlib import Path
from gramatica_cnf import convertir_a_cnf, es_cnf, formatear_gramatica, leer_gramatica

parser = argparse.ArgumentParser(
    description="Convierte una gramática CFG a Forma Normal de Chomsky."
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
args = parser.parse_args()

try:
    texto = args.archivo.read_text(encoding="utf-8")
    gramatica, inicial = leer_gramatica(texto)
    gramatica_cnf, nuevo_inicial = convertir_a_cnf(gramatica, inicial)

except (OSError, UnicodeError, ValueError) as error:
    parser.error(str(error))

resultado = formatear_gramatica(gramatica_cnf)
print(resultado)
print(f"\n¿Es CNF?: {'SÍ' if es_cnf(gramatica_cnf, nuevo_inicial) else 'NO'}")

if args.salida:
    try:
        args.salida.write_text(resultado + "\n", encoding="utf-8")

    except OSError as error:
        parser.error(f"No se pudo guardar el archivo de salida: {error}")
        
    print(f"Gramática guardada en: {args.salida}")
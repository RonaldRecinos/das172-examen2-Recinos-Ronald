"""
main.py
=======

Script principal de ejecución. Demuestra el flujo completo del sistema
de análisis de distribución de carga en la bodega de una aeronave:

    1. Validación dimensional de las matrices de entrada.
    2. Cálculo de ocupación y detección de sobrecarga.
    3. Evaluación de balance longitudinal y lateral.
    4. Extracción de la submatriz crítica de sobrecarga.

Ejecutar con:
    python main.py
"""

from cargo_hold import (
    validar_matrices,
    calcular_ocupacion,
    evaluar_balance,
    extraer_submatriz_critica,
)


def imprimir_matriz(matriz, titulo: str, formato: str = "{:8.1f}"):
    """Imprime una matriz numérica con formato alineado en consola."""
    print(f"\n{titulo}")
    print("-" * len(titulo))
    for fila in matriz:
        print(" ".join(formato.format(valor) for valor in fila))


def main():
    # -----------------------------------------------------------------
    # Datos de prueba: bodega de 5 filas (longitudinal) x 4 columnas
    # (transversal). Valores en kg.
    # -----------------------------------------------------------------
    cargas_reales = [
        [500, 480, 300, 520],
        [700, 690, 710, 705],
        [200, 150, 900, 100],
        [450, 460, 440, 455],
        [300, 320, 310, 305],
    ]

    capacidades_maximas = [
        [600, 600, 600, 600],
        [800, 800, 800, 800],
        [500, 500, 500, 500],
        [500, 500, 500, 500],
        [400, 400, 400, 400],
    ]

    tolerancia_desbalance_kg = 50.0
    ventana_k, ventana_p = 2, 2

    print("=" * 70)
    print(" SISTEMA DE ANÁLISIS DE DISTRIBUCIÓN DE CARGA - CARGO HOLD ")
    print("=" * 70)

    imprimir_matriz(cargas_reales, "Matriz de Cargas Reales (kg)", "{:8.0f}")
    imprimir_matriz(capacidades_maximas, "Matriz de Capacidades Máximas (kg)", "{:8.0f}")

    # -----------------------------------------------------------------
    # 1. Validación
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print(" PASO 1: VALIDACIÓN DIMENSIONAL Y DE COHERENCIA ")
    print("=" * 70)

    es_valida = validar_matrices(cargas_reales, capacidades_maximas)
    print(f"Resultado de validación: {'APROBADA' if es_valida else 'RECHAZADA'}")

    if not es_valida:
        print("Las matrices no son válidas. Deteniendo ejecución.")
        return

    # -----------------------------------------------------------------
    # 2. Ocupación y sobrecarga
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print(" PASO 2: CÁLCULO DE OCUPACIÓN Y DETECCIÓN DE SOBRECARGA ")
    print("=" * 70)

    resultado_ocupacion = calcular_ocupacion(cargas_reales, capacidades_maximas)
    porcentajes = resultado_ocupacion["porcentajes"]
    sobrecargas = resultado_ocupacion["sobrecargas"]

    imprimir_matriz(porcentajes, "Matriz de Porcentaje de Ocupación (%)", "{:8.1f}")

    if sobrecargas:
        print(f"\nCeldas SOBRECARGADAS detectadas ({len(sobrecargas)}):")
        for (i, j) in sobrecargas:
            print(
                f"  - Fila {i}, Columna {j}: "
                f"{cargas_reales[i][j]} kg / {capacidades_maximas[i][j]} kg "
                f"= {porcentajes[i][j]:.1f}%"
            )
    else:
        print("\nNo se detectaron celdas sobrecargadas.")

    # -----------------------------------------------------------------
    # 3. Balance y simetría
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print(" PASO 3: EVALUACIÓN DE BALANCE Y SIMETRÍA ")
    print("=" * 70)

    resultado_balance = evaluar_balance(cargas_reales, tolerancia_desbalance_kg)

    print("\nPeso total por fila longitudinal (kg):")
    for i, peso in enumerate(resultado_balance["pesos_por_fila"]):
        print(f"  Fila {i}: {peso:.1f} kg")

    print(f"\nDesbalance lateral: {resultado_balance['desbalance_lateral']:.1f} kg")
    print(f"Tolerancia permitida: {tolerancia_desbalance_kg:.1f} kg")
    estado_balance = "APROBADO" if resultado_balance["balance_aprobado"] else "RECHAZADO"
    print(f"Estado de balance: {estado_balance}")

    # -----------------------------------------------------------------
    # 4. Submatriz crítica
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" PASO 4: EXTRACCIÓN DE SUBMATRIZ CRÍTICA ({ventana_k}x{ventana_p}) ")
    print("=" * 70)

    resultado_submatriz = extraer_submatriz_critica(
        porcentajes, ventana_k, ventana_p, criterio="promedio"
    )

    fi, fj = resultado_submatriz["posicion"]
    print(f"\nZona más crítica encontrada en la posición (fila={fi}, columna={fj})")
    print(f"Promedio de ocupación de la zona: {resultado_submatriz['valor_criterio']:.1f}%")
    imprimir_matriz(
        resultado_submatriz["submatriz"],
        f"Submatriz Crítica {ventana_k}x{ventana_p} (% de ocupación)",
        "{:8.1f}",
    )

    print("\n" + "=" * 70)
    print(" FIN DEL ANÁLISIS ")
    print("=" * 70)


if __name__ == "__main__":
    main()

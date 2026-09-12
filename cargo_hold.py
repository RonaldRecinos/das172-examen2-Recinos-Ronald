"""
Módulo cargo_hold
==================

Funciones para validar, calcular ocupación, evaluar balance lateral y
extraer submatrices críticas en el modelo de distribución de carga
de la bodega (cargo hold) de una aeronave.

Convención de la matriz:
    - N filas representan la dirección longitudinal (proa -> popa).
    - M columnas representan la dirección transversal (izquierda -> derecha,
      es decir, babor -> estribor).

Todas las funciones son puras: no modifican las matrices que reciben
como entrada, sino que generan y retornan nuevas estructuras.
"""

from typing import List, Tuple, Dict, Any, Optional

# Alias de tipo para mayor legibilidad
Matriz = List[List[float]]


# ---------------------------------------------------------------------------
# 1. Módulo de Validación y Coherencia Dimensional
# ---------------------------------------------------------------------------
def validar_matrices(cargas: Matriz, capacidades: Matriz) -> bool:
    """
    Verifica la coherencia dimensional y de valores entre la matriz de
    cargas reales y la matriz de capacidades máximas.

    Reglas de validación:
        1. Ambas matrices deben tener exactamente las mismas dimensiones N x M.
        2. N >= 2 y M >= 2 (bodega mínima de 2x2 compartimientos).
        3. Todas las filas de cada matriz deben tener igual longitud
           (matriz regular, sin filas irregulares).
        4. Todos los pesos reales deben ser >= 0.
        5. Todas las capacidades máximas deben ser > 0 (no se permite una
           celda con capacidad nula o negativa).

    Args:
        cargas: matriz N x M con los pesos reales en kg.
        capacidades: matriz N x M con las capacidades máximas en kg.

    Returns:
        True si ambas matrices son dimensionalmente coherentes y sus
        valores son válidos; False en caso contrario.
    """
    if cargas is None or capacidades is None:
        return False
    if not isinstance(cargas, list) or not isinstance(capacidades, list):
        return False

    n_cargas = len(cargas)
    n_capacidades = len(capacidades)

    # Mismo número de filas
    if n_cargas != n_capacidades:
        return False

    # N >= 2
    if n_cargas < 2:
        return False

    # La matriz no puede tener filas vacías inconsistentes
    if any(not isinstance(fila, list) for fila in cargas):
        return False
    if any(not isinstance(fila, list) for fila in capacidades):
        return False

    m_referencia = len(cargas[0])

    # M >= 2
    if m_referencia < 2:
        return False

    # Regularidad y valores de la matriz de cargas
    for fila in cargas:
        if len(fila) != m_referencia:
            return False
        for peso in fila:
            if not isinstance(peso, (int, float)) or isinstance(peso, bool):
                return False
            if peso < 0:
                return False

    # Regularidad y valores de la matriz de capacidades
    for fila in capacidades:
        if len(fila) != m_referencia:
            return False
        for capacidad in fila:
            if not isinstance(capacidad, (int, float)) or isinstance(capacidad, bool):
                return False
            if capacidad <= 0:
                return False

    return True


# ---------------------------------------------------------------------------
# 2. Módulo de Cálculo de Ocupación y Detección de Sobrecarga
# ---------------------------------------------------------------------------
def calcular_ocupacion(cargas: Matriz, capacidades: Matriz) -> Dict[str, Any]:
    """
    Calcula el porcentaje de ocupación de cada celda del piso de carga y
    detecta las celdas en condición de sobrecarga (> 100%).

    PorcentajeOcupacion(i, j) = (PesoReal(i, j) / CapacidadMaxima(i, j)) * 100.0

    Esta función asume que las matrices ya fueron validadas previamente
    con validar_matrices(). No modifica las matrices originales.

    Args:
        cargas: matriz N x M validada con los pesos reales en kg.
        capacidades: matriz N x M validada con las capacidades máximas en kg.

    Returns:
        Diccionario con:
            "porcentajes": nueva matriz N x M de porcentajes de ocupación.
            "sobrecargas": lista de tuplas (fila, columna) de las celdas
                cuyo porcentaje de ocupación supera 100.0%.
    """
    n = len(cargas)
    m = len(cargas[0])

    porcentajes: Matriz = [[0.0] * m for _ in range(n)]
    sobrecargas: List[Tuple[int, int]] = []

    for i in range(n):
        for j in range(m):
            porcentaje = (cargas[i][j] / capacidades[i][j]) * 100.0
            porcentajes[i][j] = porcentaje
            if porcentaje > 100.0:
                sobrecargas.append((i, j))

    return {
        "porcentajes": porcentajes,
        "sobrecargas": sobrecargas,
    }


# ---------------------------------------------------------------------------
# 3. Módulo de Evaluación de Balance y Simetría
# ---------------------------------------------------------------------------
def evaluar_balance(cargas: Matriz, tolerancia_kg: float) -> Dict[str, Any]:
    """
    Evalúa el balance longitudinal (peso por fila) y el balance lateral
    (izquierda vs. derecha) de la carga.

    PesoTotalFila(i) = suma de todos los pesos de la fila i.
    DesbalanceLateral = |SumaPesosMitadIzquierda - SumaPesosMitadDerecha|

    Reglas de división lateral:
        - Si M es par, se divide la matriz en dos mitades iguales de
          columnas (izquierda: [0, M/2), derecha: [M/2, M)).
        - Si M es impar, la columna central (eje de simetría de la
          aeronave) se omite de la comparación.

    Args:
        cargas: matriz N x M con los pesos reales en kg.
        tolerancia_kg: desbalance lateral máximo admisible, en kg.

    Returns:
        Diccionario con:
            "pesos_por_fila": lista de N elementos con el peso total de
                cada fila longitudinal.
            "desbalance_lateral": valor absoluto del desbalance
                izquierda/derecha, en kg.
            "balance_aprobado": booleano, True si desbalance_lateral es
                menor o igual a tolerancia_kg.
    """
    n = len(cargas)
    m = len(cargas[0])

    pesos_por_fila = [sum(fila) for fila in cargas]

    mitad = m // 2

    if m % 2 == 0:
        columnas_izquierda = range(0, mitad)
        columnas_derecha = range(mitad, m)
    else:
        columnas_izquierda = range(0, mitad)
        columnas_derecha = range(mitad + 1, m)
        # La columna central (índice == mitad) se omite: está sobre el
        # eje longitudinal de simetría de la aeronave.

    suma_izquierda = sum(cargas[i][j] for i in range(n) for j in columnas_izquierda)
    suma_derecha = sum(cargas[i][j] for i in range(n) for j in columnas_derecha)

    desbalance_lateral = abs(suma_izquierda - suma_derecha)
    balance_aprobado = desbalance_lateral <= tolerancia_kg

    return {
        "pesos_por_fila": pesos_por_fila,
        "desbalance_lateral": desbalance_lateral,
        "balance_aprobado": balance_aprobado,
    }


# ---------------------------------------------------------------------------
# 4. Módulo de Extracción de Submatriz de Sobrecarga Crítica
# ---------------------------------------------------------------------------
def extraer_submatriz_critica(
    porcentajes: Matriz,
    k: int,
    p: int,
    criterio: str = "promedio",
) -> Dict[str, Any]:
    """
    Recorre todas las submatrices contiguas de tamaño k x p dentro de la
    matriz de porcentajes de ocupación y extrae la que representa la zona
    más crítica de sobrecarga.

    Se utilizan matrices de sumas de prefijos (prefix sums) para evaluar
    cada ventana en tiempo O(1), lo que permite recorrer todas las
    ventanas posibles en O(N x M) en lugar de O(N x M x k x p).

    Args:
        porcentajes: matriz N x M de porcentajes de ocupación (salida de
            calcular_ocupacion).
        k: número de filas de la ventana de búsqueda.
        p: número de columnas de la ventana de búsqueda.
        criterio: "promedio" selecciona la submatriz con mayor promedio
            de ocupación; "conteo" selecciona la submatriz con mayor
            número de celdas sobrecargadas (> 100%).

    Returns:
        Diccionario con:
            "submatriz": la submatriz k x p extraída, con los valores de
                porcentaje de ocupación originales (relativos) intactos.
            "posicion": tupla (fila_inicio, columna_inicio) de la esquina
                superior izquierda de la submatriz elegida.
            "valor_criterio": valor numérico (promedio o conteo) que
                obtuvo la submatriz elegida.

    Raises:
        ValueError: si k o p son <= 0, o si la ventana k x p no cabe
            dentro de las dimensiones de la matriz.
    """
    n = len(porcentajes)
    m = len(porcentajes[0]) if n > 0 else 0

    if k <= 0 or p <= 0:
        raise ValueError("Las dimensiones de la ventana (k, p) deben ser positivas.")
    if k > n or p > m:
        raise ValueError(
            f"La ventana {k}x{p} no cabe dentro de la matriz {n}x{m}."
        )
    if criterio not in ("promedio", "conteo"):
        raise ValueError("criterio debe ser 'promedio' o 'conteo'.")

    # Matrices de prefijos con una fila y columna extra de ceros (base 0)
    prefijo_suma = [[0.0] * (m + 1) for _ in range(n + 1)]
    prefijo_sobrecarga = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n):
        for j in range(m):
            valor = porcentajes[i][j]
            es_sobrecarga = 1 if valor > 100.0 else 0
            prefijo_suma[i + 1][j + 1] = (
                valor
                + prefijo_suma[i][j + 1]
                + prefijo_suma[i + 1][j]
                - prefijo_suma[i][j]
            )
            prefijo_sobrecarga[i + 1][j + 1] = (
                es_sobrecarga
                + prefijo_sobrecarga[i][j + 1]
                + prefijo_sobrecarga[i + 1][j]
                - prefijo_sobrecarga[i][j]
            )

    def suma_ventana(prefijo, fi: int, fj: int):
        """Suma de la ventana k x p cuya esquina superior izquierda es (fi, fj)."""
        return (
            prefijo[fi + k][fj + p]
            - prefijo[fi][fj + p]
            - prefijo[fi + k][fj]
            + prefijo[fi][fj]
        )

    mejor_valor: Optional[float] = None
    mejor_posicion: Tuple[int, int] = (0, 0)

    for fi in range(0, n - k + 1):
        for fj in range(0, m - p + 1):
            if criterio == "conteo":
                valor_actual = suma_ventana(prefijo_sobrecarga, fi, fj)
            else:
                suma_ocupacion = suma_ventana(prefijo_suma, fi, fj)
                valor_actual = suma_ocupacion / (k * p)

            if mejor_valor is None or valor_actual > mejor_valor:
                mejor_valor = valor_actual
                mejor_posicion = (fi, fj)

    fi, fj = mejor_posicion
    submatriz = [fila[fj:fj + p] for fila in porcentajes[fi:fi + k]]

    return {
        "submatriz": submatriz,
        "posicion": mejor_posicion,
        "valor_criterio": mejor_valor,
    }

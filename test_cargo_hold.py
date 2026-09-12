"""
test_cargo_hold.py
===================

Pruebas unitarias para el módulo cargo_hold.

Cobertura:
    - validar_matrices: casos típicos y de borde (dimensiones, valores
      negativos, capacidades nulas, matrices irregulares).
    - calcular_ocupacion: cálculo correcto de porcentajes y detección de
      sobrecargas, incluyendo el caso límite exacto de 100%.
    - evaluar_balance: matrices balanceadas, desbalanceadas, M par e impar.
    - extraer_submatriz_critica: ventanas típicas, ventana igual a la
      matriz completa, y errores por ventana fuera de rango.

Ejecutar con:
    python -m unittest tests/test_cargo_hold.py -v
    (ejecutar desde la raíz del proyecto)
"""

import unittest
import sys
import os

# Permite importar cargo_hold.py desde la raíz del proyecto al correr
# las pruebas desde la carpeta tests/ o desde la raíz.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cargo_hold import (
    validar_matrices,
    calcular_ocupacion,
    evaluar_balance,
    extraer_submatriz_critica,
)


class TestValidarMatrices(unittest.TestCase):
    """Casos de prueba para el módulo de validación dimensional."""

    def test_matrices_validas_tipicas(self):
        cargas = [[100, 200], [150, 250]]
        capacidades = [[300, 300], [300, 300]]
        self.assertTrue(validar_matrices(cargas, capacidades))

    def test_dimensiones_distintas_filas(self):
        cargas = [[100, 200], [150, 250], [10, 10]]
        capacidades = [[300, 300], [300, 300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_irregular_cargas(self):
        # Fila con distinta cantidad de columnas
        cargas = [[100, 200], [150]]
        capacidades = [[300, 300], [300, 300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_irregular_capacidades(self):
        cargas = [[100, 200], [150, 250]]
        capacidades = [[300, 300], [300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_peso_negativo(self):
        cargas = [[100, -5], [150, 250]]
        capacidades = [[300, 300], [300, 300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_peso_cero_es_valido(self):
        # Un peso de 0 kg es válido (compartimiento vacío)
        cargas = [[0, 200], [150, 0]]
        capacidades = [[300, 300], [300, 300]]
        self.assertTrue(validar_matrices(cargas, capacidades))

    def test_capacidad_cero_invalida(self):
        cargas = [[100, 200], [150, 250]]
        capacidades = [[300, 0], [300, 300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_capacidad_negativa_invalida(self):
        cargas = [[100, 200], [150, 250]]
        capacidades = [[300, -100], [300, 300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_muy_pequena_1x2(self):
        # N < 2 debe rechazarse
        cargas = [[100, 200]]
        capacidades = [[300, 300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_muy_pequena_2x1(self):
        # M < 2 debe rechazarse
        cargas = [[100], [200]]
        capacidades = [[300], [300]]
        self.assertFalse(validar_matrices(cargas, capacidades))

    def test_matriz_minima_valida_2x2(self):
        cargas = [[0, 0], [0, 0]]
        capacidades = [[1, 1], [1, 1]]
        self.assertTrue(validar_matrices(cargas, capacidades))

    def test_matrices_none(self):
        self.assertFalse(validar_matrices(None, [[1, 1], [1, 1]]))
        self.assertFalse(validar_matrices([[1, 1], [1, 1]], None))


class TestCalcularOcupacion(unittest.TestCase):
    """Casos de prueba para el cálculo de ocupación y detección de sobrecarga."""

    def test_ocupacion_normal(self):
        cargas = [[100, 200], [300, 400]]
        capacidades = [[200, 200], [300, 400]]
        resultado = calcular_ocupacion(cargas, capacidades)
        esperado = [[50.0, 100.0], [100.0, 100.0]]
        self.assertEqual(resultado["porcentajes"], esperado)

    def test_sin_sobrecargas(self):
        cargas = [[50, 50], [50, 50]]
        capacidades = [[100, 100], [100, 100]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertEqual(resultado["sobrecargas"], [])

    def test_con_sobrecargas(self):
        cargas = [[150, 50], [50, 250]]
        capacidades = [[100, 100], [100, 100]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertIn((0, 0), resultado["sobrecargas"])
        self.assertIn((1, 1), resultado["sobrecargas"])
        self.assertNotIn((0, 1), resultado["sobrecargas"])
        self.assertNotIn((1, 0), resultado["sobrecargas"])

    def test_limite_exacto_100_no_es_sobrecarga(self):
        # Exactamente 100% NO debe considerarse sobrecarga (regla es > 100%)
        cargas = [[100, 100], [100, 100]]
        capacidades = [[100, 100], [100, 100]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertEqual(resultado["sobrecargas"], [])

    def test_no_modifica_matrices_originales(self):
        cargas = [[100, 200], [300, 400]]
        capacidades = [[200, 200], [300, 400]]
        cargas_copia = [fila[:] for fila in cargas]
        capacidades_copia = [fila[:] for fila in capacidades]

        calcular_ocupacion(cargas, capacidades)

        self.assertEqual(cargas, cargas_copia)
        self.assertEqual(capacidades, capacidades_copia)

    def test_carga_cero_da_cero_por_ciento(self):
        cargas = [[0, 0], [0, 0]]
        capacidades = [[100, 200], [300, 400]]
        resultado = calcular_ocupacion(cargas, capacidades)
        self.assertEqual(resultado["porcentajes"], [[0.0, 0.0], [0.0, 0.0]])


class TestEvaluarBalance(unittest.TestCase):
    """Casos de prueba para la evaluación de balance longitudinal y lateral."""

    def test_pesos_por_fila(self):
        cargas = [[100, 200], [300, 400]]
        resultado = evaluar_balance(cargas, tolerancia_kg=1000)
        self.assertEqual(resultado["pesos_por_fila"], [300, 700])

    def test_balance_perfecto_m_par(self):
        # Izquierda: columnas 0,1 = 100+100+100+100=400
        # Derecha: columnas 2,3 = 100+100+100+100=400
        cargas = [[100, 100, 100, 100], [100, 100, 100, 100]]
        resultado = evaluar_balance(cargas, tolerancia_kg=0)
        self.assertEqual(resultado["desbalance_lateral"], 0)
        self.assertTrue(resultado["balance_aprobado"])

    def test_desbalance_m_par(self):
        cargas = [[500, 0, 0, 0], [0, 0, 0, 0]]
        resultado = evaluar_balance(cargas, tolerancia_kg=100)
        self.assertEqual(resultado["desbalance_lateral"], 500)
        self.assertFalse(resultado["balance_aprobado"])

    def test_columna_central_omitida_m_impar(self):
        # M=3: columna central (índice 1) se omite del cálculo de balance
        # Izquierda: columna 0 = 100 + 100 = 200
        # Derecha: columna 2 = 100 + 100 = 200
        # La columna central (999999, un valor extremo) no debe influir.
        cargas = [[100, 999999, 100], [100, 999999, 100]]
        resultado = evaluar_balance(cargas, tolerancia_kg=0)
        self.assertEqual(resultado["desbalance_lateral"], 0)
        self.assertTrue(resultado["balance_aprobado"])

    def test_desbalance_dentro_de_tolerancia(self):
        cargas = [[110, 100], [100, 100]]
        # Izquierda = 110+100=210, Derecha=100+100=200, desbalance=10
        resultado = evaluar_balance(cargas, tolerancia_kg=15)
        self.assertEqual(resultado["desbalance_lateral"], 10)
        self.assertTrue(resultado["balance_aprobado"])

    def test_desbalance_igual_a_tolerancia_es_aprobado(self):
        cargas = [[110, 100], [100, 100]]
        resultado = evaluar_balance(cargas, tolerancia_kg=10)
        self.assertTrue(resultado["balance_aprobado"])


class TestExtraerSubmatrizCritica(unittest.TestCase):
    """Casos de prueba para la extracción de la submatriz crítica."""

    def test_submatriz_2x2_promedio(self):
        porcentajes = [
            [10.0, 10.0, 10.0],
            [10.0, 200.0, 200.0],
            [10.0, 200.0, 200.0],
        ]
        resultado = extraer_submatriz_critica(porcentajes, k=2, p=2, criterio="promedio")
        self.assertEqual(resultado["posicion"], (1, 1))
        self.assertEqual(resultado["submatriz"], [[200.0, 200.0], [200.0, 200.0]])
        self.assertAlmostEqual(resultado["valor_criterio"], 200.0)

    def test_submatriz_criterio_conteo(self):
        porcentajes = [
            [150.0, 50.0, 50.0],
            [50.0, 150.0, 150.0],
            [50.0, 50.0, 50.0],
        ]
        resultado = extraer_submatriz_critica(porcentajes, k=2, p=2, criterio="conteo")
        # La ventana con esquina (0,1) contiene [50,50 / 150,150] -> 2 sobrecargas
        self.assertEqual(resultado["valor_criterio"], 2)

    def test_ventana_igual_a_matriz_completa(self):
        porcentajes = [[10.0, 20.0], [30.0, 40.0]]
        resultado = extraer_submatriz_critica(porcentajes, k=2, p=2)
        self.assertEqual(resultado["posicion"], (0, 0))
        self.assertEqual(resultado["submatriz"], porcentajes)

    def test_ventana_1x1(self):
        porcentajes = [[10.0, 90.0], [30.0, 40.0]]
        resultado = extraer_submatriz_critica(porcentajes, k=1, p=1)
        self.assertEqual(resultado["posicion"], (0, 1))
        self.assertEqual(resultado["submatriz"], [[90.0]])

    def test_ventana_mayor_que_matriz_lanza_error(self):
        porcentajes = [[10.0, 20.0], [30.0, 40.0]]
        with self.assertRaises(ValueError):
            extraer_submatriz_critica(porcentajes, k=3, p=2)

    def test_ventana_invalida_cero_lanza_error(self):
        porcentajes = [[10.0, 20.0], [30.0, 40.0]]
        with self.assertRaises(ValueError):
            extraer_submatriz_critica(porcentajes, k=0, p=2)

    def test_criterio_invalido_lanza_error(self):
        porcentajes = [[10.0, 20.0], [30.0, 40.0]]
        with self.assertRaises(ValueError):
            extraer_submatriz_critica(porcentajes, k=1, p=1, criterio="inexistente")

    def test_no_modifica_matriz_original(self):
        porcentajes = [[10.0, 20.0], [30.0, 40.0]]
        copia = [fila[:] for fila in porcentajes]
        extraer_submatriz_critica(porcentajes, k=1, p=1)
        self.assertEqual(porcentajes, copia)


if __name__ == "__main__":
    unittest.main(verbosity=2)

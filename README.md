# En la ingeniería aeronáutica y el transporte aéreo de carga, la distribución de masas dentro de la bodega (cargo hold) no es un simple cálculo de almacenamiento, sino un factor crítico que determina la aeronavegabilidad y la seguridad estructural del vuelo:Integridad Estructural del Piso: Cada panel o sección de la estructura del piso soporta un límite de carga seguro expresado en kilogramos. Si una celda excede su capacidad máxima de diseño (sobrecarga $>100\%$), se pueden generar deformaciones plásticas o fatiga severa en los largueros del fuselaje, comprometiendo la integridad de la aeronave.Estabilidad y Centro de Gravedad: El balance lateral y longitudinal previene momentos de alabeo o desvíos aerodinámicos imprevistos. Un desbalance excesivo entre el lado izquierdo (babor) y derecho (estribor) desestabiliza los comandos de vuelo, mientras que una mala distribución longitudinal altera el centro de gravedad fuera de los límites certificados, afectando el ángulo de ataque y el control del estabilizador horizontal.

[ Datos de Entrada: Cargas y Capacidades ]
                 │
                 ▼
      ┌─────────────────────┐
      │  validador.py       │ ──(False)──> [ Detener Ejecución ]
      └─────────┬─────────┘
                │ (True)
                ▼
      ┌──────────────────────────────────────────────┐
      │            modulo_cargas.py                  │
      │                                              │
      │  ┌────────────────────────────────────────┐  │
      │  │ calcular_ocupacion()                   │──┼──> Matriz % / Lista de Sobrecargas
      │  └────────────────────────────────────────┘  │
      │  ┌────────────────────────────────────────┐  │
      │  │ evaluar_balance()                      │──┼──> Vectores de Fila / Desbalance Lateral
      │  └────────────────────────────────────────┘  │
      │  ┌────────────────────────────────────────┐  │
      │  │ extraer_submatriz_critica()            │──┼──> Submatriz de Concentración (k x p)
      │  └────────────────────────────────────────┘  │
      └──────────────────────┬───────────────────────┘
                             │
                             ▼
                [ main.py / Pruebas Unitarias ]
                 (Visualización de Resultados)

Para evaluar el rendimiento de los algoritmos implementados, se define a $N$ como el número de filas (eje longitudinal) y $M$ como el número de columnas (eje transversal) de las matrices de la aeronave:
Complejidad Temporal:La gran mayoría de los módulos (como el cálculo de ocupación y el análisis de balance) requieren recorrer celda por celda la matriz bidimensional mediante bucles anidados. Dado que el número total de elementos a procesar es el producto directo de las dimensiones, el tiempo de ejecución crece de manera lineal respecto al tamaño total de la cuadrícula. En el caso del módulo de extracción de submatrices de tamaño fijo, el recorrido de las ventanas deslizantes se realiza en tiempo proporcional a los bloques válidos, manteniendo la cota asintótica acotada dentro del orden de complejidad matricial.

Complejidad Espacial:Para cumplir estrictamente con el principio de inmutabilidad (evitar alterar las matrices de entrada originales), los algoritmos reservan espacio en memoria para almacenar nuevas estructuras derivadas —como la matriz de porcentajes de ocupación y los arreglos de resultados—, las cuales escalan de forma proporcional al volumen de datos proporcionados por la bodega de carga.



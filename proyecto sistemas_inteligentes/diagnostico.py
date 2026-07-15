# -*- coding: utf-8 -*-
"""
Módulo de Diagnóstico Clínico-Motriz - Callao 2026
Procesa métricas en tiempo real y genera un informe de sugerencias terapéuticas.
"""

class Diagnostico:
    def __init__(self):
        # Almacenamiento de métricas por juego
        self.datos = {
            "DODGE": {
                "tiempo_supervivido": 0.0,
                "obstaculos_esquivados": 0,
                "nivel_maximo": 1
            },
            "CATCH": {
                "estrellas_atrapadas": 0,
                "tiempo_total": 45.0,
                "tasa_captura_por_minuto": 0.0,
                "nivel_maximo": 1
            },
            "OPPOSITION": {
                "intentos_correctos": 0,
                "errores_tiempo": 0,
                "racha_maxima": 0,
                "tiempos_reaccion": []  # Guarda el delta de tiempo de cada pulsación exitosa
            },
            "TEAR": {
                "bolitas_completadas": 0,
                "errores_cesto_incorrecto": 0,
                "tiempos_amasado": [],   # Duración de cada fase de amasado circular
                "hojas_completadas": 0
            }
        }
        self.juegos_jugados = set()

    def registrar_juego(self, juego):
        self.juegos_jugados.add(juego)

    def registrar_dodge(self, tiempo, nivel):
        self.registrar_juego("DODGE")
        self.datos["DODGE"]["tiempo_supervivido"] = max(self.datos["DODGE"]["tiempo_supervivido"], tiempo)
        self.datos["DODGE"]["nivel_maximo"] = max(self.datos["DODGE"]["nivel_maximo"], nivel)
        self.datos["DODGE"]["obstaculos_esquivados"] = int(tiempo * (1.5 + (nivel * 0.2)))

    def registrar_catch(self, estrellas, nivel):
        self.registrar_juego("CATCH")
        self.datos["CATCH"]["estrellas_atrapadas"] = max(self.datos["CATCH"]["estrellas_atrapadas"], estrellas)
        self.datos["CATCH"]["nivel_maximo"] = max(self.datos["CATCH"]["nivel_maximo"], nivel)
        self.datos["CATCH"]["tasa_captura_por_minuto"] = (self.datos["CATCH"]["estrellas_atrapadas"] / 45.0) * 60.0

    def registrar_op_exito(self, tiempo_tomado):
        self.registrar_juego("OPPOSITION")
        self.datos["OPPOSITION"]["intentos_correctos"] += 1
        self.datos["OPPOSITION"]["tiempos_reaccion"].append(tiempo_tomado)

    def registrar_op_fallo(self):
        self.registrar_juego("OPPOSITION")
        self.datos["OPPOSITION"]["errores_tiempo"] += 1

    def registrar_op_racha(self, racha):
        self.datos["OPPOSITION"]["racha_maxima"] = max(self.datos["OPPOSITION"]["racha_maxima"], racha)

    def registrar_tear_bolita(self, tiempo_taller):
        self.registrar_juego("TEAR")
        self.datos["TEAR"]["bolitas_completadas"] += 1
        self.datos["TEAR"]["tiempos_amasado"].append(tiempo_taller)

    def registrar_tear_error_cesto(self):
        self.registrar_juego("TEAR")
        self.datos["TEAR"]["errores_cesto_incorrecto"] += 1

    def registrar_tear_hoja_completa(self):
        self.registrar_juego("TEAR")
        self.datos["TEAR"]["hojas_completadas"] += 1

    def generar_informe(self):
        """
        Analiza cuantitativamente los datos guardados de las actividades 
        jugadas y redacta observaciones cualitativas y planes de acción clínicos.
        """
        informe = {}
        
        # 1. ANALISIS JUEGO 1: DODGE
        if "DODGE" in self.juegos_jugados:
            d = self.datos["DODGE"]
            t = d["tiempo_supervivido"]
            if t < 15.0:
                rango = "DEFICIENTE (Riesgo de coordinación visomotora)"
                obs = "Presenta retraso crítico de reacción periférica y problemas de anticipación espacial ante obstáculos móviles."
                reco = "Ejercicios de seguimiento visual lineal con pelotas físicas a baja velocidad y fortalecimiento de reflejos rápidos."
            elif t < 35.0:
                rango = "PROMEDIO AJUSTADO (Funcional estándar)"
                obs = "La coordinación óculo-manual responde bien a velocidades bajas/medias, pero flaquea bajo estrés por aceleración."
                reco = "Prácticas de deportes de raqueta recreativos, malabares con dos pelotas para potenciar la visión periférica."
            else:
                rango = "EXCELENTE (Rendimiento psicomotriz superior)"
                obs = "Reflejos visomotores estables de alto nivel. Excelente gestión y planificación espacial continua bajo exigencia."
                reco = "Mantener el entrenamiento actual. Desafiar con actividades de coordinación bilateral desasociada."
                
            informe["DODGE"] = {
                "titulo": "1. Esquivar Bloques (Control Visomotor Dinámico)",
                "metrica": f"Tiempo de supervivencia: {t:.1f}s | Obstáculos esquivados: ~{d['obstaculos_esquivados']} | Nivel: {d['nivel_maximo']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        # 2. ANALISIS JUEGO 2: CATCH
        if "CATCH" in self.juegos_jugados:
            c = self.datos["CATCH"]
            tasa = c["tasa_captura_por_minuto"]
            if tasa < 12.0:
                rango = "REDUCIDO (Dificultades de estabilización de puntería)"
                obs = "Dificultad de puntería fina y control propioceptivo. Se presume presencia de temblor fino o dismetría al fijar posición."
                reco = "Actividades terapéuticas de ensamble guiado, uso de pesas ligeras en muñeca para reducir oscilaciones espontáneas."
            elif tasa < 24.0:
                rango = "FUNCIONAL (Control espacial estándar)"
                obs = "Control cinemático estable. Consigue la fijación del blanco de forma secuencial aunque ralentizada."
                reco = "Ejercicios de delineado continuo en papel sin levantar el lápiz y ensartado de cuentas medianas."
            else:
                rango = "DESTREZA SOBRESALIENTE (Alta precisión y control estático)"
                obs = "Sincronía espacio-temporal impecable. Capacidad excepcional para estabilizar el cursor en objetivos flotantes."
                reco = "Potenciar con dibujo técnico detallado, caligrafía artística o actividades de micromotricidad."

            informe["CATCH"] = {
                "titulo": "2. Alcanzar Estrellas (Precisión de Coordenadas de Mano)",
                "metrica": f"Estrellas atrapadas: {c['estrellas_atrapadas']} (~{tasa:.1f} por min) | Nivel: {c['nivel_maximo']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        # 3. ANALISIS JUEGO 3: OPPOSITION
        if "OPPOSITION" in self.juegos_jugados:
            o = self.datos["OPPOSITION"]
            tiempos = o["tiempos_reaccion"]
            prom_reaccion = sum(tiempos) / len(tiempos) if tiempos else 0.0
            total_intentos = o["intentos_correctos"] + o["errores_tiempo"]
            pct_exito = (o["intentos_correctos"] / total_intentos * 100) if total_intentos > 0 else 0.0
            
            if pct_exito < 55.0 or (prom_reaccion > 4.5 and prom_reaccion != 0):
                rango = "COMPROMETIDO (Praxia de disociación digital compleja)"
                obs = "Se denota sinquinesia (los dedos restantes acompañan involuntariamente al dedo objetivo) y lentitud de planificación."
                reco = "Uso de masillas terapéuticas de densidades medias para aislar extensiones, flexión forzada selectiva de dedos individuales."
            elif pct_exito < 80.0:
                rango = "ADECUADO / EN DESARROLLO (Pérdida de foco temporal)"
                obs = "Ejecuta de manera consciente la secuencia bimanual, pero pierde coordinación bajo ritmos rápidos o aleatoriedad."
                reco = "Secuenciación rítmica dactilar sobre mesa (tappings rítmicos controlados por metrónomo), abrochar botones."
            else:
                rango = "EXCELENTE DISOCIACIÓN DIGITAL (Agilidad bimanual alta)"
                obs = "Capacidad óptima de aislamiento neurodinámico de los 5 dedos de forma simétrica bilateral. Reacción veloz."
                reco = "Mantener estimulación con instrumentos de cuerda o viento (piano, guitarra), dactilografía veloz."

            informe["OPPOSITION"] = {
                "titulo": "3. Oposición Digital Bimanual (Aislamiento de Dedos)",
                "metrica": f"Éxito dactilar: {pct_exito:.1f}% ({o['intentos_correctos']}/{total_intentos}) | T. Reacción Prom: {prom_reaccion:.2f}s | Racha máx: {o['racha_maxima']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        # 4. ANALISIS JUEGO 4: TEAR
        if "TEAR" in self.juegos_jugados:
            t = self.datos["TEAR"]
            tiempos_a = t["tiempos_amasado"]
            prom_amasado = sum(tiempos_a) / len(tiempos_a) if tiempos_a else 0.0
            
            if t["bolitas_completadas"] < 2:
                rango = "REQUIERE INTERVENCIÓN (Incoordinación bimanual de tracción)"
                obs = "Dificultad marcada en pasos secuenciales (rasgar requiere tracciones opuestas asíncronas) o debilidad en pinza digital de sostén."
                reco = "Rasgado real de hojas de papel periódico de diferente grosor y gramaje, amasado fuerte de plastilina gruesa."
            elif t["errores_cesto_incorrecto"] > 2:
                rango = "ATENCIÓN DISOCIADA (Falla en inhibición cognitiva)"
                obs = "La motricidad fina es funcional, pero existe un fallo cognitivo en la discriminación de color o en la correspondencia espacial."
                reco = "Juegos de mesa físicos de clasificación por formas y colores bajo restricciones lúdicas complejas."
            else:
                rango = "ÓPTIMO Y COORDINADO (Praxia fina secuencial completa)"
                obs = "Habilidad de praxia secuencial madura y limpia (gestos de agarre, tracción de rasgado, giros circulares precisos y entrega)."
                reco = "Actividades cotidianas con cubiertos finos, manualidades con hilos (macramé) o costura básica."

            informe["TEAR"] = {
                "titulo": "4. Mesa de Rasgado Progresivo (Praxia Fina, Amasado y Clasificación)",
                "metrica": f"Bolitas creadas: {t['bolitas_completadas']} | Hojas limpias: {t['hojas_completadas']} | Amasado prom: {prom_amasado:.1f}s | Fallos color: {t['errores_cesto_incorrecto']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        return informe
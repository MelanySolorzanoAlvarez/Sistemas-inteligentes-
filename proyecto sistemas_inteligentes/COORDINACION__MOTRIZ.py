# -*- coding: utf-8 -*-
import cv2
import mediapipe as mp
import pygame
import sys
import random
import math
import time
import os
import urllib.request
import tempfile

# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────
GAME_W, GAME_H = 800, 600
SCREEN_W, SCREEN_H = GAME_W, GAME_H 
FPS = 60

# Colores del Entorno Lúdico
C_BG        = (10, 10, 30)
C_TEXT      = (255, 255, 255)
C_ACCENT    = (255, 220, 0)
C_PLAYER    = (0, 255, 200)
C_OBSTACLE  = (255, 80, 60)
C_BUTTON    = (30, 30, 70)
C_BUTTON_H  = (50, 50, 120)

# Colores de la Mesa de Trabajo (Madera)
C_MESA      = (105, 65, 40)
C_MESA_DARK = (70, 40, 20)

COLOR_MAP = {
    "ROJO": (255, 60, 60),
    "VERDE": (60, 220, 100),
    "AMARILLO": (255, 230, 0),
    "AZUL": (40, 140, 255)
}
COLOR_ORDER = ["ROJO", "VERDE", "AMARILLO", "AZUL"]


# ─────────────────────────────────────────────
# CLASE DIAGNÓSTICO (INTEGRADA DIRECTAMENTE)
# ─────────────────────────────────────────────
class Diagnostico:
    def __init__(self):
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
                "tiempos_reaccion": []
            },
            "TEAR": {
                "bolitas_completadas": 0,
                "errores_cesto_incorrecto": 0,
                "tiempos_amasado": [],
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
        informe = {}
        
        # 1. DODGE
        if "DODGE" in self.juegos_jugados:
            d = self.datos["DODGE"]
            t = d["tiempo_supervivido"]
            if t < 15.0:
                rango = "DEFICIENTE"
                obs = "Retraso critico de reaccion y pobre anticipacion espacial."
                reco = "Ejercicios de seguimiento visual con pelotas a baja velocidad."
            elif t < 35.0:
                rango = "PROMEDIO"
                obs = "Buen desempeño a velocidades bajas. Flaquea bajo aceleracion."
                reco = "Practicas de ping-pong o malabares suaves para vision periferica."
            else:
                rango = "EXCELENTE"
                obs = "Reflejos visomotores estables y excelente planificacion espacial."
                reco = "Mantener entrenamiento. Retar con coordinacion bilateral."
                
            informe["DODGE"] = {
                "titulo": "1. Esquivar Bloques (Control Visomotor)",
                "metrica": f"Tiempo: {t:.1f}s | Obstaculos: ~{d['obstaculos_esquivados']} | Niv: {d['nivel_maximo']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        # 2. CATCH
        if "CATCH" in self.juegos_jugados:
            c = self.datos["CATCH"]
            tasa = c["tasa_captura_por_minuto"]
            if tasa < 12.0:
                rango = "DEFICIENTE"
                obs = "Punteria imprecisa. Posible temblor fino o dismetria leve al apuntar."
                reco = "Alcanzar objetos guiados y usar pesas ligeras en la muñeca."
            elif tasa < 24.0:
                rango = "PROMEDIO"
                obs = "Control cinematico estable. Apunta bien pero de forma pausada."
                reco = "Ejercicios de delineado continuo en papel sin levantar el lapiz."
            else:
                rango = "EXCELENTE"
                obs = "Excelente sincronia y estabilizacion del cursor sobre los blancos."
                reco = "Potenciar con dibujo tecnico o caligrafia de precision."

            informe["CATCH"] = {
                "titulo": "2. Alcanzar Estrellas (Precision Espacial)",
                "metrica": f"Atrapadas: {c['estrellas_atrapadas']} (~{tasa:.1f}/min) | Niv: {c['nivel_maximo']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        # 3. OPPOSITION
        if "OPPOSITION" in self.juegos_jugados:
            o = self.datos["OPPOSITION"]
            tiempos = o["tiempos_reaccion"]
            prom_reaccion = sum(tiempos) / len(tiempos) if tiempos else 0.0
            total_intentos = o["intentos_correctos"] + o["errores_tiempo"]
            pct_exito = (o["intentos_correctos"] / total_intentos * 100) if total_intentos > 0 else 0.0
            
            if pct_exito < 55.0 or (prom_reaccion > 4.5 and prom_reaccion != 0):
                rango = "COMPROMETIDO"
                obs = "Sinquinesia detectada (movimiento involuntario de otros dedos)."
                reco = "Masillas terapeuticas aislando extensiones de cada dedo."
            elif pct_exito < 80.0:
                rango = "ADECUADO"
                obs = "Ejecuta de manera consciente pero pierde ritmo en velocidades altas."
                reco = "Tappings ritmicos sobre mesa siguiendo la guia de un metronomo."
            else:
                rango = "EXCELENTE"
                obs = "Optimo aislamiento bimanual de dedos. Reaccion dactilar muy veloz."
                reco = "Estimulacion libre con piano, guitarra o dactilografia ciega."

            informe["OPPOSITION"] = {
                "titulo": "3. Oposicion Digital (Aislamiento de Dedos)",
                "metrica": f"Exito: {pct_exito:.1f}% | Reaccion Prom: {prom_reaccion:.2f}s | Racha: {o['racha_maxima']}",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        # 4. TEAR
        if "TEAR" in self.juegos_jugados:
            t = self.datos["TEAR"]
            tiempos_a = t["tiempos_amasado"]
            prom_amasado = sum(tiempos_a) / len(tiempos_a) if tiempos_a else 0.0
            
            if t["bolitas_completadas"] < 2:
                rango = "DEFICIENTE"
                obs = "Incoordinacion bimanual de traccion o debilidad en pinza digital."
                reco = "Rasgado manual de papel periodico y abotonado de prendas reales."
            elif t["errores_cesto_incorrecto"] > 2:
                rango = "ATENCION DISOCIADA"
                obs = "Motricidad fina funcional pero con fallas de seleccion de color/cesto."
                reco = "Actividades de clasificacion de piezas fisicas con distracciones."
            else:
                rango = "EXCELENTE"
                obs = "Planificacion motriz secuencial limpia (rasga, amasa y traslada)."
                reco = "Manualidades detalladas, costura basica o uso de cubiertos finos."

            informe["TEAR"] = {
                "titulo": "4. Mesa de Rasgado (Praxia Fina y Cesto)",
                "metrica": f"Bolas: {t['bolitas_completadas']} | Hojas: {t['hojas_completadas']} | Amasado: {prom_amasado:.1f}s",
                "rango": rango,
                "observacion": obs,
                "recomendacion": reco
            }

        return informe


# ─────────────────────────────────────────────
# DETECTOR DE MANO Y GESTOS AVANZADOS
# ─────────────────────────────────────────────
class HandTracker:
    def __init__(self):
        self.hand_x = 0.5
        self.hand_y = 0.5
        self.hand_detected = False
        self.is_clicking = False
        self.is_fist = False
        self.detected_hands_landmarks = []
        
        model_url = (
            "https://storage.googleapis.com/mediapipe-models/"
            "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        )
        self.model_path = os.path.join(tempfile.gettempdir(), "hand_landmarker.task")
        
        if not os.path.exists(self.model_path):
            print(" Descargando modelo HandLandmarker oficial (~9 MB)...")
            urllib.request.urlretrieve(model_url, self.model_path)
            print(" Modelo descargado de forma segura.")

        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision as mp_vision

        base_options = mp_tasks.BaseOptions(model_asset_path=self.model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.4,
            min_hand_presence_confidence=0.4
        )
        self.detector = mp_vision.HandLandmarker.create_from_options(options)

    def _check_gestures(self, landmarks):
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        fingers_closed = True
        for tip, pip in zip(tips, pips):
            if landmarks[tip].y < landmarks[pip].y:
                fingers_closed = False
                
        fist_detected = fingers_closed and (landmarks[4].y > landmarks[3].y or abs(landmarks[4].x - landmarks[2].x) < 0.05)

        dx = landmarks[8].x - landmarks[4].x
        dy = landmarks[8].y - landmarks[4].y
        pinza_dist = math.hypot(dx, dy)
        
        is_pinza = pinza_dist < 0.055
        return fist_detected, is_pinza

    def process(self, frame_bgr):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        result = self.detector.detect(mp_image)
        self.detected_hands_landmarks = []
        
        if result.hand_landmarks:
            self.hand_detected = True
            self.detected_hands_landmarks = result.hand_landmarks
            
            landmarks = result.hand_landmarks[0]
            pointer = landmarks[8] if landmarks[8].y < landmarks[6].y else landmarks[9]
            
            self.hand_x = pointer.x
            self.hand_y = pointer.y
            self.is_fist, self.is_clicking = self._check_gestures(landmarks)
        else:
            self.hand_detected = False
            self.is_clicking = False
            self.is_fist = False

# ─────────────────────────────────────────────
# ELEMENTOS COMPARTIDOS DEL JUEGO
# ─────────────────────────────────────────────
class StarField:
    def __init__(self, n=80):
        self.stars = [[random.randint(0, GAME_W), random.randint(0, GAME_H), random.uniform(0.5, 2.0)] for _ in range(n)]
    def update(self):
        for s in self.stars:
            s[1] += s[2]
            if s[1] > GAME_H: s[1] = 0; s[0] = random.randint(0, GAME_W)
    def draw(self, surf):
        for s in self.stars:
            pygame.draw.circle(surf, (200, 200, 255), (int(s[0]), int(s[1])), 1)

class Obstacle:
    def __init__(self, speed):
        self.w = random.randint(40, 70)
        self.h = random.randint(20, 35)
        self.x = random.randint(0, GAME_W - self.w)
        self.y = -self.h
        self.speed = speed
    def update(self): self.y += self.speed
    def draw(self, surf): pygame.draw.rect(surf, C_OBSTACLE, (self.x, self.y, self.w, self.h), border_radius=5)
    def get_rect(self): return pygame.Rect(self.x, self.y, self.w, self.h)

# ─────────────────────────────────────────────
# CONTROLADOR PRINCIPAL Y MENÚS
# ─────────────────────────────────────────────
class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Sistema de Evaluacion Psicomotriz - Callao 2026")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_menu  = pygame.font.SysFont("monospace", 20, bold=True)
        self.font_hud   = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_diag  = pygame.font.SysFont("monospace", 13, bold=True)
        self.font_giant = pygame.font.SysFont("monospace", 42, bold=True)

        self.cap = cv2.VideoCapture(0)
        self.tracker = HandTracker()
        
        # SISTEMA DE DIAGNÓSTICO E INTERFAZ
        self.diagnostico = Diagnostico()
        
        self.current_screen = "MENU" 
        self.cursor_x, self.cursor_y = GAME_W // 2, GAME_H // 2
        self.stars_bg = StarField()
        
        # Botones menu
        self.btn_dodge = pygame.Rect(GAME_W // 2 - 200, 160, 400, 50)
        self.btn_catch = pygame.Rect(GAME_W // 2 - 200, 225, 400, 50)
        self.btn_opp   = pygame.Rect(GAME_W // 2 - 200, 290, 400, 50)
        self.btn_tear  = pygame.Rect(GAME_W // 2 - 200, 355, 400, 50)
        self.btn_exit  = pygame.Rect(GAME_W // 2 - 200, 435, 400, 50)
        
        # Botones en la pantalla Game Over para ir al apartado visual de diagnóstico
        self.btn_ver_diag = pygame.Rect(GAME_W // 2 - 180, 260, 360, 45)
        
        self.click_released = True
        self.score = 0
        self.level = 1
        self.game_timer = 0.0
        self.last_game = ""
        self.difficulty_mode = "FACIL"
        
        # Variables JUEGO 1 y 2
        self.target_star_x, self.target_star_y = 400, 300
        self.catch_count = 0
        self.obstacles = []
        self.spawn_timer = 0.0
        self.player_x = GAME_W // 2
        
        # Variables JUEGO 3: OPPOSITION
        self.opp_lives = 3
        self.opp_target_finger_idx = 0
        self.opp_task_timer = 0.0
        self.opp_max_time_allowed = 6.0
        self.opp_streak = 0            

        # Variables JUEGO 4: PAPER_TEAR
        self.tear_lives = 3
        self.tear_phase = "AGARRE_PILA"  
        
        self.color_order_index = 0 
        self.tear_paper_color = "ROJO"
        
        self.trozos_restantes_izquierda = 0  
        self.trozos_rects_izquierda = [] 
        
        self.tear_task_timer = 0.0
        self.tear_max_time_allowed = 25.0
        self.tear_streak = 0
        self.tear_last_y = 0
        
        self.circle_pts_history = []
        self.circle_progress = 0.0 
        
        self.botes_counts = {"ROJO": 0, "VERDE": 0, "AMARILLO": 0, "AZUL": 0}
        self.botes_rects = {
            "ROJO": pygame.Rect(50, GAME_H - 100, 110, 75),
            "VERDE": pygame.Rect(230, GAME_H - 100, 110, 75),
            "AMARILLO": pygame.Rect(420, GAME_H - 100, 110, 75),
            "AZUL": pygame.Rect(610, GAME_H - 100, 110, 75)
        }

    def update_cursor(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.tracker.process(frame)
            if self.tracker.hand_detected:
                target_x = int(self.tracker.hand_x * GAME_W)
                target_y = int(self.tracker.hand_y * GAME_H)
                self.cursor_x += (target_x - self.cursor_x) * 0.25
                self.cursor_y += (target_y - self.cursor_y) * 0.25
                return
        m_x, m_y = pygame.mouse.get_pos()
        self.cursor_x, self.cursor_y = m_x, m_y

    def run(self):
        try:
            running = True
            while running:
                dt = self.clock.tick(FPS) / 1000.0
                self.stars_bg.update()
                self.update_cursor()

                intent_click = False
                if self.tracker.is_clicking:
                    if self.click_released:
                        intent_click = True
                        self.click_released = False
                else:
                    self.click_released = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT: running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: self.current_screen = "MENU"
                        if event.key == pygame.K_r and self.current_screen == "GAME_OVER": self.reset_game(self.last_game)
                        if self.current_screen == "MENU":
                            if event.key == pygame.K_1: self.difficulty_mode = "FACIL"
                            if event.key == pygame.K_2: self.difficulty_mode = "INTERMEDIO"
                            if event.key == pygame.K_3: self.difficulty_mode = "DIFICIL"
                            if event.key == pygame.K_4: self.difficulty_mode = "ADAPTATIVA"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: intent_click = True

                if self.current_screen == "MENU": self.draw_menu(intent_click)
                elif self.current_screen == "JUEGO_DODGE": self.update_dodge(dt); self.draw_dodge()
                elif self.current_screen == "JUEGO_CATCH": self.update_catch(dt); self.draw_catch()
                elif self.current_screen == "JUEGO_OPPOSITION": self.update_opposition(dt); self.draw_opposition()
                elif self.current_screen == "JUEGO_TEAR": self.update_paper_tear(dt); self.draw_paper_tear()
                elif self.current_screen == "GAME_OVER": self.draw_game_over(intent_click)
                elif self.current_screen == "SCREEN_DIAGNOSTICO": self.draw_screen_diagnostico(intent_click)

                pygame.display.flip()
        except Exception:
            import traceback
            traceback.print_exc()
            input("\nOcurrio un error (ver arriba). Presiona ENTER para salir...")
        finally:
            self.cap.release(); pygame.quit(); sys.exit()

    def draw_menu(self, intent_click):
        self.screen.fill(C_BG); self.stars_bg.draw(self.screen)
        title = self.font_title.render("MODULO EVALUADOR MOTRIZ", True, C_PLAYER)
        self.screen.blit(title, (GAME_W // 2 - title.get_width() // 2, 25))
        diff_lbl = self.font_hud.render(f"MODO DE DIFICULTAD ACTIVO: {self.difficulty_mode}", True, C_ACCENT)
        self.screen.blit(diff_lbl, (GAME_W // 2 - diff_lbl.get_width() // 2, 75))
        
        c_rect = pygame.Rect(self.cursor_x - 5, self.cursor_y - 5, 10, 10)
        botones = [
            ("DODGE", self.btn_dodge, "JUEGO_DODGE", "1. Esquivar Bloques"),
            ("CATCH", self.btn_catch, "JUEGO_CATCH", "2. Alcanzar Estrellas"),
            ("OPPOSITION", self.btn_opp, "JUEGO_OPPOSITION", "3. Oposicion Digital Bimanual"),
            ("TEAR", self.btn_tear, "JUEGO_TEAR", "4. Mesa de Rasgado Progresivo"),
            ("EXIT", self.btn_exit, "EXIT", "5. Salir")
        ]
        for key, rect, action, txt in botones:
            is_hovered = rect.colliderect(c_rect)
            if is_hovered and intent_click:
                if action == "EXIT": pygame.quit(); sys.exit()
                else: self.reset_game(key); return
            pygame.draw.rect(self.screen, C_BUTTON_H if is_hovered else C_BUTTON, rect, border_radius=8)
            lbl = self.font_menu.render(txt, True, C_TEXT)
            self.screen.blit(lbl, (rect.x + 15, rect.y + 12))

        radius = 14 if self.tracker.is_clicking else 10
        pygame.draw.circle(self.screen, C_PLAYER, (int(self.cursor_x), int(self.cursor_y)), radius)

    def reset_game(self, game_type):
        self.score = 0; self.level = 1; self.game_timer = 0.0; self.obstacles.clear()
        if game_type == "DODGE": self.current_screen = "JUEGO_DODGE"; self.last_game = "DODGE"
        elif game_type == "CATCH": 
            self.current_screen = "JUEGO_CATCH"; self.last_game = "CATCH"
            self.catch_count = 0
            self.spawn_new_target_star()
        elif game_type == "OPPOSITION":
            self.current_screen = "JUEGO_OPPOSITION"; self.last_game = "OPPOSITION"
            self.opp_lives = 3; self.opp_streak = 0; self.opp_target_finger_idx = 0; self.set_opposition_time_limits()
        elif game_type == "TEAR":
            self.current_screen = "JUEGO_TEAR"; self.last_game = "TEAR"
            self.tear_lives = 3; self.tear_streak = 0; self.botes_counts = {c: 0 for c in COLOR_ORDER}
            self.color_order_index = 0
            self.tear_paper_color = COLOR_ORDER[self.color_order_index]
            self.start_sheet_cycle()

    def start_sheet_cycle(self):
        mode = self.difficulty_mode
        if mode == "FACIL": self.tear_max_time_allowed = 30.0
        elif mode == "INTERMEDIO": self.tear_max_time_allowed = 22.0
        elif mode == "DIFICIL": self.tear_max_time_allowed = 15.0
        else:
            self.tear_max_time_allowed = max(11.0, 30.0 - self.tear_streak * 2.5)

        self.tear_phase = "AGARRE_PILA"
        self.trozos_restantes_izquierda = 0
        self.tear_task_timer = 0.0
        self.circle_progress = 0.0
        self.circle_pts_history.clear()

    # ─────────────────────────────────────────────
    # LÓGICA DE PAPER_TEAR
    # ─────────────────────────────────────────────
    def update_paper_tear(self, dt):
        self.game_timer += dt
        self.tear_task_timer += dt
        
        if self.tear_task_timer >= self.tear_max_time_allowed:
            self.tear_lives -= 1; self.tear_streak = 0
            if self.tear_lives <= 0: 
                self.diagnostico.registrar_tear_bolita(self.tear_task_timer)
                self.current_screen = "GAME_OVER"
                return
            self.start_sheet_cycle()
            return

        c_x, c_y = self.cursor_x, self.cursor_y
        
        rect_fajo_hojas = pygame.Rect(320, 200, 160, 110)
        rect_zona_amasado = pygame.Rect(450, 180, 280, 210) 

        if self.tear_phase == "AGARRE_PILA":
            if rect_fajo_hojas.collidepoint(c_x, c_y) and self.tracker.is_clicking:
                self.tear_phase = "RASGADO_1"
                self.tear_last_y = c_y

        elif self.tear_phase == "RASGADO_1":
            if not self.tracker.is_clicking:
                self.tear_phase = "AGARRE_PILA"
                return
            if c_y - self.tear_last_y > 45:
                self.tear_phase = "RASGADO_2"
                self.tear_last_y = c_y

        elif self.tear_phase == "RASGADO_2":
            if not self.tracker.is_clicking:
                self.tear_phase = "AGARRE_PILA"
                return
            if c_y - self.tear_last_y > 45:
                self.tear_phase = "SELECCION_TROZO"
                self.trozos_restantes_izquierda = 4
                self.trozos_rects_izquierda = [
                    pygame.Rect(40, 160 + (i * 60), 75, 50) for i in range(4)
                ]

        elif self.tear_phase == "SELECCION_TROZO":
            if self.tracker.is_clicking:
                for i in range(self.trozos_restantes_izquierda):
                    r_target = self.trozos_rects_izquierda[i]
                    if r_target.collidepoint(c_x, c_y):
                        self.tear_phase = "AREA_BOLITA"
                        self.circle_progress = 0.0
                        self.circle_pts_history.clear()
                        break

        elif self.tear_phase == "AREA_BOLITA":
            if rect_zona_amasado.collidepoint(c_x, c_y):
                self.circle_pts_history.append((c_x, c_y))
                if len(self.circle_pts_history) > 15: self.circle_pts_history.pop(0)
                
                if len(self.circle_pts_history) >= 4: 
                    xs = [p[0] for p in self.circle_pts_history]
                    ys = [p[1] for p in self.circle_pts_history]
                    
                    if (max(xs) - min(xs)) > 10 and (max(ys) - min(ys)) > 10:
                        self.circle_progress += 5.0 
                        if self.circle_progress >= 100.0:
                            self.tear_phase = "CESTO"
                            self.diagnostico.registrar_tear_bolita(self.tear_task_timer)

        elif self.tear_phase == "CESTO":
            if not self.tracker.is_clicking:
                return 
                
            for color, r_bote in self.botes_rects.items():
                if r_bote.collidepoint(c_x, c_y):
                    if color == self.tear_paper_color:
                        self.botes_counts[color] += 1
                        self.score += 700 * self.level
                        self.tear_streak += 1
                        self.trozos_restantes_izquierda -= 1
                        
                        if self.trozos_restantes_izquierda > 0:
                            self.tear_phase = "SELECCION_TROZO"
                            self.tear_task_timer = 0.0 
                        else:
                            self.diagnostico.registrar_tear_hoja_completa()
                            self.color_order_index += 1
                            if self.color_order_index >= len(COLOR_ORDER):
                                self.color_order_index = 0
                                self.level += 1
                                self.botes_counts = {c: 0 for c in COLOR_ORDER} 
                                
                            self.tear_paper_color = COLOR_ORDER[self.color_order_index]
                            self.start_sheet_cycle()
                    else:
                        self.diagnostico.registrar_tear_error_cesto()
                        self.tear_lives -= 1; self.tear_streak = 0
                        if self.tear_lives <= 0: 
                            self.current_screen = "GAME_OVER"
                            return
                        self.tear_phase = "SELECCION_TROZO" 
                    return

    def draw_paper_tear(self):
        self.screen.fill(C_MESA_DARK)
        pygame.draw.rect(self.screen, C_MESA, (30, 140, GAME_W - 60, 270), border_radius=5)
        pygame.draw.rect(self.screen, (135, 90, 60), (30, 140, GAME_W - 60, 270), width=4, border_radius=5)
        
        pygame.draw.rect(self.screen, (35, 25, 20), (0, 0, GAME_W, 45))
        self.screen.blit(self.font_hud.render(f"PUNTAJE: {self.score:06d}  |  NIVEL GLOBAL: {self.level}", True, C_ACCENT), (20, 12))
        self.screen.blit(self.font_hud.render(f"HOJA ACTUAL: {self.tear_paper_color}", True, COLOR_MAP[self.tear_paper_color]), (500, 12))

        pct = max(0.0, 1.0 - (self.tear_task_timer / self.tear_max_time_allowed))
        pygame.draw.rect(self.screen, (50, 40, 35), (30, 120, GAME_W - 60, 8), border_radius=3)
        pygame.draw.rect(self.screen, C_PLAYER, (30, 120, int((GAME_W - 60) * pct), 8), border_radius=3)

        self.screen.blit(self.font_hud.render("VIDAS:", True, C_TEXT), (30, 75))
        for i in range(3):
            pygame.draw.rect(self.screen, C_OBSTACLE if i < self.tear_lives else (80,70,65), (100+(i*22), 77, 14, 14), border_radius=3)

        color_rgb = COLOR_MAP[self.tear_paper_color]

        if self.tear_phase == "AGARRE_PILA":
            pygame.draw.rect(self.screen, color_rgb, (320, 200, 160, 110), border_radius=4)
            lbl_inst = self.font_menu.render("AGARRA LA HOJA CON TU PINZA!", True, C_TEXT)
            self.screen.blit(lbl_inst, (340, 75))

        elif self.tear_phase == "RASGADO_1":
            pygame.draw.rect(self.screen, color_rgb, (320, 200, 75, 110), border_radius=3)
            pygame.draw.rect(self.screen, color_rgb, (405, 200, 75, 110), border_radius=3)
            pygame.draw.line(self.screen, C_ACCENT, (400, 190), (400, 320), 4)
            lbl_inst = self.font_menu.render("RASGA HACIA ABAJO UNA VEZ MAS!", True, C_ACCENT)
            self.screen.blit(lbl_inst, (340, 75))

        elif self.tear_phase == "RASGADO_2":
            for i in range(4):
                pygame.draw.rect(self.screen, color_rgb, (320 + (i*40), 200, 35, 110), border_radius=2)
            lbl_inst = self.font_menu.render("ULTIMO TIRON HACIA ABAJO!", True, C_ACCENT)
            self.screen.blit(lbl_inst, (340, 75))

        if self.tear_phase in ["SELECCION_TROZO", "AREA_BOLITA", "CESTO"]:
            pygame.draw.rect(self.screen, (60, 45, 35), (25, 150, 110, 250), border_radius=6)
            for i in range(self.trozos_restantes_izquierda):
                r_box = self.trozos_rects_izquierda[i]
                pygame.draw.rect(self.screen, color_rgb, r_box, border_radius=4)
                pygame.draw.rect(self.screen, C_TEXT, r_box, width=1, border_radius=4)

            if self.tear_phase == "SELECCION_TROZO":
                lbl_inst = self.font_menu.render("SELECCIONA UNA HOJITA IZQUIERDA", True, C_TEXT)
                self.screen.blit(lbl_inst, (310, 75))

        if self.tear_phase == "AREA_BOLITA":
            rect_zona_amasado = pygame.Rect(450, 180, 280, 210)
            pygame.draw.rect(self.screen, (40, 30, 25), rect_zona_amasado, border_radius=8)
            pygame.draw.rect(self.screen, C_PLAYER, rect_zona_amasado, width=2, border_radius=8)
            
            reduc = int(40 * (self.circle_progress / 100.0))
            pygame.draw.circle(self.screen, color_rgb, (590, 270), 45 - reduc // 2)
            
            pygame.draw.rect(self.screen, (20,20,20), (470, 350, 240, 14), border_radius=5)
            pygame.draw.rect(self.screen, C_ACCENT, (470, 350, int(240 * (self.circle_progress/100.0)), 14), border_radius=5)
            
            lbl_inst = self.font_menu.render("MUEVE EN CIRCULOS RAPIDO!", True, C_ACCENT)
            self.screen.blit(lbl_inst, (310, 75))

        elif self.tear_phase == "CESTO":
            pygame.draw.circle(self.screen, color_rgb, (int(self.cursor_x), int(self.cursor_y)), 14)
            pygame.draw.circle(self.screen, C_TEXT, (int(self.cursor_x), int(self.cursor_y)), 14, 2)
            lbl_inst = self.font_menu.render(f"LLEVA LA BOLITA AL CESTO {self.tear_paper_color}!", True, color_rgb)
            self.screen.blit(lbl_inst, (310, 75))

        for color, rect in self.botes_rects.items():
            rgb = COLOR_MAP[color]
            pygame.draw.rect(self.screen, rgb, rect, border_radius=6, width=3)
            pygame.draw.rect(self.screen, (rgb[0]//5, rgb[1]//5, rgb[2]//5), rect.inflate(-6, -6), border_radius=4)
            
            for b in range(self.botes_counts[color]):
                pygame.draw.circle(self.screen, rgb, (rect.x + 20 + (b*16), rect.y + 38), 7)
                pygame.draw.circle(self.screen, (255,255,255), (rect.x + 20 + (b*16), rect.y + 38), 7, 1)
                
            lbl_b = self.font_hud.render(f"{color[:3]} ({self.botes_counts[color]}/4)", True, C_TEXT)
            self.screen.blit(lbl_b, (rect.x + rect.w//2 - lbl_b.get_width()//2, rect.y - 22))

        pygame.draw.circle(self.screen, C_PLAYER if self.tracker.is_clicking else C_TEXT, (int(self.cursor_x), int(self.cursor_y)), 10, 2)

    # ─────────────────────────────────────────────
    # LÓGICA DE JUEGOS 1 Y 2
    # ─────────────────────────────────────────────
    def update_dodge(self, dt):
        self.game_timer += dt; self.score += int(dt * 30); self.level = 1 + int(self.game_timer / 12)
        self.player_x = self.cursor_x; self.spawn_timer += dt
        if self.spawn_timer >= max(0.3, 1.4 - self.level * 0.1):
            self.spawn_timer = 0.0; self.obstacles.append(Obstacle(speed=4.0 + self.level * 0.6))
        p_rect = pygame.Rect(self.player_x - 20, GAME_H - 70, 40, 40)
        for obs in self.obstacles[:]:
            obs.update()
            if obs.y > GAME_H: self.obstacles.remove(obs)
            if obs.get_rect().colliderect(p_rect): 
                self.diagnostico.registrar_dodge(self.game_timer, self.level)
                self.current_screen = "GAME_OVER"

    def draw_dodge(self):
        self.screen.fill(C_BG); self.stars_bg.draw(self.screen)
        pygame.draw.rect(self.screen, (30, 30, 70), (0, GAME_H - 30, GAME_W, 30))
        pygame.draw.circle(self.screen, C_PLAYER, (int(self.player_x), GAME_H - 50), 20)
        for obs in self.obstacles: obs.draw(self.screen)
        self.draw_hud_game()

    def spawn_new_target_star(self):
        self.target_star_x, self.target_star_y = random.randint(80, GAME_W - 80), random.randint(80, GAME_H - 120)

    def update_catch(self, dt):
        self.game_timer += dt; self.level = 1 + int(self.game_timer / 15)
        if math.hypot(self.cursor_x - self.target_star_x, self.cursor_y - self.target_star_y) < 35:
            self.score += 500 * self.level
            self.catch_count += 1
            self.spawn_new_target_star()
        
        if self.game_timer > 45.0: 
            self.diagnostico.registrar_catch(self.catch_count, self.level)
            self.current_screen = "GAME_OVER"

    def draw_catch(self):
        self.screen.fill((15, 10, 35)); self.stars_bg.draw(self.screen)
        p = int(5 * math.sin(time.time() * 10))
        pygame.draw.circle(self.screen, C_ACCENT, (self.target_star_x, self.target_star_y), 22 + p)
        pygame.draw.circle(self.screen, (255, 255, 255), (self.target_star_x, self.target_star_y), 12)
        pygame.draw.circle(self.screen, C_PLAYER, (int(self.cursor_x), int(self.cursor_y)), 15)
        self.draw_hud_game()
        lbl_time = self.font_hud.render(f"TIEMPO LIMITE: {max(0.0, 45.0 - self.game_timer):.1f}s", True, C_OBSTACLE)
        self.screen.blit(lbl_time, (GAME_W - lbl_time.get_width() - 20, 60))

    # ─────────────────────────────────────────────
    # JUEGO 3: OPPOSITION
    # ─────────────────────────────────────────────
    def set_opposition_time_limits(self):
        mode = self.difficulty_mode
        if mode == "FACIL":
            self.opp_max_time_allowed = 6.0
        elif mode == "INTERMEDIO":
            self.opp_max_time_allowed = 4.0
        elif mode == "DIFICIL":
            self.opp_max_time_allowed = 2.5
        else:  
            self.opp_max_time_allowed = 6.0
        self.opp_task_timer = 0.0

    def update_opposition(self, dt):
        self.game_timer += dt; self.opp_task_timer += dt
        if self.difficulty_mode == "ADAPTATIVA":
            if self.opp_streak < 3: self.opp_max_time_allowed = 6.0; self.level = 1
            elif self.opp_streak < 6: self.opp_max_time_allowed = 3.0; self.level = 2
            else: self.opp_max_time_allowed = 1.5; self.level = 3
        else: self.level = 1 + int(self.game_timer / 15)
        
        if self.opp_task_timer >= self.opp_max_time_allowed:
            self.diagnostico.registrar_op_fallo()
            self.opp_lives -= 1; self.opp_streak = 0
            if self.opp_lives <= 0: self.current_screen = "GAME_OVER"; return
            self.roll_next_target_finger(); return
            
        hands = self.tracker.detected_hands_landmarks
        if len(hands) == 2:
            t_pt = [8, 12, 16, 20][self.opp_target_finger_idx]; both_ok = True
            for hl in hands:
                if math.hypot(hl[4].x - hl[t_pt].x, hl[4].y - hl[t_pt].y) > 0.038: both_ok = False; break
            if both_ok: 
                self.diagnostico.registrar_op_exito(self.opp_task_timer)
                self.diagnostico.registrar_op_racha(self.opp_streak)
                self.score += int((self.opp_max_time_allowed - self.opp_task_timer) * 200) * self.level
                self.opp_streak += 1
                self.roll_next_target_finger()

    def roll_next_target_finger(self):
        if self.difficulty_mode == "FACIL" or (self.difficulty_mode == "ADAPTATIVA" and self.opp_streak < 5):
            self.opp_target_finger_idx = (self.opp_target_finger_idx + 1) % 4
        else:
            c = self.opp_target_finger_idx; n = random.randint(0, 3)
            while n == c: n = random.randint(0, 3)
            self.opp_target_finger_idx = n
        self.opp_task_timer = 0.0

    def draw_opposition(self):
        self.screen.fill((15, 15, 35)); self.stars_bg.draw(self.screen); self.draw_hud_game()
        self.screen.blit(self.font_hud.render(f"MODO: {self.difficulty_mode} | RACHA: {self.opp_streak}", True, C_PLAYER), (20, 60))
        self.screen.blit(self.font_hud.render("VIDAS MENTALES: ", True, C_TEXT), (20, 90))
        for i in range(3): pygame.draw.rect(self.screen, C_OBSTACLE if i < self.opp_lives else (50, 50, 60), (170 + (i * 25), 90, 18, 18), border_radius=4)
        pct = max(0.0, 1.0 - (self.opp_task_timer / self.opp_max_time_allowed))
        pygame.draw.rect(self.screen, (40, 40, 60), (20, 130, GAME_W - 40, 15), border_radius=5)
        pygame.draw.rect(self.screen, C_PLAYER, (20, 130, int((GAME_W - 40) * pct), 15), border_radius=5)
        pygame.draw.rect(self.screen, (20, 20, 50), (40, 220, GAME_W - 80, 180), border_radius=15)
        pygame.draw.rect(self.screen, C_PLAYER, (40, 220, GAME_W - 80, 180), width=3, border_radius=15)
        lbl_a = self.font_giant.render(f"TOCA {['INDICE', 'MEDIO', 'ANULAR', 'MEÑIQUE'][self.opp_target_finger_idx]}!", True, C_ACCENT)
        self.screen.blit(lbl_a, (GAME_W // 2 - lbl_a.get_width() // 2, 260))

    def draw_hud_game(self):
        pygame.draw.rect(self.screen, (20, 20, 50), (0, 0, GAME_W, 45))
        self.screen.blit(self.font_hud.render(f"PUNTAJE: {self.score:06d}", True, C_ACCENT), (20, 12))
        lbl_l = self.font_hud.render(f"NIVEL: {self.level}", True, C_PLAYER)
        self.screen.blit(lbl_l, (GAME_W // 2 - lbl_l.get_width() // 2, 12))
        lbl_b = self.font_hud.render("[ESC] Volver al Menu", True, C_TEXT)
        self.screen.blit(lbl_b, (GAME_W - lbl_b.get_width() - 20, 12))

    # ─────────────────────────────────────────────
    # PANTALLA GAME OVER
    # ─────────────────────────────────────────────
    def draw_game_over(self, intent_click):
        self.screen.fill((20, 5, 5))
        t = self.font_title.render("EVALUACION CONCLUIDA", True, C_OBSTACLE)
        self.screen.blit(t, (GAME_W // 2 - t.get_width() // 2, 80))
        
        s = self.font_menu.render(f"Puntaje total obtenido: {self.score}", True, C_TEXT)
        self.screen.blit(s, (GAME_W // 2 - s.get_width() // 2, 140))
        
        # Boton visual para abrir diagnostico en el ejecutable
        c_rect = pygame.Rect(self.cursor_x - 5, self.cursor_y - 5, 10, 10)
        is_hovered = self.btn_ver_diag.colliderect(c_rect)
        if is_hovered and intent_click:
            self.current_screen = "SCREEN_DIAGNOSTICO"
            return
            
        pygame.draw.rect(self.screen, C_BUTTON_H if is_hovered else C_BUTTON, self.btn_ver_diag, border_radius=6)
        lbl_btn = self.font_menu.render("VER REPORTE DE EVALUACION", True, C_PLAYER)
        self.screen.blit(lbl_btn, (self.btn_ver_diag.x + self.btn_ver_diag.w//2 - lbl_btn.get_width()//2, self.btn_ver_diag.y + 12))
        
        h1 = self.font_hud.render("[R] Reiniciar este juego", True, C_ACCENT)
        self.screen.blit(h1, (GAME_W // 2 - h1.get_width() // 2, 350))
        
        h2 = self.font_hud.render("[ESC] Regresar al Menu Principal", True, C_PLAYER)
        self.screen.blit(h2, (GAME_W // 2 - h2.get_width() // 2, 395))

        radius = 14 if self.tracker.is_clicking else 10
        pygame.draw.circle(self.screen, C_PLAYER, (int(self.cursor_x), int(self.cursor_y)), radius)

    # ─────────────────────────────────────────────
    # APARTADO VISUAL DEL DIAGNÓSTICO EN EL EJECUTABLE
    # ─────────────────────────────────────────────
    def draw_screen_diagnostico(self, intent_click):
        self.screen.fill((15, 15, 25))
        
        title = self.font_title.render("DIAGNOSTICO CLINICO-MOTRIZ", True, C_PLAYER)
        self.screen.blit(title, (GAME_W // 2 - title.get_width() // 2, 20))
        
        reporte = self.diagnostico.generar_informe()
        btn_back = pygame.Rect(GAME_W // 2 - 150, 535, 300, 40)
        c_rect = pygame.Rect(self.cursor_x - 5, self.cursor_y - 5, 10, 10)
        
        if not reporte:
            lbl_no = self.font_menu.render("No hay datos cargados para esta sesion de juego.", True, C_OBSTACLE)
            self.screen.blit(lbl_no, (GAME_W // 2 - lbl_no.get_width() // 2, 200))
        else:
            y_offset = 80
            for juego_id, data in reporte.items():
                # Recuadro de fondo por juego
                box_r = pygame.Rect(30, y_offset, GAME_W - 60, 100)
                pygame.draw.rect(self.screen, (25, 25, 45), box_r, border_radius=6)
                pygame.draw.rect(self.screen, C_BUTTON_H, box_r, width=1, border_radius=6)
                
                # Título del juego + Rango (en su respectivo color)
                lbl_t = self.font_hud.render(data["titulo"], True, C_ACCENT)
                self.screen.blit(lbl_t, (45, y_offset + 8))
                
                color_rango = C_PLAYER if "EXCELENTE" in data["rango"] or "SOBRESALIENTE" in data["rango"] else C_OBSTACLE
                lbl_r = self.font_diag.render(f"Estado: {data['rango']}", True, color_rango)
                self.screen.blit(lbl_r, (GAME_W - lbl_r.get_width() - 45, y_offset + 10))
                
                # Métricas e indicadores
                lbl_m = self.font_diag.render(f"Metricas: {data['metrica']}", True, C_TEXT)
                self.screen.blit(lbl_m, (45, y_offset + 32))
                
                # Observación clínica
                lbl_o = self.font_diag.render(f"Obs: {data['observacion']}", True, (180, 180, 200))
                self.screen.blit(lbl_o, (45, y_offset + 52))
                
                # Plan de tratamiento / Acción
                lbl_rec = self.font_diag.render(f"Tratamiento: {data['recomendacion']}", True, C_PLAYER)
                self.screen.blit(lbl_rec, (45, y_offset + 72))
                
                y_offset += 112

        # Botón para volver
        is_hovered = btn_back.colliderect(c_rect)
        if is_hovered and intent_click:
            self.current_screen = "MENU"
            return
            
        pygame.draw.rect(self.screen, C_BUTTON_H if is_hovered else C_BUTTON, btn_back, border_radius=6)
        lbl_back = self.font_menu.render("REGRESAR AL MENU", True, C_TEXT)
        self.screen.blit(lbl_back, (btn_back.x + btn_back.w//2 - lbl_back.get_width()//2, btn_back.y + 8))
        
        radius = 14 if self.tracker.is_clicking else 10
        pygame.draw.circle(self.screen, C_PLAYER, (int(self.cursor_x), int(self.cursor_y)), radius)


if __name__ == "__main__":
    controller = GameController()
    controller.run()
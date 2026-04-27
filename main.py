"""
RACE PRODUCCIONES - vMix Auto Rally Timing
Desarrollado por: Victor Hugo Lagos
Descripción: Automatización de tiempos de Rally para vMix utilizando Web Scraping (Playwright).
"""

import tkinter as tk
from tkinter import messagebox
import requests
from playwright.sync_api import sync_playwright
import threading
import queue
import time

# --- CONFIGURACIÓN DE RED ---
# Cambia esta IP por la de tu PC con vMix si no es local
VMIX_URL = "http://127.0.0.1:8088/api/"
TARGET_URL = "https://rallyenvivo.com/#/home/child"

class RallyController:
    """Controlador principal para la gestión de tiempos y comunicación con vMix."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RACE PRODUCCIONES - vMix AUTO")
        self.root.geometry("400x600")
        self.root.configure(bg="#1e1e1e")

        # Control de estado y colas
        self.task_queue = queue.Queue()
        self.cola_tiempos = []  
        self.autos_procesados = set()  
        self.auto_mode = False

        self._setup_ui()
        
        # Hilo de trabajo para no bloquear la interfaz gráfica (GUI)
        threading.Thread(target=self.worker_loop, daemon=True).start()

    def _setup_ui(self):
        """Inicializa los componentes de la interfaz de usuario."""
        tk.Label(self.root, text="CONTROL DE TIEMPOS - RACE", fg="white", 
                 bg="#1e1e1e", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="Iniciando navegador...", 
                                     fg="#f1c40f", bg="#1e1e1e")
        self.status_label.pack()

        # Botones de control manual
        self.crear_boton("ACTUALIZAR COLA (MANUAL)", "#2ecc71", "update")
        self.crear_boton("LIMPIAR COLA (RESET)", "#e74c3c", "reset")
        
        # Switch de modo automático
        self.btn_auto = tk.Button(self.root, text="MODO AUTOMÁTICO: OFF", bg="#555", fg="white", 
                                 font=("Arial", 10, "bold"), height=2, width=30, command=self.toggle_auto)
        self.btn_auto.pack(pady=20)

        tk.Label(self.root, text="En modo AUTO, el sistema escanea cada 5 segundos.", 
                 fg="#888", bg="#1e1e1e", font=("Arial", 8)).pack()

    def toggle_auto(self):
        """Alterna entre el modo de escaneo automático y manual."""
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.btn_auto.config(text="MODO AUTOMÁTICO: ON", bg="#2980b9")
            self.status_label.config(text="ESCANEANDO AUTOMÁTICAMENTE...", fg="#3498db")
        else:
            self.btn_auto.config(text="MODO AUTOMÁTICO: OFF", bg="#555")
            self.status_label.config(text="SISTEMA EN PAUSA", fg="#f1c40f")

    def crear_boton(self, texto, color, tipo):
        """Helper para crear botones uniformes."""
        btn = tk.Button(self.root, text=texto, bg=color, fg="white", font=("Arial", 10, "bold"),
                        height=2, width=30, command=lambda: self.task_queue.put(tipo))
        btn.pack(pady=10)

    def mostrar_notificacion(self, piloto, tiempo):
        """Dispara una notificación visual en pantalla (Thread-safe)."""
        self.root.after(0, self._crear_ventana_notificacion, piloto, tiempo)

    def _crear_ventana_notificacion(self, piloto, tiempo):
        """Crea un pop-up que se destruye automáticamente."""
        notif = tk.Toplevel(self.root)
        notif.geometry("250x100+10+10") 
        notif.configure(bg="#2c3e50")
        notif.overrideredirect(True) 
        notif.attributes("-topmost", True) 

        tk.Label(notif, text="NUEVOS DATOS DETECTADOS", fg="#f1c40f", bg="#2c3e50", font=("Arial", 8, "bold")).pack(pady=5)
        tk.Label(notif, text=f"{piloto}", fg="white", bg="#2c3e50", font=("Arial", 10)).pack()
        tk.Label(notif, text=f"TIEMPO: {tiempo}", fg="#2ecc71", bg="#2c3e50", font=("Arial", 11, "bold")).pack()

        notif.after(5000, notif.destroy)

    def enviar_vmix(self, titulo, campo, valor):
        """Envía datos a la API de vMix mediante peticiones HTTP GET."""
        try:
            params = {
                'Function': 'SetText', 
                'Input': titulo, 
                'SelectedName': f"{campo}.Text", 
                'Value': valor
            }
            requests.get(VMIX_URL, params=params, timeout=1)
        except Exception as e:
            print(f"Error de conexión con vMix: {e}")

    def worker_loop(self):
        """Bucle de trabajo principal en hilo secundario utilizando Playwright."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False) # Headless=True para producción sin ventana
            page = browser.new_page()
            try:
                page.goto(TARGET_URL)
                self.status_label.config(text="SISTEMA LISTO", fg="#2ecc71")
            except Exception as e:
                self.status_label.config(text="ERROR AL CARGAR WEB", fg="#e74c3c")
                print(f"Error de navegación: {e}")

            while True:
                try:
                    # Manejo de tareas manuales
                    tarea = self.task_queue.get(timeout=1)
                    if tarea == "reset":
                        self.cola_tiempos = []
                        self.autos_processed = set()
                        print("Cola de tiempos reseteada.")
                    elif tarea == "update":
                        self.escanear_y_actualizar(page)
                except queue.Empty:
                    pass

                # Ejecución automática
                if self.auto_mode:
                    self.escanear_y_actualizar(page)
                    time.sleep(5)

    def escanear_y_actualizar(self, page):
        """Extrae los datos de la tabla web y gestiona la cola de tiempos."""
        try:
            # Selector genérico para filas de tablas
            filas = page.query_selector_all("tr, .row, [role='row']")
            nuevos_detectados = []

            for f in filas:
                texto = f.inner_text().replace('\n', ' | ').strip()
                cols = [c.strip() for c in texto.split('|') if c.strip()]
                
                # Validación básica de estructura de fila (Posición, Nro, Categoria, Piloto, Navegante, Tiempo)
                if len(cols) >= 6 and cols[0].isdigit() and ":" in cols[5]:
                    num_auto = cols[1]
                    if num_auto not in self.autos_procesados:
                        nuevos_detectados.append(cols)
                        nombre_piloto = f"{cols[3]} / {cols[4]}"
                        self.mostrar_notificacion(nombre_piloto, cols[5])

            if nuevos_detectados:
                for piloto in nuevos_detectados:
                    self.cola_tiempos.insert(0, piloto)
                    self.autos_procesados.add(piloto[1])
                
                # Mantenemos solo los últimos 10 para vMix
                self.cola_tiempos = self.cola_tiempos[:10]
                self.procesar_y_enviar_cola()
        except Exception as e:
            print(f"Error durante el escaneo: {e}")

    def procesar_y_enviar_cola(self):
        """Formatea los datos acumulados y los inyecta en los campos de vMix."""
        if not self.cola_tiempos: return
        
        # Listas para agrupar datos por columna en vMix (multiline text)
        l_pos, l_nro, l_pilotos, l_tiempos, l_dif1, l_difant = [], [], [], [], [], []

        for f in self.cola_tiempos:
            l_pos.append(f[0]) 
            l_nro.append(f[1])
            l_pilotos.append(f"{f[3]} / {f[4]}")
            l_tiempos.append(f[5])
            l_dif1.append(f[6] if "+" in f[6] else "00:00.0")
            l_difant.append(f[7] if "+" in f[7] else "00:00.0")

        # Título del Input en vMix
        input_title = "TIEMPOS CATEGORIA"
        
        # Actualización de campos masiva
        self.enviar_vmix(input_title, "Categoria", self.cola_tiempos[0][2])
        self.enviar_vmix(input_title, "N° largada", "\n".join(l_pos))
        self.enviar_vmix(input_title, "N° auto", "\n".join(l_nro))
        self.enviar_vmix(input_title, "PilotoNavegante", "\n".join(l_pilotos))
        self.enviar_vmix(input_title, "Tiempo", "\n".join(l_tiempos))
        self.enviar_vmix(input_title, "Dif con el ante", "\n".join(l_difant))
        self.enviar_vmix(input_title, "Dif con el 1°", "\n".join(l_dif1))
        
        print(f"vMix actualizado: Último ingreso - {self.cola_tiempos[0][3]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RallyController(root)
    root.mainloop()

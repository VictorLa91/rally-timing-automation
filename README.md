# 🏎️ Live Rally Timing Automation for vMix

Este sistema es una solución robusta de **Broadcast Automation** desarrollada en Python. Permite extraer tiempos de carrera en tiempo real desde plataformas de cronometraje web e inyectarlos directamente en **vMix** mediante su API oficial.

Desarrollado específicamente para flujos de trabajo de **RACE PRODUCCIONES**, optimizando la tarea del Switcher Master en transmisiones en vivo de Rally, Safari y Motocross. Como recomendacion, se sugiere que e

---

## ✨ Características Principales

- **Web Scraping Dinámico:** Utiliza **Playwright** para navegar y extraer datos de tablas complejas en tiempo real.
- **Integración con vMix:** Comunicación vía HTTP GET para actualizar campos de texto en GT Titles de forma instantánea.
- **Modo Automático:** Escaneo cíclico cada 5 segundos para asegurar que el directo siempre tenga la última información.
- **Sistema de Notificaciones:** Pop-ups visuales integrados en la herramienta para alertar al operador sobre nuevos ingresos de tiempos.
- **Manejo de Encodings:** Soporte completo para caracteres especiales (ñ, tildes) en nombres de pilotos y navegantes.

---

## 🛠️ Requisitos Previos

Antes de ejecutar el script, asegúrate de tener instalado:

1. **Python 3.8+**
2. **vMix** (con la API Web habilitada en el puerto 8088 por defecto).
3. Un **Input de Título** en vMix llamado exactamente `TIEMPOS CATEGORIA` (o ajusta el nombre en el código).

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio o descargar el código
```bash
git clone https://github.com/VictorLa91/rally-timing-automation.git
cd rally-timing-automation
```

## 📡 Escenarios de Despliegue

El sistema está diseñado para ser flexible según la complejidad de la producción:

1. **Operación Unificada:** El **Switcher Master** ejecuta el script en una segunda pantalla en la misma PC de vMix, controlando los tiempos mientras realiza el poncheo de cámaras.
2. **Operación Remota (Recomendado):** Un **segundo operador** (productor de datos) ejecuta el script desde otra computadora dentro de la misma red local (LAN). Esto permite que el Switcher Master se desentienda del flujo de datos, mientras el operador monitorea que los tiempos sean correctos.

> **⚠️ Requisitos de Configuración Críticos:**
> - **vMix API:** Debe estar habilitada en `Settings > Web Controller` (puerto 8088 por defecto).
> - **Diseño del Título:** El Input en vMix debe contener campos de texto cuyos nombres coincidan EXACTAMENTE con los definidos en el código (ej. `Categoria`, `N° auto`, `PilotoNavegante`, etc.).
> - **Conectividad:** Si se usa desde otra PC, asegúrate de cambiar `127.0.0.1` en el código por la dirección IP local de la computadora que tiene vMix.

# EntregaPasoAula

> **Aviso:** Este es un proyecto educativo realizado en el contexto de la universidad en 2022. El código no sigue los estándares ni las mejores metodologías de desarrollo actuales. Ha sido publicado con fines de referencia y aprendizaje.

Aplicación de escritorio para el **conteo de personas en video de aula**. Analiza un archivo de video cuadro a cuadro, detecta movimiento mediante differencing de frames, rastrea el centroid de la silueta y cuenta personas que entran o salen de un espacio definido por barreras horizontales configurables.

### Ejemplo de la interfaz en funcionamiento



https://github.com/user-attachments/assets/18812e42-6e13-4757-bcee-025849a42f80



## Características principales

- Detección de movimiento mediante frame differencing (resta entre cuadro actual y cuadro de referencia)
- Binarización y detección de contornos para extraer la silueta en movimiento
- Tracking del centroide mediante momentos de imagen
- Máquina de estados con 4 estados: `INSIDE`, `OUTSIDE`, `ENTERING`, `EXITING`
- Dos barreras horizontales configurables para definir la zona de conteo
- Interfaz gráfica PyQt5 con visualización del video en tiempo real
- Controles de velocidad, pausa y reinicio
- Modo debug con ventanas intermedias (grayscale, delta, blur, threshold)
- Archivo de video de ejemplo incluido (`video.wmv`)

## Documentación adicional

El proyecto incluye documentación complementaria en formato PDF:

| Documento                           | Descripción                                     |
| ----------------------------------- | ----------------------------------------------- |
| `Documentación del programador.pdf` | Documentación técnica dirigida al desarrollador |
| `Documentación del usuario.pdf`     | Guía de uso para el usuario final               |

## Prerrequisitos

- **Python 3.x**
- **Sistema operativo:** Windows, Linux o macOS

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/ManuelDuque/EntregaPasoAula.git
cd EntregaPasoAula
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

| Paquete       | Versión  |
| ------------- | -------- |
| PyQt5         | 5.15.7   |
| opencv-python | 4.7.0.68 |
| imutils       | 0.5.4    |

> **Nota:** `numpy` se instala automáticamente como dependencia de `opencv-python`.

## Ejecución

```bash
python main.py
```

Se abrirá una ventana de 800×600 píxeles titulada "Paso aula" con el video de ejemplo cargado.

## Configuración

La configuración se define en `src/config.json`:

```json
{
  "video_relative_path": "video.wmv",
  "FPS": 60,
  "MAX_SPEED": 100,
  "ui": {
    "ui_relative_path": "mainwindow.ui",
    "window_title": "Paso aula",
    "counter_text": "People: {0}"
  },
  "barriers": {
    "upper": {
      "y": 35,
      "color": [0, 255, 0],
      "thickness": 5
    },
    "lower": {
      "y": 22,
      "color": [255, 0, 0],
      "thickness": 5
    }
  }
}
```

| Campo                 | Descripción                                             |
| --------------------- | ------------------------------------------------------- |
| `video_relative_path` | Ruta del archivo de video (relativa al directorio raíz) |
| `FPS`                 | Velocidad de reproducción en cuadros por segundo        |
| `MAX_SPEED`           | Velocidad máxima permitida en el control de velocidad   |
| `ui.window_title`     | Título de la ventana                                    |
| `ui.counter_text`     | Texto del contador de personas (formato `{0}` = número) |
| `barriers.upper`      | Barrera superior: posición Y, color RGB y grosor        |
| `barriers.lower`      | Barrera inferior: posición Y, color RGB y grosor        |

## Estructura del proyecto

```
EntregaPasoAula/
├── main.py                              # Punto de entrada
├── mainwindow.ui                        # Diseño de la interfaz (Qt Designer, 800×600)
├── video.wmv                            # Video de ejemplo incluido
├── Documentación del programador.pdf    # Documentación técnica
├── Documentación del usuario.pdf        # Guía de usuario
├── src/
│   ├── config.json                      # Configuración de la aplicación
│   ├── ui.py                            # Ventana PyQt5 y visualización de video
│   ├── processor.py                     # Lógica de procesamiento y conteo
│   └── utils.py                         # Singleton decorator + utilidades
└── README.md
```

### Archivos principales

| Archivo            | Descripción                                                                                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`          | Punto de entrada. Crea la aplicación Qt y la ventana principal.                                                                                                                        |
| `src/ui.py`        | Clase `Window`: ventana PyQt5 que muestra el video, barreras superpuestas, contador de personas y controles de interacción (pausa, reinicio, velocidad, debug).                        |
| `src/processor.py` | Clase `Processor`: implementa la detección de movimiento por frame differencing, extracción de contornos, tracking del centroid y la máquina de estados para conteo de entrada/salida. |
| `src/utils.py`     | Clase `Utils`: decorator singleton, carga de JSON y resolución de rutas.                                                                                                               |
| `mainwindow.ui`    | Archivo de diseño de interfaz generado con Qt Designer.                                                                                                                                |

## Arquitectura

### Flujo de procesamiento

```
Video Frame (cuadro actual)
    │
    ▼
┌──────────────────────────┐
│ Conversión a escala       │
│ de grises                 │
└────────┬─────────────────┘
         ▼
┌──────────────────────────┐
│ Frame Differencing       │  absdiff(cuadro_actual, cuadro_referencia)
│ (processor)              │
└────────┬─────────────────┘
         ▼
┌──────────────────────────┐
│ Gaussian Blur +          │
│ Threshold + Contornos    │  Extracción de silueta en movimiento
└────────┬─────────────────┘
         │ Mayor contorno encontrado
         ▼
┌──────────────────────────┐
│ Momentos de imagen       │  Cálculo del centroide (cx, cy)
│ Centroid tracking        │
└────────┬─────────────────┘
         │ Posición del centroide
         ▼
┌──────────────────────────┐
│ Máquina de estados       │
│ INSIDE / OUTSIDE /       │  Comparación contra barreras
│ ENTERING / EXITING       │  Conteo de personas
└────────┬─────────────────┘
         │
         ▼
    Actualizar UI + Contador
```

### Máquina de estados

```
                    cy < upper_barrier
              ┌───────────────────────┐
              │                       │
              ▼                       │
         ┌─────────┐           ┌──────┴─────┐
         │ ENTERING │──────────│   INSIDE   │
         └─────────┘           └──────┬─────┘
              │ cy < lower_barrier     │
              │                       ▼
         ┌────┴──────┐          ┌──────────┐
         │  OUTSIDE  │◄─────────│ EXITING  │
         └───────────┘          └──────────┘
```

- **OUTSIDE**: El centroide está por debajo de la barrera inferior
- **ENTERING**: El centroide cruza hacia arriba desde fuera
- **INSIDE**: El centroide está entre ambas barreras
- **EXITING**: El centroide cruza hacia abajo desde dentro

> El contador nunca baja de cero.

## Modo debug

Al activar el modo debug ("Show all windows"), se abren 5 ventanas adicionales de OpenCV que muestran los pasos intermedios del procesamiento:

1. **Frame** — Cuadro original
2. **Gray** — Escala de grises
3. **Frame Delta** — Diferencia entre cuadros
4. **Blurred** — Delta con blur gaussiano
5. **Thresh** — Umbral binario resultante

## Tecnologías

| Tecnología   | Uso                                               |
| ------------ | ------------------------------------------------- |
| Python 3     | Lenguaje de programación                          |
| PyQt5        | Interfaz gráfica de escritorio                    |
| OpenCV (cv2) | Procesamiento de video y visión por computadora   |
| imutils      | Utilidades de OpenCV (resize, contour operations) |
| NumPy        | Operaciones matriciales                           |

## Autor

[ManuelDuque](https://github.com/ManuelDuque)

# 🧗 Climbing & Gym Tracker (L5-S1 Edition)

Aplicación web self-hosted en **Streamlit** optimizada para dispositivos móviles y modo oscuro, diseñada para el seguimiento integral de sesiones de **Gimnasio** y **Escalada** (Boulder y Cuerda) con especial atención al cuidado de la espalda baja (**L5-S1**) y prevención de sobrecargas.

---

## 🚀 Despliegue con Docker (Recomendado)

La aplicación incluye persistencia automática de datos en SQLite mediante volúmenes de Docker.

### 1. Clonar o descargar el repositorio
```bash
git clone <tu-repositorio>
cd "Blog Escalada"
```

### 2. Levantar el servicio
```bash
docker compose up -d --build
```

### 3. Acceder a la aplicación
Abre tu navegador (o añade el acceso directo a la pantalla de inicio de tu móvil):
👉 **http://localhost:8501** (o `http://<IP-DE-TU-SERVIDOR>:8501`)

Para detener el contenedor:
```bash
docker compose down
```

---

## 💻 Ejecución Local (Sin Docker)

Si prefieres ejecutarlo directamente en tu entorno Python (3.10+):

```bash
# 1. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Lanzar la aplicación
streamlit run app.py
```

---

## 📁 Estructura del Proyecto

```text
├── app.py                  # Aplicación principal Streamlit
├── requirements.txt        # Dependencias (streamlit, pandas, plotly)
├── Dockerfile              # Imagen Python 3.11-slim optimizada
├── docker-compose.yml      # Servicio 'gym-tracker' con volumen ./data
├── .streamlit/
│   └── config.toml         # Configuración modo oscuro y responsive
├── data/
│   └── entrenamientos.db   # Base de datos SQLite persistente
└── README.md               # Documentación y guía de uso
```

---

## 🗄️ Esquema de Base de Datos (SQLite)

La base de datos se almacena en `data/entrenamientos.db` y crea automáticamente dos tablas:

### 1. `registros_gym`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER | Clave primaria autoincremental |
| `fecha` | TEXT | Fecha de la sesión (`YYYY-MM-DD`) |
| `tipo_sesion` | TEXT | Nombre o enfoque de la sesión |
| `bloque` | TEXT | Activación Lumbar, Fuerza, etc. |
| `ejercicio` | TEXT | Nombre del ejercicio |
| `serie` | INTEGER | Número de serie (1, 2, 3...) |
| `reps_objetivo` | TEXT | Repeticiones o tiempo pautado (ej. `6`, `25s`) |
| `reps_reales` | INTEGER | Repeticiones completadas |
| `peso_kg` | REAL | Carga en kg |
| `rir` | INTEGER | Repeticiones en reserva (0 a 5) |
| `notas_lumbar` | TEXT | Control L5-S1: OK, Fatiga leve, Tensión lumbar, Molestia (Parar) |

### 2. `registros_escalada`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER | Clave primaria autoincremental |
| `fecha` | TEXT | Fecha de la sesión |
| `modalidad` | TEXT | `Boulder` o `Cuerda` |
| `grado` | TEXT | Color en Boulder o Grado francés en Cuerda |
| `orden_dificultad` | INTEGER | Índice numérico para ordenación estricta |
| `intentos` | INTEGER | Número de pegues |
| `resultado` | TEXT | Flash, Encadenado, Proyecto, A vista, etc. |
| `sensacion_fisica`| TEXT | Estado L5-S1, antebrazos cargados, pump alto... |
| `notas` | TEXT | Crux, pared, sensaciones adicionales |

---

## 🤖 Formato JSON para Rutinas Generadas por IA

En la **Pestaña 1 (Gimnasio)** puedes pegar directamente rutinas generadas por cualquier IA (ChatGPT, Claude, etc.) utilizando este formato exacto:

```json
{
  "fecha": "2026-10-16",
  "tipo_sesion": "Fuerza y Protección Lumbar",
  "ejercicios": [
    {
      "bloque": "1. Activación Lumbar",
      "nombre": "Deadbug Estático",
      "series": 3,
      "reps_obj": "6",
      "peso_kg": 0
    },
    {
      "bloque": "1. Activación Lumbar",
      "nombre": "Plancha Lateral",
      "series": 3,
      "reps_obj": "25s",
      "peso_kg": 0
    },
    {
      "bloque": "2. Fuerza",
      "nombre": "Jalón al Pecho",
      "series": 3,
      "reps_obj": "10",
      "peso_kg": 45,
      "imagen_url": "https://...",
      "lumbar_tip": "Mantén torso casi vertical sin balanceos"
    }
  ]
}
```

> **Nota sobre imágenes y técnica:** Si no incluyes `imagen_url` ni `lumbar_tip`, la app utiliza su motor inteligente de coincidencia por palabras clave para asignar automáticamente la imagen anatómica local y el protocolo de seguridad L5-S1 correspondiente.

### 💡 Prompt sugerido para pedir rutinas a tu IA:
> *"Actúa como preparador físico especialista en readaptación de columna (L5-S1). Génerame una rutina en formato JSON para Climbing & Gym Tracker con fecha 'YYYY-MM-DD', tipo_sesion y una lista de ejercicios con los campos bloque, nombre, series, reps_obj, peso_kg, y opcionalmente lumbar_tip con recomendaciones para proteger L5-S1."*

---

## 🧗 Lógica de Dificultades y Gráficas

- **Boulder**: Escala cromática ordenada de menor a mayor dificultad:
  `Amarillo (#FFD700)` → `Blanco (#E0E0E0)` → `Verde (#2ECC71)` → `Azul (#3498DB)` → `Rojo (#E74C3C)` → `Rosa (#FF69B4)` → `Marrón (#8B4513)`.
  Se almacena un `orden_dificultad` de 1 a 7 para que la pirámide de rendimiento siempre se dibuje en orden de dificultad real.
- **Cuerda**: Graduación francesa estándar de menor a mayor:
  `4` → `4+` → `5a` → `5b` → `5c` → `6a` → `6a+` → `6b` → `6b+` → `6c` → `6c+` → `7a` → `7a+` → `7b` (`orden_dificultad` de 1 a 14).
- **Semáforo de Salud L5-S1 & Pump**: Indicadores rápidos de volumen seguro, tensión en zona lumbar y alertas de congestión extrema en antebrazos ("como piedras").

---

## 🌐 Despliegue en Internet y Actualizaciones Continuas (CI/CD)

### Método 1: Git directo en tu servidor (El más rápido)
1. Sube tu código a un repositorio en **GitHub**:
2. En tu servidor (VPS, Raspberry Pi, PC de casa...):
   ```bash
   git clone https://github.com/TU_USUARIO/climbing-gym-tracker.git
   cd climbing-gym-tracker
   docker compose up -d --build
   ```
3. **Para actualizar tras hacer cambios:**
   ```bash
   git pull
   docker compose up -d --build
   ```
   *(Tus datos en `./data/entrenamientos.db` permanecen 100% intactos porque están en un volumen montado).*

### Método 2: Pipeline Automatizado con GitHub Actions & GHCR (Nivel Pro)
El proyecto incluye un flujo de integración continua en [`.github/workflows/docker-publish.yml`](.github/workflows/docker-publish.yml):
1. Cada vez que haces `git push` a tu repositorio, GitHub compila la imagen Docker automáticamente y la publica en **GitHub Container Registry** (`ghcr.io`).
2. En tu servidor en internet solo necesitas el archivo [`docker-compose.prod.yml`](docker-compose.prod.yml).
3. Con el servicio **Watchtower** incluido, el servidor detecta nuevas versiones en internet y **se actualiza solo automáticamente cada hora** sin que tengas que intervenir.


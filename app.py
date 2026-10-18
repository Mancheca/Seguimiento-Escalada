import os
import json
import sqlite3
import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# CONSTANTES Y CONFIGURACIONES
# ==========================================
DB_DIR = Path("data")
DB_FILE = DB_DIR / "entrenamientos.db"

COLORES_BOULDER = ["Amarillo", "Blanco", "Verde", "Azul", "Rojo", "Rosa", "Marrón"]
HEX_COLORES_BOULDER = {
    "Amarillo": "#FFD700",
    "Blanco": "#E0E0E0",
    "Verde": "#2ECC71",
    "Azul": "#3498DB",
    "Rojo": "#E74C3C",
    "Rosa": "#FF69B4",
    "Marrón": "#8B4513"
}

GRADOS_CUERDA = ["4", "4+", "5a", "5b", "5c", "6a", "6a+", "6b", "6b+", "6c", "6c+", "7a", "7a+", "7b"]

RESULTADOS_BOULDER = [
    "Flash (1er intento)",
    "Encadenado (Top)",
    "Proyecto (Intentos)",
    "Panel Volumen / ARC"
]

RESULTADOS_CUERDA = [
    "A vista",
    "Flash",
    "Encadenada (Punto Rojo)",
    "Top-Rope / Autoasegurador",
    "Con cuelgues (Proyecto)",
    "Serie 4x4 / ARC"
]

SENSACIONES_BOULDER = [
    "Destrepe controlado - Lumbar OK",
    "Caída suave - Lumbar OK",
    "Antebrazos cargados",
    "Tensión en dedos/poleas",
    "Molestia L5-S1 (Parar)"
]

SENSACIONES_CUERDA = [
    "Fluido - Buen reposo activo",
    "Pump moderado en antebrazos",
    "Antebrazos como piedras (Pump alto)",
    "Manos cansadas / Se abren",
    "Molestia L5-S1"
]

OPCIONES_LUMBAR_GYM = [
    "OK - Sin molestia",
    "Fatiga leve",
    "Tensión lumbar",
    "Molestia (Parar)"
]

# Guía visual y de técnica con foco en protección L5-S1
GUIA_EJERCICIOS = {
    "Deadbug Estático": {
        "image": "assets/exercises/deadbug_estatico.jpg",
        "focus": "Anti-extensión lumbar profunda y control de pelvis",
        "lumbar_tip": "Presiona activamente la zona lumbar contra la colchoneta. Imagina aplastar una uva con la espalda baja. Si notas que la zona lumbar se despega, no bajes tanto las piernas."
    },
    "Bird-Dog Controlado": {
        "image": "assets/exercises/bird_dog_controlado.jpg",
        "focus": "Estabilidad rotacional, multífidos y glúteos",
        "lumbar_tip": "Mantén la pelvis completamente paralela al suelo. No busques elevar mucho el pie o la mano para no arquear la columna; enfócate en alargarte hacia los extremos."
    },
    "Plancha Lateral": {
        "image": "assets/exercises/plancha_lateral.jpg",
        "focus": "Cuadrado lumbar y oblicuos (estabilidad lateral)",
        "lumbar_tip": "Alinea cabeza, hombros, cadera y tobillos. Empuja el suelo con el codo para no colapsar el hombro y mantén la cadera alta y fija."
    },
    "Jalón al Pecho": {
        "image": "assets/exercises/jalon_al_pecho.jpg",
        "focus": "Dorsal ancho y tracción vertical",
        "lumbar_tip": "Mantén el torso casi vertical (máximo 10-15° de inclinación). Tracciona desde los codos hacia abajo sin dar tirones lumbares hacia atrás."
    },
    "Dominadas Asistidas": {
        "image": "assets/exercises/dominadas_asistidas.jpg",
        "focus": "Tracción vertical y brazos",
        "lumbar_tip": "Mantén las piernas ligeramente adelantadas (posición hollow) para fijar el abdomen y evitar arquear la zona lumbar al subir."
    },
    "Jalón Estrecho": {
        "image": "assets/exercises/jalon_estrecho.jpg",
        "focus": "Dorsal medio, braquial y bíceps",
        "lumbar_tip": "Mantén el pecho erguido y las costillas hacia abajo. La estabilidad nace de los muslos bloqueados en los rodillos, no de compensar con la columna."
    },
    "Press Hombros Sentado Mancuernas": {
        "image": "assets/exercises/press_hombros_sentado_mancuernas.jpg",
        "focus": "Deltoides anterior y medio",
        "lumbar_tip": "Ajusta el respaldo entre 75° y 80° (no a 90°). Pega bien el sacro y la zona dorsal al respaldo; los pies firmes en el suelo evitan la hiperextensión lumbar."
    },
    "Press Máquina": {
        "image": "assets/exercises/press_maquina.jpg",
        "focus": "Empuje vertical guiado",
        "lumbar_tip": "Regula el asiento para que los agarres queden a la altura de las clavículas. El apoyo lumbar continuo en la máquina protege totalmente L5-S1."
    },
    "Press Half-Kneeling": {
        "image": "assets/exercises/press_half_kneeling.jpg",
        "focus": "Deltoides y estabilidad de core unilateral",
        "lumbar_tip": "Aprieta con fuerza el glúteo de la rodilla apoyada en el suelo; esto 'bloquea' la cadera en posición neutra e impide que la espalda baja se arquee."
    },
    "Remo Mancuerna Apoyado": {
        "image": "assets/exercises/remo_mancuerna_apoyado.jpg",
        "focus": "Dorsal ancho, romboides y retractores",
        "lumbar_tip": "Apoya una mano y rodilla sobre el banco plano. La columna debe quedar paralela al suelo, relajada pero recta, sin cargas axiales."
    },
    "Remo Polea Baja": {
        "image": "assets/exercises/remo_polea_baja.jpg",
        "focus": "Tracción horizontal y densidad de espalda",
        "lumbar_tip": "Mantén las rodillas ligeramente flexionadas. El tronco debe permanecer erguido y estable: evita balancearte hacia adelante y atrás con la espalda baja."
    },
    "Remo Pecho Apoyado": {
        "image": "assets/exercises/remo_pecho_apoyado.jpg",
        "focus": "Tracción horizontal con cero carga espinal",
        "lumbar_tip": "¡La mejor opción para discopatías! Al estar el pecho totalmente apoyado en el banco a 30-45°, la columna lumbar no sufre ninguna carga de compresión."
    },
    "Sentadilla Búlgara": {
        "image": "assets/exercises/sentadilla_bulgara.jpg",
        "focus": "Fuerza unilateral de cuádriceps y glúteo",
        "lumbar_tip": "Inclina levemente el torso hacia adelante en bloque (manteniendo la espalda neutra). Esto descarga los flexores de cadera y la zona lumbar."
    },
    "Zancada Atrás": {
        "image": "assets/exercises/zancada_atras.jpg",
        "focus": "Pierna unilateral con desaceleración suave",
        "lumbar_tip": "El paso hacia atrás es mucho más seguro para la cadera y rodillas que hacia adelante. Mantén el core firme y baja en vertical."
    },
    "Prensa Unilateral": {
        "image": "assets/exercises/prensa_unilateral.jpg",
        "focus": "Piernas sin presión axial en columna",
        "lumbar_tip": "Coloca el pie en la parte media-alta de la placa. No bajes tanto como para que el glúteo o sacro se despeguen del asiento."
    },
    "Goblet Squat": {
        "image": "assets/exercises/goblet_squat.jpg",
        "focus": "Sentadilla funcional segura",
        "lumbar_tip": "Sostén la mancuerna pegada al esternón: hace de contrapeso natural, facilitando que el torso baje recto sin flexionar la zona lumbar."
    },
    "Prensa Horizontal": {
        "image": "assets/exercises/prensa_horizontal.jpg",
        "focus": "Cuádriceps y glúteos con soporte guiado",
        "lumbar_tip": "Asegúrate de que la espalda baja permanezca bien pegada al respaldo durante todo el recorrido. Detén el descenso antes del retroceso pélvico."
    },
    "Sentadilla Fitball": {
        "image": "assets/exercises/sentadilla_fitball.jpg",
        "focus": "Readaptación motora de sentadilla",
        "lumbar_tip": "La pelota en la pared soporta el peso del torso y masajea la zona lumbar. Perfecta en días de sobrecarga para mantener movilidad sin riesgo."
    },
    "Extensión Banco 45º": {
        "image": "assets/exercises/extension_banco_45.jpg",
        "focus": "Isquiosurales, glúteos y erectores",
        "lumbar_tip": "La bisagra debe ser de CADERA, no lumbar. Sube solo hasta que el cuerpo forme una línea recta diagonal. NUNCA hiperextiendas hacia atrás."
    },
    "Puente Glúteos": {
        "image": "assets/exercises/puente_gluteos.jpg",
        "focus": "Extensión de cadera y activación de glúteo mayor",
        "lumbar_tip": "Empuja el suelo a través de los talones. Al llegar arriba, aprieta los glúteos y mantén las costillas bajas para no usar la espalda baja como bisagra."
    },
    "Patada Glúteo Polea": {
        "image": "assets/exercises/patada_gluteo_polea.jpg",
        "focus": "Glúteo aislado",
        "lumbar_tip": "Sujétate bien a la torre con el torso ligeramente inclinado. La pierna viaja hacia atrás por acción pura del glúteo; no arquees la espalda al patear."
    }
}

def obtener_info_ejercicio(nombre_ej):
    """
    Busca la información técnica y visual de un ejercicio con coincidencia inteligente:
    1. Coincidencia exacta
    2. Coincidencia por palabras clave (ej: 'Jalón neutro' -> 'Jalón al Pecho')
    3. Consejo lumbar general adaptado si es un ejercicio nuevo
    """
    if not nombre_ej:
        return None

    if nombre_ej in GUIA_EJERCICIOS:
        return GUIA_EJERCICIOS[nombre_ej]

    nom_lower = nombre_ej.lower()

    # Búsqueda por subcadenas en las claves del diccionario
    for k, v in GUIA_EJERCICIOS.items():
        if k.lower() in nom_lower or nom_lower in k.lower():
            return v

    # Patrones frecuentes de ejercicios
    if any(w in nom_lower for w in ["deadbug", "dead bug"]):
        return GUIA_EJERCICIOS.get("Deadbug Estático")
    if any(w in nom_lower for w in ["bird", "dog", "cuadrupedia", "superman"]):
        return GUIA_EJERCICIOS.get("Bird-Dog Controlado")
    if any(w in nom_lower for w in ["plancha", "plank", "side bridge"]):
        return GUIA_EJERCICIOS.get("Plancha Lateral")
    if any(w in nom_lower for w in ["jalón", "jalon", "pulldown", "lat pull"]):
        return GUIA_EJERCICIOS.get("Jalón al Pecho")
    if any(w in nom_lower for w in ["dominada", "pull-up", "chin-up"]):
        return GUIA_EJERCICIOS.get("Dominadas Asistidas")
    if any(w in nom_lower for w in ["remo", "row"]):
        return GUIA_EJERCICIOS.get("Remo Pecho Apoyado")
    if any(w in nom_lower for w in ["press", "militar", "overhead", "hombro"]):
        return GUIA_EJERCICIOS.get("Press Hombros Sentado Mancuernas")
    if any(w in nom_lower for w in ["búlgara", "bulgara", "split squat", "zancada", "lunge"]):
        return GUIA_EJERCICIOS.get("Sentadilla Búlgara")
    if any(w in nom_lower for w in ["prensa", "leg press"]):
        return GUIA_EJERCICIOS.get("Prensa Horizontal")
    if any(w in nom_lower for w in ["sentadilla", "squat"]):
        return GUIA_EJERCICIOS.get("Goblet Squat")
    if any(w in nom_lower for w in ["glúteo", "gluteo", "puente", "bridge", "thrust"]):
        return GUIA_EJERCICIOS.get("Puente Glúteos")
    if any(w in nom_lower for w in ["isquio", "femoral", "extension", "extensión"]):
        return GUIA_EJERCICIOS.get("Extensión Banco 45º")

    # Si es un ejercicio nuevo sin imagen precargada, dar guía de seguridad L5-S1
    return {
        "image": None,
        "focus": "Fuerza y acondicionamiento lumbar-friendly",
        "lumbar_tip": "Mantén la columna en posición neutra. Activa el 'bracing' abdominal (apretar el abdomen como si fueras a recibir un golpe) y frena el movimiento si notas cualquier tensión o molestia en L5-S1."
    }


# ==========================================
# CONFIGURACIÓN DE PÁGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Climbing & Gym Tracker (L5-S1)",
    page_icon="🧗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de CSS para UX móvil optimizada y modo oscuro
st.markdown("""
<style>
    /* Ocultar elementos innecesarios para parecer una app móvil nativa */
    #MainMenu, header, footer {
        visibility: hidden;
        height: 0;
        margin: 0;
        padding: 0;
    }

    /* Prevenir zoom no deseado al tocar inputs en iOS Safari */
    input, select, textarea, .stSelectbox, .stNumberInput {
        font-size: 16px !important;
    }

    /* Pestañas con scroll táctil suave en móviles */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        white-space: nowrap !important;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }

    /* Estilos móviles responsivos */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.8rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            padding-bottom: 3rem !important;
        }
        .stButton>button {
            width: 100% !important;
            font-size: 1.05rem !important;
            padding: 0.75rem !important;
            border-radius: 12px !important;
            touch-action: manipulation;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 0.9rem !important;
            border-radius: 8px;
        }
        .metric-card {
            padding: 10px 14px !important;
        }
        .metric-card .metric-value {
            font-size: 1.35rem !important;
        }
    }

    /* Acordeones de ejercicios táctiles */
    div[data-testid="stExpander"] {
        background-color: #161B26 !important;
        border: 1px solid #283142 !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        padding: 10px 14px !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #1E2533 !important;
    }

    /* Tarjetas y detalles visuales modo oscuro */
    .metric-card {
        background: #1A1F29;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-card h4 {
        margin: 0;
        font-size: 0.85rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
        color: #F7FAFC;
    }

    /* Badges de alerta de salud */
    .badge-ok {
        background-color: rgba(46, 204, 113, 0.2);
        color: #2ECC71;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-warning {
        background-color: rgba(243, 156, 18, 0.2);
        color: #F39C12;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-danger {
        background-color: rgba(231, 76, 60, 0.2);
        color: #E74C3C;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# GESTOR DE BASE DE DATOS (SQLite)
# ==========================================
def get_db_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros_gym (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo_sesion TEXT,
                bloque TEXT,
                ejercicio TEXT NOT NULL,
                serie INTEGER NOT NULL,
                reps_objetivo TEXT,
                reps_reales INTEGER,
                peso_kg REAL,
                rir INTEGER,
                notas_lumbar TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros_escalada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                modalidad TEXT NOT NULL,
                grado TEXT NOT NULL,
                orden_dificultad INTEGER NOT NULL,
                intentos INTEGER NOT NULL,
                resultado TEXT NOT NULL,
                sensacion_fisica TEXT,
                notas TEXT
            );
        """)
    conn.close()

# Inicializar BD al arrancar
init_db()

def apply_plotly_dark_theme(fig, title=None, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,31,41,0.7)",
        font=dict(color="#E2E8F0", family="sans-serif", size=12),
        margin=dict(l=15, r=15, t=40 if title else 25, b=25),
        height=height,
        title=dict(text=title, font=dict(size=14)) if title else None,
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)"
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    return fig

# ==========================================
# RUTINA BASE POST-VACACIONES (L5-S1) Y GESTIÓN DE CARGAS
# ==========================================
def obtener_ultimo_peso_ejercicio(nombre_ej, serie_num=None):
    """
    Recupera el último peso y repeticiones registradas para un ejercicio en SQLite.
    Permite pre-rellenar la rutina con los pesos reales previos para sobrecarga progresiva.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if serie_num is not None:
            cursor.execute("""
                SELECT peso_kg, reps_reales, fecha, rir
                FROM registros_gym
                WHERE ejercicio = ? AND serie = ?
                ORDER BY fecha DESC, id DESC
                LIMIT 1
            """, (nombre_ej, serie_num))
            r = cursor.fetchone()
            if r and r["peso_kg"] is not None:
                conn.close()
                return dict(r)

        cursor.execute("""
            SELECT peso_kg, reps_reales, fecha, rir
            FROM registros_gym
            WHERE ejercicio = ?
            ORDER BY fecha DESC, id DESC
            LIMIT 1
        """, (nombre_ej,))
        r = cursor.fetchone()
        conn.close()
        if r and r["peso_kg"] is not None:
            return dict(r)
    except Exception:
        pass
    return None

def generar_rutina_base_l5s1(alternativas_seleccionadas):
    """
    Genera la estructura de filas para el Bloque 1 (Activación) y Bloque 2 (Fuerza),
    pre-cargando automáticamente los últimos pesos registrados por el usuario.
    """
    filas = []

    # Bloque 1: Activación Lumbar (Cuidado L5-S1)
    b1_ejercicios = [
        {"nombre": "Deadbug Estático", "series": 3, "reps_obj": "6", "reps_reales": 6, "peso_kg": 0.0},
        {"nombre": "Bird-Dog Controlado", "series": 3, "reps_obj": "6", "reps_reales": 6, "peso_kg": 0.0},
        {"nombre": "Plancha Lateral", "series": 3, "reps_obj": "25s", "reps_reales": 25, "peso_kg": 0.0}
    ]
    for ej in b1_ejercicios:
        for s in range(1, ej["series"] + 1):
            filas.append({
                "bloque": "Bloque 1 (Activación Lumbar)",
                "ejercicio": ej["nombre"],
                "serie": s,
                "reps_objetivo": ej["reps_obj"],
                "reps_reales": ej["reps_reales"],
                "peso_kg": ej["peso_kg"],
                "rir": 2,
                "notas_lumbar": "OK - Sin molestia"
            })

    # Bloque 2: Fuerza con alternativas seguras y memoria de peso previo
    for cat, ej_nombre in alternativas_seleccionadas.items():
        for s in range(1, 4):  # 3 series estándar
            ult = obtener_ultimo_peso_ejercicio(ej_nombre, s)
            peso_previo = float(ult["peso_kg"]) if (ult and ult["peso_kg"] is not None) else 0.0
            reps_previas = int(ult["reps_reales"]) if (ult and ult["reps_reales"] is not None) else 10
            filas.append({
                "bloque": f"Bloque 2 ({cat})",
                "ejercicio": ej_nombre,
                "serie": s,
                "reps_objetivo": "8-10",
                "reps_reales": reps_previas,
                "peso_kg": peso_previo,
                "rir": 2,
                "notas_lumbar": "OK - Sin molestia"
            })

    return pd.DataFrame(filas)

def parsear_json_rutina(json_str):
    """
    Parsea el JSON según el esquema especificado, vinculando automáticamente
    los últimos pesos utilizados si el usuario ya tiene historial para ese ejercicio.
    """
    data = json.loads(json_str)
    fecha = data.get("fecha", str(datetime.date.today()))
    tipo_sesion = data.get("tipo_sesion", "Sesión Personalizada")
    ejercicios = data.get("ejercicios", [])

    filas = []
    for ej in ejercicios:
        bloque = ej.get("bloque", "Fuerza")
        nombre = ej.get("nombre", "Ejercicio")
        series = int(ej.get("series", 3))
        reps_obj = str(ej.get("reps_obj", "10"))
        
        # Intentar deducir reps_reales iniciales
        reps_reales = 0
        try:
            reps_reales = int(reps_obj)
        except ValueError:
            reps_reales = 10
            
        peso_json = float(ej.get("peso_kg", 0.0))

        # Soporte para que la IA proporcione imagen o consejo personalizado en el JSON
        img_custom = ej.get("imagen_url") or ej.get("imagen") or ej.get("image")
        tip_custom = ej.get("lumbar_tip") or ej.get("consejo_lumbar") or ej.get("tip")
        focus_custom = ej.get("focus") or ej.get("enfoque")
        if img_custom or tip_custom or focus_custom:
            info_prev = GUIA_EJERCICIOS.get(nombre, {})
            GUIA_EJERCICIOS[nombre] = {
                "image": img_custom or info_prev.get("image"),
                "diagram": img_custom or info_prev.get("diagram"),
                "focus": focus_custom or info_prev.get("focus", "Fuerza y acondicionamiento"),
                "lumbar_tip": tip_custom or info_prev.get("lumbar_tip", "Mantener pelvis neutra y activar el core.")
            }

        for s in range(1, series + 1):
            # Comprobar si el usuario ya tiene un historial previo registrado para este ejercicio
            ult = obtener_ultimo_peso_ejercicio(nombre, s)
            peso_final = float(ult["peso_kg"]) if (ult and ult["peso_kg"] > 0) else peso_json
            reps_final = int(ult["reps_reales"]) if (ult and ult["reps_reales"] > 0) else reps_reales

            filas.append({
                "bloque": bloque,
                "ejercicio": nombre,
                "serie": s,
                "reps_objetivo": reps_obj,
                "reps_reales": reps_final,
                "peso_kg": peso_final,
                "rir": 2,
                "notas_lumbar": "OK - Sin molestia"
            })

    df = pd.DataFrame(filas)
    return fecha, tipo_sesion, df

APP_VERSION = "v1.01"

# ==========================================
# HEADER DE LA APP
# ==========================================
st.markdown(f"### 🧗 Climbing & Gym Tracker `{APP_VERSION}`")
st.caption("🛡️ **L5-S1 Edition** | Control de cargas, dolor lumbar y progresión en roca/resina")

# Estado de navegación: por defecto muestra el menú de actividades
if "seccion_activa" not in st.session_state:
    st.session_state["seccion_activa"] = "menu"

seccion = st.session_state["seccion_activa"]

# PANTALLA PRINCIPAL: Selector de Actividades (Menú)
if seccion == "menu":
    st.markdown("##### 🎯 Elige una actividad:")
    
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("🏋️ Gimnasio", use_container_width=True, type="primary"):
            st.session_state["seccion_activa"] = "gym"
            st.rerun()
    with c_nav2:
        if st.button("🧗 Rocódromo", use_container_width=True, type="primary"):
            st.session_state["seccion_activa"] = "climb"
            st.rerun()

    c_nav3, c_nav4 = st.columns(2)
    with c_nav3:
        if st.button("📈 Estadísticas", use_container_width=True, type="secondary"):
            st.session_state["seccion_activa"] = "stats"
            st.rerun()
    with c_nav4:
        if st.button("🗂️ Historial", use_container_width=True, type="secondary"):
            st.session_state["seccion_activa"] = "history"
            st.rerun()

    # Botón de ayuda para pedir rutinas a Gemini
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    if st.button("💡 ¿Cómo pedir una nueva rutina a Gemini?", use_container_width=True):
        st.session_state["seccion_activa"] = "help_gemini"
        st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.caption("💡 Todo adaptado a móvil. Entra en tu sesión para registrar datos sin scroll vertical innecesario.")

else:
    # Barra de navegación interior: Botón para volver al selector de actividades
    c_back, c_space = st.columns([1.2, 1])
    with c_back:
        if st.button("⬅️ Cambiar de Actividad", use_container_width=True):
            st.session_state["seccion_activa"] = "menu"
            st.rerun()
    
    st.markdown("<div style='border-top: 1px solid #283142; margin-top: 4px; margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 1: 🏋️ GIMNASIO
# ==========================================
if seccion == "gym":
    rutina_cargada = ("gym_editor_df" in st.session_state and not st.session_state["gym_editor_df"].empty)

    # 1. PANTALLA DE CARGA (Solo visible si NO hay rutina cargada)
    if not rutina_cargada:
        st.markdown("#### 🏋️ Cargar Rutina de Gimnasio")
        st.caption("Selecciona tu rutina base o pega un JSON generado por IA para comenzar.")

        col_opt1, col_opt2 = st.columns([1, 1])

        with col_opt1:
            with st.expander("⚡ Plantilla Base Post-Vacaciones (L5-S1)", expanded=True):
                st.write("**Selector de Alternativas de Fuerza (Bloque 2):**")
                
                alt_tracc_vert = st.selectbox(
                    "1. Tracción Vertical:",
                    ["Jalón al Pecho", "Dominadas Asistidas", "Jalón Estrecho"],
                    index=0
                )
                alt_emp_vert = st.selectbox(
                    "2. Empuje Vertical:",
                    ["Press Hombros Sentado Mancuernas", "Press Máquina", "Press Half-Kneeling"],
                    index=0
                )
                alt_tracc_horiz = st.selectbox(
                    "3. Tracción Horizontal:",
                    ["Remo Mancuerna Apoyado", "Remo Polea Baja", "Remo Pecho Apoyado"],
                    index=0
                )
                alt_pierna_uni = st.selectbox(
                    "4. Pierna Unilateral:",
                    ["Sentadilla Búlgara", "Zancada Atrás", "Prensa Unilateral"],
                    index=0
                )
                alt_pierna_base = st.selectbox(
                    "5. Pierna Base:",
                    ["Goblet Squat", "Prensa Horizontal", "Sentadilla Fitball"],
                    index=0
                )
                alt_cadena_post = st.selectbox(
                    "6. Cadena Posterior:",
                    ["Extensión Banco 45º", "Puente Glúteos", "Patada Glúteo Polea"],
                    index=0
                )

                if st.button("🚀 Cargar Rutina Base Post-Vacaciones", use_container_width=True, type="primary"):
                    seleccionadas = {
                        "Tracción Vertical": alt_tracc_vert,
                        "Empuje Vertical": alt_emp_vert,
                        "Tracción Horizontal": alt_tracc_horiz,
                        "Pierna Unilateral": alt_pierna_uni,
                        "Pierna Base": alt_pierna_base,
                        "Cadena Posterior": alt_cadena_post
                    }
                    df_base = generar_rutina_base_l5s1(seleccionadas)
                    st.session_state["gym_fecha"] = str(datetime.date.today())
                    st.session_state["gym_tipo_sesion"] = "Rutina Base Post-Vacaciones (L5-S1)"
                    st.session_state["gym_editor_df"] = df_base
                    st.session_state["gym_rutina_id"] = st.session_state.get("gym_rutina_id", 0) + 1
                    st.rerun()

        with col_opt2:
            with st.expander("🤖 Importador JSON (Generado por IA)", expanded=False):
                json_ejemplo = json.dumps({
                    "fecha": str(datetime.date.today()),
                    "tipo_sesion": "Fuerza Lumbar-Friendly",
                    "ejercicios": [
                        {"bloque": "1. Activación", "nombre": "Deadbug Estático", "series": 3, "reps_obj": "6", "peso_kg": 0},
                        {"bloque": "2. Fuerza", "nombre": "Jalón al Pecho", "series": 3, "reps_obj": "10", "peso_kg": 45}
                    ]
                }, indent=2, ensure_ascii=False)

                json_input = st.text_area(
                    "Pega el JSON aquí:",
                    placeholder=json_ejemplo,
                    height=180
                )

                if st.button("📥 Importar JSON a la Sesión", use_container_width=True):
                    if json_input.strip():
                        try:
                            f_json, t_json, df_json = parsear_json_rutina(json_input)
                            st.session_state["gym_fecha"] = f_json
                            st.session_state["gym_tipo_sesion"] = t_json
                            st.session_state["gym_editor_df"] = df_json
                            st.session_state["gym_rutina_id"] = st.session_state.get("gym_rutina_id", 0) + 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al procesar JSON: {str(e)}")
                    else:
                        st.warning("Pega un JSON válido antes de importar.")

    # 2. PANTALLA DE ENTRENAMIENTO (Solo visible cuando la rutina ya está cargada)
    else:
        col_hdr_l, col_hdr_r = st.columns([2, 1])
        with col_hdr_l:
            st.markdown(f"#### 🏋️ {st.session_state.get('gym_tipo_sesion', 'Rutina de Gimnasio')}")
        with col_hdr_r:
            if st.button("🔄 Cambiar Rutina", use_container_width=True):
                del st.session_state["gym_editor_df"]
                st.rerun()

        c1, c2 = st.columns([1, 2])
        with c1:
            fecha_sesion = st.date_input(
                "📅 Fecha de la sesión",
                value=datetime.datetime.strptime(st.session_state.get("gym_fecha", str(datetime.date.today())), "%Y-%m-%d").date()
            )
        with c2:
            tipo_sesion = st.text_input(
                "🏷️ Nombre de la sesión",
                value=st.session_state.get("gym_tipo_sesion", "Entrenamiento Gimnasio")
            )

        # Selector de vista para garantizar adaptación móvil perfecta
        st.markdown("##### 📝 Registro de Series")
        modo_vista = st.radio(
            "Formato de Entrada:",
            ["📱 Tarjetas Móviles (Recomendado)", "💻 Hoja de Cálculo"],
            horizontal=True,
            index=0,
            key="gym_modo_vista"
        )

        rutina_id = st.session_state.get("gym_rutina_id", 0)
        df_sesion = st.session_state["gym_editor_df"]
        edited_df = None

        if modo_vista == "📱 Tarjetas Móviles (Recomendado)":
            st.caption("Ajusta las series ejercicio por ejercicio. Todo visible en tu smartphone sin scroll lateral.")
            
            # Obtener lista ordenada y única de ejercicios
            ejercicios_unicos = []
            for _, r in df_sesion.iterrows():
                par = (r["bloque"], r["ejercicio"])
                if par not in ejercicios_unicos:
                    ejercicios_unicos.append(par)

            for b_nom, ej_nom in ejercicios_unicos:
                filas_ej = df_sesion[(df_sesion["bloque"] == b_nom) & (df_sesion["ejercicio"] == ej_nom)]
                with st.expander(f"🏋️ {ej_nom}  ·  {len(filas_ej)} series ({b_nom})", expanded=False):
                    # Guía visual y de técnica con popover inteligente
                    info_ej = obtener_info_ejercicio(ej_nom)
                    if info_ej:
                        with st.popover("ℹ️ Ver imagen y técnica (L5-S1)", use_container_width=True):
                            st.markdown(f"##### 📋 {ej_nom}")
                            img_path = info_ej.get("image")
                            if img_path and os.path.exists(img_path):
                                st.image(img_path, use_container_width=True)
                            elif "diagram" in info_ej:
                                st.image(info_ej["diagram"], use_container_width=True)
                            st.info(f"🛡️ **Protección Lumbar L5-S1:**\n\n{info_ej['lumbar_tip']}")

                    for idx, row in filas_ej.iterrows():
                        st.markdown(f"<div style='border-top: 1px solid #283142; margin-top: 6px; padding-top: 6px;'></div>", unsafe_allow_html=True)
                        
                        # Indicador de peso histórico para sobrecarga progresiva
                        ult_info = obtener_ultimo_peso_ejercicio(ej_nom, row['serie'])
                        ref_badge = ""
                        if ult_info and ult_info.get("peso_kg", 0) > 0:
                            ref_badge = f"&nbsp;<span style='color: #63B3ED; font-size: 0.78rem; background: rgba(99,179,237,0.12); padding: 2px 7px; border-radius: 4px; font-weight: 500;'>⚡ Última vez: {ult_info['peso_kg']:.1f} kg × {ult_info['reps_reales']} ({ult_info['fecha']})</span>"

                        st.markdown(f"<span style='color: #2ECC71; font-weight: 700; font-size: 0.95rem;'>Serie {row['serie']}</span> <span style='color: #A0AEC0; font-size: 0.85rem;'>(Obj: {row['reps_objetivo']})</span>{ref_badge}", unsafe_allow_html=True)

                        c_rep, c_kg, c_rir = st.columns(3)
                        with c_rep:
                            st.number_input(
                                "Reps",
                                min_value=0,
                                max_value=300,
                                value=int(row["reps_reales"]),
                                step=1,
                                key=f"reps_{rutina_id}_{idx}"
                            )
                        with c_kg:
                            st.number_input(
                                "Kg",
                                min_value=0.0,
                                max_value=500.0,
                                value=float(row["peso_kg"]),
                                step=0.5,
                                format="%.1f",
                                key=f"peso_{rutina_id}_{idx}"
                            )
                        with c_rir:
                            st.number_input(
                                "RIR",
                                min_value=0,
                                max_value=5,
                                value=int(row["rir"]),
                                step=1,
                                key=f"rir_{rutina_id}_{idx}",
                                help="Repeticiones en Reserva"
                            )

                        idx_lumbar = OPCIONES_LUMBAR_GYM.index(row["notas_lumbar"]) if row["notas_lumbar"] in OPCIONES_LUMBAR_GYM else 0
                        st.selectbox(
                            "🛡️ Control Lumbar L5-S1",
                            options=OPCIONES_LUMBAR_GYM,
                            index=idx_lumbar,
                            key=f"lumbar_{rutina_id}_{idx}"
                        )
        else:
            st.caption("Ajusta reps reales, peso en kg, RIR (reps en reserva) y vigila el estado lumbar.")
            column_config = {
                "bloque": st.column_config.TextColumn("Bloque", disabled=True),
                "ejercicio": st.column_config.TextColumn("Ejercicio", disabled=True),
                "serie": st.column_config.NumberColumn("Serie", disabled=True, format="%d"),
                "reps_objetivo": st.column_config.TextColumn("Obj.", disabled=True),
                "reps_reales": st.column_config.NumberColumn("Reps Reales", min_value=0, step=1, required=True),
                "peso_kg": st.column_config.NumberColumn("Peso (kg)", min_value=0.0, step=0.5, format="%.1f kg", required=True),
                "rir": st.column_config.NumberColumn("RIR", min_value=0, max_value=5, step=1, help="Repeticiones en Reserva"),
                "notas_lumbar": st.column_config.SelectboxColumn(
                    "Control Lumbar L5-S1",
                    options=OPCIONES_LUMBAR_GYM,
                    required=True,
                    help="Elige tu nivel de confort lumbar para esta serie"
                )
            }

            edited_df = st.data_editor(
                df_sesion,
                column_config=column_config,
                use_container_width=True,
                num_rows="dynamic",
                hide_index=True,
                key=f"gym_live_editor_{rutina_id}"
            )

        col_save, col_clear = st.columns([3, 1])
        with col_save:
            if st.button("💾 Guardar Sesión Completa en Base de Datos", type="primary", use_container_width=True):
                try:
                    filas_a_guardar = []
                    if modo_vista == "📱 Tarjetas Móviles (Recomendado)":
                        for idx, row in df_sesion.iterrows():
                            r_reales = st.session_state.get(f"reps_{rutina_id}_{idx}", row["reps_reales"])
                            p_kg = st.session_state.get(f"peso_{rutina_id}_{idx}", row["peso_kg"])
                            r_rir = st.session_state.get(f"rir_{rutina_id}_{idx}", row["rir"])
                            n_lumbar = st.session_state.get(f"lumbar_{rutina_id}_{idx}", row["notas_lumbar"])
                            filas_a_guardar.append({
                                "bloque": row.get("bloque", ""),
                                "ejercicio": row.get("ejercicio", ""),
                                "serie": int(row.get("serie", 1)),
                                "reps_objetivo": str(row.get("reps_objetivo", "")),
                                "reps_reales": int(r_reales),
                                "peso_kg": float(p_kg),
                                "rir": int(r_rir),
                                "notas_lumbar": str(n_lumbar)
                            })
                        st.session_state["gym_editor_df"] = pd.DataFrame(filas_a_guardar)
                    else:
                        for _, row in edited_df.iterrows():
                            filas_a_guardar.append({
                                "bloque": row.get("bloque", ""),
                                "ejercicio": row.get("ejercicio", ""),
                                "serie": int(row.get("serie", 1)),
                                "reps_objetivo": str(row.get("reps_objetivo", "")),
                                "reps_reales": int(row.get("reps_reales", 0)),
                                "peso_kg": float(row.get("peso_kg", 0.0)),
                                "rir": int(row.get("rir", 0)),
                                "notas_lumbar": str(row.get("notas_lumbar", "OK - Sin molestia"))
                            })
                        st.session_state["gym_editor_df"] = edited_df

                    conn = get_db_connection()
                    with conn:
                        for item in filas_a_guardar:
                            conn.execute("""
                                INSERT INTO registros_gym 
                                (fecha, tipo_sesion, bloque, ejercicio, serie, reps_objetivo, reps_reales, peso_kg, rir, notas_lumbar)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                str(fecha_sesion),
                                str(tipo_sesion),
                                item["bloque"],
                                item["ejercicio"],
                                item["serie"],
                                item["reps_objetivo"],
                                item["reps_reales"],
                                item["peso_kg"],
                                item["rir"],
                                item["notas_lumbar"]
                            ))
                    conn.close()
                    st.success("✅ ¡Sesión guardada exitosamente en la base de datos!")
                    
                    alertas = [item for item in filas_a_guardar if item["notas_lumbar"] in ["Tensión lumbar", "Molestia (Parar)"]]
                    if alertas:
                        st.warning(f"⚠️ Atención: Se han registrado {len(alertas)} serie(s) con tensión o molestia lumbar. Recuerda aplicar calor local, movilidad suave y reposar la zona.")
                except Exception as e:
                    st.error(f"Error al guardar sesión: {str(e)}")

        with col_clear:
            if st.button("🗑️ Descartar", use_container_width=True):
                del st.session_state["gym_editor_df"]
                st.rerun()

# ==========================================
# SECCIÓN 2: 🧗 ROCÓDROMO
# ==========================================
elif seccion == "climb":
    st.markdown("#### 🧗 Registro Rápido en Rocódromo")
    st.caption("Añade cada vía o bloque sobre la marcha con control de impacto y L5-S1.")

    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        fecha_climb = st.date_input("📅 Fecha", value=datetime.date.today(), key="climb_date_picker")
    with col_m2:
        modalidad = st.radio("🧗 Modalidad", ["Boulder", "Cuerda"], horizontal=True, key="climb_modalidad")

    # Función auxiliar para guardar registros de escalada
    def registrar_escalada(fecha_val, mod_val, grd_val, orden_val, ints_val, res_val, sens_val, nots_val):
        try:
            conn_climb = get_db_connection()
            with conn_climb:
                conn_climb.execute("""
                    INSERT INTO registros_escalada 
                    (fecha, modalidad, grado, orden_dificultad, intentos, resultado, sensacion_fisica, notas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(fecha_val),
                    mod_val,
                    grd_val,
                    int(orden_val),
                    int(ints_val),
                    res_val,
                    sens_val,
                    str(nots_val)
                ))
            conn_climb.close()
            st.success(f"✅ ¡{mod_val} '{grd_val}' ({res_val}) registrado con éxito!")
            if "Molestia L5-S1" in sens_val:
                st.error("🚨 ALERTA L5-S1: Has reportado molestia lumbar. Evita caídas al colchón y considera terminar la sesión de hoy.")
            st.rerun()
        except Exception as e_reg:
            st.error(f"Error al registrar: {str(e_reg)}")

    # Selector de formato de entrada
    st.markdown("##### 📝 Registro de Pegues")
    modo_entrada_climb = st.radio(
        "Formato de Entrada:",
        ["📱 Tarjetas de Grados (Recomendado)", "📝 Formulario Simple"],
        horizontal=True,
        index=0,
        key="climb_modo_entrada"
    )

    EMOJI_COLORES_BOULDER = {
        "Amarillo": "🟡",
        "Blanco": "⚪",
        "Verde": "🟢",
        "Azul": "🔵",
        "Rojo": "🔴",
        "Rosa": "🌸",
        "Marrón": "🟤"
    }

    if modo_entrada_climb == "📱 Tarjetas de Grados (Recomendado)":
        st.caption("Toca en el color o grado que acabas de escalar para desplegar la introducción de datos.")
        
        if modalidad == "Boulder":
            for idx_b, color_nom in enumerate(COLORES_BOULDER, start=1):
                emoji_c = EMOJI_COLORES_BOULDER.get(color_nom, "🧗")
                with st.expander(f"{emoji_c} Bloque {color_nom}  ·  (Nivel {idx_b})", expanded=False):
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        ints_b = st.number_input("🔁 Pegues / Intentos:", min_value=1, max_value=50, value=1, step=1, key=f"int_b_{color_nom}")
                        res_b = st.selectbox("🎯 Resultado / Estilo:", RESULTADOS_BOULDER, index=1, key=f"res_b_{color_nom}")
                    with col_b2:
                        sens_b = st.selectbox("🛡️ Control Físico / L5-S1:", SENSACIONES_BOULDER, index=0, key=f"sens_b_{color_nom}")
                        not_b = st.text_input("💬 Notas (opcional):", placeholder="Ej: desplome con talón", key=f"not_b_{color_nom}")

                    if st.button(f"➕ Registrar Bloque {color_nom}", key=f"btn_b_{color_nom}", type="primary", use_container_width=True):
                        registrar_escalada(fecha_climb, "Boulder", color_nom, idx_b, ints_b, res_b, sens_b, not_b)
        else:
            for idx_c, grado_nom in enumerate(GRADOS_CUERDA, start=1):
                with st.expander(f"🧗 Vía Grado {grado_nom}  ·  (Dificultad {idx_c})", expanded=False):
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        ints_c = st.number_input("🔁 Pegues / Intentos:", min_value=1, max_value=50, value=1, step=1, key=f"int_c_{grado_nom}")
                        res_c = st.selectbox("🎯 Resultado / Estilo:", RESULTADOS_CUERDA, index=2, key=f"res_c_{grado_nom}")
                    with col_c2:
                        sens_c = st.selectbox("🛡️ Control Físico / L5-S1:", SENSACIONES_CUERDA, index=0, key=f"sens_c_{grado_nom}")
                        not_c = st.text_input("💬 Notas (opcional):", placeholder="Ej: reposo en chapa 3", key=f"not_c_{grado_nom}")

                    if st.button(f"➕ Registrar Vía {grado_nom}", key=f"btn_c_{grado_nom}", type="primary", use_container_width=True):
                        registrar_escalada(fecha_climb, "Cuerda", grado_nom, idx_c, ints_c, res_c, sens_c, not_c)
    else:
        # Formulario estándar
        with st.form("form_escalada", clear_on_submit=True):
            col_f1, col_f2 = st.columns([1, 1])
            if modalidad == "Boulder":
                with col_f1:
                    grado = st.selectbox("🎨 Color / Grado Boulder:", COLORES_BOULDER, index=2)
                    orden_dificultad = COLORES_BOULDER.index(grado) + 1
                    intentos = st.number_input("🔁 Pegues / Intentos:", min_value=1, max_value=50, value=1, step=1)
                with col_f2:
                    resultado = st.selectbox("🎯 Resultado / Estilo:", RESULTADOS_BOULDER, index=1)
                    sensacion_fisica = st.selectbox("🛡️ Control Físico / L5-S1:", SENSACIONES_BOULDER, index=0)
            else:
                with col_f1:
                    grado = st.selectbox("🔢 Grado Francés:", GRADOS_CUERDA, index=5)
                    orden_dificultad = GRADOS_CUERDA.index(grado) + 1
                    intentos = st.number_input("🔁 Pegues / Intentos:", min_value=1, max_value=50, value=1, step=1)
                with col_f2:
                    resultado = st.selectbox("🎯 Resultado / Estilo:", RESULTADOS_CUERDA, index=2)
                    sensacion_fisica = st.selectbox("🛡️ Control Físico / L5-S1:", SENSACIONES_CUERDA, index=0)

            notas_climb = st.text_input("💬 Notas opcionales:", placeholder="Ej: vía con crux al final")
            submitted = st.form_submit_button("➕ Registrar Pegue / Vía", type="primary", use_container_width=True)

            if submitted:
                registrar_escalada(fecha_climb, modalidad, grado, orden_dificultad, intentos, resultado, sensacion_fisica, notas_climb)

    st.markdown("---")

    # Resumen de la sesión del día actual
    conn = get_db_connection()
    df_hoy = pd.read_sql_query(
        "SELECT id, modalidad, grado, orden_dificultad, intentos, resultado, sensacion_fisica, notas FROM registros_escalada WHERE fecha = ? ORDER BY id DESC",
        conn,
        params=(str(fecha_climb),)
    )
    conn.close()

    col_res_tit, col_res_opt = st.columns([1.5, 1])
    with col_res_tit:
        st.markdown(f"##### 📋 Resumen de la Sesión ({fecha_climb})")
    with col_res_opt:
        modo_resumen_climb = st.radio(
            "Vista:",
            ["📱 Tarjetas", "💻 Tabla"],
            horizontal=True,
            index=0,
            key="climb_modo_resumen",
            label_visibility="collapsed"
        )

    if not df_hoy.empty:
        # Métricas en cuadrícula 2x2 para smartphone
        m1, m2 = st.columns(2)
        total_vias = len(df_hoy)
        total_intentos = int(df_hoy["intentos"].sum())
        tops = len(df_hoy[df_hoy["resultado"].str.contains("Flash|Top|Encadenad", case=False, na=False)])
        alertas_l5 = len(df_hoy[df_hoy["sensacion_fisica"].str.contains("Molestia L5-S1", case=False, na=False)])

        with m1:
            st.markdown(f"""<div class="metric-card"><h4>Pegues Totales</h4><div class="metric-value">{total_vias}</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card"><h4>Encadenes</h4><div class="metric-value">{tops}</div></div>""", unsafe_allow_html=True)

        m3, m4 = st.columns(2)
        with m3:
            st.markdown(f"""<div class="metric-card"><h4>Intentos Acum.</h4><div class="metric-value">{total_intentos}</div></div>""", unsafe_allow_html=True)
        with m4:
            color_badge = "badge-danger" if alertas_l5 > 0 else "badge-ok"
            st.markdown(f"""<div class="metric-card"><h4>Estado L5-S1</h4><div class="metric-value"><span class="{color_badge}">{"⚠️ Molestia" if alertas_l5 > 0 else "OK"}</span></div></div>""", unsafe_allow_html=True)

        if modo_resumen_climb == "📱 Tarjetas":
            for _, r_climb in df_hoy.iterrows():
                id_item = r_climb["id"]
                mod_item = r_climb["modalidad"]
                grd_item = r_climb["grado"]
                res_item = r_climb["resultado"]
                int_item = r_climb["intentos"]
                sen_item = r_climb["sensacion_fisica"]
                not_item = r_climb.get("notas", "")

                color_hex = HEX_COLORES_BOULDER.get(grd_item, "#3498DB") if mod_item == "Boulder" else "#2ECC71"
                icono_item = "🧗 Boulder" if mod_item == "Boulder" else "🧗 Cuerda"
                pegues_str = f"{int_item} pegue" if int_item == 1 else f"{int_item} pegues"

                with st.expander(f"{icono_item}: {grd_item} · {res_item} ({pegues_str})", expanded=False):
                    c_det1, c_det2 = st.columns(2)
                    with c_det1:
                        st.markdown(f"**Modalidad:** {mod_item}")
                        st.markdown(f"**Grado / Color:** <span style='color:{color_hex}; font-weight:bold;'>● {grd_item}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Intentos:** {int_item}")
                    with c_det2:
                        st.markdown(f"**Resultado:** {res_item}")
                        badge_cls = "badge-danger" if "Molestia" in sen_item else ("badge-warning" if "Piedras" in sen_item or "cargados" in sen_item else "badge-ok")
                        st.markdown(f"**Sensación:** <span class='{badge_cls}'>{sen_item}</span>", unsafe_allow_html=True)

                    if not_item and str(not_item).strip():
                        st.markdown(f"**Notas:** *{not_item}*")

                    if st.button("🗑️ Eliminar este pegue", key=f"del_pegue_{id_item}", use_container_width=True):
                        try:
                            conn_d = get_db_connection()
                            with conn_d:
                                conn_d.execute("DELETE FROM registros_escalada WHERE id = ?", (int(id_item),))
                            conn_d.close()
                            st.success("Pegue eliminado.")
                            st.rerun()
                        except Exception as e_del:
                            st.error(f"Error al eliminar: {str(e_del)}")
        else:
            st.dataframe(
                df_hoy.drop(columns=["orden_dificultad"]),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info(f"No hay bloques ni vías registradas para el día {fecha_climb}.")

# ==========================================
# SECCIÓN 3: 📈 ESTADÍSTICAS Y GRÁFICAS
# ==========================================
elif seccion == "stats":
    st.markdown("#### 📈 Panel de Estadísticas y Progresión")

    conn = get_db_connection()
    df_gym_all = pd.read_sql_query("SELECT * FROM registros_gym ORDER BY fecha ASC", conn)
    df_climb_all = pd.read_sql_query("SELECT * FROM registros_escalada ORDER BY fecha ASC, orden_dificultad ASC", conn)
    conn.close()

    # --- Resumen de Salud Lumbar y Pump ---
    st.markdown("##### 🛡️ Monitor de Salud Lumbar y Fatiga de Antebrazos")
    
    # Contabilizar alertas
    alertas_lumbar_gym = 0
    if not df_gym_all.empty:
        alertas_lumbar_gym = len(df_gym_all[df_gym_all["notas_lumbar"].isin(["Tensión lumbar", "Molestia (Parar)"])])

    alertas_lumbar_climb = 0
    alertas_pump_climb = 0
    if not df_climb_all.empty:
        alertas_lumbar_climb = len(df_climb_all[df_climb_all["sensacion_fisica"].str.contains("Molestia L5-S1", case=False, na=False)])
        alertas_pump_climb = len(df_climb_all[df_climb_all["sensacion_fisica"].str.contains("Antebrazos como piedras", case=False, na=False)])

    total_alertas_l5 = alertas_lumbar_gym + alertas_lumbar_climb

    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Alertas L5-S1 Totales</h4>
            <div class="metric-value">
                <span class="{'badge-danger' if total_alertas_l5 > 0 else 'badge-ok'}">{total_alertas_l5}</span>
            </div>
            <small style="color: #718096;">Gym: {alertas_lumbar_gym} | Escalada: {alertas_lumbar_climb}</small>
        </div>
        """, unsafe_allow_html=True)

    with c_s2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Pump Extremo (Piedras)</h4>
            <div class="metric-value">
                <span class="{'badge-warning' if alertas_pump_climb > 0 else 'badge-ok'}">{alertas_pump_climb}</span>
            </div>
            <small style="color: #718096;">Sesiones con fatiga máxima</small>
        </div>
        """, unsafe_allow_html=True)

    with c_s3:
        sesiones_seguras = (len(df_gym_all) + len(df_climb_all)) - (total_alertas_l5 + alertas_pump_climb)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Series/Vías Sin Dolor</h4>
            <div class="metric-value">
                <span class="badge-ok">{max(0, sesiones_seguras)}</span>
            </div>
            <small style="color: #718096;">Ejecución limpia</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- SECCIÓN GIMNASIO ---
    st.markdown("##### 🏋️ Evolución en Gimnasio")
    if not df_gym_all.empty:
        ejercicios_disponibles = sorted(df_gym_all["ejercicio"].unique().tolist())
        ej_seleccionado = st.selectbox("Selecciona Ejercicio para Analizar:", ejercicios_disponibles)

        df_ej = df_gym_all[df_gym_all["ejercicio"] == ej_seleccionado].copy()

        # Gráfica 1: Peso Máximo por fecha
        df_max_peso = df_ej.groupby("fecha")["peso_kg"].max().reset_index()
        fig_peso = px.line(
            df_max_peso,
            x="fecha",
            y="peso_kg",
            markers=True,
            title=f"Evolución Peso Máximo (kg) - {ej_seleccionado}",
            labels={"fecha": "Fecha", "peso_kg": "Peso Máximo (kg)"}
        )
        fig_peso.update_traces(
            line=dict(color="#2ECC71", width=3),
            marker=dict(size=8, color="#2ECC71", symbol="circle")
        )
        apply_plotly_dark_theme(fig_peso)
        st.plotly_chart(fig_peso, use_container_width=True)

        # Gráfica 2: Volumen Total por sesión (peso x reps)
        df_ej["volumen"] = df_ej["peso_kg"] * df_ej["reps_reales"]
        df_volumen = df_ej.groupby("fecha")["volumen"].sum().reset_index()
        fig_vol = px.bar(
            df_volumen,
            x="fecha",
            y="volumen",
            title=f"Volumen Total por Sesión (Peso x Reps) - {ej_seleccionado}",
            labels={"fecha": "Fecha", "volumen": "Volumen (kg)"}
        )
        fig_vol.update_traces(marker_color="#3498DB")
        apply_plotly_dark_theme(fig_vol)
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("Aún no hay registros de gimnasio para mostrar gráficas.")

    st.markdown("---")

    # --- SECCIÓN ROCÓDROMO ---
    st.markdown("##### 🧗 Rendimiento en Escalada")

    tab_g_boulder, tab_g_cuerda = st.tabs(["🧗 Gráfica Boulder (Pirámide de Colores)", "🧗 Gráfica Cuerda (Grados Franceses)"])

    with tab_g_boulder:
        df_boulder = df_climb_all[df_climb_all["modalidad"] == "Boulder"].copy()
        if not df_boulder.empty:
            # Conteo de bloques ordenados estrictamente por COLORES_BOULDER
            boulder_counts = df_boulder["grado"].value_counts().reindex(COLORES_BOULDER, fill_value=0).reset_index()
            boulder_counts.columns = ["Color", "Cantidad"]

            # Asignar los colores reales
            bar_colors = [HEX_COLORES_BOULDER.get(c, "#888888") for c in boulder_counts["Color"]]

            fig_boulder = go.Figure(
                data=[
                    go.Bar(
                        x=boulder_counts["Color"],
                        y=boulder_counts["Cantidad"],
                        marker=dict(
                            color=bar_colors,
                            line=dict(color="#FFFFFF", width=1)
                        ),
                        text=boulder_counts["Cantidad"],
                        textposition="auto"
                    )
                ]
            )
            fig_boulder.update_layout(
                title="Pirámide de Bloques por Color (Dificultad Creciente →)",
                xaxis_title="Color del Bloque",
                yaxis_title="Cantidad Escalada",
                xaxis=dict(categoryorder="array", categoryarray=COLORES_BOULDER)
            )
            apply_plotly_dark_theme(fig_boulder)
            st.plotly_chart(fig_boulder, use_container_width=True)
        else:
            st.info("Aún no hay bloques de Boulder registrados.")

    with tab_g_cuerda:
        df_cuerda = df_climb_all[df_climb_all["modalidad"] == "Cuerda"].copy()
        if not df_cuerda.empty:
            # Barras apiladas por Grado Francés coloreado según Resultado
            # Asegurar orden exacto de dificultad
            cuerda_group = df_cuerda.groupby(["grado", "orden_dificultad", "resultado"]).size().reset_index(name="cantidad")
            cuerda_group = cuerda_group.sort_values(by="orden_dificultad")

            fig_cuerda = px.bar(
                cuerda_group,
                x="grado",
                y="cantidad",
                color="resultado",
                title="Vías de Cuerda por Grado y Resultado",
                labels={"grado": "Grado Francés", "cantidad": "Número de Vías", "resultado": "Estilo / Resultado"},
                category_orders={"grado": GRADOS_CUERDA}
            )
            apply_plotly_dark_theme(fig_cuerda)
            fig_cuerda.update_layout(barmode="stack")
            st.plotly_chart(fig_cuerda, use_container_width=True)
        else:
            st.info("Aún no hay vías de Cuerda registradas.")

# ==========================================
# SECCIÓN 4: 🗂️ HISTORIAL Y BACKUPS
# ==========================================
elif seccion == "history":
    st.markdown("#### 🗂️ Historial de Registros y Copias de Seguridad")

    conn = get_db_connection()
    df_gym = pd.read_sql_query("SELECT * FROM registros_gym ORDER BY id DESC", conn)
    df_climb = pd.read_sql_query("SELECT * FROM registros_escalada ORDER BY id DESC", conn)
    conn.close()

    subtab_h_gym, subtab_h_climb, subtab_manage = st.tabs([
        "🏋️ Historial Gimnasio",
        "🧗 Historial Escalada",
        "⚙️ Gestión & Exportación"
    ])

    with subtab_h_gym:
        st.write(f"**Total series registradas:** {len(df_gym)}")
        st.dataframe(df_gym, use_container_width=True, hide_index=True)

    with subtab_h_climb:
        st.write(f"**Total vías/bloques registrados:** {len(df_climb)}")
        st.dataframe(df_climb, use_container_width=True, hide_index=True)

    with subtab_manage:
        st.markdown("##### 📥 Descargar Copias de Seguridad (.CSV)")
        c_csv1, c_csv2 = st.columns(2)
        today_str = datetime.date.today().strftime("%Y%m%d")

        with c_csv1:
            csv_gym = df_gym.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar Gimnasio (.csv)",
                data=csv_gym,
                file_name=f"gym_backup_{today_str}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with c_csv2:
            csv_climb = df_climb.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar Escalada (.csv)",
                data=csv_climb,
                file_name=f"escalada_backup_{today_str}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("##### 🗑️ Eliminar Registro Erróneo por ID")
        del_col1, del_col2, del_col3 = st.columns([1, 1, 1])

        with del_col1:
            tabla_del = st.selectbox("Seleccionar Tabla:", ["registros_gym", "registros_escalada"])
        with del_col2:
            id_del = st.number_input("ID del registro a eliminar:", min_value=1, step=1)
        with del_col3:
            st.write("")
            st.write("")
            if st.button("🗑️ Eliminar Registro", type="secondary", use_container_width=True):
                try:
                    conn = get_db_connection()
                    with conn:
                        cursor = conn.execute(f"DELETE FROM {tabla_del} WHERE id = ?", (int(id_del),))
                        afectados = cursor.rowcount
                    conn.close()
                    if afectados > 0:
                        st.success(f"Registro con ID {id_del} eliminado de '{tabla_del}'.")
                        st.rerun()
                    else:
                        st.warning(f"No se encontró ningún registro con ID {id_del} en '{tabla_del}'.")
                except Exception as e:
                    st.error(f"Error al eliminar: {str(e)}")

        st.markdown("---")
        st.caption(f"📁 Ruta de base de datos activa: `{DB_FILE.resolve()}` | Persistido en volumen Docker.")

# ==========================================
# SECCIÓN 5: 💡 GUÍA & AYUDA: PEDIR RUTINAS A GEMINI
# ==========================================
if seccion == "help_gemini":
    st.markdown("#### 💡 Cómo pedir una nueva rutina a Gemini")
    st.caption("Copia este prompt, pégalo en Gemini y obtendrás el JSON 100% compatible con la app.")

    st.markdown("""
    > [!TIP]
    > **Gemini generará un código JSON exacto**. Solo tendrás que copiarlo, entrar en **🏋️ Gimnasio**, pegarlo en la caja de texto y pulsar **Cargar Rutina desde JSON**.
    """)

    st.markdown("##### 1. Prompt listo para copiar:")
    prompt_texto = """Actúa como un entrenador personal de fuerza especializado en escalada y biomecánica con protección estricta de la columna lumbar (patología L5-S1 / discopatía).

Quiero una rutina para hoy con las siguientes características:
- Objetivo: [Fuerza / Hipertrofia / Torso / Pierna / Antagonistas para escalada]
- Nivel de fatiga actual: [Bajo / Moderado / Alto]
- Restricciones L5-S1: Cero compresión axial pesada sobre la columna. Nada de sentadillas con barra trasnuca ni peso muerto convencional pesado. Preferencia por ejercicios con apoyo de pecho, unilaterales y trabajo de core anti-movimiento.

Genera la respuesta ÚNICAMENTE con un bloque de código JSON con esta estructura exacta para que pueda importarlo directamente en mi aplicación:

```json
{
  "fecha": "2026-10-18",
  "tipo_sesion": "Gym - Torso & Antagonistas L5-S1",
  "ejercicios": [
    {
      "bloque": "Calentamiento & Activación",
      "nombre": "Deadbug Estático",
      "series": 3,
      "reps_objetivo": 10,
      "peso_sugerido": 0.0,
      "lumbar_tip": "Presionar la zona lumbar plana contra el suelo; sin arco."
    },
    {
      "bloque": "Fuerza Principal",
      "nombre": "Remo con Pecho Apoyado",
      "series": 4,
      "reps_objetivo": 8,
      "peso_sugerido": 45.0,
      "lumbar_tip": "Pecho firme contra el banco a 30-45°. Cero tirón lumbar."
    },
    {
      "bloque": "Accesorios",
      "nombre": "Press Militar Half-Kneeling",
      "series": 3,
      "reps_objetivo": 10,
      "peso_sugerido": 16.0,
      "lumbar_tip": "Glúteo de la pierna retrasada bloqueado para fijar la pelvis."
    }
  ]
}
```
Solo responde con el bloque JSON, sin texto de saludo adicional."""

    st.code(prompt_texto, language="markdown")

    st.markdown("##### 2. ¿Cómo importarlo en la App?")
    st.markdown("""
    1. **Copia el JSON** que te devuelva Gemini.
    2. Vuelve al menú y pulsa **🏋️ Gimnasio**.
    3. Pulsa en **📋 Cargar Rutina desde JSON**.
    4. Pega el texto y pulsa **Cargar Rutina desde JSON**.
    5. La app comprobará automáticamente si ya tienes pesos previos registrados para esos ejercicios y te los rellenará solos.
    """)


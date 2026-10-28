"""Datos simulados de la demo.

Todo lo que hay aquí es inventado: obras, clientes, códigos y montos. Los montos
salen de una curva S determinista, así que cada vez que se genera el sitio da lo
mismo.
"""
import math

HOY = "28-oct-2026"
MES_ACTUAL = (2026, 10)

MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

CUENTAS = [("mat", "Materiales"), ("mo", "Mano de obra"), ("gg", "GG Obra")]


def rotulo_mes(anio, mes):
    return f"{MESES_ES[mes - 1]}-{str(anio)[2:]}"


def meses_desde(inicio, n):
    anio, mes = inicio
    salida = []
    for _ in range(n):
        salida.append((anio, mes))
        mes += 1
        if mes > 12:
            anio, mes = anio + 1, 1
    return salida


def pesos_curva_s(n):
    """Reparto mensual con forma de campana: acumulado en S."""
    w = [math.sin(math.pi * (i + 0.5) / n) ** 2 for i in range(n)]
    s = sum(w)
    return [x / s for x in w]


# Factor real/presupuesto por cuenta (desvío) y factor con que la proyección
# guardada estima lo que falta.
OBRAS = [
    dict(
        id=1, slug="mirador", codigo="OB-2601",
        nombre="Edificio Mirador del Valle", cliente="Inmobiliaria Altavista",
        comuna="Viña del Mar", jefe="Valentina Rojas",
        inicio=(2026, 1), meses=14, estado=("cierre", "En cierre"),
        presupuesto=dict(mat=218_400_000, mo=146_200_000, gg=63_900_000), venta=512_000_000,
        real=dict(mat=1.04, mo=0.98, gg=1.06), proy=dict(mat=1.08, mo=1.00, gg=1.10),
        proyeccion=dict(nombre="Proyección 1", fecha="12-oct-2026", autor="Valentina Rojas"),
    ),
    dict(
        id=2, slug="aromos", codigo="OB-2603",
        nombre="Centro Logístico Los Aromos", cliente="Logística Andes Sur",
        comuna="Pudahuel", jefe="Tomás Herrera",
        inicio=(2026, 3), meses=15, estado=("ejecucion", "En ejecución"),
        presupuesto=dict(mat=342_700_000, mo=205_300_000, gg=88_100_000), venta=760_000_000,
        real=dict(mat=1.06, mo=1.03, gg=0.97), proy=dict(mat=1.05, mo=1.04, gg=0.98),
        proyeccion=dict(nombre="Proyección 1", fecha="20-oct-2026", autor="Tomás Herrera"),
    ),
    dict(
        id=3, slug="costanera", codigo="OB-2607",
        nombre="Clínica Costanera Sur", cliente="Red de Salud Pacífico",
        comuna="Concepción", jefe="Camila Fuentes",
        inicio=(2026, 7), meses=12, estado=("inicio", "Inicio"),
        presupuesto=dict(mat=265_500_000, mo=180_400_000, gg=79_200_000), venta=618_000_000,
        real=dict(mat=0.95, mo=1.02, gg=1.01), proy=dict(mat=0.99, mo=1.01, gg=1.00),
        proyeccion=dict(nombre="Proyección 1", fecha="22-oct-2026", autor="Camila Fuentes"),
    ),
]


def _ruido(i, k):
    return 1 + 0.07 * math.sin(i * 1.7 + k * 2.3)


def calcular(obra):
    """Agrega a la obra sus meses, gasto real mensual y proyección por cuenta."""
    meses = meses_desde(obra["inicio"], obra["meses"])
    w = pesos_curva_s(obra["meses"])
    corte = meses.index(MES_ACTUAL)  # índice del mes en curso (incluido en el real)
    obra["lista_meses"] = meses
    obra["corte"] = corte
    obra["real_mensual"] = {}
    obra["proy_mensual"] = {}
    for k, (c, _) in enumerate(CUENTAS):
        p = obra["presupuesto"][c]
        real = [int(round(p * w[i] * obra["real"][c] * _ruido(i, k), -3)) for i in range(corte + 1)]
        proy = [int(round(p * w[i] * obra["proy"][c], -3)) for i in range(corte + 1, obra["meses"])]
        obra["real_mensual"][c] = real
        obra["proy_mensual"][c] = proy
    obra["presupuesto_total"] = sum(obra["presupuesto"].values())
    obra["gastado"] = sum(sum(v) for v in obra["real_mensual"].values())
    obra["al_termino"] = obra["gastado"] + sum(sum(v) for v in obra["proy_mensual"].values())
    obra["avance"] = obra["gastado"] / obra["presupuesto_total"]
    a, m = meses[0]
    b, n = meses[-1]
    obra["periodo"] = f"{rotulo_mes(a, m)} a {rotulo_mes(b, n)}"
    return obra


for _o in OBRAS:
    calcular(_o)


# ── Ítems de cada cuenta ─────────────────────────────────────────────────────
# (código, descripción, unidad, precio unitario de referencia, subcategoría)

CATALOGO_MAT = [
    ("MT-10412", "Cable cobre THHN 12 AWG rojo", "ML", 690, "Conductores"),
    ("MT-10418", "Cable libre de halógenos 2,5 mm² azul", "ML", 540, "Conductores"),
    ("MT-10433", "Cable multiconductor 4x10 mm²", "ML", 6_850, "Conductores"),
    ("MT-10451", "Cable de poder 3x70 mm² + T", "ML", 41_200, "Conductores"),
    ("MT-11207", "Tubo conduit EMT 3/4\" x 3 m", "UN", 4_350, "Canalizaciones"),
    ("MT-11215", "Bandeja portaconductores perforada 300 mm", "ML", 18_900, "Canalizaciones"),
    ("MT-11230", "Tubo PVC rígido 25 mm x 3 m", "UN", 1_480, "Canalizaciones"),
    ("MT-11244", "Caja de derivación estanca 100x100", "UN", 2_150, "Canalizaciones"),
    ("MT-12105", "Gabinete metálico 600x400x200", "UN", 128_000, "Tableros y protecciones"),
    ("MT-12118", "Interruptor termomagnético 2x16 A", "UN", 6_900, "Tableros y protecciones"),
    ("MT-12126", "Interruptor diferencial 2x25 A 30 mA", "UN", 24_600, "Tableros y protecciones"),
    ("MT-12140", "Barra de cobre 20x5 mm", "ML", 31_800, "Tableros y protecciones"),
    ("MT-12152", "Contactor tripolar 25 A", "UN", 38_400, "Tableros y protecciones"),
    ("MT-13310", "Panel LED 60x60 40 W", "UN", 21_900, "Iluminación"),
    ("MT-13322", "Proyector LED 100 W exterior", "UN", 46_500, "Iluminación"),
    ("MT-13335", "Luminaria de emergencia LED", "UN", 17_800, "Iluminación"),
    ("MT-13347", "Campana LED industrial 150 W", "UN", 89_000, "Iluminación"),
    ("MT-14402", "Abrazadera tipo omega 3/4\"", "UN", 180, "Fijaciones y accesorios"),
    ("MT-14418", "Varilla roscada 3/8\" x 1 m", "UN", 1_250, "Fijaciones y accesorios"),
    ("MT-14425", "Terminal de compresión 10 mm²", "UN", 560, "Fijaciones y accesorios"),
    ("MT-14431", "Amarra plástica 300 mm (bolsa 100)", "UN", 3_900, "Fijaciones y accesorios"),
    ("MT-15501", "Barra copperweld 5/8\" x 1,5 m", "UN", 14_700, "Puesta a tierra"),
    ("MT-15512", "Soldadura exotérmica 90 g", "UN", 8_900, "Puesta a tierra"),
    ("MT-15520", "Conductor de cobre desnudo 35 mm²", "ML", 5_600, "Puesta a tierra"),
    ("MT-16608", "Enchufe doble 10 A con tierra", "UN", 3_400, "Enchufes y control"),
    ("MT-16615", "Interruptor 9/12 doble", "UN", 2_950, "Enchufes y control"),
    ("MT-16627", "Sensor de movimiento 360°", "UN", 15_800, "Enchufes y control"),
]

CATALOGO_MO = [
    ("MO-201", "Maestro eléctrico primera", "HH", 9_800, "Cuadrilla de montaje"),
    ("MO-202", "Maestro eléctrico segunda", "HH", 8_200, "Cuadrilla de montaje"),
    ("MO-203", "Ayudante eléctrico", "HH", 5_900, "Cuadrilla de montaje"),
    ("MO-211", "Técnico en tableros", "HH", 11_400, "Especialistas"),
    ("MO-212", "Técnico en corrientes débiles", "HH", 10_900, "Especialistas"),
    ("MO-221", "Supervisor eléctrico", "HH", 15_600, "Supervisión"),
    ("MO-222", "Prevencionista de riesgos", "HH", 12_300, "Supervisión"),
    ("MO-223", "Bodeguero de obra", "HH", 6_800, "Supervisión"),
    ("MO-231", "Horas extraordinarias cuadrilla", "HH", 12_250, "Horas extraordinarias"),
]

CATALOGO_GG = [
    ("GG-301", "Contenedor oficina 20 pies (arriendo)", "MES", 420_000, "Instalación de faena"),
    ("GG-302", "Baño químico (arriendo)", "MES", 165_000, "Instalación de faena"),
    ("GG-311", "Plataforma tijera 10 m (arriendo)", "DÍA", 68_000, "Arriendo de equipos"),
    ("GG-312", "Generador 20 kVA (arriendo)", "DÍA", 54_000, "Arriendo de equipos"),
    ("GG-321", "Camión pluma (servicio)", "SERV", 310_000, "Fletes y traslados"),
    ("GG-322", "Flete de materiales a obra", "SERV", 185_000, "Fletes y traslados"),
    ("GG-331", "Póliza todo riesgo construcción", "UN", 2_400_000, "Seguros y garantías"),
    ("GG-332", "Boleta de garantía fiel cumplimiento", "UN", 1_150_000, "Seguros y garantías"),
    ("GG-341", "Colaciones del personal", "UN", 4_800, "Alimentación y alojamiento"),
    ("GG-342", "Alojamiento cuadrilla", "NOCHE", 32_000, "Alimentación y alojamiento"),
    ("GG-351", "Kit EPP (casco, guantes y lentes)", "UN", 24_500, "Elementos de protección"),
    ("GG-352", "Arnés de seguridad con línea de vida", "UN", 89_000, "Elementos de protección"),
]

CATALOGOS = {"mat": CATALOGO_MAT, "mo": CATALOGO_MO, "gg": CATALOGO_GG}

SUBCATEGORIAS = {
    c: list(dict.fromkeys(x[4] for x in CATALOGOS[c])) for c in CATALOGOS
}


# Cuánto pesa cada subcategoría en el gasto: los conductores y tableros se
# llevan la mayor parte; las fijaciones, poco.
PESO_SUB = {
    "Conductores": 2.6, "Tableros y protecciones": 1.9, "Iluminación": 1.6, "Canalizaciones": 1.2,
    "Puesta a tierra": 0.5, "Enchufes y control": 0.45, "Fijaciones y accesorios": 0.3,
    "Cuadrilla de montaje": 3.0, "Supervisión": 1.0, "Especialistas": 1.2, "Horas extraordinarias": 0.5,
    "Instalación de faena": 1.0, "Arriendo de equipos": 1.3, "Seguros y garantías": 0.8,
}


def _items(obra, cuenta, k):
    """Reparte el gasto real de la cuenta entre ítems del catálogo.

    Las cantidades son enteras, así que la suma no cuadra al peso: la diferencia
    se carga al mes en curso para que la tabla de Proyección y las de detalle
    digan lo mismo.
    """
    import random
    rnd = random.Random(obra["id"] * 100 + k)
    cat = CATALOGOS[cuenta]
    elegidos = cat if cuenta != "mat" else rnd.sample(cat, 22)
    pesos = [rnd.uniform(0.5, 1.8) * PESO_SUB.get(x[4], 1) * x[3] ** 0.3 for x in elegidos]
    total = sum(obra["real_mensual"][cuenta])
    corte = obra["corte"]
    meses = obra["lista_meses"]
    items = []
    for (cod, desc, un, precio, sub), w in zip(elegidos, pesos):
        precio = int(round(precio * rnd.uniform(0.93, 1.08), -1))
        cant = max(1, round(total * w / sum(pesos) / precio))
        ini = rnd.randint(0, max(0, corte - 1))
        fin = rnd.randint(ini, corte)
        items.append(dict(
            cod=cod, desc=desc, un=un, precio=precio, cant=cant, monto=cant * precio, sub=sub,
            docs=rnd.randint(1, 14), periodo=(meses[ini], meses[fin]),
        ))
    items.sort(key=lambda x: -x["monto"])
    obra["real_mensual"][cuenta][corte] += sum(i["monto"] for i in items) - total
    return items


def _recalcular_totales(obra):
    obra["gastado"] = sum(sum(v) for v in obra["real_mensual"].values())
    obra["al_termino"] = obra["gastado"] + sum(sum(v) for v in obra["proy_mensual"].values())
    obra["avance"] = obra["gastado"] / obra["presupuesto_total"]


for _o in OBRAS:
    _o["items"] = {c: _items(_o, c, k) for k, (c, _) in enumerate(CUENTAS)}
    _recalcular_totales(_o)


# ── Usuarios y perfiles ──────────────────────────────────────────────────────

PERFILES = [
    # (nombre, nivel en el árbol, descripción breve, acceso)
    ("Gerencia general", 0, "Ve todas las obras y aprueba proyecciones.", "Todas las obras"),
    ("Jefatura de proyectos", 1, "Gestiona obras y sus proyecciones.", "Todas las obras"),
    ("Jefe de obra", 2, "Revisa y clasifica el gasto de sus obras.", "Obras asignadas"),
    ("Asistente de obra", 3, "Consulta la información de sus obras.", "Obras asignadas"),
    ("Administración", 1, "Consulta gasto y mantiene configuraciones.", "Todas las obras"),
    ("Contabilidad", 2, "Consulta el gasto y su origen en el ERP.", "Todas las obras"),
]

USUARIOS = [
    ("Usuario Demo", "demo@ejemplo.cl", "Gerencia general", "Todas", "Activo", "hoy"),
    ("Andrea Molina", "amolina@ejemplo.cl", "Gerencia general", "Todas", "Activo", "27-oct-2026"),
    ("Rodrigo Saavedra", "rsaavedra@ejemplo.cl", "Jefatura de proyectos", "Todas", "Activo", "28-oct-2026"),
    ("Valentina Rojas", "vrojas@ejemplo.cl", "Jefe de obra", "Mirador del Valle", "Activo", "28-oct-2026"),
    ("Tomás Herrera", "therrera@ejemplo.cl", "Jefe de obra", "Los Aromos", "Activo", "26-oct-2026"),
    ("Camila Fuentes", "cfuentes@ejemplo.cl", "Jefe de obra", "Costanera Sur", "Activo", "28-oct-2026"),
    ("Diego Paredes", "dparedes@ejemplo.cl", "Asistente de obra", "Los Aromos, Costanera Sur", "Activo", "24-oct-2026"),
    ("Francisca León", "fleon@ejemplo.cl", "Administración", "Todas", "Activo", "22-oct-2026"),
    ("Martín Cáceres", "mcaceres@ejemplo.cl", "Contabilidad", "Todas", "Activo", "25-oct-2026"),
    ("Javiera Núñez", "jnunez@ejemplo.cl", "Asistente de obra", "Mirador del Valle", "Inactivo", "03-ago-2026"),
]


# ── Propuestas ───────────────────────────────────────────────────────────────

PROPUESTAS = [
    # (n°, obra, cliente, responsable, estado clave, estado texto, precio UF, margen, modificación)
    ("P-001", "Hospital Regional del Sur · torre B", "Constructora Meridiano", "Rodrigo Saavedra", "revision", "En revisión", 1_730, 0.246, "27-oct-2026 18:41"),
    ("P-002", "Bodega Logística Quilicura", "Inversiones Cordillera", "Valentina Rojas", "borrador", "Borrador", None, None, "26-oct-2026 10:12"),
    ("P-003", "Centro Comercial Oriente · ampliación", "Grupo Comercial Austral", "Tomás Herrera", "enviada", "Enviada al cliente", 6_450, 0.231, "24-oct-2026 16:05"),
    ("P-004", "Supermercado Los Robles · iluminación", "Retail Andino", "Camila Fuentes", "revision", "En revisión", 3_120, 0.187, "22-oct-2026 11:20"),
    ("P-005", "Edificio Parque Alameda", "Inmobiliaria Altavista", "Rodrigo Saavedra", "borrador", "Borrador", None, None, "21-oct-2026 09:47"),
    ("P-006", "Clínica Costanera Sur · tablero general", "Red de Salud Pacífico", "Camila Fuentes", "adjudicada", "Adjudicada", 2_280, 0.262, "02-oct-2026 09:12"),
]

# Detalle de la propuesta P-001: partidas con sus líneas.
# (código o None, descripción, subcat., un., cantidad, costo unitario, rendimiento HH/un, estado del código)
# estado: "confirmado", "alta", "media", "sin"
PARTIDAS_P001 = [
    ("Alimentadores generales", [
        ("MT-10451", "Cable de poder 3x70 mm² + T", "Conductores", "ML", 145, 41_200, 0.35, "confirmado"),
        ("MT-14425", "Terminal de compresión 70 mm²", "Fijaciones y accesorios", "UN", 12, 1_350, 0.20, "confirmado"),
        ("MT-11215", "Bandeja portaconductores perforada 300 mm", "Canalizaciones", "ML", 96, 18_900, 0.45, "alta"),
        ("MT-14418", "Varilla roscada 3/8\" x 1 m", "Fijaciones y accesorios", "UN", 80, 1_250, 0.10, "alta"),
    ]),
    ("Tablero general de distribución", [
        ("MT-12105", "Gabinete metálico 800x600x250", "Tableros y protecciones", "UN", 2, 186_000, 6.0, "confirmado"),
        ("MT-12140", "Barra de cobre 30x5 mm", "Tableros y protecciones", "ML", 14, 39_600, 0.80, "media"),
        ("MT-12126", "Interruptor diferencial 4x40 A 30 mA", "Tableros y protecciones", "UN", 8, 52_300, 0.50, "alta"),
        ("MT-12118", "Interruptor termomagnético 3x32 A", "Tableros y protecciones", "UN", 24, 18_700, 0.40, "alta"),
        (None, "Analizador de redes trifásico", "Tableros y protecciones", "UN", 1, 395_000, 1.5, "sin"),
    ]),
    ("Iluminación pisos 1 a 4", [
        ("MT-13310", "Panel LED 60x60 40 W", "Iluminación", "UN", 312, 21_900, 0.60, "confirmado"),
        ("MT-13335", "Luminaria de emergencia LED", "Iluminación", "UN", 64, 17_800, 0.50, "alta"),
        ("MT-16627", "Sensor de movimiento 360°", "Enchufes y control", "UN", 48, 15_800, 0.40, "media"),
        ("MT-10418", "Cable libre de halógenos 2,5 mm²", "Conductores", "ML", 4_200, 540, 0.02, "confirmado"),
        ("MT-11207", "Tubo conduit EMT 3/4\" x 3 m", "Canalizaciones", "UN", 620, 4_350, 0.25, "alta"),
    ]),
    ("Puesta a tierra", [
        ("MT-15501", "Barra copperweld 5/8\" x 1,5 m", "Puesta a tierra", "UN", 16, 14_700, 0.80, "confirmado"),
        ("MT-15512", "Soldadura exotérmica 90 g", "Puesta a tierra", "UN", 40, 8_900, 0.30, "media"),
        ("MT-15520", "Conductor de cobre desnudo 35 mm²", "Puesta a tierra", "ML", 260, 5_600, 0.05, "alta"),
    ]),
]

# Sugerencias que el asistente muestra para la línea seleccionada.
SUGERENCIAS_P001 = dict(
    linea="Barra de cobre 30x5 mm",
    candidatos=[
        ("MT-12140", "Barra de cobre 20x5 mm", "ML", 31_800, "media", "Misma familia; cambia la medida"),
        ("MT-12144", "Barra de cobre 30x5 mm estañada", "ML", 44_900, "media", "Coincide la medida; distinto acabado"),
        ("MT-12161", "Pletina de cobre 30x3 mm", "ML", 27_400, "baja", "Producto parecido, otra sección"),
    ],
)

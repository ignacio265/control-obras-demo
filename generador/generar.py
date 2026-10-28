"""Genera las páginas estáticas de la demo en ../sitio.

Solo arma HTML: el sitio publicado no lleva JavaScript ni servidor. Se usa este
script para no repetir a mano el menú, el pie y el aviso de demo en cada página.

    python3 generador/generar.py
"""
import hashlib
from html import escape
from pathlib import Path

from datos import (CUENTAS, HOY, MES_ACTUAL, OBRAS, PARTIDAS_P001, PERFILES, PROPUESTAS,
                   SUBCATEGORIAS, SUGERENCIAS_P001, USUARIOS, rotulo_mes)

SITIO = Path(__file__).resolve().parent.parent / "sitio"

CALENDAR = "https://calendar.app.google/a8F5saYxdxWwMsWz7"
WHATSAPP = ("https://wa.me/56985272032?text=Hola%2C%20vi%20la%20demo%20en%20ardillalab.com%20"
            "y%20me%20gustar%C3%ADa%20agendar%20una%20reuni%C3%B3n")


# ── Formato ──────────────────────────────────────────────────────────────────

def clp(n):
    signo = "-" if n < 0 else ""
    return f"{signo}${abs(n):,.0f}".replace(",", ".")


def millones(n):
    signo = "-" if n < 0 else ""
    return f"{signo}${abs(n) / 1e6:,.1f} M".replace(",", "#").replace(".", ",").replace("#", ".")


def pct(x, dec=1):
    return f"{x * 100:.{dec}f} %".replace(".", ",")


# ── Íconos (trazos simples, heredan el color) ───────────────────────────────

ICONOS = {
    "proyectos": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"/>',
    "dashboard": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "propuestas": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/>',
    "usuarios": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "configuracion": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    "marca": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "curva": '<path d="M3 20c6 0 6-16 18-16"/><path d="M3 20h18"/>',
    "mas": '<path d="M12 5v14M5 12h14"/>',
    "descargar": '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
    "calendario": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-12.3 7.4L3 21l2.1-5.6A8.4 8.4 0 1 1 21 11.5Z"/>',
    "sync": '<path d="M21 12a9 9 0 0 1-15.5 6.2L3 16M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5M3 21v-5h5"/>',
}


def icono(nombre):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONOS[nombre]}</svg>'


# ── Piezas comunes ───────────────────────────────────────────────────────────

def boton_bloqueado(texto, accion, primario=False, ico=None, clase=""):
    """Botón de acción visible pero inerte: al pasar el mouse dice qué haría."""
    clases = "btn" + (" btn-primario" if primario else "") + (f" {clase}" if clase else "")
    i = icono(ico) if ico else ""
    # Dentro de una tabla desplazable el globo se cortaría: ahí va el title nativo.
    ayuda = f'title="🔒 {escape(accion)}"' if "tip-tabla" in clases else f'data-accion="{escape(accion)}"'
    return (f'<button type="button" class="{clases}" aria-disabled="true" {ayuda} '
            f'aria-label="{escape(texto)} (bloqueado en la demo: {escape(accion)})">'
            f'{i}{escape(texto)}</button>')


def boton_demo(texto, primario=False, ico=None):
    """Botón que abre el aviso de «agenda una demo»."""
    clases = "btn abre-demo" + (" btn-primario" if primario else "")
    i = icono(ico) if ico else ""
    return f'<button type="button" class="{clases}" popovertarget="demo">{i}{escape(texto)}</button>'


def guia(html):
    return f'<aside class="guia"><span class="guia-icono" aria-hidden="true">i</span><p>{html}</p></aside>'


def modal_demo():
    return f"""
<div id="demo" popover class="modal-demo" role="dialog" aria-labelledby="demo-titulo">
  <div class="modal-cuerpo">
    <div class="modal-ardilla">{icono("curva")}</div>
    <h2 id="demo-titulo">¿Te interesa conocer más?</h2>
    <p>Esta función está disponible en la versión completa. Agenda una demo y te la muestro funcionando con tus propias obras.</p>
    <div class="modal-botones">
      <a class="btn btn-primario" href="{CALENDAR}" target="_blank" rel="noopener">{icono("calendario")}Agendar en Google Calendar</a>
      <a class="btn btn-whatsapp" href="{WHATSAPP}" target="_blank" rel="noopener">{icono("chat")}Escribir por WhatsApp</a>
    </div>
    <button type="button" class="modal-cerrar" popovertarget="demo" popovertargetaction="hide">Seguir explorando</button>
  </div>
</div>"""


TECNOLOGIAS = ["Python", "Django", "JavaScript", "R", "PostgreSQL", "SQL", "HTML y CSS",
               "Docker", "Google Cloud Run", "Cloud SQL", "Cloud Storage", "pandas",
               "API REST del ERP"]


def pie():
    chips = "".join(f'<span class="chip">{t}</span>' for t in TECNOLOGIAS)
    return f"""
<footer class="pie">
  <details>
    <summary>Observaciones de la demo</summary>
    <p>Esta demo está escrita solo en HTML y CSS: no guarda nada, no tiene usuarios reales y todos los datos (obras, clientes, códigos y montos) son simulados.
    El aplicativo original corre en la nube y está desarrollado con:</p>
    <div class="chips">{chips}</div>
  </details>
  <span>Desarrollado por <a href="https://ardillalab.com" target="_blank" rel="noopener">ardillalab.com</a></span>
</footer>"""


def menu(activo, obra_activa=None):
    def item(clave, href, texto):
        cls = "nav-item activo" if activo == clave else "nav-item"
        return f'<a href="{href}" class="{cls}">{icono(clave)}<span>{texto}</span></a>'

    obras = "".join(
        f'<li><a href="obra-{o["slug"]}-proyeccion.html"'
        f'{" class=\"activo\" aria-current=\"page\"" if o["id"] == obra_activa else ""}'
        f' title="{escape(o["nombre"])}">{escape(o["nombre"])}</a></li>'
        for o in OBRAS)
    return f"""
<nav class="sidebar" aria-label="Menú principal">
  {item("proyectos", "index.html", "Proyectos")}
  <ul class="menu-obras">{obras}</ul>
  {item("dashboard", "dashboard.html", "Dashboard")}
  {item("propuestas", "propuestas.html", "Propuestas")}
  <div class="menu-sep"></div>
  {item("usuarios", "usuarios.html", "Usuarios")}
  {item("configuracion", "configuracion.html", "Configuración")}
</nav>"""


def version_css():
    """Marca de versión de la hoja: cambia cuando cambia el CSS y evita la caché vieja."""
    return hashlib.sha1((SITIO / "css" / "estilos.css").read_bytes()).hexdigest()[:8]


def pagina(nombre, titulo, cuerpo, activo, obra_activa=None, perfil_activo=False):
    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)} · Control de Obras</title>
<meta name="description" content="Demo navegable de un sistema de control financiero de obras. Datos simulados.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@600;700&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="css/estilos.css?v={version_css()}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='6' fill='%23E8872A'/%3E%3Cpath d='M6 18v-6M10 18V7M14 18v-4M18 18V9' stroke='white' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E">
</head>
<body>
<header class="topbar">
  <a class="marca" href="index.html">
    <span class="marca-icono">{icono("marca")}</span>
    <span class="marca-texto">Control de <span>Obras</span></span>
  </a>
  <div class="topbar-der">
    <span class="pastilla-demo">Modo demo · datos simulados</span>
    <a href="mi-perfil.html" class="user-chip{' activo' if perfil_activo else ''}" title="Mi perfil">
      <span class="avatar" aria-hidden="true">UD</span><span class="user-chip-nombre">Usuario Demo</span>
    </a>
  </div>
</header>
<div class="layout">
{menu(activo, obra_activa)}
<main class="content">
{cuerpo}
</main>
</div>
{pie()}
{modal_demo()}
</body>
</html>
"""
    (SITIO / nombre).write_text(html, encoding="utf-8")


# ── Proyectos (home) ─────────────────────────────────────────────────────────

def pag_proyectos():
    tarjetas = []
    for o in OBRAS:
        est_cls, est_txt = o["estado"]
        tarjetas.append(f"""
<article class="tarjeta obra">
  <div class="obra-cab"><span class="obra-num">{o["codigo"]}</span><span class="estado estado-{est_cls}">{est_txt}</span></div>
  <div class="obra-cuerpo">
    <h2>{escape(o["nombre"])}</h2>
    <p class="obra-cliente">{escape(o["cliente"])} · {escape(o["comuna"])}</p>
    <dl class="obra-datos">
      <div><dt>Presupuesto</dt><dd>{millones(o["presupuesto_total"])}</dd></div>
      <div><dt>Gastado</dt><dd>{millones(o["gastado"])}</dd></div>
      <div><dt>Período</dt><dd>{o["periodo"]}</dd></div>
      <div><dt>Jefe de obra</dt><dd>{escape(o["jefe"])}</dd></div>
    </dl>
    <div class="avance-fila"><span>Avance del gasto</span><b>{pct(o["avance"], 0)}</b></div>
    <div class="barra"><b style="width:{min(o["avance"], 1) * 100:.1f}%"></b></div>
  </div>
  <div class="obra-pie">
    <span class="fecha">Actualizado {HOY}</span>
    <a class="btn btn-primario" href="obra-{o["slug"]}-proyeccion.html">Ver proyección</a>
  </div>
</article>""")

    cuerpo = f"""
<div class="cabecera">
  <h1>Mis <span>Proyectos</span></h1>
  <div class="cabecera-acciones">
    {boton_bloqueado("Sincronizar ERP", "Traería desde el ERP los documentos nuevos de compras, bodega y remuneraciones", ico="sync", clase="tip-abajo")}
    {boton_bloqueado("Nuevo proyecto", "Abriría el formulario para crear una obra y cargar su presupuesto inicial", primario=True, ico="mas", clase="tip-abajo tip-der")}
  </div>
</div>
{guia("<strong>Tus obras en un vistazo.</strong> Cada tarjeta resume el presupuesto, lo gastado y el avance del gasto de una obra. "
      "El gasto llega solo desde el ERP de la empresa; aquí no se digita. Entra a una obra para ver su proyección mes a mes.")}
<section class="obras">{"".join(tarjetas)}</section>
"""
    pagina("index.html", "Proyectos", cuerpo, "proyectos")


# ── Obra: navegación y proyección ───────────────────────────────────────────

def subnav(o, activo):
    tabs = [("proyeccion", "Proyección"), ("materiales", "Materiales"), ("mano-de-obra", "Mano de Obra"), ("gg-obra", "GG Obra")]
    enlaces = "".join(
        f'<a href="obra-{o["slug"]}-{k}.html"{" class=\"activo\"" if k == activo else ""}>{t}</a>' for k, t in tabs)
    return f'<nav class="subnav" aria-label="Secciones de la obra">{enlaces}</nav>'


def migas(o, seccion):
    return (f'<div class="migas"><a href="index.html">Proyectos</a> › '
            f'<a href="obra-{o["slug"]}-proyeccion.html">{escape(o["nombre"])}</a> › {seccion}</div>')


def tabla_proyeccion(o, con_proyeccion):
    meses = o["lista_meses"]
    corte = o["corte"]
    cols_mes = "".join(
        f'<th class="num{" mes-actual" if (a, m) == MES_ACTUAL else ""}">{rotulo_mes(a, m)}</th>' for a, m in meses)
    if con_proyeccion:
        resumen = ["A la fecha", "Por gastar", "Al término", "DIF", "%"]
        grupo_meses = "Real y proyectado"
    else:
        resumen = ["A la fecha", "Saldo", "% gastado"]
        grupo_meses = "Gastado"
    cab_res = "".join(f'<th class="num">{t}</th>' for t in resumen)

    filas = []
    tot = dict(p=0, fecha=0, resto=0, mens=[0] * len(meses))
    for c, nombre in CUENTAS:
        p = o["presupuesto"][c]
        real = o["real_mensual"][c]
        proy = o["proy_mensual"][c]
        fecha = sum(real)
        resto = sum(proy)
        tot["p"] += p
        tot["fecha"] += fecha
        tot["resto"] += resto
        celdas = []
        for i in range(len(meses)):
            act = " mes-actual" if i == corte else ""
            if i <= corte:
                v = real[i]
                tot["mens"][i] += v
                celdas.append(f'<td class="num{act}">{clp(v)}</td>')
            elif con_proyeccion:
                v = proy[i - corte - 1]
                tot["mens"][i] += v
                celdas.append(f'<td class="num proyectado">{clp(v)}</td>')
            else:
                celdas.append('<td class="num vacio">—</td>')
        filas.append((nombre, p, fecha, resto, celdas))

    def celdas_resumen(p, fecha, resto):
        if con_proyeccion:
            termino = fecha + resto
            dif = p - termino
            cls = "dif-pos" if dif >= 0 else "dif-neg"
            return (f'<td class="num">{clp(fecha)}</td><td class="num">{clp(resto)}</td>'
                    f'<td class="num">{clp(termino)}</td><td class="num {cls}">{clp(dif)}</td>'
                    f'<td class="num {cls}">{pct(termino / p)}</td>')
        return (f'<td class="num">{clp(fecha)}</td><td class="num">{clp(p - fecha)}</td>'
                f'<td class="num">{pct(fecha / p)}</td>')

    cuerpo = ""
    for nombre, p, fecha, resto, celdas in filas:
        cuerpo += (f'<tr><td class="col-fija">{nombre}</td><td class="num">{clp(p)}</td>'
                   f'{celdas_resumen(p, fecha, resto)}{"".join(celdas)}</tr>')
    tot_mens = "".join(
        f'<td class="num{" mes-actual" if i == corte else ""}{" proyectado" if con_proyeccion and i > corte else ""}">'
        f'{clp(v) if (i <= corte or con_proyeccion) else "—"}</td>'
        for i, v in enumerate(tot["mens"]))
    cuerpo += (f'<tr class="fila-total"><td class="col-fija">Total costo</td><td class="num">{clp(tot["p"])}</td>'
               f'{celdas_resumen(tot["p"], tot["fecha"], tot["resto"])}{tot_mens}</tr>')

    venta = o["venta"]
    margen_ppto = venta - tot["p"]
    if con_proyeccion:
        margen_fin = venta - tot["fecha"] - tot["resto"]
        res_margen = (f'<td class="num">—</td><td class="num">—</td><td class="num">{clp(margen_fin)}</td>'
                      f'<td class="num">{clp(margen_fin - margen_ppto)}</td><td class="num">{pct(margen_fin / venta)}</td>')
    else:
        res_margen = '<td class="num">—</td><td class="num">—</td><td class="num">—</td>'
    cuerpo += (f'<tr class="fila-margen" title="El margen no se gasta: no tiene consumo mensual.">'
               f'<td class="col-fija">Margen ({pct(margen_ppto / venta)})</td><td class="num">{clp(margen_ppto)}</td>'
               f'{res_margen}{"".join("<td></td>" for _ in meses)}</tr>')

    leyenda = ('<div class="leyenda"><span><i style="background:var(--ink)"></i>Gasto real del ERP</span>'
               + ('<span><i style="background:var(--plan)"></i>Proyectado</span>' if con_proyeccion else "")
               + '<span><i style="background:var(--copper)"></i>Mes en curso</span></div>')
    return f"""
<div class="tarjeta tabla-card">
  <div class="tabla-scroll">
    <table>
      <thead>
        <tr class="grupos"><th class="col-fija"></th><th>Presupuesto</th><th colspan="{len(resumen)}">Resumen</th><th colspan="{len(meses)}">{grupo_meses}</th></tr>
        <tr><th class="col-fija">Cuenta</th><th class="num">Total</th>{cab_res}{cols_mes}</tr>
      </thead>
      <tbody>{cuerpo}</tbody>
    </table>
  </div>
  {leyenda}
</div>"""


def pag_proyeccion(o):
    pr = o["proyeccion"]
    desv = o["presupuesto_total"] - o["al_termino"]
    margen_fin = (o["venta"] - o["al_termino"]) / o["venta"]
    cuerpo = f"""
{migas(o, "Proyección")}
<div class="cabecera">
  <h1>Proyección — <span>{escape(o["nombre"])}</span></h1>
  <div class="cabecera-acciones">
    {boton_bloqueado("Exportar", "Descargaría esta tabla en una planilla Excel con el mismo formato", ico="descargar", clase="tip-abajo tip-der")}
  </div>
</div>
{subnav(o, "proyeccion")}
{guia("<strong>El estado financiero de la obra, mes a mes.</strong> Cruza el presupuesto con el gasto real que llega del ERP. "
      "La vista <em>Gastos mensuales</em> muestra solo lo ocurrido; una <em>proyección</em> guardada agrega la estimación de lo que falta "
      "y muestra cómo terminaría la obra si se cumple.")}
<section class="kpis">
  <div class="tarjeta kpi"><div class="kpi-rotulo">Presupuesto de costo</div><div class="kpi-valor">{millones(o["presupuesto_total"])}</div><div class="kpi-nota">Venta {millones(o["venta"])}</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Gastado a la fecha</div><div class="kpi-valor">{millones(o["gastado"])}</div><div class="kpi-nota">{pct(o["avance"])} del presupuesto</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Proyectado al término</div><div class="kpi-valor">{millones(o["al_termino"])}</div><div class="kpi-nota">según {pr["nombre"]}</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Desviación proyectada</div><div class="kpi-valor">{millones(desv)}</div><div class="kpi-nota {"bien" if desv >= 0 else "mal"}">{"bajo" if desv >= 0 else "sobre"} el presupuesto</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Margen proyectado</div><div class="kpi-valor">{pct(margen_fin)}</div><div class="kpi-nota">presupuestado {pct((o["venta"] - o["presupuesto_total"]) / o["venta"])}</div></div>
</section>
<div class="estados">
  <input type="radio" name="estado" id="est-gastos">
  <input type="radio" name="estado" id="est-proy1" checked>
  <div class="barra-estados">
    <div class="segmentado" role="tablist">
      <label for="est-gastos">Gastos mensuales</label>
      <label for="est-proy1">{pr["nombre"]} · {pr["fecha"]}</label>
    </div>
    <div class="cabecera-acciones">
      {boton_demo("Curva S", ico="curva")}
      {boton_demo("Agregar nueva proyección", primario=True, ico="mas")}
    </div>
  </div>
  <div class="panel-estado panel-gastos">
    <p class="nota-estado">Solo el gasto real registrado hasta {rotulo_mes(*MES_ACTUAL)}. Los meses que vienen quedan vacíos.</p>
    {tabla_proyeccion(o, False)}
  </div>
  <div class="panel-estado panel-proy1">
    <p class="nota-estado">Guardada por {pr["autor"]} el {pr["fecha"]}. Los meses en azul son la estimación de lo que falta por gastar.</p>
    {tabla_proyeccion(o, True)}
  </div>
</div>
"""
    pagina(f"obra-{o['slug']}-proyeccion.html", f"Proyección · {o['nombre']}", cuerpo, "proyectos", obra_activa=o["id"])




# ── Obra: Materiales, Mano de Obra y GG Obra ─────────────────────────────────

def filtros_bloqueados(campos, accion="Filtraría la tabla según los campos elegidos"):
    """Barra de filtros de adorno: los campos se ven pero no se pueden usar."""
    html = ""
    for rotulo, valor in campos:
        html += (f'<label class="campo"><span>{rotulo}</span>'
                 f'<input type="text" value="{escape(valor)}" disabled></label>')
    return (f'<div class="tarjeta filtros">{html}'
            f'<div class="filtros-botones">{boton_bloqueado("Filtrar", accion)}</div></div>')


DETALLE = {
    "mat": dict(pagina="materiales", titulo="Materiales", sub="Consumos",
                cant="Cantidad", guia="<strong>Todo lo que la obra consumió en materiales.</strong> "
                "Cada fila agrupa un ítem del ERP con sus documentos de compra y salidas de bodega. "
                "La columna <em>Partida</em> dice a qué parte del presupuesto se carga."),
    "mo": dict(pagina="mano-de-obra", titulo="Mano de Obra", sub="Remuneraciones",
               cant="HH", guia="<strong>El costo del personal de la obra.</strong> "
               "Las remuneraciones llegan del ERP agrupadas por cargo y se cargan a su partida, "
               "para comparar lo pagado contra lo presupuestado."),
    "gg": dict(pagina="gg-obra", titulo="GG Obra", sub="Gastos generales",
               cant="Cantidad", guia="<strong>Los gastos generales propios de la obra.</strong> "
               "Arriendos, fletes, seguros y servicios que no son material ni mano de obra, "
               "ordenados por partida."),
}


def pag_detalle(o, cuenta):
    d = DETALLE[cuenta]
    items = o["items"][cuenta]
    total = sum(i["monto"] for i in items)

    por_sub = {}
    for i in items:
        por_sub[i["sub"]] = por_sub.get(i["sub"], 0) + i["monto"]
    resumen = "".join(
        f'<div class="partida-resumen"><div class="partida-fila"><span>{escape(s)}</span><b>{millones(v)}</b></div>'
        f'<div class="barra oliva"><b style="width:{v / total * 100:.1f}%"></b></div></div>'
        for s, v in sorted(por_sub.items(), key=lambda x: -x[1]))

    filas = ""
    for i in items:
        (a1, m1), (a2, m2) = i["periodo"]
        per = rotulo_mes(a1, m1) if (a1, m1) == (a2, m2) else f"{rotulo_mes(a1, m1)} a {rotulo_mes(a2, m2)}"
        filas += (f'<tr><td class="mono">{i["cod"]}</td><td>{escape(i["desc"])}</td>'
                  f'<td class="num">{i["cant"]:,}</td><td>{i["un"]}</td>'.replace(",", ".")
                  + f'<td class="num">{clp(i["precio"])}</td><td class="num"><b>{clp(i["monto"])}</b></td>'
                  f'<td class="num">{i["docs"]}</td><td>{per}</td>'
                  f'<td><span class="partida">{escape(i["sub"])}</span></td></tr>')
    filas += (f'<tr class="fila-total"><td></td><td>Total {len(items)} ítems</td><td></td><td></td><td></td>'
              f'<td class="num">{clp(total)}</td><td></td><td></td><td></td></tr>')

    cuerpo = f"""
{migas(o, d["titulo"])}
<div class="cabecera">
  <h1>{d["titulo"]} <span>· {d["sub"]}</span></h1>
  <div class="cabecera-acciones">
    {boton_bloqueado("Asignar partida", "Permitiría cambiar la partida de los ítems seleccionados", clase="tip-abajo")}
    {boton_bloqueado("Exportar", "Descargaría el detalle en una planilla Excel", ico="descargar", clase="tip-abajo tip-der")}
  </div>
</div>
{subnav(o, d["pagina"])}
{guia(d["guia"])}
<section class="tarjeta partidas-card">
  <div class="partidas-cab"><h2>Por partida</h2><span class="muted">{millones(total)} a la fecha · 100 % clasificado</span></div>
  <div class="partidas-grid">{resumen}</div>
</section>
{filtros_bloqueados([("Mes", "Todos"), ("Partida", "Todas"), ("Buscar", "código o descripción")])}
<div class="tarjeta tabla-card">
  <div class="tabla-scroll">
    <table>
      <thead><tr><th>Código</th><th>Descripción</th><th class="num">{d["cant"]}</th><th>Un.</th>
        <th class="num">Precio unit.</th><th class="num">Monto</th><th class="num" title="Documentos del ERP">Docs</th>
        <th>Período</th><th>Partida</th></tr></thead>
      <tbody>{filas}</tbody>
    </table>
  </div>
</div>
"""
    pagina(f"obra-{o['slug']}-{d['pagina']}.html", f"{d['titulo']} · {o['nombre']}", cuerpo, "proyectos", obra_activa=o["id"])


# ── Dashboard ────────────────────────────────────────────────────────────────

COLORES_OBRA = ["var(--copper)", "var(--olive)", "var(--plan)"]


def gasto_por_mes():
    """{(año, mes): [gasto obra1, obra2, obra3]} para los meses con gasto real."""
    meses = {}
    for k, o in enumerate(OBRAS):
        for i, am in enumerate(o["lista_meses"][: o["corte"] + 1]):
            fila = meses.setdefault(am, [0] * len(OBRAS))
            fila[k] += sum(o["real_mensual"][c][i] for c, _ in CUENTAS)
    return dict(sorted(meses.items()))


def grafico_barras(meses):
    ancho, alto, izq, abajo, arriba = 720, 270, 56, 28, 12
    tope = max(sum(v) for v in meses.values())
    escala = 10 ** (len(str(int(tope))) - 1)
    tope = (int(tope / escala) + 1) * escala
    n = len(meses)
    paso = (ancho - izq - 10) / n
    barra = paso * 0.58
    alto_util = alto - abajo - arriba
    svg = [f'<svg class="grafico" viewBox="0 0 {ancho} {alto}" role="img" aria-label="Gasto mensual por obra">']
    for t in range(5):
        v = tope * t / 4
        y = alto - abajo - alto_util * t / 4
        svg.append(f'<line x1="{izq}" x2="{ancho - 6}" y1="{y:.1f}" y2="{y:.1f}" class="g-linea"/>'
                   f'<text x="{izq - 8}" y="{y + 4:.1f}" class="g-eje" text-anchor="end">{v / 1e6:.0f} M</text>')
    for j, ((a, m), vals) in enumerate(meses.items()):
        x = izq + paso * j + (paso - barra) / 2
        y = alto - abajo
        for k, v in enumerate(vals):
            h = alto_util * v / tope
            if h > 0:
                svg.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{barra:.1f}" height="{h:.1f}" '
                           f'style="fill:{COLORES_OBRA[k]}" rx="2"><title>{OBRAS[k]["nombre"]} · {rotulo_mes(a, m)}: {clp(v)}</title></rect>')
                y -= h
        svg.append(f'<text x="{x + barra / 2:.1f}" y="{alto - 8}" class="g-eje" text-anchor="middle">{rotulo_mes(a, m)}</text>')
    svg.append("</svg>")
    return "".join(svg)


def pag_dashboard():
    ppto = sum(o["presupuesto_total"] for o in OBRAS)
    gastado = sum(o["gastado"] for o in OBRAS)
    consumo = "".join(
        f'<li><div class="partida-fila"><span>{escape(o["nombre"])}</span><b>{pct(o["avance"], 0)}</b></div>'
        f'<div class="barra"><b style="width:{min(o["avance"], 1) * 100:.1f}%"></b></div></li>' for o in OBRAS)
    top = {}
    for o in OBRAS:
        for i in o["items"]["mat"]:
            t = top.setdefault(i["cod"], [i["desc"], 0])
            t[1] += i["monto"]
    top5 = sorted(top.values(), key=lambda x: -x[1])[:5]
    lista_top = "".join(f'<li><span>{escape(dsc)}</span><b>{millones(v)}</b></li>' for dsc, v in top5)

    meses = gasto_por_mes()
    leyenda = "".join(f'<span><i style="background:{COLORES_OBRA[k]}"></i>{escape(o["nombre"])}</span>' for k, o in enumerate(OBRAS))
    cab = "".join(f'<th class="num">{rotulo_mes(a, m)}</th>' for a, m in meses)
    filas = ""
    for k, o in enumerate(OBRAS):
        filas += (f'<tr><td class="col-fija">{escape(o["nombre"])}</td>'
                  + "".join(f'<td class="num">{clp(v[k]) if v[k] else "—"}</td>' for v in meses.values())
                  + f'<td class="num"><b>{clp(sum(v[k] for v in meses.values()))}</b></td></tr>')
    filas += ('<tr class="fila-total"><td class="col-fija">Total</td>'
              + "".join(f'<td class="num">{clp(sum(v))}</td>' for v in meses.values())
              + f'<td class="num">{clp(gastado)}</td></tr>')

    cuerpo = f"""
<div class="cabecera"><h1>Dashboard <span>· Control de gestión</span></h1></div>
{guia("<strong>La mirada de gerencia sobre todas las obras.</strong> Resume cuánto se ha gastado, qué tan consumido va cada presupuesto "
      "y en qué se va el dinero. Toca una tarjeta para ver su análisis en detalle.")}
<section class="tablero">
  <button type="button" class="tarjeta tarjeta-boton" popovertarget="demo">
    <h2>Proyectos y gasto</h2>
    <div class="tablero-cifras">
      <div><span>Obras activas</span><b>{len(OBRAS)}</b></div>
      <div><span>Presupuesto</span><b>{millones(ppto)}</b></div>
      <div><span>Gastado</span><b>{millones(gastado)}</b></div>
    </div>
    <span class="ver-mas">Ver análisis →</span>
  </button>
  <button type="button" class="tarjeta tarjeta-boton" popovertarget="demo">
    <h2>Consumo de presupuestos</h2>
    <ul class="lista-consumo">{consumo}</ul>
    <span class="ver-mas">Ver análisis →</span>
  </button>
  <button type="button" class="tarjeta tarjeta-boton" popovertarget="demo">
    <h2>Materiales más consumidos</h2>
    <ol class="lista-top">{lista_top}</ol>
    <span class="ver-mas">Ver análisis →</span>
  </button>
</section>
<section class="tarjeta bloque">
  <div class="conmuta">
    <input type="radio" name="vista" id="vista-graf" checked>
    <input type="radio" name="vista" id="vista-det">
    <div class="barra-estados">
      <h2>Gasto mensual por obra</h2>
      <div class="segmentado"><label for="vista-graf">Gráfico</label><label for="vista-det">Detalle por obra</label></div>
    </div>
    <div class="panel-estado">{grafico_barras(meses)}<div class="leyenda">{leyenda}</div></div>
    <div class="panel-estado">
      <div class="tabla-scroll"><table><thead><tr><th class="col-fija">Obra</th>{cab}<th class="num">Total</th></tr></thead>
      <tbody>{filas}</tbody></table></div>
    </div>
  </div>
</section>
"""
    pagina("dashboard.html", "Dashboard", cuerpo, "dashboard")


# ── Propuestas ───────────────────────────────────────────────────────────────

VALOR_UF = 39_850
VALOR_HH = 10_500
ETIQUETA_CODIGO = {
    "confirmado": ("tag-confirmado", "Confirmado"),
    "alta": ("tag-alta", "Sugerencia alta"),
    "media": ("tag-media", "Sugerencia media"),
    "baja": ("tag-baja", "Sugerencia baja"),
    "sin": ("tag-sin", "Sin código"),
}


def totales_p001():
    mat = sum(l[4] * l[5] for _, ls in PARTIDAS_P001 for l in ls)
    hh = sum(l[4] * l[6] for _, ls in PARTIDAS_P001 for l in ls)
    directo = mat + hh * VALOR_HH
    margen = 0.246
    uf = round(directo / (1 - margen) / VALOR_UF)
    return dict(mat=mat, hh=hh, directo=directo, uf=uf, margen=1 - directo / (uf * VALOR_UF))


def iniciales(nombre):
    p = nombre.split()
    return (p[0][0] + p[-1][0]).upper()


def pag_propuestas():
    t = totales_p001()
    estados = [("todas", "Todas"), ("borrador", "Borrador"), ("enviada", "Enviada al cliente"),
               ("revision", "En revisión"), ("adjudicada", "Adjudicada")]
    cuenta = {k: sum(1 for p in PROPUESTAS if p[4] == k) for k, _ in estados}
    cuenta["todas"] = len(PROPUESTAS)
    radios = "".join(f'<input type="radio" name="fp" id="fp-{k}"{" checked" if k == "todas" else ""}>' for k, _ in estados)
    chips = "".join(f'<label for="fp-{k}" class="chip-filtro"><i class="punto punto-{k}"></i>{t_}<b>{cuenta[k]}</b></label>'
                    for k, t_ in estados)
    filas = ""
    for n, obra, cliente, resp, est, est_txt, uf, margen, fecha in PROPUESTAS:
        if n == "P-001":
            uf, margen = t["uf"], t["margen"]
            abrir = '<a class="btn btn-chico" href="propuesta-p001.html">Abrir</a>'
        else:
            abrir = boton_bloqueado("Abrir", "En la demo solo se puede abrir la propuesta P-001", clase="btn-chico tip-tabla")
        filas += (f'<tr class="e-{est}"><td class="mono">{n}</td><td><b>{escape(obra)}</b></td><td>{escape(cliente)}</td>'
                  f'<td><span class="persona"><span class="avatar">{iniciales(resp)}</span>{escape(resp)}</span></td>'
                  f'<td><span class="estado estado-p-{est}">{est_txt}</span></td>'
                  f'<td class="num">{f"{uf:,} UF".replace(",", ".") if uf else "—"}</td>'
                  f'<td class="num">{pct(margen) if margen else "—"}</td><td class="num">{fecha}</td><td>{abrir}</td></tr>')
    cuerpo = f"""
<div class="cabecera">
  <h1>Propuestas</h1>
  <div class="cabecera-acciones">
    {boton_bloqueado("Nueva propuesta", "Crearía una propuesta nueva a partir de los análisis de precio unitario de un cliente", primario=True, ico="mas", clase="tip-abajo tip-der")}
  </div>
</div>
{guia("<strong>Las ofertas a clientes, desde el borrador hasta la adjudicación.</strong> Cada propuesta arma su precio "
      "partida por partida con materiales del catálogo de la empresa. Cuando se adjudica, pasa a ser el presupuesto de una obra nueva.")}
<div class="filtro-estados">
  {radios}
  <div class="chips-filtro">{chips}</div>
  <div class="tarjeta tabla-card">
    <div class="tabla-scroll">
      <table>
        <thead><tr><th>N°</th><th>Obra</th><th>Cliente</th><th>Responsable</th><th>Estado</th>
          <th class="num">Precio ofertado</th><th class="num">Margen</th><th class="num">Última modificación</th><th></th></tr></thead>
        <tbody>{filas}</tbody>
      </table>
    </div>
  </div>
</div>
"""
    pagina("propuestas.html", "Propuestas", cuerpo, "propuestas")


def pag_propuesta_detalle():
    t = totales_p001()
    p = PROPUESTAS[0]
    conteo = {}
    filas = ""
    for n, (partida, lineas) in enumerate(PARTIDAS_P001, 1):
        filas += (f'<tr class="fila-partida"><td colspan="9"><b>{n} · {escape(partida)}</b>'
                  f'<span> · {len(lineas)} líneas</span></td></tr>')
        for cod, desc, sub, un, cant, costo, rend, est in lineas:
            conteo[est] = conteo.get(est, 0) + 1
            cls, txt = ETIQUETA_CODIGO[est]
            sel = " seleccionada" if desc == SUGERENCIAS_P001["linea"] else ""
            filas += (f'<tr class="linea{sel}"><td class="mono">{cod or "—"}</td><td>{escape(desc)}</td>'
                      f'<td><span class="tag {cls}">{txt}</span></td><td>{un}</td>'
                      f'<td class="num">{f"{cant:,}".replace(",", ".")}</td><td class="num">{clp(costo)}</td>'
                      f'<td class="num">{clp(cant * costo)}</td><td class="num">{str(rend).replace(".", ",")}</td>'
                      f'<td class="num">{f"{cant * rend:.1f}".replace(".", ",")}</td></tr>')
    resumen_codigos = "".join(
        f'<li><span class="tag {ETIQUETA_CODIGO[k][0]}">{ETIQUETA_CODIGO[k][1]}</span><b>{conteo.get(k, 0)}</b></li>'
        for k in ("confirmado", "alta", "media", "sin"))
    candidatos = ""
    for i, (cod, nom, un, costo, nivel, motivo) in enumerate(SUGERENCIAS_P001["candidatos"]):
        cls, txt = ETIQUETA_CODIGO[nivel]
        candidatos += f"""
<div class="candidato">
  <div class="candidato-cab"><span class="mono">{cod}</span><span class="tag {cls}">{txt}</span></div>
  <b>{escape(nom)}</b>
  <span class="muted">{un} · {clp(costo)} · {escape(motivo)}</span>
  {boton_bloqueado("Usar este código", "Asignaría este código del catálogo a la línea y traería su costo", primario=(i == 0), clase="btn-chico")}
</div>"""

    cuerpo = f"""
<div class="migas"><a href="propuestas.html">Propuestas</a> › {p[0]} · versión 2</div>
<div class="cabecera">
  <div>
    <h1>{escape(p[1])}</h1>
    <p class="cabecera-meta"><span class="estado estado-p-{p[4]}">{p[5]}</span> {escape(p[2])} · Responsable {escape(p[3])}</p>
  </div>
  <div class="cabecera-acciones">
    {boton_bloqueado("Exportar", "Descargaría la propuesta en Excel con su desglose por partida", ico="descargar", clase="tip-abajo")}
    {boton_bloqueado("Enviar al cliente", "Enviaría la propuesta al cliente y la dejaría en estado «Enviada»", clase="tip-abajo")}
    {boton_bloqueado("Adjudicar", "Convertiría la propuesta en el presupuesto inicial de una obra nueva", primario=True, clase="tip-abajo tip-der")}
  </div>
</div>
{guia("<strong>El selector de materiales de la propuesta.</strong> Cada partida lista los materiales que la componen. "
      "El asistente de códigos propone el código del catálogo que mejor calza con cada descripción del cliente; "
      "una persona confirma o elige otro.")}
<section class="kpis">
  <div class="tarjeta kpi"><div class="kpi-rotulo">Materiales</div><div class="kpi-valor">{millones(t["mat"])}</div><div class="kpi-nota">{sum(len(l) for _, l in PARTIDAS_P001)} líneas</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">HH proyectadas</div><div class="kpi-valor">{f"{t['hh']:,.0f}".replace(",", ".")}</div><div class="kpi-nota">según rendimientos</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Costo directo</div><div class="kpi-valor">{millones(t["directo"])}</div><div class="kpi-nota">materiales y mano de obra</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Precio ofertado</div><div class="kpi-valor">{f"{t['uf']:,}".replace(",", ".")} UF</div><div class="kpi-nota">{millones(t["uf"] * VALOR_UF)}</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Margen</div><div class="kpi-valor">{pct(t["margen"])}</div><div class="kpi-nota bien">sobre el mínimo</div></div>
</section>
<div class="editor">
  <div class="editor-tabla tarjeta tabla-card">
    <div class="editor-barra">
      <input type="text" placeholder="Agregar ítem del catálogo: nombre o código" disabled>
      {boton_bloqueado("+ Partida", "Agregaría una partida nueva a la propuesta", clase="tip-der")}
    </div>
    <div class="tabla-scroll">
      <table>
        <thead><tr><th>Código</th><th>Descripción</th><th>Estado del código</th><th>Un</th><th class="num">Cantidad</th>
          <th class="num">Costo unit.</th><th class="num">Subtotal</th><th class="num">Rend.</th><th class="num">HH</th></tr></thead>
        <tbody>{filas}</tbody>
      </table>
    </div>
  </div>
  <aside class="editor-panel">
    <section class="tarjeta panel">
      <h2>Asistente de códigos</h2>
      <ul class="lista-codigos">{resumen_codigos}</ul>
      {boton_bloqueado("Confirmar sugerencias altas", "Confirmaría de una vez todas las líneas con sugerencia alta", clase="btn-ancho")}
    </section>
    <section class="tarjeta panel">
      <h2>Línea seleccionada</h2>
      <p class="linea-sel">{escape(SUGERENCIAS_P001["linea"])}</p>
      <p class="muted panel-nota">Candidatos del catálogo, del más al menos parecido:</p>
      {candidatos}
    </section>
  </aside>
</div>
"""
    pagina("propuesta-p001.html", f"{p[0]} · Propuestas", cuerpo, "propuestas")


# ── Usuarios, perfiles y Mi perfil ───────────────────────────────────────────

def pag_usuarios():
    filas = ""
    for nombre, correo, perfil, obras, estado, ultimo in USUARIOS:
        filas += (f'<tr class="u-{estado.lower()}"><td><span class="persona"><span class="avatar">{iniciales(nombre)}</span><b>{escape(nombre)}</b></span></td>'
                  f'<td>{correo}</td><td>{escape(perfil)}</td><td>{escape(obras)}</td>'
                  f'<td><span class="estado {"estado-cierre" if estado == "Activo" else "estado-inactivo"}">{estado}</span></td>'
                  f'<td class="num">{ultimo}</td>'
                  f'<td>{boton_bloqueado("Editar", "Abriría la ficha para cambiar el perfil, las obras o desactivar a la persona", clase="btn-chico tip-tabla")}</td></tr>')
    activos = sum(1 for u in USUARIOS if u[4] == "Activo")
    cuerpo = f"""
<div class="cabecera">
  <h1>Usuarios</h1>
  <div class="cabecera-acciones">
    <a class="btn" href="perfiles.html">Ver perfiles</a>
    {boton_demo("Agregar usuario", primario=True, ico="mas")}
  </div>
</div>
{guia("<strong>Quién entra al sistema y qué puede ver.</strong> Cada persona tiene un perfil, que define lo que puede hacer, "
      "y una lista de obras, que define dónde puede hacerlo.")}
<div class="filtro-estados filtro-usuarios">
  <input type="radio" name="fu" id="fu-activo" checked>
  <input type="radio" name="fu" id="fu-inactivo">
  <div class="chips-filtro">
    <label for="fu-activo" class="chip-filtro">Activos<b>{activos}</b></label>
    <label for="fu-inactivo" class="chip-filtro">Inactivos<b>{len(USUARIOS) - activos}</b></label>
  </div>
  <div class="tarjeta tabla-card">
    <div class="tabla-scroll">
      <table>
        <thead><tr><th>Nombre</th><th>Correo</th><th>Perfil</th><th>Obras</th><th>Estado</th><th class="num">Último ingreso</th><th></th></tr></thead>
        <tbody>{filas}</tbody>
      </table>
    </div>
  </div>
</div>
"""
    pagina("usuarios.html", "Usuarios", cuerpo, "usuarios")


def pag_perfiles():
    nodos = ""
    for nombre, nivel, desc, acceso in PERFILES:
        n = sum(1 for u in USUARIOS if u[2] == nombre and u[4] == "Activo")
        nodos += (f'<li class="nodo" style="--nivel:{nivel}"><div class="tarjeta nodo-caja">'
                  f'<div><b>{escape(nombre)}</b><p class="muted">{escape(desc)}</p></div>'
                  f'<div class="nodo-datos"><span class="chip">{acceso}</span><span class="chip">{n} persona{"s" if n != 1 else ""}</span></div>'
                  f'</div></li>')
    cuerpo = f"""
<div class="migas"><a href="usuarios.html">Usuarios</a> › Perfiles</div>
<div class="cabecera">
  <h1>Perfiles</h1>
  <div class="cabecera-acciones">{boton_demo("Editar perfiles", primario=True)}</div>
</div>
{guia("<strong>Los perfiles se ordenan en un árbol.</strong> Cada perfil reporta a uno superior, y quien está más arriba "
      "puede administrar a las personas de las ramas que dependen de él.")}
<ul class="arbol">{nodos}</ul>
"""
    pagina("perfiles.html", "Perfiles", cuerpo, "usuarios")


def pag_mi_perfil():
    obras = "".join(f'<li><a href="obra-{o["slug"]}-proyeccion.html">{escape(o["nombre"])}</a><span class="muted">{o["codigo"]}</span></li>' for o in OBRAS)
    cuerpo = f"""
<div class="cabecera"><h1>Mi <span>perfil</span></h1></div>
{guia("<strong>Tus datos y tus obras.</strong> Aquí cada persona revisa con qué perfil entra, a qué obras tiene acceso y cambia su propia contraseña.")}
<div class="perfil-grid">
  <section class="tarjeta panel">
    <div class="perfil-cab"><span class="avatar avatar-grande">UD</span><div><h2>Usuario Demo</h2><p class="muted">demo@ejemplo.cl</p></div></div>
    <dl class="obra-datos">
      <div><dt>Perfil</dt><dd>Gerencia general</dd></div>
      <div><dt>Estado</dt><dd>Activo</dd></div>
      <div><dt>Último ingreso</dt><dd>{HOY}</dd></div>
      <div><dt>Obras</dt><dd>{len(OBRAS)}</dd></div>
    </dl>
    <h3>Obras asignadas</h3>
    <ul class="lista-obras">{obras}</ul>
  </section>
  <section class="tarjeta panel">
    <h2>Cambiar contraseña</h2>
    <label class="campo campo-ancho"><span>Contraseña actual</span><input type="password" value="demo-demo" disabled></label>
    <label class="campo campo-ancho"><span>Contraseña nueva</span><input type="password" disabled></label>
    <label class="campo campo-ancho"><span>Repite la contraseña nueva</span><input type="password" disabled></label>
    <div class="form-botones">
      {boton_bloqueado("Cancelar", "Descartaría los cambios y volvería a la pantalla anterior")}
      {boton_bloqueado("Guardar", "Cambiaría tu contraseña y cerraría tus otras sesiones abiertas", primario=True, clase="tip-der")}
    </div>
  </section>
</div>
"""
    pagina("mi-perfil.html", "Mi perfil", cuerpo, None, perfil_activo=True)


# ── Configuración ────────────────────────────────────────────────────────────

def subnav_config(activo):
    tabs = [("configuracion", "Subcategorías"), ("rendimientos", "Rendimientos")]
    return ('<nav class="subnav" aria-label="Secciones de configuración">'
            + "".join(f'<a href="{k}.html"{" class=\"activo\"" if k == activo else ""}>{t}</a>' for k, t in tabs)
            + "</nav>")


def pag_configuracion():
    bloques = ""
    for c, nombre in CUENTAS:
        filas = ""
        for s in SUBCATEGORIAS[c]:
            n = len({i["cod"] for o in OBRAS for i in o["items"][c] if i["sub"] == s})
            filas += (f'<tr><td>{escape(s)}</td><td class="num">{n}</td>'
                      f'<td>{boton_bloqueado("Editar", "Permitiría cambiar el nombre de la subcategoría", clase="btn-chico tip-tabla")}</td></tr>')
        bloques += (f'<section class="tarjeta tabla-card"><h2 class="tabla-titulo">{nombre}</h2><div class="tabla-scroll"><table>'
                    f'<thead><tr><th>Subcategoría</th><th class="num">Ítems</th><th></th></tr></thead>'
                    f'<tbody>{filas}</tbody></table></div></section>')
    cuerpo = f"""
<div class="cabecera">
  <h1>Configuración</h1>
  <div class="cabecera-acciones">{boton_bloqueado("Nueva subcategoría", "Crearía una subcategoría nueva dentro de una cuenta", primario=True, ico="mas", clase="tip-abajo tip-der")}</div>
</div>
{subnav_config("configuracion")}
{guia("<strong>Las subcategorías ordenan el gasto dentro de cada cuenta.</strong> Son las partidas que se ven en Materiales, "
      "Mano de Obra y GG Obra, y las mismas para todas las obras.")}
<div class="config-grid">{bloques}</div>
"""
    pagina("configuracion.html", "Configuración", cuerpo, "configuracion")


def pag_rendimientos():
    import random
    rnd = random.Random(7)
    cods = {}
    for o in OBRAS:
        for i in o["items"]["mat"]:
            cods[i["cod"]] = i
    filas = ""
    for cod in sorted(cods):
        i = cods[cod]
        rend = round(rnd.uniform(0.02, 0.9) if i["un"] == "ML" else rnd.uniform(0.1, 6), 2)
        filas += (f'<tr><td class="mono">{cod}</td><td>{escape(i["desc"])}</td><td>{i["un"]}</td>'
                  f'<td class="num">{str(rend).replace(".", ",")}</td><td><span class="partida">{escape(i["sub"])}</span></td>'
                  f'<td>{boton_bloqueado("Editar", "Permitiría corregir el rendimiento de este material", clase="btn-chico tip-tabla")}</td></tr>')
    cuerpo = f"""
<div class="cabecera">
  <h1>Configuración</h1>
  <div class="cabecera-acciones">{boton_bloqueado("Carga masiva", "Subiría una planilla con los rendimientos de muchos materiales a la vez", ico="descargar", clase="tip-abajo tip-der")}</div>
</div>
{subnav_config("rendimientos")}
{guia("<strong>Cuántas horas de trabajo toma instalar cada material.</strong> Con estos rendimientos el sistema estima las horas "
      "hombre de una obra o de una propuesta a partir de sus cantidades.")}
<div class="tarjeta tabla-card">
  <div class="tabla-scroll">
    <table>
      <thead><tr><th>Código</th><th>Material</th><th>Un.</th><th class="num">HH por unidad</th><th>Subcategoría</th><th></th></tr></thead>
      <tbody>{filas}</tbody>
    </table>
  </div>
</div>
"""
    pagina("rendimientos.html", "Rendimientos", cuerpo, "configuracion")


def pag_404():
    cuerpo = f"""
<div class="vacio-404 tarjeta">
  <h1>Esta página no existe</h1>
  <p class="muted">Puede que el enlace esté mal escrito. Vuelve a las obras y sigue explorando la demo.</p>
  <a class="btn btn-primario" href="index.html">Ir a Proyectos</a>
</div>
"""
    pagina("404.html", "Página no encontrada", cuerpo, None)


if __name__ == "__main__":
    pag_proyectos()
    for obra in OBRAS:
        pag_proyeccion(obra)
        for c, _ in CUENTAS:
            pag_detalle(obra, c)
    pag_dashboard()
    pag_propuestas()
    pag_propuesta_detalle()
    pag_usuarios()
    pag_perfiles()
    pag_mi_perfil()
    pag_configuracion()
    pag_rendimientos()
    pag_404()
    print("Listo:", len(list(SITIO.glob("*.html"))), "páginas")

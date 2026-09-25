"""Módulo 3 - Lógica de evaluación del almacenamiento (umbrales y cálculos)."""

UMBRAL_ADVERTENCIA = 80.0
UMBRAL_CRITICO = 90.0

DISCO_LIBRE_ADVERTENCIA = 20.0
DISCO_LIBRE_CRITICO = 10.0

_MAX_SIZE_LOG_ILIMITADO = 268435456  # 2 TB: valor de "sin límite" en el log

_ENGINE_EDITION_EXPRESS = 4  # SERVERPROPERTY('EngineEdition')


def porcentaje(parte, total):
    """Porcentaje seguro: devuelve None si el total es 0 o falta un valor."""
    if parte is None or total in (None, 0):
        return None
    return float(parte) * 100.0 / float(total)


def nivel_por_porcentaje(pct):
    if pct is None:
        return "ok"
    if pct >= UMBRAL_CRITICO:
        return "critico"
    if pct >= UMBRAL_ADVERTENCIA:
        return "advertencia"
    return "ok"


def describir_crecimiento(valor, es_porcentaje):
    """Traduce growth / is_percent_growth a texto legible."""
    if valor is None:
        return "Desconocido"
    if int(valor) == 0:
        return "Deshabilitado (tamaño fijo)"
    if es_porcentaje:
        return f"{int(valor)} % del tamaño actual"
    return f"{int(valor) * 8 / 1024:,.0f} MB por evento"


def limite_archivo_mb(tipo, crecimiento_valor, max_size_paginas, asignado_mb):
    """Tamaño máximo que puede alcanzar el archivo, en MB."""
    if crecimiento_valor is not None and int(crecimiento_valor) == 0:
        return float(asignado_mb)          # no crece: el límite es su tamaño actual
    if max_size_paginas is None or int(max_size_paginas) == -1:
        return None
    if tipo == "LOG" and int(max_size_paginas) == _MAX_SIZE_LOG_ILIMITADO:
        return None
    return int(max_size_paginas) * 8 / 1024.0


def describir_limite(limite_mb):
    if limite_mb is None:
        return "Ilimitado (lo limita el disco)"
    return f"{limite_mb:,.2f} MB"


def evaluar_archivo(archivo):
    """Calcula disponible, porcentajes, límite y nivel de riesgo de un archivo."""
    resultado = dict(archivo)
    asignado = float(archivo.get("asignado_mb") or 0)
    usado = archivo.get("usado_mb")
    usado = float(usado) if usado is not None else None

    resultado["disponible_mb"] = (asignado - usado) if usado is not None else None
    resultado["pct_usado"] = porcentaje(usado, asignado)
    resultado["crecimiento"] = describir_crecimiento(
        archivo.get("crecimiento_valor"), archivo.get("crecimiento_es_porcentaje")
    )

    limite = limite_archivo_mb(
        archivo.get("tipo"),
        archivo.get("crecimiento_valor"),
        archivo.get("tamano_maximo_paginas"),
        asignado,
    )
    resultado["limite"] = describir_limite(limite)
    resultado["pct_limite"] = porcentaje(usado, limite) if limite else None

    if usado is None:
        resultado["nivel"] = "advertencia"
        resultado["motivo"] = "No se pudo leer el espacio usado (revisar permisos VIEW DEFINITION)."
        return resultado

    if limite is not None:
        nivel = nivel_por_porcentaje(resultado["pct_limite"])
        motivo = f"Usa {resultado['pct_limite']:.1f} % de su tamaño máximo permitido."
    else:
        nivel = "ok"
        pct = resultado["pct_usado"] or 0
        if pct >= UMBRAL_CRITICO:
            motivo = "Casi lleno, pero crecerá automáticamente (autocrecimiento activo)."
        else:
            motivo = "Espacio suficiente; puede crecer automáticamente."

    if archivo.get("crecimiento_es_porcentaje") and nivel == "ok":
        nivel = "advertencia"
        motivo += " Crecimiento en porcentaje: se recomienda un valor fijo en MB."

    resultado["nivel"] = nivel
    resultado["motivo"] = motivo
    return resultado


def limite_edicion_mb(edicion_info):
    """Límite de tamaño por base de datos (solo archivos de datos) según la edición."""
    if not edicion_info:
        return None
    if edicion_info.get("codigo_edicion") != _ENGINE_EDITION_EXPRESS:
        return None
    version = edicion_info.get("version_mayor") or 0
    gb = 50 if int(version) >= 17 else 10
    return gb * 1024.0


def evaluar_limite_edicion(datos_asignado_mb, limite_mb):
    """Devuelve (pct, nivel) del tamaño de datos respecto al límite de la edición."""
    if limite_mb is None:
        return None, "ok"
    pct = porcentaje(datos_asignado_mb, limite_mb)
    return pct, nivel_por_porcentaje(pct)


def evaluar_volumen(volumen):
    """Agrega pct_libre y nivel a una unidad de disco."""
    resultado = dict(volumen)
    pct_libre = porcentaje(volumen.get("disponible_mb"), volumen.get("total_mb"))
    resultado["pct_libre"] = pct_libre
    if pct_libre is None:
        resultado["nivel"] = "ok"
    elif pct_libre < DISCO_LIBRE_CRITICO:
        resultado["nivel"] = "critico"
    elif pct_libre < DISCO_LIBRE_ADVERTENCIA:
        resultado["nivel"] = "advertencia"
    else:
        resultado["nivel"] = "ok"
    return resultado


def resumir_crecimiento(historial_ascendente):
    """Compara la primera y la última medición (lista en orden ascendente)."""
    if len(historial_ascendente) < 2:
        return None

    primera = historial_ascendente[0]
    ultima = historial_ascendente[-1]
    segundos = (ultima["fecha_captura"] - primera["fecha_captura"]).total_seconds()
    dias = segundos / 86400.0

    delta_usado = float(ultima["datos_usado_mb"]) - float(primera["datos_usado_mb"])
    delta_asignado = float(ultima["total_asignado_mb"]) - float(primera["total_asignado_mb"])

    return {
        "mediciones": len(historial_ascendente),
        "desde": primera["fecha_captura"],
        "hasta": ultima["fecha_captura"],
        "dias": dias,
        "delta_datos_usado_mb": delta_usado,
        "delta_total_asignado_mb": delta_asignado,
        "promedio_diario_datos_mb": (delta_usado / dias) if dias >= 1 else None,
    }


def estimar_dias_hasta_limite(datos_usado_actual_mb, limite_mb, promedio_diario_mb):
    """Estimación lineal de días hasta alcanzar el límite de la edición."""
    if limite_mb is None or not promedio_diario_mb or promedio_diario_mb <= 0:
        return None
    restante = limite_mb - float(datos_usado_actual_mb)
    if restante <= 0:
        return 0.0
    return restante / promedio_diario_mb

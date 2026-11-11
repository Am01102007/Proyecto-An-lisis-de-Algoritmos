"""Protocolo experimental (sección 6): mediana de 5 repeticiones, datos de la máquina."""
import json
import platform
import statistics
import time

from config import REPETICIONES, RESULTADOS


def medir(funcion, *args, repeticiones=REPETICIONES):
    """Ejecuta funcion(*args) y devuelve (mediana en ms, último resultado).

    Solo se mide la llamada a la función: la preparación de datos queda por fuera.
    Si la primera ejecución pasa de un minuto, no se repite (regla 3 del protocolo).
    """
    tiempos = []
    resultado = None
    for _ in range(repeticiones):
        inicio = time.perf_counter_ns()
        resultado = funcion(*args)
        tiempos.append((time.perf_counter_ns() - inicio) / 1e6)
        if tiempos[0] > 60_000:
            break
    return statistics.median(tiempos), resultado


def guardar_maquina():
    """Guarda procesador, RAM, sistema operativo y versión de Python en resultados/maquina.json."""
    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / 2**30, 1)
    except ImportError:
        ram_gb = "instalar psutil o escribir a mano"
    info = {
        "procesador": platform.processor() or platform.machine(),
        "ram_gb": ram_gb,
        "sistema_operativo": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
    }
    (RESULTADOS / "maquina.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return info

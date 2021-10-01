# -*- coding: utf-8 -*-
import inspect
import argparse
import logging
from datetime import datetime
from common import config

# 1) Evito importar todo con importlib.
from importlib import import_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    inicio = datetime.now()
    parser = argparse.ArgumentParser()
    # 2) El nombre de la Clase ingresada,
    # debe ser igual en config.yaml -> ott_sites
    new_site_choices = list(config()['ott_sites'].keys())
    # 3) Parser de argumentos de la terminal:
    parser.add_argument('--c', help='País para Scrapear', type=str)
    parser.add_argument('--o', help='Operación', type=str)
    parser.add_argument('--dIni', help='Fecha Inicio', type=str)
    parser.add_argument('--dEnd', help='Fecha Fin', type=str)
    parser.add_argument('ott_site', help='Sitios Para Scrapear', type=str,
                        choices=new_site_choices)
    parser.add_argument('--p', help='Codigo de Plataformas', type=str)
    parser.add_argument('--date', help='Fecha del log buscado', type=str)
    parser.add_argument('--t', help='Tipo Update', type=str)
    parser.add_argument('--m', help='Varios Paises', type=str, nargs='*')

    args = parser.parse_args()

    ott_site_country = args.c
    ott_operation = args.o
    ott_platforms = args.ott_site
    fechaInicio = args.dIni
    fechaFin = args.dEnd
    plataformas = args.p
    tipo = args.t
    lista = args.m
    logat = args.date
    countries = args.m

    # 4) Indico en formato "string", el nombre del módulo a importar.
    module = None
    module = 'platforms.' + ott_platforms.lower()
    #####################################################
    # IMPORTANTE: El nombre del archivo, debe ser igual #
    # al nombre de la clase.                            #
    # Ejemplo: Clase-> "Pepe", archivo: pepe.py         #
    #                                                   #
    # module = 'platforms.pepe'                         #
    #####################################################

    status_code = 0
    # 5) Obtengo el módulo a importar:
    MODULE_NAME = module
    try:
        # 7) Importo el módulo correcto.
        module = import_module(MODULE_NAME)

        # 8) Hago la instancia de la Clase. La clase == ott_platforms
        PlatformClass = getattr(module, ott_platforms)
    except ModuleNotFoundError as exc:
        print(exc)
        print("\n¡¡¡El nombre del archivo y la clase no coinciden!!!\n")
        print(f"Para importar: \"{ott_platforms}\"...")
        print(f"El archivo debe llamarse: \"{ott_platforms.lower()}.py\"")

        ott_operation = 'no operation'
        status_code = 3

    if ott_operation in ('scraping', 'testing', 'top-ten'):
        _inspected_class = inspect.getfullargspec(PlatformClass)
        args_class = _inspected_class.args
        number_args = len(args_class)
        if number_args > 4 or "countries" in args_class:
            try:
                PlatformClass(ott_platforms, ott_site_country, ott_operation,
                              countries)
            except Exception:
                PlatformClass(ott_platforms, ott_site_country, ott_operation)
        else:
            PlatformClass(ott_platforms, ott_site_country, ott_operation)

    # if ott_operation in ('excel'):
    #     platform_code = config()['ott_sites'][ott_platforms]["countries"].get(ott_site_country)
    #     if platform_code:
    #         from analysis.utils.excel_template import ExcelTemplate
    #         ExcelTemplate.export_excel(platform_code, logat)
    #     else:
    #         print(f"Error in PlatformCode. See config.yaml")

    fin = datetime.now()

    print('Tiempo transcurrido:', fin - inicio)
    exit(status_code)

import redis
import schedule
import time
import os
from datetime import datetime
import sys

REDIS_SERVERS = {
    'local': ('localhost', 6379, None),
    'dev': ('devEnvironmentRedisIP', 80,'fXDzN5hn2utYCvscNdWdRWxGAZC3cT34x2FQ'),
    'qa': ('qaEnvironmentRedisIP', 80, 'REzQHC3R91YZVMK7DAa9QgzGFVSixfceugEH'),
    'pre': ('preEnvironmentRedisIP', 80,'aMKRDHnz7bjcUNGf236UgYDV4N8tCS8bTd5B')
}


def dump_redis_data(env, interval_minutes):
    # Si el env no es uno de los valores válidos, lanzar exception
    if env not in REDIS_SERVERS:
        raise ValueError("Entorno no válido, fistro")

    ip, port, password = REDIS_SERVERS[env]

    # r = redis.Redis(host=ip, port=port, db=0)

    def dump_redis_hierarchy(file_path):
        client = redis.StrictRedis(host=ip, port=port,  password=password, decode_responses=True)

        # Abre el fichero y escribe HSETs a 
        with open(file_path, 'w') as file:
            # Obtiene todas las keys
            keys = client.keys('*')

            for key in keys:
                # Key es un hash?
                if client.type(key) == 'hash':
                    # Obtener fields y values del hash actual
                    hash_data = client.hgetall(key)

                    for field, value in hash_data.items():
                        # Escribir el HSET
                        file.write(f'HSET "{key}" "{field}" "{value}"\n')


    def dump_job():
        # Crear un directorio para la fecha actual si no existe
        current_date = datetime.now().strftime('%Y-%m-%d')
        folder_path = os.path.join(os.getcwd(), current_date)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Nombre del fichero con la hora local
        dump_time = datetime.now().strftime('%H-%M-%S')
        dump_file = f"{env}_{dump_time}"
        dump_file_path = os.path.join(folder_path, dump_file)

        print('Volcando a ', dump_file_path)

        # Volcado de Redis a fichero no te digo de qué tipo
        dump_redis_hierarchy(dump_file_path)

    # Ejecutar el Job de volcado el número de minutos especificado por parámetro
    schedule.every(interval_minutes).minutes.do(dump_job)


    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Parámetros [local|dev|qa|pre] [interval_minutes]")
        sys.exit(1)

    env = sys.argv[1]
    interval_minutes = int(sys.argv[2])

    dump_redis_data(env, interval_minutes)

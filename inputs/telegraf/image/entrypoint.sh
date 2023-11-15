#!/bin/bash

# Establecer los permisos antes de ejecutar el comando principal
mkdir -p /source/data/logs
chown -R telegraf:telegraf /source
chmod -R 755 /source
chown -R telegraf:telegraf /source/data/logs

# Ejecutar el comando principal del contenedor
exec "$@"


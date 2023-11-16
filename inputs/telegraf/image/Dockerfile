FROM telegraf:latest


RUN apt-get update && apt-get install -y python3 python3-requests libxslt1-dev libssl-dev libffi-dev python3-lxml libxml2-dev libxslt-dev python3-pip


RUN pip3 install jinja2-cli[yaml] --break-system-packages
RUN pip3 install PyYAML==5.3.1 --break-system-packages
RUN pip3 install cffi --break-system-packages
RUN pip3 install influxdb  --break-system-packages
RUN pip3 install xmltodict --break-system-packages
RUN pip3 install pexpect --break-system-packages
RUN pip3 install lxml --break-system-packages
RUN pip3 install pytest --break-system-packages
RUN pip3 install mock --break-system-packages
RUN pip3 install yamlreader --break-system-packages
RUN pip3 install junos-eznc==2.2.0 --break-system-packages
RUN pip3 install pandas --break-system-packages 



COPY start.sh /source/start.sh

COPY factcache.py /usr/local/lib/python3.11/dist-packages/jnpr/junos/factcache.py

COPY pfe_exceptions.py /source/pfe_exceptions.py

COPY routers.yaml /source/routers.yaml

COPY credentials.yaml /source/credentials.yaml

RUN chmod +x /source/start.sh


# Copiar y configurar archivos

COPY start.sh /source/start.sh

COPY factcache.py /usr/local/lib/python3.11/dist-packages/jnpr/junos/factcache.py

RUN chmod +x /source/start.sh

COPY entrypoint.sh /source/entrypoint.sh

RUN chmod +x /source/entrypoint.sh

WORKDIR /source

ENTRYPOINT ["/source/entrypoint.sh"]

CMD ["/source/start.sh"]








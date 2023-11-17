![Beta](https://img.shields.io/badge/status-beta-yellowgreen.svg?style=flat "Beta")
# open-nti-mt

OpenNTI is a container packaged with all tools needed to collect and visualize time series data from network devices.

This version has support for the command **show pfe statistics exceptions**

## How to install

1) Clone the repo

```
https://github.com/psagrera/open-nti-mt.git
```

2) Adjust the settings in routers.yaml and credentials.yaml as needed for the **exceptions** section

_Note: This directory will be revamped shortly_

```
cd inputs/telegraf/image/

**routers.yaml**

- hostname: x.x.x.x <--- ip or hostname
  tag: hl3 <-- optional

**credentials.yaml** 

- username: lab
  password: lab123

```
3) Adjust the settings in hosts.yaml, credentials.yaml and commands.yaml as needed for the **traditional** section

   _Note: A parser must exist for each command to be collected. To create a new parser for a command, please refer the section how to create a a new parser_ **How to create a new parser**
```
cd inputs/telegraf/input-netconf/data/

**host.yaml**

hosts:
    192.168.252.64:        lab  vmx <-- ip or hostname and tags

cd inputs/telegraf/input-netconf/data/variables

**credentials.yaml**

lab_credentials:
    username: jncie 
    password: jncie123 
    tags: lab

**commands.yaml**

generic_commands:
   commands: |
      show chassis routing-engine | display xml
      show pfe statistics traffic | display xml
      show task memory | display xml
   tags: lab
```

4) Set the interval time in the data collection at your convenience in the docker-compose file

```
***docker-compose-telegraf.yml***

version: '3.3'

services:
  
  input-netconf:
    build: ./inputs/telegraf/image
    container_name: input-netconf
    environment:
     - "TELEGRAF_AGENT_INTERVAL_SECONDS=120" <--- in seconds
```
5) Run docker-compose file

```
docker-compose -f docker-compose-telegraf.yml up -d
```
6) Verify that containers are up and running

```
docker ps

CONTAINER ID   IMAGE                                 COMMAND                  CREATED          STATUS          PORTS                                                                                  NAMES
e1ecdcf653dc   quay.io/influxdb/chronograf:1.5.0.1   "/usr/bin/chronograf…"   52 minutes ago   Up 51 minutes   0.0.0.0:8888->8888/tcp, :::8888->8888/tcp                                              chronograf
11530952ab25   kapacitor:1.5.0                       "/entrypoint.sh kapa…"   52 minutes ago   Up 51 minutes   0.0.0.0:9092->9092/tcp, :::9092->9092/tcp                                              kapacitor
008b91141c36   open-nti-new_input-netconf            "/source/entrypoint.…"   52 minutes ago   Up 51 minutes   8092/udp, 8125/udp, 8094/tcp                                                           input-netconf
1b537d86a17b   grafana/grafana:5.3.2                 "/run.sh"                52 minutes ago   Up 52 minutes   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp                                              grafana
134c68ea8924   influxdb:1.6.4                        "/entrypoint.sh infl…"   52 minutes ago   Up 52 minutes   0.0.0.0:8086->8086/tcp, :::8086->8086/tcp, 0.0.0.0:8090->8090/tcp, :::8090->8090/tcp   influxdb
```

7) Verify that data are being inserted into the database

```
docker exec -it influxdb /bin/bash
root@134c68ea8924:/# influx
Connected to http://localhost:8086 version 1.6.4
InfluxDB shell version: 1.6.4
> use juniper
Using database juniper
> show measurements
name: measurements
name
----
192.168.252.64.0.discard_route
192.168.252.64.0.discard_route_IPv6
192.168.252.64.0.invalid_L2_token
192.168.252.64.0.invalid_stream
192.168.252.64.0.sw_error
192.168.252.64.0.unknown_family
192.168.252.64.0.unknown_iif <--- **pfe exceptions**
192.168.252.64.chassis.routing-engine.0.cpu-idle <-- **traditional commands**
192.168.252.64.chassis.routing-engine.0.mastership-state
192.168.252.64.chassis.routing-engine.0.memory-buffer-utilization
192.168.252.64.chassis.routing-engine.0.up-time-msec
```
## How to create a new parser

To be done

## How to add / change a new command or credentials

To be done

## How to visualize data

1) **Open grafana at http://localhost:3000 (admin/admin)**

   You should see two preconfigured dashboards

   - Data Agent dashboard
   - PFE exceptions

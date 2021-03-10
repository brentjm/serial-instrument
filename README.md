# serial-instrument-server
Docker containers to provide various multiple protocol interfaces to
communicate to serial enabled instruments (e.g. Mettler Toledo balances. IKA
stirrers, Julabo chillers, Cole Parmer Pumps, ...etc.)

## Example
Start this container system on a wifi enabled microcomputer that is attached to
a serial instrument.  Automatically upon power up of the microcomputer and
serial instrument, the microcomputer will read all available instrument
parameters (i.e. set points, values, ...) and publish them to the MQTT broker
as well as provide an interface to aquire them using HTTP or OPC UA.  Sending
instrument commands is done by sending the following JSON schema as a MQTT
payload, an the body of an HTTP PUT, or writing OPC UA tag.
`
    {
        "user": user_name,
        "password": password,
        "command":
        {
            "command_name", command_name,
            "parameters": parameters"
        }
    }
`

The services running on the microcomputer provide some additional benefits,
such as queuing commands, rate limiting the serial command rate to avoid
serial timing issues, buffering instrument data, "locking" an instrument with
a username and password.

## How it works
- A microcomputer is connected serially to an instrument (e.g. Dsub-9/RS-232).
- The microcomputer contains a docker-compose file that defines multiple services.
  - Each service is specific to a specific instrument and contains a python
    package to convert generalized commands sent over a socket defined by a
    JSON object to vendor specific serial commands.
    - This instrument specific package has a module with a base class *SerialInstrument*.
    - Separate modules for each instrument are available that inherit the *SerialInstrument* and
      overide the methods to retrieve data and add methods to set instrument parameters.
  - Additional services relay the JSON object commands between different network protocols:
    - MQTT
    - HTTP
    - OPC UA

## Get started
1. Clone the serial instrument repo on the desired microcomputer.
2. Edit the *docker-compose.yml* file and define the desired instrument service.
For example,
`
    mettlertoledo:
      build:
        context: .
        dockerfile: ./serial-socket/instruments/mettlertoledo_PG5002S/Dockerfile
      image: mettlertoledo_pg5002s
      container_name: mettlertoledo_pg5002s
      networks:
        - equipment
      ports:
        - "54132:54132"
      devices:
        - "/dev/ttyUSB0:/dev/ttyUSB0"
      restart: unless-stopped
`
3. Edit the *service-variables.env* file and define the variables used by the containers.
`
    HOST="frigg"                 # The host name/IP of the microcomputer is used to define message origin.
    SOCKET_HOST_SERVICE="fake"   # The host name/IP (or service name in docker-compose) is needed for inter-service communication.
    SOCKET_PORT=54132            # The socket port.
    MQTT_BROKER="192.168.1.3"    # The host name/IP of the MQTT Broker.
    CLIENT_ID="frigg"            # Client ID for MQTT (Can be the same as host name of microcomputer).
`
4. Plug the microcomputer into the instrument.
5. Start the services `docker-compose up --build -d`
6. Use the tools from `https://github.com/brentjm/iot-docker-services.git` to
   create database dashboards (*Grafana*), automate data flows and calculations
   (*Node-RED*), and create "digital-twins" (*custom ReactJS drag-n'-drop
   interface*).
   
## Author
   Brent Maranzano

## License
   MIT

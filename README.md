# Tópicos Especiales en Telemática

### Estudiante: Miguel Jaramillo, mjaramil20@eafit.edu.co

### Profesor: Edwin Montoya, emontoya@eafit.edu.co

# P2P - Comunicación entre procesos mediante API REST y RPC

## 1. Breve descripción de la actividad
La actividad consiste en crear una red P2P no estructurada basada en servidor de directorio y localización. Para las comunicaciones se utilizará API REST y gRPC.

### 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
El pclient se comunica correctamente con el pserver a través de gRPC. El pserver se comunica correctamente con el server a través de API REST y se comunica con otros pserver a través de gRPC. Además, todas las funcionalidades (descarga, carga) y las funcionalidades que se derivan de las anteriores mencionadas funcionan satisfactoriamente.

### 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

## 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

![ArquitecturaReto1y2Listo2 drawio](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/e3943e52-d008-4771-a78b-026b2853e246)

La arquitectura es la de una red P2P no estructurado basada en el servidor. El flujo de la comunicación para la carga y descarga de archivos se da de la siguiente manera:

**Carga:**
1. Desde el pclient se le dice por gRPC al pserver que se quiere cargar un archivo.
2. El pserver se comunica con el server a través de RESTAPI para preguntarle por la URL de algún peer.
3. El servidor le devuelve la URL de uno de los otros peers.
4. El pserver se comunica por gRPC con el pserver del otro peer y le dice que quiere cargar un archivo.
5. El pserver del segundo peer revisa si tiene el archivo, en caso de no tenerlo lo agrega a su index y notifica al servidor del nuevo index.
6. El pserver del segundo peer le dice al otro pserver que la carga fue satisfactoria.
7. El pserver le notifica al pclient que se cargó el archivo.
8. El pclient muestra por consola que se logró la carga.

**Descarga:**
1. Desde el pclient se le dice por gRPC al pserver que se quiere descargar un archivo
2. El pserver se comunica con el server a través de RESTAPI para preguntarle por la URL de algún peer que tenga el archivo.
3. El servidor le devuelve la URL de uno de los otros peers.
4. El pserver se comunica por gRPC con el pserver del otro peer y le dice que quiere descargar un archivo en especifico.
5. El pserver del segundo peer revisa si tiene el archivo, en caso de tenerlo le pide al primer peer que lo cargue.
6. El pserver del primer peer recibe el pedido y agrega el archivo del segundo peer a su index.
7. El pserver le notifica al server de su nuevo index.
8. El pclient muestra por consola que se logró la descarga.

## 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus números de versiones.
**Detalles técnicos** </br>
El lenguaje de programación que se utilizó tanto para peer como para server fue `python`. Las librerias que se utilizarón fueron grpcio==1.62.0, grpcio-tools==1.62.0, python-dotenv==1.0.1, flask==3.0.2 y requests==2.31.0. Todas estas en las últimas versiones de cada una. 

**Detalles del desarrollo** </br>
Vamos a dividir el desarrollo en `peer` y `server`.
Para el desarrollo del `peer` primero se dividió este entre pclient y pserver. </br>
`pclient` tendra como principal funcionalidad la CLI que tendra entre sus opciones:
1. **Exit** -> Termina la ejecución del programa.
2. **Download** -> Descarga un archivo.
3. **Upload** -> Carga de archivos.
4. **List index** -> Para ver los archivos que tengo
5. **Logout** -> Para salirse de la sesion mas no terminar ejecución.

Cabe mencionar que al hacer cada uno de estos llamados, pclient a través de gRPC se comunica con pserver para que este se encargue de llevar a cabo cualquiera de estas opciones.

`pserver` sera el encargado de comunicarse con el servidor y con otros peers. Con el servidor se conectara a través de API REST y con los demás peers se comunicará a través de gRPC. 

Los métodos **gRPC** que tiene pserver son:
1. **RequestLogIn** -> Que manda las credenciales al server para verificar si puede iniciar sesión.
2. **RequestLogOut** -> Le notifica al server que ya el peer esta inactivo.
3. **DownloadFile** -> Se encarga de todo el proceso de descargar un archivo este a su vez llama otros métodos.
4. **UploadFile** -> Se encarga de todo el proceso de cargar un archivo este a su vez llama otros métodos.
5. **RequestFile** -> Se encarga principalmente de ver si tiene o no el archivo solicitado.
6. **RequestUpload** -> Se encarga de pedir que el peer guarde un archivo.
7. **RequestPinging** -> Es llamado luego del login para empezar a hacer ping al server.
8. **ListIndex** -> Muestra los archivos que se tiene en el momento.

Los métodos **API REST** que tiene pserver son:
1. **SendIndex** -> Manda al server la lista de archivos del peer.
2. **DownloadRequest** -> Notifica al servidor que se quiere descargar un archivo.
3. **UploadFileRequest** -> Notifica al servidor que se quiere cargar un archivo.
4. **LogIn** -> Le manda las credenciales al servidor para validarlas.
5. **LogOut** -> Le notifica al servidor que el peer va a estar inactivo.
6. **SendPingThread** -> Le manda un ping al servidor periodicamente para informarle que esta activo.

Para estos últimos el `server` les retorna lo siguiente:
1. **index** -> Agrega al diccionario de archivos la URL del peer a los archivos que tenga.
2. **download** -> Devuelve la URL de algun peer activo de manera aleatoria.
3. **upload** -> Devuelve la URL de algun peer activo que tenga el archivo.
4. **login** -> Devuelve si las credenciales son validas y las agrega a un diccionario.
5. **logout** -> Remueve al peer de la lista de activos.
6. **ping** -> Actualiza la última conexion del peer.

Además el `server` tiene un hilo que revisara periodicamente el estado de actividad de los peers para ver si los saca de la lista de peers activos.

**Archivo .proto**
```text
syntax = "proto3";

message File{
	string file_name = 1;
}

message Credentials {
	string username = 1;
	string password = 2;
}

message Url {
	string url = 1;
}

message Reply{
	int32 status_code = 1;
}

message Index {
	repeated string my_list = 1; 
}

message UploadMessage{
	string url = 1;
	string file_name = 2;
}

message Any{

}

service PServer{
   rpc DownloadFile(File) returns (Reply) {}
	rpc UploadFile(File) returns (Reply) {}

	rpc RequestFile(UploadMessage) returns (Reply) {}
	rpc RequestUpload(File) returns (Reply) {}

	rpc RequestLogIn(Credentials) returns (Reply) {}
	rpc RequestLogOut(Url) returns (Reply) {}

	rpc RequestPinging(Any) returns (Reply) {}

	rpc ListIndex(Any) returns (Index) {}
}
```

**Estructura de carpetas** </br>
El proyecto se dividió en 4 carpetas:
1. **peer:** Donde se encuentra todo lo relacionado con el peer como lo es pserver y pclient.
2. **server:** Donde esta todo lo relacionado al servidor.
3. **protos:** Donde se encuentra el archivo .proto.
4. **configs:** Donde se encuentran todos los .env.

![carpetas](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/f6cde53f-f2d2-4c7a-bb8a-01668273640c)

**Ejecución** </br>
El proyecto se ejecuta de la siguiente manera:
1. **Servidor:** Para ejecutar el servidor hay que pararse en la carpeta `./server/` y ejecutar `python server.py`
2. **Peer:** Para ejecutar el peer hay que pararse en la carpeta `./peer/` y ejecutar `python pclient.py ..confis/.env_pclient1 ../configs/.env_pserver1` donde los últimos parametros son archivos de configuración que contienen datos. 

**Configuración de parametros** </br>
Los parametros como el puerto y url se configuran en archivos .env dentro de la carpeta de configs.

**Pantallazos desarrollo** </br>
 
![pantallazodesarrollo](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/0dc5bdb8-0251-42a1-a49d-f18bd35c24af)

![pantallazodesarrollo2](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/694356c6-7f9f-4ab5-82af-a6475b852031)

## 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus números de versiones.

El proyecto se desplegó en AWS con docker.

Se creó un archivo de docker para el servidor:
```text
# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the image
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port the app runs on
RUN export $(cat .env_pserver | xargs)
EXPOSE $PSERVER_PORT
```
y un archivo de docker para el servidor:
```text
# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the image
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port the app runs on
RUN export $(cat .env_server | xargs)
EXPOSE $SERVER_PORT

# Run the application
CMD ["python", "server.py", ".env_server"]
```
Luego se creó una maquina virtual para el servidor y una para el peer siguiendo los lineamientos del primer link de las referencias con las siguientes reglas de seguridad respectivamente:

![image](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/69faa322-250e-4227-9c67-de06cf6fcb41)

![image](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/d7513176-5a19-41ff-b8a1-3c764a8cc5d7)

Luego se accedió a la maquina virtual usando SSH y se ejectaron los siguientes comandos:
```bash
sudo apt update
sudo apt install docker.io -y
sudo apt install docker-compose -y
sudo apt install git -y
sudo systemctl enable docker
sudo systemctl start docker
git clone https://github.com/mstermigol/mjaramil20-st0263
cd mjaramil20-st0263
cd server
```
Luego creamos un archivo llamado `.env_server` donde definiamos la url y puerto del server en nuestro caso:
```text
SERVER_URL="34.201.94.254"
SERVER_PORT="80"
```
Después ejecutabamos los comandos:
```bash
docker build -t server
docker run -d -p 5000:5000
```
Con esto ya tenemos el servidor listo y escuchando peticiones.

Después continuamos con la máquina virtual para el cliente, allí repetimos estos comandos que utilizamos en el server pero con un cambio y es que en el ultimo nos úbicamos en peer:
```bash
sudo apt update
sudo apt install docker.io -y
sudo apt install docker-compose -y
sudo apt install git -y
sudo systemctl enable docker
sudo systemctl start docker
git clone https://github.com/mstermigol/mjaramil20-st0263
cd mjaramil20-st0263
cd peer
```
Luego creamos dos archivos para nuestras configuraciones que van a ser `.env_pclient` y `.env_pserver` que respectivamente tienen:
```text
PSERVER_URL="54.174.76.166"
PSERVER_PORT="5001"
```
```text
PSERVER_URL="54.174.76.166"
PSERVER_PORT="5001"
PSERVER_LOCAL_URL="0.0.0.0"
SERVER_URL="34.201.94.254"
SERVER_PORT="5000" 
```
Una vez creamos estos archivos corremos los siguientes comandos:
```bash
docker build -t peer1 .
docker run -it -p 5000:5000 peer1
docker exec -it {id_imagen} /bin/bash
```
Y luego de correr estos comandos estariamos en una línea de comandos distinta donde ya correriamos nuestro código con:
`python pclient.py .env_pclient .env_pserver`
Y ya estamos listos para usar el programa.

Para ingresar como otro peer, abrimos una terminal nueva, nos conectamos con SSH a la instancia de peer y hacemos el mismo proceso, solo que en los archivos `.env` cambiamos el puerto por otro distinto.

![workingInaws](https://github.com/mstermigol/mjaramil20-st0263/assets/85334763/6578770d-c974-4df4-9428-1cc7053bd1c7)

## 5. Otra información que considere relevante para esta actividad.

### Referencias:
- https://github.com/st0263eafit/st0263-241/tree/main/Laboratorio-RPC
- https://github.com/st0263eafit/st0263-241/tree/main
- https://www.youtube.com/watch?v=WB37L7PjI5k&t=411s

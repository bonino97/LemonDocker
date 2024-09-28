# **README.md**

## **LemonBooster: Plataforma Automatizada de Reconocimiento y Escaneo de Vulnerabilidades**

### **Descripción**

LemonBooster es una plataforma automatizada que integra múltiples herramientas de seguridad para la enumeración, discovery y escaneo de vulnerabilidades. Este README proporciona instrucciones detalladas para instalar y ejecutar LemonBooster en un Droplet de Digital Ocean.

---

## **Índice**

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
   - [1. Conectarse al Droplet](#1-conectarse-al-droplet)
   - [2. Actualizar el Sistema e Instalar Dependencias](#2-actualizar-el-sistema-e-instalar-dependencias)
   - [3. Clonar el Repositorio](#3-clonar-el-repositorio)
   - [4. Construir la Imagen Docker](#4-construir-la-imagen-docker)
   - [5. Ejecutar el Contenedor Docker](#5-ejecutar-el-contenedor-docker)
   - [6. Verificar que el Contenedor Está Corriendo](#6-verificar-que-el-contenedor-está-corriendo)
3. [Uso de la API](#uso-de-la-api)
   - [Ejemplos de Solicitudes](#ejemplos-de-solicitudes)
4. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
   - [Implementar Autenticación](#implementar-autenticación)
   - [Configurar el Firewall](#configurar-el-firewall)
5. [Notas Adicionales](#notas-adicionales)
6. [Créditos](#créditos)

---

## **Requisitos Previos**

- Una cuenta en **Digital Ocean**.
- Un **Droplet** con **Ubuntu 22.04 (LTS)** instalado.
- Acceso SSH al Droplet.
- Claves SSH configuradas para el acceso seguro.
- Git instalado en tu máquina local (para clonar el repositorio si es necesario).

---

## **Instalación**

### **1. Conectarse al Droplet**

Desde tu terminal local, conecta con tu Droplet utilizando SSH:

```bash
ssh root@<IP_DEL_DROPLET>
```

Reemplaza `<IP_DEL_DROPLET>` con la dirección IP pública de tu Droplet.

### **2. Actualizar el Sistema e Instalar Dependencias**

Actualiza los paquetes del sistema e instala Git y Docker:

```bash
# Actualizar el sistema
apt-get update && apt-get upgrade -y

# Instalar Git
apt-get install -y git

# Instalar Docker
apt-get install -y docker.io

# Iniciar y habilitar Docker
systemctl start docker
systemctl enable docker
```

### **3. Clonar el Repositorio**

Clona el repositorio de LemonBooster en tu Droplet:

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

Asegúrate de reemplazar `https://github.com/tu_usuario/tu_repositorio.git` con la URL real de tu repositorio.

### **4. Construir la Imagen Docker**

Construye la imagen Docker utilizando el Dockerfile proporcionado:

```bash
docker build -t lemonbooster -f Dockerfile .
```

Este proceso puede tardar varios minutos, ya que se están instalando todas las herramientas y dependencias.

### **5. Ejecutar el Contenedor Docker**

Inicia el contenedor Docker con el siguiente comando:

```bash
docker run -d -p 8000:8000 --name lemonbooster lemonbooster
```

- `-d`: Ejecuta el contenedor en segundo plano.
- `-p 8000:8000`: Mapea el puerto 8000 del contenedor al puerto 8000 del host.
- `--name lemonbooster`: Nombra el contenedor para facilitar su gestión.

### **6. Verificar que el Contenedor Está Corriendo**

Comprueba que el contenedor está en ejecución:

```bash
docker ps
```

Deberías ver una salida similar a:

```
CONTAINER ID   IMAGE          COMMAND             CREATED          STATUS          PORTS                    NAMES
<CONTAINER_ID> lemonbooster   "/entrypoint.sh"    xx minutes ago   Up xx minutes   0.0.0.0:8000->8000/tcp   lemonbooster
```

---

## **Uso de la API**

La API está disponible en el puerto `8000` de tu Droplet.

### **Ejemplos de Solicitudes**

#### **Ejecutar Nmap**

```bash
curl -X POST http://<IP_DEL_DROPLET>:8000/run \
-H 'Content-Type: application/json' \
-d '{
    "tool": "nmap",
    "args": ["-sV", "scanme.nmap.org"]
}'
```

#### **Ejecutar Amass para Enumeración de Subdominios**

```bash
curl -X POST http://<IP_DEL_DROPLET>:8000/run \
-H 'Content-Type: application/json' \
-d '{
    "tool": "amass",
    "args": ["enum", "-d", "example.com"]
}'
```

#### **Ejecutar Nuclei para Escaneo de Vulnerabilidades**

```bash
curl -X POST http://<IP_DEL_DROPLET>:8000/run \
-H 'Content-Type: application/json' \
-d '{
    "tool": "nuclei",
    "args": ["-u", "https://example.com"]
}'
```

---

## **Consideraciones de Seguridad**

Es fundamental asegurar tu API para evitar accesos no autorizados.

### **Implementar Autenticación**

Modifica el archivo `api/server.py` para incluir autenticación mediante una clave API.

**Paso 1: Editar `server.py`**

```bash
nano api/server.py
```

**Añade el siguiente código al inicio del archivo:**

```python
API_KEY = 'TU_CLAVE_API'
```

**Modifica la función `run_tool()` para incluir la verificación de la clave API:**

```python
@app.route('/run', methods=['POST'])
def run_tool():
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # Resto del código...
```

**Paso 2: Reconstruir la Imagen Docker**

Después de modificar `server.py`, debes reconstruir la imagen Docker:

```bash
docker build -t lemonbooster -f Dockerfile .
```

**Paso 3: Reiniciar el Contenedor**

Detén y elimina el contenedor anterior:

```bash
docker stop lemonbooster
docker rm lemonbooster
```

Inicia un nuevo contenedor:

```bash
docker run -d -p 8000:8000 --name lemonbooster lemonbooster
```

**Paso 4: Enviar Solicitudes Autenticadas**

Incluye el encabezado `X-API-Key` en tus solicitudes:

```bash
curl -X POST http://<IP_DEL_DROPLET>:8000/run \
-H 'Content-Type: application/json' \
-H 'X-API-Key: TU_CLAVE_API' \
-d '{
    "tool": "nuclei",
    "args": ["-u", "https://example.com"]
}'
```

### **Configurar el Firewall**

Utiliza `ufw` para restringir el acceso al puerto 8000:

```bash
# Instalar ufw si no está instalado
apt-get install -y ufw

# Permitir SSH
ufw allow ssh

# Permitir acceso al puerto 8000 solo desde tu IP
ufw allow from <TU_IP> to any port 8000

# Habilitar ufw
ufw enable
```

Reemplaza `<TU_IP>` con la dirección IP desde la cual accederás a la API.

---

## **Notas Adicionales**

- **Actualización de Herramientas**: Para actualizar las herramientas dentro del contenedor, actualiza el `Dockerfile` y reconstruye la imagen.
- **Limitaciones**: Asegúrate de tener el permiso adecuado antes de escanear dominios o sistemas que no te pertenecen.
- **Seguridad**: Nunca expongas la API sin autenticación en entornos de producción.

---

## **Créditos**

- **Autor**: Tu Nombre
- **Repositorio**: [GitHub - tu_usuario/tu_repositorio](https://github.com/tu_usuario/tu_repositorio)
- **Licencia**: MIT

---

## **Ejemplo de Uso Completo**

Supongamos que deseas utilizar `subfinder` para enumerar subdominios de `example.com`.

**Paso 1: Enviar la Solicitud**

```bash
curl -X POST http://<IP_DEL_DROPLET>:8000/run \
-H 'Content-Type: application/json' \
-H 'X-API-Key: TU_CLAVE_API' \
-d '{
    "tool": "subfinder",
    "args": ["-d", "example.com"]
}'
```

**Paso 2: Interpretar la Respuesta**

La API devolverá un JSON con los resultados:

```json
{
  "stdout": "www.example.com\nmail.example.com\n...",
  "stderr": "",
  "returncode": 0
}
```

---

## **Solución de Problemas**

- **El contenedor no se ejecuta**: Verifica los logs del contenedor con `docker logs lemonbooster` para identificar posibles errores.
- **No puedo acceder a la API**: Asegúrate de que el puerto 8000 está abierto y que el firewall está configurado correctamente.
- **Error de autenticación**: Verifica que estás enviando el encabezado `X-API-Key` con la clave correcta.

---

## **Contacto**

Si tienes preguntas o necesitas asistencia adicional, puedes contactarme en:

- **Email**: tu_email@example.com
- **LinkedIn**: [linkedin.com/in/tu_usuario](https://linkedin.com/in/tu_usuario)

---

**Nota**: Siempre respeta las leyes y regulaciones aplicables al realizar pruebas de seguridad y escaneos de vulnerabilidades. Obtén el permiso adecuado antes de escanear sistemas o redes que no te pertenecen.

---

## **Conclusión**

Con este README detallado, deberías poder instalar y ejecutar LemonBooster en tu Droplet de Digital Ocean, y utilizar la API para ejecutar las herramientas de seguridad incluidas. Asegúrate de seguir las consideraciones de seguridad para proteger tu instancia y los sistemas que interactúan con ella.

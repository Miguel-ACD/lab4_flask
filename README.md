# Laboratorio 3 Flask

Aplicacion en Flask para login con codigo de verificacion por correo y CRUD de usuarios.

## Funciones

- Login con usuario, contrasena y correo donde se recibira el codigo.
- Validacion del usuario contra base de datos MySQL.
- Envio de codigo de verificacion por correo usando SMTP.
- Panel de administracion.
- CRUD de usuarios con id, nombre, email y rol.
- Configuracion con Docker y script SQL.

## Requisitos

- Docker Desktop instalado y abierto.
- Una cuenta de Gmail para enviar los codigos.
- Verificacion en 2 pasos activada en la cuenta de Google.
- Una clave de aplicacion de Google para usar SMTP.

## Descargar el proyecto

Se puede descargar el proyecto desde GitHub de dos formas:

Opcion 1: descargar ZIP.

1. Entrar al repositorio en GitHub.
2. Presionar el boton `Code`.
3. Seleccionar `Download ZIP`.
4. Descomprimir el archivo ZIP.
5. Entrar a la carpeta del proyecto descomprimido.

Opcion 2: clonar el repositorio.

```powershell
git clone URL_DEL_REPOSITORIO
cd NOMBRE_DE_LA_CARPETA
```

## Configurar el archivo .env

Crear el archivo `.env` usando el ejemplo:

```powershell
copy .env.example .env
```

Abrir el archivo `.env` y completar estos datos:

```env
SECRET_KEY=coloca_una_clave_secreta
ADMIN_USER=admin
ADMIN_PASSWORD=coloca_una_contrasena
ADMIN_EMAIL=admin@demo.com

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_clave_de_aplicacion
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_DEFAULT_SENDER=tu_correo@gmail.com
```

En `SECRET_KEY` se coloca cualquier texto largo para proteger la sesion de Flask, por ejemplo una frase larga inventada.

En `ADMIN_USER` y `ADMIN_PASSWORD` se define el usuario y contrasena para iniciar sesion en el sistema.

Donde dice `tu_correo@gmail.com`, colocar el correo real que enviara los mensajes.

Ejemplo:

```env
MAIL_USERNAME=micorreo@gmail.com
MAIL_DEFAULT_SENDER=micorreo@gmail.com
```

Donde dice `tu_clave_de_aplicacion`, colocar la clave de aplicacion de Google. No colocar la contrasena normal del correo.

## Crear clave de aplicacion en Gmail

Para crear la clave de aplicacion:

1. Entrar a la cuenta de Google.
2. Ir a `https://myaccount.google.com/security`.
3. Activar la verificacion en 2 pasos si todavia no esta activada.
4. Entrar a `https://myaccount.google.com/apppasswords`.
5. Crear una nueva clave de aplicacion.
6. Copiar la clave generada.
7. Pegarla en `.env`, en esta linea:

```env
MAIL_PASSWORD=clave_generada_por_google
```

Google muestra esa clave una sola vez. Si se pierde, se debe crear otra.

Si no aparece la opcion de claves de aplicacion, puede ser porque la cuenta no tiene verificacion en 2 pasos, es una cuenta de trabajo o estudio con restricciones, o tiene proteccion avanzada activada.

Referencia oficial de Google: `https://support.google.com/accounts/answer/185833`

## Ejecutar el sistema

Despues de completar el archivo `.env`, ejecutar:

```powershell
docker compose down
docker compose up --build
```

Cuando termine de iniciar, abrir:

```text
http://localhost:5000
```

## Probar el login

En la pantalla principal colocar:

```text
Usuario: el valor colocado en ADMIN_USER
Contrasena: el valor colocado en ADMIN_PASSWORD
Correo para recibir el codigo: tu_correo_destino@gmail.com
```

El correo destino puede ser el mismo correo configurado en `.env` o cualquier otro correo real.

Luego revisar la bandeja de entrada del correo destino, copiar el codigo recibido y pegarlo en la pantalla de verificacion.

## Operaciones CRUD

Desde el panel de administracion se puede:

- Crear usuarios.
- Listar usuarios.
- Editar usuarios.
- Eliminar usuarios con confirmacion.

## Si no llega el correo

Revisar:

- Que Docker Desktop este abierto.
- Que el archivo `.env` exista.
- Que `MAIL_USERNAME` tenga el correo real.
- Que `MAIL_DEFAULT_SENDER` tenga el mismo correo real.
- Que `MAIL_PASSWORD` tenga una clave de aplicacion, no la contrasena normal.
- Que la verificacion en 2 pasos este activada.
- Que el correo no haya llegado a spam.

Tambien se puede revisar la consola donde esta corriendo `docker compose up --build` para ver errores.

## Estructura

```text
lab3_flask/
  app.py
  requirements.txt
  schema.sql
  Dockerfile
  docker-compose.yml
  .env.example
  templates/
  static/
```

## Video demostrativo

Video del funcionamiento del sistema:

```text
https://drive.google.com/file/d/1FACQ4GJxeyAPqzs3Q_2Hjluvxc6_Gpzg/view?usp=sharing
```

## Nota importante

El archivo `.env` no se debe subir a GitHub porque contiene el correo y la clave de aplicacion. El archivo que si se sube es `.env.example`, porque solo sirve como ejemplo.

# Manual de instalación y configuración

## 1. Requisitos

Para ejecutar el proyecto se requiere:

* Windows 10/11.
* Python 3.14 o compatible.
* SQL Server 2025 Express o una instancia compatible.
* SQL Server Management Studio (SSMS).
* Microsoft ODBC Driver 17 o 18 for SQL Server.
* Git.

## 2. Clonar el repositorio

Clonar el repositorio y entrar al directorio del proyecto:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd proyecto-admin-sgbd
```

## 3. Crear el entorno virtual

Crear el entorno virtual de Python:

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Si el entorno está activo, la terminal mostrará:

```text
(.venv)
```

## 4. Instalar dependencias

Actualizar pip:

```powershell
python -m pip install --upgrade pip
```

Instalar las dependencias del proyecto:

```powershell
pip install -r requirements.txt
```

Las principales dependencias utilizadas actualmente son:

* `pyodbc`
* `python-dotenv`
* `pandas`
* `plotly`
* `streamlit`

## 5. Configuración de SQL Server

El proyecto utiliza SQL Server como sistema gestor de bases de datos.

La configuración utilizada durante el desarrollo es:

* Motor: SQL Server Express
* Servidor: `DESKTOP-JFIRD2I\SQLEXPRESS`
* Base de datos: `BD_AdminSGBD`
* Usuario de consulta: `adminsgbd_consulta`

El nombre del servidor puede variar dependiendo del equipo de cada integrante.

## 6. Configuración de variables de entorno

El proyecto utiliza un archivo `.env` para almacenar información sensible de conexión.

Crear:

```text
config/.env
```

A partir del archivo de ejemplo:

```text
config/.env.example
```

El archivo `.env` debe contener los valores correspondientes al entorno local del integrante.

> **Importante:** el archivo `config/.env` contiene información sensible y está excluido mediante `.gitignore`. Nunca debe subirse al repositorio.

Cada integrante debe configurar sus propias credenciales y parámetros de conexión.

## 7. Drivers ODBC

La aplicación utiliza `pyodbc` para conectarse a SQL Server.

Verificar los drivers disponibles desde Python:

```powershell
python -c "import pyodbc; print(pyodbc.drivers())"
```

Debe aparecer al menos uno de los siguientes:

```text
ODBC Driver 17 for SQL Server
ODBC Driver 18 for SQL Server
```

## 8. Preparación de la base de datos

Los scripts SQL necesarios se encuentran en:

```text
sql/00-configuracion/
```

Entre ellos se encuentran:

```text
crear_base_pruebas.sql
crear_usuario_consultivo.sql
```

Estos scripts permiten preparar la base de datos y el usuario utilizado para las pruebas de conexión y permisos.

## 9. Probar la conexión

Con el entorno virtual activo, ejecutar:

```powershell
python test_connection.py
```

Una conexión correcta debe mostrar información similar a:

```text
Conexión exitosa.
Servidor: <servidor>
Base actual: BD_AdminSGBD
Versión:
Microsoft SQL Server ...
```

## 10. Probar permisos

Ejecutar:

```powershell
python test_permissions.py
```

La prueba debe mostrar la identidad de la conexión y los permisos efectivos del usuario.

Para el usuario de consulta utilizado durante la configuración se verificaron:

```text
CONNECT
SELECT
```

Esto permite conectarse a la base de datos y realizar consultas sin otorgar permisos de modificación innecesarios.

## 11. Ejecutar la aplicación

Con las dependencias instaladas y la conexión configurada:

```powershell
streamlit run app/app.py
```

Streamlit iniciará el servidor local de la aplicación y mostrará la dirección disponible en la terminal.

## 11.1 Preparar el Módulo 3 (almacenamiento)

Ejecutar en SSMS **como administrador** (autenticación de Windows), en este orden y una sola vez por máquina:

1. `sql/03-almacenamiento/01_crear_objetos_historial.sql` — crea el esquema `monitoreo`, la tabla de historial, el procedimiento de captura y la vista resumen.
2. `sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql` — da al usuario consultivo `VIEW DEFINITION`, `SELECT` sobre `monitoreo` y `EXECUTE` sobre el procedimiento de captura.
3. (Opcional, para la demostración) `sql/03-almacenamiento/03_generar_carga_prueba.sql` — agrega filas reales a una tabla de prueba para que exista crecimiento que medir.

### Captura periódica (Programador de tareas de Windows)

SQL Server Express no incluye SQL Server Agent, así que las mediciones automáticas se programan en Windows. Desde PowerShell, en la raíz del repositorio y con el entorno virtual ya creado:

```powershell
# Probar primero a mano (debe imprimir una línea "OK | BD_AdminSGBD | ...")
.venv\Scripts\python.exe scripts\capturar_almacenamiento.py

# Crear la tarea: una medición cada 6 horas mientras la sesión de Windows esté iniciada.
# StartWhenAvailable: si la computadora estaba apagada a la hora programada, la ejecuta al encender.
$accion     = New-ScheduledTaskAction -Execute "$PWD\scripts\capturar_almacenamiento.bat"
$disparador = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 6)
$ajustes    = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "ProyectoSGBD_CapturaAlmacenamiento" -Action $accion -Trigger $disparador -Settings $ajustes

# Ejecutarla una vez para comprobar
Start-ScheduledTask -TaskName "ProyectoSGBD_CapturaAlmacenamiento"
```

Cada ejecución deja una línea en `logs/captura_almacenamiento.log` (ignorado por Git). Para eliminar la tarea: `Unregister-ScheduledTask -TaskName "ProyectoSGBD_CapturaAlmacenamiento"`.

## 12. Solución de problemas comunes

### Error: no se encuentra el driver ODBC

Verificar los drivers instalados:

```powershell
python -c "import pyodbc; print(pyodbc.drivers())"
```

Si no aparece `ODBC Driver 17 for SQL Server` o `ODBC Driver 18 for SQL Server`, instalar un driver ODBC compatible con SQL Server.

### Error de conexión a SQL Server

Verificar:

1. Que el servicio de SQL Server esté iniciado.
2. Que el nombre del servidor sea correcto.
3. Que la base de datos exista.
4. Que las credenciales configuradas en `config/.env` sean correctas.
5. Que el driver ODBC configurado esté instalado.

### Error relacionado con `.env`

Comprobar que exista:

```text
config/.env
```

y que contenga las variables requeridas por `app/database/connection.py`.

### El archivo `.env` aparece en Git

Ejecutar:

```powershell
git check-ignore -v config\.env
```

El archivo debe aparecer como ignorado por una regla `.env` del `.gitignore`.

## 13. Verificación final

Antes de comenzar el desarrollo, comprobar:

```powershell
python --version
pip --version
python -c "import pyodbc; print(pyodbc.drivers())"
python test_connection.py
python test_permissions.py
git status
```

El proyecto estará correctamente configurado cuando las pruebas de conexión y permisos sean exitosas y el archivo `.env` permanezca fuera del repositorio.

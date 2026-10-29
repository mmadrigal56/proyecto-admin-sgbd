# Manual de instalación y configuración

Este manual prepara la aplicación desde cero en una computadora con Windows. Cada integrante trabaja con su propia instancia local de SQL Server, por lo que los pasos de SQL Server se hacen **una vez en cada máquina**.

## 1. Requisitos

| Programa | Versión probada | Notas |
|---|---|---|
| Windows | 10 / 11 | |
| SQL Server | 2025 Express (17.0.x) | Instancia `SQLEXPRESS` |
| SQL Server Management Studio (SSMS) | Versión actual | Para ejecutar los scripts |
| Microsoft ODBC Driver for SQL Server | 18 | El 17 también funciona cambiando `DB_DRIVER` |
| Python | 3.11, 3.12 o 3.13 | `numpy==2.2.6` no tiene versión para 3.14 |
| Git | Cualquiera reciente | |

## 2. Configurar SQL Server

1. Instalar SQL Server Express con la instancia `SQLEXPRESS`.
2. Activar la **autenticación mixta**: en SSMS, clic derecho sobre el servidor → *Propiedades* → *Seguridad* → *Modo de autenticación de SQL Server y Windows*. Reiniciar el servicio `SQL Server (SQLEXPRESS)`.
3. Comprobarlo en SSMS:

   ```sql
   SELECT SERVERPROPERTY('IsIntegratedSecurityOnly') AS solo_windows;  -- debe devolver 0
   ```

Sin autenticación mixta, la aplicación falla con `Login failed for user 'adminsgbd_consulta'. (18456)` aunque la contraseña sea correcta.

## 3. Clonar el repositorio

```powershell
git clone https://github.com/mmadrigal56/proyecto-admin-sgbd
cd proyecto-admin-sgbd
```

## 4. Crear el entorno virtual e instalar dependencias

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación ("la ejecución de scripts está deshabilitada"):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Con el entorno activo, la línea de la terminal empieza con `(.venv)`. Dependencias principales: `streamlit`, `pyodbc`, `pandas`, `plotly`, `python-dotenv`.

Verificar el controlador ODBC:

```powershell
python -c "import pyodbc; print(pyodbc.drivers())"
```

Debe aparecer `ODBC Driver 18 for SQL Server`.

## 5. Configurar `config/.env`

```powershell
Copy-Item config\.env.example config\.env
code config\.env
```

| Variable | Valor |
|---|---|
| `DB_SERVER` | Servidor e instancia, por ejemplo `localhost\SQLEXPRESS` |
| `DB_NAME` | `BD_AdminSGBD` |
| `DB_USER` / `DB_PASSWORD` | Usuario consultivo y la contraseña definida en el paso 7 |
| `DB_ADMIN_USER` / `DB_ADMIN_PASSWORD` | Usuario administrativo del Módulo 6 y su contraseña |
| `DB_DRIVER` | `ODBC Driver 18 for SQL Server` |
| `DB_TRUST_SERVER_CERTIFICATE` | `yes` en instalaciones locales |

> **Importante:** `config/.env` contiene contraseñas y está excluido por `.gitignore`. Nunca debe subirse al repositorio. Editarlo con VS Code; el Bloc de notas puede no guardar el archivo correctamente.

## 6. Contraseñas en los scripts

Los scripts que crean logins traen la contraseña de ejemplo `CAMBIAR_ESTA_CONTRASEÑA`. Cambiarla **solo en la ventana de SSMS**, ejecutar y cerrar la pestaña **sin guardar**. Si por error se guardó, restaurar el archivo antes de cualquier commit:

```powershell
git restore sql/00-configuracion/crear_usuario_consultivo.sql
```

## 7. Preparar SQL Server: scripts en orden

Ejecutar en SSMS, conectado con **autenticación de Windows** (administrador de la instancia), en este orden:

| # | Script | Qué hace | Obligatorio |
|---|---|---|---|
| 1 | `sql/00-configuracion/crear_base_pruebas.sql` | Crea `BD_AdminSGBD` | Sí |
| 2 | `sql/00-configuracion/crear_usuario_consultivo.sql` | Crea `adminsgbd_consulta` (cambiar contraseña) | Sí |
| 3 | `sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql` | `VIEW SERVER STATE` para las DMV | Sí |
| 4 | `sql/03-almacenamiento/01_crear_objetos_historial.sql` | Esquema `monitoreo`, historial de almacenamiento y procedimiento de captura | Sí |
| 5 | `sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql` | `VIEW DEFINITION`, lectura del historial y ejecución de la captura | Sí |
| 6 | `sql/05-auditoria/00_otorgar_permisos_auditoria.sql` | `VIEW ANY DEFINITION` y lectura de dependencias | Sí |
| 7 | `sql/06-mantenimiento/01_crear_usuario_administrativo.sql` | Crea `adminsgbd_mantenimiento` con `db_ddladmin` (cambiar contraseña) | Sí |
| 8 | `sql/06-mantenimiento/02_otorgar_permisos_mantenimiento.sql` | Permisos de detección y tabla `monitoreo.RegistroMantenimiento` | Sí |
| 9 | `sql/06-mantenimiento/03_crear_procedimientos_mantenimiento.sql` | Procedimientos de mantenimiento y `EXECUTE` para el administrativo | Sí |

SSMS puede subrayar en rojo objetos que todavía no existen al abrir un script (IntelliSense). Los errores reales son los que aparecen en la pestaña *Mensajes* al ejecutar.

### Datos de demostración (opcionales)

| Script | Para qué sirve |
|---|---|
| `sql/02-rendimiento/preparar_escenario_bloqueo.sql` | Provocar un bloqueo real entre dos sesiones (Módulo 2) |
| `sql/03-almacenamiento/03_generar_carga_prueba.sql` | Insertar 20 000 filas reales para generar crecimiento (Módulo 3) |
| `sql/04-respaldos/crear_respaldo.sql` | Crear un respaldo completo en la carpeta predeterminada (Módulo 4) |
| `sql/05-auditoria/05_generar_dependencia_rota.sql` | Crear una vista con dependencia rota (Módulo 5); `06_limpiar_dependencia_rota.sql` la elimina |
| `sql/06-mantenimiento/04_generar_escenario_prueba.sql` | Tabla con índices fragmentados y estadísticas sin actualizar (Módulo 6) |

`sql/04-respaldos/recuperacion_prueba.sql` contiene rutas de la máquina donde se hizo la prueba original: revisarlas antes de ejecutarlo.

## 8. Probar la conexión y los permisos

```powershell
python test_connection.py
python test_permissions.py
```

`test_connection.py` debe mostrar "Conexión exitosa" con el servidor y la base. `test_permissions.py` debe listar al menos `CONNECT` y `VIEW DATABASE STATE`.

## 9. Ejecutar la aplicación

```powershell
.venv\Scripts\Activate.ps1
streamlit run app/app.py
```

Se abre `http://localhost:8501`. La primera vez Streamlit pide un correo opcional: dejarlo vacío y presionar Enter. Para detener la aplicación: `Ctrl + C`.

## 10. Captura periódica del almacenamiento (opcional)

SQL Server Express no permite usar SQL Server Agent, así que las mediciones automáticas del Módulo 3 se programan con el Programador de tareas de Windows. Desde la raíz del repositorio, con el entorno virtual creado:

```powershell
# Probar a mano: debe imprimir "OK | BD_AdminSGBD | ..."
.venv\Scripts\python.exe scripts\capturar_almacenamiento.py

# Crear la tarea (cada 6 horas; si la computadora estaba apagada, se ejecuta al encender)
$accion     = New-ScheduledTaskAction -Execute "$PWD\scripts\capturar_almacenamiento.bat"
$disparador = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 6)
$ajustes    = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "ProyectoSGBD_CapturaAlmacenamiento" -Action $accion -Trigger $disparador -Settings $ajustes
```

Cada ejecución deja una línea en `logs/captura_almacenamiento.log` (ignorado por Git). Para quitar la tarea: `Unregister-ScheduledTask -TaskName "ProyectoSGBD_CapturaAlmacenamiento"`.

## 11. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Login failed for user ... (18456)` | Autenticación solo de Windows, o contraseña distinta a la de `.env` | Paso 2; revisar `config/.env` |
| `Data source name not found` / `IM002` | Falta el ODBC Driver 18 o `DB_DRIVER` no coincide | Instalar el controlador o ajustar `DB_DRIVER` |
| `Faltan variables de entorno: ...` | `config/.env` incompleto o no guardado | Revisar el paso 5 |
| `No module named 'streamlit'` | El entorno virtual no está activo | `.venv\Scripts\Activate.ps1` |
| Tablas vacías en Almacenamiento o Mantenimiento aunque haya datos | Falta `VIEW DEFINITION` o `SELECT` en esa máquina | Ejecutar los scripts 5 y 8 del paso 7 |
| Logins incompletos en Auditoría | Falta `VIEW ANY DEFINITION` | Script 6 del paso 7 |
| El Módulo 6 dice que faltan variables administrativas | `DB_ADMIN_USER` / `DB_ADMIN_PASSWORD` sin configurar | Paso 5 |
| Un cambio en `app/database/queries/` no se refleja | Streamlit no recarga los módulos importados | Detener con `Ctrl + C` y volver a ejecutar |
| `pip install` falla en `numpy` | Python 3.14 | Usar Python 3.11–3.13 |

Para confirmar que `.env` está ignorado:

```powershell
git check-ignore -v config\.env
```

## 12. Verificación final

La instalación está completa cuando:

- `python test_connection.py` y `python test_permissions.py` terminan sin errores.
- `streamlit run app/app.py` muestra "Conexión exitosa con SQL Server" en Inicio.
- Las siete páginas del menú (Inicio y módulos 1 a 6) cargan sin errores rojos.
- `git status` no muestra `config/.env`.

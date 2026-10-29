# Sistema para el monitoreo, administración y auditoría de un SGBD

Proyecto grupal del curso **EIF402 — Administración de Bases de Datos**, Universidad Nacional de Costa Rica, II ciclo 2026.

Aplicación web local que monitorea, administra y audita una instancia real de **Microsoft SQL Server**. Toda la información se obtiene directamente del SGBD mediante vistas de catálogo, vistas de administración dinámica (DMV) y procedimientos almacenados propios; no se usan datos simulados en lugar de las consultas administrativas.

## Módulos

| # | Módulo | Qué permite hacer |
|---|---|---|
| 1 | Estado de la instancia | Servidor, instancia, edición, versión, estado operativo, hora de inicio, tiempo de actividad, memoria del proceso y bases de datos |
| 2 | Rendimiento | Consultas de mayor consumo (CPU, duración, lecturas), sesiones activas y sesiones bloqueadas/bloqueadoras |
| 3 | Almacenamiento | Espacio asignado, utilizado y disponible; archivos, filegroups, disco, límite de la edición, objetos de mayor tamaño e historial de crecimiento con captura periódica |
| 4 | Respaldos | Último respaldo, tipo, tamaño, estado, antigüedad e historial registrado en `msdb` |
| 5 | Auditoría | Logins, usuarios, roles de servidor y de base, permisos con filtros y objetos con dependencias rotas |
| 6 | Mantenimiento | Detección de estadísticas desactualizadas e índices fragmentados; actualización y `REORGANIZE`/`REBUILD` con usuario administrativo, confirmación previa e historial |

## Tecnologías

| Componente | Tecnología |
|---|---|
| SGBD | Microsoft SQL Server 2025 Express |
| Lenguaje | Python 3.11 o superior (probado con 3.11, 3.12 y 3.13) |
| Interfaz | Streamlit 1.62 |
| Conexión | `pyodbc` + ODBC Driver 18 for SQL Server |
| Procesamiento y gráficos | pandas, Plotly |
| Configuración | `python-dotenv` (`config/.env`) |
| Control de versiones | Git y GitHub (ramas y pull requests hacia `main`) |

## Inicio rápido

Requisitos: Windows 10/11, SQL Server Express con autenticación mixta, SSMS, ODBC Driver 18, Python y Git.

```powershell
git clone https://github.com/mmadrigal56/proyecto-admin-sgbd
cd proyecto-admin-sgbd
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config\.env.example config\.env   # completar servidor y contraseñas locales
```

Luego, en SSMS y como administrador, ejecutar los scripts de `sql/` en el orden indicado en el [manual de instalación](docs/manuales/instalacion.md#7-preparar-sql-server-scripts-en-orden), y finalmente:

```powershell
python test_connection.py
streamlit run app/app.py
```

La aplicación abre en `http://localhost:8501`.

## Seguridad

- La aplicación usa dos cuentas de SQL Server con permisos mínimos:
  - `adminsgbd_consulta`: solo lectura; la usan todos los módulos para consultar.
  - `adminsgbd_mantenimiento`: rol `db_ddladmin` en `BD_AdminSGBD` (no `sysadmin`); solo la usa el Módulo 6 para ejecutar mantenimiento, después de una confirmación explícita.
- Las escrituras de la aplicación (mediciones de almacenamiento y registro de mantenimiento) pasan por procedimientos almacenados; ninguna cuenta recibe `INSERT` directo sobre las tablas de registro.
- Las credenciales viven solo en `config/.env`, excluido por `.gitignore`. El repositorio solo contiene `config/.env.example` con valores de ejemplo.

## Documentación

| Documento | Contenido |
|---|---|
| [Manual de instalación](docs/manuales/instalacion.md) | Preparar el entorno desde cero, scripts SQL en orden, configuración y solución de problemas |
| [Manual de usuario](docs/manuales/usuario.md) | Cómo usar cada módulo e interpretar sus resultados |
| [Manual técnico](docs/tecnica/manual-tecnico.md) | Arquitectura, estructura del código, consultas, objetos creados, permisos y decisiones de diseño |
| [Arquitectura](docs/arquitectura/arquitectura.md) | Capas de la solución y flujo de datos |
| [Matriz de requerimientos](docs/matriz-requerimientos.md) | Estado y evidencia de cada requerimiento |
| [Bitácora](docs/bitacora/bitacora.md) | Avances, decisiones, problemas y soluciones por semana |
| [Informe de pruebas](evidencias/semana-09/informe_pruebas.md) | Nueve pruebas de integración con evidencia |

## Estructura del repositorio

```text
proyecto-admin-sgbd/
├── app/
│   ├── app.py                  # Punto de entrada y menú (st.navigation)
│   ├── inicio.py               # Página de inicio y prueba de conexión
│   ├── pages/                  # Una página por módulo (1 a 6)
│   ├── database/
│   │   ├── connection.py       # Conexión consultiva y administrativa
│   │   └── queries/            # Consultas de cada módulo
│   └── services/               # Lógica de evaluación (umbrales del Módulo 3)
├── config/.env.example         # Plantilla de configuración sin credenciales
├── docs/                       # Manuales, arquitectura, matriz y bitácora
├── evidencias/semana-NN/       # Capturas y archivos de continuidad de cada semana
├── scripts/                    # Captura periódica de almacenamiento (Programador de tareas)
├── sql/00-configuracion … 06-mantenimiento/
├── test_connection.py
├── test_permissions.py
└── requirements.txt
```

## Organización del trabajo

| Semana | Responsable | Entrega |
|---|---|---|
| 1 | Mariana Madrigal | Requisitos, arquitectura y repositorio |
| 2 | Javier Garita | Instalación, configuración y conexión |
| 3 | Andrey Solís | Módulo 1 — Estado de la instancia |
| 4 | Nicole Masís | Módulo 2 — Rendimiento |
| 5 | Juan Artavia | Módulo 3 — Almacenamiento |
| 6 | Mariana Madrigal | Módulo 4 — Respaldos y recuperación |
| 7 | Javier Garita | Módulo 5 — Auditoría |
| 8 | Andrey Solís | Módulo 6 — Mantenimiento preventivo |
| 9 | Nicole Masís | Integración y pruebas |
| 10 | Juan Artavia | Documentación, presentación y entrega |

Cada semana dejó un archivo de continuidad en `evidencias/semana-NN/`.

## Limitaciones conocidas

- SQL Server Express no permite usar SQL Server Agent: la captura periódica del Módulo 3 se programa con el Programador de tareas de Windows.
- Cada integrante trabaja con su propia instancia local; los scripts de `sql/` deben ejecutarse una vez en cada máquina.
- Los módulos 3, 4 y 6 trabajan sobre la base configurada en `DB_NAME` (`BD_AdminSGBD`).
- El historial de respaldos refleja lo registrado en `msdb`; comprobar que una copia se puede recuperar requiere una restauración de prueba.

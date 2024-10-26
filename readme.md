# 🎭 Generador de Identidades Simuladas v1.0

## 📖 Descripción

El Generador de Identidades Simuladas es una herramienta de software diseñada con fines educativos para crear perfiles ficticios detallados y coherentes. Utiliza la API de Anthropic y el modelo de lenguaje Claude 3.5 Sonnet para generar datos realistas que pueden ser utilizados para poblar bases de datos de prueba, crear escenarios de entrenamiento, o para cualquier otro propósito educativo que requiera datos personales simulados.

⚠️ **Aviso importante**: Este proyecto es exclusivamente para fines educativos y de investigación. No debe utilizarse para crear identidades falsas con intención de engaño o para cualquier actividad ilegal.

## 🌟 Características

- Generación de datos personales ficticios
- Creación de historias familiares coherentes
- Simulación de historiales educativos
- Generación de experiencias laborales realistas
- Creación de perfiles psicológicos detallados
- Generación de otros datos adicionales (mascotas, vehículos, hobbies, etc.)
- Opción para guardar las identidades generadas en formatos JSON o TXT

## 🛠️ Requisitos

- Python 3.7 o superior
- Conexión a Internet
- API Key de Anthropic

## 📦 Instalación

1. Clone este repositorio:
   ```
   git clone https://github.com/686f6c61/generador-identidades-simuladas.git
   ```

2. Navegue al directorio del proyecto:
   ```
   cd generador-identidades-simuladas
   ```

3. Instale las dependencias necesarias:
   ```
   pip install -r requirements.txt
   ```

## 🔑 Configuración de la API Key

Para utilizar este programa, necesitará una API Key de Anthropic. Siga estos pasos para obtenerla y configurarla:

1. Visite [https://www.anthropic.com](https://www.anthropic.com) y cree una cuenta si aún no tiene una.
2. Una vez que tenga acceso, busque la sección para generar una API Key.
3. Copie la API Key generada.
4. En el directorio raíz del proyecto, cree un archivo llamado `.env`.
5. Abra el archivo `.env` y añada la siguiente línea, reemplazando `YOUR_API_KEY` con su API Key real:
   ```
   ANTHROPIC_API_KEY=YOUR_API_KEY
   ```
6. Guarde y cierre el archivo `.env`.

⚠️ **Nota**: Nunca comparta su API Key ni la suba a repositorios públicos.

## 🚀 Uso

Para ejecutar el programa, use el siguiente comando en la terminal:
python profile.py

## 📋 Menú Principal

1. Generar datos personales
2. Generar historia familiar
3. Generar historial educativo
4. Generar experiencia laboral
5. Generar perfil psicológico
6. Generar otros datos
7. Generar identidad completa
8. Guardar identidad en archivo (JSON o TXT)
9. Salir

## 🧠 Modelo de IA Utilizado

Este proyecto utiliza el modelo `claude-3-5-sonnet-20241022` de Anthropic, que es la versión más reciente de Claude 3.5 Sonnet al momento de la creación de este proyecto. Este modelo ofrece capacidades avanzadas de generación de texto y comprensión de contexto, lo que permite crear identidades simuladas altamente detalladas y coherentes.

## 💾 Guardado de Datos

Las identidades generadas pueden guardarse en dos formatos:

- **JSON**: Ideal para su uso posterior en aplicaciones o para análisis de datos.
- **TXT**: Un formato legible para humanos, perfecto para revisión rápida o uso en documentos.

## 🛡️ Privacidad y Seguridad

- Todas las identidades generadas son completamente ficticias.
- Los datos no se almacenan en ningún servidor externo; solo se guardan localmente si el usuario lo solicita.
- Se recomienda no utilizar información real o sensible como entrada para la generación de identidades.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si desea contribuir al proyecto:

1. Haga un fork del repositorio
2. Cree una nueva rama para su característica
3. Realice sus cambios
4. Envíe un pull request

Por favor, asegúrese de actualizar las pruebas según corresponda y adherirse al código de conducta del proyecto.

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo `LICENSE` para más detalles.

## 👤 Autor

- GitHub: [@686f6c61](https://github.com/686f6c61)

## 🙏 Agradecimientos

- Anthropic por proporcionar acceso a su API y al modelo Claude 3.5 Sonnet.
- Todos los contribuyentes y usuarios que ayudan a mejorar este proyecto.

---

🔍 Para cualquier pregunta, problema o sugerencia, por favor abra un issue en este repositorio.

¡Gracias por usar el Generador de Identidades Simuladas! 🌟

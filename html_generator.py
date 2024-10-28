import os
import json
from datetime import datetime
from jinja2 import Template
import shutil

class GeneradorHTML:
    def __init__(self):
        self.template_base = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ perfil.datos_personales.nombre_completo }} - Perfil</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .profile-image { max-width: 300px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .section-title { border-bottom: 2px solid #007bff; padding-bottom: 0.5rem; margin-bottom: 1.5rem; color: #0056b3; }
        .card { margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .timeline-item { position: relative; padding-left: 20px; margin-bottom: 10px; }
        .timeline-item:before { content: '•'; position: absolute; left: 0; color: #007bff; }
        .skill-badge { background-color: #e9ecef; padding: 5px 10px; border-radius: 15px; margin: 2px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container py-5">
        <!-- Datos Personales -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body text-center">
                        <img src="images/{{ imagen }}" alt="Foto de perfil" class="profile-image mb-3">
                        <h2 class="card-title">{{ perfil.datos_personales.nombre_completo }}</h2>
                        <p class="text-muted">{{ perfil.datos_personales.edad }} años</p>
                        <hr>
                        <div class="text-start">
                            <p><strong>DNI:</strong> {{ perfil.datos_personales.dni }}</p>
                            <p><strong>Dirección:</strong> {{ perfil.datos_personales.direccion }}</p>
                            <p><strong>Sexo:</strong> {{ perfil.datos_personales.sexo }}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <!-- Datos Biométricos -->
                <div class="card">
                    <div class="card-body">
                        <h3 class="section-title">Datos Biométricos</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Altura:</strong> {{ perfil.datos_personales.datos_biometricos.altura }}</p>
                                <p><strong>Peso:</strong> {{ perfil.datos_personales.datos_biometricos.peso }}</p>
                                <p><strong>Constitución:</strong> {{ perfil.datos_personales.datos_biometricos.constitucion }}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Color de ojos:</strong> {{ perfil.datos_personales.datos_biometricos.color_ojos }}</p>
                                <p><strong>Color de pelo:</strong> {{ perfil.datos_personales.datos_biometricos.color_pelo }}</p>
                                {% if perfil.datos_personales.datos_biometricos.marcas_visibles %}
                                <p><strong>Marcas visibles:</strong> {{ perfil.datos_personales.datos_biometricos.marcas_visibles }}</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Historia Familiar -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Historia Familiar</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h4>Padres</h4>
                        <p><strong>Padre:</strong> {{ perfil.historia_familiar.padres.padre.nombre }} ({{ perfil.historia_familiar.padres.padre.edad }} años)<br>
                        {{ perfil.historia_familiar.padres.padre.profesion }}</p>
                        <p><strong>Madre:</strong> {{ perfil.historia_familiar.padres.madre.nombre }} ({{ perfil.historia_familiar.padres.madre.edad }} años)<br>
                        {{ perfil.historia_familiar.padres.madre.profesion }}</p>
                    </div>
                    <div class="col-md-6">
                        <h4>Hermanos</h4>
                        {% for hermano in perfil.historia_familiar.hermanos %}
                        <p><strong>{{ hermano.nombre }}</strong> ({{ hermano.edad }} años)<br>
                        {{ hermano.profesion }}</p>
                        {% endfor %}
                    </div>
                </div>
                
                <h4 class="mt-4">Eventos Importantes</h4>
                <div class="timeline">
                    {% for evento in perfil.historia_familiar.eventos_importantes %}
                    <div class="timeline-item">{{ evento }}</div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Educación -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Educación</h3>
                <div class="mb-4">
                    <h4>Universidad</h4>
                    <p><strong>{{ perfil.educacion.universidad.carrera }}</strong><br>
                    {{ perfil.educacion.universidad.centro }}<br>
                    {{ perfil.educacion.universidad.periodo }}</p>
                    {% if perfil.educacion.universidad.notas_destacadas %}
                    <p><em>{{ perfil.educacion.universidad.notas_destacadas }}</em></p>
                    {% endif %}
                </div>

                <h4>Otros Cursos</h4>
                {% for curso in perfil.educacion.otros_cursos %}
                <div class="mb-3">
                    <p><strong>{{ curso.nombre }}</strong><br>
                    {{ curso.centro }} ({{ curso.año }})<br>
                    Duración: {{ curso.duracion }}</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Experiencia Laboral -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Experiencia Laboral</h3>
                {% for trabajo in perfil.experiencia.trabajos %}
                <div class="mb-4">
                    <h4>{{ trabajo.cargo }}</h4>
                    <p class="text-muted">{{ trabajo.empresa }} | {{ trabajo.periodo }}</p>
                    
                    <h5>Responsabilidades:</h5>
                    <ul>
                    {% for resp in trabajo.responsabilidades %}
                        <li>{{ resp }}</li>
                    {% endfor %}
                    </ul>

                    <h5>Logros:</h5>
                    <ul>
                    {% for logro in trabajo.logros %}
                        <li>{{ logro }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endfor %}

                <h4>Habilidades</h4>
                <div class="mb-3">
                    {% for habilidad in perfil.experiencia.habilidades %}
                    <span class="skill-badge">{{ habilidad }}</span>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Perfil Psicológico -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Perfil Psicológico</h3>
                
                <div class="row mb-4">
                    {% for rasgo, datos in perfil.perfil_psicologico.rasgos_principales.items() %}
                    <div class="col-md-6 mb-3">
                        <h4 class="text-capitalize">{{ rasgo }}</h4>
                        <p><strong>Puntuación:</strong> {{ datos.puntuacion }}/10</p>
                        <ul>
                        {% for ejemplo in datos.ejemplos %}
                            <li>{{ ejemplo }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% endfor %}
                </div>

                <h4>Fortalezas</h4>
                <ul class="mb-4">
                {% for fortaleza in perfil.perfil_psicologico.fortalezas %}
                    <li>{{ fortaleza }}</li>
                {% endfor %}
                </ul>

                <h4>Áreas de Mejora</h4>
                <ul class="mb-4">
                {% for area in perfil.perfil_psicologico.areas_mejora %}
                    <li>{{ area }}</li>
                {% endfor %}
                </ul>

                <h4>Estilo de Comunicación</h4>
                <p>{{ perfil.perfil_psicologico.estilo_comunicacion.descripcion }}</p>
                <p><strong>Muletillas comunes:</strong> {{ perfil.perfil_psicologico.estilo_comunicacion.muletillas|join(', ') }}</p>
            </div>
        </div>

        <!-- Perfil Social -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Perfil Social</h3>
                
                <!-- Viajes -->
                <div class="mb-4">
                    <h4>Viajes en España</h4>
                    {% if perfil.perfil_social.viajes.viajes_espana %}
                        {% for viaje in perfil.perfil_social.viajes.viajes_espana %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>{{ viaje.lugar }}</h5>
                                <p><strong>Fecha:</strong> {{ viaje.fecha }}</p>
                                <p><strong>Duración:</strong> {{ viaje.duracion }}</p>
                                <p><strong>Motivo:</strong> {{ viaje.motivo }}</p>
                                <p><strong>Acompañantes:</strong> {{ viaje.acompanantes }}</p>
                                {% if viaje.anecdota %}
                                <p><strong>Anécdota:</strong> {{ viaje.anecdota }}</p>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}

                    <h4 class="mt-4">Viajes Internacionales</h4>
                    {% if perfil.perfil_social.viajes.viajes_internacional %}
                        {% for viaje in perfil.perfil_social.viajes.viajes_internacional %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>{{ viaje.lugar }}, {{ viaje.pais }}</h5>
                                <p><strong>Fecha:</strong> {{ viaje.fecha }}</p>
                                <p><strong>Duración:</strong> {{ viaje.duracion }}</p>
                                <p><strong>Motivo:</strong> {{ viaje.motivo }}</p>
                                <p><strong>Acompañantes:</strong> {{ viaje.acompanantes }}</p>
                                {% if viaje.anecdota %}
                                <p><strong>Anécdota:</strong> {{ viaje.anecdota }}</p>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}
                </div>

                <!-- Hábitos Sociales y Alimentación -->
                <div class="mb-4">
                    <h4>Hábitos Sociales y Alimentación</h4>
                    <p><strong>Estilo de alimentación:</strong> {{ perfil.perfil_social.social.estilo_alimentacion }}</p>
                    
                    <h5 class="mt-3">Platos Favoritos</h5>
                    {% for plato in perfil.perfil_social.social.platos_favoritos %}
                    <div class="card mb-3">
                        <div class="card-body">
                            <h6>{{ plato.nombre }}</h6>
                            <p><strong>Receta:</strong> {{ plato.receta }}</p>
                            <p><strong>Ocasión:</strong> {{ plato.ocasion }}</p>
                        </div>
                    </div>
                    {% endfor %}

                    <h5 class="mt-3">Últimas Reuniones Sociales</h5>
                    {% for reunion in perfil.perfil_social.social.ultimas_reuniones %}
                    <div class="card mb-3">
                        <div class="card-body">
                            <p><strong>Fecha:</strong> {{ reunion.fecha }}</p>
                            <p><strong>Menú:</strong> {{ reunion.menu }}</p>
                            <p><strong>Invitados:</strong> {{ ", ".join(reunion.invitados) }}</p>
                            <p><strong>Música:</strong> {{ ", ".join(reunion.musica) }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Otros Datos -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Otros Datos</h3>
                
                {% if perfil.otros_datos.mascota.tiene %}
                <h4>Mascota</h4>
                <p><strong>{{ perfil.otros_datos.mascota.raza }}</strong> llamado/a {{ perfil.otros_datos.mascota.nombre }} ({{ perfil.otros_datos.mascota.edad }} años)</p>
                {% endif %}

                <h4>Conducción</h4>
                {% if perfil.otros_datos.conduccion.coche.conduce %}
                <p><strong>Coche:</strong> {{ perfil.otros_datos.conduccion.coche.marca }} {{ perfil.otros_datos.conduccion.coche.modelo }} ({{ perfil.otros_datos.conduccion.coche.anos }} años)<br>
                Carnet desde hace {{ perfil.otros_datos.conduccion.coche.edad_carnet }} años</p>
                {% endif %}

                <h4>Hobbies</h4>
                {% for hobby in perfil.otros_datos.hobbies %}
                <div class="mb-3">
                    <p><strong>{{ hobby.nombre }}:</strong> {{ hobby.descripcion }}</p>
                </div>
                {% endfor %}

                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Color favorito:</strong> {{ perfil.otros_datos.color_favorito }}</p>
                        <p><strong>Estilo de vestimenta:</strong> {{ perfil.otros_datos.estilo_vestimenta }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Talla de ropa:</strong> {{ perfil.otros_datos.talla_ropa }}</p>
                        <p><strong>Talla de zapatos:</strong> {{ perfil.otros_datos.talla_zapatos }}</p>
                    </div>
                </div>
            </div>
        </div>

        {% if pareja %}
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="section-title">Perfil de la Pareja</h3>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Nombre:</strong> {{ pareja.nombre_apellidos }}</p>
                        <p><strong>Edad:</strong> {{ pareja.edad }}</p>
                        <p><strong>Profesión:</strong> {{ pareja.profesion }}</p>
                        <p><strong>Estudios:</strong> {{ pareja.estudios }}</p>
                        <p><strong>Trabajo Actual:</strong> {{ pareja.trabajo_actual }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Personalidad:</strong> {{ pareja.personalidad }}</p>
                        <p><strong>Gustos:</strong> {{ pareja.gustos }}</p>
                        <p><strong>Conduce:</strong> {{ 'Sí' if pareja.conduce else 'No' }}</p>
                        {% if pareja.coche.tiene %}
                        <p><strong>Coche:</strong> {{ pareja.coche.marca }} {{ pareja.coche.modelo }}</p>
                        {% endif %}
                    </div>
                </div>
                
                <h4>Lo que más le gusta de {{ perfil.datos_personales.nombre_completo }}:</h4>
                <ul>
                    {% for gusto in pareja.cosas_que_le_gustan %}
                    <li>{{ gusto }}</li>
                    {% endfor %}
                </ul>

                <h4>Lo que menos le gusta de {{ perfil.datos_personales.nombre_completo }}:</h4>
                <ul>
                    {% for detesta in pareja.cosas_que_detesta %}
                    <li>{{ detesta }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

    def generar_html(self, perfil_json, ruta_imagen=None):
        """Genera un archivo HTML con los datos del perfil y opcionalmente una imagen"""
        try:
            # Cargar el perfil
            if isinstance(perfil_json, str):
                with open(perfil_json, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
            else:
                perfil = perfil_json

            # Obtener el DNI del perfil
            dni = perfil['datos_personales']['dni']
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Crear directorio para el perfil HTML
            directorio = f'perfiles_html/{dni}_{fecha}'
            os.makedirs(f'{directorio}/images', exist_ok=True)

            # Manejar la imagen si existe
            nombre_imagen = None
            if ruta_imagen:
                nombre_imagen = os.path.basename(ruta_imagen)
                shutil.copy2(ruta_imagen, f'{directorio}/images/{nombre_imagen}')

            # Generar el HTML
            template = Template(self.template_base)
            html_content = template.render(
                perfil=perfil,
                imagen=nombre_imagen,
                pareja=perfil.get('perfil_pareja', None)  # Añadir el perfil de la pareja al contexto de la plantilla
            )

            # Guardar el HTML
            ruta_html = f'{directorio}/index.html'
            with open(ruta_html, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"\n✅ Vista HTML generada en: {ruta_html}")
            return ruta_html

        except Exception as e:
            print(f"\n❌ Error al generar el HTML: {e}")
            return None










import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import re

class GeneradorStorytelling:
    """Clase para generar storytelling narrativo de identidades simuladas"""
    
    def __init__(self):
        """Inicializa el generador de storytelling y configura la API"""
        self.modelo = "gpt-4-turbo-preview"
        self.configurar_api()
        
    def configurar_api(self):
        """Configura y valida la API key de OpenAI"""
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            print("❌ No se encontró la API key de OpenAI")
            self.solicitar_api_key()
        else:
            try:
                # Intentar hacer una llamada simple para validar la API key
                self.client = OpenAI(api_key=self.api_key)
                self.client.models.list()
                # Eliminado el mensaje duplicado aquí
            except Exception as e:
                print(f"❌ Error al validar la API key de OpenAI: {e}")
                self.solicitar_api_key()

    def solicitar_api_key(self):
        """Solicita al usuario que introduzca su API key de OpenAI"""
        print("\n=== SOLICITUD DE API KEY DE OPENAI ===")
        print("La API key de OpenAI comienza con 'sk-' y tiene ~51 caracteres")
        self.api_key = input("Por favor, introduce tu API key de OpenAI: ").strip()
        
        if self.api_key.startswith('sk-') and len(self.api_key) > 40:
            # Guardar en .env
            try:
                with open('.env', 'a') as f:
                    f.write(f"\nOPENAI_API_KEY={self.api_key}")
                print("✅ API key guardada en .env")
            except Exception as e:
                print(f"⚠️ No se pudo guardar en .env: {e}")
        else:
            print("❌ API key no válida. Debe comenzar con 'sk-' y tener la longitud adecuada")
            self.solicitar_api_key()

    def estimar_costo(self, prompt, respuesta):
        """Estima el coste de la generación (ahora silencioso)"""
        try:
            tokens_entrada = len(prompt.split()) * 1.3  # Estimación aproximada
            tokens_salida = len(respuesta.split()) * 1.3
            costo = (tokens_entrada * 0.01 + tokens_salida * 0.03) / 1000
            return costo
        except:
            return 0

    def seleccionar_estilo_narrativo(self):
        """Permite al usuario seleccionar el estilo narrativo deseado"""
        print("\n=== SELECCIÓN DE ESTILO NARRATIVO ===")
        print("1. Narrativa Literaria (estilo novela)")
        print("2. Dossier Profesional (estilo informe)")
        print("3. Perfil Periodístico (estilo reportaje)")
        print("4. Biografía Técnica (estilo CV expandido)")
        print("5. Informe Psicológico (estilo clínico)")
        
        estilos = {
            "1": {
                "nombre": "Narrativa Literaria",
                "instrucciones": """Genera una narrativa en estilo novelístico, con un tono personal 
                y emotivo. Incluye diálogos, descripciones vívidas y desarrollo de personajes.""",
                "tono": "personal y emotivo",
                "formato": "párrafos narrativos fluidos"
            },
            "2": {
                "nombre": "Dossier Profesional",
                "instrucciones": """Crea un informe detallado y estructurado, con un tono formal 
                y profesional. Organiza la información en secciones claras, usando lenguaje preciso 
                y objetivo. Incluye análisis de antecedentes y patrones de comportamiento.""",
                "tono": "formal y analítico",
                "formato": "secciones estructuradas con subtítulos"
            },
            "3": {
                "nombre": "Perfil Periodístico",
                "instrucciones": """Desarrolla un perfil al estilo de reportaje periodístico de 
                profundidad. Combina hechos objetivos con observaciones perspicaces y citas 
                contextuales. Mantén un equilibrio entre información y narrativa.""",
                "tono": "investigativo y descriptivo",
                "formato": "estilo artículo de revista"
            },
            "4": {
                "nombre": "Biografía Técnica",
                "instrucciones": """Genera una biografía detallada con enfoque en logros y 
                capacidades técnicas. Estructura cronológica clara con énfasis en desarrollo 
                profesional y habilidades. Incluye métricas y datos específicos.""",
                "tono": "técnico y profesional",
                "formato": "cronológico con métricas"
            },
            "5": {
                "nombre": "Informe Psicológico",
                "instrucciones": """Crea un perfil psicológico detallado con análisis de 
                comportamiento, patrones de personalidad y motivaciones. Usa terminología 
                técnica apropiada y estructura de informe clínico.""",
                "tono": "clínico y analítico",
                "formato": "informe técnico psicológico"
            }
        }
        
        while True:
            opcion = input("\nSeleccione el estilo narrativo (1-5): ").strip()
            if opcion in estilos:
                estilo = estilos[opcion]
                print(f"\n✅ Seleccionado: {estilo['nombre']}")
                return estilo
            else:
                print("❌ Opción no válida. Por favor, seleccione un número del 1 al 5.")

    def generar_historia_seccion(self, seccion, datos, contexto_previo="", estilo_narrativo=None):
        """Genera la narrativa para una sección específica de la identidad"""
        if not estilo_narrativo:
            estilo_narrativo = {
                "nombre": "Narrativa Literaria",
                "instrucciones": "Genera una narrativa en estilo novelístico",
                "tono": "personal y emotivo",
                "formato": "párrafos narrativos fluidos"
            }

        prompts = {
            "datos_personales": f"""Escribe sobre esta persona siguiendo el estilo {estilo_narrativo['nombre']}.
            {estilo_narrativo['instrucciones']}
            
            Mantén el tono {estilo_narrativo['tono']} y usa el formato de {estilo_narrativo['formato']}.""",
            
            "historia_familiar": """Desarrolla la historia familiar de esta persona como una narrativa 
            coherente y emotiva. Incluye anécdotas familiares, relaciones entre los miembros y 
            momentos significativos que han moldeado a la familia.""",
            
            "educacion": """Narra el viaje educativo de esta persona, destacando no solo los logros 
            académicos sino también las experiencias que lo/la formaron como individuo. Incluye 
            detalles sobre profesores memorables, desafíos superados y momentos de crecimiento personal.""",
            
            "experiencia": """Cuenta la historia profesional como un viaje de desarrollo personal y 
            profesional. Incluye los desafíos enfrentados, lecciones aprendidas y cómo cada experiencia 
            ha contribuido a su crecimiento.""",
            
            "perfil_psicologico": """Describe la complejidad psicológica de esta persona, sus 
            motivaciones profundas, miedos, esperanzas y sueños. Incluye cómo su personalidad 
            se manifiesta en diferentes situaciones y relaciones.""",
            
            "otros_datos": """Explora los aspectos únicos de su vida diaria, sus pasiones, 
            rituales personales y las pequeñas cosas que hacen que esta persona sea quien es."""
        }

        prompt = f"""{prompts.get(seccion, "Describe esta información de manera narrativa:")}

        Información disponible:
        {json.dumps(datos, indent=2, ensure_ascii=False)}

        Contexto previo de la historia:
        {contexto_previo}

        Instrucciones adicionales:
        - Mantén un tono consistente y personal
        - Incluye detalles específicos que hagan la historia más vívida
        - Evita repeticiones con el contexto previo
        - Usa transiciones naturales entre ideas
        - Mantén un equilibrio entre descripción y narración"""

        try:
            print(f"Generando narrativa para {seccion}...")
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
                presence_penalty=0.6,
                frequency_penalty=0.6
            )
            
            narrativa = response.choices[0].message.content.strip()
            
            # Estimar y mostrar el coste
            costo = self.estimar_costo(prompt, narrativa)
            print(f"💰 Costo estimado para {seccion}: ${costo:.4f}")
            
            return narrativa
            
        except Exception as e:
            print(f"❌ Error al generar narrativa para {seccion}: {e}")
            return None

    def generar_storytelling_completo(self, identidad):
        """Genera una historia completa a partir de todos los datos de la identidad"""
        print("\n📝 Generando storytelling completo...")
        
        # Solicitar estilo narrativo
        estilo_narrativo = self.seleccionar_estilo_narrativo()
        
        historia_completa = []
        contexto_acumulado = ""

        # Orden específico para la narrativa
        secciones = [
            "datos_personales",
            "historia_familiar",
            "educacion",
            "experiencia",
            "perfil_psicologico",
            "otros_datos"
        ]

        for seccion in secciones:
            if seccion in identidad and identidad[seccion]:
                print(f"Generando narrativa para: {seccion}...")
                narrativa = self.generar_historia_seccion(
                    seccion, 
                    identidad[seccion],
                    contexto_acumulado,
                    estilo_narrativo
                )
                if narrativa:
                    historia_completa.append(narrativa)
                    contexto_acumulado += "\n" + narrativa

        return "\n\n".join(historia_completa)

    def guardar_storytelling(self, historia, nombre_base):
        """Guarda la historia generada en un archivo TXT"""
        if not os.path.exists('historias'):
            os.makedirs('historias')
            
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"historias/{nombre_base}_{fecha}_historia.txt"
        
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as file:
                file.write(historia)
            print(f"✅ Historia guardada como: {nombre_archivo}")
            return nombre_archivo
        except Exception as e:
            print(f"❌ Error al guardar la historia: {e}")
            return None

    def listar_perfiles_guardados(self):
        """Lista todos los perfiles guardados (JSON y TXT) y permite seleccionar uno"""
        archivos = []
        
        # Buscar en la carpeta 'perfiles' (JSON)
        if os.path.exists('perfiles'):
            archivos.extend([
                ('json', f) for f in os.listdir('perfiles') 
                if f.endswith('.json')
            ])
        
        # Buscar en la carpeta 'historias' (TXT)
        if os.path.exists('historias'):
            archivos.extend([
                ('txt', f) for f in os.listdir('historias') 
                if f.endswith('.txt')
            ])
        
        if not archivos:
            print("❌ No hay perfiles guardados")
            return None
        
        print("\n=== PERFILES GUARDADOS ===")
        for i, (tipo, archivo) in enumerate(archivos, 1):
            nombre = archivo.replace('.json', '').replace('.txt', '')
            print(f"{i}. [{tipo.upper()}] {nombre}")
        
        while True:
            try:
                seleccion = input("\nSeleccione el número del perfil (0 para cancelar): ")
                if seleccion == "0":
                    return None
                
                indice = int(seleccion) - 1
                if 0 <= indice < len(archivos):
                    tipo, archivo = archivos[indice]
                    if tipo == 'json':
                        ruta = os.path.join('perfiles', archivo)
                        with open(ruta, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    else:  # tipo == 'txt'
                        ruta = os.path.join('historias', archivo)
                        return self.extraer_datos_txt(ruta)
                else:
                    print("❌ Selección no válida")
            except ValueError:
                print("❌ Por favor, introduzca un número válido")
            except Exception as e:
                print(f"❌ Error al cargar el archivo: {e}")
        return None

    def extraer_datos_txt(self, ruta):
        """Extrae datos estructurados de un archivo TXT"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Diccionario para almacenar las secciones
            datos = {
                "datos_personales": {},
                "historia_familiar": {},
                "educacion": {},
                "experiencia": {},
                "perfil_psicologico": {},
                "otros_datos": {}
            }
            
            # Detectar secciones en el texto
            secciones = re.split(r'\n(?=DATOS PERSONALES:|HISTORIA FAMILIAR:|EDUCACIÓN:|EXPERIENCIA:|PERFIL PSICOLÓGICO:|OTROS DATOS:)', contenido)
            
            for seccion in secciones:
                if seccion.strip():
                    if seccion.startswith('DATOS PERSONALES:'):
                        datos['datos_personales'] = self.extraer_datos_personales(seccion)
                    elif seccion.startswith('HISTORIA FAMILIAR:'):
                        datos['historia_familiar'] = {'contenido': seccion.strip()}
                    elif seccion.startswith('EDUCACIÓN:'):
                        datos['educacion'] = {'contenido': seccion.strip()}
                    elif seccion.startswith('EXPERIENCIA:'):
                        datos['experiencia'] = {'contenido': seccion.strip()}
                    elif seccion.startswith('PERFIL PSICOLÓGICO:'):
                        datos['perfil_psicologico'] = {'contenido': seccion.strip()}
                    elif seccion.startswith('OTROS DATOS:'):
                        datos['otros_datos'] = {'contenido': seccion.strip()}
            
            return datos
            
        except Exception as e:
            print(f"❌ Error al procesar el archivo TXT: {e}")
            return None

    def extraer_datos_personales(self, seccion):
        """Extrae datos personales específicos del texto"""
        datos = {}
        
        # Patrones de búsqueda para datos personales
        patrones = {
            'nombre_completo': r'Nombre:?\s*([^\n]+)',
            'edad': r'Edad:?\s*(\d+)',
            'sexo': r'Sexo:?\s*([^\n]+)',
            'dni': r'DNI:?\s*([^\n]+)',
            'direccion': r'Dirección:?\s*([^\n]+)'
        }
        
        # Extraer datos biométricos
        datos['datos_biometricos'] = {}
        biometricos = {
            'altura': r'Altura:?\s*([^\n]+)',
            'peso': r'Peso:?\s*([^\n]+)',
            'color_ojos': r'Color de ojos:?\s*([^\n]+)',
            'color_pelo': r'Color de pelo:?\s*([^\n]+)',
            'constitucion': r'Constitución:?\s*([^\n]+)',
            'marcas_visibles': r'Marcas visibles:?\s*([^\n]+)'
        }
        
        # Extraer datos básicos
        for campo, patron in patrones.items():
            match = re.search(patron, seccion, re.IGNORECASE)
            if match:
                datos[campo] = match.group(1).strip()
        
        # Extraer datos biométricos
        for campo, patron in biometricos.items():
            match = re.search(patron, seccion, re.IGNORECASE)
            if match:
                datos['datos_biometricos'][campo] = match.group(1).strip()
        
        return datos

    def generar_perfil_completo(self):
        """Genera un perfil completo nuevo usando Claude"""
        print("\n=== GENERANDO PERFIL COMPLETO PARA STORYTELLING ===")
        
        prompt_perfil = """Genera un perfil completo y coherente que incluya todas estas secciones:

        1. DATOS PERSONALES:
        - Nombre completo
        - Edad
        - DNI
        - Dirección
        - Datos biométricos (altura, peso, color ojos, pelo, constitución, marcas visibles)

        2. HISTORIA FAMILIAR:
        - Padres
        - Hermanos
        - Historia familiar detallada
        - Eventos importantes

        3. HISTORIAL EDUCATIVO:
        - Educación primaria y secundaria
        - Estudios superiores
        - Cursos y certificaciones
        - Logros académicos

        4. EXPERIENCIA LABORAL:
        - Trayectoria profesional
        - Empresas y cargos
        - Logros y responsabilidades
        - Habilidades desarrolladas

        5. PERFIL SOCIAL:
        - 5 últimos viajes por España (lugares y fechas)
        - 2 viajes internacionales
        - Estilo de alimentación
        - Platos favoritos
        - Últimas reuniones sociales

        6. PERFIL PSICOLÓGICO:
        - Personalidad
        - Motivaciones
        - Miedos y aspiraciones
        - Forma de relacionarse

        7. OTROS DATOS:
        - Hobbies e intereses
        - Habilidades especiales
        - Rutinas diarias
        - Peculiaridades

        Genera un perfil coherente y detallado. Devuelve los datos en formato JSON estructurado."""

        try:
            print("Generando perfil base...")
            perfil = self.client.chat.completions.create(
                model=self.modelo,
                messages=[{"role": "user", "content": prompt_perfil}],
                temperature=0.8,
                max_tokens=3000
            )
            
            # Extraer el JSON de la respuesta
            contenido = perfil.choices[0].message.content
            json_match = re.search(r'\{.*\}', contenido, re.DOTALL)
            if json_match:
                datos_perfil = json.loads(json_match.group())
                return datos_perfil
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")

        except Exception as e:
            print(f"❌ Error al generar perfil completo: {e}")
            return None

    def generar_storytelling_desde_cero(self):
        """Genera un perfil completo y su storytelling"""
        try:
            # Generar perfil completo
            datos_perfil = self.generar_perfil_completo()
            if not datos_perfil:
                return None

            # Preguntar si desea guardar el perfil
            guardar = input("\n¿Desea guardar el perfil generado? (s/n): ").lower()
            if guardar == 's':
                print("\nSeleccione el formato de guardado:")
                print("1. JSON (recomendado para reutilización)")
                print("2. TXT (más legible)")
                print("3. Ambos formatos")
                
                formato = input("Seleccione una opción (1-3): ")
                
                if formato in ['1', '3']:
                    nombre_archivo = f"perfiles/perfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    os.makedirs('perfiles', exist_ok=True)
                    with open(nombre_archivo, 'w', encoding='utf-8') as f:
                        json.dump(datos_perfil, f, ensure_ascii=False, indent=2)
                    print(f"✅ Perfil guardado en JSON: {nombre_archivo}")
                
                if formato in ['2', '3']:
                    nombre_archivo = f"perfiles/perfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    os.makedirs('perfiles', exist_ok=True)
                    with open(nombre_archivo, 'w', encoding='utf-8') as f:
                        for seccion, datos in datos_perfil.items():
                            f.write(f"\n{seccion.upper()}:\n")
                            f.write(json.dumps(datos, ensure_ascii=False, indent=2))
                            f.write("\n" + "="*50 + "\n")
                    print(f"✅ Perfil guardado en TXT: {nombre_archivo}")

            # Generar storytelling
            print("\nGenerando storytelling del perfil...")
            historia = self.generar_storytelling_completo(datos_perfil)
            if historia:
                nombre_base = datos_perfil.get('datos_personales', {}).get('nombre_completo', 'perfil')
                archivo = self.guardar_storytelling(historia, nombre_base)
                if archivo:
                    print(f"\n✨ ¡Historia narrativa guardada exitosamente!")
                    return True

            return False

        except Exception as e:
            print(f"❌ Error al generar storytelling desde cero: {e}")
            return False






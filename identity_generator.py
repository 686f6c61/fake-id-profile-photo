import os
from datetime import datetime
import json
import random
from dotenv import load_dotenv
from anthropic import Anthropic
import re
from photo_generator import GeneradorFotos
from storytelling_generator import GeneradorStorytelling
from wiki_manager import WikipediaManager
from openai import OpenAI
from html_generator import GeneradorHTML

class GeneradorIdentidadClaude:
    def __init__(self):
        self.configurar_api()
        self.generador_fotos = GeneradorFotos()
        self.identidad = {
            "datos_personales": None,
            "historia_familiar": None,
            "educacion": None,
            "experiencia": None,
            "perfil_psicologico": None,
            "perfil_pareja": None,
            "otros_datos": None,
            "foto_perfil": None,  # Nueva clave para guardar la ruta de la foto
            "perfil_social": None
        }
        self.wiki_manager = WikipediaManager()

    def configurar_api(self):
        """Configura las APIs necesarias"""
        load_dotenv()
        
        # Configurar Claude
        api_key_claude = os.getenv('ANTHROPIC_API_KEY')
        if api_key_claude:
            self.anthropic = Anthropic(api_key=api_key_claude)
            print("✅ API key de Claude configurada correctamente")
        else:
            print("❌ No se encontró la API key de Claude")
            return False
        
        # Configurar Stability AI
        api_key_stability = os.getenv('STABILITY_API_KEY')
        if api_key_stability:
            print("✅ API key de Stability AI configurada correctamente")
        else:
            print("❌ No se encontró la API key de Stability AI")
            return False
        
        # Configurar OpenAI (una sola vez)
        api_key_openai = os.getenv('OPENAI_API_KEY')
        if api_key_openai:
            try:
                self.openai_client = OpenAI(api_key=api_key_openai)
                self.openai_client.models.list()
                print("✅ API key de OpenAI configurada correctamente")
            except Exception as e:
                print(f"❌ Error al validar la API key de OpenAI: {e}")
                return False
        else:
            print("❌ No se encontró la API key de OpenAI")
            return False
        
        # Configurar Wikipedia
        try:
            self.wiki_manager = WikipediaManager()
            # Hacer una búsqueda de prueba para validar
            test_result = self.wiki_manager.wiki.page("España")
            if test_result.exists():
                print("✅ API de Wikipedia configurada correctamente")
            else:
                print("❌ Error al validar la API de Wikipedia")
                return False
        except Exception as e:
            print(f"❌ Error al configurar Wikipedia: {e}")
            return False
        
        return True

    def validar_dni(self, numero):
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        
        # Extraer número y letra
        numero_str = str(numero)[:-1]
        letra_proporcionada = str(numero)[-1].upper()
        
        # Calcular letra correcta
        letra_calculada = letras[int(numero_str) % 23]
        
        return letra_proporcionada == letra_calculada

    def generar_dni(self):
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        numero = random.randint(10000000, 99999999)
        letra = letras[numero % 23]
        return f"{numero}{letra}"

    def generar_datos_personales(self, preferencias=None):
        print("\nGenerando datos personales...")
        prompt = """Genera datos personales ficticios para una identidad simulada. 
        Incluye:
        - Nombre completo
        - Sexo (Hombre/Mujer)
        - Edad (entre 18 y 65 años)
        - DNI (en formato 12345678X)
        - Dirección completa en España
        - Datos biométricos:
            - Altura
            - Peso
            - Color de ojos
            - Color de pelo
            - Constitución (Atlético, Delgado, Robusto, etc.)
            - Marcas de nacimiento, heridas o señales visibles (si las hay)
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {
            "nombre_completo": "",
            "sexo": "",
            "edad": 0,
            "dni": "",
            "direccion": "",
            "datos_biometricos": {
                "altura": "",
                "peso": "",
                "color_ojos": "",
                "color_pelo": "",
                "constitucion": "",
                "marcas_visibles": ""
            }
        }"""

        if preferencias:
            prompt += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,  # Aumentado a 2500
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extraer el contenido de texto de la respuesta
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            # Extraer el JSON de la respuesta
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                datos = json.loads(json_str.group())
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            # Validar y regenerar DNI si es necesario
            while not self.validar_dni(datos['dni']):
                datos['dni'] = self.generar_dni()
                
            self.identidad["datos_personales"] = datos
            print("✅ Datos personales generados correctamente")
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f"❌ Error al generar datos personales: {e}")
            print("Respuesta de Claude:", content)
        return None

    def generar_historia_familiar(self, preferencias=None):
        print("\nGenerando historia familiar...")
        
        if not self.identidad["datos_personales"] or "sexo" not in self.identidad["datos_personales"]:
            print("❌ Error: Primero debes generar los datos personales")
            return None
        
        # Preguntar si tiene pareja
        tiene_pareja = input("¿Desea que tenga pareja? (s/n): ").lower() == 's'
        
        if tiene_pareja:
            print("\nSeleccione el tipo de pareja:")
            print("1. Novio")
            print("2. Novia")
            print("3. Otro (especificar)")
            
            while True:
                opcion_pareja = input("Seleccione una opción (1-3): ")
                
                if opcion_pareja == "1":
                    tipo_pareja = "novio"
                    break
                elif opcion_pareja == "2":
                    tipo_pareja = "novia"
                    break
                elif opcion_pareja == "3":
                    tipo_pareja = input("Por favor, especifique el tipo de pareja: ").lower()
                    break
                else:
                    print("❌ Opción no válida. Por favor, seleccione 1, 2 o 3.")
        
        prompt = f"""Genera una historia familiar ficticia coherente para esta persona:
        {json.dumps(self.identidad['datos_personales'], indent=2)}
        
        Incluye:
        - Información sobre padres (nombres, edades, profesiones)
        - Información sobre hermanos si los hay
        - Información sobre abuelos
        - Exactamente 15 eventos familiares importantes
        - 6 amigos cercanos con la siguiente información para cada uno:
            - Nombre y apellidos
            - Estudios
            - Ciudad de residencia
            - Lugar actual de trabajo
            - Situación sentimental
            - Nombre de la pareja (si aplica)
        - Situación sentimental: {"En pareja con su " + tipo_pareja if tiene_pareja else "Soltero/a"}
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {{
            "padres": {{
                "padre": {{
                    "nombre": "",
                    "edad": 0,
                    "profesion": ""
                }},
                "madre": {{
                    "nombre": "",
                    "edad": 0,
                    "profesion": ""
                }}
            }},
            "hermanos": [],
            "abuelos": {{
                "paternos": {{}},
                "maternos": {{}}
            }},
            "eventos_importantes": [],
            "amigos": [
                {{
                    "nombre_apellidos": "",
                    "estudios": "",
                    "ciudad_residencia": "",
                    "trabajo_actual": "",
                    "situacion_sentimental": "",
                    "pareja": ""
                }}
            ],
            "situacion_sentimental": ""
        }}
        
        Asegúrate de que "eventos_importantes" contenga exactamente 15 eventos y "amigos" contenga exactamente 6 amigos."""

        if preferencias:
            prompt += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                datos = json.loads(json_str.group())
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            self.identidad["historia_familiar"] = datos
            print("✅ Historia familiar generada correctamente")
            
            if tiene_pareja:
                self.generar_perfil_pareja()
            
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f"❌ Error al generar historia familiar: {e}")
            print("Respuesta de Claude:", content)
        return None

    def generar_perfil_pareja(self):
        print("\nGenerando perfil de la pareja...")
        prompt = f"""Genera un perfil detallado para la pareja de esta persona:
        {json.dumps(self.identidad['datos_personales'], indent=2)}
        
        Incluye la siguiente información:
        - Nombre y apellidos
        - Edad
        - Dónde se conocieron
        - Estudios
        - Trabajo actual (si tiene)
        - Si conduce o no
        - Marca del coche (si tiene)
        - Si tiene moto (marca si tiene)
        - Hijos (nombres, edades y dónde estudian si los tienen)
        - 3 manías que tiene
        - 3 cosas que más le gustan de su pareja
        - 3 cosas que más detesta de su pareja
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {{
            "nombre_apellidos": "",
            "edad": 0,
            "donde_se_conocieron": "",
            "estudios": "",
            "trabajo_actual": "",
            "conduce": true/false,
            "coche": {{
                "tiene": true/false,
                "marca": ""
            }},
            "moto": {{
                "tiene": true/false,
                "marca": ""
            }},
            "hijos": [
                {{
                    "nombre": "",
                    "edad": 0,
                    "donde_estudia": ""
                }}
            ],
            "manias": [],
            "cosas_que_gustan": [],
            "cosas_que_detesta": []
        }}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                datos = json.loads(json_str.group())
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            self.identidad["perfil_pareja"] = datos
            print("✅ Perfil de la pareja generado correctamente")
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f" Error al generar perfil de la pareja: {e}")
            print("Respuesta de Claude:", content)
        return None

    def generar_educacion(self, preferencias=None):
        print("\nGenerando historial educativo...")
        if not self.identidad["datos_personales"]:
            print("❌ Error: Primero debes generar los datos personales")
            return None

        prompt = f"""Genera un historial educativo coherente para esta persona:
        {json.dumps(self.identidad['datos_personales'], indent=2)}
        
        Incluye:
        - Educación primaria
        - Educación secundaria
        - Educación universitaria (si aplica)
        - Cursos y certificaciones
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {{
            "primaria": {{
                "centro": "",
                "periodo": "",
                "ubicacion": ""
            }},
            "secundaria": {{
                "centro": "",
                "periodo": "",
                "especialidad": ""
            }},
            "universidad": {{
                "centro": "",
                "carrera": "",
                "periodo": "",
                "notas_destacadas": ""
            }},
            "otros_cursos": []
        }}"""

        if preferencias:
            prompt += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extraer el contenido de texto de la respuesta
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            # Extraer el JSON de la respuesta
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                datos = json.loads(json_str.group())
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            self.identidad["educacion"] = datos
            print("✅ Historial educativo generado correctamente")
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f"❌ Error al generar educación: {e}")
            print("Respuesta de Claude:", content)
        return None

    def generar_experiencia(self, preferencias=None):
        print("\nGenerando experiencia laboral...")
        if not self.identidad["datos_personales"] or not self.identidad["educacion"]:
            print("❌ Error: Primero debes generar datos personales y educación")
            return None

        prompt = f"""Genera una experiencia laboral coherente para esta persona:
        {json.dumps(self.identidad['datos_personales'], indent=2)}
        {json.dumps(self.identidad['educacion'], indent=2)}
        
        Incluye al menos 3 trabajos con:
        - Empresa
        - Cargo
        - Periodo
        - Responsabilidades
        - Logros
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {{
            "trabajos": [
                {{
                    "empresa": "",
                    "cargo": "",
                    "periodo": "",
                    "responsabilidades": [],
                    "logros": []
                }}
            ],
            "habilidades": [],
            "sectores_experiencia": []
        }}
        
        Asegrate de incluir al menos 3 trabajos en la lista "trabajos"."""

        if preferencias:
            prompt += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extraer el contenido de texto de la respuesta
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            # Extraer el JSON de la respuesta
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                datos = json.loads(json_str.group())
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            self.identidad["experiencia"] = datos
            print("✅ Experiencia laboral generada correctamente")
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f"❌ Error al generar experiencia: {e}")
            print("Respuesta de Claude:", content)
        return None

    def generar_perfil_psicologico(self, preferencias=None):
        print("\nGenerando perfil psicológico...")
        prompt_base = f"""Genera un perfil psicológico coherente para esta persona:
        {json.dumps(self.identidad, indent=2)}
        
        Incluye:
        - Rasgos de personalidad principales (con ejemplos de comportamiento para cada rasgo)
        - Fortalezas y debilidades
        - Estilo de comunicación (incluyendo muletillas frecuentes)
        - Valores personales
        - 10 formas específicas de actuar de este perfil
        - IQ (entre 85 y 145)
        - Frase motivacional favorita
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {{
            "rasgos_principales": {{
                "extraversion": {{
                    "puntuacion": 0,
                    "ejemplos": []
                }},
                "apertura": {{
                    "puntuacion": 0,
                    "ejemplos": []
                }},
                "responsabilidad": {{
                    "puntuacion": 0,
                    "ejemplos": []
                }},
                "amabilidad": {{
                    "puntuacion": 0,
                    "ejemplos": []
                }},
                "estabilidad": {{
                    "puntuacion": 0,
                    "ejemplos": []
                }}
            }},
            "fortalezas": [],
            "areas_mejora": [],
            "estilo_comunicacion": {{
                "descripcion": "",
                "muletillas": []
            }},
            "valores": [],
            "formas_de_actuar": [],
            "iq": 0,
            "frase_motivacional": ""
        }}"""

        if preferencias:
            prompt_base += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt_base
                }]
            )
            
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            # Intentar extraer el JSON completo
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                try:
                    datos = json.loads(json_str.group())
                except json.JSONDecodeError:
                    # Si falla, intentar reparar el JSON
                    json_reparado = self._reparar_json(json_str.group())
                    datos = json.loads(json_reparado)
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            self.identidad["perfil_psicologico"] = datos
            print("✅ Perfil psicológico generado correctamente")
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f"❌ Error al generar perfil psicológico: {e}")
            print("Respuesta de Claude:", content)
        return None

    def _reparar_json(self, json_str):
        # Intentar cerrar llaves y corchetes abiertos
        stack = []
        for char in json_str:
            if char in '{[':
                stack.append(char)
            elif char in '}]':
                if stack and ((stack[-1] == '{' and char == '}') or (stack[-1] == '[' and char == ']')):
                    stack.pop()
                else:
                    stack.append(char)
        
        while stack:
            if stack[-1] == '{':
                json_str += '}'
            elif stack[-1] == '[':
                json_str += ']'
            stack.pop()
        
        return json_str

    def generar_identidad_completa(self, con_indicaciones=False):
        try:
            content = None  # Inicializar con None
            
            # Generar todas las secciones
            self.generar_datos_personales(input("Indicaciones para datos personales: ") if con_indicaciones else None)
            self.generar_historia_familiar(input("Indicaciones para historia familiar: ") if con_indicaciones else None)
            self.generar_educacion(input("Indicaciones para educación: ") if con_indicaciones else None)
            self.generar_experiencia(input("Indicaciones para experiencia: ") if con_indicaciones else None)
            self.generar_perfil_social(input("Indicaciones para perfil social: ") if con_indicaciones else None)  # Nueva línea
            self.generar_perfil_psicologico(input("Indicaciones para perfil psicológico: ") if con_indicaciones else None)
            self.generar_otros_datos(input("Indicaciones para otros datos: ") if con_indicaciones else None)
            
            print("\n✅ Identidad completa generada exitosamente")
            
            # Preguntar si desea guardar la identidad
            guardar = input("\n¿Desea guardar la identidad generada? (s/n): ").lower()
            if guardar == 's':
                print("\nSeleccione el formato de guardado:")
                print("1. JSON (recomendado para reutilización)")
                print("2. TXT (más legible)")
                print("3. Ambos formatos")
                
                formato = input("Seleccione una opción (1-3): ")
                
                if formato in ['1', '2', '3']:
                    if formato in ['1', '3']:
                        archivo_json = self.guardar_en_archivo(formato='json')
                        if archivo_json:
                            print(f"✨ Identidad guardada en JSON: {archivo_json}")
                
                    if formato in ['2', '3']:
                        archivo_txt = self.guardar_en_archivo(formato='txt')
                        if archivo_txt:
                            print(f"✨ Identidad guardada en TXT: {archivo_txt}")
                else:
                    print("❌ Opción no válida. No se guardó la identidad.")
            
            # Preguntar si desea generar una foto
            generar_foto = input("\n¿Desea generar una foto de perfil? (s/n): ").lower()
            if generar_foto == 's':
                self.generar_foto_perfil()
                print("\n✅ Foto de perfil generada exitosamente")
            
            if content:
                # Procesar 'content' solo si tiene un valor
                self.identidad['datos_personales'] = json.loads(content)
            else:
                raise Exception("No se pudo generar los datos personales")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error al generar la identidad completa: {e}")
            return False

    def guardar_en_archivo(self, formato='json'):
        if not os.path.exists('perfiles'):
            os.makedirs('perfiles')
            
        dni = self.identidad['datos_personales']['dni']
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if formato == 'json':
            nombre_archivo = f"perfiles/{dni}_{fecha}.json"
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.identidad, f, indent=2, ensure_ascii=False)
                print(f"✅ Archivo JSON guardado como: {nombre_archivo}")
                return nombre_archivo
            except Exception as e:
                print(f"❌ Error al guardar el archivo JSON: {e}")
                return None
        
        elif formato == 'txt':
            nombre_archivo = f"perfiles/{dni}_{fecha}.txt"
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write("=== IDENTIDAD SIMULADA ===\n\n")
                    
                    for seccion, datos in self.identidad.items():
                        if datos:
                            f.write(f"\n=== {seccion.upper().replace('_', ' ')} ===\n")
                            self._escribir_seccion(f, datos)
                            
                print(f"✅ Archivo TXT guardado como: {nombre_archivo}")
                return nombre_archivo
            except Exception as e:
                print(f"❌ Error al guardar el archivo TXT: {e}")
                return None
        
        else:
            print("❌ Formato no válido. Por favor, elija 'json' o 'txt'.")
            return self.guardar_en_archivo()  # Llamada recursiva para volver a preguntar

    def _escribir_seccion(self, archivo, datos, nivel=0):
        if isinstance(datos, dict):
            for clave, valor in datos.items():
                archivo.write("  " * nivel + f"{clave.capitalize()}:\n")
                self._escribir_seccion(archivo, valor, nivel + 1)
        elif isinstance(datos, list):
            for item in datos:
                if isinstance(item, dict):
                    self._escribir_seccion(archivo, item, nivel)
                    archivo.write("\n")
                else:
                    archivo.write("  " * nivel + f"- {item}\n")
        else:
            archivo.write("  " * nivel + f"{datos}\n")

    def generar_otros_datos(self, preferencias=None):
        print("\nGenerando otros datos...")
        prompt = f"""Genera otros datos adicionales para esta persona:
        {json.dumps(self.identidad['datos_personales'], indent=2)}
        
        Incluye la siguiente información:
        - Mascota (si tiene, incluir raza, nombre y edad)
        - Conducción:
            - Si conduce coche: marca, modelo, años, edad en la que se sacó el carnet
            - Si conduce moto: marca, años, cilindrada, año en el que se sacó el carnet
        - Última lesión
        - Hobbies (enumerar 3 y detallarlos)
        - Color favorito
        - Estilo de vestimenta
        - Prenda favorita
        - Talla de zapatos
        - Talla de ropa
        
        Devuelve los datos en formato JSON con estas claves exactas:
        {{
            "mascota": {{
                "tiene": true/false,
                "raza": "",
                "nombre": "",
                "edad": 0
            }},
            "conduccion": {{
                "coche": {{
                    "conduce": true/false,
                    "marca": "",
                    "modelo": "",
                    "anos": 0,
                    "edad_carnet": 0
                }},
                "moto": {{
                    "conduce": true/false,
                    "marca": "",
                    "anos": 0,
                    "cilindrada": "",
                    "ano_carnet": 0
                }}
            }},
            "ultima_lesion": "",
            "hobbies": [
                {{
                    "nombre": "",
                    "descripcion": ""
                }},
                {{
                    "nombre": "",
                    "descripcion": ""
                }},
                {{
                    "nombre": "",
                    "descripcion": ""
                }}
            ],
            "color_favorito": "",
            "estilo_vestimenta": "",
            "prenda_favorita": "",
            "talla_zapatos": "",
            "talla_ropa": ""
        }}"""

        if preferencias:
            prompt += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text if isinstance(response.content, list) else response.content
            
            json_str = re.search(r'\{.*\}', content, re.DOTALL)
            if json_str:
                datos = json.loads(json_str.group())
            else:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta")
            
            self.identidad["otros_datos"] = datos
            print("✅ Otros datos generados correctamente")
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print("Respuesta de Claude:", content)
        except Exception as e:
            print(f"❌ Error al generar otros datos: {e}")
            print("Respuesta de Claude:", content)
        return None

    def generar_foto_perfil(self):
        """Genera una foto de perfil usando el GeneradorFotos"""
        try:
            # Verificar que existen datos personales
            if not self.identidad["datos_personales"]:
                print("\n❌ Error: Primero debes generar los datos personales")
                return None

            # Verificar que los datos necesarios están presentes
            datos_requeridos = ["sexo", "edad", "datos_biometricos"]
            for dato in datos_requeridos:
                if dato not in self.identidad["datos_personales"]:
                    print(f"\n❌ Error: Falta información de {dato} en los datos personales")
                    return None

            # Verificar datos biométricos
            datos_biometricos = ["color_pelo", "color_ojos", "constitucion"]
            for dato in datos_biometricos:
                if dato not in self.identidad["datos_personales"]["datos_biometricos"]:
                    print(f"\n❌ Error: Falta información de {dato} en los datos biométricos")
                    return None

            print("\n📸 Generando foto de perfil...")
            ruta_foto = self.generador_fotos.generar_foto(self.identidad["datos_personales"])
            
            if ruta_foto:
                self.identidad["foto_perfil"] = ruta_foto
                print(f"\n✅ Foto de perfil generada y guardada en: {ruta_foto}")
                return ruta_foto
            else:
                print("\n❌ Error al generar la foto de perfil")
                return None

        except Exception as e:
            print(f"\n❌ Error inesperado al generar foto de perfil: {e}")
            return None

    def generar_anecdotas_viaje(self, viaje):
        """Genera anécdotas culturales específicas para un viaje usando GPT-4"""
        prompt_anecdotas = f"""Genera 3 anécdotas culturales específicas y memorables sobre este viaje:

        Lugar: {viaje['lugar']}
        Fecha: {viaje['fecha']}
        Duración: {viaje['duracion']}
        Motivo: {viaje['motivo']}
        Acompañantes: {viaje['acompanantes']}

        Las anécdotas deben:
        - Estar relacionadas con la cultura local (gastronomía, costumbres, eventos, etc.)
        - Ser específicas y detalladas
        - Incluir interacciones con locales o experiencias únicas
        - Mencionar lugares o eventos reales de la ciudad
        - Tener entre 3-4 líneas cada una

        Devuelve un JSON con esta estructura exacta:
        {{
            "anecdotas_culturales": [
                {{
                    "titulo": "título breve de la anécdota",
                    "descripcion": "descripción detallada de la anécdota",
                    "lugar_especifico": "nombre del lugar donde ocurrió",
                    "elementos_culturales": ["elemento cultural 1", "elemento cultural 2"]
                }},
                {{anécdota 2}},
                {{anécdota 3}}
            ]
        }}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt_anecdotas}],
                temperature=0.8,
                max_tokens=1000
            )
            
            contenido = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', contenido, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception as e:
            print(f"❌ Error al generar anécdotas culturales: {e}")
            return None

    def generar_perfil_social(self, preferencias=None):
        """Genera el perfil social completo con viajes y anécdotas culturales"""
        try:
            # Generar viajes y datos básicos como antes
            # ... código existente ...

            # Añadir anécdotas culturales a cada viaje
            print("\nGenerando anécdotas culturales para cada viaje...")

            for viaje in viajes["viajes_espana"]:
                anecdotas = self.generar_anecdotas_viaje(viaje)
                if anecdotas:
                    viaje["anecdotas_culturales"] = anecdotas["anecdotas_culturales"]
                    print(f"✅ Anécdotas generadas para {viaje['lugar']}")
            
            for viaje in viajes["viajes_internacional"]:
                anecdotas = self.generar_anecdotas_viaje(viaje)
                if anecdotas:
                    viaje["anecdotas_culturales"] = anecdotas["anecdotas_culturales"]
                    print(f"✅ Anécdotas generadas para {viaje['lugar']}, {viaje['pais']}")

            # Continuar con el resto del perfil social...

            self.identidad["perfil_social"] = perfil_social
            print("✅ Perfil social generado exitosamente")
            return perfil_social

        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Error al generar perfil social: {e}")
            return None

def mostrar_menu_principal():
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Generar datos personales")
    print("2. Generar historia familiar")
    print("3. Generar historial educativo")
    print("4. Generar experiencia laboral")
    print("5. Generar perfil social")
    print("6. Generar perfil psicológico")
    print("7. Generar otros datos")
    print("8. Generar identidad completa")
    print("9. Generar imagen desde archivo existente")
    print("10. Guardar identidad en archivo")
    print("11. Generar storytelling narrativo")
    print("12. Generar vista HTML del perfil (beta)")  # Modificado
    print("13. Salir")
    return input("Seleccione una opción (1-13): ")

def mostrar_banner_inicial():
    """Muestra el banner inicial del programa"""
    print("""
╔════════════════════════════════════════╗
║     GENERADOR DE IDENTIDADES 2.0       ║
║                                        ║
║  Desarrollado por: @hex686f6c61        ║
║  GitHub: github.com/686f6c61           ║
╚════════════════════════════════════════╝
    """)
    
    print("🤖 Sistema Iniciado")
    print("📝 Listo para generar perfiles\n")

def cargar_datos_archivo():
    """Carga datos biométricos desde un archivo existente"""
    # Listar archivos disponibles
    if not os.path.exists('perfiles'):
        print("❌ La carpeta 'perfiles' no existe")
        return None
        
    archivos = [f for f in os.listdir('perfiles') if f.endswith(('.json', '.txt'))]
    
    if not archivos:
        print("❌ No hay archivos de perfiles disponibles")
        return None
    
    print("\nPerfiles disponibles:")
    for i, archivo in enumerate(archivos, 1):
        print(f"{i}. {archivo}")
    
    try:
        seleccion = int(input("\nSeleccione el número del perfil a usar: ")) - 1
        if 0 <= seleccion < len(archivos):
            ruta = os.path.join('perfiles', archivos[seleccion])
        else:
            print("❌ Selección inválida")
            return None
            
        # Resto del código de lectura igual...
        if ruta.endswith('.json'):
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                # Asegurarnos de que el sexo esté incluido
                if 'datos_personales' in datos:
                    return datos['datos_personales']
                else:
                    # Si los datos están en el nivel raíz
                    return datos
        elif ruta.endswith('.txt'):
            datos_personales = {}
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
                # Extraer datos básicos
                nombre_match = re.search(r'Nombre_completo:\s*(.+)', contenido)
                if nombre_match:
                    datos_personales['nombre_completo'] = nombre_match.group(1).strip()
                
                # Extraer edad
                edad_match = re.search(r'Edad:\s*(\d+)', contenido)
                if edad_match:
                    datos_personales['edad'] = int(edad_match.group(1))
                
                # Extraer sexo
                sexo_match = re.search(r'Sexo:\s*(.+)', contenido)
                if sexo_match:
                    datos_personales['sexo'] = sexo_match.group(1).strip()
                
                datos_personales['datos_biometricos'] = {}
                for campo in ['altura', 'peso', 'color_ojos', 'color_pelo', 'constitucion']:
                    match = re.search(rf'{campo}:\s*(.+)', contenido, re.IGNORECASE)
                    if match:
                        datos_personales['datos_biometricos'][campo] = match.group(1).strip()
                
                return datos_personales
                
    except ValueError:
        print("❌ Por favor, introduzca un número válido")
        return None
    except Exception as e:
        print(f"❌ Error al cargar el archivo: {e}")
        return None

def main():
    try:
        # Inicialización
        mostrar_banner_inicial()
        generador = GeneradorIdentidadClaude()
        storytelling = GeneradorStorytelling()
        
        while True:
            mostrar_menu_principal()
            opcion = input("Seleccione una opción (1-13): ").strip()
            
            if opcion == '13':
                print("\n👋 ¡Gracias por usar el generador de identidades!")
                break
                
            if opcion not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
                print("\n❌ Opción no válida")
                input("\nPresione Enter para continuar...")
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            try:
                if opcion == '1':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_datos_personales(indicaciones)
                elif opcion == '2':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_historia_familiar(indicaciones)
                elif opcion == '3':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_historial_educativo(indicaciones)
                elif opcion == '4':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_experiencia_laboral(indicaciones)
                elif opcion == '5':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_perfil_social(indicaciones)
                elif opcion == '6':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_perfil_psicologico(indicaciones)
                elif opcion == '7':
                    indicaciones = input("Indique preferencias (o presione Enter para ninguna): ")
                    generador.generar_otros_datos(indicaciones)
                elif opcion == '8':
                    print("\n=== GENERACIÓN DE IDENTIDAD COMPLETA ===")
                    print("1. Generar nueva identidad")
                    print("2. Cargar perfil existente")
                    sub_opcion = input("\nSeleccione una opción (1-2): ")
                    if sub_opcion == '1':
                        con_indicaciones = input("\n¿Desea proporcionar indicaciones para cada parte? (s/n): ").lower() == 's'
                        generador.generar_identidad_completa(con_indicaciones)
                    elif sub_opcion == '2':
                        perfiles = generador.listar_perfiles_guardados()
                        if perfiles:
                            print("\nPerfiles disponibles:")
                            for i, perfil in enumerate(perfiles, 1):
                                print(f"{i}. {perfil}")
                            seleccion = input("\nSeleccione el número del perfil a usar: ")
                    else:
                        print("\n❌ Opción no válida")
                elif opcion == '9':
                    if not generador.identidad.get('datos_personales'):
                        print("\n❌ Primero debes generar los datos personales")
                        continue
                    foto_generator = GeneradorFotos()
                    foto_generator.generar_foto(generador.identidad['datos_personales'])
                elif opcion == '10':
                    if not any(generador.identidad.values()):
                        print("\n❌ No hay datos para guardar")
                        continue
                    generador.guardar_en_archivo()
                elif opcion == '11':
                    try:
                        print("\n=== GENERACIÓN DE STORYTELLING NARRATIVO ===")
                        print("1. Usar perfil actual")
                        print("2. Cargar perfil desde archivo JSON")
                        
                        sub_opcion = input("\nSeleccione una opción (1-2): ").strip()
                        
                        if sub_opcion == '1':
                            if not any(generador.identidad.values()):
                                print("\n❌ No hay datos en el perfil actual para generar storytelling")
                                continue
                            datos_perfil = generador.identidad
                            nombre_base = datos_perfil.get('datos_personales', {}).get('nombre_completo', 'perfil')
                        
                        elif sub_opcion == '2':
                            # Listar archivos JSON disponibles
                            if not os.path.exists('perfiles'):
                                print("\n❌ No existe la carpeta 'perfiles'")
                                continue
                                
                            archivos_json = [f for f in os.listdir('perfiles') if f.endswith('.json')]
                            if not archivos_json:
                                print("\n❌ No hay archivos JSON disponibles")
                                continue
                                
                            print("\nPerfiles disponibles:")
                            for i, archivo in enumerate(archivos_json, 1):
                                print(f"{i}. {archivo}")
                                
                            seleccion = input("\nSeleccione el número del perfil (0 para cancelar): ")
                            if seleccion == "0":
                                continue
                                
                            try:
                                indice = int(seleccion) - 1
                                if 0 <= indice < len(archivos_json):
                                    ruta_json = os.path.join('perfiles', archivos_json[indice])
                                    with open(ruta_json, 'r', encoding='utf-8') as f:
                                        datos_perfil = json.load(f)
                                        nombre_base = datos_perfil.get('datos_personales', {}).get('nombre_completo', 'perfil')
                                else:
                                    print("\n❌ Selección no válida")
                                    continue
                            except (ValueError, IndexError):
                                print("\n❌ Selección no válida")
                                continue
                        else:
                            print("\n❌ Opción no válida")
                            continue
                        
                        # Generar storytelling con el perfil seleccionado
                        historia = storytelling.generar_storytelling_completo(datos_perfil)
                        
                        if historia:
                            # Asegurar que existe el directorio de historias
                            os.makedirs('historias', exist_ok=True)
                            
                            # Generar nombre de archivo con fecha y hora
                            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nombre_archivo = f"historias/{nombre_base}_{fecha}_storytelling.txt"
                            
                            # Guardar la historia
                            try:
                                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                                    f.write(historia)
                                print(f"\n✅ Historia guardada exitosamente en: {nombre_archivo}")
                            except Exception as e:
                                print(f"\n❌ Error al guardar la historia: {e}")
                        else:
                            print("\n❌ No se pudo generar la historia")
                            
                    except Exception as e:
                        print(f"\n❌ Error al generar storytelling: {e}")
                elif opcion == '12':
                    try:
                        print("\n=== GENERACIÓN DE VISTA HTML ===")
                        
                        # 1. Seleccionar archivo JSON
                        print("\nSeleccione el archivo JSON del perfil:")
                        if not os.path.exists('perfiles'):
                            print("❌ No existe la carpeta 'perfiles'")
                            continue
                            
                        archivos_json = [f for f in os.listdir('perfiles') if f.endswith('.json')]
                        if not archivos_json:
                            print("❌ No hay archivos JSON disponibles")
                            continue
                            
                        for i, archivo in enumerate(archivos_json, 1):
                            print(f"{i}. {archivo}")
                            
                        seleccion = input("\nSeleccione el número del perfil (0 para cancelar): ")
                        if seleccion == "0":
                            continue
                            
                        try:
                            indice = int(seleccion) - 1
                            if 0 <= indice < len(archivos_json):
                                ruta_json = os.path.join('perfiles', archivos_json[indice])
                                with open(ruta_json, 'r', encoding='utf-8') as f:
                                    perfil = json.load(f)
                            else:
                                print("❌ Selección no válida")
                                continue
                        except (ValueError, IndexError):
                            print("❌ Selección no válida")
                            continue
                        
                        # 2. Preguntar por la foto
                        usar_foto = input("\n¿Desea incluir una fotografía? (s/n): ").lower() == 's'
                        ruta_foto = None
                        
                        if usar_foto:
                            print("\nSeleccione la foto a utilizar:")
                            if not os.path.exists('fotos'):
                                print("❌ No existe la carpeta 'fotos'")
                                continue
                                
                            fotos = [f for f in os.listdir('fotos') if f.endswith(('.jpg', '.png', '.jpeg'))]
                            if not fotos:
                                print("❌ No hay fotos disponibles")
                                continue
                                
                            for i, foto in enumerate(fotos, 1):
                                print(f"{i}. {foto}")
                                
                            seleccion_foto = input("\nSeleccione el número de la foto (0 para cancelar): ")
                            if seleccion_foto == "0":
                                continue
                                
                            try:
                                indice_foto = int(seleccion_foto) - 1
                                if 0 <= indice_foto < len(fotos):
                                    ruta_foto = os.path.join('fotos', fotos[indice_foto])
                                else:
                                    print("❌ Selección no válida")
                                    continue
                            except (ValueError, IndexError):
                                print("❌ Selección no válida")
                                continue
                        
                        # 3. Generar HTML
                        html_generator = GeneradorHTML()
                        ruta_html = html_generator.generar_html(perfil, ruta_foto if usar_foto else None)
                        
                        if ruta_html:
                            print(f"\n✅ Vista HTML generada exitosamente en: {ruta_html}")
                        else:
                            print("\n❌ Error al generar la vista HTML")
                            
                    except Exception as e:
                        print(f"\n❌ Error al generar vista HTML: {e}")
                
                input("\nPresione Enter para continuar...")
                os.system('cls' if os.name == 'nt' else 'clear')
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPresione Enter para continuar...")
                os.system('cls' if os.name == 'nt' else 'clear')
                
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta pronto!")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()


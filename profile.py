import os
from datetime import datetime
import json
import random
from dotenv import load_dotenv
from anthropic import Anthropic
import re

class GeneradorIdentidadClaude:
    def __init__(self):
        self.configurar_api()
        self.identidad = {
            "datos_personales": None,
            "historia_familiar": None,
            "educacion": None,
            "experiencia": None,
            "perfil_psicologico": None,
            "perfil_pareja": None,
            "otros_datos": None
        }

    def configurar_api(self):
        """Configura y valida la API key de Claude"""
        # Intentar cargar de .env
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        while not api_key:
            print("\n=== CONFIGURACIÓN DE API DE CLAUDE ===")
            api_key = input("Por favor, introduce tu API key de Claude (comienza con 'sk-ant-'): ")
            
            if api_key.startswith('sk-ant-'):
                # Guardar en .env para futuros usos
                with open('.env', 'w') as f:
                    f.write(f"ANTHROPIC_API_KEY={api_key}")
            else:
                print("❌ API key inválida. Debe comenzar con 'sk-ant-'")
                api_key = None
        
        self.anthropic = Anthropic(api_key=api_key)
        
        # Validar la conexión
        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{
                    "role": "user",
                    "content": "Test de conexión"
                }]
            )
            print("✅ Conexión con Claude establecida correctamente")
        except Exception as e:
            print(f"❌ Error al conectar con Claude: {e}")
            self.configurar_api()  # Recursivamente pedir una nueva key si falla

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
        
        tiene_pareja = input("¿Desea que la persona tenga pareja? (s/n): ").lower() == 's'
        
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
        - Situación sentimental: {"En pareja" if tiene_pareja else "Soltero/a"}
        
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
        - 3 cosas que más le gustan a su pareja de ella/él
        - 3 cosas que más detesta su pareja de ella/él
        
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
            print(f"❌ Error al generar perfil de la pareja: {e}")
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
                max_tokens=1000,
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
        
        Asegúrate de incluir al menos 3 trabajos en la lista "trabajos"."""

        if preferencias:
            prompt += f"\n\nTen en cuenta las siguientes preferencias del usuario: {preferencias}"

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
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

    def generar_identidad_completa(self, con_indicaciones):
        secciones = [
            ("datos personales", self.generar_datos_personales),
            ("historia familiar", self.generar_historia_familiar),
            ("historial educativo", self.generar_educacion),
            ("experiencia laboral", self.generar_experiencia),
            ("perfil psicológico", self.generar_perfil_psicologico),
            ("otros datos", self.generar_otros_datos)
        ]
        
        for nombre_seccion, funcion in secciones:
            print(f"\nGenerando {nombre_seccion}...")
            if con_indicaciones:
                preferencias = input(f"Indique preferencias para {nombre_seccion} (o presione Enter para ninguna): ")
                datos = funcion(preferencias if preferencias else None)
            else:
                datos = funcion()
            
            if datos:
                print(f"✅ {nombre_seccion.capitalize()} generados correctamente")
            else:
                print(f"❌ Error al generar {nombre_seccion}")
        
        if "historia_familiar" in self.identidad and self.identidad["historia_familiar"].get("situacion_sentimental") == "En pareja":
            print("\nGenerando perfil de la pareja...")
            self.generar_perfil_pareja()

    def guardar_en_archivo(self):
        if not os.path.exists('perfiles'):
            os.makedirs('perfiles')
            
        dni = self.identidad['datos_personales']['dni']
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        formato = input("¿En qué formato desea guardar el archivo? (json/txt): ").lower()
        
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

def mostrar_menu_principal():
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Generar datos personales")
    print("2. Generar historia familiar")
    print("3. Generar historial educativo")
    print("4. Generar experiencia laboral")
    print("5. Generar perfil psicológico")
    print("6. Generar otros datos")
    print("7. Generar identidad completa")
    print("8. Guardar identidad en archivo (JSON o TXT)")
    print("9. Salir")
    return input("Seleccione una opción (1-9): ")

def mostrar_introduccion():
    print("\n" + "=" * 50)
    print("GENERADOR DE IDENTIDADES SIMULADAS v1.0".center(50))
    print("=" * 50)
    print("\nBienvenido al Generador de Identidades Simuladas.")
    print("Este programa utiliza la API de Anthropic y el modelo")
    print("Claude 3.5 Sonnet para crear perfiles ficticios")
    print("detallados y coherentes.")
    print("\nDesarrollado por: @hex686f6c61")
    print("GitHub: https://github.com/686f6c61")
    print("\nPuede generar los siguientes componentes:")
    print("  - Datos personales")
    print("  - Historia familiar")
    print("  - Historial educativo")
    print("  - Experiencia laboral")
    print("  - Perfil psicológico")
    print("  - Otros datos")
    print("\nAl final, podrá guardar la identidad generada")
    print("en un archivo JSON o TXT.")
    print("\nPresione Enter para comenzar o Ctrl+C para salir...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nSaliendo del programa...")
        raise

def main():
    try:
        mostrar_introduccion()
        
        print("\nConfigurando la conexión con Claude...")
        generador = GeneradorIdentidadClaude()
        
        while True:
            opcion = mostrar_menu_principal()
            
            if opcion in ['1', '2', '3', '4', '5', '6']:
                preferencias = input("Indique preferencias (o presione Enter para ninguna): ")
                if opcion == '1':
                    datos = generador.generar_datos_personales(preferencias if preferencias else None)
                elif opcion == '2':
                    datos = generador.generar_historia_familiar(preferencias if preferencias else None)
                elif opcion == '3':
                    datos = generador.generar_educacion(preferencias if preferencias else None)
                elif opcion == '4':
                    datos = generador.generar_experiencia(preferencias if preferencias else None)
                elif opcion == '5':
                    datos = generador.generar_perfil_psicologico(preferencias if preferencias else None)
                elif opcion == '6':
                    datos = generador.generar_otros_datos(preferencias if preferencias else None)
                
                if datos:
                    print("\nDatos generados:")
                    print(json.dumps(datos, indent=2, ensure_ascii=False))
            
            elif opcion == '7':
                con_indicaciones = input("¿Desea proporcionar indicaciones para cada parte? (s/n): ").lower() == 's'
                generador.generar_identidad_completa(con_indicaciones)
                print("\n✅ Identidad completa generada")
            
            elif opcion == '8':
                if any(generador.identidad.values()):
                    archivo = generador.guardar_en_archivo()
                    if archivo:
                        print(f"\n✨ ¡Identidad guardada exitosamente en formato {'JSON' if archivo.endswith('.json') else 'TXT'}!")
                else:
                    print("\n❌ No hay datos para guardar. Genere algunos datos primero.")
            
            elif opcion == '9':
                print("\n¡Gracias por usar el Generador de Identidades Simuladas!")
                print("Versión: 1.0")
                print("Desarrollado por: @hex686f6c61")
                print("GitHub: https://github.com/686f6c61")
                print("Hasta pronto.")
                break
            
            else:
                print("\n❌ Opción no válida. Por favor, seleccione una opción del 1 al 9.")
            
            input("\nPresione Enter para continuar...")
    
    except KeyboardInterrupt:
        print("\n\nInterrupción detectada. Saliendo del programa...")
    except Exception as e:
        print(f"\n❌ Se ha producido un error inesperado: {e}")
    finally:
        print("\n¡Gracias por usar el Generador de Identidades Simuladas!")
        print("Versión: 1.0")
        print("Desarrollado por: @686f6c61")
        print("GitHub: https://github.com/686f6c61")
        print("Hasta pronto.")

if __name__ == "__main__":
    main()

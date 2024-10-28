import os
from datetime import datetime
from dotenv import load_dotenv
import json
import requests
from PIL import Image
from io import BytesIO
from anthropic import Anthropic

class GeneradorFotos:
    """Clase principal para la generación de fotos de identidades simuladas"""
    
    def __init__(self):
        """Inicializa el generador de fotos y configura la API"""
        self.configurar_api()
        # Inicializamos los atributos para almacenar configuraciones
        self.parametros = {}
        self.plano_descripcion = ""
        self.angulo_descripcion = ""
        
    def configurar_api(self):
        """Configura y valida la API key de Stability AI
        Solicita la key si no está configurada y la valida antes de guardarla"""
        load_dotenv()
        self.api_key = os.getenv('STABILITY_API_KEY')
        
        # Bucle de solicitud de API key si no existe
        while not self.api_key:
            print("\n=== CONFIGURACIÓN DE API DE STABILITY AI ===")
            self.api_key = input("Por favor, introduce tu API key de Stability AI (comienza con 'sk-'): ")
            
            # Validación b��sica y guardado de la API key
            if self.api_key.startswith('sk-'):
                with open('.env', 'a') as f:
                    f.write(f"\nSTABILITY_API_KEY={self.api_key}")
            else:
                print("❌ API key no válida. Debe comenzar con 'sk-'")
                self.api_key = None

        # Validación completa de la API key
        try:
            self.validar_api_key()
            print("✅ API key de Stability AI configurada correctamente")
        except Exception as e:
            print(f"❌ Error al validar la API key: {e}")
            self.api_key = None
            self.configurar_api()

    def validar_api_key(self):
        """Valida la API key haciendo una llamada de prueba al endpoint de balance"""
        url = "https://api.stability.ai/v1/user/balance"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

    def solicitar_parametros_foto(self):
        """Interfaz de usuario para configurar los parámetros de la foto
        Permite seleccionar tipo de plano, ángulo, belleza, peinado y fondo"""
        self.parametros = {}
        
        # Tipo de plano
        print("\n=== CONFIGURACIÓN DE LA FOTO ===")
        print("Tipo de plano:")
        print("1. Retrato (primer plano)")
        print("2. Medio cuerpo")
        print("3. Cuerpo entero")
        opcion = input("Seleccione una opción (1-3) [1]: ").strip() or "1"
        
        # Guardamos la descripción del plano
        self.plano_descripcion = {
            "1": "FOTOGRAFÍA TIPO RETRATO (primer plano, encuadre desde los hombros hasta la cabeza)",
            "2": "FOTOGRAFÍA DE MEDIO CUERPO (encuadre desde la cintura hasta la cabeza)",
            "3": "FOTOGRAFÍA DE CUERPO ENTERO (persona completa de pies a cabeza)"
        }.get(opcion, "FOTOGRAFÍA TIPO RETRATO")
        
        self.parametros['plano'] = opcion
        
        # Ángulo
        print("\nÁngulo de la foto:")
        print("1. Frontal")
        print("2. Tres cuartos")
        print("3. Perfil")
        opcion = input("Seleccione una opción (1-3) [1]: ").strip() or "1"
        
        # Guardamos la descripción del ángulo
        self.angulo_descripcion = {
            "1": "ÁNGULO FRONTAL (mirando directamente a la cámara)",
            "2": "ÁNGULO TRES CUARTOS (rostro y cuerpo girados 45 grados)",
            "3": "ÁNGULO DE PERFIL (mostrando el lateral completo)"
        }.get(opcion, "ÁNGULO FRONTAL")
        
        self.parametros['angulo'] = opcion
        
        # Nivel de belleza
        print("\nNivel de belleza física:")
        print("1. Normal")
        print("2. Atractivo")
        print("3. Muy atractivo")
        print("4. Excepcional")
        opcion = input("Seleccione una opción (1-4) [1]: ").strip() or "1"
        self.parametros['belleza'] = {
            "1": "aspecto normal y natural",
            "2": "atractivo",
            "3": "muy atractivo",
            "4": "excepcionalmente atractivo"
        }.get(opcion, "aspecto normal y natural")
        
        # Estilo de peinado
        print("\nEstilo de peinado:")
        print("1. Casual")
        print("2. Formal")
        print("3. Moderno")
        print("4. Clásico")
        print("5. Personalizado")
        opcion = input("Seleccione una opción (1-5) [1]: ").strip() or "1"
        self.parametros['peinado'] = {
            "1": "casual",
            "2": "formal",
            "3": "moderno",
            "4": "clásico",
            "5": input("Describa el peinado deseado: ") if opcion == "5" else "casual"
        }.get(opcion, "casual")
        
        # Fondo
        print("\n¿Desea un fondo específico?")
        print("1. Fondo neutro (por defecto)")
        print("2. Fondo personalizado")
        if input("Seleccione una opción (1-2) [1]: ").strip() == "2":
            print("\nTipos de fondo disponibles:")
            print("1. Oficina profesional")
            print("2. Estudio fotográfico")
            print("3. Exterior urbano")
            print("4. Naturaleza")
            print("5. Personalizado")
            opcion = input("Seleccione una opción (1-5): ").strip()
            self.parametros['fondo'] = {
                "1": "oficina profesional",
                "2": "estudio fotográfico",
                "3": "exterior urbano",
                "4": "entorno natural y paisaje",
                "5": f"fondo personalizado: {input('Describa el fondo deseado: ')}"
            }.get(opcion, "fondo neutro")
        else:
            self.parametros['fondo'] = "fondo neutro"
        
        return self.parametros

    def traducir_a_ingles(self, texto_espanol):
        """Utiliza la API de Claude para traducir el prompt al inglés
        Mantiene el formato y estructura del texto original"""
        try:
            client = Anthropic()
            # Configuración del mensaje para Claude
            mensaje = f"""Traduce el siguiente texto al inglés, manteniendo el formato y la estructura. 
            Asegúrate de que la traducción sea natural y apropiada para un prompt de generación de imágenes:

            {texto_espanol}

            Devuelve SOLO la traducción, sin comentarios adicionales."""

            # Llamada a la API de Claude
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                messages=[
                    {"role": "user", "content": mensaje}
                ]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            print(f"❌ Error al traducir: {e}")
            return None

    def generar_prompt(self, datos_personales):
        """Genera el prompt para la IA en español y lo traduce al inglés
        Incluye todas las características específicas de la foto"""
        # Primero solicitamos los parámetros
        self.solicitar_parametros_foto()
        
        # Generamos el prompt en español
        prompt_espanol = f"""Generar una fotografía hiperrealista con estas características específicas:

        TIPO DE FOTOGRAFÍA:
        {self.plano_descripcion}
        {self.angulo_descripcion}
        - Pose natural y relajada
        - Composición profesional de fotografía
        - Asegurar que el encuadre respete exactamente el tipo de plano solicitado

        CARACTERÍSTICAS DE LA PERSONA:
        - {datos_personales.get('sexo', 'persona')}, {datos_personales.get('edad', '30')} años
        - Nivel de atractivo: {self.parametros['belleza']}
        - Cabello {datos_personales['datos_biometricos']['color_pelo']} con estilo {self.parametros['peinado']}
        - Ojos {datos_personales['datos_biometricos']['color_ojos']}
        - Complexión {datos_personales['datos_biometricos']['constitucion']}
        - Altura {datos_personales['datos_biometricos']['altura']}

        ASPECTOS TÉCNICOS:
        - Fotografía profesional de alta calidad
        - Iluminación profesional de estudio
        - Fondo: {self.parametros['fondo']}
        - Enfoque nítido y claro
        - Texturas naturales de piel
        - Sin filtros ni efectos artísticos
        - Calidad fotográfica realista

        IMPORTANTE: El tipo de plano debe ser EXACTAMENTE {self.plano_descripcion.lower()}, 
        respetando el encuadre especificado y el ángulo {self.angulo_descripcion.lower()}."""

        if datos_personales['datos_biometricos'].get('marcas_visibles'):
            prompt_espanol += f"\n\nSeñas particulares: {datos_personales['datos_biometricos']['marcas_visibles']}"

        # Mostramos el prompt en español
        print("\nPrompt en español (para referencia):")
        print(prompt_espanol)
        
        # Traducimos al inglés
        prompt_ingles = self.traducir_a_ingles(prompt_espanol)
        
        return prompt_ingles if prompt_ingles else prompt_espanol

    def generar_foto(self, datos_personales):
        """Método principal para generar la foto
        Coordina todo el proceso desde el prompt hasta el guardado"""
        if not datos_personales or 'datos_biometricos' not in datos_personales:
            print("❌ Error: Se requieren datos biométricos para generar la foto")
            return None
            
        prompt = self.generar_prompt(datos_personales)  # Pasamos datos_personales completo
        print("\nPrompt generado para la IA:")
        print(prompt)
        
        # Generar la imagen
        imagen_bytes = self.generar_con_stable_diffusion(prompt)
        if imagen_bytes:
            # Guardar la imagen
            return self.guardar_foto(imagen_bytes, datos_personales)
        return None

    def guardar_foto(self, imagen_bytes, datos_personales):
        """Guarda la foto generada en el sistema de archivos
        Crea un nombre único basado en el nombre y la fecha"""
        if not os.path.exists('fotos'):
            os.makedirs('fotos')
            
        # Usar nombre y fecha como identificador
        nombre = datos_personales.get('nombre_completo', 'perfil').replace(' ', '_').lower()
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"fotos/{nombre}_{fecha}.jpeg"  # Cambiado a .jpeg
        
        try:
            with open(nombre_archivo, 'wb') as file:
                file.write(imagen_bytes)
            print(f"✅ Foto guardada como: {nombre_archivo}")
            return nombre_archivo
        except Exception as e:
            print(f"❌ Error al guardar la foto: {e}")
            return None

    # Ejemplo de implementación con Stable Diffusion API
    def generar_con_stable_diffusion(self, prompt):
        """Realiza la llamada a la API de Stability AI para generar la imagen
        Maneja los errores y devuelve los bytes de la imagen"""
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
        
        data = {
            "prompt": prompt,
            "output_format": "jpeg",  # Cambiado a JPEG
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                files={"none": ''},
                data=data
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ Error en la API: {response.status_code}")
                print(response.json())
                return None
                
        except Exception as e:
            print(f"❌ Error al generar la imagen: {e}")
            return None

# Ejemplo de uso:
if __name__ == "__main__":
    # Datos de prueba para generar una foto
    datos_prueba = {
        "nombre_completo": "Juan Ejemplo",
        "datos_biometricos": {
            "color_pelo": "brown",
            "color_ojos": "green",
            "constitucion": "athletic",
            "altura": "180cm",
            "marcas_visibles": "small scar on left eyebrow"
        }
    }
    
    # Crear instancia y generar foto de prueba
    generador = GeneradorFotos()
    prompt = generador.generar_foto(datos_prueba)
    print("\nPrompt generado:")
    print(prompt)

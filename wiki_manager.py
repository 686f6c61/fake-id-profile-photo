import wikipediaapi
import random
from typing import Dict, List, Optional

class WikipediaManager:
    def __init__(self, language='es'):
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='ProfileGenerator/0.2'
        )
    
    def obtener_info_lugar(self, lugar: str) -> Optional[Dict]:
        """Obtiene información relevante de un lugar desde Wikipedia, enfocándose en cultura"""
        try:
            page = self.wiki.page(lugar)
            if not page.exists():
                # Intentar búsqueda alternativa
                search = self.wiki.page(f"{lugar} (España)")
                if search.exists():
                    page = search
                else:
                    return None
            
            # Inicializar diccionario de información
            info = {
                "nombre": page.title,
                "resumen": page.summary[:300],  # Resumen breve
                "cultura": [],
                "fiestas": [],
                "gastronomia": [],
                "monumentos": []
            }
            
            # Buscar secciones específicas de cultura
            secciones_culturales = [
                "Cultura",
                "Patrimonio",
                "Monumentos",
                "Fiestas",
                "Tradiciones",
                "Gastronomía",
                "Arte",
                "Lugares de interés"
            ]
            
            def explorar_secciones(seccion, nivel=0):
                if nivel > 2:  # Limitar profundidad de búsqueda
                    return
                
                titulo = seccion.title.lower()
                
                # Procesar sección actual
                if any(cultural.lower() in titulo for cultural in secciones_culturales):
                    if seccion.text:
                        categoria = next((s for s in secciones_culturales if s.lower() in titulo), "Cultura")
                        info_seccion = {
                            "titulo": seccion.title,
                            "contenido": seccion.text[:500]  # Limitar longitud
                        }
                        
                        if "fiest" in titulo.lower():
                            info["fiestas"].append(info_seccion)
                        elif "gastron" in titulo.lower():
                            info["gastronomia"].append(info_seccion)
                        elif "monument" in titulo.lower() or "patrimonio" in titulo.lower():
                            info["monumentos"].append(info_seccion)
                        else:
                            info["cultura"].append(info_seccion)
                
                # Explorar subsecciones
                for subseccion in seccion.sections:
                    explorar_secciones(subseccion, nivel + 1)
            
            # Explorar todas las secciones
            for seccion in page.sections:
                explorar_secciones(seccion)
            
            return info if any([info["cultura"], info["fiestas"], info["gastronomia"], info["monumentos"]]) else None
            
        except Exception as e:
            print(f"❌ Error al obtener información de Wikipedia para {lugar}: {e}")
            return None

    def generar_anecdota_viaje(self, info_lugar: Dict) -> str:
        """Genera una anécdota interesante basada en la información cultural del lugar"""
        try:
            elementos = []
            
            # Priorizar información cultural
            if info_lugar["cultura"]:
                elementos.extend([dato["contenido"] for dato in info_lugar["cultura"]])
            
            if info_lugar["fiestas"]:
                elementos.extend([dato["contenido"] for dato in info_lugar["fiestas"]])
            
            if info_lugar["gastronomia"]:
                elementos.extend([dato["contenido"] for dato in info_lugar["gastronomia"]])
            
            if info_lugar["monumentos"]:
                elementos.extend([dato["contenido"] for dato in info_lugar["monumentos"]])
            
            # Si no hay información cultural específica, usar el resumen
            if not elementos and info_lugar["resumen"]:
                elementos.append(info_lugar["resumen"])
            
            # Seleccionar y combinar elementos para la anécdota
            if elementos:
                seleccion = random.sample(elementos, min(2, len(elementos)))
                anecdota = " ".join(seleccion)
                return f"Durante la visita a {info_lugar['nombre']}, {anecdota.lower()}"
            
            return f"Visitó {info_lugar['nombre']}, pero no se encontró información cultural específica."
            
        except Exception as e:
            print(f"❌ Error al generar anécdota: {e}")
            return ""

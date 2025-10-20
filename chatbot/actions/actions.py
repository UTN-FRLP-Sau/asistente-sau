from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, List, Any, Dict

# =======================================================
# 1. ACTION DETECTAR MODO (FINAL Y SIMPLIFICADA)
# =======================================================

class ActionDetectarModo(Action):
    """
    Detecta si el NLU clasificó una opción de menú (ya sea número o palabra) 
    o si es texto libre.
    """
    def name(self) -> Text:
        return "action_detectar_modo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        intent = tracker.latest_message['intent'].get('name')
        num_val = tracker.get_slot("numero_opcion")
        
        # ⭐️ Si NLU clasificó como elegir_opcion (gracias al nlu.yml corregido)
        if intent == "elegir_opcion" and num_val:
            return [
                SlotSet("modo_conversacion", "menu"),
                # El slot numero_opcion ya tiene el valor (ej: "1" de la palabra "becas")
                FollowupAction("action_manejar_menu")
            ]

        # Si no es una opción, es modo libre (Texto con IA)
        user_message = tracker.latest_message.get("text", "").strip().lower()
        return [
            SlotSet("modo_conversacion", "libre"),
            SlotSet("texto_opcion", user_message),
            FollowupAction("action_responder_modo_libre")
        ]

# =======================================================
# 2. ACTION MANEJAR MENÚ (FINAL Y ESTABLE)
# =======================================================

class ActionManejarMenu(Action):
    """Maneja la navegación y las respuestas de los menús."""
    def name(self) -> Text:
        return "action_manejar_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        events = []
        num_str = tracker.get_slot("numero_opcion")
        contexto = tracker.get_slot("contexto_menu")
        
        if num_str is None:
            dispatcher.utter_message(text="Por favor, ingresá una opción numérica válida.")
            return []
            
        try:
            num = int(num_str)
        except ValueError:
            dispatcher.utter_message(response="utter_fallback")
            events.append(SlotSet("numero_opcion", None))
            return events


        # 1. MENÚ PRINCIPAL
        if contexto == "principal":
            if num == 1:
                # 1. Becas
                dispatcher.utter_message(response="utter_menu_becas")
                events.append(SlotSet("contexto_menu", "becas"))
            elif num == 2:
                # 2. Deportes
                dispatcher.utter_message(response="utter_menu_deportes")
                events.append(SlotSet("contexto_menu", "deportes"))
            elif num == 3:
                # 3. Comedor
                dispatcher.utter_message(response="utter_menu_comedor")
                events.append(SlotSet("contexto_menu", "comedor"))
            elif num == 4:
                # 4. Salir
                dispatcher.utter_message(response="utter_salir")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")
        
        # 2. SUBMENÚ BECAS 
        elif contexto == "becas":
            if num == 1:
                # 1. Requisitos
                dispatcher.utter_message(response="utter_respuesta_requisitos_becas")
                dispatcher.utter_message(response="utter_menu_becas") # Repetir el menú
            elif num == 2:
                # 2. Fechas
                dispatcher.utter_message(response="utter_respuesta_fechas_becas")
                dispatcher.utter_message(response="utter_menu_becas") # Repetir el menú
            elif num == 3:
                # 3. Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")
                
        # 3. SUBMENÚ DEPORTES
        elif contexto == "deportes":
            if num == 1:
                # 1. Horarios
                dispatcher.utter_message(response="utter_respuesta_horarios_deportes")
                dispatcher.utter_message(response="utter_menu_deportes") # Repetir el menú
            elif num == 2:
                # 2. Lugares
                dispatcher.utter_message(response="utter_respuesta_lugares_deportes")
                dispatcher.utter_message(response="utter_menu_deportes") # Repetir el menú
            elif num == 3:
                # 3. Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")

        # 4. SUBMENÚ COMEDOR
        elif contexto == "comedor":
            if num == 1:
                # 1. Menú semanal
                dispatcher.utter_message(response="utter_respuesta_menu_comedor")
                dispatcher.utter_message(response="utter_menu_comedor") # Repetir el menú
            elif num == 2:
                # 2. Precios
                dispatcher.utter_message(response="utter_respuesta_precios_comedor")
                dispatcher.utter_message(response="utter_menu_comedor") # Repetir el menú
            elif num == 3:
                # 3. Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")

        # Limpiamos el slot de la opción numérica al finalizar
        events.append(SlotSet("numero_opcion", None))
        return events

# =======================================================
# 3. ACTION RESPONDER MODO LIBRE (FINAL Y ESTABLE)
# =======================================================

class ActionResponderModoLibre(Action):
    """Responde a preguntas abiertas y comandos de texto."""
    def name(self) -> Text:
        return "action_responder_modo_libre"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        events = []
        
        # Manejo de comandos de texto (que no fueron clasificados como elegir_opcion)
        if intent == "salir_menu":
            dispatcher.utter_message(response="utter_salir")
            events.append(SlotSet("contexto_menu", "principal"))
            events.append(SlotSet("modo_conversacion", "menu"))
            return events
            
        elif intent == "greet":
            # Si el usuario dice "hola" o palabras que llevan al menú, pero Core no lo envió a la Rule de greet
            dispatcher.utter_message(response="utter_menu_principal")
            events.append(SlotSet("contexto_menu", "principal"))
            events.append(SlotSet("modo_conversacion", "menu"))
            return events

        # Manejo de preguntas de conocimiento
        elif intent == "preguntar_becas":
            dispatcher.utter_message(response="utter_respuesta_becas")
        elif intent == "preguntar_deportes":
            dispatcher.utter_message(response="utter_respuesta_deportes")
        elif intent == "preguntar_comedor":
            dispatcher.utter_message(response="utter_respuesta_comedor")
        
        else:
            # Fallback del modo libre (si la IA no entiende la pregunta)
            dispatcher.utter_message(response="utter_fallback")
            dispatcher.utter_message(response="utter_menu_principal")
            events.append(SlotSet("contexto_menu", "principal"))

        # Limpiamos los slots de modo libre y aseguramos el modo conversacion al salir de la accion
        events.append(SlotSet("texto_opcion", None))
        events.append(SlotSet("modo_conversacion", "menu")) 
        return events
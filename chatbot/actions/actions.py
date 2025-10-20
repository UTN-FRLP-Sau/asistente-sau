from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, List, Any, Dict

# =======================================================
# 0. BASE DE CONOCIMIENTO (RESPUESTAS DEL DOCUMENTO .DOCX)
# =======================================================

FAQ_RESPUESTAS = {
    # Área de Becas (8 Preguntas)
    "becas": {
        1: "Tipos de becas: Existen **Becas Nacionales** (Manuel Belgrano, Progresar, YPF) y **Becas de Rectorado** (investigación, servicio, BASE).",
        2: "La inscripción se realiza de manera **online** a través de los formularios oficiales publicados en la convocatoria correspondiente. El enlace y las instrucciones se comparten en los canales oficiales de la Secretaría de Asuntos Universitarios.",
        3: "Requisitos generales: Cursar alguna carrera en la Universidad Tecnológica Nacional, **no poseer título universitario** y cursar como mínimo **3 materias** durante el año.",
        4: "La documentación varía, pero suele incluir: **DNI y constancia de CUIL**, **certificado de alumno regular, analítico** (o en trámite/constancia de materias aprobadas y promedio), y **documentación socioeconómica** o cualquier otro documento que la convocatoria especifique.",
        5: "Las fechas se publican en los **canales oficiales** de la facultad y de la Secretaría de Asuntos Universitarios.",
        6: "Sí, podés postularte a más de una beca en simultáneo, pero **solo podrás beneficiarte de una de ellas**.",
        7: "Se te informará directamente por los **medios de contacto** que hayas registrado en tu postulación.",
        8: "Sí, siempre que cumplas con los requisitos establecidos por la beca y presentes la **solicitud de renovación en tiempo y forma**."
    },
    # Área de Boleto Estudiantil (11 Preguntas)
    "boleto_estudiantil": {
        1: "Para solicitarlo, primero debés **registrar tu tarjeta SUBE** a tu nombre (argentina.gob.ar/sube). Luego, completá el **formulario de inscripción** en el sitio oficial del Boleto Estudiantil. Finalmente, recibirás un turno o indicación para **presentarte con tu documentación y activar el beneficio**.",
        2: "Los requisitos varían, pero en general se solicita: ser **alumno/a regular**, tener **tarjeta SUBE nominada** a tu nombre, cumplir con una **distancia mínima** entre domicilio e institución (más de 2 km), y **no recibir otro beneficio similar**.",
        3: "Después de la inscripción online, el trámite se completa de forma **presencial** en las sedes indicadas en tu provincia o ciudad (dependencias de gobierno, comunas, delegaciones municipales o sucursales de Correo Argentino, según corresponda).",
        4: "Una vez activada, el beneficio comienza a funcionar a partir del **primer día del ciclo lectivo** o, en algunos casos, desde el **mes siguiente** a la inscripción, dependiendo de la fecha en que se hizo el trámite.",
        5: "Debés **dar de baja la tarjeta** desde tu cuenta de “Mi SUBE” en la web oficial y registrar una nueva. Luego, tendrás que **reactivar el beneficio** en una Terminal Automática o mediante la aplicación autorizada para recuperar el saldo y los viajes.",
        6: "Sí. Es válido únicamente durante el **ciclo lectivo y de lunes a viernes**, quedando inactivo los fines de semana y feriados. La fecha exacta depende de la jurisdicción, pero generalmente es el último día hábil del ciclo escolar/académico.",
        7: "En muchos casos la renovación es **automática** si fuiste beneficiario el año anterior. Si no requiere reinscripción, solo debés pasar la tarjeta por una Terminal Automática. Si sí se requiere, debés completar nuevamente el formulario de solicitud en el sitio oficial.",
        8: "Depende de la jurisdicción y el nivel educativo. En la Provincia de Buenos Aires, los estudiantes universitarios y terciarios cuentan con hasta **45 viajes mensuales** con tarifa subsidiada.",
        9: "Sí, se puede utilizar en **colectivos, trenes y subtes** que acepten la tarjeta SUBE, siempre dentro de la jurisdicción donde se otorgó el beneficio.",
        10: "Debés **informar el cambio** en la plataforma del Boleto Estudiantil o en el punto de atención donde tramitaste el beneficio. Si seguís cumpliendo los requisitos, podrás mantener el boleto activo.",
        11: "Podés acercarte a la **Secretaría de Asuntos Universitarios** o realizar la denuncia a través de la página de denuncias del boleto especial estudiantil: `https://denuncias-bes.transporte.gba.gob.ar/denunciasboleto.php`."
    },
    # Área de Deportes (7 Preguntas)
    "deportes": {
        1: "Las disciplinas que ofrece la facultad son: **fútbol** (femenino y masculino), **básquet 5x5** (masculino), **básquet 3x3** (masculino) y **vóley** (femenino y masculino).",
        2: "Los horarios están disponibles en el **Instagram oficial de la Secretaría de Asuntos Universitarios**: `@sau.utnfrlp` o podés acercarte personalmente a la SAU.",
        3: "Es necesario completar el **formulario de inscripción** que se encuentra en el instagram `@sau.utnfrlp` y posteriormente presentar el **apto médico** correspondiente.",
        4: "Podés informarte acercándote a la **Secretaría de Asuntos Universitarios** o consultando directamente con los **profesores** de cada disciplina.",
        5: "Sí, es posible participar en **más de una disciplina**.",
        6: "No, **no es necesario** contar con experiencia previa.",
        7: "No, **no es obligatorio** participar en las competencias, podés acercarte únicamente a entrenar."
    },
    # Área de Comedor (7 Preguntas)
    "comedor": {
        1: "El retiro de viandas se realiza de **lunes a viernes de 12:00 a 14:00 y de 19:00 a 21:00**, en el SUM de la facultad.",
        2: "Las viandas cuestan **$2500**.",
        3: "El menú diario tiene las siguientes opciones: **convencional, vegetariano, pan y postres, y también apto para celíacos**. Se comparte por las historias de Instagram de la Secretaría de Asuntos Universitarios: `@sau.utnfrlp`.",
        4: "Debes registrar el usuario, si no estás registrado en el sistema, completá el **formulario de inscripción** en el instagram `@sau.utnfrlp`.",
        5: "Debes ingresar a `https://ticket.frlp.utn.edu.ar`, elegís las viandas y el turno. Si no tienes saldo, se abona la diferencia vía **Mercado Pago**. La acreditación es automática.",
        6: "La compra de viandas se hace con **una semana de anticipación**. El límite para comprar es el **viernes a las 21:00 hs**.",
        7: "Podés comunicarte enviando un mail a: **comedor@frlp.utn.edu.ar**."
    },
    # Área de Bolsa de Trabajo (7 Preguntas)
    "bolsa_trabajo": {
        1: "Tenés que completar el **formulario de inscripción** (disponible en el Instagram `@sau.utnfrlp` o en posters de la facultad) y **adjuntar tu currículum vitae**.",
        2: "El CV se carga a la base de datos de postulantes **al momento de completar el formulario de inscripción** en la Bolsa de Trabajo.",
        3: "Las propuestas laborales se envían por **correo únicamente a los estudiantes que cumplen con los requisitos** solicitados por la empresa.",
        4: "Sí, se te enviará un correo con la oferta siempre que cumplas con los requisitos solicitados y **podés postularte a todas las ofertas que recibas**.",
        5: "El primer contacto lo realiza la facultad. Luego, si mostrás interés y envías tu CV, la **empresa se comunicará directamente con vos** para continuar el proceso.",
        6: "Tenés que **enviar un mail a la bolsa de trabajo** y ellos se encargan de realizar la baja.",
        7: "Sí, tenés que **enviar la nueva versión a la Bolsa de Trabajo** para que se reemplace la información anterior."
    },
    # Área de Pasantías (20 Preguntas)
    "pasantias": {
        1: "Las pasantías educativas son prácticas profesionales que permiten a los estudiantes aplicar sus conocimientos en un entorno laboral real. Pueden realizarlas los **estudiantes de educación superior que cumplan con los requisitos** establecidos.",
        2: "Primero tenés que **consultar qué pasantías existen** (hay varios convenios activos) y luego **completar el formulario de la bolsa de trabajo**.",
        3: "Los requisitos **varían según la pasantía** y los requerimientos de la empresa. Cada convocatoria específica el perfil y conocimientos. También es necesario haber aprobado un **mínimo de materias**.",
        4: "Las pasantías **no se publican** en ningún lugar, sino que **se les envía un mail a los alumnos** informando sobre dicho tema.",
        5: "No es necesario presentar ninguna documentación. Lo importante es la confección y firma correcta del **Convenio Marco** y el **Convenio Individual**.",
        6: "Sí, podés postularte a más de una propuesta, pero **solo podés quedar en una sola pasantía**.",
        7: "Sí, generalmente las pasantías estudiantiles son **todas remuneradas**, salvo alguna excepción.",
        8: "La duración depende de cada convocatoria. Normalmente dura entre **3 meses y 1 año**, con posibilidad de renovar 1 vez.",
        9: "Tenés que cumplir con **20 horas semanales**, según lo establecido en la normativa vigente.",
        10: "Sí, las pasantías están diseñadas para poder realizarse **en paralelo con la cursada**, respetando la carga horaria máxima.",
        11: "Se otorga una certificación **solo en caso de ser necesario**, ya que la información queda asentada con el convenio individual.",
        12: "Sí, se hacen **seguimientos esporádicos** para regular que se cumpla la ley.",
        13: "Sí, todas las pasantías están reguladas por la **Ley Nacional N.° 26.427**, que garantiza que se realicen bajo condiciones legales.",
        14: "Sirve para: ganar **experiencia laboral y profesional**, obtener **conocimiento** y tener un **ingreso mínimo** que permita continuar los estudios.",
        15: "No, si eso sucede debes **acudir a la Secretaría de Asuntos Universitarios**.",
        16: "Debes **enviar un correo a SAU con bolsa de trabajo** o acercarte personalmente.",
        17: "La información siempre viene de la empresa. Si llega por parte de la empresa, hay que asegurarse que exista **convenio marco** entre la empresa y la facultad, y ahí se puede avanzar.",
        18: "En caso de que haya 2 propuestas o más, podés elegir cuál te interesa, pero esto tiene que ser **previo al Convenio Individual (CI)**.",
        19: "La baja se realiza mediante una **adenda solicitando a la empresa** y al estudiante los motivos. El área administrativa de la bolsa de trabajo realiza una adenda para adjuntar al expediente.",
        20: "Podés **enviar un mail a la Secretaría de Asuntos Universitarios** solicitando la baja o podés acercarte directamente a la oficina."
    }
}

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

    def _responder_submenu(self, dispatcher: CollectingDispatcher, contexto: Text, num: int) -> None:
        """Función auxiliar para responder preguntas de submenús y volver a mostrar el menú."""
        respuesta = FAQ_RESPUESTAS.get(contexto, {}).get(num)
        
        if respuesta:
            dispatcher.utter_message(text=respuesta)
            dispatcher.utter_message(response=f"utter_menu_{contexto}")
        else:
            # Opción numérica que existe pero no tiene contenido (p. ej. en submenú)
            dispatcher.utter_message(text="Lo siento, esa opción no es válida o aún no tiene contenido. Por favor, elegí un número de la lista o volvé al menú principal.")
            dispatcher.utter_message(response=f"utter_menu_{contexto}")

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

        # --- NAVEGACIÓN PRINCIPAL ---
        if contexto == "principal":
            if num == 1:
                dispatcher.utter_message(response="utter_menu_becas")
                events.append(SlotSet("contexto_menu", "becas"))
            elif num == 2:
                dispatcher.utter_message(response="utter_menu_boleto_estudiantil")
                events.append(SlotSet("contexto_menu", "boleto_estudiantil"))
            elif num == 3:
                dispatcher.utter_message(response="utter_menu_deportes")
                events.append(SlotSet("contexto_menu", "deportes"))
            elif num == 4:
                dispatcher.utter_message(response="utter_menu_comedor")
                events.append(SlotSet("contexto_menu", "comedor"))
            elif num == 5:
                dispatcher.utter_message(response="utter_menu_bolsa_trabajo")
                events.append(SlotSet("contexto_menu", "bolsa_trabajo"))
            elif num == 6:
                dispatcher.utter_message(response="utter_menu_pasantias")
                events.append(SlotSet("contexto_menu", "pasantias"))
            elif num == 7:
                dispatcher.utter_message(response="utter_salir")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")
        
        # --- NAVEGACIÓN SUBMENÚS (Y VOLVER AL MENÚ PRINCIPAL) ---
        
        # SUBMENÚ BECAS (8 preguntas + 9 para volver)
        elif contexto == "becas":
            if 1 <= num <= 8:
                self._responder_submenu(dispatcher, "becas", num)
            elif num == 9: # Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")

        # SUBMENÚ BOLETO ESTUDIANTIL (11 preguntas + 12 para volver)
        elif contexto == "boleto_estudiantil":
            if 1 <= num <= 11:
                self._responder_submenu(dispatcher, "boleto_estudiantil", num)
            elif num == 12: # Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")

        # SUBMENÚ DEPORTES (7 preguntas + 8 para volver)
        elif contexto == "deportes":
            if 1 <= num <= 7:
                self._responder_submenu(dispatcher, "deportes", num)
            elif num == 8: # Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")

        # SUBMENÚ COMEDOR (7 preguntas + 8 para volver)
        elif contexto == "comedor":
            if 1 <= num <= 7:
                self._responder_submenu(dispatcher, "comedor", num)
            elif num == 8: # Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")
                
        # SUBMENÚ BOLSA DE TRABAJO (7 preguntas + 8 para volver)
        elif contexto == "bolsa_trabajo":
            if 1 <= num <= 7:
                self._responder_submenu(dispatcher, "bolsa_trabajo", num)
            elif num == 8: # Volver al menú principal
                dispatcher.utter_message(response="utter_menu_principal")
                events.append(SlotSet("contexto_menu", "principal")) 
            else:
                dispatcher.utter_message(response="utter_fallback")

        # SUBMENÚ PASANTIAS (20 preguntas + 21 para volver)
        elif contexto == "pasantias":
            if 1 <= num <= 20:
                self._responder_submenu(dispatcher, "pasantias", num)
            elif num == 21: # Volver al menú principal
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

    def _manejar_pregunta_libre(self, dispatcher: CollectingDispatcher, intent: Text, area: Text, num_pregunta_default: int) -> None:
        """Función auxiliar para responder preguntas de conocimiento libre con la primera respuesta del área."""
        respuesta = FAQ_RESPUESTAS.get(area, {}).get(num_pregunta_default)
        if respuesta:
            # Enviamos la respuesta base
            dispatcher.utter_message(text=respuesta)
            # Ofrecemos ver el menú del área para más detalle
            dispatcher.utter_message(text=f"Si deseas más detalles sobre {area.replace('_', ' ')}, puedes ver el menú completo eligiendo esa opción.")
        else:
            # Fallback si no encuentra la respuesta base
            dispatcher.utter_message(response="utter_fallback")

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        events = []
        
        # --- Manejo de comandos de texto (que no fueron clasificados como elegir_opcion) ---
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

        # --- Manejo de preguntas de conocimiento (Intents específicos) ---
        elif intent == "preguntar_becas":
            self._manejar_pregunta_libre(dispatcher, intent, "becas", 1) # Respuesta a '¿Qué tipos de becas existen?'
        elif intent == "preguntar_boleto_estudiantil":
            self._manejar_pregunta_libre(dispatcher, intent, "boleto_estudiantil", 1) # Respuesta a '¿Cómo solicito el boleto estudiantil?'
        elif intent == "preguntar_deportes":
            self._manejar_pregunta_libre(dispatcher, intent, "deportes", 1) # Respuesta a '¿Qué deportes ofrece la facultad?'
        elif intent == "preguntar_comedor":
            self._manejar_pregunta_libre(dispatcher, intent, "comedor", 1) # Respuesta a '¿Cuáles son los horarios del comedor universitario?'
        elif intent == "preguntar_bolsa_trabajo":
            self._manejar_pregunta_libre(dispatcher, intent, "bolsa_trabajo", 1) # Respuesta a '¿Cómo me inscribo en la bolsa de trabajo?'
        elif intent == "preguntar_pasantias":
            self._manejar_pregunta_libre(dispatcher, intent, "pasantias", 1) # Respuesta a '¿Qué son las pasantías y quiénes pueden realizarlas?'
        
        else:
            # Fallback del modo libre (si la IA no entiende la pregunta)
            dispatcher.utter_message(response="utter_fallback")
            dispatcher.utter_message(response="utter_menu_principal")
            events.append(SlotSet("contexto_menu", "principal"))

        # Limpiamos los slots de modo libre y aseguramos el modo conversacion al salir de la accion
        events.append(SlotSet("texto_opcion", None))
        events.append(SlotSet("modo_conversacion", "menu")) 
        return events
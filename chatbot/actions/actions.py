from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, List, Any, Dict

# =======================================================
# 0. BASE DE CONOCIMIENTO
# =======================================================

FAQ_RESPUESTAS = {
    # Área de Becas (8 Preguntas)
    "becas": {
        1: (
            "En nuestra facultad contamos con distintos tipos de *becas*:\n\n"
            "*Becas Nacionales:*\n"
            "• *Beca Manuel Belgrano:* duración inicial de 12 meses, renovable hasta 3 años para carreras de pregrado "
            "y hasta 5 años para carreras de grado. Monto mensual: $81.685.\n"
            "  - Requisitos: ser argentino/a (nativo o naturalizado, con DNI), estudiante regular en universidad pública "
            "(nacional o provincial) en carrera estratégica.\n"
            "  - Edad: ingresantes entre 18 y 30 años; estudiantes avanzados hasta 35 años; sin límite para personas con "
            "discapacidad o familias monoparentales con hijos menores (con documentación).\n"
            "  - Condición socioeconómica: ingresos del hogar no deben superar los 3 Salarios Mínimos, Vitales y Móviles.\n"
            "  - Requisito académico (para cursantes): haber aprobado al menos 2 materias cuatrimestrales o 1 anual en 2024. "
            "Ingresantes del primer semestre 2025 quedan exentos.\n\n"
            "• *Beca Fundación YPF:* duración de 12 meses (renovable), con monto total anual de $335.000 en 9 cuotas mensuales "
            "de abril a diciembre.\n"
            "  - Requisitos: ser argentino/a nativo/a o por opción. Ingresantes hasta 24 años, avanzados hasta 26 años.\n"
            "  - Cursar una carrera de grado vinculada a ingeniería, ciencias de la tierra, tecnología o gestión ambiental "
            "en una universidad pública.\n"
            "  - Ingresantes: egresado del nivel medio sin materias adeudadas.\n"
            "  - Avanzados: tener entre 35% y 50% del plan aprobado.\n"
            "  - Se solicita carta de recomendación, carta de interés y documentación respaldatoria.\n\n"
            "• *Beca Progresar:* monto base mensual de $35.000.\n"
            "  - Ingresantes: cobran el 80% mensual ($28.000), con retención del 20% liberado tras tres certificaciones anuales, "
            "sumando 3 cuotas estímulo adicionales.\n"
            "  - Estudiantes avanzados: cobran el 100% mensual y también reciben las 3 cuotas estímulo tras la tercera certificación.\n"
            "  - Requisitos: ingresantes entre 17 y 24 años; avanzados hasta 30 años.\n\n"
            "*Becas de Rectorado:*\n"
            "Incluyen las de *investigación*, *servicio* y las *Becas BASE* (Becas de Ayuda Socio-Económica)."
        ),
        2: "La inscripción se realiza de manera *online* a través de los formularios oficiales publicados en la convocatoria correspondiente. El enlace y las instrucciones se comparten en los canales oficiales de la Secretaría de Asuntos Universitarios.",
        3: "Requisitos generales: Cursar alguna carrera en la Universidad Tecnológica Nacional, *no poseer título universitario* y cursar como mínimo *3 materias* durante el año.",
        4: "La documentación varía, pero suele incluir: *DNI y constancia de CUIL*, *certificado de alumno regular, analítico* (o en trámite/constancia de materias aprobadas y promedio), y *documentación socioeconómica* o cualquier otro documento que la convocatoria especifique.",
        5: "Las fechas se publican en los *canales oficiales* de la facultad y de la Secretaría de Asuntos Universitarios.",
        6: "Sí, podés postularte a más de una beca en simultáneo, pero *solo podrás beneficiarte de una de ellas*.",
        7: "Se te informará directamente por los *medios de contacto* que hayas registrado en tu postulación.",
        8: "Sí, siempre que cumplas con los requisitos establecidos por la beca y presentes la *solicitud de renovación en tiempo y forma*."
    },
    # Área de Boleto Estudiantil (11 Preguntas)
    "boleto_estudiantil": {
        1: "Para solicitarlo, primero debés *registrar tu tarjeta SUBE* a tu nombre (argentina.gob.ar/sube). Luego, completá el *formulario de inscripción* en el sitio oficial del Boleto Estudiantil. Finalmente, recibirás un turno o indicación para *presentarte con tu documentación y activar el beneficio*.",
        2: "Los requisitos varían, pero en general se solicita: ser *alumno/a regular*, tener *tarjeta SUBE nominada* a tu nombre, cumplir con una *distancia mínima* entre domicilio e institución (más de 2 km), y *no recibir otro beneficio similar*.",
        3: "Después de la inscripción online, el trámite se completa de forma *presencial* en las sedes indicadas en tu provincia o ciudad (dependencias de gobierno, comunas, delegaciones municipales o sucursales de Correo Argentino, según corresponda).",
        4: "Una vez activada, el beneficio comienza a funcionar a partir del *primer día del ciclo lectivo* o, en algunos casos, desde el *mes siguiente* a la inscripción, dependiendo de la fecha en que se hizo el trámite.",
        5: "Debés *dar de baja la tarjeta* desde tu cuenta de “Mi SUBE” en la web oficial y registrar una nueva. Luego, tendrás que *reactivar el beneficio* en una Terminal Automática o mediante la aplicación autorizada para recuperar el saldo y los viajes.",
        6: "Sí. Es válido únicamente durante el *ciclo lectivo y de lunes a viernes*, quedando inactivo los fines de semana y feriados. La fecha exacta depende de la jurisdicción, pero generalmente es el último día hábil del ciclo escolar/académico.",
        7: "En muchos casos la renovación es *automática* si fuiste beneficiario el año anterior. Si no requiere reinscripción, solo debés pasar la tarjeta por una Terminal Automática. Si sí se requiere, debés completar nuevamente el formulario de solicitud en el sitio oficial.",
        8: "Depende de la jurisdicción y el nivel educativo. En la Provincia de Buenos Aires, los estudiantes universitarios y terciarios cuentan con hasta *45 viajes mensuales* con tarifa subsidiada.",
        9: "Sí, se puede utilizar en *colectivos, trenes y subtes* que acepten la tarjeta SUBE, siempre dentro de la jurisdicción donde se otorgó el beneficio.",
        10: "Debés *informar el cambio* en la plataforma del Boleto Estudiantil o en el punto de atención donde tramitaste el beneficio. Si seguís cumpliendo los requisitos, podrás mantener el boleto activo.",
        11: "Podés acercarte a la *Secretaría de Asuntos Universitarios* o realizar la denuncia a través de la página de denuncias del boleto especial estudiantil: `https://denuncias-bes.transporte.gba.gob.ar/denunciasboleto.php`."
    },
    # Área de Deportes (7 Preguntas)
    "deportes": {
        1: "Las disciplinas que ofrece la facultad son: *fútbol* (femenino y masculino), *básquet 5x5* (masculino), *básquet 3x3* (masculino) y *vóley* (femenino y masculino).",
        2: "Los horarios están disponibles en el *Instagram oficial de la Secretaría de Asuntos Universitarios*: `@sau.utnfrlp` o podés acercarte personalmente a la SAU.",
        3: "Es necesario completar el *formulario de inscripción* que se encuentra en el instagram `@sau.utnfrlp` y posteriormente presentar el *apto médico* correspondiente.",
        4: "Podés informarte acercándote a la *Secretaría de Asuntos Universitarios* o consultando directamente con los *profesores* de cada disciplina.",
        5: "Sí, es posible participar en *más de una disciplina*.",
        6: "No, *no es necesario* contar con experiencia previa.",
        7: "No, *no es obligatorio* participar en las competencias, podés acercarte únicamente a entrenar."
    },
    # Área de Comedor (7 Preguntas)
    "comedor": {
        1: "El retiro de viandas se realiza de *lunes a viernes de 12:00 a 14:00 y de 19:00 a 21:00*, en el SUM de la facultad.",
        2: "Las viandas cuestan *$2500*.",
        3: "El menú diario tiene las siguientes opciones: *convencional, vegetariano, pan y postres, y también apto para celíacos*. Se comparte por las historias de Instagram de la Secretaría de Asuntos Universitarios: `@sau.utnfrlp`.",
        4: "Debes registrar el usuario, si no estás registrado en el sistema, completá el *formulario de inscripción* en el instagram `@sau.utnfrlp`.",
        5: "Debes ingresar a `https://ticket.frlp.utn.edu.ar`, elegís las viandas y el turno. Si no tienes saldo, se abona la diferencia vía *Mercado Pago*. La acreditación es automática.",
        6: "La compra de viandas se hace con *una semana de anticipación*. El límite para comprar es el *viernes a las 21:00 hs*.",
        7: "Podés comunicarte enviando un mail a: *comedor@frlp.utn.edu.ar*."
    },
    # Área de Bolsa de Trabajo (7 Preguntas)
    "bolsa_trabajo": {
        1: "Tenés que completar el *formulario de inscripción* (disponible en el Instagram `@sau.utnfrlp` o en posters de la facultad) y *adjuntar tu currículum vitae*.",
        2: "El CV se carga a la base de datos de postulantes *al momento de completar el formulario de inscripción* en la Bolsa de Trabajo.",
        3: "Las propuestas laborales se envían por *correo únicamente a los estudiantes que cumplen con los requisitos* solicitados por la empresa.",
        4: "Sí, se te enviará un correo con la oferta siempre que cumplas con los requisitos solicitados y *podés postularte a todas las ofertas que recibas*.",
        5: "El primer contacto lo realiza la facultad. Luego, si mostrás interés y envías tu CV, la *empresa se comunicará directamente con vos* para continuar el proceso.",
        6: "Tenés que *enviar un mail a la bolsa de trabajo* y ellos se encargan de realizar la baja.",
        7: "Sí, tenés que *enviar la nueva versión a la Bolsa de Trabajo* para que se reemplace la información anterior."
    },
    # Área de Pasantías (20 Preguntas)
    "pasantias": {
        1: "Las pasantías educativas son prácticas profesionales que permiten a los estudiantes aplicar sus conocimientos en un entorno laboral real. Pueden realizarlas los *estudiantes de educación superior que cumplan con los requisitos* establecidos.",
        2: "Primero tenés que *consultar qué pasantías existen* (hay varios convenios activos) y luego *completar el formulario de la bolsa de trabajo*.",
        3: "Los requisitos *varían según la pasantía* y los requerimientos de la empresa. Cada convocatoria específica el perfil y conocimientos. También es necesario haber aprobado un *mínimo de materias*.",
        4: "Las pasantías *no se publican* en ningún lugar, sino que *se les envía un mail a los alumnos* informando sobre dicho tema.",
        5: "No es necesario presentar ninguna documentación. Lo importante es la confección y firma correcta del *Convenio Marco* y el *Convenio Individual*.",
        6: "Sí, podés postularte a más de una propuesta, pero *solo podés quedar en una sola pasantía*.",
        7: "Sí, generalmente las pasantías estudiantiles son *todas remuneradas*, salvo alguna excepción.",
        8: "La duración depende de cada convocatoria. Normalmente dura entre *3 meses y 1 año*, con posibilidad de renovar 1 vez.",
        9: "Tenés que cumplir con *20 horas semanales*, según lo establecido en la normativa vigente.",
        10: "Sí, las pasantías están diseñadas para poder realizarse *en paralelo con la cursada*, respetando la carga horaria máxima.",
        11: "Se otorga una certificación *solo en caso de ser necesario*, ya que la información queda asentada con el convenio individual.",
        12: "Sí, se hacen *seguimientos esporádicos* para regular que se cumpla la ley.",
        13: "Sí, todas las pasantías están reguladas por la *Ley Nacional N.° 26.427*, que garantiza que se realicen bajo condiciones legales.",
        14: "Sirve para: ganar *experiencia laboral y profesional*, obtener *conocimiento* y tener un *ingreso mínimo* que permita continuar los estudios.",
        15: "No, si eso sucede debes *acudir a la Secretaría de Asuntos Universitarios*.",
        16: "Debes *enviar un correo a SAU con bolsa de trabajo* o acercarte personalmente.",
        17: "La información siempre viene de la empresa. Si llega por parte de la empresa, hay que asegurarse que exista *convenio marco* entre la empresa y la facultad, y ahí se puede avanzar.",
        18: "En caso de que haya 2 propuestas o más, podés elegir cuál te interesa, pero esto tiene que ser *previo al Convenio Individual (CI)*.",
        19: "La baja se realiza mediante una *adenda solicitando a la empresa* y al estudiante los motivos. El área administrativa de la bolsa de trabajo realiza una adenda para adjuntar al expediente.",
        20: "Podés *enviar un mail a la Secretaría de Asuntos Universitarios* solicitando la baja o podés acercarte directamente a la oficina."
    }
}


# =======================================================
# 1. MAPEO DE INTENTS ESPECÍFICOS A FAQ 
# =======================================================

INTENT_TO_FAQ_MAP = {
    # --- ÁREA DE BECAS (8 preguntas) ---
    "preguntar_becas_tipos": ("becas", 1),
    "preguntar_becas_inscripcion": ("becas", 2),
    "preguntar_becas_requisitos": ("becas", 3),
    "preguntar_becas_documentacion": ("becas", 4),
    "preguntar_becas_fechas": ("becas", 5),
    "preguntar_becas_varias": ("becas", 6),
    "preguntar_becas_seleccion": ("becas", 7),
    "preguntar_becas_renovacion": ("becas", 8),

    # --- ÁREA DE BOLETO ESTUDIANTIL (11 preguntas) ---
    "preguntar_boleto_solicitud": ("boleto_estudiantil", 1),
    "preguntar_boleto_requisitos": ("boleto_estudiantil", 2),
    "preguntar_boleto_tramite_lugar": ("boleto_estudiantil", 3),
    "preguntar_boleto_habilitacion_tiempo": ("boleto_estudiantil", 4),
    "preguntar_boleto_perdida": ("boleto_estudiantil", 5),
    "preguntar_boleto_vencimiento": ("boleto_estudiantil", 6),
    "preguntar_boleto_renovacion": ("boleto_estudiantil", 7),
    "preguntar_boleto_viajes": ("boleto_estudiantil", 8),
    "preguntar_boleto_aplicacion": ("boleto_estudiantil", 9),
    "preguntar_boleto_cambio_carrera": ("boleto_estudiantil", 10),
    "preguntar_boleto_contacto_problemas": ("boleto_estudiantil", 11),

    # --- ÁREA DE DEPORTES (7 preguntas) ---
    "preguntar_deportes_oferta": ("deportes", 1),
    "preguntar_deportes_horarios": ("deportes", 2),
    "preguntar_deportes_documentacion": ("deportes", 3),
    "preguntar_deportes_competencias": ("deportes", 4),
    "preguntar_deportes_varios": ("deportes", 5),
    "preguntar_deportes_experiencia": ("deportes", 6),
    "preguntar_deportes_obligacion": ("deportes", 7),

    # --- ÁREA DE COMEDOR (7 preguntas) ---
    "preguntar_comedor_horarios": ("comedor", 1),
    "preguntar_comedor_precios": ("comedor", 2),
    "preguntar_comedor_menu": ("comedor", 3),
    "preguntar_comedor_inscripcion": ("comedor", 4),
    "preguntar_comedor_compra": ("comedor", 5),
    "preguntar_comedor_reserva": ("comedor", 6),
    "preguntar_comedor_contacto": ("comedor", 7),

    # --- ÁREA DE BOLSA DE TRABAJO (7 preguntas) ---
    "preguntar_bolsa_inscripcion": ("bolsa_trabajo", 1),
    "preguntar_bolsa_cv_subida": ("bolsa_trabajo", 2),
    "preguntar_bolsa_ofertas": ("bolsa_trabajo", 3),
    "preguntar_bolsa_postulacion_multiple": ("bolsa_trabajo", 4),
    "preguntar_bolsa_contacto_empresa": ("bolsa_trabajo", 5),
    "preguntar_bolsa_eliminar_datos": ("bolsa_trabajo", 6),
    "preguntar_bolsa_cv_actualizar": ("bolsa_trabajo", 7),

    # --- ÁREA DE PASANTÍAS (20 preguntas) ---
    "preguntar_pasantias_que_son": ("pasantias", 1),
    "preguntar_pasantias_inscripcion": ("pasantias", 2),
    "preguntar_pasantias_requisitos": ("pasantias", 3),
    "preguntar_pasantias_publicacion": ("pasantias", 4),
    "preguntar_pasantias_documentacion": ("pasantias", 5),
    "preguntar_pasantias_multiple": ("pasantias", 6),
    "preguntar_pasantias_remuneracion": ("pasantias", 7),
    "preguntar_pasantias_duracion": ("pasantias", 8),
    "preguntar_pasantias_horas_semanales": ("pasantias", 9),
    "preguntar_pasantias_cursada": ("pasantias", 10),
    "preguntar_pasantias_certificacion": ("pasantias", 11),
    "preguntar_pasantias_seguimiento": ("pasantias", 12),
    "preguntar_pasantias_ley_proteccion": ("pasantias", 13),
    "preguntar_pasantias_utilidad": ("pasantias", 14),
    "preguntar_pasantias_exceso_horas": ("pasantias", 15),
    "preguntar_pasantias_contacto_problema": ("pasantias", 16),
    "preguntar_pasantias_proceso_gestion": ("pasantias", 17),
    "preguntar_pasantias_elegir_empresa": ("pasantias", 18),
    "preguntar_pasantias_baja": ("pasantias", 19),
    "preguntar_pasantias_baja_base_datos": ("pasantias", 20),
}


# =======================================================
# 2. ACTION DETECTAR MODO 
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
        
        # Si NLU clasificó como elegir_opcion
        if intent == "elegir_opcion" and num_val:
            return [
                SlotSet("modo_conversacion", "menu"),
                FollowupAction("action_manejar_menu")
            ]

        # Si no es una opción, es modo libre
        user_message = tracker.latest_message.get("text", "").strip().lower()
        return [
            SlotSet("modo_conversacion", "libre"),
            SlotSet("texto_opcion", user_message),
            FollowupAction("action_responder_modo_libre")
        ]

# =======================================================
# 3. ACTION MANEJAR MENÚ
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
            # Opción numérica que existe pero no tiene contenido
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
# 4. NUEVA ACTION PARA MANEJAR VOLVER_ATRAS
# =======================================================

class ActionResetContextAndShowMainMenu(Action):
    """
    Acción dedicada a ser llamada por la regla 'volver_atras'.
    Restablece los slots de navegación y muestra el menú principal de forma directa.
    """
    def name(self) -> Text:
        return "action_reset_context_and_show_main_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Muestra el menú principal
        dispatcher.utter_message(response="utter_menu_principal")
        
        # Restablece el contexto al menú principal y limpia otros slots
        return [
            SlotSet("contexto_menu", "principal"),
            SlotSet("numero_opcion", None),
            SlotSet("modo_conversacion", "menu")
        ]


# =======================================================
# 5. ACTION RESPONDER MODO LIBRE
# =======================================================

class ActionResponderModoLibre(Action):
    """Responde a preguntas abiertas y comandos de texto usando el mapeo INTENT_TO_FAQ_MAP."""
    def name(self) -> Text:
        return "action_responder_modo_libre"

    # --- FUNCIÓN AUXILIAR  ---
    def _manejar_pregunta_libre(self, dispatcher: CollectingDispatcher, area: Text, num_pregunta: int, tracker: Tracker) -> None:
        """Función auxiliar para responder preguntas de conocimiento libre, obtener el contexto y repetir el menú."""
        respuesta = FAQ_RESPUESTAS.get(area, {}).get(num_pregunta)
        
        nombre_area = area.replace('_', ' ').title()
        
        contexto_menu = tracker.get_slot("contexto_menu") 
        utterance_menu = f"utter_menu_{contexto_menu}"

        if respuesta:
            dispatcher.utter_message(text=respuesta)
            dispatcher.utter_message(response=utterance_menu) 
        else:
            dispatcher.utter_message(text=f"Lo siento, no pude encontrar una respuesta específica para tu consulta sobre {nombre_area}.")
            dispatcher.utter_message(response="utter_fallback")

    # --- FUNCIÓN RUN  ---
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        events = []
        
        # --- Manejo de preguntas de conocimiento (Intents específicos mapeados) ---
        if intent in INTENT_TO_FAQ_MAP:
            # Obtenemos el área y el número de pregunta mapeado del diccionario
            area, num = INTENT_TO_FAQ_MAP[intent]
            
            self._manejar_pregunta_libre(dispatcher, area, num, tracker)
            
        else:
            # Fallback del modo libre (si la IA no entiende la pregunta o es out_of_scope)
            dispatcher.utter_message(response="utter_fallback")
            dispatcher.utter_message(response="utter_menu_principal")
            events.append(SlotSet("contexto_menu", "principal"))

        # Limpiamos los slots de modo libre y aseguramos el modo conversacion al salir de la accion
        events.append(SlotSet("texto_opcion", None))
        events.append(SlotSet("modo_conversacion", "menu")) 
        return events

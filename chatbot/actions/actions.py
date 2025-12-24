from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, List, Any, Dict

# =======================================================
# 0. TÍTULOS Y RESPUESTAS (OPTIMIZADO PARA UX)
# =======================================================

FAQ_TITULOS = {
    "becas": {
        1: "Tipos de Becas (Nac.)", 
        2: "Inscripción (Pasos)", 
        3: "Requisitos (Gral.)", 
        4: "Documentos a llevar",
        5: "Fechas (Calendario)", 
        6: "Múltiple Postulación", 
        7: "Ver Resultados", 
        8: "Renovación (Anual)"
    },
    "boleto_estudiantil": {
        1: "Cómo solicitarlo", 
        2: "Requisitos y Distancia", 
        3: "Sedes de trámite", 
        4: "¿Cuándo se activa?",
        5: "Pérdida (Sube/Robo)", 
        6: "Vencimiento (Días)", 
        7: "Renovación (Manual)", 
        8: "Viajes permitidos",
        9: "Trenes y Colectivos", 
        10: "Cambio de Carrera", 
        11: "Problemas (Denuncias)"
    },
    "deportes": {
        1: "Disciplinas (Oferta)", 
        2: "Horarios y Lugar", 
        3: "Inscripción (Médico)", 
        4: "Torneos y Competencia",
        5: "Hacer 2 deportes", 
        6: "Sin exp. previa", 
        7: "¿Es obligatorio?"
    },
    "comedor": {
        1: "Horarios (Viandas)", 
        2: "Precio ($2500)", 
        3: "Menú (Opciones)", 
        4: "Registro (Usuario)",
        5: "Comprar y Pagar", 
        6: "Reserva (Anticipada)", 
        7: "Mail de contacto"
    },
    "bolsa_trabajo": {
        1: "Cómo Inscribirse", 
        2: "Subir CV (Archivo)", 
        3: "Ofertas (Mail)", 
        4: "Postulación Múltiple",
        5: "Nexo con Empresas", 
        6: "Darse de Baja", 
        7: "Actualizar CV"
    },
    "pasantias": {
        1: "¿Qué es una pasantía?", 
        2: "Cómo empezar (Pasos)", 
        3: "Requisitos (Empresa)", 
        4: "¿Dónde se ven?",
        5: "Convenios (Firmas)", 
        6: "Hacer 2 pasantías", 
        7: "Pago (Sueldo)", 
        8: "Duración (Meses)",
        9: "Carga Horaria (20hs)", 
        10: "Pasantía y Cursada", 
        11: "Certificado Final", 
        12: "Control de la SAU",
        13: "Ley Nacional 26.427", 
        14: "Ventajas/Beneficios", 
        15: "Exceso de Horas", 
        16: "Consultas (Dudas)",
        17: "Gestión (Empresas)", 
        18: "Elegir entre 2 op.", 
        19: "Renunciar (Adenda)", 
        20: "Baja de Base Datos"
    }
}

FAQ_RESPUESTAS = {
    "becas": {
        1: (
            "En nuestra facultad contamos con:\n"
            "Becas Nacionales: como la Beca Manuel Belgrano, la Beca Progresar y las Becas de YPF.\n\n"
            "Becas de Rectorado: como las de investigación, de servicio y las Becas BASE (Becas de Ayuda Socio-Económica).\n"
            "En cuanto a las becas nacionales:\n"
            "La Beca Manuel Belgrano tiene una duración inicial de 12 meses, renovable hasta 3 años para carreras de pregrado y hasta 5 años para carreras de grado universitario. El monto mensual es de $81.685, y algunos requisitos generales son: ser argentino/a (nativo o naturalizado, con DNI), ser estudiante regular (ingresante o cursante) en universidad pública (nacional o provincial) en alguna carrera considerada estratégica. Y en cuanto a la edad: si sos ingresante: entre 18 y 30 años, si sos estudiante avanzado: hasta 35 años y sin límite de edad para personas con discapacidad o familias monoparentales con hijos menores (con documentación que lo respalde). En cuanto a la condición socioeconómica: los ingresos del hogar no deben superar los 3 Salarios Mínimos, Vitales y Móviles. Requisito académico para cursantes: haber aprobado al menos 2 materias cuatrimestrales o 1 materia anual durante 2024. Los ingresantes del primer semestre 2025 quedan exentos de ese requisito.\n"
            "La Beca Fundación YPF, tiene una duración anual de 12 meses, con posibilidad de renovación si se cumplen los requisitos, el monto de la beca es de $335.000 en 9 cuotas mensuales de abril a diciembre. Los requisitos son: ser argentino nativo o por opción, si sos ingresante hasta los 24 años, si sos estudiante avanzado hasta los 26 años, Cursar una carrera de grado vinculada a ingeniería, ciencias de la tierra, tecnología o gestión ambiental en una universidad pública.\n"
            "Para los ingresantes: ser egresado del nivel medio sin adeudar materias y para los estudiantes avanzados: tener entre 35 % y 50 % del plan de estudios aprobado. Se debe presentar carta de recomendación, carta de interés y documentación respaldatoria.\n"
            "La Beca Progresar tiene un monto base mensual de $35.000, pero tenemos las retenciones y esquema de pago, para estudiantes ingresantes: se paga el 80% mensualmente, es decir, $28.000, reteniéndose el 20% hasta completar tres certificaciones anuales; luego se libera con 3 cuotas estímulo adicionales al año, para estudiantes avanzados: cobran el 100% del monto desde la primera cuota, y también reciben esas 3 cuotas estímulo tras la tercera certificación académica, como requisitos generales para los ingresantes: entre 17 y 24 años y para estudiantes avanzados hasta los 30 años."
        ),
        2: "La inscripción se realiza de manera online a través de los formularios oficiales publicados en la convocatoria correspondiente. El enlace y las instrucciones se comparten en los canales oficiales de la Secretaría de Asuntos Universitarios.",
        3: "Cursar alguna carrera en la Universidad Tecnológica Nacional, no poseer título universitario y cursar como mínimo 3 materias durante el año",
        4: "La documentación varía según la beca, pero suele incluir: DNI y constancia de CUIL, certificado de alumno regular, analítico, certificado de analitico en tramite o constancia de materias aprobadas y promedio, documentación socioeconómica o cualquier otro documento que la convocatoria especifique.",
        5: "Las fechas se publican en los canales oficiales de la facultad y de la Secretaría de Asuntos Universitarios.",
        6: "Sí, podés postularte a más de una beca en simultáneo, pero solo podrás beneficiarte de una de ellas.",
        7: "Se te informará directamente por los medios de contacto que hayas registrado en tu postulación.",
        8: "Sí, siempre que cumplas con los requisitos establecidos por la beca y presentes la solicitud de renovación en tiempo y forma."
    },
    "boleto_estudiantil": {
        1: "Para solicitar el boleto estudiantil primero debés registrar tu tarjeta SUBE a tu nombre a través de la página oficial (argentina.gob.ar/sube). Luego, completá el formulario de inscripción en el sitio oficial del Boleto Estudiantil. Una vez enviado, recibirás un turno o indicación para presentarte con tu documentación y activar el beneficio.",
        2: "Los requisitos varían según el nivel educativo y la provincia, pero en general se solicita: ser alumno/a regular, tener tarjeta SUBE nominada a tu nombre, cumplir con una distancia mínima entre tu domicilio y la institución educativa (más de 2 km), no recibir otro beneficio similar.",
        3: "Después de la inscripción online, el trámite se completa de forma presencial en las sedes indicadas en tu provincia o ciudad. Puede ser en dependencias del gobierno, comunas, delegaciones municipales o sucursales de Correo Argentino, según corresponda.",
        4: "Una vez activada la tarjeta SUBE Estudiantil, el beneficio comienza a funcionar a partir del primer día del ciclo lectivo o, en algunos casos, desde el mes siguiente a la inscripción, dependiendo de la fecha en la que se haya realizado el trámite.",
        5: "Debés dar de baja la tarjeta desde tu cuenta de “Mi SUBE” en la web oficial y registrar una nueva tarjeta a tu nombre. Luego, tendrás que reactivar el beneficio en una Terminal Automática o mediante la aplicación autorizada, para recuperar el saldo y los viajes correspondientes.",
        6: "Sí. El beneficio es válido únicamente durante el ciclo lectivo y de lunes a viernes, quedando inactivo los fines de semana y feriados. La fecha exacta de vencimiento depende de la jurisdicción, pero en general es el último día hábil del ciclo escolar o académico.",
        7: "En muchos casos, la renovación es automática si ya fuiste beneficiario el año anterior. Pero en algunas provincias o municipios es necesario volver a validar la tarjeta o inscribirse nuevamente. Si tu provincia o ciudad no requiere reinscripción, solo deberás pasar la tarjeta SUBE por una Terminal Automática para habilitar la carga mensual de viajes. En los casos donde sí se requiere reinscripción, deberás completar nuevamente el formulario de solicitud en el sitio oficial.",
        8: "La cantidad de viajes depende de la jurisdicción y el nivel educativo. En la Provincia de Buenos Aires, los estudiantes universitarios y terciarios cuentan con hasta 45 viajes mensuales con tarifa subsidiada.",
        9: "Sí, el Boleto Estudiantil se puede utilizar en colectivos, trenes y subtes que acepten la tarjeta SUBE, siempre dentro de la jurisdicción donde se otorgó el beneficio.",
        10: "Debés informar el cambio en la plataforma del Boleto Estudiantil o en el punto de atención donde tramitaste el beneficio. Si seguís cumpliendo los requisitos y estudiando en una institución habilitada, podrás mantener el boleto activo.",
        11: "Podes acercarte a la Secretaría de Asuntos Universitarios o realizar la denuncia a través de la pagina de denuncias del boleto especial estudiantil: https://denuncias-bes.transporte.gba.gob.ar/denunciasboleto.php"
    },
    "deportes": {
        1: "Las disciplinas que ofrece la facultad son: fútbol (femenino y masculino), básquet 5x5 (masculino), básquet 3x3 (masculino) y vóley (femenino y masculino).",
        2: "Los horarios se encuentran disponibles en el Instagram oficial de la Secretaría de Asuntos Universitarios: @sau.utnfrlp o podes acercarte personalmente a la SAU.",
        3: "Es necesario completar el formulario de inscripción que se encuentra en el instagram de la Secretaría de Asuntos Universitarios: @sau.utnfrlp y posteriormente presentar el apto médico correspondiente en caso de no tenerlo. Ante cualquier duda acerca del mismo podes acercarte a la SAU o consultar por nuestro instagram.",
        4: "Podés informarte acercándote a la Secretaría de Asuntos Universitarios o consultando directamente con los profesores de cada disciplina.",
        5: "Sí, es posible participar en más de una disciplina.",
        6: "No, no es necesario contar con experiencia previa.",
        7: "No, no es obligatorio participar en las competencias, podés acercarte únicamente a entrenar."
    },
    "comedor": {
        1: "Para el retiro de viandas se realiza de lunes a viernes de 12:00 a 14:00 y de 19:00 a 21:00, en el SUM de la facultad",
        2: "Las viandas cuestan $2500",
        3: "En el menú diario se encuentran las siguientes opciones: convencional, vegetariano, pan y postres y también apto para celíacos. el menu sera fijo todas las semanas y se compartirá por medio de las historias de instagram de la Secretaría de Asuntos Universitarios: @sau.utnfrlp",
        4: "Debes registrar el usuario, si no estás registrado en el sistema completa el formulario de inscripción que se encuentra en el instagram de la secretaría de asuntos universitarios: @sau.utnfrlp, el alta de los usuarios se realiza de lunes a viernes a partir de las 10:00 hs, vas a recibir un correo con los datos correspondientes",
        5: (
            "Para comprar las viandas tenes que ingresar a: https://ticket.frlp.utn.edu.ar, luego elegís las viandas que quieras comprar y el turno en el cual vas a retirarla. "
            "Si te quedo saldo cargado, lo usas para comprar las viandas, y en el caos de que no tengas saldo suficiente, deberás abonar la diferencia vía Mercado Pago, luego confirmas la compra y la plataforma del comedor te va a redirigir a Mercado Pago para que efectues el pago. "
            "Una vez hayas realizado esto, se te redirigirá automáticamente a la página del comedor, donde podrás visualizar las viandas que compraste y el estado de las mismas. "
            "La acreditación es automática, te llegará un mail a tu correo informando el pago, si está pendiente o fue rechazado. tener en cuenta que algunos medios de pago pueden tardar hasta una hora en acreditarse"
        ),
        6: "La compra de viandas se hace con una semana de anticipación, las viandas que compras durante la semana, las vas a retirar la semana siguiente y el límite para comprar es el viernes a las 21:00 hs.",
        7: "Podes comunicarte enviando un mail a: comedor@frlp.utn.edu.ar"
    },
    "bolsa_trabajo": {
        1: "Para inscribirte tenes que completar el formulario de inscripción el cual lo podés encontrar en el instagram de la Secretaría de Asuntos Universitarios: @sau.utnfrlp o en los posters colgados por las diferentes áreas de las facultad y tenés que adjuntar tu currículum vitae. Una vez inscripto/a, tus datos quedarán registrados en la base de datos de postulantes de la Facultad.",
        2: "El CV se carga a la base de datos de postulantes al momento de completar el formulario de inscripción en la Bolsa de Trabajo.",
        3: "Las propuestas laborales se envían por correo únicamente a los estudiantes que cumplen con los requisitos solicitados por la empresa.",
        4: "Sí, se te enviará un correo con la oferta laboral siempre que cumplas con los requisitos solicitados y podés postularte a todas las ofertas que recibas.",
        5: "El primer contacto lo realiza la facultad con la empresa, la cual nos envía la propuesta laboral para que hagamos la difusión, luego les enviamos la oferta laboral a los postulantes que cumplan con los requisitos mínimos establecidos por la empresa solicitante. Si mostrás interés y les envías tu CV, la empresa se comunicará directamente con vos para continuar el proceso.",
        6: "Si ya no querés recibir más propuestas laborales tenes que enviar un mail a la bolsa de trabajo y nosotros nos encargamos de realizar la baja.",
        7: "Sí, podés actualizar tu CV. Para hacerlo, tenés que enviar la nueva versión a la Bolsa de Trabajo para que se reemplace la información anterior."
    },
    "pasantias": {
        1: "Las pasantías educativas son prácticas profesionales que permiten a los estudiantes aplicar sus conocimientos en un entorno laboral real y pueden realizarlas los estudiantes de educación superior que cumplan con los requisitos establecidos por la facultad y la normativa vigente.",
        2: "Primero tenes que consultar qué pasantías existen, actualmente hay varios convenios activos, para empezar a participar tenes que completar el formulario de la bolsa de trabajo. Es importante tener en cuenta que la empresa abre y cierra los programas de pasantías, cuando se informa por una pasantía también se informa de los convenios marco y se establece un convenio individual y una vez se avanzó con dichos documentos, a partir de ahí arranca la actividad. Nosotros les enviaremos la información sobre las pasantías, incluidos los convenios",
        3: "Los requisitos varían según la pasantía, es decir, dependiendo de los requerimientos de la empresa). Cada convocatoria específica el perfil buscado, la carrera o conocimientos requeridos. Y también es necesario que hayan pasado un mínimo de materias",
        4: "Las pasantías no se publican en ningún lugar, sino que más bien se les envía un mail a los alumnos informando sobre dicho tema.",
        5: "No es necesario presentar ninguna documentación, lo importante es la confección del Convenio Marco y que se encuentre correctamente conformado y firmado el Convenio Individual.",
        6: "Sí, siempre que cumplas con los requisitos de cada propuesta, pero solo podes quedar en una sola pasantía.",
        7: "Sí, generalmente las pasantías estudiantiles son todas remuneradas salvo alguna excepción.",
        8: "La duración depende de lo establecido en cada convocatoria, siempre dentro de los plazos que permite la normativa vigente. Normalmente dura entre 3 meses y 1 año con posibilidad de renovar 1 vez.",
        9: "Tenés que cumplir con 20 horas semanales, según lo establecido en la normativa vigente.",
        10: "Sí, las pasantías están diseñadas para poder realizarse en paralelo con la cursada, respetando la carga horaria máxima.",
        11: "Se otorga una certificación solo en caso de ser necesario, ya que la información queda asentada con el convenio individual.",
        12: "Sí, se hacen seguimientos esporádicos para regular que se cumpla la ley.",
        13: "Sí, todas las pasantías están reguladas por la Ley Nacional N.° 26.427, que garantiza que se realicen bajo condiciones legales.",
        14: "destacar experiencia laboral y profesional siendo estudiante, obtención de conocimiento y además tener un ingreso mínimo que permita continuar los estudios",
        15: "no, si eso sucede acudir a la secretaría de asuntos universitarios",
        16: "enviar correo a sau con bolsa de trabajo o acercarse personalmente",
        17: "la info siempre viene de la empresa, nos llega la información y la publicamos, si llega de la bolsa de trabajo desde nosotros es porque ya hay un convenio marco establecido, si llega por parte de la empresa hay que asegurarse que exista convenio marca entre la empresa y la facultad, y ahí se puede avanzar.",
        18: "en caso de que haya 2 propuestas o mas podes elegir cual te interesa, eso tiene que ser previo al ci",
        19: "La baja de una pasantía se realiza mediante una adenda solicitando a la empresa, y en caso de ser necesario también al estudiante, los motivos por el cual solicita la baja y desde el área administrativa de la bolsa de trabajo, realizaremos una adenda para adjuntar con el expediente dejando asentado la baja del estudiante.",
        20: "Para solicitar la baja de la base de datos de pasantía, podes enviar un mail a la Secretaría de Asuntos Universitarios solicitando la baja o podés acercarte directamente a la oficina."
    }
}

MENUS_CONFIG = {
    "principal": {"titulo": "Menú Principal", "filas": 7},
    "becas": {"titulo": "Becas", "filas": 8},
    "boleto_estudiantil": {"titulo": "Boleto", "filas": 11},
    "deportes": {"titulo": "Deportes", "filas": 7},
    "comedor": {"titulo": "Comedor", "filas": 7},
    "bolsa_trabajo": {"titulo": "Bolsa de Trabajo", "filas": 7},
    "pasantias": {"titulo": "Pasantías", "filas": 20}
}

# =======================================================
# 1. ACCIONES DE MENÚ
# =======================================================

class ActionMostrarMenuActual(Action):
    def name(self) -> Text:
        return "action_mostrar_menu_actual"

    def run(self, dispatcher, tracker, domain):
        contexto = tracker.get_slot("contexto_menu") or "principal"
        pagina = int(tracker.get_slot("pagina_menu") or 1)
        config = MENUS_CONFIG.get(contexto, MENUS_CONFIG["principal"])
        
        opciones_visibles = []
        if contexto == "principal":
            areas = ["Becas", "Boleto Estudiantil", "Deportes", "Comedor", "Bolsa de Trabajo", "Pasantías", "Salir"]
            for i, nombre in enumerate(areas, 1):
                opciones_visibles.append({"id": str(i), "title": nombre})
        else:
            titulos_area = FAQ_TITULOS.get(contexto, {})
            # Definimos un tamaño fijo de 7 (WSP ADMITE MAXIMO 10)
            TAMANO_PAGINA = 7
            inicio = (pagina - 1) * TAMANO_PAGINA
            fin_rango = inicio + TAMANO_PAGINA
            
            for i in range(inicio + 1, min(fin_rango + 1, config["filas"] + 1)):
                if i in titulos_area:
                    opciones_visibles.append({
                        "id": str(i),
                        "title": titulos_area[i][:24]
                    })

            # Botones de navegación (solo si corresponden)
            if fin_rango < config["filas"]:
                opciones_visibles.append({"id": "next", "title": "➡️ Ver más preguntas"})
            if pagina > 1:
                opciones_visibles.append({"id": "prev", "title": "⬅️ Anterior"})
            
            opciones_visibles.append({"id": "99", "title": "🏠 Menú Principal"})

        dispatcher.utter_message(json_message={
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Asistente UTN"},
                "body": {"text": f"📍 *{config['titulo']}*\nElegí una opción:"},
                "action": {"button": "Ver Opciones", "sections": [{"title": "Lista", "rows": opciones_visibles}]}
            }
        })
        return [SlotSet("numero_opcion", None)]

class ActionManejarMenu(Action):
    def name(self) -> Text:
        return "action_manejar_menu"

    def run(self, dispatcher, tracker, domain):
        opcion_raw = tracker.get_slot("numero_opcion") or tracker.latest_message.get('text')
        contexto = tracker.get_slot("contexto_menu") or "principal"
        pagina = int(tracker.get_slot("pagina_menu") or 1)

        if not opcion_raw:
            return [FollowupAction("action_mostrar_menu_actual")]

        opcion_str = str(opcion_raw).lower().strip()

        # 1. LÓGICA DE NAVEGACIÓN
        if any(x in opcion_str for x in ["next", "ver más", "ver mas"]):
            return [SlotSet("pagina_menu", pagina + 1), FollowupAction("action_mostrar_menu_actual")]
        
        if any(x in opcion_str for x in ["prev", "anterior"]):
            return [SlotSet("pagina_menu", max(1, pagina - 1)), FollowupAction("action_mostrar_menu_actual")]
            
        if "99" in opcion_str or "principal" in opcion_str:
            return [SlotSet("contexto_menu", "principal"), SlotSet("pagina_menu", 1), FollowupAction("action_mostrar_menu_actual")]

        # 2. SELECCIÓN DE CATEGORÍAS (DESDE PRINCIPAL)
        if contexto == "principal":
            mapa = {"1":"becas","2":"boleto_estudiantil","3":"deportes","4":"comedor","5":"bolsa_trabajo","6":"pasantias"}
            if opcion_str in mapa:
                return [SlotSet("contexto_menu", mapa[opcion_str]), SlotSet("pagina_menu", 1), FollowupAction("action_mostrar_menu_actual")]
            
            # Buscar por nombre si no mandó el número
            for num_map, ctx_map in mapa.items():
                if ctx_map.replace("_", " ") in opcion_str:
                    return [SlotSet("contexto_menu", ctx_map), SlotSet("pagina_menu", 1), FollowupAction("action_mostrar_menu_actual")]

            if "7" in opcion_str or "salir" in opcion_str:
                dispatcher.utter_message(text="¡Chau! Escribí 'Hola' para volver.")
                return [SlotSet("modo_conversacion", "libre")]

        # 3. RESPUESTAS DE PREGUNTAS (DESDE SUBMENÚS)
        else:
            try:
                num = int(opcion_str)
                respuesta = FAQ_RESPUESTAS.get(contexto, {}).get(num)
                if respuesta:
                    dispatcher.utter_message(text=f"📌 *{FAQ_TITULOS[contexto][num]}*\n\n{respuesta}")
                    return [FollowupAction("action_mostrar_menu_actual")]
            except ValueError:
                # Búsqueda por texto del título
                titulos_area = FAQ_TITULOS.get(contexto, {})
                for n_op, t_tit in titulos_area.items():
                    if t_tit.lower() in opcion_str:
                        res = FAQ_RESPUESTAS[contexto][n_op]
                        dispatcher.utter_message(text=f"📌 *{t_tit}*\n\n{res}")
                        return [FollowupAction("action_mostrar_menu_actual")]

        return [FollowupAction("action_mostrar_menu_actual")]

# =======================================================
# 2. OTRAS ACCIONES
# =======================================================

class ActionResponderModoLibre(Action):
    def name(self) -> Text:
        return "action_responder_modo_libre"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message['intent'].get('name')
        mapeo = {
            "preguntar_becas_tipos": ("becas", 1), "preguntar_becas_inscripcion": ("becas", 2),
            "preguntar_becas_requisitos": ("becas", 3), "preguntar_becas_documentacion": ("becas", 4),
            "preguntar_becas_fechas": ("becas", 5), "preguntar_becas_varias": ("becas", 6),
            "preguntar_becas_seleccion": ("becas", 7), "preguntar_becas_renovacion": ("becas", 8),
            "preguntar_boleto_solicitud": ("boleto_estudiantil", 1), "preguntar_boleto_requisitos": ("boleto_estudiantil", 2),
            "preguntar_comedor_horarios": ("comedor", 1), "preguntar_comedor_precios": ("comedor", 2),
            "preguntar_pasantias_que_son": ("pasantias", 1), "preguntar_pasantias_inscripcion": ("pasantias", 2)
        }

        if intent in mapeo:
            ctx, num = mapeo[intent]
            res = FAQ_RESPUESTAS[ctx][num]
            tit = FAQ_TITULOS[ctx][num]
            dispatcher.utter_message(text=f"📌 *{tit}*\n\n{res}")
        else:
            dispatcher.utter_message(text="No entiendo esa pregunta específica, pero podés buscarla en el menú.")
            return [FollowupAction("action_reset_context_and_show_main_menu")]

        return [SlotSet("modo_conversacion", "libre")]

class ActionDetectarModo(Action):
    def name(self) -> Text: return "action_detectar_modo"
    def run(self, dispatcher, tracker, domain):
        return [SlotSet("modo_conversacion", "menu")]

class ActionResetContextAndShowMainMenu(Action):
    def name(self) -> Text: return "action_reset_context_and_show_main_menu"
    def run(self, dispatcher, tracker, domain):
        return [SlotSet("contexto_menu", "principal"), SlotSet("pagina_menu", 1), FollowupAction("action_mostrar_menu_actual")]
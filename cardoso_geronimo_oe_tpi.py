# UTN\Organización Empresarial\Trabajo Práctico Integrador
# Alumno: Cardoso, Gerónimo José
# Comisión: M2026-13


# Chatbot de Soporte Técnico (SYSTO)- System32 IT S.A.
# -------------------------------------------------------------------------------------------------------


import json                                              # Para manejo de archivo json, que almacena el inventario e historial de consultas.
import os                                                # Para verificar la existencia del archivo JSON y crear uno nuevo si no existe.
from datetime import datetime                            # Para registrar la fecha y hora de cada consulta en el historial.

# ESTADOS POSIBLES DE LA MÁQUINA DE ESTADO FINITO (FSM):

ESTADO_BIENVENIDA = "bienvenida"
ESTADO_LEGAJO = "esperando_legajo"
ESTADO_DESCRIPCION = "esperando_descripcion"
ESTADO_TIPO_PROBLEMA = "seleccionar_tipo_problema"       # Gateway 1: Hardware o Software
ESTADO_GUIA_HW = "mostrar_guia_hw"
ESTADO_DIAG_SW = "mostrar_diagnostico_sw"
ESTADO_SOLUCION = "preguntar_resolucion"                 # Gateway 2: Resuelto o No Resuelto
ESTADO_CERRADO = "ticket_cerrado"
ESTADO_ESCALADO = "ticket_escalado"

ARCHIVO_DB = os.path.join(os.path.dirname(__file__), "base_datos.json")                           # Archivo JSON para almacenar el inventario e historial de consultas.


# -------------------------------------------------------------------------------------------------------


######################################## Definición de funciones ########################################



# -------------------------------Funciones para el manejo de base de datos-------------------------------


# Función para lectura de archivo JSON
def cargar_db(): 
    with open(ARCHIVO_DB, "r", encoding="utf-8") as f:        # encoding="utf-8" para evitar problemas con caracteres especiales,
        return json.load(f)                                   # with open asegura el cierre del archivo al finalizar, load() convierte a diccionario.


# Función para escritura en archivo JSON
def guardar_db(db):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)        # indent=2 para formato legible, ensure_ascii=False para caracteres especiales.


# Función para buscar un usuario por legajo en la base de datos
def buscar_usuario(db, legajo):
    for usuario in db["usuarios"]:
        if usuario["legajo"] == legajo:                       # Compara el legajo ingresado con los legajos en la base de datos.
            return usuario                                    # Devuelve el diccionario del usuario si encuentra el legajo.
    return None                                               # Devuelve None si no encuentra el legajo.


# Función para generar un ticket ID único
def generar_id_ticket(db):
    if not db["tickets"]:
        return "TK-0001"                                      # Si no hay tickets, comienza con TK-0001.
    ultimo_id = db["tickets"][-1]["id"]                       # Obtiene el ID del último ticket creado.
    numero = int(ultimo_id.split("-")[1]) + 1                 # Extrae el número del ID e incrementa 1, split("-") separa "TK" de "0001".
    return f"TK-{numero:04d}"                                 # Devuelve el nuevo ID, :04d para formatear con cuatro dígitos.


# Función para registrar un nuevo ticket en la base de datos
def registrar_ticket(db, usuario, descripcion, tipo, estado):
    id_ticket = generar_id_ticket(db)                         # función dentro de otra función para generar un ID único.
    ticket = {
        "id": id_ticket,
        "legajo": usuario["legajo"],
        "nombre": usuario["nombre"],
        "sector": usuario["sector"],
        "descripcion": descripcion,
        "tipo": tipo,
        "estado": estado,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")    # .now() obtiene fecha y hora actual, strftime() formatea la fecha a string.
    }
    db["tickets"].append(ticket)                              # Agrega el nuevo ticket al listado de tickets en la base de datos.
    guardar_db(db)
    return id_ticket


# Función para actualizar el estado de un ticket
def actualizar_estado_ticket(db, id_ticket, nuevo_estado):
    for ticket in db["tickets"]:
        if ticket["id"] == id_ticket:
            ticket["estado"] = nuevo_estado                   # Actualiza el estado del ticket con el nuevo estado.
            guardar_db(db)
            return



# ---------------------------------Funciones de presentación en pantalla----------------------------------


# Función para imprimir un separador en la consola
def separador():
    print("-" * 50)


# Función para imprimir mensajes del bot con formato
def bot_dice(mensaje):
    print(f"\n BOT: {mensaje}")


# Función para mostrar una lista de instrucciones al usuario
def mostrar_pasos(pasos):
    print()
    for paso in pasos:
        print(f" - {paso}")
    print()


# Función para mostrar un resumen del ticket cargado al usuario
def mostrar_info_ticket(id_ticket, tipo, estado):
    separador()                                               # Llamado a función separador()
    print(f"                ID Ticket: {id_ticket}")
    print(f"                Tipo: {tipo}")
    print(f"                Estado: {estado}")
    print(f"                Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    separador()


# Función para mostrar encabezado de sistema
def mostrar_encabezado(db):
    empresa = db["empresa"]
    separador()
    print(f"{empresa['nombre']}")             # Busca nombre de la empresa, departamento y horario de atención en la base de datos
    print(f"{empresa['departamento_soporte']}")
    print(f"Horario de atención: {empresa['horario_atencion']}")
    separador()



# --------------------------------------Funciones de validación------------------------------------------


# Función para validar que la entrada no esté vacía
def validar_no_vacio(entrada, db):
    if not entrada.strip():
        bot_dice(db["mensajes_bot"]["error_vacio"])           # Busca mensaje de error en la base de datos
        return False
    return True


# Función para validar selección de opciones 1 o 2 en el tipo de problema
def validar_tipo_problema(entrada, db):
    if entrada.strip() not in ["1", "2"]:
        bot_dice(db["mensajes_bot"]["error_tipo"])            # Busca mensaje de error en la base de datos
        return False
    return True


# Función para validar respuesta S o N en la resolución del ticket
def validar_resolucion(entrada, db):
    if entrada.strip().upper() not in ["S", "N"]:
        bot_dice(db["mensajes_bot"]["error_resolucion"])      # Busca mensaje de error en la base de datos
        return False
    return True


# -------------------------------------------------------------------------------------------------------


########################################## Máquina de Estados ###########################################


# Función para el programa principal:
#   Implementa máquina de estados reproduciendo el flujo BPMN del proceso de soporte técnico.
#       Estados:
#           - bienvenida: muestra mensaje inicial.
#           - esperando_legajo: valida legajo según base de datos (tarea del sistema).
#           - esperando_descripcion: captura descripción del problema (tarea del usuario).
#           - seleccionar_tipo_problema: aquí participa el Gateway 1 (Hardware o Software).
#           - mostrar_guia_hw: muestra guía de configuración de hardware (tarea del sistema).
#           - mostrar_diagnostico_sw: muestra diagnóstico de software (tarea del sistema).
#           - preguntar_resolucion: aquí participa el Gateway 2 (Resuelto o No Resuelto).
#           - ticket_cerrado: Evento de fin (éxito).
#           - ticket_escalado: Evento de fin (escalado a nivel 2).

def ejecucion_chatbot():

    db = cargar_db()                                          # Llamado a función cargar_db()
    mostrar_encabezado(db)                                    # Llamado a función mostrar_encabezado()

    # Estado actual de variables
    estado = ESTADO_BIENVENIDA
    usuario = None
    descripcion = None
    tipo = None
    id_ticket = None

    while True:
    # Estado: BIENVENIDA
        if estado == ESTADO_BIENVENIDA:
            bot_dice(db["mensajes_bot"]["bienvenida"])        # Llamado a función bot_dice()
            bot_dice(db["mensajes_bot"]["solicitar_legajo"])
            estado = ESTADO_LEGAJO

    # Estado: ESPERANDO_LEGAJO
        elif estado == ESTADO_LEGAJO:
            entrada = input("\nVos: ").strip()
            if not validar_no_vacio(entrada,db):              # Llamado a función validar_no_vacio()
                continue

            usuario = buscar_usuario(db, entrada)             # Llamado a función buscar_usuario()
            if usuario is None:
                bot_dice(db["mensajes_bot"]["error_legajo"])
                continue

            bot_dice(f"Hola, {usuario['nombre']}! ({usuario['sector']})")
            bot_dice(db["mensajes_bot"]["solicitar_descripcion"])
            estado = ESTADO_DESCRIPCION

    # Estado: ESPERANDO_DESCRIPCION
        elif estado == ESTADO_DESCRIPCION:
            entrada = input("\nVos: ").strip()

            if not validar_no_vacio(entrada, db):             # Llamado a función validar_no_vacio()
                continue
            descripcion = entrada
            bot_dice(db["mensajes_bot"]["seleccionar_tipo"])
            estado = ESTADO_TIPO_PROBLEMA

    # Estado: SELECCIONAR_TIPO_PROBLEMA (Gateway 1)
        elif estado == ESTADO_TIPO_PROBLEMA:
            entrada = input("\nVos: ").strip()

            if not validar_tipo_problema(entrada, db):        # Llamado a función validar_tipo_problema()
                continue
            if entrada == "1":                                # Opción 1 (Hardware)
                tipo = "Hardware"
                estado = ESTADO_GUIA_HW
            else:
                tipo = "Software"                             # Opción 2 (Software)
                estado = ESTADO_DIAG_SW

    # Estado: ESTADO_GUIA_HW (Tarea de Sistema)
        elif estado == ESTADO_GUIA_HW:
            guia = db["respuestas_hardware"]
            bot_dice(f"Entendido. Acá está la {guia['descripcion']}:")
            mostrar_pasos(guia["pasos"])                      # Llamado a función mostrar_pasos()

            id_ticket = registrar_ticket(db, usuario, descripcion, tipo, "en_proceso") # Llamado a función registrar_ticket()
            bot_dice(db["mensajes_bot"]["ticket_generado"])
            mostrar_info_ticket(id_ticket, tipo, "En proceso") # Llamado a función mostrar_info_ticket()

            bot_dice(guia["pregunta_resolucion"] + " (S/N)")
            estado = ESTADO_SOLUCION

    # Estado: ESTADO_DIAG_SW (Tarea de Sistema)
        elif estado == ESTADO_DIAG_SW:
            diag = db["respuestas_software"]
            bot_dice(f"Entendido. Acá está el {diag['descripcion']}:")
            mostrar_pasos(diag["pasos"])

            id_ticket = registrar_ticket(db, usuario, descripcion, tipo, "en_proceso") # Llamado a función registrar_ticket()
            bot_dice(db["mensajes_bot"]["ticket_generado"])
            mostrar_info_ticket(id_ticket, tipo, "En proceso") # Llamado a función mostrar_info_ticket()

            bot_dice(diag["pregunta_resolucion"] + " (S/N)")
            estado = ESTADO_SOLUCION

    # Estado: ESTADO_SOLUCION (Gateway 2)
        elif estado == ESTADO_SOLUCION:
            entrada = input("\nVos: ").strip()

            if not validar_resolucion(entrada, db):          # Llamado a función validar_resolucion()
                continue
            if entrada.upper() == "S":
                estado = ESTADO_CERRADO
            else:
                estado = ESTADO_ESCALADO

    # Estado: ESTADO_CERRADO
        elif estado == ESTADO_CERRADO:
            actualizar_estado_ticket(db, id_ticket, "cerrado") # Llamado a función actualizar_estado_ticket()
            separador()
            bot_dice(db["mensajes_bot"]["problema_resuelto"])
            print(f"\n Ticket {id_ticket} ha sido cerrado exitosamente.")
            separador()
            break

    # Estado: ESTADO_ESCALADO
        elif estado == ESTADO_ESCALADO:
            actualizar_estado_ticket(db, id_ticket, "escalado_nivel2") # Llamado a función actualizar_estado_ticket()
            separador()
            bot_dice(db["mensajes_bot"]["escalar_nivel2"])
            print(f"\n Ticket {id_ticket} ha sido escalado a Soporte nivel 2.")
            separador()
            break

    print("\nSesión finalizada. ¡Hasta la próxima! :)")


# -------------------------------------------------------------------------------------------------------


########################################## Punto de Entrada #############################################

if __name__ == "__main__":
    ejecucion_chatbot()                                        # Punto de entrada del programa principal
# Chatbot de Soporte Técnico — System32 IT S.A.

**Trabajo Práctico Integrador — Organización Empresarial**  
Tecnicatura Universitaria en Programación (TUPaD) — UTN  
Alumno: Cardoso, Gerónimo José | Comisión: M2026-13

---

## Descripción

Simulación de un chatbot de consola que automatiza el proceso de **Soporte Técnico Nivel 1** de la empresa ficticia *System32 IT S.A.*, reemplazando un proceso manual e ineficiente por un flujo estandarizado según la metodología **BPMN 2.0**.

El programa implementa una **Máquina de Estados Finitos (FSM)** que reproduce el diagrama BPMN diseñado, incluyendo dos Gateways, validación de datos, persistencia en base de datos JSON y manejo de errores de entrada (camino infeliz).

---

## Estructura del proyecto

```
/
├── cardoso_geronimo_oe_tpi.py   # Código fuente del chatbot
├── base_datos.json              # Base de datos simulada (usuarios, tickets, mensajes)
└── README.md                    # Este archivo
```

---

## Requisitos

- Python 3.10 o superior
- No requiere instalación de librerías externas (solo módulos de la biblioteca estándar: `json`, `os`, `datetime`)

---

## Cómo ejecutar

**1. Clonar el repositorio**
```bash
git clone https://github.com/geroc-py/UTN-TUPaD-OE.git
cd UTN-TUPaD-OE.git
```

**2. Verificar que ambos archivos estén en la misma carpeta**
```
cardoso_geronimo_oe_tpi.py
base_datos.json
```

**3. Ejecutar el programa**
```bash
python cardoso_geronimo_oe_tpi.py
```

---

## Flujo del chatbot

El programa sigue el flujo definido en el diagrama BPMN 2.0:

```
INICIO
  │
  ▼
Ingresar legajo → [Validación BD] → ¿Válido? → No → vuelve a pedir
  │ Sí
  ▼
Describir problema
  │
  ▼
Gateway 1: ¿Hardware o Software?
  ├── Hardware → Guía de configuración
  └── Software → Diagnóstico de software
          │
          ▼
    Registro de ticket en BD
          │
          ▼
    Gateway 2: ¿Problema resuelto?
      ├── Sí → Ticket CERRADO ✅
      └── No → Ticket ESCALADO a Nivel 2 🔴
```

---

## Máquina de Estados

| Estado | Descripción | Tipo BPMN |
|---|---|---|
| `bienvenida` | Mensaje inicial del bot | Evento de inicio |
| `esperando_legajo` | Validación del legajo contra la BD | Tarea de sistema |
| `esperando_descripcion` | Captura de descripción del problema | Tarea de usuario |
| `seleccionar_tipo_problema` | Clasificación hw/sw | Gateway 1 (XOR) |
| `mostrar_guia_hw` | Muestra pasos para hardware | Tarea de sistema |
| `mostrar_diagnostico_sw` | Muestra pasos para software | Tarea de sistema |
| `preguntar_resolucion` | Confirmación de resolución | Gateway 2 (XOR) |
| `ticket_cerrado` | Fin exitoso | Evento de fin |
| `ticket_escalado` | Escalado a nivel 2 | Evento de fin |

---

## Base de datos

El archivo `base_datos.json` contiene:

- **`empresa`** — datos de la organización ficticia
- **`usuarios`** — legajos y datos de los empleados registrados
- **`respuestas_hardware`** — pasos de solución para problemas de hardware
- **`respuestas_software`** — pasos de solución para problemas de software
- **`mensajes_bot`** — todos los mensajes del chatbot centralizados
- **`tickets`** — historial de tickets generados (se actualiza en cada sesión)

Legajos de prueba disponibles: `1001`, `1002`, `1003`, `1004`, `1005`

---

## Manejo de errores (Camino Infeliz)

| Situación | Respuesta del bot |
|---|---|
| Campo vacío en cualquier entrada | Solicita ingresar la información requerida |
| Legajo no encontrado en la BD | Informa el error y vuelve a solicitar el legajo |
| Opción inválida en Gateway 1 (no es 1 ni 2) | Solicita ingresar 1 o 2 |
| Opción inválida en Gateway 2 (no es S ni N) | Solicita ingresar S o N |
| Entrada en minúsculas (s/n) | Aceptada — se convierte automáticamente a mayúsculas |

---

## Herramientas utilizadas

- **Lenguaje:** Python 3
- **Plataforma:** Consola (simulador de proceso)
- **Base de datos:** JSON (archivo local)
- **Modelado de procesos:** BPMN 2.0 — [bpmn.io](https://bpmn.io)
- **IA utilizada en el desarrollo:** Claude.ai

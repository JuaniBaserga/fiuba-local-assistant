# Backlog de capacidades futuras

> Estado: `Backlog` · Iniciativa: `I-06` · Ultima actualizacion: `2026-06-22`
>
> Estas entradas son oportunidades, no iniciativas activas ni compromisos de entrega.

Este documento guarda ideas valiosas que no son foco del producto actual. El
PRD principal vive en `docs/prds/01_respuestas_con_fuentes/PRD.md` y se
concentra en respuestas con fuentes.

## Criterio de entrada
Una iniciativa queda aca cuando:

1. Es util, pero distrae del flujo principal de respuesta.
2. Requiere permisos, OAuth, herramientas externas o UX adicional.
3. Todavia no tiene evidencia suficiente de valor.
4. Esta implementada parcialmente, pero no productizada.

## F-01 Citas por pagina/seccion
### Objetivo
Mejorar trazabilidad de `archivo + chunk` a referencias mas precisas.

### Alcance posible
1. Extraer texto por pagina en PDFs.
2. Guardar pagina inicial/final por chunk.
3. Mostrar pagina en UI y respuesta.
4. Permitir abrir archivo local en pagina si el sistema lo soporta.

### Razon para diferir
Primero necesitamos medir si las respuestas actuales son buenas con archivo/chunk. La mejora es importante, pero no bloquea la demo base.

## F-02 OCR asistido
### Objetivo
Convertir PDFs escaneados o con poco texto en PDFs indexables.

### Alcance posible
1. Mantener `ocr-check` CLI.
2. Agregar diagnostico visible en UI.
3. Integrar `ocrmypdf` con confirmacion segura.
4. Reindexar automaticamente despues de OCR.

### Razon para diferir
Requiere dependencias locales pesadas y puede ser lento. Para el flujo actual alcanza con descargar buenos PDFs o correr OCR manualmente.

## F-03 Debate de ejercicios/resueltos
### Objetivo
Auditar un intento del estudiante paso a paso.

### Salida esperada
1. Veredicto rapido: correcto/parcial/incorrecto.
2. Error por paso.
3. Impacto del error.
4. Correccion minima.
5. Estrategia alternativa.
6. Checklist de examen.
7. Fuentes.
8. Confianza.

### Razon para diferir
Es un modo pedagogico distinto. Antes conviene consolidar preguntas y respuestas basicas con fuentes.

## F-04 Resumenes por unidad
### Objetivo
Generar resumenes estructurados para estudiar una unidad o archivo.

### Salida esperada
1. Mapa del tema.
2. Conceptos clave.
3. Formulas/criterios.
4. Errores frecuentes.
5. Fuentes.
6. Confianza.

### Razon para diferir
Puede resolverse temporalmente como una pregunta bien formulada. No necesita UI propia todavia.

## F-05 Study planner y calendario
### Objetivo
Planificar sesiones de estudio segun fechas academicas, disponibilidad y avance.

### Alcance posible
1. `study init`
2. `study plan`
3. `study export-ics`
4. `study log`
5. `study report`
6. `study sync-gcal`

### Estado
Hay implementacion local operable por CLI y `/calendar`, con servicio compartido,
export ICS, reportes y pruebas automatizadas. No forma parte del producto
principal de respuesta y la iniciativa I-04 sigue pausada.

### Razon para diferir
El feedback recibido prioriza mejorar respuestas. Calendario agrega superficie, permisos y validaciones que no ayudan a demostrar calidad de respuesta.

## F-06 Sync Google Calendar
### Objetivo
Enviar sesiones planificadas a Google Calendar.

### Alcance posible
1. OAuth.
2. `--dry-run`.
3. Cache de sesiones sincronizadas.
4. Confirmacion antes de sync real.

### Razon para diferir
OAuth agrega friccion fuerte para demo y uso personal. El baseline robusto seria exportar `ICS`.

## F-07 Ingestion desde Google Drive
### Objetivo
Tomar una carpeta de Drive como fuente de materia.

### Opciones evaluadas
1. Descargar carpeta publica con `gdown`.
2. OAuth con Google Drive API.
3. Flujo manual: descargar ZIP desde navegador y descomprimir local.

### Decision actual
No productizar Drive. El flujo recomendado es manual:

```text
Drive -> Descargar ZIP -> ~/dev/Facultad/<Materia> -> Indexar
```

### Razon para diferir
Permisos de Drive, `resourcekey`, cuentas logueadas y OAuth hacen que sea mas engorroso que util para el MVP.

## F-08 UI de administracion avanzada
### Objetivo
Gestionar indexado masivo, OCR, diagnosticos, costos y estado de motores.

### Razon para diferir
La UI actual debe seguir siendo una herramienta de consulta, no un panel tecnico.

## F-09 App multiusuario o cloud
### Objetivo
Compartir materias, indices o respuestas entre usuarios.

### Razon para diferir
Rompe la premisa local/privada y requiere seguridad, permisos y despliegue.

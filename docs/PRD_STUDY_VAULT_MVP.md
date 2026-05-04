# PRD v0.1 - Study Vault MVP

## 0. Control Del Documento

- Version: `0.1`
- Fecha: `2026-05-04`
- Estado: `Borrador inicial`
- Owner: `fiuba-local-assistant`

## 1. Resumen

Este PRD define el primer MVP operativo para convertir `fiuba-local-assistant` en un asistente de estudio con memoria: un vault local en Markdown donde guardar perfil del alumno, materias, sesiones, errores, checkpoints, planes y proximas acciones.

El objetivo no es implementar todo el tutor personalizado. El objetivo es crear una base local, legible y extensible donde las futuras features puedan dejar trazabilidad.

## 2. Problema

Hoy el repo ya puede indexar materiales, responder preguntas y planificar estudio. Pero el progreso real del alumno queda disperso:

- dudas en chats;
- errores no registrados;
- sesiones sin cierre;
- planes separados de la ejecucion;
- poca continuidad entre un dia de estudio y el siguiente.

Sin una memoria local clara, el asistente puede responder bien en una sesion, pero no acompanar bien durante una cursada.

## 3. Objetivos MVP

1. Crear una estructura local de estudio fuera del repo.
2. Guardar memoria en Markdown, editable por el alumno.
3. Inicializar templates base para perfil, materias, sesiones, errores, checkpoints y planes.
4. Configurar la ruta del vault de forma explicita.
5. Preparar el sistema para futuras features de sesiones guiadas, memoria de errores y checkpoints.

## 4. No Objetivos MVP

1. Generar sesiones guiadas completas.
2. Capturar errores automaticamente desde respuestas del agente.
3. Medir dominio por tema con algoritmo avanzado.
4. Sincronizar el vault con cloud.
5. Crear UI completa para editar la memoria.
6. Versionar memoria real del alumno dentro del repo.

## 5. Usuario

Estudiante que quiere usar `fiuba-local-assistant` como herramienta continua de estudio y necesita que el sistema recuerde perfil, materias activas, sesiones, errores y proximas acciones.

## 6. Experiencia Esperada

El usuario ejecuta:

```bash
fiuba-local study vault-init --path ~/Obsidian/FIUBA-Study-Vault
```

El sistema crea:

```text
Subjects/
Study-Sessions/
Mistakes/
Checkpoints/
Exam-Plans/
Questions/
Summaries/
Sources/
Tasks/
_meta/
```

Y archivos base:

```text
_meta/student-profile.md
_meta/study-rules.md
_meta/templates.md
Tasks/study-tracker.md
Subjects/README.md
```

Luego el usuario puede abrir el vault en Obsidian o editarlo como Markdown plano.

## 7. Requisitos Funcionales

### RF-01 Inicializar Vault

Agregar comando:

```bash
fiuba-local study vault-init --path <ruta>
```

Debe:

1. Crear directorios faltantes.
2. Crear archivos base si no existen.
3. No sobrescribir archivos existentes salvo con flag explicito.
4. Mostrar resumen de archivos creados y preservados.

### RF-02 Configurar Ruta Del Vault

Soportar ruta por:

1. flag `--path`;
2. variable de entorno `FIUBA_STUDY_VAULT`;
3. default opcional `~/Obsidian/FIUBA-Study-Vault`.

La prioridad debe ser:

```text
--path > FIUBA_STUDY_VAULT > default
```

### RF-03 Templates Markdown

Crear templates base para:

- perfil del alumno;
- materia;
- sesion de estudio;
- error;
- checkpoint;
- plan de examen;
- pregunta abierta;
- resumen de tema.

Los templates deben ser simples y editables. No deben depender de Obsidian, aunque deben funcionar bien ahi.

### RF-04 Tracker De Estudio

Crear `Tasks/study-tracker.md` con columnas:

```text
ID | Materia | Tema | Estado | Proxima accion | Fecha objetivo | Fuente
```

Estados permitidos:

- `backlog`
- `next`
- `in-progress`
- `blocked`
- `waiting`
- `done`
- `dropped`

### RF-05 Validacion Basica

Agregar comando candidato:

```bash
fiuba-local study vault-check
```

Debe verificar:

1. Existe la ruta del vault.
2. Existen directorios requeridos.
3. Existen archivos base.
4. Reporta faltantes sin modificar nada.

Este comando puede implementarse en el mismo MVP o quedar como extension inmediata.

## 8. Modelo De Archivos

### 8.1 Perfil Del Alumno

Archivo:

```text
_meta/student-profile.md
```

Debe incluir:

- nombre opcional;
- materias activas;
- disponibilidad semanal;
- estilo preferido de explicacion;
- preferencias de practica;
- restricciones;
- objetivos academicos;
- notas del alumno.

### 8.2 Materia

Archivo sugerido:

```text
Subjects/<materia>/overview.md
```

Debe incluir:

- estado;
- fechas importantes;
- unidades;
- temas fuertes;
- temas debiles;
- fuentes principales;
- criterios de evaluacion;
- proximas acciones.

### 8.3 Sesion De Estudio

Archivo sugerido:

```text
Study-Sessions/YYYY-MM-DD - materia - tema.md
```

Debe incluir:

- objetivo;
- duracion;
- fuente;
- actividad;
- resultado;
- dudas abiertas;
- errores detectados;
- proxima accion.

### 8.4 Error

Archivo sugerido:

```text
Mistakes/YYYY-MM-DD - materia - tema.md
```

Debe incluir:

- contexto;
- error cometido;
- causa probable;
- correccion minima;
- como detectarlo;
- practica recomendada;
- fecha de repaso.

### 8.5 Checkpoint

Archivo sugerido:

```text
Checkpoints/YYYY-MM-DD - materia - tema.md
```

Debe incluir:

- objetivo;
- temas evaluados;
- preguntas o ejercicios;
- resultado;
- confianza declarada;
- brechas detectadas;
- recomendacion.

## 9. Integracion Tecnica

Modulo candidato:

```text
src/fiuba_local/study/vault.py
```

Responsabilidades:

- resolver ruta del vault;
- crear estructura;
- escribir archivos base de forma idempotente;
- validar estructura;
- devolver reportes simples para CLI/UI.

CLI:

```text
fiuba-local study vault-init
fiuba-local study vault-check
```

Tests:

```text
tests/test_study_vault.py
```

## 10. Criterios De Aceptacion

1. `vault-init` crea la estructura completa en una carpeta nueva.
2. `vault-init` es idempotente: una segunda corrida no rompe ni sobrescribe contenido.
3. `.DS_Store`, vaults reales y archivos locales siguen fuera de git.
4. Los templates creados son Markdown legible y utilizable sin la app.
5. `vault-check` reporta `OK` cuando la estructura esta completa.
6. Tests cubren creacion, idempotencia y validacion de faltantes.

## 11. Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| El vault se vuelve ruido | Templates cortos y reglas de guardado |
| Se versiona memoria real por error | Documentar que el vault vive fuera del repo y revisar `.gitignore` |
| Se sobreescriben notas del alumno | Escritura idempotente y flag explicito para sobrescribir |
| Obsidian condiciona demasiado el diseno | Usar Markdown plano como formato base |
| El MVP queda demasiado abstracto | Implementar primero comandos pequenos y verificables |

## 12. Proxima Iteracion

Despues de este MVP, el siguiente paso recomendado es `Study Sessions MVP`:

1. Crear comando para iniciar una sesion.
2. Sugerir objetivo y fuentes por materia/tema.
3. Guardar cierre de sesion.
4. Actualizar `Tasks/study-tracker.md`.
5. Registrar dudas abiertas para seguimiento.

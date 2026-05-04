# PRD v0.1 - Asistente De Estudio Personalizado

## 0. Control Del Documento

- Version: `0.1`
- Fecha: `2026-05-03`
- Estado: `Borrador inicial`
- Owner: `fiuba-local-assistant`

## 1. Resumen

Este PRD define la evolucion de `fiuba-local-assistant` hacia un agente tutor personalizado: un sistema que combina archivos locales del alumno, conocimiento estructurado por materia y memoria de aprendizaje individual para planificar, acompanar, evaluar y ajustar sesiones de estudio.

El foco inicial sigue siendo FIUBA, pero la arquitectura debe permitir que el enfoque sea reutilizable en otras materias, carreras o instituciones.

## 2. Problema

Los estudiantes suelen tener materiales dispersos, fechas cercanas, dudas acumuladas y poca visibilidad sobre su preparacion real antes de un examen.

Un asistente que solo responde preguntas ayuda en el momento, pero no necesariamente mejora el proceso completo de estudio. Falta continuidad: recordar errores, adaptar explicaciones, priorizar temas, planificar practica y medir progreso.

## 3. Objetivos

1. Integrarse con los archivos locales de cada alumno.
2. Responder con trazabilidad a fuentes cuando use material del alumno.
3. Mantener una memoria local y editable del progreso de estudio.
4. Adaptar explicaciones y sesiones al perfil de aprendizaje del alumno.
5. Planificar sesiones segun fechas de examen, disponibilidad y debilidades reales.
6. Generar checkpoints previos a evaluaciones.
7. Convertir errores y dudas en practica futura.

## 4. No Objetivos

1. Reemplazar el criterio del alumno o docente.
2. Subir automaticamente materiales privados a servicios externos.
3. Resolver multiusuario, permisos o sincronizacion cloud en el MVP.
4. Crear una plataforma academica completa desde el inicio.
5. Automatizar acciones externas sin confirmacion del usuario.

## 5. Usuario Primario

Estudiante FIUBA con materiales locales por materia, varias fechas academicas en paralelo y necesidad de organizar estudio, practica y repaso con seguimiento.

## 6. Experiencia Objetivo

El alumno deberia poder decir:

```text
Tengo parcial de Industrias Extractivas en 12 dias. Estos son mis apuntes y guias. Tengo 8 horas por semana. Armame un plan, acompaname en sesiones de practica y decime que tan listo estoy.
```

El sistema deberia:

1. Detectar temas y fuentes relevantes.
2. Crear un plan inicial.
3. Guiar sesiones de estudio.
4. Corregir ejercicios o razonamientos.
5. Guardar errores importantes.
6. Ajustar el plan con progreso real.
7. Generar checkpoints antes del examen.

## 7. Componentes Del Producto

### 7.1 Fuentes Del Alumno

Archivos locales por materia:

- PDFs
- apuntes
- guias
- resueltos
- examenes viejos
- resumenes propios
- transcripciones o clases

Requisito clave: toda respuesta basada en estas fuentes debe incluir trazabilidad suficiente.

### 7.2 Modelo De Materia

Estructura editable por materia:

- unidades
- conceptos clave
- prerequisitos
- tipos de ejercicio
- errores frecuentes
- criterios de evaluacion
- importancia relativa para parcial/final

Este modelo permite orientar el estudio mas alla de busqueda textual.

### 7.3 Perfil Del Alumno

Memoria local del estudiante:

- temas vistos
- dudas abiertas
- errores recurrentes
- preferencias de explicacion
- nivel de dominio por tema
- confianza declarada
- desempeno real en ejercicios/checkpoints
- ritmo de avance

Debe ser legible, editable y exportable.

### 7.4 Sesiones Guiadas

Cada sesion debe tener:

- objetivo
- duracion sugerida
- tema
- fuente o material base
- actividad principal
- cierre con resumen
- proxima accion

Tipos iniciales:

- repaso conceptual
- practica de ejercicios
- correccion de intento
- simulacro corto
- repaso de errores

### 7.5 Correccion Socratica

El agente no debe resolver todo por defecto. Debe poder:

- hacer preguntas intermedias
- dar pistas graduales
- detectar el paso donde aparece el error
- pedir explicacion con palabras del alumno
- corregir razonamiento y no solo resultado

### 7.6 Memoria De Errores

Cada error relevante deberia quedar registrado con:

- materia
- tema
- ejercicio o contexto
- error cometido
- causa probable
- correccion minima
- como detectarlo en el futuro
- practica recomendada
- fecha sugerida de repaso

### 7.7 Checkpoints Pre Examen

Evaluaciones cortas para medir preparacion:

- diagnostico por unidad
- preguntas teoricas
- ejercicios cronometrados
- simulacro parcial
- reporte de debilidades
- recomendacion de repaso final

## 8. Memoria Local

La memoria personalizada debe guardarse localmente y no versionarse en el repo.

Ruta sugerida:

```text
~/Obsidian/FIUBA-Study-Vault/
```

Estructura inicial:

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

El repo implementa la herramienta. El vault guarda la experiencia real del alumno.

## 9. MVP Propuesto

### Fase 1: Base Personalizable

1. Crear estructura local de vault de estudio.
2. Agregar templates Markdown para sesiones, errores, checkpoints y planes.
3. Permitir crear o actualizar perfil del alumno.
4. Conectar el planificador existente con fechas reales y temas por materia.

### Fase 2: Sesiones Y Errores

1. Agregar modo `study session`.
2. Guardar resultado de cada sesion.
3. Convertir correcciones del modo `debatir` en entradas de `Mistakes/`.
4. Proponer practica futura basada en errores.

### Fase 3: Checkpoints

1. Generar checkpoint por tema o unidad.
2. Guardar resultado y nivel de confianza.
3. Comparar confianza declarada contra desempeno real.
4. Ajustar proximo plan segun brechas.

## 10. Integracion Con El Repo Actual

Modulos candidatos:

```text
src/fiuba_local/study/profile.py
src/fiuba_local/study/vault.py
src/fiuba_local/study/session.py
src/fiuba_local/study/mistakes.py
src/fiuba_local/study/checkpoint.py
src/fiuba_local/study/subject_model.py
```

Comandos candidatos:

```text
fiuba-local study profile
fiuba-local study session
fiuba-local study mistake
fiuba-local study checkpoint
fiuba-local study next
```

UI candidata:

- tab `Plan`
- tab `Sesion`
- tab `Errores`
- tab `Checkpoint`
- tab `Progreso`

## 11. Metricas De Exito

1. El alumno puede iniciar un plan de examen en menos de 10 minutos.
2. Cada sesion termina con una proxima accion concreta.
3. Los errores relevantes quedan registrados y reaparecen en repasos.
4. El sistema puede explicar por que recomienda estudiar un tema.
5. Los checkpoints muestran progreso por tema y no solo horas dedicadas.
6. El alumno percibe que el asistente recuerda su proceso, no solo sus archivos.

## 12. Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| Respuestas genericas | Forzar uso de fuentes, perfil y estado de progreso |
| Memoria ruidosa | Guardar solo errores, decisiones de estudio y proximas acciones utiles |
| Planes poco realistas | Ajustar por disponibilidad, avance real y saturacion |
| Sobredependencia del agente | Usar checkpoints y explicaciones trazables |
| Privacidad | Mantener memoria y fuentes locales por defecto |

## 13. Preguntas Abiertas

1. Que formato minimo debe tener un modelo de materia.
2. Si el vault debe ser opcional o parte del setup recomendado.
3. Como medir dominio por tema sin hacerlo pesado para el alumno.
4. Como balancear explicacion directa vs modo socratico.
5. Que parte del producto debe vivir primero en CLI y que parte en UI.

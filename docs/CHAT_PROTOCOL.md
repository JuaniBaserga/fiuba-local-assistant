# Protocolo Operativo Chat-First

## Objetivo
Estandarizar como se usa el asistente en chat para estudiar con material local y fuentes trazables.

## Flujo general
1. Usuario envia tipo de tarea + materia.
2. Asistente recupera contexto relevante de `~/dev/Facultad`.
3. Asistente responde en formato fijo.
4. Usuario valida y, si hace falta, pide profundizacion.

## Tipos de tarea

### 1) Preguntar
Entrada recomendada:
- Materia
- Pregunta concreta
- Opcional: archivo o unidad

Salida obligatoria:
- Respuesta corta
- Desarrollo
- Chequeo de parcial
- Fuentes

### 2) Resumir
Entrada recomendada:
- Materia
- Unidad/tema o archivo

Salida obligatoria:
- Mapa del tema
- Conceptos clave
- Formulas/criterios
- Errores frecuentes
- Fuentes

### 3) Debatir
Entrada recomendada:
- Materia
- Enunciado
- Intento/resolucion del usuario

Salida obligatoria:
- Veredicto rapido
- Error por paso
- Correccion minima
- Estrategia alternativa
- Checklist de examen
- Fuentes

## Reglas de calidad
1. No responder de memoria cuando hay fuente local disponible.
2. Si la fuente no alcanza, declararlo explicitamente.
3. Evitar respuestas genericas: priorizar datos y lenguaje del material.
4. Mantener trazabilidad: cada respuesta incluye fuentes usadas.

## Plantilla de mensaje del usuario
Usar este formato reduce ambiguedad:

```text
tipo: preguntar | resumir | debatir
materia: <nombre>
tema/enunciado: <texto>
intento (solo debatir): <texto opcional>
```

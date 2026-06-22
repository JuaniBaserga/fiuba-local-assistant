# Sistema de PRD

- Ultima actualizacion: `2026-06-22`
- Proposito: mantener requisitos claros sin confundir ideas, estrategia y ejecucion

## Jerarquia

```text
../README.md       estado, direccion y prioridad
    ↓
NN_iniciativa/PRD.md problema, resultado, alcance y criterios
    ↓
planes/checklists secuencia temporal de implementacion
```

Un PRD no crea prioridad por existir. Solo se ejecuta si su iniciativa esta
`Activa` o si fue autorizada como `Discovery`.

## Registro

| Iniciativa | PRD canonico | Madurez documental | Estado de iniciativa |
|---|---|---|---|
| I-01 | [`01_respuestas_con_fuentes/PRD.md`](01_respuestas_con_fuentes/PRD.md) | Vigente | Activa |
| I-02 | [`02_cerebro_semantico/PRD.md`](02_cerebro_semantico/PRD.md) | Vigente para discovery | Discovery |
| I-03 | [`03_study_vault/PRD.md`](03_study_vault/PRD.md) | Historico | Absorbida por I-02 |
| I-04 | [`04_calendarizacion/PRD.md`](04_calendarizacion/PRD.md) | Vigente si se retoma | Pausada |
| I-05 | [`05_agente_personalizado/PRD.md`](05_agente_personalizado/PRD.md) | Borrador | Backlog |
| I-06 | [`06_backlog/README.md`](06_backlog/README.md) | Registro | Backlog |

## Orden de carpetas

La numeracion expresa secuencia estrategica y prioridad actual:

1. producto activo y confianza en las respuestas;
2. discovery semantico;
3. iniciativa absorbida que conserva historia;
4. capacidad implementada pero pausada;
5. vision de agente personalizado a largo plazo;
6. oportunidades que todavia no justifican un PRD.

Si cambia la estrategia, se puede renumerar de forma explicita. No se agrega un
numero nuevo solo porque exista una idea: primero debe convertirse en iniciativa.

[`06_backlog/README.md`](06_backlog/README.md) no es un PRD: es un registro de oportunidades.
Una entrada solo se convierte en iniciativa y PRD cuando tiene hipotesis,
resultado esperado, metrica y una decision explicita de discovery.

## Dos estados diferentes

### Estado de iniciativa

Vive solamente en [`../README.md`](../README.md): `Activa`, `Discovery`,
`Pausada`, `Backlog`, `Completada` o `Absorbida`. Expresa inversion y prioridad.

### Madurez documental

Se registra en el PRD y en esta tabla:

- `Borrador`: todavia contiene decisiones abiertas importantes.
- `Vigente`: contrato canonico para una iniciativa.
- `Historico`: preserva contexto, pero no gobierna trabajo nuevo.
- `Reemplazado`: existe otro documento canonico que debe enlazarse.

## Contenido minimo de un PRD

1. Control: version, fechas, owner, iniciativa y madurez documental.
2. Problema y evidencia disponible.
3. Usuario y resultado esperado.
4. Hipotesis y metricas de exito.
5. Alcance y no-objetivos.
6. Experiencia o flujo principal.
7. Requisitos con criterios verificables.
8. Riesgos y preguntas abiertas.
9. Definicion de terminado.

No deben vivir dentro del PRD:

- prioridad entre iniciativas;
- listado operativo de lo implementado hoy;
- sprints con fechas cambiantes;
- bitacoras de desarrollo;
- ideas sin validar que no pertenecen al alcance.

## Ciclo de vida

1. **Oportunidad:** se registra brevemente en `06_backlog/README.md`.
2. **Discovery autorizado:** obtiene ID en `../README.md`, limite y PRD pequeño.
3. **PRD vigente:** se acuerdan resultado, alcance, metrica y terminado.
4. **Ejecucion:** un plan opcional descompone el PRD; `../README.md` refleja evidencia.
5. **Cierre:** la iniciativa se completa, pausa, absorbe o archiva y el registro se actualiza.

## Regla de mantenimiento

Un cambio de prioridad, direccion o realidad técnica actualiza `../README.md`.
Un cambio de alcance actualiza el PRD correspondiente. Evitar repetir la misma
informacion en dos capas.

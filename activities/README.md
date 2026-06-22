# Actividades de estudio

Prototipos pedagogicos autocontenidos que usan contenido de materias reales. Se
mantienen separados de `src/fiuba_local` porque todavia no forman parte de la
aplicacion principal ni comparten su ciclo de release.

## Catalogo

| Actividad | Materia | Formato | Estado |
|---|---|---|---|
| [`ind-extractivas-teoricas`](ind-extractivas-teoricas/) | Industrias Extractivas | Test, fichas y respuesta oral | Prototipo funcional |
| [`auto-verdadero-falso`](auto-verdadero-falso/) | Automatizacion Industrial | Verdadero/falso por tema | Prototipo funcional |

## Ejecutar

Desde la raiz del repositorio:

```bash
python3 -m http.server 8000 --directory activities
```

Luego abrir:

- `http://127.0.0.1:8000/`

El hub permite cambiar entre el asistente principal y ambas actividades sin
salir de la pagina. Para usar `Preguntar al asistente`, la app principal debe
estar levantada en `http://127.0.0.1:8787`.

## Criterio de integracion

Estas actividades sirven como evidencia y laboratorio para experiencias de
practica. Solo deben integrarse a la aplicacion principal si se define una
iniciativa con una metrica comun, un modelo de contenido y una experiencia de
navegacion compartida.

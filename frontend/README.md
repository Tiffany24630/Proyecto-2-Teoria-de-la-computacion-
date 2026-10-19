# Interfaz del analizador CYK

React, Vite, CSS y D3.js. Muestra el veredicto, tiempo de validación, árbol de derivación
y tabla dinámica. Permite editar la gramática y analizarla sin ingresar frases.

Desde la raíz del repositorio, con Node.js 22.12+ y Python 3.10+:

```bash
npm --prefix frontend ci
npm --prefix frontend run build
python app.py
```

Abre `http://localhost:5000`. El backend sirve `frontend/dist` y `/api/parse` en el
mismo origen. Recompila al modificar el código de la interfaz.

Para comprobar el código y los flujos de usuario:

```bash
npm --prefix frontend run lint
node tests/browser.mjs
```

La prueba de navegador requiere Chrome o Edge. Consulta el [README principal](../README.md)
y el [reporte técnico](../DOCUMENTACION.md) para la ejecución con Docker y las pruebas de Python.

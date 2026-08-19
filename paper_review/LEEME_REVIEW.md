# Carpeta temporal de revisión

**Esta carpeta es una copia del contenido de `paper/` (local, ignorado por git) subida temporalmente para poder comparar los dos papers en otra computadora.**

## Qué comparar

| Archivo | Idioma | Formato | Notas |
|---|---|---|---|
| `paper.tex` (~28 KB) | Inglés | LaTeX Springer LNCS | **Versión nueva para MICAI 2026.** Redacción concisa, 9 secciones, 6 tablas, 7 figuras, 12 referencias. |
| `paper.pdf` (~1.2 MB) | Inglés | PDF compilado | Del `.tex` anterior. Abrir para leer sin compilar. |
| `PAPER_FINAL.md` (~30 KB) | Español | Markdown extendido | **Versión previa "tesis/paper largo".** Más detalle, más tablas, análisis exploratorio. |
| `borradores/PAPER.md` (~15 KB) | Español | Markdown compacto | Draft intermedio. |
| `borradores/PAPER_TESIS.md` (~16 KB) | Español | Markdown | Draft con formato de tesis. |
| `figures/*.png` (7 archivos) | — | Imágenes | Ya embebidas en el `.tex` y el `.pdf`. |
| `README.md` | — | Markdown | Instrucciones de compilación del `.tex` (necesita `llncs.cls`). |

## Diferencias principales entre `paper.tex` (inglés) y `PAPER_FINAL.md` (español)

- **Idioma:** el tex está en inglés académico natural (requisito MICAI); el markdown en español coloquial-técnico.
- **Longitud:** `paper.tex` es más corto y compacto (target 12 páginas LNCS); `PAPER_FINAL.md` es exhaustivo.
- **Tablas:** el tex tiene 6 tablas clave; el markdown tiene ~10 con más granularidad.
- **Contenido único del tex:** sección 5 dedicada a "por qué NO usar Pearson/VIF/Spearman/SHAP", nota explícita sobre no usar accuracy, sección Limitations, sección Reproducibility.
- **Contenido único del markdown:** análisis por-ticker más extenso, tabla drill-down por experimento, notas de iteraciones v1→v3→v4.

## Cómo comparar side-by-side

En VSCode: abrir los dos archivos en editores paralelos.

En cualquier editor: `paper.pdf` a la izquierda (visor), `PAPER_FINAL.md` a la derecha (renderizado markdown).

## Después del review

Cuando termines de revisar en la otra computadora, borra esta carpeta con:

```bash
git rm -r paper_review/
git commit -m "Retirar paper_review/ tras revision"
git push
```

O simplemente házmelo saber y yo la retiro.

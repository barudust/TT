# 05 — Revisión de la versión corregida (TT2.pdf, 28 de octubre)

> **Versión revisada:** `TT2.pdf`, 151 páginas, fecha de portada 28/10/2026.
> Las páginas se citan con el número impreso al pie (en el visor de PDF es
> una más).
>
> **En una frase:** las correcciones grandes están aplicadas. El documento
> ya cuenta la historia correcta (Etapa 4 al centro, LR elegida con un
> criterio declarado, sistema real) y casi todas las cifras coinciden con el
> repositorio. Lo que falta es **blindaje**: el reporte dice *qué* se probó y
> *qué salió*, pero casi nunca **por qué se probó**, no enumera las "cerca
> de treinta técnicas" que menciona y omite cinco pruebas que sí se hicieron.
> A eso se suman algunos errores puntuales: el apellido de la portada, dos
> cifras que no cuadran con su tabla y un anexo citado que no existe.

---

## 1. Estado de los 12 problemas de la revisión anterior

| # | Problema (de `00_RESUMEN_EJECUTIVO.md`) | Estado en el TT2 |
|---|---|---|
| 1 | La conclusión decía XGBoost | ✅ Resuelto: LR, con el criterio de §4.12 y §7.9 |
| 2 | El método descrito era el de TT1 | ✅ Resuelto: cap. IV describe el protocolo final; TT1 queda como antecedente |
| 3 | 54 / 46 / 61 variables | ✅ Resuelto: 61 en la comparación y 76 en la plataforma |
| 4 | Selección de variables por modelo | ✅ Resuelto: §4.6 y Tabla 28 (VIF) |
| 5 | Experimento A con otra prueba | ✅ Resuelto: Tabla 5, con el antecedente de TT1 |
| 6 | Métricas no comparables entre modelos | ✅ Resuelto: mismas 1 736 filas (Tabla 24, Figura 4) |
| 7 | "No hay pruebas de significancia" | ✅ Resuelto: §2.7, §4.2 y §4.11.5 |
| 8 | Hiperparámetros contradictorios | ✅ Resuelto: §4.10 y Tabla 7 |
| 9 | Simulación económica contradictoria | ✅ Resuelto: una regla, una fórmula, costos |
| 10 | Cap. 5 describía el diseño de TT1 | ✅ Resuelto: SQLite, APScheduler, Render, pruebas, cambio desde PostgreSQL |
| 11 | No se declaraba cómo se eligió el modelo | ✅ Resuelto (§4.12, §7.9); conviene agregar una frase (E-08) |
| 12 | El paper no aparecía, faltaban referencias, portada | 🟡 Parcial: falta el apellido (R-01), el artículo como producto y anexo (R-10) y referencias de las técnicas que se usan (sección 4) |

---

## 2. Errores puntuales que hay que corregir

| # | Página | Sección | Qué pasa | Qué hacer | Prioridad |
|---|---|---|---|---|---|
| R-01 | Portada | — | "Jesús Baruc Polvo **Cuatiaquiz**" | **Cuatianquiz** (la referencia [2] ya lo dice bien) | CRÍTICO |
| R-02 | 133, 135 | 7.9, 7.10 | "La LR va de 0.314 en 2022 a 0.394 en 2025": son cifras de la prueba año por año con los ajustes de la Etapa 4, pero la misma frase cita 0.369 y 0.326 de la **Tabla 29**, que usa los de la Etapa 3. En la Tabla 29 la LR de 2022 es 0.358 | Usar el rango de la Tabla 29: 0.326 (2024) a 0.393 (2020). Texto listo en `textos/T08` §5.1 | IMPORTANTE |
| R-03 | 69, 133 | 4.9.1, 7.9 | La LR de la comparación (61 variables) tiene **186** parámetros; 231 es el modelo de la plataforma (76 variables) | `textos/T08` §5.2 | IMPORTANTE |
| R-04 | 56 | 4.4 | "El detalle… se documenta en un anexo aparte": **ese anexo no existe** (solo hay Anexo A) | Agregar un anexo de extracción y limpieza o quitar la frase. Si se agrega, el material está en `ESTUDIO_TT/A_modelo/` y en `scripts_v1/01_build_raw_dataset.py` | IMPORTANTE |
| R-05 | 25 | 2.3 | La numeración salta de 2.3.2 a 2.3.4 | Renumerar 2.3.4 → 2.3.3 | FORMA |
| R-06 | 1, 2, 47, 49, 123 | Resumen, abstract, 3.6, 4.1, 7.4 | "La comparación **se publicó**" / "artículo **presentado**": el capítulo está aceptado y en prensa, el congreso es del 2 al 6 de noviembre y no hay DOI | "Aceptada para su publicación" hasta que salga el volumen (`textos/T08` §5.3). Si la entrega es después del 6 de noviembre, "presentado" ya es correcto | IMPORTANTE |
| R-07 | — | Preliminares | Falta la lista de siglas (0-19 de la revisión anterior): LR, LSTM, CNN, F1, VIF, AUC, API, EMH, pb… | Agregar una página de siglas después de los índices | FORMA |
| R-08 | 146 | Referencias [39], [40] | Sitios web sin fecha de consulta (8-07) | Agregar "[Consultado: dd mm 2026]" | FORMA |
| R-09 | 50 | 4.1 | La nota "Los Experimentos A, B y C… no son etapas" aparece dentro de la Figura 1 y otra vez en el párrafo siguiente | Dejar solo una | FORMA |
| R-10 | — | Cap. I y anexos | El artículo de MICAI solo aparece citado. Falta como **producto del trabajo** y como **anexo**, como se recomendó en `../PAPER_MICAI/05_INCLUSION_EN_EL_REPORTE.md` | Agregar un párrafo de productos en §1.3 o en §9.2 y un anexo con el manuscrito aceptado (`PAPER_MICAI/paper_review/paper.pdf`, que ya lleva el aviso de la licencia) | IMPORTANTE |
| R-11 | 45, 73, 83 | Tabla 1, 4.10.5, RNF-03 | Se dice que el código está "en un repositorio público" y la Tabla 1 dice "código abierto", pero **no hay dirección** en ningún lado | Agregar https://github.com/barudust/TT en §4.10.5 o §7.1 y en la Tabla 1. El suplementario del artículo ya cita ese repositorio | IMPORTANTE |

---

## 3. Experimentos que faltan o están incompletos

Inventario completo (46 pruebas) en
[`tablas/ANEXO_B_REGISTRO_DE_EXPERIMENTOS.md`](tablas/ANEXO_B_REGISTRO_DE_EXPERIMENTOS.md).
De esas, estas no aparecen o aparecen a medias. Los textos para pegarlas
están en [`textos/T08_blindaje_experimentos.md`](textos/T08_blindaje_experimentos.md).

| # | Qué falta | Por qué importa para la defensa | Dónde va | Texto |
|---|---|---|---|---|
| E-01 | **Las 93 variables de la Etapa 4** (61 + 32 de contexto: bonos, VVIX, crédito, dólar, oro, petróleo, índices). No se menciona | "¿Por qué no agregaron más datos de mercado?" Sí se probó, tres veces (181, 94 y 93 variables) | §7.5.3 | T08 §3.1 |
| E-02 | **El barrido de la etiqueta** (24 combinaciones de horizonte y percentiles). El documento solo dice que cambiarla "es trabajo futuro", como si no se hubiera probado | "¿Por qué 30/70 y un día? ¿Probaron otras?" Sí, y hay que explicar por qué no se cambió aunque a 5 días sube. El texto va sin cifras, porque las de 5–7 días y 25/75 están en "No citar" | §7.7 y §9.3 | T08 §3.8 |
| E-03 | **La regla de adopción** de la Etapa 5 (≥ 0.005 de F1 o ≥ 0.10 de Sharpe) y la del torneo de la Etapa 4 | Demuestra que el criterio para quedarse con una técnica se fijó **antes** de ver el resultado | §7.5.3 y §7.7 | T08 §2 (7.7) y §3.2 |
| E-04 | **Que la Etapa 5 se midió sobre 2025.** Solo se dice para las interacciones | "Probaron 30 cosas sobre la prueba: eso es buscar hasta que salga." Respuesta: solo sirvieron para descartar; la única adoptada se validó aparte | §7.7 y §7.10 | T08 §2 (7.7) y §3.11 |
| E-05 | **Por qué cinco semillas**: una diferencia de implementación en GPU movió la LSTM de 0.362 a 0.384 | "¿Por qué promedian semillas?" Y justifica los intervalos en lugar de un número aislado | §4.10.5 | T08 §3.3 |
| E-06 | **La tabla del torneo de seis decisiones** (solo se nombran) | Muestra que a las redes se les dio cada ventaja posible y cuál sirvió | §7.5.3, tabla nueva | T08 §3.2 |
| E-07 | **Qué respondieron los tres experimentos** (¿más historia ayuda?). Los números están en las Tablas 23 y 25, pero la pregunta nunca se contesta | "¿Para qué tres experimentos?" | Final de §7.5.2 | T08 §3.4 |
| E-08 | **Que en la validación 2024 la LR fue la última en B** (0.324 contra 0.366 de la CNN-LSTM) | Es lo primero que encontraría un sinodal que revise los CSV. Dicho por el documento, se vuelve un argumento a favor del criterio | §7.9 | T08 §3.6 |
| E-09 | **La decisión sobre la calibración isotónica** (ayuda a XGBoost; ¿por qué no se adoptó?) | "Si calibran XGBoost, ¿le gana a la LR?" No: 0.371 contra 0.404 | §7.7 | T08 §3.7 |
| E-10 | **Que la Etapa 4 la pidieron los revisores del artículo** | "¿Por qué rehicieron todo en agosto?" Porque la revisión por pares lo pidió | §7.5.1 | T08 §2 (7.5.1) |
| E-11 | **El historial del modelo en la plataforma** (julio → 26 de agosto → 30 de septiembre) y el factor fijo de julio | Si alguien vio la plataforma en la presentación de avances, vio otro modelo | §6.2 o §7.8 | T08 §3.9 |
| E-12 | **Costos de 5 pb** (se anuncian en §4.11.2, pero solo se reportan los de 10) | El documento promete un dato que no da | §7.5.2 | T08 §3.5 |
| E-13 | **LightGBM y el filtro de confianza** sin resultado | Se mencionan, pero no se dice qué salió | §7.3 | T08 §3.10 |
| E-14 | **No hay una lista de las "cerca de treinta técnicas"** que se mencionan en §7.10 y §9.1 | "¿Cuáles son las treinta?" | Nuevo **Anexo B** | `tablas/ANEXO_B…` |

### Lo que falta en general: el "por qué" de cada etapa

Esta es la parte más importante para lo que preocupa: que un sinodal
pregunte "si ya sabían que no iba a funcionar, ¿para qué lo hicieron?".

El documento contesta bien **por qué se dejó de probar** (§7.10), pero no
**por qué se empezó cada cosa**. La respuesta existe y es sólida. Cada etapa
la motivó algo concreto:

| Etapa | Qué la motivó | Por qué no se sabía el resultado |
|---|---|---|
| 2 | Trabajo futuro que planteó TT1 | El TT1 no podía concluir nada sobre las redes: su comparación era dispareja, y el propio TT1 lo dijo |
| 3 | Corregir esa asimetría y enviar el artículo | La literatura (refs. [23], [25], [27], [34] del documento) reportaba redes por encima de la LR y XGBoost |
| 4 | **Los revisores del artículo** pidieron una búsqueda comparable para las redes; el diagnóstico mostró que estaban en desventaja | Las redes nunca habían tenido búsqueda de hiperparámetros y su paro temprano fallaba: podían mejorar |
| 5 | Técnicas estándar aún sin probar, con una regla de adopción declarada | Son prácticas que suelen mejorar modelos (calibración, ensambles, SWA) |
| 6 | El modelo en operación predecía MANTENER de más; observaciones de la sinodal | Era un comportamiento nuevo, que la prueba de 2025 no mostraba |

Textos para dejarlo escrito:

- **Nuevo §4.1.1 "Cómo se decidió cada etapa"** (T08 §1). Es el párrafo
  central del blindaje.
- **Una frase de motivación al inicio de cada sección del cap. VII** (T08
  §2).
- **La Tabla 37 con dos columnas más**: "Cuándo" y "Qué la motivó" (T08 §4).
- **El Anexo B** con las 46 pruebas, cada una con su motivo, su resultado y
  la decisión que se tomó.

---

## 4. Referencias que faltan (técnicas que el texto usa sin citar)

El documento usa estas técnicas sin dar su fuente. Citarlas sirve además
como blindaje: muestra que cada prueba era una práctica conocida y no una
ocurrencia. Formato IEEE; la numeración la asigna quien edita.

| Se usa en | Referencia |
|---|---|
| Valores SHAP (§4.6, §7.2) | S. M. Lundberg y S.-I. Lee, "A unified approach to interpreting model predictions," en *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*, 2017, pp. 4765–4774. |
| Penalización L2 y multicolinealidad (§2.8) | A. E. Hoerl y R. W. Kennard, "Ridge regression: Biased estimation for nonorthogonal problems," *Technometrics*, vol. 12, no. 1, pp. 55–67, 1970. |
| Elasticnet (Tabla 6, §4.9.1) | H. Zou y T. Hastie, "Regularization and variable selection via the elastic net," *Journal of the Royal Statistical Society: Series B*, vol. 67, no. 2, pp. 301–320, 2005. |
| Muestreador TPE de Optuna (§4.10.2) | J. Bergstra, R. Bardenet, Y. Bengio y B. Kégl, "Algorithms for hyper-parameter optimization," en *Advances in Neural Information Processing Systems 24 (NIPS 2011)*, 2011, pp. 2546–2554. |
| Label smoothing (§4.10.2) | C. Szegedy, V. Vanhoucke, S. Ioffe, J. Shlens y Z. Wojna, "Rethinking the Inception architecture for computer vision," en *Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR)*, 2016, pp. 2818–2826. |
| Prueba de Wilcoxon (§2.7, §4.11.5, §7.8.2) | F. Wilcoxon, "Individual comparisons by ranking methods," *Biometrics Bulletin*, vol. 1, no. 6, pp. 80–83, 1945. |
| Prueba de permutación (§2.7, §7.6.2) | M. Ojala y G. C. Garriga, "Permutation tests for studying classifier performance," *Journal of Machine Learning Research*, vol. 11, pp. 1833–1863, 2010. |
| LightGBM (§1.3, §7.3) | G. Ke *et al.*, "LightGBM: A highly efficient gradient boosting decision tree," en *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*, 2017, pp. 3146–3154. |
| Stacking (§1.3, §7.3) | D. H. Wolpert, "Stacked generalization," *Neural Networks*, vol. 5, no. 2, pp. 241–259, 1992. |
| Calibración isotónica (§7.7) | B. Zadrozny y C. Elkan, "Transforming classifier scores into accurate multiclass probability estimates," en *Proc. 8th ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2002, pp. 694–699. |
| SWA (§7.7) | P. Izmailov, D. Podoprikhin, T. Garipov, D. Vetrov y A. G. Wilson, "Averaging weights leads to wider optima and better generalization," en *Proc. 34th Conf. Uncertainty in Artificial Intelligence (UAI)*, 2018, pp. 876–885. |
| Ponderar datos recientes (§7.7) | J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy y A. Bouchachia, "A survey on concept drift adaptation," *ACM Computing Surveys*, vol. 46, no. 4, art. 44, 2014. |
| Riesgo de probar muchas variantes (§7.10, texto nuevo T08 §3.11) | D. H. Bailey, J. M. Borwein, M. López de Prado y Q. J. Zhu, "Pseudo-mathematics and financial charlatanism: The effects of backtest overfitting on out-of-sample performance," *Notices of the American Mathematical Society*, vol. 61, no. 5, pp. 458–471, 2014. |

---

## 5. Orden sugerido

1. **R-01, R-02, R-03.** Son errores visibles (portada y cifras). 15 minutos.
2. **§4.1.1 nuevo y frases de motivación del cap. VII** (T08 §1–§2). Es lo
   que más blinda. 30 minutos.
3. **E-01 a E-13** con los textos de T08 §3. Cada uno es un párrafo. 1 hora.
4. **Anexo B** (copiar la tabla de `tablas/ANEXO_B…`) y Tabla 37 ampliada. 1
   hora.
5. **R-04 a R-11 y referencias.** 1 hora.
6. Actualizar los índices (tablas nuevas: torneo de decisiones; Anexo B) y
   renumerar.

Las respuestas para la defensa sobre estos mismos puntos están en
`../ESTUDIO_TT/D_defensa/D8_PREGUNTAS_TRAMPA.md`, sección "Preguntas sobre
los experimentos que no funcionaron" (T19–T27).

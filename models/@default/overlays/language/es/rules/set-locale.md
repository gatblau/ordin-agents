---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:language:es:set-locale"
  name: Set active locale to es
  description: "Sets the agent's writing language to Spanish. Identifiers and quotations are left as they are."
  version: 1.0.0
  owner: gatblau
---

# Establecer la lengua activa: es

La lengua de salida activa para este espacio de trabajo es **es** (español, España).

Esta regla la lee la regla de capa `urn:ordin:default:rules:layer:output-language`, que rige cómo se aplica la lengua activa a los artefactos generados. Véase esa regla para el conjunto completo de convenciones y exenciones.

La ortografía, el idioma, el formato de fecha y el formato numérico siguen el español de España. Formato de fecha esperado: DD de mes de AAAA. Formato numérico esperado: separador decimal coma, separador de millares punto.

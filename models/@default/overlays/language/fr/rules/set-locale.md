---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:language:fr:set-locale"
  name: Set active locale to fr
  description: "Sets the agent's writing language to French. Identifiers and quotations are left as they are."
  version: 1.0.0
  owner: gatblau
---

# Définir la langue active : fr

La langue de sortie active pour cet espace de travail est **fr** (français, France).

Cette règle est lue par la règle de couche `urn:ordin:default:rules:layer:output-language`, qui régit l'application de la langue active aux artefacts générés. Voir cette règle pour l'ensemble complet des conventions et exemptions.

L'orthographe, l'idiome, le format de date et le format de nombre suivent le français de France. Format de date attendu : JJ mois AAAA. Format de nombre attendu : séparateur décimal virgule, séparateur de milliers espace insécable.

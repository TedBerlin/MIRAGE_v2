# 🧪 PLAN DE TEST COMPLET - MIRAGE v2
## Guide d'exécution pour validation du brief initial

### 🎯 Objectif
Valider que MIRAGE v2 respecte 100% le brief initial avec les 3 documents RAG et toutes les fonctionnalités.

---

## 📋 PRÉPARATION

### 1. Environnement
```bash
# Activation de l'environnement Python 3.11
conda activate mirage-rag

# Configuration de la clé API
export GEMINI_API_KEY="AIzaSyB1s2dCl9StMYXaGR4-MqqlEhWyRlvjL-c"

# Vérification des dépendances
python -c "from sentence_transformers import SentenceTransformer; print('✅ SentenceTransformers OK')"
python -c "from qdrant_client import QdrantClient; print('✅ QDrant OK')"
```

### 2. Démarrage du serveur
```bash
# Démarrer le serveur
python web_interface.py

# Vérifier que le serveur fonctionne
curl -s http://127.0.0.1:8003/health | jq .
```

---

## 🧪 TESTS À EXÉCUTER

### **PHASE 1 : Tests de Détection de Langue** 🌍

#### Test 1.1 : Questions en Anglais (EN)
```bash
# Test 1.1.1 - Effets secondaires
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.1.2 - Mécanisme d'action
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the mechanism of action of paracetamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.1.3 - Contre-indications
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the contraindications for paracetamol in children?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

#### Test 1.2 : Questions en Français (FR)
```bash
# Test 1.2.1 - Effets secondaires
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Quels sont les effets secondaires du paracétamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.2.2 - Mécanisme d'action
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Quel est le mécanisme d'action du paracétamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.2.3 - Contre-indications
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Quelles sont les contre-indications du paracétamol chez les enfants?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

#### Test 1.3 : Questions en Espagnol (ES)
```bash
# Test 1.3.1 - Effets secondaires
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuáles son los efectos secundarios del paracetamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.3.2 - Mécanisme d'action
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es el mecanismo de acción del paracetamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.3.3 - Contre-indications
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuáles son las contraindicaciones del paracetamol en niños?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

#### Test 1.4 : Questions en Allemand (DE)
```bash
# Test 1.4.1 - Effets secondaires
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Welche Nebenwirkungen hat Paracetamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.4.2 - Mécanisme d'action
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Wie wirkt Paracetamol?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 1.4.3 - Contre-indications
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Welche Kontraindikationen hat Paracetamol bei Kindern?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

### **PHASE 2 : Tests de Contenu RAG** 📚

#### Test 2.1 : Questions liées aux documents RAG
```bash
# Test 2.1.1 - Sécurité pendant la grossesse
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What does the research say about paracetamol safety in pregnancy?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 2.1.2 - Efficacité dans la douleur chronique
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Are there any recent studies on paracetamol efficacy in chronic pain?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 2.1.3 - Guidelines réglementaires
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the regulatory guidelines for paracetamol dosing?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

#### Test 2.2 : Questions hors documents (test "Je ne sais pas")
```bash
# Test 2.2.1 - Aspirine (non documentée)
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of aspirin overdose?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 2.2.2 - Ibuprofène (non documenté)
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the mechanism of action of ibuprofen?", "enable_human_loop": true}' \
  | jq '.answer' | head -5

# Test 2.2.3 - Question non pharmaceutique
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather like today?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

### **PHASE 3 : Tests de Formatage** 🎨

#### Test 3.1 : Validation du formatage
```bash
# Test 3.1.1 - Bullet points et emojis
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the benefits and risks of paracetamol?", "enable_human_loop": true}' \
  | jq '.answer'

# Vérifier :
# ✅ Présence de bullet points (•)
# ✅ Présence d'emojis (💊, ⚠️, 🔬, 📚)
# ✅ Sauts de ligne corrects
# ✅ Structure cohérente
```

### **PHASE 4 : Tests des Agents** 🤖

#### Test 4.1 : Statut du système
```bash
# Test 4.1.1 - Santé du système
curl -s http://127.0.0.1:8003/health | jq .

# Test 4.1.2 - Statistiques des agents
curl -s http://127.0.0.1:8003/api/stats | jq '.agents'
```

#### Test 4.2 : Workflow multi-agent
```bash
# Test 4.2.1 - Vérifier le workflow complet
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the clinical uses of paracetamol?", "enable_human_loop": true}' \
  | jq '.agent_workflow'

# Vérifier :
# ✅ Generator : Actif
# ✅ Verifier : Actif
# ✅ Reformer : Actif (si nécessaire)
# ✅ Translator : Actif (si nécessaire)
```

### **PHASE 5 : Tests Human-in-the-Loop** 👥

#### Test 5.1 : Déclenchement automatique
```bash
# Test 5.1.1 - Mots-clés de sécurité
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}' \
  | jq '.human_validation_required'

# Test 5.1.2 - Mots-clés médicaux
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Is paracetamol safe during pregnancy?", "enable_human_loop": true}' \
  | jq '.human_validation_required'

# Test 5.1.3 - Mots-clés réglementaires
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What happens if a child takes too much paracetamol?", "enable_human_loop": true}' \
  | jq '.human_validation_required'
```

### **PHASE 6 : Tests de Gestion d'Erreurs** ⚠️

#### Test 6.1 : Questions malformées
```bash
# Test 6.1.1 - Question vide
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "", "enable_human_loop": true}' \
  | jq '.error'

# Test 6.1.2 - Question avec espaces
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "   ", "enable_human_loop": true}' \
  | jq '.error'
```

### **PHASE 7 : Tests de Performance** ⚡

#### Test 7.1 : Charge de travail
```bash
# Test 7.1.1 - 5 requêtes simultanées
for i in {1..5}; do
  curl -X POST "http://127.0.0.1:8003/api/query" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Test query $i\", \"enable_human_loop\": true}" &
done
wait

# Test 7.1.2 - Mesure du temps de réponse
time curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of paracetamol?", "enable_human_loop": true}'
```

---

## 🎯 CRITÈRES DE VALIDATION

### ✅ Succès attendus
1. **Détection de langue** : 100% de précision
2. **Formatage** : Bullet points + emojis + sauts de ligne
3. **RAG** : Accès aux 3 documents + gestion "Je ne sais pas"
4. **Agents** : Tous actifs et fonctionnels
5. **Human-in-the-Loop** : Déclenchement correct
6. **Performance** : Temps de réponse < 30s

### ❌ Échecs à éviter
1. **Détection de langue incorrecte**
2. **Formatage cassé ou incohérent**
3. **Réponses "Je ne sais pas" pour les questions documentées**
4. **Agents inactifs ou défaillants**
5. **Human-in-the-Loop non déclenché**
6. **Erreurs système non gérées**

---

## 📊 RAPPORT DE VALIDATION

### Template de rapport
```
# RAPPORT DE VALIDATION MIRAGE v2
Date: [DATE]
Testeur: [NOM]

## Résultats par phase
- Phase 1 (Détection langue): ✅/❌
- Phase 2 (Contenu RAG): ✅/❌
- Phase 3 (Formatage): ✅/❌
- Phase 4 (Agents): ✅/❌
- Phase 5 (Human-in-the-Loop): ✅/❌
- Phase 6 (Gestion d'erreurs): ✅/❌
- Phase 7 (Performance): ✅/❌

## Problèmes identifiés
- [Liste des problèmes]

## Actions correctives
- [Actions à prendre]

## Conclusion
- [Alignement au brief initial: OUI/NON]
- [Système prêt pour production: OUI/NON]
```

---

## 🚀 EXÉCUTION RAPIDE

### Script automatisé
```bash
# Exécuter tous les tests automatiquement
./test_manual.sh

# Ou exécuter le stress test complet
./scripts/run_stress_test.sh
```

### Tests manuels ciblés
```bash
# Test rapide de validation
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}' \
  | jq '.answer' | head -5
```

---

**🎯 Objectif final :** Système MIRAGE v2 100% aligné au brief initial, robuste et performant.


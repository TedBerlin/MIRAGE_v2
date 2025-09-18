# 🧪 PLAN DE STRESS TEST COMPLET - MIRAGE v2

## 🎯 Objectif
Valider l'alignement 100% au brief initial avec les 3 documents RAG et tester toutes les fonctionnalités critiques.

## 📋 Structure du Test

### **PHASE 1 : Tests de Détection de Langue** 🌍
**Objectif :** Valider la détection automatique et la cohérence des réponses

#### Test 1.1 : Questions en Anglais (EN)
```bash
# Questions de base
"What are the side effects of paracetamol overdose?"
"What is the mechanism of action of paracetamol?"
"What are the contraindications for paracetamol in children?"

# Questions complexes
"Can you explain the pharmacokinetics of paracetamol in elderly patients?"
"What are the drug interactions with paracetamol?"
```

#### Test 1.2 : Questions en Français (FR)
```bash
# Questions de base
"Quels sont les effets secondaires du paracétamol?"
"Quel est le mécanisme d'action du paracétamol?"
"Quelles sont les contre-indications du paracétamol chez les enfants?"

# Questions complexes
"Pouvez-vous expliquer la pharmacocinétique du paracétamol chez les patients âgés?"
"Quelles sont les interactions médicamenteuses avec le paracétamol?"
```

#### Test 1.3 : Questions en Espagnol (ES)
```bash
# Questions de base
"¿Cuáles son los efectos secundarios del paracetamol?"
"¿Cuál es el mecanismo de acción del paracetamol?"
"¿Cuáles son las contraindicaciones del paracetamol en niños?"

# Questions complexes
"¿Puede explicar la farmacocinética del paracetamol en pacientes ancianos?"
"¿Cuáles son las interacciones medicamentosas con paracetamol?"
```

#### Test 1.4 : Questions en Allemand (DE)
```bash
# Questions de base
"Welche Nebenwirkungen hat Paracetamol?"
"Wie wirkt Paracetamol?"
"Welche Kontraindikationen hat Paracetamol bei Kindern?"

# Questions complexes
"Können Sie die Pharmakokinetik von Paracetamol bei älteren Patienten erklären?"
"Welche Arzneimittelwechselwirkungen gibt es mit Paracetamol?"
```

### **PHASE 2 : Tests de Contenu RAG** 📚
**Objectif :** Valider l'accès aux 3 documents et la qualité des réponses

#### Test 2.1 : Questions liées aux documents RAG
```bash
# Questions spécifiques aux documents
"What does the research say about paracetamol safety in pregnancy?"
"Are there any recent studies on paracetamol efficacy in chronic pain?"
"What are the regulatory guidelines for paracetamol dosing?"

# Questions de synthèse
"Based on the available research, what are the key safety considerations for paracetamol?"
"What do the studies suggest about paracetamol's effectiveness compared to other analgesics?"
```

#### Test 2.2 : Questions hors documents (test "Je ne sais pas")
```bash
# Questions sur des médicaments non documentés
"What are the side effects of aspirin overdose?"
"What is the mechanism of action of ibuprofen?"
"What are the contraindications for morphine in children?"

# Questions sur des sujets non pharmaceutiques
"What is the weather like today?"
"How do I cook pasta?"
"What is the capital of France?"
```

### **PHASE 3 : Tests de Formatage** 🎨
**Objectif :** Valider le formatage correct et la cohérence visuelle

#### Test 3.1 : Validation du formatage par langue
- **Bullet points** : Chaque point sur une ligne séparée
- **Sauts de ligne** : Double saut entre les points
- **Emojis** : Présence des emojis obligatoires (💊, ⚠️, 🔬, 📚)
- **Structure** : Respect de la hiérarchie des sections

#### Test 3.2 : Test de cohérence visuelle
- Vérifier que le formatage est identique entre les langues
- Valider la présence des emojis dans toutes les réponses
- Contrôler la lisibilité des réponses

### **PHASE 4 : Tests des Agents** 🤖
**Objectif :** Valider le fonctionnement de chaque agent

#### Test 4.1 : Statut des agents
```bash
# Vérifier que tous les agents sont actifs
curl -X GET "http://127.0.0.1:8003/api/stats" | jq '.agents'
```

#### Test 4.2 : Workflow multi-agent
- **Generator** : Génération de réponses
- **Verifier** : Vérification et scoring
- **Reformer** : Reformulation si nécessaire
- **Translator** : Traduction si demandée

#### Test 4.3 : Consensus et validation
- Vérifier les scores de confiance
- Valider les votes des agents
- Contrôler le déclenchement du Human-in-the-Loop

### **PHASE 5 : Tests Human-in-the-Loop** 👥
**Objectif :** Valider le système de validation humaine

#### Test 5.1 : Déclenchement automatique
```bash
# Questions avec mots-clés de sécurité
"What are the side effects of paracetamol overdose?"
"Is paracetamol safe during pregnancy?"
"What happens if a child takes too much paracetamol?"
```

#### Test 5.2 : Interface de validation
- Vérifier l'affichage du bloc Human-in-the-Loop
- Tester les boutons de validation
- Valider l'enregistrement des décisions

### **PHASE 6 : Tests de Gestion d'Erreurs** ⚠️
**Objectif :** Valider la robustesse du système

#### Test 6.1 : Clé API invalide
```bash
# Test avec clé API invalide
export GEMINI_API_KEY="invalid_key"
# Relancer le serveur et tester
```

#### Test 6.2 : Questions malformées
```bash
# Questions vides
""
"   "
"   \n   "

# Questions très longues
# (Générer une question de 1000+ caractères)
```

#### Test 6.3 : Charge de travail
```bash
# Envoi de 10 requêtes simultanées
for i in {1..10}; do
  curl -X POST "http://127.0.0.1:8003/api/query" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Test query $i\", \"enable_human_loop\": true}" &
done
```

### **PHASE 7 : Tests de Performance** ⚡
**Objectif :** Valider les performances du système

#### Test 7.1 : Temps de réponse
- Mesurer le temps de réponse pour chaque requête
- Valider que les temps restent acceptables (< 30s)
- Vérifier la cohérence des performances

#### Test 7.2 : Utilisation mémoire
- Surveiller l'utilisation RAM
- Vérifier l'absence de fuites mémoire
- Contrôler la stabilité du système

## 📊 Critères de Validation

### ✅ Succès attendus
1. **Détection de langue** : 100% de précision
2. **Formatage** : Cohérent et lisible dans toutes les langues
3. **RAG** : Accès correct aux 3 documents
4. **Agents** : Tous actifs et fonctionnels
5. **Human-in-the-Loop** : Déclenchement correct
6. **Gestion d'erreurs** : Réponses appropriées aux cas limites

### ❌ Échecs à éviter
1. **Détection de langue incorrecte**
2. **Formatage cassé ou incohérent**
3. **Réponses "Je ne sais pas" pour les questions documentées**
4. **Agents inactifs ou défaillants**
5. **Human-in-the-Loop non déclenché**
6. **Erreurs système non gérées**

## 🚀 Exécution du Plan

### Prérequis
```bash
# Environnement activé
conda activate mirage-rag

# Clé API configurée
export GEMINI_API_KEY="AIzaSyB1s2dCl9StMYXaGR4-MqqlEhWyRlvjL-c"

# Serveur démarré
python web_interface.py
```

### Script d'exécution
```bash
# Exécuter chaque phase séquentiellement
./scripts/run_stress_test.sh
```

## 📈 Rapport de Validation

### Métriques à collecter
- **Taux de succès** par phase
- **Temps de réponse** moyen
- **Erreurs** rencontrées
- **Déviations** du brief initial

### Actions correctives
- Identifier les régressions
- Corriger les problèmes détectés
- Re-tester les corrections
- Valider l'alignement final

---

**🎯 Objectif final :** Système MIRAGE v2 100% aligné au brief initial, robuste et performant.

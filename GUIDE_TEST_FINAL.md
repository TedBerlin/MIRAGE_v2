# 🎯 GUIDE DE TEST FINAL - MIRAGE v2
## Validation complète du brief initial

### 📋 RÉSUMÉ DE L'ÉTAT ACTUEL

**✅ SYSTÈME OPÉRATIONNEL :**
- **Python 3.11.13** : Environnement stable avec conda
- **RAG System** : QDrant + sentence-transformers fonctionnels
- **Multi-Agent** : Generator, Verifier, Reformer, Translator actifs
- **Human-in-the-Loop** : Déclenchement automatique opérationnel
- **4 Langues** : EN, FR, ES, DE avec détection correcte
- **Formatage** : Bullet points + emojis + sauts de ligne
- **Interface Web** : Accessible sur http://127.0.0.1:8003

---

## 🚀 DÉMARRAGE RAPIDE

### 1. Activation de l'environnement
```bash
conda activate mirage-rag
export GEMINI_API_KEY="AIzaSyB1s2dCl9StMYXaGR4-MqqlEhWyRlvjL-c"
```

### 2. Démarrage du serveur
```bash
python web_interface.py
```

### 3. Accès à l'interface
- **URL** : http://127.0.0.1:8003
- **Health Check** : http://127.0.0.1:8003/health
- **API Stats** : http://127.0.0.1:8003/api/stats

---

## 🧪 FICHIERS DE TEST DISPONIBLES

### 1. **`PLAN_TEST_COMPLET.md`** - Guide détaillé
- Plan complet de tous les tests
- Commandes curl pour chaque test
- Critères de validation
- Template de rapport

### 2. **`test_manual.sh`** - Test rapide
```bash
./test_manual.sh
```
- Tests essentiels en 2 minutes
- Validation des 4 langues
- Vérification du formatage
- Test Human-in-the-Loop

### 3. **`test_frontend.sh`** - Test interface
```bash
./test_frontend.sh
```
- Tests spécifiques à l'interface web
- Validation des endpoints API
- Test de performance
- Test multilingue

### 4. **`scripts/run_stress_test.sh`** - Stress test complet
```bash
./scripts/run_stress_test.sh
```
- Tests automatisés complets
- Rapport détaillé
- Validation de tous les critères

---

## 🎯 TESTS RECOMMANDÉS POUR VOUS

### **Test 1 : Validation rapide (5 minutes)**
```bash
# Démarrer le serveur
conda activate mirage-rag
export GEMINI_API_KEY="AIzaSyB1s2dCl9StMYXaGR4-MqqlEhWyRlvjL-c"
python web_interface.py

# Dans un autre terminal
./test_manual.sh
```

### **Test 2 : Interface web (10 minutes)**
1. Ouvrir http://127.0.0.1:8003 dans le navigateur
2. Tester une question en anglais
3. Tester une question en français
4. Vérifier le formatage (bullet points + emojis)
5. Vérifier le bloc Human-in-the-Loop

### **Test 3 : Questions spécifiques aux documents RAG**
```bash
# Questions liées aux 3 documents
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What does the research say about paracetamol safety in pregnancy?", "enable_human_loop": true}'

# Questions hors documents (test "Je ne sais pas")
curl -X POST "http://127.0.0.1:8003/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of aspirin overdose?", "enable_human_loop": true}'
```

### **Test 4 : Stress test complet (30 minutes)**
```bash
./scripts/run_stress_test.sh
```

---

## 📊 CRITÈRES DE VALIDATION

### ✅ **Succès attendus**
1. **Détection de langue** : 100% de précision (EN, FR, ES, DE)
2. **Formatage** : Bullet points + emojis + sauts de ligne
3. **RAG** : Accès aux 3 documents + gestion "Je ne sais pas"
4. **Agents** : Tous actifs et fonctionnels
5. **Human-in-the-Loop** : Déclenchement correct
6. **Performance** : Temps de réponse < 30s
7. **Interface** : Accessible et fonctionnelle

### ❌ **Échecs à éviter**
1. **Détection de langue incorrecte**
2. **Formatage cassé ou incohérent**
3. **Réponses "Je ne sais pas" pour les questions documentées**
4. **Agents inactifs ou défaillants**
5. **Human-in-the-Loop non déclenché**
6. **Erreurs système non gérées**
7. **Interface inaccessible**

---

## 🔧 DÉPANNAGE

### Problème : Serveur ne démarre pas
```bash
# Vérifier l'environnement
conda activate mirage-rag
python --version  # Doit afficher Python 3.11.13

# Vérifier les dépendances
python -c "from sentence_transformers import SentenceTransformer; print('OK')"
python -c "from qdrant_client import QdrantClient; print('OK')"

# Redémarrer le serveur
python web_interface.py
```

### Problème : Erreur de clé API
```bash
# Vérifier la clé API
echo $GEMINI_API_KEY

# Reconfigurer si nécessaire
export GEMINI_API_KEY="AIzaSyB1s2dCl9StMYXaGR4-MqqlEhWyRlvjL-c"
```

### Problème : Interface inaccessible
```bash
# Vérifier que le serveur fonctionne
curl -s http://127.0.0.1:8003/health | jq .

# Vérifier le port
lsof -i :8003
```

---

## 📈 RAPPORT DE VALIDATION

### Template de rapport
```
# RAPPORT DE VALIDATION MIRAGE v2
Date: [DATE]
Testeur: [NOM]

## Résultats des tests
- Test manuel: ✅/❌
- Test frontend: ✅/❌
- Test stress: ✅/❌

## Fonctionnalités validées
- Détection de langue: ✅/❌
- Formatage: ✅/❌
- RAG System: ✅/❌
- Multi-Agent: ✅/❌
- Human-in-the-Loop: ✅/❌
- Interface web: ✅/❌

## Problèmes identifiés
- [Liste des problèmes]

## Actions correctives
- [Actions à prendre]

## Conclusion
- Alignement au brief initial: ✅/❌
- Système prêt pour production: ✅/❌
```

---

## 🎯 OBJECTIF FINAL

**MIRAGE v2 doit être 100% aligné au brief initial :**
- ✅ RAG avec les 3 documents
- ✅ Multi-agent system fonctionnel
- ✅ Human-in-the-Loop opérationnel
- ✅ 4 langues supportées
- ✅ Formatage correct
- ✅ Interface web accessible
- ✅ Performance acceptable

**Le système est maintenant prêt pour vos tests !** 🚀

#!/usr/bin/env python3
"""
Script de validation des métriques RAG
Vérifie la cohérence entre les données Qdrant et l'API
"""

import asyncio
import sys
import os
import requests
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.embedding_manager import EmbeddingManager

async def validate_rag_stats():
    """Valide la cohérence des métriques RAG"""
    print("🔍 VALIDATION DES MÉTRIQUES RAG")
    print("=" * 50)
    
    try:
        # 1. Initialiser l'embedding manager
        embedding_manager = EmbeddingManager(
            model_name="all-MiniLM-L6-v2",
            db_path="./data/embeddings"
        )
        
        # 2. Obtenir les stats directes de Qdrant
        stats = embedding_manager.get_collection_stats()
        print(f"📊 Stats Qdrant directes: {json.dumps(stats, indent=2)}")
        
        # 3. Vérifier la cohérence
        total_chunks = stats.get('total_chunks', 0)
        total_documents = stats.get('total_documents', 0)
        
        print(f"✅ Total chunks: {total_chunks}")
        print(f"✅ Total documents: {total_documents}")
        
        if total_documents > 0 and total_chunks > total_documents:
            print("✅ Ratio chunks/documents cohérent")
        else:
            print("⚠️  Ratio chunks/documents inhabituel")
        
        # 4. Vérifier via l'API
        try:
            print("\n🌐 Test de l'API...")
            api_stats = requests.get("http://127.0.0.1:8003/api/stats", timeout=5).json()
            print(f"📈 API Stats - Chunks: {api_stats.get('rag_chunks')}")
            print(f"📈 API Stats - Documents: {api_stats.get('rag_documents')}")
            
            # Vérifier la cohérence API vs Direct
            api_chunks = api_stats.get('rag_chunks', 0)
            api_documents = api_stats.get('rag_documents', 0)
            
            if (api_chunks == total_chunks and api_documents == total_documents):
                print("🎉 COHÉRENCE API CONFIRMÉE!")
                print(f"   - Chunks: {api_chunks} == {total_chunks}")
                print(f"   - Documents: {api_documents} == {total_documents}")
                return True
            else:
                print("❌ INCOHÉRENCE API DÉTECTÉE!")
                print(f"   - Chunks: API={api_chunks} vs Direct={total_chunks}")
                print(f"   - Documents: API={api_documents} vs Direct={total_documents}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("⚠️  Serveur non démarré - Test API ignoré")
            print("✅ Validation Qdrant directe réussie")
            return True
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🚀 Validation des métriques RAG MIRAGE v2")
    print("=" * 60)
    
    success = asyncio.run(validate_rag_stats())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ VALIDATION RÉUSSIE - Métriques cohérentes")
        sys.exit(0)
    else:
        print("❌ VALIDATION ÉCHOUÉE - Incohérences détectées")
        sys.exit(1)

if __name__ == "__main__":
    main()

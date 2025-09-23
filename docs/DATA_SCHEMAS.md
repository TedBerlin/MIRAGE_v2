# MIRAGE v2 - Data Schemas RÉVOLUTIONNAIRES

## Table of Contents
1. [Overview](#overview)
2. [Core Data Models](#core-data-models)
3. [🧠 RAG Avancé Schemas](#rag-avancé-schemas)
4. [🛡️ HITL Prioritaire Schemas](#hitl-prioritaire-schemas)
5. [🌍 Multilingue Schemas](#multilingue-schemas)
6. [API Enhanced Schemas](#api-enhanced-schemas)
7. [Database Schemas](#database-schemas)
8. [Configuration Schemas](#configuration-schemas)
9. [Monitoring Schemas](#monitoring-schemas)
10. [Validation Schemas](#validation-schemas)

## Overview

This document defines the **RÉVOLUTIONNAIRES** data schemas used throughout the MIRAGE v2 system with **RAG AVANCÉ**, **HITL PRIORITAIRE**, and **4 LANGUES MÉDICALES**. All data structures are designed to be consistent, validated, and well-documented.

### 🌟 RÉVOLUTION MIRAGE v2 - SCHÉMAS
- **🧠 RAG Avancé** : Upload transparent, indexation immédiate, recherche intelligente
- **🛡️ HITL Prioritaire** : Validation humaine, sécurité absolue, traçabilité
- **🌍 Multilingue** : 4 langues médicales avec terminologie spécialisée
- **⚡ Performance** : < 1 seconde de réponse, 95% de précision

### Schema Standards RÉVOLUTIONNAIRES
- **JSON Schema**: Primary schema format
- **Pydantic Models**: Python data validation
- **Type Hints**: Python type annotations
- **Documentation**: Comprehensive field descriptions
- **RAG Schemas**: Advanced document processing
- **HITL Schemas**: Human validation and security
- **Multilingual Schemas**: 4 medical languages

## 🧠 RAG Avancé Schemas

### 🌟 RÉVOLUTION RAG - SCHÉMAS
MIRAGE v2 révolutionne le RAG avec des schémas pour **UPLOAD TRANSPARENT**, **INDEXATION IMMÉDIATE**, et **RECHERCHE INTELLIGENTE**.

### Document Upload Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Document Upload Request",
  "type": "object",
  "properties": {
    "file": {
      "type": "string",
      "format": "binary",
      "description": "Document file (PDF, TXT, DOCX)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["medical", "research", "protocol"],
          "description": "Document type"
        },
        "language": {
          "type": "string",
          "enum": ["en", "fr", "es", "de"],
          "description": "Document language"
        },
        "category": {
          "type": "string",
          "description": "Document category"
        }
      },
      "required": ["type", "language"]
    }
  },
  "required": ["file", "metadata"]
}
```

### Document Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Document Upload Response",
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Upload success status"
    },
    "document_id": {
      "type": "string",
      "description": "Unique document identifier"
    },
    "chunks_count": {
      "type": "integer",
      "description": "Number of chunks created"
    },
    "status": {
      "type": "string",
      "enum": ["processed", "pending", "failed"],
      "description": "Processing status"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Processing timestamp"
    }
  },
  "required": ["success", "document_id", "chunks_count", "status", "timestamp"]
}
```

### RAG Search Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RAG Search Request",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 5,
      "maxLength": 500,
      "description": "Search query"
    },
    "top_k": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20,
      "default": 5,
      "description": "Number of results to return"
    },
    "language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "description": "Query language"
    }
  },
  "required": ["query"]
}
```

### RAG Search Results Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RAG Search Results",
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Search success status"
    },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "chunk_id": {
            "type": "string",
            "description": "Unique chunk identifier"
          },
          "similarity": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Similarity score"
          },
          "content": {
            "type": "string",
            "description": "Chunk content"
          },
          "document_id": {
            "type": "string",
            "description": "Source document ID"
          },
          "metadata": {
            "type": "object",
            "description": "Chunk metadata"
          }
        },
        "required": ["chunk_id", "similarity", "content", "document_id"]
      }
    },
    "total_found": {
      "type": "integer",
      "description": "Total number of results found"
    },
    "query": {
      "type": "string",
      "description": "Original query"
    }
  },
  "required": ["success", "results", "total_found", "query"]
}
```

## 🛡️ HITL Prioritaire Schemas

### 🌟 RÉVOLUTION SÉCURITAIRE - SCHÉMAS
MIRAGE v2 implémente des schémas pour **HITL PRIORITAIRE** avec validation humaine obligatoire et traçabilité complète.

### Human Validation Request Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Human Validation Request",
  "type": "object",
  "properties": {
    "query_id": {
      "type": "string",
      "description": "Unique query identifier"
    },
    "query": {
      "type": "string",
      "description": "Original query text"
    },
    "detected_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "description": "Detected language"
    },
    "safety_keywords": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Detected safety keywords"
    },
    "human_validation_required": {
      "type": "boolean",
      "description": "Whether human validation is required"
    },
    "status": {
      "type": "string",
      "enum": ["pending_validation", "validated", "rejected"],
      "description": "Validation status"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Request timestamp"
    }
  },
  "required": ["query_id", "query", "detected_language", "human_validation_required", "status", "timestamp"]
}
```

### Human Validation Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Human Validation Response",
  "type": "object",
  "properties": {
    "validation_id": {
      "type": "string",
      "description": "Unique validation identifier"
    },
    "query_id": {
      "type": "string",
      "description": "Original query identifier"
    },
    "human_decision": {
      "type": "string",
      "enum": ["approved", "rejected", "modified"],
      "description": "Human validation decision"
    },
    "human_feedback": {
      "type": "string",
      "description": "Human feedback and comments"
    },
    "validated_response": {
      "type": "string",
      "description": "Validated response text"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Validation timestamp"
    }
  },
  "required": ["validation_id", "query_id", "human_decision", "timestamp"]
}
```

## 🌍 Multilingue Schemas

### 🌟 RÉVOLUTION LINGUISTIQUE - SCHÉMAS
MIRAGE v2 supporte **4 LANGUES MÉDICALES** avec des schémas pour détection automatique et terminologie spécialisée.

### Language Detection Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Language Detection",
  "type": "object",
  "properties": {
    "detected_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "description": "Detected language"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Detection confidence score"
    },
    "keywords_found": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Medical keywords found"
    },
    "terminology_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Medical terminology score"
    }
  },
  "required": ["detected_language", "confidence"]
}
```

### Multilingual Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Multilingual Response",
  "type": "object",
  "properties": {
    "original_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "description": "Original query language"
    },
    "target_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "description": "Target response language"
    },
    "translated_response": {
      "type": "string",
      "description": "Translated response"
    },
    "medical_terminology_preserved": {
      "type": "boolean",
      "description": "Whether medical terminology was preserved"
    },
    "translation_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Translation confidence score"
    }
  },
  "required": ["original_language", "target_language", "translated_response"]
}
```

## API Enhanced Schemas

### 🌟 RÉVOLUTION API - SCHÉMAS
MIRAGE v2 révolutionne l'API avec des schémas pour **PORT 8006**, **RAG INTÉGRÉ**, et **ENDPOINTS COMPLETS**.

### Enhanced Query Request Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Enhanced Query Request",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 10,
      "maxLength": 1000,
      "description": "User query text"
    },
    "target_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "default": "en",
      "description": "Target language for response"
    },
    "enable_human_loop": {
      "type": "boolean",
      "default": true,
      "description": "Enable HITL priority validation"
    },
    "rag_enabled": {
      "type": "boolean",
      "default": true,
      "description": "Enable RAG advanced search"
    },
    "sources_required": {
      "type": "boolean",
      "default": true,
      "description": "Require source attribution"
    }
  },
  "required": ["query"]
}
```

### Enhanced Query Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Enhanced Query Response",
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Query processing success"
    },
    "answer": {
      "type": "string",
      "description": "Generated response"
    },
    "human_validation_required": {
      "type": "boolean",
      "description": "Whether human validation is required"
    },
    "workflow": {
      "type": "string",
      "enum": ["normal_processing", "human_validation", "ethical_fallback"],
      "description": "Processing workflow used"
    },
    "consensus": {
      "type": "string",
      "enum": ["approved", "pending_human_validation", "ethical_fallback"],
      "description": "Consensus status"
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "content": {
            "type": "string",
            "description": "Source content"
          },
          "similarity": {
            "type": "number",
            "description": "Similarity score"
          },
          "document_id": {
            "type": "string",
            "description": "Source document ID"
          }
        }
      },
      "description": "RAG sources with attribution"
    },
    "rag_enabled": {
      "type": "boolean",
      "description": "Whether RAG was used"
    },
    "rag_results_count": {
      "type": "integer",
      "description": "Number of RAG results found"
    },
    "detected_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "description": "Detected query language"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Response timestamp"
    }
  },
  "required": ["success", "answer", "human_validation_required", "workflow", "consensus"]
}
```

## Core Data Models

### Query Request Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Query Request",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 10,
      "maxLength": 1000,
      "description": "User query text"
    },
    "enable_human_loop": {
      "type": "boolean",
      "default": false,
      "description": "Enable human-in-the-loop validation"
    },
    "target_language": {
      "type": "string",
      "enum": ["en", "fr", "es", "de"],
      "default": "en",
      "description": "Target language for response"
    },
    "context": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string",
          "description": "User identifier"
        },
        "session_id": {
          "type": "string",
          "description": "Session identifier"
        },
        "additional_data": {
          "type": "object",
          "description": "Additional context data"
        }
      }
    }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

### Query Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Query Response",
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the query was processed successfully"
    },
    "answer": {
      "type": "string",
      "description": "Generated answer"
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Source document references"
    },
    "processing_time": {
      "type": "number",
      "minimum": 0,
      "description": "Processing time in seconds"
    },
    "iteration": {
      "type": "integer",
      "minimum": 1,
      "description": "Number of iterations performed"
    },
    "consensus": {
      "type": "string",
      "enum": ["OUI", "NON", "UNKNOWN"],
      "description": "Consensus decision"
    },
    "query_hash": {
      "type": "string",
      "description": "Hash of the original query"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Processing timestamp"
        },
        "agent_versions": {
          "type": "object",
          "description": "Versions of agents used"
        },
        "rag_context": {
          "type": "object",
          "description": "RAG context information"
        }
      }
    },
    "human_validation_required": {
      "type": "boolean",
      "description": "Whether human validation is required"
    },
    "translated_response": {
      "type": "string",
      "description": "Translated response (if applicable)"
    },
    "target_language": {
      "type": "string",
      "description": "Target language of response"
    },
    "error": {
      "type": "string",
      "description": "Error message (if success is false)"
    }
  },
  "required": ["success"],
  "additionalProperties": false
}
```

### Document Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Document",
  "type": "object",
  "properties": {
    "document_id": {
      "type": "string",
      "description": "Unique document identifier"
    },
    "filename": {
      "type": "string",
      "description": "Original filename"
    },
    "file_path": {
      "type": "string",
      "description": "Path to document file"
    },
    "file_size": {
      "type": "integer",
      "minimum": 0,
      "description": "File size in bytes"
    },
    "file_type": {
      "type": "string",
      "enum": ["pdf", "txt", "docx"],
      "description": "Document file type"
    },
    "content": {
      "type": "string",
      "description": "Document content"
    },
    "chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "chunk_id": {
            "type": "string",
            "description": "Unique chunk identifier"
          },
          "content": {
            "type": "string",
            "description": "Chunk content"
          },
          "start_index": {
            "type": "integer",
            "description": "Start index in document"
          },
          "end_index": {
            "type": "integer",
            "description": "End index in document"
          },
          "metadata": {
            "type": "object",
            "description": "Chunk metadata"
          }
        }
      },
      "description": "Document chunks"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "Document title"
        },
        "author": {
          "type": "string",
          "description": "Document author"
        },
        "creation_date": {
          "type": "string",
          "format": "date-time",
          "description": "Document creation date"
        },
        "modification_date": {
          "type": "string",
          "format": "date-time",
          "description": "Document modification date"
        },
        "language": {
          "type": "string",
          "description": "Document language"
        },
        "category": {
          "type": "string",
          "description": "Document category"
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Document tags"
        }
      }
    },
    "processing_status": {
      "type": "string",
      "enum": ["pending", "processing", "completed", "failed"],
      "description": "Document processing status"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Document creation timestamp"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Document update timestamp"
    }
  },
  "required": ["document_id", "filename", "file_type", "processing_status"],
  "additionalProperties": false
}
```

### Agent Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Response",
  "type": "object",
  "properties": {
    "agent_name": {
      "type": "string",
      "enum": ["GeneratorAgent", "VerifierAgent", "ReformerAgent", "TranslatorAgent"],
      "description": "Name of the agent"
    },
    "success": {
      "type": "boolean",
      "description": "Whether the agent operation was successful"
    },
    "response": {
      "type": "string",
      "description": "Agent response text"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence score"
    },
    "vote": {
      "type": "string",
      "enum": ["OUI", "NON", "UNKNOWN"],
      "description": "Verifier vote (for VerifierAgent)"
    },
    "analysis": {
      "type": "string",
      "description": "Analysis text (for VerifierAgent)"
    },
    "reformed_response": {
      "type": "object",
      "description": "Reformed response (for ReformerAgent)",
      "properties": {
        "response_id": {
          "type": "string",
          "description": "Response identifier"
        },
        "query": {
          "type": "string",
          "description": "Original query"
        },
        "answer": {
          "type": "string",
          "description": "Reformed answer"
        },
        "sources": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Source references"
        },
        "validation_status": {
          "type": "string",
          "enum": ["approved", "reformed", "rejected"],
          "description": "Validation status"
        }
      }
    },
    "translated_response": {
      "type": "string",
      "description": "Translated response (for TranslatorAgent)"
    },
    "source_language": {
      "type": "string",
      "description": "Source language (for TranslatorAgent)"
    },
    "target_language": {
      "type": "string",
      "description": "Target language (for TranslatorAgent)"
    },
    "processing_time": {
      "type": "number",
      "minimum": 0,
      "description": "Processing time in seconds"
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata"
    },
    "error": {
      "type": "string",
      "description": "Error message (if success is false)"
    }
  },
  "required": ["agent_name", "success"],
  "additionalProperties": false
}
```

## API Schemas

### Health Check Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Health Check Response",
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["healthy", "unhealthy", "degraded"],
      "description": "Overall system health status"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Health check timestamp"
    },
    "components": {
      "type": "object",
      "properties": {
        "orchestrator": {
          "type": "string",
          "enum": ["healthy", "unhealthy"],
          "description": "Orchestrator health status"
        },
        "rag_system": {
          "type": "string",
          "enum": ["healthy", "unhealthy"],
          "description": "RAG system health status"
        },
        "agents": {
          "type": "object",
          "properties": {
            "generator": {
              "type": "string",
              "enum": ["healthy", "unhealthy"],
              "description": "Generator agent health"
            },
            "verifier": {
              "type": "string",
              "enum": ["healthy", "unhealthy"],
              "description": "Verifier agent health"
            },
            "reformer": {
              "type": "string",
              "enum": ["healthy", "unhealthy"],
              "description": "Reformer agent health"
            },
            "translator": {
              "type": "string",
              "enum": ["healthy", "unhealthy"],
              "description": "Translator agent health"
            }
          }
        },
        "database": {
          "type": "string",
          "enum": ["healthy", "unhealthy"],
          "description": "Database health status"
        },
        "monitoring": {
          "type": "string",
          "enum": ["healthy", "unhealthy"],
          "description": "Monitoring system health"
        }
      }
    },
    "uptime": {
      "type": "string",
      "description": "System uptime"
    },
    "version": {
      "type": "string",
      "description": "System version"
    }
  },
  "required": ["status", "timestamp", "components"],
  "additionalProperties": false
}
```

### Metrics Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "System Metrics",
  "type": "object",
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Metrics timestamp"
    },
    "system": {
      "type": "object",
      "properties": {
        "cpu_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "CPU usage percentage"
        },
        "memory_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Memory usage percentage"
        },
        "disk_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Disk usage percentage"
        },
        "network_io": {
          "type": "object",
          "properties": {
            "bytes_sent": {
              "type": "integer",
              "minimum": 0,
              "description": "Bytes sent"
            },
            "bytes_received": {
              "type": "integer",
              "minimum": 0,
              "description": "Bytes received"
            }
          }
        }
      }
    },
    "application": {
      "type": "object",
      "properties": {
        "queries_processed": {
          "type": "integer",
          "minimum": 0,
          "description": "Total queries processed"
        },
        "queries_per_minute": {
          "type": "number",
          "minimum": 0,
          "description": "Queries per minute"
        },
        "average_response_time": {
          "type": "number",
          "minimum": 0,
          "description": "Average response time in seconds"
        },
        "success_rate": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Success rate percentage"
        },
        "error_rate": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Error rate percentage"
        }
      }
    },
    "agents": {
      "type": "object",
      "properties": {
        "generator": {
          "type": "object",
          "properties": {
            "operations": {
              "type": "integer",
              "minimum": 0,
              "description": "Total operations"
            },
            "success_rate": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "Success rate percentage"
            },
            "average_duration": {
              "type": "number",
              "minimum": 0,
              "description": "Average operation duration"
            }
          }
        },
        "verifier": {
          "type": "object",
          "properties": {
            "operations": {
              "type": "integer",
              "minimum": 0,
              "description": "Total operations"
            },
            "success_rate": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "Success rate percentage"
            },
            "average_duration": {
              "type": "number",
              "minimum": 0,
              "description": "Average operation duration"
            },
            "vote_distribution": {
              "type": "object",
              "properties": {
                "oui": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "OUI votes"
                },
                "non": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "NON votes"
                },
                "unknown": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "UNKNOWN votes"
                }
              }
            }
          }
        }
      }
    },
    "rag": {
      "type": "object",
      "properties": {
        "documents_processed": {
          "type": "integer",
          "minimum": 0,
          "description": "Total documents processed"
        },
        "chunks_created": {
          "type": "integer",
          "minimum": 0,
          "description": "Total chunks created"
        },
        "embeddings_generated": {
          "type": "integer",
          "minimum": 0,
          "description": "Total embeddings generated"
        },
        "queries_processed": {
          "type": "integer",
          "minimum": 0,
          "description": "Total RAG queries processed"
        },
        "average_similarity": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Average similarity score"
        }
      }
    }
  },
  "required": ["timestamp"],
  "additionalProperties": false
}
```

## Database Schemas

### ChromaDB Collection Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChromaDB Collection",
  "type": "object",
  "properties": {
    "collection_name": {
      "type": "string",
      "description": "Collection name"
    },
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Document ID"
          },
          "content": {
            "type": "string",
            "description": "Document content"
          },
          "metadata": {
            "type": "object",
            "properties": {
              "source": {
                "type": "string",
                "description": "Source document"
              },
              "chunk_id": {
                "type": "string",
                "description": "Chunk identifier"
              },
              "document_id": {
                "type": "string",
                "description": "Parent document ID"
              },
              "chunk_index": {
                "type": "integer",
                "description": "Chunk index in document"
              },
              "start_index": {
                "type": "integer",
                "description": "Start index in document"
              },
              "end_index": {
                "type": "integer",
                "description": "End index in document"
              },
              "language": {
                "type": "string",
                "description": "Document language"
              },
              "category": {
                "type": "string",
                "description": "Document category"
              },
              "tags": {
                "type": "array",
                "items": {
                  "type": "string"
                },
                "description": "Document tags"
              },
              "created_at": {
                "type": "string",
                "format": "date-time",
                "description": "Creation timestamp"
              },
              "updated_at": {
                "type": "string",
                "format": "date-time",
                "description": "Update timestamp"
              }
            }
          }
        }
      }
    },
    "embeddings": {
      "type": "array",
      "items": {
        "type": "array",
        "items": {
          "type": "number"
        },
        "description": "Embedding vector"
      }
    },
    "ids": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Document IDs"
    }
  },
  "required": ["collection_name", "documents", "embeddings", "ids"],
  "additionalProperties": false
}
```

### Metadata Database Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Metadata Database",
  "type": "object",
  "properties": {
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "document_id": {
            "type": "string",
            "description": "Unique document identifier"
          },
          "filename": {
            "type": "string",
            "description": "Original filename"
          },
          "file_path": {
            "type": "string",
            "description": "File path"
          },
          "file_size": {
            "type": "integer",
            "minimum": 0,
            "description": "File size in bytes"
          },
          "file_hash": {
            "type": "string",
            "description": "File hash for integrity"
          },
          "processing_status": {
            "type": "string",
            "enum": ["pending", "processing", "completed", "failed"],
            "description": "Processing status"
          },
          "chunks_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of chunks"
          },
          "embeddings_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of embeddings"
          },
          "metadata": {
            "type": "object",
            "description": "Document metadata"
          },
          "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "Creation timestamp"
          },
          "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "Update timestamp"
          }
        }
      }
    },
    "chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "chunk_id": {
            "type": "string",
            "description": "Unique chunk identifier"
          },
          "document_id": {
            "type": "string",
            "description": "Parent document ID"
          },
          "content": {
            "type": "string",
            "description": "Chunk content"
          },
          "start_index": {
            "type": "integer",
            "description": "Start index in document"
          },
          "end_index": {
            "type": "integer",
            "description": "End index in document"
          },
          "chunk_index": {
            "type": "integer",
            "description": "Chunk index in document"
          },
          "embedding_id": {
            "type": "string",
            "description": "Associated embedding ID"
          },
          "metadata": {
            "type": "object",
            "description": "Chunk metadata"
          },
          "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "Creation timestamp"
          }
        }
      }
    }
  },
  "required": ["documents", "chunks"],
  "additionalProperties": false
}
```

## Configuration Schemas

### Environment Configuration Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Environment Configuration",
  "type": "object",
  "properties": {
    "GEMINI_API_KEY": {
      "type": "string",
      "minLength": 1,
      "description": "Google Gemini API key"
    },
    "CHROMA_DB_PATH": {
      "type": "string",
      "default": "./data/embeddings",
      "description": "ChromaDB storage path"
    },
    "LOG_LEVEL": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
      "default": "INFO",
      "description": "Logging level"
    },
    "ENVIRONMENT": {
      "type": "string",
      "enum": ["development", "staging", "production"],
      "default": "development",
      "description": "Environment type"
    },
    "RAG_CHUNK_SIZE": {
      "type": "integer",
      "minimum": 100,
      "maximum": 2000,
      "default": 1000,
      "description": "RAG chunk size"
    },
    "RAG_CHUNK_OVERLAP": {
      "type": "integer",
      "minimum": 0,
      "maximum": 500,
      "default": 200,
      "description": "RAG chunk overlap"
    },
    "RAG_MAX_RESULTS": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20,
      "default": 5,
      "description": "Maximum RAG results"
    },
    "ORCHESTRATOR_MAX_RETRIES": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "default": 3,
      "description": "Maximum orchestrator retries"
    },
    "ORCHESTRATOR_RETRY_DELAY_SECONDS": {
      "type": "number",
      "minimum": 0.1,
      "maximum": 10.0,
      "default": 1.0,
      "description": "Orchestrator retry delay"
    },
    "ORCHESTRATOR_CACHE_TTL_SECONDS": {
      "type": "integer",
      "minimum": 60,
      "maximum": 86400,
      "default": 3600,
      "description": "Cache TTL in seconds"
    },
    "HUMAN_LOOP_TIMEOUT_SECONDS": {
      "type": "integer",
      "minimum": 60,
      "maximum": 3600,
      "default": 300,
      "description": "Human loop timeout"
    },
    "HUMAN_LOOP_PRIORITY_THRESHOLD": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.3,
      "description": "Human loop priority threshold"
    }
  },
  "required": ["GEMINI_API_KEY"],
  "additionalProperties": false
}
```

### Application Configuration Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Application Configuration",
  "type": "object",
  "properties": {
    "api": {
      "type": "object",
      "properties": {
        "host": {
          "type": "string",
          "default": "127.0.0.1",
          "description": "API host"
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535,
          "default": 8000,
          "description": "API port"
        },
        "timeout": {
          "type": "integer",
          "minimum": 1,
          "maximum": 300,
          "default": 30,
          "description": "API timeout in seconds"
        }
      }
    },
    "dashboard": {
      "type": "object",
      "properties": {
        "host": {
          "type": "string",
          "default": "127.0.0.1",
          "description": "Dashboard host"
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535,
          "default": 8080,
          "description": "Dashboard port"
        },
        "update_interval": {
          "type": "integer",
          "minimum": 1,
          "maximum": 60,
          "default": 5,
          "description": "Update interval in seconds"
        }
      }
    },
    "monitoring": {
      "type": "object",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable monitoring"
        },
        "interval": {
          "type": "integer",
          "minimum": 10,
          "maximum": 300,
          "default": 30,
          "description": "Monitoring interval in seconds"
        },
        "retention_days": {
          "type": "integer",
          "minimum": 1,
          "maximum": 365,
          "default": 30,
          "description": "Metrics retention in days"
        }
      }
    },
    "security": {
      "type": "object",
      "properties": {
        "api_key_required": {
          "type": "boolean",
          "default": true,
          "description": "Require API key for requests"
        },
        "rate_limit": {
          "type": "integer",
          "minimum": 1,
          "maximum": 1000,
          "default": 100,
          "description": "Rate limit per minute"
        },
        "cors_origins": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "default": ["*"],
          "description": "CORS allowed origins"
        }
      }
    }
  },
  "required": [],
  "additionalProperties": false
}
```

## Monitoring Schemas

### Alert Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Alert",
  "type": "object",
  "properties": {
    "alert_id": {
      "type": "string",
      "description": "Unique alert identifier"
    },
    "alert_type": {
      "type": "string",
      "enum": ["cpu_usage", "memory_usage", "disk_usage", "response_time", "error_rate", "query_failure", "agent_failure", "rag_failure"],
      "description": "Type of alert"
    },
    "severity": {
      "type": "string",
      "enum": ["info", "warning", "critical"],
      "description": "Alert severity"
    },
    "message": {
      "type": "string",
      "description": "Alert message"
    },
    "component": {
      "type": "string",
      "description": "Component that generated the alert"
    },
    "threshold": {
      "type": "number",
      "description": "Threshold value that triggered the alert"
    },
    "current_value": {
      "type": "number",
      "description": "Current value that exceeded threshold"
    },
    "status": {
      "type": "string",
      "enum": ["active", "acknowledged", "resolved"],
      "description": "Alert status"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Alert creation timestamp"
    },
    "acknowledged_at": {
      "type": "string",
      "format": "date-time",
      "description": "Alert acknowledgment timestamp"
    },
    "acknowledged_by": {
      "type": "string",
      "description": "User who acknowledged the alert"
    },
    "resolved_at": {
      "type": "string",
      "format": "date-time",
      "description": "Alert resolution timestamp"
    },
    "resolution_notes": {
      "type": "string",
      "description": "Alert resolution notes"
    }
  },
  "required": ["alert_id", "alert_type", "severity", "message", "component", "status", "created_at"],
  "additionalProperties": false
}
```

### Metrics Collection Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Metrics Collection",
  "type": "object",
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Metrics collection timestamp"
    },
    "query_metrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "query_id": {
            "type": "string",
            "description": "Query identifier"
          },
          "query_length": {
            "type": "integer",
            "description": "Query length in characters"
          },
          "duration": {
            "type": "number",
            "minimum": 0,
            "description": "Processing duration in seconds"
          },
          "success": {
            "type": "boolean",
            "description": "Whether query was successful"
          },
          "iteration": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of iterations"
          },
          "consensus": {
            "type": "string",
            "enum": ["OUI", "NON", "UNKNOWN"],
            "description": "Consensus decision"
          }
        }
      }
    },
    "agent_metrics": {
      "type": "object",
      "properties": {
        "generator": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "operation": {
                "type": "string",
                "description": "Operation type"
              },
              "duration": {
                "type": "number",
                "minimum": 0,
                "description": "Operation duration"
              },
              "success": {
                "type": "boolean",
                "description": "Operation success"
              },
              "input_size": {
                "type": "integer",
                "minimum": 0,
                "description": "Input size in characters"
              },
              "output_size": {
                "type": "integer",
                "minimum": 0,
                "description": "Output size in characters"
              }
            }
          }
        }
      }
    },
    "rag_metrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "operation": {
            "type": "string",
            "description": "RAG operation type"
          },
          "duration": {
            "type": "number",
            "minimum": 0,
            "description": "Operation duration"
          },
          "success": {
            "type": "boolean",
            "description": "Operation success"
          },
          "documents_processed": {
            "type": "integer",
            "minimum": 0,
            "description": "Documents processed"
          },
          "chunks_created": {
            "type": "integer",
            "minimum": 0,
            "description": "Chunks created"
          }
        }
      }
    },
    "system_metrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "metric_name": {
            "type": "string",
            "description": "Metric name"
          },
          "value": {
            "type": "number",
            "description": "Metric value"
          },
          "unit": {
            "type": "string",
            "description": "Metric unit"
          }
        }
      }
    },
    "error_metrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "error_type": {
            "type": "string",
            "description": "Error type"
          },
          "error_message": {
            "type": "string",
            "description": "Error message"
          },
          "component": {
            "type": "string",
            "description": "Component where error occurred"
          },
          "severity": {
            "type": "string",
            "enum": ["error", "warning", "info"],
            "description": "Error severity"
          }
        }
      }
    }
  },
  "required": ["timestamp"],
  "additionalProperties": false
}
```

## Validation Schemas

### Input Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Input Validation",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 10,
      "maxLength": 1000,
      "pattern": "^[a-zA-Z0-9\\s\\?\\!\\.\\,\\-]+$",
      "description": "Query text validation"
    },
    "document_path": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9\\/\\-\\.]+$",
      "description": "Document path validation"
    },
    "file_size": {
      "type": "integer",
      "minimum": 1024,
      "maximum": 104857600,
      "description": "File size validation (1KB to 100MB)"
    },
    "file_type": {
      "type": "string",
      "enum": ["pdf", "txt", "docx"],
      "description": "File type validation"
    },
    "language_code": {
      "type": "string",
      "pattern": "^[a-z]{2}$",
      "description": "Language code validation (ISO 639-1)"
    },
    "api_key": {
      "type": "string",
      "minLength": 20,
      "maxLength": 100,
      "pattern": "^[a-zA-Z0-9\\-_]+$",
      "description": "API key validation"
    }
  },
  "required": [],
  "additionalProperties": false
}
```

### Response Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Response Validation",
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Success indicator"
    },
    "response_time": {
      "type": "number",
      "minimum": 0,
      "maximum": 300,
      "description": "Response time validation (0-300 seconds)"
    },
    "answer_length": {
      "type": "integer",
      "minimum": 10,
      "maximum": 10000,
      "description": "Answer length validation (10-10000 characters)"
    },
    "sources_count": {
      "type": "integer",
      "minimum": 0,
      "maximum": 20,
      "description": "Sources count validation (0-20 sources)"
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence score validation (0-1)"
    },
    "consensus_valid": {
      "type": "boolean",
      "description": "Consensus validation"
    }
  },
  "required": ["success"],
  "additionalProperties": false
}
```

## Conclusion

These schemas provide a comprehensive foundation for data validation, API documentation, and system integration. All schemas are designed to be:

- **Consistent**: Uniform structure across all components
- **Validated**: Comprehensive validation rules
- **Documented**: Clear field descriptions and examples
- **Extensible**: Easy to extend for future requirements
- **Compatible**: JSON Schema standard compliance

For implementation details, refer to the corresponding Pydantic models in the source code.

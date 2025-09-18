"""
Specialized CLI commands for MIRAGE v2.

Additional commands for advanced operations and system management.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import click
import structlog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.orchestrator import Orchestrator
from rag.rag_engine import RAGEngine
from agents.generator_agent import GeneratorAgent
from agents.verifier_agent import VerifierAgent
from agents.reformer_agent import ReformerAgent
from agents.translator_agent import TranslatorAgent

logger = structlog.get_logger(__name__)


@click.command()
@click.option('--ingest', '-i', is_flag=True, help='Ingest documents from data directory')
@click.option('--stats', '-s', is_flag=True, help='Show RAG system statistics')
@click.option('--clear', '-c', is_flag=True, help='Clear all documents from RAG system')
@click.option('--add', '-a', type=click.Path(exists=True), help='Add a specific document to RAG system')
@click.pass_context
def rag_command(ctx, ingest, stats, clear, add):
    """
    Manage the RAG (Retrieval-Augmented Generation) system.
    
    Examples:
        mirage rag --ingest          # Ingest all documents
        mirage rag --stats           # Show system statistics
        mirage rag --clear           # Clear all documents
        mirage rag --add document.pdf # Add specific document
    """
    try:
        # Initialize RAG engine
        rag_engine = RAGEngine()
        
        if ingest:
            click.echo("📚 Ingesting documents...")
            result = rag_engine.ingest_documents()
            
            if result["success"]:
                click.echo(f"✅ Successfully ingested {result['documents_processed']} documents")
                click.echo(f"📝 Created {result['chunks_created']} chunks")
                click.echo(f"🔢 Generated {result['embeddings_generated']} embeddings")
            else:
                click.echo(f"❌ Ingestion failed: {result.get('error', 'Unknown error')}", err=True)
                sys.exit(1)
        
        elif stats:
            click.echo("📊 RAG System Statistics:")
            stats = rag_engine.get_system_stats()
            
            if "error" not in stats:
                # Display document stats
                doc_stats = stats.get("documents", {})
                click.echo(f"   📄 Total files: {doc_stats.get('total_files', 0)}")
                click.echo(f"   📁 Files: {', '.join(doc_stats.get('files', []))}")
                
                # Display embedding stats
                emb_stats = stats.get("embeddings", {})
                click.echo(f"   🔢 Vector DB documents: {emb_stats.get('total_documents', 0)}")
                click.echo(f"   🏷️  Metadata fields: {len(emb_stats.get('metadata_fields', []))}")
                
                # Display metadata stats
                meta_stats = stats.get("metadata", {})
                click.echo(f"   📊 Metadata documents: {meta_stats.get('total_documents', 0)}")
                click.echo(f"   📈 Document types: {meta_stats.get('document_types', {})}")
            else:
                click.echo(f"❌ Failed to get stats: {stats['error']}", err=True)
                sys.exit(1)
        
        elif clear:
            if click.confirm("⚠️  Are you sure you want to clear all documents from the RAG system?"):
                click.echo("🗑️  Clearing RAG system...")
                success = rag_engine.embedding_manager.reset_collection()
                
                if success:
                    click.echo("✅ RAG system cleared successfully")
                else:
                    click.echo("❌ Failed to clear RAG system", err=True)
                    sys.exit(1)
            else:
                click.echo("❌ Operation cancelled")
        
        elif add:
            document_path = Path(add)
            click.echo(f"📄 Adding document: {document_path.name}")
            
            result = rag_engine.add_document(document_path)
            
            if result["success"]:
                click.echo(f"✅ Document added successfully")
                click.echo(f"📝 Created {result['chunks_created']} chunks")
                click.echo(f"🆔 Document ID: {result['document_id']}")
            else:
                click.echo(f"❌ Failed to add document: {result.get('error', 'Unknown error')}", err=True)
                sys.exit(1)
        
        else:
            click.echo("❌ Please specify an action: --ingest, --stats, --clear, or --add", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ RAG command failed: {str(e)}", err=True)
        sys.exit(1)


@click.command()
@click.option('--list', '-l', is_flag=True, help='List all available agents')
@click.option('--test', '-t', type=click.Choice(['generator', 'verifier', 'reformer', 'translator', 'all']), help='Test specific agent')
@click.option('--info', '-i', type=click.Choice(['generator', 'verifier', 'reformer', 'translator']), help='Show agent information')
@click.pass_context
def agents_command(ctx, list, test, info):
    """
    Manage and test MIRAGE agents.
    
    Examples:
        mirage agents --list                    # List all agents
        mirage agents --test generator          # Test generator agent
        mirage agents --test all                # Test all agents
        mirage agents --info verifier           # Show verifier agent info
    """
    try:
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo("❌ Error: GEMINI_API_KEY not found in environment variables", err=True)
            sys.exit(1)
        
        if list:
            click.echo("🤖 Available MIRAGE Agents:")
            agents = [
                ("Generator", "The Innovator", "Primary response generator for pharmaceutical research"),
                ("Verifier", "The Analyst", "Quality assurance and validation of generated responses"),
                ("Reformer", "The Editor", "Response refinement and quality enhancement"),
                ("Translator", "The Linguist", "Language translation and localization")
            ]
            
            for name, nickname, description in agents:
                click.echo(f"   🤖 {name} ({nickname})")
                click.echo(f"      {description}")
        
        elif test:
            click.echo(f"🧪 Testing {test} agent(s)...")
            
            if test == "all":
                agents_to_test = ["generator", "verifier", "reformer", "translator"]
            else:
                agents_to_test = [test]
            
            for agent_type in agents_to_test:
                click.echo(f"\n🔍 Testing {agent_type} agent...")
                
                try:
                    if agent_type == "generator":
                        agent = GeneratorAgent(api_key)
                        test_cases = [
                            {
                                "query": "What are the side effects?",
                                "context": "This medication can cause dizziness and headache.",
                                "expected_unknown": False
                            }
                        ]
                        results = agent.test_agent(test_cases)
                    
                    elif agent_type == "verifier":
                        agent = VerifierAgent(api_key)
                        test_cases = [
                            {
                                "query": "What are the side effects?",
                                "context": "This medication can cause dizziness and headache.",
                                "response": "The medication can cause dizziness and headache as side effects.",
                                "expected_vote": "OUI"
                            }
                        ]
                        results = agent.test_agent(test_cases)
                    
                    elif agent_type == "reformer":
                        agent = ReformerAgent(api_key)
                        test_cases = [
                            {
                                "query": "What are the side effects?",
                                "context": "This medication can cause dizziness and headache.",
                                "response": "Dizziness and headache.",
                                "verifier_analysis": "Response is accurate but could be more comprehensive. VOTE: OUI"
                            }
                        ]
                        results = agent.test_agent(test_cases)
                    
                    elif agent_type == "translator":
                        agent = TranslatorAgent(api_key)
                        test_cases = [
                            {
                                "response": "This medication can cause dizziness and headache.",
                                "context": "Pharmaceutical research document.",
                                "source_language": "en",
                                "target_language": "fr"
                            }
                        ]
                        results = agent.test_agent(test_cases)
                    
                    # Display results
                    if results["passed"] == results["total_tests"]:
                        click.echo(f"   ✅ {agent_type} agent: {results['passed']}/{results['total_tests']} tests passed")
                    else:
                        click.echo(f"   ❌ {agent_type} agent: {results['passed']}/{results['total_tests']} tests passed")
                        for test_result in results["test_results"]:
                            if not test_result["passed"]:
                                click.echo(f"      Error: {test_result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    click.echo(f"   ❌ {agent_type} agent test failed: {str(e)}")
        
        elif info:
            click.echo(f"ℹ️  {info.title()} Agent Information:")
            
            try:
                if info == "generator":
                    agent = GeneratorAgent(api_key)
                elif info == "verifier":
                    agent = VerifierAgent(api_key)
                elif info == "reformer":
                    agent = ReformerAgent(api_key)
                elif info == "translator":
                    agent = TranslatorAgent(api_key)
                
                agent_info = agent.get_agent_info()
                
                click.echo(f"   Name: {agent_info['name']}")
                click.echo(f"   Type: {agent_info['type']}")
                click.echo(f"   Model: {agent_info['model']}")
                click.echo(f"   Role: {agent_info['role']}")
                click.echo(f"   Capabilities:")
                for capability in agent_info['capabilities']:
                    click.echo(f"      • {capability}")
                click.echo(f"   Optimizations:")
                for optimization in agent_info['optimizations']:
                    click.echo(f"      • {optimization}")
                
                if info == "translator":
                    click.echo(f"   Supported Languages: {', '.join(agent_info['supported_languages'])}")
            
            except Exception as e:
                click.echo(f"❌ Failed to get agent info: {str(e)}", err=True)
                sys.exit(1)
        
        else:
            click.echo("❌ Please specify an action: --list, --test, or --info", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Agents command failed: {str(e)}", err=True)
        sys.exit(1)


@click.command()
@click.option('--monitor', '-m', is_flag=True, help='Start real-time monitoring')
@click.option('--logs', '-l', is_flag=True, help='Show recent logs')
@click.option('--metrics', '-t', is_flag=True, help='Show performance metrics')
@click.option('--clear-logs', '-c', is_flag=True, help='Clear log files')
@click.pass_context
def monitor_command(ctx, monitor, logs, metrics, clear_logs):
    """
    Monitor MIRAGE system performance and logs.
    
    Examples:
        mirage monitor --logs           # Show recent logs
        mirage monitor --metrics        # Show performance metrics
        mirage monitor --monitor        # Start real-time monitoring
        mirage monitor --clear-logs     # Clear log files
    """
    try:
        if logs:
            click.echo("📋 Recent MIRAGE Logs:")
            log_file = Path("logs/mirage.log")
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Show last 20 lines
                    for line in lines[-20:]:
                        click.echo(f"   {line.strip()}")
            else:
                click.echo("   No log file found")
        
        elif metrics:
            click.echo("📊 MIRAGE Performance Metrics:")
            
            # Check API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                click.echo("❌ Error: GEMINI_API_KEY not found in environment variables", err=True)
                sys.exit(1)
            
            # Initialize orchestrator
            orchestrator = Orchestrator(api_key=api_key)
            
            # Get system stats
            stats = orchestrator.get_system_stats()
            
            if "error" not in stats:
                # Display orchestrator stats
                orch_stats = stats.get("orchestrator", {})
                click.echo(f"   🔧 Orchestrator:")
                click.echo(f"      Human loop: {'Enabled' if orch_stats.get('enable_human_loop') else 'Disabled'}")
                click.echo(f"      Max iterations: {orch_stats.get('max_iterations', 'N/A')}")
                click.echo(f"      Request timeout: {orch_stats.get('request_timeout', 'N/A')}s")
                
                # Display cache stats
                cache_stats = stats.get("cache", {})
                click.echo(f"   💾 Cache:")
                click.echo(f"      Context cache: {cache_stats.get('context_cache_size', 0)} entries")
                click.echo(f"      Response cache: {cache_stats.get('response_cache_size', 0)} entries")
                click.echo(f"      TTL: {cache_stats.get('cache_ttl', 'N/A')}s")
                
                # Display RAG stats
                rag_stats = stats.get("rag", {})
                if "error" not in rag_stats:
                    click.echo(f"   📚 RAG System:")
                    click.echo(f"      Documents: {rag_stats.get('documents', {}).get('total_files', 0)}")
                    click.echo(f"      Embeddings: {rag_stats.get('embeddings', {}).get('total_documents', 0)}")
            else:
                click.echo(f"❌ Failed to get metrics: {stats['error']}", err=True)
                sys.exit(1)
        
        elif monitor:
            click.echo("📊 Starting real-time monitoring...")
            click.echo("   Press Ctrl+C to stop")
            
            try:
                import time
                while True:
                    # Get current stats
                    api_key = os.getenv("GEMINI_API_KEY")
                    if api_key:
                        orchestrator = Orchestrator(api_key=api_key)
                        stats = orchestrator.get_system_stats()
                        
                        if "error" not in stats:
                            cache_stats = stats.get("cache", {})
                            click.echo(f"\r💾 Cache: {cache_stats.get('response_cache_size', 0)} responses, {cache_stats.get('context_cache_size', 0)} contexts", nl=False)
                    
                    time.sleep(5)
            
            except KeyboardInterrupt:
                click.echo("\n✅ Monitoring stopped")
        
        elif clear_logs:
            if click.confirm("⚠️  Are you sure you want to clear all log files?"):
                log_dir = Path("logs")
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        log_file.unlink()
                    click.echo("✅ Log files cleared")
                else:
                    click.echo("ℹ️  No log directory found")
            else:
                click.echo("❌ Operation cancelled")
        
        else:
            click.echo("❌ Please specify an action: --logs, --metrics, --monitor, or --clear-logs", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Monitor command failed: {str(e)}", err=True)
        sys.exit(1)


@click.command()
@click.option('--config', '-c', is_flag=True, help='Show current configuration')
@click.option('--validate', '-v', is_flag=True, help='Validate configuration')
@click.option('--reset', '-r', is_flag=True, help='Reset to default configuration')
@click.pass_context
def config_command(ctx, config, validate, reset):
    """
    Manage MIRAGE system configuration.
    
    Examples:
        mirage config --config      # Show current configuration
        mirage config --validate    # Validate configuration
        mirage config --reset       # Reset to defaults
    """
    try:
        if config:
            click.echo("⚙️  MIRAGE Configuration:")
            
            # Environment variables
            click.echo(f"   🔑 API Key: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not set'}")
            click.echo(f"   🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
            click.echo(f"   📊 Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
            click.echo(f"   🐛 Debug: {os.getenv('DEBUG', 'false')}")
            
            # RAG configuration
            click.echo(f"   📚 RAG Chunk Size: {os.getenv('RAG_CHUNK_SIZE', '1000')}")
            click.echo(f"   🔢 RAG Max Results: {os.getenv('RAG_MAX_RESULTS', '5')}")
            click.echo(f"   🎯 Similarity Threshold: {os.getenv('RAG_SIMILARITY_THRESHOLD', '0.7')}")
            
            # Agent configuration
            click.echo(f"   🔄 Max Iterations: {os.getenv('MAX_ITERATIONS', '3')}")
            click.echo(f"   ⏱️  Cache TTL: {os.getenv('CACHE_TTL_SECONDS', '3600')}s")
            click.echo(f"   👨‍⚕️ Human Loop: {os.getenv('ENABLE_HUMAN_IN_LOOP', 'true')}")
        
        elif validate:
            click.echo("✅ Validating MIRAGE configuration...")
            
            validation_results = []
            
            # Check API key
            if os.getenv("GEMINI_API_KEY"):
                validation_results.append(("API Key", "✅ Set"))
            else:
                validation_results.append(("API Key", "❌ Not set"))
            
            # Check data directories
            data_dirs = ["data/raw_documents", "data/processed", "data/embeddings", "logs"]
            for dir_path in data_dirs:
                if Path(dir_path).exists():
                    validation_results.append((f"Directory {dir_path}", "✅ Exists"))
                else:
                    validation_results.append((f"Directory {dir_path}", "❌ Missing"))
            
            # Check configuration file
            env_file = Path(".env")
            if env_file.exists():
                validation_results.append(("Configuration file", "✅ Found"))
            else:
                validation_results.append(("Configuration file", "⚠️  Not found (using defaults)"))
            
            # Display results
            all_valid = True
            for item, status in validation_results:
                click.echo(f"   {status} {item}")
                if "❌" in status:
                    all_valid = False
            
            if all_valid:
                click.echo("\n✅ Configuration validation passed!")
            else:
                click.echo("\n❌ Configuration validation failed!")
                sys.exit(1)
        
        elif reset:
            if click.confirm("⚠️  Are you sure you want to reset configuration to defaults?"):
                click.echo("🔄 Resetting configuration...")
                
                # Clear cache
                try:
                    api_key = os.getenv("GEMINI_API_KEY")
                    if api_key:
                        orchestrator = Orchestrator(api_key=api_key)
                        orchestrator.clear_cache()
                        click.echo("   ✅ Cache cleared")
                except Exception as e:
                    click.echo(f"   ⚠️  Cache clear failed: {str(e)}")
                
                # Reset log files
                log_dir = Path("logs")
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        log_file.unlink()
                    click.echo("   ✅ Log files cleared")
                
                click.echo("✅ Configuration reset completed")
            else:
                click.echo("❌ Operation cancelled")
        
        else:
            click.echo("❌ Please specify an action: --config, --validate, or --reset", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Config command failed: {str(e)}", err=True)
        sys.exit(1)

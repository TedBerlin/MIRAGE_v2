"""
Main CLI entry point for MIRAGE v2.

Provides the main command-line interface using Click.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import click
import structlog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.orchestrator import Orchestrator
from rag.rag_engine import RAGEngine
from .commands import rag_command, agents_command, monitor_command, config_command

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@click.group()
@click.version_option(version="1.0.0", prog_name="MIRAGE v2")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), help='Set log level')
@click.pass_context
def cli(ctx, verbose, log_level):
    """
    MIRAGE v2 - Medical Intelligence Research Assistant for Generative Enhancement
    
    A secure, ethical, and robust AI system for pharmaceutical R&D.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Store options in context
    ctx.obj['verbose'] = verbose
    ctx.obj['log_level'] = log_level
    
    # Configure logging level
    if verbose:
        ctx.obj['log_level'] = 'DEBUG'
    
    # Set up logging
    import logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if verbose:
        click.echo("🔍 Verbose mode enabled")
        click.echo(f"📊 Log level: {log_level}")


@cli.command()
@click.argument('question', type=str)
@click.option('--human', '-h', is_flag=True, help='Enable human-in-the-loop validation')
@click.option('--format', '-f', 'output_format', default='text', type=click.Choice(['text', 'json']), help='Output format')
@click.option('--language', '-l', default='en', type=click.Choice(['en', 'fr', 'es', 'de']), help='Response language')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed processing information')
@click.pass_context
def query(ctx, question, human, output_format, language, verbose):
    """
    Query the MIRAGE system with a pharmaceutical research question.
    
    QUESTION: Your research question about pharmaceuticals, drugs, or medical topics.
    
    Examples:
        mirage query "What are the side effects of this medication?"
        mirage query "How should this drug be administered?" --human
        mirage query "What is the mechanism of action?" --format json --language fr
    """
    try:
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo("❌ Error: GEMINI_API_KEY not found in environment variables", err=True)
            click.echo("   Please set your Gemini API key: export GEMINI_API_KEY=your_key_here", err=True)
            sys.exit(1)
        
        # Initialize orchestrator
        if verbose:
            click.echo("🚀 Initializing MIRAGE orchestrator...")
        
        orchestrator = Orchestrator(
            api_key=api_key,
            enable_human_loop=human,
            max_iterations=3
        )
        
        # Process query
        if verbose:
            click.echo(f"🔍 Processing query: {question}")
            click.echo(f"🌍 Language: {language}")
            click.echo(f"👨‍⚕️ Human loop: {'Enabled' if human else 'Disabled'}")
        
        result = orchestrator.process_query(
            query=question,
            enable_human_loop=human,
            target_language=language
        )
        
        # Display results
        if result["success"]:
            if output_format == "json":
                import json
                click.echo(json.dumps(result, indent=2))
            else:
                _display_text_result(result, verbose)
        else:
            click.echo(f"❌ Query failed: {result.get('error', 'Unknown error')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def health(ctx):
    """
    Check the health status of the MIRAGE system.
    
    Performs comprehensive health checks on all system components.
    """
    try:
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo("❌ Error: GEMINI_API_KEY not found in environment variables", err=True)
            sys.exit(1)
        
        # Initialize orchestrator
        orchestrator = Orchestrator(api_key=api_key)
        
        # Perform health check
        click.echo("🏥 Performing MIRAGE system health check...")
        health_status = orchestrator.health_check()
        
        # Display health status
        _display_health_status(health_status)
        
        # Exit with appropriate code
        if health_status["overall"] == "healthy":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Health check failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query_id', type=str)
@click.option('--format', '-f', 'output_format', default='text', type=click.Choice(['text', 'json']), help='Output format')
@click.pass_context
def audit(ctx, query_id, output_format):
    """
    Audit a specific query by ID to retrieve detailed processing information.
    
    QUERY_ID: The unique identifier of the query to audit.
    
    Examples:
        mirage audit abc123def456
        mirage audit abc123def456 --format json
    """
    try:
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo("❌ Error: GEMINI_API_KEY not found in environment variables", err=True)
            sys.exit(1)
        
        # Initialize orchestrator
        orchestrator = Orchestrator(api_key=api_key)
        
        # Get system stats (in a real implementation, this would query logs)
        click.echo(f"🔍 Auditing query: {query_id}")
        
        # For now, return system stats as audit information
        stats = orchestrator.get_system_stats()
        
        if output_format == "json":
            import json
            audit_result = {
                "query_id": query_id,
                "audit_timestamp": "2024-01-01T00:00:00Z",  # In real implementation, get from logs
                "system_stats": stats
            }
            click.echo(json.dumps(audit_result, indent=2))
        else:
            click.echo(f"📊 Audit Results for Query: {query_id}")
            click.echo(f"🕐 Audit Timestamp: 2024-01-01T00:00:00Z")
            click.echo(f"📈 System Status: {'Healthy' if 'error' not in stats else 'Issues detected'}")
            
    except Exception as e:
        click.echo(f"❌ Audit failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('questions_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for validation results')
@click.option('--format', '-f', 'output_format', default='text', type=click.Choice(['text', 'json', 'csv']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation information')
@click.pass_context
def validate(ctx, questions_file, output, output_format, verbose):
    """
    Validate the MIRAGE system on a batch of questions.
    
    QUESTIONS_FILE: Path to a text file containing questions (one per line).
    
    Examples:
        mirage validate questions.txt
        mirage validate questions.txt --output results.json --format json
        mirage validate questions.txt --output results.csv --format csv --verbose
    """
    try:
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo("❌ Error: GEMINI_API_KEY not found in environment variables", err=True)
            sys.exit(1)
        
        # Read questions file
        questions_path = Path(questions_file)
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions = [line.strip() for line in f if line.strip()]
        
        if not questions:
            click.echo("❌ No questions found in file", err=True)
            sys.exit(1)
        
        click.echo(f"📋 Loaded {len(questions)} questions from {questions_path}")
        
        # Initialize orchestrator
        orchestrator = Orchestrator(api_key=api_key)
        
        # Process questions
        results = []
        for i, question in enumerate(questions, 1):
            if verbose:
                click.echo(f"🔍 Processing question {i}/{len(questions)}: {question[:50]}...")
            
            result = orchestrator.process_query(question)
            results.append({
                "question": question,
                "success": result["success"],
                "processing_time": result.get("processing_time", 0),
                "iteration": result.get("iteration", 1),
                "consensus": result.get("consensus", "unknown"),
                "error": result.get("error") if not result["success"] else None
            })
        
        # Calculate statistics
        total_questions = len(results)
        successful_questions = sum(1 for r in results if r["success"])
        avg_processing_time = sum(r["processing_time"] for r in results) / total_questions
        success_rate = successful_questions / total_questions
        
        # Display results
        if output:
            _save_validation_results(results, output, output_format)
            click.echo(f"💾 Results saved to: {output}")
        else:
            _display_validation_results(results, output_format, verbose)
        
        # Display summary
        click.echo(f"\n📊 Validation Summary:")
        click.echo(f"   Total questions: {total_questions}")
        click.echo(f"   Successful: {successful_questions}")
        click.echo(f"   Success rate: {success_rate:.2%}")
        click.echo(f"   Average processing time: {avg_processing_time:.2f}s")
        
    except Exception as e:
        click.echo(f"❌ Validation failed: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


def _display_text_result(result, verbose):
    """Display query result in text format."""
    click.echo(f"\n🎯 Answer:")
    click.echo(f"{result['answer']}")
    
    if verbose:
        click.echo(f"\n📊 Processing Details:")
        click.echo(f"   Query ID: {result.get('query_hash', 'N/A')}")
        click.echo(f"   Processing time: {result.get('processing_time', 0):.2f}s")
        click.echo(f"   Iterations: {result.get('iteration', 1)}")
        click.echo(f"   Consensus: {result.get('consensus', 'unknown')}")
        
        if result.get('human_validation_required'):
            click.echo(f"   👨‍⚕️ Human validation: Required")
        
        if result.get('translated_response'):
            click.echo(f"   🌍 Translation: {result.get('target_language', 'unknown')}")


def _display_health_status(health_status):
    """Display system health status."""
    overall_status = health_status["overall"]
    status_emoji = "✅" if overall_status == "healthy" else "❌"
    
    click.echo(f"\n{status_emoji} Overall Status: {overall_status.upper()}")
    
    # Display component status
    click.echo(f"\n🔧 Component Status:")
    for component, status in health_status.items():
        if component != "overall" and component != "timestamp":
            if isinstance(status, str):
                status_emoji = "✅" if status == "healthy" else "❌"
                click.echo(f"   {status_emoji} {component}: {status}")
            elif isinstance(status, dict):
                click.echo(f"   📊 {component}:")
                for sub_component, sub_status in status.items():
                    sub_emoji = "✅" if sub_status == "healthy" else "❌"
                    click.echo(f"      {sub_emoji} {sub_component}: {sub_status}")


def _display_validation_results(results, output_format, verbose):
    """Display validation results."""
    if output_format == "json":
        import json
        click.echo(json.dumps(results, indent=2))
    elif output_format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["question", "success", "processing_time", "iteration", "consensus", "error"])
        writer.writeheader()
        writer.writerows(results)
        click.echo(output.getvalue())
    else:
        for i, result in enumerate(results, 1):
            status = "✅" if result["success"] else "❌"
            click.echo(f"{status} Q{i}: {result['question'][:50]}...")
            if verbose and not result["success"]:
                click.echo(f"   Error: {result['error']}")


def _save_validation_results(results, output_path, output_format):
    """Save validation results to file."""
    output_path = Path(output_path)
    
    if output_format == "json":
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    elif output_format == "csv":
        import csv
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["question", "success", "processing_time", "iteration", "consensus", "error"])
            writer.writeheader()
            writer.writerows(results)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, result in enumerate(results, 1):
                status = "PASS" if result["success"] else "FAIL"
                f.write(f"{status}: {result['question']}\n")
                if not result["success"]:
                    f.write(f"  Error: {result['error']}\n")


# Add specialized commands to CLI
try:
    from .commands import rag_command, agents_command, monitor_command, config_command
    cli.add_command(rag_command, name='rag')
    cli.add_command(agents_command, name='agents')
    cli.add_command(monitor_command, name='monitor')
    cli.add_command(config_command, name='config')
except ImportError:
    # Commands will be added when available
    pass


if __name__ == '__main__':
    cli()

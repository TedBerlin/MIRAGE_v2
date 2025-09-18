"""
Workflow Manager for MIRAGE v2.

Manages complex workflows and state transitions in the orchestration process.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class WorkflowState(Enum):
    """Workflow states for tracking process progression."""
    INITIALIZED = "initialized"
    CONTEXT_RETRIEVED = "context_retrieved"
    RESPONSE_GENERATED = "response_generated"
    RESPONSE_VERIFIED = "response_verified"
    CONSENSUS_REACHED = "consensus_reached"
    HUMAN_VALIDATION = "human_validation"
    RESPONSE_REFORMED = "response_reformed"
    TRANSLATION_COMPLETED = "translation_completed"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowManager:
    """Manages workflow states and transitions for orchestration."""
    
    def __init__(self):
        self.active_workflows = {}
        self.workflow_history = []
        self.state_transitions = {
            WorkflowState.INITIALIZED: [WorkflowState.CONTEXT_RETRIEVED, WorkflowState.FAILED],
            WorkflowState.CONTEXT_RETRIEVED: [WorkflowState.RESPONSE_GENERATED, WorkflowState.FAILED],
            WorkflowState.RESPONSE_GENERATED: [WorkflowState.RESPONSE_VERIFIED, WorkflowState.FAILED],
            WorkflowState.RESPONSE_VERIFIED: [
                WorkflowState.CONSENSUS_REACHED,
                WorkflowState.RESPONSE_REFORMED,
                WorkflowState.HUMAN_VALIDATION,
                WorkflowState.FAILED
            ],
            WorkflowState.CONSENSUS_REACHED: [
                WorkflowState.TRANSLATION_COMPLETED,
                WorkflowState.HUMAN_VALIDATION,
                WorkflowState.COMPLETED
            ],
            WorkflowState.RESPONSE_REFORMED: [
                WorkflowState.RESPONSE_VERIFIED,
                WorkflowState.CONSENSUS_REACHED,
                WorkflowState.FAILED
            ],
            WorkflowState.HUMAN_VALIDATION: [
                WorkflowState.TRANSLATION_COMPLETED,
                WorkflowState.COMPLETED,
                WorkflowState.FAILED
            ],
            WorkflowState.TRANSLATION_COMPLETED: [WorkflowState.COMPLETED],
            WorkflowState.COMPLETED: [],
            WorkflowState.FAILED: []
        }
        
        logger.info("WorkflowManager initialized")
    
    def create_workflow(self, workflow_id: str, query: str) -> Dict[str, Any]:
        """
        Create a new workflow instance.
        
        Args:
            workflow_id: Unique identifier for the workflow
            query: The query being processed
            
        Returns:
            Workflow instance
        """
        workflow = {
            "id": workflow_id,
            "query": query,
            "state": WorkflowState.INITIALIZED,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "start_time": time.time(),
            "steps": [],
            "metadata": {
                "iterations": 0,
                "retries": 0,
                "human_interventions": 0
            }
        }
        
        self.active_workflows[workflow_id] = workflow
        self._add_step(workflow_id, "workflow_created", "Workflow initialized")
        
        logger.info("Workflow created", workflow_id=workflow_id, query=query[:100])
        return workflow
    
    def transition_state(
        self,
        workflow_id: str,
        new_state: WorkflowState,
        step_name: str,
        step_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Transition workflow to a new state.
        
        Args:
            workflow_id: Workflow identifier
            new_state: Target state
            step_name: Name of the step being executed
            step_data: Additional data for the step
            
        Returns:
            True if transition successful, False otherwise
        """
        if workflow_id not in self.active_workflows:
            logger.error("Workflow not found", workflow_id=workflow_id)
            return False
        
        workflow = self.active_workflows[workflow_id]
        current_state = workflow["state"]
        
        # Check if transition is valid
        if new_state not in self.state_transitions.get(current_state, []):
            logger.error(
                "Invalid state transition",
                workflow_id=workflow_id,
                current_state=current_state.value,
                new_state=new_state.value
            )
            return False
        
        # Update workflow
        workflow["state"] = new_state
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Add step
        self._add_step(workflow_id, step_name, f"Transitioned to {new_state.value}", step_data)
        
        # Update metadata based on state
        self._update_metadata(workflow_id, new_state)
        
        logger.info(
            "State transition completed",
            workflow_id=workflow_id,
            from_state=current_state.value,
            to_state=new_state.value,
            step=step_name
        )
        
        return True
    
    def _add_step(
        self,
        workflow_id: str,
        step_name: str,
        description: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Add a step to the workflow."""
        step = {
            "name": step_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        self.active_workflows[workflow_id]["steps"].append(step)
    
    def _update_metadata(self, workflow_id: str, state: WorkflowState):
        """Update workflow metadata based on state."""
        metadata = self.active_workflows[workflow_id]["metadata"]
        
        if state == WorkflowState.RESPONSE_REFORMED:
            metadata["iterations"] += 1
        elif state == WorkflowState.HUMAN_VALIDATION:
            metadata["human_interventions"] += 1
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID."""
        return self.active_workflows.get(workflow_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status summary."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        return {
            "id": workflow["id"],
            "state": workflow["state"].value,
            "created_at": workflow["created_at"],
            "updated_at": workflow["updated_at"],
            "duration": time.time() - workflow["start_time"],
            "steps_count": len(workflow["steps"]),
            "metadata": workflow["metadata"]
        }
    
    def complete_workflow(self, workflow_id: str, final_result: Dict[str, Any]) -> bool:
        """
        Complete a workflow and move to history.
        
        Args:
            workflow_id: Workflow identifier
            final_result: Final result of the workflow
            
        Returns:
            True if successful, False otherwise
        """
        if workflow_id not in self.active_workflows:
            logger.error("Workflow not found for completion", workflow_id=workflow_id)
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        # Update final state
        workflow["state"] = WorkflowState.COMPLETED
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["completed_at"] = datetime.now().isoformat()
        workflow["total_duration"] = time.time() - workflow["start_time"]
        workflow["final_result"] = final_result
        
        # Move to history
        self.workflow_history.append(workflow)
        del self.active_workflows[workflow_id]
        
        logger.info(
            "Workflow completed",
            workflow_id=workflow_id,
            duration=workflow["total_duration"],
            steps=len(workflow["steps"])
        )
        
        return True
    
    def fail_workflow(self, workflow_id: str, error: str) -> bool:
        """
        Mark workflow as failed.
        
        Args:
            workflow_id: Workflow identifier
            error: Error message
            
        Returns:
            True if successful, False otherwise
        """
        if workflow_id not in self.active_workflows:
            logger.error("Workflow not found for failure", workflow_id=workflow_id)
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        # Update final state
        workflow["state"] = WorkflowState.FAILED
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["failed_at"] = datetime.now().isoformat()
        workflow["total_duration"] = time.time() - workflow["start_time"]
        workflow["error"] = error
        
        # Move to history
        self.workflow_history.append(workflow)
        del self.active_workflows[workflow_id]
        
        logger.error(
            "Workflow failed",
            workflow_id=workflow_id,
            duration=workflow["total_duration"],
            error=error
        )
        
        return True
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows."""
        return list(self.active_workflows.values())
    
    def get_workflow_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflow history."""
        return self.workflow_history[-limit:]
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        total_workflows = len(self.workflow_history) + len(self.active_workflows)
        
        if total_workflows == 0:
            return {
                "total_workflows": 0,
                "active_workflows": 0,
                "completed_workflows": 0,
                "failed_workflows": 0,
                "average_duration": 0.0,
                "success_rate": 0.0
            }
        
        # Count by state
        completed = sum(1 for w in self.workflow_history if w["state"] == WorkflowState.COMPLETED)
        failed = sum(1 for w in self.workflow_history if w["state"] == WorkflowState.FAILED)
        
        # Calculate average duration
        completed_workflows = [w for w in self.workflow_history if w["state"] == WorkflowState.COMPLETED]
        avg_duration = (
            sum(w["total_duration"] for w in completed_workflows) / len(completed_workflows)
            if completed_workflows else 0.0
        )
        
        return {
            "total_workflows": total_workflows,
            "active_workflows": len(self.active_workflows),
            "completed_workflows": completed,
            "failed_workflows": failed,
            "average_duration": avg_duration,
            "success_rate": completed / total_workflows if total_workflows > 0 else 0.0
        }
    
    def cleanup_old_workflows(self, max_age_hours: int = 24):
        """Clean up old workflows from history."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        original_count = len(self.workflow_history)
        self.workflow_history = [
            w for w in self.workflow_history
            if w.get("start_time", 0) > cutoff_time
        ]
        
        removed_count = original_count - len(self.workflow_history)
        
        if removed_count > 0:
            logger.info("Cleaned up old workflows", removed_count=removed_count)
        
        return removed_count

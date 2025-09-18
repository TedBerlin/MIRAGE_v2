"""
Consensus Manager for MIRAGE v2.

Manages consensus logic and decision-making in the orchestration process.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class ConsensusLevel(Enum):
    """Consensus levels for decision making."""
    HIGH = "high"          # > 0.8 confidence
    MEDIUM = "medium"      # 0.5 - 0.8 confidence
    LOW = "low"           # < 0.5 confidence
    REJECTED = "rejected"  # Explicit rejection


class ConsensusDecision(Enum):
    """Consensus decisions."""
    APPROVE = "approve"
    REFORM = "reform"
    REJECT = "reject"
    HUMAN_REVIEW = "human_review"


class ConsensusManager:
    """Manages consensus logic and decision-making."""
    
    def __init__(
        self,
        high_confidence_threshold: float = 0.8,
        medium_confidence_threshold: float = 0.5,
        max_iterations: int = 3,
        human_review_threshold: float = 0.3
    ):
        self.high_confidence_threshold = high_confidence_threshold
        self.medium_confidence_threshold = medium_confidence_threshold
        self.max_iterations = max_iterations
        self.human_review_threshold = human_review_threshold
        
        # Consensus history
        self.consensus_history = []
        
        logger.info(
            "ConsensusManager initialized",
            high_threshold=high_confidence_threshold,
            medium_threshold=medium_confidence_threshold,
            max_iterations=max_iterations
        )
    
    def evaluate_consensus(
        self,
        verification_result: Dict[str, Any],
        iteration: int = 1,
        enable_human_loop: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate consensus based on verification results.
        
        Args:
            verification_result: Result from verifier agent
            iteration: Current iteration number
            enable_human_loop: Whether human loop is enabled
            
        Returns:
            Consensus evaluation result
        """
        try:
            vote = verification_result.get("vote")
            confidence = verification_result.get("confidence", 0.0)
            issues_found = verification_result.get("issues_found", [])
            safety_concerns = verification_result.get("safety_concerns", [])
            
            # Determine consensus level
            consensus_level = self._determine_consensus_level(vote, confidence)
            
            # Make consensus decision
            decision = self._make_consensus_decision(
                consensus_level, vote, confidence, issues_found, 
                safety_concerns, iteration, enable_human_loop
            )
            
            # Create consensus result
            consensus_result = {
                "consensus_level": consensus_level.value,
                "decision": decision.value,
                "vote": vote,
                "confidence": confidence,
                "iteration": iteration,
                "issues_found": issues_found,
                "safety_concerns": safety_concerns,
                "reasoning": self._generate_reasoning(
                    consensus_level, decision, vote, confidence, issues_found, safety_concerns
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            # Record in history
            self.consensus_history.append(consensus_result)
            
            logger.info(
                "Consensus evaluated",
                consensus_level=consensus_level.value,
                decision=decision.value,
                vote=vote,
                confidence=confidence,
                iteration=iteration
            )
            
            return consensus_result
            
        except Exception as e:
            logger.error("Consensus evaluation failed", error=str(e))
            return {
                "consensus_level": ConsensusLevel.REJECTED.value,
                "decision": ConsensusDecision.REJECT.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _determine_consensus_level(self, vote: str, confidence: float) -> ConsensusLevel:
        """Determine consensus level based on vote and confidence."""
        if vote == "NON":
            return ConsensusLevel.REJECTED
        
        if vote == "OUI":
            if confidence >= self.high_confidence_threshold:
                return ConsensusLevel.HIGH
            elif confidence >= self.medium_confidence_threshold:
                return ConsensusLevel.MEDIUM
            else:
                return ConsensusLevel.LOW
        
        # Unknown vote
        return ConsensusLevel.LOW
    
    def _make_consensus_decision(
        self,
        consensus_level: ConsensusLevel,
        vote: str,
        confidence: float,
        issues_found: List[str],
        safety_concerns: List[str],
        iteration: int,
        enable_human_loop: bool
    ) -> ConsensusDecision:
        """Make consensus decision based on all factors."""
        
        # Safety concerns always require human review
        if safety_concerns and enable_human_loop:
            return ConsensusDecision.HUMAN_REVIEW
        
        # High confidence approval
        if consensus_level == ConsensusLevel.HIGH:
            return ConsensusDecision.APPROVE
        
        # Rejected responses
        if consensus_level == ConsensusLevel.REJECTED:
            if iteration < self.max_iterations:
                return ConsensusDecision.REFORM
            else:
                return ConsensusDecision.REJECT
        
        # Medium confidence
        if consensus_level == ConsensusLevel.MEDIUM:
            if issues_found and iteration < self.max_iterations:
                return ConsensusDecision.REFORM
            elif enable_human_loop and confidence < 0.7:
                return ConsensusDecision.HUMAN_REVIEW
            else:
                return ConsensusDecision.APPROVE
        
        # Low confidence
        if consensus_level == ConsensusLevel.LOW:
            if iteration < self.max_iterations:
                return ConsensusDecision.REFORM
            elif enable_human_loop:
                return ConsensusDecision.HUMAN_REVIEW
            else:
                return ConsensusDecision.REJECT
        
        # Default fallback
        return ConsensusDecision.HUMAN_REVIEW
    
    def _generate_reasoning(
        self,
        consensus_level: ConsensusLevel,
        decision: ConsensusDecision,
        vote: str,
        confidence: float,
        issues_found: List[str],
        safety_concerns: List[str]
    ) -> str:
        """Generate human-readable reasoning for the consensus decision."""
        reasoning_parts = []
        
        # Base reasoning
        if consensus_level == ConsensusLevel.HIGH:
            reasoning_parts.append(f"High confidence approval (confidence: {confidence:.2f})")
        elif consensus_level == ConsensusLevel.MEDIUM:
            reasoning_parts.append(f"Medium confidence approval (confidence: {confidence:.2f})")
        elif consensus_level == ConsensusLevel.LOW:
            reasoning_parts.append(f"Low confidence (confidence: {confidence:.2f})")
        elif consensus_level == ConsensusLevel.REJECTED:
            reasoning_parts.append("Response rejected by verifier")
        
        # Decision reasoning
        if decision == ConsensusDecision.APPROVE:
            reasoning_parts.append("Decision: Approve response")
        elif decision == ConsensusDecision.REFORM:
            reasoning_parts.append("Decision: Reform response for improvement")
        elif decision == ConsensusDecision.REJECT:
            reasoning_parts.append("Decision: Reject response")
        elif decision == ConsensusDecision.HUMAN_REVIEW:
            reasoning_parts.append("Decision: Require human review")
        
        # Issues and concerns
        if issues_found:
            reasoning_parts.append(f"Issues found: {', '.join(issues_found)}")
        
        if safety_concerns:
            reasoning_parts.append(f"Safety concerns: {', '.join(safety_concerns)}")
        
        return ". ".join(reasoning_parts) + "."
    
    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get consensus statistics."""
        if not self.consensus_history:
            return {
                "total_evaluations": 0,
                "consensus_levels": {},
                "decisions": {},
                "average_confidence": 0.0,
                "success_rate": 0.0
            }
        
        # Count consensus levels
        consensus_levels = {}
        for result in self.consensus_history:
            level = result["consensus_level"]
            consensus_levels[level] = consensus_levels.get(level, 0) + 1
        
        # Count decisions
        decisions = {}
        for result in self.consensus_history:
            decision = result["decision"]
            decisions[decision] = decisions.get(decision, 0) + 1
        
        # Calculate average confidence
        confidences = [r["confidence"] for r in self.consensus_history if "confidence" in r]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Calculate success rate (approve + human_review)
        successful_decisions = decisions.get("approve", 0) + decisions.get("human_review", 0)
        success_rate = successful_decisions / len(self.consensus_history)
        
        return {
            "total_evaluations": len(self.consensus_history),
            "consensus_levels": consensus_levels,
            "decisions": decisions,
            "average_confidence": avg_confidence,
            "success_rate": success_rate
        }
    
    def get_recent_consensus(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent consensus evaluations."""
        return self.consensus_history[-limit:]
    
    def analyze_consensus_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in consensus decisions."""
        if not self.consensus_history:
            return {"error": "No consensus history available"}
        
        # Analyze by iteration
        iteration_analysis = {}
        for result in self.consensus_history:
            iteration = result["iteration"]
            if iteration not in iteration_analysis:
                iteration_analysis[iteration] = {
                    "count": 0,
                    "approve": 0,
                    "reform": 0,
                    "reject": 0,
                    "human_review": 0,
                    "avg_confidence": 0.0
                }
            
            iteration_analysis[iteration]["count"] += 1
            decision = result["decision"]
            iteration_analysis[iteration][decision] += 1
        
        # Calculate average confidence by iteration
        for iteration in iteration_analysis:
            iteration_results = [r for r in self.consensus_history if r["iteration"] == iteration]
            confidences = [r["confidence"] for r in iteration_results if "confidence" in r]
            iteration_analysis[iteration]["avg_confidence"] = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )
        
        # Analyze issue patterns
        issue_patterns = {}
        for result in self.consensus_history:
            for issue in result.get("issues_found", []):
                issue_patterns[issue] = issue_patterns.get(issue, 0) + 1
        
        # Analyze safety concern patterns
        safety_patterns = {}
        for result in self.consensus_history:
            for concern in result.get("safety_concerns", []):
                safety_patterns[concern] = safety_patterns.get(concern, 0) + 1
        
        return {
            "iteration_analysis": iteration_analysis,
            "issue_patterns": issue_patterns,
            "safety_patterns": safety_patterns,
            "total_evaluations": len(self.consensus_history)
        }
    
    def should_retry(self, iteration: int, consensus_result: Dict[str, Any]) -> bool:
        """Determine if a retry should be attempted."""
        decision = consensus_result.get("decision")
        consensus_level = consensus_result.get("consensus_level")
        
        # Don't retry if already at max iterations
        if iteration >= self.max_iterations:
            return False
        
        # Retry for reform decisions
        if decision == "reform":
            return True
        
        # Don't retry for approvals or human reviews
        if decision in ["approve", "human_review"]:
            return False
        
        # Retry for low confidence if not rejected
        if consensus_level == "low" and decision != "reject":
            return True
        
        return False
    
    def cleanup_old_history(self, max_age_hours: int = 24):
        """Clean up old consensus history."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        original_count = len(self.consensus_history)
        self.consensus_history = [
            r for r in self.consensus_history
            if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff_time
        ]
        
        removed_count = original_count - len(self.consensus_history)
        
        if removed_count > 0:
            logger.info("Cleaned up old consensus history", removed_count=removed_count)
        
        return removed_count

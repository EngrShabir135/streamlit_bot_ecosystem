from .base_agent import BaseAgent
from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid

class PlannerBot(BaseAgent):
    def __init__(self):
        super().__init__("planner_bot", 10)
        self.daily_plans = []
        self.weekly_plans = []
        self.task_allocations = []
        
    async def process_message(self, message: Dict) -> Dict:
        return {"status": "processed", "planner_note": "Message handled by Planner"}
    
    async def perform_task(self, task: Dict) -> Dict:
        return await self.create_plan(task)
    
    async def create_plan(self, task_evaluation: Dict) -> Dict:
        plan = {
            "plan_id": str(uuid.uuid4()),
            "based_on_evaluation": task_evaluation.get('task_id'),
            "priority": task_evaluation.get('priority'),
            "allocated_resources": self._allocate_resources(task_evaluation),
            "timeline": self._create_timeline(task_evaluation),
            "subtasks": self._breakdown_subtasks(task_evaluation),
            "dependencies": self._identify_dependencies(task_evaluation),
            "risk_assessment": self._assess_risks(task_evaluation),
            "created_at": datetime.now().isoformat()
        }
        
        sub_agent_results = await self.distribute_to_sub_agents({
            "type": "planning_assistance",
            "plan": plan,
            "evaluation": task_evaluation
        })
        
        plan["sub_agent_contributions"] = sub_agent_results
        self.daily_plans.append(plan)
        
        return plan
    
    def _allocate_resources(self, evaluation: Dict) -> Dict:
        complexity = evaluation.get('complexity', 1)
        priority = evaluation.get('priority', 'medium')
        
        return {
            "sub_agents": min(10, max(2, complexity * 2)),
            "computation_power": complexity * 0.1,
            "time_allocation_hours": complexity * 0.5,
            "priority_level": priority
        }
    
    def _create_timeline(self, evaluation: Dict) -> Dict:
        complexity = evaluation.get('complexity', 1)
        
        return {
            "estimation_hours": complexity * 2,
            "milestones": [
                {"phase": "planning", "duration_hours": 0.5},
                {"phase": "execution", "duration_hours": complexity * 1.5},
                {"phase": "review", "duration_hours": 0.5}
            ],
            "deadline": (datetime.now() + timedelta(hours=complexity * 2)).isoformat()
        }
    
    def _breakdown_subtasks(self, evaluation: Dict) -> List[Dict]:
        complexity = evaluation.get('complexity', 1)
        num_subtasks = min(10, max(1, complexity))
        
        subtasks = []
        for i in range(num_subtasks):
            subtasks.append({
                "id": i + 1,
                "description": f"Subtask {i+1} for {evaluation.get('task_id', 'unknown')}",
                "estimated_duration_minutes": 30 * complexity / num_subtasks,
                "required_skills": ["execution"],
                "dependencies": [j for j in range(1, i)] if i > 0 else []
            })
        
        return subtasks
    
    def _identify_dependencies(self, evaluation: Dict) -> List[str]:
        return ["data_availability", "resource_allocation", "approval_process"]
    
    def _assess_risks(self, evaluation: Dict) -> Dict:
        complexity = evaluation.get('complexity', 1)
        
        return {
            "high_risk": complexity >= 8,
            "medium_risk": 5 <= complexity < 8,
            "low_risk": complexity < 5,
            "mitigation_strategies": [
                "Allocate backup resources",
                "Implement progress monitoring",
                "Prepare contingency plans"
            ]
        }
    
    def get_performance_metrics(self) -> Dict:
        return {
            "plans_created": len(self.daily_plans),
            "allocation_efficiency": 0.89,
            "timeline_accuracy": 0.85,
            "resource_utilization": 0.91
        }
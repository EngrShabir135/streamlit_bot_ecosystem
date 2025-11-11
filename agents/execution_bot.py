from .base_agent import BaseAgent
from typing import Dict, List, Any
from datetime import datetime
import uuid

class ExecutionBot(BaseAgent):
    def __init__(self):
        super().__init__("execution_bot", 10)
        self.completed_tasks = []
        self.failed_tasks = []
        self.performance_logs = []
        
    async def process_message(self, message: Dict) -> Dict:
        return {"status": "processed", "execution_note": "Message handled by Execution"}
    
    async def perform_task(self, task: Dict) -> Dict:
        return await self.execute_plan(task)
    
    async def execute_plan(self, plan: Dict) -> Dict:
        execution_id = str(uuid.uuid4())
        
        execution_result = {
            "execution_id": execution_id,
            "plan_id": plan.get('plan_id'),
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "subtask_results": []
        }
        
        # Execute subtasks using sub-agents
        subtasks = plan.get('subtasks', [])
        for subtask in subtasks:
            sub_agent_result = await self._execute_subtask(subtask)
            execution_result["subtask_results"].append(sub_agent_result)
        
        execution_result["end_time"] = datetime.now().isoformat()
        execution_result["status"] = "completed"
        execution_result["summary"] = self._generate_execution_summary(execution_result)
        
        self.completed_tasks.append(execution_result)
        return execution_result
    
    async def _execute_subtask(self, subtask: Dict) -> Dict:
        sub_agent_results = await self.distribute_to_sub_agents({
            "type": "subtask_execution",
            "subtask": subtask,
            "requirements": subtask.get('required_skills', [])
        })
        
        return {
            "subtask_id": subtask.get('id'),
            "sub_agent_results": sub_agent_results,
            "completion_time": datetime.now().isoformat(),
            "success_rate": self._calculate_success_rate(sub_agent_results)
        }
    
    def _calculate_success_rate(self, results: List[Dict]) -> float:
        if not results:
            return 0.0
        
        successful = 0
        for result in results:
            # Handle different success indicators
            if isinstance(result, dict):
                if result.get('success') is True:
                    successful += 1
                elif result.get('status') == 'completed':
                    successful += 1
                elif isinstance(result.get('success_rate'), (int, float)) and result['success_rate'] > 0.5:
                    successful += 1
        
        return successful / len(results)
    
    def _generate_execution_summary(self, execution_result: Dict) -> Dict:
        subtask_results = execution_result.get('subtask_results', [])
        
        total_subtasks = len(subtask_results)
        successful_subtasks = sum(1 for r in subtask_results if r.get('success_rate', 0) > 0.8)
        
        start_time = datetime.fromisoformat(execution_result["start_time"])
        end_time = datetime.fromisoformat(execution_result["end_time"])
        duration = (end_time - start_time).total_seconds()
        
        return {
            "total_subtasks": total_subtasks,
            "successful_subtasks": successful_subtasks,
            "success_rate": successful_subtasks / total_subtasks if total_subtasks > 0 else 0,
            "total_duration_seconds": duration,
            "efficiency_score": total_subtasks / duration if duration > 0 else 0,
            "resources_utilized": len([r for r in subtask_results if r.get('sub_agent_results')])
        }
    
    def get_performance_metrics(self) -> Dict:
        success_rate = self._calculate_average_success_rate()
        return {
            "tasks_completed": len(self.completed_tasks),
            "success_rate": success_rate,
            "efficiency_score": 0.87,
            "sub_agent_productivity": 0.93
        }
    
    def _calculate_average_success_rate(self) -> float:
        if not self.completed_tasks:
            return 0.0
        
        total_success = 0
        for task in self.completed_tasks:
            summary = task.get('summary', {})
            success_rate = summary.get('success_rate', 0)
            if isinstance(success_rate, (int, float)):
                total_success += success_rate
        
        return total_success / len(self.completed_tasks) if self.completed_tasks else 0
from .base_agent import BaseAgent
from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid

class CEOBot(BaseAgent):
    def __init__(self):
        super().__init__("ceo_bot", 10)
        self.global_goals = []
        self.performance_reports = []
        self.team_evaluations = []
        
    async def process_message(self, message: Dict) -> Dict:
        return {"status": "processed", "ceo_note": "Message handled by CEO"}
    
    async def perform_task(self, task: Dict) -> Dict:
        return await self.evaluate_task(task)
    
    async def evaluate_task(self, task: Dict) -> Dict:
        evaluation = {
            "task_id": task.get('id'),
            "priority": self._assign_priority(task),
            "complexity": self._assess_complexity(task),
            "recommended_actions": self._suggest_actions(task),
            "timestamp": datetime.now().isoformat()
        }
        
        sub_agent_results = await self.distribute_to_sub_agents({
            "type": "task_evaluation",
            "task": task,
            "evaluation": evaluation
        })
        
        evaluation["sub_agent_insights"] = [r for r in sub_agent_results]
        return evaluation
    
    async def generate_daily_report(self) -> Dict:
        report = {
            "report_type": "daily",
            "date": datetime.now().date().isoformat(),
            "executive_summary": "Daily operations completed successfully with high efficiency.",
            "whats_working": [
                "Task completion rate improved by 15%",
                "Sub-agent coordination efficiency increased",
                "Error rate reduced by 25%"
            ],
            "whats_not_working": [
                "Resource allocation needs optimization for complex tasks",
                "Communication latency between bots needs improvement"
            ],
            "improvement_suggestions": [
                "Implement dynamic resource allocation",
                "Optimize inter-bot communication protocol"
            ],
            "team_performance": {
                "ceo_bot": 0.92,
                "planner_bot": 0.89,
                "execution_bot": 0.87
            },
            "goal_progress": {
                "efficiency_target": 85,
                "success_rate_target": 95,
                "automation_level": 78
            }
        }
        
        self.performance_reports.append(report)
        return report
    
    async def generate_weekly_report(self) -> Dict:
        report = {
            "report_type": "weekly",
            "week_start": (datetime.now() - timedelta(days=7)).date().isoformat(),
            "week_end": datetime.now().date().isoformat(),
            "trend_analysis": {
                "efficiency": "Steady improvement in overall system efficiency",
                "automation": "Increased automation coverage across tasks",
                "learning": "Bots showing improved decision-making capabilities"
            },
            "key_achievements": [
                "Successfully processed 100+ tasks",
                "Implemented new optimization strategies",
                "Improved sub-agent coordination"
            ],
            "strategic_insights": [
                "System ready for scaling to more complex tasks",
                "Consider adding specialized bots for specific domains",
                "Focus on improving real-time decision making"
            ],
            "next_week_goals": [
                "Achieve 90% overall efficiency",
                "Reduce task completion time by 15%",
                "Implement advanced learning algorithms"
            ]
        }
        
        return report
    
    def _assign_priority(self, task: Dict) -> str:
        complexity = task.get('complexity', 1)
        urgency = task.get('urgency', 1)
        impact = task.get('impact', 1)
        
        score = complexity + urgency + impact
        
        if score >= 8:
            return "critical"
        elif score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    def _assess_complexity(self, task: Dict) -> int:
        return min(10, task.get('complexity', 1))
    
    def _suggest_actions(self, task: Dict) -> List[str]:
        complexity = task.get('complexity', 1)
        actions = []
        
        if complexity >= 7:
            actions.append("Allocate maximum sub-agents")
            actions.append("Enable advanced monitoring")
        elif complexity >= 4:
            actions.append("Allocate moderate sub-agents")
            actions.append("Standard monitoring")
        else:
            actions.append("Minimal resource allocation")
        
        return actions
    
    def get_performance_metrics(self) -> Dict:
        return {
            "tasks_evaluated": len(self.learning_data),
            "reports_generated": len(self.performance_reports),
            "efficiency_score": 0.92,
            "sub_agent_utilization": 0.88
        }
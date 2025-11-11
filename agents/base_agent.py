from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime
import asyncio
import uuid

class BaseAgent(ABC):
    def __init__(self, name: str, sub_agents_count: int = 10):
        self.name = name
        self.sub_agents = [SubAgent(f"{name}_sub_{i}") for i in range(sub_agents_count)]
        self.message_queue = asyncio.Queue()
        self.performance_metrics = {}
        self.learning_data = []
        self.is_active = True
        
    @abstractmethod
    async def process_message(self, message: Dict) -> Dict:
        pass
    
    @abstractmethod
    async def perform_task(self, task: Dict) -> Dict:
        pass
    
    async def receive_message(self, message: Dict) -> Dict:
        return await self.process_message(message)
    
    async def distribute_to_sub_agents(self, task: Dict) -> List[Dict]:
        subtasks = self._break_down_task(task)
        results = []
        
        for i, subtask in enumerate(subtasks):
            if i < len(self.sub_agents):
                result = await self.sub_agents[i].perform_task(subtask)
                results.append(result)
        
        return results
    
    def _break_down_task(self, task: Dict) -> List[Dict]:
        num_subtasks = min(len(self.sub_agents), task.get('allocated_sub_agents', 3))
        return [task] * num_subtasks
    
    async def learn_from_results(self, results: List[Dict]):
        """FIXED: Handle both list of dicts and single dict properly"""
        if results:
            # Ensure we're working with a list of dictionaries
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                elif hasattr(result, '__dict__'):
                    valid_results.append(result.__dict__)
            
            self.learning_data.extend(valid_results)
            
            # Calculate success rate only if we have valid results
            if valid_results:
                success_count = 0
                for result in valid_results:
                    # Check for success in different possible formats
                    if result.get('success') is True:
                        success_count += 1
                    elif result.get('status') == 'completed':
                        success_count += 1
                    elif isinstance(result.get('success_rate'), (int, float)) and result['success_rate'] > 0.5:
                        success_count += 1
                
                success_rate = success_count / len(valid_results) if valid_results else 0
                self.performance_metrics['recent_success_rate'] = success_rate
        else:
            # No results to learn from
            self.performance_metrics['recent_success_rate'] = 0
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "status": "active" if self.is_active else "inactive",
            "sub_agents_active": self.get_active_sub_agents_count(),
            "queue_size": self.message_queue.qsize(),
            "last_activity": datetime.now().isoformat()
        }
    
    def get_active_sub_agents_count(self) -> int:
        return len([sa for sa in self.sub_agents if sa.is_active])
    
    def get_sub_agents_status(self) -> List[Dict]:
        return [{"name": sa.name, "active": sa.is_active, "status": "active" if sa.is_active else "inactive"} 
                for sa in self.sub_agents]
    
    def clear_queue(self):
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except:
                break

class SubAgent:
    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.task_history = []
        
    async def perform_task(self, task: Dict) -> Dict:
        self.task_history.append({
            "task": task,
            "timestamp": datetime.now(),
            "status": "completed"
        })
        
        # Simulate task execution with variable success
        await asyncio.sleep(0.1)
        success = True  # Simple simulation
        
        return {
            "sub_agent": self.name,
            "task_id": task.get('id', str(uuid.uuid4())),
            "result": f"Completed {task.get('type', 'unknown')} task",
            "success": success,
            "metrics": {"efficiency": 0.85, "quality": 0.92},
            "timestamp": datetime.now().isoformat()
        }
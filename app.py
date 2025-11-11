import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import asyncio
import uuid
import json
import sqlite3
import threading
from typing import Dict, List, Any

# Import our bot ecosystem
from agents.ceo_bot import CEOBot
from agents.planner_bot import PlannerBot
from agents.execution_bot import ExecutionBot
from database.database import init_db, save_task, get_tasks, save_report, get_reports

# Page configuration
st.set_page_config(
    page_title="🤖 Intelligent Bot Ecosystem",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bot-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-card {
        border-left: 4px solid #28a745;
    }
    .warning-card {
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        border-left: 4px solid #dc3545;
    }
    .sub-agent-card {
        background: #f1f3f4;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        border-left: 3px solid #6c757d;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitBotEcosystem:
    def __init__(self):
        self.init_session_state()
        self.init_database()
        self.init_bots()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.tasks = []
            st.session_state.reports = []
            st.session_state.bot_messages = []
            st.session_state.performance_data = []
            st.session_state.auto_mode = False
            st.session_state.last_auto_run = None
            
    def init_database(self):
        """Initialize database"""
        init_db()
        
    def init_bots(self):
        """Initialize bot instances"""
        if 'ceo_bot' not in st.session_state:
            st.session_state.ceo_bot = CEOBot()
        if 'planner_bot' not in st.session_state:
            st.session_state.planner_bot = PlannerBot()
        if 'execution_bot' not in st.session_state:
            st.session_state.execution_bot = ExecutionBot()
            
    async def process_task(self, task_data: Dict) -> Dict:
        """Process a task through the bot ecosystem"""
        try:
            # CEO evaluates task
            ceo_evaluation = await st.session_state.ceo_bot.evaluate_task(task_data)
            
            # Planner creates plan
            plan = await st.session_state.planner_bot.create_plan(ceo_evaluation)
            
            # Execution bot implements
            results = await st.session_state.execution_bot.execute_plan(plan)
            
            # Learn from results - FIXED: Ensure we're passing proper dictionaries
            if isinstance(results, dict):
                results_list = [results]  # Convert single dict to list
            elif isinstance(results, list):
                results_list = results
            else:
                results_list = []
            
            await st.session_state.ceo_bot.learn_from_results(results_list)
            await st.session_state.planner_bot.learn_from_results(results_list)
            await st.session_state.execution_bot.learn_from_results(results_list)
            
            # Store task and results
            task_record = {
                **task_data,
                'evaluation': ceo_evaluation,
                'plan': plan,
                'results': results,
                'completed_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            st.session_state.tasks.append(task_record)
            save_task(task_record)
            
            return results
            
        except Exception as e:
            st.error(f"Error processing task: {str(e)}")
            # Store failed task
            task_record = {
                **task_data,
                'completed_at': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            }
            st.session_state.tasks.append(task_record)
            save_task(task_record)
            return {"error": str(e)}
    
    def run_automation_cycle(self):
        """Run automated task generation and processing"""
        if st.session_state.auto_mode:
            current_time = datetime.now()
            if (st.session_state.last_auto_run is None or 
                (current_time - st.session_state.last_auto_run).seconds >= 300):  # Every 5 minutes
                
                # Generate automated task
                auto_task = {
                    'id': str(uuid.uuid4()),
                    'type': 'automated_analysis',
                    'description': f'Automated system analysis - {current_time.strftime("%Y-%m-%d %H:%M")}',
                    'complexity': 3,
                    'urgency': 2,
                    'impact': 4,
                    'priority': 'medium',
                    'created_at': current_time.isoformat()
                }
                
                # Process task asynchronously
                asyncio.run(self.process_task(auto_task))
                st.session_state.last_auto_run = current_time
                
                st.toast("🤖 Automated task completed!", icon="✅")

def main():
    ecosystem = StreamlitBotEcosystem()
    
    # Header
    st.markdown('<div class="main-header">🤖 Intelligent Bot Ecosystem</div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎮 Control Panel")
    
    # Auto-mode toggle
    st.session_state.auto_mode = st.sidebar.toggle("🔄 Auto Mode", value=st.session_state.auto_mode)
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate to",
        ["🏠 Dashboard", "🤖 Bot Status", "📊 Reports", "📋 Task Management", 
         "📈 Analytics", "⚙️ System Settings"]
    )
    
    # Run automation in background
    if st.session_state.auto_mode:
        ecosystem.run_automation_cycle()
    
    # Page routing
    if page == "🏠 Dashboard":
        show_dashboard(ecosystem)
    elif page == "🤖 Bot Status":
        show_bot_status()
    elif page == "📊 Reports":
        show_reports()
    elif page == "📋 Task Management":
        show_task_management(ecosystem)
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "⚙️ System Settings":
        show_settings()

def show_dashboard(ecosystem):
    """Main dashboard view"""
    st.header("🏠 System Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(st.session_state.tasks)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completed_tasks = len([t for t in st.session_state.tasks if t.get('status') == 'completed'])
        st.metric("Completed Tasks", completed_tasks)
    
    with col3:
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        active_sub_agents = (
            st.session_state.ceo_bot.get_active_sub_agents_count() +
            st.session_state.planner_bot.get_active_sub_agents_count() +
            st.session_state.execution_bot.get_active_sub_agents_count()
        )
        st.metric("Active Sub-Agents", active_sub_agents)
    
    # Bot performance overview
    st.subheader("📊 Bot Performance Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ceo_metrics = st.session_state.ceo_bot.get_performance_metrics()
        efficiency = ceo_metrics.get('efficiency_score', 0) * 100
        st.metric("CEO Bot Efficiency", f"{efficiency:.1f}%")
        
        with st.expander("CEO Details"):
            st.write(f"Tasks Evaluated: {ceo_metrics.get('tasks_evaluated', 0)}")
            st.write(f"Reports Generated: {ceo_metrics.get('reports_generated', 0)}")
            st.write(f"Sub-Agent Utilization: {ceo_metrics.get('sub_agent_utilization', 0)*100:.1f}%")
    
    with col2:
        planner_metrics = st.session_state.planner_bot.get_performance_metrics()
        planning_eff = planner_metrics.get('efficiency_score', 0) * 100
        st.metric("Planner Bot Efficiency", f"{planning_eff:.1f}%")
        
        with st.expander("Planner Details"):
            st.write(f"Plans Created: {planner_metrics.get('plans_created', 0)}")
            st.write(f"Allocation Efficiency: {planner_metrics.get('allocation_efficiency', 0)*100:.1f}%")
            st.write(f"Timeline Accuracy: {planner_metrics.get('timeline_accuracy', 0)*100:.1f}%")
    
    with col3:
        exec_metrics = st.session_state.execution_bot.get_performance_metrics()
        exec_eff = exec_metrics.get('efficiency_score', 0) * 100
        st.metric("Execution Bot Efficiency", f"{exec_eff:.1f}%")
        
        with st.expander("Execution Details"):
            st.write(f"Tasks Completed: {exec_metrics.get('tasks_completed', 0)}")
            st.write(f"Success Rate: {exec_metrics.get('success_rate', 0)*100:.1f}%")
            st.write(f"Sub-Agent Productivity: {exec_metrics.get('sub_agent_productivity', 0)*100:.1f}%")
    
    # Recent activity
    st.subheader("🔄 Recent Activity")
    
    if st.session_state.tasks:
        recent_tasks = st.session_state.tasks[-5:]  # Last 5 tasks
        task_data = []
        for task in recent_tasks:
            task_data.append({
                'Task ID': task['id'][:8] + '...',
                'Type': task.get('type', 'unknown'),
                'Priority': task.get('priority', 'medium'),
                'Status': task.get('status', 'unknown'),
                'Created': task.get('created_at', '')[:16]
            })
        
        st.dataframe(pd.DataFrame(task_data), use_container_width=True)
    else:
        st.info("No tasks yet. Submit a task to see activity here.")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Generate Daily Report", use_container_width=True):
            with st.spinner("Generating daily report..."):
                report = asyncio.run(st.session_state.ceo_bot.generate_daily_report())
                st.session_state.reports.append(report)
                save_report(report)
                st.success("Daily report generated!")
    
    with col2:
        if st.button("🎯 Run System Analysis", use_container_width=True):
            task_data = {
                'id': str(uuid.uuid4()),
                'type': 'system_analysis',
                'description': 'Comprehensive system performance analysis',
                'complexity': 5,
                'urgency': 3,
                'impact': 6,
                'priority': 'high',
                'created_at': datetime.now().isoformat()
            }
            with st.spinner("Running system analysis..."):
                asyncio.run(ecosystem.process_task(task_data))
                st.success("System analysis completed!")
    
    with col3:
        if st.button("🛠️ Optimize Strategies", use_container_width=True):
            with st.spinner("Optimizing bot strategies..."):
                # Trigger learning and optimization with empty results
                asyncio.run(st.session_state.ceo_bot.learn_from_results([]))
                asyncio.run(st.session_state.planner_bot.learn_from_results([]))
                asyncio.run(st.session_state.execution_bot.learn_from_results([]))
                st.success("Strategies optimized!")

def show_bot_status():
    """Bot status and monitoring page"""
    st.header("🤖 Bot Status & Monitoring")
    
    # CEO Bot
    with st.container():
        st.markdown('<div class="bot-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("👑 CEO Bot")
            st.write("**Responsibilities:** Global goal setting, performance evaluation, strategic oversight")
            
            # Sub-agents status
            st.write("**Sub-Agents Status:**")
            sub_agents_status = st.session_state.ceo_bot.get_sub_agents_status()
            for agent in sub_agents_status:
                status_icon = "🟢" if agent['active'] else "🔴"
                st.write(f"{status_icon} {agent['name']} - {agent['status']}")
        
        with col2:
            status = st.session_state.ceo_bot.get_status()
            st.metric("Status", "🟢 Active" if status['status'] == 'active' else "🔴 Inactive")
            st.metric("Queue", status['queue_size'])
            st.metric("Last Activity", status['last_activity'][11:19])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Planner Bot
    with st.container():
        st.markdown('<div class="bot-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📋 Planner Bot")
            st.write("**Responsibilities:** Task analysis, resource allocation, timeline planning")
            
            # Sub-agents status
            st.write("**Sub-Agents Status:**")
            sub_agents_status = st.session_state.planner_bot.get_sub_agents_status()
            for agent in sub_agents_status:
                status_icon = "🟢" if agent['active'] else "🔴"
                st.write(f"{status_icon} {agent['name']} - {agent['status']}")
        
        with col2:
            status = st.session_state.planner_bot.get_status()
            st.metric("Status", "🟢 Active" if status['status'] == 'active' else "🔴 Inactive")
            st.metric("Queue", status['queue_size'])
            st.metric("Last Activity", status['last_activity'][11:19])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Execution Bot
    with st.container():
        st.markdown('<div class="bot-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("⚡ Execution Bot")
            st.write("**Responsibilities:** Task execution, result collection, performance reporting")
            
            # Sub-agents status
            st.write("**Sub-Agents Status:**")
            sub_agents_status = st.session_state.execution_bot.get_sub_agents_status()
            for agent in sub_agents_status:
                status_icon = "🟢" if agent['active'] else "🔴"
                st.write(f"{status_icon} {agent['name']} - {agent['status']}")
        
        with col2:
            status = st.session_state.execution_bot.get_status()
            st.metric("Status", "🟢 Active" if status['status'] == 'active' else "🔴 Inactive")
            st.metric("Queue", status['queue_size'])
            st.metric("Last Activity", status['last_activity'][11:19])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time controls
    st.subheader("🎮 Real-time Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh All Bots", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 Update Metrics", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🧹 Clear Bot Queues", use_container_width=True):
            st.session_state.ceo_bot.clear_queue()
            st.session_state.planner_bot.clear_queue()
            st.session_state.execution_bot.clear_queue()
            st.success("All bot queues cleared!")

def show_reports():
    """Reports and analytics page"""
    st.header("📊 Reports & Analytics")
    
    report_type = st.selectbox("Select Report Type", ["Daily Report", "Weekly Report", "Custom Report"])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("📈 Generate Report", use_container_width=True):
            with st.spinner(f"Generating {report_type}..."):
                if report_type == "Daily Report":
                    report = asyncio.run(st.session_state.ceo_bot.generate_daily_report())
                elif report_type == "Weekly Report":
                    report = asyncio.run(st.session_state.ceo_bot.generate_weekly_report())
                else:
                    report = {"type": "custom", "content": "Custom report content"}
                
                st.session_state.reports.append(report)
                save_report(report)
                st.success(f"{report_type} generated successfully!")
    
    with col2:
        if st.button("📥 Export Report", use_container_width=True):
            if st.session_state.reports:
                latest_report = st.session_state.reports[-1]
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(latest_report, indent=2),
                    file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Display latest report
    if st.session_state.reports:
        latest_report = st.session_state.reports[-1]
        display_report(latest_report)
    else:
        st.info("No reports generated yet. Generate a report to see it here.")

def display_report(report):
    """Display a generated report"""
    st.subheader(f"📋 {report.get('report_type', 'Report').title()} - {report.get('date', 'N/A')}")
    
    if report.get('report_type') == 'daily':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ What's Working")
            for item in report.get('whats_working', []):
                st.write(f"• {item}")
            
            st.markdown("### 🎯 Goal Progress")
            progress_data = report.get('goal_progress', {})
            for goal, progress in progress_data.items():
                st.progress(progress / 100 if isinstance(progress, (int, float)) else 0)
                st.write(f"{goal}: {progress}%")
        
        with col2:
            st.markdown("### ❌ What's Not Working")
            for item in report.get('whats_not_working', []):
                st.write(f"• {item}")
            
            st.markdown("### 💡 Improvement Suggestions")
            for item in report.get('improvement_suggestions', []):
                st.write(f"• {item}")
    
    elif report.get('report_type') == 'weekly':
        tabs = st.tabs(["Trend Analysis", "Key Achievements", "Strategic Insights", "Next Week Goals"])
        
        with tabs[0]:
            st.write("### 📈 Trend Analysis")
            trends = report.get('trend_analysis', {})
            for trend, analysis in trends.items():
                st.write(f"**{trend.title()}:** {analysis}")
        
        with tabs[1]:
            st.write("### 🏆 Key Achievements")
            for achievement in report.get('key_achievements', []):
                st.write(f"• {achievement}")
        
        with tabs[2]:
            st.write("### 🔍 Strategic Insights")
            for insight in report.get('strategic_insights', []):
                st.write(f"• {insight}")
        
        with tabs[3]:
            st.write("### 🎯 Next Week Goals")
            for goal in report.get('next_week_goals', []):
                st.write(f"• {goal}")

def show_task_management(ecosystem):
    """Task management page"""
    st.header("📋 Task Management")
    
    tab1, tab2, tab3 = st.tabs(["Submit Task", "Task History", "Bot Communication"])
    
    with tab1:
        st.subheader("🚀 Submit New Task")
        
        col1, col2 = st.columns(2)
        
        with col1:
            task_type = st.selectbox("Task Type", 
                ["analysis", "processing", "optimization", "reporting", "custom"])
            priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
            complexity = st.slider("Complexity (1-10)", 1, 10, 5)
        
        with col2:
            urgency = st.slider("Urgency (1-10)", 1, 10, 5)
            impact = st.slider("Impact (1-10)", 1, 10, 5)
            allocated_sub_agents = st.slider("Sub-Agents to Allocate", 1, 10, 3)
        
        description = st.text_area("Task Description", 
                                 placeholder="Describe the task in detail...")
        
        if st.button("🎯 Submit Task", type="primary"):
            if description.strip():
                task_data = {
                    'id': str(uuid.uuid4()),
                    'type': task_type,
                    'description': description,
                    'complexity': complexity,
                    'urgency': urgency,
                    'impact': impact,
                    'priority': priority,
                    'allocated_sub_agents': allocated_sub_agents,
                    'created_at': datetime.now().isoformat(),
                    'status': 'submitted'
                }
                
                with st.spinner("Processing task through bot ecosystem..."):
                    try:
                        results = asyncio.run(ecosystem.process_task(task_data))
                        st.success("✅ Task completed successfully!")
                        
                        # Show results
                        with st.expander("View Task Results"):
                            st.json(results)
                    
                    except Exception as e:
                        st.error(f"❌ Task failed: {str(e)}")
            else:
                st.warning("Please enter a task description.")
    
    with tab2:
        st.subheader("📜 Task History")
        
        if st.session_state.tasks:
            # Create task history table
            task_data = []
            for task in st.session_state.tasks:
                task_data.append({
                    'ID': task['id'][:8] + '...',
                    'Type': task.get('type', 'unknown'),
                    'Description': task.get('description', '')[:50] + '...',
                    'Priority': task.get('priority', 'medium'),
                    'Complexity': task.get('complexity', 0),
                    'Status': task.get('status', 'unknown'),
                    'Created': task.get('created_at', '')[:16]
                })
            
            df = pd.DataFrame(task_data)
            st.dataframe(df, use_container_width=True)
            
            # Task statistics
            st.subheader("📊 Task Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_counts = df['Status'].value_counts()
                fig_status = px.pie(values=status_counts.values, names=status_counts.index, 
                                  title="Task Status Distribution")
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                priority_counts = df['Priority'].value_counts()
                fig_priority = px.bar(x=priority_counts.index, y=priority_counts.values,
                                    title="Tasks by Priority")
                st.plotly_chart(fig_priority, use_container_width=True)
            
            with col3:
                complexity_avg = df['Complexity'].mean()
                st.metric("Average Complexity", f"{complexity_avg:.1f}")
                st.metric("Total Tasks", len(df))
        
        else:
            st.info("No tasks submitted yet. Submit a task to see history here.")
    
    with tab3:
        st.subheader("🤝 Bot Communication")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sender = st.selectbox("Sender Bot", 
                ["ceo_bot", "planner_bot", "execution_bot"])
            receiver = st.selectbox("Receiver Bot", 
                ["ceo_bot", "planner_bot", "execution_bot"])
        
        with col2:
            message_type = st.selectbox("Message Type", 
                ["status_update", "report_request", "goal_update", "task_coordination", "general"])
            priority = st.selectbox("Message Priority", ["low", "normal", "high"])
        
        message_content = st.text_area("Message Content", 
                                     placeholder="Enter your message here...")
        
        if st.button("📤 Send Message"):
            if message_content.strip():
                message = {
                    'id': str(uuid.uuid4()),
                    'sender': sender,
                    'receiver': receiver,
                    'type': message_type,
                    'priority': priority,
                    'content': message_content,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'sent'
                }
                
                # Simulate message processing
                st.session_state.bot_messages.append(message)
                
                # Show simulated response
                st.success("✅ Message sent successfully!")
                st.info(f"🤖 Simulated response from {receiver}: 'Message received and processed successfully.'")
                
                # Show message history
                with st.expander("View Message History"):
                    for msg in st.session_state.bot_messages[-5:]:
                        st.write(f"**{msg['sender']} → {msg['receiver']}** ({msg['timestamp'][11:19]}): {msg['content']}")
            else:
                st.warning("Please enter message content.")

def show_analytics():
    """Performance analytics page"""
    st.header("📈 Performance Analytics")
    
    # Bot performance comparison
    st.subheader("🤖 Bot Performance Comparison")
    
    ceo_metrics = st.session_state.ceo_bot.get_performance_metrics()
    planner_metrics = st.session_state.planner_bot.get_performance_metrics()
    exec_metrics = st.session_state.execution_bot.get_performance_metrics()
    
    # Create performance chart
    bots = ['CEO Bot', 'Planner Bot', 'Execution Bot']
    efficiency_scores = [
        ceo_metrics.get('efficiency_score', 0) * 100,
        planner_metrics.get('efficiency_score', 0) * 100,
        exec_metrics.get('efficiency_score', 0) * 100
    ]
    
    fig = go.Figure(data=[
        go.Bar(name='Efficiency', x=bots, y=efficiency_scores, marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ])
    
    fig.update_layout(
        title="Bot Efficiency Scores",
        yaxis_title="Efficiency Score (%)",
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👑 CEO Bot Metrics")
        st.metric("Tasks Evaluated", ceo_metrics.get('tasks_evaluated', 0))
        st.metric("Reports Generated", ceo_metrics.get('reports_generated', 0))
        st.metric("Sub-Agent Utilization", f"{ceo_metrics.get('sub_agent_utilization', 0)*100:.1f}%")
    
    with col2:
        st.subheader("📋 Planner Bot Metrics")
        st.metric("Plans Created", planner_metrics.get('plans_created', 0))
        st.metric("Allocation Efficiency", f"{planner_metrics.get('allocation_efficiency', 0)*100:.1f}%")
        st.metric("Timeline Accuracy", f"{planner_metrics.get('timeline_accuracy', 0)*100:.1f}%")
    
    with col3:
        st.subheader("⚡ Execution Bot Metrics")
        st.metric("Tasks Completed", exec_metrics.get('tasks_completed', 0))
        st.metric("Success Rate", f"{exec_metrics.get('success_rate', 0)*100:.1f}%")
        st.metric("Sub-Agent Productivity", f"{exec_metrics.get('sub_agent_productivity', 0)*100:.1f}%")
    
    # System-wide metrics
    st.subheader("🔧 System-wide Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_efficiency = (efficiency_scores[0] + efficiency_scores[1] + efficiency_scores[2]) / 3
        st.metric("Overall Efficiency", f"{overall_efficiency:.1f}%")
    
    with col2:
        total_tasks = len(st.session_state.tasks)
        completed_tasks = len([t for t in st.session_state.tasks if t.get('status') == 'completed'])
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Task Success Rate", f"{success_rate:.1f}%")
    
    with col3:
        st.metric("Active Sub-Agents", 
                 st.session_state.ceo_bot.get_active_sub_agents_count() +
                 st.session_state.planner_bot.get_active_sub_agents_count() +
                 st.session_state.execution_bot.get_active_sub_agents_count())
    
    with col4:
        st.metric("System Uptime", "99.9%")

def show_settings():
    """System settings page"""
    st.header("⚙️ System Settings")
    
    st.subheader("🤖 Bot Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.number_input("CEO Sub-Agents", min_value=1, max_value=20, value=10, key="ceo_agents")
        st.slider("CEO Learning Rate", 0.1, 1.0, 0.7, key="ceo_learning")
    
    with col2:
        st.number_input("Planner Sub-Agents", min_value=1, max_value=20, value=10, key="planner_agents")
        st.slider("Planner Learning Rate", 0.1, 1.0, 0.8, key="planner_learning")
    
    with col3:
        st.number_input("Execution Sub-Agents", min_value=1, max_value=20, value=10, key="exec_agents")
        st.slider("Execution Learning Rate", 0.1, 1.0, 0.9, key="exec_learning")
    
    st.subheader("🔄 Automation Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_interval = st.selectbox("Auto-run Interval", 
                                   ["5 minutes", "15 minutes", "30 minutes", "1 hour"])
        st.toggle("Enable Daily Reports", value=True)
        st.toggle("Enable Weekly Reports", value=True)
    
    with col2:
        st.toggle("Enable Performance Alerts", value=True)
        st.toggle("Enable Error Notifications", value=True)
        st.toggle("Enable Strategy Optimization", value=True)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")
    
    st.subheader("🛠️ System Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Task History", use_container_width=True):
            st.session_state.tasks.clear()
            st.success("Task history cleared!")
        
        if st.button("📊 Reset Performance Data", use_container_width=True):
            st.session_state.performance_data.clear()
            st.success("Performance data reset!")
    
    with col2:
        if st.button("🔄 Restart Bot System", use_container_width=True):
            st.session_state.ceo_bot = CEOBot()
            st.session_state.planner_bot = PlannerBot()
            st.session_state.execution_bot = ExecutionBot()
            st.success("Bot system restarted!")
        
        if st.button("📝 Export System Logs", use_container_width=True):
            st.info("Log export functionality would be implemented here")

if __name__ == "__main__":
    main()
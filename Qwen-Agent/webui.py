import gradio as gr
from qwen_agent.admin_modal import create_admin_modal
import json
from qwen_agent.agents import Assistant
from qwen_agent.tools import base as tool_base
from qwen_agent.utils.output_beautify import typewriter_print
from qwen_agent.agents.poly_personality_orchestrator import PolyPersonalityOrchestrator
from qwen_agent.llm.qwenomni_oai import QwenOmniChatAtOAI

# Get list of all available tools
AVAILABLE_TOOLS = {
    name: tool.__doc__ or "No description available"
    for name, tool in tool_base.TOOL_REGISTRY.items()
}

def run_all_clusters_pipeline(user_input):
    """Run the PolyPersonalityOrchestrator pipeline with all clusters"""
    try:
        llm = QwenOmniChatAtOAI({
            'model': 'qwen3',
            'model_server': 'http://localhost:11434/v1',
            'api_key': 'EMPTY',
            'generate_cfg': {
                'temperature': 0.7,
                'top_p': 0.8
            }
        })
        orchestrator = PolyPersonalityOrchestrator(llm)
        results = orchestrator.run_full_pipeline(user_input)
        return "\n\n".join([f"Step {i+1}: {step}" for i, step in enumerate(results)])
    except Exception as e:
        return f"❌ Error running pipeline: {str(e)}"

def create_agent_config(name, description, personality, selected_tools, temperature):
    """Create an agent configuration based on user inputs"""
    llm_cfg = {
        'model': 'qwen3',
        'model_server': 'http://localhost:11434/v1',
        'api_key': 'EMPTY',
        'generate_cfg': {
            'temperature': float(temperature),
            'top_p': 0.8
        }
    }
    
    system_message = f"""You are {name}, an AI assistant with the following traits:
{personality}

Your primary purpose is: {description}

You have access to specific tools that you should use when appropriate to accomplish tasks."""

    return llm_cfg, system_message, selected_tools

class AgentChat:
    def __init__(self):
        self.agent = None
        self.messages = []
        self.chat_history = []
    
    def create_new_agent(self, name, description, personality, tools, temperature):
        if not name or not description or not personality or not tools:
            return "⚠️ Please fill in all required fields!"
        
        try:
            llm_cfg, system_message, selected_tools = create_agent_config(
                name, description, personality, tools, temperature
            )
            
            self.agent = Assistant(
                llm=llm_cfg,
                system_message=system_message,
                function_list=tools
            )
            self.messages = []
            self.chat_history = []
            return f"✅ Agent '{name}' created successfully! You can now start chatting."
        except Exception as e:
            return f"❌ Error creating agent: {str(e)}"
    
    def chat(self, message, history):
        if not self.agent:
            return history + [[message, "⚠️ Please create an agent first!"]]
        
        if not message:
            return history
        
        self.messages.append({'role': 'user', 'content': message})
        response_text = ''
        
        try:
            for response in self.agent.run(messages=self.messages):
                response_text = typewriter_print(response, response_text)
                
            self.messages.extend(response)
            history.append([message, response_text])
            return history
        except Exception as e:
            history.append([message, f"❌ Error: {str(e)}"])
            return history
    
    def clear_history(self):
        self.messages = []
        self.chat_history = []
        return []

def create_ui():
    agent_chat = AgentChat()
    
    with gr.Blocks(
        title="Qwen3 Agent Builder",
        theme=gr.themes.Soft(),
        css="""
            .container { max-width: 800px; margin: auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .tool-description { font-size: 0.9em; color: #666; }
        """
    ) as interface:
        with gr.Column(elem_classes="container"):
            gr.Markdown("# 🤖 Qwen3 Agent Builder", elem_classes="header")
            gr.Markdown("Create and customize your own AI agent with specific tools and personality.")
            
            with gr.Tabs():
                with gr.Tab("🚀 All Clusters"):
                    with gr.Column():
                        gr.Markdown("### AI Software Engineer Pipeline")
                        gr.Markdown("Input your software development task and let the AI clusters work together to build it.")
                        user_input = gr.Textbox(
                            label="Development Task",
                            placeholder="Example: Build a complete web application with user authentication and analytics",
                            lines=3
                        )
                        run_button = gr.Button("🚀 Run Pipeline", variant="primary", size="lg")
                        with gr.Row():
                            output_area = gr.Textbox(
                                label="Pipeline Output",
                                lines=15,
                                max_lines=30,
                                interactive=False,
                                show_label=True
                            )

                        run_button.click(
                            fn=lambda x: run_all_clusters_pipeline(x) if x.strip() else "⚠️ Please enter a development task.",
                            inputs=user_input,
                            outputs=output_area,
                            api_name="run_pipeline"
                        )

                with gr.Tab("📝 Agent Configuration"):
                    with gr.Column():
                        name = gr.Textbox(
                            label="Agent Name",
                            placeholder="Enter a name for your agent",
                            info="Required"
                        )
                        description = gr.Textbox(
                            label="Agent Purpose",
                            placeholder="Describe what this agent should do",
                            lines=3,
                            info="Required"
                        )
                        personality = gr.Textbox(
                            label="Agent Personality",
                            placeholder="Describe the agent's personality traits and behavior",
                            lines=3,
                            info="Required"
                        )
                        temperature = gr.Slider(
                            minimum=0.1,
                            maximum=2.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature (Creativity)",
                            info="Higher values make the output more random"
                        )
                        
                        with gr.Accordion("🛠️ Available Tools", open=True):
                            tools = gr.CheckboxGroup(
                                choices=list(AVAILABLE_TOOLS.keys()),
                                label="Select Tools",
                                info="Choose the tools this agent should have access to"
                            )
                            
                            with gr.Accordion("Tool Descriptions", open=False):
                                for tool_name, tool_desc in AVAILABLE_TOOLS.items():
                                    gr.Markdown(f"**{tool_name}**: {tool_desc}", elem_classes="tool-description")
                        
                        create_btn = gr.Button("🚀 Create Agent", variant="primary")
                        status = gr.Markdown()

                        create_btn.click(
                            fn=agent_chat.create_new_agent,
                            inputs=[name, description, personality, tools, temperature],
                            outputs=[status]
                        )

                with gr.Tab("💬 Chat"):
                    chatbot = gr.Chatbot(
                        show_label=False,
                        height=400,
                        type="messages"
                    )
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your message",
                            placeholder="Type your message here...",
                            scale=4
                        )
                        send = gr.Button("Send", variant="primary", scale=1)
                    
                    clear = gr.Button("🗑️ Clear History")

                    send.click(
                        fn=agent_chat.chat,
                        inputs=[msg, chatbot],
                        outputs=[chatbot]
                    )
                    clear.click(
                        fn=agent_chat.clear_history,
                        inputs=[],
                        outputs=[chatbot]
                    )

                with gr.Tab("⚙️ Admin"):
                    with gr.Column():
                        gr.Markdown("### Admin Settings")
                        admin_modal_btn = gr.Button("Open Admin Modal")
                        admin_modal = gr.Accordion("Admin Options", open=False)
                        with admin_modal:
                            gr.Markdown("#### Edit Agent")
                            edit_agent_name = gr.Textbox(label="Agent Name")
                            edit_agent_description = gr.Textbox(label="Agent Purpose", lines=3)
                            edit_agent_personality = gr.Textbox(label="Agent Personality", lines=3)
                            upload_training_data = gr.File(
                                label="Upload Training Data (.zip, .txt, .rtf, .pdf, code files)", 
                                file_types=['.zip', '.txt', '.rtf', '.pdf', '.py', '.js', '.java', '.cpp', '.c']
                            )
                            apply_training_btn = gr.Button("Apply Training")
                            training_status = gr.Markdown()

                        admin_modal_btn.click(lambda: admin_modal.open(), None, None)

                        def process_training_files(files):
                            if not files:
                                return "No files uploaded."
                            try:
                                # Process training files logic here
                                return "Training files processed successfully!"
                            except Exception as e:
                                return f"Error processing training files: {str(e)}"

                        apply_training_btn.click(
                            fn=process_training_files,
                            inputs=[upload_training_data],
                            outputs=[training_status]
                        )

    return interface

if __name__ == "__main__":
    # First ensure Ollama has qwen3 model
    import os
    os.system("ollama pull qwen3")
    
    interface = create_ui()
    interface.launch(
        debug=True
    )

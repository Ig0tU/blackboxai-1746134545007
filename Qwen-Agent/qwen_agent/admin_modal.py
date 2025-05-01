import gradio as gr
import requests

def create_admin_modal():
    with gr.Column():
        gr.Markdown("### Admin Modal")
        edit_agent_name = gr.Textbox(label="Agent Name")
        edit_agent_description = gr.Textbox(label="Agent Purpose", lines=3)
        edit_agent_personality = gr.Textbox(label="Agent Personality", lines=3)
        upload_training_data = gr.File(label="Upload Training Data (.zip, .txt, .rtf, .pdf, code files)", file_types=['.zip', '.txt', '.rtf', '.pdf', '.py', '.js', '.java', '.cpp', '.c'])
        apply_training_btn = gr.Button("Apply Training")
        training_status = gr.Markdown()

        gr.Markdown("#### Webhook Management")
        webhook_url = gr.Textbox(label="Webhook URL")
        add_webhook_btn = gr.Button("Add Webhook")
        webhook_status = gr.Markdown()

        gr.Markdown("#### Client Access Control")
        client_id = gr.Textbox(label="Client ID")
        enable_bot_btn = gr.Button("Enable Bot for Client")
        client_status = gr.Markdown()

        gr.Markdown("#### Embed Code")
        embed_code = gr.Textbox(label="Embed Code", interactive=False, lines=4)
        generate_embed_btn = gr.Button("Generate Embed Code")

        # Event handlers
        apply_training_btn.click(
            fn=lambda files: process_training_files(files, edit_agent_name.value),
            inputs=[upload_training_data],
            outputs=[training_status]
        )
        add_webhook_btn.click(
            fn=lambda url: add_webhook(url, edit_agent_name.value),
            inputs=[webhook_url],
            outputs=[webhook_status]
        )
        enable_bot_btn.click(
            fn=lambda cid: enable_bot_for_client(cid, edit_agent_name.value),
            inputs=[client_id],
            outputs=[client_status]
        )
        generate_embed_btn.click(
            fn=lambda bot_name: generate_embed_code(bot_name),
            inputs=[edit_agent_name],
            outputs=[embed_code]
        )

    return gr.Column()

def process_training_files(files, bot_name):
    if not files:
        return "No files uploaded."
    bot_id = bot_name or "default_bot"
    url = f"http://localhost:9000/training/{bot_id}"
    try:
        files_to_send = [('files', (file.name, open(file.name, 'rb'))) for file in files]
        response = requests.post(url, files=files_to_send)
        if response.status_code == 200:
            return f"Training applied successfully! {response.json().get('message', '')}"
        else:
            return f"Failed to apply training: {response.text}"
    except Exception as e:
        return f"Error uploading training data: {str(e)}"

def add_webhook(url, bot_name):
    bot_id = bot_name or "default_bot"
    api_url = f"http://localhost:9000/webhooks/"
    try:
        response = requests.post(api_url, json={"bot_id": bot_id, "webhook_url": url})
        if response.status_code == 200:
            return "Webhook added successfully."
        else:
            return f"Failed to add webhook: {response.text}"
    except Exception as e:
        return f"Error adding webhook: {str(e)}"

def enable_bot_for_client(client_id, bot_name):
    bot_id = bot_name or "default_bot"
    api_url = f"http://localhost:9000/clients/{client_id}/enable_bot/{bot_id}"
    try:
        response = requests.post(api_url)
        if response.status_code == 200:
            return f"Bot enabled for client {client_id}."
        else:
            return f"Failed to enable bot: {response.text}"
    except Exception as e:
        return f"Error enabling bot: {str(e)}"

def generate_embed_code(bot_name):
    bot_id = bot_name or "default_bot"
    embed = f'<script src="https://yourdomain.com/embed.js" data-bot-id="{bot_id}"></script>'
    return embed

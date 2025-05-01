#!/bin/bash

# This script automates the integration of admin_modal.py into webui.py

WEBUI_FILE="/project/sandbox/user-workspace/Qwen-Agent/webui.py"
ADMIN_MODAL_IMPORT="from qwen_agent.admin_modal import create_admin_modal"
ADMIN_TAB_CODE='
                with gr.Tab("⚙️ Admin"):
                    admin_modal = create_admin_modal()
                    with gr.Column():
                        admin_modal.render()
'

# Check if import already exists
if ! grep -q "$ADMIN_MODAL_IMPORT" "$WEBUI_FILE"; then
    # Add import after other imports (after first import block)
    sed -i "/import gradio as gr/a $ADMIN_MODAL_IMPORT" "$WEBUI_FILE"
    echo "Added admin_modal import to webui.py"
else
    echo "admin_modal import already present in webui.py"
fi

# Insert admin tab code inside create_ui function
# Find line number of 'with gr.Tabs():'
TAB_LINE=$(grep -n "with gr.Tabs():" "$WEBUI_FILE" | cut -d: -f1)

if [ -z "$TAB_LINE" ]; then
    echo "Could not find 'with gr.Tabs():' in webui.py"
    exit 1
fi

# Check if admin tab code already present
if ! grep -q "with gr.Tab(\"⚙️ Admin\"):" "$WEBUI_FILE"; then
    # Insert admin tab code after 'with gr.Tabs():'
    sed -i "$((TAB_LINE+1))i $ADMIN_TAB_CODE" "$WEBUI_FILE"
    echo "Inserted admin tab code into webui.py"
else
    echo "Admin tab code already present in webui.py"
fi

echo "Integration automation complete."

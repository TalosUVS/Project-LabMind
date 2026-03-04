import os
import re
import base64
import io
from flask import Flask, render_template, request, jsonify
from PIL import Image
from google import genai
from google.genai import types

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- CONFIGURATION ---
# Securely get key from environment
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("CRITICAL ERROR: GEMINI_API_KEY is missing from environment", flush=True)
    # API_KEY = "YOUR_API_KEY_HERE" # Uncomment for local testing if needed

client = genai.Client(api_key=API_KEY)

def clean_response(text):
    """Cleans up the response to ensure raw HTML renders correctly."""
    text = re.sub(r'^```html', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```', '', text, flags=re.MULTILINE)
    text = re.sub(r'```$', '', text, flags=re.MULTILINE)
    
    # Convert Markdown headers to HTML for better mobile rendering
    text = re.sub(r'### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text) # Bold
    
    return text.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # --------------------------------------------
        # 1) INPUT: accept either JSON(base64) or multipart(FormData)
        # --------------------------------------------
        if request.is_json:
            data = request.get_json(silent=True) or {}
            image_data = data.get('image', '')
            raw_mode = str(data.get('mode', 'identify')).strip().lower()
            raw_voice = data.get('custom_prompt')
            local_label = data.get('local_detection', 'Unknown')

            # Extract base64 payload
            if isinstance(image_data, str) and "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            raw_mode = str(request.form.get('mode', 'identify')).strip().lower()
            raw_voice = request.form.get('custom_prompt')
            local_label = request.form.get('local_detection', 'Unknown')

            uploaded = request.files.get('image')
            if not uploaded:
                return jsonify({"result": "<p style='color:red; font-weight:bold;'>Error: Missing image upload</p>"}), 400
            image = Image.open(uploaded.stream)

        # Normalize image mode (avoids edge cases with PNG/HEIC conversions)
        try:
            image = image.convert('RGB')
        except Exception:
            pass

        # --------------------------------------------
        # 2) SMART INPUT SANITIZATION
        # --------------------------------------------
        user_voice_prompt = None
        if raw_voice and isinstance(raw_voice, str):
            clean_voice = raw_voice.strip()
            if clean_voice and clean_voice.lower() not in ['null', 'undefined', '']:
                user_voice_prompt = clean_voice

        print(f"🔍 DEBUG -> Mode: '{raw_mode}' | Voice: '{user_voice_prompt}' | Label: '{local_label}'", flush=True)

        # --------------------------------------------
        # 3) CONSTRUCT ROBUST PROMPTS
        # --------------------------------------------
        hint_block = ""
        if local_label != "Unknown":
            hint_block = f"CONTEXT: Camera detected '{local_label}'. Use this to refine your analysis."

        # A) VOICE OVERRIDE (Only if user actually spoke)
        if user_voice_prompt:
            print("--- EXECUTION: VOICE MODE ---", flush=True)
            sys_instruction = f"""
            You are an expert Electronics Engineer acting as a real-time lab assistant.
            {hint_block}

            The user is asking: "{user_voice_prompt}"

            1. Answer the specific question directly.
            2. If asking for code, wrap it in <pre><code> tags.
            3. If asking for wiring, provide a clear HTML Table.
            4. Keep responses concise and use strict HTML formatting.
            """
            user_message = f"Answer this specific question about the image: {user_voice_prompt}"

        # B) CONNECT & CODE MODE (Aggressive Engineering Mode)
        elif raw_mode == 'connect':
            print("--- EXECUTION: CONNECT MODE ---", flush=True)
            sys_instruction = f"""
            You are a Senior Embedded Systems Architect.
            {hint_block}

            TASK: The user wants to build a circuit with this hardware.

            MANDATORY OUTPUT SECTIONS (Use strict HTML):

            <h3>1. Hardware Analysis</h3> 
            <p>Brief summary of what components are visible and how they should interact.</p>

            <h3>2. Wiring Diagram</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><th>Component Pin</th><th>Controller Pin</th><th>Note</th></tr>
                </table>

            <h3>3. Firmware Implementation</h3>
            <p>Complete, minimal, working code (C++ for Arduino, MicroPython for others):</p>
            <pre><code>
            // Your code here
            </code></pre>
            """
            user_message = "Analyze connections, generate a wiring table, and write the firmware code."

        # C) SCAN MODE (Identification Mode - Default)
        else:
            print("--- EXECUTION: IDENTIFY MODE ---", flush=True)
            sys_instruction = f"""
            You are a Senior Hardware Analyst.
            {hint_block}

            TASK: Identify components with extreme precision. Do NOT write code. Focus on hardware specs.

            MANDATORY OUTPUT SECTIONS (Use strict HTML):

            <h3>1. Component Identification</h3>
            <ul>
                <li><b>Name:</b> [Exact Model]</li>
                <li><b>Main Chip:</b> [e.g. RP2040, ESP32-S3, ATmega328P]</li>
                <li><b>Logic Voltage:</b> [e.g. 3.3V, 5V]</li>
            </ul>

            <h3>2. Technical Specs</h3>
            <ul>
                <li><b>Pins:</b> [GPIO count/type]</li>
                <li><b>Power:</b> [Input voltage range]</li>
                <li><b>Protocols:</b> [I2C, SPI, UART, etc]</li>
            </ul>

            <h3>3. Datasheet Summary</h3>
            <p>[Critical usage warnings, pinout details, or best practices]</p>
            """
            user_message = "Perform a technical hardware scan of this image and identify the specs."

        # --------------------------------------------
        # 4) CALL GEMINI
        # --------------------------------------------
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[user_message, image],
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.3,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1500,
                response_mime_type="text/plain",
            )
        )

        return jsonify({"result": clean_response(response.text)})

    except Exception as e:
        print(f"❌ ERROR: {e}", flush=True)
        return jsonify({"result": f"<p style='color:red; font-weight:bold;'>Error: {str(e)}</p>"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6999)

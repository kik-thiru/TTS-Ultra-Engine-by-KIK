from flask import Flask, render_template, request, send_file
import asyncio
import edge_tts
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

async def generate_audio(text, voice, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)

@app.route('/')
def index():
    return render_template('index.html')

voice_database = {
    'ta-IN': {
        'Female': ['ta-IN-PallaviNeural'],
        'Male': ['ta-IN-ValluvarNeural']
    },
    'ta-LK': {
        'Female': ['ta-LK-SaranyaNeural'],
        'Male': ['ta-LK-KumarNeural']
    },
    'ta-SG': {
        'Female': ['ta-SG-VenbaNeural'],
        'Male': ['ta-SG-AnbuNeural']
    },
    'en-IN': {
        'Female': ['en-IN-NeerjaNeural'],
        'Male': ['en-IN-PrabhatNeural']
    },
    'en-US': {
        'Female': ['en-US-AriaNeural', 'en-US-EmmaNeural', 'en-US-JennyNeural'],
        'Male': ['en-US-GuyNeural', 'en-US-AndrewNeural', 'en-US-BrianNeural']
    },
    'hi-IN': {
        'Female': ['hi-IN-SwaraNeural', 'hi-IN-AnanyaNeural'],
        'Male': ['hi-IN-MadhurNeural']
    },
    'es-ES': {
        'Female': ['es-ES-ElviraNeural', 'es-ES-EstrellaNeural'],
        'Male': ['es-ES-AlvaroNeural', 'es-ES-SaulNeural']
    },
    'fr-FR': {
        'Female': ['fr-FR-DeniseNeural', 'fr-FR-BrigitteNeural'],
        'Male': ['fr-FR-HenriNeural', 'fr-FR-AlainNeural']
    },
    'de-DE': {
        'Female': ['de-DE-KatjaNeural', 'de-DE-AmalaNeural'],
        'Male': ['de-DE-ConradNeural', 'de-DE-KillianNeural']
    },
    'te-IN': {'Female': ['te-IN-ShrutiNeural'], 'Male': ['te-IN-MohanNeural']},
    'ml-IN': {'Female': ['ml-IN-SobhanaNeural'], 'Male': ['ml-IN-MidhunNeural']},
    'kn-IN': {'Female': ['kn-IN-SapnaNeural'], 'Male': ['kn-IN-GaganNeural']},
    'ur-IN': {'Female': ['ur-IN-UzmaNeural'], 'Male': ['ur-IN-AsadNeural']},
    'or-IN': {'Female': ['or-IN-SubhadraNeural'], 'Male': ['or-IN-KishoreNeural']},
    'bn-IN': {'Female': ['bn-IN-TanishaNeural'], 'Male': ['bn-IN-BashkarNeural']},
    'gu-IN': {'Female': ['bn-IN-TanishaNeural', 'gu-IN-DhwaniNeural'], 'Male': ['gu-IN-NiranjanNeural']},
    'mr-IN': {'Female': ['mr-IN-AarohiNeural'], 'Male': ['mr-IN-ManoharNeural']},
    'pa-IN': {'Female': ['pa-IN-OjasviNeural'], 'Male': ['pa-IN-AnmolNeural']},
    'ne-NP': {'Female': ['ne-NP-HemkalaNeural'], 'Male': ['ne-NP-SagarNeural']},
    'ar-SA': {'Female': ['ar-SA-ZariyahNeural'], 'Male': ['ar-SA-HamedNeural']},
    'it-IT': {'Female': ['it-IT-ElsaNeural'], 'Male': ['it-IT-DiegoNeural']},
    'pt-BR': {'Female': ['pt-BR-FranciscaNeural'], 'Male': ['pt-BR-AntonioNeural']},
    'ja-JP': {'Female': ['ja-JP-NanamiNeural'], 'Male': ['ja-JP-KeitaNeural']},
    'zh-CN': {'Female': ['zh-CN-XiaoxiaoNeural'], 'Male': ['zh-CN-YunxiNeural']}
}

def get_selected_voice(lang, gender, voice_index=0):
    lang_data = voice_database.get(lang, {'Female': [f'{lang}-FemaleNeural'], 'Male': [f'{lang}-MaleNeural']})
    voices = lang_data.get(gender, lang_data.get('Female', [f'{lang}-FemaleNeural']))
    if voice_index < len(voices):
        return voices[voice_index]
    return voices[0]

@app.route('/convert', methods=['POST'])
def convert():
    output_file = os.path.join(BASE_DIR, "output.mp3")
    if os.path.exists(output_file):
        try: os.remove(output_file)
        except: pass

    try:
        text = request.form.get('text', '')
        lang = request.form.get('lang', 'ta-IN')
        gender = request.form.get('gender', 'Female')
        voice_index = int(request.form.get('voice_index', 0))
        rate = request.form.get('rate', '+0%')
        pitch = request.form.get('pitch', '+0Hz')

        if not text.strip():
            return "Text cannot be empty", 400

        selected_voice = get_selected_voice(lang, gender, voice_index)
        asyncio.run(generate_audio(text, selected_voice, rate, pitch, output_file))

        if os.path.exists(output_file):
            return send_file(output_file, mimetype="audio/mpeg")
        else:
            return "Audio generation failed.", 500
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

@app.route('/preview', methods=['POST'])
def preview():
    try:
        lang = request.form.get('lang', 'ta-IN')
        gender = request.form.get('gender', 'Female')
        voice_index = int(request.form.get('voice_index', 0))
        rate = request.form.get('rate', '+0%')
        pitch = request.form.get('pitch', '+0Hz')

        sample_texts = {
            'ta': 'வணக்கம், இது குரல் சோதனை.',
            'hi': 'नमस्ते, यह आवाज़ का परीक्षण है।',
            'es': 'Hola, esta es una prueba de voz.',
            'fr': 'Bonjour, ceci est un test vocal.',
            'de': 'Hallo, dies ist ein Sprachtest.',
            'te': 'నమస్కారం, ఇది వాయిస్ పరీక్ష.',
            'ml': 'നമസ്കാരം, ഇത് ഒരു ശബ്ദ പരിശോധനയാണ്.',
            'kn': 'ನಮಸ್ಕಾರ, ಇದು ಧ್ವನಿ ಪರೀಕ್ಷೆ.',
            'ur': 'ہیلو، یہ ایک صوتی ٹیسٹ ہے۔',
            'bn': 'হ্যালো, এটি একটি ভয়েস পরীক্ষা।',
            'ne': 'नमस्कार, यो आवाज परीक्षण हो।',
            'ar': 'مرحباً، هذا اختبار صوتي.',
            'it': 'Ciao, questo è un test vocale.',
            'pt': 'Olá, este é um teste de voz.',
            'ja': 'こんにちは、これは音声テストです。',
            'zh': '你好，这是语音测试。'
        }

        prefix = lang[:2]
        text = sample_texts.get(prefix, 'Hello, this is a voice sample preview.')

        selected_voice = get_selected_voice(lang, gender, voice_index)
        preview_file = os.path.join(BASE_DIR, "preview.mp3")

        if os.path.exists(preview_file):
            try: os.remove(preview_file)
            except: pass

        async def create_preview():
            communicate = edge_tts.Communicate(text, selected_voice, rate=rate, pitch=pitch)
            await communicate.save(preview_file)

        asyncio.run(create_preview())

        if os.path.exists(preview_file):
            return send_file(preview_file, mimetype="audio/mpeg")
        else:
            return "Preview failed", 500
    except Exception as e:
        return str(e), 500

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    try:
        name = request.form.get('name', 'Anonymous')
        person_type = request.form.get('person_type', 'Normal Person')
        comment = request.form.get('comment', '')

        if not comment.strip():
            return "Comment cannot be empty", 400

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feedback_file = os.path.join(BASE_DIR, "feedback.txt")
        
        feedback_entry = f"--- Feedback ---\nDate & Time: {current_time}\nName: {name if name.strip() else 'Anonymous'}\nCategory: {person_type}\nComment: {comment}\n--------------------\n\n"

        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(feedback_entry)

        return "Feedback saved successfully", 200
    except Exception as e:
        print(f"Feedback Error: {str(e)}")
        return str(e), 500

@app.route('/view_feedback', methods=['GET', 'POST'])
def view_feedback():
    ADMIN_PASSWORD = "KIK/comkge@15"  # உங்களது ரகசிய பாஸ்வேர்ட்
    logged_in = False
    error = ""
    content = ""

    if request.method == 'POST':
        password = request.form.get('password', '')
        if password != ADMIN_PASSWORD:
            error = "Wrong Password!"
            logged_in = False
        else:
            logged_in = True
            feedback_file = os.path.join(BASE_DIR, "feedback.txt")
            if os.path.exists(feedback_file):
                with open(feedback_file, "r", encoding="utf-8") as f:
                    content = f.read()

    return render_template('view_feedback.html', logged_in=logged_in, error=error, content=content)

if __name__ == '__main__':
    app.run(debug=True)

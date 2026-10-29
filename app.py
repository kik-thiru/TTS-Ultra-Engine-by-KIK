import asyncio
from datetime import datetime, timedelta
import os
import edge_pss  # unused, kept clean
import edge_tts
from flask import Flask, redirect, render_template, request, send_file, url_for
import psycopg2
import psycopg2.extras

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Render Internal Database URL
DATABASE_URL = "postgresql://tts_feedback_database_user:wJJTpPaOBBVBCg1RsNtqXFuz9oX6wJ9c@dpg-dbhdsno8v5cc7387f1s0-a/tts_feedback_database"


# டேட்டாபேஸ் மற்றும் டேபிளை உருவாக்கும் பங்க்ஷன்
def init_db():
  try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                person_type TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    cur.close()
    conn.close()
  except Exception as e:
    print(f"Database Initialization Error: {e}")


# அப்ளிகேஷன் ஸ்டார்ட் ஆகும்போது டேபிளை உறுதி செய்கிறோம்
init_db()


async def generate_audio(text, voice, rate, pitch, output_path):
  communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
  await communicate.save(output_path)


@app.route("/")
def index():
  return render_template("index.html")


voice_database = {
    "ta-IN": {"Female": ["ta-IN-PallaviNeural"], "Male": ["ta-IN-ValluvarNeural"]},
    "ta-LK": {"Female": ["ta-LK-SaranyaNeural"], "Male": ["ta-LK-KumarNeural"]},
    "ta-SG": {"Female": ["ta-SG-VenbaNeural"], "Male": ["ta-SG-AnbuNeural"]},
    "en-IN": {"Female": ["en-IN-NeerjaNeural"], "Male": ["en-IN-PrabhatNeural"]},
    "en-US": {
        "Female": [
            "en-US-AriaNeural",
            "en-US-EmmaNeural",
            "en-US-JennyNeural",
        ],
        "Male": ["en-US-GuyNeural", "en-US-AndrewNeural", "en-US-BrianNeural"],
    },
    "hi-IN": {
        "Female": ["hi-IN-SwaraNeural", "hi-IN-AnanyaNeural"],
        "Male": ["hi-IN-MadhurNeural"],
    },
    "es-ES": {
        "Female": ["es-ES-ElviraNeural", "es-ES-EstrellaNeural"],
        "Male": ["es-ES-AlvaroNeural", "es-ES-SaulNeural"],
    },
    "fr-FR": {
        "Female": ["fr-FR-DeniseNeural", "fr-FR-BrigitteNeural"],
        "Male": ["fr-FR-HenriNeural", "fr-FR-AlainNeural"],
    },
    "de-DE": {
        "Female": ["de-DE-KatjaNeural", "de-DE-AmalaNeural"],
        "Male": ["de-DE-ConradNeural", "de-DE-KillianNeural"],
    },
    "te-IN": {"Female": ["te-IN-ShrutiNeural"], "Male": ["te-IN-MohanNeural"]},
    "ml-IN": {"Female": ["ml-IN-SobhanaNeural"], "Male": ["ml-IN-MidhunNeural"]},
    "kn-IN": {"Female": ["kn-IN-SapnaNeural"], "Male": ["kn-IN-GaganNeural"]},
    "ur-IN": {"Female": ["ur-IN-UzmaNeural"], "Male": ["ur-IN-AsadNeural"]},
    "or-IN": {
        "Female": ["or-IN-SubhadraNeural"],
        "Male": ["or-IN-KishoreNeural"],
    },
    "bn-IN": {"Female": ["bn-IN-TanishaNeural"], "Male": ["bn-IN-BashkarNeural"]},
    "gu-IN": {
        "Female": ["bn-IN-TanishaNeural", "gu-IN-DhwaniNeural"],
        "Male": ["gu-IN-NiranjanNeural"],
    },
    "mr-IN": {"Female": ["mr-IN-AarohiNeural"], "Male": ["mr-IN-ManoharNeural"]},
    "pa-IN": {"Female": ["pa-IN-OjasviNeural"], "Male": ["pa-IN-AnmolNeural"]},
    "ne-NP": {"Female": ["ne-NP-HemkalaNeural"], "Male": ["ne-NP-SagarNeural"]},
    "ar-SA": {"Female": ["ar-SA-ZariyahNeural"], "Male": ["ar-SA-HamedNeural"]},
    "it-IT": {"Female": ["it-IT-ElsaNeural"], "Male": ["it-IT-DiegoNeural"]},
    "pt-BR": {
        "Female": ["pt-BR-FranciscaNeural"],
        "Male": ["pt-BR-AntonioNeural"],
    },
    "ja-JP": {"Female": ["ja-JP-NanamiNeural"], "Male": ["ja-JP-KeitaNeural"]},
    "zh-CN": {"Female": ["zh-CN-XiaoxiaoNeural"], "Male": ["zh-CN-YunxiNeural"]},
}


def get_selected_voice(lang, gender, voice_index=0):
  lang_data = voice_database.get(
      lang,
      {"Female": [f"{lang}-FemaleNeural"], "Male": [f"{lang}-MaleNeural"]},
  )
  voices = lang_data.get(gender, lang_data.get("Female", [f"{lang}-FemaleNeural"]))
  if voice_index < len(voices):
    return voices[voice_index]
  return voices[0]


@app.route("/convert", methods=["POST"])
def convert():
  output_file = os.path.join(BASE_DIR, "output.mp3")
  if os.path.exists(output_file):
    try:
      os.remove(output_file)
    except:
      pass

  try:
    text = request.form.get("text", "")
    lang = request.form.get("lang", "ta-IN")
    gender = request.form.get("gender", "Female")
    voice_index = int(request.form.get("voice_index", 0))
    rate = request.form.get("rate", "+0%")
    pitch = request.form.get("pitch", "+0Hz")

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


@app.route("/preview", methods=["POST"])
def preview():
  try:
    lang = request.form.get("lang", "ta-IN")
    gender = request.form.get("gender", "Female")
    voice_index = int(request.form.get("voice_index", 0))
    rate = request.form.get("rate", "+0%")
    pitch = request.form.get("pitch", "+0Hz")

    sample_texts = {
        "ta": "வணக்கம், இது குரல் சோதனை.",
        "hi": "नमस्ते, यह आवाज़ का परीक्षण है।",
        "es": "Hola, esta es una prueba de voz.",
        "fr": "Bonjour, ceci est un test vocal.",
        "de": "Hallo, dies ist ein Sprachtest.",
        "te": "నమస్కారం, ఇది వాయిస్ పరీక్ష.",
        "ml": "നമസ്കാരം, ഇത് ഒരു ശബ്ദ പരിശോധനയാണ്.",
        "kn": "ನಮಸ್ಕಾರ, ಇದು ಧ್ವನಿ ಪರೀಕ್ಷೆ.",
        "ur": "ہیلو، یہ ایک صوتی ٹیسٹ ہے۔",
        "bn": "হ্যালো, এটি একটি ভয়েস পরীক্ষা।",
        "ne": "नमस्कार, यो आवाज परीक्षण हो।",
        "ar": "مرحباً، هذا اختبار صوتي.",
        "it": "Ciao, questo è un test vocale.",
        "pt": "Olá, este é um teste de voz.",
        "ja": "こんにちは、これは音声テストです。",
        "zh": "你好，这是语音测试。",
    }

    prefix = lang[:2]
    text = sample_texts.get(prefix, "Hello, this is a voice sample preview.")

    selected_voice = get_selected_voice(lang, gender, voice_index)
    preview_file = os.path.join(BASE_DIR, "preview.mp3")

    if os.path.exists(preview_file):
      try:
        os.remove(preview_file)
      except:
        pass

    async def create_preview():
      communicate = edge_tts.Communicate(
          text, selected_voice, rate=rate, pitch=pitch
      )
      await communicate.save(preview_file)

    asyncio.run(create_preview())

    if os.path.exists(preview_file):
      return send_file(preview_file, mimetype="audio/mpeg")
    else:
      return "Preview failed", 500
  except Exception as e:
    return str(e), 500


# ஃபீட்பேக்கை டேட்டாபேஸில் சேமிக்கும் ரவுட்
@app.route("/send_feedback", methods=["POST"])
def send_feedback():
  try:
    name = request.form.get("name", "Anonymous")
    person_type = request.form.get("person_type", "Normal Person")
    comment = request.form.get("comment", "")

    if not comment.strip():
      return "Comment cannot be empty", 400

    clean_name = name.strip() if name.strip() else "Anonymous"

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedback (name, person_type, comment) VALUES (%s, %s, %s)",
        (clean_name, person_type, comment),
    )
    conn.commit()
    cur.close()
    conn.close()

    return "Feedback saved successfully", 200
  except Exception as e:
    print(f"Feedback DB Error: {str(e)}")
    return str(e), 500


# மேம்படுத்தப்பட்ட அட்மின் டேஷ்போர்டு & டெலீட் கன்ட்ரோல்ஸ்
@app.route("/view_feedback", methods=["GET", "POST"])
def view_feedback():
  ADMIN_PASSWORD = "KIK/comkge@15"
  password = request.form.get("password") or request.args.get("password")

  # பாஸ்வேர்ட் சரிபார்ப்பு
  if password != ADMIN_PASSWORD:
    # முதல் முறை லாகின் செய்யும்போது அல்லது தவறுதலாக இருந்தால் லாகின் பேஜ் காட்டப்படும்
    # GET அல்லது POST-ல் தவறான பாஸ்வேர்ட் வந்தால் error காட்டலாம்
    error = "Wrong Password!" if request.method == "POST" else ""
    return render_template(
        "view_feedback.html", logged_in=False, error=error, content=""
    )

  try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # டெலீட் ஆப்ஷன்கள் கையாளுதல்
    action = request.form.get("action")

    if action == "delete_one":
      feedback_id = request.form.get("feedback_id")
      cur.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
      conn.commit()

    elif action == "delete_all":
      cur.execute("DELETE FROM feedback")
      conn.commit()

    elif action == "delete_time":
      time_filter = request.form.get("time_filter")
      now = datetime.now()

      if time_filter == "1_hour":
        limit_time = now - timedelta(hours=1)
      elif time_filter == "24_hours":
        limit_time = now - timedelta(days=1)
      elif time_filter == "7_days":
        limit_time = now - timedelta(days=7)
      elif time_filter == "30_days":
        limit_time = now - timedelta(days=30)
      else:
        limit_time = None

      if limit_time:
        cur.execute("DELETE FROM feedback WHERE created_at >= %s", (limit_time,))
        conn.commit()

    # சர்ச் மற்றும் ஃபீட்பேக் பட்டியல் எடுப்பது
    search_query = request.args.get("search", "").strip()
    if search_query:
      cur.execute(
          "SELECT * FROM feedback WHERE name ILIKE %s OR comment ILIKE %s OR"
          " person_type ILIKE %s ORDER BY created_at DESC",
          (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"),
      )
    else:
      cur.execute("SELECT * FROM feedback ORDER BY created_at DESC")

    feedbacks = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "view_feedback.html",
        logged_in=True,
        feedbacks=feedbacks,
        password=password,
        search=search_query,
    )

  except Exception as e:
    print(f"Admin Dashboard Error: {e}")
    return f"Database Error: {e}", 500


if __name__ == "__main__":
  app.run(debug=True)

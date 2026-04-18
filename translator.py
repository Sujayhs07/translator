"""
English ↔ Kannada Translator with Text-to-Speech (Both directions)
===================================================================
Requirements:
    pip install streamlit anthropic gtts

Run:
    streamlit run kannada_translator.py

Set your API key either:
  - As an environment variable:  export ANTHROPIC_API_KEY="sk-ant-..."
  - Or enter it in the sidebar inside the app
"""

import io
import os
import base64
import streamlit as st
import anthropic
from gtts import gTTS

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="English ↔ Kannada Translator",
    page_icon="ಕ",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Georgia', serif; }
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    .block-container { max-width: 800px; padding-top: 2rem; }
    label { font-size: 0.85rem !important; font-weight: 600 !important; }

    div.stButton > button[kind="primary"] {
        background-color: #C85A2B;
        border-color: #C85A2B;
        color: #fff;
        font-weight: 600;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #a8471f;
        border-color: #a8471f;
    }

    .output-box {
        background: #fffdf9;
        border: 1px solid #ddd9d0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        font-size: 1.1rem;
        line-height: 1.8;
        min-height: 120px;
        color: #1a1915;
        margin-top: 0.25rem;
        word-break: break-word;
        white-space: pre-wrap;
    }
    .output-placeholder {
        color: #b0aaa0;
        font-style: italic;
    }
    .success-box {
        background: #ebf5ef;
        border: 1px solid #5baa7a;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: #1a4a2e;
        font-size: 0.88rem;
        margin-top: 0.5rem;
    }
    .lang-badge {
        display: inline-block;
        background: #FAF0EB;
        border: 1px solid #C85A2B;
        color: #C85A2B;
        border-radius: 99px;
        padding: 2px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at https://console.anthropic.com"
    )
    st.caption("Or set the `ANTHROPIC_API_KEY` environment variable.")
    st.divider()
    st.markdown("**How it works:**")
    st.markdown(
        "1. Type English text\n"
        "2. **Translate** → see Kannada\n"
        "3. **Speak English** → hear English audio\n"
        "4. **Speak Kannada** → hear Kannada audio"
    )

api_key = api_key_input.strip() or os.environ.get("ANTHROPIC_API_KEY", "")


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## ಕ &nbsp; English ↔ Kannada Translator")
st.caption("Translate text · Hear it in English · Hear it in Kannada")
st.divider()


# ── Helpers ────────────────────────────────────────────────────────────────────
def translate_to_kannada(text: str, key: str) -> str:
    """Call Claude API and return the Kannada translation."""
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=(
            "You are a professional English-to-Kannada translator. "
            "Translate the user's English text into natural, fluent Kannada script. "
            "Return ONLY the Kannada translation — no explanations, no romanisation, "
            "no English text, no commentary. Just the Kannada text."
        ),
        messages=[{"role": "user", "content": text}],
    )
    return msg.content[0].text.strip()


def make_audio(text: str, lang: str) -> bytes:
    """Generate MP3 bytes via gTTS. lang='en' for English, 'kn' for Kannada."""
    tts = gTTS(text=text, lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def audio_player(audio_bytes: bytes, label: str):
    """Render an autoplay HTML5 audio player."""
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(f"""
    <p style="font-size:0.85rem;color:#7a756a;margin-bottom:4px;">{label}</p>
    <audio autoplay controls style="width:100%;margin-bottom:0.5rem;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3" />
        Your browser does not support audio.
    </audio>
    """, unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────────
for _k in ("kannada_result", "last_english"):
    if _k not in st.session_state:
        st.session_state[_k] = ""
for _k in ("audio_en", "audio_kn"):
    if _k not in st.session_state:
        st.session_state[_k] = None


# ══════════════════════════════════════════════════════════════════════════════
# ENGLISH INPUT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lang-badge">🇬🇧 English — Input</div>', unsafe_allow_html=True)

english_text = st.text_area(
    "✍️ Enter English text",
    placeholder="Type or paste your English text here…",
    height=160,
    max_chars=1000,
    key="english_input",
)
st.caption(f"{len(english_text)} / 1,000 characters")

col1, col2, col3 = st.columns([3, 3, 2])

with col1:
    translate_btn = st.button(
        "🌐 Translate → Kannada",
        type="primary",
        use_container_width=True,
        disabled=not english_text.strip(),
    )
with col2:
    speak_en_btn = st.button(
        "🔊 Speak in English",
        use_container_width=True,
        disabled=not english_text.strip(),
    )
with col3:
    clear_btn = st.button("✕ Clear All", use_container_width=True)


# ── Clear all ──────────────────────────────────────────────────────────────────
if clear_btn:
    st.session_state.kannada_result = ""
    st.session_state.last_english   = ""
    st.session_state.audio_en       = None
    st.session_state.audio_kn       = None
    st.rerun()


# ── Translate ──────────────────────────────────────────────────────────────────
if translate_btn:
    if not api_key:
        st.error("⚠️ No API key found. Paste your Anthropic API key in the sidebar.")
    elif not english_text.strip():
        st.warning("Please enter some English text first.")
    else:
        with st.spinner("Translating to Kannada…"):
            try:
                result = translate_to_kannada(english_text.strip(), api_key)
                st.session_state.kannada_result = result
                st.session_state.last_english   = english_text.strip()
                st.session_state.audio_en       = None
                st.session_state.audio_kn       = None
            except anthropic.AuthenticationError:
                st.error("❌ Invalid API key. Please check the sidebar.")
            except anthropic.RateLimitError:
                st.error("❌ Rate limit reached. Please wait and try again.")
            except Exception as e:
                st.error(f"❌ Translation error: {e}")


# ── Speak English ──────────────────────────────────────────────────────────────
if speak_en_btn:
    if not english_text.strip():
        st.warning("Please enter some English text first.")
    else:
        with st.spinner("Generating English audio…"):
            try:
                st.session_state.audio_en = make_audio(english_text.strip(), "en")
                st.session_state.audio_kn = None
            except Exception as e:
                st.error(f"❌ English TTS error: {e}")


# ── English audio player ───────────────────────────────────────────────────────
if st.session_state.audio_en:
    audio_player(st.session_state.audio_en, "🔊 Speaking in English")


# ══════════════════════════════════════════════════════════════════════════════
# KANNADA OUTPUT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="lang-badge">🇮🇳 ಕನ್ನಡ — Kannada Output</div>', unsafe_allow_html=True)

if st.session_state.kannada_result:
    # Show translated text
    st.markdown(
        f'<div class="output-box">{st.session_state.kannada_result}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="success-box">✅ Translation complete!</div>',
        unsafe_allow_html=True,
    )

    # Copy helper
    with st.expander("📋 Copy Kannada text"):
        st.code(st.session_state.kannada_result, language=None)
        st.caption("Select all (Ctrl+A) → Copy (Ctrl+C)")

    # Speak Kannada button
    st.markdown("")
    speak_kn_btn = st.button(
        "🔊 Speak in Kannada",
        use_container_width=False,
    )

    if speak_kn_btn:
        with st.spinner("Generating Kannada audio…"):
            try:
                st.session_state.audio_kn = make_audio(
                    st.session_state.kannada_result, "kn"
                )
                st.session_state.audio_en = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Kannada TTS error: {e}")

else:
    st.markdown(
        '<div class="output-box output-placeholder">'
        'Kannada translation will appear here after you click Translate…'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Kannada audio player ───────────────────────────────────────────────────────
if st.session_state.audio_kn:
    audio_player(st.session_state.audio_kn, "🔊 Speaking in Kannada")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Powered by [Claude (Anthropic)](https://www.anthropic.com) · "
    "TTS by [gTTS](https://gtts.readthedocs.io) · "
    "Built with [Streamlit](https://streamlit.io)"
)
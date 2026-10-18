from pathlib import Path

from utils.ambient_audio import AMBIENT_AUDIO_HTML


def test_ambient_audio_offers_local_track_by_user_action_without_synth():
    assert 'button.addEventListener("click"' in AMBIENT_AUDIO_HTML
    assert 'button.textContent = "▶ Play"' in AMBIENT_AUDIO_HTML
    assert "autoplay" not in AMBIENT_AUDIO_HTML.lower()
    assert "http://" not in AMBIENT_AUDIO_HTML
    assert "https://" not in AMBIENT_AUDIO_HTML
    assert "AudioContext" not in AMBIENT_AUDIO_HTML
    assert "Original ambient synth" not in AMBIENT_AUDIO_HTML
    assert 'id="volume"' in AMBIENT_AUDIO_HTML
    assert "localStorage.setItem" in AMBIENT_AUDIO_HTML
    assert "Can You Hear The Music" in AMBIENT_AUDIO_HTML
    assert 'src="/app/static/audio/oppenheimer_theme.mp3"' in AMBIENT_AUDIO_HTML
    assert 'await track.play()' in AMBIENT_AUDIO_HTML
    assert "Couldn't play the track" in AMBIENT_AUDIO_HTML


def test_application_shell_includes_the_global_audio_control():
    project = Path(__file__).parents[1]
    app_source = (project / "app.py").read_text()
    config_source = (project / ".streamlit" / "config.toml").read_text()

    assert "from utils.ambient_audio import AMBIENT_AUDIO_HTML" in app_source
    assert "st.components.v1.html(AMBIENT_AUDIO_HTML" in app_source
    assert "enableStaticServing = true" in config_source
    assert (project / "static" / "audio" / "oppenheimer_theme.mp3").is_file()

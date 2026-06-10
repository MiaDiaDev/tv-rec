"""Gradio user interface for German TV Recommender."""

import gradio as gr
from typing import List
from app.models.schemas import UserPreferences, Recommendation
from app.services.recommender import recommender_service
from app.utils.genre_mapper import STANDARD_GENRES, MOOD_TO_GENRES


def format_recommendation(rec: Recommendation) -> str:
    """
    Format a recommendation as HTML.

    Args:
        rec: Recommendation object

    Returns:
        HTML formatted string
    """
    # Format start time
    if rec.start_time:
        time_str = rec.start_time.strftime("%H:%M Uhr")
    else:
        time_str = "Auf Abruf"

    # Format duration
    duration_min = rec.duration_minutes
    duration_str = f"{duration_min} Min."

    # Format genres
    genres_str = ", ".join(rec.genres) if rec.genres else "Unterhaltung"

    # Content type badge
    type_badge = "🎬 Film" if rec.content_type == "movie" else "📺 Serie"

    # Source badge
    source_badge = "📡 Live TV" if rec.is_live else "🎥 Mediathek"

    # Build HTML
    html = f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <h3 style="margin: 0 0 8px 0; color: #333;">{rec.title}</h3>
                <p style="margin: 4px 0; color: #666;">
                    <strong>{rec.channel}</strong> | {time_str} | {duration_str}
                </p>
                <p style="margin: 4px 0;">
                    <span style="background: #e3f2fd; padding: 2px 8px; border-radius: 4px; font-size: 0.9em;">{type_badge}</span>
                    <span style="background: #f3e5f5; padding: 2px 8px; border-radius: 4px; font-size: 0.9em; margin-left: 5px;">{source_badge}</span>
                </p>
                <p style="margin: 8px 0; color: #888; font-size: 0.9em;">{genres_str}</p>
            </div>
        </div>
        {f'<p style="margin: 10px 0 0 0; color: #555;">{rec.description}</p>' if rec.description else ''}
        {f'<a href="{rec.url_video}" target="_blank" style="display: inline-block; margin-top: 10px; color: #1976d2;">▶ Video ansehen</a>' if rec.url_video else ''}
    </div>
    """
    return html


def get_recommendations_ui(
    mood: str,
    genres: List[str],
    content_type: str,
    include_live: bool,
    include_mediathek: bool
) -> str:
    """
    Get recommendations based on user input.

    Args:
        mood: User's mood
        genres: Selected genres
        content_type: Content type filter (German labels)
        include_live: Include live TV
        include_mediathek: Include Mediathek

    Returns:
        HTML formatted recommendations
    """
    try:
        # Map German UI labels to internal values
        content_type_map = {
            "Alle": None,
            "Film": "movie",
            "Serie": "show"
        }
        internal_content_type = content_type_map.get(content_type)

        # Create preferences
        preferences = UserPreferences(
            mood=mood,
            genres=genres if genres else [],
            content_type=internal_content_type
        )

        # Get recommendations
        recommendations = recommender_service.get_recommendations(
            preferences=preferences,
            include_live=include_live,
            include_mediathek=include_mediathek,
            limit=20
        )

        if not recommendations:
            return "<p style='color: #999; text-align: center; padding: 20px;'>Keine Empfehlungen gefunden. Bitte versuchen Sie andere Filter.</p>"

        # Format all recommendations
        html_output = f"<h2>🎯 {len(recommendations)} Empfehlungen für Sie</h2>"
        for rec in recommendations:
            html_output += format_recommendation(rec)

        return html_output

    except Exception as e:
        return f"<p style='color: red;'>Fehler beim Laden der Empfehlungen: {str(e)}</p>"


def create_ui():
    """Create and configure the Gradio interface."""

    # Available options
    moods = list(MOOD_TO_GENRES.keys())
    genres = sorted(list(STANDARD_GENRES))
    content_types = ["Alle", "Film", "Serie"]

    with gr.Blocks(title="German TV Recommender", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 📺 German TV Recommender

            Finden Sie heute Abend das perfekte Fernsehprogramm!
            Wählen Sie Ihre Stimmung und Vorlieben aus.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎭 Ihre Vorlieben")

                mood = gr.Dropdown(
                    choices=moods,
                    label="Stimmung",
                    value="entspannt",
                    info="Wie fühlen Sie sich heute?"
                )

                genre_select = gr.Dropdown(
                    choices=genres,
                    label="Genres",
                    multiselect=True,
                    info="Wählen Sie ein oder mehrere Genres (optional)"
                )

                content_type = gr.Radio(
                    choices=content_types,
                    label="Inhaltstyp",
                    value="Alle",
                    info="Film oder Serie?"
                )

                with gr.Row():
                    include_live = gr.Checkbox(
                        label="Live TV einbeziehen",
                        value=True
                    )
                    include_mediathek = gr.Checkbox(
                        label="Mediathek einbeziehen",
                        value=True
                    )

                recommend_btn = gr.Button(
                    "🔍 Empfehlungen anzeigen",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=2):
                gr.Markdown("### 📋 Ihre Empfehlungen")
                output = gr.HTML(
                    value="<p style='color: #999; text-align: center; padding: 20px;'>Wählen Sie Ihre Vorlieben und klicken Sie auf 'Empfehlungen anzeigen'</p>"
                )

        # Connect button to function
        recommend_btn.click(
            fn=get_recommendations_ui,
            inputs=[mood, genre_select, content_type, include_live, include_mediathek],
            outputs=output
        )

        gr.Markdown(
            """
            ---

            **Datenquellen:** ARD/ZDF Mediathek • TVprofil.net EPG

            **Hinweis:** Die App zeigt heute Abend verfügbare Sendungen und On-Demand-Inhalte.
            """
        )

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

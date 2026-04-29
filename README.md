# Star Catcher - Streamlit Version

This is a Streamlit-ready version of the interactive Star Catcher game.

Important note: Streamlit Community Cloud does not display a normal Pygame window like a desktop app. For this reason, the game logic was adapted into an HTML5 Canvas game embedded inside Streamlit using `streamlit.components.v1.html`.

## Game Controls

- Desktop: Left/Right arrows or A/D
- Mobile: tap and hold the left or right side of the game area
- Goal: catch stars, avoid meteors, and survive for 60 seconds

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `README.md`
3. Go to Streamlit Community Cloud.
4. Click **New app**.
5. Choose your GitHub repository.
6. Set the main file path to:

```text
app.py
```

7. Click **Deploy**.

Your game will be available as a shareable Streamlit link.

## Project Structure

```text
starcatcher_streamlit/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

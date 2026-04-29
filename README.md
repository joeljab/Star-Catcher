# Star Catcher - Pygame Web Game

This is a simple interactive Pygame game that can run locally on a computer and can also be packaged for the web using **Pygbag**, so students can open it from a simple browser link.

## Game idea

The player controls a basket at the bottom of the screen.

- Catch yellow stars to increase the score.
- Avoid red meteors.
- Survive for 60 seconds.
- Controls:
  - Keyboard: Left / Right arrows or A / D
  - Browser/mobile: tap or click the left/right side of the game screen

## Run locally

```bash
pip install pygame-ce
python main.py
```

If `pygame-ce` does not work on your setup, use:

```bash
pip install pygame
python main.py
```

## Run in browser locally with Pygbag

Install Pygbag:

```bash
pip install pygbag
```

From inside this folder, run:

```bash
pygbag .
```

Then open the local link shown in the terminal, usually:

```text
http://localhost:8000
```

## Build web version

```bash
pygbag --build .
```

This creates a `build/web` folder. Upload the contents of `build/web` to GitHub Pages, Netlify, Itch.io, or any static hosting service.

## GitHub Pages option

This project includes a GitHub Actions workflow in:

```text
.github/workflows/deploy.yml
```

To get a simple link:

1. Create a GitHub repository.
2. Upload these files.
3. Go to **Settings > Pages**.
4. Set source to **GitHub Actions**.
5. Push to the `main` branch.
6. GitHub will publish the game as a web link.

Your final link will usually look like:

```text
https://YOUR-USERNAME.github.io/YOUR-REPOSITORY-NAME/
```

## Files

```text
main.py
requirements.txt
.github/workflows/deploy.yml
```

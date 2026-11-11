# AI Image Generator (Flask + Pillow)

Sqrock IT Solutions Python Internship — Phase 1, Task 4.

A web app that turns a text prompt into an image. Runs **offline out of the box**: it uses Pillow to render unique abstract art derived deterministically from the prompt (same prompt → same image), with the prompt caption overlaid.

## Features
- Text prompt input with clickable suggestions
- Generated image preview
- **Download** the generated PNG
- Loading spinner while generating
- Offline generator (gradient + translucent shapes + caption, seeded by the prompt)
- Clearly marked integration point (`live_image()`) to plug in a real text-to-image API via `IMAGE_API_KEY`
- Responsive dark UI

## Run
```bash
pip install -r requirements.txt
python app.py        # http://127.0.0.1:5000
```

### Live AI (optional)
Wire your preferred text-to-image API into `live_image()` in `app.py` and set `IMAGE_API_KEY`; the app switches to live mode automatically and falls back to the offline generator on any error.

## Tech
Python · Flask · Pillow (PIL) · HTML/CSS/JS · base64 image delivery.

**Author:** Ajvi Dylgjeri

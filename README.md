# 🍷 Premium Financial Modeling App

A next-generation Streamlit application for rapid scenario planning, investor-ready exports, and board-level reporting for consumer-product companies (initial template: craft winery / distillery).  
Built with a **dark-mode + gold** design system, interactive premium widgets, and one-click exports to pitch-deck PDF, Excel, and investment memo.

---

## 🌟 Core Features

| Category | Highlights |
|----------|------------|
| **Interactive UI** | Percentage allocator, scenario toggle, price inputs with live margin, quick-action presets |
| **Financial Engine** | Revenue, contribution margin, cash-flow, IRR/MOIC, payback, sensitivity grids (NumPy Financial) |
| **Magical Exports** | 5-slide pitch-deck PDF, print-ready Excel one-pager, markdown→PDF investment memo |
| **Collaboration** | Shareable links with time-limited access & QR codes |
| **Production UX** | Google Analytics, keyboard shortcuts (Cmd / Ctrl + K), global error boundary, lazy-loading & debounced sliders |

---

## 🛠️ Local Development

### 1. Clone & install

```bash
git clone https://github.com/your-org/premium-financial-app.git
cd premium-financial-app
python -m venv .venv              # optional but recommended
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` in the project root (auto-loaded by python-dotenv):

| Variable | Purpose | Example |
|----------|---------|---------|
| `GA_TRACKING_ID` | Google Analytics (optional) | `G-XXXXXXX` |
| `STREAMLIT_SERVER_PORT` | Override default port | `8502` |
| `APP_SECRET_KEY` | Session / link signing | `super-secret-hex` |
| `MAPBOX_TOKEN` | Map visualisations (future) | `pk.ey…` |

```bash
cp .env.example .env   # then edit values
```

### 3. Run the app

```bash
streamlit run streamlit_app/app.py
```

Open `http://localhost:8501` and explore ✨  
All heavy calculations show a spinner ‑ average cold-start < 1 s on M-Series Apple Silicon.

---

## ☁️ Deploy to Streamlit Cloud

1. Push the repo to GitHub.  
2. In **share.streamlit.io** click *New app* ➜ select repo & `streamlit_app/app.py`.  
3. Set **Secrets** (Environment tab) for the variables above.  
4. Click *Deploy* → profit 🍾

Tips:
- **Wide mode** is the default via `config.toml`.
- Streamlit Cloud auto-caches `@st.cache_data` → snappy UX.
- Use **“Bounce to app”** link in PRs for ephemeral previews.

---

## 🖥️ Other Deployment Options

| Platform | Guide |
|----------|-------|
| **Docker** | `docker compose up --build` – see `docker-compose.yml` |
| **Heroku** | Provision container stack, set env vars, scale web dyno |
| **AWS ECS / Fargate** | Build image & push to ECR, use `./infra/ecs.tf` (Terraform) |
| **Azure Web Apps** | Deploy via GitHub Actions workflow |

All containers run **gunicorn + streamlit** in headless mode for memory efficiency.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd / Ctrl + K` | Open Quick-Action palette |
| `← / →` | Navigate scenario toggle |
| `Esc` | Close dialogs / modals |

---

## 📈 Analytics & Monitoring

- **Google Analytics 4** via [`GA_TRACKING_ID`] – anonymised IP, event-based.
- Server logs forwarded to **Log DNA** (see `docker-compose.yml`).
- `st.toast` for client-side error capture + Sentry integration (commented stub).

---

## 🚀 Performance Optimisations

* **Lazy-load** charts & exports (`st.experimental_rerun` only when visible).  
* **Debounced** slider inputs (300 ms) to cut redundant recalcs.  
* **Pre-computed** common scenarios cached in `calculations.py`.  
* Websocket compression & service-worker caching enabled in `config.toml`.

---

## 🖼️ Screenshot Gallery

| Desktop | Mobile |
|---------|--------|
| ![Dashboard](docs/screens/dashboard.png) | ![Mobile Cards](docs/screens/mobile_cards.png) |
| ![Channel Mix](docs/screens/channel_mix.png) | ![QR Share](docs/screens/qr_share.png) |

> More examples in `docs/screens/`.

---

## 🧩 Project Structure (abridged)

```
.
├── streamlit_app/
│   ├── app.py               # Main entrypoint
│   ├── components/          # Custom widgets & charts
│   ├── utils/
│   │   ├── calculations.py  # Financial logic
│   │   ├── export.py        # PDF / Excel / memo exports
│   │   └── analytics.py     # GA tracking helper
│   └── styles/custom.css    # Global theme overrides
├── .streamlit/config.toml   # Theme & runtime settings
├── requirements.txt
└── README.md
```

---

## 🧪 Running Tests

Unit tests use **pytest**:

```bash
pip install pytest
pytest
```

---

## 🤝 Contributing

1. Fork the repo & create a feature branch.  
2. Run `pre-commit install` for linting & formatting.  
3. Open a PR – CI will run tests & Streamlit Cloud preview.  

We welcome improvements: new widgets, sector templates, performance tweaks.

---

## 📄 License

MIT © 2025 San Francisco AI Factory – please attribute and link back.  
Logos & brand assets are trademarks of their respective owners.

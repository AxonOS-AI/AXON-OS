# Axon OS — Platform Layer

> "Build innovation on top of stability."

Axon OS is a platform-oriented layer built on top of Ubuntu.
It transforms a standard Linux distribution into a specialized environment for AI development, experimentation, and system automation.

---

## Project Structure

```
axon-os/
├── phase1_boot/               ← Phase 1: Boot Interface
│   ├── plymouth/              ← Plymouth boot theme (real Ubuntu boot)
│   │   ├── axon.plymouth      ← Theme config file
│   │   ├── axon.script        ← Animation script
│   │   └── assets/            ← Logo and images
│   ├── splash_simulator/      ← Python visual simulator (preview)
│   │   ├── main.py            ← Entry point
│   │   ├── config.py          ← Configuration constants
│   │   ├── animation.py       ← Animation engine
│   │   └── logo_generator.py  ← SVG logo builder
│   └── scripts/
│       ├── install_theme.sh   ← Install Plymouth theme to system
│       └── check_deps.sh      ← Check system dependencies
├── docs/
│   └── PHASE1_NOTES.md        ← Phase 1 technical notes
└── README.md
```

---

## Phases Overview

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Boot Interface | 🔨 In Progress |
| 2 | Desktop Environment | 🔜 Planned |
| 3 | System Dashboard | 🔜 Planned |
| 4 | Project Manager | 🔜 Planned |
| 5 | AI Runtime | 🔜 Planned |
| 6 | Update System | 🔜 Planned |

---

## Phase 1 — Quick Start

### Option A: Preview the boot screen (no installation needed)
```bash
cd phase1_boot/splash_simulator
pip install pygame
python main.py
```

### Option B: Install Plymouth theme on Ubuntu
```bash
cd phase1_boot/scripts
chmod +x install_theme.sh
sudo ./install_theme.sh
```

---

## Requirements

- Ubuntu 20.04 / 22.04 / 24.04
- Python 3.8+
- pygame (for simulator only)
- Plymouth (pre-installed on Ubuntu)

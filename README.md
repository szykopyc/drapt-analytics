# Drapt Analytics

**Status:** _Temporarily on hold until Summer 2025_

Drapt Analytics is an in-progress portfolio analytics platform designed to provide insightful performance and risk metrics for long-only and long-short strategies. Built with a Python backend, Drapt aims to offer robust financial analytics through an intuitive and modern web interface.

---

## Planned Summer 2025 Revamp

The project is currently paused for academic commitments and quant preparation. Development will resume in **Summer 2025** with a full architectural overhaul and feature expansion, including:

### **Frontend**
- Migration to a **dynamic JavaScript frontend** using **React**
- Interactive, responsive dashboards for portfolio input and visualization
- Real-time data rendering using component-driven architecture
- Integration of charting libraries (e.g., Recharts, Plotly.js) for analytics display

### **Backend**
- Transition from Flask to **FastAPI** for improved performance and async capabilities
- Modularized portfolio analysis functions for better maintainability
- RESTful API endpoints for real-time interaction with the frontend
- Nightly **cron jobs** to perform batch analytics and reduce peak load

### **Performance + UX**
- **Caching of portfolio analysis** results to enhance response times
- More efficient portfolio data handling and preprocessing
- Cleaner user authentication flow using **JWT tokens**

---

## Long-Term Vision

Drapt Analytics aims to become a fully functional, end-to-end portfolio research tool, enabling users to:

- Upload portfolios and simulate performance
- Analyze risk-adjusted returns and factor exposures
- Access custom metrics like Value at Risk, drawdowns, and strategy attribution
- Run Monte Carlo simulations and scenario analyses

---

## Tech Stack (Planned)

- **Frontend:** React, Tailwind CSS or Material UI, Recharts/Plotly
- **Backend:** Python, FastAPI, Pandas, NumPy
- **Database:** SQLite or PostgreSQL
- **Deployment:** Docker, Nginx, optional CI/CD via GitHub Actions
- **Task Scheduling:** Cron, optional Celery for async tasks

---

## Status Update

Development resumes: **May 27, 2025**  
Next milestone: **Frontend + API integration MVP (End of June 2025)**

Stay tuned for updates. Contributions, suggestions, and feedback are always welcome once development resumes.

---

© 2025 Szymon Kopycinski. All rights reserved.
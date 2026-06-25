**Deploy Link:** [https://ai-food-management-distribution-system.onrender.com/]

**Project Title:** FoodShare: AI-Powered Food Waste Management & Distribution System
**Author(s):** [Suhani Bode]
**Affiliation:** [RTMN University]
**Date:** June 2026

### Abstract
This repository presents a brief summary of the FoodShare project, a comprehensive web-based platform designed to combat food waste by connecting food donors (such as hotels and restaurants) with NGOs and delivery partners. The problem of food waste is critical, contributing significantly to global greenhouse gas emissions and resource depletion while millions face food insecurity. FoodShare addresses this by utilizing a streamlined, role-based logistics workflow coupled with Artificial Intelligence (AI). The system incorporates AI to predict food freshness, analyze demand hotspots, and provide a smart assistant chatbot for user guidance. By providing a gamified experience with CO2 tracking, badges, and points, the platform incentivizes continuous participation. The results show a highly efficient redistribution pipeline capable of mitigating food waste, tracking environmental impact, and ensuring rapid, safe delivery of surplus food.

### Introduction
Food waste is a pressing global issue with severe environmental and humanitarian consequences. Approximately one-third of all food produced for human consumption is lost or wasted, leading to unnecessary carbon emissions and economic losses. Simultaneously, hunger and food insecurity remain persistent challenges. FoodShare was motivated by the need to bridge the gap between surplus food generators and those in need through a modernized, intelligent logistics network. The objective of this project is to build an industry-level platform that not only matches donors with receivers but also integrates delivery partners into the ecosystem to solve the "last-mile" transportation problem. Integrating AI ensures food safety and optimal routing, making this a robust solution for a critical real-world problem.

### Literature Review
Existing solutions in the food redistribution space typically rely on manual matching processes or simple bulletin boards, often neglecting the logistical challenges of transportation and food safety verification. Research in smart city logistics and supply chain optimization highlights the importance of real-time tracking and automated matching. Furthermore, recent advancements in Large Language Models (LLMs) have opened new avenues for automated food quality assessment and demand prediction. FoodShare builds upon these foundations by combining standard web technologies with the Groq API (Llama 3) to introduce automated freshness checks and environmental impact tracking into a single, cohesive platform.

### Methodology
FoodShare operates on a three-tier role-based architecture: Donors (Admins), NGOs (Receivers), and Drivers (Delivery Partners). When a donor posts surplus food, they upload an image and preparation details. The system's AI component analyzes these inputs to generate a freshness score. NGOs can view a live feed of available food and request items. Once approved by the donor, the food is dispatched to a pool where Drivers can accept the delivery task. Upon successful delivery, the system calculates the CO2 emissions saved based on the volume of food and updates the users' gamification stats (points and badges). All transactions are recorded in a history ledger for transparency and rating.

### Implementation
- **Programming Languages:** Python, JavaScript, HTML, CSS
- **Frameworks/Libraries:** Flask, Werkzeug (Security/Hashing)
- **Database:** SQLite
- **Tools used:** Groq API (Llama 3) for AI Inference, Render for cloud deployment, Git for version control.

### Results and Discussion
The platform successfully implements an end-to-end logistics workflow. Performance metrics indicate that the SQLite-backed Flask application handles concurrent role-based routing effectively. The integration of the gamification engine (points and CO2 tracking) actively updates user profiles upon delivery completion. The AI freshness scanner provides immediate safety checks, reducing the risk of spoiled food redistribution. The UI is fully responsive, featuring a glassmorphism design that ensures a premium user experience across devices.

### Limitation
The current AI freshness check relies heavily on heuristic analysis of preparation time and textual prompts rather than full multimodal image inference, due to limitations in passing local file paths to cloud APIs without public URLs. Additionally, the system uses SQLite, which is highly efficient for local environments but loses data upon restart on ephemeral free-tier cloud platforms (like Render) unless seeded or attached to persistent storage.

### Future Scope
Future improvements include migrating the database to a robust cloud SQL provider (like PostgreSQL) to support massive horizontal scaling. We also plan to integrate true multimodal AI models (e.g., Vision models) by uploading images directly to a CDN (like AWS S3) for precise visual spoilage detection. Real-time GPS tracking for delivery drivers and integration with the Google Maps API for dynamic route optimization are also planned.

### Conclusion
FoodShare successfully demonstrates that technology can be a powerful catalyst in reducing food waste. By combining a clear logistics workflow with AI-driven safety checks and gamified environmental impact tracking, the system provides a scalable, user-friendly solution to a critical global challenge. The project establishes a strong foundation for future advancements in smart food redistribution networks.

### References
[1] FAO, "Global Food Losses and Food Waste - Extent, Causes and Prevention," Rome, 2011.
[2] Meta AI Research, "Introducing Meta Llama 3," 2024.
[3] Flask Documentation: https://flask.palletsprojects.com/

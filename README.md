# agentic-career-advisor
An Agentic AI Career Advisor using Dual-LLM architecture and local RTX 5090



**Version 1, DUAL Agent Architecture (app-agentic.py)**
Η βασική, ελαφριά έκδοση που χρησιμοποιεί ένα (1) ισχυρό μοντέλο (Qwen 3.6 35B) για να εξυπηρετήσει δύο ρόλους:

Agent 1 (Evaluator): Αναλύει το ιστορικό στο παρασκήνιο και εξάγει ψυχομετρικά JSON (Reality Check, Delusion Level).

Agent 2 (Advisor): Παίρνει μυστικές οδηγίες και απαντά στον χρήστη (Streaming).

Απαιτήσεις: 1 x LLM Server (συνιστάται RTX 5090).



**Version 2, TRIPLE Triple-Agent Architecture (app-agentic-greek.py)**

Η προηγμένη έκδοση για μέγιστη γλωσσική ακρίβεια. Προσθέτει έναν τρίτο Agent στο Pipeline για καλύτερα Ελληνικά.

Agent 1 (Evaluator - Qwen 35B): Ψυχομετρική ανάλυση (Backend).

Agent 2 (Advisor - Qwen 35B): Παραγωγή του προσχεδίου της απάντησης (Backend).

Agent 3 (Editor - KriKri 8B): Φιλολογική επιμέλεια και διόρθωση του προσχεδίου σε τέλεια, φυσικά Ελληνικά, κάνοντας stream το τελικό αποτέλεσμα στον χρήστη (Frontend).

Απαιτήσεις: 2 x LLM Servers (π.χ. RTX 5090 για τη λογική + 2ος Server για το KriKri).

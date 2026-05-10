# **🎓 Agentic AI Career Advisor**

Ένα πειραματικό σύστημα **Πρακτορικής Τεχνητής Νοημοσύνης (Agentic AI)** για επαγγελματικό προσανατολισμό εφήβων. Το σύστημα παρακάμπτει τα συμβατικά orchestration frameworks (όπως το LangGraph) χρησιμοποιώντας native Python State Tracking και Dynamic Prompt Injection.

## **🚀 Διαθέσιμες Εκδόσεις (Architectures)**

Το αποθετήριο περιλαμβάνει δύο διαφορετικές υλοποιήσεις, ανάλογα με τους διαθέσιμους υπολογιστικούς πόρους:

### **1\. Dual-Agent Architecture (app-agentic.py)**

Η βασική, ελαφριά έκδοση που χρησιμοποιεί ένα (1) ισχυρό μοντέλο (Qwen 3.6 35B) για να εξυπηρετήσει δύο ρόλους:

* **Agent 1 (Evaluator):** Αναλύει το ιστορικό στο παρασκήνιο και εξάγει ψυχομετρικά JSON (Reality Check, Delusion Level).  
* **Agent 2 (Advisor):** Παίρνει μυστικές οδηγίες και απαντά στον χρήστη (Streaming).  
* **Απαιτήσεις:** 1 x LLM Server (συνιστάται RTX 5090).

### **2\. Triple-Agent Architecture (app-agentic-greek.py)**

Η προηγμένη έκδοση για μέγιστη γλωσσική ακρίβεια. Προσθέτει έναν τρίτο Agent στο Pipeline για αψεγάδιαστα Ελληνικά.

* **Agent 1 (Evaluator \- Qwen 35B):** Ψυχομετρική ανάλυση (Backend).  
* **Agent 2 (Advisor \- Qwen 35B):** Παραγωγή του προσχεδίου της απάντησης (Backend).  
* **Agent 3 (Editor \- KriKri 8B):** Φιλολογική επιμέλεια και διόρθωση του προσχεδίου σε πολύ καλά, "φυσικά" Ελληνικά, κάνοντας stream το τελικό αποτέλεσμα στον χρήστη (Frontend).  
* **Απαιτήσεις:** 2 x LLM Servers (π.χ. RTX 5090 για τη λογική \+ 2ος Server για το KriKri).

## **⚙️ Πώς να το τρέξετε**

Εγκαταστήστε τα απαιτούμενα πακέτα:  
pip install streamlit openai

Εκκίνηση της έκδοσης Dual-Agent:  
./app-agentic.sh

Εκκίνηση της έκδοσης Triple-Agent (Απαιτεί το KriKri LLM):  
./app-agentic-greek.sh

## **📖 Τεκμηρίωση**

Δείτε την πλήρη τεχνική ανάλυση και το διάγραμμα ροής (HLD/LLD) στο [Έγγραφο Σχεδιασμού (Design Document)](https://github.com/theotox/agentic-career-advisor/blob/main/career_advisor_design_doc.md) και στο [Live Infographic](https://theotox.github.io/agentic-career-advisor/).

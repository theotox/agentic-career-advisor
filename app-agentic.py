import streamlit as st
from openai import OpenAI
import time
import json
import re
import logging

# ================= ΡΥΘΜΙΣΕΙΣ LOGGING =================
# Ρυθμίζουμε το logging ώστε να καταγράφει δομημένα τα πάντα στο τερματικό/αρχείο
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# ================= ΡΥΘΜΙΣΕΙΣ STREAMLIT & API =================
st.set_page_config(page_title="Ψηφιακός Σύμβουλος", page_icon="🎓", layout="centered")

# Νέο IP και Port για την RTX 5090
client = OpenAI(
    base_url="http://100.126.179.69:8080/v1",
    api_key="sk-no-key-required"
)

# Το νέο alias του μοντέλου
MODEL_NAME = "qwen3.6-claude4.7"

# ================= PROMPTS =================
LLM1_BASE_PROMPT = """Είσαι ένας έμπειρος, ενσυναισθητικός και ρεαλιστής Σύμβουλος Επαγγελματικού Προσανατολισμού για εφήβους.
Ο στόχος σου είναι να καθοδηγείς τη συζήτηση, να κάνεις ερωτήσεις αυτογνωσίας και να αξιολογείς τις ικανότητές τους.

Κανόνες:
1. Κάνε ΜΙΑ ερώτηση κάθε φορά.
2. Αν χρειαστεί, γίνε αυστηρός: θύμισέ τους ότι οι στόχοι απαιτούν σκληρή δουλειά.
3. Μην δίνεις αμέσως τη λύση, βοήθησέ τους να τη βρουν.
4. Απάντα ΑΠΟΚΛΕΙΣΤΙΚΑ στα Ελληνικά."""

LLM2_EVALUATOR_PROMPT = """Είσαι ένας αόρατος Αξιολογητής Επαγγελματικού Προσανατολισμού (Backend Profiler Agent).
Σκοπός σου είναι να αναλύεις το ιστορικό της συζήτησης και να εξάγεις συμπεράσματα.
Επίστρεψε ΑΠΟΚΛΕΙΣΤΙΚΑ ένα έγκυρο JSON αντικείμενο, χωρίς καθόλου markdown (```json) και χωρίς εξηγήσεις.
Δομή:
{
  "psychometric_profile": {"teamwork_vs_independence": 0, "conscientiousness_work_ethic": 0, "resilience_to_failure": 0},
  "vocational_interests_riasec": {"realistic_doer": 0, "investigative_thinker": 0, "artistic_creator": 0, "social_helper": 0, "enterprising_persuader": 0, "conventional_organizer": 0},
  "hobbies_and_lifestyle": {"sports_engagement": "", "other_interests": ""},
  "reality_check_metrics": {"stated_dream_job": "", "identified_academic_gaps": [], "delusion_level": 0, "willingness_to_sweat": 0},
  "agent_directives": {"profiling_completeness_percentage": 0, "missing_data_to_explore": "", "recommended_llm1_stance": ""}
}"""

# ================= ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ =================
def extract_json_from_text(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except Exception as e:
        logging.error(f"Σφάλμα Parsing JSON: {e} | Αρχικό κείμενο: {text}")
        return None

def run_evaluator_agent(chat_history):
    transcript = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history if msg['role'] != 'system'])
    messages = [
        {"role": "system", "content": LLM2_EVALUATOR_PROMPT},
        {"role": "user", "content": f"Ανάλυσε την παρακάτω συζήτηση και επίστρεψε το JSON:\n\n{transcript}"}
    ]
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=1024
        )
        return extract_json_from_text(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Σφάλμα κατά την κλήση του Evaluator API: {e}")
        return None

# ================= ΑΡΧΙΚΟΠΟΙΗΣΗ APP =================
st.title("🎓 Ψηφιακός Σύμβουλος Σταδιοδρομίας")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": LLM1_BASE_PROMPT},
        {"role": "assistant", "content": "Γεια σου! Είμαι ο ψηφιακός σου σύμβουλος. Πες μου, αν δεν υπήρχαν βαθμοί και σχολεία, με τι θα ήθελες να ασχολείσαι όλη τη μέρα;"}
    ]

# Μεταβλητή για το In-App Debugging
if "latest_eval" not in st.session_state:
    st.session_state.latest_eval = None

# Εμφάνιση ιστορικού
for message in st.session_state.messages:
    if message["role"] not in ["system"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ================= ΚΥΡΙΑ ΛΟΓΙΚΗ =================
if prompt := st.chat_input("Γράψε την απάντησή σου εδώ..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ΦΑΣΗ 1: ΑΞΙΟΛΟΓΗΣΗ (LLM-2)
    with st.spinner("Γίνεται αξιολόγηση προφίλ..."):
        eval_start = time.time()
        evaluator_data = run_evaluator_agent(st.session_state.messages)
        eval_latency = time.time() - eval_start
        
        st.session_state.latest_eval = evaluator_data # Αποθήκευση για το Debug Panel
        
        # Καταγραφή στο log αρχείο
        if evaluator_data:
            logging.info(f"🕵️ EVALUATOR Ολοκληρώθηκε σε {eval_latency:.2f}s:\n{json.dumps(evaluator_data, indent=2, ensure_ascii=False)}")
        else:
            logging.warning("❌ Αποτυχία δημιουργίας έγκυρου JSON από τον Evaluator.")

    # ΦΑΣΗ 2: ΑΠΑΝΤΗΣΗ (LLM-1)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        llm1_messages = [msg.copy() for msg in st.session_state.messages]
        
        if evaluator_data:
            completeness = evaluator_data.get("agent_directives", {}).get("profiling_completeness_percentage", 0)
            stance = evaluator_data.get("agent_directives", {}).get("recommended_llm1_stance", "")
            missing = evaluator_data.get("agent_directives", {}).get("missing_data_to_explore", "")
            delusion = evaluator_data.get("reality_check_metrics", {}).get("delusion_level", 0)
            
            secret_directive = f"ΜΥΣΤΙΚΗ ΟΔΗΓΙΑ ΑΠΟ ΤΟΝ ΑΞΙΟΛΟΓΗΤΗ: Το προφίλ είναι ολοκληρωμένο στο {completeness}%. "
            secret_directive += f"Επίπεδο Ψευδαίσθησης (1-10): {delusion}. "
            secret_directive += f"Συνιστώμενη στάση: '{stance}'. Τι λείπει: '{missing}'. "
            if completeness >= 85:
                secret_directive += "ΤΟ ΠΡΟΦΙΛ ΕΙΝΑΙ ΕΤΟΙΜΟ. Σταμάτα τις ερωτήσεις και δώσε του την τελική σου ρεαλιστική επαγγελματική συμβουλή και ανάλυση!"
            else:
                secret_directive += "Προσάρμοσε την επόμενη ερώτησή σου με βάση αυτά."
            
            # Injection
            llm1_messages[0]["content"] = LLM1_BASE_PROMPT + "\n\n=== ΔΥΝΑΜΙΚΗ ΟΔΗΓΙΑ ΑΠΟ ΑΞΙΟΛΟΓΗΤΗ ===\n" + secret_directive
            logging.info(f"💉 INJECTION στο LLM-1: {secret_directive}")

        try:
            start_time = time.time()
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=llm1_messages,
                stream=True,
                temperature=0.7,
                max_tokens=2048
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            logging.info(f"✅ LLM-1 Απάντησε επιτυχώς σε {time.time() - start_time:.2f}s")
            
        except Exception as e:
            st.error(f"Σφάλμα σύνδεσης με τον llama-server: {e}")
            logging.error(f"LLM-1 Error: {e}")

# ================= IN-APP DEBUG PANEL =================
st.divider()
with st.expander("🛠️ Debug Panel (Αθέατο στον χρήστη)"):
    st.markdown("**Τελευταία Αξιολόγηση (LLM-2 JSON):**")
    if st.session_state.latest_eval:
        st.json(st.session_state.latest_eval)
    else:
        st.caption("Αναμονή πρώτης αλληλεπίδρασης...")
    
    st.markdown("**Ιστορικό Μηνυμάτων (LLM-1 Payload):**")
    st.json(st.session_state.messages)
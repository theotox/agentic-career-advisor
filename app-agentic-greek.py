import streamlit as st
from openai import OpenAI
import time
import json
import re
import logging

# ================= ΡΥΘΜΙΣΕΙΣ LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# ================= ΡΥΘΜΙΣΕΙΣ STREAMLIT & API =================
st.set_page_config(page_title="Ψηφιακός Σύμβουλος", page_icon="🎓", layout="centered")

# Client 1: To "Βαρύ" μηχάνημα με την RTX 5090 (Λογική & Αξιολόγηση)
client_qwen = OpenAI(
    base_url="http://100.126.179.69:8080/v1",
    api_key="sk-no-key-required"
)
MODEL_QWEN = "qwen3.6-claude4.7"

# Client 2: Το "Γρήγορο" μηχάνημα (Γλωσσική Επιμέλεια στα Ελληνικά)
client_krikri = OpenAI(
    base_url="http://100.90.101.96:8086/v1",
    api_key="sk-no-key-required"
)
MODEL_KRIKRI = "krikri"

# ================= PROMPTS =================
LLM1_BASE_PROMPT = """Είσαι ένας έμπειρος, ενσυναισθητικός και ρεαλιστής Σύμβουλος Επαγγελματικού Προσανατολισμού για εφήβους.
Ο στόχος σου είναι να καθοδηγείς τη συζήτηση, να κάνεις ερωτήσεις αυτογνωσίας και να αξιολογείς τις ικανότητές τους.

Κανόνες:
1. Κάνε ΜΙΑ ερώτηση κάθε φορά.
2. Αν χρειαστεί, γίνε αυστηρός: θύμισέ τους ότι οι στόχοι απαιτούν σκληρή δουλειά.
3. Μην δίνεις αμέσως τη λύση, βοήθησέ τους να τη βρουν.
4. Απάντα στα Ελληνικά."""

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

LLM3_EDITOR_PROMPT = """Είσαι ένας αόρατος, αυτοματοποιημένος διορθωτής κειμένου (Editor Agent).
Ο ρόλος σου είναι να διορθώνεις τυχόν συντακτικά, γραμματικά και ορθογραφικά λάθη, ώστε τα Ελληνικά να είναι φυσικά και ρέοντα.
ΑΥΣΤΗΡΟΙ ΚΑΝΟΝΕΣ (Η ΠΑΡΑΒΙΑΣΗ ΤΟΥΣ ΕΙΝΑΙ ΚΡΙΣΙΜΟ ΣΦΑΛΜΑ):
1. ΑΠΑΓΟΡΕΥΕΤΑΙ να γράψεις "Διορθωμένο κείμενο:", "Ορίστε:", ή οποιαδήποτε άλλη εισαγωγή.
2. ΑΠΑΓΟΡΕΥΕΤΑΙ να κάνεις σχόλια, προτάσεις ή ερωτήσεις στο τέλος (π.χ. "Θέλετε να δείτε εναλλακτική;").
3. Ξεκίνα ΑΠΕΥΘΕΙΑΣ με την πρώτη λέξη του διορθωμένου κειμένου και τελείωσε με την τελευταία.
4. ΜΗΝ πιάσεις κουβέντα. Διατήρησε ακριβώς το ίδιο νόημα και ύφος."""

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
    
    # Προσθήκη Logging για το Prompt του Evaluator
    logging.info(f"🚀 ΠΡΟΣ LLM-2 (ΑΞΙΟΛΟΓΗΤΗΣ) Payload:\n{json.dumps(messages, indent=2, ensure_ascii=False)}")
    
    try:
        response = client_qwen.chat.completions.create(
            model=MODEL_QWEN,
            messages=messages,
            temperature=0.1,
            max_tokens=1024
        )
        return extract_json_from_text(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Σφάλμα κατά την κλήση του Evaluator API (Qwen): {e}")
        return None

# ================= ΑΡΧΙΚΟΠΟΙΗΣΗ APP =================
st.title("🎓 Ψηφιακός Σύμβουλος Σταδιοδρομίας")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": LLM1_BASE_PROMPT},
        {"role": "assistant", "content": "Γεια σου! Είμαι ο ψηφιακός σου σύμβουλος. Πες μου, αν δεν υπήρχαν βαθμοί και σχολεία, με τι θα ήθελες να ασχολείσαι όλη τη μέρα;"}
    ]

if "latest_eval" not in st.session_state:
    st.session_state.latest_eval = None

for message in st.session_state.messages:
    if message["role"] not in ["system"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ================= ΚΥΡΙΑ ΛΟΓΙΚΗ =================
if prompt := st.chat_input("Γράψε την απάντησή σου εδώ..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ΦΑΣΗ 1: ΑΞΙΟΛΟΓΗΣΗ (Qwen 35B)
    with st.spinner("Γίνεται αξιολόγηση προφίλ..."):
        eval_start = time.time()
        evaluator_data = run_evaluator_agent(st.session_state.messages)
        st.session_state.latest_eval = evaluator_data
        
        if evaluator_data:
            logging.info(f"🕵️ EVALUATOR (Qwen) Ολοκληρώθηκε σε {time.time() - eval_start:.2f}s")
        else:
            logging.warning("❌ Αποτυχία δημιουργίας έγκυρου JSON.")

    # ΦΑΣΗ 2: ΣΥΝΤΑΞΗ ΑΠΑΝΤΗΣΗΣ ΑΠΟ ΤΟΝ ΣΥΜΒΟΥΛΟ (Qwen 35B) - ΧΩΡΙΣ STREAMING
    with st.spinner("Ο σύμβουλος συντάσσει την απάντηση..."):
        llm1_messages = [msg.copy() for msg in st.session_state.messages]
        raw_response_text = ""
        
        if evaluator_data:
            completeness = evaluator_data.get("agent_directives", {}).get("profiling_completeness_percentage", 0)
            stance = evaluator_data.get("agent_directives", {}).get("recommended_llm1_stance", "")
            missing = evaluator_data.get("agent_directives", {}).get("missing_data_to_explore", "")
            delusion = evaluator_data.get("reality_check_metrics", {}).get("delusion_level", 0)
            
            secret_directive = f"ΜΥΣΤΙΚΗ ΟΔΗΓΙΑ: Το προφίλ είναι στο {completeness}%. Επίπεδο Ψευδαίσθησης: {delusion}. Στάση: '{stance}'. Λείπει: '{missing}'."
            if completeness >= 85:
                secret_directive += " ΤΟ ΠΡΟΦΙΛ ΕΤΟΙΜΟ. Δώσε ρεαλιστική συμβουλή!"
            else:
                secret_directive += " Προσάρμοσε την επόμενη ερώτησή σου."
            
            llm1_messages[0]["content"] = LLM1_BASE_PROMPT + "\n\n=== ΟΔΗΓΙΑ ===\n" + secret_directive

        try:
            start_qwen = time.time()
            
            # Προσθήκη Logging για το Prompt του Συμβούλου
            logging.info(f"🚀 ΠΡΟΣ LLM-1 (ΣΥΜΒΟΥΛΟΣ) Payload:\n{json.dumps(llm1_messages, indent=2, ensure_ascii=False)}")
            
            # ΣΗΜΑΝΤΙΚΟ: Εδώ το stream είναι False! Περιμένουμε ολόκληρο το κείμενο για να το δώσουμε στον Επιμελητή.
            qwen_response = client_qwen.chat.completions.create(
                model=MODEL_QWEN,
                messages=llm1_messages,
                stream=False,
                temperature=0.7,
                max_tokens=2048
            )
            raw_response_text = qwen_response.choices[0].message.content
            logging.info(f"✅ LLM-1 (Qwen) Έγραψε το προσχέδιο σε {time.time() - start_qwen:.2f}s")
            
        except Exception as e:
            st.error(f"Σφάλμα Qwen: {e}")
            logging.error(f"Qwen Error: {e}")

    # ΦΑΣΗ 3: ΓΛΩΣΣΙΚΗ ΕΠΙΜΕΛΕΙΑ (KriKri 8B) & STREAMING ΣΤΟΝ ΧΡΗΣΤΗ
    if raw_response_text:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            final_polished_response = ""
            
            editor_messages = [
                {"role": "system", "content": LLM3_EDITOR_PROMPT},
                {"role": "user", "content": f"Διόρθωσε το παρακάτω κείμενο στα σωστά Ελληνικά. ΕΠΙΣΤΡΕΨΕ ΑΥΣΤΗΡΑ ΜΟΝΟ ΤΟ ΔΙΟΡΘΩΜΕΝΟ ΚΕΙΜΕΝΟ ΧΩΡΙΣ ΚΑΜΙΑ ΕΙΣΑΓΩΓΗ Η ΚΑΤΑΚΛΕΙΔΑ:\n\n{raw_response_text}"}
            ]
            
            try:
                start_krikri = time.time()
                
                # Προσθήκη Logging για το Prompt του Επιμελητή
                logging.info(f"🚀 ΠΡΟΣ LLM-3 (ΕΠΙΜΕΛΗΤΗΣ) Payload:\n{json.dumps(editor_messages, indent=2, ensure_ascii=False)}")
                
                # Εδώ κάνουμε stream το KriKri για να δει ο χρήστης να γράφεται η απάντηση!
                krikri_stream = client_krikri.chat.completions.create(
                    model=MODEL_KRIKRI,
                    messages=editor_messages,
                    stream=True,
                    temperature=0.1, # Χαμηλή θερμοκρασία για να μην αλλάξει το νόημα
                    max_tokens=2048
                )
                
                for chunk in krikri_stream:
                    if chunk.choices[0].delta.content is not None:
                        final_polished_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(final_polished_response + "▌")
                
                message_placeholder.markdown(final_polished_response)
                
                # Αποθηκεύουμε στο ιστορικό ΜΟΝΟ τα "τέλεια" Ελληνικά του KriKri
                st.session_state.messages.append({"role": "assistant", "content": final_polished_response})
                logging.info(f"✅ LLM-3 (KriKri) Ολοκλήρωσε το streaming σε {time.time() - start_krikri:.2f}s")
                
            except Exception as e:
                # Fallback: Αν το KriKri "πέσει", δείχνουμε το αρχικό κείμενο του Qwen
                st.error(f"Σφάλμα KriKri (Fallback στο αρχικό κείμενο): {e}")
                message_placeholder.markdown(raw_response_text)
                st.session_state.messages.append({"role": "assistant", "content": raw_response_text})

# ================= IN-APP DEBUG PANEL =================
st.divider()
with st.expander("🛠️ Debug Panel (Αθέατο στον χρήστη)"):
    st.markdown("**Τελευταία Αξιολόγηση (LLM-2 JSON):**")
    if st.session_state.latest_eval:
        st.json(st.session_state.latest_eval)
    else:
        st.caption("Αναμονή πρώτης αλληλεπίδρασης...")

import streamlit as st
import pandas as pd

# ======== CUSTOM CSS ========
# Asjusting the sizes of the images
st.markdown("""
<style>
    /* Reduce logo sizes by limiting their maximum height */
    [data-testid="stImage"] img {
        max-height: 80px;
        width: auto;
    }
</style>
""", unsafe_allow_html=True)

# ======== CUSTOM CSS ========
st.markdown("""
<style>
    /* 1) Adjust the sizes of the images and remove rounding */
    [data-testid="stImage"] img {
        max-height: 80px;
        width: auto;
        border-radius: 0 !important;
    }
    
    /* Improve padding of the main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ---------------------------------------------------------------------
       2) BUTTON STYLING
       Adjust spacing, width, and look of primary buttons
       --------------------------------------------------------------------- */
    div.stButton > button {
        background-color: #00C1D4 !important; /* TUHH Turquoise */
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        transition: background-color 0.3s;
        height: 60px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    div.stButton > button:hover {
        background-color: #009fb0 !important;
        color: white !important;
    }
    div.stButton > button:active {
        background-color: #008291 !important;
        color: white !important;
    }
    div.stButton > button p {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: white !important;
        margin: 0;
    }
    
    /* ---------------------------------------------------------------------
       3) IDEA INPUT BOX STYLING
       Create a Turquoise container around the text inputs.
       --------------------------------------------------------------------- */
    .idea-box {
        background-color: rgba(0, 193, 212, 0.1); /* Light turquoise background */
        border: 2px solid #00C1D4;
        border-radius: 12px;
        padding: 25px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    /* 4) Placeholder and Transition Styling */
    .placeholder-card {
        background-color: #f8f9fa;
        border-left: 5px solid #00C1D4;
        border-radius: 6px;
        padding: 20px;
        font-size: 16px;
        margin-bottom: 20px;
        color: #333;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .fade-in-container {
        animation: fadeIn 0.6s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)

# ======== HEADER ========
col_title, col_logo1, col_logo2 = st.columns([2.5, 1, 1])

with col_title:
    st.title("Evaluation")

with col_logo1:
    try:
        st.image("img/Entre.svg", use_container_width=True)
    except:
        pass

with col_logo2:
    try:
        st.image("img/TUHH_logo_rgb.svg", use_container_width=True)
    except:
        pass

st.divider()

# ======== CONFIGURATION ========
COLUMN_NAME_TO_EXTRACT = "entry_text"

# ======== SESSION STATE INITIALIZATION ========
if "ideas_to_evaluate" not in st.session_state:
    st.session_state.ideas_to_evaluate = []

if "current_eval_index" not in st.session_state:
    st.session_state.current_eval_index = 0

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

if "eval_confirm_submit" not in st.session_state:
    st.session_state.eval_confirm_submit = False

if "show_csv_upload" not in st.session_state:
    st.session_state.show_csv_upload = False

if "scroll_to_csv" not in st.session_state:
    st.session_state.scroll_to_csv = False

if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""

ideas_list = st.session_state.ideas_to_evaluate
current_idx = st.session_state.current_eval_index

# ======== CSV UPLOAD UI ========
if not ideas_list:
    # 1. Introductory, for now implementing a Placeholder, will be filled with a text later
    #st.markdown('<div class="placeholder-card">This is a placeholder</div>', unsafe_allow_html=True)
    st.header("Willkommen")
    st.write("Die Seite fungiert als Schnittstelle für die Evaluation von Ideen. Hier können Sie eine CSV-Datei hochladen, um mit der Bewertung zu beginnen.")
    
    # 2. 'Weiter' Button
    if not st.session_state.show_csv_upload:
        if st.button("Weiter", use_container_width=True):
            st.session_state.show_csv_upload = True
            st.session_state.scroll_to_csv = True
            st.rerun()
    else:
        st.button("Weiter", use_container_width=True, disabled=True)

    # 3. CSV Upload Section (hidden initially)
    if st.session_state.show_csv_upload:
        # Target element for scrolling
        st.markdown('<div id="csv-upload-section"></div>', unsafe_allow_html=True)
        
        # Wrap in a fade-in container for a smooth transition
        st.markdown('<div class="fade-in-container">', unsafe_allow_html=True)
        
        st.info("Bitte laden Sie eine CSV-Datei hoch, um mit der Bewertung zu beginnen.")
        uploaded_file = st.file_uploader("CSV-Datei hochladen", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine='python')
                if not df.empty:
                    # Clean BOM (Byte Order Mark) and spaces from column names
                    df.columns = [c.replace('\ufeff', '').strip() for c in df.columns]
                    
                    required_cols = [COLUMN_NAME_TO_EXTRACT, "space_type", "case_number"]
                    missing_cols = [c for c in required_cols if c not in df.columns]
                    if not missing_cols:
                        # Extract participant/session ID if present in the ID column
                        participant_id = ""
                        for col in df.columns:
                            if col.lower() in ["id", "participant_id", "group_id"]:
                                non_empty_ids = df[col].dropna().astype(str).str.strip()
                                non_empty_ids = non_empty_ids[non_empty_ids != ""]
                                if not non_empty_ids.empty:
                                    participant_id = non_empty_ids.iloc[0]
                                    break
                        st.session_state.participant_id = participant_id

                        # Only keep and process rows where space_type column contains the value/tag 'ideation'
                        filtered_df = df[df["space_type"].astype(str).str.contains("ideation", na=False)]
                        
                        ideas_to_eval = []
                        for _, row in filtered_df.iterrows():
                            idea_text = str(row[COLUMN_NAME_TO_EXTRACT]).strip()
                            case_number = str(row["case_number"]).strip() if "case_number" in df.columns else ""
                            if idea_text:
                                ideas_to_eval.append({
                                    "entry_text": idea_text,
                                    "case_number": case_number
                                })
                                
                        if ideas_to_eval:
                            st.session_state.ideas_to_evaluate = ideas_to_eval
                            st.success(f"{len(ideas_to_eval)} Ideen mit space_type 'ideation' importiert!")
                            # Reset the transition states for clean start next time
                            st.session_state.show_csv_upload = False
                            st.session_state.scroll_to_csv = False
                            st.rerun()
                        else:
                            st.warning("Keine gültigen Ideen mit space_type 'ideation' in der Datei gefunden.")
                    else:
                        st.error(f"Fehlende Spalten in der CSV: {', '.join(missing_cols)}")
            except Exception as e:
                st.error(f"Fehler beim Einlesen: {e}")
                
        st.markdown('</div>', unsafe_allow_html=True)

        # Auto-Scroll trigger using a custom script with dynamic time-based key
        if st.session_state.scroll_to_csv:
            import streamlit.components.v1 as components
            import time
            
            js_code = f"""
            <script>
            function scrollToElement() {{
                var target = window.parent.document.getElementById('csv-upload-section');
                if (target) {{
                    target.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                }} else {{
                    setTimeout(scrollToElement, 50);
                }}
            }}
            scrollToElement();
            </script>
            <!-- {time.time()} -->
            """
            components.html(js_code, height=0)
            st.session_state.scroll_to_csv = False

# ======== EVALUATION UI ========
else:
    # Split layout: Left (List of Ideas) | Right (Evaluation Table)
    col_left, col_right = st.columns([1, 1.5], gap="large")

    # -----------------------------
    # LEFT: ALL GENERATED IDEAS
    # -----------------------------
    with col_left:
        st.subheader("Generierte Ideen")
        st.markdown('<div class="idea-box">', unsafe_allow_html=True)
        
        for idx, idea in enumerate(ideas_list):
            entry_text = idea["entry_text"]
            # Highlight the currently evaluating idea
            if idx == current_idx:
                st.markdown(f"**👉 Idee {idx+1}:**<br><span style='color:#00C1D4; font-weight:bold;'>{entry_text}</span>", unsafe_allow_html=True)
            elif idx < current_idx:
                # Already evaluated
                st.markdown(f"**✅ Idee {idx+1}:**<br><span style='text-decoration:line-through; color:gray;'>{entry_text}</span>", unsafe_allow_html=True)
            else:
                # Up next
                st.markdown(f"**Idee {idx+1}:**<br>{entry_text}", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # RIGHT: EVALUATION TABLE
    # -----------------------------
    with col_right:
        if current_idx < len(ideas_list):
            st.subheader(f"Bewertung: Idee {current_idx + 1}")
            case_num = ideas_list[current_idx].get("case_number", "")
            st.info(f"Aktuelle Idee von ({case_num}):\n\n**{ideas_list[current_idx]['entry_text']}**")
            
            st.write("Bitte bewerten Sie die Eingaben anhand der folgenden Kriterien:")

            # Define criteria and fixed weights
            # fixed weights are only information needed for me
            criteria_specs = [
                {"key": "novelty", "name": "Neuheit", "weight": 0.25},
                {"key": "usefulness", "name": "Nutzen", "weight": 0.25},
                {"key": "feasibility", "name": "Machbarkeit", "weight": 0.25},
                {"key": "elaboration", "name": "Ausarbeitung", "weight": 0.15},
                {"key": "strategic_fit", "name": "Strategischer Fit", "weight": 0.10},
            ]

            st.markdown("---")
            
            # Options available
            options = ["1", "2", "3", "4"]
            
            with st.container():
                # HEADER
                t1, t2 = st.columns([2.5, 3.5])
                with t1:
                    st.markdown("<div style='margin-top: 10px;'><b>Kriterien</b></div>", unsafe_allow_html=True)
                with t2:
                    with st.popover("ℹ️ Skalenbeschreibung", use_container_width=True):
                        st.write("**1** = sehr niedrig")
                        st.write("**2** = niedrig")
                        st.write("**3** = hoch")
                        st.write("**4** = sehr hoch")
                st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)
                
                current_ratings = {}
                all_options_selected = True
                
                # ROWS
                for c in criteria_specs:
                    c1, c2 = st.columns([2.5, 3.5])
                    
                    with c1: # Explanation for the criterias
                        with st.popover(c['name'], use_container_width=False):
                            if c['key'] == 'novelty':
                                st.write("„(engl. Novelty) Dieses Kriterium misst, wie ungewöhnlich, originell oder überraschend eine Idee ist. Es geht darum, wie eine Idee sich im Vergleich zu den Ideen im gleichen Set unterscheiden. Es muss jetzt nicht darauf geachtet werden, ob die Idee ein komplettes Denkmuster bricht. “")
                            elif c['key'] == 'usefulness':
                                st.write("„(engl. Usefulness/Utility) Hier wird der praktische Wert und der Nutzen der Idee bewertet. Eine Idee kann noch so kreativ sein, wenn sie das eigentliche Problem nicht löst oder keinen echten Mehrwert bietet, ist sie nicht nützlich. “")
                            elif c['key'] == 'feasibility':
                                st.write("„(engl. Feasibility) Hier geht es darum, wie realistisch und machbar die Idee in der Praxis ist. Dabei spielen technische Machbarkeit, wirtschaftliche Kosten sowie rechtliche oder gesellschaftliche Rahmenbedingungen eine Rolle. “")
                            elif c['key'] == 'elaboration':
                                st.write("„(engl. Elaboration) Dieses Kriterium bewertet, wie detailliert und durchdacht die Idee beschrieben ist. Eine gut ausgearbeitete Idee lässt weniger Fragen offen und erklärt logisch das „Wer, Was, Wie und Warum“. “")
                            elif c['key'] == 'strategic_fit':
                                st.write("„(engl. Strategic Fit) Hier wird geprüft, wie gut die Idee in das große Ganze passt. Es geht darum, ob die Idee zu aktuellen Markttrends, den Bedürfnissen der Zielgruppe oder den strategischen Zielen des jeweiligen Umfelds passt. “")
                    
                    with c2:
                        val = st.radio(
                            label=f"radio_{current_idx}_{c['key']}",
                            label_visibility="collapsed",
                            options=options,
                            index=None,
                            horizontal=True,
                            key=f"real_eval_{current_idx}_{c['key']}"
                        )
                        if val:
                            current_ratings[c['name']] = int(val)
                        else:
                            all_options_selected = False
                            
                    st.markdown("<hr style='margin: 5px 0; border: 0.5px solid #eee;'>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # NEXT BUTTON Logic
            def save_and_next():
                # Store the evaluation
                st.session_state.evaluations.append({
                    "idea": ideas_list[current_idx],
                    "ratings": current_ratings
                })
                # Advance counter
                st.session_state.current_eval_index += 1

            if st.button("Nächste Idee bewerten" if current_idx < len(ideas_list)-1 else "Bewertung abschließen", 
                         use_container_width=True, 
                         disabled=not all_options_selected):
                save_and_next()
                st.rerun()

        # -----------------------------
        # ALL IDEAS EVALUATED
        # -----------------------------
        else:
            st.success("🎉 Sie haben alle Ideen erfolgreich bewertet!")
            st.info("Bitte laden Sie Ihre Bewertungen als CSV herunter:")
            
            # Prepare Export DataFrame
            export_rows = []
            pid = st.session_state.get("participant_id", "")
            for i, ev in enumerate(st.session_state.evaluations):
                idea_data = ev.get("idea", {})
                idea_text = idea_data.get("entry_text", "") if isinstance(idea_data, dict) else str(idea_data)
                case_number = idea_data.get("case_number", "") if isinstance(idea_data, dict) else ""
                ratings = ev.get("ratings", {})
                export_rows.append({
                    "ID": pid,
                    "idea_number": i + 1,
                    "case_number": case_number,
                    "idea_text": idea_text,
                    "novelty_rating": ratings.get("Neuheit", ""),
                    "usefulness_rating": ratings.get("Nutzen", ""),
                    "feasibility_rating": ratings.get("Machbarkeit", ""),
                    "elaboration_rating": ratings.get("Ausarbeitung", ""),
                    "strategic_fit_rating": ratings.get("Strategischer Fit", "")
                })
            
            if export_rows:
                df_export = pd.DataFrame(export_rows)
                csv_data = df_export.to_csv(index=False, sep=";").encode('utf-8')
                
                # Determine download file name dynamically
                pid = st.session_state.get("participant_id", "")
                download_filename = f"evaluation_results_{pid}.csv" if pid else "evaluation_results.csv"
                
                st.download_button(
                    label="📥 Evaluations-Ergebnisse herunterladen",
                    data=csv_data,
                    file_name=download_filename,
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            
            st.markdown("<hr>", unsafe_allow_html=True)
            if st.button("Neue Evaluation starten", use_container_width=True):
                st.session_state.evaluations = []
                st.session_state.current_eval_index = 0
                st.session_state.eval_confirm_submit = False
                st.session_state.show_csv_upload = False
                st.session_state.scroll_to_csv = False
                if "ideas_to_evaluate" in st.session_state:
                    del st.session_state["ideas_to_evaluate"]
                if "participant_id" in st.session_state:
                    st.session_state.participant_id = ""
                st.rerun()

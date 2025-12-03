# afd_visualizer_enhanced.py
"""
AFD Visualizer — Professional version (Streamlit)
- Clean, production-ready Python
- Improved AFD class with typing and logging
- Interactive stepper, autoplay, and path animation
- Graphviz visualization + PNG export
- Sidebar for creating or uploading an AFD (JSON)
- Polished CSS and responsive layout

Drop this file in your Streamlit app folder and run:
    streamlit run afd_visualizer_enhanced.py

Requirements (pip):
    streamlit
    graphviz

Optional (for rendering PNG export):
    graphviz system package (apt-get install graphviz) if not present

"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set

import graphviz
import streamlit as st

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AFDVisualizer")


# ---------------------------
# AFD core implementation
# ---------------------------
@dataclass
class AFD:
    alphabet: Set[str]
    etats: Set[str]
    etat_initial: str
    etats_finaux: Set[str]
    transitions: Dict[str, Dict[str, str]]
    etat_actuel: str = field(init=False)

    def __post_init__(self) -> None:
        if self.etat_initial not in self.etats:
            raise ValueError("etat_initial must be an element of etats")
        for e in self.etats_finaux:
            if e not in self.etats:
                raise ValueError("all etats_finaux must be in etats")
        self.reinitialiser()

    def reinitialiser(self) -> None:
        """Réinitialise l'automate à l'état initial."""
        self.etat_actuel = self.etat_initial
        logger.debug("Réinitialisation -> %s", self.etat_actuel)

    def traiter_symbole(self, symbole: str) -> bool:
        """Traite un symbole et effectue la transition si possible.

        Returns True if transition succeeded, False otherwise.
        """
        if symbole not in self.alphabet:
            logger.debug("Symbole invalide: %s", symbole)
            return False

        trans = self.transitions.get(self.etat_actuel, {})
        if symbole in trans:
            self.etat_actuel = trans[symbole]
            logger.debug("Transition: %s --%s--> %s", trans, symbole, self.etat_actuel)
            return True

        logger.debug("Aucune transition depuis %s sur '%s'", self.etat_actuel, symbole)
        return False

    def accepter_chaine(self, chaine: Iterable[str]) -> bool:
        """Retourne True si la chaîne est acceptée par l'automate."""
        self.reinitialiser()
        for s in chaine:
            if not self.traiter_symbole(s):
                return False
        return self.etat_actuel in self.etats_finaux

    def obtenir_chemin(self, chaine: Iterable[str]) -> List[str]:
        self.reinitialiser()
        chemin = [self.etat_actuel]
        for s in chaine:
            if self.traiter_symbole(s):
                chemin.append(self.etat_actuel)
            else:
                # stop at first invalid transition
                break
        return chemin


# ---------------------------
# Utilities
# ---------------------------

def creer_afd_exemple() -> AFD:
    alphabet = {"a", "b"}
    etats = {"q0", "q1", "q2"}
    etat_initial = "q0"
    etats_finaux = {"q2"}
    transitions = {
        "q0": {"a": "q1", "b": "q0"},
        "q1": {"a": "q1", "b": "q2"},
        "q2": {"a": "q1", "b": "q0"},
    }
    return AFD(alphabet, etats, etat_initial, etats_finaux, transitions)


def afd_to_graphviz(afd: AFD, highlight_path: Optional[List[str]] = None) -> graphviz.Digraph:
    """Crée un Graphviz Digraph représentant l'AFD.

    highlight_path: optional list of states to highlight (in order)
    """
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR", size="8,5")

    # invisible start arrow
    dot.node("__start__", label="", shape="none")
    dot.edge("__start__", afd.etat_initial, arrowhead="normal")

    # nodes
    for etat in sorted(afd.etats):
        if etat in afd.etats_finaux:
            dot.node(etat, shape="doublecircle", style="filled" if highlight_path and etat in highlight_path else "")
        else:
            dot.node(etat, shape="circle", style="filled" if highlight_path and etat in highlight_path else "")

    # transitions (group same edges for nicer labels)
    edges: Dict[(str, str), List[str]] = {}
    for src, trans in afd.transitions.items():
        for sym, dst in trans.items():
            edges.setdefault((src, dst), []).append(sym)

    for (src, dst), syms in edges.items():
        label = ",".join(sorted(syms))
        dot.edge(src, dst, label=label)

    return dot


def parse_afd_from_json(text: str) -> AFD:
    """Charge un AFD depuis une JSON string.

    JSON schema expected:
    {
      "alphabet": ["a","b"],
      "etats": ["q0","q1"],
      "etat_initial": "q0",
      "etats_finaux": ["q2"],
      "transitions": {"q0": {"a":"q1","b":"q0"}, ...}
    }
    """
    obj = json.loads(text)
    return AFD(set(obj["alphabet"]), set(obj["etats"]), obj["etat_initial"], set(obj["etats_finaux"]),
               obj["transitions"])


# ---------------------------
# Streamlit UI
# ---------------------------

# Page setup
st.set_page_config(page_title="AFD Visualizer — Professional", page_icon="🔠", layout="wide")

# Modern Professional CSS with Glass Morphism
st.markdown(
    """
    <style>
    /* Modern Professional Design with Glass Effect */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main content wrapper */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header with gradient text */
    .main-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(45deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    .main-subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.85);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Glass cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.93);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.8rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .section-header::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 2px;
    }

    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 0.5rem;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    /* Secondary buttons */
    .secondary-btn > button {
        background: rgba(255, 255, 255, 0.9);
        color: #667eea;
        border: 2px solid #667eea;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .stSlider > div > div > div > div {
        background: white;
        border: 3px solid #667eea;
    }

    /* Graph container */
    .stGraphviz {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
    }

    /* Status badges */
    .accepted-badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .rejected-badge {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Path display */
    .path-display {
        background: rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 1rem;
        margin: 1rem 0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

    section[data-testid="stSidebar"] .sidebar-header {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }

    /* Info cards */
    .info-card {
        background: rgba(102, 126, 234, 0.08);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
    }

    .info-card h4 {
        color: #1e293b;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .info-card p {
        color: #475569;
        margin: 0;
        font-size: 1rem;
        font-weight: 500;
    }

    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 2rem 0;
    }

    /* Tooltips */
    .tooltip-icon {
        display: inline-block;
        width: 18px;
        height: 18px;
        background: #667eea;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 18px;
        font-size: 12px;
        margin-left: 0.5rem;
        cursor: help;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Header
st.markdown(
    """
    <div class="main-header">
        <h1 class="main-title">🔠 AFD Visualizer</h1>
        <p class="main-subtitle">Interactive finite automaton visualization with professional-grade animations and real-time simulation</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Main layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔍 String Testing & Simulation</div>', unsafe_allow_html=True)

    # String input with modern styling
    chaine = st.text_input(
        "**Input String**",
        value="abab",
        placeholder="Enter a string (e.g., abab, aabb, ...)",
        help="Use characters from the AFD's alphabet"
    )

    # Simulation controls
    st.markdown("**Simulation Controls**")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        step_mode = st.radio(
            "Simulation Mode:",
            ["Automatic Play", "Step by Step"],
            index=0,
            help="Choose how to visualize the simulation"
        )

    with col_sim2:
        if step_mode == "Automatic Play":
            autoplay_speed = st.slider(
                "Animation Speed",
                0.1, 2.0, 0.6,
                step=0.1,
                help="Seconds per step in automatic mode"
            )

    # Run simulation button
    if st.button("▶️ **Run Simulation**", use_container_width=True):
        if not chaine:
            st.warning("Please enter a valid string.")
        elif any(c not in afd.alphabet for c in chaine):
            st.error("String contains characters not in the AFD's alphabet.")
        else:
            # Calculate path and result
            chemin = afd.obtenir_chemin(chaine)
            accepted = afd.accepter_chaine(chaine)

            # Store in session state
            st.session_state["last_chaine"] = chaine
            st.session_state["last_chemin"] = chemin
            st.session_state["last_accepted"] = accepted

            # Show result
            if accepted:
                st.markdown(
                    f'<div class="accepted-badge">✅ String "{chaine}" is ACCEPTED</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="rejected-badge">❌ String "{chaine}" is REJECTED</div>',
                    unsafe_allow_html=True
                )

    # Display last result and path
    if "last_chemin" in st.session_state:
        st.markdown("**Execution Path**")
        st.markdown(
            f'<div class="path-display">{" → ".join(st.session_state["last_chemin"])}</div>',
            unsafe_allow_html=True
        )

        # Animation controls
        st.markdown("**Animation Controls**")
        chemin = st.session_state["last_chemin"]

        if step_mode == "Step by Step":
            col_step1, col_step2, col_step3 = st.columns([1, 2, 1])
            with col_step2:
                idx = st.number_input(
                    "Current Step",
                    min_value=0,
                    max_value=len(chemin) - 1,
                    value=0,
                    step=1,
                    label_visibility="collapsed"
                )

            # Visual step indicator
            steps_html = ""
            for i, state in enumerate(chemin):
                if i == idx:
                    steps_html += f'<span style="background:#667eea;color:white;padding:8px 12px;border-radius:8px;margin:0 2px;font-weight:bold;">{state}</span>'
                else:
                    steps_html += f'<span style="background:rgba(102,126,234,0.1);color:#475569;padding:8px 12px;border-radius:8px;margin:0 2px;">{state}</span>'

            st.markdown(f'<div style="text-align:center;margin:1rem 0;">{steps_html}</div>', unsafe_allow_html=True)
            st.markdown(f"**Current State:** `{chemin[idx]}`")

            if idx == len(chemin) - 1:
                st.success("🏁 Simulation Complete!")
        else:
            # Auto-play animation
            import time

            placeholder = st.empty()

            for i, state in enumerate(chemin):
                # Create visual progress
                progress_html = ""
                for j in range(len(chemin)):
                    if j <= i:
                        progress_html += f'<span style="background:#667eea;color:white;padding:8px 12px;border-radius:8px;margin:0 2px;font-weight:bold;">{chemin[j]}</span>'
                    else:
                        progress_html += f'<span style="background:rgba(102,126,234,0.1);color:#475569;padding:8px 12px;border-radius:8px;margin:0 2px;">{chemin[j]}</span>'

                placeholder.markdown(
                    f"""
                    <div style="margin:1rem 0;">
                        <div style="text-align:center;margin-bottom:1rem;">{progress_html}</div>
                        <div style="text-align:center;font-size:1.2rem;font-weight:bold;">
                            Current State: <span style="color:#667eea;">{state}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                time.sleep(autoplay_speed)

            placeholder.success("🎉 Simulation Complete!")

    st.markdown('</div>', unsafe_allow_html=True)  # Close glass-card

    # Export section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📥 Export & Diagnostics</div>', unsafe_allow_html=True)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("💾 Download JSON", use_container_width=True):
            blob = json.dumps({
                "alphabet": sorted(list(afd.alphabet)),
                "etats": sorted(list(afd.etats)),
                "etat_initial": afd.etat_initial,
                "etats_finaux": sorted(list(afd.etats_finaux)),
                "transitions": afd.transitions,
            }, ensure_ascii=False, indent=2)
            st.download_button(
                "Download JSON",
                blob,
                file_name="afd_transitions.json",
                mime="application/json",
                use_container_width=True
            )

    with col_exp2:
        if st.button("📊 Export Statistics", use_container_width=True):
            st.info(f"""
            **AFD Statistics:**
            - States: {len(afd.etats)}
            - Alphabet size: {len(afd.alphabet)}
            - Final states: {len(afd.etats_finaux)}
            - Transitions: {sum(len(t) for t in afd.transitions.values())}
            """)

    st.markdown('</div>', unsafe_allow_html=True)  # Close glass-card

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Visualization & Export</div>', unsafe_allow_html=True)

    # Highlight path if exists
    highlight_path = st.session_state.get("last_chemin") if st.session_state.get("last_chemin") else None
    dot = afd_to_graphviz(afd, highlight_path=highlight_path)

    # Display graph
    st.graphviz_chart(dot)

    # Graph info
    st.markdown("**Graph Information**")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("States", len(afd.etats))
    with col_info2:
        st.metric("Transitions", sum(len(t) for t in afd.transitions.values()))
    with col_info3:
        st.metric("Final States", len(afd.etats_finaux))

    # PNG export
    try:
        png_bytes = dot.pipe(format="png")
        if st.button("📸 Download PNG", use_container_width=True):
            st.download_button(
                "Download Diagram (PNG)",
                png_bytes,
                file_name="afd_diagram.png",
                mime="image/png",
                use_container_width=True
            )
    except Exception as e:
        st.info("📝 PNG export requires Graphviz binaries. Visualization will still work.")

    st.markdown('</div>', unsafe_allow_html=True)  # Close glass-card

# Sidebar Configuration
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ AFD Configuration</div>', unsafe_allow_html=True)

    # Mode selection
    mode = st.radio(
        "Select AFD Source:",
        ["Example AFD", "Upload JSON File"],
        index=0,
        help="Choose between built-in example or custom AFD"
    )

    if mode == "Example AFD":
        afd = creer_afd_exemple()
        st.success("✅ Using example AFD")
    else:
        uploaded = st.file_uploader(
            "Upload AFD JSON",
            type=["json"],
            help="Upload a JSON file with AFD definition"
        )
        if uploaded is not None:
            try:
                afd = parse_afd_from_json(uploaded.read().decode("utf-8"))
                st.success("✅ Custom AFD loaded successfully")
            except Exception as e:
                st.error(f"Error loading JSON: {e}")
                st.stop()
        else:
            st.info("📁 Please upload a JSON file or use the example")
            st.stop()

    # AFD Information Cards
    st.markdown("### AFD Properties")

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h4>📝 Alphabet</h4>', unsafe_allow_html=True)
    st.markdown(f'<p>{" ".join(sorted(afd.alphabet))}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h4>🏷️ States</h4>', unsafe_allow_html=True)
    st.markdown(f'<p>{" ".join(sorted(afd.etats))}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h4>🚀 Initial State</h4>', unsafe_allow_html=True)
    st.code(afd.etat_initial, language="text")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h4>🎯 Final States</h4>', unsafe_allow_html=True)
    st.markdown(f'<p>{" ".join(sorted(afd.etats_finaux))}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick transitions preview
    with st.expander("🔗 Transitions Preview"):
        for state, trans in afd.transitions.items():
            st.text(f"{state}: {trans}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        <p>🎓 <strong>AFD Visualizer Professional</strong> — Academic Edition</p>
        <p style="font-size:0.8rem;opacity:0.7;">Interactive Finite Automaton Visualization Tool</p>
    </div>
    """,
    unsafe_allow_html=True
)

# End of file
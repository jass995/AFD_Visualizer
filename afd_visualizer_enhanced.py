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

# Custom CSS (polished, minimal)
st.markdown(
    """
    <style>
    /* Container */
    .stApp { font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
    .title { text-align:center; font-size:36px; font-weight:700; margin-bottom:6px }
    .subtitle { text-align:center; color: #6c757d; margin-top: -10px }

    /* Card look */
    .card { background: rgba(255,255,255,0.85); padding:16px; border-radius:12px; box-shadow: 0 6px 18px rgba(0,0,0,0.08); }

    /* Buttons */
    .big-btn { padding: 10px 18px; font-weight:600; }

    /* Small touches */
    .state-pill { padding:6px 10px; border-radius:999px; background:#f1f3f5; display:inline-block; margin-right:6px }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'>🔠 AFD Visualizer — Professional</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Interactive, clean and production-ready automaton visualizer</div>",
            unsafe_allow_html=True)
st.write("---")

# Sidebar: choose or upload AFD
with st.sidebar:
    st.header("Configuration AFD")
    mode = st.radio("Mode:", ["Example AFD", "Upload JSON"], index=0)

    if mode == "Example AFD":
        afd = creer_afd_exemple()
    else:
        uploaded = st.file_uploader("Upload AFD JSON file", type=["json"])
        if uploaded is not None:
            try:
                afd = parse_afd_from_json(uploaded.read().decode("utf-8"))
            except Exception as e:
                st.error(f"Erreur lors du parsing du JSON: {e}")
                st.stop()
        else:
            st.info("Upload a JSON file or select 'Example AFD' to continue.")
            st.stop()

    st.markdown("**Alphabet:**")
    st.write(", ".join(sorted(afd.alphabet)))
    st.markdown("**États:**")
    st.write(", ".join(sorted(afd.etats)))
    st.markdown(f"**État initial:** `{afd.etat_initial}`")
    st.markdown(f"**États finaux:** {', '.join(sorted(afd.etats_finaux))}")
    st.markdown("---")

# Main layout: left = controls, right = visualization
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🔎 Tester des chaînes")

    chaine = st.text_input("Entrez une chaîne (ex: abab)", value="ab")

    # Stepper controls
    st.markdown("**Contrôles de simulation**")
    step_mode = st.radio("Mode de lecture:", ["Automatique", "Pas à pas"], index=0)
    autoplay_speed = st.slider("Vitesse (s par étape)", 0.1, 2.0, 0.6, step=0.1) if step_mode == "Automatique" else None

    # Simulate button
    if st.button("▶️ Lancer la simulation", key="run_sim"):
        if not chaine:
            st.warning("Entrez une chaîne valide.")
        elif any(c not in afd.alphabet for c in chaine):
            st.error("La chaîne contient des symboles hors alphabet de l'AFD.")
        else:
            # store chemin in session_state for animation controls
            chemin = afd.obtenir_chemin(chaine)
            st.session_state["last_chaine"] = chaine
            st.session_state["last_chemin"] = chemin

            accepted = afd.accepter_chaine(chaine)
            if accepted:
                st.success(f"✅ La chaîne '{chaine}' est ACCEPTÉE")
            else:
                st.error(f"❌ La chaîne '{chaine}' est REJETÉE")

    # Show last result and stepper
    if "last_chemin" in st.session_state:
        st.markdown("**Dernier chemin parcouru**")
        st.code(" → ".join(st.session_state["last_chemin"]))

        # Stepper animation (simple)
        st.markdown("**Animation (Pas à pas)**")
        chemin = st.session_state["last_chemin"]
        if step_mode == "Pas à pas":
            idx = st.number_input("Étape", min_value=0, max_value=len(chemin) - 1, value=0, step=1)
            st.markdown(f"État courant: **{chemin[idx]}**")
        else:
            # autoplay: show sequence with st.empty and time.sleep
            placeholder = st.empty()
            import time

            for state in chemin:
                placeholder.markdown(f"**État courant:** `{state}`")
                time.sleep(autoplay_speed)

            placeholder.success("Animation terminée")

    st.markdown("---")
    st.header("📥 Export & Diagnostics")
    if st.button("Télécharger les transitions (JSON)"):
        blob = json.dumps({
            "alphabet": sorted(list(afd.alphabet)),
            "etats": sorted(list(afd.etats)),
            "etat_initial": afd.etat_initial,
            "etats_finaux": sorted(list(afd.etats_finaux)),
            "transitions": afd.transitions,
        }, ensure_ascii=False, indent=2)
        st.download_button("Télécharger JSON", blob, file_name="afd_transitions.json")

with col2:
    st.header("📊 Visualisation et Export PNG")

    # highlight path if exists
    highlight_path = st.session_state.get("last_chemin") if st.session_state.get("last_chemin") else None
    dot = afd_to_graphviz(afd, highlight_path=highlight_path)

    st.graphviz_chart(dot)

    # show legend and details
    st.markdown("**Légende / Info**")
    st.markdown("- Cercle double = état final")

    # PNG export
    try:
        png_bytes = dot.pipe(format="png")
        st.download_button("📸 Télécharger le diagramme (PNG)", png_bytes, file_name="afd_diagram.png")
    except Exception as e:
        st.info("Export PNG indisponible (Graphviz binaire manquant). Vous pouvez quand même visualiser le graphe.")
        logger.debug("graphviz export error: %s", e)

# Footer: tips
st.write("---")
st.markdown(
    ""
)

# End of file

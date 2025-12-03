import streamlit as st
import graphviz
from afd_core import creer_afd_exemple

# Configuration de la page
st.set_page_config(
    page_title="AFD Visualizer",
    page_icon="🔠",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    # Titre principal avec style
    st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .accepted {
        color: #2ecc71;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .rejected {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">🔠 AFD Visualizer</h1>', unsafe_allow_html=True)
    st.markdown("### Automate Fini Déterministe - Reconnaissance de Chaînes")

    # Initialiser l'AFD
    afd = creer_afd_exemple()

    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration AFD")

        st.subheader("Alphabet")
        st.write(f"**Alphabet actuel:** {afd.alphabet}")

        st.subheader("États")
        st.write(f"**États:** {afd.etats}")
        st.write(f"**État initial:** `{afd.etat_initial}`")
        st.write(f"**États finaux:** {afd.etats_finaux}")

        st.subheader("📊 Table de Transition")
        for etat, transitions in afd.transitions.items():
            st.write(f"**{etat}:** {transitions}")

        st.markdown("---")
        st.info("💡 **Exemple de chaînes acceptées:** ab, aab, abab")
        st.info("💡 **Exemple de chaînes rejetées:** b, aa, abb")

    # Layout en deux colonnes
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("🎯 Test de Chaînes")

        # Input pour la chaîne
        chaine = st.text_input(
            "Entrez une chaîne à tester:",
            placeholder="Exemple: abab",
            help="Utilisez seulement les caractères 'a' et 'b'"
        )

        # Bouton de test
        if st.button("🔍 Vérifier la chaîne", type="primary"):
            if chaine:
                # Vérifier si la chaîne est valide
                if all(char in afd.alphabet for char in chaine):
                    resultat = afd.accepter_chaine(chaine)
                    chemin = afd.obtenir_chemin(chaine)

                    # Afficher le résultat
                    if resultat:
                        st.markdown(f'<p class="accepted">✅ La chaîne "{chaine}" est ACCEPTÉE</p>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="rejected">❌ La chaîne "{chaine}" est REJETÉE</p>',
                                    unsafe_allow_html=True)

                    # Afficher le chemin
                    st.subheader("🛣️ Chemin parcouru:")
                    chemin_str = " → ".join(chemin)
                    st.code(chemin_str)

                    # Animation du chemin
                    st.subheader("🎬 Animation des transitions:")
                    with st.expander("Voir les étapes détaillées"):
                        afd.reinitialiser()
                        etat_courant = afd.etat_initial

                        for i, char in enumerate(chaine):
                            etat_suivant = afd.transitions[etat_courant][char]
                            st.write(f"**Étape {i + 1}:** `{etat_courant}` --**{char}**--> `{etat_suivant}`")
                            etat_courant = etat_suivant

                else:
                    st.error("❌ La chaîne contient des caractères invalides. Utilisez seulement 'a' et 'b'.")

    with col2:
        st.header("📊 Visualisation AFD")

        # Créer le graphe avec graphviz
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR')

        # Ajouter les états
        for etat in afd.etats:
            if etat == afd.etat_initial:
                # État initial
                dot.node('start', '', shape='none', width='0', height='0')
                dot.edge('start', etat)

            if etat in afd.etats_finaux:
                # État final (double cercle)
                dot.node(etat, etat, shape='doublecircle')
            else:
                dot.node(etat, etat, shape='circle')

        # Ajouter les transitions
        for etat_depart, transitions in afd.transitions.items():
            for symbole, etat_arrivee in transitions.items():
                dot.edge(etat_depart, etat_arrivee, label=symbole)

        # Afficher le graphe
        st.graphviz_chart(dot)

        # Légende
        st.caption("**Légende:**")
        st.caption("• 🔵 Cercle simple: état normal")
        st.caption("• 🔴 Double cercle: état final")
        st.caption("• 🟢 Flèche: transition avec symbole")

    # Section des exemples
    st.markdown("---")
    st.header("🧪 Exemples Rapides")

    exemples = ["ab", "aab", "b", "aa", "abab"]
    cols = st.columns(len(exemples))

    for i, exemple in enumerate(exemples):
        with cols[i]:
            if st.button(f"Test: {exemple}", key=f"btn_{exemple}"):
                resultat = afd.accepter_chaine(exemple)
                if resultat:
                    st.success(f"'{exemple}' ✓")
                else:
                    st.error(f"'{exemple}' ✗")


if __name__ == "__main__":
    main()
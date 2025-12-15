import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/chat")


def main():
    st.title(" Chatbot Profil Candidat")

    st.write("Posez une question.")
    query = st.text_input("Question")

    if st.button("Envoyer") and query:
        resp = requests.post(API_URL, json={"query": query})
        if resp.status_code == 200:
            st.markdown("### Réponse")
            st.write(resp.json()["answer"])
        else:
            st.error(f"Erreur API: {resp.status_code}")


if __name__ == "__main__":
    main()
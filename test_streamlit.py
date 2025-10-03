import streamlit as st

st.title("Teste Streamlit")
st.write("Se consegue ver isto, o Streamlit está a funcionar!")

if st.button("Clique aqui"):
    st.success("Botão funcionou!")

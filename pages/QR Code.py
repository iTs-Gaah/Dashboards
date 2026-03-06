import streamlit as st
import qrcode
from io import BytesIO

# Função que zera a porra do input no estado da sessão
def limpar_input():
    st.session_state["meu_link"] = ""

st.title("Gerador de QR Code")

# A key é obrigatória para o Streamlit saber o que limpar
link = st.text_input("Insira aqui o seu link:", key="meu_link")

# Divide a tela em duas colunas para os botões ficarem alinhados
col1, col2 = st.columns(2)

with col1:
    gerar = st.button("Gerar QR Code")

with col2:
    st.button("🧹 Limpar link", on_click=limpar_input)

if gerar:
    if link:
        # Cria o QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(link)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva na memória
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # Mostra a imagem
        st.image(byte_im, caption="Feito!")
        
        # Botão para baixar a imagem
        st.download_button(
            label="Baixar a imagem",
            data=byte_im,
            file_name="qr_code.png",
            mime="image/png"
        )
    else:
        st.error("Esqueceu de inserir o link!")

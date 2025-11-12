# ===============================================
# APP STREAMLIT - ANÁLISE DE SENTIMENTO DE MÚSICAS DE ROCK
# ===============================================
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIGURAÇÕES BÁSICAS ----------
st.set_page_config(
    page_title="Análise de Sentimentos - Rock",
    page_icon="🎸",
    layout="wide"
)

st.title("🎸 Análise de Sentimentos das 1000 Músicas de Rock (Letras.com)")
st.markdown("Este painel interativo mostra a análise de sentimentos aplicada às 1000 músicas de rock mais buscadas no site Letras.com.")

# ---------- CARREGAMENTO DOS DADOS ----------
@st.cache_data
def carregar_dados():
    df = pd.read_csv("analise_sentimento_outputs/letras_sentimento.csv", encoding="utf-8-sig")
    return df

df = carregar_dados()

if df.empty:
    st.error("❌ Nenhum dado encontrado. Verifique se o arquivo 'letras_sentimento.csv' foi gerado pelo script principal.")
    st.stop()

# ---------- FILTROS LATERAIS ----------
st.sidebar.header("🎚️ Filtros")
artistas = sorted(df['artista'].unique().tolist())
idiomas = sorted(df['idioma_detectado'].unique().tolist())

artista_sel = st.sidebar.multiselect("Selecione Artista(s)", artistas, default=[])
idioma_sel = st.sidebar.multiselect("Filtrar por idioma detectado", idiomas, default=[])

min_pol, max_pol = st.sidebar.slider(
    "Faixa de Polaridade", 
    float(df['sent_polarity'].min()), 
    float(df['sent_polarity'].max()), 
    (float(df['sent_polarity'].min()), float(df['sent_polarity'].max()))
)

# Aplica filtros
df_filtrado = df.copy()
if artista_sel:
    df_filtrado = df_filtrado[df_filtrado['artista'].isin(artista_sel)]
if idioma_sel:
    df_filtrado = df_filtrado[df_filtrado['idioma_detectado'].isin(idioma_sel)]
df_filtrado = df_filtrado[(df_filtrado['sent_polarity'] >= min_pol) & (df_filtrado['sent_polarity'] <= max_pol)]

st.markdown(f"**{len(df_filtrado)} músicas exibidas após os filtros aplicados.**")

# ---------- MÉTRICAS RESUMIDAS ----------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎵 Total de Músicas", len(df_filtrado))
with col2:
    st.metric("💬 Polaridade Média", round(df_filtrado['sent_polarity'].mean(), 3))
with col3:
    st.metric("📈 Maior Polaridade", round(df_filtrado['sent_polarity'].max(), 3))

st.divider()

# ---------- GRÁFICOS ----------
tab1, tab2, tab3, tab4 = st.tabs(["Distribuição", "Artistas", "Tamanho x Polaridade", "Top Músicas"])

with tab1:
    st.subheader("📊 Distribuição de Polaridade")
    fig = px.histogram(
        df_filtrado, 
        x="sent_polarity",
        nbins=25,
        color_discrete_sequence=["royalblue"],
        title="Distribuição da Polaridade das Letras"
    )
    fig.update_layout(xaxis_title="Polaridade", yaxis_title="Número de músicas", bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🎤 Polaridade Média por Artista (Top 20)")
    art_group = (
        df_filtrado.groupby("artista")["sent_polarity"]
        .mean()
        .sort_values(ascending=False)
        .head(20)
        .reset_index()
    )
    fig2 = px.bar(
        art_group,
        x="sent_polarity",
        y="artista",
        orientation="h",
        color="sent_polarity",
        color_continuous_scale="RdYlGn",
        labels={"sent_polarity": "Polaridade Média", "artista": "Artista"}
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("📏 Relação: Tamanho da Letra × Polaridade")
    fig3 = px.scatter(
        df_filtrado,
        x="tam_letra",
        y="sent_polarity",
        hover_data=["titulo", "artista"],
        color="sent_polarity",
        color_continuous_scale="RdYlGn",
        labels={"tam_letra": "Tamanho (nº palavras)", "sent_polarity": "Polaridade"}
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("🏆 Músicas Mais Positivas e Negativas")
    colp, coln = st.columns(2)

    top_pos = df_filtrado.sort_values("sent_polarity", ascending=False).head(10)
    top_neg = df_filtrado.sort_values("sent_polarity", ascending=True).head(10)

    with colp:
        st.markdown("#### 🎶 Top 10 Positivas")
        for _, row in top_pos.iterrows():
            st.markdown(f"**{row['titulo']}** — *{row['artista']}* ({row['sent_polarity']:.3f})")
            st.caption(row['letra'][:300] + "...")

    with coln:
        st.markdown("#### ⚡ Top 10 Negativas")
        for _, row in top_neg.iterrows():
            st.markdown(f"**{row['titulo']}** — *{row['artista']}* ({row['sent_polarity']:.3f})")
            st.caption(row['letra'][:300] + "...")

st.divider()
st.markdown("💡 *Desenvolvido por Elder e Kiyoko  — Projeto Acadêmico de Análise de Sentimentos com NLP e Web Scraping.*")

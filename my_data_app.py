import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time

st.set_page_config(page_title="Real Estate Scraper Senegal", layout="wide", initial_sidebar_state="expanded")

# Custom CSS pour rendre l'app plus jolie
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 48px;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .main-header p {
        color: white;
        font-size: 18px;
        margin-top: 10px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 32px;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 20px 0;
    }
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }
    .category-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 5px solid #667eea;
        transition: transform 0.3s;
    }
    .category-card:hover {
        transform: translateX(5px);
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>🏘️ Real Estate Scraper Senegal</h1>
        <p>Scraping intelligent des données immobilières de Coinafrique</p>
    </div>
""", unsafe_allow_html=True)

# Background function
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Display dataframe compact
def load(dataframe, title, key, key1):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f" {title}", key=key1):
            st.markdown(f"<div class='success-box'><b>Données chargées avec succès!</b></div>", unsafe_allow_html=True)

            st.subheader(' Dimensions des données')
            st.write(f'**{dataframe.shape[0]} lignes** et **{dataframe.shape[1]} colonnes**')

            st.subheader(' Aperçu des 20 premières lignes')
            st.dataframe(dataframe.head(20), use_container_width=True)

            if st.checkbox("Voir toutes les données", key=f"show_all_{key}"):
                st.subheader(' Toutes les données')
                st.dataframe(dataframe, use_container_width=True)

            csv = convert_df(dataframe)
            st.download_button(
                label=" Télécharger en CSV",
                data=csv,
                file_name=f'{title}.csv',
                mime='text/csv',
                key=key)

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# -------------------------------------------------------
# 🔥 CORRECTIONS : Aucune écriture de CSV ne remplace df
# -------------------------------------------------------

def Load_data_villas(nul_page):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for p in range(1, int(nul_page) + 1):
        status_text.markdown(f"<div class='info-box'> Scraping des Villas - Page {p}/{nul_page}...</div>", unsafe_allow_html=True)
        progress_bar.progress(p / int(nul_page))

        url = f'https://sn.coinafrique.com/categorie/villas?page={p}'

        try:
            res = get(url, timeout=10)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='col s6 m4 l3')
            data = []

            for container in containers:
                try:
                    title_elem = container.find('p', class_='ad__card-description')
                    price_elem = container.find('p', class_='ad__card-price')
                    adress_elem = container.find('p', class_='ad__card-location')
                    image_tag = container.find('img', class_='ad__card-img')
                    link_elem = container.find('a')

                    if not all([title_elem, price_elem, adress_elem, link_elem]):
                        continue

                    Title = title_elem.text.strip().split()
                    ad_type = Title[0] if Title else 'N/A'
                    price = price_elem.text.replace('CFA', '').strip()
                    adress = adress_elem.text.replace('location_on', '').strip()
                    image_link = image_tag['src']

                    page_url = 'https://sn.coinafrique.com' + link_elem['href']
                    time.sleep(0.5)

                    res_s = get(page_url, timeout=10)
                    sous_page = bs(res_s.content, "html.parser")
                    listes = sous_page.find('div', 'details-characteristics')

                    rooms = 'N/A'
                    if listes and listes.find('ul'):
                        lis = listes.find('ul').find_all('li')
                        if lis:
                            rooms = lis[0].text.replace('Nbre de pièces', '').strip()

                    data.append({
                        "AD_Type": ad_type,
                        "price": price,
                        "adress": adress,
                        "rooms": rooms,
                        "image_link": image_link
                    })

                except:
                    continue

            df = pd.concat([df, pd.DataFrame(data)], axis=0)

        except Exception as e:
            st.warning(f"Erreur page {p}: {e}")

    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("Villas_clean.csv", index=False)

    progress_bar.empty()
    status_text.empty()
    st.markdown(f"<div class='success-box'> {len(df)} villas scrapées avec succès!</div>", unsafe_allow_html=True)

    return df


def load_data_terrain(nul_page):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for p in range(1, int(nul_page) + 1):
        status_text.markdown(f"<div class='info-box'> Scraping des Terrains - Page {p}/{nul_page}...</div>", unsafe_allow_html=True)
        progress_bar.progress(p / int(nul_page))

        url = f'https://sn.coinafrique.com/categorie/terrains?page={p}'

        try:
            res = get(url, timeout=10)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='col s6 m4 l3')
            data = []

            for container in containers:
                try:
                    title_elem = container.find('p', class_='ad__card-description')
                    price_elem = container.find('p', class_='ad__card-price')
                    adress_elem = container.find('p', class_='ad__card-location')
                    image_tag = container.find('img', class_='ad__card-img')
                    link_elem = container.find('a')

                    if not all([title_elem, price_elem, adress_elem, link_elem]):
                        continue

                    Title = title_elem.text.strip().split()
                    ad_type = Title[0] if Title else 'N/A'
                    price = price_elem.text.replace('CFA', '').strip()
                    adress = adress_elem.text.replace('location_on', '').strip()
                    image_link = image_tag['src']

                    page_url = 'https://sn.coinafrique.com' + link_elem['href']
                    time.sleep(0.5)

                    res_s = get(page_url, timeout=10)
                    sous_page = bs(res_s.content, "html.parser")
                    listes = sous_page.find('div', 'details-characteristics')

                    surface = 'N/A'
                    if listes and listes.find('ul'):
                        lis = listes.find('ul').find_all('li')
                        if lis:
                            surface = lis[0].text.replace('Superficie', '').strip()

                    data.append({
                        "AD_Type": ad_type,
                        "price": price,
                        "surface": surface,
                        "adress": adress,
                        "image_link": image_link
                    })

                except:
                    continue

            df = pd.concat([df, pd.DataFrame(data)], axis=0)

        except Exception as e:
            st.warning(f"Erreur page {p}: {e}")

    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("Terrain_clean.csv", index=False)

    progress_bar.empty()
    status_text.empty()
    st.markdown(f"<div class='success-box'> {len(df)} terrains scrapés avec succès!</div>", unsafe_allow_html=True)

    return df


def load_appartments_data(nul_page):
    df = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for p in range(1, int(nul_page) + 1):
        status_text.markdown(f"<div class='info-box'> Scraping des Appartements - Page {p}/{nul_page}...</div>", unsafe_allow_html=True)
        progress_bar.progress(p / int(nul_page))

        url = f'https://sn.coinafrique.com/categorie/appartements?page={p}'

        try:
            res = get(url, timeout=10)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='col s6 m4 l3')
            data = []

            for container in containers:
                try:
                    title_elem = container.find('p', class_='ad__card-description')
                    price_elem = container.find('p', class_='ad__card-price')
                    adress_elem = container.find('p', class_='ad__card-location')
                    image_tag = container.find('img', class_='ad__card-img')
                    link_elem = container.find('a')

                    if not all([title_elem, price_elem, adress_elem, link_elem]):
                        continue

                    Title = title_elem.text.strip().split()
                    ad_type = Title[0] if Title else 'N/A'
                    price = price_elem.text.replace('CFA', '').strip()
                    adress = adress_elem.text.replace('location_on', '').strip()
                    image_link = image_tag['src']

                    page_url = 'https://sn.coinafrique.com' + link_elem['href']
                    time.sleep(0.5)

                    res_s = get(page_url, timeout=10)
                    sous_page = bs(res_s.content, "html.parser")
                    listes = sous_page.find('div', 'details-characteristics')

                    rooms = 'N/A'
                    if listes and listes.find('ul'):
                        lis = listes.find('ul').find_all('li')
                        if lis:
                            rooms = lis[0].text.replace('Nbre de pièces', '').strip()

                    data.append({
                        "AD_Type": ad_type,
                        "price": price,
                        "adress": adress,
                        "rooms": rooms,
                        "image_link": image_link
                    })

                except:
                    continue

            df = pd.concat([df, pd.DataFrame(data)], axis=0)

        except Exception as e:
            st.warning(f"Erreur page {p}: {e}")

    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv("Appartment_clean.csv", index=False)

    progress_bar.empty()
    status_text.empty()
    st.markdown(f"<div class='success-box'> {len(df)} appartements scrapés avec succès!</div>", unsafe_allow_html=True)

    return df



# ----------------------------------------------------------
# Sidebar
# ----------------------------------------------------------

st.sidebar.markdown("##  Configuration")
st.sidebar.markdown("---")
Pages = st.sidebar.slider(' Nombre de pages à scraper', min_value=1, max_value=50, value=5, step=1)
st.sidebar.markdown("---")

Choices = st.sidebar.radio('', [
    ' Scraper des données',
    ' Télécharger données scrapées',
    ' Dashboard des données',
    ' Évaluer l\'application'
], label_visibility="collapsed")

add_bg_from_local('img_file2.jpg')
local_css('style.css')

# ----------------------------------------------------------
# Scraper
# ----------------------------------------------------------

if Choices == ' Scraper des données':
    st.markdown("##  Scraping de Données")

    st.markdown("""
    <div class='info-box'>
        <b>ℹ Information:</b> Le scraping peut prendre du temps. 
        Soyez patient et respectez le site web!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("###  Sélectionnez la catégorie à scraper")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='category-card'>
            <h3 style='color: #667eea;'> Villas</h3>
            <p style='color: #666;'>Type d'annonce, Prix, Adresse, Chambres, Image</p>
        </div>
        """, unsafe_allow_html=True)
        scrape_villas = st.checkbox("Scraper les Villas", key="villa_check")

    with col2:
        st.markdown("""
        <div class='category-card'>
            <h3 style='color: #667eea;'> Terrains</h3>
            <p style='color: #666;'>Type d'annonce, Prix, Surface, Adresse, Image</p>
        </div>
        """, unsafe_allow_html=True)
        scrape_terrains = st.checkbox("Scraper les Terrains", key="terrain_check")

    with col3:
        st.markdown("""
        <div class='category-card'>
            <h3 style='color: #667eea;'> Appartements</h3>
            <p style='color: #666;'>Type d'annonce, Prix, Adresse, Chambres, Image</p>
        </div>
        """, unsafe_allow_html=True)
        scrape_appartements = st.checkbox("Scraper les Appartements", key="appart_check")

    st.markdown("---")

    if st.button(' LANCER LE SCRAPING', key='start_scrape'):
        if not (scrape_villas or scrape_terrains or scrape_appartements):
            st.error(" Veuillez sélectionner au moins une catégorie à scraper!")
        else:
            with st.spinner('Scraping en cours...'):

                if scrape_villas:
                    st.markdown("###  Scraping des Villas")
                    df_v = Load_data_villas(Pages)
                    load(df_v, 'Données Villas', '1', '101')

                if scrape_terrains:
                    st.markdown("###  Scraping des Terrains")
                    df_t = load_data_terrain(Pages)
                    load(df_t, 'Données Terrains', '2', '102')

                if scrape_appartements:
                    st.markdown("###  Scraping des Appartements")
                    df_a = load_appartments_data(Pages)
                    load(df_a, 'Données Appartements', '3', '103')

                st.balloons()


# ----------------------------------------------------------
# Fichiers téléchargés
# ----------------------------------------------------------

elif Choices == ' Télécharger données scrapées':
    st.markdown("##  Téléchargement des Données")

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            Villas = pd.read_csv('Villas_clean.csv')
            load(Villas, 'Villas', '1', '101')
        except:
            st.warning("Fichier Villas_clean.csv non trouvé")

    with col2:
        try:
            Terrain = pd.read_csv('Terrain_clean.csv')
            load(Terrain, 'Terrains', '2', '102')
        except:
            st.warning("Fichier Terrain_clean.csv non trouvé")

    with col3:
        try:
            Appartment = pd.read_csv('Appartment_clean.csv')
            load(Appartment, 'Appartements', '3', '103')
        except:
            st.warning("Fichier Appartment_clean.csv non trouvé")


# ----------------------------------------------------------
# Dashboard
# ----------------------------------------------------------

elif Choices == ' Dashboard des données':

    try:
        df1 = pd.read_csv('Villas_clean.csv')
        df2 = pd.read_csv('Terrain_clean.csv')
        df3 = pd.read_csv('Appartment_clean.csv')

        st.markdown("##  Dashboard Immobilier")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2>{len(df1)}</h2>
                    <p>Villas</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2>{len(df2)}</h2>
                    <p>Terrains</p>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2>{len(df3)}</h2>
                    <p>Appartements</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top 5 Prix Villas")
            fig = plt.figure(figsize=(10, 6))
            price_counts = df1['price'].value_counts()[:5]
            plt.bar(price_counts.index, price_counts.values)
            st.pyplot(fig)

        with col2:
            st.markdown("### Top 5 Prix Terrains")
            fig = plt.figure(figsize=(10, 6))
            price_counts = df2['price'].value_counts()[:5]
            plt.bar(price_counts.index, price_counts.values)
            st.pyplot(fig)

    except:
        st.error("Veuillez scraper d'abord les données !")


# ----------------------------------------------------------
# Evaluation
# ----------------------------------------------------------

else:
    st.markdown("##  Évaluez Notre Application")

    st.markdown("""
    <div class='info-box'>
        <b> Votre avis compte !</b><br>
        Aidez-nous à améliorer cette application en partageant votre expérience.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button(" Kobo Evaluation Form", use_container_width=True):
            st.markdown('<meta http-equiv="refresh" content="0; url=https://ee.kobotoolbox.org/x/fHh5uOes">', unsafe_allow_html=True)

        st.write("")
        if st.button(" Google Forms Evaluation", use_container_width=True):
            st.markdown('<meta http-equiv="refresh" content="0; url=https://forms.gle/YGKK9jDgDcJQQQxMA">', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Développé pour l'immobilier au Sénégal | Données de <a href='https://sn.coinafrique.com/' target='_blank'>Coinafrique</a></p>
    </div>
""", unsafe_allow_html=True)

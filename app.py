import requests
import streamlit as st
import pandas as pd
import plost
import pydeck as pdk


# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Data Eng. with Kasra", page_icon=":computer:", layout="wide")

#Load Data----------------------------------------------------
df = pd.read_csv('MetroVan.csv')
df = df.drop_duplicates(subset='ZipCode', keep="first")
df_obj = df.select_dtypes(['object'])
df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Use local CSS ----------------------------
with open('style/style.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#Side setting -------------------------------------
st.sidebar.header('Dashboard V2.0')
st.sidebar.subheader('Housing parameter')
#df.Town.value_counts().sort_values()
df1 = df.groupby('Town').size().sort_values(ascending=False).reset_index(name='count')
#Sel_Town = st.sidebar.radio("Select town", df.Town.value_counts())  #unique
Sel_Town = st.sidebar.radio("Select town", df1.Town.unique())  #unique
rdf = df.loc[df['Town'] == Sel_Town]  # Set selected Town
# ---- HEADER SECTION ---------------------------------
with st.container():
    st.subheader("British Columbia Housing Distribution and Price Viso")
# Row A ---------------------------------------
#with st.container():
#    st.write("---")
#    col1, col2, col3 = st.columns(3)
#    col1.metric("Max price: " + str(rdf.shape[0]), "Max: " + str(rdf.Price.min()) , "Max: " + str(rdf.Price.max()))
#    col2.metric("Min price: " + str(rdf.shape[0]), "Min: " + str(rdf.Price.min()) , "Min: " + str(rdf.Price.min()))
#    col3.metric("Average: " + str(rdf.shape[0]), "Avg: " + str(rdf.Price.min()) , "Avg: " + str(rdf.Price.min())) 
    
# Row B ---------------------------------------
with st.container():
    st.write("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        dfr = rdf.query(' -121 > longitude > -124')
        dfr = rdf.query('48 < latitude < 51')

        st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
        latitude = dfr.latitude.mean(),
        longitude = dfr.longitude.mean(),
        zoom=11,
        pitch=50,
        ),
        layers=[
        pdk.Layer(
           'ScatterplotLayer', #'HexagonLayer',
           data=dfr,
           get_position='[longitude, latitude]',
           radius=50,
           elevation_scale=14,
           elevation_range=[0, 500],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=dfr,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=50,
        ), ],))

    with col2:
        plost.area_chart(data=rdf, x='Price', y=dict(field='Area', aggregate='mean'), color='Beds', height=530)
    
    with col3:
        st.vega_lite_chart(rdf, {
    'mark': {'type': 'circle', 'tooltip': True},
    'width': 600,
    "height": 530,
    'encoding': {
        'x': {'field': 'Price', 'type': 'quantitative'},
        'y': {'field': 'Beds', 'type': 'quantitative'},
        'size': {'field': 'Baths', 'type': 'quantitative'},
        'color': {'field': 'Baths', 'type': 'quantitative'},
    },
})

# Row C ---------------------------------------
with st.container():
    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander('Know more...'):
            st.write("Item price")
        plost.line_chart(data=rdf,  x='ZipCode',  y='Price', height=450)

    with col2:
        with st.expander('Listing in the town by following Brokers'):
            st.write("They are active brokers in the selected town")
        #st.caption("Broker List")
        st.dataframe(rdf.Broker.unique(), width=880)

    
    with col3:
        with st.expander('Know more...'):
            st.write("Correlation between Number of beds and price")
        plost.donut_chart(data=rdf, theta='Price', color='Beds', height=450)
# Row D ---------------------------------------
with st.container():
    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        plost.hist(data=rdf,  x='Price', bin=20,  aggregate='count')

    with col2:
        plost.xy_hist(data=rdf, x='Price', y='Area', x_bin=dict(maxbins=20),  y_bin=dict(maxbins=20),  height=400)
  
    with col3:
        plost.bar_chart(data=rdf, bar='Price', value='Area', width=600, pan_zoom='Beds')
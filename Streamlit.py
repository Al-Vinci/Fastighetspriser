import streamlit as st
import joblib
import os
import numpy as np
import pandas as pd

# Laddar modeller
# LGBM-modell + lista på kolumner som användes vid träning
model_lgbm, lgbm_features = joblib.load("villa_lgbm.pkl")
model_lgbm_lagenhet, lgbm_features_lagenhet = joblib.load("lagenhet_lgbm.pkl")
model_lgbm_fritidshus, lgbm_features_fritidshus = joblib.load("fritidshus_lgbm.pkl")
model_lgbm_radhus, lgbm_features_radhus = joblib.load("radhus_lgbm.pkl")

# CatBoost-modell
model_cb = joblib.load("villa_cb_gs.pkl")
model_cb_lagenhet = joblib.load("lagenhet_cb.pkl")
model_cb_fritidshus = joblib.load("fritidshus_cb.pkl")
model_cb_radhus = joblib.load("radhus_cb.pkl")

st.title("Bostadspriser, prediktion")

val = st.radio("Välj boendeform:", ["Lägenhet", "Hus", "Radhus", "Fritidshus"], horizontal=True)

# För att göra inputs kolumnvis istället för en lista
col1, col2, col3 = st.columns(3)

with col1:
    boarea = st.number_input("Boarea (kvm)", min_value=10, max_value=500, value=100)
    rum = st.number_input("Antal rum", min_value=1, max_value=15, value=4)

with col2:
    if val in ["Hus", "Fritidshus", "Radhus"]:
        biarea = st.number_input("Biarea (kvm)", min_value=0, max_value=500, value=30)
        tomtarea = st.number_input("Tomtarea (kvm)", min_value=0, max_value=100000, value=500)

    if val == "Lägenhet":
        vaning = st.number_input("Våning", min_value=0, max_value=100, value=0, step=1)

with col3:
    adress = st.text_input("Adress utan nummer", "Karlavägen")
    omrade = st.text_input("Område", "Östermalm")
    ort = st.text_input("Ort", "Stockholm")


if val == "Hus":
    # Skapa input-dataframe
    input_dict = {
        "Boarea": boarea,
        "Biarea": biarea,
        "Rum": rum,
        "Tomtarea": tomtarea,
        "Adress": adress,
        "Område": omrade,
        "Ort": ort}

    X_new = pd.DataFrame([input_dict])

    # LGBM: kategoriska kolumner och reindex
    categorical_cols_lgbm = ["Adress", "Område", "Ort"]

    for col in categorical_cols_lgbm:
        if col in X_new.columns:
            X_new[col] = X_new[col].astype("category")

    # Säkerställ att alla kolumner som modellen tränades på finns
    X_new_lgbm = X_new.reindex(columns=lgbm_features, fill_value=0)

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # Prediktioner
    if st.button("Beräkna pris"):
        # Spara tidigare resultat
        previous_result = st.session_state.last_result
        # LGBM
        y_pred_lgbm_log = model_lgbm.predict(X_new_lgbm)[0]
        y_pred_lgbm = np.expm1(y_pred_lgbm_log)
        # CatBoost
        y_pred_cb = model_cb.predict(X_new)[0]
        # Visa resultat
        st.success(
            f"LGBM-modellen: {y_pred_lgbm:,.0f} kr | "
            f"CatBoost-modellen: {y_pred_cb:,.0f} kr")
        # Uppdatera session_state med senaste resultat
        st.session_state.last_result = f"LGBM: {y_pred_lgbm:,.0f} kr | CatBoost: {y_pred_cb:,.0f} kr"

    # Visa tidigare resultat med 60% opacity
        if previous_result:
            st.markdown(
                f"<p style='opacity:0.5;font-size:16px;'>Tidigare prediktion: {previous_result}</p>",
                unsafe_allow_html=True)


elif val == "Lägenhet":
# Skapa input-dataframe
    input_dict_lagenhet = {
        "Boarea": boarea,
        "Rum": rum,
        "Våning": vaning,
        "Adress": adress,
        "Område": omrade,
        "Ort": ort}

    X_new_lgh = pd.DataFrame([input_dict_lagenhet])

    # LGBM: kategoriska kolumner och reindex
    categorical_cols_lgbm = ["Adress", "Område", "Ort"]

    for col in categorical_cols_lgbm:
        if col in X_new_lgh.columns:
            X_new_lgh[col] = X_new_lgh[col].astype("category")

    # Säkerställ att alla kolumner som modellen tränades på finns
    X_new_lgh_lgbm = X_new_lgh.reindex(columns=lgbm_features_lagenhet, fill_value=0)

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # Prediktioner
    if st.button("Beräkna pris"):
        # Spara tidigare resultat
        previous_result = st.session_state.last_result
        # LGBM
        y_pred_lgbm_lagenhet_log = model_lgbm_lagenhet.predict(X_new_lgh_lgbm)[0]
        y_pred_lgbm_lagenhet = np.expm1(y_pred_lgbm_lagenhet_log)
        # CatBoost
        y_pred_cb_lagenhet = model_cb_lagenhet.predict(X_new_lgh)[0]
        # Visa resultat
        st.success(
            f"LGBM-modellen: {y_pred_lgbm_lagenhet:,.0f} kr | "
            f"CatBoost-modellen: {y_pred_cb_lagenhet:,.0f} kr")
        # Uppdatera session_state med senaste resultat
        st.session_state.last_result = f"LGBM: {y_pred_lgbm_lagenhet:,.0f} kr | CatBoost: {y_pred_cb_lagenhet:,.0f} kr"

    # Visa tidigare resultat med 60% opacity
        if previous_result:
            st.markdown(
                f"<p style='opacity:0.5;font-size:16px;'>Tidigare prediktion: {previous_result}</p>",
                unsafe_allow_html=True)


elif val == "Fritidshus":
    # Skapa input-dataframe
    input_dict = {
        "Boarea": boarea,
        "Biarea": biarea,
        "Rum": rum,
        "Tomtarea": tomtarea,
        "Adress": adress,
        "Område": omrade,
        "Ort": ort}

    X_new = pd.DataFrame([input_dict])

    # LGBM: kategoriska kolumner och reindex
    categorical_cols_lgbm = ["Adress", "Område", "Ort"]

    for col in categorical_cols_lgbm:
        if col in X_new.columns:
            X_new[col] = X_new[col].astype("category")

    # Säkerställ att alla kolumner som modellen tränades på finns
    X_new_lgbm_fth = X_new.reindex(columns=lgbm_features_fritidshus, fill_value=0)

    # Konverterar till str
    X_new["Ort"] = X_new["Ort"].astype("str")
    
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # Prediktioner
    if st.button("Beräkna pris"):
        # Spara tidigare resultat
        previous_result = st.session_state.last_result
        # LGBM
        y_pred_lgbm_fth_log = model_lgbm_fritidshus.predict(X_new_lgbm_fth)[0]
        y_pred_lgbm_fth = np.expm1(y_pred_lgbm_fth_log)
        # CatBoost
        y_pred_cb_fth = model_cb_fritidshus.predict(X_new)[0]
        # Visa resultat
        st.success(
            f"LGBM-modellen: {y_pred_lgbm_fth:,.0f} kr | "
            f"CatBoost-modellen: {y_pred_cb_fth:,.0f} kr")
        # Uppdatera session_state med senaste resultat
        st.session_state.last_result = f"LGBM: {y_pred_lgbm_fth:,.0f} kr | CatBoost: {y_pred_cb_fth:,.0f} kr"

    # Visa tidigare resultat med 60% opacity
        if previous_result:
            st.markdown(
                f"<p style='opacity:0.5;font-size:16px;'>Tidigare prediktion: {previous_result}</p>",
                unsafe_allow_html=True)

if val == "Radhus":
    # Skapa input-dataframe
    input_dict = {
        "Boarea": boarea,
        "Biarea": biarea,
        "Rum": rum,
        "Tomtarea": tomtarea,
        "Adress": adress,
        "Område": omrade,
        "Ort": ort}

    X_new = pd.DataFrame([input_dict])

    # LGBM: kategoriska kolumner och reindex
    categorical_cols_lgbm = ["Adress", "Område", "Ort"]

    for col in categorical_cols_lgbm:
        if col in X_new.columns:
            X_new[col] = X_new[col].astype("category")

    # Säkerställ att alla kolumner som modellen tränades på finns
    X_new_lgbm_radhus = X_new.reindex(columns=lgbm_features_radhus, fill_value=0)

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # Prediktioner
    if st.button("Beräkna pris"):
        # Spara tidigare resultat
        previous_result = st.session_state.last_result
        # LGBM
        y_pred_lgbm_log_radhus = model_lgbm_radhus.predict(X_new_lgbm_radhus)[0]
        y_pred_lgbm_radhus = np.expm1(y_pred_lgbm_log_radhus)
        # CatBoost
        y_pred_cb_radhus = model_cb_radhus.predict(X_new)[0]
        
        # Visa resultat
        st.success(
            f"LGBM-modellen: {y_pred_lgbm_radhus:,.0f} kr | "
            f"CatBoost-modellen: {y_pred_cb_radhus:,.0f} kr")
        # Uppdatera session_state med senaste resultat
        st.session_state.last_result = f"LGBM: {y_pred_lgbm_radhus:,.0f} kr | CatBoost: {y_pred_cb_radhus:,.0f} kr"

    # Visa tidigare resultat med 60% opacity
        if previous_result:
            st.markdown(
                f"<p style='opacity:0.5;font-size:16px;'>Tidigare prediktion: {previous_result}</p>",
                unsafe_allow_html=True)


############# Röstning ##############
st.header("Rösta på bästa modellen")

# Filnamn för att spara röster
rost_fil = "roster.csv"

# Initiera fil om den inte finns
if not os.path.exists(rost_fil):
    df_init = pd.DataFrame({"bostadstyp": [], "choice": []})
    df_init.to_csv(rost_fil, index=False)

# Ladda röster
roster = pd.read_csv(rost_fil)

# Välj boendeform
bostadstyp = val

# Röstningsval
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("LightGBM"):
        rost_val = "LightGBM"
with col2:
    if st.button("CatBoost"):
        rost_val = "CatBoost"
with col3:
    if st.button("Ingen"):
        rost_val = "Ingen"


if "rost_val" in locals():
    ny_rost = pd.DataFrame({"bostadstyp": [bostadstyp], "choice": [rost_val]})
    roster = pd.concat([roster, ny_rost], ignore_index=True)
    roster.to_csv(rost_fil, index=False)
    st.success(f"Tack, du röstade på: {rost_val} för {bostadstyp}")

# Visa resultat per boendeform
if not roster.empty:
    st.subheader("Röstningsresultat per boendeform")

    for b_typ in ["Lägenhet", "Hus", "Fritidshus"]:
        st.write(f"##### {b_typ}")
        urval = roster[roster["bostadstyp"] == b_typ]
        if urval.empty:
            st.write("Inga röster än.")
        else:
            rost_resultat = urval["choice"].value_counts()
            # Jämför CatBoost och LightGBM
            if "CatBoost" in rost_resultat and "LightGBM" in rost_resultat:
                total = rost_resultat["CatBoost"] + rost_resultat["LightGBM"]
                if rost_resultat["CatBoost"] > rost_resultat["LightGBM"]:
                    st.info(f"CatBoost leder med {(rost_resultat['CatBoost']/total*100):.0f}%")
                elif rost_resultat["LightGBM"] > rost_resultat["CatBoost"]:
                    st.info(f"LightGBM leder med {(rost_resultat['LightGBM']/total*100):.0f}%")
                else:
                    st.info("Det är lika mellan CatBoost och LightGBM!")



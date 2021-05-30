import streamlit as st
import numpy as np
import pandas as pd
import altair as alt




df = pd.read_csv("/Users/yukikubota/Desktop/Python/DataAnalitics/user_visit.csv")

st.dataframe(df)

options = st.multiselect(
        'Which columns do you investigate?',
        df.columns
        )

if len(options) > 0 :
    df.loc[:,options]
    
    c = alt.Chart(df).mark_circle().encode(
        x='user_id', y='referrer')
    st.altair_chart(c, use_container_width=True)
    
    
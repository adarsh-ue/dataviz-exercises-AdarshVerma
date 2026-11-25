#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture 9 — Class Exercise
World Happiness Dashboard: Step 4 dashboard + a diverging-colour chart.

Purpose: helps a UN policy analyst see which countries lead on happiness,
and how far each country sits above or below the global average.

@author: Adarsh Verma
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page configuration, title and data source
st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout='wide')
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# Data Ingestion (path relative to this file, so it also works when deployed)
DATA = Path(__file__).parent.parent / "data" / "world_happiness_2023.csv"
df = pd.read_csv(DATA)
df.columns = ['Country', 'Region', 'Score', 'GDP', 'Social_Support',
              'Life_Expectancy', 'Freedom', 'Generosity', 'Corruption']

GLOBAL_AVG = df['Score'].mean()

# Side bar filters
with st.sidebar:
    st.header("Filters")
    regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

# filter data by region and top_n
filtered = df if selected_region == 'All Regions' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean() - GLOBAL_AVG:+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1, 'Score')['Country'].values[0])

st.divider()

# ── Chart 1: top N bar chart (from Step 4) ───────────────────────────────
fig = px.bar(top, x='Score', y='Country', orientation='h',
             labels={'Score': 'Happiness Score (0–10)', 'Country': ''},
             template='plotly_white',
             title=f'Happiest {top_n} Countries in 2023 - {selected_region}')

fig.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                  xaxis=dict(range=[0, 8.0]), height=600)

st.plotly_chart(fig, width='stretch')

st.divider()

# ── Chart 2 (exercise): diverging chart around the global average ───────
# Meaningful midpoint = global average score. Each bar shows how far a
# country sits above (blue) or below (red) that average.
dev = filtered.assign(Deviation=filtered['Score'] - GLOBAL_AVG).sort_values('Deviation')

# symmetric colour range so equal distances get equal colour intensity
max_abs = dev['Deviation'].abs().max()

fig2 = px.bar(dev, x='Deviation', y='Country', orientation='h',
              color='Deviation',
              color_continuous_scale='RdBu',          # diverging: red ↔ blue
              color_continuous_midpoint=0,            # white = global average
              range_color=[-max_abs, max_abs],
              hover_data={'Score': ':.2f', 'Region': True, 'Deviation': ':+.2f'},
              labels={'Deviation': 'Difference from global average', 'Country': ''},
              template='plotly_white',
              title=f'Above or below the global average? 2023 - {selected_region}')

# thin outline so near-average (almost white) bars stay visible
fig2.update_traces(marker_line_color='lightgrey', marker_line_width=0.5)

# midpoint line + annotation
fig2.add_vline(x=0, line_width=1.5, line_dash='dash', line_color='dimgrey')
fig2.add_annotation(x=0, y=1, xref='x', yref='paper',
                    text=f'Midpoint: global average = {GLOBAL_AVG:.2f}',
                    showarrow=False, yanchor='bottom', xanchor='left', xshift=6,
                    font=dict(size=12, color='dimgrey'))

fig2.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                   xaxis=dict(range=[-max_abs * 1.1, max_abs * 1.1], zeroline=False),
                   coloraxis_colorbar=dict(title='Δ score'),
                   height=max(400, 22 * len(dev) + 120),
                   margin=dict(t=80))

st.plotly_chart(fig2, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")

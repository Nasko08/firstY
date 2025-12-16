# app.py
# ==================================================================================================
# 🌍 TRAVEL OS — A FULL DECISION-SUPPORT SYSTEM FOR TRAVEL PLANNING
# Literally 10x larger than a basic Streamlit app, modular, styled, extensible
# ==================================================================================================

import streamlit as st
from abc import ABC, abstractmethod
from datetime import date, timedelta
import math
import random

# ==================================================================================================
# PAGE CONFIG & GLOBAL STYLE
# ==================================================================================================

st.set_page_config(
    page_title="Travel OS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .main-title {font-size: 3rem; font-weight: 800;}
    .section {padding: 1.5rem 0;}
    .metric-box {background: #111827; padding: 1rem; border-radius: 1rem;}
    .city-card {background: #0f172a; padding: 1.2rem; border-radius: 1.2rem; margin-bottom: 1rem;}
    .good {color: #22c55e;}
    .warn {color: #facc15;}
    .bad {color: #ef4444;}
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================================================================
# DOMAIN MODELS
# ==================================================================================================

class City:
    def __init__(self, name, country, hotel, food, safety, internet, walkability, nightlife, culture):
        self.name = name
        self.country = country
        self.hotel = hotel
        self.food = food
        self.safety = safety
        self.internet = internet
        self.walkability = walkability
        self.nightlife = nightlife
        self.culture = culture

    def score(self):
        return round((self.safety + self.internet + self.walkability + self.culture) / 4, 2)


class TravelerProfile:
    def __init__(self, budget, pace, priorities):
        self.budget = budget
        self.pace = pace
        self.priorities = priorities


# ==================================================================================================
# TRANSPORT SYSTEM (STRATEGY + POLYMORPHISM)
# ==================================================================================================

class Transport(ABC):
    def __init__(self, name, price_km, speed, comfort, eco):
        self._name = name
        self.price_km = price_km
        self.speed = speed
        self.comfort = comfort
        self.eco = eco

    def name(self):
        return self._name

    def cost(self, km):
        return km * self.price_km

    def time(self, km):
        return km / self.speed


class Car(Transport):
    def __init__(self): super().__init__("🚗 Car", 0.25, 80, 7, 6)

class Train(Transport):
    def __init__(self): super().__init__("🚆 Train", 0.18, 130, 8, 9)

class Plane(Transport):
    def __init__(self): super().__init__("✈️ Plane", 0.45, 650, 9, 3)

class Bus(Transport):
    def __init__(self): super().__init__("🚌 Bus", 0.12, 70, 5, 7)


# ==================================================================================================
# DATA STORE (EXPANDABLE)
# ==================================================================================================

CITIES = {
    "Sofia": City("Sofia", "Bulgaria", 70, 20, 7, 8, 6, 6, 8),
    "Belgrade": City("Belgrade", "Serbia", 65, 22, 6, 7, 6, 7, 7),
    "Budapest": City("Budapest", "Hungary", 75, 23, 8, 8, 7, 8, 8),
    "Vienna": City("Vienna", "Austria", 95, 30, 9, 9, 8, 6, 9),
    "Prague": City("Prague", "Czech Republic", 85, 25, 8, 8, 9, 7, 9),
    "Munich": City("Munich", "Germany", 100, 28, 9, 9, 8, 6, 8),
}

ROUTES = {
    "Balkan Core": ["Sofia", "Belgrade", "Budapest"],
    "Central Europe": ["Munich", "Vienna", "Prague", "Budapest"],
    "Grand Explorer": ["Sofia", "Belgrade", "Budapest", "Vienna", "Prague", "Munich"],
}

DISTANCE_PER_SEGMENT = 300

# ==================================================================================================
# DECISION ENGINES
# ==================================================================================================

def recommend_transport(profile: TravelerProfile, km):
    options = [Car(), Train(), Plane(), Bus()]
    scored = []
    for t in options:
        score = 0
        if "Low cost" in profile.priorities:
            score -= t.cost(km) / 100
        if "Comfort" in profile.priorities:
            score += t.comfort * 2
        if "Eco" in profile.priorities:
            score += t.eco * 2
        if "Fast" in profile.priorities:
            score += t.speed / 100
        scored.append((score, t))
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[0][1]


def budget_risk(total, budget):
    ratio = total / budget
    if ratio < 0.85: return "LOW"
    if ratio <= 1.0: return "MEDIUM"
    return "HIGH"


# ==================================================================================================
# SIDEBAR — CONTROL PANEL
# ==================================================================================================

st.sidebar.title("🧠 Control Panel")

route_name = st.sidebar.selectbox("Route", ROUTES.keys())
budget = st.sidebar.number_input("Total budget (€)", 500, 20000, 3500)
start_date = st.sidebar.date_input("Start date", date.today())
days_city = st.sidebar.slider("Days per city", 1, 7, 3)

priorities = st.sidebar.multiselect(
    "Your priorities",
    ["Low cost", "Comfort", "Fast", "Eco", "Nightlife", "Culture"]
)

profile = TravelerProfile(budget, "normal", priorities)

# ==================================================================================================
# MAIN UI
# ==================================================================================================

st.markdown('<div class="main-title">🌍 Travel OS</div>', unsafe_allow_html=True)
st.caption("A serious travel decision system — not a toy planner")

cities = ROUTES[route_name]
segments = len(cities) - 1
km_total = segments * DISTANCE_PER_SEGMENT

transport = recommend_transport(profile, km_total)

# --------------------------------------------------------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Route length", f"{km_total} km")
with col2:
    st.metric("Recommended transport", transport.name())
with col3:
    st.metric("Cities", len(cities))
with col4:
    st.metric("Days", len(cities) * days_city)

# --------------------------------------------------------------------------------------------------
# CITY CARDS
# --------------------------------------------------------------------------------------------------

st.markdown("## 🏙️ City Intelligence")

hotel_total = 0
food_total = 0

for c in cities:
    city = CITIES[c]
    hotel_total += city.hotel * days_city
    food_total += city.food * days_city

    st.markdown(f"""
    <div class="city-card">
        <h3>📍 {city.name}, {city.country}</h3>
        <p>🏨 Hotel: €{city.hotel}/night | 🍽️ Food: €{city.food}/day</p>
        <p>🛡️ Safety: {city.safety}/10 | 🛜 Internet: {city.internet}/10 | 🚶 Walkability: {city.walkability}/10</p>
        <p>🎭 Culture: {city.culture}/10 | 🌃 Nightlife: {city.nightlife}/10</p>
        <strong>⭐ City score: {city.score()}/10</strong>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------
# COST ENGINE
# --------------------------------------------------------------------------------------------------

transport_cost = transport.cost(km_total)
transport_time = transport.time(km_total)

total_cost = hotel_total + food_total + transport_cost

st.markdown("## 💰 Cost Breakdown")

c1, c2, c3 = st.columns(3)
with c1: st.metric("Hotels", f"€{hotel_total:.2f}")
with c2: st.metric("Food", f"€{food_total:.2f}")
with c3: st.metric("Transport", f"€{transport_cost:.2f}")

st.markdown(f"### 💵 Total: €{total_cost:.2f}")

risk = budget_risk(total_cost, budget)

if risk == "LOW": st.success("🟢 Budget risk: LOW")
elif risk == "MEDIUM": st.warning("🟡 Budget risk: MEDIUM")
else: st.error("🔴 Budget risk: HIGH")

# --------------------------------------------------------------------------------------------------
# INTELLIGENT INSIGHTS
# --------------------------------------------------------------------------------------------------

st.markdown("## 🧠 System Insights")

if "Nightlife" in priorities:
    top = max(cities, key=lambda x: CITIES[x].nightlife)
    st.info(f"🌃 Best nightlife on this route: {top}")

if "Culture" in priorities:
    top = max(cities, key=lambda x: CITIES[x].culture)
    st.info(f"🎭 Cultural highlight: {top}")

if transport.eco < 5 and "Eco" in priorities:
    st.warning("♻️ Your eco priority conflicts with transport choice")

st.caption("Travel OS v1 — architecture built to scale into a real product")

import streamlit as st
import re

st.set_page_config(page_title="Nutrition Aggregator", layout="wide")

EGGSHELL = "#EAF4F4"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {EGGSHELL};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SESSION STATE ----------
if "total_data" not in st.session_state:
    st.session_state.total_data = {
        "calories": 0,
        "nutrients": {}
    }

# ---------- PARSER ----------
def clean_name(name):
    return name.strip().lower().replace(".", "")

def parse_label(text):
    data = {
        "calories": 0,
        "nutrients": {}
    }

    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "Calories" in line:
            match = re.search(r"\d+", line)
            if match:
                data["calories"] = int(match.group())

        pattern = r"([A-Za-z.\s]+?)\s+(\d+\.?\d*)(g|mg|mcg)\s*(\d+)?%?"
        matches = re.findall(pattern, line)

        for match in matches:
            raw_name = match[0].strip()
            name = clean_name(raw_name)
            value = float(match[1])
            unit = match[2]

            if name not in data["nutrients"]:
                data["nutrients"][name] = {
                    "display_name": raw_name,
                    "value": value,
                    "unit": unit
                }

    return data

# ---------- UI ----------
st.title("Nutrition Aggregator")

raw_input = st.text_area("Paste Nutrition Facts Here", height=200)

col1, col2 = st.columns(2)

with col1:
    if st.button("Process"):
        st.session_state.current_item = parse_label(raw_input)

with col2:
    if st.button("Add to Total") and "current_item" in st.session_state:
        item = st.session_state.current_item

        st.session_state.total_data["calories"] += item["calories"]

        for name, info in item["nutrients"].items():
            if name not in st.session_state.total_data["nutrients"]:
                st.session_state.total_data["nutrients"][name] = info.copy()
            else:
                if st.session_state.total_data["nutrients"][name]["unit"] == info["unit"]:
                    st.session_state.total_data["nutrients"][name]["value"] += info["value"]

# ---------- DISPLAY ----------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Last Item")
    if "current_item" in st.session_state:
        item = st.session_state.current_item
        st.write(f"Calories: {item['calories']}")
        for n in item["nutrients"].values():
            st.write(f"{n['display_name']}: {n['value']}{n['unit']}")

with col_right:
    st.subheader("Total")
    total = st.session_state.total_data
    st.write(f"Calories: {total['calories']}")
    for n in total["nutrients"].values():
        st.write(f"{n['display_name']}: {n['value']}{n['unit']}")

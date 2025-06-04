import streamlit as st
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="Supplement Schedule Extractor", layout="wide")
st.title("Upload Your Supplement Prescription (JPEG Only)")

uploaded_file = st.file_uploader("Choose a prescription image (JPEG)", type=['jpg', 'jpeg'])

def parse_prescription(text):
    supplements = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or 'Spry.' in line:
            continue
        if 'Tab.' in line or 'Cap.' in line:
            match = re.match(
                r'(Tab\.|Cap\.)\s+([A-Za-z0-9\s\-\+>]+)\s+Day (\d+) - Day (\d+)\s+(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]+(\d+)',
                line)
            if match:
                type_ = match.group(1)
                name = match.group(2).strip()
                day_start = match.group(3)
                day_end = match.group(4)
                dose_morning = int(match.group(5))
                dose_noon = int(match.group(6))
                dose_evening = int(match.group(7))
                dose_night = int(match.group(8))
                timing = {}
                if dose_morning > 0: timing["Morning"] = dose_morning
                if dose_noon > 0: timing["Noon"] = dose_noon
                if dose_evening > 0: timing["Evening"] = dose_evening
                if dose_night > 0: timing["Night"] = dose_night
                supplements.append({
                    "Name": name,
                    "Type": type_,
                    "Days": f"Day {day_start} - Day {day_end}",
                    "Timing": timing
                })
    return supplements

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Prescription", use_column_width=True)
    text = pytesseract.image_to_string(image)
    supplements = parse_prescription(text)
    if supplements:
        st.subheader("Extracted Supplement Schedule")
        for supp in supplements:
            st.markdown(f"**{supp['Name']} ({supp['Type']}) — {supp['Days']}**")
            for time, dose in supp['Timing'].items():
                st.write(f"{time}: {dose}")
            st.markdown("---")
    else:
        st.warning("No valid supplements found. Try a clearer image.")

st.markdown(
    """
    <hr>
    <sub>
    This is a rapid demo MVP for supplement schedule extraction. Only works for typed JPEGs, ignores sprays, no data is stored.
    </sub>
    """, unsafe_allow_html=True)

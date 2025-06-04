import streamlit as st
import re

st.set_page_config(page_title="Supplement Schedule Extractor", layout="wide")
st.title("Supplement Schedule Extractor")
st.write("Paste your prescription text below (from any OCR tool).")

prescription_text = st.text_area(
    "Paste the text from your prescription here (use an OCR website like [onlineocr.net](https://www.onlineocr.net/) to get text from your image).",
    height=300
)

def parse_prescription(text):
    supplements = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty, spray, and irrelevant lines
        if not line or 'Spry.' in line or 'Spry' in line or line.lower().startswith('finding summary'):
            continue
        # Only lines with Tab. or Cap.
        if 'Tab.' in line or 'Cap.' in line or 'Tab' in line or 'Cap' in line:
            # Fuzzy match: type, name, day range, possible doses
            type_match = re.search(r'(Tab\.?|Cap\.?)', line)
            name_match = re.search(r'(Tab\.?|Cap\.?)\s*([A-Za-z0-9 >\+\-]+)', line)
            days_match = re.search(r'Day\s*(\d+)[^\d]+Day\s*(\d+)', line)
            # Find doses (e.g. 1 - 0 - 0 - 1 or 0 - 0 - 0 - 1)
            dose_match = re.search(r'(\d)\s*-\s*(\d)\s*-\s*(\d)\s*-\s*(\d)', line)
            if type_match and name_match and days_match:
                type_ = type_match.group(1).replace('.', '')
                name = name_match.group(2).strip()
                day_start = days_match.group(1)
                day_end = days_match.group(2)
                dose_morning = dose_match.group(1) if dose_match else "?"
                dose_noon = dose_match.group(2) if dose_match else "?"
                dose_evening = dose_match.group(3) if dose_match else "?"
                dose_night = dose_match.group(4) if dose_match else "?"
                timing = {}
                if dose_morning != "0" and dose_morning != "?": timing["Morning"] = int(dose_morning)
                if dose_noon != "0" and dose_noon != "?": timing["Noon"] = int(dose_noon)
                if dose_evening != "0" and dose_evening != "?": timing["Evening"] = int(dose_evening)
                if dose_night != "0" and dose_night != "?": timing["Night"] = int(dose_night)
                supplements.append({
                    "Name": name,
                    "Type": type_,
                    "Days": f"Day {day_start} - Day {day_end}",
                    "Timing": timing if timing else "Dose missing or unclear"
                })
    return supplements

if prescription_text:
    supplements = parse_prescription(prescription_text)
    if supplements:
        st.subheader("Extracted Supplement Schedule")
        for supp in supplements:
            st.markdown(f"**{supp['Name']} ({supp['Type']}) — {supp['Days']}**")
            if isinstance(supp['Timing'], dict):
                for time, dose in supp['Timing'].items():
                    st.write(f"{time}: {dose}")
            else:
                st.write(supp['Timing'])
            st.markdown("---")
    else:
        st.warning("No valid supplements found. Double-check the pasted text formatting.")

st.markdown(
    """
    <hr>
    <sub>
    ⚡️ This MVP takes prescription text only (no images, due to free hosting limits).  
    Use [onlineocr.net](https://www.onlineocr.net/) to convert your prescription image to text, then paste it above.<br>
    Ignores sprays. Handles imperfect OCR and most real-world formatting issues.
    </sub>
    """,
    unsafe_allow_html=True
)

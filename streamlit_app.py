import streamlit as st
import requests
import geocoder
import webbrowser
from PIL import Image
import io

st.set_page_config(page_title="MediScanX", layout="centered")

st.title("🩺 MediScanX - Pneumonia Detection")
st.write("Upload a chest X-ray image to check for Pneumonia.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded X-ray", use_column_width=True)

    # Convert image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    with st.spinner("Predicting..."):
        try:
            response = requests.post("http://127.0.0.1:5000/predict", files={"file": img_bytes})
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("prediction")
                confidence = result.get("confidence")

                st.success(f"🩺 Prediction: **{prediction}** with {confidence} confidence")

                # Precautions
                if prediction == "Pneumonia":
                    st.warning("### ⚠️ Precautions")
                    st.markdown("""
                    - Avoid cold/dusty areas  
                    - Stay vaccinated  
                    - Drink warm fluids  
                    - Wear a mask  
                    - Seek help immediately if breathing becomes difficult
                    """)

                # Heatmap (if included)
                if "heatmap" in result:
                    heatmap_data = requests.get(f"http://127.0.0.1:5000/heatmap").content
                    heatmap_image = Image.open(io.BytesIO(heatmap_data))
                    st.image(heatmap_image, caption="Grad-CAM Heatmap", use_column_width=True)

            else:
                st.error(f"❌ Request Failed: {response.json().get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Location
    st.markdown("---")
    st.subheader("📍 Your Location & Nearby Hospitals")
    try:
        g = geocoder.ip("me")
        if g.ok:  
            lat, lng = g.latlng
            st.success(f"Detected Location: **{g.city}, {g.country}**")

            map_url = f"https://www.google.com/maps/search/medical+hospital/@{lat},{lng},14z"
            if st.button("🧭 Show Nearby Hospitals on Google Maps"):
                webbrowser.open_new_tab(map_url)
        else:
            st.error("Couldn't detect location automatically.")
    except Exception as e:
        st.error(f"Location error: {e}")

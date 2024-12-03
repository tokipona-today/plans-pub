import streamlit as st
import random
from pathlib import Path
import cv2

st.set_page_config(layout="wide")

script_dir = Path(__file__).parent
images_dir = script_dir / "img"

def load_images():
    image_paths = sorted(list(images_dir.glob("plan_*.jpg")))
    images = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in image_paths]
    display_order = list(range(len(images)))
    random.shuffle(display_order)
    return images, display_order

def initialize_session():
    if 'display_order' not in st.session_state:
        st.session_state.images, st.session_state.display_order = load_images()
        num_images = len(st.session_state.images)
        st.session_state.current_order = [0] * num_images
        st.session_state.results = [False] * num_images

def check_order():
    results = []
    errors = 0
    for i, display_idx in enumerate(st.session_state.display_order):
        is_correct = st.session_state.current_order[i] == display_idx
        if not is_correct:
            errors += 1
        results.append(is_correct)
    return errors, results

def main():
    st.title("Retrouvez l'ordre des plans")
    
    if 'images' not in st.session_state:
        initialize_session()
    
    with st.form(key='order_form'):
        cols = st.columns(4)
        current_results = None
        
        if st.session_state.get('check_pressed', False):
            errors, current_results = check_order()
            st.write(f"Nombre d'erreurs : {errors}")
        
        for i, img_idx in enumerate(st.session_state.display_order):
            with cols[i % 4]:
                frame_color = "transparent"
                if current_results is not None:
                    frame_color = "#acc18a" if current_results[i] else "#ff5666"
                
                st.markdown(f"""
                    <style>
                        .frame_{i} {{ padding: 5px; background-color: {frame_color}; }}
                    </style>
                    <div class="frame_{i}">
                    """, unsafe_allow_html=True)
                
                st.image(st.session_state.images[img_idx])
                st.markdown("</div>", unsafe_allow_html=True)
                
                selected_pos = st.slider(f"Position", 0, len(st.session_state.images)-1, 
                                       value=st.session_state.current_order[i],
                                       key=f"slider_{i}")
                st.session_state.current_order[i] = selected_pos

        if st.form_submit_button("Vérifier l'ordre"):
            st.session_state.check_pressed = True
            st.rerun()

if __name__ == "__main__":
    main()
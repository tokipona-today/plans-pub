import streamlit as st
import random
from pathlib import Path
import cv2
import time

st.set_page_config(layout="wide")

script_dir = Path(__file__).parent
images_dir = script_dir / "img"


def get_available_movies():
    """Return a dictionary of movie folders with their first image path"""
    movies = {}
    for movie_dir in images_dir.iterdir():
        if movie_dir.is_dir():
            # Get the first image in the directory
            first_image = next(movie_dir.glob("plan_*.jpg"), None)
            if first_image:
                movies[movie_dir.name] = first_image
    return movies


def load_images(movie_folder):
    """Load images from the selected movie folder"""
    image_paths = sorted(list((images_dir / movie_folder).glob("plan_*.jpg")))
    images = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in image_paths]
    display_order = list(range(len(images)))
    random.shuffle(display_order)
    return images, display_order


def initialize_session(movie_folder=None):
    """Initialize or reset session state"""
    if movie_folder:
        st.session_state.selected_movie = movie_folder
        st.session_state.images, st.session_state.display_order = load_images(movie_folder)
        num_images = len(st.session_state.images)
        st.session_state.current_order = [0] * num_images
        st.session_state.results = None
        st.session_state.attempts = 0
        st.session_state.start_time = time.time()
        st.session_state.best_score = 0
        st.session_state.total_correct = 0
    elif 'selected_movie' not in st.session_state:
        st.session_state.selected_movie = None


def check_order():
    results = []
    correct_count = 0
    for i, display_idx in enumerate(st.session_state.display_order):
        is_correct = st.session_state.current_order[i] == display_idx
        if is_correct:
            correct_count += 1
        results.append(is_correct)
    return correct_count, results


def display_statistics():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Nombre de tentatives", st.session_state.attempts)

    with col2:
        elapsed_time = int(time.time() - st.session_state.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        st.metric("Temps écoulé", f"{minutes:02d}:{seconds:02d}")

    with col3:
        avg_correct = st.session_state.total_correct / max(1, st.session_state.attempts)
        st.metric("Moyenne d'images correctes", f"{avg_correct:.1f}")

    with col4:
        st.metric("Meilleur score", f"{st.session_state.best_score}/{len(st.session_state.images)}")

    if st.session_state.results is not None:
        correct_count = sum(st.session_state.results)
        total_count = len(st.session_state.results)
        progress = correct_count / total_count
        st.progress(progress)
        st.write(f"Progression : {correct_count}/{total_count} images correctement placées")


def display_movie_selection():
    """Display the movie selection page"""
    st.title("Choisissez un film")
    
    movies = get_available_movies()
    cols = st.columns(4)
    
    for i, (movie_name, first_image) in enumerate(movies.items()):
        with cols[i % 4]:
            st.image(cv2.cvtColor(cv2.imread(str(first_image)), cv2.COLOR_BGR2RGB))
            if st.button(movie_name, key=f"movie_{movie_name}"):
                initialize_session(movie_name)
                st.rerun()


def game_interface():
    """Display the game interface"""
    st.title(f"Retrouvez l'ordre des plans - {st.session_state.selected_movie}")

    if st.button("Changer de film", key="change_movie"):
        st.session_state.selected_movie = None
        st.rerun()

    with st.form(key='order_form'):
        cols = st.columns(4)

        for i, img_idx in enumerate(st.session_state.display_order):
            with cols[i % 4]:
                frame_color = "transparent"
                if st.session_state.results is not None:
                    frame_color = "#acc18a" if st.session_state.results[i] else "#ff5666"

                st.markdown(f"""
                    <style>
                        .frame_{i} {{ padding: 5px; background-color: {frame_color}; }}
                    </style>
                    <div class="frame_{i}">
                    """, unsafe_allow_html=True)

                st.image(st.session_state.images[img_idx])
                st.markdown("</div>", unsafe_allow_html=True)

                selected_pos = st.slider(
                    f"Position", 
                    1, 
                    len(st.session_state.images),
                    value=st.session_state.current_order[i] + 1,
                    key=f"slider_{i}"
                )
                st.session_state.current_order[i] = selected_pos - 1

        submit = st.form_submit_button("Vérifier l'ordre")
        if submit:
            st.session_state.attempts += 1
            correct_count, results = check_order()
            st.session_state.results = results
            st.session_state.total_correct += correct_count
            st.session_state.best_score = max(st.session_state.best_score, correct_count)
            st.write(f"Images correctement placées : {correct_count}/{len(st.session_state.images)}")
            st.rerun()

    display_statistics()


def main():
    initialize_session()
    
    if st.session_state.selected_movie is None:
        display_movie_selection()
    else:
        game_interface()


if __name__ == "__main__":
    main()

# 💪 AI Fitness Planner

An interactive Streamlit app that generates personalized 7-day fitness and meal plans, estimates calories, and suggests local foods based on your location.

## Features

- **Profile-based Plan:** Enter your details and get a custom fitness & meal plan for 7 days.
- **Calorie Estimates:** See BMR, TDEE, and daily calorie targets.
- **Location-based Suggestions:** Get budget-friendly local produce with estimated calories.
- **Meal Image Upload:** Upload a meal photo for a mock AI calorie estimate.

## Quick Start

1. **Clone the repo:**
    ```sh
    git clone https://github.com/yourusername/fitness_planner.git
    cd fitness_planner
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the app:**
    ```sh
    streamlit run app.py
    ```

## Dependencies

- [Streamlit](https://streamlit.io/)
- [geopy](https://geopy.readthedocs.io/)
- [Pillow](https://python-pillow.org/)
- [requests](https://docs.python-requests.org/)

## API

Uses [Nutritionix](https://www.nutritionix.com/business/api) for food calorie data.

## License

MIT

---

*Made with ❤️ for learning and testing. Not for medical use.*

import streamlit as st
import random
from geopy.geocoders import Nominatim
from PIL import Image

st.set_page_config(page_title="AI Fitness Planner", page_icon="💪", layout="wide")

st.title("💪 AI-Powered Fitness Planner")
st.write("Accurate-enough estimates for learning and testing. Fill your profile and click Generate Plan.")

# --- Initialize session state ---
if "plan" not in st.session_state:
    st.session_state.plan = None
if "food_pref" not in st.session_state:
    st.session_state.food_pref = []

# --- Profile Form ---
with st.form("profile_form"):
    name = st.text_input("Name", value=st.session_state.get("name", ""))
    age = st.number_input("Age", min_value=10, max_value=100, value=int(st.session_state.get("age", 25)))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if st.session_state.get("gender","Male")=="Male" else 1)
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(st.session_state.get("weight", 70.0)))
    height = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=float(st.session_state.get("height", 170.0)))
    activity = st.selectbox("Activity level", ["Sedentary", "Lightly active", "Moderately active", "Very active"], index=2)
    goal = st.selectbox("Goal", ["Lose Weight", "Maintain", "Gain Muscle"], index=0)
    food_pref = st.multiselect("Food preferences", ["Vegetarian", "Vegan", "Non-Vegetarian", "Gluten-Free", "Dairy-Free"], default=st.session_state.get("food_pref", []))
    budget = st.selectbox("Budget", ["Low", "Medium", "High"], index=1)
    submit = st.form_submit_button("Generate Plan")

if submit:
    # Save profile to session
    st.session_state.update({
        "name": name,
        "age": age,
        "gender": gender,
        "weight": weight,
        "height": height,
        "activity": activity,
        "goal": goal,
        "food_pref": food_pref,
        "budget": budget
    })

    # --- BMR/TDEE calculation ---
    def calc_bmr(g, w, h, a):
        if g == "Male":
            return 10 * w + 6.25 * h - 5 * a + 5
        if g == "Female":
            return 10 * w + 6.25 * h - 5 * a - 161
        return 10 * w + 6.25 * h - 5 * a - 78

    def act_mult(level):
        return {"Sedentary": 1.2, "Lightly active": 1.375, "Moderately active": 1.55, "Very active": 1.725}[level]

    bmr = calc_bmr(gender, weight, height, age)
    tdee = bmr * act_mult(activity)
    if goal == "Lose Weight":
        target = max(1200, round(tdee - 500))
    elif goal == "Gain Muscle":
        target = round(tdee + 300)
    else:
        target = round(tdee)

    # --- Meal pool ---
    meals_pool = [
        ("Oats with banana", 350),
        ("Eggs & toast", 350),
        ("Smoothie bowl", 300),
        ("Grilled chicken salad", 450),
        ("Rice + dal + veg", 650),
        ("Chapati + sabzi + salad", 600),
        ("Paneer curry + rice", 700),
        ("Veg pulao", 600),
        ("Protein shake", 250),
        ("Fruit & nuts", 200),
        ("Grilled fish + veggies", 550),
        ("Mixed veg curry + roti", 520)
    ]

    # --- Meal selection with preference handling ---
    def pick_meals(preferences):
        filtered = []
        for m in meals_pool:
            name_lower = m[0].lower()
            include = True
            if "Vegetarian" in preferences and any(x in name_lower for x in ["chicken", "fish"]):
                include = False
            if "Vegan" in preferences and any(x in name_lower for x in ["chicken","fish","egg","milk","paneer"]):
                include = False
            if include:
                filtered.append(m)
        if not filtered:
            filtered = meals_pool  # fallback
        breakfast = random.choice([m for m in filtered if m[1] <= 400])
        lunch = random.choice([m for m in filtered if 400 <= m[1] <= 700])
        dinner = random.choice([m for m in filtered if m[1] >= 300])
        snack = random.choice([m for m in filtered if m[1] <= 350])
        return breakfast, lunch, dinner, snack

    workouts_by_goal = {
        "Lose Weight": ["30 min brisk walk", "30 min HIIT", "30 min cycling", "30 min yoga/stretch"],
        "Maintain": ["30 min jog", "30 min bodyweight routine", "30 min swim", "30 min mixed cardio"],
        "Gain Muscle": ["45 min strength training", "Legs + core 45 min", "Push day 45 min", "Pull day 45 min"]
    }

    plan_list = []
    for i in range(7):
        b, l, d, s = pick_meals(food_pref)
        workout = random.choice(workouts_by_goal[goal])
        day = {
            "day": f"Day {i+1}",
            "meals": {
                "breakfast": {"item": b[0], "cal": b[1]},
                "lunch": {"item": l[0], "cal": l[1]},
                "dinner": {"item": d[0], "cal": d[1]},
                "snack": {"item": s[0], "cal": s[1]}
            },
            "workout": workout
        }
        plan_list.append(day)

    st.session_state.plan = {
        "profile": st.session_state,
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_cals": target,
        "7day": plan_list
    }

# --- Display Plan ---
if st.session_state.plan:
    plan = st.session_state.plan
    st.success(f"Plan for {plan['profile']['name']}")
    st.write(f"BMR: {plan['bmr']} kcal · TDEE: {plan['tdee']} kcal · Target: {plan['target_cals']} kcal/day")
    st.write("")
    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("Regenerate Plan"):
            st.session_state.plan = None
            st.experimental_rerun()
    for day in plan["7day"]:
        with st.expander(day["day"], expanded=False):
            meals = day["meals"]
            st.write(f"Breakfast: {meals['breakfast']['item']} — {meals['breakfast']['cal']} kcal")
            st.write(f"Lunch: {meals['lunch']['item']} — {meals['lunch']['cal']} kcal")
            st.write(f"Dinner: {meals['dinner']['item']} — {meals['dinner']['cal']} kcal")
            st.write(f"Snack: {meals['snack']['item']} — {meals['snack']['cal']} kcal")
            st.write(f"🏋️ Workout: {day['workout']}")
            total_day = meals['breakfast']['cal'] + meals['lunch']['cal'] + meals['dinner']['cal'] + meals['snack']['cal']
            st.write(f"Estimated daily food calories (sum of items): {total_day} kcal")

# --- Location-based food suggestions ---
st.write("")
st.subheader("🍎 Location-based food suggestions")
loc = st.text_input("Enter your city or location", value=st.session_state.get("location",""))
if loc:
    st.session_state["location"] = loc
    try:
        geolocator = Nominatim(user_agent="fitness_planner")
        found = geolocator.geocode(loc)
        if found:
            st.write(f"📍 {found.address.split(',')[0]}")
            local_foods = {
                "Mumbai": ["Banana","Papaya","Spinach","Tomato","Bottle Gourd"],
                "Delhi": ["Apple","Carrot","Cauliflower","Guava","Pumpkin"],
                "Chennai": ["Mango","Coconut","Drumstick","Okra","Tamarind"],
                "Bangalore": ["Orange","Beans","Spinach","Capsicum","Cucumber"]
            }
            city = loc.strip().title()
            foods = local_foods.get(city, ["Banana", "Spinach", "Tomato", "Onion", "Cabbage"])
            st.write("Budget-friendly local produce:")
            for it in foods:
                st.write(f"• {it}")
        else:
            st.error("Location not found. Check spelling.")
    except Exception as e:
        st.error("Error while looking up location.")

# --- Photo upload & mock calorie estimator ---
st.write("")
st.subheader("📸 Upload a food photo for calorie estimate")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="food_image")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    calories_estimated = random.randint(100, 800)
    st.success(f"Estimated Calories for this food: {calories_estimated} kcal")

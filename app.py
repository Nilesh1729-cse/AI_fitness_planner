import streamlit as st
import random
from geopy.geocoders import Nominatim
from PIL import Image
import requests

st.set_page_config(page_title="AI Fitness Planner", page_icon="💪", layout="wide")
st.title("💪 AI-Powered Fitness Planner")
st.write("Accurate-enough estimates for learning and testing. Fill your profile and click Generate Plan.")

# --- Nutritionix credentials ---
NUTRITIONIX_APP_ID = "5d192848"
NUTRITIONIX_API_KEY = "7b8b548e8e9e8e23f91a445acf66529b"

def get_food_calories(food_name):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"query": food_name, "timezone": "UTC"}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "foods" in data and len(data["foods"]) > 0:
            food = data["foods"][0]
            name = food.get("food_name", food_name)
            calories = food.get("nf_calories")
            if calories is None:
                return name, None
            return name, int(round(float(calories)))
        else:
            return food_name, None
    except Exception:
        return food_name, None

# --- Session State Initialization ---
if "plan" not in st.session_state:
    st.session_state.plan = None
if "food_pref" not in st.session_state:
    st.session_state.food_pref = []
if "location" not in st.session_state:
    st.session_state.location = ""

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

    # BMR/TDEE helpers
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

    # Meal pool
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

    def pick_meals(preferences):
        filtered = []
        for m in meals_pool:
            nm = m[0].lower()
            ok = True
            if "Vegetarian" in preferences and any(x in nm for x in ["chicken", "fish"]):
                ok = False
            if "Vegan" in preferences and any(x in nm for x in ["chicken", "fish", "egg", "milk", "paneer"]):
                ok = False
            if ok:
                filtered.append(m)
        if not filtered:
            filtered = meals_pool

        breakfasts = [m for m in filtered if m[1] <= 400] or [m for m in meals_pool if m[1] <= 400]
        lunches = [m for m in filtered if 400 <= m[1] <= 700] or [m for m in meals_pool if 400 <= m[1] <= 700]
        dinners = [m for m in filtered if m[1] >= 300] or [m for m in meals_pool if m[1] >= 300]
        snacks = [m for m in filtered if m[1] <= 350] or [m for m in meals_pool if m[1] <= 350]

        breakfast = random.choice(breakfasts)
        lunch = random.choice(lunches)
        dinner = random.choice(dinners)
        snack = random.choice(snacks)
        return breakfast, lunch, dinner, snack

    workouts_by_goal = {
        "Lose Weight": ["30 min brisk walk", "30 min HIIT", "30 min cycling", "30 min yoga/stretch"],
        "Maintain": ["30 min jog", "30 min bodyweight routine", "30 min swim", "30 min mixed cardio"],
        "Gain Muscle": ["45 min strength training", "Legs + core 45 min", "Push day 45 min", "Pull day 45 min"]
    }

    # Build plan
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
        "profile": {
            "name": name, "age": age, "gender": gender, "weight": weight, "height": height,
            "activity": activity, "goal": goal, "food_pref": food_pref, "budget": budget
        },
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

# --- Location-based suggestions ---
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
                "mumbai": ["Banana","Papaya","Spinach","Tomato","Bottle Gourd"],
                "delhi": ["Apple","Carrot","Cauliflower","Guava","Pumpkin"],
                "chennai": ["Mango","Coconut","Drumstick","Okra","Tamarind"],
                "bangalore": ["Orange","Beans","Spinach","Capsicum","Cucumber"]
            }
            city = loc.strip().lower()
            items = local_foods.get(city, ["Banana","Spinach","Tomato","Onion","Cabbage"])
            st.write("Budget-friendly local produce with estimated calories:")
            for it in items:
                name, cal = get_food_calories(it)
                st.write(f"• {name.title()} — {cal if cal else 'Est. N/A'} kcal per serving")
        else:
            st.error("Location not found. Check spelling.")
    except Exception as e:
        st.error("Error while looking up location.")

# --- Meal Image Upload & Mock Calorie Estimator ---
st.subheader("📸 Upload your meal for calorie estimate")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Meal", use_column_width=True)

    st.write("Estimating calories...")
    est_cal = random.randint(200, 800)  # mock AI estimation
    st.success(f"Estimated calories for this meal: {est_cal} kcal")

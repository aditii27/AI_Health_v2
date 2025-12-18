import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import importlib.util
import base64
from PIL import Image
from datetime import datetime

# Load and apply custom CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to add background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Check if team_info module exists and import it
try:
    import team_info
    has_team_info = True
except ImportError:
    has_team_info = False

# Load environment variables
load_dotenv()

# Initialize the model (will be done lazily)
model = None

# Function to calculate daily calorie requirements
def calculate_calorie_requirements(age, gender, weight, height, fitness_goal):
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    if fitness_goal == "Weight Loss":
        return bmr * 1.2
    elif fitness_goal == "Weight Gain":
        return bmr * 1.5
    else:
        return bmr * 1.375

# Function to generate the plan
def generate_plan_with_prompt(metrics, prompt_template):
    global model
    if model is None:
        try:
            model = ChatGroq(model="llama3-8b-8192")
        except Exception as e:
            raise Exception(f"Failed to initialize AI model. Please check your GROQ_API_KEY in the .env file. Error: {e}")
    prompt = prompt_template.format(**metrics)
    response = model.invoke(prompt)
    return response

# Function to format the response neatly
def format_plan(response):
    try:
        content = response.content
        sections = content.split("\n\n")
        formatted = ""
        for section in sections:
            formatted += f"**{section.strip()}**\n\n"
        return formatted
    except Exception as e:
        return f"Error formatting plan: {e}"

# Ayurvedic prompt template
ayurveda_prompt_template = """
You are a health expert specialized in both modern medicine and Ayurveda. Generate a personalized weekly diet and exercise plan for {name}, a {age}-year-old {gender} with a BMI of {bmi} ({health_status}).

Fitness Goal: {fitness_goal}.
Daily Calorie Requirement: {daily_calories} kcal.
Dietary Preference: {dietary_preference}.
Food Allergies: {food_allergies}.
Local Cuisine: {local_cuisine}.
Month: {month}.
Ayurvedic Consideration: True

Plan should include:
1. A daily diet plan with meal timings, calorie details, and meal alternatives.
2. Exercise routines based on goals, incorporating cardio, strength, and flexibility.
3. Dynamic plan adjustments based on month and local cuisine preferences.
4. Wearable integration for tracking steps, heart rate, and calorie burn.
5. Progress monitoring for daily calorie burn and weight tracking.
6. **Food Delivery Integration**:
   - Meal suggestions based on diet plans.
   - Integration with food delivery platforms (Uber Eats, DoorDash).
   - Searching menu items that fit calorie and dietary preferences.
   - Multi-restaurant meal aggregation for complete diet fulfillment.
   - Location-based meal recommendations.
   - Customizable meal delivery schedules.
7. **Ayurvedic Elements**:
   - Dosha assessment based on provided metrics.
   - Ayurvedic dietary recommendations aligned with your dosha type.
   - Seasonal herbs and spices for balance.
   - Daily routines (Dinacharya) for optimal health.
   - Natural remedies complementing modern medicine.

Provide a detailed plan for each weekday: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.

Return output as:
Day: {{weekday}}
  - Breakfast: Time, Description, Calories, Ayurvedic Properties
  - Lunch: Time, Description, Calories, Ayurvedic Properties
  - Snacks: Time, Description, Calories, Ayurvedic Properties
  - Dinner: Time, Description, Calories, Ayurvedic Properties
  - Exercise: Description, Duration, Dosha Benefits
  - Wearable Tracking: Steps, Heart Rate, Calories Burned
  - Progress Monitoring: Daily calorie intake vs. burn.
  - Food Delivery: Suggested meal items and delivery options.
  - Ayurvedic Tips: Daily wellness practices based on dosha.
"""

# Regular prompt template
regular_prompt_template = """
You are a health expert. Generate a personalized weekly diet and exercise plan for {name}, a {age}-year-old {gender} with a BMI of {bmi} ({health_status}).

Fitness Goal: {fitness_goal}.
Daily Calorie Requirement: {daily_calories} kcal.
Dietary Preference: {dietary_preference}.
Food Allergies: {food_allergies}.
Local Cuisine: {local_cuisine}.
Month: {month}.

Plan should include:
1. A daily diet plan with meal timings, calorie details, and meal alternatives.
2. Exercise routines based on goals, incorporating cardio, strength, and flexibility.
3. Dynamic plan adjustments based on month and local cuisine preferences.
4. Wearable integration for tracking steps, heart rate, and calorie burn.
5. Progress monitoring for daily calorie burn and weight tracking.
6. **Food Delivery Integration**:
   - Meal suggestions based on diet plans.
   - Integration with food delivery platforms (Uber Eats, DoorDash).
   - Searching menu items that fit calorie and dietary preferences.
   - Multi-restaurant meal aggregation for complete diet fulfillment.
   - Location-based meal recommendations.
   - Customizable meal delivery schedules.

Provide a detailed plan for each weekday: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.

Return output as:
Day: {{weekday}}
  - Breakfast: Time, Description, Calories
  - Lunch: Time, Description, Calories
  - Snacks: Time, Description, Calories
  - Dinner: Time, Description, Calories
  - Exercise: Description, Duration
  - Wearable Tracking: Steps, Heart Rate, Calories Burned
  - Progress Monitoring: Daily calorie intake vs. burn.
  - Food Delivery: Suggested meal items and delivery options.
"""

# Streamlit app
st.set_page_config(page_title="AI Health & Wellness Planner", layout="wide")
load_css()

# Add the meditation background image
add_bg_from_local('images/image-3.jpg')

# Create two columns for the header
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🌿 AI-Based Holistic Health & Wellness Planner")
    st.markdown("""
    <div class='main-content'>
        Integrate modern science with ancient Ayurvedic wisdom for your personalized wellness journey.
    </div>
    """, unsafe_allow_html=True)


with col2:
    # Display the spices image
    st.image('images/Image-1.jpg', caption='Natural ingredients for holistic wellness', use_container_width=True)

# Add sidebar with team information
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.header("✨ About this Project")
    st.write("Integration of Ayurveda and modern medical science for comprehensive wellness insights")
    
    if has_team_info:
        st.subheader("👥 Team Members")
        st.markdown("- Aditi Soni [LinkedIn](https://www.linkedin.com/in/aditi-soni-259813285/)")
        st.markdown("- Bhumika Patel [LinkedIn](https://www.linkedin.com/in/bhumika-patel-ml/)")
        st.markdown("- Aditi Lakhera [LinkedIn](https://www.linkedin.com/in/aditi-lakhera-b628802bb/)")
        st.markdown("- Anushri Tiwari [LinkedIn](https://www.linkedin.com/in/anushri-tiwari-916494300 )")
        
        st.subheader("🔗 Project Links")
        st.markdown("[GitHub Repository](https://github.com/Abs6187/AI_Health_v2)")
        st.markdown("[Presentation](https://github.com/Abs6187/AI_Health_v2/blob/main/HackGirl_PPT_HackSRIT.pptx)")
        st.markdown("[Hackathon](https://unstop.com/hackathons/hacksrit-shri-ram-group-of-institutions-jabalpur-1471613)")
    st.markdown("</div>", unsafe_allow_html=True)

# Main content
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

# Create three columns for input fields
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📝 Personal Details")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, value=25)
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"])

with col2:
    st.subheader("📊 Physical Metrics")
    weight = st.number_input("Weight (kg)", min_value=1, value=70)
    height = st.number_input("Height (cm)", min_value=1, value=170)
    fitness_goal = st.selectbox("Fitness Goal", options=["Weight Loss", "Weight Gain", "Maintenance"])

with col3:
    st.subheader("🍽️ Dietary Preferences")
    dietary_preference = st.selectbox("Dietary Preference", options=["Vegetarian", "Vegan", "Keto", "Halal", "None"])
    food_allergies = st.text_input("Food Allergies (if any)")
    local_cuisine = st.text_input("Preferred Local Cuisine (e.g., Indian, Italian, Chinese)")

# Additional preferences
st.subheader("🌿 Wellness Preferences")
col1, col2 = st.columns(2)

with col1:
    month = st.selectbox("Select Month", options=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    include_ayurveda = st.checkbox("Include Ayurvedic wellness insights", value=True)

# Calculate and display metrics
bmi = round(weight / (height / 100) ** 2, 2)
health_status = "Underweight" if bmi < 18.5 else "Normal weight" if bmi <= 24.9 else "Overweight"
daily_calories = calculate_calorie_requirements(age, gender, weight, height, fitness_goal)

# Display metrics in a nice format
st.markdown("""
<div class='metric-container'>
    <h3>Your Health Metrics</h3>
    <p>BMI: {:.1f} ({:s})</p>
    <p>Daily Calorie Target: {:,d} kcal</p>
</div>
""".format(bmi, health_status, int(daily_calories)), unsafe_allow_html=True)

# User metrics
metrics = {
    "name": name,
    "age": age,
    "gender": gender,
    "bmi": bmi,
    "health_status": health_status,
    "fitness_goal": fitness_goal,
    "dietary_preference": dietary_preference,
    "food_allergies": food_allergies,
    "daily_calories": int(daily_calories),
    "local_cuisine": local_cuisine,
    "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "month": month,
}

# Generate and display plan
if st.button("Generate Personalized Plan"):
    with st.spinner("🌟 Creating your personalized wellness journey..."):
        try:
            # Choose the appropriate prompt based on the Ayurveda option
            selected_prompt = ayurveda_prompt_template if include_ayurveda else regular_prompt_template
            plan = generate_plan_with_prompt(metrics, selected_prompt)
            formatted_plan = format_plan(plan)
            
            plan_title = "🌺 Integrated Ayurvedic & Modern Wellness Plan" if include_ayurveda else "💪 Personalized Health Plan"
            st.header(f"{plan_title} for {month}")
            st.markdown(formatted_plan)
            
            # Create download button for the plan
            current_date = datetime.now().strftime("%Y%m%d")
            filename = f"wellness_plan_{name.replace(' ', '_')}_{current_date}.txt"
            
            # Prepare the content for the text file
            plan_content = f"""
{plan_title} for {month}
Generated for: {name}
Date: {datetime.now().strftime('%Y-%m-%d')}

Personal Details:
---------------
Age: {age}
Gender: {gender}
Weight: {weight} kg
Height: {height} cm
BMI: {bmi:.1f} ({health_status})
Daily Calorie Target: {int(daily_calories)} kcal

Preferences:
-----------
Fitness Goal: {fitness_goal}
Dietary Preference: {dietary_preference}
Food Allergies: {food_allergies if food_allergies else 'None'}
Local Cuisine: {local_cuisine}

{formatted_plan}

Generated by AI Health & Wellness Planner
"""
            # Create a download button
            st.download_button(
                label="📥 Download Plan as Text File",
                data=plan_content,
                file_name=filename,
                mime="text/plain",
                help="Click to download your personalized wellness plan",
                key="download_plan"
            )
            
            # Add a divider
            st.markdown("---")
            
            # Add some helpful tips
            st.markdown("""
            ### 📋 Tips for Using Your Plan:
            1. Save your plan for offline reference
            2. Print it out and keep it visible
            3. Track your progress daily
            4. Adjust the plan as needed based on your progress
            """)
            
        except Exception as e:
            st.error(f"Error generating the plan: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
    Made with ❤️ for better health and wellness
</div>
""", unsafe_allow_html=True)


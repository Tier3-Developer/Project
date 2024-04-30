import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import base64
import openai


st.set_page_config(
        page_title="AI & Sleep",
        page_icon="👩‍⚕️",  # You can use an emoji or specify the URL for an image
       # layout="wide",
    )




hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

def initialize_gpt_session():
    """Initializes or resets the GPT model in the session state."""
    st.session_state["openai_model"] = "gpt-3.5-turbo"
    st.session_state.messages = []

def load_gpt3_model(previous_page):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Go Back"):
            st.session_state.current_page = previous_page
    st.title(f":rainbow[This is an AI Bot]🤖")
    
    
    openai.api_key =st.secrets["OPENAI_API_KEY"]
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
		

def add_bg_image(image_base64):
    # Custom CSS to hide Streamlit's default menus and footer and style the button
    hide_st_style = f"""
                <style>
                /* Hide Streamlit's default menu, footer and header */
                #MainMenu {{visibility: hidden;}}
                footer {{visibility: hidden;}}
                header {{visibility: hidden;}}
                /* Fullscreen background image setup */
                .stApp {{
                    background-image: url("data:image/gif;base64,{image_base64}");
                    background-size: cover;
                    background-position: center;
                    height: 100vh;
                }}
                /* Style buttons directly */
                .stButton > button {{
                    background-color: white; /* Button color */
                    color: black; /* Text color */
                    border-radius: 20px; /* Rounded corners */
                    padding: 6px 16px; /* Padding inside the button */
                    border: none; /* No border */
                    font-size: 10px; /* Font size */
                    box-shadow: 2px 5px 5px rgba(0,0,0,0.2); /* Shadow effect */
                    margin: 0px; /* Spacing around button */
                    width: auto; /* Match the button width to the column width */
                }}
                .stButton > button:hover {{
                    background-color: #C6EBC5; /* Light grey background on hover */
                    box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24); /* Shadow on hover */
                }}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    
def check_if_started():
    # If the button has been pressed, show the new page layout
    if 'started' not in st.session_state or not st.session_state['started']:
        # Display the 'Get Started' button
        _, col2, _ = st.columns([1,0.5,1])
        with col2:
            if st.button("Get Started"):
                st.session_state['started'] = True
                st.session_state.current_page = 'form'
                st.experimental_rerun()
    



def display_emoji(disorder):
    emojis = {
        'Healthy': '😊',
        'Sleep Apnea': '😷',
        'Insomnia': '😫'
    }
    return emojis.get(disorder, '❓')


# Function to get base64 encoded image
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
    
def load_model():
    with open('sleep_gb.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

def provide_feedback(user_inputs, predicted_disorder):
    feedback = {}

    # General feedback based on the disorder
    feedback['General Feed:'] = {
        "Healthy": "You are currently classified as healthy. It's important to continue monitoring and managing health factors to maintain this status.",
        "Sleep Apnea": "Management of sleep apnea is crucial to reduce health risks associated with the condition.",
        "Insomnia": "Improving sleep quality and managing stress are key to treating insomnia effectively."
    }[predicted_disorder]

    # Feedback for Healthy
    if predicted_disorder == "Healthy":
        if user_inputs['age'] > 50:
            feedback['age'] = "Being over 50 can increase your risk for several sleep disorders, including insomnia and sleep apnea."
        if user_inputs['sleep_duration'] < 6:
            feedback['sleep_duration'] = "Sleeping less than 6 hours regularly might increase your risk of developing sleep-related disorders."
        if user_inputs['quality_of_sleep'] < 3:
            feedback['quality_of_sleep'] = "Poor sleep quality can be an early sign of developing sleep conditions."
        if user_inputs['stress_level'] > 6:
            feedback['stress'] = "High stress levels are often a precursor to sleep problems; managing it is crucial."
        if user_inputs['physical_activity_level'] < 30:
            feedback['physical_activity'] = "Low physical activity is associated with poorer health outcomes, including poor sleep health."
        if user_inputs['heart_rate'] > 80:
            feedback['heart_rate'] = "An elevated heart rate can be an indicator of stress or other health issues that may affect sleep."
        if user_inputs['daily_steps'] < 5000:
            feedback['daily_steps'] = "A low step count can be linked to lower overall health, which could impact sleep health."
        if user_inputs['elevated_bmi'] == 1:
            feedback['elevated_bmi'] = "An elevated BMI could predispose you to sleep apnea or other sleep disturbances."
        if user_inputs['systolic_bp'] > 135 or user_inputs['diastolic_bp'] > 85:
            feedback['blood_pressure'] = "High blood pressure is associated with many health issues, including sleep apnea."

    # Feedback for Sleep Apnea
    elif predicted_disorder == "Sleep Apnea":
        if user_inputs['heart_rate'] > 80:
            feedback['heart_rate'] = "Your heart rate is higher than normal, which is commonly associated with sleep apnea."
        if user_inputs['daily_steps'] < 5000:
            feedback['daily_steps'] = "A low level of daily activity is associated with sleep apnea; increasing it may help alleviate symptoms."
        if user_inputs['elevated_bmi'] == 1:
            feedback['elevated_bmi'] = "An elevated BMI is strongly linked to sleep apnea."
        if user_inputs['systolic_bp'] > 135 or user_inputs['diastolic_bp'] > 85:
            feedback['blood_pressure'] = "High blood pressure is often found in those with sleep apnea."
        if user_inputs['quality_of_sleep'] < 3:
            feedback['quality_of_sleep'] = "Poor sleep quality is a significant indicator of sleep apnea."

    # Feedback for Insomnia
    elif predicted_disorder == "Insomnia":
        if user_inputs['sleep_duration'] < 6:
            feedback['sleep_duration'] = "Sleeping less than 6 hours is often linked to insomnia."
        if user_inputs['quality_of_sleep'] < 3:
            feedback['quality_of_sleep'] = "Poor sleep quality is a common symptom of insomnia."
        if user_inputs['stress_level'] > 6:
            feedback['stress'] = "High stress levels are often associated with insomnia; managing it is essential."
        if user_inputs['physical_activity_level'] < 31:
            feedback['physical_activity'] = "Low physical activity can contribute to insomnia; increasing activity might help."

    return feedback


def display_results(predicted_disorder, user_inputs):
    st.markdown("<h1 style='color: white;'>Results</h1>", unsafe_allow_html=True)
    color = '#008000' if predicted_disorder == 'Healthy' else '#FF0000'
    emoji = display_emoji(predicted_disorder)
    background_image_path = "images/bg.jpg"  # Keep the image path as it was
    background_image_base64 = get_base64_encoded_image(background_image_path)
    
    background_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{background_image_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .prediction-container {
            background-color: #f0f2f6;
            border-left: 5px solid #4caf50;
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .prediction-label {
            color: #4caf50;
            font-weight: bold;
            margin: 0;
        }
        .emoji-text {
            font-size: 2rem;
            line-height: 2rem;
        }
        .feedback-header {
            color: #003C43;
            margin-top: 20px;
        }
        .feedback-item {
            background-color: #FB6D48;  /* Blue background */
            color: black;              /* White text */
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)

    # Construct the HTML for predicted disorder
    prediction_html = f"<div class='prediction-container'><h1 class='prediction-label'>Prediction of Sleep Health:</h1> <h2 style='color: {color};'>{predicted_disorder} {emoji}</h2>"

    # Get feedback based on user inputs
    feedback = provide_feedback(user_inputs, predicted_disorder)
    if feedback:
        # Construct the HTML for feedback
        feedback_html = "<h1 class='feedback-header'>Feedback based on your input:</h1>"
        for key, value in feedback.items():
            feedback_html += f"<div class='feedback-item'><strong>{key.replace('_', ' ').title()}:</strong><br> {value}</div>"
        # Combine prediction and feedback HTML
        prediction_html += feedback_html

    # Close the prediction container
    prediction_html += "</div>"

    # Render the HTML
    st.markdown(prediction_html, unsafe_allow_html=True)
    
    # # Button to navigate to therapy
    # if st.button("Go to Therapy Suggestions"):
    #     st.session_state['page'] = 'therapy'
    #     st.experimental_rerun()

def display_therapy(user_inputs, predicted_disorder):
    st.title(":green[Personalized Therapy Advice Based on] :red[Risk Levels:]")
    background_image_path = "images/home.jpg"  # Keep the image path as it was
    background_image_base64 = get_base64_encoded_image(background_image_path)
    
    background_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{background_image_base64}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)

     
    # Define the risk levels and corresponding therapy advice for each feature
    risk_levels = {
        'age': {'low': (19,30 ), 'moderate': (31,40), 'high': (41, 100)},
        'sleep_duration': {'low': (7, 9), 'moderate': (5, 7), 'high': (0, 5)},
        'quality_of_sleep': {'low': (5, 10), 'moderate': (4, 5), 'high': (1, 3)},
        'physical_activity_level': {'low': (60,90), 'moderate': (41, 59), 'high': (20,40)},
        'stress_level': {'low': (1, 3), 'moderate': (4,6), 'high': (7, 10)},
        'heart_rate': {'low': (60, 70), 'moderate': (70, 80), 'high': (80, 110)},
        'daily_steps': {'low': (8000, 15000), 'moderate': (5000, 7999), 'high': (0, 4999)},
        'systolic_bp': {'low': (110, 120), 'moderate': (120, 135), 'high': (136, 180)},
        'diastolic_bp': {'low': (70, 80), 'moderate': (80, 89), 'high': (90, 100)},
    }

    therapy_advice = {
        'age': {
            'low': "Maintain a healthy lifestyle to continue your wellness as you age.",
            'moderate': "Regular check-ups become more important as you enter middle age.",
            'high': "Increased frequency of medical screenings is recommended. As per our analysis your age group may get effected to sleep disorders"
        },
        'sleep_duration': {
            'low': "Maintain your good sleep duration to continue feeling rested.",
            'moderate': "Aim to increase your sleep duration to the recommended 7-9 hours.",
            'high': "Critical sleep deprivation detected; seek medical advice."
        },
        'quality_of_sleep': {
            'low': "You're getting good sleep quality. Keep up the good habits!",
            'moderate': "Your sleep quality can improve; avoid screens before bed and establish a relaxing routine.",
            'high': "Low sleep quality can impact health; consider a sleep study."
        },
        'physical_activity_level': {
            'low': "Excellent level of physical activity. Continue this routine for good health.",
            'moderate': "Increasing your physical activity can help improve your health and sleep.",
            'high': "It's important to start incorporating physical activity into your daily routine."
        },
        'stress_level': {
            'low': "Your stress levels seem manageable. Continue your current stress management practices.",
            'moderate': "Consider exploring additional stress reduction techniques.",
            'high': "High stress levels can affect health. Consider professional support for stress management."
        },
        'heart_rate': {
            'low': "Your heart rate is in a healthy range. Continue monitoring it regularly.",
            'moderate': "Your heart rate suggests moderate risk. Consider lifestyle changes and regular monitoring.",
            'high': "Seek medical advice as a high heart rate can be a health risk."
        },
        'daily_steps': {
            'low': "You're very active, which is great for your health. Keep it up!",
            'moderate': "Try to increase your daily steps to achieve more health benefits.",
            'high': "Increasing your daily activity level is important for your overall health."
        },
        # 'elevated_bmi': {
        #     'low': "You have a healthy BMI. Continue to maintain a balanced diet and regular exercise.",
        #     'moderate': "Monitor your diet and exercise routine to manage your weight effectively.",
        #     'high': "Consider a structured approach to weight loss with professional guidance."
        # },
        'systolic_bp': {
            'low': "Your systolic blood pressure is in a good range. Regular monitoring is advised.",
            'moderate': "Monitor your blood pressure regularly and consider lifestyle changes to maintain it.",
            'high': "Consult with a healthcare provider to manage your systolic blood pressure."
        },
        'diastolic_bp': {
            'low': "Your diastolic blood pressure is healthy. Keep monitoring it as part of your routine health checks.",
            'moderate': "Stay mindful of your diastolic blood pressure and maintain a healthy lifestyle.",
            'high': "High diastolic blood pressure can be a risk factor for health issues. Seek medical advice."
        },
    }
    
    # Custom CSS to inject for better alignment and design
    st.markdown("""
        <style>
        .risk-item {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color:wite;
            
        }
        .low-risk { background-color: #41B06E;border: 5px solid #FFD1E3; }
        .moderate-risk { background-color: #FF9800;border: 5px solid #FFD1E3; }
        .high-risk { background-color: #E72929;border: 5px solid #FFD1E3; }
        .text-black { color: #074173; }
        </style>
        """, unsafe_allow_html=True)
    
    # Initialize containers to hold the features for each risk level
    risk_feature_lists = {
        'low': [],
        'moderate': [],
        'high': []
    }
    
    # Determine the risk level for each feature and append to lists
    for feature, levels in risk_levels.items():
        value = user_inputs.get(feature)
        if isinstance(levels['low'], tuple):  # If the value is a range
            low, high = levels['low']
            risk_level = ('low' if low <= value <= high else
                          'moderate' if levels['moderate'][0] <= value <= levels['moderate'][1] else
                          'high')
        else:  # If the value is binary for elevated BMI
            risk_level = ('low' if value == levels['low'] else
                          'moderate' if value == levels['moderate'] else
                          'high')

        # Get the appropriate advice from the therapy_advice dictionary
        advice = therapy_advice[feature][risk_level]
        risk_feature_lists[risk_level].append((feature, value, advice))

    # Sort risk levels by the number of features and display them
    # Display the high risk features first, then moderate, then low
    for level in ['high', 'moderate', 'low']:  # Explicit order
        features = risk_feature_lists[level]
        if features:
            st.markdown(f"### {level.capitalize()} Risk Features")
            # Organize the features into rows of up to 3 columns
            for i in range(0, len(features), 3):
                row_features = features[i:i + 3]
                cols = st.columns(3)
                for idx, (feature, value, advice) in enumerate(row_features):
                    with cols[idx % 3]:
                        st.markdown(
                            f"<div class='risk-item {level}-risk'>"
                            f"<strong class='text-black'>{feature.replace('_', ' ').title()}</strong> {value}<br>"
                            f"<strong class='text-black'>Suggestion :</strong> {advice}</div>", 
                            unsafe_allow_html=True
                        )
            # Add spacing after each risk level category
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <style>
        .suggestions-container {
            border: 5px solid #ff4b4b; /* Red border */
            background-color: #003C43; /* Red background */
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            color: white; /* White text */
        }
        </style>
        """, unsafe_allow_html=True)

    if predicted_disorder != 'Healthy':
        with st.container():
            suggestion_items = {
                "Sleep Apnea": [
                    "Consider undergoing a sleep study for potential CPAP therapy.",
                    "Avoid alcohol and sedatives which can exacerbate symptoms.",
                    "Maintain a healthy weight to reduce the risk of sleep apnea.",
                    "Sleep on your side instead of your back to improve breathing.",
                    "Use a humidifier in your bedroom to keep the air moist."
                ],
                "Insomnia": [
                    "Maintain a consistent sleep schedule even on weekends.",
                    "Practice relaxation techniques before bed, like reading or taking a bath.",
                    "Limit caffeine and alcohol intake, especially close to bedtime.",
                    "Create a comfortable sleep environment with a dark, quiet, and cool room.",
                    "Try cognitive behavioral therapy for insomnia (CBT-I) with a therapist."
                ]
            }

            suggestions_html = "<ul>" + "".join([f"<li>{suggestion}</li>" for suggestion in suggestion_items.get(predicted_disorder, [])]) + "</ul>"
            st.markdown(f"<div class='suggestions-container'><h2>Remedial Suggestions for {predicted_disorder}:</h2>{suggestions_html}</div>", unsafe_allow_html=True)

def main():
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'started'  # Set a default page, e.g., 'home'

    # Button to open the chat with the bot
    if st.session_state.current_page in ['form', 'results', 'therapy']:
        col1, col2 = st.columns([1, 0.3])
        with col1:
            if st.button("Home Page"):
                st.session_state.current_page = 'started'  # Set to start page
                st.session_state['started'] = False  # Reset the start flag
                st.experimental_rerun()
        with col2:
            if st.button("Ask our Bot", key='bot_button'):
                st.session_state.previous_page = st.session_state.current_page
                st.session_state.current_page = 'chatbot'
                initialize_gpt_session()

    # Include a conditional for when the chatbot page is supposed to be displayed
    if st.session_state.current_page == 'chatbot':
        load_gpt3_model(st.session_state.get('previous_page', 'started'))  # Pass the previous page to the chatbot function


    # Set up the initial state
    if 'started' not in st.session_state:
        st.session_state['started'] = False
        st.session_state.current_page = 'home'
    # If the 'Get Started' button hasn't been pressed, show the start page
    if not st.session_state['started']:
        # Add the background and central title for the start page
        file_path = "images/sleep2.gif"  # replace with your GIF file path
        image_base64 = get_base64_encoded_image(file_path)
        add_bg_image(image_base64)
        st.markdown("<h1 style='text-align: center; color: white;'>Diagnostic System for Sleep Disorder</h1>", unsafe_allow_html=True)        
    # if 'started' not in st.session_state or not st.session_state['started']:
    #     st.markdown("<h1 style='text-align: center; color: white;'>Diagnostic System for Sleep Disorder</h1>", unsafe_allow_html=True)
    
    # Check if the 'Get Started' button has been pressed and display the appropriate page
    check_if_started()
    

    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #FEFAF6;
        color: #141E46;
        font-weight: bold;
    }
    div.stButton > button:last-child {
        background-color: #FEFAF6;
        color:solid #141E46;
        font-weight: bold;
    }
    </style>""", unsafe_allow_html=True)
    submit_button = False
    if st.session_state['started']:
     if 'current_page' not in st.session_state:
        st.session_state.current_page = 'form'
    # model = load_model()
    if st.session_state.current_page == 'form':
     background_image_path = "images/form.jpg"
     background_image_base64 = get_base64_encoded_image(background_image_path)
     background_style = f"""
        <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{background_image_base64}");
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
            }}
        </style>
        """
     st.markdown(background_style, unsafe_allow_html=True)     
     
                
				
     st.title("Sleep Disorder Prediction System")
     
     with st.form(key='my_form'):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=19, max_value=120, step=1)
            sleep_duration = st.number_input("Sleep Duration (in hours)", value=8.0)
            quality_of_sleep = st.number_input("Quality of Sleep", value=5, min_value=1, max_value=10, step=1)
            physical_activity_level = st.number_input("Physical Activity Level (in min)", value=45, min_value=20, max_value=90, step=1)
            stress_level = st.number_input("Stress Level", value=5, min_value=1, max_value=10, step=1)
            heart_rate = st.number_input("Average Resting Heart Rate (bpm)", value=70, min_value=60, max_value=110, step=1)
            submit_button = st.form_submit_button("Predict")
        with col2:
            daily_steps = st.number_input("Average Daily Steps", value=3000, min_value=1000, max_value=15000)
            bmi_category = st.selectbox("BMI Category", ["Normal Weight", "Overweight", "Obese"])
            gender = st.selectbox("Gender", ["Male", "Female"])
            systolic_bp = st.number_input("Systolic Blood Pressure", value=120, min_value=110, max_value=150, step=1)
            diastolic_bp = st.number_input("Diastolic Blood Pressure", value=80, min_value=70, max_value=95, step=1)
            occupation = st.selectbox("Occupation", ["humanities", "medical", "technical"])
                     
    if submit_button:
        model = load_model()
        input_data = pd.DataFrame({
            'age': [age],
            'sleep_duration': [sleep_duration],
            'quality_of_sleep': [quality_of_sleep],
            'physical_activity_level': [physical_activity_level],
            'stress_level': [stress_level],
            'heart_rate': [heart_rate],
            'daily_steps': [daily_steps],
            'elevated_bmi': [1 if bmi_category in ["Obese", "Overweight"] else 0],
            'systolic_bp': [systolic_bp],
            'diastolic_bp': [diastolic_bp],
            'is_Male': [1 if gender == "Male" else 0],
            'wf_humanities': [1 if occupation == "humanities" else 0],
            'wf_medical': [1 if occupation == "medical" else 0],
            'wf_technical': [1 if occupation == "technical" else 0]
        })

        

        # st.session_state['submitted'] = True
        st.session_state['predicted_disorder'] = predicted_disorder
        st.session_state['user_inputs'] = {
            'age': age,
            'sleep_duration': sleep_duration,
            'quality_of_sleep': quality_of_sleep,
            'physical_activity_level': physical_activity_level,
            'stress_level': stress_level,
            'heart_rate': heart_rate,
            'daily_steps': daily_steps,
            'elevated_bmi': 1 if bmi_category in ["Obese", "Overweight"] else 0,
            'systolic_bp': systolic_bp,
            'diastolic_bp': diastolic_bp,
            'is_Male': 1 if gender == "Male" else 0,
            'occupation': occupation  # Storing occupation for use elsewhere if needed
        }

        st.session_state.current_page = 'results'

        
    elif st.session_state.current_page == 'results':
        
        display_results(st.session_state['predicted_disorder'], st.session_state['user_inputs'])
        col1, col2 = st.columns([1,0.5])
        with col1:
            if st.button("Back to Form"):
                st.session_state.current_page = 'form'
        with col2:
            if st.button("Go to Therapy Suggestions", key='therapy_button'):
                st.session_state.current_page = 'therapy'
                st.experimental_rerun()
    elif st.session_state.current_page == 'therapy':
     display_therapy(st.session_state['user_inputs'], st.session_state['predicted_disorder'])
     st.button("Back to Results", on_click=lambda: st.session_state.update(current_page='results'))
if __name__ == "__main__":
    main()

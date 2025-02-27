import streamlit as st
from dotenv import load_dotenv
import os
from google.generativeai import GenerativeModel, configure
import json

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Please set your GEMINI_API_KEY in the .env file.", icon="🚨")
    st.stop()

configure(api_key=api_key)

# Conversion function (unchanged)
def convert_units(value, from_unit, to_unit, category):
    conversions = {
        "Length": {
            "meters": 1.0,
            "feet": 0.3048,
            "inches": 0.0254,
            "centimeters": 0.01,
            "kilometers": 1000.0,
            "miles": 1609.34
        },
        "Weight": {
            "kilograms": 1.0,
            "pounds": 0.453592,
            "grams": 0.001,
            "ounces": 0.0283495
        },
        "Temperature": {
            "Celsius": lambda x: x,
            "Fahrenheit": lambda x: (x * 9/5) + 32,
            "Kelvin": lambda x: x + 273.15
        },
        "Volume": {
            "liters": 1.0,
            "gallons": 3.78541,
            "milliliters": 0.001,
            "cubic feet": 28.3168
        }
    }

    if category == "Temperature":
        if from_unit == "Fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "Kelvin":
            celsius = value - 273.15
        else:
            celsius = value
        if to_unit == "Fahrenheit":
            return (celsius * 9/5) + 32
        elif to_unit == "Kelvin":
            return celsius + 273.15
        else:
            return celsius
    
    to_base = value * conversions[category][from_unit]
    result = to_base / conversions[category][to_unit]
    return result

# Gemini Parsing Function (unchanged)
def parse_with_gemini(input_text):
    try:
        model = GenerativeModel(model_name="gemini-1.5-flash")
        
        prompt = f"""
        Parse this conversion request: "{input_text}"
        Return ONLY valid JSON in this format:
        {{
            "value": number,
            "from_unit": "string",
            "to_unit": "string",
            "category": "string"
        }}
        The category must be one of: "Length", "Weight", "Temperature", or "Volume".
        Use full unit names like "centimeters" not "cm", "kilograms" not "kg".
        """

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40
            }
        )

        raw_response = response.text.strip()
        
        if "```json" in raw_response:
            raw_response = raw_response.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_response:
            raw_response = raw_response.split("```")[1].strip()
            
        try:
            result = json.loads(raw_response)
            
            required_keys = {"value", "from_unit", "to_unit", "category"}
            if not required_keys.issubset(result.keys()):
                st.error("Response is missing required keys.", icon="❌")
                return None
                
            valid_categories = {"Length", "Weight", "Temperature", "Volume"}
            if result["category"] not in valid_categories:
                st.error(f"Invalid category: {result['category']}. Must be one of {valid_categories}", icon="❌")
                return None
                
            return float(result["value"]), result["from_unit"], result["to_unit"], result["category"]
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse JSON: {e}", icon="❌")
            return None

    except Exception as e:
        st.error(f"Gemini API error: {str(e)}", icon="🚫")
        return None

# Custom CSS for VIP look
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a4a 100%);
        color: #ffffff;
    }
    .stButton>button {
        background-color: #ff4b5c;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff6b7c;
        transform: scale(1.05);
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
    .stSelectbox>div>div>select, .stTextInput>input, .stNumberInput>input {
        color: #ffffff;
        background-color: transparent;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ff4b5c;
        color: white;
    }
    h1 {
        color: #ffd700;
        text-align: center;
        font-family: 'Arial', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stSuccess {
        background-color: rgba(0, 255, 0, 0.2);
        border: 1px solid #00ff00;
        border-radius: 10px;
    }
    .stError {
        background-color: rgba(255, 0, 0, 0.2);
        border: 1px solid #ff0000;
        border-radius: 10px;
    }
    .stWarning {
        background-color: rgba(255, 215, 0, 0.2);
        border: 1px solid #ffd700;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit App
st.title("✨ VIP Unit Converter ✨")
st.markdown("Transform units with style! Use manual controls or ask AI like 'convert 5 feet to meters' 🌟", unsafe_allow_html=True)

# Tabs with emojis
tab1, tab2 = st.tabs(["📏 Manual Mode", "🤖 AI Mode"])

# Unit options
unit_options = {
    "Length": ["meters", "feet", "inches", "centimeters", "kilometers", "miles"],
    "Weight": ["kilograms", "pounds", "grams", "ounces"],
    "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
    "Volume": ["liters", "gallons", "milliliters", "cubic feet"]
}

with tab1:
    st.markdown("### Manual Conversion", unsafe_allow_html=True)
    categories = ["Length", "Weight", "Temperature", "Volume"]
    category = st.selectbox("Category 🌈", categories, key="manual_category")
    
    col1, col2 = st.columns(2)
    with col1:
        from_unit = st.selectbox("From Unit", unit_options[category], key="manual_from")
    with col2:
        to_unit = st.selectbox("To Unit", unit_options[category], key="manual_to")
    
    value = st.number_input("Enter Value 🎯", min_value=0.0, step=0.1, key="manual_value", format="%.2f")
    
    if st.button("Convert Now 🚀", key="manual_button"):
        if value >= 0:
            result = convert_units(value, from_unit, to_unit, category)
            st.success(f"{value} {from_unit} = **{result:.4f} {to_unit}** 🎉", icon="✅")
        else:
            st.error("Please enter a positive value! ❌", icon="🚫")

with tab2:
    st.markdown("### AI-Powered Conversion", unsafe_allow_html=True)
    user_input = st.text_input("Ask me anything! (e.g., 'convert 56cm to meters') 💬", "")
    if st.button("Convert with AI 🌟", key="ai_button"):
        if user_input:
            with st.spinner("Processing with AI magic... ✨"):
                parsed = parse_with_gemini(user_input)
                if parsed:
                    value, from_unit, to_unit, category = parsed
                    try:
                        result = convert_units(float(value), from_unit, to_unit, category)
                        st.success(f"{value} {from_unit} = **{result:.4f} {to_unit}** 🎉", icon="✅")
                    except KeyError as e:
                        st.error(f"Unsupported unit: {e}. Use full names like 'meters'! ❌", icon="🚫")
                    except ValueError:
                        st.error("Invalid number in request! ❌", icon="🚫")
                else:
                    st.error("Couldn't parse your request. Try again! ❌", icon="🚫")
        else:
            st.warning("Please enter a request first! ⚠️", icon="🚨")

# Footer
st.markdown("""
    <hr style="border: 1px solid #ffd700;">
    <p style="text-align: center; color: #ffd700;">
        🚀 Crafted with ❤️ by <strong>Taha Hussain</strong> | Powered by Gemini AI 🌟
    </p>
""", unsafe_allow_html=True)
import streamlit as st
import zxcvbn
import time
import re
from typing import Dict, List, Tuple

# Set page configuration
st.set_page_config(
    page_title="Password Strength Analyzer",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern UI
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 20px;
    }
    .main {
        padding: 2rem;
    }
    .password-feedback {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .st-emotion-cache-1kyxreq {
        margin-top: 2em;
    }
    </style>
""", unsafe_allow_html=True)

def calculate_entropy(password: str) -> float:
    """Calculate password entropy."""
    char_sets: Dict[str, str] = {
        'lowercase': 'abcdefghijklmnopqrstuvwxyz',
        'uppercase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'numbers': '0123456789',
        'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?'
    }
    
    pool_size = 0
    for char_set in char_sets.values():
        if any(c in char_set for c in password):
            pool_size += len(char_set)
    
    return len(password) * (pool_size.bit_length() if pool_size > 0 else 0)

def analyze_password_patterns(password: str) -> List[str]:
    """Analyze password for common patterns."""
    patterns = []
    
    # Check for repeated characters
    if re.search(r'(.)\1{2,}', password):
        patterns.append("Contains repeated characters")
    
    # Check for sequential numbers
    if re.search(r'(?:0123|1234|2345|3456|4567|5678|6789|7890)', password):
        patterns.append("Contains sequential numbers")
    
    # Check for sequential letters
    if re.search(r'(?:abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)', password.lower()):
        patterns.append("Contains sequential letters")
    
    # Check for keyboard patterns
    keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn']
    if any(pattern in password.lower() for pattern in keyboard_patterns):
        patterns.append("Contains keyboard patterns")
    
    return patterns

def get_strength_color(score: int) -> str:
    """Get color based on password strength score."""
    colors = {
        0: "red",
        1: "orange",
        2: "yellow",
        3: "lightgreen",
        4: "green"
    }
    return colors.get(score, "red")

def main():
    st.title("🔒 Password Strength Analyzer")
    st.markdown("### Check how strong your password is")
    
    # Password input
    password = st.text_input(
        "Enter your password",
        type="password",
        help="Your password will not be stored or transmitted anywhere"
    )
    
    if password:
        # Add a small delay for visual feedback
        with st.spinner("Analyzing password..."):
            time.sleep(0.5)
            
        # Get zxcvbn analysis
        result = zxcvbn.zxcvbn(password)
        score = result['score']
        
        # Calculate additional metrics
        entropy = calculate_entropy(password)
        patterns = analyze_password_patterns(password)
        
        # Display strength meter
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(to right, 
                    {get_strength_color(score)} {(score + 1) * 20}%, 
                    #eee {(score + 1) * 20}%);
                height: 10px;
                border-radius: 5px;
                margin: 20px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )
        
        # Display score and feedback
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### Strength Score: {score}/4")
            st.markdown(f"**Entropy:** {entropy:.2f} bits")
            
        with col2:
            crack_times = result['crack_times_display']
            st.markdown("### Estimated Crack Time:")
            st.markdown(f"**Online attack:** {crack_times['online_throttling_100_per_hour']}")
            st.markdown(f"**Offline attack:** {crack_times['offline_fast_hashing_1e10_per_second']}")
        
        # Display feedback and suggestions
        st.markdown("### Analysis")
        
        feedback = result['feedback']
        warning = feedback.get('warning', '')
        suggestions = feedback.get('suggestions', [])
        
        if warning:
            st.warning(warning)
            
        if suggestions:
            st.info("Suggestions for improvement:")
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")
                
        if patterns:
            st.warning("Detected patterns:")
            for pattern in patterns:
                st.markdown(f"- {pattern}")
        
        # Password requirements
        st.markdown("### Password Requirements")
        requirements = {
            "Length": len(password) >= 12,
            "Uppercase": bool(re.search(r'[A-Z]', password)),
            "Lowercase": bool(re.search(r'[a-z]', password)),
            "Numbers": bool(re.search(r'[0-9]', password)),
            "Special Characters": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        for req, met in requirements.items():
            st.markdown(
                f"{'✅' if met else '❌'} {req}"
            )
    
    # Add information about the tool
    with st.sidebar:
        st.markdown("### About")
        st.markdown("""
        This password strength analyzer uses multiple approaches to evaluate your password:
        
        1. **zxcvbn Algorithm**: Advanced pattern matching and entropy calculation
        2. **Custom Pattern Analysis**: Checks for common patterns and sequences
        3. **Entropy Calculation**: Measures password randomness
        4. **Basic Requirements**: Length and character variety
        
        Your password is analyzed locally and is never stored or transmitted.
        """)

if __name__ == "__main__":
    main()

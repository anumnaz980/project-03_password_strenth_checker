import streamlit as st
import time
import re
from typing import Dict, List, Tuple
import math


st.set_page_config(
    page_title="Password Strength Analyzer",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="expanded",
)


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
    
    
    if re.search(r'(.)\1{2,}', password):
        patterns.append("Contains repeated characters")
    
    
    if re.search(r'(?:0123|1234|2345|3456|4567|5678|6789|7890)', password):
        patterns.append("Contains sequential numbers")
    
   
    if re.search(r'(?:abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)', password.lower()):
        patterns.append("Contains sequential letters")
    
    
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

def calculate_password_strength(password: str) -> Dict:
    """Calculate password strength using multiple factors."""
    score = 0
    feedback = {"warning": "", "suggestions": []}
    
    # Length score (0-4 points)
    length_score = min(4, len(password) // 3)
    score += length_score
    
    # Character variety score (0-4 points)
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    variety_score = sum([has_lower, has_upper, has_digit, has_special])
    score += variety_score
    
    # Pattern deduction (0-2 points)
    pattern_score = 2
    if re.search(r'(.)\1{2,}', password):
        pattern_score -= 1
        feedback["suggestions"].append("Avoid repeated characters")
    
    if re.search(r'(?:0123|1234|2345|3456|4567|5678|6789|7890)', password):
        pattern_score -= 1
        feedback["suggestions"].append("Avoid sequential numbers")
    
    if re.search(r'(?:abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)', password.lower()):
        pattern_score -= 1
        feedback["suggestions"].append("Avoid sequential letters")
    
    score += pattern_score
    
    # Entropy-based score (0-2 points)
    entropy = calculate_entropy(password)
    entropy_score = min(2, int(entropy / 50))
    score += entropy_score
    
    # Calculate crack time estimate
    possible_chars = 0
    if has_lower: possible_chars += 26
    if has_upper: possible_chars += 26
    if has_digit: possible_chars += 10
    if has_special: possible_chars += 32
    
    if possible_chars == 0:
        possible_chars = 1  # Prevent division by zero
    
    combinations = possible_chars ** len(password)
    seconds_to_crack = combinations / (1e10)  # Assuming 10 billion attempts per second
    
    crack_times = {
        "online_throttling_100_per_hour": "centuries" if seconds_to_crack > 1e8 else f"{int(seconds_to_crack/3600)} hours",
        "offline_fast_hashing_1e10_per_second": "centuries" if seconds_to_crack > 1e8 else f"{int(seconds_to_crack)} seconds"
    }
    
    # Generate feedback
    if score < 2:
        feedback["warning"] = "This password is very weak"
    elif score < 4:
        feedback["warning"] = "This password is weak"
    elif score < 6:
        feedback["warning"] = "This password is moderate"
    elif score < 8:
        feedback["warning"] = "This password is strong"
    else:
        feedback["warning"] = "This password is very strong"
    
    return {
        "score": min(4, score // 2),  # Convert to 0-4 scale
        "feedback": feedback,
        "crack_times_display": crack_times
    }

def main():
    st.title("🔒 Password Strength Analyzer")
    st.markdown("### Check how strong your password is")
    
    password = st.text_input(
        "Enter your password",
        type="password",
        help="Your password will not be stored or transmitted anywhere"
    )
    
    if password:
        with st.spinner("Analyzing password..."):
            time.sleep(0.5)
            
        result = calculate_password_strength(password)
        score = result['score']
        
        # Calculate additional metrics
        entropy = calculate_entropy(password)
        patterns = analyze_password_patterns(password)
        
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### Strength Score: {score}/4")
            st.markdown(f"**Entropy:** {entropy:.2f} bits")
            
        with col2:
            crack_times = result['crack_times_display']
            st.markdown("### Estimated Crack Time:")
            st.markdown(f"**Online attack:** {crack_times['online_throttling_100_per_hour']}")
            st.markdown(f"**Offline attack:** {crack_times['offline_fast_hashing_1e10_per_second']}")
        
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
    
    with st.sidebar:
        st.markdown("### About")
        st.markdown("""
        This password strength analyzer uses multiple approaches to evaluate your password:
        
        1. **Length Analysis**: Longer passwords are stronger
        2. **Character Variety**: Mix of different character types
        3. **Pattern Detection**: Identifies common patterns and sequences
        4. **Entropy Calculation**: Measures password randomness
        5. **Basic Requirements**: Length and character variety
        
        Your password is analyzed locally and is never stored or transmitted.
        """)

if __name__ == "__main__":
    main()

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import numpy as np
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import colorsys
import random
import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_lottie import st_lottie
import requests

# Load environment variables
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Set page config
st.set_page_config(
    page_title="Career Path Visualizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful UI
st.markdown("""
<style>
    .main {
        background-color: #f5f8fa;
    }
    .stApp {
        font-family: 'Poppins', sans-serif;
    }
    .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
    }
    .card {
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .path-item {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin: 5px;
        text-align: center;
        font-weight: 500;
        transition: all 0.3s ease;
        position: relative;
    }
    .path-item:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 14px rgba(0,0,0,0.15);
    }
    .path-number {
        position: absolute;
        top: -10px;
        left: -10px;
        background-color: #2c3e50;
        color: white;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 12px;
    }
    .stButton>button {
        background: linear-gradient(to right, #6e8efb, #a777e3);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 12px rgba(159, 122, 234, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(159, 122, 234, 0.4);
    }
    .card-metrics {
        background: linear-gradient(135deg, #3a7bd5, #00d2ff);
        border-radius: 10px;
        padding: 20px;
        color: white;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.8;
    }
    .stHeadingContainer {
        text-align: center;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Sample career paths for demo purposes
SAMPLE_PATHS = {
    "machine learning engineer": [
        "Linear Algebra", "Statistics Fundamentals", "Python Basics", 
        "Data Structures", "Pandas", "Data Visualization", 
        "Scikit-Learn", "Model Evaluation", "Neural Networks", "Deep Learning"
    ],
    "web developer": [
        "HTML Basics", "CSS Fundamentals", "JavaScript Core", 
        "DOM Manipulation", "Responsive Design", "Frontend Framework", 
        "Backend Basics", "Database Design", "API Development", "Deployment"
    ],
    "data scientist": [
        "Statistics Foundations", "Python Programming", "Data Cleaning", 
        "SQL Basics", "Data Visualization", "Exploratory Analysis", 
        "Machine Learning", "Feature Engineering", "Model Validation", "Communication Skills"
    ],
    "ux designer": [
        "Design Principles", "User Research", "Wireframing", "Prototyping", 
        "Visual Design", "Interaction Design", "Usability Testing", "User Personas", 
        "Information Architecture", "Design Systems"
    ]
}

# Function to load lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Generate vibrant colors
def generate_colors(n):
    colors = []
    for i in range(n):
        h = i / n
        s = 0.8
        v = 0.9
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append(f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})')
    return colors

def generate_learning_path(career_path, num_points=10):
    """Generate a learning path using Gemini API or fallback to samples"""
    if not api_key:
        # Return sample data if no API key
        for key in SAMPLE_PATHS:
            if key in career_path.lower():
                return SAMPLE_PATHS[key][:num_points]
        return SAMPLE_PATHS["machine learning engineer"][:num_points]
    
    # Use Gemini API if key available
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    Create a sequential learning path for someone pursuing a career in {career_path}.
    Generate exactly {num_points} concise learning points that should be mastered in order.
    
    Each point should be 2-3 words only and represent a specific skill, technology, or concept.
    Format the response as a JSON list of strings only, with no additional explanation.
    
    For example, if the career was "Machine Learning Engineer", the response might look like:
    ["Linear Algebra", "Statistics Fundamentals", "Python Basics", "Data Structures", "Pandas"]
    
    Provide the JSON list for {career_path}:
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            learning_path = json.loads(json_str)
            
            if len(learning_path) > num_points:
                learning_path = learning_path[:num_points]
            
            return learning_path
        else:
            return SAMPLE_PATHS["machine learning engineer"][:num_points]
            
    except Exception as e:
        st.error(f"Error generating learning path: {str(e)}")
        return SAMPLE_PATHS["machine learning engineer"][:num_points]

def create_learning_path_3d_graph(path):
    """Create an advanced interactive 3D graph for the learning path"""
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with positions along a curved path
    positions = {}
    
    # Define a 3D spiral for positioning nodes
    radius = 1.5
    total_angle = 2 * np.pi
    height_scale = 0.2
    
    for i, point in enumerate(path):
        angle = (i / (len(path) - 1)) * total_angle
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = i * height_scale
        positions[point] = (x, y, z)
        G.add_node(point, pos=(x, y, z))
    
    # Add edges
    for i in range(len(path) - 1):
        G.add_edge(path[i], path[i+1])
    
    # Generate node colors - gradient from start to finish
    colors = generate_colors(len(path))
    
    # Create nodes for plotly
    node_x = []
    node_y = []
    node_z = []
    node_text = []
    node_colors = []
    node_sizes = []
    
    for i, node in enumerate(path):
        x, y, z = positions[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(f"<b>{i+1}. {node}</b>")
        node_colors.append(colors[i])
        node_sizes.append(40 + (i * 2))  # Slightly larger nodes toward the end
    
    # Create edges for plotly
    edge_x = []
    edge_y = []
    edge_z = []
    edge_colors = []
    
    for edge in G.edges():
        x0, y0, z0 = positions[edge[0]]
        x1, y1, z1 = positions[edge[1]]
        
        # Create a curved edge with 10 points
        for t in np.linspace(0, 1, 10):
            # Use a slight curve for the edge
            xt = x0 + (x1 - x0) * t
            yt = y0 + (y1 - y0) * t
            zt = z0 + (z1 - z0) * t + np.sin(t * np.pi) * 0.1
            
            edge_x.append(xt)
            edge_y.append(yt)
            edge_z.append(zt)
            
            # Color for gradient edges
            idx = list(G.nodes()).index(edge[0])
            edge_colors.append(colors[idx])
    
    # Create edge trace
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(color=edge_colors, width=5),
        mode='lines',
        hoverinfo='none',
        showlegend=False
    )
    
    # Create node trace
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=node_text,
        hoverinfo='text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            opacity=0.9,
            line=dict(color='white', width=1),
            symbol='circle'
        ),
        textposition="top center",
        showlegend=False
    )
    
    # Create a more visually appealing figure
    fig = go.Figure(data=[edge_trace, node_trace])
    
    # Update layout for a sleek modern look
    fig.update_layout(
        scene=dict(
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
            zaxis=dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            ),
            aspectratio=dict(x=1, y=1, z=0.5)
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
    )
    
    return fig

def create_2d_learning_path_viz(path):
    """Create a fancy 2D visualization for smaller screens"""
    # Generate colors
    colors = generate_colors(len(path))
    
    # Create nodes and edges data
    nodes_x = []
    nodes_y = []
    nodes_text = []
    nodes_color = []
    
    # Use a curved layout for nodes
    for i, skill in enumerate(path):
        angle = np.pi * (0.1 + 0.8 * i / (len(path) - 1))
        r = 5
        nodes_x.append(r * np.cos(angle))
        nodes_y.append(r * np.sin(angle))
        nodes_text.append(f"<b>{i+1}. {skill}</b>")
        nodes_color.append(colors[i])
    
    # Create edges
    edge_x = []
    edge_y = []
    
    for i in range(len(path) - 1):
        # Add curved edges
        x0, y0 = nodes_x[i], nodes_y[i]
        x1, y1 = nodes_x[i+1], nodes_y[i+1]
        
        # Calculate control points for a quadratic bezier curve
        control_x = (x0 + x1) / 2
        control_y = (y0 + y1) / 2 + 1.5  # Pull the curve upward
        
        # Generate points along the curve
        t_values = np.linspace(0, 1, 20)
        for t in t_values:
            # Quadratic Bezier formula
            x_t = (1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * control_x + t * t * x1
            y_t = (1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * control_y + t * t * y1
            edge_x.append(x_t)
            edge_y.append(y_t)
            
        # Add None to create a break in the line
        edge_x.append(None)
        edge_y.append(None)
    
    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=3, color='rgba(150, 150, 150, 0.5)'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node trace
    node_trace = go.Scatter(
        x=nodes_x, y=nodes_y,
        mode='markers+text',
        text=nodes_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=25,
            color=nodes_color,
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace])
    
    # Update layout
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(b=0, l=0, r=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
        height=450
    )
    
    return fig

def main():
    # Load animations
    lottie_path = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_pwohahvd.json")
    lottie_complete = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_Fy7YCm.json")
    
    # Header with animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_path:
            st_lottie(lottie_path, height=200, key="header_anim")
        
        st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Career Learning Path Visualizer</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 18px;'>Generate beautiful visualizations of your career learning path</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Configure Your Path")
        
        career_path = st.text_input("Career Path", "Machine Learning Engineer", 
                                  placeholder="e.g., Data Scientist, UX Designer")
        
        num_points = st.slider("Number of Learning Points", 5, 15, 10)
        
        # API key input
        api_key_input = st.text_input("Gemini API Key (optional)", 
                                    type="password", 
                                    help="Get key from Google AI Studio")
        
        if api_key_input:
            genai.configure(api_key=api_key_input)
            st.success("✅ API key set!")
        elif api_key:
            st.success("✅ Using environment API key")
        else:
            st.warning("⚠️ No API key - using sample data")
        
        generate_button = st.button("Generate Learning Path")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sample learning paths
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Sample Career Paths")
        
        sample_careers = list(SAMPLE_PATHS.keys())
        selected_sample = st.selectbox("Try a sample path", ["Select a path"] + [p.title() for p in sample_careers])
        
        if selected_sample != "Select a path":
            if st.button(f"Load {selected_sample} Path"):
                career_path = selected_sample.lower()
                st.session_state.path = SAMPLE_PATHS[career_path.lower()]
                st.session_state.current_career = career_path
                st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'path' not in st.session_state:
        st.session_state.path = SAMPLE_PATHS["machine learning engineer"]
        st.session_state.current_career = "Machine Learning Engineer"
    
    # Generate new path if button clicked
    if generate_button:
        with st.spinner("🚀 Generating your learning path..."):
            path = generate_learning_path(career_path, num_points)
            st.session_state.path = path
            st.session_state.current_career = career_path
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        colored_header(
            label=f"3D Learning Path for: {st.session_state.current_career.title()}",
            description="Interactive 3D visualization - drag to rotate, scroll to zoom",
            color_name="violet-70"
        )
        
        # Create 3D visualization
        fig_3d = create_learning_path_3d_graph(st.session_state.path)
        st.plotly_chart(fig_3d, use_container_width=True, height=600)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Metrics
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.markdown('<div class="card-metrics">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(st.session_state.path)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Learning Steps</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with metrics_col2:
            st.markdown('<div class="card-metrics">', unsafe_allow_html=True)
            est_time = len(st.session_state.path) * 3
            st.markdown(f'<div class="metric-value">{est_time}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Est. Months</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed path
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Learning Path Steps")
        
        for i, item in enumerate(st.session_state.path, 1):
            st.markdown(f"""
            <div class="path-item">
                <div class="path-number">{i}</div>
                {item}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 2D Visualization
    st.markdown('<div class="card">', unsafe_allow_html=True)
    colored_header(
        label="Alternative 2D View",
        description="Simplified view of your learning progression",
        color_name="blue-70"
    )
    
    fig_2d = create_2d_learning_path_viz(st.session_state.path)
    st.plotly_chart(fig_2d, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download option
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            "Download Learning Path (JSON)",
            data=json.dumps(st.session_state.path, indent=2),
            file_name=f"{st.session_state.current_career.lower().replace(' ', '_')}_learning_path.json",
            mime="application/json"
        )
        
        if lottie_complete:
            st_lottie(lottie_complete, height=100, key="complete_anim")
    
    # Footer
    st.markdown("<div class='footer' style='text-align:center; margin-top:30px; color:#7f8c8d;'>Interactive Career Path Visualizer | Make your learning journey beautiful</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
import os
import cv2
import glob
import uuid
import mimetypes
from werkzeug.utils import secure_filename
import google.generativeai as genai
from flask import Flask, request, render_template, jsonify, session
from dotenv import load_dotenv

# --- INITIAL SETUP ---
load_dotenv()
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Configure the Gemini API client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Constants
FRAMES_DIR = 'static/frames'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create required directories
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs('temp', exist_ok=True)

# Store conversation history in memory, keyed by session ID
conversation_histories = {}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_video_file(file):
    """Validate video file type and size."""
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    if not allowed_file(file.filename):
        raise ValueError(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    content_type = file.content_type
    if not content_type or not content_type.startswith('video/'):
        raise ValueError("Invalid content type. Must be a video file.")

def get_session_id():
    """Get or create a session ID."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def process_video_to_frames(video_path, session_id):
    """Extracts frames from video and handles cleanup."""
    try:
        # Create session-specific directory
        session_frames_dir = os.path.join(FRAMES_DIR, session_id)
        os.makedirs(session_frames_dir, exist_ok=True)

        # Clean up old frames
        for f in glob.glob(f'{session_frames_dir}/*'):
            try:
                os.remove(f)
            except Exception as e:
                print(f"Error cleaning up old frame: {e}")

        frame_paths = []
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError("Could not open video file")

        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(int(fps), int(total_frames / 20))  # Extract max 20 frames
        frame_count = 0
        saved_count = 0

        while frame_count < total_frames:
            success, image = video.read()
            if not success:
                break

            if frame_count % frame_interval == 0:
                frame_filename = f"frame_{saved_count}.jpg"
                frame_path = os.path.join(session_frames_dir, frame_filename)
                success = cv2.imwrite(frame_path, image)
                if success:
                    print(f"Successfully saved frame to: {frame_path}")
                    frame_paths.append(frame_path)
                    saved_count += 1
                else:
                    print(f"Failed to save frame to: {frame_path}")

            frame_count += 1

        video.release()
        
        # Clean up the input video file
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"Error removing temporary video file: {e}")

        if not frame_paths:
            raise ValueError("No frames could be extracted from the video")

        return frame_paths

    except Exception as e:
        # Clean up on error
        try:
            os.remove(video_path)
        except:
            pass
        raise ValueError(f"Error processing video: {str(e)}")


# --- REAL GEMINI AI FUNCTIONS ---
def get_video_summary_from_ai(frame_paths, session_id):
    """Generates a summary of the video frames using the Gemini API."""
    try:
        if not frame_paths:
            raise ValueError("No frames provided for analysis")

        # Use a powerful multimodal model
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Prepare the domain-specific prompt for intelligent video analysis
        prompt_text = """
You are an advanced AI video analysis assistant specializing in detailed content understanding and educational responses. Analyze the video frames and prepare to engage in educational discussions about the content.

**Primary Analysis Instructions:**
1. **Content Analysis:**
   * Identify and describe key events, actions, and subjects in the video
   * Note temporal progression and significant changes
   * Recognize patterns and relationships between elements

2. **Technical & Professional Assessment:**
   * Evaluate technical aspects (quality, composition, lighting)
   * Identify professional or industry-specific elements
   * Note any relevant guidelines, standards, or best practices

3. **Educational Response Format:**
   For MCQ-style questions:
   * Provide concise, factual answers
   * Include key terms and specific details
   * If applicable, explain why other options would be incorrect

   For descriptive questions:
   * Give structured, comprehensive responses
   * Use clear headings and subheadings
   * Include examples and relevant context
   * Maintain academic tone and proper terminology

**Initial Summary Structure:**
* **Key Content Overview:**
    * Main subjects and actions
    * Timeline of events
    * Notable technical aspects

* **Professional Analysis:**
    * Industry guidelines/standards observed
    * Technical quality assessment
    * Best practices identified

* **Educational Points:**
    * Key learning elements
    * Notable technical terms
    * Relevant contextual information
"""

        # Create the content payload for the API
        prompt_parts = [prompt_text]
        for path in frame_paths:
            prompt_parts.append(genai.upload_file(path))

        print("Sending request to Gemini API...")
        response = model.generate_content(prompt_parts)

        # Store the real response in session-specific history
        conversation_histories[session_id] = [
            {'role': 'model', 'parts': [response.text]}
        ]
        
        return response.text

    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        raise ValueError(f"Failed to analyze video: {str(e)}")


def chat_with_ai(user_question, session_id):
    """Handles follow-up questions using the stored conversation history."""
    try:
        if session_id not in conversation_histories:
            return "Please analyze a video first before asking questions."

        # Start a chat session with the session-specific history
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Get existing history and print for debugging
        history = conversation_histories[session_id]
        print(f"Chat history before question: {len(history)} messages")
        
        # Start chat with history
        chat = model.start_chat(history=history)

        print(f"User follow-up question: {user_question}")
        response = chat.send_message(user_question)

        # Format the response to convert markdown to proper HTML
        formatted_response = response.text
        
        # Split into lines for better processing
        lines = formatted_response.split('\n')
        processed_lines = []
        in_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:  # Skip empty lines
                if in_section:
                    processed_lines.append('</div>')
                    in_section = False
                continue
            
            if line.startswith('*') and not line.startswith('**'):
                if in_section:
                    processed_lines.append('</div>')
                
                # Remove asterisk and create a section
                text = line[1:].strip()
                if text:
                    processed_lines.append(f'<div class="content-section"><h4 class="section-title">{text}</h4>')
                    in_section = True
            else:
                # For normal content lines
                if ':' in line:  # This is a subheading
                    parts = line.split(':', 1)
                    heading = parts[0].strip()
                    content = parts[1].strip()
                    processed_lines.append(f'<div class="sub-section"><h5>{heading}:</h5><p>{content}</p></div>')
                else:
                    processed_lines.append(f'<p>{line}</p>')
        
        if in_section:
            processed_lines.append('</div>')
            
        # Join back into a single string
        formatted_response = '\n'.join(processed_lines)
        
        # Convert any remaining bold text
        formatted_response = formatted_response.replace('**', '')
        # Fix any double list endings
        formatted_response = formatted_response.replace('</li></ul></li></ul>', '</li></ul>')
        # Add paragraph tags for better spacing
        formatted_response = formatted_response.replace('\n\n', '</p><p>')
        formatted_response = '<p>' + formatted_response + '</p>'
        # Clean up any artifacts
        formatted_response = formatted_response.replace('<p><ul>', '<ul>')
        formatted_response = formatted_response.replace('</ul></p>', '</ul>')
        formatted_response = formatted_response.replace('</strong><strong>', ' ')  # Fix double strong tags
        # Clean up any remaining newlines within list items
        formatted_response = formatted_response.replace('\n', ' ')
        
        # Update session history
        conversation_histories[session_id].extend([
            {'role': 'user', 'parts': [user_question]},
            {'role': 'model', 'parts': [formatted_response]}
        ])

        return formatted_response

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return "I'm sorry, I encountered an error processing your question. Please try again."


# --- FLASK ROUTES (THE API ENDPOINTS) ---
@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handles video upload and analysis with proper validation and error handling."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400

        video_file = request.files['video']
        validate_video_file(video_file)
        
        session_id = get_session_id()
        secure_name = secure_filename(video_file.filename)
        video_path = os.path.join('temp', f"{session_id}_{secure_name}")
        
        # Save and process video
        video_file.save(video_path)
        frame_paths = process_video_to_frames(video_path, session_id)
        
        # Generate AI summary
        summary = get_video_summary_from_ai(frame_paths, session_id)
        
        # Store initial conversation
        conversation_histories[session_id] = [
            {'role': 'model', 'parts': [summary]}
        ]
        
        # Return frames info for potential display
        frame_info = [{
            'path': os.path.basename(p),
            'url': f'/static/frames/{session_id}/{os.path.basename(p)}',
            'timestamp': idx
        } for idx, p in enumerate(frame_paths)]
        print(f"Frame info: {frame_info}")  # Debug print
        
        return jsonify({
            'summary': summary,
            'session_id': session_id,
            'frames': frame_info,
            'status': 'success'
        })

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during processing'}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat interactions with session management."""
    try:
        data = request.get_json()
        user_question = data.get('question')
        if not user_question:
            return jsonify({'error': 'No question provided'}), 400

        session_id = get_session_id()
        ai_response = chat_with_ai(user_question, session_id)
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred processing your question'}), 500

@app.route('/frames/<session_id>')
def get_frames(session_id):
    """Get frame images for a session."""
    try:
        session_frames_dir = os.path.join(FRAMES_DIR, session_id)
        if not os.path.exists(session_frames_dir):
            return jsonify({'error': 'No frames found for this session'}), 404

        frames = glob.glob(f'{session_frames_dir}/*.jpg')
        frame_info = [{'path': os.path.basename(f), 'url': f'/static/frames/{session_id}/{os.path.basename(f)}'} 
                     for f in sorted(frames)]
        
        return jsonify({'frames': frame_info})

    except Exception as e:
        print(f"Error retrieving frames: {str(e)}")
        return jsonify({'error': 'Error retrieving frame images'}), 500


# --- RUN THE APP ---
if __name__ == '__main__':
    app.run(debug=True)
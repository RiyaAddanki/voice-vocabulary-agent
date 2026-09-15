import gradio as gr
from transformers import pipeline
import json
import random

# Initialize speech recognition and text-to-speech pipelines
try:
    asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")
    tts_pipeline = pipeline("text-to-speech", model="espnet/hindi_male_fgl")
except:
    asr_pipeline = None
    tts_pipeline = None

# Vocabulary database
VOCABULARY_DB = {
    "beginner": [
        {"word": "serendipity", "definition": "The occurrence of events by chance in a happy or beneficial way", "example": "Meeting my best friend was pure serendipity."},
        {"word": "ephemeral", "definition": "Lasting for a very short time", "example": "Cherry blossoms are ephemeral, blooming only in spring."},
        {"word": "ubiquitous", "definition": "Present, appearing, or found everywhere", "example": "Smartphones have become ubiquitous in modern society."},
        {"word": "eloquent", "definition": "Fluent or persuasive in speaking or writing", "example": "The speaker gave an eloquent speech about climate change."},
        {"word": "pragmatic", "definition": "Dealing with things in a practical, realistic way", "example": "She took a pragmatic approach to solving the problem."},
    ],
    "intermediate": [
        {"word": "obfuscate", "definition": "To deliberately make something unclear or obscure", "example": "The report tried to obfuscate the true cost of the project."},
        {"word": "perspicacious", "definition": "Having keen insight or understanding", "example": "His perspicacious analysis revealed hidden patterns in the data."},
        {"word": "ameliorate", "definition": "To make something better or improve it", "example": "New policies will help ameliorate working conditions."},
        {"word": "cantankerous", "definition": "Bad-tempered, quarrelsome, or argumentative", "example": "The cantankerous old man complained about everything."},
        {"word": "sycophant", "definition": "A person who acts obsequiously to someone important", "example": "He was surrounded by sycophants who only praised him."},
    ],
    "advanced": [
        {"word": "sesquipedalian", "definition": "Characterized by long words; long-winded", "example": "His sesquipedalian writing style made the article hard to understand."},
        {"word": "defenestration", "definition": "The action of throwing someone out of a window", "example": "The historical defenestration of Prague was a turning point."},
        {"word": "floccinaucinihilipilification", "definition": "The act of estimating something as worthless", "example": "Critics practiced floccinaucinihilipilification of modern art."},
        {"word": "verisimilitude", "definition": "The quality of appearing to be true or real", "example": "The novel had such verisimilitude that readers believed it was autobiographical."},
        {"word": "anfractuosity", "definition": "The quality of being winding or full of twists", "example": "The anfractuosity of the mountain path made the hike challenging."},
    ]
}

class VocabularyAgent:
    def __init__(self):
        self.current_word = None
        self.score = 0
        self.streak = 0
        self.learned_words = []
        self.quiz_mode = False
        
    def get_random_word(self, difficulty="beginner"):
        """Get a random vocabulary word based on difficulty level"""
        words = VOCABULARY_DB.get(difficulty, VOCABULARY_DB["beginner"])
        self.current_word = random.choice(words)
        return self.current_word
    
    def get_word_info(self, word_dict):
        """Format word information for display"""
        return f"""
🎯 **Word:** {word_dict['word'].upper()}

📚 **Definition:** {word_dict['definition']}

📝 **Example:** "{word_dict['example']}"
        """
    
    def check_answer(self, user_input, correct_word):
        """Check if user's answer is correct"""
        user_input_clean = user_input.lower().strip()
        correct_clean = correct_word.lower().strip()
        
        if user_input_clean == correct_clean:
            self.score += 10
            self.streak += 1
            return True, f"✅ Correct! You earned 10 points! Streak: {self.streak}"
        else:
            self.streak = 0
            return False, f"❌ Incorrect. The answer was: **{correct_word}**. Keep learning!"
    
    def reset_progress(self):
        """Reset learning progress"""
        self.score = 0
        self.streak = 0
        self.learned_words = []
        return "🔄 Progress reset! Ready to learn?"

# Initialize agent
agent = VocabularyAgent()

# Define the interface functions
def learn_word(difficulty_level):
    """Learn a new word"""
    word_info = agent.get_random_word(difficulty_level)
    info_text = agent.get_word_info(word_info)
    return info_text, f"Current Score: {agent.score} | Streak: {agent.streak}", agent.current_word["word"]

def submit_answer(user_answer):
    """Submit answer for quiz"""
    if not agent.current_word:
        return "Please click 'Learn a Word' first!", f"Score: {agent.score}"
    
    is_correct, feedback = agent.check_answer(user_answer, agent.current_word["word"])
    return feedback, f"Current Score: {agent.score} | Streak: {agent.streak}"

def get_hint():
    """Get a hint for the current word"""
    if not agent.current_word:
        return "No word selected. Click 'Learn a Word' first!"
    word = agent.current_word["word"]
    hint = f"The word starts with '{word[0]}' and has {len(word)} letters"
    return hint

def reset_game():
    """Reset the game"""
    message = agent.reset_progress()
    return message, "Score: 0 | Streak: 0", ""

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="Voice Vocabulary Agent") as demo:
    gr.Markdown("# 🗣️ Voice Vocabulary Learning Agent")
    gr.Markdown("Learn new words interactively! Improve your vocabulary through our AI-powered voice agent.")
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📖 Learn New Words")
            difficulty = gr.Radio(
                choices=["beginner", "intermediate", "advanced"],
                value="beginner",
                label="Select Difficulty Level"
            )
            learn_btn = gr.Button("🎯 Learn a Word", variant="primary", size="lg")
            
            word_display = gr.Markdown("Click 'Learn a Word' to get started!")
            score_display = gr.Textbox(value="Score: 0 | Streak: 0", interactive=False, label="Progress")
            
            gr.Markdown("### ✍️ Quiz Time")
            user_input = gr.Textbox(
                placeholder="Type the word you just learned...",
                label="Your Answer"
            )
            submit_btn = gr.Button("📤 Submit Answer", variant="primary")
            feedback = gr.Textbox(interactive=False, label="Feedback")
            
            gr.Markdown("### 💡 Need Help?")
            hint_btn = gr.Button("🔍 Get Hint")
            hint_display = gr.Textbox(interactive=False, label="Hint")
            
            reset_btn = gr.Button("🔄 Reset Progress", variant="stop")
        
        with gr.Column(scale=1):
            gr.Markdown("### 📚 How to Use")
            gr.Markdown("""
1. **Select Difficulty**: Choose your level
2. **Learn**: Click 'Learn a Word' to see a new vocabulary word
3. **Quiz**: Type the word you just learned
4. **Submit**: Check your answer
5. **Hints**: Use hints if you're stuck
6. **Score**: Track your progress!

**Difficulty Levels:**
- 🟢 **Beginner**: Common but sophisticated words
- 🟡 **Intermediate**: More challenging vocabulary
- 🔴 **Advanced**: Rare and complex words

**Tips:**
- Focus on one difficulty level at a time
- Try to build a streak without getting stuck
- Use hints strategically
- Practice regularly to improve!
            """)
    
    # Hidden state to store current word
    current_word_state = gr.State(value="")
    
    # Connect button clicks
    learn_btn.click(
        fn=learn_word,
        inputs=[difficulty],
        outputs=[word_display, score_display, current_word_state]
    )
    
    submit_btn.click(
        fn=submit_answer,
        inputs=[user_input],
        outputs=[feedback, score_display]
    )
    
    hint_btn.click(
        fn=get_hint,
        outputs=[hint_display]
    )
    
    reset_btn.click(
        fn=reset_game,
        outputs=[feedback, score_display, user_input]
    )
    
    gr.Markdown("""
---
**Built with ❤️ using Gradio and Hugging Face**

*This prototype demonstrates an interactive vocabulary learning agent. In a production version, this could include:*
- 🎤 Actual voice input/output using speech recognition
- 🤖 AI-powered conversational hints and explanations
- 📊 Detailed progress tracking and analytics
- 🌍 Multiple languages
- 🎮 Gamification features
    """)

if __name__ == "__main__":
    demo.launch(share=True, debug=True)

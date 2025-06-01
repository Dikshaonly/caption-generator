import os
from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
from PIL import Image
import io
import random
from fastapi.middleware.cors import CORSMiddleware


PORT = int(os.environ.get("PORT", 8000))



app = FastAPI(title="Vibe Caption API", version="1.0.0")
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vibesync-5qf0.onrender.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
emotion_pipe = pipeline("image-classification", model="dima806/facial_emotions_image_detection")
# Scene/vibe detection using a general image classification model
scene_pipe = pipeline("image-classification", model="google/vit-base-patch16-224")

# Scene-based caption templates
SCENE_CAPTIONS = {
    # Nature & Outdoors
    "beach": [
        "Salt in the air, sand in my hair 🏖️ #BeachVibes",
        "Ocean therapy session complete 🌊 #Peaceful",
        "Life's better by the water 💙 #BeachLife",
        "Vitamin Sea incoming! ☀️ #Paradise",
        "Where the sky meets the sea ✨ #Horizon"
    ],
    # Celestial & Night
    "moon": [
        "Moonlit magic happening ✨🌙 #Lunar",
        "Dancing under the moonlight 🌕 #NightVibes",
        "Moon child energy activated 🌙 #Celestial",
        "When the moon hits your eye... 🌙✨ #Romantic",
        "Lunar therapy session in progress 🌕 #Peaceful",
        "Howling at the moon tonight 🐺🌙 #Wild",
        "Moonbeams and dreams 🌙💫 #Mystical"
    ],

    "sunset": [
        "Chasing sunsets and dreams 🌅 #GoldenHour",
        "Nature's daily masterpiece 🎨 #Sunset",
        "Every sunset is a promise of tomorrow ✨ #Hope",
        "Sky on fire tonight 🔥 #Breathtaking",
        "Golden hour magic never gets old 💫 #Blessed"
    ],
    "mountain": [
        "Peak vibes only 🏔️ #MountainLife",
        "Higher altitude, higher gratitude 🙏 #Summit",
        "The mountains are calling... 📞 #Adventure",
        "Finding peace at elevation ⛰️ #Serenity",
        "Sky-high perspectives 🦅 #ViewFromTheTop"
    ],
    "forest": [
        "Lost in the woods, found in nature 🌲 #ForestTherapy",
        "Tree therapy session 🌳 #NatureHealing",
        "Into the wild I go 🍃 #Adventure",
        "Forest bathing is real 🌿 #Mindful",
        "Among the giants 💚 #Peaceful"
    ],
    "rain": [
        "Dancing in the rain 🌧️ #Refreshing",
        "Petrichor and good vibes ☔ #RainyDay",
        "Let the rain wash away yesterday 💧 #Renewal",
        "Storm chaser mood 🌩️ #Wild",
        "Rainy days = cozy vibes ☔ #Mood"
    ],
    "snow": [
        "Winter wonderland activated ❄️ #SnowDay",
        "Let it snow, let it glow ✨ #Winter",
        "Frozen moments, warm hearts 💙 #Snow",
        "Winter magic is real ⛄ #Wonderland",
        "Cold outside, cozy inside 🔥 #WinterVibes"
    ],
    # Social & Entertainment
    "party": [
        "Party mode: ACTIVATED 🎉 #LetsGo",
        "Dancing through life one beat at a time 💃 #PartyVibes",
        "Good times and crazy friends 🎊 #Squad",
        "Life's a party, dress accordingly ✨ #Celebration",
        "Turn up the music, turn up the fun! 🎵 #Party",
        "Making memories on the dance floor 🕺 #GoodTimes",
        "Party like there's no tomorrow 🎉 #YOLO",
        "Confetti in my hair, joy in my heart 🎊 #Festive"
    ],
    
    # Urban & Architecture
    "city": [
        "City lights and late nights 🌃 #UrbanVibes",
        "Concrete jungle where dreams are made 🏙️ #CityLife",
        "Metropolitan mood activated 🚕 #Urban",
        "Skyline state of mind 🏢 #CityVibes",
        "Urban exploring mode on 📍 #Adventure"
    ],
    "building": [
        "Architecture appreciation post 🏛️ #Design",
        "Lines, angles, and inspiration 📐 #Geometry",
        "Built environment, elevated mood 🏗️ #Urban",
        "Structure and style 🎨 #Architecture",
        "Man-made marvels ✨ #Engineering"
    ],
    "street": [
        "Street scenes and city dreams 🛣️ #UrbanLife",
        "Every street tells a story 📖 #Exploring",
        "Pavement poetry in motion 🚶 #Walk",
        "City sidewalk chronicles 📝 #Life",
        "Streets full of possibilities 🌟 #Adventure"
    ],
    
    # Water & Weather
    "water": [
        "Water you doing? Just vibing 💧 #Refreshing",
        "H2O and good vibes only 🌊 #Pure",
        "Liquid serenity 💙 #Calm",
        "Water therapy in session 🏊 #Healing",
        "Going with the flow 🌊 #Peaceful"
    ],
    "lake": [
        "Lake life is the best life 🏞️ #Tranquil",
        "Mirror, mirror on the lake 🪞 #Reflection",
        "Still waters, deep thoughts 💭 #Peaceful",
        "Lakeside state of mind 🛶 #Serenity",
        "Nature's perfect mirror ✨ #Beautiful"
    ],
    "sky": [
        "Head in the clouds ☁️ #Dreaming",
        "Sky's the limit today 🚀 #Limitless",
        "Cloud watching champion 👀 #Peaceful",
        "Infinite blue above 💙 #Freedom",
        "Sky therapy session ✨ #Mindful"
    ],
    
    # Transportation
    "ship": [
        "Sailing through life 🚢 #Adventure",
        "Anchors aweigh! ⚓ #Journey",
        "Smooth sailing ahead ⛵ #Optimistic",
        "Ocean vessel vibes 🌊 #Nautical",
        "Ship happens, roll with it 🚢 #Philosophy"
    ],
    "boat": [
        "Row, row, row your boat 🚣 #Adventure",
        "Boat life best life ⛵ #Freedom",
        "Floating through paradise 🏝️ #Bliss",
        "Maritime mood activated 🌊 #Nautical",
        "Life's better on the water 💙 #BoatLife"
    ],
    "car": [
        "Road trip ready 🚗 #Adventure",
        "Life in the fast lane 🏎️ #Speed",
        "Journey over destination 🛣️ #Travel",
        "Four wheels and freedom 🚙 #Road",
        "Drive mode: activated 🚘 #Journey"
    ],
    
    # Animals & Nature
    "dog": [
        "Paws-itively perfect day 🐕 #DogLife",
        "My human's pretty cool too 🐶 #BestFriend",
        "Tail-wagging good times 🐕‍🦺 #Joy",
        "Unconditional love looks like this 💕 #Dogs",
        "Who's a good day? Today is! 🐾 #Happy"
    ],
    "cat": [
        "Feline fine today 🐱 #CatLife",
        "Purr-fectly content 😸 #Zen",
        "Independent but make it cute 🐈 #Mood",
        "Nine lives, infinite sass 😼 #Attitude",
        "Meow or never 🐾 #CatVibes"
    ],
    "bird": [
        "Free as a bird 🕊️ #Freedom",
        "Early bird gets the good vibes 🐦 #Morning",
        "Soaring high today 🦅 #Elevated",
        "Tweet dreams are made of this 🐤 #Happy",
        "Wings and wonderful things 🦋 #Flight"
    ],
    
    # Food & Lifestyle
    "food": [
        "Fuel for the soul 🍽️ #Foodie",
        "Good food, good mood 😋 #Delicious",
        "Eating my way to happiness 🥰 #Food",
        "Life's too short for bad food ✨ #Taste",
        "Feeding the soul, one bite at a time 🍴 #Yum"
    ],
    "flower": [
        "Bloom where you're planted 🌸 #Growth",
        "Flower power activated 🌺 #Beautiful",
        "Stop and smell the roses 🌹 #Mindful",
        "Petals and positive vibes 🌻 #Happy",
        "Nature's art gallery 🎨 #Gorgeous"
    ],
    
    # Default/General
    "default": [
        "Living my best life ✨ #Blessed",
        "Good vibes only today 🌟 #Positive",
        "Making memories one moment at a time 📸 #Life",
        "Today's mood: grateful 🙏 #Thankful",
        "Capturing the magic ✨ #Moment"
    ]
}

# Emotion + Scene combination templates
COMBO_CAPTIONS = {
    ("happy", "beach"): [
        "Beach therapy + good vibes = perfect day! 🏖️😊 #BeachHappy",
        "Sunshine outside, sunshine inside! ☀️💙 #BeachBliss"
    ],
    ("happy", "sunset"): [
        "Chasing sunsets with a smile 🌅😄 #GoldenMoments",
        "Happy heart, golden hour magic ✨😊 #SunsetJoy"
    ],
    ("sad", "rain"): [
        "Sometimes you need the storm to appreciate the rainbow 🌧️💙 #Healing",
        "Rain washes everything clean, including hearts ☔💧 #Renewal"
    ],
    ("peaceful", "lake"): [
        "Inner peace meets outer beauty 🏞️🧘 #Serenity",
        "Still waters, calm soul 💙✨ #Tranquil"
    ],
    ("happy", "party"): [
        "Living my best party life! 🎉😄 #PartyHappy",
        "Good vibes and great friends! 🎊✨ #Celebration"
    ],
    ("excited", "party"): [
        "Energy through the roof tonight! 🎉⚡ #PartyMode",
        "Can't contain this party excitement! 🕺🎊 #TurnUp"
    ],
    ("peaceful", "moon"): [
        "Moonlight meditation vibes 🌙🧘 #LunarPeace",
        "Finding serenity under the stars ✨🌕 #Tranquil"
    ],
    ("happy", "moon"): [
        "Moon makes everything magical! 🌙😊 #LunarJoy",
        "Smiling at the moon, moon smiling back 🌕💫 #MoonChild"
    ],
    ("excited", "city"): [
        "City energy matching my vibe! 🌃⚡ #UrbanExcitement",
        "Ready to take on the world! 🏙️🚀 #CityVibes"
    ]
}

def classify_scene(image):
    """Classify the scene/vibe of the image"""
    try:
        results = scene_pipe(image)
        # Get top prediction
        top_prediction = results[0]
        
        # Map common ImageNet classes to our scene categories
        scene_mapping = {
            # Nature
            "seashore": "beach",
            "lakeside": "beach", 
            "beach": "beach",
            "ocean": "beach",
            "coastline": "beach",
            "pier": "beach",
            "dock": "beach",
            
            "mountain": "mountain",
            "valley": "mountain",
            "cliff": "mountain",
            "volcano": "mountain",
            "alp": "mountain",
            
            "forest": "forest",
            "tree": "forest",
            "jungle": "forest",
            "park": "forest",
            "garden": "forest",
            "grove": "forest",
            
            "lake": "lake",
            "pond": "lake",
            "reservoir": "lake",
            
            "sky": "sky",
            "cloud": "sky",
            "atmosphere": "sky",
            
            # Celestial/Night scenes - NEW MOON MAPPINGS
            "moon": "moon",
            "lunar": "moon",
            "night": "moon",
            "nighttime": "moon",
            "evening": "moon",
            "dusk": "moon",
            "twilight": "moon",
            "moonlight": "moon",
            "crescent": "moon",
            "full moon": "moon",
            "astronomy": "moon",
            "celestial": "moon",
            "starry": "moon",
            "stars": "moon",
            "constellation": "moon",
            
            # Urban
            "city": "city",
            "downtown": "city",
            "skyline": "city",
            "metropolitan": "city",
            "urban": "city",
            "skyscraper": "building",
            "building": "building",
            "architecture": "building",
            "tower": "building",
            "bridge": "building",
            "street": "street",
            "road": "street",
            "sidewalk": "street",
            "crosswalk": "street",
            
            # Social/Entertainment - NEW PARTY MAPPINGS
            "party": "party",
            "celebration": "party",
            "festival": "party",
            "concert": "party",
            "nightclub": "party",
            "club": "party",
            "dance": "party",
            "dancing": "party",
            "disco": "party",
            "birthday": "party",
            "wedding": "party",
            "event": "party",
            "gathering": "party",
            "crowd": "party",
            "people": "party",
            "confetti": "party",
            "balloons": "party",
            "music": "party",
            "stage": "party",
            "lights": "party",
            "entertainment": "party",
            
            # Transportation
            "ship": "ship",
            "vessel": "ship",
            "yacht": "ship",
            "cruise": "ship",
            "boat": "boat",
            "sailboat": "boat",
            "canoe": "boat",
            "kayak": "boat",
            "car": "car",
            "vehicle": "car",
            "automobile": "car",
            "truck": "car",
            
            # Animals
            "dog": "dog",
            "puppy": "dog",
            "golden retriever": "dog",
            "cat": "cat",
            "kitten": "cat",
            "bird": "bird",
            "eagle": "bird",
            "owl": "bird",
            "parrot": "bird",
            
            # Nature elements
            "flower": "flower",
            "rose": "flower",
            "sunflower": "flower",
            "daisy": "flower",
            "tulip": "flower",
            
            # Food
            "food": "food",
            "meal": "food",
            "restaurant": "food",
            "pizza": "food",
            "sandwich": "food",
            
            # Weather patterns (these might be harder to detect directly)
            "rain": "rain",
            "storm": "rain",
            "snow": "snow",
            "winter": "snow",
        }
        
        pred_label = top_prediction["label"].lower()
        

        for key, scene in scene_mapping.items():
            if key in pred_label:
                return scene, top_prediction["score"]
        
        
        return "default", top_prediction["score"]
        
    except Exception as e:
        print(f"Scene classification error: {e}")
        return "default", 0.5

def generate_combined_caption(emotion: str, scene: str, emotion_confidence: float, scene_confidence: float) -> str:
    """Generate caption based on both emotion and scene"""
    
    # Normalize inputs
    emotion_lower = emotion.lower()
    scene_lower = scene.lower()
    
    # Check for specific emotion-scene combinations
    combo_key = (emotion_lower, scene_lower)
    if combo_key in COMBO_CAPTIONS:
        return random.choice(COMBO_CAPTIONS[combo_key])
    
    # If scene confidence is higher, prioritize scene
    if scene_confidence > emotion_confidence and scene_lower in SCENE_CAPTIONS:
        base_caption = random.choice(SCENE_CAPTIONS[scene_lower])
        
        
        if emotion_lower == "happy":
            return base_caption.replace("vibes", "happy vibes").replace("mood", "joyful mood")
        elif emotion_lower == "sad":
            return base_caption.replace("vibes", "reflective vibes").replace("mood", "contemplative mood")
        elif emotion_lower == "excited":
            return base_caption.replace("vibes", "exciting vibes").replace("mood", "energetic mood")
        
        return base_caption
    
   
    else:
        emotion_templates = {
            "happy": SCENE_CAPTIONS.get("default", ["Good vibes! ✨"]),
            "sad": ["Taking it one day at a time 💙 #Healing"],
            "angry": ["Channeling energy positively 🔥 #Motivation"],
            "surprised": ["Life keeps surprising me! 🌀 #Unexpected"],
            "fear": ["Growing through challenges 🌱 #Strength"],
            "neutral": ["Living in the moment ✨ #Present"]
        }
        
        base_templates = emotion_templates.get(emotion_lower, emotion_templates["neutral"])
        base_caption = random.choice(base_templates)
        
   
        if scene_lower != "default" and scene_lower in SCENE_CAPTIONS:
            scene_keywords = {
                "beach": "by the water",
                "sunset": "during golden hour", 
                "mountain": "with elevated views",
                "city": "in the urban jungle",
                "forest": "surrounded by nature",
                "rain": "in the rain"
            }
            
            if scene_lower in scene_keywords:
                base_caption = base_caption.replace("today", f"today {scene_keywords[scene_lower]}")
        
        return base_caption

@app.post("/vibe")
async def detect_vibe(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Detect emotion
        emotion_result = emotion_pipe(image)
        top_emotion = emotion_result[0]["label"]
        emotion_confidence = emotion_result[0]["score"]
        
        # Detect scene/vibe
        scene, scene_confidence = classify_scene(image)
        
        # Generate combined caption
        caption = generate_combined_caption(
            top_emotion, scene, emotion_confidence, scene_confidence
        )
        
        return {
            "emotion": top_emotion.lower(),
            "emotion_confidence": emotion_confidence,
            "scene": scene,
            "scene_confidence": scene_confidence,
            "caption": caption,
            "vibe": emotion_result,  
            "primary_vibe": "emotion" if emotion_confidence > scene_confidence else "scene"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "caption": "Something went wrong, but the moment is still beautiful! ✨ #TechIssues"
        }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server running with emotion + scene detection!"}

@app.get("/")
async def root():
    return {
        "message": "Vibe Caption API is running!",
        "endpoints": {
            "/health": "Health check",
            "/vibe": "Upload image to get caption (POST)",
            "/docs": "API documentation"
        }
    }
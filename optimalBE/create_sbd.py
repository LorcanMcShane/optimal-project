from pymongo import MongoClient
import bcrypt

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.optimalDB
sbd = db.sbd

sbd_list = [
    {
        "exercise": "Squat",
        "description": """The barbell squat is often referred to as the "king of all exercises" due to its ability to develop lower body strength, power, and muscle mass while also engaging the core and stabilizing muscles. This fundamental compound movement primarily targets the quadriceps, hamstrings, and glutes, but it also recruits the lower back, abdominals, and even upper body muscles to maintain proper posture and balance. Squatting with a barbell is one of the best ways to improve overall athletic performance, as the movement mimics natural human biomechanics, making it highly functional for activities like running, jumping, and lifting. Additionally, squats are incredibly effective at strengthening the posterior chain, which is crucial for preventing injuries and enhancing mobility. The squat is not just about muscle growth; it also improves joint stability, bone density, and flexibility, making it beneficial for people of all fitness levels. Performing squats with proper form is critical to preventing knee and lower back strain, and variations such as front squats, box squats, and goblet squats allow for different training adaptations based on individual needs. Squatting also stimulates the release of growth hormones and testosterone, making it an excellent exercise for overall body composition and strength development. Whether you're an athlete, bodybuilder, or someone looking to increase functional strength and endurance, the barbell squat is a foundational exercise that delivers unmatched benefits in both performance and aesthetics.""",

        "tips": {"tips_headers": ["Maintain a strong stance",
                                  "Brace your core",
                                  "Keep your chest up",
                                  "Break at the hips first",
                                  "Drive through your heels"],
                 "tips_content": ["Position your feet shoulder-width apart with toes slightly pointed out for balance.",
                                  "Keep your abs tight to protect your spine and improve overall stability.",
                                  "Avoid leaning forward excessively by keeping your chest lifted throughout the movement.",
                                  "Initiate the squat by pushing your hips back before bending your knees.",
                                  "Push the weight up through your heels and midfoot to prevent excessive strain on your knees."]},
        "written_cues": {"written_cue_headers": ["Feet shoulder-width apart", "Screw your feet into the floor", "Big belly breath & brace", "Hips back, then down", "Knees track over toes", "Chest up, don’t fold", "Drive through midfoot", "Explode up"],
                         "written_cue_content": ["Find your optimal stance.", "Create stability.", "Engage your core.", "Control your descent.", "Avoid caving in or flaring out.", "Maintain a strong upper back.", "Keep balance; don’t rock forward.", "Push the floor away."]}
    },

    {
        "exercise": "Bench Press",
        "description": "The bench press is one of the most fundamental and widely recognized exercises in strength training, playing a crucial role in building upper body strength, power, and muscle mass. As a compound movement, it engages multiple muscle groups, primarily targeting the pectoral muscles, deltoids, and triceps, while also recruiting stabilizing muscles such as the core and even the legs to maintain proper form. This exercise is a staple in powerlifting, bodybuilding, and general fitness routines, serving as a benchmark for measuring upper body strength. The ability to press heavy weights not only enhances athletic performance but also contributes to functional strength, benefiting daily activities such as pushing, lifting, and carrying objects. Additionally, the bench press improves muscular endurance, promotes bone density, and can even aid in boosting testosterone levels, which supports overall muscle growth and recovery. Proper technique is essential to maximize effectiveness and prevent injury, as incorrect form can lead to strain on the shoulders or wrists. Incorporating variations like incline, decline, and dumbbell presses can help target different parts of the chest and prevent muscular imbalances. Whether you're an elite athlete, a bodybuilder, or someone looking to improve their physique and strength, the bench press remains an essential exercise for developing a powerful upper body and achieving long-term fitness goals.",
        "tips": {
            "tips_headers": [
                    "Keep your feet planted",
                    "Grip the bar correctly",
                    "Engage your upper back",
                    "Lower the bar with control",
                    "Use a slight arch"
            ],
            "tips_content": [
                "Maintain a stable base by keeping your feet flat on the ground to maximize leg drive and power.",
                "Use a firm grip with your wrists in a neutral position to prevent strain and improve control.",
                "Retract your shoulder blades and keep your back tight for better stability and strength.",
                "Avoid bouncing the bar off your chest; lower it slowly to maintain tension and prevent injury.",
                "A natural arch in your lower back helps maintain proper form and reduces stress on your shoulders."
            ]
        },
        "written_cues": {
            "written_cue_headers": [
                "Feet planted & engaged",
                "Upper back tight",
                "Grip the bar tight",
                "Wrists stacked over elbows",
                "Big breath & brace",
                "Controlled descent",
                "Elbows at ~75° angle",
                "Drive through the floor"
            ],
            "written_cue_content": [
                "Use leg drive.",
                "Retract and depress scapula.",
                "Engage forearms and lats.",
                "Maintain bar path.",
                "Create stability.",
                "Lower the bar with intent.",
                "Avoid excessive flare/tuck.",
                "Use leg drive to push."
            ]
        }
    },

    {
        "exercise": "Deadlift",
        "description": "The deadlift is one of the most essential and powerful exercises in strength training, widely regarded as the ultimate test of full-body strength and functionality. As a compound movement, it engages multiple muscle groups, including the glutes, hamstrings, quadriceps, lower back, traps, and core, making it one of the most efficient lifts for building raw strength and muscle mass. Unlike many other exercises, the deadlift mimics real-life movements such as lifting heavy objects from the ground, making it highly functional and beneficial for everyday activities. It strengthens the posterior chain, which plays a critical role in athletic performance, injury prevention, and overall stability. Additionally, deadlifting helps improve grip strength, which carries over to various other lifts and sports. The movement also stimulates the release of anabolic hormones like testosterone and growth hormone, promoting muscle development and fat loss. However, proper form is crucial to avoid injury, as improper technique can place excessive strain on the lower back. Variations such as the sumo deadlift, Romanian deadlift, and trap bar deadlift allow for muscle targeting and can help lifters of all experience levels find a version that suits their biomechanics. Whether you’re a powerlifter, an athlete, or simply someone looking to improve overall strength and functionality, the deadlift remains an unparalleled exercise for building power, resilience, and total-body strength.",
        "tips": {
            "tips_headers": [
                "Set up with a strong stance",
                "Engage your core and lats",
                "Drive through your heels",
                "Keep the bar close",
                "Lock out with control"
            ],
            "tips_content": [
                "Keep your feet hip-width apart and grip the bar just outside your legs for maximum leverage.",
                "Brace your core and pull your shoulder blades down to protect your lower back.",
                "Push the floor away with your heels rather than relying on your lower back to lift.",
                "The bar should stay as close to your body as possible to reduce unnecessary strain.",
                "Stand up tall by fully extending your hips, but avoid excessive leaning back at the top."
            ]
        },
        "written_cues": {
            "written_cue_headers": [
                "Feet hip-width apart",
                "Bar over midfoot",
                "Grip tight & set lats",
                "Hinge at hips, then bend knees",
                "Chest up, back neutral",
                "Big breath & brace",
                "Push the floor away",
                "Lockout with glutes, not back"
            ],
            "written_cue_content": [
                "Find a strong stance.",
                "Keep the bar close.",
                "Engage your upper body.",
                "Keep tension.",
                "No rounding or overextending.",
                "Core stability is key.",
                "Use leg drive.",
                "Finish strong."
            ]
        }
    }






]

for exercise in sbd_list:
    sbd.insert_one(exercise)

# Read the workspace and give ne an appropriate README.md file for GitHub. Name of the app: PenPal

# PenPal

PenPal is an AI powered automated journaling application that uses numerous data points from your phone to automatically journal.

## Features

- **Journaling and Storytelling:** Our project excels in storytelling by creating journal entries that eloquently narrate the events, emotions, and transitions within a day. This storytelling aspect beautifully captures the cyclical nature of life, from morning routines to evening relaxation, forming a complete circle of experiences.

- **Editing and Personalization:** PenPal empowers users to take charge of their narratives. You can easily edit your journal entries, adding personal insights, memories, and emotions. This personalization ensures that each entry resonates with the unique cycles and rhythms of your life.

- **Voice Cloning:** One of our proudest achievements is enabling users to have their journal entries read in their voice using AI. This not only adds a personal touch but also creates an auditory representation of the phases in one's life, enhancing the documentation experience.

- **Interacting with Past Self:** PenPal goes beyond traditional journaling. Users can interact with an older persona of themselves, constructed from past journal entries. This unique feature allows for introspection and reflection on how different phases have shaped your journey.

## Setup

To install PenPal, follow these steps:

1. Clone the repository: `git clone https://github.com/username/penpal.git`
2. Navigate into the project directory: `cd penpal`
3. Install the dependencies: `pip install -r requirements.txt`
4. Replace OpenAI API key in `server.py` with your own API key
5. Start the server: `uvicorn server:app --reload`

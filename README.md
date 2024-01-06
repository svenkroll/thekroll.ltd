# [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/R6R8QT94J)  Minimalistic technology concept for a AI powered website 

## Description
Welcome to a revolutionary era of web interaction with our ChatGPT-Enhanced Website based on vectorized local data! This isn't just another website; it's a paradigm shift in digital interaction, blending advanced AI capabilities with intuitive design. Built for the modern user who values efficiency and innovation, this website represents a leap in web development, where AI does the heavy lifting, and you reap the rewards. See it live at `https://thekroll.ltd`

## Features
- **AI-Powered Contextual Interactions**: Harnessing the power of OpenAI's ChatGPT, our website answers queries with precision, tapping into a well of contextual data tailored to the company and individual user profiles.
- **Efficient Data Utilization**: At the heart of our system is ChromaDB, a sophisticated engine that adeptly handles the vectorization of JSON files. This ensures that the AI model receives only the most relevant context, leading to responses that are both accurate and meaningful.
- **Lazy Loading, Maximum Impact**: Why build a full website when AI can do it for you? Embrace the future where designing detailed web pages is a thing of the past. Our system smartly populates content, saving you countless hours of work.
- **Dynamic Content Generation**: Imagine a website that creates stunning, relevant images on-the-fly using Dall-E, or displays complex information like PDFs right outside the chat window. That's the magic we offer – dynamic, responsive, and always engaging.

## Installation
1. **Clone the Repository**: `git clone [repository URL]`
2. **Set Up Environment**: Configure your environment as per `.env.dist`.
3. **Install Dependencies**: `pip install -r requirements.txt`.
4. **Model Setup**: `python download_models.py` for necessary models.

## Usage
- **Starting the Server**:
  ```bash
  cd thekroll.ltd
  python app/main.py
  ```
- **Accessing the Site**: Open `http://localhost:8080` in your browser.

### Deep Dive into the Technology:
- **ChromaDB & Data Vectorization**: We use ChromaDB for efficient data management. It vectorizes JSON files, ensuring that ChatGPT receives only the most relevant data. This leads to more accurate and contextually appropriate responses but also keeps the whole content where it should. Safe! In addition we save the time and cost to fine tune a model with our data, just update the JSON data files and restart the process.
- **Dynamic Content with Dall-E**: Our integration with Dall-E allows for the creation of images tailored to user interactions, adding a visually engaging layer to the experience.
- **Efficient Information Display**: Information like PDFs is displayed seamlessly, ensuring that users have all the necessary data at their fingertips, without cluttering the chat interface.

## Contributing
Your contributions can help shape the future of web interaction. Join us in this journey!

## License
Open-sourced under the MIT License.

## Contact
Reach out to me at sven@thekroll.ltd for collaboration or queries.

## Acknowledgments
Kudos to OpenAI for their ChatGPT API, and to all who dare to innovate in the digital space.

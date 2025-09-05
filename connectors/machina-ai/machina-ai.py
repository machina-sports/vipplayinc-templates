from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from openai import OpenAI

import base64
from io import BytesIO
from PIL import Image


def edit_image(request_data):

    headers = request_data.get("headers")

    params = request_data.get("params")

    api_key = headers.get("api_key", "")

    image_id = params.get("image_id", "")

    model_name = params.get("model", "")

    instruction = params.get("instruction", "")

    images_base64 = params.get("images_base64", [])

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    if not images_base64:
        return {"status": "error", "message": "At least one image is required."}

    image_files = []
    try:
        for idx, img_base64 in enumerate(images_base64):
            if ',' in img_base64:
                img_base64 = img_base64.split(',')[1]
            
            img_bytes = base64.b64decode(img_base64)
            
            try:
                img = Image.open(BytesIO(img_bytes))
                if img.format == 'WEBP':
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.getchannel('A'))
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    temp_filepath = f"/work/images/temp_{image_id}_{idx}.png"
                    img.save(temp_filepath, 'PNG')
                else:
                    temp_filepath = f"/work/images/temp_{image_id}_{idx}.png"
                    with open(temp_filepath, 'wb') as f:
                        f.write(img_bytes)
            except Exception as e:
                return {"status": "error", "message": f"Error converting image format: {str(e)}"}
            
            image_files.append(temp_filepath)
    except Exception as e:
        return {"status": "error", "message": f"Error saving images: {str(e)}"}

    prompt = f"""
        Using the context of this poll/quiz question as guidance ONLY:
        {instruction}

        Create a professional sports composition optimized for mobile app layout with these requirements:

        Image Pre-processing:
        - Remove any overlaid graphics or distracting elements
        - Focus on capturing clear, dynamic action poses or relevant context
        - Select images that best represent the context

        Depth and Focus Management (TWO LAYERS ONLY):
        FOREGROUND - Focus Length (100% focus):
        - If a main subject (such as a player, coach, trophy, or ball) is present, position it strategically
        - Occupy 10-20% of frame height (smaller for app layout)
        - Position centered or in lower third/center-left/right, but always far from all borders
        - Full dynamic range and contrast
        - Prominent and detailed but not overwhelming
        - Absolutely no part of the main subject should be cropped or touch the image edges
        - If there is no main subject, focus on the environment, stadium, or relevant context in the foreground

        BACKGROUND - Soft Focus (60% focus):
        - Stadium/city/venue elements only
        - Reduced contrast and muted details
        - Creates depth without distracting
        - Should occupy 70-80% of the frame

        SUBJECT PLACEMENT & MARGINS:
        - If a main subject is present, it must be positioned well away from all image borders (at least 25-30% margin on every side)
        - The main subject should be centered or placed to maximize empty space (negative space) around it
        - No part of the main subject should be cropped or touch the image edges
        - The main subject should occupy no more than 15-20% of the total image area
        - If there is no main subject, create a visually appealing composition focusing on the stadium, venue, or relevant environment, ensuring balanced empty space and clear margins
        - Do not add any text or graphic overlays to the image
        - The composition must allow for unobstructed placement of app elements above, below, and to the sides of the main subject or environment

        Layout Guidelines for App Integration:
        - Create balanced composition with generous margins (25-30% on all sides)
        - Leave clear space for possible app UI elements
        - Avoid placing main subjects in top 25% or bottom 25% of frame
        - Maintain clear separation between focused and blurred elements
        - Arrange elements to support visual storytelling while preserving UI space
        - Ensure main subject or key environment doesn't interfere with potential app element placement areas

        Visual Style:
        - Create clean, professional sports aesthetic
        - Apply subtle lighting enhancements while keeping realism
        - Keep the overall composition minimal and focused
        - Ensure smooth transition between focused and blurred areas
        - Use negative space effectively for app interface elements

        Technical Quality Requirements:
        - Create natural photo-realistic blur in background
        - Preserve original image quality and resolution
        - Ensure sufficient contrast for possible text overlay readability

        CRITICAL RULES:
        - If no main subject is present, focus on the environment or context
        - Never add text or artificial overlays
        - NO person duplication
        - NO unrealistic positioning
        - NO artificial or surreal effects
        - NO inconsistent lighting or shadows
        - NO mixing of different sports or contexts
        - MAIN SUBJECTS MUST NOT OCCUPY MORE THAN 20% OF FRAME HEIGHT
        - LEAVE AMPLE MARGINS FOR APP LAYOUT ELEMENTS (minimum 25-30% on all sides)
        - MAIN SUBJECTS MUST BE FAR FROM ALL IMAGE BORDERS (minimum 25-30% margin)
        - NO CROPPING OR TOUCHING OF MAIN SUBJECT TO IMAGE EDGES
        - LEAVE LARGE EMPTY SPACE FOR APP OVERLAYS
        """

    try:
        llm = OpenAI(api_key=api_key)

        image_files = [
            open(path, "rb")
            for path in image_files
        ]

        result = llm.images.edit(
            model=model_name,
            image=image_files,
            prompt=prompt,
            size="1024x1536",
            quality="high",
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        full_filepath = f"/work/images/{image_id}.webp"

        with open(full_filepath, 'wb') as f:

            f.write(image_bytes)

        final_filename = f"{image_id}.webp"

        # convert to png

        img = Image.open(full_filepath)
        
        final_filename = f"{image_id}.png"
        
        full_filepath = f"/work/images/{final_filename}"
        
        img.save(full_filepath, 'PNG')

        result = {
            "final_filename": final_filename,
            "full_filepath": full_filepath
        }

        return {"status": True, "data": result, "message": "Image generated."}

    except Exception as e:

        return {"status": False, "error": {"message": f"Exception when generating image: {e}"}} 


def generate_image(request_data):

    headers = request_data.get("headers")

    params = request_data.get("params")

    api_key = headers.get("api_key", "")

    image_id = params.get("image_id", "")

    model_name = params.get("model", "")

    instruction = params.get("instruction", "")

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    prompt = f""""""

    try:
        llm = OpenAI(api_key=api_key)

        result = llm.images.generate(
            model=model_name,
            prompt=prompt,
            size="1536x1024",
            quality="high",
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        full_filepath = f"/work/images/{image_id}.webp"

        with open(full_filepath, 'wb') as f:

            f.write(image_bytes)

        final_filename = f"{image_id}.webp"

        result = {
            "final_filename": final_filename,
            "full_filepath": full_filepath
        }

        return {"status": True, "data": result, "message": "Image generated."}

    except Exception as e:
        return {"status": False, "message": f"Exception when generating image: {e}"} 
    

def invoke_embedding(params):

    api_key = params.get("api_key", "")

    model_name = params.get("model_name")

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    try:
        llm = OpenAIEmbeddings(api_key=api_key, model=model_name)
        # llm = OpenAI(api_key=api_key)

    except Exception as e:
        return {"status": "error", "message": f"Exception when creating model: {e}"}

    return {"status": True, "data": llm, "message": "Model loaded."}


def invoke_prompt(params):

    api_key = params.get("api_key")

    model_name = params.get("model_name")

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    try:
        llm = ChatOpenAI(model=model_name, api_key=api_key)

    except Exception as e:
        return {"status": "error", "message": f"Exception when creating model: {e}"}

    return {"status": True, "data": llm, "message": "Model loaded."}


def transcribe_audio_to_text(params):
    """
    Transcribe an audio file to text using the new OpenAI Whisper transcription API.

    :param params: Dictionary containing the 'api_key' and 'audio-path' parameters.
    :return: Transcribed text or error message.
    """

    api_key = params.get("headers").get("api_key")
    file_items = params.get("params").get("audio-path", [])

    audio_file_path = file_items[0]

    try:

        llm = OpenAI(api_key=api_key)

        with open(audio_file_path, "rb") as audio_file:
            print(f"Transcribing file: {audio_file_path}")

            transcript = llm.audio.transcriptions.create(
              model="whisper-1",
              file=audio_file
            )

        return {"status": True, "data": transcript.text}

    except Exception as e:
        return {"status": False, "message": f"Exception when transcribing audio: {e}"} 
    
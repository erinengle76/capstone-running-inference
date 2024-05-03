import transformers
import torch
from PIL import Image
import io
import re
import json

def model_fn(model_dir):
    """
    Load the model and processor from the specified directory and prepare them for use.
    Args:
        model_dir (str): The directory where the model and processor are stored.
    Returns:
        dict: A dictionary containing the model, processor, and device.
    """
    print('Loading Model')
    # Set the device to GPU if available, otherwise use CPU.
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load the processor and model from the pre-trained checkpoint.
    processor = transformers.DonutProcessor.from_pretrained("azhara001/donut-base-demo-v2")
    model = transformers.VisionEncoderDecoderModel.from_pretrained("azhara001/donut-base-demo-v2").to(device)

    # Bundle the model artifacts into a dictionary.
    model_artifacts = {
        "processor": processor,
        "model": model,
        "device": device
    }
    print('Successfully packaged model artifacts')
    return model_artifacts

def input_fn(request_body, request_content_type):
    """
    Prepare input data for prediction.
    Args:
        request_body (bytes): The raw binary image data from the request.
        request_content_type (str): The MIME type of the request data.
    Returns:
        PIL.Image.Image: The image extracted from the request body.
    Raises:
        ValueError: If the content type is not supported.
    """
    print('Running input_fn')
    if request_content_type.startswith('image/'):  # Handling typical image formats.
        image_stream = io.BytesIO(request_body)
        image = Image.open(image_stream)
        print('Image instantiated')
        return image
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(model_input, model_artifacts):
    """
    Perform prediction using the loaded model and processed input data.
    Args:
        model_input (PIL.Image.Image): The image to be processed.
        model_artifacts (dict): A dictionary containing the model, processor, and device.
    Returns:
        dict: A dictionary containing the outputs and processor for further processing.
    """
    print('Running prediction')

    model = model_artifacts['model']
    device = model_artifacts['device']
    processor = model_artifacts['processor']

    # Convert the image to RGB and adjust its orientation if necessary.
    input_data = model_input.convert("RGB")
    if input_data.size[0] < input_data.size[1]:
        input_data = input_data.transpose(Image.ROTATE_90)

    # Define the expected image size for the model and adjust the processor settings.
    image_size = [1280, 960]
    processor.image_processor.size = image_size[::-1]
    processor.image_processor.do_align_long_axis = False

    # Process the image and prepare tensors for the model.
    pixel_values = processor(input_data, return_tensors="pt").pixel_values
    task_prompt = "<s_demo_v1>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt")["input_ids"]

    # Generate predictions.
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_position_embeddings,
        early_stopping=True,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=1,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
        output_scores=True,
    )

    # Package the outputs for final processing.
    prediction_output = {"outputs": outputs, "processor": processor}
    return prediction_output

def output_fn(prediction_output, content_type):
    """
    Process the model's prediction outputs into a readable and structured format.
    Args:
        prediction_output (dict): The outputs from the predict function.
        content_type (str): The expected content type of the output data.
    Returns:
        str: The structured prediction result in JSON format.
    Raises:
        ValueError: If the content type is not supported.
    """
    print('Running output processing')
    if content_type == 'application/json':
        processor = prediction_output['processor']
        outputs = prediction_output['outputs']

        # Decode the outputs to a human-readable sequence and clean up.
        sequence = processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()

        # Convert the cleaned sequence to JSON.
        output_data = processor.token2json(sequence)
        return json.dumps(output_data)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

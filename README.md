# capstone-running-inference

This repo hosts the code used to host our custom inference script and model via Sagemaker and access it using AWS lambda.

### Custom Inference Script

The tar archive titled space-donut, located within the custom-inference sub-folder, contains the inference python file and the requirements file and is in the appropriate format to be uploaded to S3 for the purposes of inference.

To upload to S3, first your computer must have the AWS command line interface configured. The role configured must have appropriate access permissions to modify the desired S3 bucket. Then, you can run the following in the command line:

```bash
aws s3 cp local-file-path s3://bucket-name/path/in/bucket
```

### Building a Sagemaker Endpoint

Once it is located in the bucket, Sagemaker must be configured with the appropriate permissions to access the S3 bucket. After configuring the appropriate permissions, create a domain to access Sagemaker studio. Once the domain is created, open Sagemaker Studio and open an instance of JupyterLab. From here you can upload and run the model-creation.ipynb script, located within the custom-inference sub-folder. The script must be modified to include the desired model, endpoint configuration, and endpoint names. The S3 bucket and sagemaker ARN must also be updated at the top. The script contains cells to test the endpoint, but a test image must first be uploaded into the same directory in the JupyterLab instance.

### Accessing the Endpoint via Lambda Script

The lambda_function.py file and requirements.txt needs to be packaged in a zip folder created in a virtual environment in which all of the dependencies are available. In order to set up the lambda function and package it locally, the following instructions from ChatGPT-4 were followed to deploy the script successfully in lambda. The lambda folder solely contains the lambda script, as the zip contains details regarding the boto3 configuration, which cannot be securely uploaded to this repo.

The lambda function file must be modified to include the endpoint name defined in the step above.

Managing dependencies for your AWS Lambda function is crucial, especially when your function interacts with AWS services like S3 and SageMaker. In Python, dependencies are often managed through a virtual environment or directly packaging libraries with your application code. Here’s how to handle these dependencies before deploying your Lambda function:

#### Step 1: Set Up Your Project

1. **Create a new directory** for your Lambda project. This will help in organizing your code and dependencies.

   ```bash
   mkdir lambda_project
   cd lambda_project
   ```

2. **Create a Python file** for your Lambda function, such as `lambda_function.py`.

#### Step 2: Manage Dependencies

1. **Create a `requirements.txt` file** in your project directory:
   ```plaintext
   boto3
   ```

2. **Install dependencies and package everything**:
   - You can use a script to install packages to a build directory and then zip everything:
     ```bash
     mkdir package
     pip install -r requirements.txt -t package/
     cd package
     zip -r ../function.zip .
     cd ..
     zip -g function.zip lambda_function.py
     ```

#### Step 3: Deploy to Lambda

1. **Upload the zip file** to AWS Lambda:
   - You can upload it directly in the AWS Management Console by selecting your function and then uploading the zip file under the "Function code" section.
   - Alternatively, you can use the AWS CLI:
     ```bash
     aws lambda update-function-code --function-name YourFunctionName --zip-file fileb://function.zip
     ```

2. **Set the handler information** correctly in the Lambda configuration to ensure it points to your function:
   - If your file is named `lambda_function.py` and your Lambda handler function is `lambda_handler`, set the handler as `lambda_function.lambda_handler`.

#### Tips and Best Practices

- **Keep your dependencies minimal**: Only include the necessary libraries to reduce the deployment package size and improve cold start times.
- **Test locally**: Use tools like AWS SAM (Serverless Application Model) or local testing tools to test your Lambda function locally before deploying.
- **Use layers**: For shared dependencies across multiple Lambda functions, consider using Lambda Layers to manage these libraries.

By following these steps, you can efficiently manage your Lambda dependencies, ensuring a smoother development and deployment process.
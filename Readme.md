# Image Processing Pipeline Project

## Project Overview
This project implements a **scalable image processing pipeline** using cloud services. The system processes image data, applies transformations, and stores the results in **AWS S3**.

## Key Features
- **Automated Image Processing**: Uses Python scripts to process images.
- **AWS S3 Integration**: Input and output storage for image data.
- **Dockerized Deployment**: Configurable environment using Docker.
- **Scalability**: Efficient workload distribution.

## Project Structure
```
Image-Processing-Pipeline/
│── Project2_Report.pdf          # Detailed project documentation
│── README.md                    # Project documentation
│── DynamoDB_dataloader/
│   ├── data_loader.py           # Loads metadata into DynamoDB
│── Work_load-generator/
│   ├── workload.py              # Simulates workload for the pipeline
│── docker/                      
│   ├── dockerfile               # Docker setup for deployment
│   ├── encoding.dat             # Model encoding data
│   ├── entry.sh                 # Entry script for Docker container
│   ├── handler.py               # Handles image processing
```

## Installation & Setup
### Prerequisites
1. Install **Docker**:
   ```sh
   sudo apt install docker.io
   ```
2. Install **AWS CLI** and configure credentials:
   ```sh
   aws configure
   ```
3. Install required Python dependencies:
   ```sh
   pip install boto3 pillow
   ```

### Running the Pipeline
1. **Build and Run Docker Container**:
   ```sh
   docker build -t image-processing-pipeline .
   docker run -d image-processing-pipeline
   ```

2. **Load Image Metadata into DynamoDB**:
   ```sh
   python DynamoDB_dataloader/data_loader.py
   ```

3. **Simulate Workload**:
   ```sh
   python Work_load-generator/workload.py
   ```

## AWS S3 Buckets
- **Input Bucket**: `cse546-paas-input-bucket-videos`
- **Output Bucket**: `cse546-paas-output-bucket-results`

## Data Flow Overview
1. **Image Upload**:
   - Users upload images to the input S3 bucket.
   
2. **Processing Pipeline**:
   - `handler.py` processes images using predefined transformations.
   - Data is extracted and loaded into **DynamoDB**.

3. **Processed Output**:
   - The transformed images are stored in the output S3 bucket.

## Configuration Details
- Modify `dockerfile` to adjust the containerized environment.
- Update `entry.sh` for startup configurations.

## Testing
- Use `workload.py` to generate and test workload scenarios.
- Manually inspect the processed images in the output bucket.

## License
This project is open-source under the **MIT License**.

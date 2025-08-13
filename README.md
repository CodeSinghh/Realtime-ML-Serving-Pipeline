## 🧠 Problem Identification & Approach

Before diving into the project, it’s important to understand the problem statement.  
In large companies, many critical services rely heavily on machine learning (ML) model predictions. As a result, ML engineers frequently develop and deploy new models with better performance or newer logic. However, while models keep getting shipped, few systems exist to manage or govern:

- How many models are currently in use  
- Which ones are outdated or redundant  
- Which ones are producing valid outputs  
- And which are causing latency or unexpected errors  

Over time, as more models are added without cleanup or orchestration, this leads to bloated infrastructure — increased storage usage, higher RAM consumption, slower response times, and error-prone predictions.

To address this, I built a backend system that intelligently manages ML models — tracking usage, staging predictions, running health checks, and loading only the required models. This project is inspired by Uber’s Michelangelo architecture, particularly their Realtime Prediction Service (RPS).

What makes this project stand out is that I couldn’t find anything like it published online — not on GitHub, not step-by-step Medium articles.  
So, it’s a complex problem to grasp and even harder to implement correctly. Yet it’s real, impactful, and built entirely from scratch.  

## ⚙️ Infrastructure Provisioning with Terraform (IaC Workflow)

So at first, I created the Terraform setup because I wanted to build the infrastructure using Infrastructure as Code (IaC), since it’s faster, consistent across environments, and avoids manual mistakes.

I started with the `main.tf` file, which takes care of all the core infrastructure — like provisioning the EC2 instance, assigning it the right security groups, enabling Docker through bootstrap scripts, and even setting up CloudWatch log groups and CPU alarms.

Then I created the `variables.tf` file to make everything parameterized — things like AWS region, AMI ID, EC2 type, or SSH key can be changed anytime without touching the main logic, which keeps the code reusable and clean.

After that, I moved to `networking.tf`, which sets up the VPC, subnet, route table, and internet gateway — giving my EC2 a structured and internet-accessible network with DNS and IP mapping.

I also included `cloudwatch.tf` to monitor the EC2’s health using alarms and log groups, so I’d always be aware of resource spikes like high CPU usage.

For future extensibility, I added a placeholder `waf.tf` to later integrate AWS WAF, although it’s optional and currently inactive.

Lastly, I used `outputs.tf` to print the EC2’s public IP, ID, and DNS right after provisioning — so I don’t have to dig through the AWS Console every time.

Once everything was set up, I followed the Terraform workflow using:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```
✅ I've also committed the `.terraform.lock.hcl` file to ensure consistent provider versions across environments and prevent unexpected issues during deployment.

## 🧠 Python Backend Design

After completing the Terraform infrastructure setup, I initiated the backend logic using **Python with Flask**. Flask provided a lightweight and flexible framework for building RESTful APIs, giving me precise control over how the ML model serves predictions, how health metrics are tracked, and how version management behaves in real-time. This made it the ideal fit for building a scalable and modular ML model serving system.

The main entry point of the application is `main.py`, which defines all the HTTP API routes such as model inference, health checks, and dynamic version switching. It serves as the central controller for managing incoming requests and coordinating them with the internal model logic.

Supporting this, `model_loader.py` handles the model’s lifecycle. It is responsible for loading models from disk, tracking the currently active version, and safely updating models on the fly without disrupting active inference.  
<p align="center">
  <img width="1000" alt="model_loader.py screenshot" src="https://github.com/user-attachments/assets/cb7ac9cc-32ca-4d79-a58b-77f58c68ee51" />
</p>
<p align="center"><b> Model is Upload Successfully ✅ • Model Last Used status " Never Used " </b></p>

The `health_check.py` module monitors system health. It exposes runtime metrics like model availability, responsiveness, last inference time, and potential internal issues — helping maintain observability across deployments.  
<p align="center">
  <img width="1000" alt="health_check.py screenshot" src="https://github.com/user-attachments/assets/f7688f7d-2a80-4c52-9da3-42537352be80" />
</p>
<p align="center"><b>Model Last Used Got Updated Precisely to the Second ⏱️ • Model Health is " Healthy " Because It is Giving Results</b></p>

For handling user inputs and executing predictions, `predict.py` was implemented. It processes incoming prompts or input data, routes them through the appropriate model, and formats the response back to the client. This includes input validation, tokenization (if applicable), and managing edge cases during inference.  
<p align="center">
  <img width="800" alt="predict.py screenshot" src="https://github.com/user-attachments/assets/e35915ae-b6b2-4ef3-9a7a-02f6bbe73f59" />
</p>
<p align="center"><b>Model is Responding to the Inputs</b></p>

Finally, the entire backend was containerized using **Docker** to ensure consistent and reproducible deployments across local machines, cloud environments.
## 🐳 Containerization & Runtime Environment

To containerize the application cleanly and prepare it for any environment, I created a production-grade Docker setup using a multi-stage Dockerfile. The idea was to build once and run anywhere, but without the clutter of unnecessary build-time dependencies or large image layers that slow things down.

In the first stage, I used `python:3.11-slim` as the builder base — it's lightweight and sufficient for installing all Python dependencies without bloating the final image. The install path is redirected using `--prefix=/install` to keep the build artifacts isolated. This not only makes the image clean but also allows for easier control over what's actually copied into the runtime. After the packages are installed, I explicitly remove caches, `__pycache__`, and `.dist-info` files — which don't need to ship with production containers and only add noise.

The second stage begins from a fresh slim image again, where I copy just the necessary dependencies and source code. I’ve added labels — like maintainer, version, and purpose — which helps in container scanning and asset traceability, especially in CI pipelines or container registries.

Running the application as a non-root user (`appuser`) is not just a best practice — it's a hard requirement in many secure environments. This avoids the risk of privilege escalation, especially when containers are deployed across different tenants or shared clusters. Environment variables like `PYTHONUNBUFFERED=1` ensure logs stream directly and are not buffered, which is important when stdout is being monitored in production via log aggregators.

Lastly, I’ve included a `.dockerignore` file to avoid polluting the Docker context with local development junk — things like `.env`, IDE configs, and compiled Python files. Without it, even accidental files could end up bloating the image or leaking secrets, and through this cleanup process, I was able to reduce the image size by **66%** — from **2.26 GB to 770 MB**.
<p align="center">
  <img width="1000" alt="Docker image before optimization" src="https://github.com/user-attachments/assets/63bc4feb-45b3-4ec8-b998-779ccc684178" />
</p>
<p align="center"><b>Before Optimization: 2.26 GB</b></p>

<p align="center">
  <img width="1000" alt="Docker image after optimization" src="https://github.com/user-attachments/assets/8eb9c9d1-ca0a-4efd-af00-eb0237c28e1e" />
</p>
<p align="center"><b>After Optimization: 773.3 MB</b></p>

📍 You can find the public Docker image here: [dhirajsingh6/ml-model-manager](https://hub.docker.com/r/dhirajsingh6/ml-model-manager)

## 🧪 Real-World Model Testing Flow

Once the trained `.h5` model was uploaded to the backend server (hosted on EC2), I bootstrapped the Flask-based inference service and triggered real-time tests using `curl` requests to live endpoints such as `/predict` and `/health`. This allowed me to simulate production-like conditions, validate inference accuracy, and observe dynamic behaviors like model switching and health responsiveness — without relying on mock test suites.

This testing flow reflects how many lean teams validate models in early-phase environments: directly, transparently, and close to real usage. It gave me high confidence in the model’s behavior, allowed for instant debugging, and keeping the system simple yet effective.

## ✅ Conclusion

This project was built from scratch to solve a real-world infrastructure problem — how to intelligently manage ML model lifecycles in production environments. From automated provisioning using Terraform, to containerized model serving with Docker and Flask, and finally validating behavior through real-time inference testing — every piece is designed to be minimal, functional, and close to how modern ML platforms actually operate.

What sets this system apart is not just the stack, but the mindset behind it: clarity over complexity, signal over noise. There’s no copy-pasting, no shallow abstraction — just clean, purposeful engineering that scales with need. Whether in early prototyping or production rollout phases, this architecture provides a strong foundation to monitor, manage, and serve machine learning models reliably.

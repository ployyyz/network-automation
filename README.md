# N_Kafka

## Project Overview
This project is a collaborative network automation project that uses Apache Kafka to handle router commands and responses.

A Flask API receives router commands and sends them to Kafka. A Python worker consumes the commands, connects to routers through SSH, executes the commands, and sends the results back through Kafka.

## Technologies Used
- Python
- Flask
- Apache Kafka
- Paramiko (SSH)
- Docker Compose

## Project Structure
- app.py - Flask API and Kafka producer/consumer
- worker.py - Processes router commands and executes them through SSH
- frontend/ - Frontend component
- docker-compose.yml - Kafka service setup

## My Contributions
I worked collaboratively with my team members and participated in all parts of the project, including development, implementation, integration, testing, and documentation.

## Team Project
Developed collaboratively with team members.

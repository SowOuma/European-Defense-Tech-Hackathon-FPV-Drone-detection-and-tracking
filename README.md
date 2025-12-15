# Synteza chalenge of EDTH : Detecting and Tracking FPV Drones with AI


## Overview
This project focuses on the development of an autonomous computer vision system capable of detecting and tracking small FPV drones in real time at distances of up to 500 meters. The system operates without external communication or human intervention and was developed during a hackathon.

## Problem Statement
Small FPV drones are extremely difficult to detect using traditional radar or RF-based systems. Most tactical units rely on human visual detection, which is unreliable and slow. This project explores an AI-based visual solution to address this gap.

## Solution
The system uses computer vision and AI models to:
- Detect small FPV drones in video streams
- Track targets in real time using CV tracking techniques
- Operate autonomously in a tactical environment

Synthetic datasets generated using **Synteza’s platform** (which provides  data generation tools) were used to train and evaluate the models.

## Key Features
- Real-time FPV drone detection at long range (~500 m)
- Autonomous operation (no human input, no external communication)
- AI-based detection and tracking
- Training on labeled synthetic data generated from 3D models

## Technologies
- Python
- OpenCV
- YOLO and bytracker
- Synthetic data generated via **Synteza platform**

## Context
The project was inspired by real-world scenarios in which Ukrainian forces must protect critical logistics nodes near Kharkiv from repeated FPV drone attacks.

## Status
Hackathon prototype – proof of concept demonstrating the feasibility of AI-based visual detection of FPV drones.


## Features
- **Real-time FPV Drone Detection**: Capable of identifying and tracking drones at distances up to 500 meters.
- **Autonomous Operation**: Fully autonomous system with no need for external communication or human input.
- **AI-based Computer Vision**: Utilizes machine learning models and computer vision trackers to achieve real-time detection and tracking.
- **Synthetic Dataset Generation**: 3D models of drones used to generate labeled datasets for training the AI models.

## Objective
The main goal of this project is to improve the detection and defense capabilities against small FPV drones, which pose a significant challenge in modern warfare scenarios. The system was designed to assist in securing critical logistical nodes, especially in conflict zones like Kharkiv, Ukraine, where these drones are used for surveillance and attacks.





## Dataset
This project uses synthetic 3D models of drones to generate labeled datasets for training AI models. The 3D models can be found in the datasets/ folder.

### Explications :
- **Description** : Présente brièvement l'objectif du projet et la raison de son développement.
- **Features** : Liste des fonctionnalités principales.
- **Objective** : Met l'accent sur l'impact de ce projet dans un contexte réel (zone de guerre, protection des infrastructures).
- **Tools & Technologies** : Détaille les outils et langages utilisés.
- **Installation** : Explique comment installer et configurer le projet.
- **Usage** : Instructions pour démarrer le projet sur un flux vidéo.
- **Dataset** : Mentionne l'utilisation des modèles 3D pour générer des jeux de données d'entraînement.
- **Contributing** : Encouragement à contribuer au projet en améliorant le code.
- **License** : Ajoute une licence MIT ou autre si nécessaire.

Cela devrait te fournir une documentation propre et claire pour ton projet sur GitHub. N'hésite pas à ajuster les détails en fonction des spécificités de ton implémentation.

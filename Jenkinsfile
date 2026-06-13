pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git 'https://github.com/Dharunr257/production-ready-two-tier-flask-app.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                pytest test_app.py
                '''
            }
        }
    }
}
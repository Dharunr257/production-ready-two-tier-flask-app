pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv

                ./venv/bin/python -m pip install --upgrade pip

                ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                ./venv/bin/pytest test_app.py
                '''
            }
        }
    }
}
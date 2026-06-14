pipeline {

    agent any

    stages {

        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }

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

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t production-ready-two-tier-flask-app:latest .
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                echo "Starting Trivy Scan..."

                trivy image \
                --scanners vuln \
                production-ready-two-tier-flask-app:latest
                '''
            }
        }

        stage('Deploy To Application Server') {
            steps {
                sh '''
                echo "Starting deployment..."

                ssh app-server "/home/ubuntu/deployment/deploy.sh"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                echo "Running post-deployment health check..."

                ssh app-server "curl -f http://localhost:5000/health"
                '''
            }
        }
    }

    post {

        success {

            echo '======================================='
            echo 'PIPELINE SUCCESSFUL'
            echo 'Application Deployed Successfully'
            echo '======================================='
        }

        failure {

            echo '======================================='
            echo 'PIPELINE FAILED'
            echo 'Check Jenkins Console Output'
            echo '======================================='
        }

        always {

            sh '''
            echo "Docker Images:"
            docker images | head -10 || true
            '''
        }
    }
}
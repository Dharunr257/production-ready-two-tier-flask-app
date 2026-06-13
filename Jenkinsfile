pipeline {
agent any

environment {
    APP_SERVER = "172.31.24.41"   
}

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
            sudo trivy image \
            --scanners vuln \
            production-ready-two-tier-flask-app:latest
            '''
        }
    }

    stage('Deploy To Application Server') {
        steps {
            sh '''
            ssh -o StrictHostKeyChecking=no ubuntu@$APP_SERVER "

            cd ~/production-ready-two-tier-flask-app &&

            git pull &&

            docker compose down &&

            docker compose up -d --build

            "
            '''
        }
    }

    stage('Health Check') {
        steps {
            sh '''
            ssh -o StrictHostKeyChecking=no ubuntu@$APP_SERVER "

            curl -f http://localhost:5000/health

            "
            '''
        }
    }
}

post {

    success {
        echo 'Deployment Successful'
    }

    failure {
        echo 'Pipeline Failed'
    }

    always {
        sh 'docker images | head -10 || true'
    }
}


}

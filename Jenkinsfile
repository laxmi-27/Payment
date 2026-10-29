pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE = 'C:\\DockerCLI\\cli-plugins\\docker-compose.exe'
    }

    stages {
        stage('Validate Docker Compose') {
            steps {
                bat '"%COMPOSE%" -f docker-compose.yml config --quiet'
            }
        }

        stage('Build Docker Images') {
            steps {
                bat '"%COMPOSE%" -f docker-compose.yml build'
            }
        }
    }

    post {
        success {
            echo 'CI passed. No containers were intentionally started or replaced.'
        }
        failure {
            echo 'CI failed. Check the Console Output.'
        }
    }
}
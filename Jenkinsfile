pipeline {
    agent any

    environment {
        IMAGE_NAME = "setthapong/asoc-demo"
        IMAGE_TAG  = "${BUILD_NUMBER}"
        REPORT_DIR = "reports"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare') {
            steps {
                sh '''
                    set -e
                    mkdir -p ${REPORT_DIR}
                    echo "Workspace: $(pwd)"
                    ls -la
                    docker version
                '''
            }
        }

        stage('SAST - Semgrep') {
            steps {
                sh '''
                    set +e
                    docker run --rm \
                      -v "$PWD:/src" \
                      semgrep/semgrep \
                      semgrep --config=p/security-audit /src \
                      --json --output /src/${REPORT_DIR}/semgrep.json
                    EXIT_CODE=$?
                    echo "Semgrep exit code: $EXIT_CODE"
                    ls -la ${REPORT_DIR} || true
                    exit 0
                '''
            }
        }

        stage('SCA - Trivy FS') {
            steps {
                sh '''
                    set +e
                    docker run --rm \
                      -v "$PWD:/project" \
                      aquasec/trivy:0.62.0 \
                      fs /project \
                      --format json \
                      --output /project/${REPORT_DIR}/trivy-fs.json
                    EXIT_CODE=$?
                    echo "Trivy FS exit code: $EXIT_CODE"
                    ls -la ${REPORT_DIR} || true
                    exit 0
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    docker build \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Container Scan - Trivy Image') {
            steps {
                sh '''
                    set +e
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v "$PWD:/project" \
                      aquasec/trivy:0.62.0 \
                      image ${IMAGE_NAME}:${IMAGE_TAG} \
                      --format json \
                      --output /project/${REPORT_DIR}/trivy-image.json
                    EXIT_CODE=$?
                    echo "Trivy image exit code: $EXIT_CODE"
                    ls -la ${REPORT_DIR} || true
                    exit 0
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        set -e
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
                echo "Final workspace check"
                pwd
                ls -la
                ls -la ${REPORT_DIR} || true
                find ${REPORT_DIR} -type f -name "*.json" || true
            '''
            archiveArtifacts artifacts: 'reports/**/*.json', fingerprint: true, allowEmptyArchive: true
            echo 'Pipeline completed.'
        }
        success {
            echo 'Build, scan, and push succeeded.'
        }
        unstable {
            echo 'Pipeline finished with warnings.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
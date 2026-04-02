pipeline {
    agent any

    environment {
        IMAGE_NAME = "setthapong/asoc-demo"
        IMAGE_TAG  = "${BUILD_NUMBER}"
        REPORT_DIR = "reports"
        EXPORT_DIR = "/exports/asoc-demo/${BUILD_NUMBER}"
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
                    set -eux
                    mkdir -p "${REPORT_DIR}"
                    chmod 777 "${REPORT_DIR}" || true
                    echo '{"test":"ok"}' > "${REPORT_DIR}/test.json"
                    echo "Workspace: $(pwd)"
                    ls -la
                    ls -la "${REPORT_DIR}"
                    docker version
                '''
            }
        }

        stage('SAST - Semgrep') {
            steps {
                sh '''
                    set +e
                    mkdir -p "${REPORT_DIR}"

                    echo "=== Jenkins workspace debug ==="
                    echo "PWD=$(pwd)"
                    ls -la
                    find . -maxdepth 3 -type f | sort

                    if [ ! -f "./app.py" ]; then
                    echo "ERROR: app.py not found in workspace root"
                    exit 1
                    fi

                    docker run --rm \
                    -v "$(pwd):/src" \
                    semgrep/semgrep:latest \
                    semgrep scan \
                        --config=auto \
                        --json \
                        --output /src/${REPORT_DIR}/semgrep.json \
                        --exclude /src/${REPORT_DIR} \
                        /src/app.py

                    EXIT_CODE=$?
                    echo "Semgrep exit code: $EXIT_CODE"

                    echo "=== Report files ==="
                    ls -la "${REPORT_DIR}" || true

                    echo "=== semgrep.json head ==="
                    sed -n '1,120p' "${REPORT_DIR}/semgrep.json" || true

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
                      fs /project --format json \
                      > "${REPORT_DIR}/trivy-fs.json"
                    EXIT_CODE=$?
                    echo "Trivy FS exit code: $EXIT_CODE"
                    ls -la "${REPORT_DIR}" || true
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
                      aquasec/trivy:0.62.0 \
                      image ${IMAGE_NAME}:${IMAGE_TAG} --format json \
                      > "${REPORT_DIR}/trivy-image.json"
                    EXIT_CODE=$?
                    echo "Trivy image exit code: $EXIT_CODE"
                    ls -la "${REPORT_DIR}" || true
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

        stage('Generate HTML Summary') {
            steps {
                sh '''
                    cat > "${REPORT_DIR}/index.html" <<EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ASOC Demo Report - Build ${BUILD_NUMBER}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; line-height: 1.5; }
    h1 { margin-bottom: 8px; }
    .meta { margin-bottom: 20px; }
    .card {
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }
    code {
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 4px;
    }
    a { text-decoration: none; }
  </style>
</head>
<body>
  <h1>ASOC Security Scan Report</h1>
  <div class="meta">
    <p><strong>Build:</strong> ${BUILD_NUMBER}</p>
    <p><strong>Image:</strong> ${IMAGE_NAME}:${IMAGE_TAG}</p>
    <p><strong>Generated:</strong> $(date -u '+%Y-%m-%d %H:%M:%S UTC')</p>
  </div>

  <div class="card">
    <h2>SAST - Semgrep</h2>
    <p>Raw report: <a href="semgrep.json">semgrep.json</a></p>
  </div>

  <div class="card">
    <h2>SCA - Trivy Filesystem</h2>
    <p>Raw report: <a href="trivy-fs.json">trivy-fs.json</a></p>
  </div>

  <div class="card">
    <h2>Container Scan - Trivy Image</h2>
    <p>Raw report: <a href="trivy-image.json">trivy-image.json</a></p>
  </div>

  <div class="card">
    <h2>Pipeline Evidence</h2>
    <p>Validation file: <a href="test.json">test.json</a></p>
  </div>
</body>
</html>
EOF
                    ls -la "${REPORT_DIR}"
                '''
            }
        }

        stage('Export Reports to Host') {
            steps {
                sh '''
                    set -eux
                    mkdir -p "${EXPORT_DIR}"
                    cp -f "${REPORT_DIR}"/* "${EXPORT_DIR}/" || true
                    ls -la "${EXPORT_DIR}" || true
                '''
            }
        }
    }

    post {
        always {
            sh '''
                echo "=== FINAL CHECK ==="
                pwd
                ls -la
                ls -la "${REPORT_DIR}" || true
                find "${REPORT_DIR}" -maxdepth 1 -type f | sort || true
                echo "=== EXPORT CHECK ==="
                ls -la "${EXPORT_DIR}" || true
            '''
            archiveArtifacts artifacts: 'reports/*', fingerprint: true, allowEmptyArchive: true
            echo 'Pipeline completed.'
        }
        success {
            echo 'Build, scan, push, export, and archive succeeded.'
        }
        unstable {
            echo 'Pipeline finished with warnings.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
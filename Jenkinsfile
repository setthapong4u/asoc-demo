pipeline {
    agent any

    environment {
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
                    set -eu
                    mkdir -p "${REPORT_DIR}"
                    echo '{"test":"ok"}' > "${REPORT_DIR}/test.json"
                '''
            }
        }

        stage('Debug Workspace') {
            steps {
                sh '''
                    set -eu
                    echo "=== WORKSPACE DEBUG ==="
                    pwd
                    ls -la
                    find . -maxdepth 5 -type f | sort
                '''
            }
        }

        stage('SAST - Semgrep') {
            steps {
                sh '''
                    set +e
                    mkdir -p "${REPORT_DIR}"

                    python3 -m pip install --user semgrep

                    ~/.local/bin/semgrep scan \
                      --config=p/python \
                      --json \
                      --output "${REPORT_DIR}/semgrep.json" \
                      --exclude "${REPORT_DIR}" \
                      app.py \
                      > "${REPORT_DIR}/semgrep-console.log" 2>&1

                    EXIT_CODE=$?
                    echo "Semgrep exit code: $EXIT_CODE"

                    echo "=== REPORT FILES ==="
                    ls -la "${REPORT_DIR}" || true

                    echo "=== SEMGREP CONSOLE ==="
                    sed -n '1,200p' "${REPORT_DIR}/semgrep-console.log" || true

                    echo "=== SEMGREP JSON ==="
                    sed -n '1,200p' "${REPORT_DIR}/semgrep.json" || true

                    exit 0
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*', fingerprint: true, allowEmptyArchive: true
        }
    }
}
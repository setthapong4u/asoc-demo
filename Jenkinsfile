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
                    set -eux
                    mkdir -p "${REPORT_DIR}"
                    chmod 777 "${REPORT_DIR}" || true
                    echo '{"test":"ok"}' > "${REPORT_DIR}/test.json"
                '''
            }
        }

        stage('Debug Workspace') {
            steps {
                sh '''
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

                    echo "=== BEFORE SEMGREP ==="
                    pwd
                    ls -la
                    ls -la "${REPORT_DIR}" || true
                    test -f app.py && echo "app.py exists"

                    docker run --rm \
                      --entrypoint /bin/sh \
                      -v "$(pwd):/src" \
                      semgrep/semgrep:latest \
                      -c "ls -la /src && semgrep scan --config=p/python --json --output /src/${REPORT_DIR}/semgrep.json --exclude /src/${REPORT_DIR} /src/app.py" \
                      2>&1 | tee "${REPORT_DIR}/semgrep-console.log"

                    EXIT_CODE=${PIPESTATUS[0]}
                    echo "Semgrep exit code: $EXIT_CODE"

                    echo "=== AFTER SEMGREP ==="
                    ls -la "${REPORT_DIR}" || true

                    echo "=== SEMGREP CONSOLE LOG ==="
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
            sh '''
                echo "=== FINAL CHECK ==="
                pwd
                ls -la
                ls -la "${REPORT_DIR}" || true
                find "${REPORT_DIR}" -maxdepth 1 -type f | sort || true
            '''
            archiveArtifacts artifacts: 'reports/*', fingerprint: true, allowEmptyArchive: true
            echo 'SAST-only pipeline completed.'
        }
    }
}
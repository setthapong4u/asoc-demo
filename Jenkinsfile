pipeline {
    agent any

    environment {
        REPORT_DIR = "reports"
        SEMGREP_IMAGE = "semgrep/semgrep:latest"
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

                    echo "=== CLEAN OLD FILES ==="
                    rm -f "${REPORT_DIR}/semgrep.json" "${REPORT_DIR}/semgrep-console.log" || true

                    echo "=== CREATE CONTAINER ==="
                    CID=$(docker create --entrypoint /bin/sh "${SEMGREP_IMAGE}" -c "
                        cd /src && \
                        ls -la && \
                        semgrep scan \
                          --config=p/python \
                          --json \
                          --output /src/${REPORT_DIR}/semgrep.json \
                          --exclude /src/${REPORT_DIR} \
                          /src/app.py
                    ")
                    echo "Container ID: ${CID}"

                    echo "=== COPY WORKSPACE INTO CONTAINER ==="
                    docker cp . "${CID}:/src"

                    echo "=== VERIFY CONTAINER CONTENT ==="
                    docker start -a "${CID}" > "${REPORT_DIR}/semgrep-console.log" 2>&1
                    EXIT_CODE=$?
                    echo "Semgrep exit code: ${EXIT_CODE}"

                    echo "=== COPY REPORTS BACK ==="
                    docker cp "${CID}:/src/${REPORT_DIR}/semgrep.json" "${REPORT_DIR}/semgrep.json" 2>/dev/null || true

                    echo "=== REMOVE CONTAINER ==="
                    docker rm -f "${CID}" >/dev/null 2>&1 || true

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
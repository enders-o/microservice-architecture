@Library('microservice-architecture@main') _
    
node('python_agent') {
    stage('Build Microservices') {
        checkout scm
        dir('Analyzer') {
            python_lint('analyzer', 'analyzer-svc', 8110)
        }

        dir('Receiver') {
            python_lint('receiver', 'receiver-svc', 8080)
        }

        dir('Processing') {
            python_lint('processing', 'processing-svc', 8100)
        }

        dir('Storage') {
            python_lint('storage', 'storage-svc', 8090)
        }
    }
}

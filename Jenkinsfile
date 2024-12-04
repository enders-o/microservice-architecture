@Library('microservice-architecture@main') _
    
node('python_agent') {
    stage('Build Microservices') {
        checkout scm
        dir('Analyzer') {
            python_build('analyzer', 'analyzer-svc', 8110)
        }

        dir('Receiver') {
            python_build('receiver', 'receiver-svc', 8080)
        }

        dir('Processing') {
            python_build('processing', 'processing-svc', 8100)
        }

        dir('Storage') {
            python_build('storage', 'storage-svc', 8090)
        }
    }
}

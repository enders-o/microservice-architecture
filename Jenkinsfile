@Library('microservice-architecture@main') _

pipeline {
    agent { label 'python_agent' }
    parameters {
        booleanParam(defaultValue: false, description: 'Deploy the App', name:'DEPLOY')
    }
    stages {
        stage('Build All Services') {
            steps {
                script {
                    checkout scm
                    
                    dir('Analyzer') {  
                        python_build('analyzer', 'analyzer-svc', 8110)()
                    }
                    
                    dir('Receiver') {
                        python_build('receiver', 'receiver-svc', 8110)()
                    }
                    
                    dir('Processing') {
                        python_build('processing', 'processing-svc', 8110)()
                    }
                    
                    dir('Storage') {
                        python_build('storage', 'storage-svc', 8110)()
                    }

                    dir('Anomaly') {
                        python_build('anomaly', 'anomaly-svc', 8110)()
                    }
                }
            }
        }
    }
}

@Library('microservice-architecture@main') _
pipeline {
    agent { label 'python_agent' }
    
    stages {
        stage('Build Microservices') {
            parallel {
                stage('Analyzer Service') {
                    steps {
                        dir('Analyzer') {
                            script {
                                python_build('analyzer', 'analyzer-svc', 8110)
                            }
                        }
                    }
                }
                
                stage('Receiver Service') {
                    steps {
                        dir('Receiver') {
                            script {
                                python_build('receiver', 'receiver-svc', 8080)
                            }
                        }
                    }
                }
                
                stage('Processing Service') {
                    steps {
                        dir('Processing') {
                            script {
                                python_build('processing', 'processing-svc', 8100)
                            }
                        }
                    }
                }
                
                stage('Storage Service') {
                    steps {
                        dir('Storage') {
                            script {
                                python_build('storage', 'storage-svc', 8090)
                            }
                        }
                    }
                }
            }
        }
    }
    
}

def call(dockerRepoName, imageName, portNum){
    pipeline {
        agent { label 'python_agent' }
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name:'DEPLOY')
        }
        stages {
            stage('Linter') {
                steps{
                    sh 'pylint --fail-under 5 *.py'
                }
            }
            stage('Package') {
                when {
                        expression { env.GIT_BRANCH == 'origin/main' }
                }
                steps {
                    withCredentials([string(credentialsId: 'Dockerhub', variable: 'TOKEN')]) {
                        sh "docker login -u 'enderso' -p '$TOKEN' docker.io"
                        sh "docker build -t ${dockerRepoName}:latest --tag enderso/${dockerRepoName}:${imageName} ."
                        sh "docker push enderso/${dockerRepoName}:${imageName}"
                    }
                }
            }
            stage('Deploy') {
                when {
                    expression { params.DEPLOY }
                }
                steps{
                    sh "docker stop ${dockerRepoName} || true && docker rm ${dockerRepoName} || true"
                    sh "docker run -d -p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
                }

            }
        }
    }
}


def call(dockerRepoName, imageName, portNum){
    return {
        stage('Linter') {
            sh 'pylint --fail-under 5 *.py'
        }
        stage('Package') {
            if (env.GIT_BRANCH == 'origin/main') {
                withCredentials([string(credentialsId: 'Dockerhub', variable: 'TOKEN')]) {
                    sh "docker login -u 'enderso' -p '$TOKEN' docker.io"
                    sh "docker build -t ${dockerRepoName}:latest --tag enderso/${dockerRepoName}:${imageName} ."
                    sh "docker push enderso/${dockerRepoName}:${imageName}"
                }
            }
        }
        stage('Deploy') {
            if (params.DEPLOY) {
                sh "docker stop ${dockerRepoName} || true && docker rm ${dockerRepoName} || true"
                sh "docker run -d -p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
            }
        }
    }
}

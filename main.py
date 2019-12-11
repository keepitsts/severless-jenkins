Will this create another release?
check for change!


Look for all these changes! 
9th
10th
8th

3rd
4th
5th
6th
Let check for this!

7th

def nonprodAcct = '345248387622'
def nonprodBucket = 'sts-np-compliance-bundles'
def prodAcct = '737855703655'
def prodBucket = 'sts-compliance-bundles'
def functionName = 'aws-jenkins-test'
def region = 'us-east-1'
// def DEV_ROLE_ARN = 'arn:aws:iam::345248387622:role/JenkinsAssumedRole' 


pipeline {
    agent any 
    stages {
        stage(‘Checkout’) { 
            steps {
                checkout scm 
                    /* .. snip .. */
            }
        }
        
        stage(‘Build’) {
            steps {
                sh "zip ${commitID()}.zip main.py"
            }
        }
        
        stage(‘Sonarqube’) { 
            steps {
                   
                 withSonarQubeEnv('jenkins-python-aws') {
                    
                }
                echo 'sonar part'
            } 
        }
        
        stage(‘Push_NonProd’) { 
            when { 
            not { 
                branch 'master' 
            }
        }
            steps {
                withAWS(role: 'JenkinsAssumedRole', roleAccount: nonprodAcct) {
                    sh "aws s3 cp ${commitID()}.zip s3://${nonprodBucket}/${functionName}/${commitID()}.zip"
                }
            }
        }
        
        stage(‘Push_Prod’) { 
            when { 
             
                branch 'master' 
            }
            steps {

                withAWS(role: 'JenkinsAssumedRole', roleAccount: prodAcct) {
                    sh "aws s3 cp ${commitID()}.zip s3://${prodBucket}/${functionName}/${commitID()}.zip"
                }

            }
        }
        stage(‘Deploy_NonProd’) {
            when { 
            not { 
                branch 'master' 
            }
        }    
            steps {
              withAWS(role: 'JenkinsAssumedRole', roleAccount: nonprodAcct) {
                    
                    sh "aws lambda update-function-code --function-name ${functionName} \
                        --s3-bucket ${nonprodBucket} \
                        --s3-key ${functionName}/${commitID()}.zip \
                        --region ${region}"
                    
                     sh "aws lambda publish-version --function-name ${functionName} \
                         --description '<https://github.com/keepitsts/jenkins-serverless-aws/commit/${commitID()}>'"                  
                }
                
            } 
        }
        stage(‘Deploy_Prod’) {
            when { 
             
                branch 'master' 
            }
            steps {
                withAWS(role: 'JenkinsAssumedRole', roleAccount: prodAcct) {
                    sh "aws lambda update-function-code --function-name ${functionName} \
                        --s3-bucket ${prodBucket} \
                        --s3-key ${functionName}/${commitID()}.zip \
                        --region ${region}"
                    
                    sh "aws lambda publish-version --function-name ${functionName} \
                         --description '<https://github.com/keepitsts/jenkins-serverless-aws/commit/${commitID()}>'" 
                }
            } 
        }
    }
}

def commitID() {
    sh 'git rev-parse HEAD > .git/commitID'
    def commitID = readFile('.git/commitID').trim()
    sh 'rm .git/commitID'
    commitID
}

